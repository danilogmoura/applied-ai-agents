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

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com registry de skills

Implemente um dicionário para registrar e recuperar skills:

```python
from typing import Callable, Dict, List, Optional, Any
from datetime import datetime
import json

class SkillSystem:
    def __init__(self):
        self.skills = {}          # name -> {description, handlers, versions}
        self.pipeline_log = []
    
    def register_skill(self, name: str, description: str, 
                       handler: Callable[[dict], dict],
                       category: str = "general") -> None:
        """Registrar nova skill no registry."""
        if name not in self.skills:
            self.skills[name] = {
                "name": name,
                "description": description,
                "category": category,
                "handlers": {},
                "created_at": datetime.now().isoformat(),
                "versions": [],
            }
        
        # Registra handler na versão atual (v1)
        version = "1.0.0"
        self.skills[name]["handlers"][version] = handler
        self.skills[name]["versions"].append(version)
    
    def get_skill(self, name: str) -> Optional[Dict]:
        """Retornar skill pelo nome."""
        if name in self.skills:
            skill = self.skills[name].copy()
            # Remove o handler do dict (não serializável)
            skill["handler_count"] = len(skill["handlers"])
            del skill["handlers"]
            return skill
        return None
    
    def list_skills(self, category: str = None) -> List[Dict]:
        """Lista todas as skills (ou filtra por categoria)."""
        result = []
        for name, skill in self.skills.items():
            if category and skill.get("category") != category:
                continue
            result.append({
                "name": skill["name"],
                "description": skill["description"],
                "category": skill["category"],
                "versions": skill["versions"],
            })
        return result
```

### Passo 2 — Implemente versionamento de skills

```python
    def version_skill(self, name: str, version: str,
                      handler: Callable) -> None:
        """Versionar skill (v1, v2, etc.)."""
        if name not in self.skills:
            raise ValueError(f"Skill '{name}' não existe")
        
        # Valida formato de versão (semântico: MAJOR.MINOR.PATCH)
        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError("Versão deve ser MAJOR.MINOR.PATCH (ex: 1.2.0)")
        
        self.skills[name]["handlers"][version] = handler
        self.skills[name]["versions"].append(version)
    
    def set_active_version(self, name: str, version: str) -> bool:
        """Define qual versão é a ativa."""
        if name not in self.skills:
            return False
        
        if version not in self.skills[name]["handlers"]:
            return False
        
        self.skills[name]["active_version"] = version
        return True
    
    def get_active_handler(self, name: str) -> Optional[Callable]:
        """Retorna handler da versão ativa."""
        if name not in self.skills:
            return None
        
        active_version = self.skills[name].get("active_version", "1.0.0")
        handler = self.skills[name]["handlers"].get(active_version)
        
        if handler is None:
            # Fallback para última versão disponível
            handler = list(self.skills[name]["handlers"].values())[-1]
        
        return handler
```

### Passo 3 — Compose pipelines

```python
class Pipeline:
    def __init__(self, name: str, steps: List[str]):
        self.name = name
        self.steps = steps  # ["summarize", "translate", "format"]
        self.created_at = datetime.now().isoformat()

    def compose_pipeline(self, skill_names: List[str]) -> 'Pipeline':
        """Compor múltiplas skills em sequência."""
        pipeline = Pipeline(
            name=f"pipeline_{'_'.join(skill_names)}",
            steps=skill_names,
        )
        return pipeline
    
    def execute_pipeline(self, pipeline: Pipeline, input_data: Dict) -> Dict:
        """Executar pipeline com error handling."""
        result = {
            "pipeline": pipeline.name,
            "steps_executed": [],
            "errors": [],
            "output": input_data.copy(),
            "status": "success",
        }
        
        current_output = input_data.copy()
        
        for step_name in pipeline.steps:
            try:
                # Obtém handler da skill
                handler = self.get_active_handler(step_name)
                
                if handler is None:
                    raise ValueError(f"Skill '{step_name}' não encontrada")
                
                # Executa skill
                step_result = handler(current_output)
                
                # Atualiza output
                if isinstance(step_result, dict):
                    current_output.update(step_result)
                else:
                    current_output["result"] = step_result
                
                result["steps_executed"].append({
                    "step": step_name,
                    "status": "success",
                })
            
            except Exception as e:
                error_info = {
                    "step": step_name,
                    "status": "failed",
                    "error": str(e),
                }
                result["errors"].append(error_info)
                result["status"] = "partial_success" if result["steps_executed"] else "failed"
                break  # Para na primeira falha
        
        result["output"] = current_output
        self.pipeline_log.append(result)
        
        return result
```

### Passo 4 — Descubra skills relevantes

```python
    def discover_skills(self, task_description: str, 
                        top_k: int = 3) -> List[Dict]:
        """Descobrir skills relevantes pela descrição (keyword matching)."""
        task_words = set(task_description.lower().split())
        
        scores = []
        for name, skill in self.skills.items():
            # Conta palavras que aparecem na descrição
            skill_words = set(skill["description"].lower().split())
            overlap = len(task_words & skill_words)
            
            if overlap > 0:
                scores.append({
                    "name": name,
                    "description": skill["description"],
                    "score": overlap,
                    "category": skill["category"],
                })
        
        # Ordena por score (descrescente)
        scores.sort(key=lambda x: x["score"], reverse=True)
        
        return scores[:top_k]
```

### Passo 5 — Adicione skills pré-definidas

```python
def create_sample_skills() -> 'SkillSystem':
    """Cria sistema com skills de exemplo."""
    system = SkillSystem()
    
    # Skill: sumarizar texto
    def summarize_handler(data: dict) -> dict:
        text = data.get("text", "")
        # Simula sumarização
        sentences = text.split(". ")
        summary = ". ".join(sentences[:min(2, len(sentences))])
        return {"summary": summary}
    
    system.register_skill(
        name="summarize",
        description="Sumariza texto em resumo conciso",
        handler=summarize_handler,
        category="text",
    )
    
    # Skill: traduzir texto
    def translate_handler(data: dict) -> dict:
        text = data.get("summary", data.get("text", ""))
        return {"translated": f"[Traduzido] {text}"}
    
    system.register_skill(
        name="translate",
        description="Traduz texto para idioma alvo",
        handler=translate_handler,
        category="text",
    )
    
    # Skill: analisar sentimento
    def sentiment_handler(data: dict) -> dict:
        text = data.get("translated", data.get("text", ""))
        positive_words = ["bom", "excelente", "ótimo", "incrível"]
        negative_words = ["ruim", "péssimo", "horível", "terrível"]
        
        text_lower = text.lower()
        pos_score = sum(1 for w in positive_words if w in text_lower)
        neg_score = sum(1 for w in negative_words if w in text_lower)
        
        if pos_score > neg_score:
            sentiment = "positive"
        elif neg_score > pos_score:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {"sentiment": sentiment, "confidence": round((pos_score + neg_score) / 3, 2)}
    
    system.register_skill(
        name="sentiment",
        description="Analisa sentimento do texto (positivo/negativo/neutro)",
        handler=sentiment_handler,
        category="analysis",
    )
    
    # Skill: formatar output
    def format_handler(data: dict) -> dict:
        return {
            "formatted": json.dumps(data, indent=2, ensure_ascii=False),
            "timestamp": datetime.now().isoformat(),
        }
    
    system.register_skill(
        name="format",
        description="Formata output em JSON estruturado",
        handler=format_handler,
        category="output",
    )
    
    return system
```

### Passo 6 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de skills e composição")
    parser.add_argument("--register", help="Registra skills de arquivo JSON")
    parser.add_argument("--list", action="store_true", help="Lista skills registradas")
    parser.add_argument("--pipeline", help="Executa pipeline (ex: summarize+translate)")
    parser.add_argument("--input", help="Arquivo de input (JSON ou texto)")
    parser.add_argument("--discover", help="Descobre skills por keyword")
    parser.add_argument("--top-k", type=int, default=3, help="Top K resultados")
    args = parser.parse_args()
    
    system = create_sample_skills()
    
    if args.list:
        skills = system.list_skills()
        print(json.dumps(skills, indent=2, ensure_ascii=False))
    
    elif args.pipeline:
        # Parse pipeline steps
        steps = [s.strip() for s in args.pipeline.split("+")]
        pipeline = system.compose_pipeline(steps)
        
        # Input
        input_data = {"text": "Este é um texto de exemplo para processar."}
        if args.input:
            with open(args.input) as f:
                if args.input.endswith(".json"):
                    input_data = json.load(f)
                else:
                    input_data = {"text": f.read()}
        
        result = system.execute_pipeline(pipeline, input_data)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.discover:
        results = system.discover_skills(args.discover, top_k=args.top_k)
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    else:
        # Mostra ajuda
        print("🔧 Skill System - Execute uma das opções:")
        print("  --list              Lista todas as skills")
        print("  --pipeline <steps>  Executa pipeline (ex: summarize+translate)")
        print("  --discover <text>   Descobre skills relevantes")
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `register_skill()` armazena name, description, category e handler no registry
- [ ] `version_skill()` valida formato semântico MAJOR.MINOR.PATCH e registra novo handler
- [ ] `compose_pipeline()` cria Pipeline com lista de steps; `execute_pipeline()` executa sequencialmente com error handling
- [ ] `discover_skills()` faz keyword matching entre task_description e skill descriptions
- [ ] `get_active_handler()` retorna handler da versão ativa com fallback para última versão
- [ ] CLI aceita `--list`, `--pipeline` (formato step+step), `--discover` e gera JSON

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

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
