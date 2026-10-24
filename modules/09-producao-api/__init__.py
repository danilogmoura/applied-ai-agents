"""Módulo P4 — Produto em Produção

Implantação da solução como API REST com FastAPI + Uvicorn,
empacotada em Docker, com documentação Swagger e monitoramento.

Problema: O agente funciona no seu computador, mas como colocá-lo
em produção para ser consumido por qualquer aplicação?
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Importações principais do módulo
from app.main import app
from app.models import AgentRequest, AgentResponse, HealthResponse
from app.services.agent_service import AgentService
from app.middleware.monitoring import MonitoringMiddleware

__all__ = ["app", "AgentRequest", "AgentResponse", "HealthResponse", "AgentService"]
