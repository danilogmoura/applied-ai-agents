"""
Índice vetorial persistente (ChromaDB) + CLI de construção.

Fluxo:
    extract_all -> TokenChunker -> [cotação] -> QwenEmbedder -> ChromaStore.upsert

O índice fica em `.corpus_index/` (persistente, fora do controle de git).
Uma vez construído, consultas não chamam a API de embedding do livro inteiro —
só embeddam a query e buscam os top-k chunks. É isso que evita "carregar o
livro no LLM".

Execução:
    python -m tools.build_index --dry-run     # só cota tokens/custo, sem API
    python -m tools.build_index               # embedda e grava o índice
    python -m tools.build_index --rebuild     # apaga e reconstroi do zero
"""

from __future__ import annotations

import argparse
from pathlib import Path

from tools.chunk import TokenChunker
from tools.embed import estimate_embed_cost, resolve_model
from tools.extract import extract_all

DEFAULT_ROOT = Path("docs/applied-ai-agents")
DEFAULT_INDEX_DIR = Path(".corpus_index")
COLLECTION = "corpus"


def _estimate_total_tokens(chunks, chunker: TokenChunker) -> int:
    """Tokens totais a embeddar (inclui uma pequena sobra por metadados)."""
    total = 0
    for c in chunks:
        total += chunker._count(c.text) + 16  # folga p/ título/prefixo
    return total


class ChromaStore:
    """Encapsula o collection ChromaDB com upsert/query por metadados."""

    def __init__(self, persist_dir: Path, collection_name: str = COLLECTION) -> None:
        import chromadb

        persist_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(persist_dir))
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def count(self) -> int:
        return self.collection.count()

    def clear(self) -> None:
        import chromadb

        name = self.collection.name
        self.client.delete_collection(name)
        self.collection = self.client.get_or_create_collection(
            name=name, metadata={"hnsw:space": "cosine"}
        )

    def upsert(self, ids, embeddings, documents, metadatas) -> None:
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(self, embedding, k: int = 5):
        return self.collection.query(
            query_embeddings=[embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )


def build(
    root: Path = DEFAULT_ROOT,
    index_dir: Path = DEFAULT_INDEX_DIR,
    max_tokens: int = 400,
    overlap: int = 60,
    dry_run: bool = False,
    rebuild: bool = False,
    batch_report_every: int = 1024,
) -> None:
    chunker = TokenChunker(max_tokens=max_tokens, overlap_tokens=overlap)
    print(f"[extract] lendo fontes em {root} ...")
    blocks = extract_all(root)
    print(f"[extract] {len(blocks)} blocos")

    print("[chunk] fatiando ...")
    chunks = chunker.chunk_all(blocks)
    print(f"[chunk] {len(chunks)} chunks")

    total_tokens = _estimate_total_tokens(chunks, chunker)
    cost = estimate_embed_cost(total_tokens, len(chunks))
    print(f"[cost ] {cost}")

    if dry_run:
        print("[dry-run] nenhuma chamada à API foi feita. Índice NÃO gravado.")
        return

    from tools.embed import _BATCH_SIZE, QwenEmbedder

    embedder = QwenEmbedder(model=resolve_model())
    store = ChromaStore(index_dir)
    if rebuild and store.count():
        print("[index] --rebuild: limpando coleção existente")
        store.clear()

    print(f"[embed ] gerando vetores para {len(chunks)} chunks via {embedder.model} ...")
    step = _BATCH_SIZE
    done = 0
    for start in range(0, len(chunks), step):
        window = chunks[start : start + step]
        vectors = embedder.embed([c.text for c in window])
        store.upsert(
            ids=[c.id for c in window],
            embeddings=vectors,
            documents=[c.text for c in window],
            metadatas=[
                {
                    "source": c.source,
                    "doc_id": c.doc_id,
                    "title": c.title,
                    "kind": c.kind,
                    "order": c.order,
                    "chunk_index": c.chunk_index,
                    "n_chunks": c.n_chunks,
                }
                for c in window
            ],
        )
        done += len(window)
        if done % batch_report_every < step:
            print(f"[embed ]   {done}/{len(chunks)} chunks indexados")

    print(f"[index ] pronto: {store.count()} vetores em {index_dir}")


def smoke_check() -> None:
    """Embedda 2 textos reais e valida dimensionalidade contra o gateway Qwen."""
    from tools.embed import EMBED_DIMENSION, QwenEmbedder, resolve_model

    model = resolve_model()
    print(f"[smoke ] testando {model} @ Qwen MaaS (dim alvo={EMBED_DIMENSION}) ...")
    embedder = QwenEmbedder(model=model, dimensions=EMBED_DIMENSION)
    vecs = embedder.embed(["planejamento resiliente de agentes", "context engineering"])
    dims = {len(v) for v in vecs}
    ok = len(vecs) == 2 and dims == {EMBED_DIMENSION}
    print(f"[smoke ] retornou {len(vecs)} vetores, dim={sorted(dims)} "
          f"(esperado {EMBED_DIMENSION}) -> {'OK' if ok else 'MISMATCH'}")
    if not ok:
        raise SystemExit(1)


def main() -> None:
    ap = argparse.ArgumentParser(description="Constrói o índice vetorial do corpus.")
    ap.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    ap.add_argument("--index-dir", type=Path, default=DEFAULT_INDEX_DIR)
    ap.add_argument("--max-tokens", type=int, default=400)
    ap.add_argument("--overlap", type=int, default=60)
    ap.add_argument("--dry-run", action="store_true", help="Só cotação, sem API.")
    ap.add_argument("--rebuild", action="store_true", help="Apaga e reconstroi.")
    ap.add_argument(
        "--smoke",
        action="store_true",
        help="Testa a conexão/embedding (2 textos) e sai, sem construir índice.",
    )
    args = ap.parse_args()

    if args.smoke:
        smoke_check()
        return

    if not args.root.exists():
        raise SystemExit(f"Root não encontrado: {args.root}")

    build(
        root=args.root,
        index_dir=args.index_dir,
        max_tokens=args.max_tokens,
        overlap=args.overlap,
        dry_run=args.dry_run,
        rebuild=args.rebuild,
    )


if __name__ == "__main__":
    main()
