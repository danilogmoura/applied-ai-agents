# 🗺️ Mapa de Cobertura — 10-avaliacao

> Gerado por `tools/coverage_map.py` (modo A). Ponteiros verificáveis para as
> fontes do corpus — **não** é texto autoral nem tradução. Quotes vêm crus da fonte.

_Conceitos analisados: 8 · limiar sim ≥ 0.50_

## O Problema da Qualidade Invisível
- ✅ sim=0.62 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c3GH`
  > Evaluation earns it’s real place when it changes engineering decisions. A score that nobody acts on is decoration. A failed test that does not lead to a better prompt, stronger retrieval, safer tool boundary, clearer…
- ✅ sim=0.62 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_2`
  > This gives you a quantifiable quality metric you can track over time. Figure 2.10: The LLM-as-a-Judge evaluation pipeline for CI/CD Pattern: new observability metrics Existing performance dashboards (CPU, RAM, 5xx…
- ✅ sim=0.61 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_62`
  > Improve模式：自动改进（Improve Mode） Eval告诉你哪里不好，Improve帮你改好。 它读取Eval的评估结果，针对薄弱环节进行定向改进。改完之后你可以再运行一次Eval，看产出质量是否真的提升了。这就形成了一个「评估 → 改进 → 再评估」的循环。…

## Erros Comuns de Iniciantes
- ✅ sim=0.54 [EN] — `We Make Mistakes · `fastapi-docs-en/docs/deployment/concepts.md``
  > We Make Mistakes We, as humans, make **mistakes**, all the time. Software almost *always* has **bugs** hidden in different places. 🐛 And we as developers keep improving the code as we find those bugs and as we implement…
- ✅ sim=0.52 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HZ`
  > Avoiding Common Pitfalls in Idea Generation Ideas die long before a backtest ever sees them; they wither in quiet corners, assumptions left unspoken, data quietly poisoned, incentives that favor flash over…

## Pipeline de Avaliação
- ✅ sim=0.66 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c3DA`
  > The output is what the user receives. The path is what tells me whether the system deserved to produce it. 14.3 Evaluation as a Pipeline Evaluation should be a repeatable pipeline, not occasional manual checking. Manual…
- ✅ sim=0.58 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch04`
  > Run experiments with your own evaluation pipeline to find the best model, again, balancing all your objectives. Continually monitor your model in production to detect failure and collect feedback to improve your…
- ✅ sim=0.58 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c3DA`
  > The output of an evaluation pipeline should not be only pass or fail. That is too thin for agent systems. The pipeline should produce signals the team can act on: weak examples, regression reports, cost movement,…

## Golden Dataset
- ✅ sim=0.53 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch08`
  > UC Irvine’s Machine Learning Repository and OpenML are two older dataset repositories, each hosting several thousand datasets. The Open Data Network lets you search among tens of thousands of datasets. Cloud service…
- ✅ sim=0.52 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch08`
  > Manually annotate these 2,000 synthetic instructions. Now your dataset has a total of 11,000 examples. This is, of course, an oversimplification of the actual dataset curation process, with the vast majority of steps…
- ✅ sim=0.51 [EN] — `Gold Sponsors · `fastapi-docs-en/docs/index.md``
  > Gold Sponsors <div class="fastapi-sponsors fastapi-sponsors--gold"> {% for sponsor in sponsors.gold -%} <a class="fastapi-sponsors__card fastapi-sponsors__card--gold" href="{{ sponsor.url }}" title="{{ sponsor.title…

## Métricas de Avaliação
- ✅ sim=0.64 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch04`
  > Before developing AI evaluation metrics, it’s crucial to first understand the business metrics you’re targeting. Many applications focus on stickiness metrics, such as daily, weekly, or monthly active users (DAU, WAU,…
- ✅ sim=0.62 [EN] — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_14`
  > Design robust evaluation criteria: Develop clear, quantifiable metrics for assessing performance. This might involve the following:Creating rubrics for human evaluation Defining automated scoring mechanisms Establishing…
- ✅ sim=0.62 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch04`
  > Tie evaluation metrics to business metrics Within a business, an application must serve a business goal. The application’s metrics must be considered in the context of the business problem it’s built to solve. For…

## LLM-as-a-Judge
- ✅ sim=0.68 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c3GH`
  > This is useful because many LLM outputs cannot be evaluated by exact match. A judge model can catch missing details, weak explanations, unsupported claims, poor grounding, unsafe recommendations, or low usefulness. But…
- ✅ sim=0.66 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c3GH`
  > The dataset should not exist to make the system look good. It should exist to show where the system is still weak. 14.5 AI-as-a-Judge Manual review is valuable, but it does not scale well. A team can manually inspect…
- ✅ sim=0.65 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch03`
  > Why AI as a Judge? AI judges are fast, easy to use, and relatively cheap compared to human evaluators. They can also work without reference data, which means they can be used in production environments where there is no…

## Testes A/B
- ✅ sim=0.56 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_5`
  > These are non-negotiable, high-value queries where failure is not an option (e.g. 'iphone' must return Apple products). Implementation Use pytest to block deployments if core queries degrade. # test_search_quality.py…
- ✅ sim=0.52 [EN] — `Testing: extended example · `fastapi-docs-en/docs/tutorial/testing.md``
  > Testing: extended example Now let's extend this example and add more details to see how to test different parts
- ✅ sim=0.51 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_5`
  > Only changes that show a statistically significant improvement are gradually rolled out to all users. Control (A): Keyword search + simple vector (baseline). Treatment (B): The new hybrid + re-ranking pipeline. Metric…

## Benchmarking Regressivo
- ✅ sim=0.53 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_62`
  > Benchmark模式：统计验证（Benchmark Mode） Benchmark模式解决的是另一个问题：Skill的触发精度。 它的做法是优化Skill的description字段。具体来说，它会生成各种触发场景的查询语句，测试Skill是否在该触发的时候触发、不该触发的时候保持沉默。通过反复调整description的措辞，提升触发的精准度。…
- ✅ sim=0.51 [EN] — `LLM Design Patterns · Ken Huang · 2025 · OEBPS/B31249_23`
  > Benchmarking: Using standardized test sets designed to evaluate abstract reasoning and planning capabilities It is also crucial to keep ethical considerations in mind while doing any evaluation: Bias amplification:…


---

**Resumo:** 8/8 conceitos com suporte (0 sem cobertura).
