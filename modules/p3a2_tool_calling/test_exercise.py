"""
Módulo P3a-2 — Teste do Exercício

Execute com: python modules/p3a2_tool_calling/test_exercise.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Tool Schema — Schema JSON correto?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_tool_schema():
    """
    TODO: Implemente a geração de schema JSON para ferramentas.
    
    OpenAI espera: {"type": "function", "function": {...}}
    """
    def create_tool_schema(name: str, description: str, parameters: dict) -> dict:
        """TODO: Retorne o schema no formato OpenAI function calling."""
        return {}  # ← Implemente
    
    schema = create_tool_schema(
        "read_file",
        "Read the contents of a file",
        {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["file_path"]
        }
    )
    
    assert schema["type"] == "function", "Schema deve ter type='function'"
    assert "function" in schema, "Schema deve ter campo 'function'"
    assert schema["function"]["name"] == "read_file", "Nome deve corresponder"
    
    console.print(f"[green]✓[/green] Schema válido: {schema['function']['name']}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Tool Routing — Agente escolhe ferramenta certa?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_tool_routing():
    """
    TODO: Implemente roteamento de pergunta → ferramenta.
    """
    tools = [
        {"name": "search_web", "keywords": ["pesquisar", "buscar", "encontrar"]},
        {"name": "read_file", "keywords": ["ler", "arquivo", "documento"]},
        {"name": "execute_command", "keywords": ["executar", "rodar", "comando"]},
    ]
    
    def route_query(query: str) -> str:
        """TODO: Retorne o nome da ferramenta mais adequada."""
        query_lower = query.lower()
        for tool in tools:
            if any(kw in query_lower for kw in tool["keywords"]):
                return tool["name"]
        return "unknown"  # ← Substitua pela lógica real
    
    assert route_query("Pesquise sobre IA generativa") == "search_web"
    assert route_query("Leia o arquivo config.json") == "read_file"
    assert route_query("Execute um ping no servidor") == "execute_command"
    
    console.print("[green]✓[/green] Roteamento funciona corretamente!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Risk Level — Classificação de risco correta?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_risk_classification():
    """
    TODO: Classifique ferramentas por nível de risco.
    
    LOW: read_file, search_web
    MEDIUM: write_file, delete_temp
    HIGH: execute_shell, delete_user_data
    """
    def classify_risk(tool_name: str) -> str:
        """TODO: Retorne 'LOW', 'MEDIUM' ou 'HIGH'."""
        return "LOW"  # ← Implemente
    
    assert classify_risk("read_file") == "LOW"
    assert classify_risk("write_file") == "MEDIUM"
    assert classify_risk("execute_shell") == "HIGH"
    
    high_tools = [t for t in ["execute_shell", "delete_user_data", "format_disk"] 
                  if classify_risk(t) == "HIGH"]
    assert len(high_tools) == 3, "Todas as operações perigosas devem ser HIGH"
    
    console.print("[green]✓[/green] Classificação de risco OK")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: HITL Approval — Aprovação humana funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_hitl_approval():
    """
    TODO: Implemente verificação de aprovação humana (Human-In-The-Loop).
    
    Ferramentas HIGH risk SEMPRE precisam aprovação.
    """
    def requires_approval(tool_name: str, risk_level: str) -> bool:
        """TODO: Retorne True se precisa aprovação humana."""
        return False  # ← Implemente
    
    assert requires_approval("execute_shell", "HIGH") == True, \
        "Operações HIGH sempre precisam aprovação"
    assert requires_approval("read_file", "LOW") == False, \
        "Operações LOW não precisam aprovação"
    
    console.print("[green]✓[/green] HITL: HIGH=risk approval required ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Tool Error Handling — Erros são tratados?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_tool_error_handling():
    """
    TODO: Implemente tratamento de erros nas ferramentas.
    """
    def safe_execute(func: Callable, *args, max_retries: int = 3) -> dict:
        """TODO: Execute com retry e retorne {'success': bool, 'result': ..., 'error': ...}."""
        return {"success": False, "result": None, "error": "not implemented"}  # ← Implemente
    
    def good_func():
        return "ok"
    
    def bad_func():
        raise ValueError("Simulated error")
    
    result_good = safe_execute(good_func)
    result_bad = safe_execute(bad_func)
    
    assert result_good["success"] == True, \
        f"Função boa deveria retornar success=True, got {result_good}"
    assert result_bad["success"] == False, \
        f"Função ruim deveria retornar success=False, got {result_bad}"
    assert result_bad["error"] is not None, \
        "Erro deve ser capturado"
    
    console.print(f"[green]✓[/green] Error handling: success={result_good['success']}, "
                  f"error_captured={result_bad['error'] is not None}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_tool_schema, test_02_tool_routing,
             test_03_risk_classification, test_04_hitl_approval,
             test_05_tool_error_handling]
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P3a-2: Tool Calling[/bold cyan]",
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
