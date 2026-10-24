# 🏗️ Mini-Projeto Integrador — Memory & Context

> **Objetivo:** Construir um sistema de memória para agente IA.

## O que você vai construir

Um memory manager `memory_system.py` (classe `AgentWithMemory`) que:

1. **Gerencia** memória de curto prazo (context window)
2. **Persiste** memória de longo prazo entre sessões
3. **Consolida** memórias similares automaticamente
4. **Aplica** decay (esquecimento) em memórias antigas

## Requisitos

> ℹ️ **Arquitetura de referência:** No `run.py`, a memória é dividida em `ShortTermMemory` (context window) e `LongTermMemory` (persistente), orquestradas pela classe principal `AgentWithMemory`. Aqui você pode começar com uma classe única `AgentWithMemory`; quando quiser, separe curta e longa memória em classes próprias, como na referência.

```python
class AgentWithMemory:
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

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com memória de curto prazo

Implemente uma fila circular para o context window:

```python
from datetime import datetime, timedelta
from typing import Any, List, Dict, Optional
import json
import os

class AgentWithMemory:
    def __init__(self):
        self.short_term = []  # Context window atual
        self.long_term = {}   # Memória persistente {session_id: {key: {value, last_accessed}}}
        self.max_messages = 10
    
    def add_to_short_term(self, role: str, content: str, 
                          max_messages: int = None) -> List[Dict]:
        """Adicionar mensagem à memória curta, remover excessos."""
        if max_messages is None:
            max_messages = self.max_messages
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        
        # Adiciona ao fim da fila
        self.short_term.append(message)
        
        # Remove excessos (mantém apenas max_messages)
        if len(self.short_term) > max_messages:
            self.short_term = self.short_term[-max_messages:]
        
        return self.short_term
    
    def get_context_window(self, last_n: int = None) -> List[Dict]:
        """Retorna as últimas N mensagens do context window."""
        if last_n is None:
            return self.short_term
        return self.short_term[-last_n:]
    
    def clear_short_term(self):
        """Limpa memória de curto prazo."""
        self.short_term.clear()
```

### Passo 2 — Implemente persistência de longo prazo

Salve e recupere dados entre sessões:

```python
    def save_to_long_term(self, key: str, value: dict, 
                          session_id: str = "default") -> bool:
        """Salvar dado persistente por sessão."""
        if session_id not in self.long_term:
            self.long_term[session_id] = {}
        
        self.long_term[session_id][key] = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat(),
            "access_count": 0,
        }
        
        return True
    
    def retrieve_long_term(self, key: str, 
                           session_id: str = "default") -> Optional[Any]:
        """Recuperar dado da memória longa."""
        if session_id not in self.long_term:
            return None
        
        if key not in self.long_term[session_id]:
            return None
        
        entry = self.long_term[session_id][key]
        # Atualiza acesso
        entry["last_accessed"] = datetime.now().isoformat()
        entry["access_count"] += 1
        
        return entry["value"]
    
    def delete_from_long_term(self, key: str, 
                              session_id: str = "default") -> bool:
        """Remove dado da memória longa."""
        if session_id in self.long_term and key in self.long_term[session_id]:
            del self.long_term[session_id][key]
            return True
        return False
    
    def list_keys(self, session_id: str = "default") -> List[str]:
        """Lista todas as chaves de uma sessão."""
        if session_id in self.long_term:
            return list(self.long_term[session_id].keys())
        return []
```

### Passo 3 — Implemente consolidação de memórias

Agrupe memórias similares em categorias:

```python
    def consolidate_memories(self, raw_memories: List[Dict]) -> Dict:
        """Consolidar memórias similares em categorias usando keyword matching."""
        categories = {}
        
        for memory in raw_memories:
            content = memory.get("content", "").lower()
            keywords = set(content.split())
            
            # Encontra categoria mais similar
            best_category = None
            best_overlap = 0
            
            for cat, cat_keywords in categories.items():
                overlap = len(keywords & cat_keywords)
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_category = cat
            
            # Se nenhuma categoria similar, cria nova
            if best_category is None or best_overlap < 2:
                new_cat = f"category_{len(categories)}"
                categories[new_cat] = {
                    "keywords": set(),
                    "memories": [],
                    "count": 0,
                }
                best_category = new_cat
            
            # Adiciona à categoria
            categories[best_category]["keywords"].update(keywords)
            categories[best_category]["memories"].append(memory)
            categories[best_category]["count"] += 1
        
        return {
            "categories": categories,
            "total_raw": len(raw_memories),
            "total_categories": len(categories),
            "compression_ratio": round(len(categories) / len(raw_memories), 2) if raw_memories else 0,
        }
    
    def summarize_category(self, category_data: Dict) -> str:
        """Gera resumo de uma categoria consolidada."""
        memories = category_data.get("memories", [])
        if not memories:
            return ""
        
        # Extrai palavras-chave únicas
        all_words = set()
        for m in memories:
            all_words.update(m.get("content", "").split())
        
        # Remove stopwords básicas
        stop_words = {"o", "a", "os", "as", "um", "uma", "de", "do", "da", "em", "para", "com"}
        keywords = [w for w in all_words if w.lower() not in stop_words and len(w) > 2]
        
        return f"{category_data['count']} memórias | Keywords: {', '.join(keywords[:10])}"
```

### Passo 4 — Implemente decay (esquecimento)

Remova memórias antigas baseado em TTL:

```python
    def cleanup_expired(self, ttl_days: int = 7) -> int:
        """Remover memórias expiradas (> N dias sem uso)."""
        now = datetime.now()
        expired_keys = []
        
        for session_id, entries in self.long_term.items():
            for key, entry in entries.items():
                last_accessed = datetime.fromisoformat(entry["last_accessed"])
                age = (now - last_accessed).days
                
                if age > ttl_days:
                    expired_keys.append((session_id, key))
        
        # Remove memórias expiradas
        for session_id, key in expired_keys:
            if key in self.long_term.get(session_id, {}):
                del self.long_term[session_id][key]
        
        return len(expired_keys)
    
    def get_memory_stats(self) -> Dict:
        """Retorna estatísticas do sistema de memória."""
        total_entries = sum(
            len(entries) for entries in self.long_term.values()
        )
        
        return {
            "short_term_size": len(self.short_term),
            "long_term_sessions": len(self.long_term),
            "long_term_total_entries": total_entries,
            "sessions": {
                sid: len(entries) 
                for sid, entries in self.long_term.items()
            },
        }
```

### Passo 5 — Salgue/carregue estado persistente

```python
    def save_state(self, filepath: str = "memory_state.json"):
        """Salva todo estado do sistema em JSON."""
        state = {
            "short_term": self.short_term,
            "long_term": self.long_term,
            "saved_at": datetime.now().isoformat(),
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def load_state(self, filepath: str = "memory_state.json"):
        """Carrega estado do sistema a partir de JSON."""
        if not os.path.exists(filepath):
            print(f"⚠️  Arquivo {filepath} não encontrado.")
            return False
        
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.short_term = state.get("short_term", [])
        self.long_term = state.get("long_term", {})
        return True
```

### Passo 6 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de memória para agente IA")
    parser.add_argument("--session", default="user_123", help="ID da sessão")
    parser.add_argument("--messages", help="Arquivo de mensagens (JSON)")
    parser.add_argument("--consolidate", help="Arquivo para consolidar memórias (JSON)")
    parser.add_argument("--output", help="Arquivo de output")
    parser.add_argument("--ttl", type=int, default=7, help="TTL em dias para cleanup")
    parser.add_argument("--save", action="store_true", help="Salva estado")
    parser.add_argument("--load", action="store_true", help="Carrega estado")
    args = parser.parse_args()
    
    system = AgentWithMemory()
    
    # Carrega estado se solicitado
    if args.load:
        system.load_state()
    
    # Processa mensagens
    if args.messages:
        with open(args.messages) as f:
            messages = json.load(f)
        
        for msg in messages:
            system.add_to_short_term(
                role=msg.get("role", "user"),
                content=msg.get("content", ""),
            )
        
        print(f"📝 Memória curta: {len(system.short_term)} mensagens")
    
    # Consolida memórias
    if args.consolidate:
        with open(args.consolidate) as f:
            raw_memories = json.load(f)
        
        result = system.consolidate_memories(raw_memories)
        print(f"\n📊 Consolidação:")
        print(f"   Raw memories: {result['total_raw']}")
        print(f"   Categories: {result['total_categories']}")
        print(f"   Compression ratio: {result['compression_ratio']}")
        
        for cat_id, cat_data in result["categories"].items():
            summary = system.summarize_category(cat_data)
            print(f"   📁 {cat_id}: {summary}")
    
    # Cleanup
    expired = system.cleanup_expired(ttl_days=args.ttl)
    if expired > 0:
        print(f"\n🗑️  Removidas {expired} memórias expiradas")
    
    # Stats
    stats = system.get_memory_stats()
    print(f"\n📈 Estatísticas:")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # Salva estado
    if args.save:
        system.save_state()
        print("\n💾 Estado salvo em memory_state.json")
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `add_to_short_term()` mantém fila circular com max_messages mensagens
- [ ] `save_to_long_term()` e `retrieve_long_term()` persistem dados por session_id com access tracking
- [ ] `consolidate_memories()` agrupa memórias por keyword overlap (≥ 2 palavras)
- [ ] `cleanup_expired()` remove memórias com last_accessed > TTL dias
- [ ] `save_state()` / `load_state()` serializam/deserializam todo estado em JSON
- [ ] CLI aceita `--messages`, `--consolidate`, `--ttl`, `--save`, `--load`

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

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
