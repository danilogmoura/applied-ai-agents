"""Módulo P3b — Exercícios Práticos

Execute com: python modules/p3b_multi_agent/exercises.py

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
# STUBS — Implemente estas funções para fazer os testes passarem
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def route_to_specialist(task: str, specialists: list) -> str:
    """
    Roteia tarefa para especialista mais adequado baseado em keywords.
    
    TODO: Retorne o nome do especialista cujas keywords mais se aproximam
    do texto da tarefa. Se nenhum especialista corresponder, retorne 'generalist'.
    ← Implemente aqui
    """
    return "generalist"  # Placeholder vazio


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Supervisor Routing — Roteamento correto?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_supervisor_routing():
    """
    Testa roteamento do supervisor para especialistas.
    
    Cenário: Chatbot de suporte técnico da TechCorp Brasil.
    Volume: ~500 tickets/dia distribuídos assim:
      - 40% dúvidas técnicas (→ engineer)
      - 25% cobranças/faturas (→ billing)
      - 20% tutoriais/configuração (→ support)
      - 15% outros (→ generalist)
    
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
    
    assert route_to_specialist("Sistema caiu com erro 500", specialists) == "engineer"
    assert route_to_specialist("Quero saber o preço do plano", specialists) == "billing"
    assert route_to_specialist("Como configuro minha conta?", specialists) == "support"
    # ⚠️ PONTO CRÍTICO: Valide comportamento — sem keyword match → generalist
    routed_general = route_to_specialist("Olá", specialists)
    assert routed_general == "generalist", \
        f"Sem keywords → 'generalist', got {routed_general!r}"
    
    # ⚠️ PONTO CRÍTICO: Propriedade comportamental — cada keyword mapeia exatamente um especialista
    test_cases = [
        ("minha conta está crashando", "engineer"),
        ("quero pagar a fatura", "billing"),
        ("me ensina como usar", "support"),
    ]
    for query, expected in test_cases:
        routed = route_to_specialist(query, specialists)
        assert routed == expected, \
            f"{query!r} → {expected!r}, got {routed!r}"
    
    console.print("[green]✓[/green] Supervisor roteia corretamente!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Specialist Failure — Fallback quando falha?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_specialist_failure():
    """
    Redistribuição quando especialista falha.
    
    Cenário: Engineer indisponível (servidor down).
    Fallback: redistribuir para outro especialista disponível.
    Prioridade: billing → support → generalist.
    """
    specialists = ["engineer", "billing", "support", "generalist"]
    
    def execute_task(specialist: str, task: str) -> str:
        """Simula execução — engineer SEMPRE falha neste teste."""
        if specialist == "engineer":
            raise RuntimeError("Engineer indisponível")
        return f"{specialist} resolved: {task}"
    
    # TODO: Implemente fallback para outro especialista
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
        # ← Implemente lógica de fallback aqui
    
    assert used_fallback == True, "Fallback deveria ter sido acionado"
    assert result is not None and "resolved" in result, \
        f"Fallback deveria retornar resultado válido, got {result}"
    
    console.print(f"[green]✓[/green] Fallback: engineer→{used_fallback}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Agent Coordination — Agentes coordenam bem?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_agent_coordination():
    """
    Coordenação entre agentes.
    
    Cenário: Pipeline de análise de mercado.
    - researcher: coleta dados e insights
    - writer: produz relatório baseado nos findings
    Contexto compartilhado garante consistência entre etapas.
    """
    class Agent:
        def __init__(self, name: str):
            self.name = name
            self.context: Dict[str, Any] = {}
        
        def share_context(self, other: 'Agent'):
            """TODO: Compartilhe contexto com outro agente."""
            # ← Implemente aqui
            pass
        
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
    Custo total de múltiplos agentes.
    
    Cenário: Pipeline TechCorp com 4 agentes.
    Custos por execução (estimados em tokens):
      - supervisor: roteamento (~$0.002)
      - engineer: diagnóstico técnico (~$0.005)
      - billing: processamento financeiro (~$0.001)
      - support: resposta genérica (~$0.003)
    
    Objetivo: calcular métricas de custo para otimização.
    """
    agent_costs = {
        "supervisor": 0.002,
        "engineer": 0.005,
        "billing": 0.001,
        "support": 0.003,
    }
    
    # TODO: Calcule métricas de custo
    total_cost = 0.0
    most_expensive = ""
    cost_per_agent = 0.0
    
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
        # ← Implemente cálculo aqui
        costs_by_level[level["name"]] = 0.0
    
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
