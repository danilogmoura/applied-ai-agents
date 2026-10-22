# 🏗️ Architecture Design — Sistema de Memória para Agentes

> **Desafio:** Projete um sistema de memória que permita a um agente "lembrar" de conversas anteriores sem exceder o limite de contexto.

## Cenário

Um agente de assistente pessoal precisa:
- **Lembrar preferências do usuário** (nome, idioma, horários) — permanente
- **Lembrar contexto da conversa atual** — curto prazo
- **Lembrar tópicos de sessões anteriores** — longo prazo
- **Contexto máximo**: 128K tokens (gpt-4o)
- **Custo máximo**: $100/mês em tokens de contexto

Problema: uma conversa de 1 semana pode gerar 50K+ tokens de histórico. Como manter o útil sem estourar o contexto?

---

## Entregáveis

### 1. Diagrama da Arquitetura

```
[Conversa Atual] → [Memory Manager] → [Contexto para LLM]
                         ↕
              [Short-term Store]
              [Long-term Store]
              [Summarizer]
```

Defina:
- Quais stores existem?
- Quando dados migram de curto para longo prazo?
- Como o summarizer funciona?

### 2. Decisões Arquiteturais

| Decisão | Opções | Sua Escolha | Justificativa |
|---------|--------|-------------|---------------|
| **Memória curta** | Sliding window | Token budget | ? |
| **Memória longa** | Vetores (embeddings) | Texto estruturado | ? |
| **Sumarização** | Automática (LLM) | Manual / template | ? |
| **Recuperação longa** | Similaridade semântica | Keywords / tags | ? |
| **Inserção no contexto** | Sempre no início / fim / middle | ? | ? |
| **Refresh** | A cada N mensagens / evento | ? | ? |

### 3. Fluxo de Dados Detalhado

Descreva o ciclo de vida de uma mensagem:

```
1. Usuário envia mensagem
2. Memory Manager:
   a. Adiciona à memória curta
   b. Verifica se memória curta excede limite
      - Se sim: sumariza as mais antigas
      - Atualiza memória longa
   c. Busca memórias relevantes da longa
   d. Constrói contexto final para LLM
3. Contexto enviado ao LLM
4. Resposta processada
```

Quantos tokens ocupa cada etapa?

### 4. Estimativa de Custo de Memória

Calcule quantos tokens a memória consome por sessão típica:

| Componente | Tokens/session | Sessions/dia | Custo diário |
|------------|---------------|--------------|-------------|
| Memória curta | ? | ? | ? |
| Memória longa (recuperada) | ? | ? | ? |
| Sumarizações | ? | ? | ? |
| **Total diário** | | | ? |
| **Total mensal** | | | ? |

Está dentro de $100/mês?

---

## Checklist de Validação

- [ ] Distinção clara entre memória curta e longa
- [ ] Estratégia de sumarização justificada
- [ ] Mecanismo de recuperação da memória longa definido
- [ ] Custo de memória estimado e dentro do orçamento
- [ ] Considerou o que preservar vs resumir (dados pessoais vs trivia)
- [ ] Plano para edge cases (sessão muito longa, nova sessão sem histórico)

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
|----------|--------------|---------|-----------|
| **Hierarquia** | Curto/longo bem separados | Separação básica | Tudo misturado |
| **Sumarização** | Custo/benefício analisado | Apenas descreve | Não considera custo |
| **Recuperação** | Relevância garantida | Busca ingênua | Sem recuperação |
| **Custo** | Estimativa token-a-token | Estimativa grossa | Sem cálculo |
