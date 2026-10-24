# 🏗️ Mini-Projeto Integrador — Streaming & Real-Time

> **Objetivo:** Construir um sistema de streaming para respostas de LLM.

## O que você vai construir

Um stream handler `streaming_system.py` (classe `StreamingAgent`) que:

1. **Gera** chunks de tamanho limitado
2. **Formata** como SSE (Server-Sent Events)
3. **Mede** latência por token (TTFT)
4. **Recupera** erro durante streaming

## Requisitos

> ℹ️ **Arquitetura de referência:** No `run.py`, o streaming é composto por `StreamingAgent` (gera os chunks), `SSEEventGenerator` (formata SSE) e `LiveStreamDisplay` (console). Aqui você pode começar com uma classe única `StreamingAgent`.

```python
class StreamingAgent:
    def stream_chunks(self, text: str, max_chunk_size: int = 50) -> Generator[str, None, None]:
        """Gerar chunks de tamanho limitado."""
        ...
    
    def to_sse(self, data: dict) -> str:
        """Converter para formato SSE: 'data: {json}\n\n'."""
        ...
    
    def measure_token_latency(self, token_delays_ms: list) -> dict:
        """Calcular TTFT, avg latency, p95."""
        ...
    
    def compare_streaming_vs_blocking(self, total_tokens: int, 
                                       tokens_per_second: float) -> dict:
        """Comparar perceived latency entre streaming e blocking."""
        ...
    
    def recover_from_error(self, last_valid_index: int) -> int:
        """Determinar ponto de resume após falha."""
        ...
```

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com geração de chunks

Implemente chunking de texto para streaming:

```python
from typing import Generator, List, Dict
import json
import time
from datetime import datetime

class StreamingAgent:
    def stream_chunks(self, text: str, max_chunk_size: int = 50) -> Generator[str, None, None]:
        """Gerar chunks de tamanho limitado para streaming."""
        # Divide por palavras para evitar cortar no meio
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 para o espaço
            
            if current_size + word_size > max_chunk_size and current_chunk:
                # Yield do chunk atual
                yield " ".join(current_chunk)
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        # Yield do último chunk
        if current_chunk:
            yield " ".join(current_chunk)
    
    def stream_with_timing(self, text: str, max_chunk_size: int = 50,
                           delay_ms: float = 50) -> Generator[Dict, None, None]:
        """Streaming com timing de cada chunk."""
        start_time = time.time()
        
        for i, chunk in enumerate(self.stream_chunks(text, max_chunk_size)):
            elapsed_ms = (time.time() - start_time) * 1000
            
            yield {
                "chunk_index": i,
                "text": chunk,
                "elapsed_ms": round(elapsed_ms, 2),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Simula delay entre chunks
            time.sleep(delay_ms / 1000)
```

### Passo 2 — Formate como SSE (Server-Sent Events)

```python
    def to_sse(self, data: dict, event: str = "message", 
               event_id: int = None) -> str:
        """Converter para formato SSE: 'data: {json}\n\n'."""
        sse_lines = []
        
        if event_id is not None:
            sse_lines.append(f"id: {event_id}")
        
        if event:
            sse_lines.append(f"event: {event}")
        
        sse_lines.append(f"data: {json.dumps(data, ensure_ascii=False)}")
        sse_lines.append("")  # Linha vazia termina o evento SSE
        
        return "\n".join(sse_lines) + "\n"
    
    def sse_stream(self, text: str, max_chunk_size: int = 50) -> Generator[str, None, None]:
        """Gera stream no formato SSE."""
        for i, chunk in enumerate(self.stream_chunks(text, max_chunk_size)):
            sse_data = {
                "type": "chunk",
                "index": i,
                "content": chunk,
                "done": False,
            }
            yield self.to_sse(sse_data, event="chunk", event_id=i)
        
        # Evento final
        final_data = {"type": "done", "content": "", "done": True}
        yield self.to_sse(final_data, event="done", event_id=i + 1)
```

### Passo 3 — Meça latência por token (TTFT)

```python
    def measure_token_latency(self, token_delays_ms: List[float]) -> Dict:
        """Calcular TTFT, avg latency, p95."""
        if not token_delays_ms:
            return {
                "ttft_ms": 0,
                "avg_latency_ms": 0,
                "p95_latency_ms": 0,
                "total_tokens": 0,
                "total_time_ms": 0,
            }
        
        # TTFT = tempo até primeiro token
        ttft_ms = sum(token_delays_ms[:-1]) if len(token_delays_ms) > 1 else token_delays_ms[0]
        
        # Latência média por token
        avg_latency = sum(token_delays_ms) / len(token_delays_ms)
        
        # P95 = 95º percentil
        sorted_delays = sorted(token_delays_ms)
        p95_index = int(len(sorted_delays) * 0.95)
        p95_index = min(p95_index, len(sorted_delays) - 1)
        p95_latency = sorted_delays[p95_index]
        
        # Tempo total
        total_time = sum(token_delays_ms)
        
        return {
            "ttft_ms": round(ttft_ms, 2),
            "avg_latency_ms": round(avg_latency, 2),
            "p95_latency_ms": round(p95_latency, 2),
            "total_tokens": len(token_delays_ms),
            "total_time_ms": round(total_time, 2),
            "tokens_per_second": round(len(token_delays_ms) / (total_time / 1000), 2) if total_time > 0 else 0,
        }
    
    def simulate_delays(self, tokens_count: int, 
                        base_delay_ms: float = 50,
                        jitter_ms: float = 20) -> List[float]:
        """Simula delays realistas de geração de tokens."""
        import random
        
        delays = []
        for i in range(tokens_count):
            # Primeiro token tem maior delay (TTFT)
            if i == 0:
                delay = base_delay_ms * 3
            else:
                delay = base_delay_ms + random.uniform(-jitter_ms, jitter_ms)
            
            delays.append(max(10, delay))  # Mínimo 10ms
        
        return delays
```

### Passo 4 — Compare streaming vs blocking

```python
    def compare_streaming_vs_blocking(self, total_tokens: int,
                                       tokens_per_second: float) -> Dict:
        """Comparar perceived latency entre streaming e blocking."""
        # Blocking: usuário espera tudo
        blocking_time_ms = (total_tokens / tokens_per_second) * 1000
        
        # Streaming: usuário vê primeiro token rápido
        first_token_delay_ms = (1 / tokens_per_second) * 1000
        remaining_tokens = total_tokens - 1
        streaming_total_ms = (remaining_tokens / tokens_per_second) * 1000
        
        # Perceived latency = quando usuário começa ver conteúdo
        perceived_improvement_pct = (
            (blocking_time_ms - first_token_delay_ms) / blocking_time_ms * 100
        ) if blocking_time_ms > 0 else 0
        
        return {
            "blocking": {
                "total_ms": round(blocking_time_ms, 2),
                "perceived_ms": round(blocking_time_ms, 2),
                "description": "Usuário espera até resposta completa",
            },
            "streaming": {
                "first_token_ms": round(first_token_delay_ms, 2),
                "total_ms": round(streaming_total_ms, 2),
                "perceived_ms": round(first_token_delay_ms, 2),
                "description": "Usuário vê conteúdo progressivamente",
            },
            "improvement": {
                "first_token_speedup_ms": round(blocking_time_ms - first_token_delay_ms, 2),
                "perceived_improvement_pct": round(perceived_improvement_pct, 1),
            },
        }
```

### Passo 5 — Implemente recuperação de erro

```python
    def recover_from_error(self, last_valid_index: int, 
                           total_expected: int = None) -> Dict:
        """Determina ponto de resume após falha."""
        recovered = {
            "last_valid_index": last_valid_index,
            "resume_from": last_valid_index + 1,
            "status": "ready_to_resume",
        }
        
        if total_expected is not None:
            received = last_valid_index + 1
            remaining = total_expected - received
            recovered["received"] = received
            recovered["remaining"] = remaining
            recovered["completion_pct"] = round(received / total_expected * 100, 1)
            recovered["status"] = "ready_to_resume" if remaining > 0 else "complete"
        
        return recovered
    
    def test_recovery(self) -> Dict:
        """Testa cenário de recuperação."""
        # Simula: recebeu 50 chunks, falhou, precisa retomar do 51
        result = self.recover_from_error(last_valid_index=49, total_expected=100)
        return result
```

### Passo 6 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de streaming para LLM")
    parser.add_argument("--text", help="Texto para streaming")
    parser.add_argument("--file", help="Arquivo de texto")
    parser.add_argument("--format", choices=["plain", "sse"], default="sse")
    parser.add_argument("--simulate", action="store_true", help="Simula delays")
    parser.add_argument("--delays", help="Arquivo de delay profile (JSON)")
    parser.add_argument("--compare", action="store_true", help="Compara streaming vs blocking")
    args = parser.parse_args()
    
    system = StreamingAgent()
    
    # Texto para processar
    text = args.text
    if args.file:
        with open(args.file) as f:
            text = f.read()
    
    if not text:
        text = "Este é um texto de exemplo para demonstrar o sistema de streaming. Ele será dividido em chunks menores e enviado progressivamente."
    
    if args.compare:
        comparison = system.compare_streaming_vs_blocking(
            total_tokens=100,
            tokens_per_second=50,
        )
        print(json.dumps(comparison, indent=2, ensure_ascii=False))
    
    elif args.simulate:
        # Simula delays
        delays = system.simulate_delays(tokens_count=20, base_delay_ms=40, jitter_ms=15)
        latency = system.measure_token_latency(delays)
        print(json.dumps(latency, indent=2, ensure_ascii=False))
    
    elif args.format == "sse":
        # Gera SSE
        for sse_event in system.sse_stream(text):
            print(sse_event, end="")
    else:
        # Plain chunks
        for i, chunk in enumerate(system.stream_chunks(text)):
            print(f"[{i}] {chunk}")
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `stream_chunks()` divide texto por palavras em chunks de tamanho limitado
- [ ] `to_sse()` formata eventos SSE com id, event, data e linha vazia
- [ ] `measure_token_latency()` calcula TTFT, avg, p95, tokens/segundo
- [ ] `compare_streaming_vs_blocking()` compara perceived latency entre modos
- [ ] `recover_from_error()` determina ponto de resume após falha
- [ ] CLI aceita `--text`, `--simulate`, `--compare` e gera output SSE

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

## Teste seu código

```bash
python streaming_system.py --text long_response.txt --format sse
python streaming_system.py --simulate --delays delay_profile.json
```

## Desafios extras

- [ ] WebSocket server para streaming real-time
- [ ] Progressive rendering no frontend
- [ ] Typewriter effect com velocidade configurável
- [ ] Offline mode com cache de chunks
