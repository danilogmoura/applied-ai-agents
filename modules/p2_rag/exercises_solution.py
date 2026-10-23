"""Módulo P2 — SOLUÇÃO COMENTADA

Execute com: python modules/p2_rag/exercises.py

Código completo com explicações detalhadas.
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
    Similaridade cosseno mede o ângulo entre dois vetores.
    
    Fórmula: cos(θ) = dot(a,b) / (||a|| × ||b||)
    
    - 1.0 = vetores idênticos (mesma direção)
    - 0.0 = vetores ortogonais (sem relação)
    - -1.0 = vetores opostos (direções contrárias)
    
    Para embeddings, usamos apenas [0, 1] normalizando antes.
    """
    # Embeddings simulados (vetores de dimensão reduzida p/ teste)
    query = [0.8, 0.1, 0.3]  # "política de reembolso"
    doc_a = [0.7, 0.2, 0.4]  # "como pedir dinheiro de volta" → SIMILAR
    doc_b = [0.1, 0.9, 0.2]  # "treinamento de funcionários" → DIFERENTE
    
    def cosine_similarity(a: list, b: list) -> float:
        """
        Calcula similaridade cosseno entre dois vetores.
        
        1. Calcula produto escalar: Σ(aᵢ × bᵢ)
        2. Calcula norma de cada vetor: √(Σ(vᵢ²))
        3. Retorna dot(a,b) / (norm(a) × norm(b))
        """
        # Produto escalar
        dot_product = sum(x * y for x, y in zip(a, b))
        
        # Normas (magnitude) dos vetores
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        
        # Evita divisão por zero
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
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
    Chunking divide documentos longos em pedaços menores para embedding.
    
    Overlap (sobreposição) evita perder informações nas bordas dos chunks.
    Exemplo: chunk 1 termina com "...compra." chunk 2 começa com "A política..."
    """
    long_text = "A política de reembolso permite solicitações dentro de 30 dias após a compra. " * 20
    
    def chunk_document(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
        """
        Divide texto em chunks sobrepostos.
        
        1. Divide em blocos de chunk_size caracteres
        2. Cada bloco sobrepõe overlap caracteres ao anterior
        3. Mantém integridade (não corta palavras no meio)
        """
        if not text.strip():
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Se chegou ao fim, pega tudo restante
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Tenta cortar no espaço mais próximo (evita cortar palavra)
            space_pos = text.rfind(' ', start, end)
            if space_pos == -1:
                space_pos = end  # Força corte se não houver espaço
            
            chunks.append(text[start:space_pos])
            
            # Próximo chunk começa overlap caracteres depois do atual
            start = space_pos - overlap if space_pos > overlap else end
        
        return chunks
    
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
    Métricas de qualidade de recuperação:
    
    MRR (Mean Reciprocal Rank): 1 / posição do primeiro resultado relevante
    - MRR = 1.0 → primeiro resultado é relevante (perfeito!)
    - MRR = 0.5 → segundo resultado é relevante
    
    Hit@K: resultado relevante está nos top K?
    - Hit@3 = True → relevante está entre os 3 primeiros
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
    
    # Calcula MRR: encontra primeiro doc relevante e calcula 1/rank
    relevant_ids = {1, 3}  # Docs sobre reembolso
    
    first_relevant_rank = None
    for rank, doc_id in enumerate(retrieved_ranks, 1):
        if doc_id in relevant_ids:
            first_relevant_rank = rank
            break
    
    mrr = None if first_relevant_rank is None else 1.0 / first_relevant_rank
    
    # Hit@3: algum doc relevante está nos top 3?
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
    O context window é o limite máximo de tokens que um LLM processa.
    
    Se system_prompt + query + chunks + resposta > context_window,
    o modelo truncará ou rejeitará a requisição.
    
    Recomendação: usar no máximo 50% do contexto para deixar margem.
    """
    system_prompt_tokens = 150
    user_query_tokens = 50
    retrieved_chunks = [200, 180, 220]  # 3 chunks recuperados
    expected_response_tokens = 300  # estimativa da resposta
    
    # Soma TODOS os componentes que ocupam espaço no contexto
    total_tokens = (
        system_prompt_tokens +
        user_query_tokens +
        sum(retrieved_chunks) +
        expected_response_tokens
    )
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
    Pipeline RAG completo:
    
    1. INGESTION: Documentos são lidos e divididos em chunks
    2. EMBEDDING: Cada chunk recebe um vetor embedding
    3. RETRIEVAL: Query é embutida e docs similares são buscados
    4. CONTEXT: Chunks relevantes são concatenados ao prompt
    5. RESPONSE: LLM gera resposta baseada no contexto
    
    Métricas monitoram cada etapa.
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
    
    # Ingestion rate: quantos docs processamos por segundo
    ingestion_rate = docs_ingested / ingestion_time_s
    
    # Retrieval accuracy: fração de queries com doc relevante
    retrieval_accuracy = avg_relevance_score
    
    # Custo por query: tokens de input × preço + tokens de output × preço
    cost_per_query = (
        (input_tokens_per_query * price_per_1k_input) +
        (output_tokens_per_query * price_per_1k_output)
    ) / 1000.0
    
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
