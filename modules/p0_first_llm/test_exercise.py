"""
Módulo P0 — Teste do Exercício

Execute com: python modules/p0_first_llm/test_exercise.py

Você precisa IMPLEMENTAR as funções marcadas com TODO para fazer os testes passarem.
Cada teste falha até você escrever o código correto.

Importante: todas as funções auxiliares já existem em shared/cost.py.
Use-as importando: from shared.cost import count_tokens, estimate_cost, format_cost
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
    
    TODO: Use count_tokens() de shared.cost para contar tokens do texto abaixo.
    Dica: importado automaticamente acima como 'from shared.cost import count_tokens'
    Cada ~4 caracteres em inglês ≈ 1 token.
    """
    text = "Não consigo acessar minha conta. Recebo erro 403."
    
    # TODO: Substitua None pelo resultado real de count_tokens(text)
    token_count = count_tokens(text)  # ← Mude aqui
    
    assert token_count is not None and token_count > 0, \
        f"Token count deve ser > 0, got {token_count}"
    assert isinstance(token_count, int), \
        f"Token count deve ser int, got {type(token_count).__name__}"
    
    console.print(f"[green]✓[/green] Tokens contados: {token_count}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Cost Estimation — Quanto custa essa chamada?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_cost_estimation():
    """
    gpt-4o-mini: $0.15/1M tokens input, $0.60/1M tokens output
    
    TODO: Calcule o custo estimado usando estimate_cost() de shared.cost.
    Dica: importado automaticamente acima como 'from shared.cost import estimate_cost'
    """
    prompt_tokens = 50
    completion_tokens = 10
    
    # TODO: Calcule o custo usando estimate_cost(prompt_tokens, completion_tokens, model="gpt-4o-mini")
    cost = estimate_cost(prompt_tokens, completion_tokens, model="gpt-4o-mini")  # ← Mude aqui
    
    assert cost is not None and cost >= 0, \
        f"Custo deve ser >= 0, got {cost}"
    assert cost < 1.0, \
        f"Custo de uma única chamada deveria ser centavos, got ${cost:.4f}"
    
    console.print(f"[green]✓[/green] Custo estimado: ${cost:.8f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Ticket Classification — Classifique corretamente
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_ticket_classification():
    """
    TODO: Escreva uma função que classifica tickets por prioridade usando palavras-chave.
    
    Regras (categorias devem bater com run.py):
    - "erro", "500", "não acess", "403", "falha", "crítico" → "URGENTE"
    - "preço", "enterprise", "cotar", "dúvida", "informação" → "NORMAL"
    - "feedback", "sugestão", "pergunta geral" → "BAIXA"
    
    Dica: use ticket_text.lower() para comparar sem diferenciar maiúsculas/minúsculas.
    """
    def classify_ticket_manual(ticket_text: str) -> str:
        """TODO: Implemente esta função com base nas regras acima."""
        text = ticket_text.lower()
        
        urgent_keywords = ["erro", "500", "não acess", "403", "falha", "crítico"]
        normal_keywords = ["preço", "enterprise", "cotar", "dúvida", "informação"]
        baixa_keywords = ["feedback", "sugestão", "pergunta geral"]
        
        for kw in urgent_keywords:
            if kw in text:
                return "URGENTE"
        for kw in normal_keywords:
            if kw in text:
                return "NORMAL"
        for kw in baixa_keywords:
            if kw in text:
                return "BAIXA"
        return "BAIXA"
    
    # Testes manuais (sem LLM!)
    result1 = classify_ticket_manual("Recebo erro 403 ao tentar login")
    assert result1 == "URGENTE", f"Esperava 'URGENTE', got '{result1}'"
    
    result2 = classify_ticket_manual("Quero saber os preços do plano enterprise")
    assert result2 == "NORMAL", f"Esperava 'NORMAL', got '{result2}'"
    
    result3 = classify_ticket_manual("Olá, tudo bem? Sugestão de melhoria.")
    assert result3 == "BAIXA", f"Esperava 'BAIXA', got '{result3}'"
    
    console.print("[green]✓[/green] Classificação manual funciona!")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Batch Processing — Processamento em lote
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_batch_processing():
    """
    TODO: Processe múltiplos tickets e calcule custo total.
    
    Dica: use count_tokens() e estimate_cost() de shared.cost.
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
        # TODO: Estime custo para este ticket (~20 tokens de output)
        total_cost += estimate_cost(tokens, 20, model="gpt-4o-mini")
    
    assert total_tokens > 0, f"Total de tokens deveria ser positivo, got {total_tokens}"
    assert len(tickets) == 3, f"Deveríamos processar todos os 3 tickets, got {len(tickets)}"
    assert total_cost < 1.0, f"Custo total deveria ser baixo, got ${total_cost:.4f}"
    
    console.print(f"[green]✓[/green] Batch: {len(tickets)} tickets, {total_tokens} tokens, ~${total_cost:.6f}")


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
        f"String vazia deve retornar 0 tokens, got {empty_tokens}"
    
    # Texto com caracteres especiais
    special = "Senha: p@$$w0rd! ñçãé"
    special_tokens = count_tokens(special)
    assert special_tokens > 0, \
        f"Texto com caracteres especiais deve gerar tokens, got {special_tokens}"
    
    # Texto muito longo (simula ataque de prompt injection)
    long_text = "a" * 10000
    long_tokens = count_tokens(long_text)
    assert long_tokens > 0, \
        f"Texto longo deve gerar tokens, got {long_tokens}"
    
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
