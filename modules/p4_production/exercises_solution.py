"""Módulo P4 — SOLUÇÃO COMENTADA

Execute com: python modules/p4_production/exercises.py

Código completo com explicações detalhadas.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: API Endpoint Validation — Endpoints funcionam?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_api_endpoint_validation():
    """
    Validação de endpoints de API simulando FastAPI.
    
    Em produção, usaríamos httpx ou requests para testar endpoints reais.
    Aqui simulamos com funções mock que retornam dicionários.
    """
    def mock_get_health() -> dict:
        return {"status": "healthy", "uptime_seconds": 3600}
    
    def mock_post_classify(payload: dict) -> dict:
        if not payload.get("text"):
            return {"error": "text field required"}
        return {"classification": "URGENTE", "confidence": 0.95}
    
    # Valida health endpoint
    health = mock_get_health()
    assert health["status"] == "healthy", \
        f"Health check deve retornar 'healthy', got {health['status']}"
    assert health["uptime_seconds"] > 0, \
        "Uptime deve ser positivo"
    
    # Valida classify endpoint
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
    Validação de inputs estilo Pydantic.
    
    Regras comuns:
    - Campo obrigatório não pode estar vazio
    - Tamanho máximo respeitado
    - Formato válido (email, URL, etc.)
    
    Em produção, usaríamos pydantic.BaseModel com validadores.
    """
    class RequestValidator:
        def __init__(self, text: str, model: str = "gpt-4o-mini"):
            self.text = text
            self.model = model
        
        def validate(self) -> list:
            """
            Retorna lista de erros de validação.
            
            1. Verifica se text está vazio → erro "required"
            2. Verifica se text excede 4000 chars → erro "too_long"
            3. Se nenhum erro → retorna lista vazia
            """
            errors = []
            
            # Regra 1: text é obrigatório
            if not self.text or len(self.text.strip()) == 0:
                errors.append("text field is required")
            # Regra 2: tamanho máximo
            elif len(self.text) > 4000:
                errors.append(f"text too long ({len(self.text)} chars, max 4000)")
            
            return errors
    
    # Texto válido
    valid = RequestValidator(text="Olá, como funciona?")
    assert len(valid.validate()) == 0, \
        "Texto válido não deve gerar erros"
    
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
    Middleware de monitoramento de timing.
    
    Em FastAPI, isso seria um middleware que:
    1. Registra timestamp antes da request
    2. Executa a view
    3. Calcula latência
    4. Adiciona headers de timing na response
    
    Usamos uuid para request tracing.
    """
    import time
    import uuid
    
    def simulate_request(duration_ms: float) -> dict:
        time.sleep(duration_ms / 1000)
        return {"result": "ok"}
    
    def measure_middleware(func, *args) -> dict:
        """
        Mede timing de uma função e retorna métricas.
        
        1. Gera request_id único para tracing
        2. Registra start time
        3. Executa função dentro de try/except
        4. Calcula latência em ms
        5. Retorna métricas padronizadas
        """
        start = time.time()
        request_id = str(uuid.uuid4())[:8]
        
        try:
            result = func(*args)
            latency = (time.time() - start) * 1000
            return {
                "success": True,
                "latency_ms": latency,
                "request_id": request_id,
            }
        except Exception:
            latency = (time.time() - start) * 1000
            return {
                "success": False,
                "latency_ms": latency,
                "request_id": request_id,
            }
    
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
    Validação de configuração Docker básica.
    
    Requisitos mínimos para deploy:
    - Imagem base correta (python:3.12-slim)
    - Portas mapeadas (8000 para API)
    - Variáveis de ambiente necessárias (OPENAI_API_KEY)
    - Healthcheck configurado
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
    
    # Valida configuração
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
    Formatação consistente de respostas de API.
    
    Padrão adotado:
    - Sucesso: {"status": "success", "data": {...}, "meta": {...}}
    - Erro: {"status": "error", "error": "...", "meta": {...}}
    
    Meta inclui metadados comuns (timestamp, version).
    """
    def format_response(success: bool, data=None, error=None) -> dict:
        """
        Formata resposta no padrão consistente.
        
        1. Define status baseado em success boolean
        2. Inclui data ou error conforme caso
        3. Sempre inclui meta com timestamp e version
        """
        response = {
            "status": "success" if success else "error",
            "data": data if success else None,
            "meta": {"timestamp": "now", "version": "1.0"}
        }
        if not success and error:
            response["error"] = error
        return response
    
    success_resp = format_response(True, data={"classification": "ALTA"})
    error_resp = format_response(False, error="Model unavailable")
    
    # Valida formatos
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
