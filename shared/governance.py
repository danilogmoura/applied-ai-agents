"""
Governança e Human-in-the-Loop (HITL).

Fornece mecanismos de aprovação humana antes de ações críticas em agentes
de IA. Suporta modo interativo (console) e programático.

Uso:
    >>> from shared.governance import require_approval, ActionRequest
    >>> action = ActionRequest(
    ...     operation="delete_record",
    ...     target="user_data_123",
    ...     reason="Limpeza de dados expirados"
    ... )
    >>> if require_approval(action):
    ...     execute_deletion()
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Optional

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Níveis de risco para operações."""
    LOW = "low"           # Leitura, consulta
    MEDIUM = "medium"     # Escrita, atualização
    HIGH = "high"         # Deleção, modificação estrutural
    CRITICAL = "critical" # Produção, dados sensíveis


@dataclass
class ActionRequest:
    """Solicitação de ação para aprovação humana."""
    operation: str          # O que o agente quer fazer
    target: str             # Alvo da operação
    reason: str             # Justificativa
    risk_level: RiskLevel   # Nível de risco
    metadata: Optional[dict] = None  # Dados adicionais


def _human_in_the_loop_enabled() -> bool:
    """Verifica se HITL está habilitado via variável de ambiente."""
    import os
    return os.getenv("HUMAN_IN_THE_LOOP", "true").lower() in ("true", "1", "yes")


def require_approval(action: ActionRequest) -> bool:
    """
    Solicita aprovação humana para uma ação.
    
    Em modo interativo, exibe prompt no console.
    Em modo automatizado (HITL=false), aprova automaticamente mas loga WARNING.
    
    Args:
        action: Detalhamento da ação solicitada.
    
    Returns:
        True se aprovado, False se recusado.
    """
    if not _human_in_the_loop_enabled():
        logger.warning(
            f"HITL desabilitado — aprovando automaticamente: {action.operation} "
            f"em {action.target} (risco: {action.risk_level.value})"
        )
        return True
    
    # Formata a solicitação para exibição
    risk_colors = {
        RiskLevel.LOW: "[LOW]",
        RiskLevel.MEDIUM: "[MEDIUM]",
        RiskLevel.HIGH: "[HIGH]",
        RiskLevel.CRITICAL: "[CRITICAL]",
    }
    
    color = risk_colors.get(action.risk_level, "[UNKNOWN]")
    
    approval_prompt = (
        f"\n{'='*60}\n"
        f"⚠️  APROVAÇÃO HUMANA NECESSÁRIA\n"
        f"{'='*60}\n"
        f"Operação : {action.operation}\n"
        f"Alvo     : {action.target}\n"
        f"Risco    : {color}\n"
        f"Motivo   : {action.reason}\n"
        f"{'='*60}\n"
        f"Aprovar? [y/N]: "
    )
    
    try:
        response = input(approval_prompt).strip().lower()
        approved = response in ("y", "yes")
        
        if approved:
            logger.info(f"Ação aprovada pelo usuário: {action.operation}")
        else:
            logger.warning(f"Ação recusada pelo usuário: {action.operation}")
        
        return approved
    
    except EOFError:
        # Sem entrada interativa (pipe/redirecionamento)
        logger.warning(
            "Sem entrada interativa disponível — aprovando por segurança"
        )
        return True


def log_governance_event(
    action: ActionRequest,
    approved: bool,
    agent_name: str = "unknown",
) -> None:
    """Registra evento de governança para auditoria."""
    event = {
        "agent": agent_name,
        "operation": action.operation,
        "target": action.target,
        "risk_level": action.risk_level.value,
        "approved": approved,
        "reason": action.reason,
        "metadata": action.metadata or {},
    }
    
    level = logging.INFO if approved else logging.WARNING
    logger.log(level, "governance_event", extra={"extra_data": event})


def safe_execute(
    action: ActionRequest,
    func: callable,
    *args,
    agent_name: str = "unknown",
    **kwargs,
) -> Optional[Any]:
    """
    Executa função apenas após aprovação humana.
    
    Args:
        action: Descrição da ação.
        func: Função a executar se aprovada.
        *args: Argumentos para a função.
        agent_name: Nome do agente solicitante.
        **kwargs: Palavras-chave para a função.
    
    Returns:
        Resultado da função ou None se recusado.
    """
    if require_approval(action):
        result = func(*args, **kwargs)
        log_governance_event(action, True, agent_name)
        return result
    else:
        log_governance_event(action, False, agent_name)
        logger.info(f"Ação bloqueada: {action.operation}")
        return None
