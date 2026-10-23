# Plano de Alinhamento: `run.py` vs `miniproject.md`

## Visão Geral

Cada módulo tem dois artefatos que devem conversar entre si:

- **`run.py`** — código executável que demonstra o conceito do módulo
- **`miniproject.md`** — especificação do mini-projeto integrador (o que o aluno deve construir)

**Problema comum:** O `run.py` e o `miniproject.md` frequentemente usam nomes de classe diferentes, estruturas diferentes, ou métodos diferentes. Isso confunde o aluno.

## Tabela Completa de Alinhamento por Módulo

| # | Módulo | `run.py` (implementação) | `miniproject.md` (requisito) | Status | Ação Recomendada |
| --- | -------- | ------------------------- | ------------------------------ | -------- | ------------------ |
| 1 | p0_first_llm | `classify_ticket()`, `classify_batch()`, `classify_with_rules()` (funções) | `TicketClassifier` com `classify()`, `batch_classify()`, `classify_with_rules()` | ✅ Resolvido | Adicionada nota no miniproject: skeleton `TicketClassifier` é a referência; run.py é demo em funções |
| 2 | p0_fundamentals | `demo_tokenization()`, `demo_temperature()`, etc. (demos soltos) | Sem classe específica — só demos | ✅ Alinhado | Nenhuma ação |
| 3 | p1_feasibility | `BenchmarkResult`, `run_benchmarks_simulated()`, `generate_memorandum()` (funções) | `FeasibilityAnalyzer` com `measure_latency()`, `compare_costs()`, `evaluate_accuracy_threshold()`, `generate_memorandum()` | ✅ Resolvido | Nota no miniproject: `FeasibilityAnalyzer` é a referência; run.py é demo em funções |
| 4 | p2_rag | `SimpleEmbedder`, `ChromaVectorStore`, `RAGPipeline` (3 classes separadas) | `MiniRAG` (1 classe monolítica) | ✅ Resolvido | Mantido MiniRAG + nota mapeando para arquitetura modular de referência |
| 5 | p3a1_self_eval | `SelfEvaluation`, `SelfEvaluatingAgent` | `SelfEvalGenerator` | ✅ Renomeado | miniproject: SelfEvalGenerator → SelfEvaluatingAgent |
| 6 | p3a2_tool_calling | `ToolCallingAgent` | `ToolCallingSystem` | ✅ Renomeado | miniproject: ToolCallingSystem → ToolCallingAgent |
| 7 | p3a3_planning | `CircuitBreaker`, `ResilientPlanner` | `Planner` | ✅ Renomeado | miniproject: Planner → ResilientPlanner (+ nota CircuitBreaker) |
| 8 | p3b_multi_agent | `Agent`, `SupervisorAgent` | `MultiAgentSystem` | ✅ Renomeado | miniproject: MultiAgentSystem → Agent + SupervisorAgent |
| 9 | p4_production | FastAPI app (`main()`) | `AgentAPI` | ✅ Resolvido | Mantido FastAPI real + nota explicando AgentAPI como wrapper didático |
| 10 | p5_evaluation | `Evaluator`, `ABTestResult` | `EvalFramework` | ✅ Renomeado | miniproject: EvalFramework → Evaluator |
| 11 | p6_safety | `ThreatType`, `PromptInjectionDetector`, `SafetyGuardrails` | `SafetySystem` | ✅ Renomeado | miniproject: SafetySystem → SafetyGuardrails (+ nota detectores) |
| 12 | p7_memory | `Message`, `ShortTermMemory`, `LongTermMemory`, `AgentWithMemory` | `MemorySystem` | ✅ Renomeado | miniproject: MemorySystem → AgentWithMemory (+ nota Short/LongTerm) |
| 13 | p8_streaming | `StreamingAgent`, `SSEEventGenerator`, `LiveStreamDisplay` | `StreamingSystem` | ✅ Renomeado | miniproject: StreamingSystem → StreamingAgent |
| 14 | p9_caching | `ResponseCache`, `ModelRouter`, `OptimizedAgent` | `CacheSystem` | ✅ Renomeado | miniproject: CacheSystem → ResponseCache |
| 15 | p10_skills | `SkillRegistry`, `BaseSkill`, `SentimentAnalysisSkill`, `TextSummarizationSkill`, `EntityExtractionSkill`, `TranslatorSkill`, `Pipeline` | `SkillSystem` | ✅ Renomeado | miniproject: SkillSystem → SkillRegistry |
| 16 | p11_production_ops | `MetricsCollector`, `PromptTester`, `PromptManager` | `OpsSystem` | ✅ Renomeado | miniproject: OpsSystem → MetricsCollector |

## Resumo por Tipo de Problema

| Tipo | Qtd | Módulos | Solução |
| ------ | ----- | --------- | --------- |
| ❌ Nome diferente | 10 | p3a1, p3a2, p3a3, p3b, p5, p6, p7, p8, p9, p10, p11 | Renomear no miniproject.md |
| ⚠️ Função vs Classe | 2 | p0_first_llm, p1_feasibility | Padronizar abordagem |
| ⚠️ Arquitetura diferente | 1 | p2_rag | Manter modular (run.py) |
| ⚠️ Diferente mas compatível | 1 | p4_production | Manter FastAPI real |
| ✅ Alinhado | 1 | p0_fundamentals | — |
| **Total** | **16** | | |

## Padrões Identificados

### Padrão A: Funções vs Classe

**Módulos afetados:** p0_first_llm, p1_feasibility

O `run.py` usa funções soltas (`def classify_ticket(...)`), mas o `miniproject.md` pede uma classe (`class TicketClassifier`).

**Recomendação:** Simplificar o `miniproject.md` para aceitar funções. É mais natural para iniciantes e o `run.py` já faz isso corretamente.

### Padrão B: Nome Diferente da Mesma Coisa

**Módulos afetados:** p3a1, p3a2, p3a3, p3b, p5, p6, p7, p8, p9, p10, p11 (10 módulos!)

O `run.py` e `miniproject.md` descrevem a mesma estrutura mas com nomes diferentes. Este é o problema mais frequente.

**Recomendação:** Padronizar nomes no `miniproject.md` para bater com o `run.py`. O `run.py` é a referência porque é o código que realmente roda.

### Padrão C: Arquitetura Diferente

**Módulo afetado:** p2_rag

`run.py` divide em 3 classes (`SimpleEmbedder`, `ChromaVectorStore`, `RAGPipeline`) — arquitetura modular correta. `miniproject.md` pede 1 classe monolítica (`MiniRAG`).

**Recomendação:** Manter `run.py` como está (melhor prática). Ajustar `miniproject.md` para permitir/encorajar classes separadas.

## Prioridades de Correção

### Alta (confunde o aluno diretamente)

1. **p3a1_self_eval** — nome diferente (`SelfEvalGenerator` vs `SelfEvaluatingAgent`)
2. **p3a2_tool_calling** — nome diferente (`ToolCallingSystem` vs `ToolCallingAgent`)
3. **p3b_multi_agent** — nome diferente (`MultiAgentSystem` vs `Agent`+`SupervisorAgent`)
4. **p0_first_llm** — função vs classe (já houve inconsistência JSON vs palavra única)

### Média (estrutura diferente mas funcional)

1. **p1_feasibility** — funções vs classe
2. **p2_rag** — classe monolítica vs modular

### Baixa (nome diferente mas método consistente)

1. **p3a3_planning** — Planner vs CircuitBreaker+ResilientPlanner
2. **p4_production** — AgentAPI vs FastAPI app
3. **p5_evaluation** — EvalFramework vs Evaluator
4. **p6_safety** — SafetySystem vs SafetyGuardrails+PromptInjectionDetector
5. **p7_memory** — MemorySystem vs ShortTermMemory+LongTermMemory
6. **p8_streaming** — StreamingSystem vs StreamingAgent
7. **p9_caching** — CacheSystem vs ResponseCache
8. **p10_skills** — SkillSystem vs SkillRegistry
9. **p11_production_ops** — OpsSystem vs MetricsCollector

## Próximos Passos

> **Status: plano executado (2026-10-23).** Todas as 16 linhas foram resolvidas.

1. ✅ Executar correções nos módulos de alta prioridade (renomear classes no miniproject.md) — p3a1, p3a2, p3b, p0_first_llm
2. ✅ Revisar e aplicar correções de média prioridade — p1_feasibility, p2_rag
3. ✅ Aplicar correções de baixa prioridade — p3a3, p4, p5, p6, p7, p8, p9, p10, p11
4. ✅ Commit das alterações

**Abordagem adotada:** `run.py` é a referência (é o código que roda). Nos casos de nome diferente (Padrão B), o `miniproject.md` foi renomeado para bater com o `run.py`. Nos casos função-vs-classe e arquitetura (Padrões A e C), foi adicionada uma **nota de alinhamento** explicando ao aluno qual artefato é a referência do que ele entrega, preservando tanto o demo (`run.py`) quanto o entregável didático (skeleton/classe única).
