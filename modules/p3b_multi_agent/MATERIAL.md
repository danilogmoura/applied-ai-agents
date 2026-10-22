# Material Didático — P3b: Sistema Multiagente

## Conceitos Fundamentais

### Por que Múltiplos Agentes?

Um único agente tentando fazer tudo é como um generalista tentando ser expert em todas as áreas. Sistemas multiagente oferecem:

| Agente Único | Múltiplos Agentes |
| -------------- | ------------------- |
| Prompt genérico | Prompts especializados por domínio |
| Falha única = sistema todo falha | Especialista falha = fallback para outro |
| Custo alto (contexto grande) | Custo otimizado (cada agente tem contexto mínimo) |
| Dificil de debugar | Isolamento de problemas por especialista |

### Arquitetura Supervisor-Especialista

```
                    ┌──────────────┐
  Tarefa do Usuário │  SUPERVISOR  │
─────────────────→  │   (Router)   │
                    └──────┬───────┘
                           │ Decide qual especialista
              ┌────────────┼────────────┐
              ↓            ↓            ↓
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Análise  │ │ Pesquisa │ │ Tradução │
        │  de Dados│ │    Web   │          │
        └──────────┘ └──────────┘ └──────────┘
```

O supervisor:

1. **Entende** a intenção da tarefa
2. **Roteia** para o especialista mais adequado
3. **Coordena** retries e fallbacks
4. **Consolida** a resposta final

### Roteamento: LLM vs Heurísticas

Dois approaches para decidir qual especialista chamar:

**LLM-based routing** (produção):

```python
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": 
        f"Qual especialista deve lidar com: '{task}'?\n"
        f"Especialistas disponíveis: {specialists}"}]
)
```

**Heuristic routing** (demonstração):

```python
if "dados" in task.lower():
    return data_analyst_agent
elif "traduz" in task.lower():
    return translation_agent
```

Heurísticas são mais rápidas e baratas, mas menos flexíveis. LLM routing adapta-se a novas tarefas sem código novo.

### Degradation Elegante

Quando um especialista falha, o sistema não para — ele tenta alternativas:

```
Especialista A falha → Tenta Especialista B → Se B também falhar → Resposta parcial + aviso
```

Isso é chamado de **graceful degradation**: o sistema continua funcionando (mesmo que parcialmente) ao invés de crashar completamente.

### Custos em Multiagente

Cada chamada ao LLM custa tokens. Em multiagente, temos custos adicionais:

```
Custo Total = Custo_Supervisor + Σ Custo_Especialistas
```

O supervisor faz pelo menos 1 chamada (roteamento), e cada especialista pode fazer múltiplas chamadas (com retry). Isso significa que multiagente é tipicamente **mais caro** que agente único — mas entrega **melhor qualidade**.

---

## Exercício Prático

Execute `python modules/p3b_multi_agent/run.py` e observe:

1. Como o supervisor roteia diferentes tipos de tarefas
2. O que acontece quando um especialista falha (simulado)
3. Como o fallback redistribui para outro especialista
4. O log completo de roteamento gerado

## Perguntas para Reflexão

1. Se você tivesse 20 especialistas, o roteamento ficaria caro demais? Que alternativa existiria?
2. Como coordenar dois especialistas que precisam trabalhar juntos na mesma tarefa?
3. Quando faria sentido ter agentes hierárquicos (supervisor → sub-supervisores → especialistas)?

---

## Referências

### Livros

- **"Multiagent Systems"** by Kai Yu et al. — Fundamentos teóricos de sistemas multiagente
- **"Team of Agents"** by Dong et al. (DeepMind) — Paper sobre coordenação de agentes

### Documentação Oficial

- [OpenAI Function Calling for Routing](https://platform.openai.com/docs/guides/function-calling)
- [LangGraph Multi-Agent Patterns](https://langchain-ai.github.io/langgraph/) — LangChain Docs

### Vídeos

- [Building Multi-Agent Systems](https://www.youtube.com/watch?v=fJBhIuxLfPA) — AI Engineer, YouTube
- [The Future is Multi-Agent](https://www.youtube.com/watch?v=vT67ytB64JM) — Julian Deuckers, YouTube

### Tutoriais

- [CrewAI Framework](https://docs.crewai.com/) — Multi-agent orchestration
- [AutoGen by Microsoft](https://microsoft.github.io/autogen/) — Conversational agents framework
