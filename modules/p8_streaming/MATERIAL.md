# Material Didático — P8: Streaming e Tempo Real

## Conceitos Fundamentais

### Por que Streaming?

Imagine esperar 5 segundos por uma resposta vs ver cada palavra aparecer em tempo real. A diferença na experiência do usuário é enorme.

```
Sem streaming:          Com streaming:
[....................] [Generating...]
                       [Generatin...g AI...]
                       [Generating AI Assistant]
Espera 5s              Usuário vê progresso
```

### Server-Sent Events (SSE)

Protocolo simples para enviar dados do servidor ao cliente em tempo real:

```
data: {"type": "chunk", "content": "Hello"}

data: {"type": "chunk", "content": ", I'm an AI"}

data: {"type": "done", "tokens": 15, "cost": 0.001}
```

Vantagens sobre WebSocket:

- **Unidirecional**: só servidor → cliente (suficiente para LLM responses)
- **HTTP nativo**: funciona com qualquer proxy/load balancer
- **Reconexão automática**: browser reconecta se cair
- **Mais simples**: menos código no servidor

### Abort/Cancel

Usuários podem querer cancelar geração:

```python
# Cliente envia sinal de abort
agent.abort()

# Servidor para de gerar
if agent._abort_event.is_set():
    yield "[ABORTADO PELO USUÁRIO]"
    return
```

### Latência Percebida vs Real

| Métrica | Sem Streaming | Com Streaming |
| --------- | -------------- | --------------- |
| Tempo até primeira palavra | 3s | 0.2s |
| Tempo total | 5s | 5s |
| UX | "Está travado?" | "Já está respondendo!" |

O tempo total é o mesmo, mas a percepção é completamente diferente.

---

## Exercício Prático

Execute `python modules/p8_streaming/run.py` e observe:

1. Como os chunks aparecem progressivamente no terminal
2. O indicador de tempo mostrando evolução
3. A demonstração de abort/cancel após 3 chunks
4. O formato SSE que seria enviado via HTTP

## Perguntas para Reflexão

1. Se você fosse implementar FastAPI + SSE, como seria o endpoint?
2. Quando abortar automaticamente? Que critérios seriam razoáveis?
3. Como calcular custo estimado antes de começar a gerar?

---

## Referências

### Livros

- **"High Performance Python"** by Guido van Rossum & Jeff Bezanson — Capítulos sobre async programming

### Documentação Oficial

- [OpenAI Streaming API](https://platform.openai.com/docs/api-reference/streaming) — OpenAI Docs
- [Server-Sent Events Spec](https://html.spec.whatwg.org/multipage/server-sent-events.html) — W3C

### Tutoriais

- [Real-time Responses with FastAPI](https://fastapi.tiangolo.com/) — FastAPI Docs
- [Async Generators in Python](https://docs.python.org/3/library/asyncio-task.html) — Python Docs
