#!/bin/bash
# ============================================================================
# setup_corpus_index.sh — prepara ambiente e constrói o índice vetorial do corpus
#
# O que faz:
#   1. Garante um ambiente Python isolado (.venv) usando `uv` (sem sudo) ou venv.
#   2. Instala openai + chromadb + tiktoken.
#   3. Valida a conexão Qwen MaaS (--smoke).
#   4. Constrói o índice (.corpus_index/) a partir dos livros em docs/applied-ai-agents.
#
# Uso:
#   ./setup_corpus_index.sh              # setup + smoke + build completo
#   ./setup_corpus_index.sh --dry-run    # setup + cotação de custo, SEM gastar API
#   ./setup_corpus_index.sh --smoke-only # setup + teste de conexão (2 vetores)
#   ./setup_corpus_index.sh --query "context engineering"   # consulta o índice
#   ./setup_corpus_index.sh --rebuild    # apaga .corpus_index e reconstroi
#
# Requisitos: python3, e uma chave QWEN_MAAS_API_KEY no arquivo .env da raiz.
# ============================================================================

set -euo pipefail

cd "$(dirname "$0")"
VENV=".venv"
PY="$VENV/bin/python"

# ── flags ────────────────────────────────────────────────────────────────
MODE="build"          # build | dry-run | smoke-only | query | rebuild
QUERY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)   MODE="dry-run"; shift ;;
    --smoke-only) MODE="smoke-only"; shift ;;
    --rebuild)   MODE="rebuild"; shift ;;
    --query)     MODE="query"; QUERY="${2:-}"; shift 2 ;;
    -h|--help)   grep '^#' "$0" | sed 's/^# \{0,1\}//'; exit 0 ;;
    *) echo "Opção desconhecida: $1 (use --help)"; exit 1 ;;
  esac
done

echo "🧩 AI Agents Course — Setup do índice do corpus"
echo "================================================="

# ── 1. checar chave no .env ───────────────────────────────────────────────
if [ ! -f ".env" ]; then
  echo "❌ .env não encontrado na raiz. Copie .env.example e preencha QWEN_MAAS_API_KEY."
  exit 1
fi
if ! grep -qE '^QWEN_MAAS_API_KEY=.+' ".env"; then
  echo "❌ QWEN_MAAS_API_KEY ausente ou vazia no .env."
  exit 1
fi
echo "✓ QWEN_MAAS_API_KEY presente no .env"

# ── 2. criar venv (uv se houver, senão python -m venv) ────────────────────
if [ ! -x "$PY" ]; then
  echo "\n📦 Criando ambiente virtual em $VENV ..."
  if command -v uv >/dev/null 2>&1; then
    echo "   (usando uv — rápido, sem sudo)"
    uv venv "$VENV"
  else
    python3 -m venv "$VENV" || {
      echo "❌ Falha ao criar venv. Instale python3-venv OU use uv:"
      echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
      exit 1
    }
  fi
else
  echo "✓ Ambiente $VENV já existe"
fi

# ── 3. instalar dependências ──────────────────────────────────────────────
DEPS="openai chromadb tiktoken"
echo "\n📚 Instalando dependências: $DEPS"
if command -v uv >/dev/null 2>&1; then
  uv pip install --python "$PY" $DEPS
else
  "$PY" -m ensurepip --upgrade >/dev/null 2>&1 || true
  "$PY" -m pip install --quiet --upgrade pip
  "$PY" -m pip install --quiet $DEPS
fi
"$PY" -c "import openai, chromadb, tiktoken; print('✓ deps OK')"

# ── 4. rodar conforme o modo ──────────────────────────────────────────────
echo "\n🔎 Verificando fontes em docs/applied-ai-agents ..."
[ -d "docs/applied-ai-agents" ] || { echo "❌ pasta docs/applied-ai-agents não encontrada."; exit 1; }

case "$MODE" in
  smoke-only)
    echo "\n🧪 Smoke test (conexão Qwen, 2 vetores):"
    "$PY" -m tools.build_index --smoke
    ;;
  dry-run)
    echo "\n💰 Cotação de custo (nenhuma chamada à API):"
    "$PY" -m tools.build_index --dry-run
    ;;
  rebuild)
    echo "\n🔨 Reconstruindo índice do zero:"
    "$PY" -m tools.build_index --smoke
    "$PY" -m tools.build_index --rebuild
    ;;
  query)
    if [ -z "$QUERY" ]; then echo "❌ informe a busca: --query \"seu termo\""; exit 1; fi
    echo "\n🔍 Consultando índice: \"$QUERY\""
    "$PY" -m tools.query "$QUERY" --k 5
    ;;
  build)
    echo "\n🧪 Smoke test antes do build completo:"
    "$PY" -m tools.build_index --smoke
    echo "\n🚀 Gerando embeddings e gravando .corpus_index/ (~6.5k chunks, alguns minutos):"
    "$PY" -m tools.build_index
    ;;
esac

echo "\n✅ Concluído ($MODE)."
if [ "$MODE" = "build" ] || [ "$MODE" = "rebuild" ]; then
  echo "   Consulte com:  $PY -m tools.query \"um tema\" --k 5"
  echo "   Ou rode de novo:  ./setup_corpus_index.sh --query \"planning\""
fi
