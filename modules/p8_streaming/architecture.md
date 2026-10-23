# 🏗️ Architecture Design — Streaming de Respostas

> **Desafio:** Projete um sistema de streaming para respostas de LLM em tempo real.
>
> 🔬 **AVANÇADO / OPCIONAL** — Este desafio assume noções de arquitetura e infra. Se você ainda está aprendendo os fundamentos, tudo bem pular na primeira passada e voltar depois.

## Cenário

Uma aplicação web precisa mostrar respostas de IA token-by-token:

- **10K usuários simultâneos** em horário de pico
- **SLA**: TTFT (Time To First Token — tempo até o primeiro token, ou seja, quanto o usuário espera antes de ver a primeira palavra na tela) < 500ms
- **Orçamento**: máximo $500/mês em API calls
- **Requisito**: usuário pode cancelar geração a qualquer momento
- **Fallback**: se streaming falha, retorna resposta completa

---

## Entregáveis

> 🧭 **Como abordar este desafio.** Não existe uma única arquitetura correta — o que se avalia é o seu **raciocínio**. Sugestão de caminho:
>
> 1. Comece rascunhando o diagrama com blocos e setas (ASCII serve).
> 2. Para cada decisão na tabela, registre *o que escolheu* **e por quê**.
> 3. Feche com números de latência/custo, mesmo estimados.
>
> Exemplo ilustrativo (não é gabarito): em streaming, marque no diagrama onde a resposta é "parcial" vs. "final" — é essa fronteira que define cancelamento e re-renderização.

### 1. Diagrama da Arquitetura

Descreva o fluxo do pipeline streaming:

```
[Cliente] ←── [SSE Server] ←── [LLM API]
    ↑              ↓
[Abort Signal] [Buffer Manager]
    ↑              ↓
[UI Feedback]  [Token Counter]
```

Defina:

- Quantos componentes independentes?
- Como o abort signal viaja do cliente ao servidor?
- Onde o buffering acontece (antes ou depois do LLM)?

### 2. Configuração do Buffer

Para cada parâmetro, defina valor e justificativa:

| Parâmetro | Valor | Justificativa |
| ----------- | ------- | --------------- |
| buffer_size | ? tokens | ? |
| flush_interval | ? ms | ? |
| max_tokens_per_response | ? | ? |
| TTFT_target | ? ms | ? |
| max_reconnect_attempts | ? | ? |

Explique o trade-off: buffer maior = menos chunks mas mais delay inicial.

### 3. Protocolo SSE Completo

Defina o formato exato dos eventos:

```
event: chunk
data: {"token": "...", "cumulative_cost": 0.001}

event: done
data: {"total_tokens": 150, "total_cost": 0.005, "ttft_ms": 230}

event: error
data: {"code": "RATE_LIMIT", "retry_after": 5}

event: abort
data: {}
```

O que cada evento contém? Quando é enviado?

### 4. Plano de Fallback e Recuperação

O que acontece quando cada componente falha:

| Falha | Comportamento | Fallback | UX Resultante |
| ------- | -------------- | ---------- | --------------- |
| Cliente perde conexão | ? | Reconexão automática | ? |
| Servidor reinicia | ? | Reenvia últimos chunks | ? |
| LLM rate limit | ? | Backoff + retry | ? |
| Timeout no TTFT | ? | Switch para wait-for-complete | ? |
| Abort não recebido | ? | Timeout global 60s | ? |

---

## Checklist de Validação

- [ ] Fluxo completo SSE definido
- [ ] Buffer configurado com parâmetros justificados
- [ ] Protocolo SSE com todos os eventos especificados
- [ ] Plano de fallback para cada tipo de falha
- [ ] TTFT dentro do SLA (< 500ms)
- [ ] Custo estimado dentro do orçamento ($500/mês)

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
| ---------- | -------------- | --------- | ----------- |
| **Protocolo SSE** | Todos eventos definidos | Eventos básicos | Formato incompleto |
| **Buffer** | Parâmetros otimizados | Valores padrão | Sem configuração |
| **Fallbacks** | Cobertura completa | Parcial | Ausente |
| **TTFT/UX** | Considera percepção | Apenas técnica | Ignora UX |
