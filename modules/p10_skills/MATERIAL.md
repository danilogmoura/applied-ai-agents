# Material Didático — P10: Design e Composição de Skills

## Conceitos Fundamentais

### O que é uma Skill?

Uma skill é uma função especializada com interface bem definida:

```python
class SentimentSkill(BaseSkill):
    def execute(self, input_data: dict) -> dict:
        # Input: {"text": "Produto excelente!"}
        # Output: {"sentiment": "positive", "confidence": 0.85}
```

Skills são como APIs internas — cada uma faz UMA coisa bem.

### Versionamento Semântico

Cada skill pode ter múltiplas versões:

```
v1.0.0 → v1.1.0 (feature adicionada) → v2.0.0 (breaking change)
```

O registry gerencia qual versão está ativa.

### Pipeline Composition

Encadeia skills como corrente de montagem:

```
Input → [Classificar] → [Sentimento] → [Resumir] → Output
         ↓                ↓              ↓
      "spam"          "positive"     "3 frases"
```

Cada step recebe o output do anterior.

### Filtros no Pipeline

Filtros podem abortar o pipeline se condições não forem satisfeitas:

```python
pipeline.add_filter("qualidade", lambda data: data["confidence"] > 0.7)
```

Se confiança < 0.7, pipeline aborta.

---

## Exercício Prático

Execute `python modules/p10_skills/run.py` e observe:

1. Como as skills são registradas no registry
2. Execução individual de cada skill
3. Pipeline encadeando múltiplas skills
4. Estatísticas de uso por skill

## Perguntas para Reflexão

1. Quando criar uma nova skill vs combinar existentes?
2. Se uma skill falha no meio do pipeline, como rollback?
3. Como testar pipelines sem chamar LLMs reais?

---

## Referências

### Livros

- **"Designing Machine Learning Systems"** by Chip Huyen — Capítulos sobre modular agent architecture
- **"Domain-Driven Design"** by Eric Evans — Bounded contexts como skills

### Documentação Oficial

- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/) — LangChain Docs
- [Semantic Versioning](https://semver.org/) — SemVer Spec

### Tutoriais

- [LangGraph Pipelines](https://langchain-ai.github.io/langgraph/) — LangGraph Docs
- [Skill Design Patterns](https://github.com/langchain-ai/langchain/tree/master/templates) — LangChain Templates
