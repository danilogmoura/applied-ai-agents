# 🏗️ Architecture Design — Sistema Multiagente

> **Desafio:** Projete um sistema multiagente para processamento de tickets de suporte.

## Cenário

Uma empresa recebe **100K tickets/dia** categorizados em:
- **Financeiro** (reembolsos, cobranças) — 40%
- **Técnico** (bugs, login, performance) — 35%
- **Geral** (informações, políticas) — 25%

Requisitos:
- Tickets críticos devem ser priorizados (< 30s resposta)
- Agentes especializados devem ter maior accuracy
- Orçamento: máximo $2000/mês em IA
- Se o supervisor falhar, tickets não podem ficar presos

---

## Entregáveis

### 1. Diagrama da Arquitetura

Descreva a topologia multiagente:

```
[Tickets] → [Supervisor] → [Agente Financeiro]
                      ↘ [Agente Técnico]
                      ↘ [Agente Geral]
```

Defina:
- Topologia: supervisor-especialista? pipeline? peer-to-peer?
- Como o supervisor decide qual agente chamar?
- O que acontece se um especialista falhar?

### 2. Decisões Arquiteturais

| Decisão | Opções | Sua Escolha | Justificativa |
|---------|--------|-------------|---------------|
| **Roteamento** | LLM-based (prompt) | Heurísticas (regex/TF-IDF) | ? |
| **Modelo supervisor** | gpt-4o-mini / claude-haiku / local | ? | ? |
| **Modelo especialistas** | Todos iguais / diferentes por domínio | ? | ? |
| **Comunicação** | Shared state / message queue / RPC | ? | ? |
| **Fallback especialista** | Re-rotear / responder genérico / fila humana | ? | ? |
| **Autoavaliação** | Após geração / antes / nunca | ? | ? |

### 3. Análise de Custo por Caminho

Calcule o custo esperado de cada fluxo:

| Caminho | Tokens Supervisor | Tokens Especialista | Custo Estimado/dia |
|---------|-------------------|---------------------|-------------------|
| Ticket → Supervisor → Financeiro | ? | ? | ? |
| Ticket → Supervisor → Técnico | ? | ? | ? |
| Ticket → Supervisor → Geral | ? | ? | ? |
| **Total diário** | | | ? |
| **Total mensal** | | | ? |

Verifique: está dentro de $2000/mês?

### 4. Graceful Degradation

Descreva o comportamento quando componentes falham:

| Falha | Comportamento | Custo adicional | Tempo extra |
|-------|--------------|-----------------|-------------|
| Supervisor indisponível | ? | ? | ? |
| Agente Financeiro rate-limited | ? | ? | ? |
| Modelo especializado alucina | ? | ? | ? |
| Message queue backlog | ? | ? | ? |

---

## Checklist de Validação

- [ ] Definida topologia clara (supervisor-especialista ou outra)
- [ ] Justificou escolha de modelo por camada (custo vs qualidade)
- [ ] Estratégia de roteamento justificada (LLM vs heurística)
- [ ] Custo total calculado e dentro do orçamento
- [ ] Plano de graceful degradation para cada componente
- [ ] Considerou custo adicional do multiagente vs single-agent

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
|----------|--------------|---------|-----------|
| **Topologia** | Justifica escolha com dados | Apenas descreve | Inconsistente |
| **Custo** | Detalhado por caminho, dentro budget | Estimativa global | Sem cálculo |
| **Degradation** | Cobertura completa | Parcial | Ausente |
| **Trade-off roteamento** | Analisa custo flexibilidade | Ignora custo | Não considera |
