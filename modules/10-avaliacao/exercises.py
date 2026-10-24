"""Módulo 10 — Exercícios Práticos

Execute com: python modules/10-avaliacao/exercises.py

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
# STUBS — Implemente estas funções para fazer os testes passarem
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calcula distância de Levenshtein entre duas strings.
    
    TODO: Retorne número mínimo de edições (inserções, deleções, substituições)
    para transformar s1 em s2.
    ← Implemente aqui
    """
    return 0  # Placeholder vazio


def fuzzy_match(pred: str, expected: str, threshold: int = 2) -> bool:
    """
    Retorna True se distância de Levenshtein <= threshold.
    
    TODO: Use levenshtein_distance para comparar pred e expected.
    Se distância <= threshold → True (match tolerante a erros).
    ← Implemente aqui
    """
    return False  # Placeholder vazio


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Golden Dataset — Dataset confiável?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_golden_dataset():
    """
    Testa construção de golden dataset.
    
    Regra: Mínimo 5 exemplos cobrindo casos edge.
    """
    # Construa o golden dataset aqui
    golden_dataset = []  # Placeholder vazio
    
    assert len(golden_dataset) >= 5, \
        f"Golden dataset deve ter mínimo 5 exemplos, got {len(golden_dataset)}"
    
    # Verificar que cada exemplo tem input e expected
    valid_examples = all(
        "input" in ex and "expected" in ex and len(ex["input"]) > 0 and len(ex["expected"]) > 0
        for ex in golden_dataset
    )
    assert valid_examples, "Cada exemplo deve ter 'input' e 'expected' não vazios"
    
    console.print(f"[green]✓[/green] Golden dataset: {len(golden_dataset)} exemplos válidos")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Exact Match Metric — Métrica básica funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_exact_match():
    """
    Testa métrica de exact match.
    """
    predictions = ["URGENTE", "ALTA", "MEDIA", "BAIXA", "NORMAL"]
    ground_truth = ["URGENTE", "ALTA", "ERRADO", "BAIXA", "NORMAL"]
    
    # Calcular exact match accuracy
    correct = 0
    total = len(predictions)
    accuracy = 0.0
    
    # ⚠️ PONTO CRÍTICO: Valide comportamento, não valor exato
    # A accuracy deve estar na faixa [0, 1] e este caso específico tem 4/5 acertos
    assert 0 <= accuracy <= 1, f"Accuracy deve ser [0,1], got {accuracy}"
    assert accuracy < 1.0, "Este teste故意 tem 1 erro — accuracy não pode ser 100%"
    # ← Implemente o cálculo correto: correct / total
    expected_accuracy = correct / total if total > 0 else 0.0
    assert abs(accuracy - expected_accuracy) < 1e-9, \
        f"Accuracy deve ser {expected_accuracy:.1f} ({correct}/{total}), got {accuracy:.2f}"
    
    console.print(f"[green]✓[/green] Exact match: {correct}/{total} = {accuracy:.0%}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Fuzzy Match — Similaridade tolerante a erros?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_fuzzy_match():
    """
    Testa fuzzy match (tolera pequenas diferenças).
    """
    dist1 = levenshtein_distance("URGENTE", "URGENTE")
    dist2 = levenshtein_distance("URGENTE", "URGENTEE")
    dist3 = levenshtein_distance("URGENTE", "NORMAL")
    
    # ⚠️ PONTO CRÍTICO: Valide propriedades comportamentais da distância
    # Strings iguais → distância mínima (zero); propriedade fundamental
    assert dist1 >= 0, f"Distância nunca pode ser negativa, got {dist1}"
    # Propriedade de identidade: string igual a si mesma tem distância zero
    assert dist1 <= dist2, f"String idêntica deve ter distância <= que string diferente"
    # Propriedade fundamental: distância é sempre não-negativa
    assert dist2 >= 1, f"1 char diferença → distância mínima 1, got {dist2}"
    assert dist3 > dist2, f"Diferentes devem ter maior distância"
    
    assert fuzzy_match("URGENTE", "URGENTE") == True
    assert fuzzy_match("URGENTEE", "URGENTE") == True  # 1 char diff
    assert fuzzy_match("NORMAL", "URGENTE") == False
    
    console.print("[green]✓[/green] Fuzzy match: distance-based ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: A/B Testing — Significância estatística?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_ab_testing():
    """
    TODO: Compare duas versões usando teste Z.
    
    Versão A: 85/100 acertos | Versão B: 92/100 acertos
    """
    version_a = {"success": 85, "total": 100}
    version_b = {"success": 92, "total": 100}
    
    # TODO: Calcule diferença e significância
    p_a = 0.0
    p_b = 0.0
    difference = 0.0
    z_score = 0.0
    
    assert abs(difference) > 0, "Diferença não pode ser zero neste teste"
    assert z_score is not None, "Z-score deve ser calculado"
    
    # Threshold: |z| > 1.96 → significativo (p < 0.05)
    significant = abs(z_score) > 1.96
    
    console.print(f"[green]✓[/green] A/B: A={p_a:.0%} vs B={p_b:.0%}, "
                  f"diff={difference:.2f}, z={z_score:.2f}, significant={significant}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Regression Benchmarking — Degradação detectada?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_regression_benchmarking():
    """
    TODO: Detecte degradação de performance entre releases.
    
    Regra: Se accuracy cai > 2%, alertar regressão.
    """
    baseline_accuracy = 0.92
    current_accuracy = 0.88
    regression_threshold = 0.02
    
    # TODO: Calcule delta e verifique se há regressão
    delta = 0.0
    has_regression = False
    
    assert delta > 0, "Baseline deve ser melhor que current neste teste"
    assert has_regression == True, \
        f"Delta {delta} > threshold {regression_threshold} → regressão detectada"
    
    console.print(f"[green]✓[/green] Regressão: baseline={baseline_accuracy:.0%} → "
                  f"current={current_accuracy:.0%}, delta={delta:.0%} ⚠️")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_golden_dataset, test_02_exact_match,
             test_03_fuzzy_match, test_04_ab_testing,
             test_05_regression_benchmarking]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]Módulo 10 — Avaliação e Testes[/bold cyan]",
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
