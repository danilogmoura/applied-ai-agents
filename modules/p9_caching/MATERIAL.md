# Material Didático — P9: Cache e Otimização de Custo

## ⚠️ Pré-requisito

Você precisa ter concluído o módulo [P8: Streaming e Tempo Real](../p8_streaming/MATERIAL.md). Especificamente, precisa saber:

- Como implementar streaming de respostas em tempo real
- Padrões de SSE (Server-Sent Events) e WebSockets

---

## 🎯 Objetivos de Aprendizagem

Ao final deste módulo, você será capaz de:

- [ ] **Calcular** o ROI de cache (quanto se economiza vs custo de implementação)
- [ ] **Implementar** cache de respostas com TTL para perguntas repetidas (FAQ)
- [ ] **Escolher** entre LRU e LFU baseado no padrão de acesso (conversas vs FAQ)
- [ ] **Entender** como funciona internamente (hash map + doubly linked list para LRU)
- [ ] **Aplicar** model routing (enviar tarefas simples para modelos baratos)

> 💡 **Dica:** Cache é a otimização com maior ROI em produção. Se 30% das perguntas são repetidas (o que é comum), você corta custos em 30% sem mudar NADA no seu agente — só adicionando uma camada de cache.

---

## Conceitos Fundamentais

### O Problema do Custo em Escala

LLMs cobram por token. Em produção, isso pode somar rapidamente:

```
1000 chamadas × 500 tokens input × $0.15/1M = $0.075
1000 chamadas × 200 tokens output × $0.60/1M = $0.12
Total por dia: ~$0.20 → $6/mês para 1 usuário

Mas se tiver 10.000 usuários? $600/mês só em API calls!
```

### Por que isso existe?

Sem cache, cada pergunta idêntica custa dinheiro novamente:

```

Usuário A: "Qual a capital da França?" → $0.001
Usuário B: "Qual a capital da França?" → $0.001 ❌ MESMA PERGUNTA!
Usuário C: "Qual a capital da França?" → $0.001 ❌ TRÊS VEZES O MESMO!

```

Em escala, isso é desperdício enorme. Se 30% das perguntas são repetidas (FAQ comum), você está pagando 30% a mais sem necessidade.

Cache resolve isso memorizando respostas já geradas. Mas há um trade-off:

- **Cache hit**: resposta instantânea + custo zero ✅
- **Cache miss**: precisa chamar o modelo + custo normal ❌
- **Cache cheio**: precisa decidir o que remover (eviction policy)

### Erros Comuns de Iniciantes

| Erro | Consequência | Correção |
| ------ | -------------- | ---------- |
| Não usar TTL no cache | Respostas ficam para sempre → memória vazia | TTL de 24h-7d dependendo do domínio |
| Usar hash simples do texto | "França" vs "frança" = dois caches diferentes | Normalizar texto (lowercase, strip) |
| Escolher LRU para FAQ | Pergunta popular é removida porque foi usada há muito | LFU para dados repetidos, LRU para conversas |
| Ignorar cache invalidation | Dados mudam mas cache ainda serve versão antiga | Invalidar cache quando fonte de dados atualiza |
| Cache só em memória (RAM) | Reiniciar servidor = perder tudo | Redis ou SQLite para persistência |

### O Problema do Custo em Escala

Sem cache, cada pergunta idêntica custa dinheiro novamente:

```
Usuário A: "Qual a capital da França?" → $0.001
Usuário B: "Qual a capital da França?" → $0.001 ❌ MESMA PERGUNTA!
Usuário C: "Qual a capital da França?" → $0.001 ❌ TRÊS VEZES O MESMO!
```

Em escala, isso é desperdício enorme:

```
1000 chamadas × 500 tokens input × $0.15/1M = $0.075
1000 chamadas × 200 tokens output × $0.60/1M = $0.12
Total por dia: ~$0.20 → $6/mês para 1 usuário

Mas se tiver 10.000 usuários? $600/mês só em API calls!
```

### Cache de Respostas

Mesmo prompt + mesmo modelo = mesma resposta. Por que chamar a API de novo?

```python
# Primeira vez: cache miss
response = llm.call("Qual a capital da França?")  # $0.001
cache.put("capital+frança", response)

# Segunda vez: cache hit!
response = cache.get("capital+frança")  # $0.000 ✅
```

Em produção: Redis com TTL (Time To Live).

### Algoritmo: LRU vs LFU (Eviction Policy)

Quando o cache enche, precisa decidir o que remover. Duas estratégias principais:

```mermaid
flowchart LR
    subgLRU["LRU (Least Recently Used)"]
    A1["A acessado 10h"] -->|Removido| F1["F entra"]
    B1["B acessado 10:05"] -->|Mantido|
    C1["C acessado 10:10"] -->|Mantido|
    D1["D acessado 10:15"] -->|Mantido|
    E1["E acessado 10:20"] -->|Mantido|
    
    subgLFU["LFU (Least Frequently Used)"]
    A2["A: 1x acesso"] -->|Removido| F2["F entra"]
    B2["B: 3x acessos"] -->|Mantido|
    C2["C: 10x acessos"] -->|Mantido|
    D2["D: 50x acessos"] -->|Mantido|
    E2["E: 2x acessos"] -->|Mantido|
```

**Qual escolher?**

| Cenário | Melhor | Por quê? |
| --------- | -------- | ---------- |
| Chatbot (conversas sequenciais) | **LRU** | O que foi usado agora provavelmente será usado de novo |
| FAQ (perguntas repetidas) | **LFU** | As perguntas mais populares merecem ficar |
| Dados temporais (previsão do tempo) | **TTL puro** | Nem LRU nem LFU importam — dados expiram |
| Logs de sistema | **Nenhum** | Nunca reutiliza logs |

#### Como funciona internamente

```python
# LRU usa um Hash Map + Doubly Linked List
# Hash Map: O(1) para get/put
# Lista duplamente encadeada: ordena por recência

get(key):
    node = hashmap[key]
    move_to_front(node)  # marca como "recente"
    return node.value

put(key, value):
    if key exists:
        update_and_move_to_front()
    else:
        if cache full:
            evict_tail()  # remove o menos recente
        insert_at_head(key, value)
```

Redis implementa LRU aproximado (`maxmemory-policy allkeys-lru`) e LFU (`allkeys-lfu`). O LRU aproximado é uma otimização: em vez de verificar TODOS os keys, sorteia N amostras e remove o menos recente delas. Trade-off entre precisão e CPU.

### Model Routing

Nem toda tarefa precisa do modelo mais caro:

| Tarefa | Modelo Recomendado | Custo Relativo |
| -------- | ------------------- | ---------------- |
| Classificar spam | gpt-4o-mini | 1x |
| Chat básico | gpt-4o-mini | 1x |
| Analisar sentimento | gpt-4o | 15x |
| Gerar conteúdo crítico | claude-opus | 100x |

### Prompt Compression

Remover whitespace, duplicatas e informações redundantes antes de enviar ao LLM.

```
Original: 500 tokens
Comprimido: 350 tokens
Economia: 30%
```

---

## Exercício Prático

Execute `python modules/p9_caching/run.py` e observe:

1. Como o model routing escolhe modelos diferentes para tarefas diferentes
2. A segunda chamada usa cache (custo = $0)
3. A compressão de prompts reduzindo tokens
4. As estatísticas de economia total

## Perguntas para Reflexão

1. Quando NÃO usar cache? Que respostas não devem ser cacheadas?
2. Se você tivesse 1 milhão de usuários, quantos GB de cache precisaria?
3. Como balancear velocidade vs qualidade ao escolher modelos?

---

## 📌 Resumo do Módulo

Caching é a otimização de custo mais impactante em produção:

1. **ROI claro** — cada resposta cacheada custa $0.00 vs $0.0001 de lookup. Para prompts repetidos, economia é quase 100%. Cache é a primeira otimização a implementar.

2. **TTL = frescor vs economia** — TTL curto = dados frescos mas menos hits. TTL longo = mais hits mas risco de dados desatualizados. Balanceamento depende do domínio.

3. **LRU vs LFU** — LRU (Least Recently Used) funciona bem para acesso temporal. LFU (Least Frequently Used) melhor para acesso por frequência. Escolha depende do padrão de uso.

4. **Model routing inteligente** — tarefas simples → modelo barato; tarefas complexas → modelo caro. Reduz custo médio sem perder qualidade.

5. **Compressão de prompts** — remover tokens redundantes reduz custo por chamada. Prompt engineering não é só qualidade, é economia.

> ✅ **Você está pronto para:** Agora que custos estão otimizados, vamos estruturar skills reutilizáveis.

---

## 🔗 Próximos Passos

Com caching, seus agentes são econômicos. Mas como organizar código em componentes reutilizáveis e versionados?

→ Leia o módulo [P10: Skills](../p10_skills/MATERIAL.md) para aprender design e versionamento de skills.

---

## Referências

### Livros

- **"Designing Machine Learning Systems"** by Chip Huyen — Capítulos sobre cost optimization e caching strategies
- **"Fundamentals of Information Storage and Retrieval"** by Jean-Yves Marie — Capítulos sobre cache architectures

### Documentação Oficial

- [OpenAI Pricing](https://openai.com/api/pricing/) — OpenAI Docs
- [Redis Caching Best Practices](https://redis.io/docs/manual/caching/) — Redis Docs

### Tutoriais

- [LangChain Cache](https://python.langchain.com/docs/modules/model_io/output_parsers/) — LangChain Docs
- [Prompt Engineering Guide](https://www.promptingguide.ai/) — Prompting Guide
