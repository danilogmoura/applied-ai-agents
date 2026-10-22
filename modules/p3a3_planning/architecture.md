# 🏗️ Architecture Design — Planner com Resiliência

> **Desafio:** Projete um planner resiliente para agente que executa tarefas multi-etapas.

## Cenário

Um agente precisa executar uma tarefa complexa em múltiplos passos:

```
1. Buscar dados de API externa
2. Processar e transformar dados
3. Validar qualidade dos dados
4. Gerar relatório
5. Enviar por email
6. Salvar no sistema
```

Requisitos:

- Cada passo pode falhar independentemente
- Se um passo falha, não perder progresso anterior
- Rate limits da API podem bloquear temporariamente
- Orçamento: máximo $50/mês em API calls
- Tempo total máximo: 5 minutos por tarefa

---

## Entregáveis

### 1. Diagrama da Arquitetura

Descreva o fluxo do planner com checkpoints:

```
[Usuário] → [Planner] → [Executor] → [API Externa]
              ↑            ↓            ↓
         [Checkpoint] ←── [Monitor] ←── [Circuit Breaker]
```

Defina:

- Quantos checkpoints salvar durante execução?
- Quando o circuit breaker abre/fecha?
- Como o planner decide qual retry usar (backoff vs fallback)?

### 2. Estratégia de Checkpoints

Para cada etapa, defina:

| Passo | Estado a Salvar | Freqüência | Formato |
| ------- | ----------------- | ------------ | --------- |
| 1. Buscar dados | ? | ? | ? |
| 2. Processar | ? | ? | ? |
| 3. Validar | ? | ? | ? |
| ... | ... | ... | ... |

O que exatamente é salvo em cada checkpoint? (estado completo ou incremental?)

### 3. Política de Retry e Circuit Breaker

Defina os parâmetros:

| Parâmetro | Valor | Justificativa |
| ----------- | ------- | --------------- |
| max_retries | ? | ? |
| backoff_base | ? | ? |
| jitter_range | ? | ? |
| failure_threshold | ? | ? |
| recovery_timeout | ? | ? |

Descreva o comportamento de cada estado do circuit breaker:

- **CLOSED**: chamadas normais, conta falhas
- **OPEN**: todas chamadas bloqueadas, usa fallback
- **HALF_OPEN**: 1 chamada teste, sucesso → CLOSED, falha → OPEN

### 4. Plano de Fallback por Tipo de Erro

Não use fallback genérico — seja específico:

| Tipo de Erro | Fallback Específico | Custo Extra | Tempo Extra |
| -------------- | --------------------- | ------------- | ------------- |
| 429 Too Many Requests | Backoff + retry | ? | ? |
| 503 Service Unavailable | Alternativa/local cache | ? | ? |
| Timeout | Reduzir escopo da requisição | ? | ? |
| JSON inválido | Re-prompt com correção | ? | ? |
| Modelo alucina | LLM-as-a-judge valida | ? | ? |

---

## Checklist de Validação

- [ ] Fluxo completo com checkpoints definidos
- [ ] Estado de cada checkpoint especificado
- [ ] Circuit breaker com parâmetros justificados
- [ ] Fallbacks específicos por tipo de erro
- [ ] Custo estimado dentro do orçamento ($50/mês)
- [ ] Tempo total respeita limite de 5 minutos

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
| ---------- | -------------- | --------- | ----------- |
| **Checkpoints** | Estado granular por passo | Estado genérico | Sem definição |
| **Circuit Breaker** | Parâmetros justificados | Apenas descreve | Não implementa |
| **Fallbacks** | Específicos por tipo | Genérico | Ausente |
| **Custo/Tempo** | Dentro limites | Levemente acima | Fora do orçamento |
