# Material Didático — P0: Primeiro Fluxo com LLM

## Conceitos Fundamentais

### O que é um Agente de IA?

Um agente de IA é um sistema que usa modelos de linguagem (LLMs) para tomar decisões e executar tarefas. No nível mais básico, um agente:

1. **Recebe uma entrada** (texto, dados, contexto)
2. **Processa com um LLM** (via API como OpenAI, Anthropic, etc.)
3. **Retorna uma saída** (resposta, decisão, ação)

Neste primeiro módulo, vamos construir o esqueleto mínimo de um agente: receber um "ticket" de suporte e classificar sua prioridade usando o GPT-4o-mini.

### Por que começar com classificação?

Classificação é uma das tarefas mais comuns em automação com IA:

- Triagem de tickets de suporte
- Filtragem de spam
- Categorização de conteúdo
- Detecção de sentimento

É simples o suficiente para entender o fluxo completo, mas realista o bastante para ser útil no mundo real.

### A API da OpenAI

A OpenAI oferece uma API RESTful para acessar seus modelos. O fluxo básico é:

```python
from openai import OpenAI

client = OpenAI()  # Lê OPENAI_API_KEY do ambiente
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Classifique este ticket..."}]
)
print(response.choices[0].message.content)
```

### Estimativa de Custos

Cada chamada à API tem um custo baseado no número de tokens. Tokens são pedaços de texto (palavras, partes de palavras, pontuação). A OpenAI cobra por milhão de tokens:

| Modelo | Custo por 1M tokens (input) |
|--------|---------------------------|
| gpt-4o-mini | $0.15 |
| gpt-4o | $2.50 |

Para um ticket de 200 tokens, o custo é ~$0.00003 — quase nada, mas importante rastrear em escala.

### Regras de Segurança

- **NUNCA** hardcode chaves de API no código
- Use variáveis de ambiente (`.env`)
- Valide que todas as chaves necessárias estão presentes antes de chamar a API
- Nunca exponha chaves nos logs

---

## Exercício Prático

Execute `python modules/p0_first_llm/run.py` e observe:

1. Como os tickets são processados em batch
2. O relatório de custos gerado automaticamente
3. A diferença entre classificação via LLM vs heurística (regras)

## Perguntas para Reflexão

1. Por que comparar IA com regras heurísticas? Qual a vantagem de cada abordagem?
2. Como você saberia se o LLM está classificando corretamente?
3. O que aconteceria se você processasse 10.000 tickets? Como os custos escalariam?

---

## Referências

### Livros

- **"Build Intelligent Apps with OpenAI"** — OpenAI Cookbook (gratuito, online)
- **"Natural Language Processing with Transformers"** by Lewis et al. (O'Reilly)

### Documentação Oficial

- [OpenAI Python SDK](https://platform.openai.com/docs/libraries/python)
- [OpenAI Pricing](https://openai.com/api/pricing/)
- [Tokenization Guide](https://platform.openai.com/docs/guides/tokenization)

### Vídeos

- [OpenAI Quickstart Tutorial](https://www.youtube.com/watch?v=LeRCbbKAuEQ) — YouTube

### Tutoriais

- [OpenAI Cookbook Examples](https://github.com/openai/openai-cookbook) — GitHub
- [Python OpenAI SDK Tutorial](https://platform.openai.com/docs/quickstart) — OpenAI Docs
