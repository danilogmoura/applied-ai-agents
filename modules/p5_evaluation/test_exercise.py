"""
Módulo P5 — Teste do Exercício

Execute com: python modules/p5_evaluation/test_exercise.py

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
# TESTE 1: Golden Dataset — Dataset confiável?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_golden_dataset():
    """
    TODO: Construa um golden dataset com input + resposta esperada.
    
    Regra: Mínimo 5 exemplos cobrindo casos edge.
    """
    golden_dataset = [
        {"input": "Erro 403 ao login", "expected": "URGENTE"},
        {"input": "Preço plano enterprise", "expected": "ALTA"},
        {"input": "Como funciona?", "expected": "BAIXA"},
        {"input": "Quero cancelar minha assinatura", "expected": "MEDIA"},
        {"input": "Não recebi meu reembolso", "expected": "URGENTE"},
    ]
    
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
    TODO: Implemente métrica de exact match.
    """
    predictions = ["URGENTE", "ALTA", "MEDIA", "BAIXA", "NORMAL"]
    ground_truth = ["URGENTE", "ALTA", "ERRADO", "BAIXA", "NORMAL"]
    
    # Calcular exact match accuracy
    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    total = len(predictions)
    accuracy = correct / total if total > 0 else 0.0
    
    assert 0 <= accuracy <= 1, f"Accuracy deve ser [0,1], got {accuracy}"
    assert accuracy < 1.0, "Este teste故意 tem 1 erro — accuracy não pode ser 100%"
    assert accuracy == 0.8, f"4/5 corretos = 0.8, got {accuracy}"
    
    console.print(f"[green]✓[/green] Exact match: {correct}/{total} = {accuracy:.0%}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Fuzzy Match — Similaridade tolerante a erros?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_fuzzy_match():
    """
    TODO: Implemente fuzzy match (tolera pequenas diferenças).
    """
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calcule distância de Levenshtein entre duas strings."""
        if len(s1) < len(s2):
            return levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    dist1 = levenshtein_distance("URGENTE", "URGENTE")
    dist2 = levenshtein_distance("URGENTE", "URGENTEE")
    dist3 = levenshtein_distance("URGENTE", "NORMAL")
    
    assert dist1 == 0, f"Iguais devem ter distância 0, got {dist1}"
    assert dist2 == 1, f"1 char diferença = distância 1, got {dist2}"
    assert dist3 > dist2, f"Diferentes devem ter maior distância"
    
    # Implementar fuzzy match com threshold
    def fuzzy_match(pred: str, expected: str, threshold: int = 2) -> bool:
        """Retorna True se distância <= threshold."""
        return levenshtein_distance(pred, expected) <= threshold
    
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
    
    p_a = version_a["success"] / version_a["total"]
    p_b = version_b["success"] / version_b["total"]
    
    # Calcular diferença e significância
    difference = p_b - p_a
    
    # Proporção combinada
    p_combined = (version_a["success"] + version_b["success"]) / \
                 (version_a["total"] + version_b["total"])
    
    # Erro padrão
    se = (p_combined * (1 - p_combined) * (1/version_a["total"] + 1/version_b["total"])) ** 0.5
    
    # Z-score
    z_score = difference / se if se > 0 else 0.0
    
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
    
    # Calcular delta e verificar se há regressão
    delta = baseline_accuracy - current_accuracy
    has_regression = delta > regression_threshold
    
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
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P5: Avaliação e Testes[/bold cyan]",
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
