"""
Módulo 13 — Streaming e Respostas em Tempo Real

Implementação de streaming token-by-token com Server-Sent Events (SSE).
Usuário vê a resposta sendo gerada ao invés de esperar tudo de uma vez.
Abort/cancel de geração em andamento.

Problema: Usuários não querem ver tela branca enquanto o LLM gera.
Como mostrar progresso e permitir cancelamento?
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import AsyncGenerator, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

from shared.logging_config import setup_logging
from shared.cost import count_tokens, estimate_cost, format_cost

console = Console()
logger = setup_logging("13-streaming")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STREAMING AGENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class StreamingAgent:
    """
    Agente que gera respostas token por token.
    
    Simula streaming do OpenAI (que também usa chunked responses).
    Em produção, usaria client.chat.completions.create(stream=True).
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self._abort_event: Optional[asyncio.Event] = None
        self.total_tokens_generated = 0
        self.total_requests = 0
    
    async def generate_stream(
        self,
        prompt: str,
        chunk_size: int = 3,
    ) -> AsyncGenerator[str, None]:
        """
        Gera resposta token por token via generator assíncrono.
        
        Args:
            prompt: Prompt para o LLM.
            chunk_size: Tokens por chunk (simulação).
        
        Yields:
            Strings parciais da resposta.
        
        Can be aborted via abort().
        """
        self._abort_event = asyncio.Event()
        self.total_requests += 1
        
        # Simula resposta longa do LLM
        simulated_response = self._simulate_llm_output(prompt)
        tokens = simulated_response.split()
        
        generated = []
        
        for i in range(0, len(tokens), chunk_size):
            # Verifica se deve abortar
            if self._abort_event and self._abort_event.is_set():
                logger.info("Streaming abortado pelo usuário")
                yield "[ABORTADO PELO USUÁRIO]"
                return
            
            chunk = " ".join(tokens[i:i + chunk_size])
            generated.append(chunk)
            
            # Simula latência de geração (50-150ms por chunk)
            await asyncio.sleep(0.05 + (i % 10) * 0.01)
            
            yield chunk
        
        # Conta tokens
        output_tok = len(simulated_response.encode()) // 4
        input_tok = count_tokens([{"role": "user", "content": prompt}], self.model)
        cost = estimate_cost(input_tok, output_tok, self.model)
        
        self.total_tokens_generated += output_tok
        
        logger.info(f"Streaming completo: {output_tok} tokens, {format_cost(cost)}")
    
    def _simulate_llm_output(self, prompt: str) -> str:
        """Simula saída do LLM baseada no prompt."""
        responses = {
            "hello": "Hello! I'm an AI assistant powered by a large language model. I can help you with many tasks including writing, analysis, coding, math, art direction, general knowledge, and more. How can I assist you today?",
            "python": "Python is a high-level, interpreted programming language known for its simplicity and readability. Here are some key features:\n\n1. Easy to learn syntax\n2. Large standard library\n3. Strong community support\n4. Great for web development, data science, and automation\n5. Cross-platform compatibility\n\nWould you like to know more about any specific aspect of Python?",
            "default": "This is a simulated streaming response from the AI agent. In production, this would come from the actual LLM API using stream=True, which returns tokens progressively as they're generated. The user sees each word appear in real-time instead of waiting for the complete response.",
        }
        
        prompt_lower = prompt.lower()
        for key, resp in responses.items():
            if key in prompt_lower:
                return resp
        
        return responses["default"]
    
    def abort(self) -> None:
        """Cancela geração em andamento."""
        if self._abort_event:
            self._abort_event.set()
            logger.info("Abort signal sent")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SSE EVENT GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SSEEventGenerator:
    """
    Gera eventos Server-Sent Events (SSE) para streaming HTTP.
    
    Formato SSE:
    event: message
    data: {"type": "chunk", "content": "Hello"}
    
    event: done
    data: {"type": "done", "tokens": 42, "cost": 0.001}
    """
    
    @staticmethod
    def format_chunk(content: str, request_id: str) -> str:
        """Formata chunk como evento SSE."""
        event = {
            "type": "chunk",
            "content": content,
            "request_id": request_id,
            "timestamp": time.time(),
        }
        return f"data: {json.dumps(event)}\n\n"
    
    @staticmethod
    def format_done(tokens: int, cost: float, request_id: str) -> str:
        """Formata evento de conclusão como SSE."""
        event = {
            "type": "done",
            "tokens": tokens,
            "cost": cost,
            "request_id": request_id,
            "timestamp": time.time(),
        }
        return f"data: {json.dumps(event)}\n\n"
    
    @staticmethod
    def format_error(message: str, request_id: str) -> str:
        """Formata evento de erro como SSE."""
        event = {
            "type": "error",
            "message": message,
            "request_id": request_id,
            "timestamp": time.time(),
        }
        return f"data: {json.dumps(event)}\n\n"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LIVE DISPLAY (Terminal UI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LiveStreamDisplay:
    """
    Exibe streaming em tempo real no terminal usando Rich Live.
    
    Simula o que um cliente frontend faria com SSE events.
    """
    
    def __init__(self):
        self.current_text = ""
        self.start_time = time.time()
    
    async def display(self, agent: StreamingAgent, prompt: str) -> str:
        """
        Exibe streaming ao vivo no terminal.
        
        Returns:
            Resposta completa.
        """
        full_response = []
        self.current_text = ""
        self.start_time = time.time()
        
        console.print(f"\n[bold cyan]📡 Iniciando streaming...[/]")
        console.print(f"[dim]Prompt:[/] {prompt[:60]}...")
        console.print()
        
        with Live(
            self._render(),
            refresh_per_second=10,
            screen=False,
            console=console,
        ) as live:
            async for chunk in agent.generate_stream(prompt):
                full_response.append(chunk)
                self.current_text = " ".join(full_response)
                
                elapsed = time.time() - self.start_time
                live.update(self._render(elapsed))
        
        elapsed = time.time() - self.start_time
        console.print(f"\n[dim]✅ Streaming completo em {elapsed:.1f}s[/]\n")
        
        return " ".join(full_response)
    
    def _render(self, elapsed: float = 0) -> Text:
        """Renderiza texto atual com indicador de progresso."""
        text = Text()
        text.append(f"[{elapsed:.1f}s] ", style="dim cyan")
        text.append(self.current_text or "Generating...", style="white")
        return text


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ABORT DEMONSTRATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def demonstrate_abort(agent: StreamingAgent) -> None:
    """Demonstra cancelamento de geração em andamento."""
    console.print(f"\n[bold yellow]⏱️  Demonstrando abort/cancel...[/]\n")
    
    # Inicia streaming em background. generate_stream e um async generator
    # (usa yield), entao NAO pode ir dentro de asyncio.create_task() -- esse
    # espera uma coroutine. Iteramos direto no gerador com "async for" abaixo.
    stream = agent.generate_stream(
        "Tell me about Python programming in detail", chunk_size=2
    )
    
    chunks_received = []
    start = time.time()
    
    # Recebe alguns chunks
    async for chunk in stream:
        chunks_received.append(chunk)
        console.print(f"  [green]←[/] {chunk}")
        
        # Abort após 3 chunks
        if len(chunks_received) >= 3:
            console.print(f"\n  [yellow]⏹  Abortando após {len(chunks_received)} chunks...[/]")
            agent.abort()
            break
        
        await asyncio.sleep(0.1)
    
    console.print(f"\n[dim]💡 Usuário viu 3 chunks e cancelou. Resposta incompleta.[/]")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    """Executa demonstração completa de streaming."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO 13 — Streaming e Tempo Real[/]\n\n"
        "Token-by-token streaming, Server-Sent Events (SSE),\n"
        "Live display e abort/cancel de geração.",
        title="📡 AI Agents Course",
        border_style="cyan",
    ))
    
    agent = StreamingAgent()
    display = LiveStreamDisplay()
    
    # ━━ 1. Streaming normal ━━
    console.print("\n[bold]1️⃣  Streaming Normal[/]\n")
    
    response = await display.display(
        agent,
        "Hello, tell me about yourself"
    )
    
    console.print(f"  [dim]Resposta completa ({len(response.split())} tokens)[/]")
    
    # ━━ 2. Streaming com abort ━━
    console.print("\n[bold]2️⃣  Streaming com Abort[/]\n")
    
    await demonstrate_abort(agent)
    
    # ━━ 3. SSE Format Demo ━━
    console.print("\n[bold]3️⃣  Formato SSE[/]\n")
    
    sse = SSEEventGenerator()
    sample_events = [
        sse.format_chunk("Hello", "req_abc123"),
        sse.format_chunk(", I'm an AI", "req_abc123"),
        sse.format_done(tokens=15, cost=0.001, request_id="req_abc123"),
    ]
    
    console.print("[dim]Eventos SSE que seriam enviados ao cliente:[/]\n")
    for event in sample_events:
        console.print(f"  [yellow]{event.strip()}[/]")
    
    # ━━ Estatísticas ━━
    console.print(f"\n[bold cyan]📊 Estatísticas:[/]\n")
    console.print(f"  Requests totais: {agent.total_requests}")
    console.print(f"  Tokens gerados: {agent.total_tokens_generated}")
    console.print(f"  Formato: Server-Sent Events (SSE)")
    
    console.print("\n[dim]💡 Streaming melhora drasticamente a UX![/]")


if __name__ == "__main__":
    asyncio.run(main())
