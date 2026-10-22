#!/bin/bash
# Script de instalação rápida do AI Agents Course

set -e

echo "🚀 AI Agents Course — Instalação Rápida"
echo "========================================"

# 1. Verifica Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ é necessário"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 11 ]); then
    echo "❌ Python 3.11+ necessário (encontrado: $PYTHON_VERSION)"
    exit 1
fi

echo "✓ Python $PYTHON_VERSION detectado"

# 2. Cria ambiente virtual
if [ ! -d ".venv" ]; then
    echo "\n📦 Criando ambiente virtual..."
    python3 -m venv .venv
fi

# 3. Ativa ambiente
source .venv/bin/activate

# 4. Instala dependências
echo "\n📚 Instalando dependências..."
pip install --upgrade pip
pip install -e ".[dev]"

# 5. Configura .env
if [ ! -f ".env" ]; then
    echo "\n⚙️  Configurando .env..."
    cp .env.example .env
    echo "✓ Arquivo .env criado. Edite com suas chaves de API."
else
    echo "\n⚙️  .env já existe (pule esta etapa)"
fi

# 6. Testa instalação
echo "\n🧪 Testando instalação..."
python -c "
from shared.cost import count_tokens, estimate_cost
from shared.security import get_secret
from shared.governance import RiskLevel
print('✓ Utilitários compartilhados funcionando')
"

echo "\n✅ Instalação concluída!"
echo "\n📖 Próximos passos:"
echo "   1. Edite .env com sua OPENAI_API_KEY"
echo "   2. Execute: python modules/p0_first_llm/run.py"
echo "   3. Consulte docs/curriculum.md para o guia completo"
