# 🗺️ Mapa de Cobertura — p3a3_planning

> Gerado por `tools/coverage_map.py` (modo A). Ponteiros verificáveis para as
> fontes do corpus — **não** é texto autoral nem tradução. Quotes vêm crus da fonte.

_Conceitos analisados: 6 · limiar sim ≥ 0.50_

## Erros Comuns de Iniciantes
- ✅ sim=0.54 [EN] — `We Make Mistakes · `fastapi-docs-en/docs/deployment/concepts.md``
  > We Make Mistakes We, as humans, make **mistakes**, all the time. Software almost *always* has **bugs** hidden in different places. 🐛 And we as developers keep improving the code as we find those bugs and as we implement…
- ✅ sim=0.52 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HZ`
  > Avoiding Common Pitfalls in Idea Generation Ideas die long before a backtest ever sees them; they wither in quiet corners, assumptions left unspoken, data quietly poisoned, incentives that favor flash over…

## Circuit Breaker Pattern
- ✅ sim=0.62 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_2`
  > This pattern brings some significant benefits: Abstraction : Can switch models (e.g. GPT-5 for Claude 3 Opus) with a config change, not a re-deployment Centralized c ontrol : All other resilience, cost, and monitoring…
- ✅ sim=0.59 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c31H`
  > Circuit breakers protect the system when a dependency is unhealthy. If a model provider, retrieval service, or tool server keeps failing, the runtime should stop sending more traffic to it for a period of time. This…
- ✅ sim=0.55 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_7`
  > 7 Glossary A Abstract s yntax t ree (AST) : A structured, tree-like representation of source code that captures the hierarchical relationships between classes, functions, and methods. Used in system design for semantic…

## Checkpoints
- ✅ sim=0.52 [EN] — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_10`
  > 10 Checkpointing and Recovery Checkpointing and recovery refer to the process of saving the state of a system, application, or model at specific intervals (checkpointing) and restoring it from a saved state in case of…
- ✅ sim=0.51 [EN] — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_10`
  > Let’s define the function (load_checkpoint_efficient) to load the checkpoint in ZIP format: def load_checkpoint_efficient(self, checkpoint_path): checkpoint = {} with zipfile.ZipFile(checkpoint_path, 'r') as zipf: for…

## Trade-offs de Resiliência
- ✅ sim=0.54 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3H3`
  > alert_flag = (ratio < 0.8) or (fragility < 0.95) That snippet is small and blunt: it won’t prove fairness, but it surfaces brittle dependencies before they cascade. Regulation will try to corral these risks, and…
- ✅ sim=0.53 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c0`
  > Here is the paradox that eats strategies: the more you squeeze a backtest for every basis point, the more brittle it becomes in the wild. Optimization coaxes models to fit noise, to learn idiosyncrasies of vendors, and…
- ✅ sim=0.52 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c2N0`
  > Resilience must be designed into the runtime from the beginning. A resilient system does not assume that every step will succeed. It defines in advance how the workflow should respond when a step fails, when it should…

## Simulação de Serviço
- ✅ sim=0.53 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch08`
  > Perturbation can also be used for texts. For example, to train BERT, the authors replaced 1.5% of the tokens with random words (Devlin et al., 2018). They found this perturbation led to a small performance boost. Visual…
- ✅ sim=0.52 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch08`
  > Simulations are common to generate data to teach models to use tools. As mentioned earlier, human-generated actions might not always be the most efficient for AI agents. Simulations might help uncover actions that…
- ✅ sim=0.51 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HR`
  > Governance becomes operational rather than bureaucratic when immutable decision records, time-stamped approvals, and deterministic simulation modes are part of the pipeline. Runbook rehearsals against synthetic…

## Arquitetura do Planner Resiliente
- ✅ sim=0.53 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c2N0`
  > Resilience must be designed into the runtime from the beginning. A resilient system does not assume that every step will succeed. It defines in advance how the workflow should respond when a step fails, when it should…
- ✅ sim=0.53 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c2N0`
  > This pattern aligns more naturally with the architecture developed across the earlier chapters. The model remains the reasoning core. The orchestrator controls execution. Tools expose external capabilities. Retrieval…
- ✅ sim=0.50 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3GY`
  > Architectural hygiene is the most actionable lever you own. Favor narrow, well‑documented interfaces over internal monoliths; version every model and schema; codify data contracts and compatibility tests; make feature…


---

**Resumo:** 6/6 conceitos com suporte (0 sem cobertura).
