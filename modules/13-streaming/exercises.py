"""Módulo P8 — Exercícios Práticos

Execute com: python modules/13-streaming/exercises.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Generator, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Streaming Chunk — Chunks são gerados corretamente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_streaming_chunks():
    """
    TODO: Implemente geração de chunks de streaming.
    
    Regra: Cada chunk deve ter max_size bytes e manter integridade UTF-8.
    """
    def stream_chunks(text: str, max_chunk_size: int = 50) -> Generator[str, None, None]:
        """TODO: Gere chunks de tamanho limitado mantendo integridade UTF-8."""
        # ← Implemente aqui
        return  # Placeholder vazio
    
    text = "A resposta completa do LLM que pode ser muito longa." * 5
    chunks = list(stream_chunks(text, max_chunk_size=30))
    
    assert len(chunks) > 1, \
        f"Texto longo deve gerar múltiplos chunks, got {len(chunks)}"
    assert all(len(c) <= 30 for c in chunks), \
        f"Cada chunk deve ter <= 30 chars, got max={max(len(c) for c in chunks)}"
    
    reconstructed = "".join(chunks)
    assert reconstructed == text, \
        "Chunks reconstruídos devem igualar texto original"
    
    console.print(f"[green]✓[/green] Streaming: {len(chunks)} chunks, "
                  f"max_size={max(len(c) for c in chunks)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: SSE Format — Server-Sent Events válidos?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_sse_format():
    """
    TODO: Formate chunks como SSE (Server-Sent Events).
    
    Formato SSE: "data: {json}\n\n"
    """
    def to_sse(data: dict) -> str:
        """TODO: Converta dict para formato SSE válido: data: {json}\n\n"""
        # ← Implemente aqui
        return ""  # Placeholder vazio
    
    sse_event = to_sse({"text": "Olá", "index": 0})
    
    assert sse_event.startswith("data:"), \
        "SSE deve começar com 'data:'"
    assert "\n\n" in sse_event, \
        "SSE deve terminar com duplo newline"
    
    # Evento de fim
    done_event = to_sse({"done": True})
    assert '"done": true' in done_event or "'done': True" in done_event, \
        "Evento de fim deve ter done=True"
    
    console.print("[green]✓[/green] SSE: format ✓, delimiter ✓, done event ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Token-by-Token Latency — Latência por token?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_token_latency():
    """
    TODO: Meça latência entre tokens consecutivos (TTFT - Time To First Token).
    """
    import time
    
    def simulate_stream(token_delays_ms: List[float]) -> list:
        """Simula streaming com delays variáveis."""
        results = []
        for delay in token_delays_ms:
            time.sleep(delay / 1000)
            results.append(delay)
        return results
    
    delays = [150, 45, 30, 25, 120, 35, 28]  # ms entre tokens
    
    measured = simulate_stream(delays)
    
    # TODO: Calcule métricas de latência
    ttft = 0  # ← Time To First Token
    avg_latency = 0  # ← Média
    p95_latency = 0  # ← 95º percentil
    
    assert ttft > 0, "TTFT deve ser positivo"
    assert avg_latency > 0, "Latência média deve ser positiva"
    assert p95_latency >= avg_latency, \
        f"P95 ({p95_latency}) >= média ({avg_latency:.0f})"
    
    console.print(f"[green]✓[/green] TTFT={ttft:.0f}ms | "
                  f"avg={avg_latency:.0f}ms | p95={p95_latency:.0f}ms")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Streaming vs Non-Streaming — Comparação justa?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_streaming_vs_blocking():
    """
    TODO: Compare UX entre streaming e blocking.
    
    Streaming: usuário vê progresso desde o primeiro token.
    Blocking: usuário espera tudo antes de ver qualquer coisa.
    """
    total_tokens = 100
    tokens_per_second = 30
    
    blocking_time = total_tokens / tokens_per_second  # Tudo de uma vez
    
    # Streaming: primeiro token em ~100ms, resto gradual
    streaming_first_token_ms = 100
    streaming_total_ms = blocking_time * 1000
    
    # TODO: Calcule perceived latency (quando usuário VE a primeira coisa)
    perceived_blocking = 0  # ← Usuário fica esperando...
    perceived_streaming = 0  # ...mas streaming mostra algo rápido
    
    improvement_pct = ((perceived_blocking - perceived_streaming) / perceived_blocking) * 100
    
    assert perceived_streaming < perceived_blocking, \
        "Streaming deve ter menor perceived latency"
    assert improvement_pct > 50, \
        f"Melhoria percebida deveria ser > 50%, got {improvement_pct:.0f}%"
    
    console.print(f"[green]✓[/green] Streaming: perceived={perceived_streaming}ms vs "
                  f"blocking={perceived_blocking:.0f}ms ({improvement_pct:.0f}% melhor)")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Error Recovery — Recuperação de erro no streaming?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_error_recovery():
    """
    TODO: Implemente recuperação de erro durante streaming.
    
    Se conexão cai, deve reconectar e continuar do último chunk.
    """
    class StreamRecovery:
        def __init__(self):
            self.last_index = 0
            self.received: List[str] = []
        
        def process_chunk(self, index: int, text: str) -> bool:
            """TODO: Processe chunk. Retorne False se precisa reconectar (texto é None = falha)."""
            # ← Implemente aqui
            return True  # Placeholder vazio
        
        def get_resume_point(self) -> int:
            """Retorne índice para retomar (próximo após último recebido)."""
            return self.last_index + 1
    
    recovery = StreamRecovery()
    
    # Processa chunks normais
    for i in range(10):
        if not recovery.process_chunk(i, f"chunk_{i}"):
            break  # Se falhar, para de processar
    
    # Simula falha no meio
    recovery.process_chunk(10, None)  # Falha
    
    # Deveria ter resume point
    resume_at = recovery.get_resume_point()
    assert resume_at > 0, \
        f"Resume point deve ser > 0 após processar chunks, got {resume_at}"
    assert resume_at <= 10, \
        "Resume point não pode exceder último chunk válido"
    
    console.print(f"[green]✓[/green] Recovery: resume at chunk {resume_at}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_streaming_chunks, test_02_sse_format,
             test_03_token_latency, test_04_streaming_vs_blocking,
             test_05_error_recovery]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P8: Streaming e Tempo Real[/bold cyan]",
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
