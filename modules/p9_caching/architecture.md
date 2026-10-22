# 🏗️ Architecture Design — Cache Layer

> **Desafio:** Projete uma camada de cache para otimizar custos e latência em sistema de IA.

## Cenário

Uma aplicação de chatbot precisa reduzir custos e melhorar performance:

- **50K queries/mês** (~1667/hora)
- **30% das queries são repetidas** (FAQ, comandos comuns)
- **Orçamento**: máximo $300/mês em API calls
- **SLA**: latência < 2s para respostas cacheadas
- **Requisito**: cache invalida quando dados subjacentes mudam

---

## Entregáveis

### 1. Diagrama da Arquitetura

Descreva o fluxo do cache layer:

```
[Usuário] → [Cache Proxy] → [LLM API]
              ↑         ↘
         [Lookup]    [Fill + Store]
              ↓
      [Eviction Policy]
```

Defina:

- Quantas chamadas ao LLM por query (com cache)?
- Onde o cache fica (memória, Redis, banco)?
- Quem decide quando evictar?

### 2. Estratégia de Key Generation

Para cada tipo de query, defina a chave de cache:

| Tipo de Query | Chave de Cache | Justificativa |
| --------------- | ---------------- | --------------- |
| Pergunta exata | hash(prompt + system_prompt) | ? |
| Busca similar | hash(normalize(prompt)) | ? |
| Comandos com params | hash(cmd + sorted(params)) | ? |
| Dados dinâmicos | hash(data_version) | ? |

Explique como lida com colisões de hash.

### 3. Política de Eviction

Defina os parâmetros do cache:

| Parâmetro | Valor | Justificativa |
| ----------- | ------- | --------------- |
| max_size | ? entradas | ? |
| TTL padrão | ? minutos | ? |
| TTL FAQ | ? horas | ? |
| Eviction policy | LRU / LFU / FIFO | ? |
| Memory limit | ? MB | ? |

Justifique LRU vs LFU para este cenário (queries frequentes vs únicas).

### 4. ROI do Cache

Calcule o impacto financeiro:

| Métrica | Sem Cache | Com Cache | Diferença |
| --------- | ----------- | ----------- | ----------- |
| Queries totais | 50K | 50K | - |
| Queries ao LLM | 50K | ? | ? |
| Tokens input | ? | ? | ? |
| Tokens output | ? | ? | ? |
| Custo mensal | ? | ? | ? |
| Latência média | ? | ? | ? |

Verifique: economia > 30%? Dentro do orçamento ($300/mês)?

---

## Checklist de Validação

- [ ] Fluxo completo cache proxy definido
- [ ] Estratégias de key generation cobrem todos tipos de query
- [ ] Política de eviction justificada (LRU/LFU/FIFO)
- [ ] ROI calculado com números realistas
- [ ] Economia > 30% dos custos
- [ ] Latência cache dentro do SLA (< 2s)

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
| ---------- | -------------- | --------- | ----------- |
| **Key Gen** | Cobertura completa por tipo | Apenas exata | Sem estratégia |
| **Eviction** | Parâmetros justificados | Valores padrão | Sem política |
| **ROI** | Números detalhados e realistas | Estimativa global | Sem cálculo |
| **Trade-offs** | Analisa custo/consistência | Ignora consistência | Não considera |
