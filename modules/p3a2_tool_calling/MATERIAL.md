# Material Didático — P3a-2: Tool Calling (Uso Autônomo de Ferramentas)

## Conceitos Fundamentais

### Do Texto à Ação

Até agora, nossos agentes só **geravam texto**. Mas no mundo real, agentes precisam:

- Ler arquivos do sistema de arquivos
- Consultar APIs externas
- Executar comandos
- Modificar estados

Tool calling transforma um LLM passivo em um agente ativo.

### O Pattern de Tool Calling

```
Usuário → [Agente] → "Preciso da ferramenta X com params Y"
                ↓
        [Executor] → Chama função Python real
                ↓
        [Resultado] → Retorna ao agente
                ↓
        [Agente] → Formata resposta final
```

O LLM não executa a ferramenta diretamente — ele **decide** qual ferramenta usar e **descreve** os parâmetros. Um executor seguro roda a função real.

### JSON Schema como Contrato

Cada ferramenta tem um schema que define seus parâmetros:

```json
{
  "type": "function",
  "function": {
    "name": "read_file",
    "description": "Lê conteúdo de um arquivo",
    "parameters": {
      "type": "object",
      "properties": {
        "file_path": {"type": "string", "description": "Caminho do arquivo"},
        "max_lines": {"type": "integer", "default": 100}
      },
      "required": ["file_path"]
    }
  }
}
```

Este schema é enviado ao LLM junto com o prompt. O modelo responde com JSON estruturado que pode ser validado e executado programaticamente.

### Como o Modelo Decide Chamar uma Tool

O modelo **não tem um switch ligado/desligado** para ferramentas. Ele foi **fine-tuned** durante o treinamento para reconhecer padrões nos prompts que indicam necessidade de ação.

```
Prompt recebido:
  system: "Você é um assistente com 3 ferramentas..."
  tools: [read_file, list_dir, execute_command]
  user: "Leia /etc/hosts"
         ↓
[Modelo processa com attention entre user + tools schemas]
         ↓
O modelo reconhece:
  - A palavra "Leia" → mapeia para função read_file
  - "/etc/hosts" → extrai como argumento file_path
         ↓
Resposta do modelo (JSON):
{
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "read_file",
        "arguments": '{"file_path": "/etc/hosts"}'
      }
    }
  ]
}
```

**Por que às vezes o modelo ignora ferramentas?**

1. **Schema mal descrito**: Se `description` é vago, o modelo não associa a ferramenta à intenção do usuário
2. **Prompt ambíguo**: "Me dá uma info sobre isso" — qual tool? Nenhuma descrição combina bem
3. **Overfitting**: Modelos treinados em dados específicos tendem a usar tools só quando o padrão é familiar

**Por que às vezes inventa argumentos?**

O modelo tenta ser útil. Se você pediu algo que nenhuma tool cobre, ele pode "alucinar" parâmetros imaginários tentando forçar uma chamada. Por isso a validação rigorosa é obrigatória.

### Segurança: Princípio do Menor Privilégio

Agentes com acesso a ferramentas são perigosos se não forem restritos:

| Camada de Segurança | O que faz |
| --------------------- | ----------- |
| **Whitelist** | Só permite comandos/funções pré-aprovados |
| **Risk Levels** | Classifica cada tool (LOW/MEDIUM/HIGH/CRITICAL) |
| **Human-in-the-Loop** | Pede aprovação humana para ações críticas |
| **Timeouts** | Limita tempo de execução |
| **Output Limits** | Trunca respostas muito longas |

### Human-in-the-Loop (HITL)

Para ações de risco HIGH ou CRITICAL, o agente pausa e pergunta ao humano:

```
⚠️ AÇÃO REQUER APROVAÇÃO HUMANA
┌─────────────────────────────────┐
│ Tool: execute_command           │
│ Comando: rm -rf /tmp/cache      │
│ Risco: HIGH                     │
│                                 │
│ [Y] Aprovar  [N] Recusar       │
└─────────────────────────────────┘
```

Isso garante que humanos mantenham controle sobre decisões importantes.

---

## Exercício Prático

Execute `python modules/p3a2_tool_calling/run.py` e observe:

1. Como o agente decide qual ferramenta usar baseado na pergunta
2. As ferramentas sendo executadas (ler arquivo, listar diretório, buscar)
3. Quando o HITL é acionado para ações de alto risco
4. O relatório de custos por ferramenta usada

## Perguntas para Reflexão

1. Que riscos existem em permitir que um LLM execute comandos shell? Como você mitigaria?
2. Se uma tool falhasse com erro, o agente deveria tentar outra tool ou pedir ajuda humana?
3. Como você implementaria rate limiting para evitar abuso de ferramentas?

---

## Referências

### Livros

- **"Security Engineering"** by Ross Anderson — Princípios de segurança em sistemas automatizados

### Documentação Oficial

- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)
- [Python subprocess Security](https://docs.python.org/3/library/subprocess.html#security-considerations)

###
