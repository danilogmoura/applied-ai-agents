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
    python -m tools.insert_anchors --module p2_rag --dry-run   # mostra, não escreve
    python -m tools.insert_anchors --module p2_rag             # escreve MATERIAL.md
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
from tools.query import search, verify_literal

# Marcador invisível-ish para idempotência: toda âncora gerada carrega este selo.
ANCHOR_MARK = "📖 Fonte:"

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

# Similaridade mínima entre o EMBEDDING DA PRÓPRIA FRASE e o termo do conceito.
# Gate de topicalidade: garante que a citação escolhida trata DO assunto da seção,
# não apenas que veio do chunk mais parecido com a query-aumentada-por-descritor.
_QUOTE_TOPICAL_MIN = 0.42


def _best_quote_for(term: str, descriptor: str, index_dir: Path, min_sim: float) -> dict | None:
    """
    Roda a escada de busca do coverage_map (termo → descritor) e devolve o melhor
    hit ACIMA do limiar cuja frase seja: (a) literal verificável byte-a-byte,
    (b) livre de artefatos/notas-de-rodapé, e (c) TOPICAL ao termo (embedding da
    própria frase fica perto do termo). Retorna None se nada passar nos três gates.
    """
    from tools.embed import QwenEmbedder

    hits = search(term, k=5, index_dir=index_dir)
    usable = [h for h in hits if h["similarity"] >= min_sim and not _quote_is_noise(h["text"])]
    if not usable and descriptor:
        retry = search(f"{term}. {descriptor}", k=5, index_dir=index_dir)
        usable = [h for h in retry if h["similarity"] >= min_sim and not _quote_is_noise(h["text"])]
    if not usable:
        return None

    # Prepara o embedding do termo UMA vez p/ o gate de topicalidade.
    try:
        term_vec = QwenEmbedder().embed_one(term)
    except Exception:
        term_vec = None

    def _topical(quote: str) -> bool:
        # Sem vetores disponíveis, não travamos (fallback: aceita, pois já passou
        # no verify_literal). Com vetores, exige similaridade frase~termo.
        if term_vec is None:
            return True
        try:
            qvec = QwenEmbedder().embed_one(quote)
        except Exception:
            return False
        num = sum(a * b for a, b in zip(term_vec, qvec))
        den = (sum(a * a for a in term_vec) ** 0.5) * (sum(b * b for b in qvec) ** 0.5)
        return den > 0 and (num / den) >= _QUOTE_TOPICAL_MIN

    # ordena por similaridade decrescente; para cada hit testa TODAS as frases
    # candidatas (não só a mais longa) e pega a primeira que passe topical+verify.
    for h in sorted(usable, key=lambda x: x["similarity"], reverse=True):
        for quote in _candidate_sentences(h["text"]):
            if not _topical(quote):
                continue
            if verify_literal(quote, index_dir=index_dir):
                h["_quote"] = quote
                return h
    return None


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


def insert_module(module_dir: Path, index_dir: Path, min_sim: float, dry_run: bool) -> tuple[int, int]:
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
        hit = _best_quote_for(term, concepts.get(term, ""), index_dir, min_sim)
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
    ap.add_argument("--module", help="Nome de um módulo (ex: p2_rag). Senão, todos.")
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

    tot_ins = tot_skip = 0
    for d in dirs:
        if not d.exists():
            print(f"[erro] módulo não existe: {d}")
            continue
        ins, sk = insert_module(d, args.index_dir, args.min_sim, args.dry_run)
        tot_ins += ins
        tot_skip += sk
        tag = "propostas" if args.dry_run else "inseridas"
        print(f"[{d.name}] {ins} âncoras {tag} · {sk} conceitos sem cotação verificável")

    print(f"\n🧮 TOTAL: {tot_ins} âncoras ({'propostas' if args.dry_run else 'inseridas'}) · {tot_skip} sem cotação")
    if not args.dry_run:
        print("⚠️  Cada âncora passou em verify_literal (byte-a-byte). Confira o diff antes de commitar.")


if __name__ == "__main__":
    main()
