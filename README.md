# 📖 AI Agents Course — Formação Prática em Agentes de IA com Python

Curso técnico seguindo **Aprendizagem Baseada em Problemas (PBL)**.
Toda teoria é apresentada sob demanda para destravar o código.

---

## 🗺️ Índice do Curso

### Fase 1: Fundamentos (P0–P1)

| # | Módulo | Conceito | Link | Miniprojeto |
|---|--------|----------|------|-------------|
| P0-F | Fundamentos | O que é IA e LLM? | [MATERIAL](modules/p0_fundamentals/MATERIAL.md) | — |
| P0 | Primeiro fluxo | Chamada HTTP a LLM | [MATERIAL](modules/p0_first_llm/MATERIAL.md) · [run.py](modules/p0_first_llm/run.py) | [Miniprojeto](modules/p0_first_llm/miniproject.md) |
| P1 | Viabilidade | Benchmark IA vs Regras | [MATERIAL](modules/p1_feasibility/MATERIAL.md) · [run.py](modules/p1_feasibility/run.py) | [Miniprojeto](modules/p1_feasibility/miniproject.md) |

### Fase 2: Contexto e Qualidade (P2–P3a-1)

| # | Módulo | Conceito | Link | Miniprojeto |
|---|--------|----------|------|-------------|
| P2 | RAG | Recuperação de Contexto | [MATERIAL](modules/p2_rag/MATERIAL.md) · [run.py](modules/p2_rag/run.py) | [Miniprojeto](modules/p2_rag/miniproject.md) |
| P3a-1 | Autoavaliação | Loop de crítica estruturada | [MATERIAL](modules/p3a1_self_eval/MATERIAL.md) · [run.py](modules/p3a1_self_eval/run.py) | [Miniprojeto](modules/p3a1_self_eval/miniproject.md) |

### Fase 3: Autonomia e Resiliência (P3a-2 → P3b)

| # | Módulo | Conceito | Link | Miniprojeto |
|---|--------|----------|------|-------------|
| P3a-2 | Tool Calling | Agente com funções reais + HITL | [MATERIAL](modules/p3a2_tool_calling/MATERIAL.md) · [run.py](modules/p3a2_tool_calling/run.py) | [Miniprojeto](modules/p3a2_tool_calling/miniproject.md) |
| P3a-3 | Planejamento | Circuit breaker + checkpoints | [MATERIAL](modules/p3a3_planning/MATERIAL.md) · [run.py](modules/p3a3_planning/run.py) | [Miniprojeto](modules/p3a3_planning/miniproject.md) |
| P3b | Multiagente | Supervisor + especialistas | [MATERIAL](modules/p3b_multi_agent/MATERIAL.md) · [run.py](modules/p3b_multi_agent/run.py) | [Miniprojeto](modules/p3b_multi_agent/miniproject.md) |

### Fase 4: Produção e Operações (P4–P11)

| # | Módulo | Conceito | Link | Miniprojeto |
|---|--------|----------|------|-------------|
| P4 | Produção | API FastAPI + Docker | [MATERIAL](modules/p4_production/MATERIAL.md) · [run.py](modules/p4_production/run.py) | [Miniprojeto](modules/p4_production/miniproject.md) |
| P5 | Avaliação | Golden dataset + AB testing | [MATERIAL](modules/p5_evaluation/MATERIAL.md) · [run.py](modules/p5_evaluation/run.py) | [Miniprojeto](modules/p5_evaluation/miniproject.md) |
| P6 | Segurança | Prompt injection + guardrails | [MATERIAL](modules/p6_safety/MATERIAL.md) · [run.py](modules/p6_safety/run.py) | [Miniprojeto](modules/p6_safety/miniproject.md) |
| P7 | Memória | Short/long-term memory | [MATERIAL](modules/p7_memory/MATERIAL.md) · [run.py](modules/p7_memory/run.py) | [Miniprojeto](modules/p7_memory/miniproject.md) |
| P8 | Streaming | SSE token-by-token | [MATERIAL](modules/p8_streaming/MATERIAL.md) · [run.py](modules/p8_streaming/run.py) | [Miniprojeto](modules/p8_streaming/miniproject.md) |
| P9 | Cache | Response cache + model routing | [MATERIAL](modules/p9_caching/MATERIAL.md) · [run.py](modules/p9_caching/run.py) | [Miniprojeto](modules/p9_caching/miniproject.md) |
| P10 | Skills | Skill registry + pipelines | [MATERIAL](modules/p10_skills/MATERIAL.md) · [run.py](modules/p10_skills/run.py) | [Miniprojeto](modules/p10_skills/miniproject.md) |
| P11 | Ops | CI/CD + monitoring + rollback | [MATERIAL](modules/p11_production_ops/MATERIAL.md) · [run.py](modules/p11_production_ops/run.py) | [Miniprojeto](modules/p11_production_ops/miniproject.md) |

---

## Princípios

- **Problema antes de ferramenta** — A tecnologia entra só quando se justifica
- **Evidência antes de opinião** — Escolhas arquiteturais exigem testes e medições reais
- **Simplicidade antes de complexidade** — Se um `if/else` resolve melhor que LLM, vence
- **Tópicos transversais obrigatórios**: Custo · Observabilidade · Segurança · Governança

## Pré-requisitos

- Python 3.11+
- Conta na OpenAI (ou compatível)
- Docker (módulo P4)

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"
cp .env.example .env       # Configure suas chaves
```

## Executar módulos

```bash
# Cada módulo tem seu script principal
python modules/p0_first_llm/run.py
python modules/p1_feasibility/run.py
python modules/p2_rag/run.py
# ... etc
```

## Estrutura do Projeto

```
ai-agents-course/
├── shared/                 # Utilitários compartilhados
│   ├── cost.py             # Estimativa de custos (tiktoken)
│   ├── logging_config.py   # Logs estruturados
│   ├── security.py         # Gestão de secrets (.env)
│   └── governance.py       # Human-in-the-loop
├── modules/                # Módulos do curso
│   ├── p0_fundamentals/    # Fundamentos (IA, LLM, tokens)
│   ├── p0_first_llm/       # Primeiro fluxo com LLM
│   ├── p1_feasibility/     # Análise de viabilidade
│   ├── p2_rag/             # Pipeline RAG
│   ├── p3a1_self_eval/     # Autoavaliação
│   ├── p3a2_tool_calling/  # Tool Calling
│   ├── p3a3_planning/      # Planejamento e retomada
│   ├── p3b_multi_agent/    # Multiagente
│   ├── p4_production/      # Deploy em produção
│   ├── p5_evaluation/      # Avaliação e testes
│   ├── p6_safety/          # Segurança e guardrails
│   ├── p7_memory/          # Memória e contexto
│   ├── p8_streaming/       # Streaming e tempo real
│   ├── p9_caching/         # Cache e otimização de custo
│   ├── p10_skills/         # Design de skills
│   └── p11_production_ops/ # Ops de produção (CI/CD + monitoring)
├── tests/                  # Testes por módulo
├── data/                   # Dados de exemplo
├── docs/                   # Documentação
└── docker-compose.yml      # Infraestrutura P4
```

## Avaliação

Cada módulo deve ser entregue como repositório GitHub com:

- Código funcional e testado
- Relatório de custos (tokens/gasto)
- Logs estruturados demonstrando observabilidade
- Comentários sobre trade-offs arquiteturais
