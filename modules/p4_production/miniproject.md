# 🏗️ Mini-Projeto Integrador — Production API

> **Objetivo:** Construir uma API de produção para um agente IA com validação e middleware.

## O que você vai construir

Uma API `agent_api.py` (FastAPI) que:

1. **Valida** inputs com Pydantic models
2. **Mede** timing de cada middleware
3. **Gera** Docker config para deploy
4. **Garante** formato consistente de response

## Requisitos

```python
class AgentAPI:
    def validate_input(self, request: dict) -> dict:
        """Validar input com Pydantic-like schema."""
        ...
    
    def add_middleware_timing(self, app):
        """Middleware que mede tempo de cada request."""
        ...
    
    def generate_docker_config(self) -> str:
        """Gerar Dockerfile + docker-compose.yml."""
        ...
    
    def ensure_response_format(self, response: dict) -> dict:
        """Garantir formato consistente: {status, data, metadata}."""
        ...
```

## Teste seu código

```bash
python agent_api.py --port 8000
docker-compose up --build
curl http://localhost:8000/health
```

## Desafios extras

- [ ] Authentication com JWT
- [ ] Rate limiting por IP
- [ ] OpenAPI/Swagger docs
- [ ] Health check endpoint
