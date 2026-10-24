"""Módulo P1 — Exercícios Práticos

Execute com: python modules/03-viabilidade/exercises.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Latency Measurement — Você mede a latência?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_latency_measurement():
    """
    TODO: Implemente uma função que mede o tempo de resposta.
    
    Regra: Para classificação de tickets, latência < 2s é aceitável.
    """
    import time
    
    def measure_response_time(func, *args) -> float:
        """TODO: Meça e retorne o tempo de execução em segundos."""
        # ← Implemente aqui
        return 0.0  # Placeholder vazio
    
    # Simula chamada lenta
    def slow_call():
        time.sleep(0.1)
        return "classificado"
    
    latency = measure_response_time(slow_call)
    assert latency > 0, "Latência deve ser positiva"
    assert isinstance(latency, float), f"Latência deve ser float, got {type(latency)}"
    
    console.print(f"[green]✓[/green] Latência medida: {latency*1000:.1f}ms")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Cost Comparison — IA vs Regras
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_cost_comparison():
    """
    TODO: Compare custo de IA vs regras heurísticas.
    
    Cenário: 10,000 tickets/mês
    - IA (gpt-4o-mini): ~$0.00003/ticket → $0.30/mês
    - Humano: ~$0.10/ticket → $1,000/mês
    """
    tickets_per_month = 10000
    
    ia_cost_per_ticket = 0.00003
    human_cost_per_ticket = 0.10
    
    # TODO: Calcule custos mensais
    monthly_ia_cost = None  # ← Mude aqui
    monthly_human_cost = None  # ← Mude aqui
    
    assert monthly_ia_cost > 0, "Custo IA deve ser positivo"
    assert monthly_human_cost > 0, "Custo humano deve ser positivo"
    assert monthly_ia_cost < monthly_human_cost, \
        f"IA (${monthly_ia_cost}) deveria ser mais barato que humano (${monthly_human_cost})"
    
    savings_pct = ((monthly_human_cost - monthly_ia_cost) / monthly_human_cost) * 100
    console.print(f"[green]✓[/green] Economia: {savings_pct:.1f}% com IA")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Accuracy Threshold — Quando IA é bom o suficiente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_accuracy_threshold():
    """
    TODO: Verifique se accuracy está acima do threshold mínimo.
    
    Regra: accuracy >= 0.85 é aceitável para produção.
    """
    ground_truth = ["URGENTE", "ALTA", "MEDIA", "BAIXA", "NORMAL"]
    predictions = ["URGENTE", "ALTA", "MEDIA", "BAIXA", "ERRADO"]
    
    # TODO: Calcule accuracy (proporção de acertos)
    correct = sum(1 for gt, pred in zip(ground_truth, predictions) if gt == pred)
    total = len(ground_truth)
    accuracy = None  # ← Mude aqui
    
    assert 0 <= accuracy <= 1, f"Accuracy deve ser entre 0 e 1, got {accuracy}"
    assert accuracy < 1.0, "Este teste故意 tem um erro — accuracy não pode ser 100%"
    
    # ⚠️ PONTO CRÍTICO: Valide comportamento — accuracy derivada dos dados
    expected_accuracy = correct / total if total > 0 else 0.0
    assert abs(accuracy - expected_accuracy) < 1e-9, \
        f"Accuracy deve ser {expected_accuracy:.2f} ({correct}/{total}), got {accuracy:.2f}"
    
    console.print(f"[green]✓[/green] Accuracy: {accuracy:.2f} ({correct}/{total})")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Memorando Generation — Gere recomendação automática
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_memorando_generation():
    """
    TODO: Gere um memorando de viabilidade baseado nos dados medidos.
    
    O memorando deve conter:
    - 'recommendation': string com decisão ('aprovar', 'viável', 'recomendado') ou ('reprovar', 'inviável', 'não recomendar')
    - 'reasoning': string explicando o porquê
    - 'risks': lista de riscos identificados
    - 'thresholds': dict com {'cost_viable': bool, 'latency_acceptable': bool}
    """
    data = {
        "latency_ms": 1500,
        "cost_per_1k": 0.03,
        "accuracy": 0.92,
        "volume_monthly": 10000,
    }
    
    # TODO: Crie um dicionário completo com a recomendação
    memo = {}  # ← Preencha com chaves: 'recommendation', 'reasoning', 'risks', 'thresholds'
    
    assert "recommendation" in memo, \
        "Memorando deve ter campo 'recommendation'"
    assert "reasoning" in memo, \
        "Memorando deve ter campo 'reasoning'"
    assert "risks" in memo, \
        "Memorando deve ter campo 'risks' (lista de riscos)"
    assert "thresholds" in memo, \
        "Memorando deve ter campo 'thresholds' (dict com cost_viable e latency_acceptable)"
    assert isinstance(memo["risks"], list), \
        f"'risks' deve ser uma lista, got {type(memo['risks'])}"
    assert len(memo["risks"]) >= 2, \
        f"Memorando deve listar pelo menos 2 riscos, got {len(memo['risks'])}"
    assert "cost_viable" in memo["thresholds"], \
        "'thresholds' deve ter 'cost_viable'"
    assert "latency_acceptable" in memo["thresholds"], \
        "'thresholds' deve ter 'latency_acceptable'"
    assert isinstance(memo["thresholds"]["cost_viable"], bool), \
        "'cost_viable' deve ser boolean"
    assert isinstance(memo["thresholds"]["latency_acceptable"], bool), \
        "'latency_acceptable' deve ser boolean"
    
    rec = memo["recommendation"].lower()
    assert any(word in rec for word in ["aprovar", "viável", "recomend", "sim"]), \
        f"Recomendação deveria conter 'aprovar' ou 'viável', got: {rec}"
    
    console.print(f"[green]✓[/green] Memorando: {memo['recommendation']}")
    console.print(f"[dim]Riscos identificados: {', '.join(memo['risks'])}[/]")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Scalability Analysis — Escala funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_scalability_analysis():
    """
    TODO: Projete custos para diferentes volumes e calcule break-even point.
    
    Se 1,000 tickets custam $0.03 (IA) vs $100.00 (humano):
    - Quanto custam 100,000?
    - Qual é o volume onde IA se paga (break-even)?
    """
    costs_at_1k = {
        "ia": 0.03,
        "humano": 100.00,
    }
    
    # TODO: Escale linearmente para 100k tickets
    scale_factor = 100  # 100k / 1k
    
    cost_100k_ia = None  # ← Calcule
    cost_100k_humano = None  # ← Calcule
    
    assert cost_100k_ia > 0, "Custo IA escalado deve ser positivo"
    assert cost_100k_humano > 0, "Custo humano escalado deve ser positivo"
    assert cost_100k_ia < 10.0, \
        f"Custo IA para 100k deveria ser < $10, got ${cost_100k_ia}"
    
    # TODO: Calcule break-even point (onde IA se torna mais barato)
    # Fórmula: break_even = custo_fixo_regras / (custo_humano_unitario - custo_IA_unitario)
    ia_per_ticket = costs_at_1k["ia"] / 1000  # custo por ticket IA
    humano_per_ticket = costs_at_1k["humano"] / 1000  # custo por ticket humano
    
    if humano_per_ticket > ia_per_ticket:
        break_even = int(costs_at_1k["humano"] / (humano_per_ticket - ia_per_ticket))
    else:
        break_even = float('inf')
    
    assert break_even > 0, "Break-even deve ser positivo"
    assert break_even <= 10000, \
        f"Break-even deveria ser <= 10000, got {break_even}"
    
    console.print(f"[green]✓[/green] Break-even: {break_even:,} tickets")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_latency_measurement, test_02_cost_comparison,
             test_03_accuracy_threshold, test_04_memorando_generation,
             test_05_scalability_analysis]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P1: Viabilidade[/bold cyan]",
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
