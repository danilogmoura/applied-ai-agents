"""
Módulo 04 — Pipeline RAG (Recuperação de Contexto)

Construção de pipeline completo para busca em documentos locais.
Foco: embeddings, vetor store (ChromaDB), latência e contagem de tokens.

Problema: Você tem 50 documentos PDF/Markdown e precisa que um agente
consulta informações específicas sem enviar tudo para o LLM.
Como construir um sistema eficiente de recuperação de contexto?
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from shared.logging_config import setup_logging, measure_latency
from shared.cost import count_tokens, estimate_cost, format_cost
from shared.security import get_llm_config, get_model, get_provider

console = Console()
logger = setup_logging("04-rag")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DOCUMENTOS DE EXEMPLO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SAMPLE_DOCUMENTS = [
    {
        "id": "doc_001",
        "title": "Política de Reembolso",
        "content": (
            "A política de reembolso permite solicitações dentro de 30 dias após a compra. "
            "Reembolsos completos são aplicados para produtos em até 7 dias. "
            "Produtos digitais têm política de 14 dias. Processamento leva de 5 a 10 dias úteis."
        ),
    },
    {
        "id": "doc_002",
        "title": "Guia de Segurança",
        "content": (
            "Todos os dados sensíveis devem ser criptografados com AES-256. "
            "Autenticação multifator é obrigatória para acesso a produção. "
            "Logs de auditoria devem ser mantidos por no mínimo 1 ano. "
            "Senhas devem ter mínimo de 12 caracteres com complexidade."
        ),
    },
    {
        "id": "doc_003",
        "title": "SLA de Disponibilidade",
        "content": (
            "O SLA garante 99.9% de uptime mensal. Tempo máximo de downtime permitido: "
            "43 minutos por mês. Notificação de manutenção deve ser enviada com 48h de antecedência. "
            "Créditos de serviço: 10% para downtime entre 1-4h, 25% para 4-8h, 50% para >8h."
        ),
    },
    {
        "id": "doc_004",
        "title": "Onboarding de Clientes",
        "content": (
            "O processo de onboarding inclui: configuração inicial (dia 1), treinamento (dias 2-3), "
            "período de acompanhamento (semana 1), e revisão de satisfação (semana 2). "
            "Cada cliente recebe um success manager dedicado por 90 dias."
        ),
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EMBEDDING LOCAL (sem API externa)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimpleEmbedder:
    """
    Embedder local simples usando TF-IDF-like approach.
    
    Para produção, substituir por text-embedding-3-small ou similar.
    Este embedder funciona offline e não gera custos de API.
    """
    
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vocab: dict[str, int] = {}
        self._fitted = False
    
    def _build_vocab(self, documents: list[str]) -> None:
        """Construi vocabulário a partir dos documentos."""
        word_freq: dict[str, int] = {}
        for doc in documents:
            for word in doc.lower().split():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Filtra stopwords básicas e constrói vocab
        stopwords = {"a", "e", "o", "de", "do", "da", "em", "um", "uma", "para", 
                     "com", "que", "ou", "se", "na", "no", "as", "os", "é", "por"}
        
        self.vocab = {
            word: idx for idx, (word, freq) in enumerate(
                sorted((w for w in word_freq if w not in stopwords and len(w) > 2), 
                       key=lambda x: -x[1])
            )[:self.dimension]
        }
    
    def fit_transform(self, documents: list[str]) -> list[list[float]]:
        """Gera embeddings para lista de documentos."""
        self._build_vocab(documents)
        return self.transform(documents)
    
    def transform(self, documents: list[str]) -> list[list[float]]:
        """Transforma textos em vetores de embedding."""
        embeddings = []
        
        for doc in documents:
            vec = [0.0] * self.dimension
            words = doc.lower().split()
            
            for word in words:
                if word in self.vocab:
                    idx = self.vocab[word]
                    # TF simples: frequência do termo no documento
                    tf = words.count(word) / max(len(words), 1)
                    vec[idx] += tf
            
            # Normaliza L2
            norm = sum(v * v for v in vec) ** 0.5
            if norm > 0:
                vec = [v / norm for v in vec]
            
            embeddings.append(vec)
        
        return embeddings
    
    def embed_query(self, query: str) -> list[float]:
        """Gera embedding para uma única query."""
        return self.transform([query])[0]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VETOR STORE COM CHROMADB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ChromaVectorStore:
    """Wrapper simplificado para ChromaDB."""
    
    def __init__(self, collection_name: str = "rag_docs", persist_path: Optional[str] = None):
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=persist_path) if persist_path else chromadb.Client()
            self.collection = self.client.get_or_create_collection(name=collection_name)
            logger.info(f"ChromaDB initialized: collection='{collection_name}'")
        except ImportError:
            logger.warning("chromadb não instalado — usando fallback em memória")
            self.client = None
            self.collection = None
            self._fallback_docs: list[dict] = []
    
    def add_documents(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: Optional[list[dict]] = None,
        embeddings: Optional[list[list[float]]] = None,
    ) -> None:
        """Adiciona documentos ao vetor store."""
        if self.collection:
            self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
            logger.info(f"Added {len(ids)} documents to ChromaDB")
        else:
            # Fallback em memória
            self._fallback_docs = list(zip(ids, documents, metadatas or [{}]))
    
    def search(
        self,
        query_embedding: Optional[list[float]],
        query_text: Optional[str] = None,
        top_k: int = 3,
        where: Optional[dict] = None,
    ) -> list[dict]:
        """Busca documentos similares."""
        if self.collection:
            kwargs: dict = {"n_results": top_k}
            if query_embedding:
                kwargs["where_embedding"] = query_embedding
            if query_text:
                kwargs["query_texts"] = [query_text]
            if where:
                kwargs["where"] = where
            
            results = self.collection.query(**kwargs)
            
            return [
                {
                    "id": doc_id,
                    "content": content,
                    "metadata": meta or {},
                    "distance": dist,
                }
                for doc_id, content, meta, dist in zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0],
                )
            ]
        else:
            # Fallback simples: busca por keywords
            if query_text:
                query_words = set(query_text.lower().split())
                scored = []
                for doc_id, doc_content, meta in self._fallback_docs:
                    doc_words = set(doc_content.lower().split())
                    score = len(query_words & doc_words) / max(len(query_words), 1)
                    if score > 0:
                        scored.append({
                            "id": doc_id,
                            "content": doc_content,
                            "metadata": meta,
                            "distance": 1.0 - score,
                        })
                scored.sort(key=lambda x: x["distance"])
                return scored[:top_k]
            return []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PIPELINE RAG COMPLETO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class RAGPipeline:
    """
    Pipeline RAG completo: ingestão → busca → geração.
    
    Fluxo:
    1. Ingestão: divide documentos, gera embeddings, salva no vetor store
    2. Busca: query → embedding → busca similaridade → top-k docs
    3. Geração: combina query + docs relevantes → envia para LLM
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        top_k: int = 3,
        chunk_size: int = 500,
    ):
        self.model = model
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.embedder = SimpleEmbedder()
        self.vector_store = ChromaVectorStore()
    
    def ingest(self, documents: list[dict]) -> int:
        """
        Ingere documentos no pipeline.
        
        Returns:
            Número de chunks criados.
        """
        console.print("[bold cyan]▸ Ingerindo documentos...[/]")
        
        chunks = []
        chunk_ids = []
        chunk_metadatas = []
        
        for doc in documents:
            # Divide documento em chunks
            content = doc["content"]
            words = content.split()
            
            i = 0
            while i < len(words):
                chunk = " ".join(words[i : i + self.chunk_size // 5])
                if chunk.strip():
                    chunk_id = f"{doc['id']}_chunk_{i // self.chunk_size}"
                    chunks.append(chunk)
                    chunk_ids.append(chunk_id)
                    chunk_metadatas.append({"source": doc["id"], "title": doc.get("title", "")})
                i += self.chunk_size
        
        # Gera embeddings
        embeddings = self.embedder.fit_transform(chunks)
        
        # Salva no vetor store
        self.vector_store.add_documents(
            ids=chunk_ids,
            documents=chunks,
            metadatas=chunk_metadatas,
            embeddings=embeddings,
        )
        
        console.print(f"[green]✓ {len(chunks)} chunks ingeridos[/]")
        return len(chunks)
    
    def retrieve(self, query: str) -> list[dict]:
        """Busca documentos relevantes para a query."""
        console.print(f"\n[bold cyan]▸ Buscando contexto para: '{query}'[/]")
        
        query_embedding = self.embedder.embed_query(query)
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=self.top_k,
        )
        
        for i, result in enumerate(results, 1):
            preview = result["content"][:100] + "..."
            console.print(f"  [{i}] (dist={result['distance']:.3f}) {result['metadata'].get('title', 'N/A')}")
            console.print(f"      {preview}")
        
        return results
    
    def generate(
        self,
        query: str,
        context_docs: list[dict],
    ) -> dict:
        """
        Gera resposta combinando query + contexto recuperado.
        
        Returns:
            Dicionário com resposta e métricas.
        """
        from openai import OpenAI
        
        api_key, base_url, _ = get_llm_config()
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        # Constrói prompt com contexto
        context_text = "\n\n".join(
            f"[{doc['metadata'].get('title', 'Doc')}] {doc['content']}"
            for doc in context_docs
        )
        
        prompt = f"""Responda à pergunta usando APENAS o contexto fornecido.
Se não encontrar resposta no contexto, diga: 'Não encontrei informação suficiente.'

CONTEXTO:
{context_text}

PERGUNTA: {query}

RESPOSTA:"""
        
        messages = [{"role": "user", "content": prompt}]
        input_tokens = count_tokens(prompt, self.model)
        
        with measure_latency(logger, "rag_generate") as metrics:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=500,
                temperature=0.3,
            )
        
        answer = response.choices[0].message.content
        output_tokens = count_tokens(answer, self.model)
        cost = estimate_cost(input_tokens, output_tokens, self.model)
        
        metrics["answer_length"] = len(answer)
        
        logger.info(
            "rag_response",
            extra={"extra_data": {
                "query": query,
                "docs_retrieved": len(context_docs),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
            }},
        )
        
        return {
            "query": query,
            "answer": answer,
            "context_docs": len(context_docs),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": cost,
        }
    
    def run(self, query: str) -> dict:
        """Executa pipeline completo: retrieve → generate."""
        console.print(Panel.fit(
            f"[bold]Pergunta:[/]\n{query}",
            title="🔍 RAG Pipeline",
            border_style="cyan",
        ))
        
        # Retrieve
        context_docs = self.retrieve(query)
        
        if not context_docs:
            return {"query": query, "answer": "Nenhum contexto relevante encontrado.", "cost_usd": 0}
        
        # Generate
        result = self.generate(query, context_docs)
        
        # Exibe resultado
        console.print("\n" + "=" * 60)
        console.print("[bold green]💡 Resposta:[/]\n")
        console.print(result["answer"])
        console.print("\n" + "-" * 60)
        console.print(f"Contextos usados: {result['context_docs']}")
        console.print(f"Tokens: {result['input_tokens']} input + {result['output_tokens']} output")
        console.print(f"Custo: {format_cost(result['cost_usd'])}")
        console.print("=" * 60)
        
        return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa demonstração completa do pipeline RAG."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO 04 — Pipeline RAG[/]\n\n"
        "Recuperação de contexto em documentos locais.\n"
        "Embeddings + ChromaDB + Geração com LLM.",
        title="📚 AI Agents Course",
        border_style="cyan",
    ))
    
    # Valida ambiente
    try:
        get_llm_config()
        console.print(f"[green]✓ Ambiente validado ({get_provider()})[/]")
    except EnvironmentError as e:
        console.print(f"[red]✗ {e}[/]")
        sys.exit(1)
    
    model = get_model()
    
    # Inicializa pipeline
    pipeline = RAGPipeline(model=model, top_k=2)
    
    # Ingestão
    n_chunks = pipeline.ingest(SAMPLE_DOCUMENTS)
    
    # Queries de teste
    queries = [
        "Qual o prazo para solicitar reembolso?",
        "Quais os requisitos de segurança para produção?",
        "O que acontece se o sistema ficar fora do ar?",
    ]
    
    total_cost = 0.0
    
    for query in queries:
        result = pipeline.run(query)
        total_cost += result["cost_usd"]
        console.print()
    
    # Relatório final
    console.print(Panel(
        f"Documentos ingeridos: {len(SAMPLE_DOCUMENTS)}\n"
        f"Chunks criados: {n_chunks}\n"
        f"Queries processadas: {len(queries)}\n"
        f"Custo total: [bold]{format_cost(total_cost)}[/]",
        title="📊 RAG — Resumo",
        border_style="green",
    ))
    
    console.print("\n[dim]💡 Próximo passo: Módulo 05 — Autoavaliação e reflexão[/]")


if __name__ == "__main__":
    main()
