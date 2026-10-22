# 🏗️ Mini-Projeto Integrador — Skills & Composition

> **Objetivo:** Construir um registry de skills com composição em pipeline.

## O que você vai construir

Um skill orchestrator `skill_system.py` que:

1. **Registra** skills com schema e handlers
2. **Compose** múltiplas skills em pipeline
3. **Executa** pipeline com error handling
4. **Descobre** skills relevantes por keyword

## Requisitos

```python
class SkillSystem:
    def register_skill(self, name: str, description: str, 
                       handler: Callable[[dict], dict]) -> None:
        """Registrar nova skill no registry."""
        ...
    
    def get_skill(self, name: str) -> Optional[dict]:
        """Retornar skill pelo nome."""
        ...
    
    def compose_pipeline(self, skill_names: list) -> Pipeline:
        """Compor múltiplas skills em sequência."""
        ...
    
    def execute_pipeline(self, pipeline: Pipeline, input_data: dict) -> dict:
        """Executar pipeline com error handling."""
        ...
    
    def discover_skills(self, task_description: str, top_k: int = 3) -> list:
        """Descobrir skills relevantes pela descrição."""
        ...
    
    def version_skill(self, name: str, version: str, 
                      handler: Callable) -> None:
        """Versionar skill (v1, v2, etc.)."""
        ...
```

## Teste seu código

```bash
python skill_system.py --register skills.json --list
python skill_system.py --pipeline summarize+translate --input text.txt
python skill_system.py --discover "analyze sentiment" --top-k 3
```

## Desafios extras

- [ ] Marketplace de skills compartilháveis
- [ ] Skill testing framework automatizado
- [ ] Dependency resolution entre skills
- [ ] GraphQL API para query de skills
