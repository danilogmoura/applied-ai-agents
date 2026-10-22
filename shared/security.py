"""
Gestão de secrets e variáveis de ambiente.

Protege chaves de API carregando do .env e valida presença de variáveis
críticas antes da execução.

Uso:
    >>> from shared.security import get_secret, validate_secrets
    >>> api_key = get_secret("OPENAI_API_KEY")
    >>> validate_secrets(["OPENAI_API_KEY", "ANTHROPIC_API_KEY"])
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Carrega .env do root do projeto se existir
_PROJECT_ROOT = Path(__file__).parent.parent
_ENV_PATH = _PROJECT_ROOT / ".env"

if _ENV_PATH.exists():
    load_dotenv(_ENV_PATH)
else:
    # Tenta .env no diretório atual
    load_dotenv()


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """
    Obtém uma secret do ambiente ou .env.
    
    Args:
        name: Nome da variável de ambiente.
        default: Valor padrão se não estiver definida.
    
    Returns:
        Valor da secret ou None/default.
    
    Raises:
        ValueError: Se a secret é crítica e não está definida nem tem default.
    """
    value = os.getenv(name, default)
    
    if value is None and default is None:
        logger.warning(f"Secret '{name}' não definida no ambiente ou .env")
    
    return value


def get_required_secret(name: str) -> str:
    """
    Obtém uma secret obrigatória. Levanta erro se não estiver definida.
    
    Args:
        name: Nome da variável de ambiente obrigatória.
    
    Returns:
        Valor da secret.
    
    Raises:
        EnvironmentError: Se a secret obrigatória não está definida.
    """
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(
            f"Variável de ambiente obrigatória '{name}' não definida. "
            f"Copie .env.example para .env e preencha suas chaves."
        )
    return value


def validate_secrets(required_keys: list[str]) -> bool:
    """
    Valida se todas as secrets necessárias estão presentes.
    
    Args:
        required_keys: Lista de nomes de variáveis obrigatórias.
    
    Returns:
        True se todas estão presentes.
    
    Raises:
        EnvironmentError: Se alguma secret obrigatória está ausente.
    """
    missing = [key for key in required_keys if not os.getenv(key)]
    
    if missing:
        missing_str = ", ".join(missing)
        error_msg = f"Secrets ausentes: {missing_str}"
        logger.error(error_msg)
        raise EnvironmentError(error_msg)
    
    logger.debug(f"All required secrets validated: {required_keys}")
    return True


def mask_secret(secret: str, visible_chars: int = 4) -> str:
    """
    Mascara uma secret para exibição segura em logs.
    
    Args:
        secret: A secret a ser mascarada.
        visible_chars: Número de caracteres visíveis no final.
    
    Returns:
        String mascarada (ex: 'sk-****ab12').
    """
    if not secret or len(secret) <= visible_chars:
        return "****"
    return secret[:visible_chars] + "****" + secret[-4:]


def is_production() -> bool:
    """Verifica se o código está rodando em produção."""
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def sanitize_for_log(value: str) -> str:
    """
    Sanitiza valores que podem conter secrets para logs seguros.
    
    Substitui padrões comuns de chaves API por placeholders.
    """
    import re
    
    # Padrões comuns de chaves
    patterns = [
        (r'sk-[a-zA-Z0-9]{20,}', 'sk-****'),
        (r'sk-ant-[a-zA-Z0-9]{20,}', 'sk-ant-****'),
        (r'Bearer\s+[a-zA-Z0-9\-_.~+/]+=*', 'Bearer ****'),
    ]
    
    sanitized = value
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized)
    
    return sanitized
