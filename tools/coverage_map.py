"""
Modo A do plano docs/enriquecer_materiais_rag_plan.md — Mapa de cobertura.

Para cada módulo, lê os conceitos (tabela `## 📖 Glossário` + headings `###`) e,
para cada um, consulta o índice vetorial (tools.query.search) para encontrar as
fontes que dão suporte. Escreve `modules/<m>/SOURCES.md`.

NÃO gera prosa e NÃO toca no MATERIAL.md — é só um ponteiro verificável para a
fonte. O quote exibido vem cru do chunk (nunca traduzido); marcamos [EN]/[ZH].

Execução:
    python -m tools.coverage_map                       # todos os módulos
    python -m tools.coverage_map --module 04-rag       # um só
    python -m tools.coverage_map --dry-run             # extrai conceitos, SEM API
    python -m tools.coverage_map --k 3 --min-sim 0.50
"""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from tools.build_index import DEFAULT_INDEX_DIR
from tools.embed import QWEN_API_BASE, resolve_model  # base MaaS + modelo de embed
from tools.query import search

MODULES_DIR = Path(__file__).resolve().parent.parent / "modules"

# Modelo de chat (barato) usado SÓ para a "ponte de tradução": quando um termo PT
# fica órfão, pedimos equivalentes EN/ZH e re-buscamos. Override via env CHAT_MODEL.
CHAT_MODEL = os.getenv("COVERAGE_CHAT_MODEL", "qwen3.7-flash")
_chat_client = None


def _get_chat_client():
    """Client OpenAI-compatível apontado no MaaS da Qwen (inicialização preguiçosa)."""
    global _chat_client
    if _chat_client is None:
        from openai import OpenAI

        from shared.security import get_required_secret

        _chat_client = OpenAI(
            api_key=get_required_secret("QWEN_MAAS_API_KEY"), base_url=QWEN_API_BASE
        )
    return _chat_client


def translate_term(term: str, descriptor: str) -> list[str]:
    """
    Devolve equivalentos EN (e, se aplicável, ZH) de um conceito PT-BR, para
    re-busca cross-lingual. Retorna [] em qualquer falha (nunca interrompe o mapa).
    """
    ctx = f" Contexto: {descriptor}" if descriptor else ""
    prompt = (
        "Responda APENAS com termos técnicos, uma linha cada, sem numeração nem explicação.\n"
        "Use o TERMO TÉCNICO CANÔNICO do domínio de IA/engenharia de software em inglês — "
        "NÃO uma tradução literal. Exemplos de correção de viés de tradução:\n"
        "  'Whitelist' → 'allowlist' (não 'white list'); 'Blacklist' → 'denylist';\n"
        "  'Memorando técnico' → 'decision memo' / 'architecture decision record' (não 'memorandum');\n"
        "  'Ponto de equilíbrio' → 'break-even point'; 'Causa raiz' → 'root cause'.\n"
        "Dê o equivalente canônico em INGLÊS e, se houver termo consolidado, em CHINÊS (simplificado) "
        f"deste conceito de IA:{ctx}\nConceito: {term}"
    )
    try:
        resp = _get_chat_client().chat.completions.create(
            model=CHAT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60,
            temperature=0.0,
        )
        out = (resp.choices[0].message.content or "").strip()
    except Exception:
        return []
    terms: list[str] = []
    for line in out.splitlines():
        cand = line.strip(" -•*:\t")
        if cand and len(cand) <= 48 and not re.search(r"[?？]", cand):
            terms.append(cand)
    return terms[:4]

# Conceitos com menos destes caracteres úteis são ruído de heading ("Por que ...?").
_MIN_TERM_LEN = 4

# Prefixos numéricos de heading ("1. ", "2.3 ") e emojis/símbolos decorativos.
_NUM_PREFIX = re.compile(r"^\d+(?:\.\d+)*[\).\]]?\s+")
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\u2190-\u21FF\u2600-\u27BF\uFE0F\u2B00-\u2BFF]"
)

# Palavras de estrutura/navegação que nunca são conceitos técnicos pesquisáveis.
# Usadas como primeira-palavra OU termo exato curto.
_NOISE_WORDS = {
    "core", "prático", "pratico", "avançado", "avancado", "opcional", "obrigatório",
    "objetivos", "sumário", "sumario", "pré-requisito", "pre-requisito", "introdução",
    "introducao", "conclusão", "conclusao", "visão geral", "visao geral", "resumo",
    "referências", "referencias", "nota", "dica", "importante",
    # rótulos estruturais / meta do curso (não são termos-busca)
    "parte", "pergunta", "analogia", "documentação", "documentacao", "tutoriais",
    "tutorial", "fluxo", "como", "por", "quando", "onde", "próximos", "proximos",
    "exercício", "exercicio", "atividade", "entrega", "checklist", "faq", "índice",
    "indice", "agradecimentos", "prefácio", "prefacio", "epílogo", "epilogo",
}

# Prefixos de heading que indicam rótulo estrutural mesmo com continuação:
# "Parte A", "Pergunta 2", "Analogia simples", "Fluxo simplificado", etc.
_NOISE_PREFIX = re.compile(
    r"^(?:parte|pergunta|analogia|documenta(?:ç|c)[ãa]o of|tutoriais? on|"
    r"fluxo |como funciona|por que|pr[óo]ximos passos|exerc[íi]cio|atividade)\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Extração de conceitos do MATERIAL.md
# ---------------------------------------------------------------------------

def _clean_term(raw: str) -> str:
    """Remove markdown ênfase/âncoras/emoji/prefixo numérico de um termo."""
    t = raw.strip()
    t = re.sub(r"^#+\s*", "", t)            # leading # de heading
    t = _EMOJI.sub("", t)                   # emoji/símbolo decorativo
    t = _NUM_PREFIX.sub("", t)              # "1. " / "2.3 "
    t = re.sub(r"\*\*|\*|`", "", t)         # bold/italic/code
    t = re.sub(r"\s*[—–]\s.*$", "", t)      # corta após travessão explicativo
    t = re.sub(r"\((?:opcional|obrigat[áa]rio)\)", "", t, flags=re.IGNORECASE)
    t = re.sub(r"\s+", " ", t).strip(" .:;,·-")
    return t


def _is_noise(term: str) -> bool:
    """Heurística anti-ruído para headings que não são conceitos."""
    low = term.lower().strip()
    if not low:
        return True
    if low in _NOISE_WORDS:
        return True
    # perguntas soltas ("... ?") — o corpo da pergunta não é um termo-busca bom
    if low.endswith("?"):
        return True
    # rótulo estrutural com continuação: "Parte A", "Pergunta 2", "Analogia simples"
    if _NOISE_PREFIX.match(low):
        return True
    # rótulos de bloco tipo "Conhecimento técnico necessário antes de P2"
    first = low.split()[0]
    if first in _NOISE_WORDS:
        return True
    return False


def _first_prose(body: list[str], max_chars: int = 240) -> str:
    """
    Primeira frase 'de conteúdo' de um corpo de seção: pula código cercado,
    tabelas, blockquotes, listas e linhas vazias. Serve de descritor para
    re-buscar um termo órfão quando só o título não rende similaridade.
    """
    in_fence = False
    for raw in body:
        ln = raw.strip()
        if ln.startswith("```") or ln.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not ln or ln[0] in ">|#|-*+" or re.match(r"^\d+[.)]\s", ln) or ln.startswith("["):
            continue
        text = re.sub(r"\*\*|\*|`", "", ln)
        text = re.sub(r"\[(.*?)\]\([^)]*\)", r"\1", text)  # link -> texto âncora
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) < 20:
            continue
        return text[:max_chars]
    return ""


def extract_concepts(md_text: str) -> dict[str, str]:
    """
    Extrai conceitos do MATERIAL.md e devolve {termo_exibição: descritor_da_seção}.

    - Termos do Glossário (1ª coluna de tabelas `| **Termo** | ...`) entram com
      descritor vazio (a própria linha da tabela já os contextualiza na busca).
    - Headings `###` capturam o corpo até o próximo heading; o descritor é a
      primeira frase de prosa dessa seção (fallback p/ re-busca cross-lingual).
    De-duplica por termo (lowercase), preservando a ordem de aparição.
    """
    ordered: dict[str, str] = {}   # chave = lowercase; valor = (display, descriptor)
    entries: list[tuple[str, str]] = []  # [(display, descriptor)] na ordem
    seen: set[str] = set()

    def add(term: str, descriptor: str = "") -> None:
        term = _clean_term(term)
        if len(term) < _MIN_TERM_LEN:
            return
        if not re.search(r"[A-Za-zÀ-ÿ\u4e00-\u9fff]", term):
            return
        if _is_noise(term):
            return
        key = term.lower()
        if key in seen:
            return
        seen.add(key)
        entries.append((term, descriptor))

    lines = md_text.splitlines()
    in_glossary = False
    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()

        # detecta entrada/saída da seção de glossário
        if re.match(r"^#{1,3}\s*.*Gloss[áa]rio", stripped, re.IGNORECASE):
            in_glossary = True
            i += 1
            continue
        if in_glossary and stripped.startswith("#"):
            in_glossary = False

        # linha de tabela do glossário: | **Termo** | definição | analogia |
        if in_glossary and stripped.startswith("|"):
            cells = [c for c in stripped.strip("|").split("|")]
            if len(cells) >= 2 and "**" in cells[0]:
                add(cells[0])
            i += 1
            continue

        # heading ### : coleta o corpo até o próximo heading e extrai descritor
        m = re.match(r"^###\s+(.*)$", stripped)
        if m:
            title = m.group(1)
            body: list[str] = []
            j = i + 1
            while j < n and not re.match(r"^#{1,6}\s", lines[j].strip()):
                body.append(lines[j])
                j += 1
            add(title, _first_prose(body))
            i += 1
            continue

        i += 1

    for display, descriptor in entries:
        ordered[display] = descriptor
    return ordered


# ---------------------------------------------------------------------------
# Formatação de fonte + idioma
# ---------------------------------------------------------------------------

def detect_lang(text: str) -> str:
    """[ZH] se houver ideograma CJK; senão [EN] (corpus é EN/ZH)."""
    return "[ZH]" if re.search(r"[\u4e00-\u9fff]", text) else "[EN]"


def format_source(meta_source: str, title: str) -> str:
    """
    'applied-ai-agents/<Livro> -- Autor -- Ano -- ...::doc_id' ->
        '<Livro> · Autor · Ano · doc_id'
    Para docs (kind!=book), o `title` é um heading markdown inteiro -> usamos só
    o doc_id legível. Prioriza os segmentos '--' do path (título real do livro),
    não o metadado `title` (que pode ser só um número de capítulo).
    """
    file_part, _, locator = meta_source.partition("::")
    # remove prefixo de diretório e extensão
    base = file_part.split("/", 1)[-1] if "/" in file_part else file_part
    segs = [s.strip() for s in base.split("--")]
    name = segs[0].strip() if segs else base
    # docs (sem blocos '--' de livro): usa o heading limpo como rótulo legível
    if "--" not in base and title:
        heading = _clean_heading(title)
        path = base.split("#", 1)[0]
        return f"{heading} · `{path}`" if heading else path
    # autor = primeiro seg com letras que não é ano/hash/Anna's/isbn
    author = ""
    year = ""
    for s in segs[1:]:
        if re.fullmatch(r"\d{4}", s):
            year = year or s
        elif re.search(r"[A-Za-z]", s) and not re.search(
            r"Anna|isbn|Archive|[0-9a-f]{16,}", s, re.IGNORECASE
        ):
            author = author or s
    # título curto: corta subtítulo após ':' ou '_' para caber numa linha
    name = re.split(r"[:_]", name, maxsplit=1)[0].strip()[:50]
    bits = [b for b in (name, author, year) if b]
    label = " · ".join(bits) if bits else (title or name)[:50]
    if locator:
        loc = locator.replace(".xhtml", "").replace(".html", "").replace(".md", "")
        label += f" · {loc}"
    return label


# Ruído de citação: rodapé de spam do livro ZH, âncoras/links markdown vazios.
_BOILERPLATE = re.compile(
    r"telegram|t\.me|未经授权|禁止转载|获取更多电子书|EPUB_\d+|\{ *#[a-z0-9-]+ *\}|"
    r"\{\*.*\*\}|https?://",
    re.IGNORECASE,
)


def _strip_spam(text: str) -> str:
    """Remove o bloco de spam do livro ZH (links Telegram + copyright repetidos)."""
    t = text
    # corta tudo a partir do primeiro marcador de spam de rodapé
    for marker in ("[https://t.me", "© 未经授权", "获取更多电子书", "| ID："):
        idx = t.find(marker)
        if idx != -1:
            t = t[:idx]
    return _BOILERPLATE.sub(" ", t)


def _clean_heading(title: str) -> str:
    """Heading markdown de docs -> texto legível (remove {#anchor}, backticks)."""
    h = re.sub(r"\{[^}]*\}", "", title)      # { #anchor } / {* ... *}
    h = _EMOJI.sub("", h)
    h = re.sub(r"[`*]", "", h)
    h = re.sub(r"^#+\s*", "", h.strip())
    h = re.sub(r"\s+", " ", h).strip()
    return h[:80]


def _quote_is_noise(text: str) -> bool:
    """True se o trecho é só boilerplate/spam/âncora sem conteúdo útil."""
    body = _strip_spam(text)
    body = re.sub(r"[#>*\-\[\](){}`|:\s]+", " ", body)
    substantive = re.findall(r"[A-Za-zÀ-ÿ\u4e00-\u9fff]{3,}", body)
    return len(substantive) < 4


def _snippet(text: str, limit: int = 220) -> str:
    """Remove spam/boilerplate, colhe na borda de palavra, sem cortar token."""
    t = _strip_spam(text)
    t = re.sub(r"^#+\s*", "", t.strip())          # leading # de heading md
    t = re.sub(r"\s+", " ", t).strip(" .:;,·->*# ")
    if len(t) <= limit:
        return t
    cut = t[:limit]
    space = cut.rfind(" ")
    return (cut[:space] if space > 40 else cut) + "…"


# ---------------------------------------------------------------------------
# Renderização do SOURCES.md
# ---------------------------------------------------------------------------

def _search_with_fallback(
    term: str, descriptor: str, k: int, index_dir: Path, min_sim: float
) -> list[dict]:
    """
    Busca o termo; se nada passar do limiar (ou só vier ruído), re-busca usando
    `termo + descritor da seção` — a frase de contexto costuma cruzar melhor o
    parágrafo EN/ZH quando o título PT sozinho é vago demais.
    """
    hits = search(term, k=k, index_dir=index_dir)
    usable = [h for h in hits if h["similarity"] >= min_sim and not _quote_is_noise(h["text"])]
    if usable:
        return hits
    # 1) fallback com o descritor da seção (custo zero, só embedding)
    if descriptor:
        retry = search(f"{term}. {descriptor}", k=k, index_dir=index_dir)
        retry_usable = [h for h in retry if h["similarity"] >= min_sim and not _quote_is_noise(h["text"])]
        if retry_usable:
            return retry_usable
    # 2) ponte de tradução: pede equivalentes EN/ZH ao chat e re-busca. Marca os
    #    hits como bridge p/ o SOURCES.md rotular (citação ainda vem crua da fonte).
    for eq in translate_term(term, descriptor):
        bridge = search(eq, k=k, index_dir=index_dir)
        bridge_usable = [h for h in bridge if h["similarity"] >= min_sim and not _quote_is_noise(h["text"])]
        if bridge_usable:
            for h in bridge_usable:
                h["_bridge"] = eq
            return bridge_usable
    return hits


def build_module_md(module: str, items: list[tuple[str, list[dict]]], min_sim: float) -> tuple[str, int, int]:
    """Retorna (markdown, n_con_achados, n_sem_cobertura). items=[(termo, hits)]."""
    covered = 0
    uncovered = 0
    lines: list[str] = [
        f"# 🗺️ Mapa de Cobertura — {module}",
        "",
        "> Gerado por `tools/coverage_map.py` (modo A). Ponteiros verificáveis para as",
        "> fontes do corpus — **não** é texto autoral nem tradução. Quotes vêm crus da fonte.",
        "",
        f"_Conceitos analisados: {len(items)} · limiar sim ≥ {min_sim:.2f}_",
        "",
    ]
    for term, hits in items:
        good = [h for h in hits if h["similarity"] >= min_sim and not _quote_is_noise(h["text"])]
        lines.append(f"## {term}")
        if not good:
            uncovered += 1
            best = max((h["similarity"] for h in hits), default=0.0)
            lines.append(f"- ⚪ **Sem cobertura clara nas fontes** (melhor sim={best:.2f}).")
            lines.append("")
            continue
        covered += 1
        for h in good[:3]:
            lang = detect_lang(h["text"])
            src = format_source(h["source"], h.get("title", ""))
            bridge = f" · _ponte: “{h['_bridge']}”_" if h.get("_bridge") else ""
            lines.append(f"- ✅ sim={h['similarity']:.2f} {lang}{bridge} — `{src}`")
            lines.append(f"  > {_snippet(h['text'])}")
        lines.append("")

    summary = (
        f"**Resumo:** {covered}/{len(items)} conceitos com suporte "
        f"({uncovered} sem cobertura).\n"
    )
    body = "\n".join(lines)
    return body + "\n\n---\n\n" + summary, covered, uncovered


# ---------------------------------------------------------------------------
# Orquestração
# ---------------------------------------------------------------------------

def process_module(module_dir: Path, k: int, index_dir: Path, min_sim: float, dry_run: bool) -> None:
    material = module_dir / "MATERIAL.md"
    if not material.exists():
        print(f"[skip] {module_dir.name}: sem MATERIAL.md")
        return
    concepts = extract_concepts(material.read_text(encoding="utf-8"))
    print(f"[{module_dir.name}] {len(concepts)} conceitos extraídos")

    if dry_run:
        for term, desc in concepts.items():
            mark = "  ↳desc" if desc else ""
            print("   ·", term, mark)
        return

    items = [
        (term, _search_with_fallback(term, desc, k, index_dir, min_sim))
        for term, desc in concepts.items()
    ]
    md, covered, uncovered = build_module_md(module_dir.name, items, min_sim)
    out = module_dir / "SOURCES.md"
    out.write_text(md, encoding="utf-8")
    pct = round(100 * covered / len(concepts)) if concepts else 0
    print(f"   → {out.relative_to(MODULES_DIR.parent)}  ✅{covered} ⚪{uncovered} ({pct}% cobertos)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Mapa de cobertura RAG (modo A).")
    ap.add_argument("--module", help="Nome de um módulo (ex: 04-rag). Senão, todos.")
    ap.add_argument("--k", type=int, default=3, help="Resultados por conceito.")
    ap.add_argument("--min-sim", type=float, default=0.50, help="Similaridade mínima p/ contar como cobertura.")
    ap.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    ap.add_argument("--dry-run", action="store_true", help="Só extrai conceitos, SEM chamar a API.")
    args = ap.parse_args()

    if not args.dry_run and not args.index_dir.exists():
        raise SystemExit(
            f"Índice não encontrado em {args.index_dir}. "
            "Rode primeiro: ./setup_corpus_index.sh  (ou python -m tools.build_index)"
        )

    if args.module:
        dirs = [MODULES_DIR / args.module]
    else:
        dirs = sorted(d for d in MODULES_DIR.iterdir() if (d / "MATERIAL.md").exists())

    total_cov = total_unc = 0
    for d in dirs:
        if not d.exists():
            print(f"[erro] módulo não existe: {d}")
            continue
        if args.dry_run:
            process_module(d, args.k, args.index_dir, args.min_sim, True)
        else:
            material = d / "MATERIAL.md"
            if not material.exists():
                continue
            concepts = extract_concepts(material.read_text(encoding="utf-8"))
            items = [
                (t, _search_with_fallback(t, d, args.k, args.index_dir, args.min_sim))
                for t, d in concepts.items()
            ]
            md, cov, unc = build_module_md(d.name, items, args.min_sim)
            (d / "SOURCES.md").write_text(md, encoding="utf-8")
            total_cov += cov
            total_unc += unc
            pct = round(100 * cov / len(concepts)) if concepts else 0
            print(f"[{d.name}] ✅{cov} ⚪{unc} ({pct}%) → modules/{d.name}/SOURCES.md")

    if not args.dry_run:
        tot = total_cov + total_unc
        pct = round(100 * total_cov / tot) if tot else 0
        print(f"\n🧮 TOTAL: {tot} conceitos · ✅{total_cov} ⚪{total_unc} ({pct}% cobertos)")


if __name__ == "__main__":
    main()
