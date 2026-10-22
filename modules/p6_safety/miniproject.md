# 🏗️ Mini-Projeto Integrador — Safety & Guardrails

> **Objetivo:** Construir um sistema de segurança completo com guardrails.

## O que você vai construir

Um guardrail `safety_system.py` que:

1. **Sanitiza** inputs (SQL injection, XSS, prompt injection)
2. **Valida** outputs (vazamento de dados, conteúdo inadequado)
3. **Aplica** regras de guardrail configuráveis
4. **Implementa** rate limiting e jailbreak detection

## Requisitos

```python
class SafetySystem:
    def sanitize_input(self, text: str) -> dict:
        """Detectar SQL injection, XSS, prompt injection."""
        ...
    
    def validate_output(self, text: str) -> list:
        """Validar output: sem API keys, sem PII, sem system prompt."""
        ...
    
    def check_guardrails(self, text: str, rules: list) -> list:
        """Verificar texto contra regras de guardrail."""
        ...
    
    def enforce_rate_limit(self, user_id: str, max_requests: int = 10, 
                           window_seconds: int = 60) -> bool:
        """Rate limiting por usuário."""
        ...
    
    def detect_jailbreak(self, text: str) -> bool:
        """Detectar tentativas de jailbreak/prompt injection."""
        ...
```

## Teste seu código

```bash
python safety_system.py --input malicious_prompt.txt --rules guardrails.json
python safety_system.py --batch test_cases.json --output report.json
```

## Desafios extras

- [ ] Web UI para testar guardrails
- [ ] Alertas em tempo real (Slack/Discord webhook)
- [ ] Auto-update de patterns de jailbreak
- [ ] Audit log completo
