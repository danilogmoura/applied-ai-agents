# Material Didático — P5: Avaliação e Testes

## Conceitos Fundamentais

### O Problema da Qualidade Invisível

Sem avaliação, você está cego. Mudou o prompt? Trocou de modelo? Adicionou uma feature? Sem métricas, não sabe se melhorou ou piorou.

**Avaliação é o que separa desenvolvimento amador de produção profissional.**

### Pipeline de Avaliação

```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────┐
│ Golden   │────→│ Modelo      │────→│ Avaliador    │────→│ Score    │
│ Dataset  │     │ sendo testado│     │ (exact/fuzzy/│     │ Estatístico│
│          │     │             │     │ LLM-judge)   │     │           │
└──────────┘     └─────────────┘     └──────────────┘     └──────────┘
```

Cada exemplo do dataset passa por este pipeline, gerando scores comparáveis entre versões.

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
| --------- | ------------ | ------------- |
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

### Como Fuzzy Match Calcula Similaridade

Fuzzy match usa **Distância de Levenshtein**: número mínimo de edições para transformar uma string na outra.

```
"URGENTE" vs "Urgente"
         ↓
Edições necessárias:
  1. Maiúscula → minúscula no primeiro char
         ↓
Distância = 1
Similaridade = 1 - (1 / max_len) = 1 - (1/7) = 0.86

"ALTA" vs "MÉDIA"
         ↓
Edições necessárias:
  4 substituições (A→M, L→É, T→D, A→I)
         ↓
Distância = 4
Similaridade = 1 - (4/5) = 0.20
```

**Por que score 0.85 ≠ 0.90 é significativo?**

Em avaliação de agentes, cada ponto de percentual representa dezenas de exemplos no dataset. Um salto de 0.85 para 0.90 pode ser a diferença entre "pronto para produção" e "precisa melhorar mais".

**Limitações do fuzzy match:**

- Não entende sinônimos: "urgente" vs "crítico" → similaridade baixa
- Sensível a ordem: "resposta longa" vs "longa resposta" → penaliza
- Por isso LLM-as-a-Judge existe: entende significado, não só texto

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

### Tutoriais

- [Creating Golden Datasets](https://medium.com/@langchain/create-golden-datasets-for-llm-evaluation) — LangChain Blog
- [Evaluation Best Practices](https://docs.arize.com/phoenix) — Arize Phoenix Docs
