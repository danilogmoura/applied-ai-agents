# 🏗️ Mini-Projeto Integrador — Evaluation

> **Objetivo:** Construir um framework de avaliação para outputs de LLM.

## O que você vai construir

Um avaliador `eval_framework.py` que:

1. **Constrói** dataset golden (ground truth)
2. **Calcula** métricas: exact match, fuzzy match (Levenshtein)
3. **Executa** A/B testing com Z-score
4. **Benchmark** contra baseline

## Requisitos

```python
class EvalFramework:
    def build_golden_dataset(self, questions: list, answers: list) -> list:
        """Criar dataset golden (pergunta → resposta esperada)."""
        ...
    
    def exact_match(self, predicted: str, expected: str) -> bool:
        """Verificar correspondência exata."""
        ...
    
    def fuzzy_match(self, predicted: str, expected: str, threshold: float = 0.8) -> bool:
        """Verificar similaridade com Levenshtein distance."""
        ...
    
    def ab_test(self, variant_a_results: list, variant_b_results: list) -> dict:
        """Comparar duas variantes com teste Z."""
        ...
    
    def regression_benchmark(self, current_results: list, 
                             baseline_results: list) -> dict:
        """Detectar regressão vs baseline."""
        ...
```

## Teste seu código

```bash
python eval_framework.py --golden golden.json --predictions predictions.json
python eval_framework.py --ab-test variant_a.json variant_b.json
```

## Desafios extras

- [ ] Suporte a múltiplas métricas (BLEU, ROUGE, BERTScore)
- [ ] Dashboard de resultados
- [ ] Alerta automático de regressão
- [ ] Exportar relatório em HTML
