# 🏗️ Mini-Projeto Integrador — RAG (Retrieval-Augmented Generation)

> **Objetivo:** Construir um mini-RAG completo que responde perguntas sobre documentos.

## O que você vai construir

Um sistema `mini_rag.py` que:

1. **Indexa** documentos (chunking + embeddings simulados)
2. **Recupera** documentos relevantes por similaridade
3. **Gera** resposta baseada no contexto recuperado
4. **Avalia** qualidade da recuperação (MRR, hit rate)

> ℹ️ **Arquitetura:** Este mini-projeto apresenta tudo numa classe única (`MiniRAG`) para simplificar o aprendizado. O `run.py` de referência usa uma arquitetura **modular** com três classes separadas — `SimpleEmbedder` (embeddings), `ChromaVectorStore` (índice/recuperação) e `RAGPipeline` (orquestração). Ambas as abordagens são válidas: comece com a classe única e, quando se sentir confortável, refatore para as três classes modulares (boa prática).

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

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com chunking

Divida documentos em pedaços sobrepostos. Chunking é o primeiro passo do RAG:

```python
import hashlib
import json

class MiniRAG:
    def __init__(self):
        self.index = {}  # chunk_id → {"text": str, "embedding": list, "metadata": dict}
    
    def chunk_document(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list:
        """Dividir texto em chunks sobrepostos."""
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Gera ID único baseado no conteúdo
            hash_id = hashlib.md5(chunk.encode()).hexdigest()[:8]
            chunks.append({
                "id": f"chunk_{hash_id}",
                "text": chunk,
                "start_pos": start,
                "end_pos": end,
            })
            chunk_id += 1
            
            # Avança com overlap (volta um pouco para cobrir contexto)
            start = end - overlap
        
        return chunks
```

### Passo 2 — Implemente embeddings simulados

Em vez de chamar uma API de embedding real, use hash determinístico que gera vetores consistentes:

```python
import struct

def embed_text(self, text: str, dim: int = 8) -> list:
    """Gerar embedding simulado usando hash como seed."""
    # Usa hash do texto como seed para gerar vetor determinístico
    h = hashlib.sha256(text.encode()).digest()
    
    # Converte bytes do hash em floats normalizados [-1, 1]
    vectors = []
    for i in range(dim):
        # Pega 4 bytes do hash, converte para float
        byte_start = (i * 4) % len(h)
        value = struct.unpack('>f', h[byte_start:byte_start+4])[0]
        vectors.append(value)
    
    # Normaliza para ter magnitude ~1 (útil para similaridade)
    magnitude = sum(v*v for v in vectors) ** 0.5
    if magnitude > 0:
        vectors = [v / magnitude for v in vectors]
    
    return vectors
```

### Passo 3 — Indexe documentos

Combine chunking + embeddings em um índice pesquisável:

```python
def index_documents(self, documents: list) -> dict:
    """Indexar lista de docs: cada doc vira chunks com embeddings."""
    total_chunks = 0
    
    for doc in documents:
        text = doc.get("content", "")
        metadata = {"source": doc.get("filename", "unknown")}
        
        chunks = self.chunk_document(text)
        for chunk in chunks:
            chunk_id = chunk["id"]
            chunk["embedding"] = self.embed_text(chunk["text"])
            chunk["metadata"] = metadata
            self.index[chunk_id] = chunk
            total_chunks += 1
    
    return {"indexed": total_chunks, "total_docs": len(documents)}
```

### Passo 4 — Recupere por similaridade

Use similaridade cosseno para encontrar chunks relevantes:

```python
def cosine_similarity(self, vec_a: list, vec_b: list) -> float:
    """Calcula similaridade cosseno entre dois vetores."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    mag_a = sum(a * a for a in vec_a) ** 0.5
    mag_b = sum(b * b for b in vec_b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)

def retrieve(self, query: str, top_k: int = 3) -> list:
    """Retorna os top_k chunks mais similares ao query."""
    query_embedding = self.embed_text(query)
    
    scores = []
    for chunk_id, chunk in self.index.items():
        sim = self.cosine_similarity(query_embedding, chunk["embedding"])
        scores.append((sim, chunk))
    
    # Ordena por similaridade decrescente
    scores.sort(key=lambda x: x[0], reverse=True)
    
    return [{"score": s, **chunk} for s, chunk in scores[:top_k]]
```

### Passo 5 — Gere resposta baseada no contexto

Concatena os chunks recuperados e forma uma resposta:

```python
def generate_response(self, query: str, context: list) -> str:
    """Gera resposta baseada nos chunks recuperados."""
    if not context:
        return "Nenhum documento relevante encontrado."
    
    # Junta textos dos chunks
    context_text = "\n\n---\n\n".join([c["text"] for c in context])
    
    response = (
        f"Baseado nos documentos recuperados para '{query}':\n\n"
        f"{context_text}\n\n"
        f"(Recuperados {len(context)} chunks relevantes)"
    )
    return response
```

### Passo 6 — Avalie a recuperação

MRR (Mean Reciprocal Rank) e hit@k medem qualidade da busca:

```python
def evaluate_retrieval(self, query: str, expected_chunk_id: str) -> dict:
    """Avalia se o chunk esperado está entre os resultados."""
    results = self.retrieve(query, top_k=3)
    
    # Hit@k: o esperado está nos top 3?
    hit = any(r["id"] == expected_chunk_id for r in results)
    
    # MRR: qual a posição do primeiro resultado relevante?
    rr = 0
    for i, r in enumerate(results, 1):
        if r["id"] == expected_chunk_id:
            rr = 1 / i
            break
    
    return {
        "hit_at_3": hit,
        "reciprocal_rank": round(rr, 3),
        "top_results": len(results),
    }
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `chunk_document()` divide o texto respeitando `chunk_size` e `overlap`
- [ ] `embed_text()` retorna vetor determinístico (mesmo texto → mesmo vetor)
- [ ] `index_documents()` associa cada chunk ao seu embedding e metadados
- [ ] `retrieve()` devolve os `top_k` chunks mais similares ao query
- [ ] `generate_response()` usa APENAS o contexto recuperado na resposta
- [ ] `evaluate_retrieval()` calcula `hit@k` e reciprocal rank corretamente

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

## Teste seu código

```bash
python mini_rag.py --docs policy.pdf --query "política de reembolso"
python mini_rag.py --index my_index.json --query "como solicitar estorno?"
```

## 🪨 Travei? Pistas em camadas

Funciona igualzinho às pistas dos exercícios: quando um requisito travar, abra **só o próximo nível** que você precisar — nunca todos de uma vez. O objetivo é destravar o raciocínio, não entregar a resposta mastigada.

> **Nível 1 — Direção.** Cada requisito mapeia para um `Passo` do guia acima. Antes de descer de nível, releia o Passo correspondente; na maioria das vezes ele já tem o esqueleto da função.

<details>
<summary><b>Nível 2 — A ideia por requisito</b> (clique para abrir)</summary>

- **`chunk_document()`:** varra o texto com janela deslizante — passo `chunk_size - overlap` — e retorne uma lista de fatias. O `overlap` evita cortar uma frase no ponto exato entre dois chunks.
- **`embed_text()`:** embedding *simulado*: faça um hash determinístico do texto (ex.: `hashlib`) e expanda para um vetor de 8 dimensões. Mesma entrada → mesmo vetor, sempre.
- **`index_documents()`:** para cada doc, chunk → embed → grave em `self.index[chunk_id] = {text, embedding, metadata}`. O `chunk_id` (“doc_i_chunk_j”) é a chave que `retrieve()` vai devolver.
- **`retrieve()`:** embed a query, compare com cada embedding indexado via `cosine_similarity`, ordene desc e corte em `top_k`. Retorna os chunks mais parecidos, não a resposta ainda.
- **`generate_response()`:** injete os chunks recuperados no prompt de contexto e chame o LLM (ou simule). É a única etapa que usa linguagem natural de verdade.
- **`evaluate_retrieval()`:** verifique se `expected_chunk_id` aparece nos top-k → hit@k; MRR = `1/posição` do primeiro acerto (0 se ausente).

</details>

<details>
<summary><b>Nível 3 — Quase solução</b> (abra só se o nível 2 não bastou)</summary>

```python
def retrieve(self, query, top_k=3):
    qv = self.embed_text(query)
    scored = [(cid, self.cosine_similarity(qv, c["embedding"]))
              for cid, c in self.index.items()]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [self.index[cid] for cid, _ in scored[:top_k]]
```

Todo o pipeline RAG depende dessa ordem: `index_documents()` alimenta `self.index`, `retrieve()` lê esse índice, e `generate_response()` consome justamente o que `retrieve()` devolveu.

</details>

## Desafios extras

- [ ] Suporte a múltiplos formatos (PDF, TXT, Markdown)
- [ ] Re-ranking dos resultados recuperados
- [ ] Feedback loop (marcar respostas úteis/não úteis)
- [ ] API web com FastAPI
