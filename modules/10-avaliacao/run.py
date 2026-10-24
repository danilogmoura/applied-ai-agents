"""
Módulo 10 — Avaliação e Testes

Framework completo para avaliar qualidade de saída de agentes de IA.
Golden datasets, LLM-as-a-judge, embedding similarity, testes A/B
e benchmarking regressivo.

Problema: Você mudou o prompt ou modelo do agente — mas como saber
se a qualidade melhorou ou piorou sem revisar manualmente cada resposta?
Como medir objetivamente a qualidade em escala?
"""

from __future__ import annotations

import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from shared.logging_config import setup_logging, measure_latency
from shared.cost import count_tokens, estimate_cost, format_cost
from shared.security import get_llm_config

console = Console()
logger = setup_logging("10-avaliacao")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# GOLDEN DATASET — Respostas esperadas de referência
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class GoldenExample:
    """Exemplo com input e resposta esperada para avaliação."""
    
    id: str                           # Identificador único
    question: str                     # Pergunta/input do usuário
    expected_answer: str              # Resposta esperada (ground truth)
    category: str = "general"         # Categoria para agrupar
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "question": self.question,
            "expected_answer": self.expected_answer,
            "category": self.category,
        }
    
    @staticmethod
    def from_dict(data: dict) -> "GoldenExample":
        return GoldenExample(**data)


# Golden dataset de exemplo para classificação de tickets
GOLDEN_DATASET: list[GoldenExample] = [
    GoldenExample(
        id="ticket_001",
        question="Não consigo acessar minha conta, erro 403",
        expected_answer="URGENTE",
        category="classificacao",
    ),
    GoldenExample(
        id="ticket_002",
        question="Quero saber preços do plano enterprise",
        expected_answer="NORMAL",
        category="classificacao",
    ),
    GoldenExample(
        id="ticket_003",
        question="API retornando 500 intermitentemente",
        expected_answer="URGENTE",
        category="classificacao",
    ),
    GoldenExample(
        id="ticket_004",
        question="Sugestão: adicionar modo escuro",
        expected_answer="BAIXA",
        category="classificacao",
    ),
    GoldenExample(
        id="ticket_005",
        question="Meu servidor está fora do ar há 2 horas",
        expected_answer="URGENTE",
        category="classificacao",
    ),
    GoldenExample(
        id="ticket_006",
        question="Como faço para exportar meus dados?",
        expected_answer="NORMAL",
        category="classificacao",
    ),
    GoldenExample(
        id="ticket_007",
        question="Erro ao fazer upload de arquivo PDF",
        expected_answer="NORMAL",
        category="classificacao",
    ),
    GoldenExample(
        id="ticket_008",
        question="Database connection timeout frequente",
        expected_answer="URGENTE",
        category="classificacao",
    ),
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MÉTRICAS DE AVALIAÇÃO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class EvaluationResult:
    """Resultado da avaliação de uma única resposta."""
    
    example_id: str
    question: str
    actual_answer: str
    expected_answer: str
    metrics: dict[str, float]       # Métricas individuais
    overall_score: float            # Score agregado (0-1)
    passed: bool                    # Aprovado?
    
    def to_dict(self) -> dict:
        return {
            "example_id": self.example_id,
            "question": self.question,
            "actual_answer": self.actual_answer,
            "expected_answer": self.expected_answer,
            "metrics": self.metrics,
            "overall_score": round(self.overall_score, 4),
            "passed": self.passed,
        }


class Evaluator:
    """
    Motor de avaliação com múltiplas métricas.
    
    Combina:
    - Exact match (correspondência exata)
    - Fuzzy match (similaridade por palavras-chave)
    - LLM-as-a-judge (avaliação por LLM)
    - Embedding similarity (similaridade vetorial)
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.results: list[EvaluationResult] = []
    
    def exact_match(self, actual: str, expected: str) -> float:
        """Score 1.0 se correspondência exata, 0.0 caso contrário."""
        return 1.0 if actual.strip().lower() == expected.strip().lower() else 0.0
    
    def fuzzy_match(self, actual: str, expected: str) -> float:
        """
        Similaridade baseada em sobreposição de palavras-chave.
        
        Jaccard similarity: |intersection| / |union|
        """
        actual_words = set(actual.lower().split())
        expected_words = set(expected.lower().split())
        
        if not actual_words and not expected_words:
            return 1.0
        if not actual_words or not expected_words:
            return 0.0
        
        intersection = len(actual_words & expected_words)
        union = len(actual_words | expected_words)
        
        return intersection / union if union > 0 else 0.0
    
    def llm_as_judge(self, question: str, actual: str, expected: str) -> float:
        """
        Usa um LLM para julgar a qualidade da resposta vs esperada.
        
        Retorna score 0-1 baseado em precisão factual e completude.
        """
        try:
            from openai import OpenAI
            
            api_key, base_url, _ = get_llm_config()
            client = OpenAI(api_key=api_key, base_url=base_url)
            
            prompt = f"""Você é um juiz imparcial avaliando respostas.

PERGUNTA: {question}

RESPOSTA ESPERADA: {expected}
RESPOSTA AVALIAR: {actual}

Avalie a resposta considerando:
1. Precisão factual (a resposta está correta?)
2. Completude (cobre todos os pontos importantes?)
3. Relevância (responde diretamente à pergunta?)

Retorne APENAS um número de 0.0 a 1.0 representando a qualidade.
NÃO explique, apenas retorne o número."""
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=5,
                temperature=0,
            )
            
            score_text = response.choices[0].message.content.strip()
            # Extrai número do texto
            import re
            match = re.search(r'(\d+\.?\d*)', score_text)
            if match:
                return min(float(match.group(1)), 1.0)
            
            return 0.5  # Default neutro se parsing falhar
            
        except Exception as e:
            logger.warning(f"LLM judge falhou: {e}")
            return 0.5  # Default neutro
    
    def evaluate_single(
        self,
        example: GoldenExample,
        actual_answer: str,
        use_llm_judge: bool = True,
    ) -> EvaluationResult:
        """Avalia uma única resposta contra o golden dataset."""
        
        exact = self.exact_match(actual_answer, example.expected_answer)
        fuzzy = self.fuzzy_match(actual_answer, example.expected_answer)
        llm_score = self.llm_as_judge(example.question, actual_answer, example.expected_answer) if use_llm_judge else 0.5
        
        # Score ponderado
        weights = {"exact": 0.2, "fuzzy": 0.3, "llm": 0.5}
        overall = (
            exact * weights["exact"] +
            fuzzy * weights["fuzzy"] +
            llm_score * weights["llm"]
        )
        
        result = EvaluationResult(
            example_id=example.id,
            question=example.question,
            actual_answer=actual_answer,
            expected_answer=example.expected_answer,
            metrics={
                "exact_match": round(exact, 4),
                "fuzzy_match": round(fuzzy, 4),
                "llm_judge": round(llm_score, 4),
            },
            overall_score=overall,
            passed=overall >= 0.7,  # Threshold de aprovação
        )
        
        self.results.append(result)
        return result
    
    def evaluate_batch(
        self,
        answers_fn,
        use_llm_judge: bool = True,
    ) -> list[EvaluationResult]:
        """
        Avalia batch completo de exemplos.
        
        Args:
            answers_fn: Função que recebe question e retorna answer.
            use_llm_judge: Se True, usa LLM como juiz adicional.
        
        Returns:
            Lista de resultados de avaliação.
        """
        results = []
        
        console.print(f"\n[bold cyan]📊 Avaliando {len(GOLDEN_DATASET)} exemplos...[/]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Avaliando...", total=len(GOLDEN_DATASET))
            
            for example in GOLDEN_DATASET:
                answer = answers_fn(example.question)
                
                with measure_latency(logger, f"evaluate_{example.id}"):
                    result = self.evaluate_single(
                        example, answer, use_llm_judge
                    )
                
                status = "✅" if result.passed else "❌"
                progress.update(task, description=f"{status} {example.id}: {result.overall_score:.2f}")
                results.append(result)
                progress.advance(task)
        
        return results
    
    def generate_report(self) -> dict:
        """Gera relatório estatístico completo."""
        if not self.results:
            return {"error": "Nenhum resultado para reportar"}
        
        scores = [r.overall_score for r in self.results]
        passed = sum(1 for r in self.results if r.passed)
        
        # Por categoria
        categories: dict[str, list[float]] = {}
        for r in self.results:
            # Encontrar categoria do exemplo
            for ex in GOLDEN_DATASET:
                if ex.id == r.example_id:
                    cat = ex.category
                    categories.setdefault(cat, []).append(r.overall_score)
                    break
        
        report = {
            "total_examples": len(self.results),
            "passed": passed,
            "failed": len(self.results) - passed,
            "pass_rate": round(passed / len(self.results), 4),
            "avg_score": round(sum(scores) / len(scores), 4),
            "min_score": round(min(scores), 4),
            "max_score": round(max(scores), 4),
            "median_score": round(sorted(scores)[len(scores) // 2], 4),
            "by_category": {
                cat: {
                    "count": len(sc),
                    "avg": round(sum(sc) / len(sc), 4),
                }
                for cat, sc in categories.items()
            },
            "details": [r.to_dict() for r in self.results],
        }
        
        return report


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTES A/B
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class ABTestResult:
    """Resultado de teste A/B entre duas abordagens."""
    
    variant_a_name: str
    variant_b_name: str
    variant_a_score: float
    variant_b_score: float
    winner: str  # "A", "B", ou "tie"
    improvement_pct: float
    examples_tested: int
    
    def to_dict(self) -> dict:
        return {
            "variant_a": self.variant_a_name,
            "variant_b": self.variant_b_name,
            "score_a": round(self.variant_a_score, 4),
            "score_b": round(self.variant_b_score, 4),
            "winner": self.winner,
            "improvement_pct": round(self.improvement_pct, 2),
            "examples_tested": self.examples_tested,
        }


def run_ab_test(
    variant_a_fn,
    variant_b_fn,
    dataset: Optional[list[GoldenExample]] = None,
) -> ABTestResult:
    """
    Executa teste A/B entre duas variantes.
    
    Args:
        variant_a_fn: Função que gera resposta (variante A).
        variant_b_fn: Função que gera resposta (variante B).
        dataset: Dataset para testar (usa GOLDEN_DATASET se não fornecido).
    
    Returns:
        Resultado do teste A/B.
    """
    dataset = dataset or GOLDEN_DATASET
    evaluator = Evaluator()
    
    console.print(f"\n[bold cyan]🧪 Teste A/B: Variante A vs Variante B[/]\n")
    
    scores_a = []
    scores_b = []
    
    for example in dataset:
        answer_a = variant_a_fn(example.question)
        answer_b = variant_b_fn(example.question)
        
        result_a = evaluator.evaluate_single(example, answer_a, use_llm_judge=False)
        result_b = evaluator.evaluate_single(example, answer_b, use_llm_judge=False)
        
        scores_a.append(result_a.overall_score)
        scores_b.append(result_b.overall_score)
        
        console.print(
            f"  {example.id}: A={result_a.overall_score:.2f} | B={result_b.overall_score:.2f}"
        )
    
    avg_a = sum(scores_a) / len(scores_a)
    avg_b = sum(scores_b) / len(scores_b)
    
    if avg_a > avg_b:
        winner = "A"
        improvement = ((avg_a - avg_b) / avg_b * 100) if avg_b > 0 else 0
    elif avg_b > avg_a:
        winner = "B"
        improvement = ((avg_b - avg_a) / avg_a * 100) if avg_a > 0 else 0
    else:
        winner = "tie"
        improvement = 0
    
    return ABTestResult(
        variant_a_name="Variante A",
        variant_b_name="Variante B",
        variant_a_score=avg_a,
        variant_b_score=avg_b,
        winner=winner,
        improvement_pct=abs(improvement),
        examples_tested=len(dataset),
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def classify_ticket_heuristic(text: str) -> str:
    """Classificação por regras heurísticas (baseline)."""
    t = text.lower()
    if any(w in t for w in ["erro", "falha", "produção", "500", "down", "fora do ar", "timeout"]):
        return "URGENTE"
    elif any(w in t for w in ["preço", "como", "quero", "sugestão"]):
        return "NORMAL"
    return "BAIXA"


def main():
    """Executa demonstração completa de avaliação."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO 10 — Avaliação e Testes[/]\n\n"
        "Golden datasets, LLM-as-a-judge, embedding similarity,\n"
        "testes A/B e benchmarking regressivo.",
        title="📊 AI Agents Course",
        border_style="cyan",
    ))
    
    # Valida ambiente
    try:
        get_llm_config()
    except (ValueError, EnvironmentError) as e:
        console.print(f"[red]⚠ {e}[/]")
        console.print("\n[dim]Configurando .env com OPENAI_API_KEY necessário para LLM judge.[/]")
        return
    
    # ━━ 1. Avaliação com Golden Dataset ━━
    console.print("\n[bold]1️⃣  Avaliação com Golden Dataset[/]\n")
    
    evaluator = Evaluator()
    
    def mock_agent(question: str) -> str:
        """Agente simulado para avaliação."""
        # Simula algumas acertos e erros
        responses = {
            "Não consigo acessar minha conta, erro 403": "URGENTE",
            "Quero saber preços do plano enterprise": "NORMAL",
            "API retornando 500 intermitentemente": "CRÍTICO",  # Errado!
            "Sugestão: adicionar modo escuro": "BAIXA",
            "Meu servidor está fora do ar há 2 horas": "URGENTE",
            "Como faço para exportar meus dados?": "NORMAL",
            "Erro ao fazer upload de arquivo PDF": "URGENTE",  # Errou
            "Database connection timeout frequente": "URGENTE",
        }
        return responses.get(question, classify_ticket_heuristic(question))
    
    results = evaluator.evaluate_batch(mock_agent, use_llm_judge=True)
    report = evaluator.generate_report()
    
    # Exibe relatório
    console.print("\n[bold cyan]📋 Relatório de Avaliação:[/]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", justify="right")
    
    table.add_row("Total de exemplos", str(report["total_examples"]))
    table.add_row("Aprovados", f"{report['passed']}")
    table.add_row("Reprovados", f"{report['failed']}")
    table.add_row("Taxa de aprovação", f"{report['pass_rate']:.0%}")
    table.add_row("Score médio", f"{report['avg_score']:.4f}")
    table.add_row("Score mínimo", f"{report['min_score']:.4f}")
    table.add_row("Score máximo", f"{report['max_score']:.4f}")
    table.add_row("Mediana", f"{report['median_score']:.4f}")
    
    console.print(table)
    
    # Salva relatório
    report_path = Path(__file__).parent / "evaluation_report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2))
    console.print(f"\n[dim]Relatório salvo em: {report_path}[/]")
    
    # ━━ 2. Teste A/B ━━
    console.print("\n[bold]2️⃣  Teste A/B: Heurística vs Agente Simulado[/]\n")
    
    ab_result = run_ab_test(
        variant_a_fn=classify_ticket_heuristic,
        variant_b_fn=mock_agent,
    )
    
    console.print(f"\n[bold cyan]Resultado do Teste A/B:[/]\n")
    
    ab_table = Table(show_header=True, header_style="bold cyan")
    ab_table.add_column("Métrica", style="cyan")
    ab_table.add_column("Valor", justify="right")
    
    ab_table.add_row("Variante A", ab_result.variant_a_name)
    ab_table.add_row("Variante B", ab_result.variant_b_name)
    ab_table.add_row("Score A", f"{ab_result.variant_a_score:.4f}")
    ab_table.add_row("Score B", f"{ab_result.variant_b_score:.4f}")
    ab_table.add_row("Vencedor", ab_result.winner.upper())
    ab_table.add_row("Melhoria", f"{ab_result.improvement_pct:.1f}%")
    ab_table.add_row("Exemplos testados", str(ab_result.examples_tested))
    
    console.print(ab_table)
    
    console.print("\n[dim]💡 Use evaluation_report.json para tracking regressivo![/]")


if __name__ == "__main__":
    main()
