"""
Configuração de logs estruturados para observabilidade.

Fornece logging JSON estruturado para rastreamento de custos, tokens,
latência e erros em agentes de IA.

Uso:
    >>> from shared.logging_config import setup_logging
    >>> logger = setup_logging("p0_first_llm")
    >>> logger.info("llm_call", cost=0.001, tokens=500, latency_ms=1200)
"""

from __future__ import annotations

import json
import logging
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any


class StructuredFormatter(logging.Formatter):
    """Formatador JSON para logs estruturados."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adicionar campos extras
        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data
        
        # Adicionar informações de erro se presente
        if record.exc_info and record.exc_info[0] is not None:
            log_data["error"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging(
    name: str = "ai-agents-course",
    level: str = "INFO",
    structured: bool = True,
) -> logging.Logger:
    """
    Configura o sistema de logging para o módulo.
    
    Args:
        name: Nome do logger (geralmente nome do módulo).
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        structured: Se True, usa formato JSON; se False, usa texto legível.
    
    Returns:
        Logger configurado.
    """
    logger = logging.getLogger(name)
    
    if logger.handlers:
        return logger  # Já configurado
    
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    handler = logging.StreamHandler(sys.stdout)
    
    if structured:
        formatter = StructuredFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


@contextmanager
def measure_latency(logger: logging.Logger, operation: str) -> dict[str, float]:
    """
    Context manager para medir latência de operações.
    
    Usage:
        with measure_latency(logger, "llm_call") as metrics:
            response = client.chat.completions.create(...)
            metrics["tokens"] = len(response.choices[0].message.content)
    """
    start = time.perf_counter()
    metrics: dict[str, float] = {}
    
    try:
        yield metrics
    finally:
        latency_ms = (time.perf_counter() - start) * 1000
        metrics["latency_ms"] = latency_ms
        logger.info(
            f"{operation}_completed",
            extra={"extra_data": {"latency_ms": latency_ms, **metrics}},
        )


def log_cost(
    logger: logging.Logger,
    operation: str,
    input_tokens: int,
    output_tokens: int,
    model: str,
    cost_fn: Any = None,
) -> None:
    """Registra métricas de custo de uma operação LLM."""
    from shared.cost import estimate_cost, summarize_usage
    
    usage = summarize_usage(input_tokens, output_tokens, model)
    logger.info(
        f"{operation}_cost",
        extra={"extra_data": usage},
    )
