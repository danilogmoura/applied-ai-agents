"""Esqueleto para o miniprojeto — complete as funções marcadas com TODO."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from openai import OpenAI, RateLimitError, AuthenticationError
from rich.console import Console

from shared.cost import count_tokens, estimate_cost, format_cost
from shared.security import get_required_secret

console = Console()


class TicketClassifier:
    """Classificador de tickets usando LLM."""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.api_key = get_required_secret("OPENAI_API_KEY")
        # TODO: Inicializar client OpenAI aqui com self.api_key
        self.client = None  # ← Substitua por OpenAI(api_key=self.api_key)

    def classify(self, ticket_text: str) -> dict:
        """
        Classificar ticket: category, confidence, suggested_action.

        TODO: Implementar chamando a API OpenAI com temperature=0.
        Dica: usar prompt pedindo JSON com fields: category, confidence, suggested_action.
        Exemplo de prompt:
            "Classifique este ticket e retorne APENAS um JSON válido:
             {\"category\": \"URGENTE|NORMAL|BAIXA\", \"confidence\": 0.95, \"suggested_action\": \"...\"}"
        """
        if self.client is None:
            raise RuntimeError("Client não inicializado. Verifique __init__.")

        # TODO: Montar messages com system + user prompt
        # TODO: Chamar self.client.chat.completions.create(...)
        # TODO: Retornar dict com category, confidence, suggested_action
        return {"category": "BAIXA", "confidence": 0.5, "suggested_action": "TODO"}

    def estimate_batch_cost(self, tickets: list[str], model: str = None) -> dict:
        """Estimar custo total do batch."""
        model = model or self.model
        total_input = sum(count_tokens(t, model) for t in tickets)
        # TODO: Estimar output tokens (~50 por ticket) e calcular custo
        estimated_output = len(tickets) * 50
        cost = estimate_cost(total_input, estimated_output, model=model)

        return {
            "model": model,
            "num_tickets": len(tickets),
            "total_input_tokens": total_input,
            "estimated_output_tokens": estimated_output,
            "total_cost_usd": cost,
            "cost_per_ticket_usd": cost / len(tickets) if tickets else 0,
        }

    def process_batch(self, tickets: list[dict], max_retries: int = 3) -> list:
        """Processar batch com retry e fallback."""
        results = []

        for ticket in tickets:
            console.print(f"\n[bold cyan]Processando ticket #{ticket.get('id', '?')}...[/]")

            for attempt in range(max_retries):
                try:
                    result = self.classify(ticket.get("subject", "") + " " + ticket.get("description", ""))
                    result["id"] = ticket.get("id")
                    results.append(result)
                    break  # Sucesso, vai para próximo ticket

                except RateLimitError as e:
                    wait_time = 2 ** attempt  # backoff exponencial: 2, 4, 8 segundos
                    console.print(f"  [yellow]⏳ Rate limit. Tentativa {attempt+1}/{max_retries}. Aguardando {wait_time}s...[/]")
                    time.sleep(wait_time)

                except AuthenticationError as e:
                    console.print(f"  [red]❌ Erro de autenticação. Verifique sua API key.[/]")
                    results.append({"id": ticket.get("id"), "error": "auth_error"})
                    break  # Não faz sentido retry

                except Exception as e:
                    console.print(f"  [yellow]⚠️ Erro inesperado (tentativa {attempt+1}): {e}[/]")
                    if attempt == max_retries - 1:
                        results.append({"id": ticket.get("id"), "error": str(e)})
                    time.sleep(2 ** attempt)

        return results

    def handle_error(self, error: Exception, attempt: int, max_retries: int = 3) -> bool:
        """
        Decidir se retry ou falhar.

        Returns True se deve fazer retry, False se deve parar.

        Rate limit → backoff exponencial (retry=True)
        Auth error → parar (retry=False)
        Timeout → retry até max_retries
        """
        if isinstance(error, AuthenticationError):
            console.print("  [red]❌ Erro de autenticação. Não fará retry.[/]")
            return False

        if isinstance(error, RateLimitError):
            wait_time = 2 ** attempt
            console.print(f"  [yellow]⏳ Rate limit. Aguardando {wait_time}s...[/]")
            time.sleep(wait_time)
            return True

        if attempt < max_retries - 1:
            return True

        return False

    def dry_run(self, ticket_text: str) -> dict:
        """
        Modo dry run — simula classificação sem chamar API real.
        Útil para testar a lógica antes de gastar tokens.
        """
        text_lower = ticket_text.lower()

        urgent_keywords = ["erro", "falha", "500", "403", "produção", "down", "crítico"]
        normal_keywords = ["preço", "plano", "como", "dúvida", "ajuda"]

        for kw in urgent_keywords:
            if kw in text_lower:
                return {"category": "URGENTE", "confidence": 0.9, "suggested_action": "Escalonar imediatamente"}

        for kw in normal_keywords:
            if kw in text_lower:
                return {"category": "NORMAL", "confidence": 0.7, "suggested_action": "Responder em até 24h"}

        return {"category": "BAIXA", "confidence": 0.5, "suggested_action": "Arquivar"}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Classificador de tickets com LLM")
    parser.add_argument("--input", default=None, help="Arquivo JSON com tickets")
    parser.add_argument("--model", default="gpt-4o-mini", help="Modelo OpenAI")
    parser.add_argument("--dry-run", action="store_true", help="Modo simulado sem chamar API")
    args = parser.parse_args()

    classifier = TicketClassifier(model=args.model)

    if args.dry_run:
        console.print("[bold yellow]🔧 MODO DRY RUN — Nenhuma chamada API será feita.[/]")
        sample = "Erro 500 na API, produção afetada"
        result = classifier.dry_run(sample)
        console.print(f"[green]Resultado:[/green] {result}")
    elif args.input:
        with open(args.input) as f:
            tickets = json.load(f)
        console.print(f"[cyan]Carregados {len(tickets)} tickets de {args.input}[/]")

        cost_info = classifier.estimate_batch_cost([t.get("subject","") + " " + t.get("description","") for t in tickets])
        console.print(f"[green]Custo estimado:[/green] {format_cost(cost_info['total_cost_usd'])}")

        results = classifier.process_batch(tickets)
        console.print(f"\n[bold green]✓ {len(results)} tickets classificados[/]")
    else:
        # Modo interativo
        console.print("[bold cyan]Digite tickets para classificar (digite 'sair' para encerrar)[/]\n")
        while True:
            text = input("Ticket: ").strip()
            if text.lower() in ("sair", "exit", "quit"):
                break
            if not text:
                continue

            if args.dry_run:
                result = classifier.dry_run(text)
            else:
                result = classifier.classify(text)

            console.print(f"[green]→ {result}[/]")
