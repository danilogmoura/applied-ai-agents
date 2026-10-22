# 🏗️ Mini-Projeto Integrador — RAG (Retrieval-Augmented Generation)

> **Objetivo:** Construir um mini-RAG completo que responde perguntas sobre documentos.

## O que você vai construir

Um sistema `mini_rag.py` que:

1. **Indexa** documentos (chunking + embeddings simulados)
2. **Recupera** documentos relevantes por similaridade
3. **Gera** resposta baseada no contexto recuperado
4. **Avalia** qualidade da recuperação (MRR, hit rate)

## Requisitos

```python
class MiniRAG:
    def chunk_document(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list:
        """Dividir documento em chunks."""
        ...
    
    def embed_text(self, text: str) -> list:
        """Gerar embedding simulado (hash determinístico → vetor 8-dim)."""
        ...
    
    def index_documents(self, documents: list) -> dict:
        """Indexar docs: chunks + embeddings + metadados."""
        ...
    
    def retrieve(self, query: str, top_k: int = 3) -> list:
        """Recuperar chunks mais similares ao query."""
        ...
    
    def generate_response(self, query: str, context: list) -> str:
        """Gerar resposta baseada no contexto recuperado."""
        ...
    
    def evaluate_retrieval(self, query: str, expected_chunk_id: str) -> dict:
        """Avaliar MRR e hit@k."""
        ...
```

## Teste seu código

```bash
python mini_rag.py --docs policy.pdf --query "política de reembolso"
python mini_rag.py --index my_index.json --query "como solicitar estorno?"
```

## Desafios extras

- [ ] Suporte a múltiplos formatos (PDF, TXT, Markdown)
- [ ] Re-ranking dos resultados recuperados
- [ ] Feedback loop (marcar respostas úteis/não úteis)
- [ ] API web com FastAPI
