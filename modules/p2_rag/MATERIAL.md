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

### Como Embeddings Capturam Significado

Embeddings transformam texto em **vetores de números** (geralmente 768 ou 1536 dimensões). A mágica não é matemática — é **treino**.

```
Texto: "Como resetar minha senha"
         ↓
[Modelo BERT/Text-Embedding processa]
         ↓
Vetor (768 dimensões):
[-0.023, 0.145, -0.089, ..., 0.034]
         ↓
Texto: "Esqueci a senha de acesso"
         ↓
Vetor:
[-0.021, 0.142, -0.091, ..., 0.031]
         ↓
Cosine Similarity = 0.94 → Altamente similares!
```

**Cosine Similarity**: mede o ângulo entre dois vetores, não a distância.

```
Cosine(A, B) = (A · B) / (||A|| × ||B||)

Resultado: -1 (opostos) → +1 (idênticos) → 0 (independentes)

"Senha" vs "Contraseña"    → 0.92 (diferente idioma, mesmo sentido)
"Senha" vs "Preço do produto" → 0.31 (sem relação)
```

O modelo aprendeu durante o treino que textos com significado similar produzem vetores próximos no espaço multidimensional. Não é busca por palavra-chave — é busca por **significado**.

---

## Técnicas Avançadas de Produção

### 1. Busca Híbrida (Vetorial + BM25)

Em sistemas reais, usuários buscam códigos de produto, números de chamado, IDs de erro, siglas internas. Vetores puros falham nesses casos:

```
Usuário: "Qual o status do chamado INC-4892?"
         ↓
[Busca vetorial] → docs sobre "status" e "chamado" mas não encontra INC-4892
[Busca BM25]     → encontra EXATAMENTE "INC-4892" ✅
         ↓
[RRF] Combina os rankings → resultado correto
```

**RRF (Reciprocal Rank Fusion)**: combina rankings de duas buscas sem precisar normalizar scores:

```
RRF(score) = Σ 1 / (k + rank_da_busca_i)

k = constante (geralmente 60)
Quanto melhor o rank, maior o score final.
```

Nenhum banco vetorial faz busca híbrida nativamente — é código na aplicação. Elasticsearch, OpenSearch e Qdrant já oferecem isso embutido.

#### Por que BM25 ainda existe?

BM25 é um algoritmo de busca lexical de 1994 que conta palavras com ponderação IDF (termos raros valem mais). Ele é:
- **Determinístico**: "INC-4892" sempre encontra "INC-4892"
- **Rápido**: sem cálculo de vetores
- **Barato**: roda em qualquer servidor

Vetorial entende significado; BM25 entende exatidão. Juntos, cobrem tudo.

### 2. Re-ranking (Cross-Encoder)

Após buscar N documentos, um reranker reavalia só os top-K com muito mais precisão:

```
Passo 1 — Embedding (fast, impreciso):
  Pergunta → [Embedder] → vetor
  Docs → [Embedder] → vetores
  Top-50 por cosine similarity
         ↓
Passo 2 — Reranker (slow, preciso):
  Para cada um dos 50:
    [Cross-Encoder] pergunta + doc → score 0-1
  Top-5 para o LLM
```

**Diferença fundamental:**

| Embedding (Bi-Encoder) | Reranker (Cross-Encoder) |
|------------------------|--------------------------|
| Processa pergunta e doc separadamente | Processa pergunta E doc juntos |
| ~10ms por par | ~100ms por par |
| Escala para milhões de docs | Só escala para centenas |
| Similaridade grosseira | Entende nuances contextuais |

Empresas usam APIs cloud (Cohere Rerank, Azure AI Search Semantic Ranker) ou modelos locais (`bge-reranker` em GPU, otimizado via ONNX/TensorRT).

#### Por Baixo dos Panos: Bi-Encoder vs Cross-Encoder

```
Bi-Encoder (embedding tradicional):
┌──────────┐                    ┌──────────┐
│ Pergunta │→ [Modelo] → vetor A│          │
└──────────┘                    │ Vetor DB │
┌──────────┐                    │          │
│ Doc 1    │→ [Modelo] → vetor B│          │
└──────────┘                    └──────────┘
Cosine(A, B) = 0.78

Cross-Encoder (reranker):
┌─────────────────────┐
│ Pergunta + Doc 1    │→ [Modelo único] → 0.82
│ "juntos como texto" │
└─────────────────────┘

O cross-encoder vê interações entre palavras da pergunta E do documento.
"Senha" na pergunta + "resetar senha" no doc → atenção cruzada forte.
No bi-encoder, essa interação é perdida.
```

### 3. Parent-Child / Chunking Estruturado

Chunking por tamanho arbitrário (500 tokens) quebra tabelas, assinaturas e cláusulas. A solução:

```
Documento original (pai):
┌─────────────────────────────────────────┐
│ Contrato de Serviço - Seção 4           │
│ 4.1 Confidencialidade                   │
│ As partes comprometem-se a...           │
│ 4.2 Vigência                            │
│ O contrato vale por 24 meses...         │
└─────────────────────────────────────────┘
         ↓ dividido para busca
Chunks filhos (buscados individualmente):
  chunk_4.1_confidencialidade (120 tokens)
  chunk_4.2_vigencia (80 tokens)
         ↓
Se usuário busca "prazos do contrato":
  chunk_4.2 vence (cosine alta)
         ↓
Mas devolvemos ao LLM o PAI inteiro:
  → Modelo vê contexto completo da seção 4
```

**Por que funciona:** chunks pequenos = embedding preciso. Devolver o pai = contexto rico.

### 4. Query Rewriting / Contextualização Conversacional

Em chatbots, perguntas sequenciais perdem referência:

```
Usuário: "Como faço login no sistema?"
  → Busca: "login sistema" → docs corretos ✅
         ↓
Usuário: "E se eu esquecer a senha?"
  → Busca literal: "esquecer senha" → docs genéricos ❌
  → Query rewriting: "como resetar senha no sistema de login"
  → Busca: "resetar senha sistema login" → docs corretos ✅
```

Um modelo rápido e barato (gpt-4o-mini, não gpt-4o) reescreve a pergunta mantendo contexto:

```python
prompt_rewrite = f"""
Reescreva esta pergunta mantendo o contexto da conversa:

Conversa anterior:
{conversation_history[-3:]}

Pergunta atual: {user_question}

Responda APENAS com a pergunta reescrita, sem explicação."""
```

#### Por Baixo dos Panos: Custo do Rewriting

```
Sem rewriting:        Com rewriting:
Custo busca: $0       Custo busca: $0
Custo LLM judge: $0   Custo rewrite: $0.0001
Custo geração: $0.05  Custo geração: $0.04 (menos tokens)
Custo total: $0.05    Custo total: $0.0501

Ganho: resposta mais precisa = menos iterações do usuário
Perda: $0.0001 por passo conversacional
ROI: positivo a partir de 1 iteração economizada
```

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

- **"Building LLMs for Production"** by Christopher Keith & Anthony Langstone (O'Reilly) — Capítulos sobre RAG pipelines

### Documentação Oficial

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [OpenAI Embeddings API](https://platform.openai.com/docs/guides/embeddings)
- [Vector Search Concepts](https://www.pinecone.io/learn/vector-search/) — Pinecone Docs

### Tutoriais

- [LangChain RAG Tutorial](https://python.langchain.com/docs/tutorials/rag-chatbot/) — LangChain Docs
- [ChromaDB Quickstart](https://docs.trychroma.com/getting-started) — ChromaDB Docs
