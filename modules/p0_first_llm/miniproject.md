# 🏗️ Mini-Projeto Integrador — First LLM Experience

> **Objetivo:** Construir um classificador de tickets de suporte usando prompts.

## O que você vai construir

Um sistema `ticket_classifier.py` que:

1. **Classifica** tickets por categoria (financeiro, técnico, geral)
2. **Estima custo** de processamento em lote
3. **Processa batch** de tickets com retry
4. **Lida com erros** (rate limit, timeout, invalid response)

## Requisitos

```python
class TicketClassifier:
    def classify(self, ticket_text: str) -> dict:
        """Classificar ticket: category, confidence, suggested_action."""
        ...
    
    def estimate_batch_cost(self, tickets: list, model: str = "gpt-4o-mini") -> dict:
        """Estimar custo total do batch."""
        ...
    
    def process_batch(self, tickets: list, max_retries: int = 3) -> list:
        """Processar batch com retry e fallback."""
        ...
    
    def handle_error(self, error: Exception, attempt: int) -> bool:
        """Decidir se retry ou falhar. Rate limit → backoff exponencial."""
        ...
```

## Teste seu código

```bash
python ticket_classifier.py --input sample_tickets.json --model gpt-4o-mini
python ticket_classifier.py --batch large_dataset.csv --output results.json
```

## Desafios extras

- [ ] Cache de classificações repetidas
- [ ] Dashboard simples de métricas (accuracy estimada, custo/hora)
- [ ] Exportar relatório de erros
- [ ] Modo "dry run" sem chamar API real
