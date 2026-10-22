"""
Módulo P11 — Teste do Exercício

Execute com: python modules/p11_production_ops/test_exercise.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: CI/CD Pipeline — Estágios funcionam?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_cicd_pipeline():
    """
    TODO: Implemente pipeline de CI/CD com estágios sequenciais.
    
    Estágios: lint → test → build → deploy
    Se um falha, pipeline para.
    """
    class CIPipeline:
        def __init__(self):
            self.stages = ["lint", "test", "build", "deploy"]
            self.results: Dict[str, bool] = {}
        
        def run_stage(self, stage: str) -> bool:
            """TODO: Execute estágio e retorne True se passou."""
            # Simula resultado baseado no nome do estágio
            return True  # ← Implemente lógica real
        
        def execute(self, stages_to_run: Optional[List[str]] = None) -> dict:
            """TODO: Execute pipeline sequencialmente. Pare na primeira falha."""
            return {}  # ← Implemente
    
    pipeline = CIPipeline()
    
    # Executa pipeline completo
    result = pipeline.execute()
    
    assert len(result["completed_stages"]) > 0, \
        "Pelo menos 1 estágio deve completar"
    
    # Se todos passaram, deploy deve estar na lista
    if all(result.get(stage, False) for stage in result["completed_stages"]):
        assert "deploy" in result["completed_stages"], \
            "Se tudo passou, deploy deve executar"
    
    console.print(f"[green]✓[/green] CI/CD: {len(result['completed_stages'])} stages completed")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Health Check — Verificação de saúde funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_health_check():
    """
    TODO: Implemente health check para serviços IA.
    
    Checks: LLM API response time, rate limit status, memory usage.
    """
    class HealthChecker:
        def __init__(self):
            self.checks: List[dict] = []
        
        def add_check(self, name: str, check_fn):
            """TODO: Adicione verificação ao health check."""
            pass  # ← Implemente
        
        def run_all(self) -> dict:
            """TODO: Execute todos os checks e retorne status."""
            return {"status": "unknown", "checks": []}  # ← Implemente
    
    checker = HealthChecker()
    
    # Checks simulados
    checker.add_check("llm_api", lambda: {"latency_ms": 150, "ok": True})
    checker.add_check("rate_limit", lambda: {"remaining": 80, "ok": True})
    checker.add_check("memory", lambda: {"usage_mb": 256, "ok": True})
    
    result = checker.run_all()
    
    assert result["status"] in ("healthy", "unhealthy"), \
        f"Status deve ser healthy/unhealthy, got {result['status']}"
    assert len(result["checks"]) == 3, \
        f"Deve ter 3 checks, got {len(result['checks'])}"
    
    console.print(f"[green]✓[/green] Health: {result['status']} ({len(result['checks'])} checks)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Monitoring Dashboard — Métricas coletadas?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_monitoring_dashboard():
    """
    TODO: Colete métricas para dashboard de monitoramento.
    
    Métricas: latency_p50/p95/p99, error_rate, tokens_per_second, cost_per_hour.
    """
    class MetricsCollector:
        def __init__(self):
            self.latencies: List[float] = []
            self.errors: int = 0
            self.total_requests: int = 0
            self.tokens_used: int = 0
        
        def record_request(self, latency_ms: float, success: bool, tokens: int):
            """TODO: Registre métrica de uma requisição."""
            pass  # ← Implemente
        
        def get_percentiles(self) -> dict:
            """TODO: Calcule p50, p95, p99 de latência."""
            return {"p50": 0, "p95": 0, "p99": 0}  # ← Implemente
        
        def get_error_rate(self) -> float:
            """TODO: Calcule taxa de erro."""
            return 0.0  # ← Implemente
    
    collector = MetricsCollector()
    
    # Simula 100 requests
    import random
    for _ in range(100):
        latency = random.uniform(50, 500)
        success = random.random() > 0.05  # 5% de erro
        tokens = random.randint(100, 2000)
        collector.record_request(latency, success, tokens)
    
    percentiles = collector.get_percentiles()
    error_rate = collector.get_error_rate()
    
    assert percentiles["p99"] >= percentiles["p95"] >= percentiles["p50"], \
        "P99 >= P95 >= P50"
    assert 0 <= error_rate <= 1, \
        f"Error rate deve ser entre 0 e 1, got {error_rate}"
    
    console.print(f"[green]✓[/green] Metrics: p50={percentiles['p50']:.0f}ms, "
                  f"p95={percentiles['p95']:.0f}ms, error_rate={error_rate:.0%}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Rollback Decision — Decisão de rollback correta?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_rollback_decision():
    """
    TODO: Implemente árvore de decisão para rollback automático.
    
    Regras:
    - Error rate > 10% → rollback imediato
    - Latency p95 > 2x baseline → warning
    - Accuracy drop > 5% vs baseline → rollback
    """
    class RollbackDecider:
        def __init__(self, baseline: dict):
            self.baseline = baseline
            self.decisions: List[dict] = []
        
        def evaluate(self, current: dict) -> dict:
            """TODO: Avalie métricas atuais vs baseline e retorne decisão."""
            return {"action": "keep", "reason": ""}  # ← Implemente
        
        def get_history(self) -> List[dict]:
            """Retorne histórico de decisões."""
            return self.decisions
    
    baseline = {
        "error_rate": 0.02,
        "latency_p95": 300,
        "accuracy": 0.95,
    }
    
    decider = RollbackDecider(baseline)
    
    # Cenário 1: Tudo OK
    ok_metrics = {"error_rate": 0.01, "latency_p95": 250, "accuracy": 0.96}
    decision_ok = decider.evaluate(ok_metrics)
    assert decision_ok["action"] == "keep", \
        "Métricas boas devem manter deployment"
    
    # Cenário 2: Error rate alto → rollback
    bad_metrics = {"error_rate": 0.15, "latency_p95": 400, "accuracy": 0.90}
    decision_bad = decider.evaluate(bad_metrics)
    assert decision_bad["action"] == "rollback", \
        "Error rate > 10% deve triggerar rollback"
    
    console.print(f"[green]✓[/green] Rollback: keep ✓, rollback triggered ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: A/B Testing — Testes A/B configurados?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_ab_testing():
    """
    TODO: Implemente framework de A/B testing para modelos.
    
    Compara performance de múltiplos modelos em produção.
    """
    class ABTestManager:
        def __init__(self, test_id: str):
            self.test_id = test_id
            self.variants: Dict[str, dict] = {}
        
        def add_variant(self, variant_name: str, traffic_pct: float):
            """TODO: Adicione variante com porcentagem de tráfego."""
            pass  # ← Implemente
        
        def assign(self, request_id: str) -> str:
            """TODO: Atribua request a uma variante baseada no hash."""
            return ""  # ← Implemente
        
        def record_result(self, variant: str, success: bool, metric_value: float):
            """TODO: Registre resultado para uma variante."""
            pass  # ← Implemente
        
        def get_winner(self) -> Optional[str]:
            """TODO: Retorne variante vencedora (maior avg metric)."""
            return None  # ← Implemente
    
    manager = ABTestManager("model_comparison_v1")
    
    manager.add_variant("gpt-4", 0.5)
    manager.add_variant("claude-3", 0.5)
    
    # Simula resultados
    results_gpt = [0.92, 0.88, 0.95, 0.90, 0.93]
    results_claude = [0.89, 0.91, 0.87, 0.94, 0.90]
    
    for i, val in enumerate(results_gpt):
        manager.record_result("gpt-4", True, val)
    for val in results_claude:
        manager.record_result("claude-3", True, val)
    
    winner = manager.get_winner()
    
    assert winner is not None, \
        "Deve haver um vencedor após registrar resultados"
    
    avg_gpt = sum(results_gpt) / len(results_gpt)
    avg_claude = sum(results_claude) / len(results_claude)
    
    expected_winner = "gpt-4" if avg_gpt > avg_claude else "claude-3"
    assert winner == expected_winner, \
        f"Winner should be {expected_winner}, got {winner}"
    
    console.print(f"[green]✓[/green] A/B Test: winner={winner} "
                  f"(gpt4={avg_gpt:.2f} vs claude3={avg_claude:.2f})")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_cicd_pipeline, test_02_health_check,
             test_03_monitoring_dashboard, test_04_rollback_decision,
             test_05_ab_testing]
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P11: Produção e Operações[/bold cyan]",
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
