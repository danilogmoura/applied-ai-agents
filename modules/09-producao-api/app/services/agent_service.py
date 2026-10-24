"""Serviço principal do agente de IA."""

from __future__ import annotations

import logging
import time
from typing import Optional

from shared.cost import count_tokens, estimate_cost, format_cost
from shared.logging_config import setup_logging, measure_latency

logger = setup_logging("09-producao-api.agent_service")


class AgentService:
    """
    Serviço central que orquestra chamadas LLM e ferramentas.
    
    Em produção, este serviço seria conectado ao OpenAI SDK real.
    Aqui simula respostas para demonstração.
    """
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.start_time = time.time()
    
    async def process_request(
        self,
        message: str,
        use_tools: bool = False,
        max_iterations: int = 3,
    ) -> dict:
        """
        Processa requisição do usuário através do pipeline do agente.
        
        Args:
            message: Mensagem do usuário.
            use_tools: Se deve usar ferramentas.
            max_iterations: Máximo de iterações de autoavaliação.
        
        Returns:
            Dicionário com resposta e métricas.
        """
        self.total_requests += 1
        
        input_tokens = count_tokens(message, self.model)
        
        with measure_latency(logger, "agent_process") as metrics:
            # Simula processamento LLM
            answer = self._generate_response(message)
            
            output_tokens = count_tokens(answer, self.model)
            cost = estimate_cost(input_tokens, output_tokens, self.model)
            
            self.total_tokens += input_tokens + output_tokens
            self.total_cost += cost
        
        logger.info(
            "request_processed",
            extra={"extra_data": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "cost_usd": cost,
                "latency_ms": metrics.get("latency_ms", 0),
            }},
        )
        
        return {
            "answer": answer,
            "model": self.model,
            "tokens_input": input_tokens,
            "tokens_output": output_tokens,
            "cost_usd": cost,
            "tools_used": [],
        }
    
    def _generate_response(self, message: str) -> str:
        """Gera resposta do agente (simulação)."""
        # Em produção, chama OpenAI SDK aqui
        response_map = {
            "classif": "Classe como NORMAL — sem palavras-chave de urgência detectadas.",
            "urgente": "Classe como URGENTE — erro 500 em produção detectado.",
            "preço": "Classe como NORMAL — consulta sobre preços/planos.",
        }
        
        msg_lower = message.lower()
        for key, resp in response_map.items():
            if key in msg_lower:
                return resp
        
        return f"Processado: '{message[:80]}...' — Resposta gerada pelo modelo {self.model}."
    
    def get_metrics(self) -> dict:
        """Retorna métricas de uso do serviço."""
        uptime = time.time() - self.start_time
        
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost_usd": round(self.total_cost, 6),
            "avg_cost_per_request": format_cost(self.total_cost / max(self.total_requests, 1)),
            "uptime_seconds": round(uptime, 1),
            "requests_per_minute": round(self.total_requests / max(uptime / 60, 0.001), 2),
        }
