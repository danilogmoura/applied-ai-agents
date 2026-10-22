"""
Módulo P3a-3 — Teste do Exercício

Execute com: python modules/p3a3_planning/test_exercise.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Circuit Breaker — Transições de estado corretas?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_circuit_breaker_states():
    """
    TODO: Implemente o state machine do circuit breaker.
    
    Estados: CLOSED (normal) → OPEN (falhou) → HALF_OPEN (teste) → CLOSED/OPEN
    """
    class CircuitBreaker:
        def __init__(self, failure_threshold: int = 3):
            self.failure_threshold = failure_threshold
            self.failures = 0
            self.state = "CLOSED"  # ← Pode mudar
        
        def record_failure(self) -> str:
            """TODO: Registre falha e retorne novo estado."""
            return self.state  # ← Implemente
        
        def record_success(self) -> str:
            """TODO: Registre sucesso e retorne novo estado."""
            return self.state  # ← Implemente
    
    cb = CircuitBreaker(failure_threshold=3)
    
    # Simula 3 falhas consecutivas
    for i in range(3):
        new_state = cb.record_failure()
    
    assert cb.state == "OPEN", \
        f"Após {cb.failure_threshold} falhas, estado deve ser OPEN, got {cb.state}"
    
    # Sucesso no HALF_OPEN deve voltar ao CLOSED
    cb.record_success()
    assert cb.state == "CLOSED", \
        f"Sucesso no HALF_OPEN deve voltar ao CLOSED, got {cb.state}"
    
    console.print(f"[green]✓[/green] Circuit breaker: CLOSED→OPEN→CLOSED ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Checkpoint Save/Restore — Estado preservado?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_checkpoint_save_restore():
    """
    TODO: Implemente salvar e restaurar checkpoint.
    """
    class PlannerState:
        def __init__(self):
            self.steps_completed = 0
            self.current_step = 0
            self.results: Dict[str, Any] = {}
        
        def save_checkpoint(self) -> dict:
            """TODO: Retorne serialização do estado."""
            return {}  # ← Implemente
        
        def restore_checkpoint(self, state: dict):
            """TODO: Restaure estado a partir da serialização."""
            pass  # ← Implemente
    
    planner = PlannerState()
    planner.steps_completed = 5
    planner.current_step = 6
    planner.results = {"step_1": "ok", "step_2": "done"}
    
    # Salva
    checkpoint = planner.save_checkpoint()
    
    # Simula reset total
    planner.steps_completed = 0
    planner.current_step = 0
    planner.results = {}
    
    # Restaura
    planner.restore_checkpoint(checkpoint)
    
    assert planner.steps_completed == 5, \
        f"Deveria restaurar steps_completed=5, got {planner.steps_completed}"
    assert planner.current_step == 6, \
        f"Deveria restaurar current_step=6, got {planner.current_step}"
    assert len(planner.results) == 2, \
        f"Deveria restaurar 2 resultados, got {len(planner.results)}"
    
    console.print("[green]✓[/green] Checkpoint: save & restore ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Step Validation — Cada passo é válido?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_step_validation():
    """
    TODO: Valide cada passo do plano antes de executar.
    """
    plan = [
        {"action": "search_docs", "params": {"query": "reembolso"}},
        {"action": "extract_info", "params": {"source": "doc_001"}},
        {"action": "generate_response", "params": {"context": "extracted"}},
    ]
    
    valid_actions = {"search_docs", "extract_info", "generate_response", "save_result"}
    
    # TODO: Verifique se todos os passos têm ações válidas
    invalid_steps = []
    for step in plan:
        if step["action"] not in valid_actions:
            invalid_steps.append(step)
    
    assert len(invalid_steps) == 0, \
        f"Todos os passos devem ter ações válidas, inválidos: {invalid_steps}"
    
    # TODO: Verifique se cada passo tem 'params'
    missing_params = [s for s in plan if "params" not in s or not s["params"]]
    assert len(missing_params) == 0, \
        "Cada passo deve ter params não-vazio"
    
    console.print(f"[green]✓[/green] Plano válido: {len(plan)} passos verificados")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Fallback Logic — Fallback acionado corretamente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_fallback_logic():
    """
    TODO: Implemente lógica de fallback quando passo principal falha.
    """
    def execute_primary(action: str) -> str:
        if action == "api_call":
            raise ConnectionError("API indisponível")
        return "success"
    
    def execute_fallback(action: str) -> str:
        return "cached_response"
    
    # TODO: Implemente try/except com fallback
    result = None
    used_fallback = False
    
    try:
        result = execute_primary("api_call")
    except Exception:
        used_fallback = True
        result = execute_fallback("api_call")
    
    assert used_fallback == True, "Fallback deveria ter sido acionado"
    assert result == "cached_response", \
        f"Resultado do fallback deveria ser 'cached_response', got {result}"
    
    console.print("[green]✓[/green] Fallback: primary failed → cached_response ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Plan Execution Metrics — Métricas do plano?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_plan_execution_metrics():
    """
    TODO: Calcule métricas de execução do plano.
    """
    execution_log = [
        {"step": 1, "status": "success", "latency_ms": 150},
        {"step": 2, "status": "success", "latency_ms": 200},
        {"step": 3, "status": "failed", "latency_ms": 5000},
        {"step": 4, "status": "success", "latency_ms": 180},
    ]
    
    # TODO: Calcule métricas
    success_rate = None  # ← Calcule
    avg_latency = None  # ← Calcule (só successes)
    total_latency = None  # ← Calcule (todos)
    
    assert 0 <= success_rate <= 1, f"Success rate deve ser [0,1], got {success_rate}"
    assert success_rate > 0.5, f"Success rate mínimo: 0.5, got {success_rate}"
    assert avg_latency is not None and avg_latency > 0, \
        f"Avg latency deve ser positivo, got {avg_latency}"
    
    console.print(f"[green]✓[/green] Métricas: success={success_rate:.0%}, "
                  f"avg_latency={avg_latency:.0f}ms")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_circuit_breaker_states, test_02_checkpoint_save_restore,
             test_03_step_validation, test_04_fallback_logic,
             test_05_plan_execution_metrics]
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P3a-3: Planejamento e Retomada[/bold cyan]",
                        border_style="cyan"))
    
    passed = failed = 0
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            console.print(f"[red]✗ {test_fn.__name__}: {e}[/red]")
            failed += 1
        except Exception as e:
            console.print(f"[red]✗ {test_fn.__name__}: Erro — {e}[/red]")
            failed += 1
    
    console.print(f"\nResultado: [bold green]{passed}/{passed+failed}[/bold green] passaram")
    if not failed:
        console.print("[bold green]🎉 Todos os testes passaram![/bold green]")


if __name__ == "__main__":
    run_all()
