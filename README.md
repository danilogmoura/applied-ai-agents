# AI Agents Course — Formação Prática em Agentes de IA com Python

Curso técnico seguindo **Aprendizagem Baseada em Problemas (PBL)**.
Toda teoria é apresentada sob demanda para destravar o código.

## Princípios

- **Problema antes de ferramenta** — A tecnologia entra só quando se justifica
- **Evidência antes de opinião** — Escolhas arquiteturais exigem testes e medições reais
- **Simplicidade antes de complexidade** — Se um `if/else` resolve melhor que LLM, vence
- **Tópicos transversais obrigatórios**: Custo · Observabilidade · Segurança · Governança

## Trilha de Desafios

| Módulo | Nome | Duração Estimada | Entregável |
| -------- | ------ | ------------------- | ------------ |
| **P0-F** | Fundamentos (IA + LLM) | 1h | **Obrigatório antes de começar** |
| **P0** | Primeiro fluxo com LLM | 2h | Botão autônomo com custo visível |
| **P1** | Análise de viabilidade | 1.5h | Memorando técnico comparativo |
| **P2** | RAG (Recuperação de Contexto) | 3h | Pipeline completo com ChromaDB |
| **P3a-1** | Autoavaliação e reflexão | 2.5h | Loop de crítica estruturada |
| **P3a-2** | Tool Calling | 3h | Agente com funções reais + HITL |
| **P3a-3** | Planejamento e retomada | 2.5h | Circuit breaker + checkpoints |
| **P3b** | Sistema multiagente | 4h | Supervisor + especialistas |
| **P4** | Produto em produção | 3h | API FastAPI + Docker + Swagger |
| **P5** | Avaliação e testes | 2.5h | Golden dataset + AB testing |
| **P6** | Segurança e guardrails | 2.5h | Prompt injection + content filter |
| **P7** | Memória e contexto | 3h | Short/long-term memory + summarization |
| **P8** | Streaming e tempo real | 2h | SSE token-by-token + abort |
| **P9** | Cache e otimização de custo | 2.5h | Response cache + model routing |
| **P10** | Design de skills | 3h | Skill registry + pipelines composáveis |
| **P11** | Ops de produção | 3h | Prompt testing A/B + métricas + rollback |

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
