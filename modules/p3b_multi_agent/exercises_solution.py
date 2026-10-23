"""Módulo P3b — SOLUÇÃO COMENTADA

Execute com: python modules/p3b_multi_agent/exercises.py

Código completo com explicações detalhadas.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Supervisor Routing — Roteamento correto?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_supervisor_routing():
    """
    Supervisor routing: agente supervisor encaminha tarefas para especialistas.
    
    Estratégia: keyword matching com scoring.
    Cada especialista tem keywords associadas.
    A tarefa é roteada para o especialista com mais matches.
    Se nenhum match → generalist (agente genérico).
    """
    specialists = [
        {"name": "engineer", "keywords": ["bug", "erro", "crash", "falha"]},
        {"name": "billing", "keywords": ["preço", "cobrança", "fatura", "pagamento"]},
        {"name": "support", "keywords": ["como", "tutorial", "guia", "instrução"]},
    ]
    
    def route_to_specialist(task: str) -> str:
        """
        Roteia tarefa para o especialista mais adequado.
        
        1. Converte task para lowercase
        2. Para cada especialista, conta quantas keywords aparecem
        3. Retorna especialista com maior score
        4. Se nenhum match → "generalist"
        """
        task_lower = task.lower()
        best_match = None
        best_score = 0
        
        for spec in specialists:
            # Conta quantas keywords do especialista estão na task
            score = sum(1 for kw in spec["keywords"] if kw in task_lower)
            if score > best_score:
                best_score = score
                best_match = spec["name"]
        
        return best_match if best_score > 0 else "generalist"
    
    assert route_to_specialist("Sistema caiu com erro 500") == "engineer"
    assert route_to_specialist("Quero saber o preço do plano") == "billing"
    assert route_to_specialist("Como configuro minha conta?") == "support"
    assert route_to_specialist("Olá") == "generalist"
    
    console.print("[green]✓[/green] Supervisor roteia corretamente!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Specialist Failure — Fallback quando falha?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_specialist_failure():
    """
    Fallback em sistemas multiagente: quando um especialista falha,
    redistribui a tarefa para outro especialista disponível.
    
    Estratégia: tenta especialistas em ordem circular até encontrar
    um que funcione. Mantém registro dos já tentados para evitar loop.
    """
    specialists = ["engineer", "billing", "support", "generalist"]
    
    def execute_task(specialist: str, task: str) -> str:
        """Simula execução — engineer SEMPRE falha neste teste."""
        if specialist == "engineer":
            raise RuntimeError("Engineer indisponível")
        return f"{specialist} resolved: {task}"
    
    # Implementa fallback para outro especialista
    task = "Sistema caiu"
    result = None
    used_fallback = False
    tried = set()
    
    assigned = "engineer"
    try:
        result = execute_task(assigned, task)
    except Exception:
        used_fallback = True
        tried.add(assigned)
        # Tenta próximo especialista disponível até encontrar um que funcione
        idx = specialists.index(assigned)
        for i in range(1, len(specialists)):
            fallback = specialists[(idx + i) % len(specialists)]
            if fallback not in tried:
                try:
                    result = execute_task(fallback, task)
                    break
                except Exception:
                    tried.add(fallback)
    
    assert used_fallback == True, "Fallback deveria ter sido acionado"
    assert result is not None and "resolved" in result, \
        f"Fallback deveria retornar resultado válido, got {result}"
    
    console.print(f"[green]✓[/green] Fallback: engineer→{used_fallback}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Agent Coordination — Agentes coordenam bem?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_agent_coordination():
    """
    Coordenação entre agentes via compartilhamento de contexto.
    
    Em sistemas multiagente, agentes precisam compartilhar informações
    para trabalhar juntos efetivamente. Aqui implementamos um sistema
    simples de broadcast de contexto.
    """
    class Agent:
        def __init__(self, name: str):
            self.name = name
            self.context: Dict[str, Any] = {}
        
        def share_context(self, other: 'Agent'):
            """
            Compartilha todo o contexto deste agente com outro.
            
            1. Itera sobre todos os pares key-value deste agente
            2. Chama receive_context no outro agente passando os dados
            3. O outro agente prefixa as chaves com o nome do remetente
               para evitar colisão de namespaces
            """
            for key, value in self.context.items():
                other.receive_context(self.name, {key: value})
        
        def receive_context(self, other_name: str, context: dict):
            """
            Recebe contexto de outro agente.
            
            Prefixa as chaves com o nome do remetente para evitar
            colisões (ex: researcher_findings vs writer_findings).
            """
            for key, value in context.items():
                self.context[f"{other_name}_{key}"] = value
    
    agent_a = Agent("researcher")
    agent_b = Agent("writer")
    
    agent_a.context = {"findings": "IA generativa cresce 40% ao mês"}
    
    # Compartilha contexto
    agent_a.share_context(agent_b)
    
    assert "findings" in agent_b.context, \
        "Agente B deveria receber contexto de A"
    assert agent_b.context["findings"] == "IA generativa cresce 40% ao mês", \
        "Contexto compartilhado deve ser preservado"
    
    console.print("[green]✓[/green] Coordenação: contexto compartilhado ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Multi-Agent Cost — Custo total calculado?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_multi_agent_cost():
    """
    Cálculo de custo total em sistemas multiagente.
    
    Cada agente tem seu próprio custo (tokens × preço).
    Métricas importantes:
    - total_cost: soma de todos os custos
    - most_expensive: qual agente custa mais
    - cost_per_agent: média por agente
    """
    agent_costs = {
        "supervisor": 0.002,
        "engineer": 0.005,
        "billing": 0.001,
        "support": 0.003,
    }
    
    # Calcula métricas de custo
    total_cost = sum(agent_costs.values())
    most_expensive = max(agent_costs, key=agent_costs.get)
    cost_per_agent = total_cost / len(agent_costs)
    
    assert total_cost > 0, "Custo total deve ser positivo"
    assert most_expensive in agent_costs, \
        f"Mais caro deve ser um dos agentes, got {most_expensive}"
    assert cost_per_agent > 0, "Custo médio deve ser positivo"
    assert agent_costs[most_expensive] >= cost_per_agent, \
        f"Mais caro ({agent_costs[most_expensive]}) >= média ({cost_per_agent})"
    
    console.print(f"[green]✓[/green] Custo total: ${total_cost:.3f} | "
                  f"Mais caro: {most_expensive} (${agent_costs[most_expensive]})")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Hierarchical Scaling — Escala hierárquica?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_hierarchical_scaling():
    """
    Simulação de escala hierárquica com overhead.
    
    Em sistemas multiagente hierárquicos:
    - Nível 0 (flat): 1 agente, 0% overhead
    - Nível 1: supervisor + especialistas, ~20% overhead
    - Nível 2: super-supervisor + sub-supervisores + especialistas, ~40% overhead
    
    Overhead vem da coordenação, roteamento e comunicação entre níveis.
    """
    base_cost = 0.01  # Custo sem hierarquia
    
    levels = [
        {"name": "flat", "agents": 1, "overhead_pct": 0},
        {"name": "single_level", "agents": 4, "overhead_pct": 20},
        {"name": "two_levels", "agents": 16, "overhead_pct": 40},
    ]
    
    # Calcula custo escalado por nível
    costs_by_level = {}
    for level in levels:
        # Aplica multiplicador de overhead
        overhead_multiplier = 1 + level["overhead_pct"] / 100
        costs_by_level[level["name"]] = base_cost * overhead_multiplier
    
    flat_cost = costs_by_level["flat"]
    single_cost = costs_by_level["single_level"]
    two_cost = costs_by_level["two_levels"]
    
    assert single_cost > flat_cost, \
        f"Nível único ({single_cost}) > flat ({flat_cost})"
    assert two_cost > single_cost, \
        f"Dois níveis ({two_cost}) > nível único ({single_cost})"
    assert two_cost < flat_cost * 3, \
        f"Dois níveis ({two_cost}) não pode exceder 3x flat ({flat_cost})"
    
    console.print(f"[green]✓[/green] Escala: flat=${flat_cost:.4f} → "
                  f"1-nível=${single_cost:.4f} → 2-níveis=${two_cost:.4f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_supervisor_routing, test_02_specialist_failure,
             test_03_agent_coordination, test_04_multi_agent_cost,
             test_05_hierarchical_scaling]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P3b: Sistema Multiagente[/bold cyan]",
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
