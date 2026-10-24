"""
Mini-eval de recall da busca DENSE atual.

Para cada (query, termo-alvo), embedda a query, pega top-k denso e verifica
se ALGUM chunk retornado contém o termo-alvo (case-insensitive). Mede
recall@k sem precisar de ground-truth manual por parágrafo.

Objetivo: decidir se vale adicionar BM25+RRF (híbrido) ou se a densa basta.

Execução:
    python -m tools.eval_recall --k 5
"""

from __future__ import annotations

import argparse

from tools.query import search

# (query natural, termo que DEVE aparecer em algum chunk do top-k)
CASES: list[tuple[str, str]] = [
    # siglas / nomes exatos — onde densa costuma falhar
    ("what is the ReAct pattern for agents", "react"),
    ("how does HNSW index work for vector search", "hnsw"),
    ("tree of thought reasoning in agents", "tree of thought"),
    ("explaining chain of thought prompting", "chain of thought"),
    ("retrieval augmented generation pipeline", "retrieval augmented"),
    # termos técnicos pontuais
    ("cosine similarity distance metric", "cosine"),
    ("embedding model dimension vector", "embedding"),
    ("agent tool calling function schema", "tool"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    args = ap.parse_args()

    hit = 0
    print(f"[eval ] recall@{args.k} da busca DENSE (exact-match do termo no top-k)\n")
    for query, target in CASES:
        results = search(query, k=args.k)
        found_rank = None
        best_sim = 0.0
        for rank, r in enumerate(results, start=1):
            best_sim = max(best_sim, r["similarity"])
            if target in r["text"].lower():
                found_rank = rank
                break
        ok = found_rank is not None
        hit += ok
        mark = "✓" if ok else "✗"
        where = f"rank {found_rank}" if ok else "FORA do top-k"
        print(f"{mark} [{where:>13}] sim_max={best_sim:.3f}  '{target}' <- {query!r}")

    total = len(CASES)
    print(f"\n[recall@{args.k}] {hit}/{total} = {hit/total*100:.0f}%")
    if hit == total:
        print("=> densa acertou TODOS os casos difíceis. BM25+RRF NÃO compensa agora.")
    elif hit / total >= 0.75:
        print("=> densa boa; híbrido traria ganho marginal. Adiar.")
    else:
        print("=> densa perde casos de termo exato. Vale implementar BM25+RRF.")


if __name__ == "__main__":
    main()
