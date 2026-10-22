# Material Didático — P2: Pipeline RAG (Recuperação de Contexto)

## Conceitos Fundamentais

### O Problema do Contexto Limitado

LLMs têm um limite de tokens que podem processar por vez. Imagine que você tem 50 documentos internos e quer que um agente responda perguntas baseadas neles. Enviar TODOS os documentos para cada chamada seria:

- **Caro**: Cada token custa dinheiro
- **Lento**: Mais texto = mais tempo de processamento
- **Ineficiente**: A maioria dos documentos não é relevante para a pergunta

### RAG — Retrieval Augmented Generation

RAG resolve esse problema com três etapas:

```
Pergunta → [BUSCA] → Documentos Relevantes → [GERAÇÃO] → Resposta Informada
```

1. **Retrieval (Busca)**: Encontra os documentos mais relevantes para a pergunta
2. **Augmentation (Augmentação)**: Combina a pergunta com os documentos encontrados
3. **Generation (Geração)**: O LLM responde usando o contexto fornecido

### Embeddings — A Chave da Busca Semântica

Embeddings são vetores numéricos que representam o significado de texto. Duas frases com significado similar terão vetores próximos no espaço multidimensional:

```
"Como faço reembolso?"        → [0.23, -0.45, 0.87, ...]
"Quero meu dinheiro de volta" → [0.21, -0.43, 0.89, ...]
"Regras de trânsito"          → [-0.67, 0.12, 0.34, ...]
```

A similaridade entre vetores é medida por **cosseno** ou **distância euclidiana**. Quanto mais próximos, mais similares são semanticamente.

### ChromaDB — Vetor Store

ChromaDB é um banco de dados vetorial open-source que:

- Armazena embeddings + metadados + conteúdo original
- Faz busca por similaridade em milissegundos
- Suporta filtros por metadados (ex: só buscar em "Políticas")
- Persiste dados em disco automaticamente

### Chunking — Divisão Inteligente de Documentos

Documentos longos devem ser divididos em chunks menores (tipicamente 200-500 tokens):

| Chunk muito pequeno | Chunk ideal | Chunk muito grande |
|---------------------|-------------|-------------------|
| Perde contexto | Mantém sentido completo | Muito específico demais |
| Embedding impreciso | Similaridade funciona bem | Ruído na busca |

### Tokens no Pipeline RAG

Cada etapa consome tokens:

```
Ingestão:     0 tokens (só embedding local)
Busca:        0 tokens (busca no vetor store)
Geração:      input_tokens (pergunta + docs) + output_tokens (resposta)
```

O custo está apenas na geração — a busca é gratuita quando usa embedder local.

---

## Exercício Prático

Execute `python modules/p2_rag/run.py` e observe:

1. Como os documentos são ingeridos e indexados
2. A similaridade retornada pela busca (menor = mais relevante)
3. Como o prompt final combina pergunta + contexto dos docs
4. O relatório de custos gerado

## Perguntas para Reflexão

1. Por que usar embeddings ao invés de busca por palavras-chave? Dê um exemplo onde busca semântica supera busca lexical.
2. Se você tivesse 10.000 documentos, como o pipeline mudaria?
3. Qual o impacto de usar um embedder ruim? Como você mediria a qualidade da recuperação?

---

## Referências

### Livros

- **"Building RAG Applications"** by Matt Kane (O'Reilly) — Guia prático completo
- **"Foundations of Large Language Models"** by Alec Radford — Capítulos sobre context window

### Documentação Oficial

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [Vector Search Concepts](https://www.pinecone.io/learn/vector-search/) — Pinecone Docs

### Vídeos

- [RAG vs Fine-tuning — When to Use What](https://www.youtube.com/watch?v=b3iIZUUKWFQ) — Chris Mann, YouTube
- [How Vector Databases Work](https://www.youtube.com/watch?v=dXUBbSXLWzg) — TechWorld with Nana, YouTube

### Tutoriais

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag-chatbot/) — LangChain Docs
- [ChromaDB Quickstart](https://docs.trychroma.com/getting-started) — ChromaDB Docs
