"""
Módulo P7 — Teste do Exercício

Execute com: python modules/p7_memory/test_exercise.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Short-term Memory — Memória de contexto funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_short_term_memory():
    """
    TODO: Implemente memória de curto prazo (context window).
    
    Regra: Últimas N mensagens mantidas no contexto.
    """
    class ShortTermMemory:
        def __init__(self, max_messages: int = 10):
            self.max_messages = max_messages
            self.messages: List[Dict[str, str]] = []
        
        def add(self, role: str, content: str):
            """TODO: Adicione mensagem e remova as mais antigas se exceder."""
            pass  # ← Implemente
        
        def get_context(self) -> List[Dict[str, str]]:
            """TODO: Retorne as últimas N mensagens."""
            return []  # ← Implemente
    
    memory = ShortTermMemory(max_messages=5)
    
    # Adiciona 8 mensagens (deveria manter só as últimas 5)
    for i in range(8):
        memory.add("user" if i % 2 == 0 else "assistant", f"Mensagem {i}")
    
    context = memory.get_context()
    assert len(context) == 5, \
        f"Deveria manter apenas 5 mensagens, got {len(context)}"
    assert context[0]["content"] == "Mensagem 3", \
        "Primeira mensagem do contexto deve ser a 3ª (índice 3)"
    
    console.print(f"[green]✓[/green] Short-term: {len(context)} mensagens mantidas")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Long-term Memory — Persistência entre sessões?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_long_term_memory():
    """
    TODO: Implemente memória de longo prazo (persistente).
    """
    class LongTermMemory:
        def __init__(self):
            self.storage: Dict[str, Any] = {}
        
        def save(self, key: str, value: Any, session_id: str = "default"):
            """TODO: Salve dado com metadados (session, timestamp)."""
            pass  # ← Implemente
        
        def retrieve(self, key: str, session_id: str = "default") -> Any:
            """TODO: Recupere dado pela chave e sessão."""
            return None  # ← Implemente
        
        def delete(self, key: str, session_id: str = "default") -> bool:
            """TODO: Remova dado e retorne True se encontrado."""
            return False  # ← Implemente
    
    memory = LongTermMemory()
    
    # Salva
    memory.save("user_preference", {"theme": "dark"}, "session_1")
    
    # Recupera
    retrieved = memory.retrieve("user_preference", "session_1")
    assert retrieved is not None, "Dado deveria ser recuperado"
    assert retrieved["theme"] == "dark", \
        f"Dado recuperado deveria ter theme='dark', got {retrieved}"
    
    # Não recupera em sessão diferente
    wrong_session = memory.retrieve("user_preference", "session_2")
    assert wrong_session is None, \
        "Dados não devem vazar entre sessões"
    
    console.print("[green]✓[/green] Long-term: save ✓, retrieve ✓, isolate ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Context Window Management — Janela gerida corretamente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_context_window_management():
    """
    TODO: Gerencie o context window do LLM eficientemente.
    
    Regra: Se tokens > max_tokens, resumir ou truncar.
    """
    def estimate_tokens(text: str) -> int:
        return len(text) // 4  # ~4 chars per token
    
    messages = [
        {"role": "user", "content": "Olá"},
        {"role": "assistant", "content": "Olá! Como posso ajudar?"},
        {"role": "user", "content": "Quero saber sobre reembolso"},
        {"role": "assistant", "content": "Reembolsos podem ser solicitados em até 30 dias..."},
    ] * 10  # 20 mensagens = muito contexto
    
    max_tokens = 200
    
    total_tokens = sum(estimate_tokens(m["content"]) for m in messages)
    
    # TODO: Trunque ou resuma se exceder max_tokens
    trimmed_messages = messages[:]  # ← Implemente lógica de trim
    
    trimmed_tokens = sum(estimate_tokens(m["content"]) for m in trimmed_messages)
    
    assert trimmed_tokens <= max_tokens, \
        f"Tokens após trim ({trimmed_tokens}) devem caber em {max_tokens}"
    assert len(trimmed_messages) > 0, \
        "Deveria manter pelo menos algumas mensagens"
    
    console.print(f"[green]✓[/green] Context window: {total_tokens}→{trimmed_tokens} tokens")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Memory Consolidation — Consolidação automática?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_memory_consolidation():
    """
    TODO: Implemente consolidação de memórias similares.
    
    Múltiplas menções → uma memória consolidada.
    """
    class MemoryConsolidator:
        def __init__(self):
            self.raw_memories: List[str] = []
            self.consolidated: Dict[str, int] = {}
        
        def add(self, memory: str):
            """TODO: Adicione memória e consolide se similar."""
            pass  # ← Implemente
        
        def get_summary(self) -> Dict[str, int]:
            """TODO: Retorne memórias consolidadas com contagem."""
            return {}  # ← Implemente
    
    consolidator = MemoryConsolidator()
    
    # Adiciona memórias repetidas/similares
    memories = [
        "Usuário prefere tema escuro",
        "Usuário gosta de tema dark",
        "Usuário prefere modo escuro",
        "Usuário quer notificações por email",
        "Usuário prefere notificações por email",
    ]
    
    for m in memories:
        consolidator.add(m)
    
    summary = consolidator.get_summary()
    
    # Deveria consolidar em ~2 categorias principais
    assert len(summary) <= 3, \
        f"Memórias similares deveriam ser consolidadas, got {len(summary)} categorias"
    
    total_mentions = sum(summary.values())
    assert total_mentions == len(memories), \
        f"Total de menções preservado: {total_mentions} == {len(memories)}"
    
    console.print(f"[green]✓[/green] Consolidation: {len(memories)} → {len(summary)} categorias")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Memory Decay — Memórias expiram?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_memory_decay():
    """
    TODO: Implemente decay (esquecimento) de memórias antigas.
    
    Regra: Memorias sem uso por > 7 dias são removidas.
    """
    from datetime import datetime, timedelta
    
    class DecayingMemory:
        def __init__(self, ttl_days: int = 7):
            self.ttl_days = ttl_days
            self.memories: Dict[str, datetime] = {}
        
        def add(self, key: str):
            """TODO: Adicione memória com timestamp atual."""
            pass  # ← Implemente
        
        def is_expired(self, key: str) -> bool:
            """TODO: Verifique se memória expirou."""
            return False  # ← Implemente
        
        def cleanup(self) -> int:
            """TODO: Remova memórias expiradas e retorne count."""
            return 0  # ← Implemente
    
    memory = DecayingMemory(ttl_days=7)
    
    # Simula memórias antigas (usando datetime hack)
    old_time = datetime.now() - timedelta(days=10)
    new_time = datetime.now() - timedelta(days=1)
    
    memory.memories = {
        "old_pref": old_time,
        "new_pref": new_time,
        "recent_note": datetime.now(),
    }
    
    removed = memory.cleanup()
    remaining = len(memory.memories)
    
    assert removed >= 1, \
        "Pelo menos 1 memória antiga deveria ser removida"
    assert remaining == 2, \
        f"Devem restar 2 memórias recentes, got {remaining}"
    
    console.print(f"[green]✓[/green] Decay: {removed} removida(s), {remaining} restantes")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_short_term_memory, test_02_long_term_memory,
             test_03_context_window_management, test_04_memory_consolidation,
             test_05_memory_decay]
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P7: Memória e Contexto[/bold cyan]",
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
