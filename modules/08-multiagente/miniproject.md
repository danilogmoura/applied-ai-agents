# 🏗️ Mini-Projeto Integrador — Multi-Agent Systems

> **Objetivo:** Construir um sistema multi-agent com supervisor e especialistas.

## O que você vai construir

Um orquestrador `multi_agent_system.py` (classes `Agent` + `SupervisorAgent`) que:

1. **Roteia** requests para especialistas via supervisor
2. **Fallback** quando especialista falha
3. **Compartilha** contexto entre agentes
4. **Calcula** custo total da coordenação multi-agent

## Requisitos

```python
class Agent:
    def __init__(self, name: str, role: str, model: str = "gpt-4o-mini"):
        """Agente especialista com identidade e domínio próprios."""
        ...

    def execute(self, task: str) -> str:
        """Executa tarefa dentro do domínio do especialista (pode falhar)."""
        ...

    def get_status(self) -> dict:
        """Retorna status: nome, papel, chamadas, tokens e custo."""
        ...


class SupervisorAgent:
    def add_specialist(self, agent: Agent) -> None:
        """Registra um especialista no time."""
        ...

    def route_to_specialist(self, request: str) -> dict:
        """Supervisor roteia request para melhor especialista."""
        ...
    
    def handle_specialist_failure(self, specialist_name: str, 
                                  request: str) -> dict:
        """Fallback: tentar outro especialista ou responder genericamente."""
        ...
    
    def share_context(self, agent_outputs: list) -> dict:
        """Compartilhar contexto entre agentes (sincronização)."""
        ...
    
    def calculate_multi_agent_cost(self, agent_costs: list) -> dict:
        """Calcular custo total + overhead de coordenação."""
        ...
    
    def execute_hierarchical(self, task: str, hierarchy: dict) -> dict:
        """Executar tarefa em estrutura hierárquica (manager → workers)."""
        ...
```

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe `Agent` com especialistas pré-definidos

Defina uma classe `Agent` (especialista) e registre instâncias dela no `SupervisorAgent`. Cada agente tem um domínio específico:

```python
import random
from datetime import datetime

class SupervisorAgent:
    def __init__(self):
        # Especialistas disponíveis
        self.specialists = {
            "researcher": {
                "name": "researcher",
                "domain": ["pesquisar", "buscar", "informação", "dados"],
                "response_template": "[Pesquisador] Encontrei as seguintes informações sobre '{query}':...",
                "cost_per_call": 0.005,
            },
            "analyst": {
                "name": "analyst",
                "domain": ["analisar", "sentimento", "classificar", "tendência"],
                "response_template": "[Analista] Após análise: {result}. Confiança: {confidence}%",
                "cost_per_call": 0.008,
            },
            "writer": {
                "name": "writer",
                "domain": ["escrever", "resumo", "gerar texto", "formatar"],
                "response_template": "[Escritor] Aqui está o texto formatado:\n\n{content}",
                "cost_per_call": 0.003,
            },
            "coder": {
                "name": "coder",
                "domain": ["código", "programa", "script", "implementar"],
                "response_template": "[Coder] ```python\n{code}\n```\nExplicação: {explanation}",
                "cost_per_call": 0.010,
            },
        }
        
        self.context_shared = {}  # Contexto compartilhado entre agentes
        self.cost_log = []
```

### Passo 2 — Roteie requests para especialistas

O supervisor analisa o request e escolhe o especialista mais adequado:

```python
def route_to_specialist(self, request: str, specialists: list = None) -> dict:
    """Supervisor roteia request para melhor especialista."""
    if specialists is None:
        specialists = list(self.specialists.keys())
    
    request_lower = request.lower()
    
    scores = {}
    for spec_name in specialists:
        spec = self.specialists[spec_name]
        # Conta quantas keywords do domínio aparecem no request
        matches = sum(1 for word in spec["domain"] if word in request_lower)
        scores[spec_name] = matches
    
    # Escolhe especialista com maior score
    if not scores or max(scores.values()) == 0:
        return {"specialist": "researcher", "confidence": 0.0, "reason": "Nenhuma keyword correspondente, fallback para pesquisador"}
    
    best_spec = max(scores, key=scores.get)
    confidence = scores[best_spec] / max(sum(scores.values()), 1)
    
    return {
        "specialist": best_spec,
        "confidence": round(confidence, 2),
        "scores": scores,
        "reason": f"Keyword matching: {scores[best_spec]} correspondências",
    }
```

### Passo 3 — Implemente fallback quando especialista falha

```python
def handle_specialist_failure(self, specialist_name: str, 
                              request: str) -> dict:
    """Fallback: tenta outro especialista ou responde genericamente."""
    available = [s for s in self.specialists if s != specialist_name]
    
    if not available:
        return {
            "status": "failed",
            "response": "Todos os especialistas indisponíveis. Respondendo genericamente.",
            "source": "generic_fallback",
        }
    
    # Tenta o próximo especialista disponível
    next_spec = available[0]
    print(f"  ⚠️ {specialist_name} falhou, tentando {next_spec}...")
    
    # Simula resposta do fallback
    response = f"[Fallback-{next_spec}] Não pude processar com {specialist_name}, mas aqui vai uma resposta genérica para: '{request}'"
    
    return {
        "status": "fallback",
        "original_specialist": specialist_name,
        "fallback_specialist": next_spec,
        "response": response,
    }
```

### Passo 4 — Compartilhe contexto entre agentes

```python
def share_context(self, agent_outputs: list) -> dict:
    """Compartilha contexto entre agentes (sincronização)."""
    shared = {}
    
    for output in agent_outputs:
        agent = output.get("agent", "unknown")
        content = output.get("response", "")
        
        # Extrai insights-chave do output
        if "Confiança:" in content:
            try:
                conf = float(content.split("Confiança:")[1].split("%")[0])
                shared[f"{agent}_confidence"] = conf
            except (IndexError, ValueError):
                pass
        
        if "Encontrei" in content:
            shared[f"{agent}_found_info"] = True
    
    self.context_shared.update(shared)
    return shared
```

### Passo 5 — Calcule custo total

```python
def calculate_multi_agent_cost(self, agent_costs: list) -> dict:
    """Calcula custo total + overhead de coordenação."""
    total = sum(agent_costs)
    overhead = total * 0.1  # 10% overhead por coordenação
    grand_total = total + overhead
    
    return {
        "agent_costs_sum": round(total, 4),
        "coordination_overhead": round(overhead, 4),
        "grand_total": round(grand_total, 4),
        "num_agents": len(agent_costs),
        "avg_cost_per_agent": round(grand_total / len(agent_costs), 4) if agent_costs else 0,
    }
```

### Passo 6 — Execute pipeline hierárquico

```python
def execute_hierarchical(self, task: str, hierarchy: dict) -> dict:
    """Executa tarefa em estrutura hierárquica (manager → workers)."""
    manager = hierarchy.get("manager", "researcher")
    workers = hierarchy.get("workers", [])
    
    results = []
    total_cost = 0
    
    # Manager faz roteamento inicial
    routing = self.route_to_specialist(task, workers)
    chosen = routing["specialist"]
    
    # Executa com especialista escolhido
    spec = self.specialists[chosen]
    response = spec["response_template"].format(query=task, result="análise completa", confidence=85, content="texto formatado", code="# código simulado", explanation="explicação básica")
    
    results.append({"agent": chosen, "response": response})
    total_cost += spec["cost_per_call"]
    
    # Calcula custo
    cost_info = self.calculate_multi_agent_cost([total_cost])
    
    return {
        "task": task,
        "manager": manager,
        "chosen_specialist": chosen,
        "routing_confidence": routing["confidence"],
        "results": results,
        "cost": cost_info,
    }
```

### Passo 7 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema multi-agentes")
    parser.add_argument("--task", default="analisar sentimento dos reviews")
    parser.add_argument("--hierarchy", action="store_true")
    args = parser.parse_args()
    
    system = SupervisorAgent()
    
    if args.hierarchy:
        hierarchy = {
            "manager": "researcher",
            "workers": ["analyst", "writer", "coder"],
        }
        result = system.execute_hierarchical(args.task, hierarchy)
    else:
        routing = system.route_to_specialist(args.task)
        print(f"Especialista escolhido: {routing['specialist']}")
        print(f"Confiança: {routing['confidence']}")
        print(f"Motivo: {routing['reason']}")
        result = {"routing": routing}
    
    print("\n=== Resultado ===")
    print(result)
```

## Teste seu código

```bash
python multi_agent_system.py --task "analisar sentimento dos reviews" --agents research.json
python multi_agent_system.py --hierarchy org_chart.json --batch tasks.json
```

## Desafios extras

- [ ] Agent discovery automático
- [ ] Communication protocol entre agents
- [ ] Load balancing entre workers
- [ ] Simulation dashboard com visualização de interações

## 🪨 Travei? Pistas em camadas

Funciona igualzinho às pistas dos exercícios: quando um requisito travar, abra **só o próximo nível** que você precisar — nunca todos de uma vez. O objetivo é destravar o raciocínio, não entregar a resposta mastigada.

> **Nível 1 — Direção.** Cada requisito mapeia para um `Passo` do guia acima. Antes de descer de nível, releia o Passo correspondente; na maioria das vezes ele já tem o esqueleto da função.

<details>
<summary><b>Nível 2 — A ideia por requisito</b> (clique para abrir)</summary>

- **`Agent.execute()` / `get_status()`:** cada especialista tem `name`/`role`/`model` e acumula suas chamadas/tokens/custo; `get_status()` devolve esse placar. Pode falhar de propósito para exercitar o fallback.
- **`route_to_specialist()`:** compare a request com o domínio de cada especialista (keywords/descrição) e escolha o melhor. Retorne `{specialist, reason, confidence}` — não execute ainda, só decida.
- **`handle_specialist_failure()`:** se um especialista falha, tente outro candidato do routing ou responda genericamente. É o plano B depois de `route_to_specialist()` dar errado.
- **`share_context()`:** merge as saídas dos agentes em `self.context_shared` (dict acumulado), para que um veja o trabalho do anterior. Sem isso, os especialistas ficam isolados.
- **`calculate_multi_agent_cost()`:** some os custos individuais e acrescente um overhead de coordenação (número de handoffs). Separe `agents_total` de `coordination_overhead` no dict.
- **`execute_hierarchical()`:** gerencie manager → workers: o manager decompõe a tarefa, delega a cada worker via `execute()`, e agrega. Reuse routing + share_context dentro do loop.

</details>

<details>
<summary><b>Nível 3 — Quase solução</b> (abra só se o nível 2 não bastou)</summary>

```python
def route_to_specialist(self, request, specialists=None):
    specialists = specialists or list(self.specialists)
    req = request.lower()
    best, hits = None, 0
    for name, sp in self.specialists.items():
        n = sum(k in req for k in sp["keywords"])   # aderencia do dominio
        if n > hits:
            best, hits = name, n
    return {"specialist": best, "confidence": hits / max(1, len(req.split()))}
```

`execute_hierarchical()` reaproveita essa mesma rotação: para cada subtarefa, chame `route_to_specialist()`, execute o escolhido e passe o resultado por `share_context()` antes da próxima etapa.

</details>

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `SupervisorAgent` tem registry de pelo menos 4 especialistas (`Agent`)
- [ ] `route_to_specialist()` escolhe especialista baseado em keyword matching
- [ ] `handle_specialist_failure()` faz fallback para outro especialista
- [ ] `share_context()` extrai e compartilha insights entre agentes
- [ ] `calculate_multi_agent_cost()` soma custos + overhead de coordenação
- [ ] `execute_hierarchical()` orquestra manager → workers

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.
