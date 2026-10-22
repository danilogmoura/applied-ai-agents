# Applied AI Agents 🤖

Repositório dedicado ao estudo e desenvolvimento de Agentes de Inteligência Artificial utilizando **Python**. O foco desta trilha não é apenas "fazer funcionar", mas sim construir soluções orientadas a engenharia, considerando **Custo**, **Observabilidade**, **Segurança** e **Governança**.

A metodologia aplicada é o **PBL (Aprendizagem Baseada em Problemas)**, onde cada módulo resolve um desafio prático de negócios e a tecnologia entra apenas como ferramenta de solução.

## 📌 Arquitetura da Trilha

Este repositório está estruturado em 8 laboratórios progressivos:

| Módulo | Desafio | Foco Principal |
| :--- | :--- | :--- |
| **[P0](./P0-Primeiro-Fluxo)** | Primeiro fluxo com LLM | Automação via API, proteção de chaves (secrets), tratamento de erros e métricas de custo. |
| **[P1](./P1-Analise-Viabilidade)** | Análise de viabilidade | Avaliação técnica (IA vs. Algoritmo tradicional), latência e custo-benefício. |
| **[P2](./P2-RAG)** | Recuperação de Contexto (RAG) | Busca de informações locais, vetorização, redução de alucinações e consumo de tokens. |
| **[P3a-1](./P3a1-Reflexao)** | Autoavaliação e reflexão | LLMs criticando a própria saída, Structured Outputs e controle de loops infinitos. |
| **[P3a-2](./P3a2-Tool-Calling)** | Uso autônomo de ferramentas | Tool calling, princípio do menor privilégio e *Human-in-the-loop* (aprovação humana). |
| **[P3a-3](./P3a3-Resiliencia)** | Planejamento e retomada | Circuit breakers, tratamento de indisponibilidade de APIs externas e checkpoints. |
| **[P3b](./P3b-Multiagente)** | Sistema multiagente | Roteamento de tarefas (Router), agentes especialistas e degradação elegante. |
| **[P4](./P4-Producao)** | Produto em produção | Exposição via API (FastAPI), empacotamento com Docker, documentação e monitoramento. |

## 🛠️ Stack Tecnológico Base

*   **Linguagem:** Python 3.12+
*   **Frameworks de IA:** *A definir conforme o módulo (LangChain, LangGraph, OpenAI SDK)*
*   **APIs e Backend:** FastAPI, Uvicorn, Pydantic
*   **Ferramentas:** Docker, python-dotenv (gestão de variáveis de ambiente), tiktoken (cálculo de custos)

## 🚀 Como iniciar

1. Clone o repositório:
   ```bash
   git clone [https://github.com/seu-usuario/applied-ai-agents.git](https://github.com/seu-usuario/applied-ai-agents.git)
