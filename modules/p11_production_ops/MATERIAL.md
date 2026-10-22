# Material Didático — P11: Operations de Produção (CI/CD + Monitoramento)

## Conceitos Fundamentais

### Por que Monitorar Agentes?

Em produção, você precisa saber:

- Quantas chamadas estão sendo feitas?
- Quanto está custando?
- Qual a latência média?
- Algum prompt quebrou após deploy?

### Métricas Essenciais

| Métrica | O que mede | Threshold típico |
| --------- | ----------- | ----------------- |
| **Latência P50** | Tempo médio | < 1s |
| **Latência P95** | Top 5% mais lento | < 3s |
| **Taxa de erro** | % de falhas | < 5% |
| **Custo/request** | Gasto por chamada | < $0.01 |
| **Requests/min** | Throughput | Variável |

### Prompt Testing (A/B)

Antes de deploy, teste novas versões contra dataset:

```python
tester.add_test_case("Email suspeito", "spam")
tester.add_test_case("Reunião amanhã", "not_spam")

results = await tester.run_test("prompt_v2")
# success_rate: 95% → pode deployar
```

### Rollback Automático

Se métricas degradarem após deploy, rollback automático:

```python
if dashboard["error_rate"] > 10:
    manager.rollback("spam_classifier")
```

### Logging Estruturado

Logs em JSON para facilitar análise:

```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "info",
  "metric": "latency_ms",
  "value": 250,
  "labels": {"prompt": "v2", "model": "gpt-4o-mini"}
}
```

---

## Exercício Prático

Execute `python modules/p11_production_ops/run.py` e observe:

1. Como prompts são registrados e testados
2. Comparação A/B entre versões
3. Deploy só acontece se success_rate > threshold
4. Dashboard com métricas em tempo real
5. Health check do sistema

## Perguntas para Reflexão

1. Se você tivesse 100 prompts ativos, como monitorar tudo sem ser invadido por alerts?
2. Quando fazer rollback manual vs automático?
3. Como criar um dataset de testes representativo para prompts?

---

## Referências

### Livros

- **"Building LLM Apps"** by Albert Vander Smith — Capítulos sobre production monitoring
- **"Site Reliability Engineering"** by Betsy Beyer et al. — SLOs e error budgets

### Documentação Oficial

- [OpenAI Observability](https://platform.openai.com/docs/guides/observability) — OpenAI Docs
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/) — Prometheus Docs

### Vídeos

- [LLM Production Monitoring](https://www.youtube.com/watch?v=ZCGdyYJVIoQ) — ML Ops, YouTube
- [Prompt Versioning](https://www.youtube.com/watch?v=fJBhIuxLfPA) — AI Engineer, YouTube

### Tutoriais

- [LangSmith Observability](https://www.langchain.com/langsmith) — LangSmith Docs
- [Grafana Dashboards](https://grafana.com/docs/) — Grafana Docs
