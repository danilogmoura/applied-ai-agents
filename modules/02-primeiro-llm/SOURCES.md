# 🗺️ Mapa de Cobertura — 02-primeiro-llm

> Gerado por `tools/coverage_map.py` (modo A). Ponteiros verificáveis para as
> fontes do corpus — **não** é texto autoral nem tradução. Quotes vêm crus da fonte.

_Conceitos analisados: 19 · limiar sim ≥ 0.50_

## System vs. User Messages
- ✅ sim=0.59 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch05`
  > System Prompt and User Prompt Many model APIs give you the option to split a prompt into a system prompt and a user prompt. You can think of the system prompt as the task description and the user prompt as the task.…
- ✅ sim=0.54 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/c198`
  > Before going further into prompting, let’s distinguish prompts and system prompts. Below, we explore this with two different use cases: story generation and product description. In both examples, we highlight the…
- ✅ sim=0.51 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_12`
  > 它和System Prompt有什么区别（Skills vs System Prompt） 你可能会想：这不就是一个System Prompt吗？写一堆指令让AI遵守，有什么新鲜的？ 区别很大。 System Prompt是全局的、永久加载的。你在CLAUDE.md里写的所有规则，每一轮对话AI都会看到。它像是公司的规章制度，所有员工都要遵守，不管你是做财务还是做市场。…

## A API da OpenAI
- ✅ sim=0.69 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch04`
  > Figure 4-6. An inference service runs the model and provides an interface for users to access the model. After developing a model, a developer can choose to open source it, make it accessible via an API, or both. Many…
- ✅ sim=0.68 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/cCD`
  > Tutorial: Translation with LLMs (GPT-3.5 API) Now, combining all we have learned, let’s understand how to interact with OpenAI’s proprietary LLM through their API, instructing the model to perform translation. An API…
- ✅ sim=0.64 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/cP9`
  > OpenAI developed a new version of their GPT-4 model, GPT-4o, in May 2024. The model is currently their flagship model. What distinguishes it from its predecessors is its multi-modality; it now accepts input combinations…

## Alternativas à OpenAI
- ✅ sim=0.62 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch04`
  > Figure 4-6. An inference service runs the model and provides an interface for users to access the model. After developing a model, a developer can choose to open source it, make it accessible via an API, or both. Many…
- ✅ sim=0.58 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/cP9`
  > Language models can be categorized into three types: proprietary, open models, and open-source models. Proprietary models, such as OpenAI’s GPT-4 and Anthropic’s Claude 3, are only accessible through paid APIs or web…
- ✅ sim=0.58 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/cP9`
  > Some companies offering proprietary models, like OpenAI, allow fine-tuning for their LLMs, enabling users to optimize task performance for specific use cases and within defined usage policies. Open weights and…

## Estimativa de Custos
- ✅ sim=0.52 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch01`
  > Cost metrics: how much it costs per inference request. Other metrics such as interpretability and fairness. If you’re not yet sure what metrics you want to use, don’t worry. The rest of the book will cover many of these…

## Depuração: Erros Comuns de API
- ✅ sim=0.54 [EN] — `Handling Errors · `fastapi-docs-en/docs/tutorial/handling-errors.md``
  > Handling Errors There are many situations in which you need to report an error to a client that is using your API. This client could be a browser with a frontend, a code from someone else, an IoT device, etc. You could…
- ✅ sim=0.53 [ZH] — `0.56.1 (2020-06-12) · `fastapi-docs-en/docs/release-notes.md``
  > /tiangolo/fastapi/pull/1365) by [@mrosales]( github.com/mrosales). * Fix/remove incorrect error logging when a client sends invalid payloads. PR [#1351]( github.com/tiangolo/fastapi/pull/1351) by [@dbanty](…
- ✅ sim=0.53 [EN] — `Small Errors Automatically Handled · `fastapi-docs-en/docs/deployment/concepts.md``
  > Small Errors Automatically Handled When building web APIs with FastAPI, if there's an error in our code, FastAPI will normally contain it to the single request that triggered the error. 🛡 The client will get a **500…

## O Problema da Alucinação
- ✅ sim=0.76 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/c13B`
  > Understanding Hallucinations and Bias Off-the-shelf foundation models have limitations that restrict their direct use in production. At the core, large language models (LLMs) learn from a vast amount of data collected…
- ✅ sim=0.71 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > The first hypothesis, originally expressed by Ortega et al. at DeepMind in 2021, is that a language model hallucinates because it can’t differentiate between the data it’s given and the data it generates. Let’s go…
- ✅ sim=0.69 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > While hallucination became a prominent issue with the rise of LLMs, hallucination was a common phenomenon for generative models even before the term foundation model and the transformer architecture were introduced.…

## Algoritmo: Byte Pair Encoding (BPE)
- ✅ sim=0.73 [EN] — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_02`
  > Popular subword tokenization algorithms include byte pair encoding (BPE), WordPiece, and SentencePiece, which learn to identify frequently occurring character sequences in a training corpus and create a vocabulary of…
- ✅ sim=0.71 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/cCD`
  > Alternatively, tokenization can be done by separating text based on both white spaces and punctuation; the output would be: ["The", "child", "'", "s", "coloring", "book", "."] The tokenization process is…
- ✅ sim=0.61 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch03`
  > Bits-per-Character and Bits-per-Byte One unit of entropy and cross entropy is bits. If the cross entropy of a language model is 6 bits, this language model needs 6 bits to represent each token. Since different models…

## Temperature e Sampling: Controle de Criatividade
- ✅ sim=0.72 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/cVZ`
  > Practical takeaway: Low temperature is useful for stable, controlled, and repeatable output. High temperature is useful for exploration, variation, and creativity. As a concrete example, a compliance assistant, support…
- ✅ sim=0.67 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > [ x 1 , x 2 , . . . , x N ] The probability for the ith token, p i is computed as follows: p i = softmax ( x i ) = e x i ∑ j e x j Sampling Strategies The right sampling strategy can make a model generate responses more…
- ✅ sim=0.62 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > Temperature is a constant used to adjust the logits before the softmax transformation. Logits are divided by temperature. For a given temperature T, the adjusted logit for the ith token is x i T . Softmax is then…

## Token
- ✅ sim=0.59 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_24`
  > Token经济学（Token Economics） 聊点实际的。一个Skill占多少token？多个Skill同时加载会不会打架？ 先说体量。1000字的中文大约是1500-2000 token。一个典型的Skill（1000-2000字）大约占2000-4000 token。Claude的上下文窗口是100万token，单个Skill只占0.2%-0.4%。看起来微不足道，对吧？…
- ✅ sim=0.59 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c4MY`
  > Token budget — The practical limit on how many tokens can be used for prompts, retrieved context, history, and output within a request. Tokenization — The process of breaking text into tokens before it is converted into…

## Temperature
- ✅ sim=0.56 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > Temperature is a constant used to adjust the logits before the softmax transformation. Logits are divided by temperature. For a given temperature T, the adjusted logit for the ith token is x i T . Softmax is then…
- ✅ sim=0.54 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > Figure 2-16 shows the softmax probabilities for tokens A and B at different temperatures. As the temperature gets closer to 0, the probability that the model picks token B becomes closer to 1. In our example, for a…
- ✅ sim=0.54 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/c13B`
  > High temperature (i.e., > 1): As temperatures rise, the logits decrease, resulting in a more uniform softmax output. This enhances the possibility of the model selecting fewer likely terms, resulting in more diversified…

## Prompt
- ✅ sim=0.68 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/c198`
  > Prompting and Prompt Engineering Whether using or building AI, you need to know how best to communicate with it. This is especially true for generative AI models, which primarily interact with the user through language…
- ✅ sim=0.67 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch05`
  > This chapter covers both how to write effective prompts and how to defend your applications against prompt attacks. Before diving into all the fun applications you can build with prompts, let’s first start with the…
- ✅ sim=0.64 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c160`
  > A real prompt stack includes: A system prompt defining role and rules Retrieved context from documents Few-shot examples Formatting requirements The user’s actual question The effective prompt can be much larger and…

## API Key
- ✅ sim=0.67 [EN] — `API Key Security Schemes · `fastapi-docs-en/docs/reference/security/index.md``
  > API Key Security Schemes ::: fastapi.security.APIKeyCookie ::: fastapi.security.APIKeyHeader ::: fastapi.security.APIKeyQuery
- ✅ sim=0.60 [EN] — `HTTPS for Developers · `fastapi-docs-en/docs/deployment/https.md``
  > HTTPS for Developers Here's an example of how an HTTPS API could look, step by step, paying attention mainly to the ideas important for developers
- ✅ sim=0.60 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/cCD`
  > Tutorial: Translation with LLMs (GPT-3.5 API) Now, combining all we have learned, let’s understand how to interact with OpenAI’s proprietary LLM through their API, instructing the model to perform translation. An API…

## Latency
- ✅ sim=0.62 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c30B`
  > 12.5 Where Latency Comes From Latency in agent systems has several sources. Unlike a traditional application where one database call or one downstream service may dominate response time, an agent system often spreads…
- ✅ sim=0.61 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch09`
  > Latency, TTFT, and TPOT Latency measures the time from when users send a query until they receive the complete response. For autoregressive generation, especially in the streaming mode, the overall latency can be broken…
- ✅ sim=0.59 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch04`
  > There are multiple metrics for latency for foundation models, including but not limited to time to first token, time per token, time between tokens, time per query, etc. It’s important to understand what latency metrics…

## Fallback
- ✅ sim=0.66 [EN] — `Disable Fallback · `fastapi-docs-en/docs/tutorial/frontend.md``
  > Disable Fallback If you don't want to serve a fallback file for missing frontend paths, use `fallback=None`: Then missing frontend paths return the normal `404`
- ✅ sim=0.61 [EN] — `Fallback Auto · `fastapi-docs-en/docs/tutorial/frontend.md``
  > Fallback Auto By default, `app.frontend()` uses `fallback="auto"`. If there is a `404.html` file in the frontend directory, missing frontend paths serve that file with status code `404`. Otherwise, if there is an…
- ✅ sim=0.57 [EN] — `Fixes · `fastapi-docs-en/docs/release-notes.md``
  > Fixes * 🐛 Fix blocking frontend fallback file checks. PR [#16503]( github.com/fastapi/fastapi/pull/16503) by [@tiangolo]( github.com/tiangolo)

## JSON
- ✅ sim=0.66 [EN] — `JSON Lines · `fastapi-docs-en/docs/tutorial/stream-json-lines.md``
  > JSON Lines In these cases, it's common to send "**JSON Lines**", which is a format where you send one JSON object per line. A response would have a content type of `application/jsonl` (instead of `application/json`) and…
- ✅ sim=0.61 [EN] — `Data "schema" · `fastapi-docs-en/docs/tutorial/first-steps.md``
  > Data "schema" The term "schema" might also refer to the shape of some data, like a JSON content. In that case, it would mean the JSON attributes, and data types they have, etc
- ✅ sim=0.59 [EN] — `Convert any Data to JSON-compatible · `fastapi-docs-en/docs/how-to/general.md``
  > Convert any Data to JSON-compatible To convert any data to JSON-compatible, read the docs for [Tutorial - JSON Compatible Encoder](../tutorial/encoder.md)

## Avançado: Softmax + Temperature
- ✅ sim=0.75 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > Temperature is a constant used to adjust the logits before the softmax transformation. Logits are divided by temperature. For a given temperature T, the adjusted logit for the ith token is x i T . Softmax is then…
- ✅ sim=0.73 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > [ x 1 , x 2 , . . . , x N ] The probability for the ith token, p i is computed as follows: p i = softmax ( x i ) = e x i ∑ j e x j Sampling Strategies The right sampling strategy can make a model generate responses more…
- ✅ sim=0.72 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > Figure 2-16 shows the softmax probabilities for tokens A and B at different temperatures. As the temperature gets closer to 0, the probability that the model picks token B becomes closer to 1. In our example, for a…

## Exemplo Completo: Classificação de Ticket
- ✅ sim=0.53 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch05`
  > Intent classification: identify the intent of the request. Generating response: based on this intent, instruct the model on how to respond. If there are ten possible intents, you’ll need ten different prompts. The…

## Regras de Segurança
- ✅ sim=0.50 [EN] — `Read the Tutorial first · `fastapi-docs-en/docs/advanced/security/index.md``
  > Read the Tutorial first The next sections assume you already read the main [Tutorial - User Guide: Security](../../tutorial/security/index.md). They are all based on the same concepts, but allow some extra…

## Livros
- ✅ sim=0.53 [EN] · _ponte: “语料库”_ — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_04`
  > To better understand the context in which large datasets are used, it is helpful to explore a specific example. One such dataset used in the preceding code snippet is the Colossal Clean Crawled Corpus (C4) dataset,…


---

**Resumo:** 19/19 conceitos com suporte (0 sem cobertura).
