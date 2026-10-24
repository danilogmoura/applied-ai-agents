# 🏗️ Architecture Design — Sistema Multiagente

> **Desafio:** Projete um sistema multiagente para processamento de tickets de suporte.
>
> 🔬 **AVANÇADO / OPCIONAL** — Este desafio assume noções de arquitetura e infra. Se você ainda está aprendendo os fundamentos, tudo bem pular na primeira passada e voltar depois.

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

> 🧭 **Como abordar este desafio.** Não existe uma única arquitetura correta — o que se avalia é o seu **raciocínio**. Sugestão de caminho:
>
> 1. Comece rascunhando o diagrama com blocos e setas (ASCII serve).
> 2. Para cada decisão na tabela, registre *o que escolheu* **e por quê**.
> 3. Feche com números de custo por caminho, mesmo estimados.
>
> Exemplo ilustrativo (não é gabarito): na topologia multiagente, pergunte-se "quem decide o próximo passo?" — supervisor central vs. descentralizado muda todo o resto do desenho.

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
| --------- | -------- | ------------- | --------------- |
| **Roteamento** | LLM-based (prompt) | Heurísticas (regex/TF-IDF) | ? |
| **Modelo supervisor** | gpt-4o-mini / claude-haiku / local | ? | ? |
| **Modelo especialistas** | Todos iguais / diferentes por domínio | ? | ? |
| **Comunicação** | Shared state / message queue (fila de mensagens: os agentes trocam recados por uma fila em vez de chamarem uns aos outros direto) / RPC | ? | ? |
| **Fallback especialista** | Re-rotear / responder genérico / fila humana | ? | ? |
| **Autoavaliação** | Após geração / antes / nunca | ? | ? |

### 3. Análise de Custo por Caminho

> 💡 **Como calcular custo.** Fórmula: `custo = (tokens / 1_000_000) × preço_por_milhão`.
> Preços de referência (USD por 1M tokens): **gpt-4o-mini** $0.15 entrada / $0.60 saída; **gpt-4o** $2.50 / $10.00; **text-embedding-3-small** $0.02.
> Regra prática de tokens: ~4 caracteres ≈ 1 token (≈ 750 tokens por página de texto).
> No multiagente, some supervisor **+** especialista: cada salto na cadeia adiciona tokens de entrada/saída.

Calcule o custo esperado de cada fluxo:

| Caminho | Tokens Supervisor | Tokens Especialista | Custo Estimado/dia |
| --------- | ------------------- | --------------------- | ------------------- |
| Ticket → Supervisor → Financeiro | ? | ? | ? |
| Ticket → Supervisor → Técnico | ? | ? | ? |
| Ticket → Supervisor → Geral | ? | ? | ? |
| **Total diário** | | | ? |
| **Total mensal** | | | ? |

Verifique: está dentro de $2000/mês?

> ✏️ **Exemplo resolvido (confira seu raciocínio).** Suponha 100K tickets/dia, cada um passando por supervisor + especialista. Com ~300 tokens de entrada + 150 de saída no gpt-4o-mini por salto, e 2 saltos por ticket:
>
> - Tokens/ticket ≈ 2 × (300 + 150) = 900 → 100K × 900 = 90M tokens/dia.
> - Entrada: 60M/1M × $0.15 = $9.00; Saída: 30M/1M × $0.60 = $18.00 → **≈ $27/dia ≈ $810/mês.**
> - Dentro de $2000 ✓ — mas note como o custo **dobra** só pelo segundo salto (supervisor→especialista). Troque pelos seus números.

### 4. Graceful Degradation

Descreva o comportamento quando componentes falham:

| Falha | Comportamento | Custo adicional | Tempo extra |
| ------- | -------------- | ----------------- | ------------- |
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
| ---------- | -------------- | --------- | ----------- |
| **Topologia** | Justifica escolha com dados | Apenas descreve | Inconsistente |
| **Custo** | Detalhado por caminho, dentro budget | Estimativa global | Sem cálculo |
| **Degradation** | Cobertura completa | Parcial | Ausente |
| **Trade-off roteamento** | Analisa custo flexibilidade | Ignora custo | Não considera |
