# Imagem base Python
FROM python:3.11-slim AS base

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala o projeto
WORKDIR /app
COPY pyproject.toml .
COPY shared/ shared/
COPY modules/ modules/

RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

# Copia restante do código
COPY . .

# Porta da API
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão: inicia API
# --app-dir aponta para a raiz do capitulo 09; assim os imports internos
# ("from app.models import ...") resolvem corretamente. Nomes de pasta com
# hífen nao podem ser usados como dotted-module-path (modulos.p4_production),
# por isso usamos --app-dir em vez de "modules.<pasta>.app.main".
CMD ["uvicorn", "--app-dir", "modules/09-producao-api", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
