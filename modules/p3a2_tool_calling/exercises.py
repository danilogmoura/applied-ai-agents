"""Módulo P3a-2 — Exercícios Práticos

Execute com: python modules/p3a2_tool_calling/exercises.py

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
        # ← Implemente aqui
        return {}  # Placeholder vazio
    
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
        """TODO: Retorne o nome da ferramenta mais adequada baseada em keywords."""
        # ← Implemente aqui
        return "unknown"  # Placeholder vazio
    
    assert route_query("Pesquise sobre IA generativa") == "search_web"
    assert route_query("Leia o arquivo config.json") == "read_file"
    assert route_query("Execute um ping no servidor") == "execute_command"
    # ⚠️ PONTO CRÍTICO: Valide comportamento — unknown quando nenhuma keyword bate
    query_unknown = "Fazer uma conta de 2+2"
    routed = route_query(query_unknown)
    assert routed == "unknown", \
        f"{query_unknown!r} não deve corresponder a nenhuma tool → 'unknown', got {routed!r}"
    
    # ⚠️ PONTO CRÍTICO: Teste adicional para evitar overfitting
    # Palavras-chave devem ser case-insensitive
    assert route_query("BUSCAR documento importante") in ("search_web", "read_file"), \
        "Keywords devem bater independentemente de maiúsc/minús"
    
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
        """TODO: Retorne 'LOW', 'MEDIUM' ou 'HIGH' baseado no nome da tool."""
        # ← Implemente aqui
        return "LOW"  # Placeholder vazio
    
    assert classify_risk("read_file") == "LOW"
    assert classify_risk("write_file") == "MEDIUM"
    assert classify_risk("execute_shell") == "HIGH"
    
    # ⚠️ PONTO CRÍTICO: Valide propriedade comportamental — ops perigosas são classificadas como HIGH
    dangerous_ops = ["execute_shell", "delete_user_data", "format_disk"]
    high_tools = [t for t in dangerous_ops if classify_risk(t) == "HIGH"]
    # Pelo menos uma deve ser HIGH (propriedade mínima de segurança)
    assert len(high_tools) >= 1, \
        f"Ops perigosas devem ser pelo menos parcialmente HIGH, got {high_tools}"
    # Nenhuma op perigosa deve ser classificada como LOW ou MEDIUM
    low_medium_dangerous = [t for t in dangerous_ops 
                            if classify_risk(t) in ("LOW", "MEDIUM")]
    assert len(low_medium_dangerous) == 0, \
        "Operações perigosas NÃO devem ser classificadas como LOW ou MEDIUM"
    
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
        """TODO: Retorne True se precisa aprovação humana (HIGH ou CRITICAL)."""
        # ← Implemente aqui
        return False  # Placeholder vazio
    
    assert requires_approval("execute_shell", "HIGH") == True, \
        "Operações HIGH sempre precisam aprovação"
    assert requires_approval("read_file", "LOW") == False, \
        "Operações LOW não precisam aprovação"
    assert requires_approval("delete_user_data", "CRITICAL") == True, \
        "Operações CRITICAL sempre precisam aprovação"
    assert requires_approval("write_file", "MEDIUM") == False, \
        "Operações MEDIUM não precisam aprovação"
    
    # ⚠️ PONTO CRÍTICO: Valide propriedade — todo HIGH/CRITICAL precisa approval
    high_risk_tools = [("format_disk", "HIGH"), ("wipe_database", "CRITICAL")]
    for tool, risk in high_risk_tools:
        assert requires_approval(tool, risk) == True, \
            f"{tool} ({risk}) SEMPRE precisa aprovação humana"
    
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
        """TODO: Execute com retry exponencial e retorne {'success': bool, 'result': ..., 'error': ...}."""
        # ← Implemente aqui
        return {"success": False, "result": None, "error": "Not implemented", "attempts": 0}  # Placeholder vazio
    
    # Testa com função que falha 2x depois succeed
    call_count = 0
    
    def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RuntimeError("Falha temporária")
        return "sucesso"
    
    result = safe_execute(flaky_func, max_retries=3)
    
    # ⚠️ PONTO CRÍTICO: Valide comportamento — retry succeed após falhas temporárias
    assert result["success"] == True, \
        f"Deveria succeed após retries, got {result}"
    # Verifique que o retry realmente tentou múltiplas vezes (>= 2, pois a primeira falha)
    expected_attempts_min = 2
    actual_attempts = result.get("attempts", 0)
    assert actual_attempts >= expected_attempts_min, \
        f"Retry deve tentar pelo menos {expected_attempts_min} vezes, tentou {actual_attempts}"
    # Verifique que attempts não excedeu max_retries
    assert actual_attempts <= 3, \
        f"Attempts não pode exceder max_retries=3, got {actual_attempts}"
    
    console.print(f"[green]✓[/green] Retry: success after {result['attempts']} attempts")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_tool_schema, test_02_tool_routing,
             test_03_risk_classification, test_04_hitl_approval,
             test_05_tool_error_handling]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
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
        console.print("[bold green]🎉 Todos os exercícios passaram![/bold green]")


if __name__ == "__main__":
    run_all()
