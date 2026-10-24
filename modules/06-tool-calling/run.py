"""
Módulo 06 — Tool Calling (Uso Autônomo de Ferramentas)

Agente Python capaz de executar funções reais: consultar APIs, ler arquivos,
executar comandos. Implementação do princípio do menor privilégio e travas
de aprovação humana no console.

Problema: O agente precisa ir além de gerar texto — ele precisa INTERAGIR
com o mundo real: ler dados, chamar APIs, modificar estados. Como fazer isso
com segurança?
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from shared.logging_config import setup_logging
from shared.cost import count_tokens, estimate_cost, format_cost
from shared.governance import ActionRequest, RiskLevel, require_approval, safe_execute
from shared.security import get_llm_config, get_model, get_provider, get_thinking

console = Console()
logger = setup_logging("06-tool-calling")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DEFINIÇÃO DE FERRAMENTAS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Tool:
    """
    Definição de uma ferramenta que o agente pode usar.
    
    Cada tool tem: nome, descrição, parâmetros (JSON Schema),
    função executadora e nível de risco.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        func: Callable,
        risk_level: RiskLevel = RiskLevel.LOW,
    ):
        self.name = name
        self.description = description
        self.parameters = parameters
        self.func = func
        self.risk_level = risk_level
    
    def to_schema(self) -> dict:
        """Converte para schema OpenAI function calling."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FERRAMENTAS REAIS DO AGENTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def read_file_tool(file_path: str, max_lines: int = 100) -> str:
    """Lê as primeiras linhas de um arquivo."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"ERRO: Arquivo não encontrado: {file_path}"
        
        lines = path.read_text().split("\n")[:max_lines]
        content = "\n".join(lines)
        
        if len(path.read_text().split("\n")) > max_lines:
            content += f"\n\n... (arquivo truncado em {max_lines} linhas)"
        
        return content
    except Exception as e:
        return f"ERRO ao ler arquivo: {e}"


def list_directory_tool(path: str = ".") -> str:
    """Lista conteúdo de um diretório."""
    try:
        dir_path = Path(path)
        if not dir_path.is_dir():
            return f"ERRO: Diretório não encontrado: {path}"
        
        items = []
        for item in dir_path.iterdir():
            prefix = "📁" if item.is_dir() else "📄"
            items.append(f"{prefix} {item.name}")
        
        return "\n".join(items) if items else "(vazio)"
    except Exception as e:
        return f"ERRO: {e}"


def search_files_tool(pattern: str, path: str = ".") -> str:
    """Busca arquivos por padrão no nome."""
    try:
        matches = list(Path(path).rglob(pattern))
        if not matches:
            return f"Nenhum arquivo encontrado com padrão '{pattern}'"
        
        return "\n".join(str(m) for m in matches[:20])
    except Exception as e:
        return f"ERRO: {e}"


def execute_command_tool(command: str, timeout: int = 30) -> str:
    """
    Executa comando shell (COM RESTRIÇÕES DE SEGURANÇA).
    
    Em produção, use whitelist de comandos permitidos.
    """
    import subprocess
    
    # Whitelist básica de comandos seguros
    SAFE_COMMANDS = ["ls", "cat", "echo", "date", "whoami", "pwd", "head", "tail", "wc"]
    cmd_base = command.split()[0] if command.split() else ""
    
    if cmd_base not in SAFE_COMMANDS:
        return f"ERRO: Comando '{cmd_base}' não está na whitelist de seguros."
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        output = result.stdout or result.stderr
        return output[:2000]  # Limita tamanho da resposta
    except subprocess.TimeoutExpired:
        return "ERRO: Comando expirou (timeout)"
    except Exception as e:
        return f"ERRO: {e}"


def calculate_tool(expression: str) -> str:
    """Executa cálculo matemático seguro."""
    import re
    
    # Bloqueia operações perigosas
    if re.search(r'[a-z_]|__|import|eval|exec|open|lambda', expression, re.IGNORECASE):
        return "ERRO: Expressão contém caracteres não permitidos."
    
    try:
        # Apenas operadores matemáticos básicos
        allowed = set("0123456789+-*/().% ")
        if not all(c in allowed for c in expression):
            return "ERRO: Caracteres não permitidos na expressão."
        
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Resultado: {result}"
    except Exception as e:
        return f"ERRO no cálculo: {e}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENTE COM TOOL CALLING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ToolCallingAgent:
    """
    Agente que recebe ferramentas e decide quando/usá-las.
    
    Fluxo:
    1. Usuário faz pergunta
    2. LLM decide se usa ferramenta ou responde direto
    3. Se usar → executa ferramenta com governança (HITL)
    4. Usa resultado → gera resposta final
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.tools: list[Tool] = []
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.conversation_history: list[dict] = []
    
    def register_tool(self, tool: Tool) -> None:
        """Registra uma ferramenta disponível para o agente."""
        self.tools.append(tool)
        logger.info(f"Tool registered: {tool.name} (risk={tool.risk_level.value})")
    
    def get_tools_schema(self) -> list[dict]:
        """Retorna schemas de todas ferramentas."""
        return [t.to_schema() for t in self.tools]
    
    def _call_llm(
        self,
        messages: list[dict],
        tools: Optional[list[dict]] = None,
    ) -> dict:
        """Chamada real à API OpenAI."""
        from openai import OpenAI
        
        api_key, base_url, _ = get_llm_config()
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        kwargs: dict = {
            "model": self.model,
            "extra_body": get_thinking(self.model),
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.3,
        }
        
        if tools:
            kwargs["tools"] = tools
        
        response = client.chat.completions.create(**kwargs)
        
        choice = response.choices[0]
        messages_str = json.dumps(messages, ensure_ascii=False)
        input_tok = count_tokens(messages_str, self.model)
        output_tok = count_tokens(choice.message.content or "", self.model)
        
        self.total_input_tokens += input_tok
        self.total_output_tokens += output_tok
        
        return {
            "message": choice.message,
            "finish_reason": choice.finish_reason,
        }
    
    def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """
        Executa ferramenta com governança.
        
        Ferramentas de alto risco exigem aprovação humana.
        """
        tool = next((t for t in self.tools if t.name == tool_name), None)
        
        if not tool:
            return f"ERRO: Ferramenta '{tool_name}' não encontrada."
        
        # Verifica se precisa de aprovação humana
        if tool.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            action = ActionRequest(
                operation=f"executar_ferramenta:{tool_name}",
                target=str(arguments),
                reason=f"Agente solicitou execução de {tool_name}",
                risk_level=tool.risk_level,
            )
            
            if not require_approval(action):
                return f"ERRO: Execução de '{tool_name}' recusada pelo usuário."
        
        # Executa a função
        try:
            result = tool.func(**arguments)
            logger.info(f"Tool executed: {tool_name} → {len(str(result))} chars")
            return result
        except Exception as e:
            error_msg = f"ERRO na ferramenta {tool_name}: {e}"
            logger.error(error_msg)
            return error_msg
    
    def chat(self, user_message: str) -> str:
        """
        Ciclo completo: recebe mensagem → decide → executa → responde.
        
        Args:
            user_message: Mensagem do usuário.
        
        Returns:
            Resposta final do agente.
        """
        # Adiciona mensagem do usuário ao histórico
        self.conversation_history.append({"role": "user", "content": user_message})
        
        messages = [
            {
                "role": "system",
                "content": (
                    "Você é um assistente com acesso a ferramentas. "
                    "Se precisar usar uma ferramenta, indique com tool_calls. "
                    "Sempre seja preciso e cite fontes."
                ),
            },
            *self.conversation_history,
        ]
        
        # Primeira chamada: decide se usa ferramenta
        console.print(f"\n[bold cyan]🤖 Agente:[/]\n")
        
        llm_response = self._call_llm(messages, tools=self.get_tools_schema())
        
        # Verifica se o LLM quer usar ferramenta
        if llm_response.message.tool_calls:
            tool_results = []
            
            for tool_call in llm_response.message.tool_calls:
                func = tool_call.function
                tool_name = func.name
                
                # Parse argumentos JSON
                try:
                    args = json.loads(func.arguments)
                except json.JSONDecodeError:
                    args = {}
                
                console.print(f"  [yellow]⚙️ Usando ferramenta:[/] {tool_name}({args})")
                
                # Executa com governança
                result = self._execute_tool(tool_name, args)
                tool_results.append({
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "result": result,
                })
                
                console.print(f"  [green]✓ Resultado:[/] {result[:200]}")
            
            # Segunda chamada: gera resposta com resultados das ferramentas
            messages.append(llm_response.message)
            
            for tr in tool_results:
                messages.append({
                    "role": "tool",
                    "tool_call_id": tr["tool_call_id"],
                    "content": tr["result"],
                })
            
            final_response = self._call_llm(messages)
            answer = final_response.message.content or "Não consegui processar."
        else:
            # Responde sem usar ferramentas
            answer = llm_response.message.content or "Não tenho resposta para isso."
        
        # Atualiza histórico
        self.conversation_history.append(llm_response.message.model_dump() if hasattr(llm_response.message, 'model_dump') else {"role": "assistant", "content": answer})
        
        # Exibe resposta final
        console.print(f"  [bold green]💬 Resposta:[/]\n{answer}\n")
        
        # Log de custo
        cost = estimate_cost(self.total_input_tokens, self.total_output_tokens, self.model)
        console.print(f"[dim]Tokens: {self.total_input_tokens} input + {self.total_output_tokens} output | "
                      f"Custo: {format_cost(cost)}[/]")
        
        return answer
    
    def reset(self) -> None:
        """Limpa histórico de conversa."""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa demonstração do agente com tool calling."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO 06 — Tool Calling[/]\n\n"
        "Agente com ferramentas reais + governança HITL.\n"
        "Princípio do menor privilégio.",
        title="🛠️ AI Agents Course",
        border_style="cyan",
    ))
    
    # Valida ambiente
    try:
        get_llm_config()
        console.print(f"[green]✓ Ambiente validado ({get_provider()})[/]")
    except EnvironmentError as e:
        console.print(f"[red]✗ {e}[/]")
        sys.exit(1)
    
    model = get_model()
    
    # Cria agente
    agent = ToolCallingAgent(model=model)
    
    # Registra ferramentas
    agent.register_tool(Tool(
        name="read_file",
        description="Lê as primeiras 100 linhas de um arquivo",
        parameters={
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Caminho do arquivo"},
                "max_lines": {"type": "integer", "description": "Máximo de linhas", "default": 100},
            },
            "required": ["file_path"],
        },
        func=read_file_tool,
        risk_level=RiskLevel.MEDIUM,
    ))
    
    agent.register_tool(Tool(
        name="list_directory",
        description="Lista arquivos e pastas de um diretório",
        parameters={
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Caminho do diretório", "default": "."},
            },
        },
        func=list_directory_tool,
        risk_level=RiskLevel.LOW,
    ))
    
    agent.register_tool(Tool(
        name="search_files",
        description="Busca arquivos por padrão no nome",
        parameters={
            "type": "object",
            "properties": {
                "pattern": {"type": "string", "description": "Padrão de busca (glob)"},
                "path": {"type": "string", "description": "Diretório base", "default": "."},
            },
            "required": ["pattern"],
        },
        func=search_files_tool,
        risk_level=RiskLevel.LOW,
    ))
    
    agent.register_tool(Tool(
        name="calculate",
        description="Executa cálculo matemático seguro",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string", "description": "Expressão matemática (ex: '2+2*3')"},
            },
            "required": ["expression"],
        },
        func=calculate_tool,
        risk_level=RiskLevel.LOW,
    ))
    
    # Exibe ferramentas disponíveis
    table = Table(title="🔧 Ferramentas Registradas")
    table.add_column("Ferramenta")
    table.add_column("Descrição")
    table.add_column("Risco")
    
    for tool in agent.tools:
        table.add_row(
            tool.name,
            tool.description,
            tool.risk_level.value.upper(),
        )
    
    console.print(table)
    
    # Testes interativos
    test_queries = [
        "Quantos arquivos .py existem neste módulo?",
        "Leia o README.md e resuma o projeto",
        "Calcule quanto custariam 1 milhão de chamadas gpt-4o-mini com 500 tokens cada",
    ]
    
    console.print("\n[bold blue]▸ Executando queries de teste...\n[/]")
    
    for query in test_queries:
        console.print(f"[bold magenta]👤 Usuário:[/] {query}")
        agent.chat(query)
        console.print("-" * 60)
    
    console.print("\n[dim]💡 Próximo passo: Módulo 07 — Planejamento e Retomada[/]")


if __name__ == "__main__":
    main()
