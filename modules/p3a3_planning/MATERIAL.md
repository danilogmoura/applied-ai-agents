# Material Didático — P3a-3: Planejamento e Retomada

## ⚠️ Pré-requisito

Você precisa ter concluído o módulo [P3a-2: Tool Calling](../p3a2_tool_calling/MATERIAL.md). Especificamente, precisa saber:

- Como definir schemas JSON para ferramentas com descrições claras
- O pattern de tool calling (decide → executa → retorna resultado)
- Camadas de segurança (whitelist, risk levels, HITL)

---

## 🎯 Objetivos de Aprendizagem

Ao final deste módulo, você será capaz de:

- [ ] **Implementar** o pattern Circuit Breaker para proteger contra falhas em cascata
- [ ] **Criar** checkpoints para salvar progresso e recuperar após crashes
- [ ] **Aplicar** retry com exponential backoff + jitter (retrocesso exponencial com variação aleatória) para chamadas instáveis
- [ ] **Projetar** estratégias de fallback por tipo de erro (não genérico)
- [ ] **Entender** trade-offs entre resiliência e custo/latência

> 💡 **Dica:** Em produção, coisas VÃO falhar — APIs caem, rate limits são atingidos, timeouts acontecem. Este módulo ensina a construir agentes que não quebram completamente quando um passo falha.

---

## Conceitos Fundamentais

### Por que Planejadores Precisam Ser Resilientes?

Em produção, coisas falham:

- APIs externas caem (503 Service Unavailable)
- Rate limits são atingidos (429 Too Many Requests)
- Timeouts ocorrem em chamadas lentas
- Serviços são reiniciados para deploy

Um planejador ingênuo falha completamente quando um passo falha. Um planejador resiliente:

1. **Detecta** a falha rapidamente
2. **Protege** contra retries inúteis (circuit breaker)
3. **Salva** progresso periodicamente (checkpoint)
4. **Recupera** de onde parou ao tentar novamente

### Por que isso existe?

Imagine um agente que precisa executar 10 passos para completar uma tarefa complexa:

```
Passo 1 ✅ → Passo 2 ✅ → ... → Passo 8 ✅ → Passo 9 ❌ (API caiu)
```

Sem resiliência: tudo perdido. Você teria que recomeçar do passo 1. Se cada passo custa tokens e leva segundos, isso é caro e frustrante.

Com resiliência: salva checkpoint a cada 2 passos, retry com backoff no passo 9, e continua do passo 10 se o retry falhar.

### Erros Comuns de Iniciantes

| Erro | Consequência | Correção |
| ------ | -------------- | ---------- |
| Retry sem limite | Loop infinito gastando dinheiro | Circuit breaker + max_retries |
| Backoff fixo (sempre 1s) | Thundering herd — todos tentam junto | Jitter aleatório no backoff |
| Não salvar checkpoint | Perde todo progresso se crashar | Salvar estado a cada N passos |
| Fallback genérico | Resposta ruim pior que erro claro | Fallback específico por tipo de erro |

### Circuit Breaker Pattern

Inspirado em disjuntores elétricos: se muitos erros acontecem, o circuito "abre" e para de tentar por um tempo.

```mermaid
stateDiagram-v2
    [*] --> CLOSED
    CLOSED --> OPEN: Falhas >= threshold
    OPEN --> HALF_OPEN: recovery_timeout
    HALF_OPEN --> CLOSED: Sucesso
    HALF_OPEN --> OPEN: Falha
    
    note right of CLOSED
      Chamadas fluem normalmente
      Conta falhas consecutivas
    end note
    
    note right of OPEN
      Todas chamadas bloqueadas
      Usa resposta fallback/cacheada
    end note
    
    note right of HALF_OPEN
      1 chamada de teste
      Se sucesso → CLOSED
      Se falha → OPEN
    end note
```

Este pattern evita o **cascata de falhas**: quando um serviço lento faz todos os outros serviços esperarem até esgotar memória.

### Checkpoints — Salvar o Progresso

Checkpoint é um snapshot do estado completo do sistema:

```json
{
  "timestamp": 1729500000,
  "step_index": 3,           // Já completou 3 passos
  "tokens_consumed": 15420,  // Tokens gastos até agora
  "cost_accumulated": 0.023, // Custo acumulado
  "circuits_status": {
    "external_api": {"state": "closed", "failures": 0}
  }
}
```

Se o sistema crashar ou precisar ser reiniciado, carregamos o checkpoint e continuamos do passo 3 — não do passo 1.

### Trade-offs de Resiliência

| Técnica | Vantagem | Custo |
| --------- | ---------- | ------- |
| Circuit Breaker | Evita cascata de falhas | Latência adicional (fallback) |
| Checkpoints | Recuperação após crash | I/O de escrita em disco |
| Retry com backoff | Tenta novamente suavemente | Atraso na resposta |
| Fallbacks | Sistema continua funcionando | Resposta degradada |

### Simulação de Serviço

O módulo usa `SimulatedService` para testar circuit breakers sem depender de API real:

```python
class SimulatedService:
    """Simula uma API externa que falha intermitentemente."""
    
    def __init__(self, failure_rate: float = 0.3):
        self.failure_rate = failure_rate
        self.call_count = 0
    
    def call(self) -> str:
        self.call_count += 1
        if random.random() < self.failure_rate:
            raise ConnectionError("Serviço indisponível")
        return f"Resposta #{self.call_count}"
```

Isso permite testar estados do circuit breaker de forma determinística.

### 🏗️ Arquitetura do Planner Resiliente

> Referência completa: [architecture.md](architecture.md)

O planner é um pipeline com 6 componentes interconectados:

```
[Usuário] → [Planner] → [Executor] → [API Externa]
              ↑            ↓            ↓
         [Checkpoint] ←── [Monitor] ←── [Circuit Breaker]
```

| Componente | Responsabilidade | Estado salva |
| ------------ | ------------------ | -------------- |
| **Planner** | Gera plano de passos + decide ordem | Nenhum (stateless) |
| **Executor** | Roda cada passo do plano | Resultado do passo |
| **Circuit Breaker** | Bloqueia chamadas se falhas > threshold | state (CLOSED/OPEN/HALF_OPEN) + failure_count |
| **Checkpoint** | Snapshot do progresso | step_index + tokens + custo + circuits_status |
| **Monitor** | Conta falhas + tempo + tokens | métricas por passo |
| **Retry Policy** | Backoff exponencial + jitter | retry_count + next_delay |

**Fluxo completo:**

1. Planner gera plano: `[passo1, passo2, passo3, ...]`
2. Executor roda passo N → Monitor conta sucesso/falha
3. Se falha ≥ threshold → Circuit Breaker abre (bloqueia próximas chamadas)
4. A cada N passos → Checkpoint salva estado no disco
5. Se API falha → Retry com backoff exponencial + jitter
6. Se tudo falhar → Fallback específico por tipo de erro
7. Crash/restart → Carrega último checkpoint e continua do passo salvo

**Trade-off chave:** mais checkpoints = mais recuperação mas mais I/O; mais retries = mais chance de sucesso mas mais custo.

## 🎬 O que você vai ver

Antes de rodar o código, aqui está uma prévia do que o programa vai fazer:

```
$ python modules/p3a3_planning/run.py

📋 Planner gera plano: [passo1, passo2, passo3]

▶️ Executando passo 1/3... OK
▶️ Executando passo 2/3... FALHOU

🔌 Circuit breaker aberto — pulando passo 2
↪️ Fallback ativado: tentar abordagem alternativa

✅ Passo 3 executado com sucesso
💾 Checkpoint salvo para recuperação

💰 Custo total: $0.012 | Passos: 4 tentativas
```

## Exercício Prático

Execute `python modules/p3a3_planning/run.py` e observe:

1. Como o circuit breaker transiciona entre estados
2. Quando o fallback é acionado vs quando a chamada real funciona
3. O checkpoint sendo salvo após cada passo
4. Como o planner recupera estado ao restaurar checkpoint

## Perguntas para Reflexão

1. Qual threshold de falhas seria ideal para um circuit breaker em produção? Mais ou menos que 3?
2. Se você tivesse múltiplas APIs dependentes, como gerenciaria os circuit breakers?
3. Que informações seriam críticas salvar no checkpoint para recuperação completa?

---

## 📌 Resumo do Módulo

Resilience patterns são o que separam protótipos de produção:

1. **Circuit Breaker protege contra cascata** — quando uma API falha repetidamente, parar de tentar evita sobrecarregar ainda mais e economiza tokens/custo.

2. **Checkpoints = salvar estado** — se um pipeline de 5 etapas falha na etapa 4, checkpoint permite retomar da etapa 3 sem recomeçar. Essencial para processos longos.

3. **Retry com backoff+jitter** — esperar cada vez mais entre tentativas (exponencial) + variação aleatória (jitter) resolve problemas temporários sem sobrecarregar.

4. **Fallbacks = plano B** — quando nada funciona, entregar algo imperfeito é melhor que nada. Cache antigo > erro 500.

5. **Trade-offs reais** — circuit breaker adiciona latência, checkpoints ocupam armazenamento, retry aumenta tempo total. Tudo tem custo.

> ✅ **Você está pronto para:** Agora que seu agente é resiliente, vamos escalar para múltiplos agentes especializados.

## ✅ Checklist: Como Saber Se Você Atingiu o Objetivo

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] Explico o que é circuit breaker e seus 3 estados (closed/open/half-open)
- [ ] Descrevo quando checkpoint deve ser salvo durante execução
- [ ] Explico a diferença entre retry simples e exponential backoff (retrocesso exponencial)
- [ ] Rodo `run.py` e explico como planner recupera estado do checkpoint
- [ ] Digo 2 trade-offs de adicionar resilience ao sistema

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

---

## 🔗 Próximos Passos

## 🔗 Próximos Passos

Com resilience patterns, seu agente individual sobrevive a falhas. Mas tarefas complexas exigem especialização — ninguém espera que um único agente faça tudo bem.

→ Leia o módulo [P3b: Multi-Agent Supervisor](../p3b_multi_agent/MATERIAL.md) para aprender arquitetura multiagente.

---

## Referências

(empty)

→ Leia o módulo [P3b: Multi-Agent Supervisor](../p3b_multi_agent/MATERIAL.md) para aprender arquitetura multiagente.
