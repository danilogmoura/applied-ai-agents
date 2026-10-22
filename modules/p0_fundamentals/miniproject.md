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

## Critérios de avaliação

| Critério | Básico | Avançado |
| ---------- | -------- | ---------- |
| Tokenização | Regex simples | BPE simulado com vocabulário |
| Custos | 3 modelos | + custom pricing |
| Validação | Regras básicas | + regras configuráveis |
| CLI | argparse mínimo | + subcomandos + colorido |
