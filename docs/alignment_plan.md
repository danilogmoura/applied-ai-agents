# Plano — README como índice de livro + navegação entre materiais

> **Escopo:** (1) reformatar `README.md` para funcionar como **índice de livro** com uma **introdução** antes; (2) adicionar, em cada `modules/*/MATERIAL.md`, um rodapé de navegação **← Anterior · Índice · Próximo →**.
> **Status:** ✅ executado.
> **Data:** 2026-05-19

---

## 1. Objetivo

O curso hoje tem um `README.md` que é uma tabela de links misturada com instruções de setup. A ideia é transformá-lo em algo que se leia como o **sumário de um livro**: uma introdução que explica "o que você vai aprender e em que ordem", seguida de um índice linear módulo a módulo.

Para que essa leitura flua como capítulos, cada material precisa de **navegação sequencial** no fim: ir para o capítulo anterior, voltar ao índice, ou seguir para o próximo.

---

## 2. Ordem canônica dos módulos ("capítulos")

Definida a partir do índice atual do README. Esta é a sequência usada nos links anterior/próximo:

| # | Código | Título (para o índice) | Pasta |
| --- | -------- | ------------------------ | ------- |
| 1 | P0-F | Fundamentos: O que é IA e LLM? | `01-fundamentos` |
| 2 | P0 | Primeiro fluxo: chamada HTTP a um LLM | `02-primeiro-llm` |
| 3 | P1 | Viabilidade: IA vs regras | `03-viabilidade` |
| 4 | P2 | RAG: recuperação de contexto | `04-rag` |
| 5 | P3a-1 | Autoavaliação | `05-autoavaliacao` |
| 6 | P3a-2 | Tool calling | `06-tool-calling` |
| 7 | P3a-3 | Planejamento resiliente | `07-planejamento` |
| 8 | P3b | Multiagente | `08-multiagente` |
| 9 | P4 | Produção (API + Docker) | `09-producao-api` |
| 10 | P5 | Avaliação | `10-avaliacao` |
| 11 | P6 | Segurança | `11-seguranca` |
| 12 | P7 | Memória | `12-memoria` |
| 13 | P8 | Streaming | `13-streaming` |
| 14 | P9 | Cache | `14-cache` |
| 15 | P10 | Skills | `15-skills` |
| 16 | P11 | Operações de produção | `16-operacoes` |

- **Primeiro capítulo** (`01-fundamentos`): sem "Anterior".
- **Último capítulo** (`16-operacoes`): sem "Próximo".
- Todos os demais: ambos.

---

## 3. Mudança A — `README.md` como índice de livro

### Estrutura proposta

```
# 📖 <Título do curso>

## Introdução            ← NOVO bloco narrativo
   - Para quem é o curso
   - Como está organizado (fundamentos → contexto → autonomia → produção)
   - Como usar (ler MATERIAL, rodar run.py, fazer miniprojeto)
   - Pré-requisitos resumidos em 1 frase

## Sumário               ← substitui as 4 tabelas soltas por UM índice linear
   Lista numerada 1..16, cada item:
     N. [Título](modules/<pasta>/MATERIAL.md) — <conceito em 1 linha>
        (run.py · miniprojeto) como sub-links discretos

## Como aproveitar o curso   ← mantém os princípios atuais, enxuto
## Instalação / Executar      ← move setup para DEPOIS do sumário (apêndice)
```

### Diretrizes

- **Não remover conteúdo** essencial (princípios, pré-requisitos, instalação) — apenas **reorganizar**: introdução e sumário primeiro, setup depois.
- Sumário vira **lista numerada contínua** (1–16), lida como capítulos, em vez de 4 tabelas separadas por "fase". As fases viram subtítulos dentro da introdução ou cabeçalhos leves do sumário.
- Cada linha do índice aponta para o `MATERIAL.md` (o "capítulo"); `run.py` e `miniproject.md` ficam como links secundários.

### Guardrails

- Manter todos os caminhos de link existentes e válidos.
- Não inventar módulos nem reordenar a sequência pedagógica.

---

## 4. Mudança B — Navegação em cada `MATERIAL.md`

### Formato do rodapé (padrão único)

Inserido **no fim** de cada arquivo:

```
---

## 🧭 Navegação

| ← Anterior | Índice | Próximo → |
| ------------ | -------- | ----------- |
| [P3a-2: Tool Calling](../06-tool-calling/MATERIAL.md) | [📖 Sumário do curso](../../README.md) | [P3a-3: Planejamento](../07-planejamento/MATERIAL.md) |
```

- Primeiro capítulo: célula "Anterior" = `—`.
- Último capítulo: célula "Próximo" = `—`.

### Regras de aplicação

- Aplicar nos **16** arquivos `modules/*/MATERIAL.md`.
- Se o arquivo já termina com uma seção "Próximos Passos"/"Material Complementar", o rodapé de navegação entra **depois** dela (por último).
- Caminhos relativos: de `modules/<pasta>/MATERIAL.md`, o vizinho é `../<outra_pasta>/MATERIAL.md` e o índice é `../../README.md`.

### Guardrails

- Não alterar o corpo do material — só acrescentar o rodapé.
- Conferir que cada pasta vizinha existe antes de gerar o link (evitar link quebrado).

---

## 5. Ordem de execução

1. **B** (navegação nos 16 MATERIAL.md) — define e valida a sequência canônica; é mecânica e testável.
2. **A** (README índice + introdução) — constrói o índice que os links "Índice" apontam.
3. Revisar erros de markdown (tabelas/links) em todos os arquivos tocados.
4. Commit coeso `docs(navegação): README como índice + navegação anterior/próximo nos materiais`.

---

## 6. Checklist de conclusão

- [x] Sequência canônica de 16 capítulos definida e conferida contra as pastas reais
- [x] Rodapé de navegação adicionado nos 16 `MATERIAL.md` (com exceções primeiro/último)
- [x] `README.md` reestruturado: introdução + sumário linear + setup como apêndice
- [x] Todos os links verificados (sem quebrados)
- [x] Sem erros de markdown novos
- [ ] Commit realizado
