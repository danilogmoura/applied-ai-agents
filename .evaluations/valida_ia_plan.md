# Plano de Correções — VALIDA-IA

**Avaliação:** 2026-10-22  
**Curso:** Agentes de IA Aplicada para Programadores Iniciantes  
**Módulos avaliados:** 16 (p0_fundamentals → p11_production_ops)

---

## Prioridade 1 — [CRÍTICO] Criar ponte técnica antes de P2

### 1.1 Adicionar seção "Conceitos Técnicos que Usaremos" no início do curso

- [ ] Explicar o que é JSON com analogia (ex: "como uma ficha de personagem")
- [ ] Explicar o que é HTTP/API REST (ex: "como pedir comida por delivery")
- [ ] Explicar variáveis de ambiente e `.env` (ex: "chave secreta do jogo")
- [ ] Explicar terminal básico: `cd`, `python`, `ls`
- [ ] Colocar esta seção ANTES de p0_fundamentals ou como seção introdutória nele

### 1.2 Tornar explícito pré-requisito de Python para P2

- [ ] Em p2_rag/MATERIAL.md, substituir *"recomenda-se familiaridade com Python"* por lista concreta do que precisa saber (funções, dicionários, loops)
- [ ] Ou adicionar mini-tutorial de Python necessário antes de P2

### 1.3 Mover seções avançadas para caixas OPCIONAIS

- [ ] p0_first_llm: seção BPE detalhada → marcar como `> 🔬 OPCIONAL — avançado`
- [ ] p4_production: internals do Docker (namespaces, cgroups) → marcar como opcional
- [ ] p9_caching: implementação LRU com Hash Map + Doubly Linked List → marcar como opcional

---

## Prioridade 2 — [ALTA] Reordenar P1 Feasibility

### 2.1 Mover P1 Feasibility de lugar

- [ ] Adicionar nota em p1_feasibility/MATERIAL.md indicando que é módulo **opcional/bônus** ou sugerir reordenação para pós-P3b
- [ ] Ou reescrever o exercício prático para usar dados simulados em vez de benchmark real

### 2.2 Reduzir carga cognitiva de P3b Multi-agente

- [ ] Adicionar checkpoint intermediário em p3b_multi_agent/MATERIAL.md entre conceitos e custos
- [ ] Ou separar em dois módulos conceitual vs. implementação

---

## Prioridade 3 — [MÉDIA] Unificar e completar o guia de setup

### 3.1 Criar guia de setup unificado

- [ ] Criar `SETUP_COMPLETE.md` na raiz cobrindo: Python version, virtualenv, git, editor, API key, variáveis de ambiente
- [ ] Referenciar este guia em todos os módulos que usam `run.py`

### 3.2 Adicionar seção de depuração

- [ ] Em p0_first_llm, adicionar seção explicando erros comuns de OpenAI API (chave inválida, rate limit, timeout)

---

## Melhorias Transversais

### 4.1 Padronizar formatação

- [ ] Remover `---` duplicados em p3a2_tool_calling, p5_evaluation, p6_safety, p7_memory
- [ ] Verificar todos os outros módulos para inconsistências similares

### 4.2 Traduzir termos técnicos

- [ ] Substituir termos em inglês no corpo do texto por PT-BR com inglês entre parênteses na primeira ocorrência
- [ ] Ex: "similaridade por cosseno (cosine similarity)", "backoff exponencial (exponential backoff)"

### 4.3 Corrigir referências

- [ ] Corrigir link "OpenAI Latency Benchmarks" em p1_feasibility (link incorreto)
- [ ] Adicionar nota sobre alternativas a ChromaDB em p2_rag (Pinecone, Qdrant, Weaviate)
- [ ] Adicionar nota em referências bibliográficas: *"Leituras opcionais em inglês para aprofundamento"*

### 4.4 Adicionar elementos pedagógicos faltantes

- [ ] Adicionar "O que você vai ver" antes de cada `run.py` mostrando output esperado
- [ ] Adicionar checklist verificável "Como saber se você atingiu o objetivo" no final de cada módulo
- [ ] Validar que todos os `miniproject.md` tenham: descrição, passos guiados, output esperado, critérios de sucesso

---

## Avaliação das Dimensões (referência)

| Dimensão | Nota | Status |
| ---------- | ------ | -------- |
| 1. Adequação ao pré-requisito | 4/5 | Pendente |
| 2. Progressão lógica e carga cognitiva | 4/5 | Pendente |
| 3. Equilíbrio teoria vs. prática | 4/5 | Pendente |
| 4. Alinhamento com resultado prometido | 4/5 | Pendente |
| 5. Clareza, jargão e suporte a erros | 4/5 | Pendente |
| 6. Lacunas críticas e pré-requisitos ocultos | 3/5 | Pendente |
| 7. Atualidade, ferramental e dependência | 4/5 | Pendente |

---

**Status geral:** 0/18 tarefas concluídas
