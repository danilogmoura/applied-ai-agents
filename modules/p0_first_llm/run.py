"""
Módulo P0 — Primeiro Fluxo com LLM

Automação de tarefa repetitiva via API OpenAI.
Foco: chamadas HTTP/SDK, proteção de chaves, tratamento de exceções, cálculo de custos.

Problema: Você recebeu a tarefa de automatizar a classificação de tickets de suporte.
Atualmente, um humano lê cada ticket e marca como "urgente", "normal" ou "baixa".
Como fazer isso com IA de forma segura e econômica?
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao Python para ele encontrar os módulos compartilhados (shared/)
# Sem isso, 'from shared.cost import ...' falharia porque Python procura só na pasta atual
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from shared.logging_config import setup_logging, measure_latency
from shared.cost import count_tokens, estimate_cost, format_cost, summarize_usage
from shared.security import get_required_secret, validate_secrets

console = Console()
logger = setup_logging("p0_first_llm")

# Modelo configurável via variável de ambiente (fallback para gpt-4o-mini)
MODEL = os.getenv("MODEL", "gpt-4o-mini")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DADOS DE EXEMPLO — Tickets de suporte
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SAMPLE_TICKETS = [
    {
        "id": 1,
        "subject": "Não consigo acessar minha conta",
        "description": "Recebo erro 403 ao tentar login. Já tentei resetar senha mas não chega o email.",
        "priority_guess": None,
    },
    {
        "id": 2,
        "subject": "Quero saber os preços do plano enterprise",
        "description": "Somos uma empresa de 500 funcionários e precisamos cotar para nosso time.",
        "priority_guess": None,
    },
    {
        "id": 3,
        "subject": "API está retornando 500 intermitentemente",
        "description": "Desde às 14h temos erros 500 em ~30% das requisições. Impacta produção.",
        "priority_guess": None,
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CLASSIFICADOR DE TICKETS COM LLM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def classify_ticket(ticket: dict, model: str = "gpt-4o-mini") -> dict:
    """
    Classifica um ticket usando LLM.
    
    Args:
        ticket: Dicionário com id, subject e description.
        model: Modelo OpenAI a utilizar.
    
    Returns:
        Ticket com campo 'priority' adicionado.
    """
    from openai import OpenAI
    
    # Valida secret obrigatória
    api_key = get_required_secret("OPENAI_API_KEY")
    
    client = OpenAI(api_key=api_key)
    
    prompt = f"""Classifique a prioridade deste ticket de suporte em uma única palavra:
- URGENTE: problemas de produção, falhas críticas, dados em risco
- NORMAL: dúvidas, solicitações de informação, problemas não-críticos
- BAIXA: feedback, sugestões, perguntas gerais

Ticket:
Assunto: {ticket['subject']}
Descrição: {ticket['description']}

Responda APENAS com uma destas palavras: URGENTE, NORMAL ou BAIXA."""

    messages = [{"role": "user", "content": prompt}]
    input_tokens = count_tokens(prompt, model)
    
    try:
        with measure_latency(logger, "classify_ticket") as metrics:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=20,
                temperature=0,  # ← Sempre 0 para classificação consistente
            )
        
        output_text = response.choices[0].message.content.strip().upper()
        output_tokens = count_tokens([{"role": "assistant", "content": output_text}], model)
        
        cost = estimate_cost(input_tokens, output_tokens, model=model)
        
        result = {**ticket, "priority": output_text, "cost": cost}
        
        logger.info(
            "ticket_classified",
            extra={"extra_data": {
                "ticket_id": ticket["id"],
                "priority": output_text,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
            }},
        )
        
        return result
    
    except Exception as e:
        error_type = type(e).__name__
        logger.error(f"Erro ao classificar ticket {ticket['id']}: {e}")
        
        # Mensagem de erro orientativa para o iniciante
        if "AuthenticationError" in error_type or "API key" in str(e):
            raise RuntimeError(
                f"❌ Erro de autenticação no ticket {ticket['id']}. "
                f"Verifique se OPENAI_API_KEY está definida no .env. "
                f"Leia SETUP.md para configurar."
            ) from e
        elif "RateLimitError" in error_type:
            raise RuntimeError(
                f"⏳ Rate limit atingido no ticket {ticket['id']}. "
                f"A OpenAI limita requisições por minuto. Espere alguns segundos e tente novamente."
            ) from e
        else:
            raise


def classify_batch(tickets: list[dict], model: str = None) -> list[dict]:
    """Classifica lote de tickets e retorna resumo de custos."""
    model = model or MODEL  # Usa variável configurável ou fallback
    
    results = []
    total_cost = 0.0
    total_input = 0
    total_output = 0
    
    for ticket in tickets:
        console.print(f"\n[bold cyan]Processando ticket #{ticket['id']}...[/]")
        result = classify_ticket(ticket, model)
        results.append(result)
        total_cost += result["cost"]
        
        # Acumula tokens para relatório final
        prompt = f"{ticket['subject']} {ticket['description']}"
        total_input += count_tokens(prompt, model)
        total_output += count_tokens(result["priority"], model)
    
    # Relatório de custos
    console.print("\n" + "=" * 60)
    console.print("[bold green]📊 RELATÓRIO DE CUSTOS[/]")
    console.print("=" * 60)
    console.print(f"Modelo: {model}")
    console.print(f"Tickets processados: {len(results)}")
    console.print(f"Custo total estimado: [bold]{format_cost(total_cost)}[/]")
    console.print(f"Custo por ticket: [bold]{format_cost(total_cost / len(results)) if results else '$0'}[/]")
    console.print(f"⚠️  Custo estimado para 1000 tickets: ~{format_cost(total_cost * 1000 / len(results) if results else 0)}")
    console.print("=" * 60)
    
    return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# VERSÃO SEM IA — Regras simples (para comparação no P1)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def classify_with_rules(ticket: dict) -> str:
    """
    Classificação baseada em regras simples (sem IA).
    
    Esta função será comparada com a versão LLM no módulo P1.
    """
    text = f"{ticket['subject']} {ticket['description']}".lower()
    
    urgent_keywords = ["erro", "falha", "produção", "down", "500", "403", 
                       "crítico", "urgente", "break", "outage", "perda"]
    normal_keywords = ["preço", "plano", "cotar", "como", "não consigo", "ajuda"]
    
    for keyword in urgent_keywords:
        if keyword in text:
            return "URGENTE"
    
    for keyword in normal_keywords:
        if keyword in text:
            return "NORMAL"
    
    return "BAIXA"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa o fluxo completo de classificação de tickets."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO P0 — Primeiro Fluxo com LLM[/]\n\n"
        "Automação de classificação de tickets de suporte.\n"
        "Comparação: IA vs Regras simples.",
        title="🚀 AI Agents Course",
        border_style="cyan",
    ))
    
    # Valida ambiente
    try:
        validate_secrets(["OPENAI_API_KEY"])
        console.print("[green]✓ Chaves de API validadas[/]")
    except EnvironmentError as e:
        console.print(f"[red]✗ {e}[/]")
        console.print("[yellow]Crie um arquivo .env com OPENAI_API_KEY=[/]")
        sys.exit(1)
    
    console.print(f"[cyan]Modelo: {MODEL} (configure via MODEL env var)[/]\n")
    
    # ━━ Versão com IA ━━
    console.print("[bold blue]▸ Executando classificação com LLM...[/]")
    ai_results = classify_batch(SAMPLE_TICKETS, MODEL)
    
    # ━━ Versão com regras ━━
    console.print("\n[bold magenta]▸ Executando classificação com regras...[/]")
    rule_results = [classify_with_rules(t) for t in SAMPLE_TICKETS]
    
    # ━━ Comparação ━━
    console.print("\n" + "=" * 60)
    console.print("[bold green]📋 RESULTADOS[/]")
    console.print("=" * 60)
    
    for ai, rule, ticket in zip(ai_results, rule_results, SAMPLE_TICKETS):
        match = "✓" if ai["priority"] == rule else "△"
        console.print(f"\n[bold]Ticket #{ticket['id']}: {ticket['subject']}[/]")
        console.print(f"  IA     : {ai['priority']} [{format_cost(ai['cost'])}]")
        console.print(f"  Regras : {rule} [$0.00000000]")
        console.print(f"  Match  : {match}")
    
    console.print("\n" + "=" * 60)
    console.print("[dim]💡 Próximo passo: Módulo P1 — Análise de viabilidade[/]")
    console.print("[dim]   Compare custo vs latência entre IA e regras.[/]")
    console.print("=" * 60)


if __name__ == "__main__":
    main()
