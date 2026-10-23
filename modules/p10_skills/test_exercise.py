"""
Módulo P10 — Teste do Exercício

Execute com: python modules/p10_skills/test_exercise.py

IMPLEMENTE os TODOs para fazer os testes passarem.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

console = Console()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 1: Skill Registry — Registro de skills funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_01_skill_registry():
    """
    TODO: Implemente registro de skills (catalogo centralizado).
    
    Cada skill tem: name, description, input_schema, output_schema, handler.
    """
    class SkillRegistry:
        def __init__(self):
            self.skills: Dict[str, dict] = {}
        
        def register(self, name: str, description: str, 
                     handler: Callable[[dict], dict]):
            """Registre uma nova skill."""
            self.skills[name] = {
                "name": name,
                "description": description,
                "handler": handler
            }
        
        def get(self, name: str) -> Optional[dict]:
            """Retorne skill pelo nome."""
            return self.skills.get(name)
        
        def list_all(self) -> List[str]:
            """Retorne lista de nomes registrados."""
            return list(self.skills.keys())
    
    registry = SkillRegistry()
    
    # Registra skills
    registry.register("summarize", "Resume text to key points",
                      lambda x: {"summary": "Resumo"})
    registry.register("translate", "Translate text to target language",
                      lambda x: {"translated": "Tradução"})
    registry.register("sentiment", "Analyze sentiment of text",
                      lambda x: {"sentiment": "positive"})
    
    names = registry.list_all()
    assert len(names) == 3, \
        f"Deve ter 3 skills registradas, got {len(names)}"
    
    summarize = registry.get("summarize")
    assert summarize is not None, "Skill 'summarize' deve existir"
    assert summarize["description"] == "Resume text to key points", \
        "Descrição deve corresponder"
    
    console.print(f"[green]✓[/green] Registry: {len(names)} skills registered ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 2: Skill Composition — Composição de skills funciona?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_02_skill_composition():
    """
    TODO: Compose múltiplas skills em pipeline.
    
    Input → [skill1] → intermediate → [skill2] → final output.
    """
    class SkillComposer:
        def __init__(self, registry: SkillRegistry):
            self.registry = registry
            self.pipeline: List[str] = []
        
        def add_step(self, skill_name: str):
            """Adicione skill ao pipeline."""
            if self.registry.get(skill_name):
                self.pipeline.append(skill_name)
        
        def execute(self, initial_input: dict) -> dict:
            """Execute pipeline sequencialmente."""
            current_data = initial_input.copy()
            for skill_name in self.pipeline:
                skill = self.registry.get(skill_name)
                if skill:
                    current_data = skill["handler"](current_data)
            return current_data
    
    registry = SkillRegistry()
    composer = SkillComposer(registry)
    
    # Registra skills compostas
    registry.register("extract_entities", "Extract named entities",
                      lambda x: {"entities": ["Brazil", "São Paulo"], "text": x.get("text", "")})
    registry.register("enrich", "Enrich entities with metadata",
                      lambda x: {"enriched": [{"name": e, "country": "BR"} for e in x.get("entities", [])]})
    
    composer.add_step("extract_entities")
    composer.add_step("enrich")
    
    result = composer.execute({"text": "Brasil é um país bonito"})
    
    assert "enriched" in result, \
        "Resultado final deve ter 'enriched'"
    assert len(result["enriched"]) > 0, \
        "Deve haver entidades enriquecidas"
    
    console.print(f"[green]✓[/green] Composition: 2-step pipeline, "
                  f"{len(result['enriched'])} enriched entities")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 3: Pipeline Execution — Pipeline executa corretamente?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_03_pipeline_execution():
    """
    TODO: Execute pipeline com error handling por step.
    
    Se um step falha, pipeline pode: abortar, pular, ou usar fallback.
    """
    class PipelineExecutor:
        def __init__(self, registry: SkillRegistry):
            self.registry = registry
            self.steps: List[str] = []
            self.error_policy: str = "abort"  # "abort" | "skip" | "fallback"
        
        def set_steps(self, step_names: List[str]):
            """Configure steps do pipeline."""
            self.steps = step_names
        
        def set_error_policy(self, policy: str):
            """Configure política de erro."""
            if policy in ("abort", "skip", "fallback"):
                self.error_policy = policy
        
        def execute(self, input_data: dict) -> dict:
            """Execute pipeline com error handling."""
            current_data = input_data.copy()
            for step_name in self.steps:
                skill = self.registry.get(step_name)
                if not skill:
                    if self.error_policy == "abort":
                        return {"error": f"Skill {step_name} não encontrada"}
                    continue
                try:
                    current_data = skill["handler"](current_data)
                except Exception as e:
                    if self.error_policy == "abort":
                        return {"error": f"Skill {step_name} falhou: {e}"}
                    elif self.error_policy == "skip":
                        continue
                    elif self.error_policy == "fallback":
                        current_data.setdefault("fallback", True)
            return current_data
    
    registry = SkillRegistry()
    executor = PipelineExecutor(registry)
    
    registry.register("parse_json", "Parse JSON string",
                      lambda x: {"parsed": {"key": "value"}})
    registry.register("validate", "Validate parsed data",
                      lambda x: {"valid": True, "errors": []})
    registry.register("format_output", "Format final output",
                      lambda x: {"formatted": "Output formatado"})
    
    executor.set_steps(["parse_json", "validate", "format_output"])
    result = executor.execute({"input": '{"key": "value"}'})
    
    assert "formatted" in result, \
        "Pipeline completo deve gerar output formatado"
    
    console.print("[green]✓[/green] Pipeline: 3-step execution ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 4: Skill Discovery — Descoberta automática de skills?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_04_skill_discovery():
    """
    TODO: Descubra skills relevantes para uma tarefa.
    
    Busca por keywords no description + tags.
    """
    class SkillDiscoverer:
        def __init__(self, registry: SkillRegistry):
            self.registry = registry
        
        def find_relevant(self, task_description: str, top_k: int = 3) -> List[dict]:
            """Encontre skills relevantes pela descrição da tarefa."""
            task_lower = task_description.lower()
            scored_skills = []
            for name, skill_info in self.registry.skills.items():
                desc_lower = skill_info["description"].lower()
                # Score por palavras-chave que aparecem na descrição da tarefa
                score = sum(1 for word in task_lower.split() 
                           if len(word) > 3 and word in desc_lower)
                if score > 0:
                    scored_skills.append((score, name, skill_info))
            # Ordena por score (maior primeiro) e retorna top_k
            scored_skills.sort(key=lambda x: x[0], reverse=True)
            return [{"name": s[1], **s[2]} for s in scored_skills[:top_k]]
    
    registry = SkillRegistry()
    discoverer = SkillDiscoverer(registry)
    
    registry.register("summarize", "Summarize long documents into short text",
                      lambda x: {"summary": "..."})
    registry.register("translate", "Translate text between languages",
                      lambda x: {"translated": "..."})
    registry.register("sentiment", "Analyze sentiment and emotions in text",
                      lambda x: {"sentiment": "positive"})
    registry.register("extract_entities", "Extract named entities like people and places",
                      lambda x: {"entities": []})
    registry.register("format_output", "Format data as JSON or markdown",
                      lambda x: {"formatted": "..."})
    
    results = discoverer.find_relevant("I need to analyze customer feedback sentiment")
    
    assert len(results) <= 3, \
        f"Deve retornar no máximo {top_k} resultados, got {len(results)}"
    assert len(results) > 0, \
        "Deve encontrar pelo menos 1 skill relevante"
    
    # Sentiment deve estar entre os resultados
    found_sentiment = any(s["name"] == "sentiment" for s in results)
    assert found_sentiment, \
        "Skill 'sentiment' deve ser encontrada para análise de feedback"
    
    console.print(f"[green]✓[/green] Discovery: {len(results)} relevant skills found")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TESTE 5: Skill Versioning — Versionamento de skills?
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def test_05_skill_versioning():
    """
    TODO: Implemente versionamento de skills.
    
    Mesma skill pode ter múltiplas versões. Default = mais recente.
    """
    class VersionedRegistry:
        def __init__(self):
            self.versions: Dict[str, Dict[str, dict]] = {}
        
        def register(self, name: str, version: str, 
                     handler: Callable[[dict], dict],
                     description: str = ""):
            """Registre skill com versão específica."""
            if name not in self.versions:
                self.versions[name] = {}
            self.versions[name][version] = {
                "name": name,
                "version": version,
                "handler": handler,
                "description": description
            }
        
        def get(self, name: str, version: Optional[str] = None) -> Optional[dict]:
            """Retorne skill. Se version=None, retorne latest."""
            if name not in self.versions:
                return None
            if version is None:
                # Retorna mais recente (última alfabeticamente)
                versions = sorted(self.versions[name].keys())
                version = versions[-1]
            return self.versions[name].get(version)
        
        def list_versions(self, name: str) -> List[str]:
            """Retorne lista de versões disponíveis."""
            if name in self.versions:
                return sorted(self.versions[name].keys())
            return []
    
    registry = VersionedRegistry()
    
    # Registra múltiplas versões
    registry.register("summarize", "v1",
                      lambda x: {"summary": "Old summary"},
                      "Original summarizer")
    registry.register("summarize", "v2",
                      lambda x: {"summary": "Better summary", "key_points": []},
                      "Improved summarizer with key points")
    registry.register("summarize", "v2.1",
                      lambda x: {"summary": "Best summary", "key_points": [], "confidence": 0.9},
                      "Latest with confidence scores")
    
    versions = registry.list_versions("summarize")
    assert len(versions) == 3, \
        f"Deve ter 3 versões, got {len(versions)}"
    
    # Default = latest
    default = registry.get("summarize")
    assert default is not None, \
        "Default deve retornar versão mais recente"
    assert "confidence" in default("test"), \
        "Versão default deve ter campo 'confidence' (v2.1)"
    
    # Versão específica
    v1 = registry.get("summarize", "v1")
    assert v1 is not None, "Deve conseguir acessar v1"
    
    console.print(f"[green]✓[/green] Versioning: {len(versions)} versions, "
                  f"default=v2.1 ✓")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# RUN ALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def run_all():
    tests = [test_01_skill_registry, test_02_skill_composition,
             test_03_pipeline_execution, test_04_skill_discovery,
             test_05_skill_versioning]
    
    console.print(Panel("🧪 Testes do Exercício — IMPLEMENTE os TODOs!",
                        title="[bold cyan]P10: Skills e Composição[/bold cyan]",
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
