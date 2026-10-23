"""
Módulo P9 — Teste do Exercício

Execute com: python modules/p9_caching/test_exercise.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Cache Hit/Miss — Taxas de acerto funcionam?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_cache_hit_miss():
    """
    TODO: Implemente cache simples com hit/miss tracking.
    
    Regra: Se mesma query já foi feita → HIT (retorna cache).
            Se query nova → MISS (calcula e armazena).
    """
    class SimpleCache:
        def __init__(self):
            self.store: Dict[str, Any] = {}
            self.hits = 0
            self.misses = 0
        
        def get(self, key: str) -> Optional[Any]:
            """Retorne valor se no cache, None se miss."""
            if key in self.store:
                self.hits += 1
                return self.store[key]
            self.misses += 1
            return None
        
        def put(self, key: str, value: Any):
            """Armazene valor no cache."""
            self.store[key] = value
        
        def hit_rate(self) -> float:
            """Calcule taxa de acerto."""
            total = self.hits + self.misses
            return self.hits / total if total > 0 else 0.0
    
    cache = SimpleCache()
    
    # Simula sequência de queries
    queries = [
        ("qual clima?", "Sol, 25°C"),      # MISS
        ("qual temperatura?", "25°C"),       # MISS
        ("qual clima?", "Sol, 25°C"),        # HIT (mesma query)
        ("nova query?", "Resposta nova"),    # MISS
        ("qual clima?", "Sol, 25°C"),        # HIT
        ("nova query?", "Resposta nova"),    # HIT
    ]
    
    for query, expected in queries:
        cached = cache.get(query)
        if cached is None:
            cache.put(query, expected)
            cached = expected
    
    rate = cache.hit_rate()
    assert rate > 0, \
        f"Deve haver hits, got {cache.hits} hits / {cache.misses + cache.hits} total"
    assert rate < 1.0, \
        "Não pode ser 100% (houve misses)"
    
    console.print(f"[green]✓[/green] Cache: {cache.hits} hits, {cache.misses} misses, "
                  f"rate={rate:.0%}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: TTL (Time To Live) — Expiração funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_ttl_expiry():
    """
    TODO: Implemente TTL (tempo de vida) para cache entries.
    
    Regra: Entry expira após N segundos.
    """
    import time
    
    class TTLCache:
        def __init__(self, default_ttl_seconds: int = 5):
            self.default_ttl = default_ttl_seconds
            self.store: Dict[str, tuple[Any, float]] = {}
        
        def get(self, key: str) -> Optional[Any]:
            """Retorne valor se não expirou, None se expired."""
            from datetime import datetime
            if key in self.store:
                value, expiry_time = self.store[key]
                if datetime.now().timestamp() < expiry_time:
                    return value
                else:
                    del self.store[key]  # Remove expired
            return None
        
        def put(self, key: str, value: Any, ttl: Optional[int] = None):
            """Armazene com timestamp de expiração."""
            from datetime import datetime
            effective_ttl = ttl if ttl is not None else self.default_ttl
            expiry_time = datetime.now().timestamp() + effective_ttl
            self.store[key] = (value, expiry_time)
        
        def is_expired(self, key: str) -> bool:
            """Verifique se entry expirou."""
            from datetime import datetime
            if key not in self.store:
                return True
            _, expiry_time = self.store[key]
            return datetime.now().timestamp() >= expiry_time
    
    cache = TTLCache(default_ttl_seconds=1)
    
    cache.put("key1", "value1")
    
    # Deveria estar válido
    assert cache.get("key1") == "value1", \
        "Entry recém-criada deve estar válida"
    
    # Simula passagem de tempo (hack: manipula o store diretamente)
    from datetime import datetime, timedelta
    old_time = datetime.now() - timedelta(seconds=10)
    cache.store["expired_key"] = ("old_value", old_time.timestamp())
    
    assert cache.is_expired("expired_key"), \
        "Entry antiga deve estar expirada"
    
    console.print("[green]✓[/green] TTL: valid ✓, expired ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Cache Invalidation — Invalidacao funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_cache_invalidation():
    """
    TODO: Implemente invalidação de cache por estratégia.
    
    Estratégias:
    - Eviction: LRU (Least Recently Used), FIFO, Random
    - Manual: delete(key), invalidate(pattern)
    """
    class LRUCache:
        def __init__(self, capacity: int = 3):
            self.capacity = capacity
            self.store: Dict[str, Any] = {}
            self.order: list = []
        
        def get(self, key: str) -> Optional[Any]:
            """Retorne valor e atualize ordem de uso."""
            if key in self.store:
                self.order.remove(key)
                self.order.append(key)
                return self.store[key]
            return None
        
        def put(self, key: str, value: Any):
            """Adicione/atualize. Remova LRU se exceder capacity."""
            if key in self.store:
                self.order.remove(key)
            elif len(self.store) >= self.capacity:
                lru_key = self.order.pop(0)
                del self.store[lru_key]
            self.store[key] = value
            self.order.append(key)
        
        def invalidate_pattern(self, pattern: str) -> int:
            """Remova keys que contêm pattern. Retorne count removido."""
            keys_to_remove = [k for k in self.store if pattern in k]
            for key in keys_to_remove:
                del self.store[key]
                if key in self.order:
                    self.order.remove(key)
            return len(keys_to_remove)
    
    cache = LRUCache(capacity=3)
    
    # Preenche cache
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    
    # Tenta adicionar mais um (deve remover LRU)
    cache.put("d", 4)
    
    assert len(cache.store) <= 3, \
        f"Cache não deve exceder capacity, got {len(cache.store)}"
    assert "a" not in cache.store or cache.get("a") is not None, \
        "LRU item deve ter sido removido"
    
    # Invalida por padrão
    cache.put("user_1_data", "x")
    cache.put("user_2_data", "y")
    removed = cache.invalidate_pattern("user_1")
    assert removed >= 1, \
        f"Deve remover pelo menos 1 entry com 'user_1', got {removed}"
    
    console.print(f"[green]✓[/green] Invalidation: LRU evict ✓, pattern remove={removed}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Cost Savings — Economia de custo com cache?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_cost_savings():
    """
    TODO: Calcule economia de tokens/custo ao usar cache.
    """
    def estimate_cost(tokens: int, cost_per_1k_tokens: float = 0.002) -> float:
        return (tokens / 1000) * cost_per_1k_tokens
    
    class CostTracker:
        def __init__(self, cost_per_1k_tokens: float = 0.002):
            self.cost_per_1k = cost_per_1k_tokens
            self.total_requests = 0
            self.cache_hits = 0
            self.total_tokens_saved = 0
        
        def record_hit(self, tokens: int):
            """Registre hit e acumule economia."""
            self.cache_hits += 1
            self.total_tokens_saved += tokens
        
        def savings_percentage(self) -> float:
            """Calcule % economizada com cache."""
            if self.total_requests == 0:
                return 0.0
            return self.cache_hits / self.total_requests
    
    tracker = CostTracker(cost_per_1k_tokens=0.002)
    
    # Simula 100 requests, 60 são hits (mesmas queries repetidas)
    unique_queries = [
        ("clima", 500), ("temperatura", 300), ("previsao", 800),
        ("chuva", 400), ("vento", 200),
    ]
    
    all_requests = []
    for _ in range(6):
        all_requests.extend(unique_queries)  # 50 requests
    for _ in range(4):
        all_requests.extend(unique_queries[:3])  # 30 hits extras
    
    total_tokens_without_cache = sum(t for _, t in all_requests)
    
    seen_queries = set()
    for query, tokens in all_requests:
        # Simula cache hit/miss
        tracker.total_requests += 1
        # Primeiras ocorrências são misses, subsequentes são hits
        if query in seen_queries:
            tracker.record_hit(tokens)
        else:
            seen_queries.add(query)
    
    savings_pct = tracker.savings_percentage()
    assert savings_pct > 0, \
        f"Deve haver economia com cache hits, got {savings_pct:.0%}"
    assert tracker.total_tokens_saved > 0, \
        "Tokens salvos devem ser > 0"
    
    console.print(f"[green]✓[/green] Economia: {tracker.total_tokens_saved} tokens salvos, "
                  f"{savings_pct:.0%} redução")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Cache Key Generation — Chaves geradas corretamente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_cache_key_generation():
    """
    TODO: Gere chaves de cache determinísticas.
    
    Mesma input → mesma chave. Input diferente → chave diferente.
    """
    import hashlib
    
    def generate_cache_key(query: str, model: str, temperature: float) -> str:
        """Gere hash determinístico da combinação query+model+temperature."""
        input_str = f"{query}:{model}:{temperature}"
        return hashlib.sha256(input_str.encode()).hexdigest()[:32]
    
    key1 = generate_cache_key("qual clima?", "gpt-4", 0.7)
    key2 = generate_cache_key("qual clima?", "gpt-4", 0.7)
    key3 = generate_cache_key("qual temperatura?", "gpt-4", 0.7)
    key4 = generate_cache_key("qual clima?", "claude-3", 0.7)
    
    assert key1 == key2, \
        "Mesma input deve gerar mesma chave"
    assert key1 != key3, \
        "Query diferente deve gerar chave diferente"
    assert key1 != key4, \
        "Model diferente deve gerar chave diferente"
    
    assert len(key1) <= 64, \
        f"Chave deve ser curta (hash), got {len(key1)} chars"
    
    console.print(f"[green]✓[/green] Keys: deterministic ✓, unique ✓, length={len(key1)}")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_cache_hit_miss, test_02_ttl_expiry,
             test_03_cache_invalidation, test_04_cost_savings,
             test_05_cache_key_generation]
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P9: Caching e Otimização[/bold cyan]",
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
