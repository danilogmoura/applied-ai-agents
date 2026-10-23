"""Módulo P3a-2 — SOLUÇÃO COMENTADA

Execute com: python modules/p3a2_tool_calling/exercises.py

Código completo com explicações detalhadas.
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
    Gera o schema JSON no formato OpenAI function calling.
    
    A API OpenAI espera este formato exato para tool calling:
    {
        "type": "function",           # Tipo do recurso
        "function": {                 # Detalhes da função
            "name": "...",            # Nome da ferramenta
            "description": "...",     # O que ela faz
            "parameters": {...}       # Schema JSON dos parâmetros
        }
    }
    """
    def create_tool_schema(name: str, description: str, parameters: dict) -> dict:
        """
        Gera o schema JSON no formato OpenAI function calling.
        
        1. Cria objeto com type="function"
        2. Adiciona campo "function" com name, description, parameters
        3. Retorna o schema completo
        """
        # Monta o objeto no formato esperado pela API OpenAI
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
    Roteamento inteligente: qual ferramenta usar para cada query?
    
    Estratégia: keyword matching com scoring.
    Cada ferramenta tem keywords associadas.
    A query com mais matches vence.
    """
    tools = [
        {"name": "search_web", "keywords": ["pesquisar", "buscar", "encontrar"]},
        {"name": "read_file", "keywords": ["ler", "arquivo", "documento"]},
        {"name": "execute_command", "keywords": ["executar", "rodar", "comando"]},
    ]
    
    def route_query(query: str) -> str:
        """
        Roteia query para a melhor ferramenta baseada em keywords.
        
        1. Converte query para lowercase
        2. Para cada tool, conta quantas keywords aparecem na query
        3. Retorna tool com maior score
        4. Se nenhum match → "unknown"
        """
        query_lower = query.lower()
        best_match = None
        best_score = 0
        
        for tool in tools:
            # Conta quantas keywords da tool aparecem na query
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
    Classifica ferramentas por nível de risco operacional.
    
    - LOW: apenas leitura (seguro)
    - MEDIUM: escrita/modificação (cuidado)
    - HIGH: execução/arquitetura (perigoso)
    """
    def classify_risk(tool_name: str) -> str:
        """
        Classifica ferramenta por nível de risco.
        
        1. Verifica HIGH primeiro (operações perigosas)
        2. Depois MEDIUM (operações moderadas)
        3. Default: LOW (operacões seguras)
        """
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
    Human-In-The-Loop (HITL): operações perigosas precisam aprovação humana.
    
    Regra: HIGH e CRITICAL SEMPRE precisam aprovação.
    MEDIUM e LOW podem executar automaticamente.
    """
    def requires_approval(tool_name: str, risk_level: str) -> bool:
        """
        Verifica se operação precisa aprovação humana.
        
        Regra: HIGH ou CRITICAL → precisa aprovação.
        Caso contrário → pode executar automaticamente.
        """
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
    Execução segura de ferramentas com retry exponencial.
    
    Retry exponencial: espera cada vez mais tempo entre tentativas.
    Ex: 1s → 2s → 4s → 8s...
    
    Isso evita sobrecarregar serviços que estão temporariamente indisponíveis.
    """
    import time
    
    def safe_execute(func: Callable, *args, max_retries: int = 3) -> dict:
        """
        Executa função com retry exponencial.
        
        1. Tenta executar a função
        2. Se falha, espera (backoff exponencial) e tenta novamente
        3. Se todas tentativas falham, retorna erro
        4. Retorna resultado padronizado
        """
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
    
    # Testa com função que falha 2x depois succeed
    call_count = 0
    
    def flaky_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise RuntimeError("Falha temporária")
        return "sucesso"
    
    result = safe_execute(flaky_func, max_retries=3)
    
    assert result["success"] == True, \
        f"Deveria succeed após retries, got {result}"
    assert result["attempts"] == 3, \
        f"Deveria tentar 3 vezes, got {result['attempts']}"
    
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
