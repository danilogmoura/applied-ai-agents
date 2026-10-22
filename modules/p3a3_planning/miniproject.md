# 🏗️ Mini-Projeto Integrador — Planning

> **Objetivo:** Construir um planner com circuit breaker e checkpoint.

## O que você vai construir

Um executor `planner.py` que:

1. **Executa** plano multi-step com circuit breaker
2. **Salva/restaura** checkpoints a cada step
3. **Valida** pré/pós-condições de cada step
4. **Aplica** fallback quando step falha

## Requisitos

```python
class Planner:
    def execute_with_circuit_breaker(self, plan: list) -> dict:
        """Executar plano com circuit breaker (open/closed/half-open)."""
        ...
    
    def save_checkpoint(self, step_index: int, state: dict) -> str:
        """Salvar checkpoint para restauração posterior."""
        ...
    
    def restore_checkpoint(self, checkpoint_id: str) -> dict:
        """Restaurar estado de um checkpoint."""
        ...
    
    def validate_step(self, step: dict, context: dict) -> bool:
        """Validar pré/pós-condições do step."""
        ...
    
    def execute_with_fallback(self, plan: list, fallback_plan: list) -> dict:
        """Executar plano principal, usar fallback se falhar."""
        ...
```

## Teste seu código

```bash
python planner.py --plan deployment.json
python planner.py --plan ci_cd.json --checkpoint-dir ./checkpoints
```

## Desafios extras

- [ ] Visualização do plano como DAG
- [ ] Parallel execution de steps independentes
- [ ] Metrics dashboard (tempo por step, taxa de sucesso)
- [ ] Exportar plano como workflow YAML
