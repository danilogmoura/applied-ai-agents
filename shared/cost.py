"""
Estimativa de custos de tokens usando tiktoken.

Este módulo fornece funções para calcular o custo estimado de chamadas
a LLMs baseado no número de tokens e preços por modelo.

Uso:
    >>> from shared.cost import estimate_cost, TOKEN_PRICES
    >>> tokens_input = count_tokens("Olá mundo!", model="gpt-4o-mini")
    >>> custo = estimate_cost(tokens_input, 100, model="gpt-4o-mini")
    >>> print(f"Custo estimado: ${custo:.6f}")
"""

from __future__ import annotations

import tiktoken

# Preços por modelo (por 1M de tokens) — atualizados em 2024-10
# Fonte: https://openai.com/api/pricing/
TOKEN_PRICES: dict[str, dict[str, float]] = {
    "gpt-4o": {"input": 2.50, "output": 10.00, "cache_read": 1.25},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60, "cache_read": 0.075},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00, "cache_read": 5.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50, "cache_read": 0.25},
    # Anthropic
    "claude-3-5-sonnet": {"input": 3.00, "output": 15.00, "cache_read": 3.75},
    "claude-3-haiku": {"input": 0.25, "output": 1.25, "cache_read": 0.30},
}


def get_encoding(model: str = "gpt-4o-mini") -> tiktoken.Encoding:
    """Retorna o codificador de tokens apropriado para o modelo."""
    if "gpt-4o" in model or "gpt-3.5" in model:
        return tiktoken.get_encoding("cl100k_base")
    elif "gpt-4" in model:
        return tiktoken.get_encoding("p50k_base")
    else:
        # Fallback para cl100k_base (mais comum)
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str | list[dict], model: str = "gpt-4o-mini") -> int:
    """
    Conta o número de tokens em um texto ou lista de mensagens.
    
    Args:
        text: Texto simples ou lista de mensagens OpenAI formatadas.
        model: Modelo para determinar o codificador.
    
    Returns:
        Número aproximado de tokens.
    """
    enc = get_encoding(model)
    
    if isinstance(text, list):
        # Formato de mensagens OpenAI
        tokens_per_message = 3
        tokens_per_name = 1
        total = 0
        for msg in text:
            total += tokens_per_message
            for key, value in msg.items():
                if isinstance(value, str):
                    total += len(enc.encode(value))
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict) and item.get("type") == "text":
                            total += len(enc.encode(item.get("text", "")))
        total += tokens_per_name  # nome do assistente
        return total
    else:
        return len(enc.encode(text))


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    cached_tokens: int = 0,
    model: str = "gpt-4o-mini",
) -> float:
    """
    Estima o custo em USD para uma chamada de LLM.
    
    Args:
        input_tokens: Tokens na entrada (prompt).
        output_tokens: Tokens na saída (resposta).
        cached_tokens: Tokens servidos do cache de pré-visualização.
        model: Modelo utilizado.
    
    Returns:
        Custo estimado em dólares americanos.
    """
    prices = TOKEN_PRICES.get(model)
    if not prices:
        # Estimativa genérica se modelo não estiver na tabela
        return (input_tokens + output_tokens) * 0.0001
    
    cost = 0.0
    cost += (input_tokens - cached_tokens) * prices["input"] / 1_000_000
    cost += cached_tokens * prices.get("cache_read", prices["input"]) / 1_000_000
    cost += output_tokens * prices["output"] / 1_000_000
    
    return round(cost, 8)


def format_cost(cost: float) -> str:
    """Formata custo para exibição amigável."""
    if cost < 0.0001:
        return f"${cost:.8f}"
    elif cost < 0.01:
        return f"${cost:.6f}"
    else:
        return f"${cost:.4f}"


def summarize_usage(input_tokens: int, output_tokens: int, model: str) -> dict:
    """
    Gera resumo completo de uso incluindo custo.
    
    Returns:
        Dicionário com tokens, custo e preço unitário.
    """
    cost = estimate_cost(input_tokens, output_tokens, model=model)
    prices = TOKEN_PRICES.get(model, {})
    
    return {
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost_usd": cost,
        "price_per_million_input": prices.get("input", "N/A"),
        "price_per_million_output": prices.get("output", "N/A"),
    }
