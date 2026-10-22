"""
Módulo P2 — Teste do Exercício

Execute com: python modules/p2_rag/test_exercise.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Embedding Similarity — Similaridade semântica funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_embedding_similarity():
    """
    TODO: Implemente cálculo de similaridade entre embeddings.
    
    Frases semanticamente similares devem ter maior similaridade.
    """
    # Embeddings simulados (vetores de dimensão reduzida p/ teste)
    query = [0.8, 0.1, 0.3]  # "política de reembolso"
    doc_a = [0.7, 0.2, 0.4]  # "como pedir dinheiro de volta" → SIMILAR
    doc_b = [0.1, 0.9, 0.2]  # "treinamento de funcionários" → DIFERENTE
    
    def cosine_similarity(a: list, b: list) -> float:
        """TODO: Calcule similaridade cosseno entre dois vetores."""
        # Fórmula: dot(a,b) / (norm(a) * norm(b))
        return 0.0  # ← Substitua pela implementação real
    
    sim_a = cosine_similarity(query, doc_a)
    sim_b = cosine_similarity(query, doc_b)
    
    assert 0 <= sim_a <= 1, f"Similaridade deve ser [0,1], got {sim_a}"
    assert 0 <= sim_b <= 1, f"Similaridade deve ser [0,1], got {sim_b}"
    assert sim_a > sim_b, \
        f"Doc A ({sim_a}) deveria ser mais similar que Doc B ({sim_b})"
    
    console.print(f"[green]✓[/green] Similaridade: A={sim_a:.3f} > B={sim_b:.3f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Document Chunking — Divisão correta?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_document_chunking():
    """
    TODO: Implemente chunking de documentos.
    
    Regra: chunks de ~500 tokens com overlap de 50.
    """
    long_text = "A política de reembolso permite solicitações dentro de 30 dias após a compra. " * 20
    
    def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
        """TODO: Divida o texto em chunks sobrepostos."""
        return []  # ← Implemente
    
    chunks = chunk_document(long_text)
    
    assert len(chunks) > 1, \
        f"Texto longo deveria gerar múltiplos chunks, got {len(chunks)}"
    assert isinstance(chunks, list), "Chunks deve ser uma lista"
    
    total_chars = sum(len(c) for c in chunks)
    original_chars = len(long_text)
    # Com overlap, total deve ser maior que original
    assert total_chars >= original_chars, \
        "Total de chars nos chunks deve cobrir todo o texto"
    
    console.print(f"[green]✓[/green] {len(chunks)} chunks gerados")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Retrieval Quality — Recuperação relevante?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_retrieval_quality():
    """
    TODO: Verifique se a recuperação traz docs relevantes.
    
    MRR (Mean Reciprocal Rank): quanto menor o rank, melhor.
    """
    documents = [
        {"id": 1, "content": "Reembolsos em até 30 dias"},
        {"id": 2, "content": "SLA de 99.9% uptime"},
        {"id": 3, "content": "Política de reembolso completo em 7 dias"},
        {"id": 4, "content": "Treinamento inclui configuração inicial"},
    ]
    
    query = "Como faço para pedir reembolso?"
    
    # Simula ranking retornado pelo sistema
    retrieved_ranks = [3, 1, 7, 12]  # IDs dos docs na ordem de relevância
    
    # TODO: Calcule MRR (Reciprocal Rank = 1/rank_do_primeiro_relevante)
    relevant_ids = {1, 3}  # Docs sobre reembolso
    
    first_relevant_rank = None
    for rank, doc_id in enumerate(retrieved_ranks, 1):
        if doc_id in relevant_ids:
            first_relevant_rank = rank
            break
    
    mrr = None if first_relevant_rank is None else 1.0 / first_relevant_rank
    
    assert mrr is not None and mrr > 0, \
        f"MRR deve ser positivo, got {mrr}"
    assert mrr <= 1.0, f"MRR não pode ser > 1, got {mrr}"
    
    console.print(f"[green]✓[/green] MRR: {mrr:.2f} (rank {first_relevant_rank})")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Context Window — Prompt cabe no contexto?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_context_window():
    """
    TODO: Verifique se o prompt + contexto cabem no window do LLM.
    
    gpt-4o: 128k tokens context window.
    """
    system_prompt_tokens = 150
    user_query_tokens = 50
    retrieved_chunks = [200, 180, 220]  # 3 chunks recuperados
    
    # TODO: Some todos os tokens e verifique se cabe
    total_tokens = None  # ← Calcule
    
    max_context = 128000  # gpt-4o
    
    assert total_tokens > 0, "Total de tokens deve ser positivo"
    assert total_tokens < max_context, \
        f"{total_tokens} tokens excedem window de {max_context}"
    
    margin = max_context - total_tokens
    console.print(f"[green]✓[/green] Total: {total_tokens}/{max_context} tokens (margem: {margin})")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: RAG Pipeline End-to-End — Pipeline completo?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_rag_pipeline():
    """
    TODO: Simule o pipeline RAG completo.
    
    Ingestão → Embedding → Busca → Contexto → Resposta
    """
    docs_ingested = 4
    queries_processed = 3
    avg_relevance_score = 0.85
    
    # TODO: Calcule métricas do pipeline
    ingestion_rate = None  # docs por segundo (simulado)
    retrieval_accuracy = None  # % de queries com doc relevante
    
    assert ingestion_rate is not None and ingestion_rate > 0, \
        "Ingestion rate deve ser positivo"
    assert 0 <= retrieval_accuracy <= 1, \
        f"Retrieval accuracy deve ser [0,1], got {retrieval_accuracy}"
    assert retrieval_accuracy >= 0.7, \
        f"Accuracy mínima aceitável: 0.7, got {retrieval_accuracy}"
    
    console.print(f"[green]✓[/green] Pipeline: {docs_ingested} docs, "
                  f"{retrieval_accuracy*100:.0f}% accuracy")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_embedding_similarity, test_02_document_chunking,
             test_03_retrieval_quality, test_04_context_window,
             test_05_rag_pipeline]
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P2: Pipeline RAG[/bold cyan]",
                        border_style="cyan"))
    
    passed = failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            console.print(f"[red]✗ {test_fn.__name__}: {e}[/red]")
            failed += 1
        except Exception as e:
            console.print(f"[red]✗ {test_fn.__name__}: Erro — {e}[/red]")
            failed += 1
    
    console.print(f"\nResultado: [bold green]{passed}/{passed+failed}[/bold green] passaram")
    if not failed:
        console.print("[bold green]🎉 Todos os testes passaram![/bold green]")


if __name__ == "__main__":
    run_all()
