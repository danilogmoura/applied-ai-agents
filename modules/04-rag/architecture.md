# 🏗️ Architecture Design — Pipeline RAG

> **Desafio:** Projete um sistema RAG para atendimento ao cliente de e-commerce.
>
> 🔬 **AVANÇADO / OPCIONAL** — Este desafio assume noções de arquitetura e infra. Se você ainda está aprendendo os fundamentos, tudo bem pular na primeira passada e voltar depois.

## Cenário

Uma loja online tem:

- **10K documentos** (políticas, FAQs, termos de serviço)
- **50K queries/mês** (~1667/hora em horário de pico)
- **SLA**: latência < 3s por query
- **Orçamento**: máximo $500/mês em custos de IA
- **Requisito**: fallback se LLM ou embedding falhar

---

## Entregáveis

> 🧭 **Como abordar este desafio.** Não existe uma única arquitetura correta — o que se avalia é o seu **raciocínio**. Sugestão de caminho:
>
> 1. Comece rascunhando o diagrama com blocos e setas (não precisa ser bonito; ASCII serve).
> 2. Para cada decisão na tabela, escreva *o que você escolheu* **e por quê** — a justificativa vale mais que a escolha.
> 3. Feche com números: mesmo estimados, custo/fallback mostram que você pensou no mundo real.
>
> Exemplo ilustrativo (não é gabarito): um bloco `[RAG Pipeline]` pode esconder sub-passos como *embedding → busca vetorial → rerank* — desenhe só o nível de detalhe que ajuda a explicar seu fluxo.

### 1. Diagrama da Arquitetura

Descreva os componentes e fluxos de dados:

```
[Usuário] → [Gateway] → [RAG Pipeline] → [LLM] → [Resposta]
              ↑            ↓
         [Cache]    [Fallback]
```

Identifique:

- Quantos serviços/componentes independentes?
- Como os dados fluem entre eles?
- Onde estão os pontos únicos de falha?

### 2. Decisões Arquiteturais

Para cada escolha abaixo, justifique seu raciocínio:

| Decisão | Opções | Sua Escolha | Justificativa |
| --------- | -------- | ------------- | --------------- |
| **Chunk size** | 200 / 500 / 1000 tokens | ? | ? |
| **Embedding model** | gpt-4o-embed / text-embedding-3-small / local BGE | ? | ? |
| **Vector DB** | ChromaDB / Pinecone / pgvector | ? | ? |
| **LLM principal** | gpt-4o-mini / claude-haiku / gpt-4o | ? | ? |
| **Fallback LLM** | Mesmo modelo menor / regra hard-coded | ? | ? |
| **Query rewriting** | Antes do retrieval / depois / não usar | ? | ? |

### 3. Plano de Fallback

Para cada componente, descreva o que acontece se ele falhar:

| Componente | Falha | Impacto | Fallback |
| ------------ | ------- | --------- | ---------- |
| Embedding API | Indisponível | Não consegue buscar docs relevantes | ? |
| Vector DB | Corrompido | Retrieval falha | ? |
| LLM principal | Rate limit | Geração travada | ? |
| Cache | Full | Latência sobe | ? |

### 4. Estimativa de Custo Detalhada

> 💡 **Como calcular custo.** Fórmula: `custo = (tokens / 1_000_000) × preço_por_milhão`.
> Preços de referência (USD por 1M tokens): **gpt-4o-mini** $0.15 entrada / $0.60 saída; **gpt-4o** $2.50 / $10.00; **text-embedding-3-small** $0.02.
> Regra prática de tokens: ~4 caracteres ≈ 1 token (≈ 750 tokens por página de texto).
> Exemplo: 1.667 queries/dia × 800 tokens de entrada = 1,33M tokens/dia → 1,33 × $0.15 ≈ **$0.20/dia só de entrada** no gpt-4o-mini.

Calcule o custo mensal considerando:

- Queries reais (não todas vão ao LLM — algumas respondidas pelo cache)
- Tokens de input + output por query
- Custos de embedding na ingestão (one-time) + re-embedding se necessário

---

## Checklist de Validação

- [ ] Identificou todos os componentes do pipeline RAG
- [ ] Justificou trade-offs (latência vs custo vs qualidade)
- [ ] Considerou cache de queries frequentes (FAQ)
- [ ] Plano de fallback realista para cada componente
- [ ] Custo estimado dentro do orçamento ($500/mês)
- [ ] Considerou escalabilidade (1667 queries/hora de pico)

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
| ---------- | -------------- | --------- | ----------- |
| **Trade-offs** | Analisa pr/pr de cada decisão | Menciona apenas prós | Ignora contrapontos |
| **Fallback** | Cobertura completa com impacto | Parcial | Ausente |
| **Custo** | Estimativa detalhada e realista | Estimativa grosseira | Sem cálculo |
| **Escalabilidade** | Considera picos e crescimento | Considera apenas carga atual | Ignora escala |
