# Material Didático — P2: Pipeline RAG (Recuperação de Contexto)

Este módulo implementa o padrão mais usado em produção para dar conhecimento interno ao LLM.

---

## ⚠️ Pré-requisito

Você precisa ter concluído o módulo [P0-First-LLM](../p0_first_llm/MATERIAL.md). Especificamente, precisa saber:

- Como construir um agente simples com OpenAI API
- O que é tokenização e por que tokens custam dinheiro

### Conhecimento técnico necessário antes de P2

Este módulo usa Python de forma mais avançada. Você **precisa saber**:

| Conceito | Por que aparece em P2 | Nível necessário |
| ---------- | ---------------------- | ------------------ |
| **Funções** (`def`) | Todo pipeline RAG é organizado em funções | Saber definir e chamar |
| **Dicionários** (`{}`) | Prompts, respostas da API, metadados são dicts | Ler/escrever chaves e valores |
| **Listas** (`[]`) | Documentos, chunks, embeddings são listas | Iterar, fatiar, append |
| **Import/Module** | `import chromadb`, `from openai import OpenAI` | Entender como importar bibliotecas |
| **Classes básicas** | `ChromaClient`, `BaseModel` aparecem no código | Entender instância e método |

Se não domina algum desses conceitos, revise-os antes de continuar. Não é matemática avançada — é Python básico.

> 💡 **Sobre embeddings:** Se nunca ouviu falar, foque na intuição: *vetores capturam significado*. "Como resetar senha" e "Esqueci a senha" têm vetores próximos mesmo sem palavras em comum. A matemática vem depois.

---

## 🎯 Objetivos de Aprendizagem

Ao final deste módulo, você será capaz de:

- [ ] **Explicar** o problema que RAG resolve (contexto limitado + custo de tokens)
- [ ] **Implementar** um pipeline RAG com ChromaDB (ingestão → busca → geração)
- [ ] **Compreender** como embeddings capturam significado semântico (não apenas palavras-chave)
- [ ] **Aplicar** chunking inteligente para manter contexto nos documentos
- [ ] **Avaliar** técnicas avançadas (busca híbrida, re-ranking, parent-child chunking, query rewriting)

> 💡 **Dica:** RAG é o padrão mais usado em produção hoje. Se você dominar este módulo, consegue construir 80% dos agentes de IA empresariais.

---

## Conceitos Fundamentais

### O Problema do Contexto Limitado

LLMs têm um limite de tokens que podem processar por vez. Imagine que você tem 50 documentos internos e quer que um agente responda perguntas baseadas neles. Enviar TODOS os documentos para cada chamada seria:

- **Caro**: Cada token custa dinheiro
- **Lento**: Mais texto = mais tempo de processamento
- **Ineficiente**: A maioria dos documentos não é relevante para a pergunta

### RAG — Retrieval Augmented Generation

RAG resolve esse problema com três etapas:

```mermaid
flowchart LR
    Pergunta["❓ Pergunta"] --> Busca["🔍 BUSCA\nDocumentos Relevantes"]
    Busca --> Geracao["🤖 GERAÇÃO\nResposta Informada"]
```

1. **Retrieval (Busca)**: Encontra os documentos mais relevantes para a pergunta
2. **Augmentation (Augmentação)**: Combina a pergunta com os documentos encontrados
3. **Generation (Geração)**: O LLM responde usando o contexto fornecido

### Embeddings — A Chave da Busca Semântica

Embeddings são vetores numéricos que representam o significado de texto. Duas frases com significado similar terão vetores próximos no espaço multidimensional:

```mermaid
graph LR
    subg1["'Como faço reembolso?'\n[0.23, -0.45, 0.87, ...]"] -.->|Cosine ~0.95| subg2["'Quero meu dinheiro de volta'\n[0.21, -0.43, 0.89, ...]"]
    subg1 -.->|Cosine ~0.30| subg3["'Regras de trânsito'\n[-0.67, 0.12, 0.34, ...]"]
    subg2 -.->|Cosine ~0.30| subg3
```

A similaridade entre vetores é medida por **cosseno** ou **distância euclidiana**. Quanto mais próximos, mais similares são semanticamente.

### ChromaDB — Vetor Store

ChromaDB é um banco de dados vetorial open-source que:

- Armazena embeddings + metadados + conteúdo original
- Faz busca por similaridade em milissegundos
- Suporta filtros por metadados (ex: só buscar em "Políticas")
- Persiste dados em disco automaticamente

### 🏗️ Arquitetura do Pipeline RAG

> Referência completa: [architecture.md](architecture.md)

O pipeline RAG é composto por 4 componentes principais:

```
[Documentos] → [Embedder] → [Vector DB] → [Retriever] → [LLM]
      ↑              ↑              ↑            ↑
   Ingestão     Embedding     Busca semântica  Contexto + Prompt
```

| Componente | Responsabilidade | Onde falha | Fallback |
| ------------ | ------------------ | ------------ | ---------- |
| **Embedder** | Converte texto → vetor | API indisponível | Embedder local (BGE) |
| **Vector DB** | Armazena e busca vetores | Corrompido/descoberto | ChromaDB local |
| **Retriever** | Seleciona docs relevantes | Threshold muito alto | Aumentar top_k |
| **LLM** | Gera resposta final | Rate limit/timeout | Retry com backoff |

**Fluxo completo:**

1. **Ingestão**: documentos → chunking → embedding → salvar no vector DB
2. **Busca**: pergunta → embedding → busca similaridade → top_k docs
3. **Geração**: pergunta + docs → prompt → LLM → resposta

Cada etapa tem trade-offs: chunk menor = mais preciso mas mais embeddings; top_k maior = mais contexto mas mais custo.

### Chunking — Divisão Inteligente de Documentos

Documentos longos devem ser divididos em chunks menores (tipicamente 200-500 tokens):

| Chunk muito pequeno | Chunk ideal | Chunk muito grande |
|---------------------|-------------|-------------------|
| Perde contexto | Mantém sentido completo | Muito específico demais |
| Embedding impreciso | Similaridade funciona bem | Ruído na busca |

### Tokens no Pipeline RAG

Cada etapa consome tokens:

```mermaid
graph LR
    Ingestao["Ingestão\n0 tokens\n( só embedding local)"] --> BuscaRAG["Busca\n0 tokens\n(busca no vetor store)"]
    BuscaRAG --> GeracaoRAG["Geração\ninput_tokens + output_tokens\n(aqui está o custo!)"]
```

O custo está apenas na geração — a busca é gratuita quando usa embedder local.

### Como Embeddings Capturam Significado

Embeddings transformam texto em **vetores de números** (geralmente 768 ou 1536 dimensões). A mágica não é matemática — é **treino**.

```mermaid
flowchart TD
    T1["Texto: 'Como resetar minha senha'"] --> Model["Modelo BERT/Text-Embedding"]
    Model --> V1["Vetor: [-0.023, 0.145, -0.089, ..., 0.034]"]
    T2["Texto: 'Esqueci a senha de acesso'"] --> Model
    Model --> V2["Vetor: [-0.021, 0.142, -0.091, ..., 0.031]"]
    V1 --> Cosine["Cosine Similarity = 0.94 → Altamente similares!"]
    V2 --> Cosine
```

**Cosine Similarity** (similaridade cosseno): mede o ângulo entre dois vetores, não a distância. Quanto mais próximo de 1, mais similares são semanticamente.

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

**RRF (Reciprocal Rank Fusion / fusão de classificação recíproca)**: combina rankings de duas buscas sem precisar normalizar scores:

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
| ------------------------ | -------------------------- |
| Processa pergunta e doc separadamente | Processa pergunta E doc juntos |
| ~10ms por par | ~100ms por par |
| Escala para milhões de docs | Só escala para centenas |
| Similaridade grosseira | Entende nuances contextuais |

Empresas usam APIs cloud (Cohere Rerank, Azure AI Search Semantic Ranker) ou modelos locais (`bge-reranker` em GPU, otimizado via ONNX/TensorRT).

#### Bi-Encoder vs Cross-Encoder: Interação entre Palavras

```mermaid
flowchart LR
    subgBE["Bi-Encoder (embedding tradicional)"]
    Q1["Pergunta → vetor A"] --> Cosine1["Cosine(A,B) = 0.78"]
    D1["Doc 1 → vetor B"] --> Cosine1
    
    subgCE["Cross-Encoder (reranker)"]
    Q2["Pergunta + Doc 1 juntos como texto"] --> Model2["Modelo único → 0.82"]
```

O cross-encoder vê interações entre palavras da pergunta E do documento.
"Senha" na pergunta + "resetar senha" no doc → atenção cruzada forte.
No bi-encoder, essa interação é perdida.

### 3. Parent-Child / Chunking Estruturado

Chunking por tamanho arbitrário (500 tokens) quebra tabelas, assinaturas e cláusulas. A solução:

```mermaid
flowchart TD
    Parent["📄 Contrato de Serviço - Seção 4\n4.1 Confidencialidade\nAs partes comprometem-se a...\n4.2 Vigência\nO contrato vale por 24 meses..."] --> Split["Dividido para busca"]
    Split --> Child1["chunk_4.1_confidencialidade (120 tokens)"]
    Split --> Child2["chunk_4.2_vigencia (80 tokens)"]
```

Se usuário busca "prazos do contrato":
  chunk_4.2 vence (cosine alta)
         ↓
Mas devolvemos ao LLM o PAI inteiro:
  → Modelo vê contexto completo da seção 4

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

#### Custo do Rewriting: ROI Real

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

## 🎬 O que você vai ver

Antes de rodar o código, aqui está uma prévia do que o programa vai fazer:

```
$ python modules/p2_rag/run.py

📥 Ingestão de documentos...
   3 documentos indexados no ChromaDB

🔍 Buscando contexto para pergunta...
   Documento mais relevante: guia_segurança.pdf (score: 0.15)

🤖 Gerando resposta com contexto RAG...
   "Baseado no guia de segurança, você deve..."

💰 Custo total: $0.003 | Tempo: 1.8s
```

> 💡 **Nota:** ChromaDB é apenas uma opção. No mercado existem alternativas como Pinecone, Qdrant e Weaviate. O conceito é o mesmo — mudar o banco de vetores.

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

## 📌 Resumo do Módulo

RAG é o padrão mais usado em produção para dar conhecimento interno ao LLM:

1. **O problema** — enviar 50 documentos para cada chamada é caro, lento e ineficiente. A maioria não é relevante para a pergunta.

2. **A solução RAG** — busca semântica (embeddings) encontra só os docs relevantes → combina com a pergunta → LLM responde com contexto certo. Custo só na geração, busca é gratuita.

3. **Embeddings capturam significado** — não é busca por palavra-chave. "Como resetar minha senha" e "Esqueci a senha de acesso" têm vetores próximos (cosine 0.94) mesmo sem palavras em comum.

4. **Chunking inteligente importa** — chunks pequenos = embedding preciso. Devolver o pai = contexto rico. Query rewriting mantém contexto conversacional.

5. **Técnicas avançadas** — busca híbrida (vetorial + BM25) resolve códigos/IDs exatos. Re-ranking (cross-encoder) reavalia top-K com precisão. ROI real: $0.0001 de rewrite vs resposta mais precisa.

> ✅ **Você está pronto para:** Agora que seu agente pode buscar conhecimento, vamos aprender a fazer ele **agir** — tool calling.

## ✅ Checklist: Como Saber Se Você Atingiu o Objetivo

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] Explico o problema que RAG resolve em 3 frases
- [ ] Descrevo os 4 passos do pipeline RAG (ingestão → busca → geração)
- [ ] Explico embeddings com uma analogia (vetores capturam significado)
- [ ] Rodo `run.py` e explico como contexto dos docs é combinado na resposta
- [ ] Cito 2 alternativas ao ChromaDB (Pinecone, Qdrant, Weaviate)

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

---

## 🔗 Próximos Passos

Com RAG, seu agente pode responder perguntas com base em documentos. Mas no mundo real, agentes precisam ir além de responder — eles precisam **executar ações**.

→ Leia o módulo [P3a-1: Autoavaliação](../p3a1_self_eval/MATERIAL.md) para aprender a verificar qualidade antes de entregar respostas.

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
