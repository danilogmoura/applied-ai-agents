"""
Módulo P7 — Memória e Gerenciamento de Contexto

Sistema completo de memória para agentes: curto prazo (conversation history),
longo prazo (vector store), summarization automática e gestão do context window.

Problema: Agentes sem memória são como peixes com memória de 3 segundos.
Como manter contexto entre interações sem exceder o limit de tokens?
"""

from __future__ import annotations

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
from shared.cost import count_tokens, estimate_cost, format_cost

console = Console()
logger = setup_logging("p7_memory")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MESSAGE / MEMORY MODELS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class Message:
    """Mensagem individual na conversa."""
    
    role: str              # "user", "assistant", "system"
    content: str
    timestamp: float = field(default_factory=time.time)
    tokens: int = 0        # Tokens aproximados
    
    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "tokens": self.tokens,
        }
    
    @staticmethod
    def from_dict(data: dict) -> Message:
        msg = Message(**{k: v for k, v in data.items() if k != "summary"})
        msg.tokens = len(msg.content.encode()) // 4
        return msg


@dataclass
class MemoryEntry:
    """Entrada de memória de longo prazo."""
    
    id: str
    content: str
    category: str = "general"           # Categoria da memória
    importance: float = 0.5             # Importância (0-1)
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0               # Quantas vezes foi acessada
    summary: Optional[str] = None       # Resumo compactado
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category,
            "importance": self.importance,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count,
            "summary": self.summary,
        }
    
    @staticmethod
    def from_dict(data: dict) -> MemoryEntry:
        return MemoryEntry(**data)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SHORT-TERM MEMORY (Conversation History)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ShortTermMemory:
    """
    Memória de curto prazo = histórico de conversa.
    
    Gerencia o context window: adiciona mensagens, remove as mais antigas
    quando o limite de tokens se aproxima.
    
    Estratégias de gestão:
    - Sliding window: remove as mais antigas
    - Token budget: para quando atingir limite de tokens
    - Summarization: resume conversas longas em vez de deletar
    """
    
    def __init__(self, max_tokens: int = 4000, strategy: str = "summarization"):
        """
        Args:
            max_tokens: Limite máximo de tokens para manter no histórico.
            strategy: "sliding" (remove antigas), "token_budget" (para de adicionar),
                     ou "summarization" (resume quando cheio).
        """
        self.messages: list[Message] = []
        self.max_tokens = max_tokens
        self.strategy = strategy
        self.total_tokens_used = 0
        self.summaries: list[str] = []  # Resumos de segmentos anteriores
    
    def _count_tokens(self, text: str) -> int:
        """Conta tokens aproximados."""
        return len(text.encode()) // 4
    
    def add_message(self, role: str, content: str) -> bool:
        """
        Adiciona mensagem ao histórico.
        
        Returns:
            True se adicionada com sucesso, False se excedeu limite.
        """
        msg = Message(role=role, content=content)
        msg.tokens = self._count_tokens(content)
        
        # Verifica se vai exceder o limite
        current_tokens = sum(m.tokens for m in self.messages)
        
        if current_tokens + msg.tokens > self.max_tokens:
            # Estratégia ativa
            if self.strategy == "summarization":
                self._summarize_older_messages()
                # Tenta adicionar novamente após resumir
                current_tokens = sum(m.tokens for m in self.messages)
                if current_tokens + msg.tokens > self.max_tokens:
                    # Ainda excedeu — faz sliding window
                    self._trim_to_limit()
            elif self.strategy == "sliding":
                self._trim_to_limit()
            else:  # token_budget
                logger.warning("Token budget atingido — mensagem não adicionada")
                return False
        
        self.messages.append(msg)
        self.total_tokens_used += msg.tokens
        return True
    
    def _summarize_older_messages(self) -> None:
        """Resume mensagens mais antigas para liberar espaço."""
        if len(self.messages) < 4:
            return  # Poucas mensagens, não precisa resumir
        
        # Divide mensagens em chunks para resumir
        chunk_size = max(len(self.messages) // 2, 2)
        messages_to_summarize = self.messages[:chunk_size]
        
        # Cria prompt de sumarização simplificado
        conversation = "\n".join(
            f"[{m.role}]: {m.content[:100]}" for m in messages_to_summarize
        )
        
        summary = f"... [Segmento resumido: {len(messages_to_summarize)} mensagens] ..."
        self.summaries.append(summary)
        
        # Substitui mensagens por um resumo
        summary_msg = Message(
            role="system",
            content=f"[RESUMO DE CONVERSA ANTERIOR]\n{summary}",
            tokens=self._count_tokens(summary),
        )
        
        self.messages = self.messages[chunk_size:]
        self.messages.insert(0, summary_msg)
        
        logger.info(f"Resumidos {chunk_size} mensagens → summary")
    
    def _trim_to_limit(self) -> None:
        """Remove mensagens mais antigas até caber no limite."""
        while len(self.messages) > 1:
            removed = self.messages.pop(0)
            self.total_tokens_used -= removed.tokens
            if sum(m.tokens for m in self.messages) <= self.max_tokens:
                break
    
    def get_context(self, keep_last: int = 0) -> list[dict]:
        """
        Retorna contexto atual para enviar ao LLM.
        
        Args:
            keep_last: Se > 0, mantém apenas as últimas N mensagens.
                      Se 0, retorna tudo.
        """
        messages = self.messages[-keep_last:] if keep_last > 0 else self.messages
        
        # Inclui summaries no início
        context = []
        for summary in self.summaries:
            context.append({"role": "system", "content": summary})
        
        for msg in messages:
            context.append({"role": msg.role, "content": msg.content})
        
        return context
    
    def get_status(self) -> dict:
        """Retorna status da memória de curto prazo."""
        total_tokens = sum(m.tokens for m in self.messages)
        
        return {
            "strategy": self.strategy,
            "max_tokens": self.max_tokens,
            "current_tokens": total_tokens,
            "message_count": len(self.messages),
            "summary_count": len(self.summaries),
            "utilization_pct": round(total_tokens / self.max_tokens * 100, 1),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LONG-TERM MEMORY (Vector Store Simulado)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class LongTermMemory:
    """
    Memória de longo prazo = conhecimento persistente entre sessões.
    
    Armazena informações importantes que persistem entre conversas.
    Usa embedding simples para recuperação semântica.
    """
    
    def __init__(self, max_entries: int = 100):
        self.entries: list[MemoryEntry] = []
        self.max_entries = max_entries
        self._vocab: dict[str, int] = {}
        self._fitted = False
    
    def _build_vocab(self) -> None:
        """Constrói vocabulário a partir das memórias existentes."""
        word_freq: dict[str, int] = {}
        for entry in self.entries:
            for word in entry.content.lower().split():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        stopwords = {"a", "e", "o", "de", "do", "da", "em", "um", "uma"}
        self._vocab = {
            word: idx for idx, (word, _) in enumerate(
                sorted((w for w in word_freq if w not in stopwords and len(w) > 2),
                       key=lambda x: -x[1])
            )[:128]
        }
        self._fitted = True
    
    def _embed(self, text: str) -> list[float]:
        """Gera embedding simples baseado em TF."""
        if not self._fitted:
            self._build_vocab()
        
        vec = [0.0] * len(self._vocab)
        words = text.lower().split()
        
        for word in words:
            if word in self._vocab:
                idx = self._vocab[word]
                tf = words.count(word) / max(len(words), 1)
                vec[idx] += tf
        
        # Normaliza L2
        norm = sum(v * v for v in vec) ** 0.5
        if norm > 0:
            vec = [v / norm for v in vec]
        
        return vec
    
    def _cosine_similarity(self, a: list[float], b: list[float]) -> float:
        """Calcula similaridade cosseno entre dois vetores."""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot / (norm_a * norm_b)
    
    def store(self, content: str, category: str = "general", 
              importance: float = 0.5) -> str:
        """Armazena entrada na memória de longo prazo."""
        entry_id = f"mem_{len(self.entries) + 1:04d}"
        
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            category=category,
            importance=importance,
        )
        
        self.entries.append(entry)
        
        # Mantém tamanho máximo
        if len(self.entries) > self.max_entries:
            # Remove menos importantes e mais antigas
            self.entries.sort(key=lambda e: (e.importance, e.last_accessed))
            self.entries = self.entries[-self.max_entries:]
        
        logger.info(f"Memória armazenada: {entry_id} ({category})")
        return entry_id
    
    def retrieve(self, query: str, top_k: int = 5) -> list[MemoryEntry]:
        """Recupera memórias relevantes para uma query."""
        if not self.entries:
            return []
        
        query_embedding = self._embed(query)
        
        scored = []
        for entry in self.entries:
            entry_embedding = self._embed(entry.content)
            similarity = self._cosine_similarity(query_embedding, entry_embedding)
            
            # Combina similaridade semântica + importância + frequência de acesso
            score = similarity * 0.6 + entry.importance * 0.2 + (
                min(entry.access_count / 10, 1.0) * 0.2
            )
            
            scored.append((score, entry))
        
        scored.sort(key=lambda x: -x[0])
        
        # Atualiza access_count
        for score, entry in scored[:top_k]:
            entry.last_accessed = time.time()
            entry.access_count += 1
        
        return [entry for _, entry in scored[:top_k]]
    
    def forget(self, threshold: float = 0.1) -> int:
        """Remove memórias com importância abaixo do threshold."""
        before = len(self.entries)
        self.entries = [e for e in self.entries if e.importance >= threshold]
        forgotten = before - len(self.entries)
        
        if forgotten > 0:
            logger.info(f"{forgotten} memórias esquecidas (importância < {threshold})")
        
        return forgotten
    
    def get_status(self) -> dict:
        """Retorna status da memória de longo prazo."""
        categories: dict[str, int] = {}
        for entry in self.entries:
            categories[entry.category] = categories.get(entry.category, 0) + 1
        
        return {
            "total_entries": len(self.entries),
            "max_entries": self.max_entries,
            "by_category": categories,
            "avg_importance": round(
                sum(e.importance for e in self.entries) / max(len(self.entries), 1), 3
            ),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# AGENTE COM MEMÓRIA COMPLETA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class AgentWithMemory:
    """
    Agente com memória completa: curto + longo prazo.
    
    Fluxo:
    1. Recebe input do usuário
    2. Busca memórias relevantes (longo prazo)
    3. Constrói contexto: system + summaries + short-term + retrieved memories
    4. Chama LLM
    5. Salva resposta e aprende com a interação
    """
    
    def __init__(self, model: str = "gpt-4o-mini", max_st_tokens: int = 4000):
        self.model = model
        self.st_memory = ShortTermMemory(max_tokens=max_st_tokens, strategy="summarization")
        self.lt_memory = LongTermMemory(max_entries=50)
        self.conversation_count = 0
        self.total_tokens = 0
    
    def _build_prompt(self, user_input: str) -> str:
        """Constrói prompt completo com contexto de memória."""
        parts = []
        
        # Instrução do sistema
        parts.append("Você é um assistente útil e memorioso.")
        
        # Memórias recuperadas
        relevant_memories = self.lt_memory.retrieve(user_input, top_k=3)
        if relevant_memories:
            memory_text = "\n".join(
                f"- {m.content[:100]}" for m in relevant_memories
            )
            parts.append(f"\nMEMÓRIAS RELEVANTES:\n{memory_text}")
        
        # Histórico recente
        context = self.st_memory.get_context(keep_last=6)
        if context:
            history = "\n".join(
                f"[{c['role']}]: {c['content'][:100]}" for c in context
            )
            parts.append(f"\nHISTÓRICO:\n{history}")
        
        # Input atual
        parts.append(f"\nUSUÁRIO: {user_input}")
        parts.append("\nASSISTENTE:")
        
        return "\n".join(parts)
    
    def chat(self, user_input: str) -> str:
        """
        Executa ciclo completo de conversa com memória.
        
        1. Adiciona input ao ST memory
        2. Busca LT memories relevantes
        3. Gera resposta
        4. Salva resposta no ST e LT memories
        """
        self.conversation_count += 1
        
        console.print(f"\n[bold cyan]💬 Conversa #{self.conversation_count}[/]")
        console.print(f"  [dim]Input:[/] {user_input[:80]}...")
        
        # Adiciona ao ST memory
        self.st_memory.add_message("user", user_input)
        
        # Busca memórias relevantes
        relevant = self.lt_memory.retrieve(user_input, top_k=2)
        if relevant:
            console.print(f"  [dim]📚 {len(relevant)} memórias recuperadas[/]")
        
        # Constrói prompt
        prompt = self._build_prompt(user_input)
        input_tokens = self.st_memory._count_tokens(prompt)
        
        # Simula resposta do LLM (em produção, chamaria API real)
        response = self._simulate_response(user_input, relevant)
        output_tokens = self.st_memory._count_tokens(response)
        
        # Adiciona resposta ao ST memory
        self.st_memory.add_message("assistant", response)
        
        # Aprende — salva no LT memory se importante
        importance = 0.3 + (len(user_input) / 1000)  # Simplificação
        self.lt_memory.store(
            content=f"Q: {user_input} → A: {response[:200]}",
            category="conversation",
            importance=min(importance, 1.0),
        )
        
        self.total_tokens += input_tokens + output_tokens
        
        console.print(f"  [green]Resposta:[/] {response[:100]}...")
        
        return response
    
    def _simulate_response(self, question: str, memories: list[MemoryEntry]) -> str:
        """Simula resposta do LLM baseada no contexto."""
        memory_hint = ""
        if memories:
            memory_hint = " Com base nas memórias recuperadas, "
        
        responses = {
            "meu nome é João": "Olá João! Anotei seu nome para futuras conversas.",
            "gosto de Python": "Ótimo! Python é uma excelente linguagem. Anotei isso.",
            "qual meu nome": f"Você me disse que seu nome é{'' 'João''' if 'João' in str(memories) else 'desconhecido'}.",
        }
        
        for key, resp in responses.items():
            if key in question.lower():
                return resp + memory_hint + " Posso ajudar com mais alguma coisa?"
        
        return f"Entendi! Sobre '{question[:50]}...', posso ajudar com isso.{memory_hint}"
    
    def get_status(self) -> dict:
        """Retorna status completo da memória."""
        return {
            "conversations": self.conversation_count,
            "total_tokens": self.total_tokens,
            "short_term": self.st_memory.get_status(),
            "long_term": self.lt_memory.get_status(),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa demonstração completa de memória."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO P7 — Memória e Contexto[/]\n\n"
        "Short-term (histórico), long-term (vector store),\n"
        "summarization automática e gestão do context window.",
        title="🧠 AI Agents Course",
        border_style="cyan",
    ))
    
    agent = AgentWithMemory(max_st_tokens=2000)
    
    # ━━ Demonstração de conversa com memória ━━
    conversations = [
        ("Meu nome é João e trabalho com Python.", "Apresentação"),
        ("Tenho 3 anos de experiência em machine learning.", "Experiência"),
        ("O que eu disse sobre minha experiência?", "Consulta de memória"),
        ("Qual meu nome?", "Consulta de identidade"),
        ("Quero aprender sobre transformers.", "Novo tópico"),
        ("O que eu sei sobre transformers?", "Consulta de memória recente"),
    ]
    
    console.print("\n[bold]🗣️  Simulando conversa com memória:[/]\n")
    
    for question, description in conversations:
        console.print(f"\n[bold cyan]{description}:[/]")
        response = agent.chat(question)
    
    # ━━ Status final ━━
    status = agent.get_status()
    
    console.print("\n[bold cyan]📊 Status da Memória:[/]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Componente", style="cyan")
    table.add_column("Métrica", style="cyan")
    table.add_column("Valor", justify="right")
    
    st = status["short_term"]
    lt = status["long_term"]
    
    table.add_row("Curto Prazo", "Estratégia", st["strategy"])
    table.add_row("", "Mensagens", str(st["message_count"]))
    table.add_row("", "Tokens usados", str(st["current_tokens"]))
    table.add_row("", "Utilização", f"{st['utilization_pct']}%")
    table.add_row("", "Resumos", str(st["summary_count"]))
    
    table.add_row("Longo Prazo", "Total de entradas", str(lt["total_entries"]))
    table.add_row("", "Importância média", f"{lt['avg_importance']:.3f}")
    
    console.print(table)
    
    console.print("\n[dim]💡 O agente lembra do que foi dito anteriormente![/]")


if __name__ == "__main__":
    main()
