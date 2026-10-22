"""
Módulo P1 — Análise de Viabilidade

Criação de memorando técnico que compara IA com regras simples.
Decisão baseada em latência e custo reais medidos.

Problema: Seu gestor quer saber se vale a pena usar IA para classificar tickets.
Você precisa entregar um memo objetivo com dados reais: latência, custo, acurácia.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from shared.logging_config import setup_logging, measure_latency
from shared.cost import count_tokens, estimate_cost, format_cost
from shared.security import get_required_secret

console = Console()
logger = setup_logging("p1_feasibility")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RESULTADOS DE TESTE — Simulação de benchmarks
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class BenchmarkResult:
    """Resultado de benchmark de uma abordagem."""
    approach: str           # "IA" ou "Regras"
    avg_latency_ms: float   # Latência média em ms
    p95_latency_ms: float   # Latência 95º percentil
    cost_per_call: float    # Custo por chamada
    total_cost_10k_calls: float  # Custo estimado para 10k chamadas
    accuracy: Optional[float] = None  # Acurácia (se conhecida)
    maintenance_hours: float = 0  # Horas de manutenção estimada/mês


def run_benchmarks(n_samples: int = 5, model: str = "gpt-4o-mini") -> dict[str, BenchmarkResult]:
    """
    Executa benchmarks reais contra ambas as abordagens.
    
    Args:
        n_samples: Número de amostras para testar.
        model: Modelo LLM a testar.
    
    Returns:
        Dicionário {approach: BenchmarkResult}.
    """
    from openai import OpenAI
    
    api_key = get_required_secret("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    test_prompts = [
        "Não consigo acessar minha conta, erro 403",
        "Quero saber preços do plano enterprise",
        "API retornando 500 intermitentemente",
        "Sugestão: adicionar modo escuro",
        "Meu servidor está fora do ar há 2 horas",
        "Como faço para exportar meus dados?",
        "Erro ao fazer upload de arquivo PDF",
        "Gostaria de cancelar minha assinatura",
        "Database connection timeout frequente",
        "Quando será lançada a versão mobile?",
    ]
    
    results: dict[str, BenchmarkResult] = {
        "IA": BenchmarkResult(approach="IA (LLM)", avg_latency_ms=0, p95_latency_ms=0, 
                               cost_per_call=0, total_cost_10k_calls=0),
        "Regras": BenchmarkResult(approach="Regras (if/else)", avg_latency_ms=0, p95_latency_ms=0,
                                   cost_per_call=0, total_cost_10k_calls=0),
    }
    
    ia_latencies = []
    ia_costs = []
    rule_latencies = []
    
    console.print(f"\n[bold cyan]Executando benchmarks com {n_samples} amostras...[/]\n")
    
    for i in range(min(n_samples, len(test_prompts))):
        prompt = test_prompts[i]
        
        # ━━ Benchmark IA ━━
        start = time.perf_counter()
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": f"Classifique: {prompt}"}],
                max_tokens=10,
                temperature=0,
            )
            latency_ms = (time.perf_counter() - start) * 1000
            input_tok = count_tokens([{"role": "user", "content": prompt}], model)
            output_tok = len(response.choices[0].message.content.encode())
            cost = estimate_cost(input_tok, output_tok, model)
            
            ia_latencies.append(latency_ms)
            ia_costs.append(cost)
            
            console.print(f"  [cyan]IA[/] #{i+1}: {latency_ms:.0f}ms | {format_cost(cost)}")
        except Exception as e:
            console.print(f"  [red]IA[/] #{i+1}: ERRO — {e}")
        
        # ━━ Benchmark Regras ━━
        start = time.perf_counter()
        
        def classify_rule(text: str) -> str:
            t = text.lower()
            if any(w in t for w in ["erro", "falha", "produção", "500", "down"]):
                return "URGENTE"
            elif any(w in t for w in ["preço", "como", "quero"]):
                return "NORMAL"
            return "BAIXA"
        
        classify_rule(prompt)
        latency_ms = (time.perf_counter() - start) * 1000
        rule_latencies.append(latency_ms)
        
        console.print(f"  [magenta]Regras[/] #{i+1}: {latency_ms:.1f}µs | $0.00000000")
    
    # Calcula estatísticas
    if ia_latencies:
        ia_latencies.sort()
        results["IA"].avg_latency_ms = sum(ia_latencies) / len(ia_latencies)
        results["IA"].p95_latency_ms = ia_latencies[int(len(ia_latencies) * 0.95)] if len(ia_latencies) > 1 else ia_latencies[0]
        results["IA"].cost_per_call = sum(ia_costs) / len(ia_costs)
        results["IA"].total_cost_10k_calls = results["IA"].cost_per_call * 10_000
    
    if rule_latencies:
        results["Regras"].avg_latency_ms = sum(rule_latencies) / len(rule_latencies) * 1000  # µs → ms
        results["Regras"].p95_latency_ms = max(rule_latencies) / 1000 if rule_latencies else 0
    
    # Estimativas conservadoras
    results["IA"].maintenance_hours = 5.0  # Manutenção de prompts + monitoramento
    results["Regras"].maintenance_hours = 2.0  # Apenas ajuste de keywords
    
    return results


def generate_memorandum(benchmarks: dict[str, BenchmarkResult]) -> str:
    """
    Gera memorando técnico com recomendação baseada em dados.
    
    Returns:
        Texto do memorando pronto para enviar ao gestor.
    """
    ia = benchmarks["IA"]
    rules = benchmarks["Regras"]
    
    # Critérios de decisão
    COST_THRESHOLD = 50.0  # USD/mês
    LATENCY_THRESHOLD_MS = 2000  # ms
    
    cost_viable = ia.total_cost_10k_calls < COST_THRESHOLD
    latency_acceptable = ia.avg_latency_ms < LATENCY_THRESHOLD_MS
    
    if cost_viable and latency_acceptable:
        recommendation = "RECOMENDADO — Usar IA"
        reasoning = (
            "O custo é aceitável (<$50/mês para 10k chamadas) "
            "e a latência está dentro do limite aceitável."
        )
    elif cost_viable:
        recommendation = "CONDICIONAL — Usar IA com otimizações"
        reasoning = (
            "Custo aceitável, mas latência elevada. "
            "Considere caching de prompts ou modelo menor (gpt-4o-mini)."
        )
    elif latency_acceptable:
        recommendation = "NÃO RECOMENDADO — Custos elevados"
        reasoning = (
            "Latência ok, mas custo excede limite. "
            "Prefira regras simples até reduzir volume."
        )
    else:
        recommendation = "NÃO RECOMENDADO — Use regras simples"
        reasoning = (
            "Tanto custo quanto latência excedem limites. "
            "Implemente com if/else e reavalie quando volume crescer."
        )
    
    memo = f"""
{'='*70}
MEMORANDO TÉCNICO — Análise de Viabilidade: IA vs Regras
{'='*70}

DATA: {time.strftime("%Y-%m-%d %H:%M")}
AUTOR: Sistema de Análise de Agentes IA

OBJETIVO
--------
Determinar se justifica o uso de LLM para classificação automática
de tickets de suporte versus implementação com regras simples.

BENCHMARKS EXECUTADOS
---------------------
                    | IA (gpt-4o-mini)     | Regras (if/else)
--------------------|----------------------|-------------------
Latência média      | {ia.avg_latency_ms:>10.0f}ms       | {rules.avg_latency_ms:>10.1f}ms
P95 latência        | {ia.p95_latency_ms:>10.0f}ms       | {rules.p95_latency_ms:>10.1f}ms
Custo/call          | {ia.cost_per_call:>10.8f}      | {rules.cost_per_call:>10.8f}
Custo (10k calls)   | {ia.total_cost_10k_calls:>10.2f}      | {rules.total_cost_10k_calls:>10.2f}
Manutenção/mês       | {ia.maintenance_hours:>10.1f}h      | {rules.maintenance_hours:>10.1f}h

CRITÉRIOS DE DECISÃO
--------------------
• Limite de custo: ${COST_THRESHOLD}/mês (10k chamadas)
• Limite de latência: {LATENCY_THRESHOLD_MS}ms

RESULTADO
---------
✅ Custo viável: {'SIM' if cost_viable else 'NÃO'} (${ia.total_cost_10k_calls:.2f} < ${COST_THRESHOLD})
✅ Latência aceitável: {'SIM' if latency_acceptable else 'NÃO'} ({ia.avg_latency_ms:.0f}ms < {LATENCY_THRESHOLD_MS}ms)

RECOMENDAÇÃO: {recommendation}

JUSTIFICATIVA:
{reasoning}

RISCOS MITIGADOS
----------------
• Custo: Monitoramento contínuo com alertas em shared/cost.py
• Segurança: Chaves protegidas via python-dotenv (shared/security.py)
• Observabilidade: Logs estruturados com métricas de tokens (shared/logging_config.py)
• Governança: Human-in-the-loop para ações críticas (shared/governance.py)

PRÓXIMOS PASSOS
---------------
1. Se recomendado: Implementar fluxo P0 e evoluir para P2 (RAG)
2. Se condicional: Adicionar cache de respostas e medir melhoria
3. Se não recomendado: Implementar regras + monitorar crescimento de volume

{'='*70}
"""
    
    return memo


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa análise de viabilidade completa."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO P1 — Análise de Viabilidade[/]\n\n"
        "Memorando técnico comparando IA vs Regras.\n"
        "Decisão baseada em benchmarks reais.",
        title="📊 AI Agents Course",
        border_style="cyan",
    ))
    
    # Valida ambiente
    try:
        from shared.security import validate_secrets
        validate_secrets(["OPENAI_API_KEY"])
        console.print("[green]✓ Ambiente validado[/]")
    except EnvironmentError as e:
        console.print(f"[red]✗ {e}[/]")
        sys.exit(1)
    
    model = get_required_secret("DEFAULT_MODEL", "gpt-4o-mini")
    
    # Executa benchmarks
    console.print("\n[bold blue]▸ Rodando benchmarks...[/]")
    benchmarks = run_benchmarks(n_samples=5, model=model)
    
    # Exibe tabela comparativa
    table = Table(title="Benchmark Comparativo")
    table.add_column("Métrica", style="cyan")
    table.add_column("IA (gpt-4o-mini)", justify="right")
    table.add_column("Regras (if/else)", justify="right")
    
    table.add_row("Latência média", f"{benchmarks['IA'].avg_latency_ms:.0f}ms", 
                  f"{benchmarks['Regras'].avg_latency_ms:.1f}ms")
    table.add_row("P95 Latência", f"{benchmarks['IA'].p95_latency_ms:.0f}ms",
                  f"{benchmarks['Regras'].p95_latency_ms:.1f}ms")
    table.add_row("Custo/call", format_cost(benchmarks['IA'].cost_per_call),
                  format_cost(benchmarks['Regras'].cost_per_call))
    table.add_row("Custo (10k calls)", f"${benchmarks['IA'].total_cost_10k_calls:.2f}",
                  f"${benchmarks['Regras'].total_cost_10k_calls:.2f}")
    table.add_row("Manutenção/mês", f"{benchmarks['IA'].maintenance_hours}h",
                  f"{benchmarks['Regras'].maintenance_hours}h")
    
    console.print(table)
    
    # Gera e exibe memorando
    console.print("\n[bold green]▸ Gerando memorando técnico...[/]")
    memo = generate_memorandum(benchmarks)
    
    console.print(Panel(memo, title="📄 Memorando Técnico", border_style="green"))
    
    # Salva memorando
    memo_path = Path(__file__).parent / "memorando.md"
    memo_path.write_text(memo)
    console.print(f"\n[dim]💾 Memorando salvo em: {memo_path}[/]")
    
    console.print("\n[dim]💡 Próximo passo: Módulo P2 — Pipeline RAG[/]")


if __name__ == "__main__":
    main()
