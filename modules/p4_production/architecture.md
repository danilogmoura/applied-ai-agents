# 🏗️ Architecture Design — De Script a Produto (Produção)

> **Desafio:** Projete a arquitetura para transformar um script Python local em um serviço de agente acessível por múltiplos usuários simultâneos.
>
> 🔬 **AVANÇADO / OPCIONAL** — Este desafio assume noções de arquitetura e infra (containers, deploy, escalonamento). Se você ainda está aprendendo os fundamentos, tudo bem pular na primeira passada e voltar depois.

## Cenário

Você tem um **script Python** que funciona bem localmente (1 usuário). Agora precisa:

- Atender **1000 usuários simultâneos**
- Manter **latência < 5s** por request
- Garantir que **um crash não derrube o serviço**
- Permitir **deploy sem downtime**
- Orçamento infra: máximo $300/mês

---

## Entregáveis

> 🧭 **Como abordar este desafio.** Não existe uma única arquitetura correta — o que se avalia é o seu **raciocínio**. Sugestão de caminho:
>
> 1. Comece rascunhando o diagrama com blocos e setas (ASCII serve).
> 2. Para cada decisão na tabela, registre *o que escolheu* **e por quê**.
> 3. Feche com números de dimensionamento/custo, mesmo estimados.
>
> Exemplo ilustrativo (não é gabarito): ao pensar de script local para serviço, o primeiro gargalo costuma ser estado compartilhado entre instâncias — mapeie onde a informação precisa viver.

### 1. Diagrama da Arquitetura

```
[Clientes] → [Load Balancer] → [FastAPI Workers] → [Agent Core]
                    ↑               ↑                ↑
              [Metrics]       [Rate Limiter]   [Tool Executor]
```

Defina:

- Quantas instâncias de FastAPI?
- Como gerenciar estado entre requests?
- Onde colocar rate limiting?
- Como isolar falhas do agent core?

### 2. Decisões Arquiteturais

| Decisão | Opções | Sua Escolha | Justificativa |
| --------- | -------- | ------------- | --------------- |
| **Deploy** | Docker single container (um só contêiner) | Kubernetes (orquestrador de contêineres) | ? |
| **Workers** | Uvicorn sync | Uvicorn async + threads | ? |
| **State** | Stateless (cada request independente) | Session store compartilhado | ? |
| **Rate Limiting** | Na API / no LB / no agent | ? | ? |
| **Observability** | Logging básico | Structured logging + tracing | ? |
| **Database** | Nenhuma / SQLite / Redis (banco em memória para estado compartilhado veloz) | ? | ? |

### 3. Plano de Escalonamento

Descreva como lidar com crescimento:

| Cenário | Comportamento Atual | Comportamento Escalado |
| --------- | -------------------- | ---------------------- |
| 100 usuários | ? | ? |
| 500 usuários | ? | ? |
| 1000 usuários | ? | ? |
| 5000 usuários | ? | ? |

O que muda em cada nível? (workers, memória, conexões)

### 4. Garantia de Disponibilidade

| Requisito | Implementação |
| ----------- | -------------- |
| Zero downtime deploy (atualizar o serviço sem nenhum período fora do ar) | ? |
| Crash recovery | ? |
| Health checks | ? |
| Circuit breaker (LLM cai) | ? |

---

## Checklist de Validação

- [ ] Arquitetura suporta 1000 usuários simultâneos
- [ ] Deploy sem downtime considerado
- [ ] Isolamento de falhas (crash no agent não derruba API)
- [ ] Rate limiting implementado para proteger contra abuso
- [ ] Custo estimado dentro de $300/mês
- [ ] Plano de escalonamento progressivo

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
| ---------- | -------------- | --------- | ----------- |
| **Concorrência** | Thread/async bem dimensionado | Dimensionamento básico | Ignora concorrência |
| **Isolamento** | Falhas contidas por camada | Contenção parcial | Propagação livre |
| **Deploy** | Zero downtime planejado | Deploy com brief outage | Downtime necessário |
| **Custo** | Estimativa realista por recurso | Estimativa grossa | Sem cálculo |
