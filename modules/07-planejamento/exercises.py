"""Módulo P3a-3 — Exercícios Práticos

Execute com: python modules/07-planejamento/exercises.py

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
            """Registre falha e retorne novo estado."""
            # ← Implemente aqui
            return self.state  # Placeholder vazio
        
        def record_success(self) -> str:
            """Registre sucesso e retorne novo estado."""
            # ← Implemente aqui
            return self.state  # Placeholder vazio
    
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
# TESTE 2: Task Decomposition — Tarefa decomposta corretamente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_task_decomposition():
    """
    Implemente decomposição de tarefa complexa em subtarefas.
    
    Cenário: Planner TechCorp recebe "Construir sistema RAG" e deve
    decompor em subtarefas com dependências.
    
    Regra: Tarefa principal → lista de subtarefas ordenadas com dependências.
    Cada subtarefa tem: id, task, depends_on (lista de ids).
    
    Exemplo de saída esperada:
    [
        {"id": 0, "task": "indexar documentos", "depends_on": []},
        {"id": 1, "task": "treinar embedding", "depends_on": [0]},
        {"id": 2, "task": "criar API de busca", "depends_on": [1]},
        {"id": 3, "task": "integrar frontend", "depends_on": [2]},
    ]
    """
    def decompose_task(task: str) -> list:
        """TODO: Retorne lista de dicts {'id': int, 'task': str, 'depends_on': list[int]}."""
        # ← Implemente aqui
        return []
    
    result = decompose_task("Construir sistema RAG")
    assert len(result) >= 3, \
        f"Deve ter pelo menos 3 subtarefas, got {len(result)}"
    assert all("depends_on" in t for t in result), \
        "Cada tarefa deve ter campo 'depends_on'"
    assert all("task" in t for t in result), \
        "Cada tarefa deve ter campo 'task'"
    assert all("id" in t for t in result), \
        "Cada tarefa deve ter campo 'id'"
    
    # Propriedade comportamental: primeira tarefa não depende de nenhuma
    first_task = next(t for t in result if t["id"] == min(sub["id"] for sub in result))
    assert len(first_task["depends_on"]) == 0, \
        "Primeira tarefa não deve ter dependências"
    
    # Propriedade: todas as dependências referenciam ids existentes
    all_ids = {t["id"] for t in result}
    for t in result:
        for dep in t["depends_on"]:
            assert dep in all_ids, \
                f"Tarefa {t['id']} referencia dependência {dep} que não existe"
    
    console.print(f"[green]✓[/green] Task Decomposition: {len(result)} subtarefas ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Checkpoint Save/Restore — Estado preservado?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_checkpoint_save_restore():
    """
    TODO: Implemente salvar e restaurar checkpoint.
    """
    class PlannerState:
        def __init__(self):
            self.steps_completed = 0
            self.current_step = 0
            self.results: Dict[str, Any] = {}
        
        def save_checkpoint(self) -> dict:
            """Retorne serialização do estado."""
            # ← Implemente aqui
            return {}  # Placeholder vazio
        
        def restore_checkpoint(self, state: dict):
            """Restaure estado a partir da serialização."""
            # ← Implemente aqui
            pass  # Placeholder vazio
    
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
    
    # ⚠️ PONTO CRÍTICO: Valide estrutura preservada, não valores hardcoded
    # O checkpoint deve conter todos os campos originais
    assert "steps_completed" in checkpoint, \
        "Checkpoint deve conter 'steps_completed'"
    assert "current_step" in checkpoint, \
        "Checkpoint deve conter 'current_step'"
    assert "results" in checkpoint, \
        "Checkpoint deve conter 'results'"
    # Verifique que o estado restaurado é consistente com o original
    expected_steps = 5
    assert planner.steps_completed == expected_steps, \
        f"Deveria restaurar steps_completed={expected_steps}, got {planner.steps_completed}"
    assert planner.current_step == expected_steps + 1, \
        f"current_step deve ser steps_completed+1, got {planner.current_step}"
    # ⚠️ PONTO CRÍTICO: Verifique integridade dos dados (não só contagem)
    assert len(planner.results) >= 1, \
        f"Checkpoint deve preservar pelo menos 1 resultado, got {len(planner.results)}"
    # Verifique que os resultados são dicts (estrutura preservada)
    for key, value in planner.results.items():
        assert isinstance(value, dict), f"Resultado '{key}' deve ser dict, got {type(value)}"
    
    console.print("[green]✓[/green] Checkpoint: save & restore ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Step Validation — Cada passo é válido?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_step_validation():
    """
    Valide cada passo do plano antes de executar.
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
        # ← Implemente validação aqui
        pass
    
    assert len(invalid_steps) == 0, \
        f"Todos os passos devem ter ações válidas, inválidos: {invalid_steps}"
    
    # ⚠️ PONTO CRÍTICO: Valide propriedade comportamental — cada passo tem params
    for step in plan:
        assert "params" in step and isinstance(step["params"], dict), \
            f"Cada passo deve ter 'params' como dict, got {step}"
    
    console.print(f"[green]✓[/green] Plano válido: {len(plan)} passos verificados")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Fallback Logic — Fallback acionado corretamente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_fallback_logic():
    """
    Implemente lógica de fallback quando passo principal falha.
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
    
    # ← Implemente aqui
    
    assert used_fallback == True, "Fallback deveria ter sido acionado"
    assert result == "cached_response", \
        f"Resultado do fallback deveria ser 'cached_response', got {result}"
    
    console.print("[green]✓[/green] Fallback: primary failed → cached_response ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Plan Execution Metrics — Métricas do plano?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_06_plan_execution_metrics():
    """
    Colete métricas de execução do plano.
    """
    execution_log = [
        {"step": 1, "status": "success", "latency_ms": 150},
        {"step": 2, "status": "success", "latency_ms": 200},
        {"step": 3, "status": "failed", "latency_ms": 5000},
        {"step": 4, "status": "success", "latency_ms": 180},
    ]
    
    # TODO: Calcule métricas
    total_steps = len(execution_log)
    success_steps = []
    failed_steps = []
    
    success_rate = 0.0
    avg_latency = 0.0
    total_latency = 0
    
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
    tests = [test_01_circuit_breaker_states, test_02_task_decomposition,
             test_03_checkpoint_save_restore, test_04_step_validation,
             test_05_fallback_logic, test_06_plan_execution_metrics]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
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
        console.print("[bold green]🎉 Todos os exercícios passaram![/bold green]")


if __name__ == "__main__":
    run_all()
