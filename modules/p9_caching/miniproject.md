# 🏗️ Mini-Projeto Integrador — Caching & Optimization

> **Objetivo:** Construir um sistema de caching para respostas de LLM.

## O que você vai construir

Um cache manager `cache_system.py` (classe `ResponseCache`) que:

1. **Tracka** hit/miss rates de queries
2. **Implementa** TTL (time-to-live) para entries
3. **Invalida** cache por estratégia (LRU, pattern)
4. **Calcula** economia de custo com caching

## Requisitos

> ℹ️ **Arquitetura de referência:** No `run.py`, a otimização é composta por `ResponseCache` (cache com TTL e hit/miss), `ModelRouter` (escolhe o modelo) e `OptimizedAgent` (orquestra tudo). Aqui você pode começar com uma classe única `ResponseCache`.

```python
class ResponseCache:
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

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com cache em memória

Implemente um dicionário com tracking de hit/miss:

```python
from typing import Any, Optional, Dict, List
from datetime import datetime, timedelta
import hashlib
import json
import random

class ResponseCache:
    def __init__(self):
        self.store = {}           # key -> {value, expires_at, accessed_at}
        self.hits = 0
        self.misses = 0
        self.total_requests = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Retornar valor se no cache, None se miss."""
        self.total_requests += 1
        
        if key not in self.store:
            self.misses += 1
            return None
        
        entry = self.store[key]
        
        # Verifica expiração
        if entry["expires_at"] and datetime.now() > entry["expires_at"]:
            del self.store[key]
            self.misses += 1
            return None
        
        # Atualiza acesso (para LRU)
        entry["accessed_at"] = datetime.now()
        entry["hit_count"] = entry.get("hit_count", 0) + 1
        
        self.hits += 1
        return entry["value"]
    
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Armazenar valor com TTL opcional (em segundos)."""
        expires_at = None
        if ttl is not None:
            expires_at = datetime.now() + timedelta(seconds=ttl)
        
        self.store[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": datetime.now(),
            "accessed_at": datetime.now(),
            "hit_count": 0,
        }
```

### Passo 2 — Implemente TTL e verificação de expiração

```python
    def is_expired(self, key: str) -> bool:
        """Verificar se entry expirou."""
        if key not in self.store:
            return True
        
        entry = self.store[key]
        if entry["expires_at"] is None:
            return False
        
        return datetime.now() > entry["expires_at"]
    
    def cleanup_expired(self) -> int:
        """Remove todas as entries expiradas."""
        expired_keys = [
            key for key, entry in self.store.items()
            if entry["expires_at"] and datetime.now() > entry["expires_at"]
        ]
        
        for key in expired_keys:
            del self.store[key]
        
        return len(expired_keys)
    
    def set_default_ttl(self, ttl_seconds: int = 3600):
        """Define TTL padrão para novos entries."""
        self.default_ttl = ttl_seconds
```

### Passo 3 — Calcule hit rate e economia

```python
    def hit_rate(self) -> float:
        """Calcular taxa de acerto do cache."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests
    
    def savings_percentage(self, cost_per_request: float = 0.01) -> float:
        """Calcular % economizada com cache."""
        if self.total_requests == 0:
            return 0.0
        
        # Requests atendidos pelo cache = economia
        saved_requests = self.hits
        total_cost_without_cache = self.total_requests * cost_per_request
        cost_with_cache = (self.total_requests - saved_requests) * cost_per_request
        
        savings = total_cost_without_cache - cost_with_cache
        return (savings / total_cost_without_cache) * 100 if total_cost_without_cache > 0 else 0
    
    def get_stats(self) -> Dict:
        """Retorna estatísticas completas do cache."""
        return {
            "total_requests": self.total_requests,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hit_rate(), 4),
            "cache_size": len(self.store),
            "savings_pct": round(self.savings_percentage(), 2),
        }
```

### Passo 4 — Implemente invalidação por pattern e LRU

```python
    def invalidate_pattern(self, pattern: str) -> int:
        """Remover keys que contêm pattern."""
        matched_keys = [key for key in self.store if pattern in key]
        
        for key in matched_keys:
            del self.store[key]
        
        return len(matched_keys)
    
    def invalidate_lru(self, n: int = 1) -> List[str]:
        """Remove N entries menos recentemente usadas."""
        if not self.store:
            return []
        
        # Ordena por accessed_at (menos recente primeiro)
        sorted_keys = sorted(
            self.store.keys(),
            key=lambda k: self.store[k]["accessed_at"]
        )
        
        evicted = []
        for key in sorted_keys[:n]:
            del self.store[key]
            evicted.append(key)
        
        return evicted
    
    def invalidate_all(self) -> int:
        """Limpa todo o cache."""
        count = len(self.store)
        self.store.clear()
        return count
    
    def get_lfu_keys(self, n: int = 5) -> List[str]:
        """Retorna N keys mais frequentemente usadas."""
        sorted_keys = sorted(
            self.store.keys(),
            key=lambda k: self.store[k].get("hit_count", 0),
            reverse=True
        )
        return sorted_keys[:n]
```

### Passo 5 — Gere chaves determinísticas

```python
    def generate_cache_key(self, query: str, model: str = "gpt-4o", 
                           temperature: float = 0.7) -> str:
        """Gerar hash determinístico da combinação de parâmetros."""
        # Normaliza query
        normalized_query = query.strip().lower()
        
        # Combina parâmetros
        key_string = f"{model}:{temperature}:{normalized_query}"
        
        # Gera hash SHA-256
        hash_obj = hashlib.sha256(key_string.encode('utf-8'))
        cache_key = hash_obj.hexdigest()[:16]  # Usa primeiros 16 chars
        
        return f"llm:{cache_key}"
    
    def test_key_generation(self) -> Dict:
        """Testa geração de chaves."""
        queries = [
            "Como funciona Python?",
            "O que é machine learning?",
            "Explique redes neurais",
        ]
        
        results = {}
        for q in queries:
            key = self.generate_cache_key(q, "gpt-4o", 0.7)
            results[q] = key
        
        return results
```

### Passo 6 — Simule carga de trabalho

```python
    def simulate_workload(self, queries: List[Dict], 
                          cache_hit_probability: float = 0.6) -> Dict:
        """Simula workload realista com hits/misses."""
        results = {
            "queries_processed": 0,
            "simulated_hits": 0,
            "simulated_misses": 0,
            "cache_efficiency": 0,
        }
        
        for item in queries:
            query = item.get("query", "")
            model = item.get("model", "gpt-4o")
            response = item.get("response", "")
            
            key = self.generate_cache_key(query, model, item.get("temperature", 0.7))
            
            # Decide se é hit ou miss baseado na probabilidade
            if random.random() < cache_hit_probability:
                # Simula hit: put depois get
                self.put(key, response)
                result = self.get(key)
                if result is not None:
                    results["simulated_hits"] += 1
                else:
                    results["simulated_misses"] += 1
            else:
                # Miss direto
                self.put(key, response)
                results["simulated_misses"] += 1
            
            results["queries_processed"] += 1
        
        results["cache_efficiency"] = round(
            results["simulated_hits"] / results["queries_processed"] * 100, 2
        ) if results["queries_processed"] > 0 else 0
        
        return results
```

### Passo 7 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de caching para LLM")
    parser.add_argument("--simulate", action="store_true", help="Simula workload")
    parser.add_argument("--queries", help="Arquivo de queries (JSON)")
    parser.add_argument("--output", help="Arquivo de output")
    parser.add_argument("--capacity", type=int, default=100, help="Capacidade do cache")
    parser.add_argument("--test-key-gen", action="store_true", help="Testa geração de chaves")
    args = parser.parse_args()
    
    cache = ResponseCache()
    
    if args.test_key_gen:
        results = cache.test_key_generation()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif args.simulate:
        # Carrega queries ou usa padrão
        if args.queries:
            with open(args.queries) as f:
                queries = json.load(f)
        else:
            queries = [
                {"query": "Como funciona Python?", "model": "gpt-4o", "temperature": 0.7, "response": "Python é uma linguagem..."},
                {"query": "O que é machine learning?", "model": "gpt-4o", "temperature": 0.7, "response": "ML é um subcampo..."},
                {"query": "Explique redes neurais", "model": "gpt-4o", "temperature": 0.7, "response": "Redes neurais são algoritmos..."},
                {"query": "Como funciona Python?", "model": "gpt-4o", "temperature": 0.7, "response": "Python é uma linguagem..."},  # Hit simulado
                {"query": "Novo assunto", "model": "gpt-4o", "temperature": 0.7, "response": "Novo conteúdo..."},
            ]
        
        sim_result = cache.simulate_workload(queries, cache_hit_probability=0.6)
        stats = cache.get_stats()
        
        output = {
            "simulation": sim_result,
            "stats": stats,
        }
        
        output_str = json.dumps(output, indent=2, ensure_ascii=False)
        print(output_str)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_str)
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `get()` retorna valor ou None (miss), atualiza hit_count e accessed_at
- [ ] `put()` armazena com TTL opcional via timedelta
- [ ] `is_expired()` verifica expires_at contra datetime.now()
- [ ] `hit_rate()` calcula hits / total_requests
- [ ] `invalidate_pattern()` remove keys por substring; `invalidate_lru()` remove N menos acessadas
- [ ] `generate_cache_key()` gera hash SHA-256 determinístico dos parâmetros
- [ ] CLI aceita `--simulate`, `--queries` e gera stats JSON

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

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
