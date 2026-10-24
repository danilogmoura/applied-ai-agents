# Módulo P8 — Streaming e Tempo Real

> ⚠️ **Revisão:** Este material está em revisão ativa. Alguns conceitos avançados estão marcados como OPCIONAIS para não sobrecarregar iniciantes.

## ⚠️ Pré-requisito

Você precisa ter concluído o módulo [P7: Memória e Contexto](../p7_memory/MATERIAL.md). Especificamente, precisa saber:

- Como gerenciar contexto em agentes de longo prazo
- Patterns de memória de curto e longo prazo

---

## 📋 Sumário

### 🔵 Core Obrigatório

1. Objetivos de Aprendizagem
2. Por que Streaming?
3. Erros Comuns de Iniciantes
4. Latência Percebida vs Real
5. O que você vai ver
6. Exercício Prático
7. Perguntas para Reflexão
8. Resumo do Módulo

### 🔬 Avançado — OPCIONAL

1. Server-Sent Events (SSE)
2. Como SSE Funciona no Wire
3. Abort/Cancel
4. Buffering Inteligente
5. Arquitetura do Pipeline Streaming

### 🛠️ Prático

 1. 📦 Infraestrutura do Curso
 2. ❓ Troubleshooting

---

## ⚠️ Pré-requisito

Você precisa ter concluído o módulo [P7: Memória e Contexto](../p7_memory/MATERIAL.md). Especificamente, precisa saber:

- Como gerenciar contexto em agentes de longo prazo
- Patterns de memória de curto e longo prazo

---

## 🎯 Objetivos de Aprendizagem

Ao final deste módulo, você será capaz de:

- [ ] **Explicar** a diferença entre latência percebida vs real (por que streaming muda UX)
- [ ] **Implementar** Server-Sent Events (SSE) para enviar respostas progressivamente
- [ ] **Entender** o formato SSE no wire (text/event-stream, \n\n separator)
- [ ] **Implementar** abort/cancel para permitir que usuário cancele geração
- [ ] **Aplicar** buffering inteligente (2-4 tokens por envio) para evitar jitter aparente

> 💡 **Dica:** Streaming é pura psicologia do usuário. O tempo total pode ser o mesmo, mas ver progresso imediato muda completamente a percepção. É uma das melhorias de UX com maior ROI em qualquer aplicação de IA.

---

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

### Por que isso existe?

LLMs são lentos para gerar texto completo. Um modelo pode levar 3-10 segundos para escrever uma resposta razoável. Sem streaming, o usuário fica olhando para uma tela em branco sem saber se:

- O sistema travou
- Está processando
- Vai demorar mais

Com streaming, o usuário **vê progresso imediato** — a primeira palavra aparece em ~200ms. Isso muda completamente a percepção de velocidade, mesmo que o tempo total seja o mesmo.

Além da UX, streaming permite:

- **Abort/cancel**: usuário cancela geração se perceber que o agente está errado
- **Feedback visual**: indicador de carregamento natural
- **Responsividade**: interface não bloqueia enquanto gera

### Erros Comuns de Iniciantes

| Erro | Consequência | Correção |
| ------ | -------------- | ---------- |
| Gerar tudo antes de enviar | UX ruim, timeout em respostas longas | Usar SSE para enviar chunks progressivos |
| Não implementar abort | Usuário precisa recarregar página inteira | Implementar sinal de abort + verificar no loop |
| Enviar chunk por chunk sem buffer | Rede sobrecarregada, jitter aparente | Buffer de 2-4 tokens por envio |
| Esquecer de fechar conexão SSE | Vazamento de recursos no servidor | Sempre fechar após `done` ou erro |
| Não testar com rede lenta | Streaming parece travado em mobile | Testar com throttling (3G simulation) |

### Server-Sent Events (SSE)

> 📖 Fonte: **[EN]** What are Server-Sent Events? · `fastapi-docs-en/docs/tutorial/server-sent-events.md` —
> "Each event is a small text block with 'fields' like `data`, `event`, `id`, and `retry`, separated by blank lines."

> 🔬 **AVANÇADO — OPCIONAL**: SSE é um protocolo simples para enviar dados do servidor ao cliente em tempo real. Entenda como "canal de notícias unidirecional" — servidor envia, cliente recebe.

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

> 📖 Fonte: **[EN]** StreamingResponse · `fastapi-docs-en/docs/advanced/custom-response.md` —
> "Since this small example does not need any `await` statements, we add an `await anyio.sleep(0)` to give the event loop a chance to handle cancellation."

> 🔬 **AVANÇADO — OPCIONAL**: Usuários podem querer cancelar geração. Implementar sinal de abort + verificar no loop.

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

> 📖 Fonte: **[EN]** AI Engineering · Chip Huyen · 2024 · OEBPS/ch09 —
> "Would your users prefer instant first tokens with a longer wait between tokens, or would they rather wait slightly longer for the first tokens but enjoy faster token generation afterward?"

| Métrica | Sem Streaming | Com Streaming |
| --------- | -------------- | --------------- |
| Tempo até primeira palavra | 3s | 0.2s |
| Tempo total | 5s | 5s |
| UX | "Está travado?" | "Já está respondendo!" |

O tempo total é o mesmo, mas a percepção é completamente diferente.

### Como SSE Funciona no Wire

> 🔬 **AVANÇADO — OPCIONAL**: SSE é HTTP com conexão mantida aberta e formato de texto simples. Não é mágica — é protocolo padrão da web.

SSE não é mágica — é **HTTP com conexão mantida aberta** e um formato de texto simples:

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```

A conexão TCP permanece aberta e o servidor envia chunks periodicamente:

```
event: message
data: {"chunk": "Hello", "index": 0}

event: message
data: {"chunk": ", World", "index": 1}

event: done
data: {"total_tokens": 15, "cost": 0.001}
```

### 🏗️ Arquitetura do Pipeline Streaming

> 📖 Fonte: **[EN]** What is a Stream? · `fastapi-docs-en/docs/tutorial/stream-json-lines.md` —
> "So, it will send the first item, the client will receive and start processing it, and you might still be producing the next item."

> 🔬 **AVANÇADO — OPCIONAL**: Esta seção detalha a arquitetura interna do pipeline streaming (SSE Server, Buffer Manager, Token Counter, Abort Handler).

Referência completa: [architecture.md](architecture.md)

O pipeline streaming é composto por 5 componentes:

```
[Cliente] ←── [SSE Server] ←── [LLM API]
    ↑              ↓              ↓
[Abort Signal] [Buffer Manager] [Token Counter]
```

| Componente | Responsabilidade | Parâmetro crítico |
| ------------ | ------------------ | ------------------- |
| **SSE Server** | Mantém conexão HTTP aberta + formata eventos | keep-alive timeout |
| **Buffer Manager** | Agrupa tokens em chunks (2-4 tokens) | buffer_size, flush_interval |
| **Token Counter** | Conta tokens acumulados + custo | max_tokens |
| **Abort Handler** | Verifica sinal de cancelamento | abort_event.is_set() |
| **LLM Generator** | Gera tokens um-a-um (async generator) | yield token |

**Fluxo completo:**

1. Cliente envia request → SSE Server abre conexão HTTP
2. LLM gera token 1 → Token Counter incrementa → Buffer Manager acumula
3. Buffer cheio (2-4 tokens) → SSE Server envia chunk formatado
4. Repete passos 2-3 até LLM terminar
5. SSE Server envia evento `done` com métricas finais
6. Se cliente envia abort → Abort Handler para geração

**Trade-off chave:** buffer maior = menos chunks mas mais delay inicial; buffer menor = mais responsivo mas mais overhead de rede.

## 🎬 O que você vai ver

**Regra crítica**: cada evento deve terminar com **duas quebras de linha** (`\n\n`). O cliente lê até encontrar `\n\n` e então processa o evento.

**Por que streaming é mais rápido que wait-for-complete?**

```mermaid
flowchart LR
    subgNoStream["Wait-for-complete"]
    subgStream["Streaming"]
    
    NoStream["⏳ Espera 5s completos"] --> UX1["📄 Tudo de uma vez"]
    Stream0["⚡ 0.2s"] --> Word1["📝 Primeira palavra!"]
    Stream1["⚡ 0.4s"] --> Word2["📝 Mais palavras..."]
    Stream2["⚡ 0.6s"] --> Word3["📝 Continua..."]
    Word3 --> UX2["UX percebida instantânea"]
```

**Tempo até UX:** 0.2s (streaming) vs 5.0s (wait-for-complete)

O servidor usa `yield` (generator) para enviar cada chunk sem esperar o resto. No Python com FastAPI, isso é `StreamingResponse` + async generator.

## 🎬 O que você vai ver

Antes de rodar o código, aqui está uma prévia do que o programa vai fazer:

```
$ python modules/p8_streaming/run.py

📡 Iniciando streaming...

⏱️ 0.2s → "Olá! Aqui é seu assistente..."
⏱️ 0.4s → " Vou ajudar você com sua pergunta sobre IA."
⏱️ 0.6s → " Primeiramente, é importante entender que..."
⏱️ 0.8s → "...agentes de IA usam ferramentas externas..."
   ⚠️ Abort após 3 chunks — cancelado pelo usuário

📊 Formato SSE enviado:
   data: {"text": "Olá!", "done": false}
   data: {"text": " Vou ajudar", "done": false}
   data: {"text": "", "done": true}
```

## 📦 Infraestrutura do Curso

Este módulo usa os mesmos módulos compartilhados dos anteriores:

```
applied-ai-agents/
├── modules/
│   ├── p8_streaming/
│   │   ├── run.py          ← Executa streaming agent + SSE event generator
│   │   └── exercises.py       ← Exercícios práticos (IMPLEMENTE os TODOs!)
├── shared/                  ← Módulos reutilizáveis em TODOS os módulos
│   ├── cost.py              ← count_tokens(), estimate_cost()
│   └── logging_config.py    ← setup_logging(), measure_latency()
└── ...
```

**Dependências necessárias:** `pip install aiohttp rich`

### Analogia: sys.path.insert(0, ...)

Quando você vê `sys.path.insert(0, str(Path(__file__).parent.parent))` no início de cada arquivo Python, pense assim:

> 📚 **Analogia dos Livros na Estante:** Imagine que o Python é uma pessoa procurando livros numa biblioteca. Normalmente ela só procura nas estantes próximas (diretório atual). O `sys.path.insert(0, ...)` é como dizer: "Antes de procurar aqui, também olhe naquela estante específica!" — neste caso, a estante `shared/` que está dois níveis acima. É como dar um atalho para o Python encontrar os módulos compartilhados sem precisar copiá-los para cada pasta.

### Módulos `shared/` Usados Neste Módulo

| Módulo | Função | Como é usado |
|--------|--------|--------------|
| `shared/cost.py` | Contagem de tokens e estimativa de custo | `count_tokens(text, model)` para calcular tokens gerados |
| `shared/logging_config.py` | Configuração de logs e medição de latência | `setup_logging()` + `measure_latency()` para medir tempo entre chunks |

---

## ❓ Troubleshooting

| Problema | Causa Provável | Solução |
| ---------- | ---------------- | --------- |
| `ModuleNotFoundError: No module named 'shared'` | sys.path não configurado corretamente | Verifique `sys.path.insert(0, str(Path(__file__).parent.parent))` no início do arquivo |
| `asyncio.run() missing 1 required positional argument` | Função async mal chamada | Use `asyncio.run(async_function())` — note os dois parênteses |
| Rich Live não atualiza no terminal | Terminal muito pequeno ou sem suporte a ANSI | Aumente o terminal ou use `console = Console(force_terminal=True)` |
| SSE connection drops immediately | Servidor fecha conexão prematuramente | Verifique se `Content-Type: text/event-stream` está sendo enviado |
| Chunks aparecem muito rápido/lento | Buffer size inadequado | Ajuste buffer_size: menor = mais chunks, maior = menos chunks |
| `ImportError: No module named aiohttp` | Dependência não instalada | Execute `pip install aiohttp rich` |

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

## 📌 Resumo do Módulo

Streaming é sobre percepção do usuário, não velocidade real:

1. **Latência percebida vs real** — usuário espera <2s para ver primeira palavra. Se esperar 10s sem nada, acha que travou. Streaming resolve percepção, não latência.

2. **SSE = protocolo simples** — servidor envia chunks `data: {"token": "..."}` via HTTP keep-alive. Cliente lê incrementalmente. Formato padrão da indústria.

3. **Buffering inteligente** — mostrar palavras completas (não caracteres) evita flickering. Buffer de 3-5 tokens = fluidez sem delay.

4. **Abort/cancel = controle do usuário** — se usuário percebe erro, pode cancelar geração. Implementar com asyncio.CancelledError e cleanup adequado.

5. **Custo estimado antes de gerar** — contar tokens do input, estimativa do output, custo por token. Alertar usuário ANTES de gastar $0.50 em resposta.

> ✅ **Você está pronto para:** Agora que respostas são responsivas, vamos otimizar custos com cache.

## ✅ Checklist: Como Saber Se Você Atingiu o Objetivo

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] Explico por que streaming melhora a experiência do usuário (tempo percebido)
- [ ] Descrevo como SSE funciona (data: ... \n\n)
- [ ] Explico a diferença entre streaming e wait-for-complete
- [ ] Rodo `run.py` e observo os chunks aparecendo progressivamente
- [ ] Digo 2 casos onde streaming NÃO é necessário

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

---

## 🔗 Próximos Passos

Com streaming, seus agentes respondem rapidamente. Mas respostas repetidas gastam tokens desnecessariamente — cache resolve isso.

→ Leia o módulo [P9: Caching](../p9_caching/MATERIAL.md) para aprender estratégias de cache e políticas de evicção.

---

## Material Complementar

(empty)

---

## 🧭 Navegação

| ← Anterior | Índice | Próximo → |
| --- | --- | --- |
| [← P7: Memória e Contexto](../p7_memory/MATERIAL.md) | [📖 Sumário do curso](../../README.md) | [P9: Cache e Otimização de Custo →](../p9_caching/MATERIAL.md) |
