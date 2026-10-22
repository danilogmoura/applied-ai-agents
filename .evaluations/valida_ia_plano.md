# Plano de Avaliação VALIDA-IA — Ordem e Checklist

## Ordem de Análise Sugerida

Analisar os módulos na ordem em que o aluno os encontra, do primeiro ao último.
Cada módulo passa pelas 7 dimensões da rubrica VALIDA-IA.

---

## 📋 Checklist por Dimensão

### Dimensão 1 — Adequação ao Pré-Requisito Real (duplo iniciantismo)

**Nota:** ___/5

- [ ] Módulo explica ou referencia conceitos pré-requisito (JSON, HTTP, terminal, .env)?
- [ ] Não assume conhecimento de APIs sem explicação?
- [ ] Não usa jargões de IA sem defini-los?
- [ ] Usa analogias com programação básica (variáveis, loops, funções)?
- [ ] O "duplo iniciantismo" é respeitado: iniciante em prog + iniciante em IA?
- [ ] Pré-requisitos explícitos entre módulos são reais e cobertos?

**Pré-requisitos ocultos mais comuns a verificar:**

- `python script.py` funciona sem explicar virtual env?
- `.env` explicado antes de primeira API key?
- JSON estruturado explicado antes de usar responses?
- Terminal básico (`cd`, `ls`) assumido?

---

### Dimensão 2 — Progressão Lógica e Carga Cognitiva

**Nota:** ___/5

- [ ] Conceitos são introduzidos ANTES de serem usados?
- [ ] Não há excesso de teoria antes da primeira prática?
- [ ] Há checkpoints ao longo do módulo?
- [ ] Carga cognitiva adequada (não sobrecarrega de uma vez)?
- [ ] Repetição e prática incremental presentes?
- [ ] architecture.md (quando existe) ajuda a ancorar conceitos abstratos?

---

### Dimensão 3 — Equilíbrio Teoria vs. Prática com Scaffolding

**Nota:** ___/5

- [ ] Exemplos pequenos e executáveis presentes?
- [ ] Miniprojeto guiado com passos claros?
- [ ] Exercícios incrementais (não apenas leitura)?
- [ ] Output esperado descrito no miniproject.md?
- [ ] Critérios de sucesso definidos?
- [ ] run.py executa sem erros e ensina algo?
- [ ] test_exercise.py valida aprendizado?

---

### Dimensão 4 — Alinhamento com Resultado Prometido

**Nota:** ___/5

- [ ] Objetivo declarado claro no início do MATERIAL.md?
- [ ] Conteúdo ensina exatamente o que a promessa exige?
- [ ] Miniprojeto permite demonstrar o resultado prometido?
- [ ] Checklist final verifica habilidades declaradas?
- [ ] Perguntas para reflexão alinham com objetivos?
- [ ] Resumo do módulo reflete o conteúdo real (sem mencionar coisas não cobertas)?

---

### Dimensão 5 — Clareza, Jargão e Suporte a Erros

**Nota:** ___/5

- [ ] Todo jargão técnico tem definição ou analogia?
- [ ] Padrão de tradução aplicado (termo EN primeiro, PT-BR entre parênteses)?
- [ ] Erros comuns listados em tabela?
- [ ] Mensagens de erro explicadas quando aparecem?
- [ ] Tom adequado para iniciantes (não condescendente, não técnico demais)?
- [ ] Sem contradições internas no material?
- [ ] Diagramas Mermaid ajudam ou confundem?

---

### Dimensão 6 — Lacunas Críticas e Pré-Requisitos Ocultos

**Nota:** ___/5

- [ ] Setup guiado presente (SETUP_COMPLETE.md cobre todos os módulos)?
- [ ] Aviso sobre custo de API antes de primeiro uso?
- [ ] Explicação de como rodar o código (`python modules/XXX/run.py`)?
- [ ] Tratamento de erros comum incluído?
- [ ] Segurança (API keys, .env) abordada antes de primeiro uso?
- [ ] Debugging básico ensinado?
- [ ] Miniproject.md tem TODOS os 4 elementos: descrição, passos, output esperado, critérios?

---

### Dimensão 7 — Atualidade, Ferramental e Dependência

**Nota:** ___/5

- [ ] Modelos citados estão atualizados (gpt-4o-mini, etc.)?
- [ ] Curso depende de versão específica que pode mudar?
- [ ] Princípios ensinados são transferíveis (não só framework X)?
- [ ] Alternativas apresentadas quando relevante?
- [ ] Bibliotecas usadas ainda mantidas/ativas?
- [ ] Links de referências funcionais e atuais?

---

## 📊 Matriz de Execução

Analise cada módulo nesta ordem. Marque ✅ quando completo.

| # | Módulo | D1 | D2 | D3 | D4 | D5 | D6 | D7 | Status |
| --- | -------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | -------- |
| 0a | p0_fundamentals | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅ |
| 0b | p0_first_llm | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 1 | p1_feasibility | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 2 | p2_rag | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3a1 | p3a1_self_eval | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3a2 | p3a2_tool_calling | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3a3 | p3a3_planning | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 3b | p3b_multi_agent | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 4 | p4_production | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 5 | p5_evaluation | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 6 | p6_safety | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 7 | p7_memory | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 8 | p8_streaming | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 9 | p9_caching | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 10 | p10_skills | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| 11 | p11_production_ops | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

---

## 📝 Avaliação Detalhada — P0 Fundamentals

**Nota geral:** 4/5

### Dimensão 1 — Adequação ao Pré-Requisito: 5/5 ✅

- Evidência: Seção "🔧 Conceitos Técnicos" explica JSON, API/HTTP, .env e terminal antes de qualquer código.
- Feedback: Nenhum ajuste necessário.

### Dimensão 2 — Progressão Lógica: 5/5 ✅

- Evidência: Ordem didática perfeita: IA → LLM → Tokenização → Prompt Engineering → Alucinação → Glossário.
- Feedback: Nenhum ajuste necessário.

### Dimensão 3 — Teoria vs Prática: 3/5 ⚠️

- Evidência: Exercício era só conceitual (ler + explicar). Miniprojeto com código pronto nos passos.
- Correção aplicada: Adicionada Parte B — mini-código comparando prompts.

### Dimensão 4 — Alinhamento: 4/5 ⚠️

- Evidência: Objetivos coerentes, mas "Aplicar técnicas" não verificado na prática.
- Correção aplicada: Parte B testa prompt refinado vs original em LLM real.

### Dimensão 5 — Clareza/Jargão: 5/5 ✅

- Evidência: Glossário 16 termos + analogias consistentes (RPG, delivery, GPS).
- Feedback: Nenhum ajuste necessário.

### Dimensão 6 — Lacunas Críticas: 4/5 ⚠️

- Evidência: Conceitos técnicos explicados, mas sem estimativa de custo real.
- Correção aplicada: Seção "Estimativa de Custo Real" adicionada.

### Dimensão 7 — Atualidade: 4/5 ⚠️

- Evidência: Modelos atualizados, mas referência bibliográfica pendente.
- Correção aplicada: Seção Referências removida.

### Prioridades aplicadas

1. ✅ Remover referências bibliográficas
2. ✅ Adicionar exercício prático (Parte B)
3. ✅ Adicionar estimativa de custo real

---

## 📝 Avaliação Detalhada — P0 First LLM

Para cada módulo, produza:

```markdown
## Módulo P{N}: {Nome}

**Nota geral:** X/5

### Dimensão 1 — Adequação ao Pré-Requisito: X/5
- Evidência: [trecho específico]
- Feedback: [ação concreta]

### Dimensão 2 — Progressão Lógica: X/5
...

### Dimensão 3 — Teoria vs Prática: X/5
...

### Dimensão 4 — Alinhamento: X/5
...

### Dimensão 5 — Clareza/Jargão: X/5
...

### Dimensão 6 — Lacunas Críticas: X/5
...

### Dimensão 7 — Atualidade: X/5
...

### Prioridades de correção
1. [Mais urgente]
2. [Médio]
3. [Menos urgente]

### Pontos fortes
- [Preservar]
```

---

## 🏁 Resumo Final (após todos os módulos)

Após avaliar todos os 16 módulos, produzir:

### Resumo Executivo

Síntese crítica da adequação do curso ao programador iniciante.

### Top 3 Prioridades Globais

1. [Problema mais crítico transversal]
2. [Segundo mais crítico]
3. [Terceiro mais crítico]

### Pontos Fortes Globais

- [O que está funcionando bem e deve ser preservado]

### Módulos Prontos vs. Precisan Revisão

- ✅ Prontos: [lista]
- ⚠️ Revisão necessária: [lista + motivo]
