# 🏗️ Mini-Projeto Integrador — Tool Calling

> **Objetivo:** Construir um sistema de tool calling com aprovação humana (HITL).

## O que você vai construir

Um executor `tool_caller.py` que:

1. **Gera** schema de ferramentas a partir de descrições
2. **Roteia** requests para a ferramenta correta
3. **Classifica** risco de cada operação
4. **Implementa** Human-in-the-Loop para operações sensíveis
5. **Lida** com erros de ferramentas (retry, fallback)

## Requisitos

```python
class ToolCallingSystem:
    def generate_tool_schema(self, name: str, description: str, 
                             params: dict) -> dict:
        """Gerar schema JSON de uma ferramenta."""
        ...
    
    def route_request(self, user_input: str, tools: list) -> dict:
        """Determinar qual tool usar e com quais args."""
        ...
    
    def classify_risk(self, tool_name: str, args: dict) -> str:
        """Classificar risco: low/medium/high/critical."""
        ...
    
    def execute_with_hitl(self, tool_name: str, args: dict) -> dict:
        """Executar com aprovação humana para high/critical."""
        ...
    
    def execute_with_retry(self, tool_name: str, args: dict, 
                           max_retries: int = 3) -> dict:
        """Executar com retry exponencial em caso de erro."""
        ...
```

## Teste seu código

```bash
python tool_caller.py --input "Verificar saldo da conta" --tools banking.json
python tool_caller.py --batch requests.json --output execution_log.json
```

## Desafios extras

- [ ] Registry dinâmico de ferramentas
- [ ] Audit log de todas as execuções
- [ ] Rate limiting por ferramenta
- [ ] Dashboard de uso das ferramentas
