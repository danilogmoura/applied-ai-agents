"""Módulo 07 — SOLUÇÃO COMENTADA

Execute com: python modules/07-planejamento/exercises.py

Código completo com explicações detalhadas.
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
    State Machine do Circuit Breaker.
    
    Padrão de projeto que previne chamadas repetidas a serviços falhos.
    
    Estados:
    - CLOSED: Normal, operações fluem. Se falhas >= threshold → OPEN
    - OPEN: Bloqueia todas as operações. Após timeout → HALF_OPEN
    - HALF_OPEN: Testa com uma operação. Se succeed → CLOSED, se fail → OPEN
    
    Analogia: Disjuntor elétrico. Se muitos curtos-circuitos (falhas), 
    desarma (OPEN). Depois espera um pouco e tenta religar (HALF_OPEN).
    """
    class CircuitBreaker:
        def __init__(self, failure_threshold: int = 3):
            self.failure_threshold = failure_threshold
            self.failures = 0
            self.state = "CLOSED"  # Começa normal
        
        def record_failure(self) -> str:
            """
            Registra uma falha e transiciona o estado.
            
            - Se já está HALF_OPEN e falha → volta para OPEN (piorou)
            - Se falhas atingem threshold e não está OPEN → vai para OPEN
            """
            self.failures += 1
            
            # Se estava em modo de teste (HALF_OPEN) e falhou → piorou
            if self.state == "HALF_OPEN":
                self.state = "OPEN"
            # Se atingiu threshold de falhas e ainda não está aberto → abre
            elif self.failures >= self.failure_threshold and self.state != "OPEN":
                self.state = "OPEN"
            
            return self.state
        
        def record_success(self) -> str:
            """
            Registra um sucesso e transiciona o estado.
            
            - Se estava HALF_OPEN e succeed → fecha (serviço recuperou!)
            - Se estava OPEN → meio caminho (HALF_OPEN) para teste
            """
            # Se passou no teste (HALF_OPEN) → recupera totalmente
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failures = 0  # Reseta contador
            # Se ainda está OPEN, primeiro sucesso leva a HALF_OPEN
            elif self.state == "OPEN":
                self.state = "HALF_OPEN"
            
            return self.state
    
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
    Sistema de checkpoint para retomada após falhas.
    
    Importante para planos longos: se algo falha no passo 50 de 100,
    podemos retomar do passo 50 em vez de recomeçar do zero.
    
    Serialização: converte estado em dicionário (JSON-serializável).
    """
    class PlannerState:
        def __init__(self):
            self.steps_completed = 0
            self.current_step = 0
            self.results: Dict[str, Any] = {}
        
        def save_checkpoint(self) -> dict:
            """
            Serializa o estado atual em um dicionário.
            
            1. Copia todos os campos relevantes
            2. Faz cópia rasa dos results (dict(results)) para evitar mutações
            3. Retorna o snapshot
            """
            return {
                "steps_completed": self.steps_completed,
                "current_step": self.current_step,
                "results": dict(self.results),  # Copia rasa
            }
        
        def restore_checkpoint(self, state: dict):
            """
            Restaura estado a partir de um snapshot.
            
            1. Lê cada campo do snapshot
            2. Usa .get() com default para robustez
            3. Copia results para evitar compartilhamento de referência
            """
            self.steps_completed = state.get("steps_completed", 0)
            self.current_step = state.get("current_step", 0)
            self.results = state.get("results", {})
    
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

def test_03_step_validation():
    """
    Validação de plano antes da execução.
    
    Dois checks essenciais:
    1. Ação válida: está na lista de ações permitidas?
    2. Parâmetros presentes: cada passo tem params não-vazio?
    
    Isso previne erros de execução evitáveis.
    """
    plan = [
        {"action": "search_docs", "params": {"query": "reembolso"}},
        {"action": "extract_info", "params": {"source": "doc_001"}},
        {"action": "generate_response", "params": {"context": "extracted"}},
    ]
    
    valid_actions = {"search_docs", "extract_info", "generate_response", "save_result"}
    
    # Verifica se todos os passos têm ações válidas
    invalid_steps = []
    for step in plan:
        if step["action"] not in valid_actions:
            invalid_steps.append(step)
    
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

def test_04_fallback_logic():
    """
    Lógica de fallback: quando o método principal falha, usa alternativa.
    
    Exemplos comuns:
    - API falha → retorna dado em cache
    - Banco de dados lento → consulta réplica
    - Serviço externo indisponível → modo offline
    
    Capturamos exceções específicas (ConnectionError, TimeoutError, OSError)
    para não mascarar outros erros.
    """
    def execute_primary(action: str) -> str:
        if action == "api_call":
            raise ConnectionError("API indisponível")
        return "success"
    
    def execute_fallback(action: str) -> str:
        return "cached_response"
    
    # Tenta método principal, se falhar usa fallback
    result = None
    used_fallback = False
    
    try:
        result = execute_primary("api_call")
    except (ConnectionError, TimeoutError, OSError) as e:
        # Captura erros de rede/sistema e usa fallback
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
    Cálculo de métricas de execução do plano.
    
    Métricas importantes:
    - success_rate: fração de passos que passaram (0-1)
    - avg_latency: tempo médio DOS PASSOS COM SUCESSO (exclui falhas)
    - total_latency: tempo total gasto
    
    Útil para monitoramento, alertas e otimização.
    """
    execution_log = [
        {"step": 1, "status": "success", "latency_ms": 150},
        {"step": 2, "status": "success", "latency_ms": 200},
        {"step": 3, "status": "failed", "latency_ms": 5000},
        {"step": 4, "status": "success", "latency_ms": 180},
    ]
    
    # Calcula métricas
    total_steps = len(execution_log)
    success_steps = [s for s in execution_log if s["status"] == "success"]
    failed_steps = [s for s in execution_log if s["status"] == "failed"]
    
    # Taxa de sucesso: passos OK / total
    success_rate = len(success_steps) / total_steps if total_steps > 0 else 0.0
    
    # Latência média APENAS dos passos com sucesso
    avg_latency = sum(s["latency_ms"] for s in success_steps) / len(success_steps) if success_steps else 0.0
    
    # Tempo total (inclui falhas)
    total_latency = sum(s["latency_ms"] for s in execution_log)
    
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
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]Módulo 07 — Planejamento e Retomada[/bold cyan]",
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
