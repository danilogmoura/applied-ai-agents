"""Módulo P11 — Exercícios Práticos

Execute com: python modules/16-operacoes/exercises.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: CI/CD Pipeline — Estágios do pipeline funcionam?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_cicd_pipeline():
    """
    Pipeline de CI/CD com estágios sequenciais.
    
    Cenário: Pipeline TechCorp no GitHub Actions.
    Golden dataset: 500 exemplos anotados para validação de modelo.
    Thresholds mínimos:
      - Accuracy >= 0.85
      - F1-score >= 0.80
      - Latência p95 < 500ms
    
    Estágios: lint → test → build → deploy
    Se um estágio falha, pipeline para e marca falha.
    """
    class CICDPipeline:
        def __init__(self):
            self.stages: List[str] = []
            self.results: List[dict] = []
        
        def add_stage(self, name: str, handler: Callable[[dict], dict]):
            """TODO: Adicione estágio ao pipeline."""
            # ← Implemente aqui
            pass
        
        def execute(self, context: dict) -> dict:
            """TODO: Execute pipeline sequencialmente."""
            # ← Implemente aqui
            return {}  # Placeholder vazio
    
    pipeline = CICDPipeline()
    
    def lint_step(ctx):
        if not ctx.get("code", "").strip():
            raise ValueError("Código vazio")
        return {"linted": True}
    
    def test_step(ctx):
        if not ctx.get("tests_passed", False):
            raise ValueError("Testes falharam")
        return {"tested": True}
    
    def build_step(ctx):
        return {"built": True, "artifact": "model.bin"}
    
    def deploy_step(ctx):
        return {"deployed": True, "url": "https://api.example.com/v1"}
    
    pipeline.add_stage("lint", lint_step)
    pipeline.add_stage("test", test_step)
    pipeline.add_stage("build", build_step)
    pipeline.add_stage("deploy", deploy_step)
    
    result = pipeline.execute({
        "code": "print('hello')",
        "tests_passed": True
    })
    
    assert result.get("deployed") is True, \
        "Pipeline completo deve terminar com deployed=True"
    
    # ⚠️ PONTO CRÍTICO: Valide comportamento — pipeline executou todos os estágios
    expected_stages = 4  # lint → test → build → deploy
    stages = result.get("stages_executed", [])
    assert len(stages) == expected_stages, \
        f"Pipeline deve executar {expected_stages} estágios, executou {len(stages)}"
    # Verifique que cada estágio esperado está presente
    for stage_name in ["lint", "test", "build", "deploy"]:
        assert stage_name in stages, f"Estágio '{stage_name}' deveria estar no pipeline"
    
    console.print(f"[green]✓[/green] CI/CD: {len(result['stages_executed'])} stages passed ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Health Check Service — Verificações básicas funcionam?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_health_check():
    """
    Serviço de health check com múltiplas verificações.
    
    Cenário: Monitoramento contínuo da API TechCorp.
    Checks configurados:
      - endpoint_status: latência de resposta (< 200ms)
      - memory_usage: consumo de RAM (< 80%)
      - disk_space: espaço em disco disponível (> 10GB)
    
    Status: healthy (tudo OK), degraded (algum warning),
    unhealthy (algum critical).
    """
    class HealthCheckService:
        def __init__(self):
            self.checks_configured: List[str] = []
        
        def configure_check(self, name: str, check_fn: Callable[[], dict]):
            """TODO: Configure verificação."""
            # ← Implemente aqui
            pass
        
        def run_all(self) -> dict:
            """TODO: Execute todas as verificações."""
            # ← Implemente aqui
            return {}  # Placeholder vazio
    
    service = HealthCheckService()
    
    service.configure_check("endpoint_status", 
                           lambda: {"status": "healthy", "response_time_ms": 45})
    service.configure_check("memory_usage",
                           lambda: {"status": "healthy", "usage_pct": 62.5})
    service.configure_check("disk_space",
                           lambda: {"status": "warning", "available_gb": 15})
    
    result = service.run_all()
    
    assert result["overall"] in ("healthy", "degraded", "unhealthy"), \
        "Overall deve ser healthy/degraded/unhealthy"
    
    # ⚠️ PONTO CRÍTICO: Valide comportamento — todas as verificações foram executadas
    expected_checks = 3  # endpoint_status, memory_usage, disk_space
    checks = result.get("checks", [])
    assert len(checks) == expected_checks, \
        f"Health check deve executar {expected_checks} verificações, executou {len(checks)}"
    # Verifique que cada verificação esperada está presente
    for check_name in ["endpoint_status", "memory_usage", "disk_space"]:
        found = any(c.get("name") == check_name for c in checks)
        assert found, f"Verificação '{check_name}' deveria estar nos resultados"
    
    console.print(f"[green]✓[/green] Health: {result['status']} ({len(result['checks'])} checks)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Monitoring Dashboard — Métricas coletadas?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_monitoring_dashboard():
    """
    Colete métricas para dashboard de monitoramento.
    
    Cenário: Dashboard Grafana da API TechCorp.
    Métricas coletadas:
      - latency_p50/p95/p99: percentis de latência (ms)
      - error_rate: taxa de erro (fracção [0,1])
      - tokens_per_second: throughput do modelo
      - cost_per_hour: custo estimado por hora
    
    SLA: p95 < 200ms, error_rate < 0.01.
    """
    class MetricsCollector:
        def __init__(self):
            self.latencies: List[float] = []
            self.errors: int = 0
            self.total_requests: int = 0
            self.tokens_used: int = 0
        
        def record_request(self, latency_ms: float, success: bool, tokens: int):
            """Registre métrica de uma requisição."""
            # ← Implemente aqui
            pass
        
        def get_percentiles(self) -> dict:
            """Calcule p50, p95, p99 de latência."""
            # ← Implemente aqui
            return {"p50": 0, "p95": 0, "p99": 0}
        
        def get_error_rate(self) -> float:
            """Calcule taxa de erro."""
            # ← Implemente aqui
            return 0.0
    
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
    r"""
    Implemente árvore de decisão para rollback automático.
    
    Cenário: Decisão automática de rollback na TechCorp.
    Baseline v1.0: acc=0.82, err=0.02, lat_p95=300ms
    Modelo candidato v1.1: acc=0.87 (+6%), err=0.03, lat_p95=350ms
    
    Regras:
        Error rate > 10% -> rollback imediato
        Latency p95 > 2x baseline -> warning
        Accuracy drop > 5% vs baseline -> rollback
    """
    class RollbackDecider:
        def __init__(self, baseline: dict):
            self.baseline = baseline
            self.decisions: List[dict] = []
        
        def evaluate(self, current: dict) -> dict:
            """Avalie métricas atuais vs baseline e retorne decisão."""
            # ← Implemente aqui
            return {"action": "keep", "reason": ""}
        
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
            """Adicione variante com porcentagem de tráfego."""
            # ← Implemente aqui
            pass
        
        def assign(self, request_id: str) -> str:
            """Atribua request a uma variante baseada no hash."""
            # ← Implemente aqui
            return ""
        
        def record_result(self, variant: str, success: bool, metric_value: float):
            """Registre resultado para uma variante."""
            # ← Implemente aqui
            pass
        
        def get_winner(self) -> Optional[str]:
            """Retorne variante vencedora (maior avg metric)."""
            # ← Implemente aqui
            return None
    
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
# TESTE 6: Health Check Monitoring — Monitor contínuo com threshold?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_06_health_check_monitoring():
    """
    Implemente monitor de saúde que verifica endpoints continuamente.
    
    Cenário: Monitoramento da API TechCorp no Grafana.
    Regra: Se N checks consecutivos falham → alerta CRITICAL.
    
    Funcionamento:
    - check(url) → retorna True se endpoint responde, False se não
    - record_result(healthy) → registra resultado
    - Se failures >= threshold → dispara alerta CRITICAL
    - Se success após falhas → reseta contador
    
    Isso permite detecção precoce de incidentes antes de afetar usuários.
    """
    class HealthMonitor:
        def __init__(self, threshold: int = 3):
            self.threshold = threshold
            self.failures = 0
            self.alerts: List[dict] = []
        
        def check(self, url: str) -> bool:
            """TODO: Verifique se endpoint responde. Retorne True se saudável."""
            # ← Implemente aqui
            return False
        
        def record_result(self, healthy: bool, url: str = ""):
            """TODO: Registre resultado e dispare alerta se exceder threshold."""
            # ← Implemente aqui
            pass
        
        def get_alerts(self) -> List[dict]:
            """Retorne lista de alertas disparados."""
            return self.alerts
    
    monitor = HealthMonitor(threshold=3)
    
    # Simula 3 falhas consecutivas → deve disparar CRITICAL
    for i in range(3):
        monitor.record_result(False, "https://api.techcorp.com/health")
    
    assert monitor.failures >= 3, \
        f"Deve registrar {monitor.threshold}+ falhas consecutivas, got {monitor.failures}"
    assert len(monitor.get_alerts()) > 0, \
        "Alerta CRITICAL deve ser disparado após threshold de falhas"
    
    # Sucesso após falhas deve resetar contador
    monitor.record_result(True, "https://api.techcorp.com/health")
    assert monitor.failures == 0, \
        "Sucesso deve resetar contador de falhas"
    
    console.print(f"[green]✓[/green] Health Monitor: {len(monitor.get_alerts())} alert(s) triggered ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_cicd_pipeline, test_02_health_check,
             test_03_monitoring_dashboard, test_04_rollback_decision,
             test_05_ab_testing, test_06_health_check_monitoring]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
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
