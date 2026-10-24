"""
Módulo 02-Fundamentos: Demonstração interativa dos conceitos básicos de LLM.

Este script mostra na prática:
- Como texto é tokenizado
- Como temperature afeta respostas
- Como prompts diferentes produzem resultados diferentes
- A diferença entre classificação (temp=0) e geração criativa (temp>0)
"""

import os
import json
import time


# Modelo LLM configuravel via ambiente (EXEMPLO, nao requisito).
# Troque por Claude/Gemini/Qwen/Ollama exportando MODEL no .env.
MODEL = os.getenv("MODEL", "gpt-4o-mini")

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def print_section(title: str) -> None:
    """Imprime um separador de seção."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_tokenization() -> None:
    """Demonstra como o BPE divide texto em tokens."""
    print_section("DEMO 1: Tokenização — Como texto vira números")

    textos = [
        "Hello, world!",
        "Olá, mundo! Como vai você?",
        "I don't know if this works",
        "Tokenização é divertida 🎉",
    ]

    print("Mesmo texto em idiomas diferentes gera quantidades diferentes de tokens:")
    print("-" * 50)

    for texto in textos:
        # Simulação visual — em produção usaria tiktoken
        palavras = texto.split()
        pontuacao = sum(1 for c in texto if c in '.,!?;:')
        # Estimativa grosseira: palavras ~1 token cada, pontuação separada
        tokens_estimados = len(palavras) + pontuacao
        print(f"  '{texto}'")
        print(f"    → ~{tokens_estimados} tokens (estimado)")
        print()

    print("💡 Por que importa?")
    print("   - Cada token custa dinheiro (ver tabela de preços)")
    print("   - Inglês usa menos tokens que português para mesma informação")
    print("   - Emojis contam como tokens!")


def demo_temperature() -> None:
    """Demonstra como temperature afeta as respostas."""
    if not HAS_OPENAI:
        print_section("DEMO 2: Temperature (OpenAI não disponível)")
        print("Instale a SDK: pip install openai")
        print("Configure: export OPENAI_API_KEY='sk-...'")
        return

    print_section("DEMO 2: Temperature — Criatividade vs Precisão")

    prompt_classificacao = "Classifique este ticket: 'Minha internet caiu há 3 horas'"
    prompt_criativo = "Escreva uma frase curta sobre tecnologia"

    print("\n📋 Prompt de CLASSIFICAÇÃO (temperature=0):")
    print(f"   '{prompt_classificacao}'")
    print("   → Esperamos SEMPRE a mesma resposta\n")

    try:
        client = OpenAI()
        resp1 = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt_classificacao}],
            temperature=0.0,
            max_tokens=10,
        )
        print(f"   Resposta 1: {resp1.choices[0].message.content.strip()}")

        resp2 = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt_classificacao}],
            temperature=0.0,
            max_tokens=10,
        )
        print(f"   Resposta 2: {resp2.choices[0].message.content.strip()}")

        same = resp1.choices[0].message.content == resp2.choices[0].message.content
        print(f"\n   ✅ Mesmas respostas? {'SIM' if same else 'NÃO'}")
        print("   → temperature=0 é determinístico (sempre igual)")
    except Exception as e:
        print(f"   ⚠️ Erro ao chamar API: {e}")

    print("\n🎨 Prompt CRIATIVO (temperature=1.0):")
    print(f"   '{prompt_criativo}'")
    print("   → Esperamos respostas DIFERENTES a cada chamada\n")

    try:
        for i in range(3):
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt_criativo}],
                temperature=1.0,
                max_tokens=20,
            )
            print(f"   Chamada {i+1}: {resp.choices[0].message.content.strip()}")
        print("\n   → temperature=1.0 gera variações (criativo)")
    except Exception as e:
        print(f"   ⚠️ Erro ao chamar API: {e}")


def demo_prompt_quality() -> None:
    """Demonstra como a qualidade do prompt afeta o resultado."""
    if not HAS_OPENAI:
        print_section("DEMO 3: Prompt Quality (OpenAI não disponível)")
        print("Instale a SDK: pip install openai")
        print("Configure: export OPENAI_API_KEY='sk-...'")
        return

    print_section("DEMO 3: Qualidade do Prompt — Vago vs Específico")

    textos = [
        {"id": "TKT-001", "assunto": "Não consigo acessar minha conta",
         "descricao": "Erro 403 ao tentar logar, já limpei cache"},
        {"id": "TKT-002", "assunto": "Site lento",
         "descricao": "O dashboard demora mais de 10 segundos para carregar"},
    ]

    prompts = {
        "VAGO": "Classifique este ticket.",
        "ESPECÍFICO": """Você é um classificador de tickets de suporte.
Classifique a prioridade deste ticket usando APENAS uma das opções: BAIXA, MEDIA ou ALTA.

Critérios:
- ALTA: problemas que impedem uso completo do sistema
- MEDIA: problemas parciais ou workarounds disponíveis
- BAIXA: dúvidas, sugestões ou problemas menores

Ticket:
Assunto: {assunto}
Descrição: {descricao}

Retorne APENAS a palavra: BAIXA, MEDIA ou ALTA""",
    }

    for nome_prompt, template in prompts.items():
        print(f"\n📝 Prompt {nome_prompt}:")
        print(f"   {template[:80]}...")

    print("\n" + "-" * 50)

    try:
        client = OpenAI()
        for i, ticket in enumerate(textos, 1):
            print(f"\n--- Ticket {i}: {ticket['assunto']} ---")
            for nome_prompt, template in prompts.items():
                prompt_final = template.format(**ticket)
                resp = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt_final}],
                    temperature=0.0,
                    max_tokens=10,
                )
                resposta = resp.choices[0].message.content.strip()
                print(f"   {nome_prompt:10s} → {resposta}")
    except Exception as e:
        print(f"\n   ⚠️ Erro ao chamar API: {e}")


def demo_cost_tracking() -> None:
    """Demonstra como rastrear custos por chamada."""
    print_section("DEMO 4: Rastreamento de Custos")

    precos = {
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},  # por 1M tokens
        "gpt-4o": {"input": 2.50, "output": 10.00},
    }

    print("Preços da OpenAI (por 1M tokens):")
    print("-" * 50)
    for modelo, preco in precos.items():
        print(f"  {modelo:12s} | Input: ${preco['input']:6.2f}/M | Output: ${preco['output']:6.2f}/M")

    print("\n" + "-" * 50)
    print("Exemplo prático — 100 chamadas com gpt-4o-mini:")
    print("-" * 50)

    input_tokens = 200      # por chamada
    output_tokens = 50      # por chamada
    n_chamadas = 100

    custo_input = (n_chamadas * input_tokens / 1_000_000) * precos["gpt-4o-mini"]["input"]
    custo_output = (n_chamadas * output_tokens / 1_000_000) * precos["gpt-4o-mini"]["output"]
    custo_total = custo_input + custo_output

    print(f"  Input:  {n_chamadas} × {input_tokens} tokens × ${precos['gpt-4o-mini']['input']}/1M = ${custo_input:.5f}")
    print(f"  Output: {n_chamadas} × {output_tokens} tokens × ${precos['gpt-4o-mini']['output']}/1M = ${custo_output:.5f}")
    print(f"  TOTAL:  ${custo_total:.5f} ({n_chamadas} chamadas)")

    custo_anual = custo_total * 30 * 12  # 100 chamadas/dia × 30 dias × 12 meses
    print(f"\n  Se fizer 100 chamadas/dia → ${custo_anual:.2f}/ano")
    print(f"  Se fizer 10.000 chamadas/dia → ${custo_anual * 100:.2f}/ano")

    print("\n💡 Lição: Em escala, cada token importa.")


def main() -> None:
    """Executa todas as demos."""
    print("╔" + "═" * 58 + "╗")
    print("║  FUNDAMENTOS DE IA E LLM — DEMONSTRAÇÕES PRÁTICAS       ║")
    print("╚" + "═" * 58 + "╝")

    print("\nEste módulo demonstra conceitos fundamentais na prática.")
    print("Execute cada demo para ver os conceitos em ação.\n")

    demo_tokenization()
    demo_temperature()
    demo_prompt_quality()
    demo_cost_tracking()

    print_section("Resumo")
    print("✅ Tokenização: texto → tokens (unidade de custo)")
    print("✅ Temperature: 0 = preciso, >0 = criativo")
    print("✅ Prompt quality: específico > vago")
    print("✅ Custo: conte sempre seus tokens")
    print("\nPróximo passo: Módulo 02 — Primeiro fluxo com LLM")


if __name__ == "__main__":
    main()
