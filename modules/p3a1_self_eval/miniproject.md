# 🏗️ Mini-Projeto Integrador — Self-Evaluation

> **Objetivo:** Construir um sistema que gera e auto-avalia respostas iterativamente.

## O que você vai construir

Um gerador `self_eval_generator.py` que:

1. **Gera** resposta inicial para uma pergunta
2. **Avalia** a resposta (clareza, precisão, completude)
3. **Refina** se nota < threshold
4. **Acumula** custo total das iterações

## Requisitos

```python
class SelfEvalGenerator:
    def generate_response(self, question: str) -> dict:
        """Gerar resposta inicial."""
        ...
    
    def evaluate(self, response: str, criteria: list = None) -> dict:
        """Avaliar resposta por critérios (claridade, precisão, etc.)."""
        ...
    
    def refine(self, response: str, feedback: dict) -> str:
        """Refinar resposta baseado no feedback."""
        ...
    
    def run_iteration_loop(self, question: str, max_iterations: int = 5, 
                           threshold: float = 0.8) -> dict:
        """Loop: gerar → avaliar → refinar até threshold ou max_iter."""
        ...
```

## Teste seu código

```bash
python self_eval_generator.py --question "Explique transformers" --max-iters 3
python self_eval_generator.py --batch questions.json --output results.json
```

## Desafios extras

- [ ] Critérios configuráveis por domínio
- [ ] Comparar qualidade vs custo (tokens gastos)
- [ ] Exportar histórico de iterações
- [ ] Modo "teacher" com rubric predefined
