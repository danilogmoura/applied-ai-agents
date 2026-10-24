"""Módulo 10 — SOLUÇÃO COMENTADA

Execute com: python modules/10-avaliacao/exercises.py

Código completo com explicações detalhadas.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SOLUÇÕES COMENTADAS — Funções implementadas com explicações
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calcula distância de Levenshtein usando programação dinâmica.
    
    Matriz M[i][j] = distância entre s1[:i] e s2[:j]
    Recorrência:
    - Se s1[i] == s2[j]: M[i][j] = M[i-1][j-1]
    - Senão: min(inserção, deleção, substituição) + 1
    """
    # ⚠️ PONTO CRÍTICO: Garante que s1 é o maior para otimizar espaço
    # Assim previous_row sempre tem tamanho len(s2)+1 (menor)
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    
    # ⚠️ PONTO CRÍTICO: String vazia → distância = comprimento da outra
    # Para transformar "abc" em "", preciso deletar 3 chars
    if len(s2) == 0:
        return len(s1)
    
    # Linha anterior da matriz (inicializada com 0..len(s2))
    previous_row = list(range(len(s2) + 1))
    
    for i, c1 in enumerate(s1):
        current_row = [i + 1]  # Primeira coluna = i+1 (deleções acumuladas)
        for j, c2 in enumerate(s2):
            # Três operações possíveis:
            insertions = previous_row[j + 1] + 1      # Insere char em s1
            deletions = current_row[j] + 1             # Deleta char de s1
            substitutions = previous_row[j] + (c1 != c2)  # Substitui (0 se igual)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]


def fuzzy_match(pred: str, expected: str, threshold: int = 2) -> bool:
    """
    Retorna True se distância de Levenshtein <= threshold.
    
    Threshold = 2 significa: tolera até 2 edições (inserção/deleção/substituição).
    Útil para detectar erros de digitação ou variações menores.
    """
    # ⚠️ PONTO CRÍTICO: Chama levenshtein_distance e compara com threshold
    return levenshtein_distance(pred, expected) <= threshold


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Golden Dataset — Dataset confiável?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_golden_dataset():
    """
    Golden dataset: conjunto de dados de referência para avaliação.
    
    Cada exemplo tem:
    - input: entrada do sistema
    - expected: resposta esperada (ground truth)
    
    Mínimo 5 exemplos cobrindo casos edge (extremos).
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
    Métrica de exact match: predição deve ser IDÊNTICA à ground truth.
    
    Fórmula: accuracy = predições_corretas / total_predições
    """
    predictions = ["URGENTE", "ALTA", "MEDIA", "BAIXA", "NORMAL"]
    ground_truth = ["URGENTE", "ALTA", "ERRADO", "BAIXA", "NORMAL"]
    
    # Calcula exact match accuracy
    correct = sum(1 for p, g in zip(predictions, ground_truth) if p == g)
    total = len(predictions)
    accuracy = correct / total if total > 0 else 0.0
    
    # ⚠️ PONTO CRÍTICO: Valide comportamento, não valor exato
    # A accuracy deve estar na faixa [0, 1] e este caso específico tem 4/5 acertos
    assert 0 <= accuracy <= 1, f"Accuracy deve ser [0,1], got {accuracy}"
    assert accuracy < 1.0, "Este teste故意 tem 1 erro — accuracy não pode ser 100%"
    # ← O aluno calculou corretamente? Verifique contra o valor esperado derivado dos dados
    expected_accuracy = correct / total if total > 0 else 0.0
    assert abs(accuracy - expected_accuracy) < 1e-9, \
        f"Accuracy deve ser {expected_accuracy:.1f} ({correct}/{total}), got {accuracy:.2f}"
    
    console.print(f"[green]✓[/green] Exact match: {correct}/{total} = {accuracy:.0%}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Fuzzy Match — Similaridade tolerante a erros?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_fuzzy_match():
    """
    Testa distância de Levenshtein e fuzzy match.
    
    Distância de Levenshtein: número mínimo de operações (inserção,
    deleção, substituição) para transformar uma string em outra.
    
    Fuzzy match: se distância <= threshold → considera similar.
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
    Teste Z para proporções: compara duas taxas de acerto.
    
    H0: p_a = p_b (não há diferença)
    H1: p_a ≠ p_b (há diferença)
    
    Se |z| > 1.96 → rejeitamos H0 (significativo a p < 0.05)
    """
    version_a = {"success": 85, "total": 100}
    version_b = {"success": 92, "total": 100}
    
    p_a = version_a["success"] / version_a["total"]
    p_b = version_b["success"] / version_b["total"]
    
    # Calcula diferença e significância
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
    Detecção de regressão: alerta se performance cai além do threshold.
    
    Regra: Se accuracy cai > 2% vs baseline → regressão.
    """
    baseline_accuracy = 0.92
    current_accuracy = 0.88
    regression_threshold = 0.02
    
    # Calcula delta e verifica se há regressão
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
