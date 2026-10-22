# 🏗️ Architecture Design — De Script a Produto (Produção)

> **Desafio:** Projete a arquitetura para transformar um script Python local em um serviço de agente acessível por múltiplos usuários simultâneos.

## Cenário

Você tem um **script Python** que funciona bem localmente (1 usuário). Agora precisa:
- Atender **1000 usuários simultâneos**
- Manter **latência < 5s** por request
- Garantir que **um crash não derrube o serviço**
- Permitir **deploy sem downtime**
- Orçamento infra: máximo $300/mês

---

## Entregáveis

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
|---------|--------|-------------|---------------|
| **Deploy** | Docker single container | Kubernetes | ? |
| **Workers** | Uvicorn sync | Uvicorn async + threads | ? |
| **State** | Stateless (cada request independente) | Session store compartilhado | ? |
| **Rate Limiting** | Na API / no LB / no agent | ? | ? |
| **Observability** | Logging básico | Structured logging + tracing | ? |
| **Database** | Nenhuma / SQLite / Redis | ? | ? |

### 3. Plano de Escalonamento

Descreva como lidar com crescimento:

| Cenário | Comportamento Atual | Comportamento Escalado |
|---------|--------------------|----------------------|
| 100 usuários | ? | ? |
| 500 usuários | ? | ? |
| 1000 usuários | ? | ? |
| 5000 usuários | ? | ? |

O que muda em cada nível? (workers, memória, conexões)

### 4. Garantia de Disponibilidade

| Requisito | Implementação |
|-----------|--------------|
| Zero downtime deploy | ? |
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
|----------|--------------|---------|-----------|
| **Concorrência** | Thread/async bem dimensionado | Dimensionamento básico | Ignora concorrência |
| **Isolamento** | Falhas contidas por camada | Contenção parcial | Propagação livre |
| **Deploy** | Zero downtime planejado | Deploy com brief outage | Downtime necessário |
| **Custo** | Estimativa realista por recurso | Estimativa grossa | Sem cálculo |
