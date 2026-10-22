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

### Algoritmo: Exponential Backoff com Jitter

Quando uma API falha, nunca repita imediatamente. Use backoff exponencial — mas com aleatoriedade:

```
Falha na API → espera antes de tentar de novo:

Sem jitter (pior caso):
  Tentativa 1: falha → espera 1s
  Tentativa 2: falha → espera 2s
  Tentativa 3: falha → espera 4s
  Tentativa 4: falha → espera 8s
  ... todos os clientes esperam EXATAMENTE o mesmo tempo
  → quando reiniciam, TODOS tentam juntos de novo
  → thundering herd = mais carga no servidor

Com jitter (recomendado):
  Tentativa 1: falha → espera 1s ± 0.5s (random)
  Tentativa 2: falha → espera 2s ± 1s (random)
  Tentativa 3: falha → espera 4s ± 2s (random)
  Tentativa 4: falha → espera 8s ± 4s (random)
  → cada cliente tenta em momento diferente
  → carga distribuída = servidor se recupera
```

#### A fórmula que todo engenheiro precisa saber

```
wait_time = min(max_delay, base_delay × 2^attempt) + random_jitter

base_delay = 1 segundo
max_delay = 60 segundos
attempt = número da tentativa (0, 1, 2, ...)
random_jitter = random(0, wait_time / 2)

Exemplo prático:
  attempt=0: min(60, 1×2⁰) + rand(0, 0.5) = 1 + 0.3 = 1.3s
  attempt=1: min(60, 1×2¹) + rand(0, 1)   = 2 + 0.7 = 2.7s
  attempt=2: min(60, 1×2²) + rand(0, 2)   = 4 + 1.1 = 5.1s
  attempt=3: min(60, 1×2³) + rand(0, 4)   = 8 + 2.4 = 10.4s
  attempt=5: min(60, 1×2⁵) + rand(0, 8)   = 32 + 3.2 = 35.2s
  attempt=7: min(60, 1×2⁷) + rand(0, 16)  = 60 + 8.1 = 68.1s → capped at 60
```

**Por que jitter é obrigatório?**

Sem jitter, N clientes que falham juntos vão tentar reiniciar juntos. Se N=10.000, você cria um pico de 10.000 requisições simultâneas — exatamente o que causou a falha original. Com jitter, esses 10.000 clientes se espalham por vários segundos, reduzindo a carga instantânea.

**Implementação prática:**

```python
import random
import time

def call_with_retry(api_call, max_retries=5):
    for attempt in range(max_retries):
        try:
            return api_call()
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # último retry, não tenta de novo
            
            wait = min(60, 2 ** attempt) + random.uniform(0, 2 ** (attempt - 1))
            print(f"Tentativa {attempt+1} falhou, esperando {wait:.1f}s")
            time.sleep(wait)
```

Este padrão é usado por AWS SDK, Google Cloud, OpenAI Python client e praticamente toda API de produção.

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

- **"Designing Machine Learning Systems"** by Chip Huyen — Capítulos sobre production monitoring and observability
- **"Site Reliability Engineering"** by Betsy Beyer et al. — SLOs e error budgets

### Documentação Oficial

- [OpenAI Observability](https://platform.openai.com/docs/guides/observability) — OpenAI Docs
- [Prometheus Metrics](https://prometheus.io/docs/concepts/metric_types/) — Prometheus Docs

### Tutoriais

- [LangSmith Observability](https://www.langchain.com/langsmith) — LangSmith Docs
- [Grafana Dashboards](https://grafana.com/docs/) — Grafana Docs
