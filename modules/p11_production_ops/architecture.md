# 🏗️ Architecture Design — CI/CD + Monitoramento para Agentes de IA

> **Desafio:** Projete o sistema de operations para um agente de IA em produção com 10K usuários ativos.

## Cenário

Seu agente está em produção com:
- **10K usuários ativos/mês**
- **~50K chamadas/dia**
- **Múltiplos prompts** sendo testados simultaneamente (A/B/n)
- **Múltiplos modelos** em rotação (gpt-4o-mini, claude-haiku)
- **Requisito**: detectar degradação de qualidade ANTES de ir para produção
- **Requisito**: rollback automático se métricas piorarem

Problema: diferente de software tradicional, a qualidade de um agente de IA é **subjetiva** e **não determinística**. Como monitorar e fazer deploy seguro?

---

## Entregáveis

### 1. Diagrama da Arquitetura

```
[Dev] → [CI Pipeline] → [Staging] → [Canary] → [Production]
          ↑                ↑            ↑             ↑
     [Tests]        [Golden Set]  [A/B Test]  [Monitoring]
                                              [Alerts]
                                              [Auto-rollback]
```

Defina:
- Quais gates existem entre staging → canary → production?
- Como golden sets são mantidos?
- Quando trigger auto-rollback?

### 2. Decisões Arquiteturais

| Decisão | Opções | Sua Escolha | Justificativa |
|---------|--------|-------------|---------------|
| **Test quality** | Exact match | LLM-as-a-Judge | Hybrid | ? |
| **Rollback** | Manual | Automático (threshold) | Híbrido | ? |
| **Monitoring** | Logs only | Metrics + tracing + logs | ? |
| **A/B testing** | Por user ID | Por session | Random split | ? |
| **Golden set** | Manual | Auto-generated | Hybrid | ? |
| **Alert threshold** | Erro > 5% | Qualidade < 80% | Ambos | ? |

### 3. Pipeline de Deploy Detalhado

Descreva cada stage:

**Stage 1: CI (Code Integration)**
```
Trigger: PR merged to main
Tests: unit tests + golden set regression
Gate: all tests pass
Duration: ~5 min
```

**Stage 2: Staging**
```
Trigger: CI passes
Deployment: new prompt/model to staging env
Tests: golden set + smoke tests
Gate: quality score >= 90% of baseline
Duration: ~10 min
```

**Stage 3: Canary (5% do tráfego)**
```
Trigger: Staging passes
Deployment: new version receives 5% traffic
Monitor: latency, error rate, quality sample
Duration: 30 min
Gate: no degradation detected
```

**Stage 4: Production (100%)**
```
Trigger: Canary passes
Deployment: gradual rollout (25% → 50% → 100%)
Monitor: full metrics suite
Duration: 2 hours
```

Preencha:
- Qual teste em cada stage?
- Qual gate de aprovação?
- Quanto tempo em cada stage?
- Quando trigger rollback?

### 4. Dashboard de Monitoramento

Defina as métricas essenciais:

| Métrica | Tipo | Threshold Alerta | Fonte |
|---------|------|------------------|-------|
| Latência p95 | Performance | > 5s | Request timing |
| Error rate | Reliability | > 2% | HTTP status codes |
| Quality score | AI-specific | < 80% | LLM-as-a-Judge |
| Cost per request | Financial | > $0.01 | Token counting |
| Token usage | Capacity | > 90% context | Token counter |
| Prompt drift | Drift detection | > 10% diff | Golden set comparison |

---

## Checklist de Validação

- [ ] Pipeline de deploy com gates claros (CI → staging → canary → prod)
- [ ] Golden set strategy definida e atualizada
- [ ] Métricas de qualidade AI-specific (não só latência/erro)
- [ ] Rollback automático configurado com thresholds
- [ ] A/B testing implementado para comparação justa
- [ ] Custo por request monitorado
- [ ] Detecção de prompt drift (mudança não intencional no comportamento)

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
|----------|--------------|---------|-----------|
| **Pipeline** | Gates claros em cada stage | Stages básicos | Sem gates |
| **Qualidade** | Métricas AI-specific | Métricas tradicionais | Sem métricas |
| **Rollback** | Automático com thresholds | Manual | Sem rollback |
| **Drift** | Detecção proativa | Detecção reativa | Sem detecção |
