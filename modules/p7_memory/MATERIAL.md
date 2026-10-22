# Material Didático — P7: Memória e Contexto

## Conceitos Fundamentais

### O Problema do Contexto Limitado

LLMs têm um limite de tokens que podem processar por vez (gpt-4o-mini: 128K tokens). Mas em conversas longas, esse limite é rapidamente excedido. Como gerenciar?

### Short-Term Memory = Conversation History

Memória de curto prazo é o histórico da conversa atual:

```
[system]: Você é um assistente...
[user]: Olá, meu nome é João
[assistant]: Olá João! Como posso ajudar?
[user]: Qual meu nome?
[assistant]: Você se chamou João...
```

Estratégias de gestão quando o contexto enche:

| Estratégia | Como funciona | Vantagem | Desvantagem |
|------------|--------------|----------|-------------|
| **Sliding Window** | Remove mensagens mais antigas | Simples | Perde contexto importante |
| **Token Budget** | Para de adicionar ao atingir limite | Previsível | Ignora novas mensagens |
| **Summarization** | Resume segmentos antigos | Preserva informação | Custo de sumarização |

### Long-Term Memory = Persistent Knowledge

Memória de longo prazo persiste entre sessões:

```
Sessão 1: "Meu nome é João" → salva no LT memory
Sessão 2: "Qual meu nome?" → recupera do LT memory → responde corretamente
```

Funciona como um vector store simplificado:
1. Embedding do conteúdo
2. Busca por similaridade com a query
3. Retorna memórias mais relevantes

### Summarization Automática

Quando o contexto está cheio, resume segmentos anteriores:

```
Original: 50 mensagens × 200 tokens = 10.000 tokens
Resumido: 1 summary × 100 tokens = 100 tokens
Economia: 99% de espaço liberado
```

### Importância e Forgetting

Nem tudo na memória é igualmente importante:

- **Alta importância**: Preferências do usuário, dados pessoais
- **Baixa importância**: Conversas triviais, saudações

Sistema de forgetting remove memórias de baixa importância automaticamente.

---

## Exercício Prático

Execute `python modules/p7_memory/run.py` e observe:

1. Como as memórias são armazenadas e recuperadas
2. A consulta de memória funcionando ("O que eu disse sobre minha experiência?")
3. A summarização automática quando o contexto enche
4. O status completo de ambos os tipos de memória

## Perguntas para Reflexão

1. Quando resumir vs quando deletar? Que critérios definiriam isso?
2. Se você tivesse 1000 interações, quantas memórias de longo prazo seriam razoáveis?
3. Como evitar que memórias incorretas ou enviesadas persistam?

---

## Referências

### Livros

- **"Memory and Computation"** — Capítulos sobre sistemas de memória em IA
- **"Building LLM Apps"** by Albert Vander Smith — Capítulos sobre context management

### Documentação Oficial

- [LangChain ConversationBufferWindowMemory](https://python.langchain.com/docs/modules/memory/) — LangChain Docs
- [Context Window Management](https://platform.openai.com/docs/guides/context-window) — OpenAI Docs

### Vídeos

- [LLM Memory Systems Explained](https://www.youtube.com/watch?v=ZCGdyYJVIoQ) — AI Planner, YouTube
- [Building Agents with Memory](https://www.youtube.com/watch?v=fJBhIuxLfPA) — AI Engineer, YouTube

### Tutoriais

- [Conversation Memory Patterns](https://langchain-ai.github.io/langgraph/concepts/memory/) — LangGraph Docs
- [Vector Store for Memory](https://docs.trychroma.com/) — ChromaDB Docs
