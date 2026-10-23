# 🏗️ Mini-Projeto Integrador — Ticket Classifier

> **Objetivo:** Construir um classificador de tickets de suporte usando prompts com LLM.

---

## Visão geral

Você vai construir um `TicketClassifier` que:

1. Recebe um ticket de suporte (assunto + descrição)
2. Envia para um LLM classificar a prioridade
3. Retorna categoria, confiança e ação sugerida
4. Calcula quanto custaria processar todos os tickets

Abra [`ticket_classifier_skeleton.py`](ticket_classifier_skeleton.py) como ponto de partida. Cada método tem comentários `TODO` indicando o que implementar.

> ℹ️ **Nota de nomes:** O `run.py` deste módulo é apenas uma **demonstração** e usa funções soltas (`classify_ticket()`, `classify_batch()`, `classify_with_rules()`). Já o seu mini-projeto deve seguir a **classe `TicketClassifier`** do esqueleto — que é a referência oficial. Não se confunda com a diferença: o esqueleto é o que você entrega.

### Estrutura da classe

```
TicketClassifier
├── __init__()              → configura o cliente OpenAI
├── classify()              → classifica UM ticket via LLM
├── estimate_batch_cost()   → calcula custo de N tickets
├── process_batch()         → classifica vários tickets com retry
├── handle_error()          → decide se retry ou falha
└── dry_run()               → simula sem chamar API (para testar)
```

---

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

---

## Passo a passo

### Passo 1: Inicializar o client

Substitua no `__init__`:

```python
self.client = None
```

Por:

```python
self.client = OpenAI(api_key=self.api_key)
```

### Passo 2: Implementar `classify()`

#### 2.1: Montar o prompt

O prompt diz ao LLM o que fazer. Precisa ser claro e pedir formato específico:

```python
prompt = f"""Você é um classificador de tickets de suporte.

Classifique a prioridade deste ticket e retorne APENAS um JSON válido com estas chaves:
- category: "URGENTE", "NORMAL" ou "BAIXA"
- confidence: número entre 0.0 e 1.0
- suggested_action: breve recomendação de ação

Ticket:
Assunto: {ticket_text.split(':')[0] if ':' in ticket_text else ticket_text}

Retorne APENAS o JSON, sem texto adicional."""
```

#### 2.2: Chamar a API

```python
response = self.client.chat.completions.create(
    model=self.model,
    messages=[{"role": "user", "content": prompt}],
    temperature=0,       # ← sempre 0 para classificação
    max_tokens=100,
)
```

#### 2.3: Extrair e retornar

```python
import json

raw = response.choices[0].message.content.strip()
result = json.loads(raw)  # converte string JSON → dict

return {
    "category": result["category"],
    "confidence": result["confidence"],
    "suggested_action": result["suggested_action"],
}
```

> ⚠️ **Importante:** Sempre use `temperature=0` para classificação. Isso garante consistência.

### Passo 3: Testar com um ticket

```python
classifier = TicketClassifier()
result = classifier.classify("Erro 500 na API, produção afetada")
print(result)
# Esperado: {'category': 'URGENTE', 'confidence': 0.95, 'suggested_action': '...'}
```

### Passo 4: Implementar `estimate_batch_cost()`

Já temos a lógica básica no esqueleto. Complete assim:

```python
def estimate_batch_cost(self, tickets: list[str], model: str = None) -> dict:
    model = model or self.model
    total_input = sum(count_tokens(t, model) for t in tickets)
    estimated_output = len(tickets) * 50  # ~50 tokens de resposta por ticket
    cost = estimate_cost(total_input, estimated_output, model=model)

    return {
        "model": model,
        "num_tickets": len(tickets),
        "total_input_tokens": total_input,
        "estimated_output_tokens": estimated_output,
        "total_cost_usd": cost,
        "cost_per_ticket_usd": cost / len(tickets) if tickets else 0,
    }
```

Teste:

```python
tickets = ["Erro 500", "Preço do plano", "Como funciona?"]
info = classifier.estimate_batch_cost(tickets)
print(f"Custo total: ${info['total_cost_usd']:.6f}")
```

### Passo 5: Testar modo dry run

O dry run usa regras simples (sem LLM) para validar a lógica:

```python
classifier = TicketClassifier()
result = classifier.dry_run("Erro 500 na API")
print(result)
# {'category': 'URGENTE', 'confidence': 0.9, 'suggested_action': 'Escalonar imediatamente'}
```

Use o dry run para testar antes de gastar tokens reais.

### Passo 6: Executar com arquivo de tickets

```bash
# Com API real
python modules/p0_first_llm/ticket_classifier_skeleton.py --input ../data/sample_docs.json

# Modo dry run (sem gastar tokens)
python modules/p0_first_llm/ticket_classifier_skeleton.py --dry-run
```

---

## Como testar

```bash
# Modo dry run — sem gastar tokens (recomendado para começar)
python modules/p0_first_llm/ticket_classifier_skeleton.py --dry-run

# Com API real
python modules/p0_first_llm/ticket_classifier_skeleton.py --input ../data/sample_docs.json

# Interativo
python modules/p0_first_llm/ticket_classifier_skeleton.py
```

---

## Checklist de validação

- [ ] `__init__` cria `OpenAI(api_key=...)` corretamente
- [ ] `classify()` usa `temperature=0`
- [ ] `classify()` retorna dict com `category`, `confidence`, `suggested_action`
- [ ] `estimate_batch_cost()` calcula custo real usando `shared.cost`
- [ ] `process_batch()` tem retry com backoff exponencial
- [ ] `dry_run()` funciona sem chamar API
- [ ] Código roda via `python ticket_classifier_skeleton.py --dry-run`

---

## Desafios extras

- [ ] Cache de classificações repetidas
- [ ] Dashboard simples de métricas (accuracy estimada, custo/hora)
- [ ] Exportar relatório de erros
- [ ] Suporte a múltiplos modelos (configurável via env var)

---

## Dicas

1. **Sempre teste com dry run primeiro** — evita gastar tokens enquanto debuga.
2. **Use `temperature=0` para classificação** — garante resultado consistente.
3. **Leia erros do terminal** — `AuthenticationError` = chave errada, `RateLimitError` = muito rápido.
4. **Monitore custos** — use `estimate_batch_cost()` antes de processar batches grandes.
