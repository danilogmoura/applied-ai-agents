"""
Módulo P9 — Cache e Otimização de Custo

Sistema completo de caching para respostas de LLM com Redis simulado,
model routing (caminhos baratos vs caros), prompt compression e
monitoramento de custo em tempo real.

Problema: LLMs são caros. Como reduzir custos sem perder qualidade?
Cache de respostas + roteamento inteligente de modelos.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from shared.logging_config import setup_logging
from shared.cost import TOKEN_PRICES, count_tokens, estimate_cost, format_cost

console = Console()
logger = setup_logging("p9_caching")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# COST MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class ModelInfo:
    """Informações sobre um modelo LLM."""
    
    name: str
    input_price_per_million: float   # $ por milhão de tokens de input
    output_price_per_million: float  # $ por milhão de tokens de output
    max_tokens: int
    is_fast: bool = False             # Modelo "rápido/barato"
    
    @property
    def description(self) -> str:
        return f"{self.name} ({format_cost(self.input_price_per_million / 1_000_000)} per M tokens)"


# Modelos disponíveis
MODELS = {
    "gpt-4o-mini": ModelInfo(
        name="gpt-4o-mini",
        input_price_per_million=0.15,
        output_price_per_million=0.60,
        max_tokens=128_000,
        is_fast=True,
    ),
    "gpt-4o": ModelInfo(
        name="gpt-4o",
        input_price_per_million=2.50,
        output_price_per_million=10.00,
        max_tokens=128_000,
        is_fast=False,
    ),
    "claude-haiku": ModelInfo(
        name="claude-haiku",
        input_price_per_million=0.25,
        output_price_per_million=1.25,
        max_tokens=200_000,
        is_fast=True,
    ),
    "claude-opus": ModelInfo(
        name="claude-opus",
        input_price_per_million=15.00,
        output_price_per_million=75.00,
        max_tokens=200_000,
        is_fast=False,
    ),
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CACHE SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class CacheEntry:
    """Entrada no cache de respostas."""
    
    key: str
    prompt_hash: str
    model: str
    response: str
    cost: float
    created_at: float = field(default_factory=time.time)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    ttl_seconds: int = 3600           # TTL padrão: 1 hora
    
    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds
    
    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "prompt_hash": self.prompt_hash,
            "model": self.model,
            "response": self.response,
            "cost": self.cost,
            "created_at": self.created_at,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed,
            "ttl_seconds": self.ttl_seconds,
        }
    
    @staticmethod
    def from_dict(data: dict) -> CacheEntry:
        return CacheEntry(**data)


class ResponseCache:
    """
    Cache de respostas de LLM com TTL e eviction.
    
    Em produção, usaria Redis ou Memcached.
    Aqui simula com dicionário em memória.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        self._cache: dict[str, CacheEntry] = {}
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.hits = 0
        self.misses = 0
        self.total_savings = 0.0
    
    def _make_key(self, prompt: str, model: str) -> str:
        """Gera chave de cache a partir do prompt e modelo."""
        normalized = prompt.strip().lower()
        hash_digest = hashlib.sha256(f"{model}:{normalized}".encode()).hexdigest()[:16]
        return f"{model}:{hash_digest}"
    
    def get(self, prompt: str, model: str) -> Optional[CacheEntry]:
        """Recupera entrada do cache se existir e não expirada."""
        key = self._make_key(prompt, model)
        
        entry = self._cache.get(key)
        
        if entry is None:
            self.misses += 1
            return None
        
        if entry.is_expired:
            # Remove entrada expirada
            del self._cache[key]
            self.misses += 1
            return None
        
        # Hit!
        self.hits += 1
        entry.access_count += 1
        entry.last_accessed = time.time()
        
        logger.debug(f"Cache hit: {key}")
        return entry
    
    def put(self, prompt: str, model: str, response: str, cost: float) -> None:
        """Armazena resposta no cache."""
        key = self._make_key(prompt, model)
        
        # Eviction se cheio
        if len(self._cache) >= self.max_size and key not in self._cache:
            self._evict()
        
        entry = CacheEntry(
            key=key,
            prompt_hash=hashlib.sha256(prompt.encode()).hexdigest()[:16],
            model=model,
            response=response,
            cost=cost,
            ttl_seconds=self.default_ttl,
        )
        
        self._cache[key] = entry
    
    def _evict(self) -> None:
        """Remove entrada menos acessada (LRU simplificado)."""
        if not self._cache:
            return
        
        # Encontra entrada com menor access_count
        least_used = min(
            self._cache.values(),
            key=lambda e: (e.access_count, e.last_accessed),
        )
        
        del self._cache[least_used.key]
        logger.debug(f"Evicted: {least_used.key}")
    
    def clear_expired(self) -> int:
        """Remove todas as entradas expiradas."""
        expired_keys = [k for k, v in self._cache.items() if v.is_expired]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do cache."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0
        
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_pct": round(hit_rate, 1),
            "total_savings": format_cost(self.total_savings),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MODEL ROUTER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ModelRouter:
    """
    Roteador inteligente de modelos.
    
    Escolhe o modelo mais barato adequado para cada tarefa:
    - Classificação simples → gpt-4o-mini
    - Análise complexa → gpt-4o
    - Geração criativa → claude-opus
    """
    
    def __init__(self):
        self.routing_log: list[dict] = []
    
    def route(self, task_type: str, complexity: str = "medium") -> ModelInfo:
        """
        Escolhe o melhor modelo para a tarefa.
        
        Args:
            task_type: "classify", "summarize", "generate", "analyze", "chat"
            complexity: "low", "medium", "high"
        
        Returns:
            ModelInfo do modelo escolhido.
        """
        # Tabela de roteamento simplificada
        routing_table = {
            ("classify", "low"): "gpt-4o-mini",
            ("classify", "medium"): "gpt-4o-mini",
            ("classify", "high"): "gpt-4o",
            
            ("summarize", "low"): "gpt-4o-mini",
            ("summarize", "medium"): "gpt-4o-mini",
            ("summarize", "high"): "claude-haiku",
            
            ("generate", "low"): "gpt-4o-mini",
            ("generate", "medium"): "claude-haiku",
            ("generate", "high"): "claude-opus",
            
            ("analyze", "low"): "gpt-4o-mini",
            ("analyze", "medium"): "gpt-4o",
            ("analyze", "high"): "claude-opus",
            
            ("chat", "low"): "gpt-4o-mini",
            ("chat", "medium"): "gpt-4o-mini",
            ("chat", "high"): "gpt-4o",
        }
        
        model_name = routing_table.get((task_type, complexity), "gpt-4o-mini")
        model = MODELS[model_name]
        
        self.routing_log.append({
            "task_type": task_type,
            "complexity": complexity,
            "model": model_name,
            "cost_per_input": format_cost(model.input_price_per_million / 1_000_000),
        })
        
        return model
    
    def estimate_cost(self, task_type: str, complexity: str, 
                      input_tokens: int, output_tokens: int) -> dict:
        """Estima custo para diferentes modelos."""
        model = self.route(task_type, complexity)
        cost = estimate_cost(input_tokens, output_tokens, model.name)
        
        return {
            "model": model.name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": format_cost(cost),
            "price_per_million": format_cost(model.input_price_per_million / 1_000_000),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PROMPT COMPRESSION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class PromptCompressor:
    """
    Comprime prompts para reduzir tokens/custo.
    
    Técnicas:
    - Remover whitespace excessivo
    - Truncar mensagens antigas
    - Simplificar system prompt
    - Remover exemplos redundantes
    """
    
    @staticmethod
    def compress_prompt(prompt: str) -> tuple[str, int]:
        """
        Comprime prompt e retorna versão compactada + tokens economizados.
        
        Returns:
            (compressed_prompt, tokens_saved)
        """
        original_tokens = count_tokens([{"role": "user", "content": prompt}])
        
        # Técnica 1: Normalizar whitespace
        compressed = " ".join(prompt.split())
        
        # Técnica 2: Truncar repetições
        lines = compressed.split("\n")
        unique_lines = list(dict.fromkeys(lines))  # Remove duplicatas mantendo ordem
        compressed = "\n".join(unique_lines)
        
        # Técnica 3: Remover espaços vazios no final
        compressed = compressed.rstrip()
        
        compressed_tokens = count_tokens([{"role": "user", "content": compressed}])
        saved = original_tokens - compressed_tokens
        
        return compressed, saved
    
    @staticmethod
    def truncate_messages(messages: list[dict], max_tokens: int) -> list[dict]:
        """
        Trunca mensagens mais antigas para caber no limite de tokens.
        
        Mantém system prompt e últimas mensagens intactas.
        """
        if len(messages) <= 2:
            return messages
        
        # Sempre mantém system prompt e última mensagem
        system_msg = messages[0] if messages[0]["role"] == "system" else None
        last_msg = messages[-1]
        
        middle_msgs = messages[1:-1] if system_msg else messages[:-1]
        
        # Conta tokens das mensagens que devem ser mantidas
        keep_tokens = count_tokens([system_msg, last_msg]) if system_msg else count_tokens([last_msg])
        
        # Remove mensagens do meio até caber
        while middle_msgs:
            test_tokens = keep_tokens + count_tokens(middle_msgs)
            if test_tokens <= max_tokens:
                break
            middle_msgs.pop(0)
        
        result = []
        if system_msg:
            result.append(system_msg)
        result.extend(middle_msgs)
        result.append(last_msg)
        
        return result


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENTE COM CACHE E OTIMIZAÇÃO
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class OptimizedAgent:
    """
    Agente com cache, model routing e prompt compression.
    
    Fluxo otimizado:
    1. Comprime prompt
    2. Verifica cache
    3. Se miss → roteia modelo → gera → salva no cache
    4. Retorna resposta (cache ou gerada)
    """
    
    def __init__(self):
        self.cache = ResponseCache(max_size=500)
        self.router = ModelRouter()
        self.compressor = PromptCompressor()
        self.total_spent = 0.0
        self.total_requests = 0
        self.cache_hits = 0
    
    def chat(self, prompt: str, task_type: str = "chat", 
             complexity: str = "medium") -> dict:
        """
        Executa ciclo completo com otimizações.
        
        Returns:
            Dict com resposta, modelo usado, custo e se veio do cache.
        """
        self.total_requests += 1
        
        # 1. Comprime prompt
        compressed, tokens_saved = self.compressor.compress_prompt(prompt)
        
        # 2. Roteia modelo
        model = self.router.route(task_type, complexity)
        
        # 3. Verifica cache
        cached = self.cache.get(compressed, model.name)
        
        if cached:
            self.cache_hits += 1
            logger.info(f"Cache hit — economia: {format_cost(cached.cost)}")
            
            return {
                "response": cached.response,
                "model": model.name,
                "cost": 0.0,
                "from_cache": True,
                "tokens_saved": tokens_saved,
            }
        
        # 4. Simula geração (em produção, chamaria API real)
        response = self._simulate_response(prompt, model.name)
        input_tok = count_tokens([{"role": "user", "content": compressed}])
        output_tok = len(response.encode()) // 4
        cost = estimate_cost(input_tok, output_tok, model.name)
        
        # 5. Salva no cache
        self.cache.put(compressed, model.name, response, cost)
        
        self.total_spent += cost
        
        logger.info(f"Geração nova: {format_cost(cost)} com {model.name}")
        
        return {
            "response": response,
            "model": model.name,
            "cost": cost,
            "from_cache": False,
            "tokens_saved": tokens_saved,
        }
    
    def _simulate_response(self, prompt: str, model: str) -> str:
        """Simula resposta do LLM."""
        responses = {
            "gpt-4o-mini": "Resposta rápida e barata usando gpt-4o-mini. Ideal para tarefas simples como classificação e chat básico.",
            "gpt-4o": "Resposta de alta qualidade usando gpt-4o. Melhor para análise complexa e raciocínio avançado.",
            "claude-haiku": "Resposta eficiente usando claude-haiku. Bom equilíbrio entre velocidade e qualidade.",
            "claude-opus": "Resposta premium usando claude-opus. Máxima qualidade para tarefas críticas.",
        }
        
        return responses.get(model, "Resposta simulada.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa demonstração completa de cache e otimização."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO P9 — Cache e Otimização de Custo[/]\n\n"
        "Response cache, model routing, prompt compression,\n"
        "e monitoramento de custo em tempo real.",
        title="💰 AI Agents Course",
        border_style="cyan",
    ))
    
    agent = OptimizedAgent()
    
    # ━━ 1. Model Routing Demo ━━
    console.print("\n[bold]1️⃣  Model Routing — Escolhendo o modelo certo:[/]\n")
    
    tasks = [
        ("Classificar email como spam/não-spam", "classify", "low"),
        ("Resumir artigo técnico de 10 páginas", "summarize", "high"),
        ("Gerar descrição de produto", "generate", "medium"),
        ("Analisar sentimento de review", "analyze", "medium"),
        ("Conversar sobre clima", "chat", "low"),
    ]
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Tarefa", style="cyan")
    table.add_column("Modelo", style="green")
    table.add_column("Custo/1M tokens", justify="right")
    
    for prompt, task_type, complexity in tasks:
        model = agent.router.route(task_type, complexity)
        table.add_row(
            prompt[:40],
            model.name,
            f"${model.input_price_per_million:.2f}",
        )
    
    console.print(table)
    
    # ━━ 2. Cache Demo ━━
    console.print("\n[bold]2️⃣  Cache — Mesma pergunta duas vezes:[/]\n")
    
    # Primeira chamada (cache miss)
    result1 = agent.chat("Qual a capital da França?", "chat", "low")
    console.print(f"\n  [dim]Chamada 1:[/]")
    console.print(f"    Modelo: {result1['model']}")
    console.print(f"    Custo: {format_cost(result1['cost'])}")
    console.print(f"    Do cache: {result1['from_cache']}")
    
    # Segunda chamada (cache hit!)
    result2 = agent.chat("Qual a capital da França?", "chat", "low")
    console.print(f"\n  [dim]Chamada 2:[/]")
    console.print(f"    Modelo: {result2['model']}")
    console.print(f"    Custo: {format_cost(result2['cost'])} ✅ ECONOMIA!")
    console.print(f"    Do cache: {result2['from_cache']}")
    
    # ━━ 3. Prompt Compression Demo ━━
    console.print("\n[bold]3️⃣  Prompt Compression — Reduzindo tokens:[/]\n")
    
    long_prompt = """Olá, eu gostaria de saber sobre o clima. 

O clima está bom hoje? Eu estou em São Paulo.
Eu acho que o clima é importante para o meu dia a dia.

Obrigado pela ajuda!"""
    
    compressed, saved = agent.compressor.compress_prompt(long_prompt)
    
    console.print(f"  Original: {count_tokens([{'role': 'user', 'content': long_prompt}])} tokens")
    console.print(f"  Compactado: {count_tokens([{'role': 'user', 'content': compressed}])} tokens")
    console.print(f"  Tokens economizados: {saved}")
    
    # ━━ 4. Estatísticas ━━
    stats = agent.cache.get_stats()
    
    console.print("\n[bold cyan]📊 Estatísticas:[/]\n")
    
    stats_table = Table(show_header=True, header_style="bold cyan")
    stats_table.add_column("Métrica", style="cyan")
    stats_table.add_column("Valor", justify="right")
    
    stats_table.add_row("Total de requests", str(agent.total_requests))
    stats_table.add_row("Cache hits", str(agent.cache_hits))
    stats_table.add_row("Total gasto", format_cost(agent.total_spent))
    
    stats_table.add_row("Tamanho do cache", f"{stats['size']}/{stats['max_size']}")
    stats_table.add_row("Hit rate", f"{stats['hit_rate_pct']}%")
    stats_table.add_row("Economia total", stats['total_savings'])
    
    console.print(stats_table)
    
    console.print("\n[dim]💡 Cache + Model Routing = Economia significativa![/]")


if __name__ == "__main__":
    main()
