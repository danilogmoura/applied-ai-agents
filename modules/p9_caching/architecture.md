# 🏗️ Architecture Design — Cache Layer

> **Desafio:** Projete uma camada de cache para otimizar custos e latência em sistema de IA.
>
> 🔬 **AVANÇADO / OPCIONAL** — Este desafio assume noções de arquitetura e infra. Se você ainda está aprendendo os fundamentos, tudo bem pular na primeira passada e voltar depois.

## Cenário

Uma aplicação de chatbot precisa reduzir custos e melhorar performance:

- **50K queries/mês** (~1667/hora)
- **30% das queries são repetidas** (FAQ, comandos comuns)
- **Orçamento**: máximo $300/mês em API calls
- **SLA**: latência < 2s para respostas cacheadas
- **Requisito**: cache invalida quando dados subjacentes mudam

---

## Entregáveis

> 🧭 **Como abordar este desafio.** Não existe uma única arquitetura correta — o que se avalia é o seu **raciocínio**. Sugestão de caminho:
>
> 1. Comece rascunhando o diagrama com blocos e setas (ASCII serve).
> 2. Para cada decisão na tabela, registre *o que escolheu* **e por quê**.
> 3. Feche com o ROI calculado, mesmo estimado.
>
> Exemplo ilustrativo (não é gabarito): antes de escolher a estratégia de eviction, pense no padrão de acesso real (muito repetido? muito espalhado?) — isso é o que justifica LRU/LFU/FIFO.

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
- Onde o cache fica (memória, Redis — banco de dados em memória muito rápido para guardar chaves temporárias, banco)?
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
| Eviction policy | LRU / LFU / FIFO (?) | ? |

> 💡 **O que significam as políticas de eviction** (qual item remover quando o cache enche): **LRU** (Least Recently Used — remove o usado há mais tempo), **LFU** (Least Frequently Used — remove o menos usado em volume), **FIFO** (First In, First Out — remove o mais antigo, na ordem de entrada).
| Memory limit | ? MB | ? |

Justifique LRU vs LFU para este cenário (queries frequentes vs únicas).

### 4. ROI do Cache

> 💡 **Como calcular custo.** Fórmula: `custo = (tokens / 1_000_000) × preço_por_milhão`.
> Preços de referência (USD por 1M tokens): **gpt-4o-mini** $0.15 entrada / $0.60 saída; **gpt-4o** $2.50 / $10.00; **text-embedding-3-small** $0.02.
> Regra prática de tokens: ~4 caracteres ≈ 1 token (≈ 750 tokens por página de texto).

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

> ✏️ **Exemplo resolvido (para você conferir seu raciocínio).** Suponha 50K queries/mês, média de 500 tokens de entrada + 200 de saída por query, no gpt-4o-mini.
>
> - **Sem cache:** entrada = 50K × 500 = 25M tokens → 25 × $0.15 = $3.75; saída = 50K × 200 = 10M tokens → 10 × $0.60 = $6.00. **Total ≈ $9.75/mês.**
> - **Com cache (30% hit):** só 70% vão ao LLM → 0.70 × $9.75 ≈ **$6.83/mês**.
> - **Economia ≈ 30%** ✓. Obs.: os números deste cenário são ilustrativos; troque pelos seus.

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
