"""
Módulo P0 — Teste do Exercício (Fundamentos)

Execute com: python modules/p0_fundamentals/test_exercise.py

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
# TESTE 1: Token Counting — Contagem de tokens funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_token_counting():
    """
    TODO: Implemente estimativa de contagem de tokens.
    
    Regra aproximada: ~4 caracteres por token em inglês,
    ~2 caracteres por token em português.
    """
    def estimate_tokens(text: str, language: str = "en") -> int:
        """Retorne número estimado de tokens baseado no idioma."""
        if not text.strip():
            return 0
        
        # Inglês: ~4 chars/token; Português: ~2.5 chars/token (mais acentos)
        chars_per_token = 4.0 if language == "en" else 2.5
        return max(1, round(len(text) / chars_per_token))
    
    english_text = "The quick brown fox jumps over the lazy dog."
    portuguese_text = "O rápido raposo marrom salta sobre o cão preguiçoso."
    
    en_tokens = estimate_tokens(english_text, "en")
    pt_tokens = estimate_tokens(portuguese_text, "pt")
    
    assert en_tokens > 0, \
        f"Tokens devem ser > 0, got {en_tokens}"
    assert pt_tokens > 0, \
        f"Tokens devem ser > 0, got {pt_tokens}"
    
    # Português tende a ter mais tokens por mesmo tamanho
    assert len(english_text) == len(portuguese_text), \
        "Textos devem ter mesmo comprimento"
    
    console.print(f"[green]✓[/green] Tokens: EN={en_tokens}, PT={pt_tokens}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Cost Estimation — Estimativa de custo correta?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_cost_estimation():
    """
    TODO: Calcule custo baseado em tokens e preço por 1K tokens.
    """
    def calculate_cost(tokens: int, price_per_1k: float) -> float:
        """Retorne custo em dólares dado número de tokens e preço por 1K."""
        return (tokens / 1000.0) * price_per_1k
    
    # GPT-4o: $0.01 por 1K input tokens
    gpt4_input_price = 0.01
    
    # Calcula custo para 10K tokens
    cost = calculate_cost(10000, gpt4_input_price)
    
    assert cost > 0, \
        f"Custo deve ser > 0, got {cost}"
    assert abs(cost - 0.10) < 0.001, \
        f"10K tokens a $0.01/1K = $0.10, got ${cost:.4f}"
    
    console.print(f"[green]✓[/green] Custo: 10K tokens = ${cost:.2f}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Prompt Structure — Estrutura de prompt válida?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_prompt_structure():
    """
    TODO: Valide estrutura de prompt (system/user/assistant).
    """
    def validate_prompt(messages: list) -> dict:
        """
        Retorne {'valid': bool, 'errors': [...], 'token_estimate': int}.
        
        Regras:
        - Primeiro message deve ser role='system' ou role='user'
        - Roles alternam corretamente (user→assistant→user...)
        - Content não pode ser vazio
        """
        errors = []
        token_estimate = 0
        
        if not messages:
            return {"valid": False, "errors": ["Lista vazia"], "token_estimate": 0}
        
        # Verificar primeiro message
        first_role = messages[0]["role"]
        if first_role not in ("system", "user"):
            errors.append(f"Primeiro message deve ser system/user, got {first_role}")
        
        # Verificar content não vazio e alternância
        for i, msg in enumerate(messages):
            if not msg.get("content", "").strip():
                errors.append(f"Message {i}: content vazio")
            token_estimate += len(msg.get("content", "")) // 4
            
            if i > 0:
                prev_role = messages[i-1]["role"]
                curr_role = msg["role"]
                # user/assistant devem alternar
                if prev_role == curr_role and prev_role in ("user", "assistant"):
                    errors.append(f"Messages {i-1} e {i} têm mesmo role '{curr_role}'")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "token_estimate": token_estimate,
        }
    
    valid_prompt = [
        {"role": "system", "content": "Você é um assistente útil."},
        {"role": "user", "content": "Como funciona o reembolso?"},
    ]
    
    invalid_prompt = [
        {"role": "user", "content": ""},  # Content vazio
        {"role": "assistant", "content": "Resposta"},  # Sem user antes
    ]
    
    result_valid = validate_prompt(valid_prompt)
    assert result_valid["valid"] == True, \
        "Prompt válido deve passar"
    
    result_invalid = validate_prompt(invalid_prompt)
    assert result_invalid["valid"] == False, \
        "Prompt inválido deve falhar"
    assert len(result_invalid["errors"]) > 0, \
        "Deve haver erros listados"
    
    console.print(f"[green]✓[/green] Prompt: valid ✓, invalid detected ({len(result_invalid['errors'])} errors)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Temperature Effect — Temperatura afeta saída?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_temperature_effect():
    """
    TODO: Simule efeito da temperatura na diversidade de saída.
    
    Temperatura alta → mais diversificado/criativo.
    Temperatura baixa → mais focado/determinístico.
    """
    import random
    
    def simulate_temperature(base_responses: list, temperature: float, n_samples: int = 100) -> dict:
        """
        Simule amostragem com temperatura.
        
        Low temp (0.1): quase sempre escolhe a resposta mais provável.
        High temp (1.0): distribuição mais uniforme.
        
        Retorne {'unique_responses': int, 'diversity_score': float}.
        """
        import random
        
        # Criar pesos baseados na temperatura
        # Low temp → peso alto para índice 0, baixo para outros
        # High temp → pesos mais equilibrados
        if temperature < 0.5:
            # Temperatura baixa: primeira resposta tem peso dominante
            weights = [1.0 - temperature] + [temperature / (len(base_responses) - 1)] * (len(base_responses) - 1)
        else:
            # Temperatura alta: pesos mais uniformes
            base_weight = 0.3
            spread = (1.0 - base_weight) / (len(base_responses) - 1)
            weights = [base_weight] + [spread] * (len(base_responses) - 1)
        
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Amostragem
        samples = random.choices(base_responses, weights=weights, k=n_samples)
        unique = len(set(samples))
        diversity = unique / len(base_responses)  # Normalizado 0-1
        
        return {
            "unique_responses": unique,
            "diversity_score": round(diversity, 3),
        }
    
    responses = ["A", "B", "C", "D", "E"]  # 5 respostas possíveis
    
    low_temp = simulate_temperature(responses, temperature=0.1)
    high_temp = simulate_temperature(responses, temperature=1.0)
    
    assert low_temp["unique_responses"] <= high_temp["unique_responses"], \
        f"Temperatura baixa deve ter menos diversidade: {low_temp['unique_responses']} vs {high_temp['unique_responses']}"
    
    assert high_temp["diversity_score"] > low_temp["diversity_score"], \
        "Score de diversidade deve ser maior com temperatura alta"
    
    console.print(f"[green]✓[/green] Temperatura: low={low_temp['unique_responses']} unique, "
                  f"high={high_temp['unique_responses']} unique")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Context Window — Janela de contexto limitada?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_context_window():
    """
    TODO: Limite mensagens dentro da janela de contexto.
    
    Se total de tokens > max_context, remova mensagens mais antigas.
    """
    def estimate_tokens(text: str) -> int:
        return len(text) // 4
    
    messages = [
        {"role": "system", "content": "Você é um assistente útil."},
        {"role": "user", "content": "Olá, preciso de ajuda."},
        {"role": "assistant", "content": "Claro! Como posso ajudar?"},
        {"role": "user", "content": "Quero saber sobre políticas de devolução."},
        {"role": "assistant", "content": "Nossas políticas de devolução permitem..."},
        {"role": "user", "content": "Em quanto tempo recebo o dinheiro?"},
        {"role": "assistant", "content": "O processo leva de 5 a 10 dias úteis."},
        {"role": "user", "content": "E se o produto estiver usado?"},
        {"role": "assistant", "content": "Produtos usados podem ter taxa reduzida."},
        {"role": "user", "content": "Preciso do nota fiscal?"},
    ]
    
    max_context_tokens = 150
    
    total_tokens = sum(estimate_tokens(m["content"]) for m in messages)
    
    # Truncar removendo mensagens mais antigas (exceto system)
    trimmed = []
    current_tokens = 0
    
    # Sempre manter o system prompt
    system_msg = messages[0] if messages and messages[0]["role"] == "system" else None
    if system_msg:
        sys_tokens = estimate_tokens(system_msg["content"])
        if sys_tokens <= max_context_tokens:
            trimmed.append(system_msg)
            current_tokens = sys_tokens
    
    # Adicionar mensagens da mais recente para a mais antiga até caber
    conversation_msgs = [m for m in messages[1:] if m["role"] != "system"]
    for msg in reversed(conversation_msgs):
        msg_tokens = estimate_tokens(msg["content"])
        if current_tokens + msg_tokens <= max_context_tokens:
            trimmed.append(msg)
            current_tokens += msg_tokens
    
    # Reordenar para ordem original
    trimmed.sort(key=lambda m: messages.index(m) if m in messages else 0)
    
    trimmed_tokens = sum(estimate_tokens(m["content"]) for m in trimmed)
    
    assert trimmed_tokens <= max_context_tokens, \
        f"Tokens após trim ({trimmed_tokens}) devem caber em {max_context_tokens}"
    assert len(trimmed) >= 2, \
        "Deve manter system + pelo menos uma interação"
    
    console.print(f"[green]✓[/green] Context: {total_tokens}→{trimmed_tokens} tokens, "
                  f"{len(trimmed)} mensagens mantidas")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_token_counting, test_02_cost_estimation,
             test_03_prompt_structure, test_04_temperature_effect,
             test_05_context_window]
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P0: Fundamentos[/bold cyan]",
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
