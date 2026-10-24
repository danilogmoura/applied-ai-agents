# 🗺️ Mapa de Cobertura — p10_skills

> Gerado por `tools/coverage_map.py` (modo A). Ponteiros verificáveis para as
> fontes do corpus — **não** é texto autoral nem tradução. Quotes vêm crus da fonte.

_Conceitos analisados: 9 · limiar sim ≥ 0.50_

## Erros Comuns de Iniciantes
- ✅ sim=0.54 [EN] — `We Make Mistakes · `fastapi-docs-en/docs/deployment/concepts.md``
  > We Make Mistakes We, as humans, make **mistakes**, all the time. Software almost *always* has **bugs** hidden in different places. 🐛 And we as developers keep improving the code as we find those bugs and as we implement…
- ✅ sim=0.52 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HZ`
  > Avoiding Common Pitfalls in Idea Generation Ideas die long before a backtest ever sees them; they wither in quiet corners, assumptions left unspoken, data quietly poisoned, incentives that favor flash over…

## Interface Padrão de uma Skill
- ✅ sim=0.68 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_10`
  > 拆解一个最简单的Skill（Anatomy of a Simple Skill） 先看一个最小的例子。假设你每周都要写团队周报，格式固定，但每次都要跟AI解释一遍。你可以把它做成一个Skill： --- name: weekly-report description: | 生成团队周报。当用户提到「周报」「weekly report」「本周总结」时使用此skill。 --- # 周报生成 1. 询问本周完成的主要工作 2.…
- ✅ sim=0.67 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_29`
  > 开放标准：agentskills.io（The Open Standard） 先说标准本身。2025年12月，Anthropic把Agent Skills发布为开放标准，网站是agentskills.io，官方仓库在github.com/anthropics/skills。到2026年4月，已经有20多个AI产品采纳了这个标准。 标准的核心其实非常简单：一个Skill就是一个SKILL.md文件。标准定义了三件事： ● 格式：YAML…
- ✅ sim=0.66 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_80`
  > 市场」的演进。两年前大家分享Prompt，但Prompt太碎片化了，没有结构，没有版本管理，换个模型可能就不好使了。Skill解决了这些问题，它有标准格式、有元数据、有触发条件、可以渐进式加载。Skill就是Prompt的升级版，有了固定格式、有了版本管理、有了标准。

## Versionamento Semântico
- ✅ sim=0.59 [EN] — `About versions · `fastapi-docs-en/docs/deployment/versions.md``
  > About versions Following the Semantic Versioning conventions, any version below `1.0.0` could potentially add breaking changes. FastAPI also follows the convention that any "PATCH" version change is for bug fixes and…
- ✅ sim=0.57 [EN] — `About FastAPI versions · `fastapi-docs-en/docs/deployment/versions.md``
  > About FastAPI versions **FastAPI** is already being used in production in many applications and systems. And the test coverage is kept at 100%. But its development is still moving quickly. New features are added…
- ✅ sim=0.53 [EN] — `Systems Thinking for Agentic AI · Ediz Najim · 2026 · OEBPS/c160`
  > 3.9 Prompt Versioning As soon as prompts begin to affect live system behavior, they need to be managed properly. This leads to prompt versioning. Prompt versioning means tracking and managing prompt changes over time,…

## Pipeline Composition
- ✅ sim=0.50 [EN] — `Autonomous AI Agents for Quantitative Research · Van Der Post, Hayden · 2026 · OEBPS/c3HR`
  > Network maps act like radar for pipeline governance. Visualizing agent dependencies, data lineage, and control-flow as a directed graph makes it immediate when a single node, a third-party feed or a preprocessing job,…

## Arquitetura do Sistema de Skills
- ✅ sim=0.62 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_10`
  > 拆解一个最简单的Skill（Anatomy of a Simple Skill） 先看一个最小的例子。假设你每周都要写团队周报，格式固定，但每次都要跟AI解释一遍。你可以把它做成一个Skill： --- name: weekly-report description: | 生成团队周报。当用户提到「周报」「weekly report」「本周总结」时使用此skill。 --- # 周报生成 1. 询问本周完成的主要工作 2.…
- ✅ sim=0.62 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_80`
  > 市场」的演进。两年前大家分享Prompt，但Prompt太碎片化了，没有结构，没有版本管理，换个模型可能就不好使了。Skill解决了这些问题，它有标准格式、有元数据、有触发条件、可以渐进式加载。Skill就是Prompt的升级版，有了固定格式、有了版本管理、有了标准。

## Filtros no Pipeline
- ✅ sim=0.52 [EN] — `Context Engineering for Multi-Agent Systems · Denis Rothman · 2025 · EPUB/toc`
  > Data ingestion pipeline Pipeline steps • Ingesting the context library • Execution and operation Engine room • Control deck • Production safeguards: moderation, sanitization, and policy Input sanitization (prompt…

## Error Handling em Pipelines
- ✅ sim=0.55 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_71`
  > 模式3：多阶段流水线型（Pipeline Pattern） 这是所有模式中最复杂的一种，也是处理端到端工作流的唯一靠谱方式。 核心结构很直白：把大任务拆成多个阶段，每个阶段有明确的输入和输出，阶段之间用检查点分隔。用户确认后才进入下一阶段。 我的huashu-book-pdf（书籍级PDF制作Skill）是这个模式的极端案例。你现在正在读的这本橙皮书，就是用它做的。整个流水线分5个阶段：…
- ✅ sim=0.53 [EN] — `Bigger Errors - Crashes · `fastapi-docs-en/docs/deployment/concepts.md``
  > Bigger Errors - Crashes Nevertheless, there might be cases where we write some code that **crashes the entire application** making Uvicorn and Python crash. 💥 And still, you would probably not want the application to…
- ✅ sim=0.51 [EN] — `Context Engineering for Multi-Agent Systems · Denis Rothman · 2025 · EPUB/toc`
  > Data ingestion pipeline Pipeline steps • Ingesting the context library • Execution and operation Engine room • Control deck • Production safeguards: moderation, sanitization, and policy Input sanitization (prompt…

## Registry de Skills
- ✅ sim=0.61 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_30`
  > 七大Skills平台（Seven Platforms） 目前值得关注的Skills来源有七个。我按「从官方到社区」的顺序介绍。 1. Anthropic官方Skills仓库（github.com/anthropics/skills）…
- ✅ sim=0.60 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_87`
  > 附录A 推荐Skills清单（Recommended Skills） 按使用场景分类的推荐Skills。来源标注「官方」的是Anthropic维护的，标注「社区」的来自AgentSkill.sh、skills.sh（Vercel）等平台。 核心建议 这个清单会随着生态发展不断变化。获取最新推荐，可以访问 skills.sh（Vercel开源目录）或 agentskill.sh（社区市场）浏览按分类排列的Skills目录。
- ✅ sim=0.59 [ZH] — `Agent Skills橙皮书 · 2026 · EPUB/Text/page_1_split_30`
  > 3. AgentSkill.sh 106,000+个Skills的社区市场。安装方式很方便：在Claude Code里直接输入/learn @owner/skill-name就行。社区驱动意味着更新快、覆盖面广，但也意味着质量参差不齐。有些Skill写得很精心，有些就是随手糊的一个Markdown。用之前最好先看一眼SKILL.md的内容，别无脑装。 4. SkillsMP（skillsmp.com）…

## Módulos shared/ Usados Neste Módulo
- ✅ sim=0.50 [EN] — `Context Engineering for Multi-Agent Systems · Denis Rothman · 2025 · EPUB/Chapter_5`
  > This output clearly demonstrates that the hardened Context Engine is working as intended. It successfully planned a dynamic workflow, orchestrated multiple agents, and produced a cohesive result idx_777f9040through…


---

**Resumo:** 9/9 conceitos com suporte (0 sem cobertura).
