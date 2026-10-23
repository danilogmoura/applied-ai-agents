"""Módulo P11 — SOLUÇÃO COMENTADA

Execute com: python modules/p11_production_ops/exercises_solution.py

Código completo com explicações detalhadas.
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
    
    Funcionamento:
    1. add_stage(name, handler) → registra nome e função do estágio
    2. execute(context) → itera sobre stages em ordem
    3. Se handler falha → para pipeline, marca erro
    4. Se todos passam → retorna sucesso
    
    Isso garante que código passe por lint → test → build → deploy
    antes de ir para produção.
    """
    class CICDPipeline:
        def __init__(self):
            self.stages: List[str] = []
            self.results: List[dict] = []
        
        def add_stage(self, name: str, handler: Callable[[dict], dict]):
            """
            Adiciona estágio ao pipeline.
            
            1. Armazena nome e handler no dict
            2. Handler recebe context e retorna resultado do estágio
            """
            self.stages.append({"name": name, "handler": handler})
        
        def execute(self, context: dict) -> dict:
            """
            Executa pipeline sequencialmente.
            
            1. Para cada stage → chama handler com context
            2. Se handler falha → para, registra erro
            3. Se handler passa → registra sucesso
            4. Retorna contexto final + lista de estágios
            """
            current_context = context.copy()
            stages_executed = []
            for stage in self.stages:
                try:
                    result = stage["handler"](current_context)
                    stages_executed.append(stage["name"])
                    current_context.update(result)
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Stage {stage['name']} failed: {e}",
                        "stages_executed": stages_executed
                    }
            current_context["success"] = True
            current_context["stages_executed"] = stages_executed
            return current_context
    
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
    assert len(result.get("stages_executed", [])) == 4, \
        "Devem ter 4 estágios executados"
    
    console.print(f"[green]✓[/green] CI/CD: {len(result['stages_executed'])} stages passed ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Health Check Service — Verificações básicas funcionam?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_health_check():
    """
    Serviço de health check com múltiplas verificações.
    
    Funcionamento:
    1. configure_check(name, fn) → registra verificação
    2. run_all() → executa todas as verificações
    3. overall = healthy se todos OK, degraded se algum warning, unhealthy se algum critical
    
    Isso permite monitorar saúde do sistema continuamente.
    """
    class HealthCheckService:
        def __init__(self):
            self.checks_configured: List[str] = []
            self.checks: List[tuple] = []
        
        def configure_check(self, name: str, check_fn: Callable[[], dict]):
            """
            Configura uma verificação de saúde.
            
            1. Armazena nome e função de verificação
            2. Função retorna dict com status e dados
            """
            self.checks_configured.append(name)
            self.checks.append((name, check_fn))
        
        def run_all(self) -> dict:
            """
            Executa todas as verificações.
            
            1. Para cada check → chama função
            2. Coleta resultados
            3. Determina overall: healthy/degraded/unhealthy
            4. Retorna status geral + detalhes
            """
            checks_result = []
            has_critical = False
            has_warning = False
            
            for name, check_fn in self.checks:
                try:
                    result = check_fn()
                    checks_result.append(result)
                    if result.get("status") == "critical":
                        has_critical = True
                    elif result.get("status") == "warning":
                        has_warning = True
                except Exception as e:
                    checks_result.append({"status": "critical", "error": str(e)})
                    has_critical = True
            
            if has_critical:
                overall = "unhealthy"
            elif has_warning:
                overall = "degraded"
            else:
                overall = "healthy"
            
            return {
                "status": overall,
                "overall": overall,
                "checks": checks_result
            }
    
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
    assert len(result["checks"]) == 3, \
        f"Deve ter 3 checks, got {len(result['checks'])}"
    
    console.print(f"[green]✓[/green] Health: {result['status']} ({len(result['checks'])} checks)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Monitoring Dashboard — Métricas coletadas?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_monitoring_dashboard():
    """
    Colete métricas para dashboard de monitoramento.
    
    Funcionamento:
    1. record_request(latency, success, tokens) → armazena dados
    2. get_percentiles() → calcula p50/p95/p99 usando ordenação
    3. get_error_rate() → errors / total_requests
    
    Percentil: ordena array, pega índice = n * pct / 100.
    Isso permite visualizar performance em tempo real.
    """
    class MetricsCollector:
        def __init__(self):
            self.latencies: List[float] = []
            self.errors: int = 0
            self.total_requests: int = 0
            self.tokens_used: int = 0
        
        def record_request(self, latency_ms: float, success: bool, tokens: int):
            """
            Registra métrica de uma requisição.
            
            1. Armazena latência para cálculo de percentis
            2. Incrementa total_requests
            3. Se não sucesso → incrementa errors
            4. Acumula tokens usados
            """
            self.latencies.append(latency_ms)
            self.total_requests += 1
            if not success:
                self.errors += 1
            self.tokens_used += tokens
        
        def get_percentiles(self) -> dict:
            """
            Calcula p50, p95, p99 de latência.
            
            1. Ordena latências
            2. Para cada percentil → idx = n * pct / 100
            3. Retorna valor na posição idx
            """
            if not self.latencies:
                return {"p50": 0, "p95": 0, "p99": 0}
            sorted_latencies = sorted(self.latencies)
            n = len(sorted_latencies)
            
            def percentile(pct):
                idx = int(n * pct / 100)
                idx = min(idx, n - 1)
                return sorted_latencies[idx]
            
            return {
                "p50": percentile(50),
                "p95": percentile(95),
                "p99": percentile(99)
            }
        
        def get_error_rate(self) -> float:
            """
            Calcula taxa de erro.
            
            error_rate = errors / total_requests
            """
            if self.total_requests == 0:
                return 0.0
            return self.errors / self.total_requests
    
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
    Árvore de decisão para rollback automático.
    
    Regras (prioridade):
    1. Error rate > 10% → rollback imediato (mais crítico)
    2. Latency p95 > 2x baseline → warning (menos crítico)
    3. Accuracy drop > 5% vs baseline → rollback
    
    Lógica:
    - action começa como "keep"
    - Se regra 1 ou 3 violada → action = "rollback"
    - Se regra 2 violada E action != "rollback" → action = "warning"
    - Reasons acumula todas as regras violadas
    
    Isso permite automação de resposta a incidentes.
    """
    class RollbackDecider:
        def __init__(self, baseline: dict):
            self.baseline = baseline
            self.decisions: List[dict] = []
        
        def evaluate(self, current: dict) -> dict:
            """
            Avalia métricas atuais vs baseline.
            
            1. Inicia com action="keep"
            2. Aplica regras em ordem de criticidade
            3. Error rate > 10% → rollback
            4. Latency p95 > 2x baseline → warning (se não rollback)
            5. Accuracy drop > 5% → rollback
            6. Registra decisão no histórico
            """
            reasons = []
            action = "keep"
            
            # Regra 1: Error rate > 10% → rollback imediato
            if current.get("error_rate", 0) > 0.10:
                action = "rollback"
                reasons.append(f"Error rate {current['error_rate']:.0%} > 10%")
            
            # Regra 2: Latency p95 > 2x baseline → warning
            baseline_latency = self.baseline.get("latency_p95", 300)
            if current.get("latency_p95", 0) > 2 * baseline_latency:
                if action != "rollback":
                    action = "warning"
                reasons.append(f"Latency p95 {current['latency_p95']:.0f}ms > 2x baseline {baseline_latency}ms")
            
            # Regra 3: Accuracy drop > 5% vs baseline → rollback
            baseline_accuracy = self.baseline.get("accuracy", 0.95)
            current_accuracy = current.get("accuracy", 1.0)
            if baseline_accuracy - current_accuracy > 0.05:
                action = "rollback"
                reasons.append(f"Accuracy drop {baseline_accuracy - current_accuracy:.0%} > 5%")
            
            decision = {
                "action": action,
                "reason": "; ".join(reasons) if reasons else "Métricas dentro dos limites"
            }
            self.decisions.append(decision)
            return decision
        
        def get_history(self) -> List[dict]:
            """Retorna histórico de decisões."""
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
    Framework de A/B testing para modelos em produção.
    
    Funcionamento:
    1. add_variant(name, traffic_pct) → configura variante com % de tráfego
    2. assign(request_id) → atribui request baseado em hash MD5
    3. record_result(variant, success, metric) → registra resultado
    4. get_winner() → retorna variante com maior avg metric
    
    Hash-based assignment garante consistência: mesmo request_id
    sempre vai para mesma variante.
    """
    class ABTestManager:
        def __init__(self, test_id: str):
            self.test_id = test_id
            self.variants: Dict[str, dict] = {}
        
        def add_variant(self, variant_name: str, traffic_pct: float):
            """
            Adiciona variante com porcentagem de tráfego.
            
            traffic_pct = fração de requests que vão para esta variante
            (ex: 0.5 = 50% dos requests)
            """
            self.variants[variant_name] = {
                "traffic_pct": traffic_pct,
                "results": [],
                "total_metric": 0.0
            }
        
        def assign(self, request_id: str) -> str:
            """
            Atribui request a variante baseada em hash MD5.
            
            1. Hash request_id → número inteiro
            2. target = (hash % 100) / 100 → [0, 1)
            3. Percorre variantes somando traffic_pct cumulativo
            4. Primeira variante onde target < cumulative vence
            
            Isso garante distribuição proporcional e consistente.
            """
            import hashlib
            hash_val = int(hashlib.md5(request_id.encode()).hexdigest(), 16)
            target = (hash_val % 100) / 100.0
            cumulative = 0
            for name, info in self.variants.items():
                cumulative += info["traffic_pct"]
                if target < cumulative:
                    return name
            return list(self.variants.keys())[-1]
        
        def record_result(self, variant: str, success: bool, metric_value: float):
            """
            Registra resultado para uma variante.
            
            1. Adiciona metric_value à lista de results
            2. Acumula total_metric para cálculo de média
            """
            if variant in self.variants:
                self.variants[variant]["results"].append(metric_value)
                self.variants[variant]["total_metric"] += metric_value
        
        def get_winner(self) -> Optional[str]:
            """
            Retorna variante vencedora (maior avg metric).
            
            avg = total_metric / len(results)
            Variante com maior avg é a vencedora.
            """
            winner = None
            best_avg = -1
            
            for name, info in self.variants.items():
                if info["results"]:
                    avg = info["total_metric"] / len(info["results"])
                    if avg > best_avg:
                        best_avg = avg
                        winner = name
            
            return winner
    
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
