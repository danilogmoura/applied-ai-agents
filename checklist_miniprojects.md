# Checklist — Validação dos `miniproject.md`

> **Atualização (#7 VALIDA-IA):** A auditoria anterior marcou 16/16 ✅, mas uma
> verificação real do disco mostrou que **M04 e M05 não tinham seção de critérios**
> e **M01/M02 usavam vocabulário divergente** ("Critérios de avaliação"/"Checklist
> de validação"). Todos foram padronizados agora no formato canônico:
> `## ✅ Critérios de Sucesso` + linha "só se conseguir fazer sem olhar o material",
> posicionado entre Guia e Teste. Os 16 miniprojetos passam na verificação automática.

**Objetivo:** Validar se cada `miniproject.md` tem os 4 elementos obrigatórios:

1. **Descrição** — o que o aluno vai construir
2. **Passos guiados** — tutorial passo-a-passo ou referência a guia externo
3. **Output esperado** — como testar / resultado esperado
4. **Critérios de sucesso** — checklist ou tabela de avaliação

---

## ✅ Todos os 16 módulos validados (100%)

| # | Módulo | Descrição | Passos Guiados | Output Esperado | Critérios Sucesso | Status |
| --- | -------- | ----------- | ---------------- | ----------------- | ------------------- | -------- |
| 1 | 01-fundamentos | ✅ | ✅ | ✅ | ✅ | ✅ |
| 2 | 02-primeiro-llm | ✅ | ✅ | ✅ | ✅ | ✅ |
| 3 | 03-viabilidade | ✅ | ✅ | ✅ | ✅ | ✅ |
| 4 | 04-rag | ✅ | ✅ | ✅ | ✅ | ✅ |
| 5 | 05-autoavaliacao | ✅ | ✅ | ✅ | ✅ | ✅ |
| 6 | 06-tool-calling | ✅ | ✅ | ✅ | ✅ | ✅ |
| 7 | 07-planejamento | ✅ | ✅ | ✅ | ✅ | ✅ |
| 8 | 08-multiagente | ✅ | ✅ | ✅ | ✅ | ✅ |
| 9 | 09-producao-api | ✅ | ✅ | ✅ | ✅ | ✅ |
| 10 | 10-avaliacao | ✅ | ✅ | ✅ | ✅ | ✅ |
| 11 | 11-seguranca | ✅ | ✅ | ✅ | ✅ | ✅ |
| 12 | 12-memoria | ✅ | ✅ | ✅ | ✅ | ✅ |
| 13 | 13-streaming | ✅ | ✅ | ✅ | ✅ | ✅ |
| 14 | 14-cache | ✅ | ✅ | ✅ | ✅ | ✅ |
| 15 | 15-skills | ✅ | ✅ | ✅ | ✅ | ✅ |
| 16 | 16-operacoes | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## Resumo Final

**Todos os 16 `miniproject.md` validados com sucesso!**

Cada arquivo agora contém os 4 elementos obrigatórios da rubrica VALIDA-IA:

| Elemento | Descrição |
| ---------- | ----------- |
| ✅ **Descrição** | O que o aluno vai construir (objetivo claro) |
| ✅ **Passos guiados** | Tutorial passo-a-passo com código exemplo (6-7 passos) |
| ✅ **Output esperado** | Seção "Teste seu código" com comandos bash |
| ✅ **Critérios de sucesso** | Checklist verificável ("só se conseguir fazer sem olhar") |

**Status:** 16/16 módulos ✅ (100%)
| 16 | 16-operacoes | ✅ | ✅ | ✅ | ✅ | ✅ |

---

**Resumo:** Todos os 16 `miniproject.md` agora contêm os 4 elementos obrigatórios:

- ✅ **Descrição** clara do que construir
- ✅ **Passos guiados** com código exemplo (6-7 passos cada)
- ✅ **Output esperado** via seção "Teste seu código"
- ✅ **Critérios de sucesso** com checklist verificável

---

## Progresso

- [ ] **Módulo 3/16:** 03-viabilidade — faltam passos guiados + critérios
- [ ] **Módulo 4/16:** 04-rag — faltam passos guiados + critérios
- [ ] **Módulo 5/16:** 05-autoavaliacao — faltam passos guiados + critérios
- [ ] **Módulo 6/16:** 06-tool-calling — faltam passos guiados + critérios
- [ ] **Módulo 7/16:** 07-planejamento — faltam passos guiados + critérios
- [ ] **Módulo 8/16:** 08-multiagente — faltam passos guiados + critérios
- [ ] **Módulo 9/16:** 09-producao-api — faltam passos guiados + critérios
- [ ] **Módulo 10/16:** 10-avaliacao — faltam passos guiados + critérios
- [ ] **Módulo 11/16:** 11-seguranca — faltam passos guiados + critérios
- [ ] **Módulo 12/16:** 12-memoria — faltam passos guiados + critérios
- [ ] **Módulo 13/16:** 13-streaming — faltam passos guiados + critérios
- [ ] **Módulo 14/16:** 14-cache — faltam passos guiados + critérios
- [ ] **Módulo 15/16:** 15-skills — faltam passos guiados + critérios
- [ ] **Módulo 16/16:** 16-operacoes — faltam passos guiados + critérios

---

## Padrão para Adicionar

### Passos Guiados (nova seção)

```markdown
## 📖 Guia Passo a Passo

1. **Crie a classe principal** com os métodos listados nos requisitos
2. **Implemente o método X** seguindo o exemplo...
3. **Teste com dados simulados** antes de usar API real
4. **Valide o output** comparando com o esperado...
```

### Critérios de Sucesso (nova seção)

```markdown
## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] Classe funciona com dados de teste
- [ ] Método X retorna formato esperado
- [ ] Error handling cobre casos críticos
- [ ] Custo estimado é calculado corretamente
- [ ] Código passa nos testes do módulo

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondantes antes de prosseguir.
```
