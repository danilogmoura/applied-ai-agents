"""
Módulo P4 — Produto em Produção (execução)

Inicia a API FastAPI com Uvicorn e demonstra o fluxo completo.

Uso:
    python modules/p4_production/run.py          # Inicia API local
    docker-compose up --build                    # Inicia com Docker
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel

from shared.logging_config import setup_logging

console = Console()
logger = setup_logging("p4_production.run")


def print_usage_guide():
    """Exibe guia de uso da API."""
    console.print(Panel.fit(
        "[bold yellow]MÓDULO P4 — Produto em Produção[/]\n\n"
        "API FastAPI + Docker + Swagger.\n"
        "Monitoramento e métricas integrados.",
        title="🏭 AI Agents Course",
        border_style="cyan",
    ))
    
    console.print("\n[bold green]📡 Endpoints disponíveis:[/]\n")
    
    endpoints = [
        ("POST", "/chat", "Enviar mensagem para o agente"),
        ("GET", "/health", "Status de saúde da API"),
        ("GET", "/metrics", "Métricas de uso"),
        ("GET", "/docs", "Documentação Swagger interativa"),
    ]
    
    for method, path, desc in endpoints:
        color = {"POST": "green", "GET": "blue"}[method]
        console.print(f"  [{color}]{method}[/] [bold]{path}[/] — {desc}")
    
    console.print("\n[bold cyan]🧪 Testes com curl:[/]\n")
    
    examples = [
        ('curl http://localhost:8000/health', "Verificar status"),
        (
            'curl -X POST http://localhost:8000/chat \\\n'
            '  -H "Content-Type: application/json" \\\n'
            '  -d \'{"message": "Classifique este ticket como urgente"}\'',
            "Enviar mensagem",
        ),
        ('curl http://localhost:8000/metrics', "Ver métricas"),
    ]
    
    for cmd, desc in examples:
        console.print(f"  [dim]{desc}[/]")
        console.print(f"  [yellow]{cmd}[/]\n")
    
    console.print("[bold magenta]🐳 Com Docker:[/]\n")
    console.print("  [yellow]docker-compose up --build[/]\n")
    
    console.print("[dim]💡 Este módulo completa a trilha P0→P4![/]")


def main():
    """Executa ou inicia a API."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Agents API — Módulo P4")
    parser.add_argument(
        "--serve",
        action="store_true",
        help="Inicia o servidor FastAPI",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Porta do servidor (padrão: 8000)",
    )
    
    args = parser.parse_args()
    
    if args.serve:
        port = args.port
        console.print(f"\n[bold green]🚀 Iniciando API na porta {port}...[/]")
        console.print(f"[dim]Acesse http://localhost:{port}/docs para documentação Swagger[/]\n")
        
        try:
            import uvicorn
            uvicorn.run(
                "app.main:app",
                host="0.0.0.0",
                port=port,
                reload=False,
                log_level="info",
            )
        except KeyboardInterrupt:
            console.print("\n[yellow]⛔ API encerrada pelo usuário[/]")
    else:
        print_usage_guide()


if __name__ == "__main__":
    main()
