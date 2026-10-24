# 🗺️ Mapa de Cobertura — 06-tool-calling

> Gerado por `tools/coverage_map.py` (modo A). Ponteiros verificáveis para as
> fontes do corpus — **não** é texto autoral nem tradução. Quotes vêm crus da fonte.

_Conceitos analisados: 11 · limiar sim ≥ 0.50_

## Dependências Necessárias
- ✅ sim=0.70 [EN] — `Dependencies - Depends() and Security() · `fastapi-docs-en/docs/reference/dependencies.md``
  > Dependencies - `Depends()` and `Security()`

## Do Texto à Ação
- ✅ sim=0.62 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/cEC`
  > Once tools enter the picture, a user request no longer needs to remain a pure language task. The system can fetch live data, apply business rules, inspect system state, and participate in multi-step workflows. Figure…
- ✅ sim=0.61 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/c3WW`
  > The experiment showed that the chatbot directs to inaccurate text portions. While the answer was contextually similar, it wasn’t correct. 💡The Preprocessed Text/Label and Preprocessed Graphs for this section are…
- ✅ sim=0.60 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch06`
  > Even though agents are novel, they are built upon concepts that have already appeared in this book, including self-critique, chain-of-thought, and structured outputs. Agent Overview The term agent has been used in many…

## Erros Comuns de Iniciantes
- ✅ sim=0.54 [EN] — `We Make Mistakes · `fastapi-docs-en/docs/deployment/concepts.md``
  > We Make Mistakes We, as humans, make **mistakes**, all the time. Software almost *always* has **bugs** hidden in different places. 🐛 And we as developers keep improving the code as we find those bugs and as we implement…
- ✅ sim=0.52 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HZ`
  > Avoiding Common Pitfalls in Idea Generation Ideas die long before a backtest ever sees them; they wither in quiet corners, assumptions left unspoken, data quietly poisoned, incentives that favor flash over…

## Níveis de Risco
- ✅ sim=0.53 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_37`
  > Skill的四个层级（Four Levels of Skills） Skills有一个层级体系。从最广到最窄： 理解层级关系的关键是优先级：Enterprise级优先级最高，Personal次之，Project最低。也就是说，公司统一规范会覆盖个人偏好，个人偏好会覆盖项目设置。这个设计是有道理的——如果公司规定了代码安全审查标准，你不能在项目里把它关掉。Plugin级通过命名空间隔离，不和其他层级冲突。…

## Tool Calling
- ✅ sim=0.69 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c1DF`
  > The model selected the capability; trusted backend code performed the operation. Figure 4.2: High-level function-calling flow in an LLM system 4.3 Function Calling as a Controlled Contract Function calling is a core…
- ✅ sim=0.66 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch06`
  > Rewrite the functions themselves to make them simpler, such as refactoring a complex function into two simpler functions. Use a stronger model. In general, stronger models are better at planning. Finetune a model for…
- ✅ sim=0.65 [EN] — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_25`
  > This ToolKit class provides an interface for the LLM to interact with external tools, simulating API calls and data processing tasks. Implementing automatic tool selection and use To enable LLMs to automatically select…

## JSON Schema
- ✅ sim=0.79 [EN] — `Data "schema" · `fastapi-docs-en/docs/tutorial/first-steps.md``
  > Data "schema" The term "schema" might also refer to the shape of some data, like a JSON content. In that case, it would mean the JSON attributes, and data types they have, etc
- ✅ sim=0.73 [EN] — `OpenAPI and JSON Schema · `fastapi-docs-en/docs/tutorial/first-steps.md``
  > OpenAPI and JSON Schema OpenAPI defines an API schema for your API. And that schema includes definitions (or "schemas") of the data sent and received by your API using **JSON Schema**, the standard for JSON data schemas
- ✅ sim=0.69 [EN] — `"Schema" · `fastapi-docs-en/docs/tutorial/first-steps.md``
  > "Schema" A "schema" is a definition or description of something. Not the code that implements it, but just an abstract description

## HITL
- ✅ sim=0.69 [EN] · _ponte: “Human-in-the-loop”_ — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_03`
  > For critical applications, incorporate human validation into your augmentation pipeline. Human-in-the-loop (HITL) validation is a control mechanism used in AI pipelines where humans are deliberately inserted into…
- ✅ sim=0.66 [EN] · _ponte: “Human-in-the-loop”_ — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_6`
  > Human-in-the-loop A dedicated team of domain experts constantly reviews cases flagged by low system confidence scores or negative user feedback. This feedback loop is essential for quickly identifying drift and…
- ✅ sim=0.64 [EN] · _ponte: “Human-in-the-loop”_ — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch01`
  > It’s also important to clarify the role of humans in the application. Will AI provide background support to humans, make decisions directly, or both? For example, for a customer support chatbot, AI responses can be used…

## Whitelist
- ✅ sim=0.55 [EN] · _ponte: “allowlist”_ — `Wildcards · `fastapi-docs-en/docs/tutorial/cors.md``
  > Wildcards It's also possible to declare the list as `"*"` (a "wildcard") to say that all are allowed. But that will only allow certain types of communication, excluding everything that involves credentials: Cookies,…

## Risk Level
- ✅ sim=0.50 [EN] · _ponte: “风险等级”_ — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c0`
  > Risk management is taxonomy and control system braided into a single muscle: name the threats, measure their scale, and automate the corrective reflex. Think in five languages at once , market moves, liquidity and…

## Fine-tuned
- ✅ sim=0.68 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/c4KH`
  > Understanding Fine-Tuning While pre-training gives large language models (LLMs) a general understanding of language, it falls short for instruction-following tasks. LLMs are trained to predict the next token in its…
- ✅ sim=0.68 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_1`
  > Fine-tuning is the process of taking a general-purpose, pre-trained model (like an LLM) and training it a little bit more on a smaller, specific set of data to make it an expert at a single, specialized task. The model…
- ✅ sim=0.65 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch07`
  > When to Finetune Before jumping into different finetuning techniques, it’s necessary to consider whether finetuning is the right option for you. Compared to prompt-based methods, finetuning requires significantly more…

## Attention
- ✅ sim=0.56 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/cSF`
  > The animal didn’t cross the street because it was tired. When the model processes the word “it,” attention helps it determine that “it” refers to “animal,” not “street”. Attention improves on simpler architectures by…
- ✅ sim=0.56 [EN] — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_16`
  > Attention visualization techniques Attention mechanisms are a key component of transformer-based LLMs (see Chapter 1). Visualizing attention patterns can provide insights into how the model processes and attends to…
- ✅ sim=0.50 [EN] — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_16`
  > Py array. This matrix represents how much attention each token in the sequence gives to every other token. The token IDs are then converted back to readable tokens for labeling the axes of a heatmap. Using Seaborn’s…


---

**Resumo:** 11/11 conceitos com suporte (0 sem cobertura).
