# Documentação do Curso — AI Agents Course

## Visão Geral

Este curso prático ensina a construir **agentes de inteligência artificial** usando exclusivamente Python, seguindo a metodologia de **Aprendizagem Baseada em Problemas (PBL)**.

## Arquitetura do Projeto

```
ai-agents-course/
├── shared/                          # Utilitários compartilhados
│   ├── __init__.py                  # Exportações públicas
│   ├── cost.py                      # Estimativa de custos (tiktoken)
│   ├── logging_config.py            # Logs estruturados JSON
│   ├── security.py                  # Gestão de secrets (.env)
│   └── governance.py                # Human-in-the-loop (HITL)
│
├── modules/                         # Módulos do curso (8 desafios)
│   ├── p0_first_llm/                # P0: Primeiro fluxo com LLM
│   │   └── run.py                   # Script principal
│   │
│   ├── p1_feasibility/              # P1: Análise de viabilidade
│   │   ├── run.py                   # Benchmark IA vs Regras
│   │   └── memorando.md             # Memorando gerado
│   │
│   ├── p2_rag/                      # P2: Pipeline RAG
│   │   ├── run.py                   # Ingestão + busca + geração
│   │   └── checkpoint.json          # Estado salvo
│   │
│   ├── p3a1_self_eval/              # P3a-1: Autoavaliação
│   │   └── run.py                   # Loop Pydantic + LLM
│   │
│   ├── p3a2_tool_calling/           # P3a-2: Tool Calling
│   │   └── run.py                   # Agente com ferramentas reais
│   │
│   ├── p3a3_planning/               # P3a-3: Planejamento
│   │   ├── run.py                   # Circuit breaker + checkpoints
│   │   └── checkpoint.json          # Snapshot de estado
│   │
│   ├── p3b_multi_agent/             # P3b: Multiagente
│   │   └── run.py                   # Supervisor + especialistas
│   │
│   └── p4_production/               # P4: Produção
│       ├── app/                     # Código FastAPI
│       │   ├── main.py              # App FastAPI + endpoints
│       │   ├── models.py            # Modelos Pydantic
│       │   ├── services/            # Serviços de negócio
│       │   │   └── agent_service.py # Serviço central
│       │   └── middleware/          # Middleware
│       │       └── monitoring.py    # Métricas e latência
│       └── run.py                   # Execução da API
│
│   ├── p5_evaluation/              # P5: Avaliação e testes
│   │   ├── run.py                   # Golden dataset + AB testing
│   │   └── MATERIAL.md              # Material didático
│   │
│   ├── p6_safety/                  # P6: Segurança e guardrails
│   │   ├── run.py                   # Prompt injection + content filter
│   │   └── MATERIAL.md              # Material didático
│   │
│   ├── p7_memory/                  # P7: Memória e contexto
│   │   ├── run.py                   # Short/long-term memory
│   │   └── MATERIAL.md              # Material didático
│   │
│   ├── p8_streaming/               # P8: Streaming e tempo real
│   │   ├── run.py                   # SSE token-by-token
│   │   └── MATERIAL.md              # Material didático
│   │
│   ├── p9_caching/                 # P9: Cache e otimização
│   │   ├── run.py                   # Response cache + model routing
│   │   └── MATERIAL.md              # Material didático
│   │
│   ├── p10_skills/                 # P10: Design de skills
│   │   ├── run.py                   # Skill registry + pipelines
│   │   └── MATERIAL.md              # Material didático
│   │
│   └── p11_production_ops/         # P11: Ops de produção
│       ├── run.py                   # Prompt testing A/B + métricas
│       └── MATERIAL.md              # Material didático
│
├── tests/                           # Testes unitários
│   └── test_shared.py               # Testes dos utilitários
│
├── data/                            # Dados de exemplo
│   ├── README.md                    # Instruções
│   └── sample_docs.json             # Documentos para RAG
│
├── docs/                            # Documentação adicional
│   ├── curriculum.md                # Currículo detalhado
│   ├── architecture.md              # Decisões arquiteturais
│   └── benchmarks.md                # Resultados de benchmarks
│
├── .env.example                     # Template de variáveis de ambiente
├── .gitignore                       # Arquivos ignorados pelo Git
├── docker-compose.yml               # Infraestrutura Docker
├── Dockerfile                       # Imagem de produção
├── pyproject.toml                   # Configuração Python (deps, ruff, mypy)
└── README.md                        # Este arquivo
```

## Fluxo de Aprendizado

### Fase 1: Fundamentos (P0–P1)

| Módulo | Conceito | Ferramentas | Entregável |
|--------|----------|-------------|------------|
| **P0** | Chamada HTTP a LLM | OpenAI SDK, try/except | Botão autônomo |
| **P1** | Comparação IA vs Regras | Benchmarks, latência | Memorando técnico |

### Fase 2: Contexto e Qualidade (P2–P3a-1)

| Módulo | Conceito | Ferramentas | Entregável |
|--------|----------|-------------|------------|
| **P2** | Recuperação de contexto | ChromaDB, embeddings | Pipeline RAG |
| **P3a-1** | Autoavaliação | Pydantic, structured output | Loop de crítica |

### Fase 3: Autonomia e Resiliência (P3a-2 → P3b)

| Módulo | Conceito | Ferramentas | Entregável |
| -------- | ---------- | ------------- | ------------ |
| **P3a-2** | Tool calling | Funções Python, HITL | Agente autônomo |
| **P3a-3** | Circuit breakers | State machine, JSON | Sistema resiliente |
| **P3b** | Multiagente | Router pattern | Equipe de agentes |

### Fase 4: Produção (P4)

| Módulo | Conceito | Ferramentas | Entregável |
|--------|----------|-------------|------------|
| **P4** | API REST | FastAPI, Docker, Swagger | Produto deployável |

### Fase 5: Maturidade de Produção (P5–P11)

| Módulo | Conceito | Ferramentas | Entregável |
| -------- | ---------- | ------------- | ------------ |
| **P5** | Avaliação e testes | Pydantic, golden dataset | Relatório AB testing |
| **P6** | Segurança e guardrails | Regex patterns, output validator | Sistema de filtros |
| **P7** | Memória e contexto | Short/long-term memory | Agente com memória |
| **P8** | Streaming e tempo real | Async generators, SSE | Resposta token-by-token |
| **P9** | Cache e otimização | Response cache, model routing | Redução de custos |
| **P10** | Design de skills | Skill registry, pipelines | Workflow composável |
| **P11** | Ops de produção | Prompt testing A/B, métricas | Dashboard + rollback |

## Tópicos Transversais

Cada módulo implementa obrigatoriamente:

### 1. Custo (`shared/cost.py`)

- Contagem de tokens via `tiktoken`
- Estimativa de custo por chamada
- Relatório acumulado por módulo

### 2. Observabilidade (`shared/logging_config.py`)

- Logs estruturados em JSON
- Medição de latência com context managers
- Rastreamento de tokens e custos

### 3. Segurança (`shared/security.py`)

- Chaves carregadas de `.env` (python-dotenv)
- Validação de secrets obrigatórias
- Mascaramento de secrets em logs

### 4. Governança (`shared/governance.py`)

- Human-in-the-loop para ações críticas
- Níveis de risco (LOW → CRITICAL)
- Auditoria de decisões do agente

## Como Executar

### Instalação

```bash
# Cria ambiente virtual
python -m venv .venv
source .venv/bin/activate

# Instala dependências
pip install -e ".[dev]"

# Configura chaves de API
cp .env.example .env
# Edite .env com suas chaves
```

### Executar Módulos

```bash
# P0 — Primeiro fluxo com LLM
python modules/p0_first_llm/run.py

# P1 — Análise de viabilidade
python modules/p1_feasibility/run.py

# P2 — Pipeline RAG
python modules/p2_rag/run.py

# P3a-1 — Autoavaliação
python modules/p3a1_self_eval/run.py

# P3a-2 — Tool Calling
python modules/p3a2_tool_calling/run.py

# P3a-3 — Planejamento
python modules/p3a3_planning/run.py

# P3b — Multiagente
python modules/p3b_multi_agent/run.py

# P4 — API de produção
python modules/p4_production/run.py --serve

# P5 — Avaliação e testes
python modules/p5_evaluation/run.py

# P6 — Segurança e guardrails
python modules/p6_safety/run.py

# P7 — Memória e contexto
python modules/p7_memory/run.py

# P8 — Streaming e tempo real
python modules/p8_streaming/run.py

# P9 — Cache e otimização
python modules/p9_caching/run.py

# P10 — Design de skills
python modules/p10_skills/run.py

# P11 — Ops de produção
python modules/p11_production_ops/run.py
```

### Executar Testes

```bash
pytest tests/ -v
```

### Deploy com Docker

```bash
docker-compose up --build
# API disponível em http://localhost:8000
# Docs Swagger em http://localhost:8000/docs
```

## Critérios de Avaliação

Cada módulo deve ser entregue com:

1. ✅ **Código funcional** — Executa sem erros
2. ✅ **Relatório de custos** — Tokens e gasto estimado
3. ✅ **Logs estruturados** — Observabilidade demonstrada
4. ✅ **Segurança** - Secrets protegidas
5. ✅ **Trade-offs documentados** - Por que escolheu X sobre Y

## Próximos Passos

Todos os 12 módulos (P0-P11) estão completos. Para continuar evoluindo o curso:

1. **Adicionar testes unitários** para cada módulo P5-P11
2. **Criar notebooks Jupyter** para demonstrações interativas
3. **Integrar com LLMs reais** (substituir simulações por chamadas API)
4. **Adicionar mais skills** ao registry do P10
5. **Implementar Redis real** para cache do P9
6. **Criar dashboard Grafana** conectado às métricas do P11
7. **Adicionar mais idiomas** ao tradutor do P10

Após completar os 8 módulos:

- [ ] Adicionar testes integration para cada módulo
- [ ] Implementar caching de respostas (Redis)
- [ ] Adicionar rate limiting na API
- [ ] Criar dashboard de métricas (Grafana)
- [ ] Implementar A/B testing de modelos
- [ ] Adicionar fine-tuning customizado
