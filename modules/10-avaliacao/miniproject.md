# 🏗️ Mini-Projeto Integrador — Evaluation

> **Objetivo:** Construir um framework de avaliação para outputs de LLM.

## O que você vai construir

Um avaliador `eval_framework.py` (classe `Evaluator`) que:

1. **Constrói** dataset golden (ground truth)
2. **Calcula** métricas: exact match, fuzzy match (Levenshtein)
3. **Executa** A/B testing com Z-score
4. **Benchmark** contra baseline

## Requisitos

```python
class Evaluator:
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

## 📖 Guia Passo a Passo

### Passo 1 — Construa o dataset golden

Crie um conjunto de perguntas e respostas esperadas para avaliação:

```python
import json
from typing import List, Tuple

class Evaluator:
    def __init__(self):
        self.golden_dataset = []
    
    def build_golden_dataset(self, questions: List[str], answers: List[str]) -> List[dict]:
        """Criar dataset golden (pergunta → resposta esperada)."""
        if len(questions) != len(answers):
            raise ValueError("Número de perguntas deve igual número de respostas")
        
        self.golden_dataset = [
            {"id": i, "question": q, "expected_answer": a}
            for i, (q, a) in enumerate(zip(questions, answers))
        ]
        
        return self.golden_dataset
    
    def save_golden(self, filepath: str = "golden.json"):
        """Salva dataset golden em JSON."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.golden_dataset, f, indent=2, ensure_ascii=False)
```

### Passo 2 — Implemente exact match

Verificação de correspondência exata entre predicted e expected:

```python
    def exact_match(self, predicted: str, expected: str) -> bool:
        """Verificar correspondência exata (normalização básica)."""
        # Normaliza: remove whitespace extra, lowercase
        pred_norm = ' '.join(predicted.lower().split())
        exp_norm = ' '.join(expected.lower().split())
        return pred_norm == exp_norm
    
    def exact_match_batch(self, predictions: List[str], 
                          expectations: List[str]) -> dict:
        """Calcula exact match score em batch."""
        matches = sum(
            1 for p, e in zip(predictions, expectations)
            if self.exact_match(p, e)
        )
        total = len(predictions)
        
        return {
            "exact_matches": matches,
            "total": total,
            "score": round(matches / total, 4) if total > 0 else 0,
        }
```

### Passo 3 — Implemente fuzzy match com Levenshtein

Similaridade baseada em distância de edição:

```python
    def levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calcula distância de Levenshtein entre duas strings."""
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def fuzzy_match(self, predicted: str, expected: str, 
                    threshold: float = 0.8) -> bool:
        """Verifica similaridade com Levenshtein distance."""
        if not predicted or not expected:
            return False
        
        dist = self.levenshtein_distance(predicted.lower(), expected.lower())
        max_len = max(len(predicted), len(expected))
        similarity = 1 - (dist / max_len)
        
        return similarity >= threshold
    
    def fuzzy_match_batch(self, predictions: List[str],
                          expectations: List[str],
                          threshold: float = 0.8) -> dict:
        """Calcula fuzzy match score em batch."""
        matches = sum(
            1 for p, e in zip(predictions, expectations)
            if self.fuzzy_match(p, e, threshold)
        )
        total = len(predictions)
        
        return {
            "fuzzy_matches": matches,
            "total": total,
            "threshold": threshold,
            "score": round(matches / total, 4) if total > 0 else 0,
        }
```

### Passo 4 — Implemente A/B testing com Z-score

Compare duas variantes estatisticamente:

```python
    def ab_test(self, variant_a_results: List[float], 
                variant_b_results: List[float]) -> dict:
        """Comparar duas variantes com teste Z."""
        def mean(data):
            return sum(data) / len(data) if data else 0
        
        def std_dev(data):
            m = mean(data)
            variance = sum((x - m) ** 2 for x in data) / len(data)
            return variance ** 0.5
        
        mean_a = mean(variant_a_results)
        mean_b = mean(variant_b_results)
        std_a = std_dev(variant_a_results)
        std_b = std_dev(variant_b_results)
        
        # Calcula Z-score
        n_a, n_b = len(variant_a_results), len(variant_b_results)
        if std_a == 0 or std_b == 0:
            z_score = 0
        else:
            se = (std_a ** 2 / n_a + std_b ** 2 / n_b) ** 0.5
            z_score = (mean_b - mean_a) / se if se > 0 else 0
        
        # Significância (α = 0.05, critical value = 1.96)
        significant = abs(z_score) > 1.96
        
        return {
            "variant_a": {"mean": round(mean_a, 4), "std": round(std_a, 4), "n": n_a},
            "variant_b": {"mean": round(mean_b, 4), "std": round(std_b, 4), "n": n_b},
            "z_score": round(z_score, 4),
            "significant": significant,
            "winner": "B" if mean_b > mean_a else "A",
        }
```

### Passo 5 — Implemente regression benchmark

Detecte regressão vs baseline:

```python
    def regression_benchmark(self, current_results: List[float],
                             baseline_results: List[float]) -> dict:
        """Detectar regressão vs baseline."""
        def mean(data):
            return sum(data) / len(data) if data else 0
        
        baseline_mean = mean(baseline_results)
        current_mean = mean(current_results)
        
        # Delta percentual
        if baseline_mean == 0:
            delta_pct = 0
        else:
            delta_pct = ((current_mean - baseline_mean) / baseline_mean) * 100
        
        # Regressão se performance caiu mais de 5%
        is_regression = delta_pct < -5
        
        return {
            "baseline_mean": round(baseline_mean, 4),
            "current_mean": round(current_mean, 4),
            "delta_pct": round(delta_pct, 2),
            "is_regression": is_regression,
            "status": "🔴 REGRESSÃO" if is_regression else "🟢 OK",
        }
```

### Passo 6 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Framework de avaliação")
    parser.add_argument("--golden", help="Arquivo golden dataset (JSON)")
    parser.add_argument("--predictions", help="Arquivo predictions (JSON)")
    parser.add_argument("--ab-test", nargs=2, metavar=('A', 'B'),
                        help="Arquivos para A/B testing")
    args = parser.parse_args()
    
    framework = Evaluator()
    
    if args.golden and args.predictions:
        # Carrega datasets
        with open(args.golden) as f:
            golden = json.load(f)
        with open(args.predictions) as f:
            predictions = json.load(f)
        
        # Avalia
        eval_result = framework.exact_match_batch(
            [p["answer"] for p in predictions],
            [g["expected_answer"] for g in golden]
        )
        print(json.dumps(eval_result, indent=2))
    
    elif args.ab_test:
        with open(args.ab_test[0]) as f:
            scores_a = json.load(f)
        with open(args.ab_test[1]) as f:
            scores_b = json.load(f)
        
        ab_result = framework.ab_test(scores_a, scores_b)
        print(json.dumps(ab_result, indent=2))
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `build_golden_dataset()` cria lista de dicts {question, expected_answer}
- [ ] `exact_match()` normaliza e compara strings exatamente
- [ ] `levenshtein_distance()` implementa algoritmo de matriz dinâmica
- [ ] `fuzzy_match()` calcula similaridade e aplica threshold
- [ ] `ab_test()` calcula Z-score e determina significância estatística
- [ ] `regression_benchmark()` detecta queda > 5% vs baseline

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

## Teste seu código

```bash
python eval_framework.py --golden golden.json --predictions predictions.json
python eval_framework.py --ab-test variant_a.json variant_b.json
```

## 🪨 Travei? Pistas em camadas

Funciona igualzinho às pistas dos exercícios: quando um requisito travar, abra **só o próximo nível** que você precisar — nunca todos de uma vez. O objetivo é destravar o raciocínio, não entregar a resposta mastigada.

> **Nível 1 — Direção.** Cada requisito mapeia para um `Passo` do guia acima. Antes de descer de nível, releia o Passo correspondente; na maioria das vezes ele já tem o esqueleto da função.

<details>
<summary><b>Nível 2 — A ideia por requisito</b> (clique para abrir)</summary>

- **`build_golden_dataset()`:** zip perguntas e respostas esperadas em `[{'question','expected'}...]` e grave em `self.golden_dataset`. É a base de verdade contra a qual tudo é comparado.
- **`exact_match()`:** normalizze antes de comparar (strip, lower, colapsar espaços) e devolva bool. Simples, mas rigoroso — qualquer diferença conta como erro.
- **`fuzzy_match()`:** implemente `levenshtein_distance(s1,s2)` (programação dinâmica, matriz de edições) e converta em similaridade `1 - dist/max_len`; compare com `threshold`.
- **`ab_test()`:** calcule média e desvio de cada variante e um Z-score da diferença. Devolva `{z_score, significant, winner}` — significativo quando |z| supera o crítico (~1.96).
- **`regression_benchmark()`:** compare média atual vs baseline; se cair além de um tolerance, marque regressão. Retorne delta percentual e flag `regressed`.

</details>

<details>
<summary><b>Nível 3 — Quase solução</b> (abra só se o nível 2 não bastou)</summary>

```python
def fuzzy_match(self, predicted, expected, threshold=0.8):
    p, e = predicted.lower().strip(), expected.lower().strip()
    dist = self.levenshtein_distance(p, e)
    similarity = 1 - dist / max(len(p), len(e), 1)
    return similarity >= threshold
```

A Levenshtein é o tijolo que sustenta `fuzzy_match`; reutilize a mesma normalização de `exact_match` aqui, só trocando a comparação rígida pela similaridade com threshold.

</details>

## Desafios extras

- [ ] Suporte a múltiplas métricas (BLEU, ROUGE, BERTScore)
- [ ] Dashboard de resultados
- [ ] Alerta automático de regressão
- [ ] Exportar relatório em HTML
