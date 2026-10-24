# Módulo 14 — Cache e Otimização de Custo

## ⚠️ Pré-requisito

> 🧭 Você está no **bloco avançado** (M08→M16). Perdido na sequência? Veja o [Mapa do Bloco Avançado](../08-multiagente/MATERIAL.md#-mapa-do-bloco-avançado-módulos-08--16).

Você precisa ter concluído o módulo [Módulo 13 — Streaming e Tempo Real](../13-streaming/MATERIAL.md). Especificamente, precisa saber:

- Como implementar streaming de respostas em tempo real
- Padrões de SSE (Server-Sent Events) e WebSockets

---

## 📋 Sumário

### 🔵 Core Obrigatório

1. Objetivos de Aprendizagem
2. Por que Cache?
3. Erros Comuns de Iniciantes
4. Cache de Respostas
5. O que você vai ver
6. Exercício Prático
7. Perguntas para Reflexão
8. Resumo do Módulo

### 🔬 Avançado — OPCIONAL

1. Arquitetura da Cache Layer
2. Algoritmo: LRU vs LFU (Eviction Policy)
3. Model Routing
4. Como Funciona Internamente

### 🛠️ Prático

 1. 📦 Infraestrutura do Curso
 2. ❓ Troubleshooting

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

> 📖 Fonte: **[EN]** AI Engineering · Chip Huyen · 2024 · OEBPS/ch02 —
> "Number of tokens a model was trained on, which is a proxy for how much a model learned."

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

### Cache de Respostas

> 📖 Fonte: **[EN]** AI Engineering · Chip Huyen · 2024 · OEBPS/ch09 —
> "With a prompt cache, the system prompt needs to be processed just once for the first query."

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

> 📖 Fonte: **[EN]** Systems Design for the LLM Era · Sampriti Mitra · OEBPS/Text/Chapter_5 —
> "This optimization layer shields our database, but the query cache remains our core strategy."

> 🔬 **AVANÇADO — OPCIONAL**: Esta seção detalha a arquitetura interna da cache layer (Cache Proxy, Key Generator, Lookup, Fill, Store, Eviction).

Referência completa: [architecture.md](architecture.md)

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

> 📖 Fonte: **[EN]** AI Engineering · Chip Huyen · 2024 · OEBPS/ch10 —
> "Common eviction policies include Least Recently Used (LRU), Least Frequently Used (LFU), and first in, first out (FIFO)."

> 🔬 **AVANÇADO — OPCIONAL**: Quando o cache enche, precisa decidir o que remover. LRU = "último a usar, primeiro a sair"; LFU = "menos usado, primeiro a sair".

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

> 💡 **Modelo é exemplo, não requisito**
> Onde este módulo usa `gpt-4o-mini`, leia "qualquer LLM de chat". O nome do modelo
> não faz parte dos conceitos ensinados — trocar por Claude, Gemini, Qwen ou um modelo
> local (Ollama) é só mudar a string `model=` (ou exportar `MODEL` no `.env`). Os run.py
> já lêem `shared.security.get_model()`, que respeita `MODEL`/`DEFAULT_MODEL` do ambiente.

### Model Routing

> 📖 Fonte: **[EN]** AI Engineering · Chip Huyen · 2024 · OEBPS/ch10 —
> "Instead of using one expensive model for all queries, you can route simpler queries to cheaper models."

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

> 📖 Fonte: **[EN]** AI Engineering · Chip Huyen · 2024 · OEBPS/ch09 —
> "With a prompt cache, overlapping segments in different prompts can be cached and reused."

Remover whitespace, duplicatas e informações redundantes antes de enviar ao LLM.

```
Original: 500 tokens
Comprimido: 350 tokens
Economia: 30%
```

## 📦 Infraestrutura do Curso

Este módulo usa os mesmos módulos compartilhados dos anteriores:

```
applied-ai-agents/
├── modules/
│   ├── 14-cache/
│   │   ├── run.py          ← Executa response cache + model router
│   │   └── exercises.py       ← Exercícios práticos (IMPLEMENTE os TODOs!)
├── shared/                  ← Módulos compartilhados (reutilizados em todos os módulos)
│   ├── cost.py              ← count_tokens(), estimate_cost()
│   └── logging_config.py    ← setup_logging(), measure_latency()
└── ...
```

**Dependências necessárias:** nenhuma extra além dos módulos anteriores.

### Analogia: `sys.path.insert(0, ...)`

> Explicação completa no **Módulo 01** — seção [Por que `sys.path.insert(0, ...)` no código?](../01-fundamentos/MATERIAL.md#por-que-syspathinsert0--no-código).
> Resumo: é um atalho que diz ao Python para procurar também na raiz, onde está `shared/`, em vez de só na pasta do módulo.

### Módulos `shared/` Usados Neste Módulo

| Módulo | Função | Como é usado |
|--------|--------|--------------|
| `shared/cost.py` | Contagem de tokens e estimativa de custo | `count_tokens(text, model)` para calcular tokens gerados e custos evitados |
| `shared/logging_config.py` | Configuração de logs e medição de latência | `setup_logging()` + `measure_latency()` para medir tempo de lookup vs chamada LLM |

---

## ❓ Troubleshooting

| Problema | Causa Provável | Solução |
| ---------- | ---------------- | --------- |
| `ModuleNotFoundError: No module named 'shared'` | sys.path não configurado corretamente | Verifique `sys.path.insert(0, str(Path(__file__).parent.parent))` no início do arquivo |
| Cache não funciona após reiniciar script | Cache em memória (RAM) perde dados ao reiniciar | Use SQLite ou Redis para persistência entre sessões |
| Chaves de cache colidem (hash collision) | Hash muito curto ou algoritmo fraco | Use `hashlib.sha256()` com input normalizado |
| Cache serve resposta antiga demais | TTL muito longo ou falta de invalidation | Ajuste TTL conforme domínio (curto para dados dinâmicos, longo para FAQ) |
| `ImportError: No module named redis` | Dependência não instalada | Execute `pip install redis` se quiser usar Redis real |
| Hit rate muito baixo (< 10%) | Queries nunca se repetem ou key generation inconsistente | Normalize inputs (lowercase, strip) e aumente TTL |

---

## 🎬 O que você vai ver

Antes de rodar o código, aqui está uma prévia do que o programa vai fazer:

```
$ python modules/14-cache/run.py

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

> ⏸️ **Rode agora — cache + routing**
>
> Antes de ler sobre LRU vs LFU e prompt compression, execute a camada de otimização:
>
> ```bash
> python modules/14-cache/run.py
> ```
>
> Você deve ver o model routing escolhendo modelos diferentes por tarefa, a segunda chamada respondida do cache com custo `$0`, e o total de custo evitado no fim.
>
> Se a saída divergir disso, revise os pré-requisitos antes de continuar.

## Exercício Prático

Execute `python modules/14-cache/run.py` e observe:

1. Como o model routing escolhe modelos diferentes para tarefas diferentes
2. A segunda chamada usa cache (custo = $0)
3. A compressão de prompts reduzindo tokens
4. As estatísticas de economia total

## Perguntas para Reflexão

1. Quando NÃO usar cache? Que respostas não devem ser cacheadas?
2. Se você tivesse 1 milhão de usuários, quantos GB de cache precisaria?
3. Como balancear velocidade vs qualidade ao escolher modelos?

---

## 📖 Glossário

> 📚 Este é o glossário local do módulo. Todos os termos e siglas dos 16 módulos estão consolidados no **[Glossário Unificado](../../GLOSSARIO.md)**.

| Termo | Definição | Analogia |
| ------- | ----------- | ---------- |
| **Cache de Respostas** | Guardar saídas passadas para reusar em perguntas idênticas e cortar custo | Gabarito colado na parede para não recalcular |
| **Eviction Policy** | Regra de quais itens remover quando a cache está cheia | Estante lotada: tirar o menos usado |
| **LRU** | Least Recently Used: remove o item há mais tempo não acessado | Quem pega por último fica na frente |
| **LFU** | Least Frequently Used: remove o item menos acessado no total | Livro que ninguém folheia sai primeiro |
| **Model Routing** | Escolher modelo diferente conforme dificuldade/custo da requisição | Casos simples pro estagiário, complexos pro sênior |
| **Prompt Compression** | Reduzir o tamanho do prompt preservando sentido, cortando tokens/custo | Resumir o e-mail longo em duas linhas |

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

→ Leia o módulo [Módulo 15 — Design e Composição de Skills](../15-skills/MATERIAL.md) para aprender design e versionamento de skills.

---

## Material Complementar

(empty)

---

## ✅ Como verificar seus exercícios

Você tem três formas de checar se entendeu e implementou corretamente:

**1. Rodar os exercícios direto no terminal (feedback imediato):**
```bash
python modules/14-cache/exercises.py
```
Cada função `test_*` imprime ✓ ou ✗ e mostra quantos passaram. Preencha os `TODO` até ver **"Todos os exercícios passaram!"**.

**2. Validar automaticamente com pytest (modo aluno):**
```bash
CHECK_MY_EXERCISES=1 pytest -k "14-cache"
```
Isso roda os `asserts` dos seus exercícios como testes reais — ideal para CI ou para ter certeza antes de entregar.

**3. Comparar com o gabarito:**
Abra [`exercises_solution.py`](exercises_solution.py) depois de tentar sozinho. Ele é a referência oficial e passa em todos os próprios testes.

> 💡 **Dica:** tente primeiro sem olhar a solução. Se travar, releve a seção de conceito; só consulte o gabarito como último recurso — o aprendizado vem do esforço de implementar.

---

## 🧭 Navegação

| ← Anterior | Índice | Próximo → |
| --- | --- | --- |
| [← Módulo 13 — Streaming e Tempo Real](../13-streaming/MATERIAL.md) | [📖 Sumário do curso](../../README.md) | [Módulo 15 — Design e Composição de Skills →](../15-skills/MATERIAL.md) |
