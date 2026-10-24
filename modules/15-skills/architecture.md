# 🏗️ Architecture Design — Sistema de Skills Modular

> **Desafio:** Projete um sistema de skills reutilizáveis e composáveis para um agente de IA versátil.
>
> 🔬 **AVANÇADO / OPCIONAL** — Este desafio assume noções de arquitetura e infra. Se você ainda está aprendendo os fundamentos, tudo bem pular na primeira passada e voltar depois.

## Cenário

Uma empresa quer construir um agente que faça várias coisas:

- Classificar tickets
- Buscar informações em APIs externas
- Gerar resumos de documentos
- Traduzir textos
- Extrair entidades de texto
- Calcular custos de projetos

Requisitos:

- Cada skill deve ser **independente** e **testável**
- Skills devem ser **componíveis** em pipelines
- Novas skills podem ser adicionadas sem quebrar existentes
- Versionamento SemVer (Semantic Versioning — versionamento semântico no formato `MAJOR.MINOR.PATCH`, onde MAJOR muda quando há quebra de compatibilidade) para evolução segura
- Filtros no pipeline (confiança mínima, rate limiting)

---

## Entregáveis

> 🧭 **Como abordar este desafio.** Não existe uma única arquitetura correta — o que se avalia é o seu **raciocínio**. Sugestão de caminho:
>
> 1. Comece rascunhando o diagrama com blocos e setas (ASCII serve).
> 2. Para cada decisão na tabela, registre *o que escolheu* **e por quê**.
> 3. Feche com números de custo/reuso, mesmo estimados.
>
> Exemplo ilustrativo (não é gabarito): ao compor skills, defina claramente o contrato entre elas (o que cada uma recebe e devolve) — composição sem contrato vira acoplamento frágil.

### 1. Diagrama da Arquitetura

```
[Input] → [Skill Router] → [Pipeline: Skill A → Skill B → Skill C] → [Output]
                    ↑              ↑              ↑              ↑
              [Registry]     [Validator]    [Filter]       [Result]
```

Defina:

- Como skills são registradas e descobertas?
- Como pipelines são definidos?
- Onde ficam os filtros e validações?

### 2. Decisões Arquiteturais

| Decisão | Opções | Sua Escolha | Justificativa |
| --------- | -------- | ------------- | --------------- |
| **Registro** | Registry centralizado | Service discovery | ? |
| **Composição** | Pipeline linear | DAG (Directed Acyclic Graph — grafo direcionado acíclico, permite ramificar/combinar skills em vez de só encadear em fila) | ? |
| **Versionamento** | SemVer estrito | Compatibilidade por contrato | ? |
| **Error handling** | Fail-fast | Fallback por skill | ? |
| **Filtros** | Middleware | Inline nas skills | ? |
| **Testing** | Unit test por skill | Integration test por pipeline | ? |

### 3. Exemplo de Pipeline Completo

Escolha 3-4 skills e desenhe o pipeline:

```
Input: "Preciso de um resumo do relatório Q3 e tradução para inglês"

Pipeline:
1. Intent Classifier → ["summarize", "translate"]
2. Document Fetcher → [PDF/Q3_report.pdf]
3. Summarizer → [resumo_gerado]
4. Translator → [resumo_traduzido]
5. Output Validator → [validado]
```

Para cada etapa, defina:

- Input schema
- Output schema
- Filtros aplicados
- Fallback se falhar

### 4. Matriz de Dependências

| Skill | Depende de | É usada por | Versão |
| ------- | ----------- | ------------- | -------- |
| Intent Classifier | Nenhuma | Pipeline router | 1.0.0 |
| Document Fetcher | HTTP client | Summarizer, Extractor | 1.2.0 |
| Summarizer | Document Fetcher | Output validator | 2.0.0 |
| Translator | Summarizer | Output validator | 1.1.0 |
| Output Validator | Nenhuma | Pipeline router | 1.0.0 |

Quebra de versão (major): quais pipelines seriam afetados?

---

## Checklist de Validação

- [ ] Sistema de registro de skills definido
- [ ] Composição de pipelines clara (linear ou DAG)
- [ ] Versionamento SemVer aplicado corretamente
- [ ] Error handling definido (fail-fast ou fallback)
- [ ] Filtros posicionados corretamente no pipeline
- [ ] Matriz de dependências completa
- [ ] Breaking changes mapeados

---

## Critérios de Avaliação

| Critério | Excelente (5) | Bom (3) | Fraco (1) |
| ---------- | -------------- | --------- | ----------- |
| **Modularidade** | Skills truly independentes | Acoplamento parcial | Dependências circulares |
| **Composição** | Pipeline flexível e claro | Composição rígida | Sem composição |
| **Versionamento** | Breaking changes mapeados | Versões listadas | Sem versionamento |
| **Error handling** | Fallback por cenário | Único tratamento | Sem tratamento |
