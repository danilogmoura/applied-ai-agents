# 🏗️ Mini-Projeto Integrador — Safety & Guardrails

> **Objetivo:** Construir um sistema de segurança completo com guardrails.

## O que você vai construir

Um guardrail `safety_system.py` (classe `SafetyGuardrails`) que:

1. **Sanitiza** inputs (SQL injection, XSS, prompt injection)
2. **Valida** outputs (vazamento de dados, conteúdo inadequado)
3. **Aplica** regras de guardrail configuráveis
4. **Implementa** rate limiting e jailbreak detection

## Requisitos

> ℹ️ **Arquitetura de referência:** No `run.py`, a segurança é composta por várias classes: `PromptInjectionDetector` (detecta injection/jailbreak), `ContentFilter`, `OutputValidator` e a classe principal `SafetyGuardrails` (orquestra tudo). Aqui você pode começar com uma classe única `SafetyGuardrails`; quando quiser, extraia os detectores para classes separadas, como na referência.

```python
class SafetyGuardrails:
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

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com sanitização de input

Detecte SQL injection, XSS e prompt injection:

```python
import re
from typing import List, Dict

class SafetyGuardrails:
    def __init__(self):
        self.sql_patterns = [
            r"(?i)(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER)\b.*\b(FROM|INTO|TABLE|SET|WHERE)\b)",
            r"(?i)(';\s*(DROP|DELETE|UPDATE|INSERT))",
            r"(--|#|\/\*)\s",
            r"(?i)(OR|AND)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+",
        ]
        
        self.xss_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
        ]
        
        self.prompt_injection_patterns = [
            r"(?i)(ignore\s+previous\s+instructions)",
            r"(?i)(you\s+are\s+now\s+)",
            r"(?i)(act\s+as\s+a\s+(ninja|pirate|unrestricted))",
            r"(?i)(this\s+is\s+not\s+for\s+production)",
            r"(?i)(reveal\s+your\s+(system|internal|original)\s+prompt)",
        ]
    
    def sanitize_input(self, text: str) -> Dict:
        """Detectar SQL injection, XSS, prompt injection."""
        threats = []
        
        # Verifica SQL injection
        for pattern in self.sql_patterns:
            if re.search(pattern, text):
                threats.append({
                    "type": "sql_injection",
                    "severity": "HIGH",
                    "pattern": pattern,
                    "message": "Possível SQL injection detectado",
                })
                break
        
        # Verifica XSS
        for pattern in self.xss_patterns:
            if re.search(pattern, text):
                threats.append({
                    "type": "xss",
                    "severity": "MEDIUM",
                    "pattern": pattern,
                    "message": "Possível ataque XSS detectado",
                })
                break
        
        # Verifica prompt injection
        for pattern in self.prompt_injection_patterns:
            if re.search(pattern, text):
                threats.append({
                    "type": "prompt_injection",
                    "severity": "HIGH",
                    "pattern": pattern,
                    "message": "Possível prompt injection detectado",
                })
                break
        
        return {
            "safe": len(threats) == 0,
            "threats": threats,
            "num_threats": len(threats),
        }
```

### Passo 2 — Implemente validação de output

Garanta que o output não vaze dados sensíveis:

```python
    def validate_output(self, text: str) -> List[Dict]:
        """Validar output: sem API keys, sem PII, sem system prompt."""
        issues = []
        
        # Detecta API keys
        api_key_pattern = r"(?:sk-[a-zA-Z0-9]{40}|AIza[Sy-Za-z0-9]{35})"
        if re.search(api_key_pattern, text):
            issues.append({
                "type": "api_key_leak",
                "severity": "CRITICAL",
                "message": "Possível chave de API detectada no output",
            })
        
        # Detecta PII (CPF, email, telefone)
        cpf_pattern = r"\d{3}\.?\d{3}\.?\d{3}-?\d{2}"
        if re.search(cpf_pattern, text):
            issues.append({
                "type": "pii_cpf",
                "severity": "HIGH",
                "message": "Possível CPF vazado no output",
            })
        
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        if re.search(email_pattern, text):
            issues.append({
                "type": "pii_email",
                "severity": "MEDIUM",
                "message": "Possível email vazado no output",
            })
        
        phone_pattern = r"\(?[0-9]{2}\)?[\s]-?[0-9]{4}[,-]?[0-9]{4}"
        if re.search(phone_pattern, text):
            issues.append({
                "type": "pii_phone",
                "severity": "HIGH",
                "message": "Possível telefone vazado no output",
            })
        
        # Detecta system prompt leak
        system_indicators = [
            "system prompt",
            "you are an assistant",
            "your instructions are",
        ]
        text_lower = text.lower()
        for indicator in system_indicators:
            if indicator in text_lower:
                issues.append({
                    "type": "system_prompt_leak",
                    "severity": "HIGH",
                    "message": f"Indicativo de system prompt vazado: '{indicator}'",
                })
                break
        
        return issues
    
    def is_output_safe(self, text: str) -> bool:
        """Verifica se output está limpo."""
        return len(self.validate_output(text)) == 0
```

### Passo 3 — Implemente regras de guardrail configuráveis

```python
    def check_guardrails(self, text: str, rules: List[Dict]) -> List[Dict]:
        """Verificar texto contra regras de guardrail."""
        violations = []
        
        for rule in rules:
            rule_type = rule.get("type")
            pattern = rule.get("pattern")
            severity = rule.get("severity", "MEDIUM")
            
            if rule_type == "regex" and pattern:
                if re.search(pattern, text):
                    violations.append({
                        "rule": rule.get("name", "unnamed"),
                        "type": "regex_violation",
                        "severity": severity,
                        "message": f"Violação da regra '{rule.get('name')}': {rule.get('description', '')}",
                    })
            
            elif rule_type == "keyword" and pattern:
                keywords = [k.strip().lower() for k in pattern.split(",")]
                text_lower = text.lower()
                for keyword in keywords:
                    if keyword in text_lower:
                        violations.append({
                            "rule": rule.get("name", "unnamed"),
                            "type": "keyword_violation",
                            "severity": severity,
                            "message": f"Palavra proibida detectada: '{keyword}'",
                        })
                        break
            
            elif rule_type == "length":
                max_len = rule.get("max_length", 1000)
                min_len = rule.get("min_length", 0)
                if len(text) > max_len:
                    violations.append({
                        "rule": rule.get("name", "unnamed"),
                        "type": "length_violation",
                        "severity": severity,
                        "message": f"Texto excede limite de {max_len} caracteres",
                    })
                elif len(text) < min_len:
                    violations.append({
                        "rule": rule.get("name", "unnamed"),
                        "type": "length_violation",
                        "severity": severity,
                        "message": f"Texto abaixo do mínimo de {min_len} caracteres",
                    })
        
        return violations
```

### Passo 4 — Implemente rate limiting

```python
    from datetime import datetime
    from collections import defaultdict
    
    def __init__(self):
        # ... (patterns acima)
        self.request_log = defaultdict(list)  # user_id -> [timestamps]
    
    def enforce_rate_limit(self, user_id: str, 
                           max_requests: int = 10,
                           window_seconds: int = 60) -> Dict:
        """Rate limiting por usuário com sliding window."""
        now = datetime.now()
        
        # Remove requests antigos fora da janela
        self.request_log[user_id] = [
            ts for ts in self.request_log[user_id]
            if (now - ts).total_seconds() <= window_seconds
        ]
        
        current_count = len(self.request_log[user_id])
        
        if current_count >= max_requests:
            return {
                "allowed": False,
                "reason": "rate_limit_exceeded",
                "current_count": current_count,
                "max_requests": max_requests,
                "window_seconds": window_seconds,
                "retry_after": window_seconds,
            }
        
        # Registra request
        self.request_log[user_id].append(now)
        
        return {
            "allowed": True,
            "remaining": max_requests - current_count - 1,
            "max_requests": max_requests,
        }
```

### Passo 5 — Implemente jailbreak detection

```python
    def detect_jailbreak(self, text: str) -> Dict:
        """Detectar tentativas de jailbreak/prompt injection avançado."""
        indicators = []
        text_lower = text.lower()
        
        # Padrões comuns de jailbreak
        jailbreak_patterns = {
            "role_play": [
                r"(?i)(pretend\s+you\s+are|act\s+like\s+a|imagine\s+you're)",
                r"(?i)(dungeon\s+master|dad\s+joke|crazy\s|pirate|ninja)",
            ],
            "hypothetical": [
                r"(?i)(what\s+if\s+i\s+(said|asked|wanted))",
                r"(?i)(in\s+a\s(hypothetical|fictional|theoretical)\s(scenario|world|universe))",
                r"(?i)(for\s(research|academic|educational)\s(purpose|purposes))",
            ],
            "authority": [
                r"(?i)(my\s(boss|parent|teacher|lawyer)\s(said|told\sme|allowed))",
                r"(?i)(this\s(is|was)\sauthorized|official\srequest)",
                r"(?i)(you\s(must|have\sto|need\sto)\sfollow\smy\sinstructions)",
            ],
            "reversal": [
                r"(?i)(reverse\s(your|the)\s(rules|instructions|policy))",
                r"(?i)(disregard\s(all|previous|the)\s(instructions|guidelines|warnings))",
                r"(?i)(ignore\s(allll|all|every)\s(instruction|rule|policy|warning))",
            ],
        }
        
        for category, patterns in jailbreak_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    indicators.append({
                        "category": category,
                        "pattern": pattern,
                        "confidence": 0.8 if category == "reversal" else 0.6,
                    })
                    break
        
        # Score composto
        score = sum(ind["confidence"] for ind in indicators)
        is_jailbreak = score > 0.5
        
        return {
            "is_jailbreak": is_jailbreak,
            "score": round(score, 2),
            "indicators": indicators,
            "num_indicators": len(indicators),
            "action": "BLOCK" if is_jailbreak else "ALLOW",
        }
```

### Passo 6 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sistema de segurança para IA")
    parser.add_argument("--input", help="Arquivo com input para testar")
    parser.add_argument("--text", help="Texto direto para testar")
    parser.add_argument("--rules", help="Arquivo de regras guardrail (JSON)")
    parser.add_argument("--batch", help="Arquivo com batch de testes (JSON)")
    parser.add_argument("--output", help="Arquivo de output do relatório")
    args = parser.parse_args()
    
    system = SafetyGuardrails()
    
    if args.text:
        # Sanitiza input
        sanitization = system.sanitize_input(args.text)
        print(f"\n🔍 Sanitização:")
        print(f"   Safe: {sanitization['safe']}")
        print(f"   Threats: {sanitization['num_threats']}")
        for threat in sanitization["threats"]:
            print(f"   ⚠️  {threat['type']} ({threat['severity']}): {threat['message']}")
        
        # Detecta jailbreak
        jb = system.detect_jailbreak(args.text)
        print(f"\n🔒 Jailbreak Detection:")
        print(f"   Is jailbreak: {jb['is_jailbreak']}")
        print(f"   Score: {jb['score']}")
        print(f"   Action: {jb['action']}")
    
    elif args.batch:
        with open(args.batch) as f:
            test_cases = json.load(f)
        
        report = []
        for i, case in enumerate(test_cases):
            result = system.sanitize_input(case.get("input", ""))
            report.append({
                "case": i + 1,
                "input": case.get("input", ""),
                "safe": result["safe"],
                "threats": result["num_threats"],
            })
        
        output_str = json.dumps(report, indent=2, ensure_ascii=False)
        print(output_str)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_str)
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `sanitize_input()` detecta SQL injection, XSS e prompt injection com regex
- [ ] `validate_output()` verifica vazamento de API keys, PII (CPF, email, telefone), system prompt
- [ ] `check_guardrails()` aplica regras configuráveis (regex, keyword, length)
- [ ] `enforce_rate_limit()` implementa sliding window por usuário
- [ ] `detect_jailbreak()` identifica role-play, hypothetical, authority, reversal com score composto
- [ ] CLI aceita `--text`, `--batch` e gera relatório JSON

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

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
