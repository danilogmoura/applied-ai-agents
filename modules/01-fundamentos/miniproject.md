# 🏗️ Mini-Projeto Integrador — Fundamentos IA/LLM

> **Objetivo:** Construir uma ferramenta CLI que calcula custo/token de prompts reais.

## O que você vai construir

Um programa Python `prompt_analyzer.py` que:

1. **Tokeniza** texto (simulado — use regex simples)
2. **Estima custo** baseado no modelo escolhido
3. **Valida estrutura** de prompt (system/user/assistant)
4. **Detecta problemas** (prompt muito longo, temperatura alta, etc.)

## Requisitos

```python
# Estrutura mínima esperada:

class PromptAnalyzer:
    def estimate_tokens(self, text: str, language: str = "en") -> int:
        """Estimar tokens (~4 chars/token EN, ~2 chars/token PT)."""
        ...
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calcular custo. Preços por 1K tokens:
           gpt-4o: input $0.01, output $0.03
           gpt-4o-mini: input $0.0015, output $0.006
           claude-3.5: input $0.003, output $0.015
        """
        ...
    
    def validate_prompt(self, messages: list) -> dict:
        """Validar estrutura: primeiro msg é system/user, content não vazio."""
        ...
    
    def analyze(self, prompt: list, model: str = "gpt-4o") -> dict:
        """Análise completa: tokens, custo, validação, warnings."""
        ...
```

## 📖 Guia Passo a Passo

Siga estes passos para construir o `prompt_analyzer.py`:

### Passo 1 — Crie a classe base

Crie um arquivo `prompt_analyzer.py` e defina a classe `PromptAnalyzer`. Use `argparse` para receber inputs pelo terminal:

```python
import argparse

class PromptAnalyzer:
    def __init__(self):
        # Preços por 1K tokens (fonte: openai.com/pricing)
        self.prices = {
            "gpt-4o": {"input": 0.01, "output": 0.03},
            "gpt-4o-mini": {"input": 0.0015, "output": 0.006},
            "claude-3.5": {"input": 0.003, "output": 0.015},
        }
```

### Passo 2 — Implemente a tokenização simulada

Use regex simples para contar tokens. A regra prática é:

- Inglês: ~4 caracteres por token
- Português: ~2 caracteres por token (mais complexo, menos chars/token)

```python
import re

def estimate_tokens(self, text: str, language: str = "en") -> int:
    if language == "pt":
        return len(re.findall(r'\w+', text))  # conta palavras
    return len(text) // 4  # regra EN
```

### Passo 3 — Calcule o custo

Multiplique tokens pelo preço do modelo. Converta tokens → "por 1K tokens":

```python
def calculate_cost(self, tokens: int, model: str) -> float:
    price_per_1k = self.prices[model]["input"]
    return (tokens / 1000) * price_per_1k
```

### Passo 4 — Valide a estrutura do prompt

Um prompt válido precisa:

- Primeira mensagem ser `system` ou `user`
- Campo `content` não vazio
- Lista de mensagens (não string única)

```python
def validate_prompt(self, messages: list) -> dict:
    errors = []
    if not messages:
        errors.append("Lista vazia")
    elif messages[0]["role"] not in ("system", "user"):
        errors.append("Primeira msg deve ser system ou user")
    return {"valid": len(errors) == 0, "errors": errors}
```

### Passo 5 — Monte a análise completa

Combine todos os métodos anteriores em `analyze()`. Retorne um dict com:

- `tokens`, `custo`, `valido`, `warnings`

### Passo 6 — Adicione CLI com argparse

Permite rodar via terminal:

```python
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analisador de prompts IA")
    parser.add_argument("--text", help="Texto para analisar")
    parser.add_argument("--model", default="gpt-4o")
    args = parser.parse_args()
    
    analyzer = PromptAnalyzer()
    result = analyzer.analyze([{"role": "user", "content": args.text}], args.model)
    print(result)
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `estimate_tokens()` estima tokens (~4 chars/token EN, ~2 PT)
- [ ] `calculate_cost()` aplica os preços por 1K tokens dos 3 modelos
- [ ] `validate_prompt()` checa 1ª mensagem e content não vazio
- [ ] `analyze()` retorna dict com tokens, custo, validação e warnings
- [ ] CLI aceita `--text`/`--prompt-file`, `--language` e `--model`
- [ ] Código roda via `python prompt_analyzer.py --text "..." --language pt`

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

## Teste seu código

```bash
python prompt_analyzer.py --text "Como funciona o reembolso?" --language pt
python prompt_analyzer.py --prompt-file example.json --model gpt-4o
```

## Desafios extras (opcionais)

- [ ] Suporte a múltiplos arquivos JSON
- [ ] Exportar relatório em CSV
- [ ] Comparar custos entre modelos lado a lado
- [ ] Detectar prompt injection básico
