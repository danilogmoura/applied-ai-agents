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

---

# Plano 2 — Adequação dos `architecture.md` ao programador iniciante

> **Escopo:** os 10 arquivos `modules/*/architecture.md` (desafios de design arquitetural).
> **Origem:** análise VALIDA-IA sobre os architecture.md (notas da rubrica de 7 dimensões).
> **Status:** ✅ executado (C4→C2→C1→C3→C5).

## Contexto do artefato

Diferente dos `miniproject.md` (que especificam código), os `architecture.md` são **desafios abertos de design**: Cenário → Entregáveis (1-4) → Checklist → Critérios de Avaliação (5/3/1). Estão corretamente marcados como **referência opcional/avançada** nos `MATERIAL.md`, mas hoje exigem um profissional experiente — violando o "duplo iniciantismo".

## Problemas identificados (por evidência)

| # | Problema | Módulos afetados | Evidência |
| --- | ---------- | ------------------ | ----------- |
| P1 | Pré-requisitos ocultos de infra/DevOps sem explicação | p4, p3b, p9, p8, p11 | "Kubernetes vs Docker", "Uvicorn async + threads", "message queue", "Redis", "LRU/LFU/FIFO", "canary" |
| P2 | Sem scaffold/exemplo de resposta nas tabelas abertas | todos (10) | Tabelas com `?` vazios, nenhum exemplo preenchido ou modelo parcial |
| P3 | Cálculo de custo pedido sem fórmula nem tabela de preços | p2, p3b, p7, p8, p9, p11 | "Calcule custo esperado por caminho"; "Tokens input/output?" sem preço/token |
| P4 | Jargões sem glossário inline | p3a3, p4, p8, p9, p10, p11 | TTFT, DAG, SemVer, jitter, backoff, LRU/LFU, canary, prompt drift |
| P5 | Inconsistência de terminologia/ortografia | p3a3 | "Freqüência" (ortografia antiga); padrão do repo é inglês-primeiro-(PT parênteses) |

## Correções planejadas

### C1 — Bloco "Como abordar este desafio" (resolve P2)

Inserir, logo após o cabeçalho `## Entregáveis` de cada arquivo, um mini-scaffold:

- Um exemplo resolvido do **Entregável 1 (diagrama)** já preenchido (exemplo genérico, não a resposta "oficial").
- Uma linha preenchida como modelo nas tabelas de decisão ("Exemplo preenchido" acima das linhas em branco).
- Texto: "Comece rascunhando; não existe resposta única correta."

Aplicar em: **todos os 10**.

### C2 — Mini-tabela de preços + fórmula de custo (resolve P3)

Antes de toda seção de estimativa de custo, inserir um bloco padrão:

```
> 💡 **Como calcular custo.** Fórmula: `custo = (tokens / 1000) × preço_por_1k`.
> Preços de referência (USD por 1M tokens): gpt-4o-mini $0.15 in / $0.60 out;
> gpt-4o $2.50 in / $10 out; text-embedding-3-small $0.02.
> Estimativa de tokens: ~4 chars ≈ 1 token.
```

E um exemplo numérico resolvido no módulo cujo custo é central (p9_caching ROI, p3b custo por caminho).

Aplicar em: **p2, p3b, p7, p8, p9, p11** (os que pedem cálculo de custo detalhado).

### C3 — Glossário inline na primeira ocorrência (resolve P1 + P4)

Adicionar definição de 1 linha, entre parênteses, na primeira aparição de cada termo. Lista mínima:

- **TTFT** (Time To First Token — tempo até o primeiro token aparecer)
- **DAG** (Directed Acyclic Graph — grafo direcionado sem ciclos)
- **SemVer** (versionamento semântico: MAJOR.MINOR.PATCH)
- **backoff exponencial** (esperar cada vez mais entre tentativas)
- **jitter** (variação aleatória somada ao backoff para evitar sincronia)
- **LRU / LFU / FIFO** (políticas de eviction: menos usado recente / menos frequente / primeira entrada)
- **canary deploy** (liberar para % pequeno antes de todos)
- **prompt drift** (mudança não intencional de comportamento do prompt)
- **message queue** (fila onde mensagens aguardam processamento)
- **Redis** (banco de dados em memória, usado para cache/filas)
- **Kubernetes** (orquestrador de containers) / **Docker** (empacota app em container)
- **zero downtime deploy** (atualizar sem tirar o ar do serviço)

Aplicar em: **p3a3, p4, p8, p9, p10, p11, p3b** (conforme termos presentes).

### C4 — Selo de trilha "Avançado" + aviso de pré-requisito (resolve P1 residual)

No topo de cada `architecture.md`, reforçar badge:
`> 🔬 AVANÇADO / OPCIONAL — Este desafio assume noções de infra. Se você ainda está aprendendo, tudo bem pular na primeira passada.`
(Alguns já têm isso no MATERIAL; levar para o próprio architecture.md.)

Aplicar em: **todos os 10**.

### C5 — Padronização de ortografia/terminologia (resolve P5)

- Corrigir "Freqüência" → "Frequência" (p3a3).
- Conferir padrão inglês-primeiro-(PT parênteses) nos termos técnicos conforme memória do repo.

Aplicar em: **p3a3** (+ revisão rápida nos demais).

## Ordem de execução proposta

1. **C4** (badge) — trivial, todos os 10, dá contexto imediato.
2. **C2** (preços/custo) — destrava o bloqueio mais duro (cálculo).
3. **C1** (scaffold/exemplo) — maior ganho didático.
4. **C3** (glossário) — remove pré-requisitos ocultos.
5. **C5** (ortografia) — polimento final.

## Riscos / guardrails

- Não transformar os desafios em "receita pronta": exemplos devem ser **ilustrativos**, mantendo a abertura da tarefa.
- Manter orçamento/valores originais dos cenários ($500, $2000 etc.) intactos.
- Preservar a rubrica 5/3/1 existente.

## Checklist de conclusão (Planejamento 2)

- [x] C4 aplicado nos 10 architecture.md
- [x] C2 aplicado nos módulos de custo (p2, p7, p9, p3b) + exemplo numérico em p9/p3b
- [x] C1 aplicado nos 10 (scaffold "Como abordar" + exemplo ilustrativo)
- [x] C3 glossários inline aplicados nos módulos listados (p3a3, p4, p8, p9, p10, p11, p3b)
- [x] C5 ortografia corrigida (p3a3: Freqüência→Frequência) e revisada (sem outros erros pré-Acordo)
- [ ] Commit das alterações
