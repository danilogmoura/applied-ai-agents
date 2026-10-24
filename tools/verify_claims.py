"""
Verificação de afirmações do material didático contra o corpus indexado.

Objetivo anti-alucinação: percorrer os MATERIAL.md dos módulos, extrair as
afirmações CONCEITUAIS centrais (termos em negrito/`backtick`, siglas e frases
definidoras "X é/consiste/são Y") e conferir, para cada uma, se há SUPORTE no
corpus (os livros/documentos em docs/applied-ai-agents).

Importante — o que isto NÃO é:
    Não é um "detector de erro" definitivo. É uma RÉGUA DE PROCEDÊNCIA: aponta
    quais afirmações têm eco claro na fonte (SUPPORTED), quais são parciais
    (WEAK) e quais não encontram respaldo (UNSUPPORTED -> revisar). A decisão
    final de editar o material é humana.

Classificação por claim:
    SUPPORTED   : melhor similaridade >= --support-sim  E  overlap léxico alto
    WEAK        : similaridade média OU overlap baixo (parcial)
    UNSUPPORTED : abaixo de --reject-sim => possível alucinação / fora do escopo

Execução:
    python -m tools.verify_claims                       # todos os módulos
    python -m tools.verify_claims --module p2_rag       # só um módulo
    python -m tools.verify_claims --dry-run             # só extrai, SEM API
    python -m tools.verify_claims --limit 10            # primeiras N claims
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

from tools.query import search

DEFAULT_MODULES_DIR = Path("modules")

# ── limiares de decisão (ajustáveis por flag) ───────────────────────────────
# Busca CROSS-LINGUAL: material PT-BR vs fontes EN/ZH. A similaridade densa
# (Qwen multilíngue) é o sinal confiável; overlap léxico só CONFIRMA quando os
# idiomas coincidem (claim EN vs fonte EN). Por isso overlap é bônus, não gate.
SUPPORT_SIM = 0.55   # >= isso => SUPPORTED (suporte semântico forte)
REJECT_SIM = 0.42    # < isso => UNSUPPORTED (nenhum eco na fonte)
OVERLAP_GOOD = 0.34  # se atingido, marca suporte como "literal" (mesma língua)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXTRAÇÃO DE CLAIMS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# termo em **negrito** ou `backtick` (ignora markdown de link/tabela)
_BOLD = re.compile(r"\*\*([^*\n]{3,80})\*\*")
_CODE = re.compile(r"`([^`\n]{3,60})`")
# sigla/acrônimo: 2+ letras maiúsculas seguidas opcionalmente de dígitos (RAG, MCP, HNSW, CoT)
_ACRO = re.compile(r"\b([A-Z]{2,6}(?:[0-9]+[A-Z])?)\b")
# frase definidora: "X é/consiste em/são Y" — captura X (sujeito curto antes do verbo)
_DEF = re.compile(
    r"(?im)^\s*[-*]?\s*\**([A-Za-zÀ-ÿ0-9][^.\n|]{3,70}?)\**\s+"
    r"(?:é|são|consiste(?:em)?|refere-se a|significa|quer dizer)\s+(.+?)\s*[.;]\s*$"
)

# stopwords PT/EN para o overlap léxico (não contam como "conteúdo")
_STOP = set(
    """a o as os um uma de do da das dos em no na nos nas e ou que para com por
    ser é são sua seu suas isso isto esta este essa esse the of and to in for
    with on an is are this that it as at be we you they can will not""".split()
)

# Palavras de ênfase/instrução que aparecem em **negrito** mas NÃO são claims
# factuais sobre o domínio. Filtra ruído óbvio do modo imperativo/glossário.
_EMPHASIS = {
    "nota", "importante", "dica", "atencao", "aviso", "analogia", "obs",
    "explicar", "implementar", "compreender", "aplicar", "avaliar", "identificar",
    "caro", "lento", "ineficiente", "rapido", "barato", "simples", "complexo",
    "opcional", "avancado", "obrigatorio", "core", "sempre", "nunca", "pode",
    "precisa saber", "voce vai ver", "fluxo completo", "ingestao", "busca",
    "geracao", "treino", "vetores de numeros",
}


def _clean_markdown(text: str) -> str:
    """Remove marcação residual (**, `, >, |, #) e colapsa espaços."""
    text = re.sub(r"[`*_>#|]", " ", text)
    return re.sub(r"\s+", " ", text).strip(" .:;,-")


def _is_useful_phrase(norm: str) -> bool:
    """Heurística: a frase parece uma afirmação/conceito do domínio?"""
    low = norm.lower()
    if low in _EMPHASIS:
        return False
    words = [w for w in re.findall(r"[a-zà-ÿ0-9]+", low) if w not in _STOP]
    # precisa de >=2 tokens de conteúdo OU ser um termo técnico reconhecível
    if len(words) < 2 and len(norm) < 12:
        return False
    # descarta frases que são só verbos/instrução soltos
    if all(w in _EMPHASIS for w in words):
        return False
    return True


def _content_tokens(text: str) -> set[str]:
    """Tokens de conteúdo para overlap léxico.

    Captura palavras latinas (PT/EN) E caracteres CJK individuais — essencial
    porque parte do corpus está em chinês (Agent Skills橙皮书). Sem CJK, uma
    claim legítima suportada pelo livro ZH teria overlap 0 e seria rebaixada
    injustamente a WEAK/UNSUPPORTED.
    """
    latin = re.findall(r"[a-zà-ÿ0-9]+", text.lower())
    cjk = re.findall(r"[\u4e00-\u9fff\u3040-\u30ff]", text)  # ideogramas + kana
    toks = [t for t in latin if t not in _STOP and len(t) > 2]
    return set(toks) | set(cjk)


@dataclass
class Claim:
    text: str          # a afirmação candidata (limpa)
    kind: str          # "bold" | "code" | "acronym" | "definition"
    line: int          # linha aproximada no arquivo (procedência)


def extract_claims(md_text: str, max_per_kind: int = 40) -> list[Claim]:
    """Extrai claims verificáveis do texto Markdown, deduplicadas e limitadas."""
    found: dict[str, Claim] = {}  # chave por texto normalizado -> evita duplicatas

    # Remove blocos de código / mermaid / json — não são prosa factual.
    md_text = re.sub(r"```.*?```", "", md_text, flags=re.DOTALL)

    def add(text: str, kind: str, line: int) -> None:
        norm = _clean_markdown(text).strip(" .:;,-")
        if len(norm) < 4:
            return
        # claims de negrito/código precisam "parecer" conceito do domínio
        if kind in ("bold", "code") and not _is_useful_phrase(norm):
            return
        key = norm.lower()
        if key not in found:
            found[key] = Claim(text=norm, kind=kind, line=line)

    lines = md_text.splitlines()
    counts = {"bold": 0, "code": 0, "acronym": 0, "definition": 0}

    # 1) definições explícitas primeiro (mais informativas)
    for ln, line in enumerate(lines, 1):
        m = _DEF.match(line)
        if m and counts["definition"] < max_per_kind:
            subject, predicate = m.group(1), m.group(2)
            add(f"{subject} é {predicate}".strip(), "definition", ln)
            counts["definition"] += 1

    # 2) termos em negrito
    for ln, line in enumerate(lines, 1):
        for g in _BOLD.findall(line):
            if counts["bold"] < max_per_kind and not g.startswith(("⚠", "💡", "📌", "🎯")):
                add(g, "bold", ln)
                counts["bold"] += 1

    # 3) siglas/acrônimos (contexto: a linha inteira vira a query)
    seen_acro: set[str] = set()
    for ln, line in enumerate(lines, 1):
        stripped = line.lstrip()
        if stripped.startswith("#"):  # títulos geram contexto poluído
            continue
        if "->" in line or "--" in line or "[" in line and "]" in line and "(" in line:
            continue  # diagramas mermaid / links de tabela
        for g in _ACRO.findall(line):
            if len(g) < 3 or g in seen_acro or counts["acronym"] >= max_per_kind:
                continue
            # descarta falsos positivos comuns em markdown/tabelas
            if g in {"MD", "PY", "ID", "OK", "TODO", "API", "HTTP", "JSON", "URL"}:
                continue
            # descarta palavras PT/EN em CAIXA ALTA que não são siglas (TODOS, APENAS)
            if g.isupper() and g.lower() in _EMPHASIS:
                continue
            if g in {"TODOS", "APENAS", "IMPORTANTE", "AVISO", "ERRO", "SUCESSO"}:
                continue
            seen_acro.add(g)
            ctx = _clean_markdown(line)[:90].strip()
            add(f"{g} {ctx}" if ctx else g, "acronym", ln)
            counts["acronym"] += 1

    # 4) identificadores em backtick que parecem conceito (não código/erro)
    for ln, line in enumerate(lines, 1):
        if "Error" in line or "error" in line or "pip install" in line or "$ " in line:
            continue  # troubleshooting / comandos, não claim conceitual
        for g in _CODE.findall(line):
            if counts["code"] >= max_per_kind:
                break
            if "(" in g or ")" in g or "." in g or "/" in g or "=" in g or ":" in g:
                continue  # é código/API/comando, não conceito verificável em livro
            words = [w for w in re.findall(r"[A-Za-zÀ-ÿ]{3,}", g)]
            if len(g.split()) > 3 or not words:
                continue  # muito longo ou sem conteúdo → provavelmente ruído
            add(g, "code", ln)
            counts["code"] += 1

    return list(found.values())


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERIFICAÇÃO CONTRA O ÍNDICE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


@dataclass
class Verdict:
    claim: Claim
    status: str                 # SUPPORTED | WEAK | UNSUPPORTED
    best_sim: float
    overlap: float
    literal: bool               # overlap alto => citação na mesma língua da fonte
    source: str
    quote: str


def verify_claim(claim: Claim, k: int, support_sim: float, reject_sim: float,
                 overlap_good: float) -> Verdict:
    results = search(claim.text, k=k)
    if not results:
        return Verdict(claim, "UNSUPPORTED", 0.0, 0.0, False, "", "")

    ctoks = _content_tokens(claim.text)
    best = results[0]
    best_sim = best["similarity"]

    # melhor overlap entre os top-k (chunk que mais cobre os tokens da claim)
    best_overlap = 0.0
    best_chunk = best
    for r in results:
        if not ctoks:
            break
        ktoks = _content_tokens(r["text"])
        ov = len(ctoks & ktoks) / len(ctoks)
        if ov > best_overlap:
            best_overlap = ov
            best_chunk = r

    # Critério principal = similaridade densa (cruza PT->EN/ZH).
    # Overlap alto apenas PROMOVE a um suporte "literal" (mesma língua);
    # overlap baixo NÃO rebaixa, pois é esperado entre idiomas diferentes.
    literal = best_overlap >= overlap_good
    if best_sim >= support_sim:
        status = "SUPPORTED"
    elif best_sim >= reject_sim:
        status = "WEAK"
    else:
        status = "UNSUPPORTED"

    quote = best_chunk["text"][:160].replace("\n", " ").strip()
    return Verdict(claim, status, round(best_sim, 3), round(best_overlap, 3),
                   literal, best_chunk["source"], quote)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


def _iter_modules(modules_dir: Path, only: str | None) -> list[Path]:
    mats = sorted(modules_dir.glob("*/MATERIAL.md"))
    if only:
        mats = [m for m in mats if m.parent.name == only]
    return mats


def main() -> None:
    ap = argparse.ArgumentParser(description="Verifica claims do MATERIAL.md contra o corpus.")
    ap.add_argument("--modules-dir", type=Path, default=DEFAULT_MODULES_DIR)
    ap.add_argument("--module", help="nome da pasta, ex.: p2_rag (default: todos)")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--limit", type=int, help="máx. de claims por módulo")
    ap.add_argument("--support-sim", type=float, default=SUPPORT_SIM)
    ap.add_argument("--reject-sim", type=float, default=REJECT_SIM)
    ap.add_argument("--overlap-good", type=float, default=OVERLAP_GOOD)
    ap.add_argument("--dry-run", action="store_true", help="só extrai claims, SEM chamar API")
    args = ap.parse_args()

    modules = _iter_modules(args.modules_dir, args.module)
    if not modules:
        raise SystemExit(f"Nenhum MATERIAL.md encontrado em {args.modules_dir}.")

    grand = {"SUPPORTED": 0, "WEAK": 0, "UNSUPPORTED": 0}

    for mat in modules:
        text = mat.read_text(encoding="utf-8", errors="ignore")
        claims = extract_claims(text)
        if args.limit:
            claims = claims[: args.limit]

        print(f"\n{'='*70}\n📘 {mat.parent.name}  ({len(claims)} claims extraídas)\n{'='*70}")

        if args.dry_run:
            for c in claims:
                print(f"  [{c.kind:>10}] L{c.line:<4} {c.text[:80]}")
            continue

        tally = {"SUPPORTED": 0, "WEAK": 0, "UNSUPPORTED": 0}
        for c in claims:
            v = verify_claim(c, args.k, args.support_sim, args.reject_sim, args.overlap_good)
            tally[v.status] += 1
            grand[v.status] += 1
            icon = {"SUPPORTED": "✅", "WEAK": "🟡", "UNSUPPORTED": "❌"}[v.status]
            lit = " LIT" if v.literal else ""  # suporte literal (mesma língua)
            print(f"{icon} [{v.status:>11}]{lit:<4} sim={v.best_sim:.2f} ov={v.overlap:.2f} "
                  f"({c.kind}) {c.text[:60]}")
            if v.status != "SUPPORTED":
                print(f"      ↳ fonte: {v.source}")
                print(f"        quote: {v.quote!r}")

        tot = sum(tally.values())
        pct = tally["SUPPORTED"] / tot * 100 if tot else 0
        print(f"  → {mat.parent.name}: ✅{tally['SUPPORTED']} 🟡{tally['WEAK']} "
              f"❌{tally['UNSUPPORTED']}  ({pct:.0f}% suportadas)")

    if not args.dry_run:
        gtot = sum(grand.values())
        print(f"\n{'='*70}\n🧮 TOTAL: {gtot} claims · ✅{grand['SUPPORTED']} "
              f"🟡{grand['WEAK']} ❌{grand['UNSUPPORTED']}"
              f"  ({grand['SUPPORTED']/gtot*100:.0f}% com suporte forte)\n{'='*70}")
        if grand["UNSUPPORTED"]:
            print("Ações sugeridas: revisar as ❌ (podem estar fora do escopo dos livros "
                  "ou mal formuladas) e validar as 🟡 manualmente.")


if __name__ == "__main__":
    main()
