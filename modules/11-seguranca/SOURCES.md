# 🗺️ Mapa de Cobertura — 11-seguranca

> Gerado por `tools/coverage_map.py` (modo A). Ponteiros verificáveis para as
> fontes do corpus — **não** é texto autoral nem tradução. Quotes vêm crus da fonte.

_Conceitos analisados: 6 · limiar sim ≥ 0.50_

## Erros Comuns de Iniciantes
- ✅ sim=0.54 [EN] — `We Make Mistakes · `fastapi-docs-en/docs/deployment/concepts.md``
  > We Make Mistakes We, as humans, make **mistakes**, all the time. Software almost *always* has **bugs** hidden in different places. 🐛 And we as developers keep improving the code as we find those bugs and as we implement…
- ✅ sim=0.52 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HZ`
  > Avoiding Common Pitfalls in Idea Generation Ideas die long before a backtest ever sees them; they wither in quiet corners, assumptions left unspoken, data quietly poisoned, incentives that favor flash over…

## Prompt Injection
- ✅ sim=0.85 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/c198`
  > One form of prompt hacking is prompt injection, a more targeted and often malicious approach. Prompt injection involves crafting inputs that manipulate the model into generating responses or taking actions that the…
- ✅ sim=0.77 [EN] — `Context Engineering for Multi-Agent Systems · Denis Rothman · 2025 · EPUB/Chapter_7`
  > Prompt injection is an attack idx_f3ec49ccwhere malicious instructions, hidden within the data retrieved by the RAG system, are used to trick or hijack the final language model into performing an unintended action. It's…
- ✅ sim=0.77 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch05`
  > Jailbreaking and Prompt Injection Jailbreaking a model means trying to subvert a model’s safety features. As an example, consider a customer support bot that isn’t supposed to tell you how to do dangerous things.…

## Jailbreak Detection
- ✅ sim=0.56 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch05`
  > AI safety, like any area of cybersecurity, is an evolving cat-and-mouse game where developers continuously work to neutralize known threats while attackers devise new ones. Here are a few common approaches that have…
- ✅ sim=0.54 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch05`
  > Jailbreaking and Prompt Injection Jailbreaking a model means trying to subvert a model’s safety features. As an example, consider a customer support bot that isn’t supposed to tell you how to do dangerous things.…
- ✅ sim=0.53 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch05`
  > Another internet favorite attack was the grandma exploit, in which the model is asked to act as a loving grandmother who used to tell stories about the topic the attacker wants to know about, such as the steps to…

## Content Filtering
- ✅ sim=0.55 [EN] — `Context Engineering for Multi-Agent Systems · Denis Rothman · 2025 · EPUB/Chapter_8`
  > Context Engine workflow with moderation: The workflow is initiated when a user submits a user goal to the system. This request represents the starting point of the reasoning loop. New function—pre-flight moderation…
- ✅ sim=0.54 [EN] — `Context Engineering for Multi-Agent Systems · Denis Rothman · 2025 · EPUB/Chapter_10`
  > At runtime: Before any retrieved context is passed to an agent like the Researcher or Writer, it should be re-sanitized. This protects against the possibility that a vulnerability was missed during ingestion and…
- ✅ sim=0.53 [EN] — `Context Engineering for Multi-Agent Systems · Denis Rothman · 2025 · EPUB/Chapter_8`
  > print("Moderation Report:") pprint.pprint(moderation_report) if moderation_report["flagged"]: print("\n🛑 Generated output failed post-flight moderation and will be redacted.") result = "[Content flagged as potentially…

## Data Leakage Protection
- ✅ sim=0.59 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3H3`
  > Data Privacy and Security Concerns Data is not neutral, every row you ingest brings legal duties, hostile curiosity, and new nodes of fragility. Picture a backtest that gleams in slides and meetings until one morning a…
- ✅ sim=0.56 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch10`
  > An employee copies the company’s secret or a user’s private information into a prompt and sends it to a third-party API.1 An application developer puts the company’s internal policies and data into the application’s…
- ✅ sim=0.54 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3H3`
  > Concrete defenses are non-negotiable. Pseudonymize at ingest and keep the reversible mapping inside an HSM with strict key rotation. Use differential privacy during analytics and training, an epsilon that looks modest…

## Principle of Least Privilege
- ✅ sim=0.52 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HF`
  > Design security as primitives, not as afterthoughts. Identity must be explicit and ephemeral: each human and machine identity should be short‑lived where possible and governed by least privilege. Map roles to concrete…


---

**Resumo:** 6/6 conceitos com suporte (0 sem cobertura).
