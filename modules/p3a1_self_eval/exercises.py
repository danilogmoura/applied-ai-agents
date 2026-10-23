"""Módulo P3a-1 — Exercícios Práticos

Execute com: python modules/p3a1_self_eval/exercises.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Self-Evaluation Score — Avalia a própria resposta?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_self_evaluation_score():
    """
    TODO: Implemente scoring de autoavaliação.
    
    Critérios: accuracy, completeness, clarity (cada um 0-10).
    Respostas curtas (<50 chars) devem ter score baixo.
    """
    response = "O reembolso deve ser solicitado em até 30 dias após a compra."
    
    def evaluate_response(response: str) -> dict:
        """Retorne {'accuracy': X, 'completeness': Y, 'clarity': Z} baseado no tamanho e conteúdo."""
        # ← Implemente aqui
        return {"accuracy": 0, "completeness": 0, "clarity": 0}  # Placeholder vazio
    
    scores = evaluate_response(response)
    
    assert all(k in scores for k in ["accuracy", "completeness", "clarity"]), \
        "Scores devem ter accuracy, completeness, clarity"
    assert all(0 <= v <= 10 for v in scores.values()), \
        "Cada score deve estar entre 0 e 10"
    
    avg = sum(scores.values()) / len(scores)
    console.print(f"[green]✓[/green] Média: {avg:.1f}/10")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Iteration Loop — Gera → Avalia → Refina?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_iteration_loop():
    """
    TODO: Implemente o loop de refinamento iterativo.
    
    Regra: max 3 iterações, para quando score >= threshold.
    """
    def generate_response(iteration: int) -> str:
        responses = [
            "Reembolso.",  # Muito curto
            "O reembolso pode ser solicitado dentro de 30 dias após a compra, conforme política da empresa.",  # Melhor
            "O reembolso pode ser solicitado dentro de 30 dias após a compra. Produtos digitais têm prazo de 14 dias. Processamento leva 5-10 dias úteis.",  # Completo
        ]
        return responses[iteration % len(responses)]
    
    def evaluate(text: str) -> float:
        return min(len(text) / 50.0, 10.0)  # Score baseado em completude
    
    max_iterations = 3
    threshold = 7.0
    
    # TODO: Implemente o loop gera→avalia→refina
    current = generate_response(0)
    best_score = 0
    best_response = current
    iterations_used = 0
    
    for i in range(max_iterations):
        score = evaluate(current)
        iterations_used = i + 1
        
        if score > best_score:
            best_score = score
            best_response = current
        
        if score >= threshold:
            break
        
        current = generate_response(i + 1)
    
    assert best_score >= threshold, \
        f"Score final {best_score} deveria atingir threshold {threshold}"
    assert iterations_used <= max_iterations, \
        f"Deveria parar em no máximo {max_iterations} iterações"
    
    console.print(f"[green]✓[/green] Loop: {iterations_used} iterações, score={best_score:.1f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Max Iterations Guard — Evita gasto infinito?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_max_iterations_guard():
    """
    TODO: Verifique que o loop para mesmo sem atingir threshold.
    """
    max_iterations = 5
    
    # Simula caso que NUNCA atinge threshold bom
    def bad_generate(n):
        return "resposta ruim" * n
    
    def bad_evaluate(text):
        return 2.0  # Sempre baixo
    
    # TODO: Implemente loop com guard de max_iterations
    result = None
    actual_iterations = 0
    
    for i in range(max_iterations + 10):  # Tenta ir além do limite
        actual_iterations += 1
        if actual_iterations > max_iterations:
            break  # ← O guard deve impedir isso
        result = bad_generate(i)
    
    assert actual_iterations == max_iterations, \
        f"Deveria parar em {max_iterations}, foi {actual_iterations}"
    
    console.print(f"[green]✓[/green] Guard funciona: parou em {actual_iterations} iterações")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Cost Accumulation — Custos somam corretamente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_cost_accumulation():
    """
    TODO: Calcule custo total das múltiplas iterações usando shared.cost.
    """
    from shared.cost import estimate_cost, format_cost
    
    # Simula tokens por iteração (input + output)
    costs_per_iter = [
        estimate_cost(200, 150, "gpt-4o-mini"),   # Iteração 1
        estimate_cost(300, 200, "gpt-4o-mini"),   # Iteração 2 (refinamento)
        estimate_cost(250, 180, "gpt-4o-mini"),   # Iteração 3
    ]
    
    # Some todos os custos
    total_cost = sum(costs_per_iter)
    avg_cost = total_cost / len(costs_per_iter)
    
    assert total_cost > 0, "Custo total deve ser positivo"
    assert avg_cost > 0, "Custo médio deve ser positivo"
    assert abs(total_cost - sum(costs_per_iter)) < 0.0001, \
        "Total deve igual soma dos individuais"
    
    console.print(f"[green]✓[/green] Custo total: {format_cost(total_cost)} ({len(costs_per_iter)} iterações)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Response Improvement — Melhora a cada iteração?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_response_improvement():
    """
    TODO: Verifique que respostas melhoram ao longo das iterações.
    Cada iteração subsequente deve ter score >= anterior.
    """
    scores_history = [3.0, 6.5, 8.2, 9.0]
    
    # Verifica tendência crescente
    is_improving = all(
        scores_history[i] <= scores_history[i + 1]
        for i in range(len(scores_history) - 1)
    )
    
    assert is_improving, \
        f"Scores {scores_history} deveriam mostrar melhoria consistente"
    
    improvement_pct = ((scores_history[-1] - scores_history[0]) / scores_history[0]) * 100
    console.print(f"[green]✓[/green] Melhoria: {improvement_pct:.0f}% ({scores_history[0]}→{scores_history[-1]})")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_self_evaluation_score, test_02_iteration_loop,
             test_03_max_iterations_guard, test_04_cost_accumulation,
             test_05_response_improvement]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P3a-1: Autoavaliação[/bold cyan]",
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
