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
            """Adicione mensagem e remova as mais antigas se exceder."""
            self.messages.append({"role": role, "content": content})
            if len(self.messages) > self.max_messages:
                self.messages = self.messages[-self.max_messages:]
        
        def get_context(self) -> List[Dict[str, str]]:
            """Retorne as últimas N mensagens."""
            return self.messages[-self.max_messages:]
    
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
            """Salve dado com metadados (session, timestamp)."""
            from datetime import datetime
            if session_id not in self.storage:
                self.storage[session_id] = {}
            self.storage[session_id][key] = {
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "session": session_id
            }
        
        def retrieve(self, key: str, session_id: str = "default") -> Any:
            """Recupere dado pela chave e sessão."""
            if session_id in self.storage and key in self.storage[session_id]:
                return self.storage[session_id][key]["value"]
            return None
        
        def delete(self, key: str, session_id: str = "default") -> bool:
            """Remova dado e retorne True se encontrado."""
            if session_id in self.storage and key in self.storage[session_id]:
                del self.storage[session_id][key]
                return True
            return False
    
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
    
    # Truncar se exceder max_tokens - manter system prompt + últimas mensagens
    trimmed_messages = []
    current_tokens = 0
    
    # Manter primeiras mensagens (system prompt)
    if messages and messages[0].get("role") == "system":
        system_tokens = estimate_tokens(messages[0]["content"])
        if system_tokens <= max_tokens:
            trimmed_messages.append(messages[0])
            current_tokens += system_tokens
    
    # Adicionar mensagens do final até atingir limite
    for msg in reversed(messages):
        if msg.get("role") == "system":
            continue  # Já adicionado
        msg_tokens = estimate_tokens(msg["content"])
        if current_tokens + msg_tokens <= max_tokens:
            trimmed_messages.insert(0, msg)
            current_tokens += msg_tokens
        else:
            break
    
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
            """Adicione memória e consolide se similar."""
            self.raw_memories.append(memory)
            # Verificar se já existe categoria similar
            found = False
            for category in self.consolidated:
                if any(word in memory.lower() for word in category.lower().split()[:3]):
                    self.consolidated[category] += 1
                    found = True
                    break
            if not found:
                self.consolidated[memory] = 1
        
        def get_summary(self) -> Dict[str, int]:
            """Retorne memórias consolidadas com contagem."""
            return self.consolidated.copy()
    
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
            """Adicione memória com timestamp atual."""
            from datetime import datetime
            self.memories[key] = datetime.now()
        
        def is_expired(self, key: str) -> bool:
            """Verifique se memória expirou."""
            from datetime import timedelta
            if key not in self.memories:
                return True
            age = datetime.now() - self.memories[key]
            return age.days > self.ttl_days
        
        def cleanup(self) -> int:
            """Remova memórias expiradas e retorne count."""
            expired_keys = [k for k in self.memories if self.is_expired(k)]
            for key in expired_keys:
                del self.memories[key]
            return len(expired_keys)
    
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
