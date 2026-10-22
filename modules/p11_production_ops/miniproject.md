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
