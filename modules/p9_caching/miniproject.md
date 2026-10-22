# 🏗️ Mini-Projeto Integrador — Caching & Optimization

> **Objetivo:** Construir um sistema de caching para respostas de LLM.

## O que você vai construir

Um cache manager `cache_system.py` que:

1. **Tracka** hit/miss rates de queries
2. **Implementa** TTL (time-to-live) para entries
3. **Invalida** cache por estratégia (LRU, pattern)
4. **Calcula** economia de custo com caching

## Requisitos

```python
class CacheSystem:
    def get(self, key: str) -> Optional[Any]:
        """Retornar valor se no cache, None se miss."""
        ...
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Armazenar valor com TTL opcional."""
        ...
    
    def hit_rate(self) -> float:
        """Calcular taxa de acerto do cache."""
        ...
    
    def is_expired(self, key: str) -> bool:
        """Verificar se entry expirou."""
        ...
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Remover keys que contêm pattern."""
        ...
    
    def savings_percentage(self) -> float:
        """Calcular % economizada com cache."""
        ...
    
    def generate_cache_key(self, query: str, model: str, temperature: float) -> str:
        """Gerar hash determinístico da combinação."""
        ...
```

## Teste seu código

```bash
python cache_system.py --simulate --queries queries.json --output stats.json
python cache_system.py --lru-cache --capacity 100 --test load_test.json
```

## Desafios extras

- [ ] Multi-level cache (L1 memory + L2 Redis)
- [ ] Auto-TTL baseado em frequência de acesso
- [ ] Cache warming (pré-carregar queries frequentes)
- [ ] Distributed cache com consistency protocol
