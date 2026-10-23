# 🏗️ Mini-Projeto Integrador — Planning

> **Objetivo:** Construir um planner com circuit breaker e checkpoint.

## O que você vai construir

Um executor `planner.py` (classe `ResilientPlanner`) que:

1. **Executa** plano multi-step com circuit breaker
2. **Salva/restaura** checkpoints a cada step
3. **Valida** pré/pós-condições de cada step
4. **Aplica** fallback quando step falha

## Requisitos

> ℹ️ **Arquitetura de referência:** No `run.py`, o planner é composto por duas classes: `CircuitBreaker` (gerencia os estados open/closed/half-open) e `ResilientPlanner` (orquestra steps, checkpoints e fallback). Aqui você pode começar com uma classe única `ResilientPlanner`; quando quiser, extraia o circuit breaker para a sua própria classe `CircuitBreaker`, como na referência.

```python
class ResilientPlanner:
    def execute_with_circuit_breaker(self, plan: list) -> dict:
        """Executar plano com circuit breaker (open/closed/half-open)."""
        ...
    
    def save_checkpoint(self, step_index: int, state: dict) -> str:
        """Salvar checkpoint para restauração posterior."""
        ...
    
    def restore_checkpoint(self, checkpoint_id: str) -> dict:
        """Restaurar estado de um checkpoint."""
        ...
    
    def validate_step(self, step: dict, context: dict) -> bool:
        """Validar pré/pós-condições do step."""
        ...
    
    def execute_with_fallback(self, plan: list, fallback_plan: list) -> dict:
        """Executar plano principal, usar fallback se falhar."""
        ...
```

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com estados do Circuit Breaker

Defina os 3 estados do circuit breaker: CLOSED (normal), OPEN (bloqueado), HALF_OPEN (teste):

```python
import json
import time
import random
from datetime import datetime
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Chamadas fluem normalmente
    OPEN = "open"          # Todas chamadas bloqueadas
    HALF_OPEN = "half_open" # 1 chamada de teste

class ResilientPlanner:
    def __init__(self, checkpoint_dir: str = "./checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        self.circuits = {}  # step_name → CircuitState
        self.checkpoints = {}  # checkpoint_id → state dict
        self.results = []
```

### Passo 2 — Implemente o Circuit Breaker

Se muitas falhas consecutivas, abre o circuito. Após timeout, tenta uma chamada de teste:

```python
def _get_circuit_state(self, step_name: str) -> CircuitState:
    """Retorna estado atual do circuit breaker para um step."""
    if step_name not in self.circuits:
        self.circuits[step_name] = {
            "state": CircuitState.CLOSED,
            "failures": 0,
            "last_failure_time": None,
            "consecutive_failures": 0,
        }
    return self.circuits[step_name]["state"]

def execute_with_circuit_breaker(self, plan: list) -> dict:
    """Executa plano com circuit breaker por step."""
    THRESHOLD = 3  # Falhas consecutivas para abrir
    RECOVERY_TIMEOUT = 5  # Segundos para tentar half-open
    
    for step_index, step in enumerate(plan):
        step_name = step.get("name", f"step_{step_index}")
        circuit = self.circuits.get(step_name, {
            "state": CircuitState.CLOSED,
            "failures": 0,
            "last_failure_time": None,
            "consecutive_failures": 0,
        })
        
        state = circuit["state"]
        
        # Verifica se pode transicionar de OPEN → HALF_OPEN
        if state == CircuitState.OPEN:
            if circuit["last_failure_time"]:
                elapsed = time.time() - circuit["last_failure_time"]
                if elapsed > RECOVERY_TIMEOUT:
                    circuit["state"] = CircuitState.HALF_OPEN
                    state = CircuitState.HALF_OPEN
                    print(f"  🔌 {step_name}: TRANSICIONANDO para HALF_OPEN")
                else:
                    wait = RECOVERY_TIMEOUT - elapsed
                    print(f"  ⛔ {step_name}: CIRCUIT BREAKER ABERTO (aguardando {wait:.1f}s)")
                    # Usa fallback
                    result = self._execute_step_fallback(step)
                    self.results.append({"step": step_name, "status": "fallback"})
                    continue
        
        # Se HALF_OPEN e falhar, volta para OPEN
        if state == CircuitState.HALF_OPEN:
            try:
                result = self._execute_step(step)
                circuit["state"] = CircuitState.CLOSED
                circuit["consecutive_failures"] = 0
                print(f"  ✅ {step_name}: HALF_OPEN → CLOSED (sucesso)")
            except Exception as e:
                circuit["state"] = CircuitState.OPEN
                circuit["last_failure_time"] = time.time()
                print(f"  ❌ {step_name}: HALF_OPEN → OPEN (falhou no teste)")
                self.results.append({"step": step_name, "status": "circuit_open", "error": str(e)})
                continue
        
        # CLOSED: executa normalmente
        try:
            result = self._execute_step(step)
            circuit["consecutive_failures"] = 0
            print(f"  ✅ {step_name}: executado com sucesso")
            self.results.append({"step": step_name, "status": "success", "result": result})
            
            # Salva checkpoint a cada 2 steps
            if step_index % 2 == 0:
                self.save_checkpoint(step_index, {"results": self.results})
                
        except Exception as e:
            circuit["consecutive_failures"] += 1
            circuit["failures"] += 1
            circuit["last_failure_time"] = time.time()
            print(f"  ❌ {step_name}: FALHOU ({circuit['consecutive_failures']}/{THRESHOLD} falhas)")
            
            if circuit["consecutive_failures"] >= THRESHOLD:
                circuit["state"] = CircuitState.OPEN
                print(f"  🔌 {step_name}: CIRCUIT BREAKER ABERTO!")
            
            # Tenta fallback
            fallback_result = self._execute_step_fallback(step)
            self.results.append({"step": step_name, "status": "fallback", "result": fallback_result})
    
    return {
        "total_steps": len(plan),
        "completed": sum(1 for r in self.results if r["status"] == "success"),
        "fallbacks": sum(1 for r in self.results if r["status"] == "fallback"),
        "results": self.results,
    }

def _execute_step(self, step: dict) -> dict:
    """Simula execução de um step (pode falhar aleatoriamente)."""
    if random.random() < 0.3:  # 30% de chance de falha
        raise Exception(f"Falha simulada em {step.get('name', 'unknown')}")
    return {"output": f"Resultado de {step.get('name', 'step')}"}

def _execute_step_fallback(self, step: dict) -> dict:
    """Fallback: retorna resultado genérico quando step falha."""
    return {"output": f"[FALLBACK] Resultado padrão para {step.get('name', 'step')}", "source": "fallback"}
```

### Passo 3 — Implemente Checkpoints

Salva/restaura estado para recuperação após crash:

```python
import os
import uuid

def save_checkpoint(self, step_index: int, state: dict) -> str:
    """Salva checkpoint em disco."""
    checkpoint_id = f"ckpt_{uuid.uuid4().hex[:8]}"
    checkpoint_data = {
        "id": checkpoint_id,
        "timestamp": datetime.now().isoformat(),
        "step_index": step_index,
        "state": state,
    }
    
    # Garante que diretório existe
    os.makedirs(self.checkpoint_dir, exist_ok=True)
    
    filepath = os.path.join(self.checkpoint_dir, f"{checkpoint_id}.json")
    with open(filepath, "w") as f:
        json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
    
    self.checkpoints[checkpoint_id] = checkpoint_data
    print(f"  💾 Checkpoint salvo: {checkpoint_id} (step {step_index})")
    return checkpoint_id

def restore_checkpoint(self, checkpoint_id: str) -> dict:
    """Restaura estado de um checkpoint."""
    if checkpoint_id in self.checkpoints:
        ckpt = self.checkpoints[checkpoint_id]
        self.results = ckpt["state"].get("results", [])
        print(f"  🔄 Checkpoint restaurado: {checkpoint_id} ({len(self.results)} resultados)")
        return ckpt
    
    # Tenta carregar do disco
    filepath = os.path.join(self.checkpoint_dir, f"{checkpoint_id}.json")
    if os.path.exists(filepath):
        with open(filepath) as f:
            ckpt = json.load(f)
        self.checkpoints[checkpoint_id] = ckpt
        self.results = ckpt["state"].get("results", [])
        return ckpt
    
    raise ValueError(f"Checkpoint {checkpoint_id} não encontrado")
```

### Passo 4 — Valide pré/pós-condições

```python
def validate_step(self, step: dict, context: dict) -> bool:
    """Valida se condições para executar o step são satisfeitas."""
    required_keys = step.get("required_context", [])
    for key in required_keys:
        if key not in context:
            print(f"  ⚠️ Pré-condição falhou: contexto '{key}' ausente")
            return False
    return True
```

### Passo 5 — Implemente Fallback Plan

```python
def execute_with_fallback(self, plan: list, fallback_plan: list) -> dict:
    """Tenta plano principal, usa fallback se tudo falhar."""
    try:
        result = self.execute_with_circuit_breaker(plan)
        if result["completed"] == len(plan):
            return {"strategy": "main_plan", "result": result}
    except Exception as e:
        print(f"  ⚠️ Plano principal falhou: {e}")
    
    print("  🔄 Executando plano de fallback...")
    self.results = []
    fallback_result = self.execute_with_circuit_breaker(fallback_plan)
    return {"strategy": "fallback_plan", "result": fallback_result}
```

### Passo 6 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    SAMPLE_PLAN = [
        {"name": "build", "required_context": []},
        {"name": "test", "required_context": ["build"]},
        {"name": "lint", "required_context": []},
        {"name": "deploy_staging", "required_context": ["test", "lint"]},
        {"name": "deploy_production", "required_context": ["deploy_staging"]},
    ]
    
    FALLBACK_PLAN = [
        {"name": "build"},
        {"name": "test"},
        {"name": "notify_team", "description": "Avisa equipe sobre falha"},
    ]
    
    parser = argparse.ArgumentParser(description="Planner com circuit breaker")
    parser.add_argument("--plan", default="ci_cd")
    parser.add_argument("--checkpoint-dir", default="./checkpoints")
    args = parser.parse_args()
    
    planner = Planner(checkpoint_dir=args.checkpoint_dir)
    
    if args.plan == "ci_cd":
        plan = SAMPLE_PLAN
    else:
        plan = SAMPLE_PLAN  # Em produção, carregaria de JSON
    
    result = planner.execute_with_circuit_breaker(plan)
    
    print("\n=== Resumo ===")
    print(f"Total de steps: {result['total_steps']}")
    print(f"Completados: {result['completed']}")
    print(f"Fallbacks: {result['fallbacks']}")
```

## Teste seu código

```bash
python planner.py --plan deployment.json
python planner.py --plan ci_cd.json --checkpoint-dir ./checkpoints
```

## Desafios extras

- [ ] Visualização do plano como DAG
- [ ] Parallel execution de steps independentes
- [ ] Metrics dashboard (tempo por step, taxa de sucesso)
- [ ] Exportar plano como workflow YAML

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `Planner` implementa circuit breaker com 3 estados (closed/open/half-open)
- [ ] `save_checkpoint()` salva estado em disco e retorna ID único
- [ ] `restore_checkpoint()` recupera estado salvo anteriormente
- [ ] `execute_with_circuit_breaker()` transiciona estados corretamente
- [ ] Fallback é acionado quando step falha
- [ ] CLI aceita plano via argumento

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.
