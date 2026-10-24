"""
Módulo 07 — Planejamento e Retomada

Sistema resiliente com circuit breakers e checkpoints de estado.
Se uma API externa cair, o agente recalcula rotas automaticamente.

Problema: O agente depende de APIs externas que podem falhar.
Como garantir resiliência e capacidade de retomar de onde parou?
"""

from __future__ import annotations

import logging
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from shared.logging_config import setup_logging
from shared.cost import count_tokens, estimate_cost, format_cost

console = Console()
logger = setup_logging("07-planejamento")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CIRCUIT BREAKER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class CircuitState(Enum):
    CLOSED = "closed"       # Funcionando normalmente
    OPEN = "open"           # Falhas excessivas — desativado
    HALF_OPEN = "half_open"  # Testando recuperação


@dataclass
class CircuitBreaker:
    """
    Circuit Breaker pattern para proteção contra falhas de APIs externas.
    
    Se muitas falhas consecutivas ocorrerem, o circuit abre e bloqueia
    chamadas por um período, permitindo retry gradual.
    """
    
    name: str
    failure_threshold: int = 3        # Falhas antes de abrir
    recovery_timeout: float = 30.0    # Segundos antes de tentar novamente
    half_open_max_calls: int = 1      # Chamadas permitidas em half-open
    
    _failure_count: int = 0
    _success_count: int = 0
    _state: CircuitState = CircuitState.CLOSED
    _last_failure_time: float = 0.0
    _half_open_calls: int = 0
    
    @property
    def state(self) -> CircuitState:
        """Transição automática: open → half_open após timeout."""
        if self._state == CircuitState.OPEN:
            elapsed = time.time() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_calls = 0
                logger.info(f"Circuit '{self.name}' transitioning to HALF_OPEN")
        return self._state
    
    def can_execute(self) -> bool:
        """Verifica se pode executar chamada."""
        current_state = self.state
        
        if current_state == CircuitState.CLOSED:
            return True
        elif current_state == CircuitState.HALF_OPEN:
            return self._half_open_calls < self.half_open_max_calls
        else:  # OPEN
            return False
    
    def record_success(self) -> None:
        """Registra sucesso — fecha ou avança no half-open."""
        if self._state == CircuitState.HALF_OPEN:
            self._success_count += 1
            self._half_open_calls += 1
            
            if self._success_count >= 1:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._success_count = 0
                logger.info(f"Circuit '{self.name}' CLOSED (recovered)")
        else:
            self._failure_count = max(0, self._failure_count - 1)
    
    def record_failure(self) -> None:
        """Registra falha — abre o circuit se threshold atingido."""
        self._failure_count += 1
        self._last_failure_time = time.time()
        
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            logger.warning(f"Circuit '{self.name}' re-OPENED after half-open failure")
        elif self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.error(f"Circuit '{self.name}' OPENED ({self._failure_count} failures)")
    
    def get_status(self) -> dict:
        """Retorna status atual do circuit breaker."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failures": self._failure_count,
            "successes": self._success_count,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CHECKPOINT / STATE MANAGEMENT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class ConversationCheckpoint:
    """Snapshot do estado da conversa para retomada."""
    
    timestamp: float = field(default_factory=time.time)
    messages: list[dict] = field(default_factory=list)
    tools_used: list[str] = field(default_factory=list)
    circuits_status: dict[str, dict] = field(default_factory=dict)
    tokens_consumed: int = 0
    cost_accumulated: float = 0.0
    step_index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    
    def save_to_file(self, path: str) -> None:
        """Salva checkpoint em JSON."""
        import json
        data = {
            "timestamp": self.timestamp,
            "messages": self.messages,
            "tools_used": self.tools_used,
            "circuits_status": self.circuits_status,
            "tokens_consumed": self.tokens_consumed,
            "cost_accumulated": self.cost_accumulated,
            "step_index": self.step_index,
            "metadata": self.metadata,
        }
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2))
        logger.info(f"Checkpoint saved to {path}")
    
    @staticmethod
    def load_from_file(path: str) -> Optional["ConversationCheckpoint"]:
        """Carrega checkpoint de arquivo JSON."""
        import json
        
        try:
            data = json.loads(Path(path).read_text())
            cp = ConversationCheckpoint(**data)
            logger.info(f"Checkpoint loaded from {path}")
            return cp
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            return None


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PLANNER RESILIENTE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ResilientPlanner:
    """
    Planejador de tarefas com circuit breakers e checkpoints.
    
    Fluxo:
    1. Divide tarefa em passos
    2. Executa cada passo com circuit breaker
    3. Salva checkpoint a cada passo
    4. Se falhar, recupera último checkpoint e tenta rota alternativa
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.circuits: dict[str, CircuitBreaker] = {}
        self.checkpoint_path = str(Path(__file__).parent / "checkpoint.json")
        self.current_checkpoint: Optional[ConversationCheckpoint] = None
        self.steps_completed = 0
        self.total_cost = 0.0
        self.total_tokens = 0
    
    def register_circuit(self, name: str, **kwargs) -> CircuitBreaker:
        """Registra um circuit breaker para uma API/ferramenta."""
        circuit = CircuitBreaker(name=name, **kwargs)
        self.circuits[name] = circuit
        logger.info(f"Circuit breaker registered: {name}")
        return circuit
    
    def _call_with_circuit(self, circuit_name: str, func: callable, *args, **kwargs) -> Any:
        """
        Executa função protegida por circuit breaker.
        
        Se o circuit estiver aberto, executa fallback.
        """
        circuit = self.circuits.get(circuit_name)
        
        if not circuit or circuit.can_execute():
            try:
                result = func(*args, **kwargs)
                if circuit:
                    circuit.record_success()
                return result
            except Exception as e:
                if circuit:
                    circuit.record_failure()
                raise
        else:
            status = circuit.get_status() if circuit else {}
            logger.warning(f"Circuit '{circuit_name}' is {status.get('state', 'unknown')} — using fallback")
            return self._fallback(circuit_name, *args, **kwargs)
    
    def _fallback(self, circuit_name: str, *args, **kwargs) -> str:
        """Fallback quando circuit está aberto."""
        return f"[FALLBACK] Serviço '{circuit_name}' indisponível (circuit aberto). Usando resposta cacheada."
    
    def create_checkpoint(self) -> ConversationCheckpoint:
        """Cria snapshot do estado atual."""
        circuits_status = {name: cb.get_status() for name, cb in self.circuits.items()}
        
        self.current_checkpoint = ConversationCheckpoint(
            circuits_status=circuits_status,
            tokens_consumed=self.total_tokens,
            cost_accumulated=self.total_cost,
            step_index=self.steps_completed,
        )
        
        self.current_checkpoint.save_to_file(self.checkpoint_path)
        return self.current_checkpoint
    
    def restore_checkpoint(self) -> Optional[ConversationCheckpoint]:
        """Restaura último checkpoint salvo."""
        restored = ConversationCheckpoint.load_from_file(self.checkpoint_path)
        
        if restored:
            self.current_checkpoint = restored
            self.total_tokens = restored.tokens_consumed
            self.total_cost = restored.cost_accumulated
            self.steps_completed = restored.step_index
            
            # Restaura status dos circuits
            for name, status in restored.circuits_status.items():
                if name in self.circuits:
                    logger.info(f"Restored circuit '{name}' status from checkpoint")
            
            console.print(f"\n[yellow]⚠️ Checkpoint restaurado (passo {restored.step_index})[/]")
        
        return restored
    
    def execute_task(self, task_description: str, steps: list[dict]) -> dict:
        """
        Executa tarefa dividida em passos com resiliência.
        
        Args:
            task_description: Descrição geral da tarefa.
            steps: Lista de passos {"name": str, "action": callable, "circuit": str}.
        
        Returns:
            Resultado completo da execução.
        """
        console.print(Panel.fit(
            f"[bold]{task_description}[/]\n\n"
            f"{len(steps)} passos planejados",
            title="📋 Planejador Resiliente",
            border_style="cyan",
        ))
        
        results = []
        
        for i, step in enumerate(steps):
            step_name = step["name"]
            action = step["action"]
            circuit_name = step.get("circuit")
            
            console.print(f"\n[bold cyan]▸ Passo {i+1}/{len(steps)}: {step_name}[/]")
            
            if circuit_name:
                try:
                    result = self._call_with_circuit(circuit_name, action)
                except Exception as e:
                    console.print(f"[red]✗ Falha no passo {step_name}: {e}[/]")
                    result = f"ERRO: {e}"
            else:
                try:
                    result = action()
                except Exception as e:
                    console.print(f"[red]✗ Falha no passo {step_name}: {e}[/]")
                    result = f"ERRO: {e}"
            
            results.append({"step": step_name, "result": result})
            
            # Salva checkpoint a cada 2 passos
            if (i + 1) % 2 == 0:
                self.create_checkpoint()
            
            self.steps_completed = i + 1
        
        # Relatório final
        console.print("\n" + "=" * 60)
        console.print("[bold green]✅ Tarefa concluída![/]")
        console.print(f"Passos executados: {self.steps_completed}/{len(steps)}")
        console.print(f"Custo total: {format_cost(self.total_cost)}")
        console.print(f"Tokens consumidos: {self.total_tokens}")
        console.print("=" * 60)
        
        return {
            "task": task_description,
            "steps_executed": self.steps_completed,
            "total_steps": len(steps),
            "results": results,
            "cost": self.total_cost,
            "tokens": self.total_tokens,
            "circuits": {name: cb.get_status() for name, cb in self.circuits.items()},
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SIMULAÇÃO DE SERVIÇOS COM FALHA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SimulatedService:
    """Simula serviço externo que pode falhar intermitentemente."""
    
    def __init__(self, name: str, fail_rate: float = 0.3):
        self.name = name
        self.fail_rate = fail_rate
        self.call_count = 0
        self.failure_count = 0
    
    def call(self) -> str:
        """Chamada ao serviço — pode falhar."""
        self.call_count += 1
        import random
        
        if random.random() < self.fail_rate:
            self.failure_count += 1
            raise ConnectionError(f"Serviço '{self.name}' caiu (falha {self.failure_count}/{self.call_count})")
        
        return f"[{self.name}] Resposta OK (chamada {self.call_count})"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa demonstração de planejamento resiliente."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO 07 — Planejamento e Retomada[/]\n\n"
        "Circuit breakers + checkpoints de estado.\n"
        "Resiliência contra falhas de APIs externas.",
        title="🔄 AI Agents Course",
        border_style="cyan",
    ))
    
    planner = ResilientPlanner()
    
    # Registra circuit breakers
    planner.register_circuit("weather_api", failure_threshold=2, recovery_timeout=5.0)
    planner.register_circuit("news_api", failure_threshold=2, recovery_timeout=5.0)
    planner.register_circuit("calc_service", failure_threshold=3, recovery_timeout=3.0)
    
    # Simula serviços instáveis
    weather = SimulatedService("WeatherAPI", fail_rate=0.4)
    news = SimulatedService("NewsAPI", fail_rate=0.5)
    calc = SimulatedService("CalcService", fail_rate=0.2)
    
    # Define passos da tarefa
    steps = [
        {
            "name": "Buscar clima atual",
            "action": lambda: weather.call(),
            "circuit": "weather_api",
        },
        {
            "name": "Buscar notícias do dia",
            "action": lambda: news.call(),
            "circuit": "news_api",
        },
        {
            "name": "Calcular estatísticas",
            "action": lambda: f"Total de chamadas: {weather.call_count + news.call_count}",
            "circuit": "calc_service",
        },
        {
            "name": "Gerar relatório final",
            "action": lambda: "Relatório gerado com sucesso!",
            "circuit": None,  # Sem dependência externa
        },
    ]
    
    # Executa tarefa
    result = planner.execute_task(
        "Agendar briefing matinal com clima, notícias e métricas",
        steps,
    )
    
    # Exibe status dos circuit breakers
    table = Table(title="Status dos Circuit Breakers")
    table.add_column("Nome")
    table.add_column("Estado")
    table.add_column("Falhas")
    table.add_column("Sucessos")
    
    for name, status in result["circuits"].items():
        table.add_row(
            name,
            status["state"].upper(),
            str(status["failures"]),
            str(status["successes"]),
        )
    
    console.print(table)
    
    # Demonstra recuperação de checkpoint
    console.print("\n[dim]💡 Demonstrando recuperação de checkpoint...[/]")
    
    restored = planner.restore_checkpoint()
    if restored:
        console.print(f"[green]✓ Checkpoint restaurado no passo {restored.step_index}[/]")
    
    console.print("\n[dim]💡 Próximo passo: Módulo 08 — Sistema Multiagente[/]")


if __name__ == "__main__":
    main()
