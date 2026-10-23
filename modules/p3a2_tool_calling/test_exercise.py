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
        """Retorne o schema no formato OpenAI function calling."""
        return {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }
    
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
    assert schema["function"]["description"] == "Read the contents of a file", \
        "Description deve corresponder"
    assert "parameters" in schema["function"], "Schema deve ter parameters"
    
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
        """Retorne o nome da ferramenta mais adequada baseada em keywords."""
        query_lower = query.lower()
        best_match = None
        best_score = 0
        
        for tool in tools:
            score = sum(1 for kw in tool["keywords"] if kw in query_lower)
            if score > best_score:
                best_score = score
                best_match = tool["name"]
        
        return best_match if best_score > 0 else "unknown"
    
    assert route_query("Pesquise sobre IA generativa") == "search_web"
    assert route_query("Leia o arquivo config.json") == "read_file"
    assert route_query("Execute um ping no servidor") == "execute_command"
    assert route_query("Fazer uma conta de 2+2") == "unknown", \
        "Deve retornar unknown quando nenhuma tool corresponde"
    
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
        """Retorne 'LOW', 'MEDIUM' ou 'HIGH' baseado no nome da tool."""
        low_tools = ["read_file", "search_web", "list_directory", "calculate"]
        medium_tools = ["write_file", "delete_temp", "send_email_draft"]
        high_tools = ["execute_shell", "delete_user_data", "format_disk", "execute_command"]
        
        if tool_name in high_tools:
            return "HIGH"
        elif tool_name in medium_tools:
            return "MEDIUM"
        elif tool_name in low_tools:
            return "LOW"
        else:
            return "LOW"  # Default seguro
    
    assert classify_risk("read_file") == "LOW"
    assert classify_risk("write_file") == "MEDIUM"
    assert classify_risk("execute_shell") == "HIGH"
    
    high_tools = [t for t in ["execute_shell", "delete_user_data", "format_disk"] 
                  if classify_risk(t) == "HIGH"]
    assert len(high_tools) == 3, f"Todas as operações perigosas devem ser HIGH, got {high_tools}"
    
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
        """Retorne True se precisa aprovação humana (HIGH ou CRITICAL)."""
        return risk_level in ("HIGH", "CRITICAL")
    
    assert requires_approval("execute_shell", "HIGH") == True, \
        "Operações HIGH sempre precisam aprovação"
    assert requires_approval("read_file", "LOW") == False, \
        "Operações LOW não precisam aprovação"
    assert requires_approval("delete_user_data", "CRITICAL") == True, \
        "Operações CRITICAL sempre precisam aprovação"
    assert requires_approval("write_file", "MEDIUM") == False, \
        "Operações MEDIUM não precisam aprovação"
    
    console.print("[green]✓[/green] HITL: HIGH=risk approval required ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Tool Error Handling — Erros são tratados?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_tool_error_handling():
    """
    TODO: Implemente tratamento de erros nas ferramentas com retry.
    """
    import time
    
    def safe_execute(func: Callable, *args, max_retries: int = 3) -> dict:
        """Execute com retry exponencial e retorne {'success': bool, 'result': ..., 'error': ...}."""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                result = func(*args)
                return {
                    "success": True,
                    "result": result,
                    "error": None,
                    "attempts": attempt + 1,
                }
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    wait_time = min(2 ** attempt, 1)  # Backoff exponencial capado
                    time.sleep(wait_time)
        
        return {
            "success": False,
            "result": None,
            "error": str(last_error),
            "attempts": max_retries,
        }
    
    def good_func():
        return "ok"
    
    def bad_func():
        raise ValueError("Simulated error")
    
    result_good = safe_execute(good_func)
    result_bad = safe_execute(bad_func)
    
    assert result_good["success"] == True, \
        f"Função boa deveria retornar success=True, got {result_good}"
    assert result_good["result"] == "ok", "Resultado deve ser 'ok'"
    assert result_bad["success"] == False, \
        f"Função ruim deveria retornar success=False, got {result_bad}"
    assert result_bad["error"] is not None, "Erro deve ser capturado"
    assert result_bad["attempts"] == max_retries, \
        f"Deveria tentar {max_retries} vezes, got {result_bad['attempts']}"
    
    console.print(f"[green]✓[/green] Error handling: success={result_good['success']}, "
                  f"error_captured={result_bad['error'] is not None}, "
                  f"retries={result_bad['attempts']}")


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
