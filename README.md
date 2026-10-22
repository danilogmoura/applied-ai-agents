# AI Agents Course — Formação Prática em Agentes de IA com Python

Curso técnico para desenvolvedores juniores seguindo **Aprendizagem Baseada em Problemas (PBL)**.
Toda teoria é apresentada sob demanda para destravar o código.

## Princípios

- **Problema antes de ferramenta** — A tecnologia entra só quando se justifica
- **Evidência antes de opinião** — Escolhas arquiteturais exigem testes e medições reais
- **Simplicidade antes de complexidade** — Se um `if/else` resolve melhor que LLM, vence
- **Tópicos transversais obrigatórios**: Custo · Observabilidade · Segurança · Governança

## Trilha de Desafios

| Módulo | Nome | Duração Estimada | Entregável |
| -------- | ------ | ------------------- | ------------ |
| **P0** | Primeiro fluxo com LLM | 2h | Botão autônomo com custo visível |
| **P1** | Análise de viabilidade | 1.5h | Memorando técnico comparativo |
| **P2** | RAG (Recuperação de Contexto) | 3h | Pipeline completo com ChromaDB |
| **P3a-1** | Autoavaliação e reflexão | 2.5h | Loop de crítica estruturada |
| **P3a-2** | Tool Calling | 3h | Agente com funções reais + HITL |
| **P3a-3** | Planejamento e retomada | 2.5h | Circuit breaker + checkpoints |
| **P3b** | Sistema multiagente | 4h | Supervisor + especialistas |
| **P4** | Produto em produção | 3h | API FastAPI + Docker + Swagger |

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
│   ├── p0_first_llm/       # Automação com LLM
│   ├── p1_feasibility/     # Análise de viabilidade
│   ├── p2_rag/             # Pipeline RAG
│   ├── p3a1_self_eval/     # Autoavaliação
│   ├── p3a2_tool_calling/  # Tool Calling
│   ├── p3a3_planning/      # Planejamento e retomada
│   ├── p3b_multi_agent/    # Multiagente
│   └── p4_production/      # Deploy em produção
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
