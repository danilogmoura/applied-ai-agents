# 🏗️ Architecture Design — Tool Calling Agent

> **Desafio:** Projete um agente com tool calling para automação de suporte técnico.

## Cenário

Uma equipe de suporte precisa automatizar tarefas repetitivas:

- **Ler arquivos** do sistema (logs, configs)
- **Consultar APIs** externas (status de serviços, dados de usuários)
- **Executar comandos** seguros (reiniciar serviço, limpar cache)
- **Enviar notificações** (email, Slack, webhook)

Requisitos:

- Máximo 5 ferramentas definidas
- Whitelist obrigatório para todas as operações
- HITL (Human-in-the-Loop) para operações de risco alto
- Orçamento: máximo $100/mês em API calls
- Se uma tool falhar, tentar fallback ou pedir ajuda humana

---

## Entregáveis

### 1. Diagrama da Arquitetura

Descreva o fluxo do loop tool-calling:

```
[Usuário] → [LLM] → [Parse JSON] → [Executor Seguro] → [Resultado]
              ↑                              ↓
          [Schema] ←─────── [Whitelist + Risk Level]
```

Defina:

- Quantas chamadas ao LLM por tarefa completa?
- Onde estão os pontos de validação?
- Como o resultado volta para o usuário?

### 2. Definição das Tools

Para cada ferramenta, defina:

| Campo | Exemplo |
| ------- | --------- |
| **Nome** | `read_file` |
| **Descrição** | Lê conteúdo de um arquivo do sistema |
| **Parâmetros** | `{file_path: str, max_lines: int}` |
| **Risk Level** | LOW / MEDIUM / HIGH |
| **Precisa HITL?** | Sim/Não |

Crie schemas JSON completos para 5 ferramentas.

### 3. Estratégia de Segurança

Descreva como protege o sistema:

| Camada | Mecanismo | Proteção |
| -------- | ----------- | ---------- |
| Schema validation | Pydantic | JSON inválido não crasha |
| Whitelist | Lista explícita de tools permitidas | Modelo não inventa novas tools |
| Risk levels | LOW/MEDIUM/HIGH por tool | Operações perigosas precisam aprovação |
| HITL | Aprovação humana antes de executar | Usuário confirma ações críticas |
| Rate limiting | Máx N chamadas/minuto | Previne abuso/loop infinito |

### 4. Tratamento de Falhas

O que acontece quando cada componente falha:

| Falha | Comportamento | Fallback |
| ------- | -------------- | ---------- |
| LLM retorna JSON inválido | ? | Re-prompt com instrução de correção |
| Tool indisponível | ? | Pedir ajuda humana ou usar alternativa |
| Rate limit atingido | ? | Backoff exponencial + retry |
| HITL não responde em 5min | ? | Timeout → resposta parcial ao usuário |

---

## Checklist de Validação

- [ ] Loop tool-calling completo (decide → executa → retorna)
- [ ] 5 tools com schemas JSON bem definidos
- [ ] Whitelist implementado para todas as operações
- [ ] Risk levels e HITL configurados corretamente
- [ ] Plano de fallback para cada tipo de falha
- [ ] Custo estimado dentro do orçamento ($100/mês)

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
| ---------- | -------------- | --------- | ----------- |
| **Segurança** | Todas as camadas presentes | Apenas whitelist | Sem proteção |
| **Schemas** | Completos com descrições claras | Parciais | Sem descrição |
| **Fallbacks** | Cobertura completa | Parcial | Ausente |
| **Custo** | Estimativa detalhada | Estimativa global | Sem cálculo |
