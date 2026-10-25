"""
Módulo 16 — Operations de Produção: CI/CD e Monitoramento

Sistema completo de observabilidade para agentes em produção:
- Prompt testing com A/B comparison
- Logging estruturado com tracing
- Métricas de custo, latência e qualidade
- Alertas e dashboards simulados
- Rollback automático de prompts

Problema: Como saber se um novo prompt quebrou algo?
Testes A/B + métricas em tempo real + rollback automático.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live

from shared.logging_config import setup_logging
from shared.cost import TOKEN_PRICES, count_tokens, estimate_cost, format_cost

console = Console()
logger = setup_logging("16-operacoes")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENUMS & MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AlertLevel(Enum):
    """Nível de alerta."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MetricPoint:
    """Ponto de métrica individual."""
    
    timestamp: float
    metric_name: str
    value: float
    labels: dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "metric_name": self.metric_name,
            "value": self.value,
            "labels": self.labels,
        }


@dataclass
class Alert:
    """Alerta do sistema."""
    
    level: AlertLevel
    message: str
    metric: str
    threshold: float
    current_value: float
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "message": self.message,
            "metric": self.metric,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "timestamp": self.timestamp,
        }


@dataclass
class PromptVersion:
    """Versão de prompt testada."""
    
    id: str
    name: str
    content: str
    version: int
    created_at: float = field(default_factory=time.time)
    is_active: bool = False
    test_results: dict[str, Any] = field(default_factory=dict)
    success_rate: float = 0.0
    avg_cost: float = 0.0
    avg_latency_ms: float = 0.0
    call_count: int = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "is_active": self.is_active,
            "success_rate": self.success_rate,
            "avg_cost": format_cost(self.avg_cost),
            "avg_latency_ms": round(self.avg_latency_ms, 1),
            "call_count": self.call_count,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# METRICS COLLECTOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class MetricsCollector:
    """
    Coletor de métricas para monitoramento em tempo real.
    
    Em produção, enviaria para Prometheus/Grafana.
    Aqui simula com armazenamento em memória.
    """
    
    def __init__(self, max_points: int = 10000):
        self._points: list[MetricPoint] = []
        self.max_points = max_points
        self._alerts: list[Alert] = []
        
        # Thresholds padrão
        self.thresholds = {
            "latency_p95": {"warning": 2000, "critical": 5000},  # ms
            "error_rate": {"warning": 0.05, "critical": 0.15},   # %
            "cost_per_request": {"warning": 0.01, "critical": 0.05},  # $
        }
    
    def record(self, metric_name: str, value: float, 
               labels: dict[str, str] | None = None) -> None:
        """Registra ponto de métrica."""
        point = MetricPoint(
            timestamp=time.time(),
            metric_name=metric_name,
            value=value,
            labels=labels or {},
        )
        
        self._points.append(point)
        
        # Mantém tamanho máximo (FIFO)
        if len(self._points) > self.max_points:
            self._points = self._points[-self.max_points:]
        
        # Verifica thresholds
        self._check_thresholds(metric_name, value)
    
    def _check_thresholds(self, metric_name: str, value: float) -> None:
        """Verifica se valor excede thresholds."""
        thresholds = self.thresholds.get(metric_name)
        if not thresholds:
            return
        
        if value >= thresholds["critical"]:
            alert = Alert(
                level=AlertLevel.CRITICAL,
                message=f"{metric_name} crítico: {value:.2f} (threshold: {thresholds['critical']})",
                metric=metric_name,
                threshold=thresholds["critical"],
                current_value=value,
            )
            self._alerts.append(alert)
            logger.critical(f"CRITICAL ALERT: {alert.message}")
        
        elif value >= thresholds["warning"]:
            alert = Alert(
                level=AlertLevel.WARNING,
                message=f"{metric_name} alto: {value:.2f} (threshold: {thresholds['warning']})",
                metric=metric_name,
                threshold=thresholds["warning"],
                current_value=value,
            )
            self._alerts.append(alert)
            logger.warning(f"WARNING ALERT: {alert.message}")
    
    def get_average(self, metric_name: str, window_seconds: int = 300) -> float:
        """Calcula média de métrica no último window."""
        cutoff = time.time() - window_seconds
        recent = [
            p for p in self._points
            if p.metric_name == metric_name and p.timestamp >= cutoff
        ]
        
        if not recent:
            return 0.0
        
        return sum(p.value for p in recent) / len(recent)
    
    def get_percentile(self, metric_name: str, percentile: float,
                       window_seconds: int = 300) -> float:
        """Calcula percentil de métrica."""
        cutoff = time.time() - window_seconds
        recent = sorted([
            p.value for p in self._points
            if p.metric_name == metric_name and p.timestamp >= cutoff
        ])
        
        if not recent:
            return 0.0
        
        idx = int(len(recent) * percentile / 100)
        return recent[min(idx, len(recent) - 1)]
    
    def get_dashboard(self) -> dict:
        """Retorna dados para dashboard."""
        return {
            "latency_p50": round(self.get_average("latency_ms"), 1),
            "latency_p95": round(self.get_percentile("latency_ms", 95), 1),
            "latency_p99": round(self.get_percentile("latency_ms", 99), 1),
            "error_rate": round(self.get_average("error_rate") * 100, 2),
            "cost_per_request": round(self.get_average("cost_usd"), 4),
            "requests_per_minute": round(
                len([p for p in self._points if p.metric_name == "request"]) / max(5, 1), 1
            ),
            "active_alerts": len([a for a in self._alerts if a.timestamp > time.time() - 300]),
        }
    
    def get_recent_alerts(self, limit: int = 10) -> list[dict]:
        """Retorna alertas recentes."""
        return [a.to_dict() for a in self._alerts[-limit:]]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROMPT TESTER (A/B Testing)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PromptTester:
    """
    Testador de prompts com A/B comparison.
    
    Compara versões de prompt para ver qual performa melhor.
    Em produção, rodaria contra dataset de testes antes de deploy.
    """
    
    def __init__(self, metrics: MetricsCollector):
        self.metrics = metrics
        self._versions: dict[str, PromptVersion] = {}
        self._test_dataset: list[dict] = []
    
    def register_version(self, name: str, content: str, version: int = 1) -> str:
        """Registra versão de prompt."""
        version_id = f"{name}_v{version}"
        
        prompt = PromptVersion(
            id=version_id,
            name=name,
            content=content,
            version=version,
        )
        
        self._versions[version_id] = prompt
        logger.info(f"Prompt registrado: {version_id}")
        
        return version_id
    
    def add_test_case(self, input_text: str, expected_output: str, 
                      weight: float = 1.0) -> None:
        """Adiciona caso de teste ao dataset."""
        self._test_dataset.append({
            "input": input_text,
            "expected": expected_output,
            "weight": weight,
        })
    
    async def run_test(self, version_id: str) -> dict:
        """
        Executa teste completo contra dataset.
        
        Returns:
            Resultados do teste com métricas de sucesso.
        """
        prompt = self._versions.get(version_id)
        if not prompt:
            raise ValueError(f"Prompt version not found: {version_id}")
        
        console.print(f"\n[bold cyan]🧪 Testando prompt: {version_id}[/]")
        console.print(f"  [dim]Dataset: {len(self._test_dataset)} casos[/]\n")
        
        results = {
            "total": len(self._test_dataset),
            "passed": 0,
            "failed": 0,
            "total_cost": 0.0,
            "total_latency_ms": 0.0,
            "examples": [],
        }
        
        for i, test_case in enumerate(self._test_dataset):
            start = time.time()
            
            # Simula execução do prompt
            output = self._simulate_prompt(prompt.content, test_case["input"])
            
            latency = (time.time() - start) * 1000
            cost = estimate_cost(
                count_tokens([{"role": "user", "content": prompt.content}]),
                count_tokens([{"role": "assistant", "content": output}]),
                "gpt-4o-mini",
            )
            
            # Avalia sucesso (simulado)
            passed = self._evaluate(output, test_case["expected"])
            
            results["total_cost"] += cost
            results["total_latency_ms"] += latency
            
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
            
            # Salva exemplos (max 3)
            if i < 3:
                results["examples"].append({
                    "input": test_case["input"][:50],
                    "expected": test_case["expected"][:50],
                    "actual": output[:50],
                    "passed": passed,
                })
            
            # Registra métricas
            self.metrics.record("latency_ms", latency, {"prompt": version_id})
            self.metrics.record("cost_usd", cost, {"prompt": version_id})
            self.metrics.record("error_rate", 0 if passed else 1, {"prompt": version_id})
        
        # Calcula taxas
        results["success_rate"] = round(results["passed"] / max(results["total"], 1) * 100, 1)
        results["avg_cost"] = results["total_cost"] / max(results["total"], 1)
        results["avg_latency_ms"] = results["total_latency_ms"] / max(results["total"], 1)
        
        # Atualiza versão
        prompt.success_rate = results["success_rate"]
        prompt.avg_cost = results["avg_cost"]
        prompt.avg_latency_ms = results["avg_latency_ms"]
        prompt.call_count = results["total"]
        prompt.test_results = results
        
        console.print(f"  [dim]Resultados:[/]")
        console.print(f"    Passou: {results['passed']}/{results['total']} ({results['success_rate']}%)")
        console.print(f"    Custo total: {format_cost(results['total_cost'])}")
        console.print(f"    Latência média: {results['avg_latency_ms']:.0f}ms\n")
        
        return results
    
    async def compare_versions(self, version_ids: list[str]) -> dict:
        """Compara múltiplas versões de prompt."""
        console.print("\n[bold yellow]⚖️  Comparação A/B de Prompts[/]\n")
        
        comparisons = []
        
        for vid in version_ids:
            results = await self.run_test(vid)
            comparisons.append({
                "version_id": vid,
                "success_rate": results["success_rate"],
                "avg_cost": results["avg_cost"],
                "avg_latency_ms": results["avg_latency_ms"],
            })
        
        # Ordena por success_rate
        comparisons.sort(key=lambda x: -x["success_rate"])
        
        # Mostra tabela comparativa
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Versão", style="cyan")
        table.add_column("Success Rate", justify="right")
        table.add_column("Custo Médio", justify="right")
        table.add_column("Latência Média", justify="right")
        
        for comp in comparisons:
            table.add_row(
                comp["version_id"],
                f"{comp['success_rate']}%",
                format_cost(comp["avg_cost"]),
                f"{comp['avg_latency_ms']:.0f}ms",
            )
        
        console.print(table)
        
        return {"comparisons": comparisons, "best": comparisons[0]}
    
    def _simulate_prompt(self, prompt_template: str, user_input: str) -> str:
        """Simula resposta do LLM."""
        responses = {
            "spam_classifier": "not_spam",
            "sentiment_analyzer": "positive",
            "summarizer": "Resumo do texto gerado.",
            "default": "Resposta simulada do prompt.",
        }
        
        if "spam" in prompt_template.lower():
            return "not_spam" if "não spam" in user_input.lower() else "spam"
        elif "sentiment" in prompt_template.lower():
            return "positive" if "bom" in user_input.lower() else "negative"
        elif "summarize" in prompt_template.lower():
            return "Resumo do texto gerado."
        
        return "Resposta simulada do prompt."
    
    def _evaluate(self, actual: str, expected: str) -> bool:
        """Avalia se saída está correta."""
        return actual.lower().strip() == expected.lower().strip()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROMPT MANAGER (Deploy/Rollback)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PromptManager:
    """
    Gerencia deploy e rollback de prompts em produção.
    
    Fluxo:
    1. Testa nova versão
    2. Se success_rate > threshold → deploy
    3. Se métricas degradarem → rollback automático
    """
    
    def __init__(self, tester: PromptTester, metrics: MetricsCollector):
        self.tester = tester
        self.metrics = metrics
        self._active_prompts: dict[str, str] = {}  # name -> version_id
        self._deployment_log: list[dict] = []
        self.rollback_threshold = 80.0  # % success rate mínimo
    
    def deploy(self, name: str, version_id: str) -> dict:
        """
        Deploy de prompt em produção.
        
        Só permite deploy se testes passaram.
        """
        prompt = self.tester._versions.get(version_id)
        if not prompt:
            return {"success": False, "error": f"Version not found: {version_id}"}
        
        if prompt.success_rate < self.rollback_threshold:
            return {
                "success": False,
                "error": f"Success rate {prompt.success_rate}% below threshold {self.rollback_threshold}%",
            }
        
        old_version = self._active_prompts.get(name)
        self._active_prompts[name] = version_id
        
        # Desativa versão anterior
        if old_version and old_version in self.tester._versions:
            self.tester._versions[old_version].is_active = False
        
        prompt.is_active = True
        
        deployment = {
            "name": name,
            "new_version": version_id,
            "old_version": old_version,
            "deployed_at": time.time(),
            "success_rate": prompt.success_rate,
        }
        
        self._deployment_log.append(deployment)
        
        logger.info(f"Deploy: {name} → {version_id}")
        
        return {"success": True, "deployment": deployment}
    
    def rollback(self, name: str) -> dict:
        """Rollback para versão anterior."""
        version_id = self._active_prompts.get(name)
        if not version_id:
            return {"success": False, "error": "No active version"}
        
        prompt = self.tester._versions.get(version_id)
        if not prompt:
            return {"success": False, "error": "Version not found"}
        
        # Encontra versão anterior
        previous_version = None
        for vid, vp in self.tester._versions.items():
            if vp.name == name and vp.version < prompt.version:
                previous_version = vid
        
        if previous_version:
            result = self.deploy(name, previous_version)
            result["rollback"] = True
            return result
        
        return {"success": False, "error": "No previous version to rollback to"}
    
    def get_active_prompts(self) -> list[dict]:
        """Lista prompts ativos."""
        return [
            {
                "name": name,
                "version_id": vid,
                **self.tester._versions.get(vid, PromptVersion(
                    id=vid, name=name, content="", version=0
                )).to_dict(),
            }
            for name, vid in self._active_prompts.items()
        ]
    
    def check_health(self) -> dict:
        """Verifica saúde dos prompts ativos."""
        dashboard = self.metrics.get_dashboard()
        
        health = {
            "status": "healthy",
            "metrics": dashboard,
            "issues": [],
        }
        
        if dashboard.get("error_rate", 0) > 5:
            health["status"] = "degraded"
            health["issues"].append(f"Error rate high: {dashboard['error_rate']}%")
        
        if dashboard.get("latency_p95", 0) > 3000:
            health["status"] = "degraded"
            health["issues"].append(f"P95 latency high: {dashboard['latency_p95']}ms")
        
        if dashboard.get("active_alerts", 0) > 3:
            health["status"] = "critical"
            health["issues"].append(f"Too many alerts: {dashboard['active_alerts']}")
        
        return health


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    """Executa demonstração completa de production ops."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO 16 — Production Ops: CI/CD + Monitoring[/]\n\n"
        "Prompt testing A/B, métricas em tempo real,\n"
        "alertas, dashboard e rollback automático.",
        title="🏭 AI Agents Course",
        border_style="cyan",
    ))
    
    # Inicializa componentes
    metrics = MetricsCollector()
    tester = PromptTester(metrics)
    manager = PromptManager(tester, metrics)
    
    # ━━ 1. Registra prompts ━━
    console.print("\n[bold]1️⃣  Registrando Versões de Prompt:[/]\n")
    
    v1_id = tester.register_version(
        "spam_classifier",
        "Classifique este email como spam ou não: {text}",
        version=1,
    )
    
    v2_id = tester.register_version(
        "spam_classifier",
        """Analise o email abaixo e classifique:
- Responda apenas 'spam' ou 'not_spam'
- Considura: remetente, conteúdo, links, urgência

Email: {text}""",
        version=2,
    )
    
    console.print(f"  ✅ v1: {v1_id}")
    console.print(f"  ✅ v2: {v2_id}")
    
    # ━━ 2. Adiciona casos de teste ━━
    console.print("\n[bold]2️⃣  Dataset de Testes:[/]\n")
    
    test_cases = [
        ("Compra barata! Clique aqui!", "spam", 1.0),
        ("Reunião amanhã às 10h", "not_spam", 1.0),
        ("Oferta exclusiva por tempo limitado!", "spam", 1.0),
        ("Obrigado pela entrega rápida", "not_spam", 1.0),
        ("Seu prêmio está esperando!", "spam", 1.0),
        ("Relatório mensal anexado", "not_spam", 1.0),
    ]
    
    for text, expected, weight in test_cases:
        tester.add_test_case(text, expected, weight)
        console.print(f"  [dim]• '{text[:40]}...' → {expected}")
    
    # ━━ 3. Testa prompts ━━
    console.print("\n[bold]3️⃣  Testando Prompts:[/]\n")
    
    await tester.run_test(v1_id)
    await tester.run_test(v2_id)
    
    # ━━ 4. Deploy ━━
    console.print("\n[bold]4️⃣  Deploy em Produção:[/]\n")
    
    deploy_result = manager.deploy("spam_classifier", v2_id)
    
    if deploy_result["success"]:
        console.print(f"  [green]✅ Deploy bem-sucedido![/]")
        console.print(f"  Spam classifier → v2 (success rate: {deploy_result['deployment']['success_rate']}%)")
    else:
        console.print(f"  [red]✕ Deploy bloqueado:[/] {deploy_result['error']}")
    
    # ━━ 5. Dashboard em tempo real ━━
    console.print("\n[bold]5️⃣  Dashboard de Monitoramento:[/]\n")
    
    dashboard = metrics.get_dashboard()
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", justify="right")
    
    table.add_row("Latência P50", f"{dashboard['latency_p50']:.0f}ms")
    table.add_row("Latência P95", f"{dashboard['latency_p95']:.0f}ms")
    table.add_row("Latência P99", f"{dashboard['latency_p99']:.0f}ms")
    table.add_row("Taxa de erro", f"{dashboard['error_rate']}%")
    # cost_per_request e float -> rich exige string/renderable, entao formata.
    table.add_row("Custo/request", f"${dashboard['cost_per_request']:.8f}")
    table.add_row("Alerts ativos", str(dashboard['active_alerts']))
    
    console.print(table)
    
    # ━━ 6. Health Check ━━
    console.print("\n[bold]6️⃣  Health Check:[/]\n")
    
    health = manager.check_health()
    status_icon = "🟢" if health["status"] == "healthy" else "🟡" if health["status"] == "degraded" else "🔴"
    console.print(f"  {status_icon} Status: {health['status'].upper()}")
    
    if health["issues"]:
        for issue in health["issues"]:
            console.print(f"  [yellow]⚠ {issue}[/]")
    
    # ━━ 7. Active Prompts ━━
    console.print("\n[bold]7️⃣  Prompts Ativos:[/]\n")
    
    active = manager.get_active_prompts()
    for prompt in active:
        console.print(f"  [dim]•[/] {prompt['name']}: [bold]{prompt['version_id']}[/] "
                     f"(success: {prompt['success_rate']}%, calls: {prompt['call_count']})")
    
    console.print("\n[dim]💡 Monitorar é prevenir desastres![/]")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
