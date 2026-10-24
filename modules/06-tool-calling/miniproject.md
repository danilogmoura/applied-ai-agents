# 🏗️ Mini-Projeto Integrador — Tool Calling

> **Objetivo:** Construir um sistema de tool calling com aprovação humana (HITL).

## O que você vai construir

Um executor `tool_caller.py` (classe `ToolCallingAgent`) que:

1. **Gera** schema de ferramentas a partir de descrições
2. **Roteia** requests para a ferramenta correta
3. **Classifica** risco de cada operação
4. **Implementa** Human-in-the-Loop para operações sensíveis
5. **Lida** com erros de ferramentas (retry, fallback)

## Requisitos

```python
class ToolCallingAgent:
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

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com registry de ferramentas

Defina uma lista de ferramentas pré-configuradas que o sistema pode usar:

```python
import json
from datetime import datetime

class ToolCallingAgent:
    def __init__(self):
        # Registry de ferramentas disponíveis
        self.tools = {
            "check_balance": {
                "name": "check_balance",
                "description": "Consulta saldo atual de uma conta bancária",
                "params": {"account_id": {"type": "string", "required": True}},
                "risk_level": "low",
                "handler": self._handle_check_balance,
            },
            "transfer_money": {
                "name": "transfer_money",
                "description": "Transfere valor entre contas bancárias",
                "params": {
                    "from_account": {"type": "string", "required": True},
                    "to_account": {"type": "string", "required": True},
                    "amount": {"type": "float", "required": True},
                },
                "risk_level": "high",
                "handler": self._handle_transfer,
            },
            "list_transactions": {
                "name": "list_transactions",
                "description": "Lista transações recentes de uma conta",
                "params": {"account_id": {"type": "string", "required": True}, "limit": {"type": "int", "default": 10}},
                "risk_level": "low",
                "handler": self._handle_list_transactions,
            },
        }
        
        self.audit_log = []
    
    # Handlers simulados das ferramentas
    def _handle_check_balance(self, args):
        return {"balance": 1500.00, "currency": "BRL", "account": args["account_id"]}
    
    def _handle_transfer(self, args):
        return {"status": "success", "from": args["from_account"], "to": args["to_account"], "amount": args["amount"]}
    
    def _handle_list_transactions(self, args):
        return [{"date": "2024-10-01", "desc": "Pagamento", "amount": -50.00},
                {"date": "2024-10-05", "desc": "Depósito", "amount": 1000.00}]
```

### Passo 2 — Implemente geração de schema JSON

Cada ferramenta precisa de um schema que descreva seus parâmetros para o LLM:

```python
def generate_tool_schema(self, name: str, description: str, 
                         params: dict) -> dict:
    """Gera schema JSON no formato OpenAI function calling."""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": params,
                "required": [p for p, v in params.items() if v.get("required")],
            },
        },
    }
```

### Passo 3 — Roteie requests para ferramentas

Use keyword matching simples para simular a decisão do LLM sobre qual tool chamar:

```python
def route_request(self, user_input: str, tools: list = None) -> dict:
    """Determina qual tool usar baseado no input do usuário."""
    if tools is None:
        tools = list(self.tools.keys())
    
    user_input_lower = user_input.lower()
    
    # Keyword matching simples (em produção, o LLM faz isso)
    keywords = {
        "check_balance": ["saldo", "balance", "quanto tenho", "conta"],
        "transfer_money": ["transferir", "transfer", "enviar dinheiro", "pagar"],
        "list_transactions": ["transação", "transaction", "histórico", "history", "extrato"],
    }
    
    for tool_name, words in keywords.items():
        if any(word in user_input_lower for word in words) and tool_name in tools:
            return {
                "tool": tool_name,
                "confidence": 0.8,
                "matched_keywords": [w for w in words if w in user_input_lower],
            }
    
    return {"tool": None, "confidence": 0.0, "error": "Nenhuma tool correspondente encontrada"}
```

### Passo 4 — Classifique risco

```python
def classify_risk(self, tool_name: str, args: dict) -> str:
    """Classifica risco da operação."""
    if tool_name not in self.tools:
        return "unknown"
    
    # Overwrites podem aumentar risco
    if "amount" in args and args["amount"] > 10000:
        return "critical"
    
    return self.tools[tool_name]["risk_level"]
```

### Passo 5 — Implemente HITL

Para operações high/critical, peça aprovação humana:

```python
def execute_with_hitl(self, tool_name: str, args: dict) -> dict:
    """Executa com aprovação humana para high/critical."""
    risk = self.classify_risk(tool_name, args)
    
    if risk in ("high", "critical"):
        print(f"\n⚠️ AÇÃO REQUER APROVAÇÃO HUMANA")
        print(f"   Tool: {tool_name}")
        print(f"   Args: {args}")
        print(f"   Risco: {risk.upper()}")
        print(f"   Aprovar? (s/n): ", end="")
        
        # Simula aprovação (em produção, seria UI/webhook)
        approval = input().strip().lower()
        if approval != "s":
            return {"status": "rejected", "reason": "Aprovação humana negada"}
    
    # Executa a tool
    handler = self.tools[tool_name]["handler"]
    result = handler(args)
    
    # Registra no audit log
    self.audit_log.append({
        "timestamp": datetime.now().isoformat(),
        "tool": tool_name,
        "args": args,
        "risk": risk,
        "result": result,
    })
    
    return {"status": "executed", "risk": risk, "result": result}
```

### Passo 6 — Implemente retry com backoff exponencial

```python
import time
import random

def execute_with_retry(self, tool_name: str, args: dict, 
                       max_retries: int = 3) -> dict:
    """Executa com retry exponencial em caso de erro."""
    last_error = None
    
    for attempt in range(max_retries):
        try:
            handler = self.tools[tool_name]["handler"]
            result = handler(args)
            
            if attempt > 0:
                print(f"✅ Sucesso na tentativa {attempt + 1}")
            return {"status": "success", "attempts": attempt + 1, "result": result}
        
        except Exception as e:
            last_error = e
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"❌ Tentativa {attempt + 1} falhou: {e}")
            print(f"   Retry em {wait_time:.1f}s...")
            time.sleep(min(wait_time, 2))  # Cap em 2s para teste rápido
    
    return {"status": "failed", "attempts": max_retries, "error": str(last_error)}
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

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] Classe `ToolCallingAgent` tem registry de pelo menos 3 ferramentas
- [ ] `route_request()` identifica corretamente a tool baseada em keywords
- [ ] `classify_risk()` retorna low/medium/high/critical corretamente
- [ ] `execute_with_hitl()` bloqueia operações high/critical sem aprovação
- [ ] `execute_with_retry()` tenta até max_retries com backoff exponencial
- [ ] Audit log registra todas as execuções com timestamp

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.
