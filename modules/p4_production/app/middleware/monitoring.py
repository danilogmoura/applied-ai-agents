"""Middleware de monitoramento para FastAPI."""

from __future__ import annotations

import time
import logging
from typing import Optional

logger = logging.getLogger("p4_production.middleware")


class MonitoringMiddleware:
    """
    Middleware que adiciona métricas de latência e contagem de requisições.
    
    Adiciona headers X-Request-ID, X-Response-Time e logs estruturados.
    """
    
    def __init__(self, app):
        self.app = app
        self.request_count = 0
        self.total_latency = 0.0
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.perf_counter()
        request_id = f"req-{int(start_time * 1000)}"
        
        # Captura informações da requisição
        method = scope.get("method", "?")
        path = scope.get("path", "?")
        
        # Executa a requisição
        async def send_with_metrics(response):
            response["headers"].append(
                (b"x-request-id", request_id.encode())
            )
            response["headers"].append(
                (b"x-response-time", f"{time.perf_counter() - start_time:.3f}s".encode())
            )
            await send(response)
        
        try:
            await self.app(scope, receive, send_with_metrics)
        finally:
            latency = time.perf_counter() - start_time
            self.request_count += 1
            self.total_latency += latency
            
            logger.info(
                "http_request",
                extra={"extra_data": {
                    "method": method,
                    "path": path,
                    "latency_ms": latency * 1000,
                    "request_id": request_id,
                }},
            )
    
    def get_metrics(self) -> dict:
        """Retorna métricas acumuladas."""
        avg_latency = (
            self.total_latency / self.request_count * 1000
            if self.request_count > 0 else 0
        )
        return {
            "total_requests": self.request_count,
            "avg_latency_ms": round(avg_latency, 2),
        }
