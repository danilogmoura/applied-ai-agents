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
