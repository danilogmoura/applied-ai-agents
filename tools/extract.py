"""
Extração de texto a partir das fontes em docs/applied-ai-agents/.

Duas famílias de fonte:
    - .epub  : arquivo ZIP cujo conteúdo é XHTML. Extraído com zipfile +
               strip de tags (sem dependência de LLM nem de ebooklib).
    - .md    : Markdown puro (ex.: fastapi-docs-en/docs/**). Lido direto.

Cada bloco devolvido carrega metadados de procedência para que uma
afirmação futura possa ser verificada por exact-match contra o trecho literal.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterator


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TIPOS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass
class SourceBlock:
    """Um bloco contíguo de texto extraído de uma fonte, com procedência."""

    text: str
    source: str          # caminho relativo ao root do projeto
    doc_id: str          # identificador estável (arquivo/seção)
    title: str = ""      # título do capítulo/página, quando houver
    order: int = 0       # posição dentro da fonte (para ordenar chunks)
    kind: str = "book"   # "book" | "docs"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STRIP DE HTML → TEXTO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


class _TextExtractor(HTMLParser):
    """Extrai texto visível de XHTML, descartando script/style."""

    _SKIP = {"script", "style", "head"}

    def __init__(self) -> None:
        super().__init__()
        self._parts: list[str] = []
        self._skip_depth = 0
        self._title_parts: list[str] = []
        self._in_title = False

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001
        if tag in self._SKIP:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP and self._skip_depth > 0:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        # Bloco de parágrafo/cabeçalho vira quebra de linha.
        if tag in {"p", "div", "h1", "h2", "h3", "h4", "li", "br", "tr"}:
            self._parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
        if self._skip_depth == 0:
            self._parts.append(data)

    @property
    def title(self) -> str:
        return "".join(self._title_parts).strip()

    @property
    def text(self) -> str:
        raw = "".join(self._parts)
        # Colapsa espaços/linhas em excesso, preserva parágrafos.
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n\s*\n+", "\n\n", raw)
        return raw.strip()


def html_to_text(html: str) -> tuple[str, str]:
    """Retorna (texto, título) a partir de uma string XHTML."""
    parser = _TextExtractor()
    parser.feed(html)
    return parser.text, parser.title


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EPUB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _iter_epub_html(epub_path: Path) -> Iterator[tuple[str, str]]:
    """Yield (nome_interno, html) para cada item XHTML/HTML do epub, em ordem."""
    with zipfile.ZipFile(epub_path) as zf:
        names = [
            n for n in sorted(zf.namelist())
            if n.lower().endswith((".xhtml", ".html", ".htm"))
            and not n.startswith("META-INF")
        ]
        for name in names:
            try:
                yield name, zf.read(name).decode("utf-8", errors="ignore")
            except KeyError:
                continue


def extract_epub(epub_path: Path, rel_source: str) -> list[SourceBlock]:
    """Extrai blocos de texto de um .epub, um por documento interno."""
    blocks: list[SourceBlock] = []
    for order, (inner_name, html) in enumerate(_iter_epub_html(epub_path)):
        text, title = html_to_text(html)
        if len(text) < 40:  # ignora páginas de capa/navegação vazias
            continue
        blocks.append(
            SourceBlock(
                text=text,
                source=f"{rel_source}::{inner_name}",
                doc_id=inner_name,
                title=title or epub_path.stem,
                order=order,
                kind="book",
            )
        )
    return blocks


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MARKDOWN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


_MD_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def extract_markdown(md_path: Path, rel_source: str) -> list[SourceBlock]:
    """
    Extrai blocos de um .md dividindo por cabeçalhos (seções).

    Cada seção vira um bloco com title = texto do cabeçalho, preservando
    o corpo em Markdown cru (bom para exact-match posterior).
    """
    raw = md_path.read_text(encoding="utf-8", errors="ignore")
    lines = raw.splitlines()

    blocks: list[SourceBlock] = []
    current_title = md_path.stem
    current: list[str] = []
    order = 0

    def flush(title: str, body: list[str]) -> None:
        nonlocal order
        text = "\n".join(body).strip()
        if len(text) >= 40:
            blocks.append(
                SourceBlock(
                    text=text,
                    source=f"{rel_source}#{_slug(title)}",
                    doc_id=_slug(title),
                    title=title,
                    order=order,
                    kind="docs",
                )
            )
            order += 1

    for line in lines:
        m = _MD_HEADING.match(line)
        if m:
            flush(current_title, current)
            current_title = m.group(2).strip()
            current = [line]
        else:
            current.append(line)

    flush(current_title, current)
    return blocks


def _slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DRIVER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def extract_all(root: Path) -> list[SourceBlock]:
    """
    Percorre `root` recursivamente e extrai de todos os .epub e .md.

    Args:
        root: diretório base (ex.: docs/applied-ai-agents).

    Returns:
        Lista de SourceBlock com caminhos relativos ao root.
    """
    root = root.resolve()
    all_blocks: list[SourceBlock] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = str(path.relative_to(root.parent))  # relativo a docs/
        if path.suffix.lower() == ".epub":
            all_blocks.extend(extract_epub(path, rel))
        elif path.suffix.lower() in {".md", ".markdown"}:
            all_blocks.extend(extract_markdown(path, rel))

    return all_blocks


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Extrai texto das fontes do corpus.")
    ap.add_argument(
        "--root",
        default="docs/applied-ai-agents",
        help="Diretório base dos livros/documentos.",
    )
    ap.add_argument("--limit", type=int, default=5, help="Mostra N blocos de amostra.")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        raise SystemExit(f"Root não encontrado: {root}")

    blocks = extract_all(root)
    print(f"[extract] {len(blocks)} blocos extraídos de {root}")
    by_kind: dict[str, int] = {}
    for b in blocks:
        by_kind[b.kind] = by_kind.get(b.kind, 0) + 1
    print(f"[extract] por tipo: {by_kind}")
    for b in blocks[: args.limit]:
        preview = b.text[:120].replace("\n", " ")
        print(f"  - [{b.kind}] {b.source} :: {b.title!r} :: {preview}...")
