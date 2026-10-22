# 🏗️ Mini-Projeto Integrador — Production Ops

> **Objetivo:** Construir um sistema de operações para agentes IA em produção.

## O que você vai construir

Um ops system `ops_system.py` que:

1. **Executa** pipeline CI/CD com estágios sequenciais
2. **Monitora** health check de serviços IA
3. **Coleta** métricas para dashboard (latência, erro, custo)
4. **Decide** rollback baseado em thresholds
5. **Gerencia** A/B testing de modelos

## Requisitos

```python
class OpsSystem:
    def run_cicd_pipeline(self, stages: list = None) -> dict:
        """Executar pipeline CI/CD: lint → test → build → deploy."""
        ...
    
    def run_health_checks(self) -> dict:
        """Verificar saúde: LLM API, rate limit, memory."""
        ...
    
    def record_request(self, latency_ms: float, success: bool, tokens: int) -> None:
        """Registrar métrica de request."""
        ...
    
    def get_percentiles(self) -> dict:
        """Calcular p50, p95, p99 de latência."""
        ...
    
    def evaluate_rollback(self, current_metrics: dict, 
                          baseline: dict) -> dict:
        """Decidir rollback: error_rate > 10%, accuracy drop > 5%."""
        ...
    
    def add_ab_variant(self, name: str, traffic_pct: float) -> None:
        """Adicionar variante para A/B testing."""
        ...
    
    def get_ab_winner(self) -> Optional[str]:
        """Determinar vencedor do A/B test."""
        ...
```

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com pipeline CI/CD

Implemente pipeline sequencial com estágios:

```python
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
import time
import random

class OpsSystem:
    def __init__(self):
        self.metrics = {
            "latencies": [],       # latências em ms
            "errors": [],          # booleanos
            "tokens": [],          # tokens por request
            "costs": [],           # custo por request
        }
        self.ab_variants = {}   # name -> {traffic_pct, wins, losses}
        self.cicd_log = []
    
    def run_cicd_pipeline(self, stages: List[str] = None) -> Dict:
        """Executar pipeline CI/CD: lint → test → build → deploy."""
        if stages is None:
            stages = ["lint", "test", "build", "deploy"]
        
        result = {
            "pipeline_id": f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "stages": [],
            "status": "success",
            "started_at": datetime.now().isoformat(),
        }
        
        for stage in stages:
            stage_result = {
                "stage": stage,
                "status": "running",
                "started_at": datetime.now().isoformat(),
            }
            
            try:
                # Simula execução do estágio
                if not self._execute_stage(stage):
                    stage_result["status"] = "failed"
                    stage_result["error"] = f"Stage '{stage}' failed"
                    result["status"] = "failed"
                    break
                
                stage_result["status"] = "passed"
                
            except Exception as e:
                stage_result["status"] = "error"
                stage_result["error"] = str(e)
                result["status"] = "error"
                break
            
            stage_result["completed_at"] = datetime.now().isoformat()
            result["stages"].append(stage_result)
        
        result["completed_at"] = datetime.now().isoformat()
        self.cicd_log.append(result)
        return result
    
    def _execute_stage(self, stage: str) -> bool:
        """Simula execução de um estágio do pipeline."""
        # Simula sucesso/falha (90% de chance de sucesso)
        success = random.random() < 0.9
        
        # Stage-specific checks
        if stage == "lint":
            # Simula check de linting
            return success
        elif stage == "test":
            # Simula testes unitários
            return success
        elif stage == "build":
            # Simula build de Docker image
            return success
        elif stage == "deploy":
            # Simula deploy para staging/production
            return success
        
        return True
```

### Passo 2 — Implemente health checks

```python
    def run_health_checks(self) -> Dict:
        """Verificar saúde: LLM API, rate limit, memory."""
        checks = []
        
        # Check 1: LLM API availability
        llm_status = self._check_llm_api()
        checks.append(llm_status)
        
        # Check 2: Rate limiting
        rate_limit = self._check_rate_limit()
        checks.append(rate_limit)
        
        # Check 3: Memory usage
        memory = self._check_memory()
        checks.append(memory)
        
        # Check 4: Disk space
        disk = self._check_disk()
        checks.append(disk)
        
        overall_healthy = all(c.get("healthy", False) for c in checks)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "healthy": overall_healthy,
            "checks": checks,
            "healthy_count": sum(1 for c in checks if c.get("healthy")) ,
            "total_checks": len(checks),
        }
    
    def _check_llm_api(self) -> Dict:
        """Verifica se LLM API está respondendo."""
        try:
            # Simula ping à API
            response_time_ms = random.uniform(50, 500)
            healthy = response_time_ms < 1000
            
            return {
                "name": "llm_api",
                "healthy": healthy,
                "response_time_ms": round(response_time_ms, 2),
                "message": "API responding normally" if healthy else "API timeout",
            }
        except Exception as e:
            return {
                "name": "llm_api",
                "healthy": False,
                "error": str(e),
                "message": "LLM API unreachable",
            }
    
    def _check_rate_limit(self) -> Dict:
        """Verifica status de rate limiting."""
        # Simula uso atual vs limite
        current_usage = random.uniform(0.3, 0.95)
        healthy = current_usage < 0.9
        
        return {
            "name": "rate_limit",
            "healthy": healthy,
            "usage_pct": round(current_usage * 100, 1),
            "message": "Within limits" if healthy else "Approaching limit",
        }
    
    def _check_memory(self) -> Dict:
        """Verifica uso de memória."""
        # Simula uso de memória (GB)
        used_gb = random.uniform(2, 7)
        total_gb = 8
        healthy = used_gb / total_gb < 0.85
        
        return {
            "name": "memory",
            "healthy": healthy,
            "used_gb": round(used_gb, 1),
            "total_gb": total_gb,
            "usage_pct": round(used_gb / total_gb * 100, 1),
            "message": "Memory OK" if healthy else "High memory usage",
        }
    
    def _check_disk(self) -> Dict:
        """Verifica espaço em disco."""
        used_gb = random.uniform(10, 40)
        total_gb = 50
        healthy = used_gb / total_gb < 0.9
        
        return {
            "name": "disk",
            "healthy": healthy,
            "used_gb": round(used_gb, 1),
            "total_gb": total_gb,
            "usage_pct": round(used_gb / total_gb * 100, 1),
            "message": "Disk OK" if healthy else "Low disk space",
        }
```

### Passo 3 — Registre métricas de request

```python
    def record_request(self, latency_ms: float, success: bool, 
                       tokens: int, cost: float = 0.01) -> None:
        """Registrar métrica de request."""
        self.metrics["latencies"].append(latency_ms)
        self.metrics["errors"].append(not success)
        self.metrics["tokens"].append(tokens)
        self.metrics["costs"].append(cost)
    
    def get_percentiles(self) -> Dict:
        """Calcular p50, p95, p99 de latência."""
        if not self.metrics["latencies"]:
            return {"sample_size": 0}
        
        sorted_latencies = sorted(self.metrics["latencies"])
        n = len(sorted_latencies)
        
        def percentile(p):
            idx = int(n * p)
            idx = min(idx, n - 1)
            return sorted_latencies[idx]
        
        error_rate = sum(self.metrics["errors"]) / n if n > 0 else 0
        
        return {
            "sample_size": n,
            "latency": {
                "p50_ms": round(percentile(0.50), 2),
                "p95_ms": round(percentile(0.95), 2),
                "p99_ms": round(percentile(0.99), 2),
                "avg_ms": round(sum(sorted_latencies) / n, 2),
                "min_ms": round(sorted_latencies[0], 2),
                "max_ms": round(sorted_latencies[-1], 2),
            },
            "error_rate": round(error_rate, 4),
            "total_tokens": sum(self.metrics["tokens"]),
            "total_cost": round(sum(self.metrics["costs"]), 4),
        }
    
    def record_batch(self, requests: List[Dict]) -> None:
        """Registra batch de requests simulados."""
        for req in requests:
            self.record_request(
                latency_ms=req.get("latency_ms", random.uniform(100, 1000)),
                success=req.get("success", random.random() > 0.05),
                tokens=req.get("tokens", random.randint(50, 500)),
                cost=req.get("cost", 0.01),
            )
```

### Passo 4 — Decida rollback baseado em thresholds

```python
    def evaluate_rollback(self, current_metrics: Dict,
                          baseline: Dict) -> Dict:
        """Decidir rollback: error_rate > 10%, accuracy drop > 5%."""
        decisions = []
        
        # Check 1: Error rate
        current_error = current_metrics.get("error_rate", 0)
        baseline_error = baseline.get("error_rate", 0)
        error_threshold = 0.10  # 10%
        
        if current_error > error_threshold:
            decisions.append({
                "check": "error_rate",
                "action": "ROLLBACK",
                "reason": f"Error rate {current_error:.2%} exceeds threshold {error_threshold:.0%}",
                "severity": "CRITICAL",
            })
        elif current_error > baseline_error * 2:
            decisions.append({
                "check": "error_rate",
                "action": "WARNING",
                "reason": f"Error rate doubled from baseline ({baseline_error:.2%} → {current_error:.2%})",
                "severity": "MEDIUM",
            })
        
        # Check 2: Latency degradation
        current_p95 = current_metrics.get("latency_p95_ms", 0)
        baseline_p95 = baseline.get("latency_p95_ms", 0)
        latency_threshold = 1.5  # 50% degradation
        
        if baseline_p95 > 0 and current_p95 > baseline_p95 * latency_threshold:
            decisions.append({
                "check": "latency",
                "action": "ROLLBACK",
                "reason": f"P95 latency degraded {current_p95:.0f}ms vs {baseline_p95:.0f}ms baseline",
                "severity": "HIGH",
            })
        
        # Check 3: Cost increase
        current_cost = current_metrics.get("total_cost", 0)
        baseline_cost = baseline.get("total_cost", 0)
        cost_threshold = 2.0  # 100% increase
        
        if baseline_cost > 0 and current_cost > baseline_cost * cost_threshold:
            decisions.append({
                "check": "cost",
                "action": "WARNING",
                "reason": f"Cost increased {current_cost/baseline_cost:.1f}x from baseline",
                "severity": "MEDIUM",
            })
        
        # Decisão final
        has_critical = any(d["action"] == "ROLLBACK" for d in decisions)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "should_rollback": has_critical,
            "decisions": decisions,
            "num_decisions": len(decisions),
            "recommendation": "🔴 ROLLBACK" if has_critical else "🟢 CONTINUE",
        }
```

### Passo 5 — Gerencie A/B testing de modelos

```python
    def add_ab_variant(self, name: str, traffic_pct: float,
                       model: str = None) -> None:
        """Adicionar variante para A/B testing."""
        if traffic_pct < 0 or traffic_pct > 100:
            raise ValueError("traffic_pct deve ser entre 0 e 100")
        
        self.ab_variants[name] = {
            "traffic_pct": traffic_pct,
            "model": model or name,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "total_requests": 0,
            "added_at": datetime.now().isoformat(),
        }
    
    def route_request(self) -> str:
        """Roteia request para variante baseada em traffic_pct."""
        if not self.ab_variants:
            return "default"
        
        # Normaliza traffic_pct para soma = 100
        total_pct = sum(v["traffic_pct"] for v in self.ab_variants.values())
        
        if total_pct == 0:
            return "default"
        
        import random
        r = random.uniform(0, total_pct)
        cumulative = 0
        
        for name, variant in self.ab_variants.items():
            cumulative += variant["traffic_pct"]
            if r <= cumulative:
                variant["total_requests"] += 1
                return name
        
        # Fallback para última variante
        last_name = list(self.ab_variants.keys())[-1]
        self.ab_variants[last_name]["total_requests"] += 1
        return last_name
    
    def record_ab_result(self, variant: str, won: bool) -> None:
        """Registra resultado do A/B test."""
        if variant in self.ab_variants:
            if won:
                self.ab_variants[variant]["wins"] += 1
            else:
                self.ab_variants[variant]["losses"] += 1
    
    def get_ab_winner(self) -> Optional[Dict]:
        """Determina vencedor do A/B test."""
        if not self.ab_variants:
            return None
        
        best_variant = None
        best_win_rate = 0
        
        for name, variant in self.ab_variants.items():
            total = variant["wins"] + variant["losses"]
            if total < 10:
                continue  # Dados insuficientes
            
            win_rate = variant["wins"] / total
            if win_rate > best_win_rate:
                best_win_rate = win_rate
                best_variant = {
                    "name": name,
                    "win_rate": round(win_rate, 4),
                    "wins": variant["wins"],
                    "losses": variant["losses"],
                    "total": total,
                }
        
        return best_variant
```

### Passo 6 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de ops para produção")
    parser.add_argument("--health-check", action="store_true", help="Executa health checks")
    parser.add_argument("--cicd", action="store_true", help="Executa pipeline CI/CD")
    parser.add_argument("--stages", help="Stages do pipeline (separados por vírgula)")
    parser.add_argument("--simulate", action="store_true", help="Simula requests")
    parser.add_argument("--percentiles", action="store_true", help="Mostra percentis")
    parser.add_argument("--rollback", action="store_true", help="Avalia rollback")
    parser.add_argument("--ab-test", nargs=2, metavar=('A', 'B'),
                        help="Arquivos para A/B testing")
    parser.add_argument("--output", help="Arquivo de output")
    args = parser.parse_args()
    
    ops = OpsSystem()
    
    if args.health_check:
        health = ops.run_health_checks()
        print(json.dumps(health, indent=2, ensure_ascii=False))
    
    elif args.cicd:
        stages = [s.strip() for s in args.stages.split(",")] if args.stages else None
        pipeline = ops.run_cicd_pipeline(stages)
        print(json.dumps(pipeline, indent=2, ensure_ascii=False))
    
    elif args.simulate:
        # Simula 100 requests
        requests = [
            {
                "latency_ms": random.uniform(100, 1000),
                "success": random.random() > 0.05,
                "tokens": random.randint(50, 500),
                "cost": round(random.uniform(0.005, 0.05), 4),
            }
            for _ in range(100)
        ]
        ops.record_batch(requests)
        
        stats = ops.get_percentiles()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.percentiles:
        stats = ops.get_percentiles()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif args.rollback:
        current = {
            "error_rate": 0.12,
            "latency_p95_ms": 800,
            "total_cost": 50.0,
        }
        baseline = {
            "error_rate": 0.03,
            "latency_p95_ms": 400,
            "total_cost": 20.0,
        }
        decision = ops.evaluate_rollback(current, baseline)
        print(json.dumps(decision, indent=2, ensure_ascii=False))
    
    else:
        print("🔧 Ops System - Execute uma das opções:")
        print("  --health-check      Health checks completos")
        print("  --cicd              Pipeline CI/CD")
        print("  --simulate           Simula 100 requests")
        print("  --percentiles        Mostra percentis de latência")
        print("  --rollback           Avalia necessidade de rollback")
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `run_cicd_pipeline()` executa estágios sequenciais (lint → test → build → deploy) com error handling
- [ ] `run_health_checks()` verifica LLM API, rate limit, memory e disk com status healthy/unhealthy
- [ ] `record_request()` registra latência/success/tokens/custo; `get_percentiles()` calcula p50/p95/p99
- [ ] `evaluate_rollback()` decide ROLLBACK se error_rate > 10% ou latency degradou > 50%
- [ ] `add_ab_variant()` registra variante com traffic_pct; `get_ab_winner()` determina vencedor por win_rate
- [ ] CLI aceita `--health-check`, `--cicd`, `--simulate`, `--rollback` e gera JSON

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

## Teste seu código

```bash
python ops_system.py --health-check --output health.json
python ops_system.py --cicd --stages lint,test,build
python ops_system.py --ab-test variant_a.json variant_b.json
```

## Desafios extras

- [ ] Grafana dashboard integration
- [ ] PagerDuty alerts para incidents
- [ ] Auto-scaling baseado em load
- [ ] Rollback automation com git revert
