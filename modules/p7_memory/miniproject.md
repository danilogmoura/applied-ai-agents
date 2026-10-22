# 🏗️ Mini-Projeto Integrador — Memory & Context

> **Objetivo:** Construir um sistema de memória para agente IA.

## O que você vai construir

Um memory manager `memory_system.py` que:

1. **Gerencia** memória de curto prazo (context window)
2. **Persiste** memória de longo prazo entre sessões
3. **Consolida** memórias similares automaticamente
4. **Aplica** decay (esquecimento) em memórias antigas

## Requisitos

```python
class MemorySystem:
    def add_to_short_term(self, role: str, content: str, max_messages: int = 10) -> list:
        """Adicionar mensagem à memória curta, remover excessos."""
        ...
    
    def save_to_long_term(self, key: str, value: dict, session_id: str) -> bool:
        """Salvar dado persistente por sessão."""
        ...
    
    def retrieve_long_term(self, key: str, session_id: str) -> Any:
        """Recuperar dado da memória longa."""
        ...
    
    def consolidate_memories(self, raw_memories: list) -> dict:
        """Consolidar memórias similares em categorias."""
        ...
    
    def cleanup_expired(self, ttl_days: int = 7) -> int:
        """Remover memórias expiradas (> N dias sem uso)."""
        ...
```

## Teste seu código

```bash
python memory_system.py --session user_123 --messages conversation.json
python memory_system.py --consolidate memories_dump.json --output summary.json
```

## Desafios extras

- [ ] Vector store para busca semântica na memória
- [ ] Sync entre dispositivos (SQLite → cloud)
- [ ] Memory heatmap (quais memórias são mais acessadas)
- [ ] Auto-summarization de memórias antigas
