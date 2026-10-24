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


# Modelo LLM usado quando nenhuma override existe no ambiente.
# IMPORTANTE: isto é um EXEMPLO, não um requisito. O nome do modelo não faz
# parte dos conceitos ensinados -- troque por Claude, Gemini, Qwen ou um modelo
# local (Ollama) definindo MODEL/DEFAULT_MODEL no .env. O código permanece igual.
DEFAULT_MODEL_NAME = "gpt-4o-mini"


def get_model(default: Optional[str] = None) -> str:
    """
    Retorna o nome do modelo LLM a usar, centralizando a configuracao.

    Ordem de resolucao: MODEL > DEFAULT_MODEL > default informado >
    DEFAULT_MODEL_NAME. Assim o aluno troca de provedor editando apenas o
    .env, sem tocar nos run.py.

    Args:
        default: Fallback final se nenhuma variavel de ambiente existir.

    Returns:
        Nome do modelo (string). Nunca levanta erro -- modelo tem sempre
        fallback, diferentemente de uma secret obrigatoria.
    """
    return (
        os.getenv("MODEL")
        or os.getenv("DEFAULT_MODEL")
        or default
        or DEFAULT_MODEL_NAME
    )


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


# ---------------------------------------------------------------------------
# Switch de fornecedor/modelo (OpenAI-compatible)
# ---------------------------------------------------------------------------
# Escolha no .env com LLM_PROVIDER + MODEL. Cada provider aponta para a sua
# variavel de chave e base URL, sem tocar nos run.py. Ex.:
#     LLM_PROVIDER=qwen
#     QWEN_PLAN_API_KEY=sk-sp-...
#     MODEL=qwen3.8-flash        # thinking ON (default do modelo)
#     MODEL=qwen3.8-flash-fast   # thinking OFF
# Para OpenAI (default): basta OPENAI_API_KEY.
#
# enable_thinking: na API compativel da Qwen NAO e parametro padrao da OpenAI;
# via SDK Python vai em extra_body={"enable_thinking": bool}. O nome do modelo
# com sufixo "-fast" desliga o thinking (espelha o YAML litellm do plano).
PROVIDERS: dict[str, dict[str, str]] = {
    "openai": {"key_var": "OPENAI_API_KEY", "base_url": ""},
    "qwen": {
        "key_var": "QWEN_PLAN_API_KEY",
        "base_url": "https://token-plan.maas.qwencloudapi.com/compatible-mode/v1",
    },
}


def get_provider() -> str:
    """Nome do provider ativo (LLM_PROVIDER), default 'openai'."""
    return os.getenv("LLM_PROVIDER", "openai").strip().lower()


def get_thinking(model: Optional[str] = None) -> Optional[dict]:
    """
    extra_body de thinking para client.chat.completions.create(), ou None.

    Como ligar/desligar (na ordem de prioridade):
      1. ENABLE_THINKING=true|false no .env  -> forcado, vale para qualquer modelo.
      2. sufixo '-fast' no nome do modelo     -> thinking OFF (espelha o YAML litellm).
      3. caso contrario                       -> thinking ON (default dos modelos hibridos).

    Provider Qwen: devolve {'enable_thinking': bool} (parametro nao-padrao da OpenAI,
    so aceito via extra_body). Provider OpenAI reasoning (gpt-5*/o*): devolve
    {'reasoning_effort': 'low'|'minimal'}. Outros providers/modelos: None.
    """
    provider = get_provider()
    if model is None:
        model = os.getenv("MODEL") or os.getenv("DEFAULT_MODEL") or ""

    override = os.getenv("ENABLE_THINKING")
    if override is not None:
        thinking_on = override.strip().lower() in ("1", "true", "yes", "on")
    else:
        thinking_on = not model.endswith("-fast")

    if provider == "qwen":
        return {"enable_thinking": thinking_on}
    if provider == "openai" and (
        model.startswith("gpt-5") or model.startswith("o1") or model.startswith("o3")
    ):
        return {"reasoning_effort": "low" if thinking_on else "minimal"}
    return None


def get_llm_config() -> tuple[str, Optional[str], str]:
    """
    Resolve (api_key, base_url, model) do provider escolhido no .env.

    Ordem de resolucao da chave/base:
      - LLM_PROVIDER escolhe o preset em PROVIDERS (default openai).
      - OPENAI_API_KEY / OPENAI_BASE_URL fazem override se definidas.
      - QWEN_PLAN_API_KEY / QWEN_BASE_URL idem para o provider qwen.
      - MODEL > DEFAULT_MODEL > nome padrao do provider.

    Returns:
        (api_key, base_url, model). base_url e None quando usar o endpoint padrao
        da OpenAI. Para o extra_body de thinking use get_thinking(model).

    Raises:
        EnvironmentError: se a chave obrigatoria do provider nao estiver definida.
    """
    provider = get_provider()
    preset = PROVIDERS.get(provider, PROVIDERS["openai"])

    if provider == "qwen":
        api_key = os.getenv("QWEN_PLAN_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("QWEN_BASE_URL") or preset["base_url"]
        default_model = "qwen-plus"
    else:
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL") or None
        default_model = DEFAULT_MODEL_NAME

    if not api_key:
        raise EnvironmentError(
            f"Provider '{provider}' exige uma chave. Defina "
            f"{preset['key_var']} (ou OPENAI_API_KEY) no .env."
        )

    model = os.getenv("MODEL") or os.getenv("DEFAULT_MODEL") or default_model
    return api_key, base_url, model


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
    
    # Padrões comuns de chaves.
    # Ordem importa: sk-ant- antes de sk- para não mascarar só o prefixo 'sk'.
    # Quantifier {8,} (antes {20,}) evita vazar chaves curtas em logs.
    patterns = [
        (r'sk-ant-[a-zA-Z0-9_\-]{8,}', 'sk-ant-****'),
        (r'sk-[a-zA-Z0-9_\-]{8,}', 'sk-****'),
        (r'Bearer\s+[a-zA-Z0-9\-_.~+/]+=*', 'Bearer ****'),
    ]
    
    sanitized = value
    for pattern, replacement in patterns:
        sanitized = re.sub(pattern, replacement, sanitized)
    
    return sanitized
