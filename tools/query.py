"""
Consulta o índice vetorial e devolve chunks com procedência + trechos literais.

É a peça anti-alucinação: cada resultado traz `source` (path::arquivo ou
path#secao) e o texto cru do chunk, para que uma afirmação possa ser
conferida por exact-match contra a fonte — sem reenviar o livro ao LLM.

Execução:
    python -m tools.query "planejamento resiliente de agentes"
    python -m tools.query --k 8 --kind book "context engineering"
    python -m tools.query --verify "trecho literal esperado"   # busca no índice
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.build_index import DEFAULT_INDEX_DIR, ChromaStore

# Threshold de distância cosine (espaço "cosine" do Chroma = 1 - similaridade).
# Acima disso => não há suporte na fonte => sinal de "não sei".
DEFAULT_MAX_DISTANCE = 0.55


def search(
    query_text: str,
    k: int = 5,
    index_dir: Path = DEFAULT_INDEX_DIR,
    kind: str | None = None,
    max_distance: float = DEFAULT_MAX_DISTANCE,
) -> list[dict]:
    from tools.embed import QwenEmbedder

    qvec = QwenEmbedder().embed_one(query_text)
    store = ChromaStore(index_dir)

    where = {"kind": kind} if kind else None
    res = store.collection.query(
        query_embeddings=[qvec],
        n_results=k,
        where=where,
        include=["documents", "metadatas", "distances"],
    )

    out: list[dict] = []
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    dists = res["distances"][0]
    for text, meta, dist in zip(docs, metas, dists):
        sim = 1.0 - dist
        out.append(
            {
                "source": meta.get("source"),
                "title": meta.get("title"),
                "kind": meta.get("kind"),
                "distance": round(dist, 4),
                "similarity": round(sim, 4),
                "supported": dist <= max_distance,
                "text": text,
            }
        )
    return out


def verify_literal(needle: str, index_dir: Path = DEFAULT_INDEX_DIR) -> bool:
    """
    Confirma se um trecho EXISTE byte-a-byte em algum chunk do índice.

    Uso: depois que o modelo cita algo, passe a citação aqui. Se False,
    a citação é fabricada (alucinação) — o texto não está na fonte.
    """
    store = ChromaStore(index_dir)
    got = store.collection.get(include=["documents"])
    for doc in got["documents"]:
        if needle in doc:
            return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Busca/verifica no índice do corpus.")
    ap.add_argument("query", nargs="?", help="Pergunta ou termo de busca.")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    ap.add_argument("--kind", choices=["book", "docs"], default=None)
    ap.add_argument("--max-distance", type=float, default=DEFAULT_MAX_DISTANCE)
    ap.add_argument(
        "--verify",
        metavar="TRECHO",
        help="Confirma exact-match de um trecho literal no índice.",
    )
    args = ap.parse_args()

    if not args.index_dir.exists():
        raise SystemExit(
            f"Índice não encontrado em {args.index_dir}. "
            "Rode primeiro: python -m tools.build_index"
        )

    if args.verify:
        ok = verify_literal(args.verify, args.index_dir)
        print(f"[verify] trecho {'ENCONTRADO na fonte' if ok else 'NAO ENCONTRADO (possível alucinação)'}")
        raise SystemExit(0 if ok else 1)

    if not args.query:
        raise SystemExit("Forneça uma query ou use --verify.")

    results = search(
        args.query,
        k=args.k,
        index_dir=args.index_dir,
        kind=args.kind,
        max_distance=args.max_distance,
    )
    print(f"[query ] {args.query!r}\n")
    for r in results:
        flag = "OK " if r["supported"] else "???"
        print(f"[{flag}] sim={r['similarity']:.3f} dist={r['distance']:.3f} "
              f"[{r['kind']}] {r['source']}")
        print(f"       {r['title']!r}")
        snippet = r["text"][:200].replace("\n", " ")
        print(f"       > {snippet}...\n")

    supported = sum(1 for r in results if r["supported"])
    if supported == 0:
        print("[aviso] nenhum chunk acima do threshold => responder 'NÃO SEI', "
              "não inventar.")


if __name__ == "__main__":
    main()
