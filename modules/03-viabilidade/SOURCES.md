# 🗺️ Mapa de Cobertura — 03-viabilidade

> Gerado por `tools/coverage_map.py` (modo A). Ponteiros verificáveis para as
> fontes do corpus — **não** é texto autoral nem tradução. Quotes vêm crus da fonte.

_Conceitos analisados: 11 · limiar sim ≥ 0.50_

## Métricas que Importam
- ✅ sim=0.62 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c3NZ`
  > Metrics turn runtime behavior into numbers. A single log can explain one event. A metric can show a pattern across hundreds, thousands, or millions of events. That is why metrics are essential for operating agent…
- ✅ sim=0.58 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch04`
  > Tie evaluation metrics to business metrics Within a business, an application must serve a business goal. The application’s metrics must be considered in the context of the business problem it’s built to solve. For…
- ✅ sim=0.58 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch10`
  > In this book, I’ll use the term “monitoring” to refer to the act of tracking a system’s information and “observability” to refer to the whole process of instrumentating, tracking, and debugging the system. Metrics When…

## Exemplo de Benchmark: IA vs Regras
- ✅ sim=0.62 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_62`
  > Benchmark模式：统计验证（Benchmark Mode） Benchmark模式解决的是另一个问题：Skill的触发精度。 它的做法是优化Skill的description字段。具体来说，它会生成各种触发场景的查询语句，测试Skill是否在该触发的时候触发、不该触发的时候保持沉默。通过反复调整description的措辞，提升触发的精准度。…
- ✅ sim=0.56 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch03`
  > Popular benchmarks for evaluating AI’s code generation capabilities, such as OpenAI’s HumanEval and Google’s MBPP (Mostly Basic Python Problems Dataset) use functional correctness as their metrics. Benchmarks for…
- ✅ sim=0.56 [EN] — `Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_1`
  > o pen w eights (Llama 3, Mistral) : We have full control of the data. This is required for strict air-gapped environments or for compliance. This trades operational complexity (GPU management) for compliance safety.…

## Demo: A Decisão em Código
- ✅ sim=0.54 [EN] — `How it looks · `fastapi-docs-en/docs/tutorial/security/first-steps.md``
  > How it looks Let's first just use the code and see how it works, and then we'll come back to understand what's happening

## Memorando Técnico
- ✅ sim=0.57 [EN] · _ponte: “Architecture Decision Record”_ — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3H7`
  > Technical choices matter only when married to plumbing that guarantees safe iteration. Architectures that separate ingestion, feature materialization, model inference, and execution orchestration reduce blast radius and…
- ✅ sim=0.54 [EN] · _ponte: “Architecture Decision Record”_ — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HZ`
  > Archive with purpose. When you kill an idea, document exactly why and what would resurrect it, a new data source, cheaper execution, or lower engineering cost, so future teams don’t reanimate dead work without new…
- ✅ sim=0.52 [EN] · _ponte: “Architecture Decision Record”_ — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3H3`
  > Logs aren’t enough; traces must tell causality and context. Each decision record should include the optimization objective used, data provenance flags, any overrides or human notes, and the conflict_score that…

## Trade-offs na Prática
- ✅ sim=0.52 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3H3`
  > Transparency is a discipline, not a feature toggle. Start with minimal, auditable artifacts and iterate toward richer explanations. Instrument everything with operational metrics, constrain data exposure with access…
- ✅ sim=0.51 [EN] — `AI Can Make You Smarter · Charles B_ Kreitzberg · 2026 · index_split_002`
  > and enjoyment. Now let me turn it around: if you instead choose to spend the evening with friends, what would be the opportunity cost of not writing? You said: Getting the work done, so adding pressure and feeling…
- ✅ sim=0.51 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c0`
  > Privacy and compliance impose measurable trade-offs. Differential privacy, synthetic data, and strict minimization reduce exposure at the cost of signal fidelity. Measure that utility‑privacy frontier empirically: run…

## Benchmark
- ✅ sim=0.66 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_62`
  > Benchmark模式：统计验证（Benchmark Mode） Benchmark模式解决的是另一个问题：Skill的触发精度。 它的做法是优化Skill的description字段。具体来说，它会生成各种触发场景的查询语句，测试Skill是否在该触发的时候触发、不该触发的时候保持沉默。通过反复调整description的措辞，提升触发的精准度。…
- ✅ sim=0.59 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/cCD`
  > 1. The BIG-Bench suite. Big-Bench is a suite of benchmarks comprising over 200 benchmarks testing a wide array of tasks, such as arithmetic operations (example: “Q: What is 132 plus 762? A: 894), transliteration from…
- ✅ sim=0.56 [EN] — `Building LLMs for Production · Peters, Louie & Bouchard, Louis-François · 2024 · OEBPS/c13B`
  > Extrinsic Metrics (Benchmarks) Benchmark tests are valuable tools for evaluating LLMs but have inherent limitations. Preventing data contamination from standard benchmarks leaking into training data is challenging, even…

## Latência P95
- ✅ sim=0.61 [EN] — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch09`
  > It’s more helpful to look at latency in percentiles, as they tell you something about a certain percentage of your requests. The most common percentile is the 50th percentile, abbreviated as p50 (median). If the median…
- ✅ sim=0.57 [EN] — `RAG in Practice · Hart, Nolan · 2026 · OEBPS/c175`
  > p50 = np.median(latencies) * 1000 p99 = np.percentile(latencies, 99) * 1000 print(f"P50: {p50:.1f} ms, P99: {p99:.1f} ms") No checklist replaces a real benchmark with your data and query patterns. The code snippet above…
- ✅ sim=0.53 [EN] — `RAG in Practice · Hart, Nolan · 2026 · OEBPS/c7R`
  > Reranking — Pairwise scoring per candidate. The bottleneck shifts with top-k. Mitigations: prune candidates before reranking, use a lightweight cross-encoder, or cache reranking scores for frequent queries. Retrieval —…

## Threshold
- ✅ sim=0.53 [EN] · _ponte: “decision threshold”_ — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HV`
  > from scipy.stats import norm def z_score(live_series, backtest_series): mu_bt = backtest_series.mean() sigma_bt = backtest_series.std(ddof=1) + 1e-9 return (live_series.mean() - mu_bt) / sigma_bt def breach_prob(z):…
- ✅ sim=0.52 [EN] · _ponte: “decision threshold”_ — `Agentic RAG Systems · Norman, Raymond · 2026 · OEBPS/c2W0`
  > PRODUCTION INSIGHT — Tune the Threshold Against Real Production Traffic The default similarity thresholds suggested by tutorials are usually wrong for production. The right threshold depends on the embedding model, the…
- ✅ sim=0.52 [EN] · _ponte: “decision threshold”_ — `Cracking the AI Agent Interview · Sun, Wei · 2026 · OEBPS/c644`
  > 4 if count / len(results) >= threshold: 184 5 return winner 6 else: 7 raise NoConsensusError("No majority reached") When to use: Critical decisions where the cost of a wrong answer is high. Increases cost (N× LLM calls)…

## Memorando
- ✅ sim=0.57 [EN] · _ponte: “Architecture Decision Record”_ — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3H7`
  > Technical choices matter only when married to plumbing that guarantees safe iteration. Architectures that separate ingestion, feature materialization, model inference, and execution orchestration reduce blast radius and…
- ✅ sim=0.54 [EN] · _ponte: “Architecture Decision Record”_ — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HZ`
  > Archive with purpose. When you kill an idea, document exactly why and what would resurrect it, a new data source, cheaper execution, or lower engineering cost, so future teams don’t reanimate dead work without new…
- ✅ sim=0.52 [EN] · _ponte: “Architecture Decision Record”_ — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3H3`
  > Logs aren’t enough; traces must tell causality and context. Each decision record should include the optimization objective used, data provenance flags, any overrides or human notes, and the conflict_score that…

## Break-even
- ⚪ **Sem cobertura clara nas fontes** (melhor sim=0.42).

## Heurística
- ✅ literal [EN] · _citação literal: “Heuristic”_ — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > To avoid scrutiny from both the public and competitors, many companies have stopped disclosing this information. Some teams use heuristics to filter out low-quality data from the internet
- ✅ literal [EN] · _citação literal: “Heuristic”_ — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > For example, in a self-reported survey, 90% of volunteer labelers identified as male (Köpf et al., 2023). DeepMind used simple heuristics to filter for conversations from internet data to train their model Gopher
- ✅ literal [EN] · _citação literal: “Heuristic”_ — `AI Engineering · Chip Huyen · 2024 · OEBPS/ch02`
  > OpenAI (2021) found that sampling more outputs led to better performance, but only up to 400 outputs. You can also use application-specific heuristics to select the best response


---

**Resumo:** 10/11 conceitos com suporte (1 sem cobertura).
