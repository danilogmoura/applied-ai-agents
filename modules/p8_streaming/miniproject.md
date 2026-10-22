# 🏗️ Mini-Projeto Integrador — Streaming & Real-Time

> **Objetivo:** Construir um sistema de streaming para respostas de LLM.

## O que você vai construir

Um stream handler `streaming_system.py` que:

1. **Gera** chunks de tamanho limitado
2. **Formata** como SSE (Server-Sent Events)
3. **Mede** latência por token (TTFT)
4. **Recupera** erro durante streaming

## Requisitos

```python
class StreamingSystem:
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
