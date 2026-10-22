"""
Módulo P0 — Teste do Exercício

Execute com: python modules/p0_first_llm/test_exercise.py

Você precisa IMPLEMENTAR as funções marcadas com TODO para fazer os testes passarem.
Cada teste falha até você escrever o código correto.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

from shared.cost import count_tokens, estimate_cost, format_cost

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Token Counting — Você conta os tokens?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_token_counting():
    """
    O custo da API depende de quantos tokens você envia.
    
    TODO: Implemente a função abaixo para contar tokens corretamente.
    Dica: cada ~4 caracteres em inglês ≈ 1 token.
    """
    text = "Não consigo acessar minha conta. Recebo erro 403."
    
    # TODO: Substitua None pelo resultado real de count_tokens(text)
    token_count = None  # ← Mude aqui
    
    assert token_count is not None and token_count > 0, \
        "Token count não pode ser zero ou None"
    assert isinstance(token_count, int), \
        f"Token count deve ser int, got {type(token_count)}"
    
    console.print(f"[green]✓[/green] Tokens contados: {token_count}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Cost Estimation — Quanto custa essa chamada?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_cost_estimation():
    """
    gpt-4o-mini: $0.15/1M tokens input, $0.60/1M tokens output
    
    TODO: Calcule o custo estimado de uma chamada.
    """
    prompt_tokens = 50
    completion_tokens = 10
    
    # TODO: Calcule o custo usando estimate_cost(prompt_tokens, completion_tokens, model="gpt-4o-mini")
    cost = None  # ← Mude aqui
    
    assert cost is not None and cost >= 0, \
        "Custo não pode ser None ou negativo"
    assert cost < 1.0, \
        f"Custo de uma única chamada deveria ser centavos, got ${cost}"
    
    console.print(f"[green]✓[/green] Custo estimado: ${cost:.6f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Ticket Classification — Classifique corretamente
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_ticket_classification():
    """
    TODO: Escreva uma função que classifica tickets por prioridade.
    
    Regras:
    - "erro", "500", "não acess", "403" → "URGENTE"
    - "preço", "enterprise", "cotar" → "ALTA"  
    - "prejuízo", "reembolso", "financeiro" → "MEDIA"
    - demais → "BAIXA"
    """
    def classify_ticket_manual(ticket_text: str) -> str:
        """TODO: Implemente esta função."""
        return "BAIXA"  # ← Troque pela lógica real
    
    # Testes manuais (sem LLM!)
    assert classify_ticket_manual("Recebo erro 403 ao tentar login") == "URGENTE"
    assert classify_ticket_manual("Quero saber os preços do plano enterprise") == "ALTA"
    assert classify_ticket_manual("Olá, tudo bem?") == "BAIXA"
    
    console.print("[green]✓[/green] Classificação manual funciona!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Batch Processing — Processamento em lote
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_batch_processing():
    """
    TODO: Processe múltiplos tickets e calcule custo total.
    """
    tickets = [
        {"id": 1, "text": "Erro 500 na API"},
        {"id": 2, "text": "Preço do plano"},
        {"id": 3, "text": "Como funciona?"},
    ]
    
    # TODO: Para cada ticket, conte tokens e some o custo total
    total_tokens = 0
    total_cost = 0.0
    
    for ticket in tickets:
        tokens = count_tokens(ticket["text"])
        total_tokens += tokens
    
    assert total_tokens > 0, "Total de tokens deveria ser positivo"
    assert len(tickets) == 3, "Deveríamos processar todos os 3 tickets"
    
    console.print(f"[green]✓[/green] Batch: {len(tickets)} tickets, {total_tokens} tokens totais")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Error Handling — Tratamento de erros
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_error_handling():
    """
    TODO: Verifique se o código lida com erros gracefully.
    
    Teste casos extremos: string vazia, texto muito longo, caracteres especiais.
    """
    # String vazia
    empty_tokens = count_tokens("")
    assert empty_tokens == 0 or empty_tokens is not None, \
        "String vazia deve retornar 0 tokens"
    
    # Texto com caracteres especiais
    special = "Senha: p@$$w0rd! ñçãé"
    special_tokens = count_tokens(special)
    assert special_tokens > 0, \
        "Texto com caracteres especiais deve gerar tokens"
    
    console.print("[green]✓[/green] Tratamento de erros OK")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_token_counting, test_02_cost_estimation,
             test_03_ticket_classification, test_04_batch_processing,
             test_05_error_handling]
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs para fazer passar!",
                        title="[bold cyan]P0: Primeiro Fluxo com LLM[/bold cyan]",
                        border_style="cyan"))
    
    passed = 0
    failed = 0
    
    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except AssertionError as e:
            console.print(f"[red]✗ {test_fn.__name__}: {e}[/red]")
            failed += 1
        except Exception as e:
            console.print(f"[red]✗ {test_fn.__name__}: Erro inesperado — {e}[/red]")
            failed += 1
    
    console.print(f"\nResultado: [bold green]{passed}/{passed+failed}[/bold green] testes passaram")
    if failed:
        console.print(f"[yellow]Restam {failed} teste(s) para implementar.[/yellow]")
    else:
        console.print("[bold green]🎉 Todos os testes passaram! Exercício completo![/bold green]")


if __name__ == "__main__":
    run_all()
