# 📋 Relatório de Qualidade Instrucional — VALIDA-IA

> Avaliação do curso completo (16 módulos) pela rubrica de 7 dimensões definida em
> `agents/valida_ia.md`. Público-alvo: **programador iniciante + iniciante absoluto em IA**.
> Data: 2026-10-24 · Escopo: todos os `MATERIAL.md`, `run.py` e `miniproject.md`.
> Postura: avaliador crítico, não gerador. Toda nota tem evidência citada (`path:linha`).
>
> **⚡ Reavaliado em 2026-10-24** após aplicar as 3 correções prioritárias (commit `63e68db`):
> terminologia "Módulo" na superfície, onboarding de produção e glossários 07–16. As notas abaixo
> mostram **antes → depois**. A avaliação original (notas "antes") é preservada como histórico.

---

## Nota global do curso

**Antes das correções: 3,9 / 5 · Após a 1ª rodada: ~4,4 / 5 · Após a 2ª rodada (T2 + T7):
~4,6 / 5 — curso agora coeso em progressão, clareza e anti-dependência de fornecedor.**

O curso já era notavelmente bem construído para o "duplo iniciantismo" nos arcos 1–3
(Fundamentos, Contexto, Autonomia). O risco estava concentrado no **Arco 4 (Produção/Operações,
módulos 09–16)**, que introduz FastAPI, Docker, SSE, CI/CD e observabilidade. As 3 correções
fecharam exatamente essa barreira operacional e as inconsistências de superfície.

| Dimensão | Antes | Depois | O que mudou |
| --- | :---: | :---: | --- |
| T1 Pré-requisitos ocultos / dupla iniciação | 3,5 | **4,0–4,5** | `SETUP-PRODUCAO.md` criado + pré-requisito operacional declarado no Módulo 09. |
| T2 Progressão e carga cognitiva | 4 | **4,5** | 13 micro-checkpoints ⏸️ "rode agora" inseridos nos 6 módulos longos (01/02/04/08/09/15). |
| T3 Teoria vs prática / scaffolding | 4,5 | **4,5+** | Ressalva (testes só até 08) **não se confirmou**: cobertura 16/16. |
| T4 Alinhamento com a promessa | 3,5 | **4,5** | README 0× "capítulo/livro"; FINAL_PROJECT 0× P-codes + tabela de correspondência. |
| T5 Clareza, jargão e erros | 4 | **4,5** | Glossário agora em **16/16** módulos (antes só 01–06). |
| T6 Lacunas críticas | 3,5 | **4,0–4,5** | Onboarding terminal/Docker/git publicado e linkado no 09. |
| T7 Atualidade e dependência | 4,5 | **5** | Callout "modelo é exemplo" nos módulos densos + `get_model()` centraliza troca; bug de assinatura corrigido. |

---

## Teste 1 — Adequação ao pré-requisito real e à dupla iniciação

**Nota: 3,5 / 5**

**Evidência (pontos fortes):**

- O módulo 01 neutraliza os principais pré-requisitos ocultos ANTES do primeiro código:
  define JSON, API/HTTP, `.env`/variáveis de ambiente e terminal básico, cada um com analogia
  ("API é como um delivery de comida", `01-fundamentos/MATERIAL.md:60`; tabela de comandos de
  terminal `01-fundamentos/MATERIAL.md:80`).
- Jargão de IA é definido na primeira ocorrência com intuição, não matemática: embeddings em
  `04-rag/MATERIAL.md:28` ("foque na intuição: *vetores capturam significado*. A matemática vem
  depois") e cosine similarity com analogia de setas/GPS (`04-rag/MATERIAL.md:237`).
- Circuit breaker e checkpoint (termos densos) são explicados com estados e trade-offs
  (`07-planejamento/MATERIAL.md:149`, `:183`).

**Evidência (problema):**

- A partir do módulo 09, o material assume conforto com ferramentas que o perfil "iniciante em
  programação" raramente tem: FastAPI, Pydantic, middleware, **Docker/docker-compose**, namespaces
  e cgroups (`09-producao-api/MATERIAL.md:38–49`). O pré-requisito declarado do 09 é apenas
  conteudístico ("concluiu o Módulo 08", `09-producao-api/MATERIAL.md:5`) — não cobre a habilidade
  operacional de containerizar.
- README lista Docker como pré-requisito "só a partir do Capítulo 09" (`README.md:~30`), mas não há
  um módulo/guia de transição que ensine Docker do zero antes dessa barreira.

**Feedback acionável:**

- Criar um **"Setup de Produção" guiado** (mini-guia ou módulo 08.5) cobrindo, do zero: instalar
  Docker, rodar um container `hello-world`, o que é `uvicorn --app-dir`, e git básico — antes do 09.
- No topo dos módulos 09–16, declarar explicitamente os pré-requisitos **operacionais** (não só
  conceituais): "você precisa saber X de terminal/Docker para este módulo".

---

## Teste 2 — Progressão lógica e carga cognitiva

**Nota original: 4 / 5 → reavaliada: 4,5 / 5** *(resolvido na 2ª rodada — commit `452c83a`)*

**Evidência (pontos fortes):**

- Estrutura PBL consistente: todo módulo abre com problema/contexto, depois "Objetivos de
  Aprendizagem" verificáveis (`grep` confirma `## 🎯 Objetivos` nos 16), e só então a teoria.
- Gestão de carga cognitiva explícita: seções separadas **"🔬 Avançado — OPCIONAL"** (ex.: BPE em
  `02-primeiro-llm/MATERIAL.md:379`; internals de Docker em `09-producao-api/MATERIAL.md` sumário),
  permitindo que o iniciante ignore profundidade sem perder o essencial.
- Conceitos aparecem antes do uso: tokens (01) → custo (02/03) → embeddings (04) → tools (06) →
  multiagente (08) → API (09), progressão deliberada descrita em `README.md:13–20`.

**Evidência (problema):**

- Alguns módulos têm MATERIAL.md muito longo (02 ≈ 660 linhas, 04 ≈ 500+) — risco de maratona de
  leitura antes da prática. Falta checkpoint de "pare e rode agora" mais frequente dentro do corpo.

**Feedback acionável:**

- Inserir micro-checkpoints ("⏸️ Rode `run.py` AGORA e observe X") a cada ~80–100 linhas de prosa,
  quebrando blocos longos de teoria.

---

## Teste 3 — Equilíbrio teoria vs prática com scaffolding

**Nota: 4,5 / 5**

**Evidência (pontos fortes):**

- Trindade de artefatos em todos os módulos: `MATERIAL.md` + `run.py` executável + `miniproject.md`
  (confirmado por listagem de diretórios; ex.: `02-primeiro-llm/` tem ainda `SETUP.md`,
  `ticket_classifier_skeleton.py`, `exercises.py`, `exercises_solution.py`).
- Scaffolding em camadas: esqueleto → exercícios com TODOs → solução completa
  (`exercises.py` + `exercises_solution.py` presentes nos módulos inspecionados).
- `checklist_miniprojects.md`: **16/16 miniprojetos** com os 4 elementos obrigatórios
  (descrição, passos guiados, output esperado, critérios de sucesso).
- Todo módulo fecha com "✅ Checklist: Como Saber Se Você Atingiu o Objetivo" (presente nos 16).

**Evidência (problema):** menor — nenhum relevante o suficiente para baixar a nota além do acima.

**Feedback acionável:** manter; garantir que `test_exercise.py` exista também nos módulos 09–16
(verificar cobertura de teste automatizado no arco de produção).

---

## Teste 4 — Alinhamento com o resultado prometido

**Nota: 3,5 / 5**

**Evidência (ponto forte):**

- Promessa clara e coerente com conteúdo: "formação prática em agentes de IA", 4 arcos, projeto
  final integrador "AgentForge" usando os 16 módulos (`FINAL_PROJECT.md:1–5`).

**Evidência (problema — inconsistência de terminologia/números):**

- `README.md` ainda usa a metáfora **de livro**: "Leia como um livro — do capítulo 1 ao 16"
  (`README.md:3`), "Os 16 capítulos" (`README.md:13`), e todo o sumário rotula
  "Capítulo 01…16" (`README.md:~40–90`). Isso **contradiz a decisão registrada** de padronizar
  "Módulo" (commit `9bbf5e9`), pois os MATERIAL.md dizem "# Módulo NN".
- `FINAL_PROJECT.md` usa os **códigos antigos P0–P11** no diagrama e tabelas
  (`FINAL_PROJECT.md:14–60`), que não mapeiam visivelmente para a numeração 01–16 dos módulos.
  Um aluno que concluiu "Módulo 09" não reconhece "P4" no projeto final.

**Feedback acionável (alta prioridade):**

- Reescrever `README.md` trocando "capítulo/livro" → "módulo" e alinhando o sumário aos títulos
  reais dos MATERIAL.md.
- Recodificar `FINAL_PROJECT.md` de P0–P11 → 01–16 (ou adicionar tabela de correspondência
  P-código ↔ Módulo NN) para restaurar o elo promessa↔percurso.

---

## Teste 5 — Clareza, jargão e suporte a erros

**Nota: 4 / 5**

**Evidência (pontos fortes):**

- Suporte a erros universal: `❓ Troubleshooting` presente nos 16 módulos, com tabelas
  erro→causa→solução específicas (ex.: `07-planejamento/MATERIAL.md:315–319`;
  `13-streaming/MATERIAL.md:292`).
- Seções dedicadas "Erros Comuns de Iniciantes" nos módulos (ex.: `02-primeiro-llm/MATERIAL.md:437`,
  `09-producao-api` sumário item 3).
- Tom adequado, analógico, sem presunção de senioridade nos arcos 1–3.

**Evidência (problema):**

- **Glossário dedicado só existe nos módulos 01–06** (`grep '^#{2,3}.*Gloss'` retorna apenas esses
  seis). Módulos 07–16 definem termos no corpo, mas não têm tabela de vocabulário consolidada —
  pior justamente onde o jargão é mais denso (SSE, golden dataset, A/B, cache, skills, CI/CD).

**Feedback acionável:**

- Adicionar seção "📖 Glossário" aos módulos 07–16, no mesmo formato das de 01–06
  (Termo | Definição | Analogia).

---

## Teste 6 — Lacunas críticas e pré-requisitos ocultos

**Nota: 3,5 / 5**

**Evidência (coberto):**

- Custo tratado transversal e cedo: "Do token ao centavo" (`01-fundamentos/MATERIAL.md:274`),
  estimativa de custo real (`01-fundamentos/MATERIAL.md:441`), `shared/cost.py` usado em todos.
- Segurança/API key desde o início: `.env` nunca vai pro repositório (`01-fundamentos/MATERIAL.md:68`),
  princípio do menor privilégio (`06-tool-calling/MATERIAL.md:212`), prompt injection no 11.
- Setup guiado existe pelo menos no 02 (`SETUP.md`).

**Evidência (lacuna):**

- **Não há guia de onboarding de terminal/Docker/git** antes do arco de Produção (mesma raiz do T1).
- SETUP.md aparece no 02 mas não é claro que exista equivalente para o salto operacional do 09.

**Feedback acionável:**

- Publicar um `SETUP-PRODUCAO.md` (ou expandir o apêndice de setup do README) com passo a passo de
  instalação e verificação de Docker + uvicorn, linkado no topo do módulo 09.

---

## Teste 7 — Atualidade, ferramental e dependência

**Nota original: 4,5 / 5 → reavaliada: 5 / 5** *(resolvido na 2ª rodada — commits `de9b730` + `2f34b01`)*

**Evidência (pontos fortes):**

- Não fica preso a um único fornecedor: `02-primeiro-llm/MATERIAL.md:194–199` lista Anthropic
  (claude-haiku), Google (gemini-flash) e **local gratuito** (Ollama + Llama 3); exercício sugere
  "pode ser o chat da OpenAI, Claude, ou qualquer outro" (`01-fundamentos/MATERIAL.md:491`).
- Fallbacks de fornecedor embutidos nos designs: embedder local BGE quando a API de embedding cai
  (`04-rag/MATERIAL.md:184`); model routing por criticidade incluindo claude-opus (`14-cache/MATERIAL.md:227`).
- Encoraja transferibilidade: "Explorar frameworks — LangChain, LlamaIndex, CrewAI, AutoGen —
  implemente os mesmos padrões em diferentes frameworks" (`16-operacoes/MATERIAL.md:390`).
- Modelos citados são atuais (Llama 3, claude-haiku, gemini-flash).

**Evidência (problema leve):**

- Vários exemplos usam nomes de modelo específicos que envelhecem rápido; faltar um aviso de
  "modelos mudam, o padrão importa mais que o nome" reforçaria a anti-dependência.

**Feedback acionável:**

- Adicionar callout recorrente "modelo é exemplo, não requisito" nos módulos que fixam nome de modelo.

---

## Registro pós-correção (commit `63e68db`)

As 3 prioridades urgentes foram aplicadas e verificadas no disco:

1. **Terminologia "Módulo" (era T4).** `README.md` não contém mais "capítulo/livro" (grep = 0);
   `FINAL_PROJECT.md` foi recodificado de P0–P11 → Módulos 01–16 (grep de P-codes = 0) e ganhou uma
   tabela de correspondência Módulo ↔ Componente. Elo promessa↔percurso restaurado.
2. **Onboarding de Produção (era T1 + T6).** Novo `SETUP-PRODUCAO.md` na raiz cobre git básico,
   Docker (`hello-world`) e uvicorn/FastAPI do zero, com checklist de transição. O Módulo 09 passou a
   declarar pré-requisito **operacional** (não só conceitual) e linka o guia.
3. **Glossários 07–16 (era T5).** Seção `## Glossário` (padrão Termo | Definição | Analogia) adicionada
   aos 10 módulos que faltavam; cobertura agora 16/16.

**Pendências de baixa prioridade (não bloqueiam):** inserir micro-checkpoints "⏸️ rode agora" nos
módulos longos (T2); callout recorrente "modelo é exemplo, não requisito" (T7); padronizar o emoji do
título dos glossários (novos usam `## Glossário`, alguns antigos `## 📖 Glossário`).

---

## Registro pós-correção — 2ª rodada (commits `cd7253c`, `452c83a`, `de9b730`, `2f34b01`)

As três pendências de baixa prioridade da 1ª rodada foram fechadas:

1. **Glossários padronizados (era T5).** Os 16/16 módulos usam agora o título único
   `## 📖 Glossário` (`cd7253c`). O módulo 01 manteve a numeração do Sumário
   (`## 6. 📖 Glossário`) e teve a âncora ajustada.
2. **Micro-checkpoints T2 (`452c83a`).** 13 blocos ⏸️ "Rode agora" distribuídos nos 6 módulos
   ≥450 linhas (02×3, 01/04/08/09/15×2), cada um apontando para o comando real do módulo e um
   output verificado no `run.py`. Diff 100% aditivo (96 inserções, 0 remoções).
3. **Anti-dependência de modelo T7 (`de9b730` + `2f34b01`).** Callout "💡 Modelo é exemplo,
   não requisito" nos módulos densos (01/08/10/14). Além disso, foi descoberto e corrigido um
   **bug real**: os run.py de 04/05/06/08 chamavam `get_required_secret("DEFAULT_MODEL",
   "gpt-4o-mini")` com 2 argumentos contra uma assinatura de 1 → `TypeError` em runtime. Agora há
   `shared.security.get_model()` (ordem `MODEL` > `DEFAULT_MODEL` > default), e o módulo 01 passou a
   ler o modelo do ambiente. Trocar provedor = editar `.env`, sem tocar em código.

**Validação:** `py_compile` OK em todos os run.py alterados; `get_model()` testado (default e override);
suíte compartilhada com 9 passed e 2 falhas **pré-existentes** (`format_cost_small`, `sanitize_for_log`,
confirmadas por stash no HEAD — alheias a estas mudanças, ficam como dívida técnica separada). Zero
corrupção (U+FFFD = 0) após todas as edições UTF-8.

---

## Resumo executivo

O curso é **didaticamente maduro no tripé estrutura/prática/erros**: todos os 16 módulos seguem o
mesmo esqueleto confiável (pré-requisito → objetivos verificáveis → teoria sob demanda → código
guiado → troubleshooting → checklist), com scaffolding real (esqueleto + exercícios + solução) e
gestão consciente de carga cognitiva (blocos "Avançado OPCIONAL"). Os pré-requisitos ocultos de IA
e de programação básica são neutralizados cedo e com analogias. As notas baixam por dois motivos
concentrados: **(1)** o arco de Produção (09–16) pressupõe habilidades operacionais (Docker, FastAPI,
git) que o perfil "iniciante em programação" não tem garantido, sem um onboarding de transição; e
**(2)** inconsistências de superfície que confundem o aluno sobre o próprio percurso (README fala
"capítulo/livro", FINAL_PROJECT fala "P0–P11", ambos contra a padronização "Módulo 01–16").

## As 3 prioridades mais urgentes de correção

1. **Alinhar superfície à decisão "Módulo"** — corrigir `README.md` (capítulo/livro → módulo) e
   `FINAL_PROJECT.md` (P0–P11 → 01–16 ou tabela de correspondência). É barato, remove contradição
   direta com os MATERIAL.md e restaura o elo promessa↔percurso. *(T4)*
2. **Criar onboarding de Produção antes do módulo 09** — mini-guia/módulo-ponte com Docker, uvicorn
   e git do zero, e declarar pré-requisitos operacionais no topo de 09–16. *(T1 + T6)*
3. **Adicionar Glossário aos módulos 07–16** — fechar a lacuna de vocabulário exatamente onde o
   jargão é mais denso (SSE, golden dataset, A/B, cache, skills, CI/CD). *(T5)*

## Pontos fortes que devem ser preservados

- **Carga cognitiva bem gerida**: separação sistemática de "🔬 Avançado — OPCIONAL" permite leitura
  progressiva sem sobrecarregar o iniciante.
- **Scaffolding completo e uniforme**: trindade MATERIAL/run.py/miniproject + esqueleto/exercícios/
  solução + checklist de auto-verificação nos 16 módulos (16/16 no checklist de miniprojetos).
- **Anti-dependência de fornecedor**: alternativas explícitas (Anthropic/Google/Ollama local) e
  fallbacks arquiteturais (embedder local BGE) ensinam princípios transferíveis, não uma API só.
