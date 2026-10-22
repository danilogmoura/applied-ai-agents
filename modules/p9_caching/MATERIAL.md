# Material Didático — P9: Cache e Otimização de Custo

## Conceitos Fundamentais

### O Problema do Custo em Escala

LLMs cobram por token. Em produção, isso pode somar rapidamente:

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
