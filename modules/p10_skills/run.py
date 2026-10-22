"""
Módulo P10 — Design e Composição de Skills

Sistema completo de skills versionadas com registry, schemas validados
e pipelines composáveis. Cada skill é uma função com input/output tipados.

Problema: Como compor múltiplas habilidades em agentes reutilizáveis?
Skills são LEGO blocks — encaixe-os para criar workflows complexos.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
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
logger = setup_logging("p10_skills")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SKILL REGISTRY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SkillStatus(Enum):
    """Status de uma skill no ciclo de vida."""
    
    DRAFT = "draft"           # Em desenvolvimento
    TESTED = "tested"         # Testada e validada
    PRODUCTION = "production"  # Em produção
    DEPRECATED = "deprecated"  # Substituída por outra


@dataclass
class SkillVersion:
    """Versão de uma skill."""
    
    version: str              # Semantic versioning: "1.2.0"
    description: str
    input_schema: dict        # JSON Schema do input
    output_schema: dict       # JSON Schema do output
    created_at: float = field(default_factory=time.time)
    is_active: bool = True
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "description": self.description,
            "input_schema": self.input_schema,
            "output_schema": self.output_schema,
            "created_at": self.created_at,
            "is_active": self.is_active,
        }


@dataclass
class Skill:
    """Skill completa com múltiplas versões."""
    
    name: str
    description: str
    category: str             # "nlp", "data", "web", "math", etc.
    status: SkillStatus = SkillStatus.DRAFT
    versions: dict[str, SkillVersion] = field(default_factory=dict)
    total_executions: int = 0
    avg_latency_ms: float = 0.0
    
    def add_version(self, version: str, input_schema: dict, 
                    output_schema: dict, description: str = "") -> None:
        """Adiciona nova versão da skill."""
        self.versions[version] = SkillVersion(
            version=version,
            description=description or f"Versão {version} de {self.name}",
            input_schema=input_schema,
            output_schema=output_schema,
        )
        
        # Ativa a nova versão, desativa anteriores
        for v in self.versions.values():
            v.is_active = False
        self.versions[version].is_active = True
        
        logger.info(f"Nova versão adicionada: {self.name} v{version}")
    
    def get_active_version(self) -> Optional[SkillVersion]:
        """Retorna versão ativa atual."""
        for version in self.versions.values():
            if version.is_active:
                return version
        return None


class SkillRegistry:
    """
    Registry central de todas as skills do sistema.
    
    Funcionalidades:
    - Registrar novas skills
    - Versionamento semântico
    - Lookup por nome/categoria
    - Estatísticas de uso
    """
    
    def __init__(self):
        self._skills: dict[str, Skill] = {}
    
    def register(self, skill: Skill) -> None:
        """Registra uma skill no registry."""
        self._skills[skill.name] = skill
        logger.info(f"Skill registrada: {skill.name} ({skill.category})")
    
    def get(self, name: str) -> Optional[Skill]:
        """Busca skill por nome."""
        return self._skills.get(name)
    
    def list_by_category(self, category: str) -> list[Skill]:
        """Lista skills por categoria."""
        return [s for s in self._skills.values() if s.category == category]
    
    def list_all(self) -> list[Skill]:
        """Lista todas as skills."""
        return list(self._skills.values())
    
    def upgrade_version(self, name: str, new_version: str,
                        input_schema: dict, output_schema: dict) -> bool:
        """Atualiza versão de uma skill."""
        skill = self._skills.get(name)
        if not skill:
            return False
        
        skill.add_version(new_version, input_schema, output_schema)
        return True
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do registry."""
        categories: dict[str, int] = {}
        for skill in self._skills.values():
            categories[skill.category] = categories.get(skill.category, 0) + 1
        
        return {
            "total_skills": len(self._skills),
            "by_category": categories,
            "by_status": {
                status.value: sum(
                    1 for s in self._skills.values() if s.status == status
                )
                for status in SkillStatus
            },
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BASE SKILL CLASS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BaseSkill(ABC):
    """
    Classe base para todas as skills.
    
    Toda skill deve implementar:
    - execute(input_data) → output_data
    - validate_input(schema, data) → bool
    """
    
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
        self._call_count = 0
        self._total_latency_ms = 0.0
    
    @abstractmethod
    def execute(self, input_data: dict) -> dict:
        """
        Executa a skill com os dados de entrada.
        
        Args:
            input_data: Dados conforme input_schema registrado.
        
        Returns:
            Dados conforme output_schema registrado.
        """
        pass
    
    def call(self, input_data: dict) -> dict:
        """Wrapper que mede latência e conta chamadas."""
        start = time.time()
        self._call_count += 1
        
        try:
            result = self.execute(input_data)
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            latency = (time.time() - start) * 1000
            self._total_latency_ms += latency
    
    @property
    def stats(self) -> dict:
        """Retorna estatísticas da skill."""
        return {
            "name": self.name,
            "version": self.version,
            "calls": self._call_count,
            "avg_latency_ms": round(
                self._total_latency_ms / max(self._call_count, 1), 2
            ),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONCRETE SKILLS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SentimentAnalysisSkill(BaseSkill):
    """Skill de análise de sentimento (positivo/negativo/neutro)."""
    
    def __init__(self):
        super().__init__("sentiment_analysis", "1.0.0")
    
    def execute(self, input_data: dict) -> dict:
        text = input_data.get("text", "").lower()
        
        positive_words = {"bom", "excelente", "ótimo", "gosto", "amar", "feliz"}
        negative_words = {"ruim", "péssimo", "horrível", "odeio", "triste", "rápido"}
        
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count:
            sentiment = "positive"
            confidence = min(pos_count / 3, 1.0)
        elif neg_count > pos_count:
            sentiment = "negative"
            confidence = min(neg_count / 3, 1.0)
        else:
            sentiment = "neutral"
            confidence = 0.5
        
        return {
            "sentiment": sentiment,
            "confidence": round(confidence, 2),
            "positive_words": pos_count,
            "negative_words": neg_count,
        }


class TextSummarizationSkill(BaseSkill):
    """Skill de sumarização de texto (extrativa)."""
    
    def __init__(self):
        super().__init__("text_summarization", "1.0.0")
    
    def execute(self, input_data: dict) -> dict:
        text = input_data.get("text", "")
        max_sentences = input_data.get("max_sentences", 2)
        
        sentences = text.split(". ")
        summary_sentences = sentences[:max_sentences]
        summary = ". ".join(summary_sentences) + "."
        
        compression_ratio = len(summary) / max(len(text), 1)
        
        return {
            "summary": summary,
            "original_length": len(text),
            "summary_length": len(summary),
            "compression_ratio": round(compression_ratio, 2),
            "sentences_kept": len(summary_sentences),
        }


class EntityExtractionSkill(BaseSkill):
    """Skill de extração de entidades nomeadas (simplificada)."""
    
    def __init__(self):
        super().__init__("entity_extraction", "1.0.0")
    
    def execute(self, input_data: dict) -> dict:
        text = input_data.get("text", "")
        
        # Regex patterns simplificados
        import re
        
        patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "url": r'\bhttps?://\S+\b',
            "date": r'\b\d{4}-\d{2}-\d{2}\b',
        }
        
        entities = {}
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                entities[entity_type] = list(set(matches))
        
        return {
            "entities": entities,
            "total_found": sum(len(v) for v in entities.values()),
        }


class TranslatorSkill(BaseSkill):
    """Skill de tradução simplificada (PT↔EN)."""
    
    def __init__(self):
        super().__init__("translator", "1.0.0")
        
        # Dicionário simplificado PT→EN
        self._dictionary = {
            "olá": "hello", "mundo": "world", "obrigado": "thank you",
            "bom dia": "good morning", "boa noite": "good night",
            "sim": "yes", "não": "no", "por favor": "please",
            "como vai você": "how are you", "tudo bem": "all right",
            "eu gosto": "i like", "eu amo": "i love", "eu trabalho": "i work",
            "python": "python", "programação": "programming", "dados": "data",
        }
    
    def execute(self, input_data: dict) -> dict:
        text = input_data.get("text", "")
        target_lang = input_data.get("target_language", "en")
        
        words = text.lower().split()
        translated = []
        
        for word in words:
            cleaned = word.strip(".,!?;:")
            translation = self._dictionary.get(cleaned, word)
            translated.append(translation)
        
        translated_text = " ".join(translated)
        
        return {
            "original": text,
            "translated": translated_text,
            "source_language": "pt",
            "target_language": target_lang,
            "words_translated": len([w for w in translated if w != text.split()[translated.index(w)] if w in self._dictionary]),
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PIPELINE COMPOSITOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class Pipeline:
    """
    Compositor de pipeline de skills.
    
    Encadeia múltiplas skills: output de uma → input da próxima.
    
    Exemplo:
    Input → [Sentiment] → [Filter] → [Summarize] → Output
    """
    
    def __init__(self, name: str):
        self.name = name
        self._steps: list[tuple[str, BaseSkill]] = []
        self._filters: list[tuple[str, callable]] = []
    
    def add_step(self, name: str, skill: BaseSkill) -> "Pipeline":
        """Adiciona step ao pipeline."""
        self._steps.append((name, skill))
        logger.info(f"Step adicionado: {name}")
        return self  # Chainable
    
    def add_filter(self, name: str, predicate: callable) -> "Pipeline":
        """Adiciona filtro que pode abortar o pipeline."""
        self._filters.append((name, predicate))
        return self
    
    def execute(self, input_data: dict) -> dict:
        """Executa pipeline completo."""
        current_data = input_data.copy()
        results = []
        
        console.print(f"\n[bold cyan]🔄 Executando pipeline '{self.name}':[/]")
        
        for step_name, skill in self._steps:
            console.print(f"  [dim]→[/] {step_name}...")
            
            # Aplica filtros antes do step
            for filter_name, predicate in self._filters:
                if not predicate(current_data):
                    console.print(f"    [yellow]⏹ Filtro '{filter_name}' bloqueou[/]")
                    return {
                        "success": False,
                        "aborted_at": filter_name,
                        "partial_results": results,
                    }
            
            # Executa skill
            result = skill.call(current_data)
            
            if not result["success"]:
                console.print(f"    [red]✕ Erro em {step_name}[/]")
                return {
                    "success": False,
                    "error_at": step_name,
                    "error": result["error"],
                    "partial_results": results,
                }
            
            results.append({
                "step": step_name,
                "result": result["data"],
                "stats": skill.stats,
            })
            
            # Passa output como input do próximo step
            current_data = result["data"]
            
            console.print(f"    [green]✓[/] Concluído")
        
        return {
            "success": True,
            "pipeline": self.name,
            "results": results,
            "final_output": current_data,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    """Executa demonstração completa de skills e pipelines."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO P10 — Skills e Composição[/]\n\n"
        "Skill registry versionado, skills concretas,\n"
        "e pipelines composáveis encadeando múltiplas skills.",
        title="🧩 AI Agents Course",
        border_style="cyan",
    ))
    
    # ━━ 1. Register Skills ━━
    registry = SkillRegistry()
    
    console.print("\n[bold]1️⃣  Registrando Skills:[/]\n")
    
    # Cria e registra skills
    skills_to_register = [
        ("sentiment_analysis", "Análise de sentimento", "nlp", SentimentAnalysisSkill()),
        ("text_summarization", "Sumarização de texto", "nlp", TextSummarizationSkill()),
        ("entity_extraction", "Extração de entidades", "nlp", EntityExtractionSkill()),
        ("translator", "Tradutor PT↔EN", "nlp", TranslatorSkill()),
    ]
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Nome", style="cyan")
    table.add_column("Categoria", style="cyan")
    table.add_column("Descrição", style="white")
    
    for name, desc, category, skill_instance in skills_to_register:
        skill = Skill(name=name, description=desc, category=category)
        skill.add_version(
            version="1.0.0",
            input_schema={"type": "dict", "required": ["text"]},
            output_schema={"type": "dict"},
            description=desc,
        )
        registry.register(skill)
        table.add_row(name, category, desc)
    
    console.print(table)
    
    # ━━ 2. Execute Individual Skills ━━
    console.print("\n[bold]2️⃣  Executando Skills Individuais:[/]\n")
    
    test_text = "Eu gosto muito de Python! Trabalho com dados todos os dias."
    
    sentiment_skill = SentimentAnalysisSkill()
    result = sentiment_skill.call({"text": test_text})
    console.print(f"  [dim]Sentimento:[/] {json.dumps(result['data'], indent=2)}")
    
    summarize_skill = TextSummarizationSkill()
    result = summarize_skill.call({"text": test_text, "max_sentences": 1})
    console.print(f"  [dim]Sumarização:[/] {json.dumps(result['data'], indent=2)}")
    
    entity_skill = EntityExtractionSkill()
    result = entity_skill.call({"text": "Contato: user@email.com, telefone: 1199999999"})
    console.print(f"  [dim]Entidades:[/] {json.dumps(result['data'], indent=2)}")
    
    # ━━ 3. Compose Pipeline ━━
    console.print("\n[bold]3️⃣  Pipeline Composto:[/]\n")
    
    pipeline = Pipeline("Análise de Review")
    pipeline.add_step("sentiment", SentimentAnalysisSkill())
    pipeline.add_step("summarize", TextSummarizationSkill())
    
    review_text = """Este produto é excelente! A qualidade é ótima e o preço justo.
Recomendo para todos. Entrega rápida e embalagem perfeita."""
    
    result = pipeline.execute({"text": review_text, "max_sentences": 1})
    
    if result["success"]:
        console.print(f"\n  [green]✅ Pipeline concluído![/]")
        console.print(f"  [dim]Output final:[/]")
        console.print(json.dumps(result["final_output"], indent=2, ensure_ascii=False))
    
    # ━━ 4. Registry Stats ━━
    stats = registry.get_stats()
    
    console.print("\n[bold cyan]📊 Estatísticas do Registry:[/]\n")
    
    stats_table = Table(show_header=True, header_style="bold cyan")
    stats_table.add_column("Métrica", style="cyan")
    stats_table.add_column("Valor", justify="right")
    
    stats_table.add_row("Total de skills", str(stats["total_skills"]))
    
    cat_table = Table(show_header=False)
    for cat, count in stats["by_category"].items():
        cat_table.add_row(cat, str(count))
    stats_table.add_row("Por categoria", cat_table)
    
    console.print(stats_table)
    
    console.print("\n[dim]💡 Skills são LEGO blocks — componha livremente![/]")


if __name__ == "__main__":
    main()
"""
Módulo P10 — Design de Skills e Composição

Sistema completo de registry de skills versionadas, schemas tipados,
e composição de pipelines multi-skill. Cada skill é uma função com
input/output tipados que pode ser combinada em workflows.

Problema: Como estruturar agentes complexos a partir de blocos simples?
Skills são LEGO blocks — você monta o fluxo que precisa.
"""

from __future__ import annotations

import json
import logging
import sys
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
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
logger = setup_logging("p10_skills")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SKILL REGISTRY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class SkillVersion:
    """
    Versão de uma skill com schema de input/output.
    
    Cada skill pode ter múltiplas versões (v1, v2, ...).
    O registry gerencia qual versão está ativa.
    """
    
    def __init__(self, name: str, version: str, func, 
                 input_schema: dict, output_schema: dict,
                 description: str = ""):
        self.name = name
        self.version = version
        self.func = func
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.description = description
        self.created_at = time.time()
        self.call_count = 0
        self.total_cost = 0.0
    
    async def execute(self, **kwargs) -> dict:
        """Executa a skill com validação de input."""
        self.call_count += 1
        
        # Valida input contra schema
        errors = self._validate_input(kwargs)
        if errors:
            raise ValueError(f"Schema validation failed: {errors}")
        
        # Executa
        result = await self.func(**kwargs)
        
        return {
            "skill": self.name,
            "version": self.version,
            "result": result,
            "call_count": self.call_count,
        }
    
    def _validate_input(self, kwargs: dict) -> list[str]:
        """Valida input contra schema."""
        errors = []
        
        for field_name, field_spec in self.input_schema.get("required", []).items():
            if field_name not in kwargs:
                errors.append(f"Missing required field: {field_name}")
        
        for field_name, field_spec in self.input_schema.get("properties", {}).items():
            if field_name in kwargs:
                value = kwargs[field_name]
                expected_type = field_spec.get("type", "string")
                
                type_map = {
                    "string": str,
                    "integer": int,
                    "number": (int, float),
                    "boolean": bool,
                    "array": list,
                    "object": dict,
                }
                
                if expected_type in type_map and not isinstance(value, type_map[expected_type]):
                    errors.append(
                        f"Field '{field_name}' expected {expected_type}, "
                        f"got {type(value).__name__}"
                    )
        
        return errors


class SkillRegistry:
    """
    Registry central de todas as skills do agente.
    
    Gerencia registro, lookup e versionamento de skills.
    """
    
    def __init__(self):
        self._skills: dict[str, dict[str, SkillVersion]] = {}
        self._active_versions: dict[str, str] = {}
    
    def register(self, skill: SkillVersion) -> None:
        """Registra uma skill no registry."""
        if skill.name not in self._skills:
            self._skills[skill.name] = {}
        
        self._skills[skill.name][skill.version] = skill
        
        # Se é a primeira versão, marca como ativa
        if skill.name not in self._active_versions:
            self._active_versions[skill.name] = skill.version
    
    def get(self, name: str, version: str = "latest") -> SkillVersion:
        """Busca skill pelo nome e versão."""
        if name not in self._skills:
            raise KeyError(f"Skill '{name}' not found")
        
        if version == "latest":
            version = self._active_versions.get(name, "v1")
        
        if version not in self._skills[name]:
            raise KeyError(f"Version '{version}' not found for skill '{name}'")
        
        return self._skills[name][version]
    
    def list_skills(self) -> list[dict]:
        """Lista todas as skills registradas."""
        result = []
        for name, versions in self._skills.items():
            active = self._active_versions.get(name, "v1")
            for version, skill in versions.items():
                result.append({
                    "name": name,
                    "version": version,
                    "active": version == active,
                    "description": skill.description,
                    "calls": skill.call_count,
                })
        return result
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do registry."""
        total_calls = sum(
            skill.call_count
            for versions in self._skills.values()
            for skill in versions.values()
        )
        
        return {
            "total_skills": sum(len(v) for v in self._skills.values()),
            "unique_skills": len(self._skills),
            "total_calls": total_calls,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BASE SKILL CLASS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class BaseSkill(ABC):
    """
    Classe base para skills.
    
    Subclasses implementam execute() com lógica específica.
    O registry gerencia automaticamente o versionamento.
    """
    
    name: str = "base_skill"
    version: str = "v1"
    description: str = ""
    input_schema: dict = {}
    output_schema: dict = {}
    
    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.skill_version = SkillVersion(
            name=self.name,
            version=self.version,
            func=self.execute,
            input_schema=self.input_schema,
            output_schema=self.output_schema,
            description=self.description,
        )
        self.registry.register(self.skill_version)
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Implementa a lógica da skill."""
        pass


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# BUILT-IN SKILLS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

class ClassifySkill(BaseSkill):
    """Classifica texto em categorias predefinidas."""
    
    name = "classify"
    version = "v1"
    description = "Classifica texto em categorias"
    input_schema = {
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
            "categories": {"type": "array"},
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "category": {"type": "string"},
            "confidence": {"type": "number"},
        },
    }
    
    async def execute(self, text: str, categories: list[str] | None = None) -> dict:
        """Simula classificação por LLM."""
        cats = categories or ["spam", "not_spam", "urgent"]
        
        # Simulação simplificada de classificação
        text_lower = text.lower()
        
        if any(w in text_lower for w in ["spam", "promoção", "desconto"]):
            category = "spam"
            confidence = 0.85
        elif any(w in text_lower for w in ["urgente", "emergência", "imediato"]):
            category = "urgent"
            confidence = 0.92
        else:
            category = "not_spam"
            confidence = 0.78
        
        return {
            "category": category,
            "confidence": confidence,
            "categories": cats,
        }


class SummarizeSkill(BaseSkill):
    """Resume textos longos."""
    
    name = "summarize"
    version = "v1"
    description = "Resume textos longos"
    input_schema = {
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
            "max_length": {"type": "integer"},
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "original_length": {"type": "integer"},
            "summary_length": {"type": "integer"},
        },
    }
    
    async def execute(self, text: str, max_length: int = 100) -> dict:
        """Simula sumarização por LLM."""
        original_length = len(text)
        
        # Simulação: pega as primeiras frases
        sentences = text.split(". ")
        summary_parts = []
        current_length = 0
        
        for sentence in sentences:
            if current_length + len(sentence) > max_length * 4:  # ~4 chars per token
                break
            summary_parts.append(sentence)
            current_length += len(sentence)
        
        summary = ". ".join(summary_parts) + "."
        
        return {
            "summary": summary,
            "original_length": original_length,
            "summary_length": len(summary),
            "compression_ratio": round(len(summary) / max(original_length, 1) * 100, 1),
        }


class TranslateSkill(BaseSkill):
    """Traduz texto entre idiomas."""
    
    name = "translate"
    version = "v1"
    description = "Traduz texto entre idiomas"
    input_schema = {
        "required": ["text", "target_language"],
        "properties": {
            "text": {"type": "string"},
            "target_language": {"type": "string"},
            "source_language": {"type": "string"},
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "translated_text": {"type": "string"},
            "source_language": {"type": "string"},
            "target_language": {"type": "string"},
        },
    }
    
    async def execute(self, text: str, target_language: str, 
                      source_language: str = "auto") -> dict:
        """Simula tradução por LLM."""
        translations = {
            "en": {
                "olá mundo": "hello world",
                "bom dia": "good morning",
            },
            "pt": {
                "hello world": "olá mundo",
                "good morning": "bom dia",
            },
        }
        
        # Simulação básica
        text_lower = text.lower().strip()
        
        if source_language == "auto":
            source_language = "pt" if any(c in text_lower for c in "ãõçéú") else "en"
        
        lang_pair = f"{source_language}_{target_language}"
        
        if source_language in translations and text_lower in translations[source_language]:
            translated = translations[source_language][text_lower]
        else:
            translated = f"[{target_language}] {text}"
        
        return {
            "translated_text": translated,
            "source_language": source_language,
            "target_language": target_language,
        }


class SentimentSkill(BaseSkill):
    """Analisa sentimento de texto."""
    
    name = "sentiment"
    version = "v1"
    description = "Analisa sentimento de texto"
    input_schema = {
        "required": ["text"],
        "properties": {
            "text": {"type": "string"},
        },
    }
    output_schema = {
        "type": "object",
        "properties": {
            "sentiment": {"type": "string"},
            "score": {"type": "number"},
            "confidence": {"type": "number"},
        },
    }
    
    async def execute(self, text: str) -> dict:
        """Simula análise de sentimento."""
        text_lower = text.lower()
        
        positive_words = ["bom", "excelente", "ótimo", "gosto", "amar", "feliz"]
        negative_words = ["ruim", "péssimo", "horrível", "odeio", "triste", "rápido"]
        
        pos_score = sum(1 for w in positive_words if w in text_lower)
        neg_score = sum(1 for w in negative_words if w in text_lower)
        
        if pos_score > neg_score:
            sentiment = "positive"
            score = 0.7 + (pos_score * 0.05)
        elif neg_score > pos_score:
            sentiment = "negative"
            score = 0.3 - (neg_score * 0.05)
        else:
            sentiment = "neutral"
            score = 0.5
        
        return {
            "sentiment": sentiment,
            "score": min(max(score, 0), 1),
            "confidence": 0.82,
        }


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PIPELINE COMPOSITOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@dataclass
class PipelineStep:
    """Passo individual no pipeline."""
    
    skill_name: str
    skill_version: str = "latest"
    input_mapping: dict[str, str] = field(default_factory=dict)  # {output_key: input_key}
    params: dict[str, Any] = field(default_factory=dict)


class PipelineCompositor:
    """
    Compositor de pipelines multi-skill.
    
    Encadeia outputs de uma skill como inputs da próxima.
    """
    
    def __init__(self, registry: SkillRegistry):
        self.registry = registry
        self.steps: list[PipelineStep] = []
    
    def add_step(self, skill_name: str, 
                 input_mapping: dict[str, str] | None = None,
                 params: dict[str, Any] | None = None,
                 after: str | None = None) -> None:
        """
        Adiciona passo ao pipeline.
        
        Args:
            skill_name: Nome da skill a executar.
            input_mapping: Mapeia outputs anteriores para inputs desta skill.
            params: Parâmetros fixos para esta skill.
            after: Nome do passo anterior (para controle de ordem).
        """
        step = PipelineStep(
            skill_name=skill_name,
            input_mapping=input_mapping or {},
            params=params or {},
        )
        
        if after is None:
            self.steps.append(step)
        else:
            # Insere após o passo especificado
            insert_idx = None
            for i, s in enumerate(self.steps):
                if s.skill_name == after:
                    insert_idx = i + 1
                    break
            
            if insert_idx is not None:
                self.steps.insert(insert_idx, step)
            else:
                self.steps.append(step)
    
    async def execute(self, initial_input: dict[str, Any]) -> dict:
        """
        Executa pipeline completo.
        
        Cada passo recebe o output do passo anterior.
        """
        context = dict(initial_input)
        results = {}
        
        console.print(f"\n[bold cyan]🔄 Executando pipeline ({len(self.steps)} steps)[/]")
        
        for i, step in enumerate(self.steps):
            skill = self.registry.get(step.skill_name, step.skill_version)
            
            # Resolve inputs: combina params fixos + mapeamento de outputs anteriores
            step_input = dict(step.params)
            
            # Aplica mapeamento de outputs anteriores
            for output_key, input_key in step.input_mapping.items():
                if output_key in context:
                    step_input[input_key] = context[output_key]
            
            console.print(f"  [dim]Step {i+1}/{len(self.steps)}:[/] {step.skill_name}")
            
            # Executa skill
            result = await skill.execute(**step_input)
            
            # Atualiza contexto
            context.update(result)
            results[f"step_{i}"] = result
            
            # Mostra resultado parcial
            if "summary" in result:
                console.print(f"    [green]→[/] Summary: {result['summary'][:60]}...")
            elif "category" in result:
                console.print(f"    [green]→[/] Category: {result['category']}")
            elif "sentiment" in result:
                console.print(f"    [green]→[/] Sentiment: {result['sentiment']}")
            elif "translated_text" in result:
                console.print(f"    [green]→[/] Translated: {result['translated_text'][:60]}...")
        
        results["final_output"] = context
        
        return results


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# EXECUÇÃO PRINCIPAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main():
    """Executa demonstração completa de skills e composição."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO P10 — Skills e Composição[/]\n\n"
        "Skill registry versionado, schemas tipados,\n"
        "e composição de pipelines multi-skill.",
        title="🧩 AI Agents Course",
        border_style="cyan",
    ))
    
    # ━━ 1. Registra skills ━━
    registry = SkillRegistry()
    
    ClassifySkill(registry)
    SummarizeSkill(registry)
    TranslateSkill(registry)
    SentimentSkill(registry)
    
    # ━━ 2. Lista skills ━━
    console.print("\n[bold]1️⃣  Skills Registradas:[/]\n")
    
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Skill", style="cyan")
    table.add_column("Versão", style="green")
    table.add_column("Ativa", justify="center")
    table.add_column("Descrição", style="dim")
    
    for skill_info in registry.list_skills():
        table.add_row(
            skill_info["name"],
            skill_info["version"],
            "✅" if skill_info["active"] else " ",
            skill_info["description"],
        )
    
    console.print(table)
    
    # ━━ 3. Executa skill individual ━━
    console.print("\n[bold]2️⃣  Execução Individual — Classificação:[/]\n")
    
    classify_skill = registry.get("classify", "v1")
    result = await classify_skill.execute(
        text="URGENTE: Seu pacote precisa ser retirado!",
        categories=["spam", "not_spam", "urgent"],
    )
    
    console.print(f"  Texto: 'URGENTE: Seu pacote precisa ser retirado!'")
    console.print(f"  Categoria: [bold green]{result['category']}[/]")
    console.print(f"  Confiança: {result['confidence']:.2%}")
    
    # ━━ 4. Pipeline composto ━━
    console.print("\n[bold]3️⃣  Pipeline Composto:[/]\n")
    console.print("  [dim]Classificar → Analisar Sentimento → Resumir[/]\n")
    
    pipeline = PipelineCompositor(registry)
    pipeline.add_step("classify", params={"text": "Excelente produto! Super recomendo a todos!"})
    pipeline.add_step("sentiment", input_mapping={"category": "text"})
    pipeline.add_step("summarize", input_mapping={"sentiment": "text"})
    
    pipeline_results = await pipeline.execute({
        "text": "Excelente produto! Super recomendo a todos! Qualidade incrível e entrega rápida.",
    })
    
    final = pipeline_results["final_output"]
    console.print(f"\n  [dim]Resultado final:[/]")
    console.print(f"    Categoria: {final.get('category', 'N/A')}")
    console.print(f"    Sentimento: {final.get('sentiment', 'N/A')}")
    
    # ━━ 5. Estatísticas ━━
    stats = registry.get_stats()
    
    console.print("\n[bold cyan]📊 Estatísticas:[/]\n")
    
    stats_table = Table(show_header=True, header_style="bold cyan")
    stats_table.add_column("Métrica", style="cyan")
    stats_table.add_column("Valor", justify="right")
    
    stats_table.add_row("Total de skills", str(stats["total_skills"]))
    stats_table.add_row("Skills únicas", str(stats["unique_skills"]))
    stats_table.add_row("Total de execuções", str(stats["total_calls"]))
    
    console.print(stats_table)
    
    console.print("\n[dim]💡 Skills são LEGO blocks — monte o fluxo que precisa![/]")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
