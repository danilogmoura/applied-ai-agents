# 📖 AI Agents Course — Formação Prática em Agentes de IA com Python

Um curso técnico construído sobre **Aprendizagem Baseada em Problemas (PBL)**: cada módulo começa com um problema real e apresenta a teoria apenas quando ela é necessária para destravar o código. Leia como um livro — do capítulo 1 ao 16 — ou salte direto ao tema que você precisa.

---

## Introdução

**Para quem é.** Programadores iniciantes que querem entender — e construir — agentes de IA com Python, sem precisar de um doutorado em machine learning. Se você sabe usar um computador e escrever algumas linhas de código, este curso foi feito para você.

**Como está organizado.** Os 16 capítulos seguem uma progressão deliberada em quatro arcos:

- **Fundamentos (P0-F → P1):** o que é IA/LLM, tokens, custo e como decidir se um problema merece IA.
- **Contexto e Qualidade (P2 → P3a-1):** dar conhecimento ao modelo (RAG) e fazê-lo avaliar o próprio trabalho.
- **Autonomia e Resiliência (P3a-2 → P3b):** agentes que usam ferramentas, planejam tarefas multi-etapas e sobrevivem a falhas — inclusive trabalhando em equipe.
- **Produção e Operações (P4 → P11):** tirar do script local e levar para o mundo real: API, avaliação, segurança, memória, streaming, cache, skills reutilizáveis e operações contínuas.

**Como usar cada capítulo.** Em cada módulo você tem três artefatos que conversam entre si:

1. `MATERIAL.md` — o capítulo (conceito + teoria sob demanda);
2. `run.py` — o código executável que demonstra o conceito;
3. `miniproject.md` — o mini-projeto integrador, onde você aplica o que aprendeu.

Siga a ordem dos capítulos usando a navegação **← Anterior · Índice · Próximo →** no fim de cada material.

**Pré-requisitos.** Python 3.11+, uma conta na OpenAI (ou compatível) e Docker (necessário só a partir de P4).

---

## Sumário

### Fase 1 — Fundamentos

1. [P0-F: Fundamentos — O que é IA e LLM?](modules/p0_fundamentals/MATERIAL.md) — IA, LLMs, tokenização e prompt engineering.
   ↳ [`run.py`](modules/p0_fundamentals/run.py)
2. [P0: Primeiro Fluxo com LLM](modules/p0_first_llm/MATERIAL.md) — sua primeira chamada HTTP a um modelo.
   ↳ [`run.py`](modules/p0_first_llm/run.py) · [Miniprojeto](modules/p0_first_llm/miniproject.md)
3. [P1: Análise de Viabilidade](modules/p1_feasibility/MATERIAL.md) — benchmark IA vs. regras; quando IA vale a pena.
   ↳ [`run.py`](modules/p1_feasibility/run.py) · [Miniprojeto](modules/p1_feasibility/miniproject.md)

### Fase 2 — Contexto e Qualidade

4. [P2: Pipeline RAG](modules/p2_rag/MATERIAL.md) — recuperação de contexto para dar conhecimento interno ao LLM.
   ↳ [`run.py`](modules/p2_rag/run.py) · [Miniprojeto](modules/p2_rag/miniproject.md)
5. [P3a-1: Autoavaliação e Reflexão](modules/p3a1_self_eval/MATERIAL.md) — loop de crítica estruturada.
   ↳ [`run.py`](modules/p3a1_self_eval/run.py) · [Miniprojeto](modules/p3a1_self_eval/miniproject.md)

### Fase 3 — Autonomia e Resiliência

6. [P3a-2: Tool Calling](modules/p3a2_tool_calling/MATERIAL.md) — agente com funções reais + human-in-the-loop.
   ↳ [`run.py`](modules/p3a2_tool_calling/run.py) · [Miniprojeto](modules/p3a2_tool_calling/miniproject.md)
7. [P3a-3: Planejamento e Retomada](modules/p3a3_planning/MATERIAL.md) — circuit breaker, checkpoints e retry.
   ↳ [`run.py`](modules/p3a3_planning/run.py) · [Miniprojeto](modules/p3a3_planning/miniproject.md)
8. [P3b: Sistema Multiagente](modules/p3b_multi_agent/MATERIAL.md) — supervisor + especialistas cooperando.
   ↳ [`run.py`](modules/p3b_multi_agent/run.py) · [Miniprojeto](modules/p3b_multi_agent/miniproject.md)

### Fase 4 — Produção e Operações

9. [P4: Produção (API REST com FastAPI)](modules/p4_production/MATERIAL.md) — do script local ao serviço com Docker.
   ↳ [`run.py`](modules/p4_production/run.py) · [Miniprojeto](modules/p4_production/miniproject.md)
10. [P5: Avaliação e Testes](modules/p5_evaluation/MATERIAL.md) — golden dataset + A/B testing.
    ↳ [`run.py`](modules/p5_evaluation/run.py) · [Miniprojeto](modules/p5_evaluation/miniproject.md)
11. [P6: Segurança e Guardrails](modules/p6_safety/MATERIAL.md) — prompt injection e defesas.
    ↳ [`run.py`](modules/p6_safety/run.py) · [Miniprojeto](modules/p6_safety/miniproject.md)
12. [P7: Memória e Contexto](modules/p7_memory/MATERIAL.md) — short/long-term memory.
    ↳ [`run.py`](modules/p7_memory/run.py) · [Miniprojeto](modules/p7_memory/miniproject.md)
13. [P8: Streaming e Tempo Real](modules/p8_streaming/MATERIAL.md) — SSE token-by-token.
    ↳ [`run.py`](modules/p8_streaming/run.py) · [Miniprojeto](modules/p8_streaming/miniproject.md)
14. [P9: Cache e Otimização de Custo](modules/p9_caching/MATERIAL.md) — response cache + model routing.
    ↳ [`run.py`](modules/p9_caching/run.py) · [Miniprojeto](modules/p9_caching/miniproject.md)
15. [P10: Design e Composição de Skills](modules/p10_skills/MATERIAL.md) — skill registry + pipelines.
    ↳ [`run.py`](modules/p10_skills/run.py) · [Miniprojeto](modules/p10_skills/miniproject.md)
16. [P11: Operations de Produção](modules/p11_production_ops/MATERIAL.md) — CI/CD, monitoramento e rollback.
    ↳ [`run.py`](modules/p11_production_ops/run.py) · [Miniprojeto](modules/p11_production_ops/miniproject.md)

---

## Princípios

- **Problema antes de ferramenta** — a tecnologia entra só quando se justifica.
- **Evidência antes de opinião** — escolhas arquiteturais exigem testes e medições reais.
- **Simplicidade antes de complexidade** — se um `if/else` resolve melhor que LLM, vence.
- **Tópicos transversais obrigatórios**: Custo · Observabilidade · Segurança · Governança.

---

## Apêndice — Setup

### Pré-requisitos

- Python 3.11+
- Conta na OpenAI (ou compatível)
- Docker (módulo P4)

### Instalação

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -e ".[dev]"
cp .env.example .env       # Configure suas chaves
```

### Executar módulos

```bash
# Cada módulo tem seu script principal
python modules/p0_first_llm/run.py
python modules/p1_feasibility/run.py
python modules/p2_rag/run.py
# ... etc
```

### Estrutura do Projeto

```
ai-agents-course/
├── shared/                 # Utilitários compartilhados
│   ├── cost.py             # Estimativa de custos (tiktoken)
│   ├── logging_config.py   # Logs estruturados
│   ├── security.py         # Gestão de secrets (.env)
│   └── governance.py       # Human-in-the-loop
├── modules/                # Módulos do curso (capítulos)
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

### Avaliação

Cada módulo deve ser entregue como repositório GitHub com:

- Código funcional e testado
- Relatório de custos (tokens/gasto)
- Logs estruturados demonstrando observabilidade
- Comentários sobre trade-offs arquiteturais
