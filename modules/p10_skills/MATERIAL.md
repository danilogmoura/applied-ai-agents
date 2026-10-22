# Material Didático — P10: Design e Composição de Skills

## ⚠️ Pré-requisito

Leia antes:

- [p0_fundamentals/MATERIAL.md](../p0_fundamentals/MATERIAL.md) — Fundamentos de IA e LLM
- [p3a2_tool_calling/MATERIAL.md](../p3a2_tool_calling/MATERIAL.md) — Tool Calling
- [p3b_multi_agent/MATERIAL.md](../p3b_multi_agent/MATERIAL.md) — Multiagente

---

## 🎯 Objetivos de Aprendizagem

Ao final deste módulo, você será capaz de:

- [ ] **Definir** uma skill com interface clara (input/output schemas + descrição)
- [ ] **Implementar** versionamento SemVer para evoluir skills sem quebrar consumidores
- [ ] **Compor** pipelines encadeando múltiplas skills como LEGO blocks
- [ ] **Aplicar** filtros no pipeline (confiança mínima, rate limiting, conteúdo proibido)
- [ ] **Gerenciar** error handling em pipelines (fail-fast, fallback, partial success)

> 💡 **Dica:** Skills são o conceito que transforma código bagunçado em sistema modular. Cada skill faz UMA coisa bem — e isso parece simples até você ter 50 skills trabalhando juntas. Este módulo ensina a escalar.

---

## Conceitos Fundamentais

### O que é uma Skill?

Uma skill é uma função especializada com interface bem definida:

```python
class SentimentSkill(BaseSkill):
    def execute(self, input_data: dict) -> dict:
        # Input: {"text": "Produto excelente!"}
        # Output: {"sentiment": "positive", "confidence": 0.85}
```

Skills são como APIs internas — cada uma faz UMA coisa bem.

### Por que isso existe?

Em projetos pequenos, você pode colocar tudo em um arquivo. Mas conforme o sistema cresce:

```
prompts espalhados por 10 arquivos → difícil manter consistência
funções com nomes genéricos (process(), analyze()) → ninguém sabe o que fazem
sem versionamento → atualizar uma skill quebra outro módulo
```

Skills resolvem isso criando **módulos independentes** com contrato claro:

- Cada skill faz UMA coisa bem definida
- Input/output são schemas JSON explícitos
- Versionamento permite evoluir sem quebrar consumidores
- Pipeline composition encadeia skills como LEGO blocks

### Erros Comuns de Iniciantes

| Erro | Consequência | Correção |
| ------ | -------------- | ---------- |
| Skill com muitas responsabilidades | Difícil de testar, debugar, reusar | Uma skill = uma função específica |
| Schema de input/output vago | Pipeline quebra silenciosamente entre skills | JSON Schema rigoroso + validação |
| Não versionar | Atualização quebra pipelines existentes | SemVer: v1.x.x (feature), v2.0.0 (breaking) |
| Hardcode dependências entre skills | Pipeline não funciona se ordem mudar | Registry centralizado com lookup por nome |
| Ignorar erro na skill | Pipeline continua com dado corrompido | Lançar Exception clara + fallback no pipeline |

### Interface Padrão de uma Skill

Toda skill segue o mesmo contrato:

```python
class BaseSkill:
    name: str                    # Identificador único
    version: str                 # SemVer (1.0.0)
    description: str             # O que esta skill faz
    input_schema: dict           # JSON Schema do input esperado
    output_schema: dict          # JSON Schema do output garantido
    
    def execute(self, input_data: dict) -> dict:
        """Executa a skill. Lança Exception em caso de erro."""
        ...
    
    def validate_input(self, data: dict) -> bool:
        """Valida input antes da execução."""
        ...
```

**Por que schemas?** Porque skills trocam dados entre si. Se a skill A produz `{"sentiment": "positive"}` e a skill B espera `{"label": "pos"}`, o pipeline quebra. Schemas garantem compatibilidade.

### Versionamento Semântico

Cada skill pode ter múltiplas versões:

```mermaid
graph LR
    v1["v1.0.0"] --> v1_1["v1.1.0\nfeature adicionada"]
    v1_1 --> v2["v2.0.0\nbreaking change"]
```

O registry gerencia qual versão está ativa.

#### Por que versionar skills?

```mermaid
flowchart LR
    subgSem["❌ Sem versionamento"]
    subgCom["✅ Com versionamento"]
    
    S1["Pipeline usa SentimentSkill v1"] --> S2["Dev atualiza para v2"]
    S2 --> S3["Output muda: positive → pos"]
    S3 --> S4["Pipeline quebra silenciosamente"]
    
    C1["Pipeline usa SentimentSkill@v1"] --> C2["Dev cria SentimentSkill@v2"]
    C2 --> C3["Pipeline continua funcionando"]
    C3 --> C4["Migração gradual quando pronto"]
```

### Pipeline Composition

Encadeia skills como corrente de montagem:

```mermaid
flowchart LR
    Input["📥 Input"] --> Classificar["🏷️ Classificar\n'spam'"]
    Classificar --> Sentimento["❤️ Sentimento\n'positive'"]
    Sentimento --> Resumir["📝 Resumir\n'3 frases'"]
    Resumir --> Output["📤 Output"]
```

Cada step recebe o output do anterior.

#### Pattern de Pipeline

```python
class SkillPipeline:
    def __init__(self):
        self.steps = []
        self.filters = []
    
    def add_step(self, skill: BaseSkill):
        """Adiciona skill ao pipeline."""
        self.steps.append(skill)
    
    def add_filter(self, name: str, condition: callable):
        """Adiciona filtro que pode abortar o pipeline."""
        self.filters.append((name, condition))
    
    async def run(self, input_data: dict) -> dict:
        current = input_data
        
        # Aplica filtros antes de cada step
        for step in self.steps:
            for filter_name, condition in self.filters:
                if not condition(current):
                    return {
                        "error": f"Filtro '{filter_name}' falhou",
                        "input": current
                    }
            
            # Executa skill
            try:
                current = await step.execute(current)
            except Exception as e:
                return {
                    "error": f"Skill {step.name} falhou: {e}",
                    "input": current
                }
        
        return current
```

### Filtros no Pipeline

Filtros podem abortar o pipeline se condições não forem satisfeitas:

```python
pipeline.add_filter("qualidade", lambda data: data["confidence"] > 0.7)
```

Se confiança < 0.7, pipeline aborta.

#### Patterns Comuns de Filtro

| Filtro | Quando usar | Exemplo |
| -------- | ------------- | --------- |
| **Confiança mínima** | Antes de processar resultado incerto | `confidence > 0.7` |
| **Tipo de entrada** | Só processar certos tipos | `category == "spam"` |
| **Rate limiting** | Evitar sobrecarga | `calls_per_min < 60` |
| **Conteúdo proibido** | Bloquear inputs inadequados | `has_toxicity(input) == False` |
| **Timeout** | Abortar se demorar demais | `elapsed < 5s` |

### Error Handling em Pipelines

Quando uma skill falha, você tem 3 opções:

```
Opção 1: Fail-fast (padrão)
  [A] → [B] → [C]
  [A] OK → [B] FAIL → Retorna erro imediatamente
  → Melhor para: dados críticos onde erro não pode ser ignorado

Opção 2: Fallback (resiliência)
  [A] → [B] → [C]
  [A] OK → [B] FAIL → Usa resultado alternativo de B
  [Fallback] OK → [C] OK
  → Melhor para: serviços externos instáveis

Opção 3: Partial success (tolerância)
  [A] → [B] → [C]
  [A] OK → [B] FAIL → Continua com dados parciais
  [C] processa com o que tem
  → Melhor para: resultados aproximados são aceitáveis
```

### Registry de Skills

O registry é um dicionário que mapeia nomes para implementações:

```python
registry = SkillRegistry()

# Registro
registry.register(SentimentSkill())
registry.register(ClassificationSkill())
registry.register(SummarizationSkill())

# Lookup por nome (útil para config dinâmica)
skill = registry.get("sentiment", version="1.0.0")
result = await skill.execute({"text": "Excelente produto!"})
```

**Vantagens do registry:**

- Skills são plugáveis: adicione novas sem mudar código existente
- Testabilidade: substitua skill real por mock no teste
- Observabilidade: logue todas as chamadas via registry
- Feature flags: canary deploy nova versão sem quebrar pipeline

---

## Exercício Prático

Execute `python modules/p10_skills/run.py` e observe:

1. Como as skills são registradas no registry
2. Execução individual de cada skill
3. Pipeline encadeando múltiplas skills
4. Estatísticas de uso por skill

## Perguntas para Reflexão

1. Quando criar uma nova skill vs combinar existentes?
2. Se uma skill falha no meio do pipeline, como rollback?
3. Como testar pipelines sem chamar LLMs reais?

---

## 📌 Resumo do Módulo

Skills são blocos de construção reutilizáveis de agentes:

1. **Interface consistente** — toda skill tem input/output definido. Isso permite compor pipelines como LEGO: cada peça encaixa independentemente da implementação interna.

2. **Versionamento SemVer** — v1.0.0, v1.1.0, v2.0.0. Mudanças breaking exigem novo major. Sem versionamento, update quebra tudo.

3. **Pipeline = composição** — [A] → [B] → [C]. Cada etapa processa output da anterior. Filtros podem abortar se condições não forem satisfeitas (confiança baixa, toxicity, timeout).

4. **Error handling** — fail-fast (padrão), retry (transiente), fallback (degradar). Escolher estratégia depende do custo de falha.

5. **Registry centralizado** — todas as skills registradas em um lugar. Novas skills descobertas automaticamente. Desacoplamento entre definição e uso.

> ✅ **Você está pronto para:** Agora que skills estão organizadas, vamos colocar tudo em produção com CI/CD.

---

## 🔗 Próximos Passos

Com skills versionadas e pipelines compostos, seu sistema está organizado. Mas como fazer deploy automático com monitoramento e rollback?

→ Leia o módulo [P11: Production Ops](../p11_production_ops/MATERIAL.md) para aprender CI/CD, monitoring e métricas.

---

## Referências

### Livros

- **"Designing Machine Learning Systems"** by Chip Huyen — Capítulos sobre modular agent architecture
- **"Domain-Driven Design"** by Eric Evans — Bounded contexts como skills

### Documentação Oficial

- [LangChain Tools](https://python.langchain.com/docs/modules/agents/tools/) — LangChain Docs
- [Semantic Versioning](https://semver.org/) — SemVer Spec

### Tutoriais

- [LangGraph Pipelines](https://langchain-ai.github.io/langgraph/) — LangGraph Docs
- [Skill Design Patterns](https://github.com/langchain-ai/langchain/tree/master/templates) — LangChain Templates
