# Material Didático — P5: Avaliação e Testes

## Conceitos Fundamentais

### O Problema da Qualidade Invisível

Sem avaliação, você está cego. Mudou o prompt? Trocou de modelo? Adicionou uma feature? Sem métricas, não sabe se melhorou ou piorou.

**Avaliação é o que separa desenvolvimento amador de produção profissional.**

### Golden Dataset — Respostas Esperadas

Um golden dataset é um conjunto de exemplos com input + resposta esperada (ground truth):

```python
GoldenExample(
    id="ticket_001",
    question="Não consigo acessar minha conta, erro 403",
    expected_answer="URGENTE",
)
```

Funciona como um "banco de questões" para testar o agente. Cada execução gera scores comparáveis.

### Métricas de Avaliação

| Métrica | O que mede | Quando usar |
|---------|------------|-------------|
| **Exact Match** | Correspondência exata | Classificações discretas |
| **Fuzzy Match** | Sobreposição de palavras | Textos livres parciais |
| **LLM-as-a-Judge** | Julgamento por outro LLM | Respostas complexas/abertas |
| **Embedding Similarity** | Similaridade semântica vetorial | Paraphrase detection |

### LLM-as-a-Judge

Usa um LLM mais poderoso (ex: gpt-4o) para julgar a qualidade de respostas de um modelo menor (ex: gpt-4o-mini):

```
Modelo sendo avaliado → gpt-4o-mini
Juiz avaliador       → gpt-4o
```

O juiz recebe: pergunta + resposta esperada + resposta real → retorna score 0-1.

### Testes A/B

Compara duas variantes lado a lado no mesmo dataset:

```
Variante A (heurística): Score 0.62
Variante B (agente IA):  Score 0.89
Vencedor: B (+43.5%)
```

Essencial para decidir entre abordagens antes de deploy.

### Benchmarking Regressivo

Salva resultados de cada execução. Antes de qualquer mudança:

1. Roda baseline atual → salva report.json
2. Faz mudança (prompt, modelo, etc.)
3. Roda novamente → compara com baseline
4. Se score caiu → rollback automático

---

## Exercício Prático

Execute `python modules/p5_evaluation/run.py` e observe:

1. Como o golden dataset define ground truth
2. Scores individuais por exemplo (exact, fuzzy, LLM judge)
3. Relatório estatístico completo (média, mediana, min, max)
4. Resultado do teste A/B entre heurística vs agente

## Perguntas para Reflexão

1. Como construir um golden dataset confiável? Quem valida as respostas esperadas?
2. Se o LLM-as-a-judge também pode errar, como garantir que ele é justo?
3. Qual tamanho mínimo de dataset para resultados estatisticamente significativos?

---

## Referências

### Livros

- **"Machine Learning Engineering"** by Andrey Burtenshaw — Capítulos sobre testing e evaluation
- **"Designing Machine Learning Systems"** by Chip Huyen — Capítulos sobre model evaluation

### Documentação Oficial

- [OpenAI Evals](https://platform.openai.com/docs/guides/evals) — OpenAI Docs
- [LangSmith Evaluation](https://smith.langchain.com/docs/concepts/evaluation/) — LangSmith Docs

### Vídeos

- [How to Evaluate LLM Applications](https://www.youtube.com/watch?v=vJCKZUoaZtc) — Yannic Kilcher, YouTube
- [LLM Evaluation at Scale](https://www.youtube.com/watch?v=7Lk0v3cOnBy) — Weights & Biases, YouTube

### Tutoriais

- [Creating Golden Datasets](https://medium.com/@langchain/create-golden-datasets-for-llm-evaluation) — LangChain Blog
- [Evaluation Best Practices](https://docs.arize.com/phoenix) — Arize Phoenix Docs
