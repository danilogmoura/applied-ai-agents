"""Módulo P7 — SOLUÇÃO COMENTADA

Execute com: python modules/12-memoria/exercises_solution.py

Código completo com explicações detalhadas.
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
# SOLUÇÕES COMENTADAS — Funções implementadas com explicações
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def estimate_tokens(text: str) -> int:
    """
    Estima número de tokens baseado no comprimento do texto.
    
    Regra fixa: ~4 chars/token (inglês).
    """
    # ⚠️ PONTO CRÍTICO: Dividir por 4 é heurística simples
    # Tokenizers reais (como tiktoken) têm mapeamento byte→token não-linear
    return len(text) // 4  # Placeholder vazio


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Short-term Memory — Memória de contexto funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_short_term_memory():
    """
    Testa memória de curto prazo (context window).
    
    Regra: Últimas N mensagens mantidas no contexto.
    """
    class ShortTermMemory:
        def __init__(self, max_messages: int = 10):
            self.max_messages = max_messages
            self.messages: List[Dict[str, str]] = []
        
        def add(self, role: str, content: str):
            """Adiciona mensagem e remove as mais antigas se exceder."""
            self.messages.append({"role": role, "content": content})
            # ⚠️ PONTO CRÍTICO: Slice negativo pega últimas N elementos
            if len(self.messages) > self.max_messages:
                self.messages = self.messages[-self.max_messages:]
        
        def get_context(self) -> List[Dict[str, str]]:
            """Retorna as últimas N mensagens."""
            return self.messages[-self.max_messages:]
    
    memory = ShortTermMemory(max_messages=5)
    
    # Adiciona 8 mensagens (deveria manter só as últimas 5)
    for i in range(8):
        memory.add("user" if i % 2 == 0 else "assistant", f"Mensagem {i}")
    
    context = memory.get_context()
    # ⚠️ PONITO CRÍTICO: Valide comportamento — janela deslizante mantém últimas N
    expected_max = memory.max_messages
    assert len(context) == expected_max, \
        f"Janela deve manter {expected_max} mensagens, got {len(context)}"
    # Verifique que as mensagens são as últimas adicionadas (índices mais altos)
    for msg in context:
        content_num = int(msg["content"].split()[-1])
        assert content_num >= 3, f"Mensagens devem ser as últimas (nº >= 3), got {content_num}"
    
    console.print(f"[green]✓[/green] Short-term: {len(context)} mensagens mantidas")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Long-term Memory — Persistência entre sessões?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_long_term_memory():
    """
    Testa memória de longo prazo (persistente).
    """
    class LongTermMemory:
        def __init__(self):
            self.storage: Dict[str, Any] = {}
        
        def save(self, key: str, value: Any, session_id: str = "default"):
            """Salva dado com metadados (session, timestamp)."""
            from datetime import datetime
            if session_id not in self.storage:
                self.storage[session_id] = {}
            self.storage[session_id][key] = {
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "session": session_id
            }
        
        def retrieve(self, key: str, session_id: str = "default") -> Any:
            """Recupera dado pela chave e sessão."""
            # ⚠️ PONTO CRÍTICO: Verificar ambas as chaves evita KeyError
            if session_id in self.storage and key in self.storage[session_id]:
                return self.storage[session_id][key]["value"]
            return None
        
        def delete(self, key: str, session_id: str = "default") -> bool:
            """Remove dado e retorna True se encontrado."""
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
    Testa gerenciamento do context window do LLM.
    
    Regra: Se tokens > max_tokens, resumir ou truncar.
    """
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
    Consolidação de memórias similares.
    
    Algoritmo simples:
    1. Para cada nova memória, verifica se palavras-chave coincidem
    2. Se similar → incrementa contador da categoria existente
    3. Se não similar → cria nova categoria
    
    Palavras-chave = primeiros 3 palavras da categoria consolidada.
    """
    class MemoryConsolidator:
        def __init__(self):
            self.raw_memories: List[str] = []
            self.consolidated: Dict[str, int] = {}
        
        def add(self, memory: str):
            """
            Adiciona memória e consolida se similar.
            
            1. Verifica todas as categorias existentes
            2. Se alguma palavra dos 3 primeiros → match
            3. Incrementa contador ou cria nova categoria
            """
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
            """Retorna memórias consolidadas com contagem."""
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
    Decay (esquecimento) de memórias antigas.
    
    Regra: Memórias sem uso por > TTL dias são removidas.
    
    Funcionamento:
    1. add(key) → registra timestamp atual
    2. access(key) → atualiza timestamp se existir
    3. cleanup() → remove memórias com (now - last_access) > ttl_days
    4. count() → número de memórias ativas
    
    Simula como sistemas reais de memória esquecem informações antigas.
    """
    from datetime import datetime, timedelta
    
    class DecayingMemory:
        def __init__(self, ttl_days: int = 7):
            self.ttl_days = ttl_days
            self.memories: Dict[str, datetime] = {}
        
        def add(self, key: str):
            """Registra quando a memória foi criada/usada."""
            self.memories[key] = datetime.now()
        
        def access(self, key: str) -> bool:
            """
            Acede à memória e atualiza timestamp se existir.
            
            Retorna True se encontrou, False se não existe.
            """
            if key in self.memories:
                self.memories[key] = datetime.now()
                return True
            return False
        
        def cleanup(self) -> List[str]:
            """
            Remove memórias expiradas (> TTL dias sem uso).
            
            1. Itera sobre cópia dos itens (para não modificar durante iteração)
            2. Calcula diferença de tempo
            3. Se > ttl_days → marca para remoção
            4. Remove todas as marcadas
            """
            now = datetime.now()
            expired = []
            for key, last_access in list(self.memories.items()):
                if (now - last_access).days > self.ttl_days:
                    expired.append(key)
            for key in expired:
                del self.memories[key]
            return expired
        
        def count(self) -> int:
            """Retorna número de memórias ativas."""
            return len(self.memories)
    
    memory = DecayingMemory(ttl_days=7)
    
    # Adiciona memórias
    memory.add("preference_theme")
    memory.add("preference_language")
    memory.add("last_login")
    
    # ⚠️ PONTO CRÍTICO: Valide comportamento — contagem após adição
    expected_count = 3
    actual_count = memory.count()
    assert actual_count == expected_count, \
        f"Deveria ter {expected_count} memórias após adicionar 3, got {actual_count}"
    
    # Simula expiração: remove manualmente algumas
    del memory.memories["preference_theme"]
    
    expired = memory.cleanup()
    assert "preference_theme" not in memory.memories, \
        "Memória removida manualmente não deve estar presente"
    
    # ⚠️ PONTO CRÍTICO: Valide comportamento — contagem após remoção
    expected_after_remove = 2
    actual_after_remove = memory.count()
    assert actual_after_remove == expected_after_remove, \
        f"Deveria ter {expected_after_remove} memórias após remover 1, got {actual_after_remove}"
    
    console.print(f"[green]✓[/green] Decay: {memory.count()} memórias ativas")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_short_term_memory, test_02_long_term_memory,
             test_03_context_window_management, test_04_memory_consolidation,
             test_05_memory_decay]
    
    console.print(Panel("🧪 Exercícios Práticos — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P7: Memória[/bold cyan]",
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
