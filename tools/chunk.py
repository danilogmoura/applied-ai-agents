"""
Chunking dos blocos extraídos em pedaços pesquisáveis.

Objetivo: produzir chunks que (a) caibam no limite de tokens do embedder,
(b) preservem contexto via sobreposição, e (c) mantenham o TEXTO LITERAL
para que uma citação futura seja verificável por exact-match.

Estratégia: split por parágrafo → empacota até `max_tokens` com overlap de
`overlap_tokens`. Não reescreve nem resume — só corta. Isso é essencial para
anti-alucinação: o chunk é a fonte da verdade, não um resumo do modelo.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable

from tools.extract import SourceBlock

try:  # tiktoken é opcional: sem ele usamos heurística char/4.
    import tiktoken
except ModuleNotFoundError:  # pragma: no cover - ambiente sem deps
    tiktoken = None

# text-embedding-3-small usa o encoding cl100k_base e aceita até 8191 tokens.
# Deixamos folga para não estourar ao colar metadados na hora de embeddar.
_EMBED_MODEL_MAX_TOKENS = 8191
_DEFAULT_CHUNK_TOKENS = 400
_DEFAULT_OVERLAP_TOKENS = 60


@dataclass
class Chunk:
    """Um pedaço de texto pronto para embeddar, com procedência completa."""

    id: str                 # chave estável e única: hash(source, order, idx)
    text: str               # conteúdo literal (fonte de verdade p/ exact-match)
    source: str             # caminho::arquivo ou caminho#secao
    doc_id: str
    title: str
    kind: str               # "book" | "docs"
    order: int              # posição global determinística
    chunk_index: int        # posição dentro do bloco
    n_chunks: int           # total de chunks do bloco


def _make_id(source: str, order: int, chunk_index: int) -> str:
    """
    Id globalmente único e determinístico para um chunk.

    Usa o `source` completo (que inclui o caminho do arquivo), não apenas o
    doc_id — pois dois arquivos diferentes podem ter seções homônimas (ex.:
    'Check the docs' repetido em várias páginas FastAPI), o que colidiria.
    Hash curto mantém a chave limpa para o Chroma (sem ':'/'#' problemáticos).
    """
    key = f"{source}||{order}||{chunk_index}"
    digest = hashlib.sha1(key.encode("utf-8")).hexdigest()[:20]
    return f"chk-{digest}"


def _paragraphs(text: str) -> list[str]:
    """Divide em parágrafos não-vazios, preservando o texto cru."""
    parts = [p.strip() for p in text.split("\n\n")]
    return [p for p in parts if p]


class TokenChunker:
    """Chunker por contagem real de tokens (tiktoken), com sobreposição."""

    def __init__(
        self,
        max_tokens: int = _DEFAULT_CHUNK_TOKENS,
        overlap_tokens: int = _DEFAULT_OVERLAP_TOKENS,
        model: str = "text-embedding-3-small",
    ) -> None:
        if overlap_tokens >= max_tokens:
            raise ValueError("overlap_tokens deve ser menor que max_tokens")
        self.max_tokens = min(max_tokens, _EMBED_MODEL_MAX_TOKENS)
        self.overlap_tokens = overlap_tokens
        if tiktoken is not None:
            self._enc = tiktoken.get_encoding("cl100k_base")
        else:  # fallback heurístico: ~4 chars por token (padrão OpenAI)
            self._enc = None

    def _count(self, s: str) -> int:
        """Número de tokens (tiktoken) ou estimativa char/4 no fallback."""
        if self._enc is not None:
            return len(self._enc.encode(s, disallowed_special=()))
        return max(1, len(s) // 4)

    def _tok(self, s: str) -> list[int]:
        """Codifica texto em ids de token reais (só com tiktoken disponível)."""
        assert self._enc is not None, "_tok exige tiktoken"
        return self._enc.encode(s, disallowed_special=())

    def _detok(self, ids: list[int]) -> str:
        assert self._enc is not None, "_detok exige tiktoken"
        return self._enc.decode(ids)

    def _slice_tokens(self, text: str, start: int, end: int) -> str:
        """Recorta [start:end] em unidades de token, nas duas implementações."""
        if self._enc is not None:
            return self._detok(self._tok(text)[start:end])
        step = 4
        return text[start * step : end * step]

    def chunk_block(self, block: SourceBlock) -> list[Chunk]:
        """Converte um SourceBlock em 1..N chunks com overlap."""
        paras = _paragraphs(block.text)
        if not paras:
            return []

        # Junta parágrafos em unidades que respeitem max_tokens; se um
        # parágrafo sozinho for gigante, faz split por tokens.
        units: list[str] = []
        for para in paras:
            n = self._count(para)
            if n <= self.max_tokens:
                units.append(para)
            else:
                stride = self.max_tokens - self.overlap_tokens
                for i in range(0, n, stride):
                    piece = self._slice_tokens(para, i, i + self.max_tokens)
                    if piece.strip():
                        units.append(piece)

        # Empacota unidades em chunks com sobreposição por cauda de unidades.
        chunks_text: list[str] = []
        current: list[str] = []
        current_len = 0
        for unit in units:
            unit_len = self._count(unit)
            if current and current_len + unit_len > self.max_tokens:
                chunks_text.append("\n\n".join(current).strip())
                # carry-over: mantém as últimas unidades como overlap
                tail: list[str] = []
                acc = 0
                for prev in reversed(current):
                    plen = self._count(prev)
                    if acc + plen > self.overlap_tokens:
                        break
                    tail.insert(0, prev)
                    acc += plen
                current = tail
                current_len = acc
            current.append(unit)
            current_len += unit_len
        if current:
            chunks_text.append("\n\n".join(current).strip())

        n = len(chunks_text)
        out: list[Chunk] = []
        for idx, text in enumerate(chunks_text):
            if not text:
                continue
            out.append(
                Chunk(
                    id=_make_id(block.source, block.order, idx),
                    text=text,
                    source=block.source,
                    doc_id=block.doc_id,
                    title=block.title,
                    kind=block.kind,
                    order=block.order,
                    chunk_index=idx,
                    n_chunks=n,
                )
            )
        return out

    def chunk_all(self, blocks: Iterable[SourceBlock]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for block in blocks:
            chunks.extend(self.chunk_block(block))
        return chunks


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    from tools.extract import extract_all

    ap = argparse.ArgumentParser(description="Chunking do corpus.")
    ap.add_argument("--root", default="docs/applied-ai-agents")
    ap.add_argument("--max-tokens", type=int, default=_DEFAULT_CHUNK_TOKENS)
    ap.add_argument("--overlap", type=int, default=_DEFAULT_OVERLAP_TOKENS)
    args = ap.parse_args()

    root = Path(args.root)
    blocks = extract_all(root)
    chunker = TokenChunker(max_tokens=args.max_tokens, overlap_tokens=args.overlap)
    chunks = chunker.chunk_all(blocks)

    print(f"[chunk] {len(blocks)} blocos -> {len(chunks)} chunks "
          f"(max={args.max_tokens} tok, overlap={args.overlap})")
    sizes = [chunker._count(c.text) for c in chunks[:200]]
    if sizes:
        print(f"[chunk] amostra de tamanhos: min={min(sizes)} max={max(sizes)}")
    for c in chunks[:3]:
        print(f"  - {c.id} [{c.kind}] ({len(c.text)} chars) :: {c.text[:80]!r}...")
