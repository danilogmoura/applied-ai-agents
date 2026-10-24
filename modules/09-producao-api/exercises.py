"""Módulo P4 — Exercícios Práticos

Execute com: python modules/09-producao-api/exercises.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STUBS — Implemente estas funções para fazer os testes passarem
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def measure_middleware(func, *args) -> dict:
    """
    Middleware de monitoramento de timing.
    
    TODO: Meça o tempo de execução da função e retorne:
    {'success': bool, 'latency_ms': float, 'request_id': str}
    ← Implemente aqui
    """
    return {"success": False, "latency_ms": 0, "request_id": ""}  # Placeholder vazio


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: API Endpoint Validation — Endpoints funcionam?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_api_endpoint_validation():
    """
    Testa validação de endpoints da API.
    
    Simula uma API FastAPI com endpoints de saúde e processamento.
    """
    def mock_get_health() -> dict:
        return {"status": "healthy", "uptime_seconds": 3600}
    
    def mock_post_classify(payload: dict) -> dict:
        if not payload.get("text"):
            return {"error": "text field required"}
        return {"classification": "URGENTE", "confidence": 0.95}
    
    # Valide health endpoint
    health = mock_get_health()
    assert health["status"] == "healthy", \
        f"Health check deve retornar 'healthy', got {health['status']}"
    assert health["uptime_seconds"] > 0, \
        "Uptime deve ser positivo"
    
    # Valide classify endpoint
    result = mock_post_classify({"text": "Erro 500 na API"})
    assert "classification" in result, \
        "Response deve ter campo 'classification'"
    assert 0 <= result["confidence"] <= 1, \
        f"Confidence deve ser [0,1], got {result['confidence']}"
    
    console.print(f"[green]✓[/green] API: status={health['status']}, "
                  f"classification={result['classification']}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Input Validation — Pydantic models validam?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_input_validation():
    """
    Testa validação de inputs com regras Pydantic-like.
    """
    class RequestValidator:
        def __init__(self, text: str, model: str = "gpt-4o-mini"):
            self.text = text
            self.model = model
        
        def validate(self) -> list:
            """TODO: Retorne lista de erros (vazia se válido)."""
            # ← Implemente aqui
            return []  # Placeholder vazio
    
    # Texto válido
    valid = RequestValidator(text="Olá, como funciona?")
    # ⚠️ PONTO CRÍTICO: Valide comportamento — texto válido não gera erros
    valid_errors = valid.validate()
    assert len(valid_errors) == 0, \
        f"Texto válido não deve gerar erros, got {len(valid_errors)}"
    # Verifique que o tipo de retorno é uma lista
    assert isinstance(valid_errors, list), f"validate() deve retornar lista, got {type(valid_errors)}"
    
    # Texto vazio
    empty = RequestValidator(text="")
    empty_errors = empty.validate()
    assert len(empty_errors) > 0, \
        "Texto vazio deve gerar erro de validação"
    
    # Texto muito longo (> 4000 chars)
    long_text = RequestValidator(text="x" * 5000)
    long_errors = long_text.validate()
    assert len(long_errors) > 0, \
        "Texto > 4000 chars deve gerar erro"
    
    console.print("[green]✓[/green] Validação: vazio=erro, longo=erro ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Middleware Timing — Monitoramento de latência?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_middleware_timing():
    """
    Testa middleware de monitoramento de timing.
    
    Cenário: API TechCorp com SLA de latência.
    Requisitos:
      - Latência p95 < 200ms
      - Taxa de erro < 1%
      - Rate limiting: 100 req/min por cliente
    
    O middleware deve registrar timing para cada request,
    permitindo identificar gargalos no sistema.
    """
    import time
    
    def simulate_request(duration_ms: float) -> dict:
        time.sleep(duration_ms / 1000)
        return {"result": "ok"}
    
    metrics = measure_middleware(simulate_request, 50)
    
    assert "latency_ms" in metrics, "Metrics deve ter 'latency_ms'"
    assert "request_id" in metrics, "Metrics deve ter 'request_id'"
    assert metrics["latency_ms"] > 0, "Latency deve ser positiva"
    assert metrics["success"] == True, "Success deve ser True"
    
    console.print(f"[green]✓[/green] Middleware: {metrics['latency_ms']:.1f}ms | "
                  f"id={metrics['request_id']}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Docker Configuration — Configuração válida?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_docker_configuration():
    """
    Valida configuração Docker básica.
    
    Cenário: Deploy da API TechCorp no Kubernetes.
    Requisitos mínimos:
      - Imagem base: python:3.12-slim (menor superfície de ataque)
      - Porta exposta: 8000 (FastAPI default)
      - Variáveis obrigatórias: OPENAI_API_KEY
      - Healthcheck configurado (monitoramento contínuo)
    
    Em produção, usaríamos docker-compose ou K8s manifests.
    """
    docker_config = {
        "image": "python:3.12-slim",
        "ports": {"8000": "8000"},
        "env": {"OPENAI_API_KEY": "required"},
        "healthcheck": {
            "test": ["CMD", "curl", "-f", "http://localhost:8000/health"],
            "interval": "30s",
            "timeout": "10s",
        }
    }
    
    # TODO: Valide configuração
    assert docker_config["image"].startswith("python:"), \
        "Image deve começar com 'python:'"
    assert "8000" in docker_config["ports"], \
        "Port 8000 deve estar mapeado"
    assert "OPENAI_API_KEY" in docker_config["env"], \
        "OPENAI_API_KEY deve estar no env"
    assert "healthcheck" in docker_config, \
        "Deve ter healthcheck"
    
    console.print("[green]✓[/green] Docker config: image OK, ports mapped, healthcheck ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: API Response Format — Formato consistente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_response_format():
    """
    Verifique que todas as respostas seguem o formato padrão.
    
    Cenário: API TechCorp com contrato de interface definido.
    Padrão de resposta:
      - Sucesso: {"status": "success", "data": {...}, "meta": {...}}
      - Erro: {"status": "error", "error": "...", "meta": {...}}
    
    Meta inclui metadados comuns (timestamp, version).
    Consistência facilita parsing pelo cliente frontend.
    """
    def format_response(success: bool, data=None, error=None) -> dict:
        """TODO: Formate resposta no padrão consistente."""
        # ← Implemente aqui
        return {}  # Placeholder vazio
    
    success_resp = format_response(True, data={"classification": "ALTA"})
    error_resp = format_response(False, error="Model unavailable")
    
    # TODO: Valide formatos
    assert "status" in success_resp and success_resp["status"] == "success", \
        "Sucesso deve ter status='success'"
    assert "data" in success_resp, "Sucesso deve ter 'data'"
    
    assert "status" in error_resp and error_resp["status"] == "error", \
        "Erro deve ter status='error'"
    assert "error" in error_resp, "Erro deve ter 'error'"
    
    console.print("[green]✓[/green] Formato: success + error consistentes ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_api_endpoint_validation, test_02_input_validation,
             test_03_middleware_timing, test_04_docker_configuration,
             test_05_response_format]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P4: Produção (FastAPI + Docker)[/bold cyan]",
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
