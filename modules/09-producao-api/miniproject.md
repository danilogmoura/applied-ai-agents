# 🏗️ Mini-Projeto Integrador — Production API

> **Objetivo:** Construir uma API de produção para um agente IA com validação e middleware.

## O que você vai construir

Uma API `agent_api.py` (FastAPI) que:

1. **Valida** inputs com Pydantic models
2. **Mede** timing de cada middleware
3. **Gera** Docker config para deploy
4. **Garante** formato consistente de response

> ℹ️ **Arquitetura de referência:** O `run.py` deste módulo é uma **aplicação FastAPI real** (com rotas, middleware e `main()`), que é o padrão profissional de produção. Este mini-projeto usa uma classe simplificada `AgentAPI` para você praticar os conceitos (validação, timing, Docker, formato de response) sem precisar subir um servidor. As duas abordagens são compatíveis: quando terminar, compare com o app FastAPI do `run.py`.

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

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com validação Pydantic-like

Defina modelos de input/output que validam dados antes de processar:

```python
import json
from datetime import datetime
from typing import Optional, Any

class AgentAPI:
    def __init__(self):
        self.request_log = []
    
    def validate_input(self, request: dict) -> dict:
        """Valida input com regras tipo Pydantic."""
        errors = []
        
        # Campos obrigatórios
        if "query" not in request:
            errors.append("Campo 'query' é obrigatório")
        
        if "model" in request and request["model"] not in ("gpt-4o", "gpt-4o-mini", "claude-3.5"):
            errors.append(f"Modelo '{request['model']}' não suportado")
        
        if "temperature" in request:
            temp = request["temperature"]
            if not isinstance(temp, (int, float)) or temp < 0 or temp > 2:
                errors.append("temperature deve ser float entre 0 e 2")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }
```

### Passo 2 — Implemente middleware de timing

Meça quanto tempo cada etapa leva para observabilidade:

```python
import time

def add_middleware_timing(self, app=None):
    """Middleware que mede tempo de cada request."""
    def middleware(request: dict) -> dict:
        start = time.time()
        
        # Etapa 1: Validação
        validation_start = time.time()
        validation = self.validate_input(request)
        validation_time = time.time() - validation_start
        
        if not validation["valid"]:
            return {
                "status": "error",
                "error": "Input inválido",
                "details": validation["errors"],
                "timing": {
                    "validation_ms": round((time.time() - start) * 1000, 2),
                },
            }
        
        # Etapa 2: Processamento (simulado)
        processing_start = time.time()
        response = self._process_request(request)
        processing_time = time.time() - processing_start
        
        # Etapa 3: Formatação
        format_start = time.time()
        formatted = self.ensure_response_format(response)
        format_time = time.time() - format_start
        
        total_time = time.time() - start
        
        # Registra no log
        self.request_log.append({
            "timestamp": datetime.now().isoformat(),
            "query": request.get("query", ""),
            "total_ms": round(total_time * 1000, 2),
            "stages": {
                "validation_ms": round(validation_time * 1000, 2),
                "processing_ms": round(processing_time * 1000, 2),
                "format_ms": round(format_time * 1000, 2),
            },
        })
        
        return formatted
    
    return middleware

def _process_request(self, request: dict) -> dict:
    """Simula processamento do request."""
    return {
        "status": "success",
        "data": {"response": f"Resposta simulada para: {request.get('query', '')}"},
        "metadata": {"model": request.get("model", "gpt-4o"), "tokens": 150},
    }
```

### Passo 3 — Garanta formato consistente de response

Todo endpoint retorna o mesmo schema para facilitar consumo:

```python
def ensure_response_format(self, response: dict) -> dict:
    """Garante formato consistente: {status, data, metadata}."""
    return {
        "status": response.get("status", "success"),
        "data": response.get("data", {}),
        "metadata": response.get("metadata", {}),
        "timestamp": datetime.now().isoformat(),
    }
```

### Passo 4 — Gere Docker config

Crie Dockerfile e docker-compose.yml automaticamente:

```python
def generate_docker_config(self) -> str:
    """Gera Dockerfile + docker-compose.yml."""
    dockerfile = """FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn pydantic
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    compose = """version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
"""
    
    return f"# Dockerfile\n{dockerfile}\n\n# docker-compose.yml\n{compose}"
```

### Passo 5 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="API de agente IA")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--serve", action="store_true", help="Inicia servidor HTTP")
    args = parser.parse_args()
    
    api = AgentAPI()
    
    if args.serve:
        print(f"🚀 Servidor rodando em http://localhost:{args.port}")
        print(f"📚 Docs em http://localhost:{args.port}/docs")
        # Em produção: uvicorn main:app --host 0.0.0.0 --port {args.port}
    else:
        # Testa com request simulado
        test_request = {"query": "Como funciona o reembolso?", "model": "gpt-4o"}
        middleware = api.add_middleware_timing()
        result = middleware(test_request)
        print(json.dumps(result, indent=2, ensure_ascii=False))
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `AgentAPI` valida input com regras obrigatórias (query, model, temperature)
- [ ] Middleware mede tempo por etapa (validação, processamento, formatação)
- [ ] `ensure_response_format()` retorna schema consistente {status, data, metadata}
- [ ] `generate_docker_config()` produz Dockerfile + docker-compose.yml funcionais
- [ ] CLI aceita `--port` e `--serve` para iniciar servidor

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

## Teste seu código

```bash
python agent_api.py --port 8000
docker-compose up --build
curl http://localhost:8000/health
```

## 🪨 Travei? Pistas em camadas

Funciona igualzinho às pistas dos exercícios: quando um requisito travar, abra **só o próximo nível** que você precisar — nunca todos de uma vez. O objetivo é destravar o raciocínio, não entregar a resposta mastigada.

> **Nível 1 — Direção.** Cada requisito mapeia para um `Passo` do guia acima. Antes de descer de nível, releia o Passo correspondente; na maioria das vezes ele já tem o esqueleto da função.

<details>
<summary><b>Nível 2 — A ideia por requisito</b> (clique para abrir)</summary>

- **`validate_input()`:** cheque campos obrigatórios e tipos manualmente (sem Pydantic real): retorne `{valid, errors}` acumulando faltas. É a primeira linha de defesa antes de processar.
- **`add_middleware_timing()`:** envolva o handler: registre `time.perf_counter()` antes/depois, gravem `duration_ms` e anexe em `self.request_log`. Middleware decorativo, não altera o payload.
- **`ensure_response_format()`:** normalize toda saída para o envelope `{status, data, metadata}`. Se vier fora do formato, encaixe; garanta que `metadata` traz timing/request_id.
- **`generate_docker_config()`:** devolva uma string com Dockerfile + docker-compose (FROM python, COPY, EXPOSE, CMD uvicorn). É geração de texto, não execução — basta montar as linhas certas.
- **fluxo do request:** a ordem canônica é validate → process → ensure_format, tudo cronometrado pelo middleware. Pense na API como uma esteira com essas 4 estações.

</details>

<details>
<summary><b>Nível 3 — Quase solução</b> (abra só se o nível 2 não bastou)</summary>

```python
def ensure_response_format(self, response):
    return {
        "status": response.get("status", "ok"),
        "data": response.get("data", response),
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "duration_ms": response.get("duration_ms", 0),
        },
    }
```

Encaixe `ensure_response_format()` como último estagio: o middleware mede o tempo, `validate_input()` barra o ruim na entrada, e esse método garante que toda saída sai com o mesmo envelope.

</details>

## Desafios extras

- [ ] Authentication com JWT
- [ ] Rate limiting por IP
- [ ] OpenAPI/Swagger docs
- [ ] Health check endpoint
