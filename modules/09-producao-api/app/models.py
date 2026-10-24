"""Modelos de dados para a API de produção."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AgentRequest(BaseModel):
    """Solicitação para o agente de IA."""
    
    message: str = Field(
        ...,
        description="Mensagem ou tarefa para o agente",
        examples=["Classifique este ticket como urgente"],
        min_length=1,
        max_length=4000,
    )
    
    model: str = Field(
        default="gpt-4o-mini",
        description="Modelo LLM a utilizar",
    )
    
    use_tools: bool = Field(
        default=False,
        description="Se o agente deve usar ferramentas disponíveis",
    )
    
    max_iterations: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Máximo de iterações para autoavaliação",
    )
    
    conversation_id: Optional[str] = Field(
        default=None,
        description="ID de conversa para manter contexto",
    )


class ToolResult(BaseModel):
    """Resultado de execução de ferramenta."""
    
    tool_name: str
    result: str
    cost_usd: float = 0.0
    tokens_used: int = 0


class AgentResponse(BaseModel):
    """Resposta do agente de IA."""
    
    answer: str
    model: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    tools_used: list[ToolResult] = []
    conversation_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class HealthResponse(BaseModel):
    """Status de saúde da API."""
    
    status: str = "healthy"
    version: str = "0.1.0"
    uptime_seconds: float = 0.0
    llm_available: bool = True
    circuits_open: list[str] = []


class MetricsResponse(BaseModel):
    """Métricas de uso da API."""
    
    total_requests: int = 0
    total_tokens: int = 0
    total_cost_usd: float = 0.0
    avg_latency_ms: float = 0.0
    requests_by_model: dict[str, int] = {}
    requests_by_tool: dict[str, int] = {}
