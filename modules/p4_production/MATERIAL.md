# Material Didático — P4: Produção (API REST com FastAPI)

## Conceitos Fundamentais

### De Script a Produto

Até agora, executamos scripts Python isolados. Em produção, precisamos de:

| Script Local | API de Produção |
| ------------- | ----------------- |
| Executa e para | Fica rodando 24/7 |
| Um usuário por vez | Múltiplos usuários simultâneos |
| Sem autenticação | Com validação e segurança |
| Logs no terminal | Logs estruturados em arquivo |
| Sem versionamento | Com versionamento e docs |

### FastAPI — Framework Moderno

FastAPI é um framework web para Python que oferece:

1. **Autodocumentação**: Swagger UI automática em `/docs`
2. **Validação automática**: Pydantic valida requests automaticamente
3. **Type hints**: Tipagem forte com inferência de schemas
4. **Async/await**: Suporte nativo a operações assíncronas
5. **Performance**: Uma das frameworks Python mais rápidas (comparável a Go/Node.js)

### Fluxo de uma Requisição na API

```mermaid
sequenceDiagram
    participant Client as 👤 Cliente<br/>(curl / HTTP req)
    participant Middleware as 🔧 Middleware<br/>(timing, request-id)
    participant Router as 📋 Router<br/>(validação Pydantic)
    participant AgentService as ⚡ AgentService<br/>(LLM call)
    participant OpenAI as 🤖 OpenAI API<br/>gpt-4o-mini
    
    Client->>Middleware: HTTP Request
    Middleware->>Router: timing + request-id
    Router->>AgentService: validated data
    AgentService->>OpenAI: LLM call
    OpenAI-->>AgentService: Response
    AgentService-->>Router: Result
    Router-->>Middleware: Serialized
    Middleware-->>Client: Final Response
```

Cada requisição passa por 4 camadas antes de chegar ao LLM.

```python
@app.post("/chat", response_model=AgentResponse)
async def chat(request: AgentRequest) -> AgentResponse:
    # request já é validado e tipado aqui
    result = await agent_service.process_request(...)
    return result  # FastAPI serializa automaticamente
```

### Modelos Pydantic como Contrato

Os modelos definem o contrato entre cliente e servidor:

```python
class AgentRequest(BaseModel):
    message: str                    # Obrigatório
    model: str = "gpt-4o-mini"      # Opcional com default
    use_tools: bool = False         # Booleano
    max_iterations: int = Field(ge=1, le=10, default=3)  # Validado

class AgentResponse(BaseModel):
    answer: str
    tokens_input: int
    tokens_output: int
    cost_usd: float
    conversation_id: str
```

Isso garante que:

- Requests inválidos são rejeitados antes de chegar à lógica
- Clients sabem exatamente o formato esperado
- Docs Swagger são gerados automaticamente

### Middleware de Monitoramento

Middleware intercepta todas as requisições para adicionar observabilidade:

```python
class MonitoringMiddleware:
    async def __call__(self, request, call_next):
        start = time.time()
        request_id = str(uuid.uuid4())[:8]
        
        # Adiciona headers de tracking
        response = await call_next(request)
        
        elapsed = time.time() - start
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = f"{elapsed*1000:.0f}ms"
        
        return response
```

Headers customizados permitem:

- Rastrear cada request individualmente nos logs
- Medir latência por endpoint
- Debugar problemas em produção

### Docker — Empacotamento Consistente

Docker garante que o código roda igual em qualquer ambiente:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -e ".[dev]"
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Vantagens:

- Mesma imagem local e produção
- Dependências congeladas
- Isolamento de ambientes

### Como o Docker Realmente Funciona

Docker **não é uma VM**. Ele não virtualiza hardware — usa recursos do kernel Linux:

```mermaid
flowchart TB
    subgHost["Host OS (Linux)"]
    subgC1["Container 1"]
    subgC2["Container 2 (isolado!)"]
    
    C1App["App Python\npip install"] -->|Isolado por| NS["Namespaces\nPID, network, filesystem"]
    C1App -->|Limitado por| CG["Cgroups\nCPU, memory, I/O"]
    NS --> Kernel["Kernel Linux\nUnionFS layers"]
    CG --> Kernel
    
    style C1App fill:#9f9,stroke:#333
    style NS fill:#ff9,stroke:#333
    style CG fill:#ff9,stroke:#333
```

**Namespaces**: cada container acha que tem seu próprio sistema de arquivos, rede e processos. É ilusão — o kernel separa tudo.

**Cgroups**: controlam quanto CPU/memória um container pode usar. Sem eles, um container poderia consumir todo o host.

**Layers**: cada `RUN`/`COPY` no Dockerfile cria uma layer read-only. Se você muda só o código (`COPY . .`), as camadas de dependência (`pip install`) são reutilizadas → build mais rápido.

Por isso `docker build` é lento na primeira vez (baixa todas as layers) mas rápido depois (cache de layers).

### docker-compose — Infraestrutura Completa

```yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    depends_on: [chromadb]
  
  chromadb:
    image: chromadb/chroma:latest
    volumes: [chroma_data:/chroma/chroma]
```

Orquestra múltiplos serviços com dependências e volumes persistentes.

---

## Exercício Prático

Execute `python modules/p4_production/run.py --serve` e observe:

1. A API iniciando no port 8000
2. Docs Swagger em <http://localhost:8000/docs>
3. Teste endpoints via curl ou interface interativa do Swagger
4. Métricas acumuladas em `/metrics`

Ou use Docker:

```bash
docker-compose up --build
```

## Perguntas para Reflexão

1. Por que usar async/await na API? Quando isso faz diferença vs quando não faz?
2. Se você tivesse 1000 requisições por segundo, que mudanças seriam necessárias?
3. Como você implementaria autenticação (API keys, JWT) nesta API?

---

## Referências

### Livros

- **"FastAPI in Action"** by Juan J. Borreguero — Guia completo do framework
- **"Docker Deep Dive"** by Nigel Poulton — Fundamentos de containers

### Documentação Oficial

- [FastAPI Documentation](https://fastapi.tiangolo.com/) — Docs oficiais
- [Pydantic v2 Models](https://docs.pydantic.dev/latest/concepts/models/) — Validação de dados
- [Uvicorn ASGI Server](https://www.uvicorn.org/) — Servidor assíncrono

### Tutoriais

- [Building Production APIs with FastAPI](https://testdriven.io/blog/fastapi-docker/) — TestDriven.io
- [Docker Compose Networking](https://docs.docker.com/compose/networking/) — Docker Docs
