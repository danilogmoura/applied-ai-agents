"""Módulo P2 — Exercícios Práticos

Execute com: python modules/p2_rag/exercises.py

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
        # ← Implemente aqui
        return 0.0  # Placeholder vazio
    
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
        # ← Implemente aqui
        return []  # Placeholder vazio
    
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
    Hit@K: o documento relevante está nos top K resultados?
    
    Regra: MRR >= 0.5 e Hit@3 >= 0.7 são aceitáveis para produção.
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
    
    # TODO: Calcule Hit@3 (documento relevante está nos top 3?)
    hit_at_3 = any(doc_id in relevant_ids for doc_id in retrieved_ranks[:3])
    
    assert mrr is not None and mrr > 0, \
        f"MRR deve ser positivo, got {mrr}"
    assert mrr <= 1.0, f"MRR não pode ser > 1, got {mrr}"
    assert isinstance(hit_at_3, bool), \
        f"Hit@3 deve ser boolean, got {type(hit_at_3)}"
    assert hit_at_3, \
        f"Hit@3 deveria ser True — docs relevantes estão no top 3"
    
    console.print(f"[green]✓[/green] MRR: {mrr:.2f} (rank {first_relevant_rank})")
    console.print(f"[green]✓[/green] Hit@3: {hit_at_3}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Context Window — Prompt cabe no contexto?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_context_window():
    """
    TODO: Verifique se o prompt + contexto cabem no window do LLM.
    
    gpt-4o: 128k tokens context window.
    Mas lembre-se: system_prompt + user_query + chunks + resposta_esperada
    tudo conta!
    
    Regra: usar no máximo 50% do contexto é recomendado para留出 espaço
    para a resposta gerada.
    """
    system_prompt_tokens = 150
    user_query_tokens = 50
    retrieved_chunks = [200, 180, 220]  # 3 chunks recuperados
    expected_response_tokens = 300  # estimativa da resposta
    
    # TODO: Some todos os tokens (system + query + chunks + resposta esperada)
    total_tokens = None  # ← Calcule
    recommended_max = 64000  # 50% do gpt-4o (recomendação de segurança)
    max_context = 128000  # gpt-4o
    
    assert total_tokens > 0, "Total de tokens deve ser positivo"
    assert total_tokens < recommended_max, \
        f"{total_tokens} tokens excedem limite recomendado ({recommended_max}). " \
        f"Reduza chunks ou aumente threshold de relevância."
    
    margin = recommended_max - total_tokens
    utilization_pct = (total_tokens / max_context) * 100
    console.print(f"[green]✓[/green] Total: {total_tokens}/{max_context} tokens ({utilization_pct:.1f}%)")
    console.print(f"[dim]Margem segura: {margin:,} tokens | Limite recomendado: {recommended_max:,}[/]")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: RAG Pipeline End-to-End — Pipeline completo?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_rag_pipeline():
    """
    TODO: Simule o pipeline RAG completo e calcule métricas.
    
    Ingestão → Embedding → Busca → Contexto → Resposta
    
    Métricas obrigatórias:
    - ingestion_rate: docs/segundo (simulado, > 0)
    - retrieval_accuracy: % queries com doc relevante ([0,1], >= 0.7)
    - avg_chunk_size: tamanho médio dos chunks em tokens (> 0)
    - cost_per_query: custo estimado por query em USD (> 0)
    """
    docs_ingested = 4
    queries_processed = 3
    avg_relevance_score = 0.85
    
    # Dados simulados
    ingestion_time_s = 2.5  # segundos para ingerir 4 docs
    avg_chunk_tokens = 200  # tamanho médio dos chunks
    input_tokens_per_query = 250  # query + chunks
    output_tokens_per_query = 150  # resposta gerada
    price_per_1k_input = 0.00001  # gpt-4o-mini
    price_per_1k_output = 0.00003  # gpt-4o-mini
    
    # TODO: Calcule ingestion rate (docs/segundo)
    ingestion_rate = None  # ← Calcule
    
    # TODO: Calcule retrieval accuracy (simulada)
    retrieval_accuracy = None  # ← Calcule
    
    # TODO: Calcule custo por query
    cost_per_query = None  # ← Calcule
    
    assert ingestion_rate > 0, f"Ingestion rate deve ser > 0, got {ingestion_rate}"
    assert 0 <= retrieval_accuracy <= 1, f"Retrieval accuracy deve ser [0,1], got {retrieval_accuracy}"
    assert retrieval_accuracy >= 0.7, f"Retrieval accuracy >= 0.7 esperado, got {retrieval_accuracy}"
    assert cost_per_query > 0, f"Custo por query deve ser > 0, got {cost_per_query}"
    
    console.print(f"[green]✓[/green] Ingestion: {ingestion_rate:.2f} docs/s")
    console.print(f"[green]✓[/green] Retrieval accuracy: {retrieval_accuracy:.0%}")
    console.print(f"[green]✓[/green] Custo/query: ${cost_per_query:.6f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_embedding_similarity, test_02_document_chunking,
             test_03_retrieval_quality, test_04_context_window,
             test_05_rag_pipeline]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P2: RAG[/bold cyan]",
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
        console.print("[bold green]🎉 Todos os exercícios passaram![/bold green]")


if __name__ == "__main__":
    run_all()
