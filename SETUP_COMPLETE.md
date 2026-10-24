# ⚙️ Setup Completo — Guia Unificado

Siga estes passos **uma única vez** antes de começar qualquer módulo do curso.

---

## 1. Pré-requisitos

| Item | Versão mínima | Como verificar |
| ------ | --------------- | ---------------- |
| Python | 3.11+ | `python --version` |
| pip | incluído no Python | `pip --version` |
| git | qualquer | `git --version` |
| Docker | P4 em diante | `docker --version` |

> ⚠️ Se `python --version` mostrar < 3.11, atualize o Python antes de continuar.

### Instalar Python

- **Linux/WSL:** `sudo apt install python3 python3-pip python3-venv`
- **macOS:** `brew install python`
- **Windows:** Baixe em [python.org](https://www.python.org/downloads/)

---

## 2. Clonar o repositório

```bash
git clone https://github.com/SEU-USUARIO/applied-ai-agents.git
cd applied-ai-agents
```

---

## 3. Criar ambiente virtual (virtualenv)

Sempre use um ambiente isolado para evitar conflitos com pacotes do sistema:

```bash
# Criar o ambiente na pasta .venv/
python -m venv .venv

# Ativar o ambiente
source .venv/bin/activate        # Linux / Mac
# ou
.venv\Scripts\activate           # Windows (CMD)
# ou
.venv\Scripts\Activate.ps1       # Windows (PowerShell)
```

> 💡 Quando o ambiente estiver ativo, seu terminal mostrará `(.venv)` no início da linha.

**Desativar** quando terminar:

```bash
deactivate
```

---

## 4. Instalar dependências do projeto

O arquivo `pyproject.toml` define todas as dependências. Instale com:

```bash
pip install -e ".[dev]"
```

Isso instala:

| Grupo | O que inclui |
|-------|--------------|
| **Principal** | `openai`, `anthropic`, `langgraph`, `langchain`, `chromadb`, `tiktoken`, `fastapi`, `uvicorn`, `docker`, etc. |
| **Dev** | `pytest`, `black`, `pytest-cov`, `responses` |

> ✅ Verifique se tudo instalou corretamente:
>
> ```bash
> python -c "import openai, langgraph, chromadb; print('✅ Tudo OK')"
> ```

---

## 5. Configurar chaves de API

### 5.1 Copiar o modelo `.env`

```bash
cp .env.example .env
```

### 5.2 Editar o `.env`

Abra o arquivo `.env` e substitua os valores placeholder pelas suas chaves reais:

```ini
# Obrigatório — OpenAI
OPENAI_API_KEY=sk-proj-sua-chave-real-aqui

# Opcional — Anthropic (para comparação entre modelos)
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui

# Modelo padrão (gpt-4o-mini é mais barato para exercícios)
DEFAULT_MODEL=gpt-4o-mini

# Embedding model usado pelo RAG (P2)
EMBEDDING_MODEL=text-embedding-3-small

# Base URL para providers compatíveis com OpenAI (ex: Groq, Together AI)
OPENAI_BASE_URL=https://api.openai.com/v1
```

> ⚠️ **NUNCA compartilhe seu arquivo `.env` publicamente.**  
> Ele já está no `.gitignore` por padrão — verifique com `git status` que ele não aparece como arquivo rastreado.

### 5.3 Obter chaves

| Provider | Onde obter |
|----------|------------|
| **OpenAI** | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| **Anthropic** | [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys) |

> 💰 A OpenAI cobra por uso. Para os exercícios deste curso, `gpt-4o-mini` custa ~$0.15 por 1M tokens de entrada. Use esse modelo nos exercícios para minimizar custos.

---

## 6. Estrutura de pastas relevante

```
applied-ai-agents/
├── .env                    ← Suas chaves (NÃO commitar)
├── .env.example            ← Modelo (commitar)
├── pyproject.toml          ← Dependências
├── shared/                 ← Utilitários compartilhados por todos os módulos
│   ├── cost.py             # Estimativa de custos em tokens
│   ├── logging_config.py   # Logs estruturados
│   ├── security.py         # Leitura segura de secrets
│   └── governance.py       # Human-in-the-loop
├── modules/                ← Cada módulo do curso
│   ├── 01-fundamentos/    # Fundamentos (IA, LLM, tokens)
│   ├── 02-primeiro-llm/       # Primeiro fluxo com LLM
│   ├── 03-viabilidade/     # Análise de viabilidade
│   ├── 04-rag/             # Pipeline RAG com ChromaDB
│   ├── 05-autoavaliacao/     # Autoavaliação
│   ├── 06-tool-calling/  # Tool Calling
│   ├── 07-planejamento/      # Planejamento e circuit breaker
│   ├── 08-multiagente/    # Multiagente
│   ├── 09-producao-api/      # Deploy FastAPI + Docker
│   ├── 10-avaliacao/      # Avaliação e AB testing
│   ├── 11-seguranca/          # Segurança e guardrails
│   ├── 12-memoria/          # Memória de curto/longo prazo
│   ├── 13-streaming/       # Streaming token-by-token
│   ├── 14-cache/         # Cache e otimização
│   ├── 15-skills/         # Design de skills
│   └── 16-operacoes/ # Ops: CI/CD, métricas, rollback
├── data/                   ← Dados de exemplo
├── tests/                  ← Testes globais
└── docker-compose.yml      ← Infraestrutura P4
```

---

## 7. Executar módulos

Cada módulo tem um script `run.py`. Execute assim (com o `.venv` ativado):

```bash
python modules/01-fundamentos/run.py
python modules/02-primeiro-llm/run.py
python modules/03-viabilidade/run.py
python modules/04-rag/run.py
python modules/05-autoavaliacao/run.py
python modules/06-tool-calling/run.py
python modules/07-planejamento/run.py
python modules/08-multiagente/run.py
python modules/09-producao-api/run.py
python modules/10-avaliacao/run.py
python modules/11-seguranca/run.py
python modules/12-memoria/run.py
python modules/13-streaming/run.py
python modules/14-cache/run.py
python modules/15-skills/run.py
python modules/16-operacoes/run.py
```

> 💡 Use `Tab` no terminal para autocomplete: digite `python modules/p0_` + `Tab` para completar automaticamente.

---

## 8. Executar testes

```bash
# Todos os testes
pytest

# Testes de um módulo específico
pytest modules/04-rag/exercises.py

# Com cobertura
pytest --cov=modules --cov-report=term-missing
```

---

## 9. Depuração — Erros comuns

### ❌ `ModuleNotFoundError: No module named 'openai'`

**Causa:** Ambiente virtual não está ativado ou dependências não foram instaladas.

**Solução:**

```bash
source .venv/bin/activate
pip install -e ".[dev]"
```

### ❌ `openai.AuthenticationError: Incorrect API key`

**Causa:** Chave inválida, expirada ou ausente no `.env`.

**Solução:**

1. Verifique se `.env` existe na raiz do projeto
2. Confirme que `OPENAI_API_KEY=sk-...` está preenchido (sem `sua_chave_aqui`)
3. Verifique se não há espaço extra: `OPENAI_API_KEY= sk-...` ❌ → `OPENAI_API_KEY=sk-...` ✅

### ❌ `RateLimitError: You exceeded your current quota`

**Causa:** Limite de gastos da OpenAI atingido.

**Solução:**

1. Acesse [platform.openai.com/account/limits](https://platform.openai.com/account/limits)
2. Configure limite de gasto (billing) se necessário
3. Aguarde o próximo mês ou adicione crédito

### ❌ `ConnectionError: Failed to establish a new connection`

**Causa:** Problema de rede ou `OPENAI_BASE_URL` incorreto.

**Solução:**

```bash
# Teste conectividade
curl -I https://api.openai.com

# Verifique a URL no .env
grep OPENAI_BASE_URL .env
```

### ❌ `docker: command not found`

**Causa:** Docker não está instalado (necessário apenas para P4).

**Solução:**

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install docker.io

# macOS (Homebrew)
brew install --cask docker

# Windows
# Baixe em docker.com/products/docker-desktop
```

### ❌ `ImportError: libomp.so` ou erro de compilador no `faiss-cpu`

**Causa:** Dependência C++ faltando.

**Solução:**

```bash
# Ubuntu/Debian
sudo apt install libomp-dev

# macOS
brew install libomp
```

---

## 10. Dicas rápidas

| Situação | Comando |
| ---------- | --------- |
| Ativar ambiente | `source .venv/bin/activate` |
| Desativar ambiente | `deactivate` |
| Verificar Python | `python --version` |
| Listar pacotes | `pip list` |
| Atualizar pacotes | `pip install --upgrade -e ".[dev]"` |
| Rodar módulo | `python modules/<modulo>/run.py` |
| Rodar testes | `pytest` |
| Formatar código | `black .` |

---

## 11. Variáveis de ambiente disponíveis

Todas as variáveis configuráveis no `.env`:

| Variável | Obrigatório | Padrão | Descrição |
| ---------- | ------------- | -------- | ----------- |
| `OPENAI_API_KEY` | ✅ | — | Chave da OpenAI |
| `ANTHROPIC_API_KEY` | ❌ | — | Chave da Anthropic (opcional) |
| `DEFAULT_MODEL` | ❌ | `gpt-4o-mini` | Modelo padrão para chamadas |
| `EMBEDDING_MODEL` | ❌ | `text-embedding-3-small` | Modelo de embedding (RAG) |
| `OPENAI_BASE_URL` | ❌ | `https://api.openai.com/v1` | URL base (use para providers compatíveis) |
| `API_PORT` | ❌ | `8000` | Porta da API FastAPI (P4) |
| `LOG_LEVEL` | ❌ | `INFO` | Nível de log: DEBUG, INFO, WARNING, ERROR |
| `HUMAN_IN_THE_LOOP` | ❌ | `true` | Aprovação humana ativada |

---

## Checklist final

Antes de começar o primeiro módulo, confirme:

- [ ] Python 3.11+ instalado (`python --version`)
- [ ] Repositório clonado (`cd applied-ai-agents`)
- [ ] Ambiente virtual criado e ativado (`source .venv/bin/activate`)
- [ ] Dependências instaladas (`pip install -e ".[dev]"`)
- [ ] `.env` criado com chave válida (`cp .env.example .env`)
- [ ] Teste de conexão passou (`python -c "import openai; print('OK')"` )
- [ ] Um módulo executou sem erro (`python modules/02-primeiro-llm/run.py`)

Se marcou todos ✅ — você está pronto para começar! 🚀
