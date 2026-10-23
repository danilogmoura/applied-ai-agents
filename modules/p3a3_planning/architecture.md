# 🏗️ Architecture Design — Planner com Resiliência

> **Desafio:** Projete um planner resiliente para agente que executa tarefas multi-etapas.
>
> 🔬 **AVANÇADO / OPCIONAL** — Este desafio assume noções de arquitetura e infra. Se você ainda está aprendendo os fundamentos, tudo bem pular na primeira passada e voltar depois.

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

> 🧭 **Como abordar este desafio.** Não existe uma única arquitetura correta — o que se avalia é o seu **raciocínio**. Sugestão de caminho:
>
> 1. Comece rascunhando o diagrama com blocos e setas (ASCII serve).
> 2. Para cada decisão na tabela, registre *o que escolheu* **e por quê**.
> 3. Feche com números de custo/latência, mesmo estimados.
>
> Exemplo ilustrativo (não é gabarito): ao desenhar checkpoints, pense em "se o processo morrer aqui, de onde ele retoma?" — isso guia onde colocar cada ponto de recuperação.

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
- Como o planner decide qual retry usar — exponential backoff (retentativa com espera que dobra a cada falha) vs. fallback (caminho alternativo)?

> 💡 **Termos deste desafio.** *Exponential backoff* = entre tentativas, aguardar 1s, 2s, 4s… para não martelar um serviço já sobrecarregado. *Jitter* = uma pitada de aleatoriedade nesse tempo, para evitar que muitas requisições "tentem juntas" ao mesmo tempo. *Circuit breaker* (disjuntor): se um serviço falha demais, "desliga" temporariamente e segue sem ele.

### 2. Estratégia de Checkpoints

Para cada etapa, defina:

| Passo | Estado a Salvar | Frequência | Formato |
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
