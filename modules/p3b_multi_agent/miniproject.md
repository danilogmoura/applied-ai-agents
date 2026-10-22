# 🏗️ Mini-Projeto Integrador — Multi-Agent Systems

> **Objetivo:** Construir um sistema multi-agent com supervisor e especialistas.

## O que você vai construir

Um orquestrador `multi_agent_system.py` que:

1. **Roteia** requests para especialistas via supervisor
2. **Fallback** quando especialista falha
3. **Compartilha** contexto entre agentes
4. **Calcula** custo total da coordenação multi-agent

## Requisitos

```python
class MultiAgentSystem:
    def route_to_specialist(self, request: str, specialists: list) -> dict:
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
