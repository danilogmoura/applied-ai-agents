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

### 🏗️ Arquitetura da Cache Layer

> Referência completa: [architecture.md](architecture.md)

A cache layer é um proxy que intercepta todas as chamadas ao LLM:

```
[Usuário] → [Cache Proxy] → [LLM API]
              ↑         ↘
         [Lookup]    [Fill + Store]
              ↓
      [Eviction Policy]
```

| Componente | Responsabilidade | O que decide |
| ------------ | ------------------ | -------------- |
| **Cache Proxy** | Intercepta requests antes do LLM | Hit ou miss? |
| **Key Generator** | Cria hash único por query | `hash(prompt + model + params)` |
| **Lookup** | Verifica se chave existe no cache | Redis/SQLite/memory |
| **Fill** | Chama LLM em caso de miss | Preenche cache |
| **Store** | Salva resposta no cache | Com TTL definido |
| **Eviction** | Remove entradas antigas/full | LRU/LFU/TTL |

**Fluxo completo:**

1. Usuário envia query → Cache Proxy gera key = `hash(normalize(query))`
2. Lookup verifica se key existe no cache
3. Se HIT → retorna resposta instantaneamente ($0, 0 tokens)
4. Se MISS → chama LLM → Fill armazena resposta → Store define TTL
5. Quando cache enche → Eviction remove entrada menos útil (LRU/LFU)
6. Se dados subjacentes mudam → Invalida cache correspondente

**Trade-off chave:** cache em memória (RAM) = mais rápido mas perde ao reiniciar; Redis = persistente mas adiciona latência de rede.

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

#### Como funciona internamente (OPCIONAL — avançado)

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

Nem toda tarefa precisa do modelo mais caro. O princípio é simples: **use o menor modelo que resolve a tarefa**.

| Tarefa | Modelo Recomendado | Custo Relativo | Por quê? |
| -------- | ------------------- | ---------------- | ---------- |
| Classificar spam | gpt-4o-mini | 1x | Tarefa discreta, não precisa raciocínio complexo |
| Chat básico | gpt-4o-mini | 1x | Respostas curtas e diretas |
| Analisar sentimento | gpt-4o | 15x | Precisa entender nuance e ironia |
| Gerar conteúdo crítico | claude-opus | 100x | Qualidade irreprezível necessária |

Em produção, um **router inteligente** decide qual modelo usar baseado na complexidade da tarefa:

```python
complexity = estimate_complexity(user_query)  # heurística simples
if complexity < 0.3:
    model = "gpt-4o-mini"   # tarefas triviais
elif complexity < 0.7:
    model = "gpt-4o"        # tarefas moderadas
else:
    model = "claude-opus"   # tarefas críticas
```

Isso pode reduzir o custo médio em 40-60% sem perder qualidade perceptível.

### Prompt Compression

Remover whitespace, duplicatas e informações redundantes antes de enviar ao LLM.

```
Original: 500 tokens
Comprimido: 350 tokens
Economia: 30%
```

## 🎬 O que você vai ver

Antes de rodar o código, aqui está uma prévia do que o programa vai fazer:

```
$ python modules/p9_caching/run.py

🔄 Model routing: tarefa_classificação → gpt-4o-mini
   Custo: $0.002 | Latência: 0.8s

🔍 Segunda chamada idêntica...
   ✅ HIT no cache! Custo: $0.000 | Latência: 0.001s

📦 Compressão de prompt:
   Original: 500 tokens
   Comprimido: 350 tokens
   Economia: 30%

📊 Estatísticas:
   Chamadas: 10 | Cache hits: 7 (70%)
   Tokens economizados: 1.200
   Custo evitado: $0.014
```

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

## ✅ Checklist: Como Saber Se Você Atingiu o Objetivo

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] Explico o problema que cache resolve (respostas repetidas custam dinheiro)
- [ ] Descrevo quando usar cache vs quando não usar (determinístico vs criativo)
- [ ] Explico a diferença entre model routing e cache simples
- [ ] Rodo `run.py` e explico as estatísticas de economia
- [ ] Digo 2 estratégias de evicção de cache (LRU, TTL, etc.)

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

---

## 🔗 Próximos Passos

Com caching, seus agentes são econômicos. Mas como organizar código em componentes reutilizáveis e versionados?

→ Leia o módulo [P10: Skills](../p10_skills/MATERIAL.md) para aprender design e versionamento de skills.

---

## Referências

(empty)
- [Prompt Engineering Guide](https://www.promptingguide.ai/) — Prompting Guide
