"""
Modo B do plano docs/enriquecer_materiais_rag_plan.md — Âncoras de citação.

Promove as MELHORES entradas do mapa de cobertura (modules/<m>/SOURCES.md) para
uma âncora dentro do próprio MATERIAL.md, logo abaixo do heading correspondente.

PRINCÍPIO (mesmo do modo A): enriquecer ≠ gerar. Não escrevemos prosa — só um
ponteiro verificável. A citação é colhida LITERALMENTE do chunk cru do índice e
só entra se passar em verify_literal() byte-a-byte. Se não passar, NÃO inserimos.

Regras cross-linguais (plano §3):
  - marca o idioma [EN]/[ZH];
  - NUNCA traduz o quote (traduzir = editar = risco);
  - autor + título + capítulo/localizador na linha de cabeçalho da âncora.

Idempotente: um heading que já tem âncora (marcador ANCHOR) não ganha outra.

Execução:
    python -m tools.insert_anchors --module 04-rag --dry-run   # mostra, não escreve
    python -m tools.insert_anchors --module 04-rag             # escreve MATERIAL.md
    python -m tools.insert_anchors                             # todos os módulos
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from tools.build_index import DEFAULT_INDEX_DIR
from tools.coverage_map import (
    MODULES_DIR,
    _clean_heading,
    _quote_is_noise,
    _snippet,
    detect_lang,
    format_source,
)
from tools.query import search

# Marcador invisível-ish para idempotência: toda âncora gerada carrega este selo.
ANCHOR_MARK = "📖 Fonte:"


class _LiteralCache:
    """
    Verificador literal com o corpus em MEMÓRIA. verify_literal() recarrega os 5912
    chunks do disco a CADA chamada (~12s); como testamos dezenas de frases por seção,
    isso torna a rodada inviável. Carregamos uma vez e conferimos substring in-memory —
    MESMA semântica byte-a-byte, ~1000x mais rápido.
    """
    def __init__(self, index_dir: Path) -> None:
        from tools.build_index import ChromaStore
        from tools.embed import QwenEmbedder

        store = ChromaStore(index_dir)
        got = store.collection.get(include=["documents"])
        self._docs = got["documents"]
        # UM embedder compartilhado + memoização de vetores: a mesma frase reaparece em
        # várias seções; reconstruir QwenEmbedder() por frase era o gargalo (~49 min).
        self._embedder = QwenEmbedder()
        self._vec: dict[str, list[float]] = {}

    def verify(self, needle: str) -> bool:
        return any(needle in doc for doc in self._docs)

    def embed(self, text: str) -> list[float]:
        v = self._vec.get(text)
        if v is None:
            v = self._embedder.embed_one(text)
            self._vec[text] = v
        return v

_BOILER = re.compile(r"telegram|t\.me|未经授权|获取更多电子书|EPUB_\d+|https?://", re.IGNORECASE)
# Artefatos de extração do EPUB (âncoras/índices colados no texto). Se presentes na
# frase, ela não é citável de forma limpa — mesmo passando em verify_literal, pulamos.
_ARTIFACT = re.compile(r"idx_[0-9a-f]{6,}|_{2,}|\{\s*#|href=|<[a-z]+>", re.IGNORECASE)
# Marcadores de nota de rodapé colados na palavra (extração EPUB): "conversation.15",
# "informa tion" (palavra quebrada por newline sem espaço). Frases com isso são
# verificáveis mas leem quebradas — rejeitamos como âncora.
_FOOTNOTE = re.compile(
    r"[a-z]\.[0-9]{1,3}\b"          # word.15  (número de footnote colado à palavra)
    r"|[a-zá-ú]ion\s+[a-zá-ú]{2,4}\b",  # '...tion' + palavra curta solta (palavra partida)
    re.IGNORECASE,
)
# Narração de capítulo/promo ("By the end of this chapter you will build…", "In this
# chapter we…"). Verificável mas não é conteúdo substantivo sobre o conceito — pulamos.
_CHAPTER_NARRATION = re.compile(
    r"\bby the end of this (?:chapter|section)|in this (?:chapter|section|module)"
    r"|you will (?:not only )?(?:learn|build|understand)|neste (?:cap[íi]tulo|m[óo]dulo)",
    re.IGNORECASE,
)

# Similaridade mínima entre o EMBEDDING DA FRASE e o ASSUNTO REAL DA SEÇÃO
# (título + descritor). Gate de topicalidade: garante que a citação trata DO que a
# seção ensina — não apenas do termo-ponte que a trouxe. Um trecho sobre "dashboards"
# pontua bem contra "benchmark" mas é off-topic p/ uma seção "Métricas que Importam".
_QUOTE_TOPICAL_MIN = 0.45


def _cosine(a: list[float], b: list[float]) -> float:
    num = sum(x * y for x, y in zip(a, b))
    den = (sum(x * x for x in a) ** 0.5) * (sum(y * y for y in b) ** 0.5)
    return num / den if den > 0 else 0.0


def _best_quote_for(
    term: str, heading: str, descriptor: str, index_dir: Path, min_sim: float,
    cache: "_LiteralCache",
) -> dict | None:
    """
    Roda a escada de busca do coverage_map (termo → descritor) e devolve o melhor
    hit ACIMA do limiar cuja frase seja: (a) literal verificável byte-a-byte,
    (b) livre de artefatos/notas-de-rodapé, e (c) TOPICAL ao ASSUNTO DA SEÇÃO
    (título + descritor, NÃO o termo-ponte). Dentre as frases que passam, escolhe a
    MAIS alinhada ao título — não a primeira acima do corte. Retorna None se nada passar.
    """
    hits = search(term, k=5, index_dir=index_dir)
    usable = [h for h in hits if h["similarity"] >= min_sim and not _quote_is_noise(h["text"])]
    if not usable and descriptor:
        retry = search(f"{term}. {descriptor}", k=5, index_dir=index_dir)
        usable = [h for h in retry if h["similarity"] >= min_sim and not _quote_is_noise(h["text"])]
    if not usable:
        return None

    # Âncora de topicalidade = o que a seção REALMENTE ensina (título + descritor).
    subject = f"{heading}. {descriptor}".strip(" .")
    try:
        subj_vec = cache.embed(subject)
    except Exception:
        subj_vec = None

    best: tuple[float, dict, str] | None = None  # (alinhamento, hit, frase)
    for h in sorted(usable, key=lambda x: x["similarity"], reverse=True):
        for quote in _candidate_sentences(h["text"]):
            if subj_vec is not None:
                try:
                    align = _cosine(subj_vec, cache.embed(quote))
                except Exception:
                    continue
                if align < _QUOTE_TOPICAL_MIN:
                    continue
            else:
                align = 1.0  # sem vetores: aceita (já passa no verify_literal)
            if cache.verify(quote) and (best is None or align > best[0]):
                best = (align, h, quote)
    if best is None:
        return None
    _, h, quote = best
    h["_quote"] = quote
    return h


def _candidate_sentences(text: str) -> list[str]:
    """
    Devolve TODAS as sentenças literais (byte-a-byte) candidatas do chunk cru,
    SEM spam/boilerplate/artefatos/notas-de-rodapé e com comprimento útil
    (>= ~60 chars). Ordenadas da MAIS LONGA p/ a mais curta (uma citação mais
    completa tende a ser mais informativa). Cada item é exatamente uma substring
    de `text`, de modo que verify_literal() possa confere-la.
    """
    # normaliza espaços SÓ para segmentar/dividir; a fatia final vem do texto cru.
    clean = re.sub(r"\s+", " ", text).strip()
    parts = re.split(r"(?<=[.!?。！？])\s+", clean)
    out: list[str] = []
    for p in parts:
        cand = p.strip(" >#*-\t")
        if len(cand) < 60:
            continue
        if _BOILER.search(cand) or _ARTIFACT.search(cand) or _FOOTNOTE.search(cand):
            continue
        if _CHAPTER_NARRATION.search(cand):
            continue
        if len(cand) > 240:
            cut = cand[:240]
            sp = cut.rfind(" ")
            cand = cut[:sp] if sp > 120 else cut
        out.append(cand)
    out.sort(key=len, reverse=True)
    return out


def _anchor_block(hit: dict) -> str:
    """Renderiza o bloco-citação (blockquote) no formato do plano §4."""
    lang = detect_lang(hit["_quote"])
    src = format_source(hit["source"], hit.get("title", ""))
    q = hit["_quote"].replace('"', "'").strip()
    return (
        f"> {ANCHOR_MARK} **[{lang[1:-1]}]** {src} —\n"
        f"> \"{q}\""
    )


def insert_module(
    module_dir: Path, index_dir: Path, min_sim: float, dry_run: bool,
    cache: "_LiteralCache",
) -> tuple[int, int]:
    """Retorna (âncoras_inseridas, candidatos_sem_cotacao)."""
    material = module_dir / "MATERIAL.md"
    sources = module_dir / "SOURCES.md"
    if not material.exists() or not sources.exists():
        print(f"[skip] {module_dir.name}: falta MATERIAL.md ou SOURCES.md")
        return (0, 0)

    from tools.coverage_map import extract_concepts

    concepts = extract_concepts(material.read_text(encoding="utf-8"))
    md_lines = material.read_text(encoding="utf-8").splitlines()

    inserted = skipped = 0
    new_lines: list[str] = []
    i = 0
    n = len(md_lines)
    while i < n:
        line = md_lines[i]
        new_lines.append(line)
        m = re.match(r"^###\s+(.*)$", line.strip())
        if not m:
            i += 1
            continue
        heading = _clean_heading(m.group(1))
        # acha o conceito correspondente (match pelo termo extraído == heading limpo)
        term = next((t for t in concepts if _norm(t) == _norm(heading)), None)
        if not term:
            i += 1
            continue
        # pula se a seção JÁ tem âncora antes do próximo heading
        j = i + 1
        already = False
        while j < n and not re.match(r"^#{1,6}\s", md_lines[j].strip()):
            if ANCHOR_MARK in md_lines[j]:
                already = True
                break
            j += 1
        if already:
            i += 1
            continue
        hit = _best_quote_for(term, heading, concepts.get(term, ""), index_dir, min_sim, cache)
        if not hit:
            skipped += 1
            i += 1
            continue
        block = _anchor_block(hit)
        if dry_run:
            print(f"  [{module_dir.name}] ### {heading}")
            print("    " + block.replace("\n", "\n    "))
        else:
            new_lines.append("")
            new_lines.append(block)
        inserted += 1
        i += 1

    if not dry_run and inserted:
        material.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return (inserted, skipped)


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def main() -> None:
    ap = argparse.ArgumentParser(description="Âncoras de citação no MATERIAL (modo B).")
    ap.add_argument("--module", help="Nome de um módulo (ex: 04-rag). Senão, todos.")
    ap.add_argument("--min-sim", type=float, default=0.55,
                    help="Similaridade mínima p/ promover (mais alto que o modo A: só o melhor vira âncora).")
    ap.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    ap.add_argument("--dry-run", action="store_true", help="Mostra as âncoras propostas, SEM escrever.")
    args = ap.parse_args()

    if not args.index_dir.exists():
        raise SystemExit(f"Índice não encontrado em {args.index_dir}. Rode setup_corpus_index.sh antes.")

    if args.module:
        dirs = [MODULES_DIR / args.module]
    else:
        dirs = sorted(d for d in MODULES_DIR.iterdir() if (d / "MATERIAL.md").exists())

    # corpus em memória UMA vez — evita recarregar 5912 chunks a cada frase testada.
    cache = _LiteralCache(args.index_dir)

    tot_ins = tot_skip = 0
    for d in dirs:
        if not d.exists():
            print(f"[erro] módulo não existe: {d}")
            continue
        ins, sk = insert_module(d, args.index_dir, args.min_sim, args.dry_run, cache)
        tot_ins += ins
        tot_skip += sk
        tag = "propostas" if args.dry_run else "inseridas"
        print(f"[{d.name}] {ins} âncoras {tag} · {sk} conceitos sem cotação verificável")

    print(f"\n🧮 TOTAL: {tot_ins} âncoras ({'propostas' if args.dry_run else 'inseridas'}) · {tot_skip} sem cotação")
    if not args.dry_run:
        print("⚠️  Cada âncora passou em verify_literal (byte-a-byte). Confira o diff antes de commitar.")


if __name__ == "__main__":
    main()
