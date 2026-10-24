"""
Módulo P3b — Sistema Multiagente

Arquitetura onde um agente supervisor (router) delega tarefas para
agentes especialistas, garantindo degradação elegante.

Problema: Uma única IA não consegue fazer tudo bem. Como coordenar
vários agentes especializados mantendo a resiliência?
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from shared.logging_config import setup_logging
from shared.cost import count_tokens, estimate_cost, format_cost

console = Console()
logger = setup_logging("08-multiagente")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENTE ESPECIALISTA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Agent:
    """
    Agente especialista com identidade própria.
    
    Cada agente tem um domínio específico e pode falhar independentemente.
    """
    
    def __init__(self, name: str, role: str, model: str = "gpt-4o-mini"):
        self.name = name
        self.role = role
        self.model = model
        self.tokens_used = 0
        self.cost_accumulated = 0.0
        self.call_count = 0
        self.failure_rate = 0.0  # Taxe simulada de falha
    
    def execute(self, task: str) -> str:
        """
        Executa tarefa dentro do domínio do especialista.
        
        Em produção, chama LLM real. Aqui simula resposta.
        """
        self.call_count += 1
        
        # Simula falha ocasional
        import random
        if random.random() < self.failure_rate:
            raise ConnectionError(f"Agente '{self.name}' indisponível")
        
        # Gera resposta baseada no papel
        responses = {
            "análise de dados": f"[DADOS] Analisando: '{task[:50]}...' → Padrões identificados: tendência positiva, correlação forte detectada.",
            "pesquisa web": f"[PESQUISA] Buscando: '{task[:50]}...' → Encontrados 3 fontes relevantes com consenso sobre o tema.",
            "tradução": f"[TRADUÇÃO] Traduzindo: '{task[:50]}...' → Texto traduzido com preservação de tom técnico.",
            "geração de código": f"[CÓDIGO] Gerando: '{task[:50]}...' → Função Python criada com tipagem e docstring.",
            "resumo": f"[RESUMO] Resumindo: '{task[:50]}...' → Pontos-chave extraídos em 3 parágrafos concisos.",
        }
        
        response = "Resposta gerada com sucesso."
        for key, resp in responses.items():
            if key in self.role.lower():
                response = resp
                break
        
        # Calcula custos aproximados
        input_tok = len(task.encode()) // 4
        output_tok = len(response.encode()) // 4
        cost = estimate_cost(input_tok, output_tok, self.model)
        
        self.tokens_used += input_tok + output_tok
        self.cost_accumulated += cost
        
        return response
    
    def get_status(self) -> dict:
        """Retorna status do agente."""
        return {
            "name": self.name,
            "role": self.role,
            "calls": self.call_count,
            "tokens": self.tokens_used,
            "cost": format_cost(self.cost_accumulated),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENTE SUPERVISOR (ROUTER)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SupervisorAgent:
    """
    Agente supervisor que roteia tarefas para especialistas.
    
    Usa LLM para decidir qual especialista chamar. Se um especialista
    falha, tenta fallback ou redistribui.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.specialists: list[Agent] = []
        self.total_cost = 0.0
        self.routing_log: list[dict] = []
    
    def add_specialist(self, agent: Agent) -> None:
        """Registra um especialista no time."""
        self.specialists.append(agent)
        logger.info(f"Specialist registered: {agent.name} ({agent.role})")
    
    def _route_with_llm(self, task: str) -> Optional[Agent]:
        """
        Usa LLM para decidir qual especialista é mais adequado.
        
        Em produção, chama OpenAI com prompt de roteamento.
        Aqui usa lógica heurística como demonstração.
        """
        task_lower = task.lower()
        
        # Heurísticas simples de roteamento
        keywords = {
            "dados": ["análise_de_dados", "engenharia_dados"],
            "pesquisar|buscar|consulta": ["pesquisa_web"],
            "tradu": ["tradução"],
            "código|programa|função|script": ["geração_de_código"],
            "resumo|resume|sintese": ["resumo"],
        }
        
        for pattern, specialist_names in keywords.items():
            import re
            if re.search(pattern, task_lower):
                for spec in self.specialists:
                    if any(sn in spec.name.lower() for sn in specialist_names):
                        return spec
        
        # Fallback: primeiro especialista disponível
        return self.specialists[0] if self.specialists else None
    
    def execute_task(self, task: str, max_retries: int = 2) -> dict:
        """
        Executa tarefa roteando para especialista com retry.
        
        Args:
            task: Tarefa a executar.
            max_retries: Tentativas em caso de falha.
        
        Returns:
            Resultado com metadados de roteamento.
        """
        console.print(f"\n[bold cyan]👤 Supervisor recebe:[/] {task}")
        
        # Roteia para especialista
        specialist = self._route_with_llm(task)
        
        if not specialist:
            return {
                "task": task,
                "status": "error",
                "message": "Nenhum especialista disponível",
            }
        
        console.print(f"  [yellow]→ Roteado para:[/] {specialist.name} ({specialist.role})")
        
        # Executa com retry
        result = None
        errors = []
        
        for attempt in range(max_retries + 1):
            try:
                result = specialist.execute(task)
                
                self.routing_log.append({
                    "task": task,
                    "specialist": specialist.name,
                    "attempt": attempt + 1,
                    "status": "success",
                })
                
                break
                
            except Exception as e:
                error_msg = f"Falha na tentativa {attempt + 1}: {e}"
                errors.append(error_msg)
                console.print(f"  [red]✗ {error_msg}[/]")
                
                if attempt < max_retries:
                    # Tenta outro especialista
                    remaining = [s for s in self.specialists if s.name != specialist.name]
                    if remaining:
                        specialist = remaining[0]
                        console.print(f"  [yellow]↻ Tentando especialista alternativo:[/] {specialist.name}")
                    else:
                        console.print(f"  [red]✗ Sem alternativos disponíveis[/]")
        
        if result is None:
            result = f"Falha após {max_retries + 1} tentativas. Erros: {'; '.join(errors)}"
            status = "failed"
        else:
            status = "success"
        
        # Calcula custo
        cost = estimate_cost(
            len(task.encode()) // 4,
            len(str(result).encode()) // 4,
            self.model,
        )
        self.total_cost += cost
        
        return {
            "task": task,
            "specialist": specialist.name,
            "result": result,
            "status": status,
            "attempts": len(errors) + (1 if result else 0),
            "cost": cost,
        }
    
    def get_team_status(self) -> Table:
        """Retorna tabela de status da equipe."""
        table = Table(title="👥 Status da Equipe de Agentes")
        table.add_column("Agente")
        table.add_column("Papel")
        table.add_column("Chamadas")
        table.add_column("Tokens")
        table.add_column("Custo")
        
        for spec in self.specialists:
            status = spec.get_status()
            table.add_row(
                status["name"],
                status["role"],
                str(status["calls"]),
                str(status["tokens"]),
                status["cost"],
            )
        
        return table


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa demonstração do sistema multiagente."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO P3b — Sistema Multiagente[/]\n\n"
        "Supervisor + Especialistas com degradação elegante.\n"
        "Roteamento inteligente + fallback automático.",
        title="🤖 AI Agents Course",
        border_style="cyan",
    ))
    
    # Valida ambiente
    try:
        from shared.security import validate_secrets
        validate_secrets(["OPENAI_API_KEY"])
        console.print("[green]✓ Ambiente validado[/]")
    except EnvironmentError as e:
        console.print(f"[red]✗ {e}[/]")
        sys.exit(1)
    
    model = __import__("shared.security").security.get_model()
    
    # Cria supervisor
    supervisor = SupervisorAgent(model=model)
    
    # Registra especialistas
    supervisor.add_specialist(Agent(
        name="analista_dados",
        role="análise de dados e métricas",
        model=model,
    ))
    
    supervisor.add_specialist(Agent(
        name="pesquisador",
        role="pesquisa web e consulta fontes",
        model=model,
    ))
    
    supervisor.add_specialist(Agent(
        name="dev_python",
        role="geração de código Python",
        model=model,
    ))
    
    supervisor.add_specialist(Agent(
        name="redator",
        role="resumo e síntese de conteúdo",
        model=model,
    ))
    
    # Exibe equipe
    console.print(supervisor.get_team_status())
    
    # Tarefas de teste
    tasks = [
        "Analise os dados de vendas do último trimestre e identifique tendências",
        "Pesquise as últimas novidades sobre inteligência artificial generativa",
        "Gere uma função Python que calcula média móvel de uma lista",
        "Resuma os pontos principais deste curso de agentes de IA",
        "Traduza este texto técnico para inglês",
    ]
    
    console.print("\n[bold blue]▸ Executando tarefas...\n[/]")
    
    results = []
    for task in tasks:
        result = supervisor.execute_task(task)
        results.append(result)
        
        status_icon = "✅" if result["status"] == "success" else "❌"
        console.print(f"\n{status_icon} [{result['specialist']}] {result['result'][:100]}...")
        console.print(f"   Custos: {format_cost(result['cost'])} | Tentativas: {result['attempts']}")
    
    # Relatório final
    console.print("\n" + "=" * 60)
    console.print("[bold green]📊 Relatório Final[/]")
    console.print("=" * 60)
    console.print(f"Tarefas executadas: {len(results)}")
    success = sum(1 for r in results if r["status"] == "success")
    console.print(f"Sucedidas: {success}/{len(results)}")
    console.print(f"Custo total: {format_cost(supervisor.total_cost)}")
    console.print(f"Tokens totais: {sum(s.tokens_used for s in supervisor.specialists)}")
    console.print("=" * 60)
    
    console.print(supervisor.get_team_status())
    
    console.print("\n[dim]💡 Próximo passo: Módulo P4 — Produto em Produção[/]")


if __name__ == "__main__":
    main()
