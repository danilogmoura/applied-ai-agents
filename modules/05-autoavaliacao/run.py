"""
Módulo 05 — Autoavaliação e Reflexão

Loop de auto-crítica onde o agente avalia e corrige sua própria saída
usando Structured Outputs (Pydantic) antes de entregar ao usuário.
Limite máximo de iterações para evitar loops infinitos.

Problema: O agente gerou uma resposta, mas você não confia que está correta.
Como fazer o agente se autoavaliar e melhorar antes de entregar?
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from shared.logging_config import setup_logging
from shared.cost import count_tokens, estimate_cost, format_cost
from shared.security import get_llm_config, get_model, get_provider, get_thinking

console = Console()
logger = setup_logging("05-autoavaliacao")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODELOS PYDANTIC — Estrutura validada
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

from pydantic import BaseModel, Field


class SelfEvaluation(BaseModel):
    """Avaliação estruturada da qualidade de uma resposta."""
    
    accuracy: int = Field(ge=1, le=10, description="Precisão factual (1-10)")
    completeness: int = Field(ge=1, le=10, description="Completude da resposta (1-10)")
    clarity: int = Field(ge=1, le=10, description="Clareza e objetividade (1-10)")
    issues: list[str] = Field(default_factory=list, description="Problemas identificados")
    needs_improvement: bool = Field(description="Se a resposta precisa melhoria")
    improvement_suggestion: str = Field(default="", description="Sugestão concreta de melhoria")


class AgentResponse(BaseModel):
    """Resposta final do agente com metadados de qualidade."""
    
    answer: str
    evaluation: SelfEvaluation
    iterations: int = 0  # Quantas vezes foi refinada


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENTE COM AUTOAVALIAÇÃO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SelfEvaluatingAgent:
    """
    Agente que gera respostas e as autoavalia usando LLM + Pydantic.
    
    Se a avaliação for insuficiente, refina a resposta até atingir
    qualidade mínima ou limite de iterações.
    """
    
    MIN_SCORE = 7  # Nota mínima para aprovação
    
    def __init__(self, model: str = "gpt-4o-mini", max_iterations: int = 3):
        self.model = model
        self.max_iterations = max_iterations
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        # Guardado entre iteracoes para o prompt de refinamento. Inicializado
        # vazio para a iteracao 2 nao quebrar caso a autoavaliacao da iteracao 1
        # falhe (ex.: thinking ON estourando max_tokens do structured output).
        self._last_issues: list[str] = []
    
    def _generate(self, prompt: str) -> str:
        """Chamada real ao LLM."""
        from openai import OpenAI
        
        api_key, base_url, _ = get_llm_config()
        extra_body = get_thinking(self.model)
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        response = client.chat.completions.create(
            model=self.model,
            extra_body=extra_body,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.5,
        )
        
        return response.choices[0].message.content
    
    def generate(self, question: str, context: Optional[str] = None) -> AgentResponse:
        """
        Gera resposta com loop de autoavaliação.
        
        Args:
            question: Pergunta do usuário.
            context: Contexto opcional adicional.
        
        Returns:
            Resposta aprovada na autoavaliação.
        """
        from openai import OpenAI
        from pydantic import ValidationError
        
        api_key, base_url, _ = get_llm_config()
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        iteration = 0
        current_answer = ""
        
        while iteration < self.max_iterations:
            iteration += 1
            
            if iteration == 1:
                # Primeira geração
                prompt = f"""Você é um assistente técnico especializado. Responda à pergunta de forma precisa e completa.

PERGUNTA: {question}

{'CONTEXTO ADICIONAL:\n' + context if context else ''}

RESPOSTA:"""
            else:
                # Refinamento baseado nos feedbacks
                prompt = f"""Você está refinando uma resposta anterior. Aplique as sugestões de melhoria mantendo a estrutura original.

PERGUNTA: {question}

RESPOSTA ANTERIOR:
{current_answer}

FEEDBACK DE QUALIDADE:
{chr(10).join(f'- {issue}' for issue in self._last_issues)}

Melhore a resposta aplicando todas as sugestões acima. Mantenha o mesmo formato."""
            
            console.print(f"\n[bold cyan]▸ Iteração {iteration}/{self.max_iterations}...[/]")
            
            # Gera/refine resposta
            current_answer = self._generate(prompt)
            input_tok = count_tokens(prompt, self.model)
            output_tok = count_tokens(current_answer, self.model)
            self.total_input_tokens += input_tok
            self.total_output_tokens += output_tok
            
            # Autoavaliação com Structured Output
            eval_prompt = f"""Avalie esta resposta usando estritamente o formato JSON solicitado.

PERGUNTA: {question}
RESPOSTA AVALIAR: {current_answer[:500]}

FORMATO OBRIGATÓRIO (JSON apenas):
{{
    "accuracy": <1-10>,
    "completeness": <1-10>,
    "clarity": <1-10>,
    "issues": ["lista de problemas"],
    "needs_improvement": true/false,
    "improvement_suggestion": "sugestão concreta"
}}"""
            
            try:
                response = client.beta.chat.completions.parse(
                    model=self.model,
                    extra_body=get_thinking(self.model),
                    messages=[{"role": "user", "content": eval_prompt}],
                    response_format=SelfEvaluation,
                    # Folga p/ modelos hibridos: com thinking ON os tokens de
                    # raciocinio sao cobrados ANTES do JSON; um teto baixo (200)
                    # truncava a saida e o parse falhava.
                    max_tokens=1500,
                    temperature=0,
                )
                
                evaluation = response.choices[0].message.parsed
                
                # Exibe avaliação
                scores = [evaluation.accuracy, evaluation.completeness, evaluation.clarity]
                avg_score = sum(scores) / len(scores)
                
                status = "✅ APROVADA" if avg_score >= self.MIN_SCORE else "⚠️ REFINAR"
                score_color = "green" if avg_score >= self.MIN_SCORE else "yellow"
                
                console.print(Panel(
                    Text(f"Avaliação: {status}\n"
                         f"Precisão: {evaluation.accuracy}/10\n"
                         f"Completude: {evaluation.completeness}/10\n"
                         f"Clareza: {evaluation.clarity}/10\n"
                         f"Média: {avg_score:.1f}/10 (mín: {self.MIN_SCORE})\n"
                         f"Issues: {len(evaluation.issues)}\n"
                         f"Sugestão: {evaluation.improvement_suggestion}",
                         style=score_color),
                    title=f"Iteração {iteration}",
                    border_style=score_color,
                ))
                
                self._last_issues = evaluation.issues
                
                # Aprovou?
                if avg_score >= self.MIN_SCORE and not evaluation.needs_improvement:
                    cost = estimate_cost(input_tok, output_tok, self.model)
                    
                    return AgentResponse(
                        answer=current_answer,
                        evaluation=evaluation,
                        iterations=iteration,
                    )
                
            except (ValidationError, Exception) as e:
                logger.warning(f"Falha na autoavaliação iteração {iteration}: {e}")
                console.print(f"[yellow]⚠ Falha na avaliação: {e}[/]")
        
        # Limite de iterações atingido — retorna melhor versão
        console.print("\n[yellow]⚠ Limite de iterações atingido — retornando melhor versão[/]")
        
        cost = estimate_cost(self.total_input_tokens, self.total_output_tokens, self.model)
        
        return AgentResponse(
            answer=current_answer,
            evaluation=SelfEvaluation(
                accuracy=6,
                completeness=6,
                clarity=6,
                issues=["Limite de iterações atingido"],
                needs_improvement=True,
                improvement_suggestion="Mais iterações seriam necessárias",
            ),
            iterations=self.max_iterations,
        )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa demonstração do agente com autoavaliação."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO 05 — Autoavaliação e Reflexão[/]\n\n"
        "Agente que critica e corrige sua própria saída.\n"
        "Structured Outputs (Pydantic) + limite de iterações.",
        title="🔄 AI Agents Course",
        border_style="cyan",
    ))
    
    # Valida ambiente
    try:
        get_llm_config()
        console.print(f"[green]✓ Ambiente validado ({get_provider()})[/]")
    except EnvironmentError as e:
        console.print(f"[red]✗ {e}[/]")
        sys.exit(1)
    
    model = get_model()
    
    # Testes
    test_cases = [
        {
            "question": "Explique o conceito de RAG em IA e como funciona na prática.",
            "context": None,
        },
        {
            "question": "Quais são os principais riscos de segurança ao deployar um agente de IA em produção?",
            "context": "Ambiente Python com FastAPI, Docker, e integração com APIs externas.",
        },
    ]
    
    agent = SelfEvaluatingAgent(model=model, max_iterations=3)
    
    for i, case in enumerate(test_cases, 1):
        console.print(f"\n{'='*70}")
        console.print(f"[bold]Caso de teste {i}/{len(test_cases)}[/]")
        console.print(f"{'='*70}")
        
        result = agent.generate(case["question"], case.get("context"))
        
        console.print()
        console.print(Panel(
            result.answer,
            title=f"✅ Resposta Final ({result.iterations} iteração(ões))",
            border_style="green",
        ))
        
        console.print(f"\n[dim]Iterações: {result.iterations} | "
                      f"Custo acumulado: {format_cost(estimate_cost(agent.total_input_tokens, agent.total_output_tokens, model))}[/]")
    
    console.print("\n[dim]💡 Próximo passo: Módulo 06 — Tool Calling[/]")


if __name__ == "__main__":
    main()
