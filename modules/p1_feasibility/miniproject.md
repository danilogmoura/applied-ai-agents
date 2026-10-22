# 🏗️ Mini-Projeto Integrador — Viabilidade de IA

> **Objetivo:** Construir uma ferramenta de análise de viabilidade para projetos de IA.

## O que você vai construir

Um analisador `feasibility_analyzer.py` que avalia se um problema é candidato a solução com IA:

1. **Mede latência** baseline vs IA (simulado)
2. **Compara custo** regra hard-coded vs LLM
3. **Avalia threshold** de accuracy mínimo aceitável
4. **Gera memorando** executivo com recomendação

## Requisitos

```python
class FeasibilityAnalyzer:
    def measure_latency(self, baseline_fn, llm_fn, n_trials: int = 10) -> dict:
        """Medir latência de baseline (regras) vs LLM."""
        ...
    
    def compare_costs(self, rule_cost_per_request: float, 
                      llm_tokens_per_request: int, 
                      price_per_1k: float) -> dict:
        """Comparar custo por request entre regras e LLM."""
        ...
    
    def evaluate_accuracy_threshold(self, model_accuracy: float, 
                                    min_acceptable: float) -> dict:
        """Avaliar se accuracy está acima do threshold."""
        ...
    
    def generate_memorandum(self, analysis: dict) -> str:
        """Gerar memorando executivo com: problema, dados, recomendação."""
        ...
```

## 📖 Guia Passo a Passo

Este módulo é **opcional/bônus** — não bloqueia os seguintes. Siga estes passos se quiser praticar:

### Passo 1 — Crie a classe base

Defina `FeasibilityAnalyzer` com dicionário de preços dos principais modelos:

```python
import time
import random

class FeasibilityAnalyzer:
    def __init__(self):
        self.prices = {
            "gpt-4o": {"input": 0.01, "output": 0.03},
            "gpt-4o-mini": {"input": 0.0015, "output": 0.006},
        }
```

### Passo 2 — Simule medição de latência

Como você ainda não tem APIs reais rodando, simule com `time.sleep()` e valores realistas:

```python
def measure_latency(self, baseline_fn, llm_fn, n_trials: int = 10) -> dict:
    baseline_times = [random.uniform(0.01, 0.05) for _ in range(n_trials)]
    llm_times = [random.uniform(0.5, 2.0) for _ in range(n_trials)]
    
    return {
        "baseline_avg_ms": sum(baseline_times) * 1000 / n_trials,
        "llm_avg_ms": sum(llm_times) * 1000 / n_trials,
        "baseline_p95_ms": sorted(baseline_times)[int(n_trials * 0.95)] * 1000,
        "llm_p95_ms": sorted(llm_times)[int(n_trials * 0.95)] * 1000,
    }
```

### Passo 3 — Compare custos

Regra hard-coded custa centavos por request. LLM custa por token:

```python
def compare_costs(self, rule_cost_per_request: float, 
                  llm_tokens_per_request: int, 
                  price_per_1k: float) -> dict:
    llm_cost = (llm_tokens_per_request / 1000) * price_per_1k
    ratio = rule_cost_per_request / llm_cost if llm_cost > 0 else float('inf')
    
    return {
        "rule_cost": rule_cost_per_request,
        "llm_cost": llm_cost,
        "ratio": ratio,  # > 1 significa LLM mais barato
        "break_even_volume": int(rule_cost_per_request / (llm_cost - 0.001)) if llm_cost < rule_cost_per_request else None,
    }
```

### Passo 4 — Avalie threshold de accuracy

Se o problema exige 99% de accuracy e o LLM dá 85%, não vale a pena:

```python
def evaluate_accuracy_threshold(self, model_accuracy: float, 
                                min_acceptable: float) -> dict:
    meets = model_accuracy >= min_acceptable
    gap = model_accuracy - min_acceptable
    
    return {
        "meets_threshold": meets,
        "gap_pct": round(gap * 100, 2),
        "recommendation": "APROVADO" if meets else "REPROVADO",
    }
```

### Passo 5 — Gere memorando executivo

Combine tudo em um texto legível para stakeholders:

```python
def generate_memorandum(self, analysis: dict) -> str:
    lines = [
        "# Memorando de Viabilidade IA",
        f"**Problema:** {analysis.get('problem', 'N/A')}",
        f"**Latência baseline:** {analysis['latency']['baseline_avg_ms']:.1f}ms",
        f"**Latência LLM:** {analysis['latency']['llm_avg_ms']:.1f}ms",
        f"**Custo por request (regra):** ${analysis['costs']['rule_cost']:.4f}",
        f"**Custo por request (LLM):** ${analysis['costs']['llm_cost']:.4f}",
        f"**Accuracy vs Threshold:** {analysis['accuracy']['recommendation']}",
        "",
        f"**Recomendação:** {'VIÁVEL' if analysis['accuracy']['meets_threshold'] else 'NÃO VIÁVEL'}",
    ]
    return "\n".join(lines)
```

### Passo 6 — Adicione CLI

Use `argparse` para permitir cenários pré-definidos:

```python
SCENARIOS = {
    "ticket_classification": {"baseline": 0.05, "llm_tokens": 250, "price": 0.01, "accuracy": 0.85, "min_acc": 0.80},
    "fraud_detection": {"baseline": 0.10, "llm_tokens": 500, "price": 0.03, "accuracy": 0.75, "min_acc": 0.90},
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem", default="ticket_classification")
    parser.add_argument("--budget", type=float, default=5000)
    args = parser.parse_args()
    
    scenario = SCENARIOS.get(args.problem, SCENARIOS["ticket_classification"])
    analyzer = FeasibilityAnalyzer()
    
    latency = analyzer.measure_latency(None, None)
    costs = analyzer.compare_costs(scenario["baseline"], scenario["llm_tokens"], scenario["price"])
    accuracy = analyzer.evaluate_accuracy_threshold(scenario["accuracy"], scenario["min_acc"])
    
    memo = analyzer.generate_memorandum({
        "problem": args.problem,
        "latency": latency,
        "costs": costs,
        "accuracy": accuracy,
    })
    print(memo)
```

## Teste seu código

```bash
python feasibility_analyzer.py --problem "classificar tickets de suporte" --budget 5000
python feasibility_analyzer.py --scenario fraud_detection --output report.md
```

## Desafios extras

- [ ] Suporte a múltiplos cenários (batch vs real-time)
- [ ] Exportar relatório em PDF/Markdown
- [ ] Comparar múltiplos modelos lado a lado
- [ ] Calculadora ROI (return on investment)

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] Classe `FeasibilityAnalyzer` funciona com dados simulados
- [ ] `measure_latency()` retorna dict com avg e p95 para baseline e LLM
- [ ] `compare_costs()` calcula corretamente custo por request
- [ ] `evaluate_accuracy_threshold()` compara accuracy vs threshold
- [ ] `generate_memorandum()` produz texto legível para stakeholders
- [ ] CLI aceita cenários pré-definidos via `--problem`

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.
