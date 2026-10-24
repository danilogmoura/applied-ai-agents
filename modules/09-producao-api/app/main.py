"""
API principal do Agente de IA — FastAPI com Swagger.

Endpoints:
- POST /chat — Envia mensagem para o agente
- GET /health — Status de saúde
- GET /metrics — Métricas de uso
- GET /docs — Documentação Swagger automática
"""

from __future__ import annotations

import logging
import time
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.models import AgentRequest, AgentResponse, HealthResponse, MetricsResponse
from app.services.agent_service import AgentService
from shared.logging_config import setup_logging

logger = setup_logging("09-producao-api.main")

# Instância global do serviço
agent_service = AgentService()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle da aplicação FastAPI."""
    logger.info("🚀 API do Agente de IA iniciando...")
    yield
    logger.info("🛑 API do Agente de IA encerrando...")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CRIAÇÃO DA APP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

app = FastAPI(
    title="AI Agents API",
    description=(
        "API para agentes de inteligência artificial construídos em Python.\n\n"
        "**Trilha de Curso:** P0 → P1 → P2 → P3a-1 → P3a-2 → P3a-3 → P3b → P4\n\n"
        "**Recursos:**\n"
        "- Classificação de tickets com LLM\n"
        "- Pipeline RAG com ChromaDB\n"
        "- Autoavaliação com Pydantic\n"
        "- Tool Calling com governança HITL\n"
        "- Circuit breakers e checkpoints\n"
        "- Sistema multiagente com router\n"
    ),
    version="0.1.0",
    lifespan=lifespan,
)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ENDPOINTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@app.post(
    "/chat",
    response_model=AgentResponse,
    summary="Enviar mensagem para o agente",
    description="Envia uma mensagem/tarefa para o agente de IA processar.",
)
async def chat(request: AgentRequest) -> AgentResponse:
    """
    Endpoint principal de chat com o agente.
    
    - **message**: Tarefa ou pergunta para o agente
    - **model**: Modelo LLM (padrão: gpt-4o-mini)
    - **use_tools**: Habilita tool calling se True
    - **max_iterations**: Limite de autoavaliação (1-10)
    """
    try:
        result = await agent_service.process_request(
            message=request.message,
            use_tools=request.use_tools,
            max_iterations=request.max_iterations,
        )
        
        return AgentResponse(
            answer=result["answer"],
            model=result["model"],
            tokens_input=result["tokens_input"],
            tokens_output=result["tokens_output"],
            cost_usd=result["cost_usd"],
            conversation_id=str(uuid.uuid4())[:8],
        )
    
    except Exception as e:
        logger.error(f"Erro no chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Status de saúde da API",
)
async def health() -> HealthResponse:
    """Verifica se a API e o LLM estão disponíveis."""
    uptime = time.time() - agent_service.start_time
    
    return HealthResponse(
        status="healthy",
        uptime_seconds=round(uptime, 1),
    )


@app.get(
    "/metrics",
    response_model=MetricsResponse,
    summary="Métricas de uso",
)
async def metrics() -> MetricsResponse:
    """Retorna métricas acumuladas de uso da API."""
    m = agent_service.get_metrics()
    
    return MetricsResponse(
        total_requests=m["total_requests"],
        total_tokens=m["total_tokens"],
        total_cost_usd=m["total_cost_usd"],
        avg_latency_ms=0.0,  # Seria preenchido pelo middleware
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Log ao encerrar."""
    logger.info("Encerrando API...")


if __name__ == "__main__":
    import uvicorn
    
    port = int(__import__("os").environ.get("API_PORT", "8000"))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info",
    )
