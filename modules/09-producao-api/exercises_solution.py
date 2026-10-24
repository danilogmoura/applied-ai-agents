"""Módulo 09 — SOLUÇÃO COMENTADA

Execute com: python modules/09-producao-api/exercises.py

Código completo com explicações detalhadas.
"""

from __future__ import annotations

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SOLUÇÕES COMENTADAS — Funções implementadas com explicações
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def measure_middleware(func, *args) -> dict:
    """
    Mede timing de uma função e retorna métricas.
    
    Em FastAPI, isso seria um middleware que:
    1. Registra timestamp antes da request
    2. Executa a view
    3. Calcula latência
    4. Adiciona headers de timing na response
    
    Usamos uuid para request tracing.
    """
    # ⚠️ PONTO CRÍTICO: Gera request_id único para tracing/distribuição
    request_id = str(uuid.uuid4())[:8]
    
    # ⚠️ PONTO CRÍTICO: Registra tempo ANTES da execução (baseline)
    start = time.time()
    
    try:
        # Executa função com args passados
        result = func(*args)
        # ⚠️ PONTO CRÍTICO: Tempo DEPOIS — subtração dá delta em segundos
        latency = (time.time() - start) * 1000  # converte para ms
        return {
            "success": True,
            "latency_ms": latency,
            "request_id": request_id,
        }
    except Exception:
        # Mesmo em falha, medimos o tempo até o erro
        latency = (time.time() - start) * 1000
        return {
            "success": False,
            "latency_ms": latency,
            "request_id": request_id,
        }


import uuid


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
    Middleware de monitoramento de timing.
    
    Cenário: API TechCorp com SLA de latência.
    Requisitos:
      - Latência p95 < 200ms
      - Taxa de erro < 1%
      - Rate limiting: 100 req/min por cliente
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
    Validação de configuração Docker básica.
    
    Cenário: Deploy da API TechCorp no Kubernetes.
    Requisitos mínimos:
      - Imagem base: python:3.12-slim (menor superfície de ataque)
      - Porta exposta: 8000 (FastAPI default)
      - Variáveis obrigatórias: OPENAI_API_KEY
      - Healthcheck configurado (monitoramento contínuo)
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
    
    Cenário: API TechCorp com contrato de interface definido.
    Padrão adotado:
      - Sucesso: {"status": "success", "data": {...}, "meta": {...}}
      - Erro: {"status": "error", "error": "...", "meta": {...}}
    
    Meta inclui metadados comuns (timestamp, version).
    Consistência facilita parsing pelo cliente frontend.
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
                        title="[bold cyan]Módulo 09 — Produção (FastAPI + Docker)[/bold cyan]",
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
