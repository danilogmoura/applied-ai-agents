# 📖 AI Agents Course — Formação Prática em Agentes de IA com Python

Um curso técnico construído sobre **Aprendizagem Baseada em Problemas (PBL)**: cada módulo começa com um problema real e apresenta a teoria apenas quando ela é necessária para destravar o código. Leia como um livro — do capítulo 1 ao 16 — ou salte direto ao tema que você precisa.

---

## Introdução

**Para quem é.** Programadores iniciantes que querem entender — e construir — agentes de IA com Python, sem precisar de um doutorado em machine learning. Se você sabe usar um computador e escrever algumas linhas de código, este curso foi feito para você.

**Como está organizado.** Os 16 capítulos seguem uma progressão deliberada em quatro arcos:

- **Fundamentos (Capítulos 01–03):** o que é IA/LLM, tokens, custo e como decidir se um problema merece IA.
- **Contexto e Qualidade (Capítulos 04–05):** dar conhecimento ao modelo (RAG) e fazê-lo avaliar o próprio trabalho.
- **Autonomia e Resiliência (Capítulos 06–08):** agentes que usam ferramentas, planejam tarefas multi-etapas e sobrevivem a falhas — inclusive trabalhando em equipe.
- **Produção e Operações (Capítulos 09–16):** tirar do script local e levar para o mundo real: API, avaliação, segurança, memória, streaming, cache, skills reutilizáveis e operações contínuas.

**Como usar cada capítulo.** Em cada módulo você tem três artefatos que conversam entre si:

1. `MATERIAL.md` — o capítulo (conceito + teoria sob demanda);
2. `run.py` — o código executável que demonstra o conceito;
3. `miniproject.md` — o mini-projeto integrador, onde você aplica o que aprendeu.

Siga a ordem dos capítulos usando a navegação **← Anterior · Índice · Próximo →** no fim de cada material.

**Pré-requisitos.** Python 3.11+, uma conta na OpenAI (ou compatível) e Docker (necessário só a partir do Capítulo 09).

---

## Sumário

### Fase 1 — Fundamentos

1. [Capítulo 01 — Fundamentos: O que é IA e LLM?](modules/01-fundamentos/MATERIAL.md) — IA, LLMs, tokenização e prompt engineering.
   ↳ [`run.py`](modules/01-fundamentos/run.py)
2. [Capítulo 02 — Primeiro Fluxo com LLM](modules/02-primeiro-llm/MATERIAL.md) — sua primeira chamada HTTP a um modelo.
   ↳ [`run.py`](modules/02-primeiro-llm/run.py) · [Miniprojeto](modules/02-primeiro-llm/miniproject.md)
3. [Capítulo 03 — Análise de Viabilidade](modules/03-viabilidade/MATERIAL.md) — benchmark IA vs. regras; quando IA vale a pena.
   ↳ [`run.py`](modules/03-viabilidade/run.py) · [Miniprojeto](modules/03-viabilidade/miniproject.md)

### Fase 2 — Contexto e Qualidade

1. [Capítulo 04 — Pipeline RAG](modules/04-rag/MATERIAL.md) — recuperação de contexto para dar conhecimento interno ao LLM.
   ↳ [`run.py`](modules/04-rag/run.py) · [Miniprojeto](modules/04-rag/miniproject.md)
2. [Capítulo 05 — Autoavaliação e Reflexão](modules/05-autoavaliacao/MATERIAL.md) — loop de crítica estruturada.
   ↳ [`run.py`](modules/05-autoavaliacao/run.py) · [Miniprojeto](modules/05-autoavaliacao/miniproject.md)

### Fase 3 — Autonomia e Resiliência

1. [Capítulo 06 — Tool Calling](modules/06-tool-calling/MATERIAL.md) — agente com funções reais + human-in-the-loop.
   ↳ [`run.py`](modules/06-tool-calling/run.py) · [Miniprojeto](modules/06-tool-calling/miniproject.md)
2. [Capítulo 07 — Planejamento e Retomada](modules/07-planejamento/MATERIAL.md) — circuit breaker, checkpoints e retry.
   ↳ [`run.py`](modules/07-planejamento/run.py) · [Miniprojeto](modules/07-planejamento/miniproject.md)
3. [Capítulo 08 — Sistema Multiagente](modules/08-multiagente/MATERIAL.md) — supervisor + especialistas cooperando.
   ↳ [`run.py`](modules/08-multiagente/run.py) · [Miniprojeto](modules/08-multiagente/miniproject.md)

### Fase 4 — Produção e Operações

1. [Capítulo 09 — Produção (API REST com FastAPI)](modules/09-producao-api/MATERIAL.md) — do script local ao serviço com Docker.
   ↳ [`run.py`](modules/09-producao-api/run.py) · [Miniprojeto](modules/09-producao-api/miniproject.md)
2. [Capítulo 10 — Avaliação e Testes](modules/10-avaliacao/MATERIAL.md) — golden dataset + A/B testing.
    ↳ [`run.py`](modules/10-avaliacao/run.py) · [Miniprojeto](modules/10-avaliacao/miniproject.md)
3. [Capítulo 11 — Segurança e Guardrails](modules/11-seguranca/MATERIAL.md) — prompt injection e defesas.
    ↳ [`run.py`](modules/11-seguranca/run.py) · [Miniprojeto](modules/11-seguranca/miniproject.md)
4. [Capítulo 12 — Memória e Contexto](modules/12-memoria/MATERIAL.md) — short/long-term memory.
    ↳ [`run.py`](modules/12-memoria/run.py) · [Miniprojeto](modules/12-memoria/miniproject.md)
5. [Capítulo 13 — Streaming e Tempo Real](modules/13-streaming/MATERIAL.md) — SSE token-by-token.
    ↳ [`run.py`](modules/13-streaming/run.py) · [Miniprojeto](modules/13-streaming/miniproject.md)
6. [Capítulo 14 — Cache e Otimização de Custo](modules/14-cache/MATERIAL.md) — response cache + model routing.
    ↳ [`run.py`](modules/14-cache/run.py) · [Miniprojeto](modules/14-cache/miniproject.md)
7. [Capítulo 15 — Design e Composição de Skills](modules/15-skills/MATERIAL.md) — skill registry + pipelines.
    ↳ [`run.py`](modules/15-skills/run.py) · [Miniprojeto](modules/15-skills/miniproject.md)
8. [Capítulo 16 — Operations de Produção](modules/16-operacoes/MATERIAL.md) — CI/CD, monitoramento e rollback.
    ↳ [`run.py`](modules/16-operacoes/run.py) · [Miniprojeto](modules/16-operacoes/miniproject.md)

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
- Docker (Capítulo 09)

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
python modules/02-primeiro-llm/run.py
python modules/03-viabilidade/run.py
python modules/04-rag/run.py
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
│   ├── 01-fundamentos/    # Fundamentos (IA, LLM, tokens)
│   ├── 02-primeiro-llm/       # Primeiro fluxo com LLM
│   ├── 03-viabilidade/     # Análise de viabilidade
│   ├── 04-rag/             # Pipeline RAG
│   ├── 05-autoavaliacao/     # Autoavaliação
│   ├── 06-tool-calling/  # Tool Calling
│   ├── 07-planejamento/      # Planejamento e retomada
│   ├── 08-multiagente/    # Multiagente
│   ├── 09-producao-api/      # Deploy em produção
│   ├── 10-avaliacao/      # Avaliação e testes
│   ├── 11-seguranca/          # Segurança e guardrails
│   ├── 12-memoria/          # Memória e contexto
│   ├── 13-streaming/       # Streaming e tempo real
│   ├── 14-cache/         # Cache e otimização de custo
│   ├── 15-skills/         # Design de skills
│   └── 16-operacoes/ # Ops de produção (CI/CD + monitoring)
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
