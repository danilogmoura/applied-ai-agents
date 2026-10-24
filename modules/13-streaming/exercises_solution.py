"""Módulo P8 — SOLUÇÃO COMENTADA

Execute com: python modules/13-streaming/exercises_solution.py

Código completo com explicações detalhadas.
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
    Geração de chunks de streaming.
    
    Funcionamento:
    1. Divide texto em fatias de tamanho max_chunk_size
    2. Usa generator (yield) para eficiência de memória
    3. Mantém integridade UTF-8 (Python strings são Unicode nativamente)
    4. Reconstrução perfeita via "".join(chunks)
    """
    def stream_chunks(text: str, max_chunk_size: int = 50) -> Generator[str, None, None]:
        """
        Gera chunks de tamanho limitado mantendo integridade UTF-8.
        
        1. Itera sobre o texto em intervalos de max_chunk_size
        2. Yield cada fatia
        3. Python strings são Unicode → integridade garantida
        """
        for i in range(0, len(text), max_chunk_size):
            yield text[i:i + max_chunk_size]
    
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
    Formatação de chunks como Server-Sent Events (SSE).
    
    Formato SSE padrão:
    - Linha começa com "data: "
    - Seguida pelo JSON serializado
    - Termina com duplo newline "\n\n" (delimitador de evento)
    
    Isso permite que clientes HTTP leiam eventos um por um.
    """
    def to_sse(data: dict) -> str:
        """
        Converte dict para formato SSE válido.
        
        1. Serializa dict para JSON string
        2. Prefixo "data: "
        3. Sufixo "\n\n" (delimitador de evento SSE)
        """
        import json
        return f"data: {json.dumps(data)}\n\n"
    
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
    Métricas de latência token-a-token.
    
    Métricas importantes:
    - TTFT (Time To First Token): quanto tempo até o usuário ver algo
    - Avg Latency: média entre tokens consecutivos
    - P95 Latency: 95º percentil (pior caso para 95% dos tokens)
    
    TTFT é a métrica mais importante para UX percebida.
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
    
    # Calcula métricas de latência
    ttft = measured[0] if measured else 0  # Time To First Token = primeiro delay
    avg_latency = sum(measured) / len(measured) if measured else 0  # Média aritmética
    sorted_measured = sorted(measured)
    p95_idx = int(len(sorted_measured) * 0.95)
    p95_idx = min(p95_idx, len(sorted_measured) - 1)
    p95_latency = sorted_measured[p95_idx]  # 95º percentil
    
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
    Comparação de UX entre streaming e blocking.
    
    Blocking:
    - Usuário espera TODOS os tokens antes de ver qualquer coisa
    - Perceived latency = tempo total
    
    Streaming:
    - Primeiro token chega rápido (~100ms)
    - Usuário VE progresso imediatamente
    - Perceived latency = tempo até primeiro token
    
    Streaming melhora perceived latency em ~90%+ quando tokens/s é alto.
    """
    total_tokens = 100
    tokens_per_second = 30
    
    blocking_time = total_tokens / tokens_per_second  # Tudo de uma vez
    
    # Streaming: primeiro token em ~100ms, resto gradual
    streaming_first_token_ms = 100
    streaming_total_ms = blocking_time * 1000
    
    # Calcula perceived latency (quando usuário VE a primeira coisa)
    perceived_blocking = blocking_time * 1000  # Usuário fica esperando...
    perceived_streaming = streaming_first_token_ms  # ...mas streaming mostra algo rápido
    
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
    Recuperação de erro durante streaming.
    
    Funcionamento:
    1. process_chunk(index, text) armazena chunks válidos
    2. Se text=None → falha, retorna False
    3. get_resume_point() retorna índice para retomar (último + 1)
    4. Cliente pode reconectar e continuar do resume point
    
    Isso permite recuperação de conexões intermitentes.
    """
    class StreamRecovery:
        def __init__(self):
            self.last_index = 0
            self.received: List[str] = []
        
        def process_chunk(self, index: int, text: str) -> bool:
            """
            Processa chunk. Retorna False se precisa reconectar.
            
            1. Se text is None → falha na conexão
            2. Se válido → armazena e atualiza last_index
            3. Retorna True (sucesso) ou False (falha)
            """
            if text is None:
                return False  # Falha — precisa reconectar
            self.received.append(text)
            self.last_index = index
            return True  # Sucesso
        
        def get_resume_point(self) -> int:
            """Retorna índice para retomar (próximo após último recebido)."""
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
