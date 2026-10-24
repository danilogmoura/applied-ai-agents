# 🗺️ Mapa de Cobertura — p9_caching

> Gerado por `tools/coverage_map.py` (modo A). Ponteiros verificáveis para as
> fontes do corpus — **não** é texto autoral nem tradução. Quotes vêm crus da fonte.

_Conceitos analisados: 8 · limiar sim ≥ 0.50_

## O Problema do Custo em Escala
- ✅ sim=0.57 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > At 70% utilization and $2/h for one H100,17 training GPT-3-175B would cost over $4 million: $2/H100/hour × 256 H100 × 24 hours × 256 days / 0.7 = $4,142,811.43 Tip In summary, three numbers signal a model’s scale:…
- ✅ sim=0.55 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c34S`
  > 12.15 Scaling Strategies Scaling an agent system is not only an infrastructure problem. It is also an architectural problem. Horizontal scaling adds more instances of a service. For example, multiple agent runtime…
- ✅ sim=0.54 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c2WU`
  > Chapter 12 Performance and Cost Optimization A capable agent system is not automatically an efficient one. It may answer well, use tools correctly, retrieve the right context, follow a reliable workflow, and still be…

## Erros Comuns de Iniciantes
- ✅ sim=0.54 [EN] — `We Make Mistakes · `fastapi-docs-en/docs/deployment/concepts.md``
  > We Make Mistakes We, as humans, make **mistakes**, all the time. Software almost *always* has **bugs** hidden in different places. 🐛 And we as developers keep improving the code as we find those bugs and as we implement…
- ✅ sim=0.52 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HZ`
  > Avoiding Common Pitfalls in Idea Generation Ideas die long before a backtest ever sees them; they wither in quiet corners, assumptions left unspoken, data quietly poisoned, incentives that favor flash over…

## Cache de Respostas
- ✅ sim=0.54 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/toc`
  > • Caching strategies • Scalable architecture • Optimized datastores: • Efficient change detection • Race-to-response • Semantic caching for code explanations • Improving reliability and availability at high load •…

## Arquitetura da Cache Layer
- ✅ sim=0.60 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/toc`
  > • Caching strategies • Scalable architecture • Optimized datastores: • Efficient change detection • Race-to-response • Semantic caching for code explanations • Improving reliability and availability at high load •…
- ✅ sim=0.59 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch10`
  > Since requests and responses are already flowing through the gateway, it’s a good place to implement other functionalities, such as load balancing, logging, and analytics. Some gateways even provide caching and…
- ✅ sim=0.58 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_3`
  > Calculating the query_hash and running the vector search are CPU-intensive and necessary for every context-aware query. Caching the relevant chunk IDs saves milliseconds and reduces database load Code complete for…

## Algoritmo: LRU vs LFU (Eviction Policy)
- ✅ sim=0.54 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch10`
  > Exact caching is also used for embedding-based retrieval to avoid redundant vector search. If an incoming query is already in the vector search cache, fetch the cached result. If not, perform a vector search for this…
- ✅ sim=0.53 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch06`
  > Long-term memory can be used to store the overflow from short-term memory. This operation depends on how much space you want to allocate for short-term memory. For a given query, the context input into the model…
- ✅ sim=0.52 [EN] — `lru_cache Technical Details · `fastapi-docs-en/docs/advanced/settings.md``
  > `lru_cache` Technical Details `@lru_cache` modifies the function it decorates to return the same value that was returned the first time, instead of computing it again, executing the code of the function every time. So,…

## Model Routing
- ✅ sim=0.71 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch10`
  > Because routing is usually done by models, I put routing inside the Model API box in Figure 10-5. Like scorers, routers are typically smaller than models used for generation. Grouping routers together with other models…
- ✅ sim=0.68 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c31H`
  > 12.7 Task-Based Model Routing Not every task in an agent system requires the same model. A common source of unnecessary cost is using the most capable model for every step in the workflow. This can be simple to…
- ✅ sim=0.64 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c355`
  > Model routing addresses that problem. The system can choose different models for different tasks. Simple classification, extraction, and formatting tasks may use smaller or cheaper models. Complex reasoning, high-risk…

## Prompt Compression
- ✅ sim=0.59 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch09`
  > A prompt cache is visualized in Figure 9-17. It’s also called a context cache or prefix cache. Figure 9-17. With a prompt cache, overlapping segments in different prompts can be cached and reused. For applications with…
- ✅ sim=0.58 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ix01_split_001`
  > prompt caching, Prompt caching-Prompt caching prompt catalogs, Organize and Version Prompts prompt engineering, Prompt Engineering-Summarybasics, Introduction to Prompting-Context Length and Context Efficiencycontext…
- ✅ sim=0.55 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/cCD`
  > Prompt engineering is the practice of carefully designing and refining prompts to optimize the quality, relevance, and accuracy of the model’s output. By guiding the structure, wording, and context of the prompt, prompt…

## Módulos shared/ Usados Neste Módulo
- ✅ sim=0.50 [EN] — `Context Engineering for Multi-Agent Systems · Denis Rothman · 2025 · EPUB/Chapter_5`
  > This output clearly demonstrates that the hardened Context Engine is working as intended. It successfully planned a dynamic workflow, orchestrated multiple agents, and produced a cohesive result idx_777f9040through…


---

**Resumo:** 8/8 conceitos com suporte (0 sem cobertura).
