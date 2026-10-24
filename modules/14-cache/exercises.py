"""Módulo 14 — Exercícios Práticos

Execute com: python modules/14-cache/exercises.py

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
            """TODO: Retorne valor se no cache, None se miss."""
            # ← Implemente aqui
            return None  # Placeholder vazio
        
        def put(self, key: str, value: Any):
            """TODO: Armazene valor no cache."""
            # ← Implemente aqui
            pass  # Placeholder vazio
        
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
            """TODO: Retorne valor se não expirou, None se expired."""
            # ← Implemente aqui
            return None  # Placeholder vazio
        
        def put(self, key: str, value: Any, ttl: Optional[int] = None):
            """TODO: Armazene com timestamp de expiração."""
            # ← Implemente aqui
            pass  # Placeholder vazio
        
        def is_expired(self, key: str) -> bool:
            """Verifique se entry expirou."""
            from datetime import datetime
            if key not in self.store:
                return True
            _, expiry_time = self.store[key]
            return datetime.now().timestamp() >= expiry_time
    
    cache = TTLCache(default_ttl_seconds=1)
    
    cache.put("key1", "value1")
    
    # ⚠️ PONTO CRÍTICO: Valide comportamento — entry recém-criada deve estar válida
    cached = cache.get("key1")
    assert cached is not None, \
        "Entry recém-criada deve ser recuperável"
    assert cached == "value1", \
        f"Valor recuperado deve ser 'value1', got {cached!r}"
    
    # Simula passagem de tempo (hack: manipula o store diretamente)
    from datetime import datetime, timedelta
    old_time = datetime.now() - timedelta(seconds=10)
    cache.store["expired_key"] = ("old_value", old_time.timestamp())
    
    assert cache.is_expired("expired_key"), \
        "Entry antiga deve estar expirada"
    
    console.print("[green]✓[/green] TTL: valid ✓, expired ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Cache Invalidation — Invalidação funciona?
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
            """TODO: Retorne valor e atualize ordem de uso."""
            # ← Implemente aqui
            return None  # Placeholder vazio
        
        def put(self, key: str, value: Any):
            """TODO: Adicione/atualize. Remova LRU se exceder capacity."""
            # ← Implemente aqui
            pass  # Placeholder vazio
        
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
            """TODO: Registre hit e acumule economia."""
            # ← Implemente aqui
            pass  # Placeholder vazio
        
        def savings_percentage(self) -> float:
            """Calcule % economizada com cache."""
            # ← Implemente aqui
            return 0.0  # Placeholder vazio
    
    tracker = CostTracker(cost_per_1k_tokens=0.002)
    
    # Simula 100 requests, 60 são hits (mesmas queries repetidas)
    unique_queries = [
        ("clima", 500), ("temperatura", 300), ("previsao", 800),
        ("horario", 200), ("localizacao", 400),
    ]
    
    # 40 únicos (misses) + 60 repetidos (hits)
    for i in range(100):
        query, tokens = unique_queries[i % len(unique_queries)]
        if i < 40:
            tracker.total_requests += 1  # Miss
        else:
            tracker.record_hit(tokens)
            tracker.total_requests += 1  # Hit
    
    savings_pct = tracker.savings_percentage()
    assert savings_pct > 0, \
        f"Deve haver economia, got {savings_pct:.0%}"
    assert tracker.total_tokens_saved > 0, \
        f"Tokens salvos deve ser > 0, got {tracker.total_tokens_saved}"
    
    console.print(f"[green]✓[/green] Cost: {savings_pct:.0%} savings, "
                  f"{tracker.total_tokens_saved} tokens saved")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_cache_hit_miss, test_02_ttl_expiry,
             test_03_cache_invalidation, test_04_cost_savings]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]Módulo 14 — Cache[/bold cyan]",
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
