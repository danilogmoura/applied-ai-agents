# 🏗️ Mini-Projeto Integrador — Ticket Classifier

> **Objetivo:** Construir um classificador de tickets de suporte usando prompts com LLM.

## 📖 Guia passo a passo

Leia [`miniproject_guide.md`](miniproject_guide.md) para um tutorial completo, ou use o [`ticket_classifier_skeleton.py`](ticket_classifier_skeleton.py) como ponto de partida.

## O que você vai construir

Um sistema `TicketClassifier` que:

1. **Classifica** tickets por prioridade (URGENTE, NORMAL, BAIXA)
2. **Estima custo** de processamento em lote
3. **Processa batch** de tickets com retry
4. **Lida com erros** (rate limit, timeout, auth error)

## Requisitos mínimos (obrigatórios)

- [ ] Classe `TicketClassifier` com método `classify()`
- [ ] Usa `temperature=0` para classificação consistente
- [ ] Retorna dict com `category`, `confidence`, `suggested_action`
- [ ] Calcula custo estimado por chamada usando `shared.cost`
- [ ] Implementa `dry_run()` para testar sem gastar tokens

## Requisitos avançados (opcionais)

- [ ] Batch processing com `process_batch()`
- [ ] Retry com backoff exponencial (`time.sleep(2 ** attempt)`)
- [ ] Error handling diferenciado (rate limit vs auth error)
- [ ] Modo dry run funcional (sem chamar API real)

## Como testar

```bash
# Modo dry run — sem gastar tokens (recomendado para começar)
python modules/p0_first_llm/ticket_classifier_skeleton.py --dry-run

# Com API real
python modules/p0_first_llm/ticket_classifier_skeleton.py --input ../data/sample_docs.json

# Interativo
python modules/p0_first_llm/ticket_classifier_skeleton.py
```

## Desafios extras

- [ ] Cache de classificações repetidas
- [ ] Dashboard simples de métricas (accuracy estimada, custo/hora)
- [ ] Exportar relatório de erros
- [ ] Suporte a múltiplos modelos (configurável via env var)
