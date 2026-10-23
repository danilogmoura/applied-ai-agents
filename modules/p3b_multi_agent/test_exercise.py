"""
Módulo P3b — Teste do Exercício

Execute com: python modules/p3b_multi_agent/test_exercise.py

IMPLEMENTE os TODOs para fazer os testes passarem.
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
    TODO: Implemente o roteamento do supervisor para especialistas.
    
    Regras:
    - "bug", "erro", "crash" → "engineer"
    - "preço", "cobrança", "fatura" → "billing"
    - "como funciona", "tutorial" → "support"
    - demais → "generalist"
    """
    specialists = [
        {"name": "engineer", "keywords": ["bug", "erro", "crash", "falha"]},
        {"name": "billing", "keywords": ["preço", "cobrança", "fatura", "pagamento"]},
        {"name": "support", "keywords": ["como", "tutorial", "guia", "instrução"]},
    ]
    
    def route_to_specialist(task: str) -> str:
        """Retorne o nome do especialista mais adequado baseado em keywords."""
        task_lower = task.lower()
        best_match = None
        best_score = 0
        
        for spec in specialists:
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
    TODO: Implemente redistribuição quando especialista falha.
    """
    specialists = ["engineer", "billing", "support", "generalist"]
    
    def execute_task(specialist: str, task: str) -> str:
        """Simula execução — engineer SEMPRE falha neste teste."""
        if specialist == "engineer":
            raise RuntimeError("Engineer indisponível")
        return f"{specialist} resolved: {task}"
    
    # Implemente fallback para outro especialista
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
    TODO: Verifique coordenação entre agentes.
    
    Dois agentes trabalhando juntos devem compartilhar contexto.
    """
    class Agent:
        def __init__(self, name: str):
            self.name = name
            self.context: Dict[str, Any] = {}
        
        def share_context(self, other: 'Agent'):
            """Compartilhe contexto com outro agente."""
            for key, value in self.context.items():
                other.receive_context(self.name, {key: value})
        
        def receive_context(self, other_name: str, context: dict):
            """Receba contexto de outro agente."""
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
    TODO: Calcule custo total de múltiplos agentes.
    """
    agent_costs = {
        "supervisor": 0.002,
        "engineer": 0.005,
        "billing": 0.001,
        "support": 0.003,
    }
    
    # Calcule métricas de custo
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
    TODO: Simule escala hierárquica (supervisor → sub-supervisores → especialistas).
    
    Regra: Cada nível adiciona ~20% de overhead.
    """
    base_cost = 0.01  # Custo sem hierarquia
    
    levels = [
        {"name": "flat", "agents": 1, "overhead_pct": 0},
        {"name": "single_level", "agents": 4, "overhead_pct": 20},
        {"name": "two_levels", "agents": 16, "overhead_pct": 40},
    ]
    
    # TODO: Calcule custo escalado por nível
    costs_by_level = {}
    for level in levels:
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
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
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
