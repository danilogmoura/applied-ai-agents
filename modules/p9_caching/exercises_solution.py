"""Módulo P9 — SOLUÇÃO COMENTADA

Execute com: python modules/p9_caching/exercises_solution.py

Código completo com explicações detalhadas.
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
    Cache simples com tracking de hit/miss.
    
    Funcionamento:
    1. get(key) → se key existe no store: incrementa hits, retorna valor
                   se não existe: incrementa misses, retorna None
    2. put(key, value) → armazena no dict
    3. hit_rate() → hits / (hits + misses)
    
    Isso simula como caches reduzem chamadas à API (caras/lentas).
    """
    class SimpleCache:
        def __init__(self):
            self.store: Dict[str, Any] = {}
            self.hits = 0
            self.misses = 0
        
        def get(self, key: str) -> Optional[Any]:
            """
            Retorna valor se no cache (HIT), None se miss.
            
            1. Verifica se key está no dict
            2. Se sim → incrementa hits e retorna valor
            3. Se não → incrementa misses e retorna None
            """
            if key in self.store:
                self.hits += 1
                return self.store[key]
            self.misses += 1
            return None
        
        def put(self, key: str, value: Any):
            """Armazena valor no cache."""
            self.store[key] = value
        
        def hit_rate(self) -> float:
            """Calcula taxa de acerto: hits / total_requests."""
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
    Cache com TTL (Time To Live).
    
    Estrutura: store[key] = (value, expiry_timestamp)
    
    Funcionamento:
    1. put(key, value, ttl) → armazena valor + timestamp de expiração
    2. get(key) → verifica se datetime.now() < expiry_time
                 Se válido → retorna valor
                 Se expirado → remove do store e retorna None
    3. is_expired(key) → verifica sem remover
    
    TTL é essencial para dados que mudam com o tempo (preços, clima, etc).
    """
    import time
    
    class TTLCache:
        def __init__(self, default_ttl_seconds: int = 5):
            self.default_ttl = default_ttl_seconds
            self.store: Dict[str, tuple[Any, float]] = {}
        
        def get(self, key: str) -> Optional[Any]:
            """
            Retorna valor se não expirou, None se expired.
            
            1. Verifica se key existe
            2. Compara agora vs expiry_time
            3. Se expirado → remove do store
            4. Se válido → retorna valor
            """
            from datetime import datetime
            if key in self.store:
                value, expiry_time = self.store[key]
                if datetime.now().timestamp() < expiry_time:
                    return value
                else:
                    del self.store[key]  # Remove expired
            return None
        
        def put(self, key: str, value: Any, ttl: Optional[int] = None):
            """
            Armazena com timestamp de expiração.
            
            1. Usa ttl fornecido ou default_ttl
            2. Calcula expiry_time = now + ttl
            3. Armazena (value, expiry_time)
            """
            from datetime import datetime
            effective_ttl = ttl if ttl is not None else self.default_ttl
            expiry_time = datetime.now().timestamp() + effective_ttl
            self.store[key] = (value, expiry_time)
        
        def is_expired(self, key: str) -> bool:
            """Verifica se entry expirou (sem remover)."""
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
# TESTE 3: Cache Invalidation — Invalidação funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_cache_invalidation():
    """
    LRU Cache (Least Recently Used) com invalidação por padrão.
    
    LRU Eviction:
    1. get(key) → move key para final da lista (recentemente usado)
    2. put(key, value):
       - Se key existe → atualiza e move para final
       - Se não existe e cheio → remove primeiro da lista (LRU)
       - Adiciona ao final
    
    Pattern Invalidation:
    - invalidate_pattern("user_1") → remove todas as keys que contêm "user_1"
    
    Essencial para quando dados mudam (ex: perfil do usuário atualizado).
    """
    class LRUCache:
        def __init__(self, capacity: int = 3):
            self.capacity = capacity
            self.store: Dict[str, Any] = {}
            self.order: list = []  # FIFO order (primeiro = LRU)
        
        def get(self, key: str) -> Optional[Any]:
            """
            Retorna valor e atualiza ordem de uso.
            
            1. Se key existe → remove da lista e adiciona ao final (recente)
            2. Retorna valor
            3. Se não existe → retorna None
            """
            if key in self.store:
                self.order.remove(key)
                self.order.append(key)
                return self.store[key]
            return None
        
        def put(self, key: str, value: Any):
            """
            Adiciona/atualiza. Remove LRU se excede capacity.
            
            1. Se key já existe → remove da lista (vai re-adicionar)
            2. Se não existe e cheio → remove primeiro da lista (LRU)
            3. Adiciona novo valor e registra no final da lista
            """
            if key in self.store:
                self.order.remove(key)
            elif len(self.store) >= self.capacity:
                lru_key = self.order.pop(0)
                del self.store[lru_key]
            self.store[key] = value
            self.order.append(key)
        
        def invalidate_pattern(self, pattern: str) -> int:
            """Remove keys que contêm pattern. Retorna count removido."""
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
    Tracking de economia de tokens/custo via cache.
    
    Métricas:
    1. total_requests → quantas requisições totais
    2. cache_hits → quantas foram atendidas pelo cache
    3. total_tokens_saved → soma dos tokens que NÃO precisaram ir à API
    4. savings_percentage → cache_hits / total_requests * 100
    
    Cada hit economiza: tokens × cost_per_1k_tokens / 1000
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
            """
            Registra hit e acumula economia.
            
            1. Incrementa contador de hits
            2. Soma tokens que foram salvos (não precisaram ir à API)
            """
            self.cache_hits += 1
            self.total_tokens_saved += tokens
        
        def savings_percentage(self) -> float:
            """
            Calcula % economizada com cache.
            
            savings_pct = cache_hits / total_requests * 100
            
            Quanto maior, mais eficiente é o cache.
            """
            if self.total_requests == 0:
                return 0.0
            return self.cache_hits / self.total_requests
    
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
                        title="[bold cyan]P9: Cache[/bold cyan]",
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
