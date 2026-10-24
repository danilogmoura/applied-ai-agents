# 📚 Glossário Unificado do Curso

> Todas as siglas e termos técnicos dos **16 módulos**, num só lugar. Cada módulo tem
> seu glossário local (no fim do `MATERIAL.md`); esta página os **consolida** para você
> consultar sem precisar lembrar em qual módulo o termo apareceu.
>
> Como usar: procure a sigla na tabela rápida abaixo, ou o termo na seção do módulo.
> Precisa de fluência na *sintaxe* Python usada no código? Veja a
> **[Ponte Python](PYTHON_BRIDGE.md)** — este glossário cobre *vocabulário*, aquela cobre *código*.

---

## 🔤 Siglas — consulta rápida

| Sigla | Significa | Módulo |
|-------|-----------|--------|
| **API** | Interface para chamar o modelo remotamente | [M01](modules/01-fundamentos/MATERIAL.md) |
| **HITL** | Human-in-the-Loop — aprovação humana antes de ação crítica | [M06](modules/06-tool-calling/MATERIAL.md) |
| **JSON** | Formato de dados tipo dicionário Python | [M02](modules/02-primeiro-llm/MATERIAL.md) |
| **LFU** | Least Frequently Used: remove o item menos acessado no total | [M14](modules/14-cache/MATERIAL.md) |
| **LLM** | Large Language Model | [M01](modules/01-fundamentos/MATERIAL.md) |
| **LRU** | Least Recently Used: remove o item há mais tempo não acessado | [M14](modules/14-cache/MATERIAL.md) |
| **RAG** | Retrieval Augmented Generation | [M01](modules/01-fundamentos/MATERIAL.md) |
| **SSE** | Server-Sent Events — protocolo para streaming unidirecional | [M01](modules/01-fundamentos/MATERIAL.md) |
| **TTFT** | Time To First Token: latência até o primeiro caractere aparecer | [M13](modules/13-streaming/MATERIAL.md) |

---

## 📖 Termos completos, por módulo

### Módulo 01 — 01 Fundamentos

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Alucinação** | Resposta plausível mas factualmente errada | Mentir com confiança |
| **API** | Interface para chamar o modelo remotamente | O "telefone" para falar com o LLM |
| **Context window** | Limite de tokens que o modelo pode processar | Memória de trabalho do modelo |
| **Embedding** | Vetor numérico que representa significado de texto | Coordenadas GPS para significado |
| **Fine-tuning** | Treinar adicionalmente um modelo pré-treinado | Especializar o modelo |
| **Inferência** | Gerar resposta a partir de um prompt | Usar o modelo (vs treinar) |
| **Latência** | Tempo entre enviar prompt e receber resposta | Quão rápido responde |
| **LLM** | Large Language Model — modelo treinado em texto | Um leitor voraz que prevê a próxima palavra |
| **Prompt** | Entrada enviada ao modelo | A pergunta ou instrução que você faz |
| **RAG** | Retrieval Augmented Generation — busca contexto antes de responder | Consultar enciclopédia antes de responder |
| **SSE** | Server-Sent Events — protocolo para streaming unidirecional | Canal aberto para enviar dados progressivos |
| **System prompt** | Instrução que define o comportamento do modelo | O "manual de instruções" interno |
| **Temperature** | Controle de aleatoriedade nas respostas | Criatividade vs precisão |
| **Throughput** | Quantas requisições por segundo o sistema aguenta | Capacidade de escala |
| **Token** | Unidade básica de texto (palavra/parte de palavra) | Sílabas para o modelo |
| **Tool calling** | Modelo decide chamar funções externas | Agente usando ferramentas |

### Módulo 02 — 02 Primeiro Llm

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **API Key** | Senha para acessar serviços de IA | Senha para um serviço online |
| **Fallback** | Plano B quando falha | Rota alternativa |
| **JSON** | Formato de dados tipo dicionário Python | Nota estruturada |
| **Latency** | Tempo entre envio e resposta | Ping em jogos online |
| **Prompt** | Texto enviado ao LLM como instrução | Instruções para um assistente muito literal |
| **Temperature** | Controle de criatividade (0=determinístico, 1=variado) | Modificador de dado |
| **Token** | Pedaço de texto (palavra, parte de palavra) | Sílabas na leitura |

### Módulo 03 — 03 Viabilidade

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Benchmark** | Teste comparativo entre soluções | Corrida para ver quem é mais rápido |
| **Break-even** | Ponto onde custos se igualam | "A partir daqui compensa investir" |
| **Heurística** | Regra prática simples | "Regra de dedo" |
| **Latência P95** | Tempo que 95% das chamadas respeitam | "Quase sempre é mais rápido que isso" |
| **Memorando** | Documento de decisão baseado em dados | "Relatório executivo" |
| **Threshold** | Limite mínimo aceitável | "A partir daqui é problema" |

### Módulo 04 — 04 Rag

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **ChromaDB** | Banco vetorial open-source leve | "Uma opção de Vector DB, como escolher entre Spotify ou Apple Music" |
| **Chunking** | Dividir texto longo em pedaços menores | "Cortar livro em capítulos para ler melhor" |
| **Cosine Similarity** | Medida de similaridade entre vetores (0 a 1) | "Quanto mais próximos os GPS, mais similares os textos" |
| **Embedding** | Vetor numérico que representa significado de texto | "GPS para significado" — textos similares ficam próximos |
| **RAG** | Retrieval-Augmented Generation — busca docs relevantes antes de responder | "Abrir o livro certo antes de responder a pergunta" |
| **top_k** | Número de resultados retornados pela busca | "Pedir os 3 melhores resultados" |
| **Vector DB** | Banco que armazena e busca embeddings rapidamente | "Biblioteca com catálogo inteligente" |

### Módulo 05 — 05 Autoavaliacao

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **beta.** | Prefixo experimental da API OpenAI | Versão teste de app novo |
| **Loop de Refinamento** | Gera → Avalia → Refina → Reavalia | Revisar um texto várias vezes |
| **max_iterations** | Limite máximo de tentativas | Tempo limite de prova |
| **Pydantic** | Biblioteca para validação estruturada de dados | Formulário com campos obrigatórios |
| **Structured Output** | JSON com formato previsível e validado | Receita de bolo passo a passo |
| **temperature=0** | Modo determinístico (mesmo input = mesmo output) | Robô seguindo receita vs artista improvisando |
| **ValidationError** | Exceção lançada quando JSON não valida | Formulário rejeitado pelo sistema |

### Módulo 06 — 06 Tool Calling

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Attention** | Mecanismo que conecta palavras do prompt às tools | Concentração ao ler instruções |
| **Fine-tuned** | Treinamento específico para reconhecer padrões | Piloto experiente reconhecendo situações |
| **HITL** | Human-in-the-Loop — aprovação humana antes de ação crítica | Freio de mão em encruzilhada perigosa |
| **JSON Schema** | Formato estruturado que descreve parâmetros da tool | Receita de bolo com ingredientes exatos |
| **Risk Level** | Classificação de perigo (LOW→CRITICAL) | Semáforo: verde/amarelo/vermelho |
| **Tool Calling** | Padrão onde LLM decide qual função externa chamar | Motorista escolhendo rota no GPS |
| **Whitelist** | Lista de ferramentas/comandos permitidos | Porteiro que só deixa entrar convidados |

### Módulo 07 — 07 Planejamento

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Checkpoint** | Ponto onde o progresso do plano é salvo para retomar sem recomeçar do zero | Salvar o jogo antes do chefe |
| **Circuit Breaker** | Padrão que interrompe chamadas a um serviço após N falhas seguidas, evitando efeito cascata | Disjuntor que desarma antes de pegar fogo na instalação |
| **Degradação Elegante** | Reduzir escopo/qualidade em vez de falhar tudo quando uma parte quebra | Servir o prato principal mesmo sem a sobremesa |
| **Planejador (Planner)** | Componente que decompõe um objetivo em passos executáveis e decide a ordem das ações | GPS que traça a rota antes de você ligar o carro |
| **Resiliência** | Capacidade do planejador de continuar diante de erros parciais dos serviços | Rota alternativa quando uma ponte cai |
| **Simulação de Serviço** | Stand-in falso de uma tool/API para testar o planner sem depender do serviço real | Manequim de teste antes do voo real |

### Módulo 08 — 08 Multiagente

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Custo em Multiagente** | Somatório de tokens/chamadas de todos os agentes; cresce multiplicativamente | Várias corridas de táxi em vez de uma |
| **Degradação Elegante** | Continuar entregando resultado parcial quando um agente falha | Turno reduzido mantendo o serviço essencial |
| **Heurística de Roteamento** | Regra determinística (palavra-chave, regex) para escolher o agente, mais barata que LLM | Etiqueta de cor que já diz o setor |
| **Roteamento** | Decidir qual agente trata cada entrada (via LLM ou heurística) | Recepcionista que transfere a ligação |
| **Sistema Multiagente** | Arquitetura com vários agentes especializados coordenados para uma tarefa | Time com médico, enfermeiro e farmácia |
| **Supervisor-Especialista** | Padrão onde um agente roteia tarefas para especialistas e agrega resultados | Coordenador distribuindo tickets para técnicos |

### Módulo 09 — 09 Producao Api

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **API REST** | Interface que expõe funcionalidade via HTTP e JSON, separando cliente de servidor | Cardápio fixo de um restaurante |
| **Docker / Container** | Empacota app + dependências numa imagem reproduzível; container é a instância rodando | Casa pré-fabricada: mesma planta em qualquer terreno |
| **docker-compose** | Arquivo YAML que sobe vários containers juntos em ordem | Capataz erguendo várias casas em sequência |
| **Endpoint / Rota** | Endereço (ex.: POST /chat) que recebe e devolve JSON | Balcão específico para cada tipo de pedido |
| **FastAPI** | Framework web Python moderno para criar APIs com validação automática | Cozinha pronta com fichas de pedido |
| **Middleware** | Camada que processa toda requisição antes/depois da rota (log, auth) | Segurança que carimba cada crachá na entrada |
| **Pydantic Model** | Classe que define o contrato (campos/tipos) de entrada e saída da API | Formulário com campos obrigatórios |
| **uvicorn** | Servidor ASGI que executa a aplicação FastAPI e fica escutando | Caixa que abre e atende até fechar a loja |

### Módulo 10 — 10 Avaliacao

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Benchmarking Regressivo** | Rodar a avaliação a cada mudança para detectar perda de qualidade | Teste de regressão antes do deploy |
| **Fuzzy Match** | Similaridade aproximada entre texto esperado e obtido (não exige igualdade exata) | Nota por proximidade, não cópia literal |
| **Golden Dataset** | Conjunto de entradas com respostas esperadas usadas como gabarito de referência | Prova com gabarito oficial |
| **LLM-as-a-Judge** | Usar um LLM para pontuar a qualidade da saída de outro LLM | Corretor automatizado lendo as redações |
| **Métrica de Avaliação** | Número que quantifica qualidade (precisão, similaridade, taxa de sucesso) | Régua graduada para medir acerto |
| **Significância Estatística** | Grau de confiança de que a diferença de score não foi por acaso | Repetir o experimento para confirmar |
| **Teste A/B** | Comparar duas variantes medindo qual performa melhor | Duas embalagens, ver qual vende mais |

### Módulo 11 — 11 Seguranca

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Content Filtering** | Inspeção de entrada/saída para bloquear conteúdo proibido | Filtro que revira a bagagem na alfândega |
| **Data Leakage** | Exposição acidental de dados sensíveis na saída do modelo | Recibo impresso com dado de cartão |
| **Defesa em Camadas** | Múltiplos controles independentes (input, modelo, output) somados | Porta, trava e alarme ao mesmo tempo |
| **Jailbreak** | Tentativa de contornar as restrições/alinhamento do modelo via prompt elaborado | Chave-mestra falsa para abrir área restrita |
| **Principle of Least Privilege** | Dar a cada componente apenas as permissões mínimas necessárias | Crachá que abre só o seu andar |
| **Prompt Injection** | Ataque que embute instruções maliciosas na entrada para sequestrar o comportamento do modelo | Golpista que cola ordens falsas no memorando interno |

### Módulo 12 — 12 Memoria

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Conversation History** | Sequência de mensagens trocadas que dá coerência ao diálogo | Fio da conversa até agora |
| **Importância / Forgetting** | Política que reforça memórias relevantes e descarta as esquecidas | Você lembra mais o que usa todo dia |
| **Janela de Contexto** | Quantos tokens o modelo considera de uma vez | Área visível da tela, o resto rola fora |
| **Long-Term Memory** | Conhecimento persistente recuperável entre sessões (ex.: vetor/embedding) | Agenda guardada na gaveta para consultar depois |
| **Short-Term Memory** | Histórico da conversa atual, limitado pela janela de contexto | Memória de trabalho, some ao virar a página |
| **Summarization** | Comprimir o histórico antigo em resumo para caber no contexto | Ata resumida da reunião longa |

### Módulo 13 — 13 Streaming

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Abort / Cancel** | Interromper a geração em andamento quando o cliente fecha ou pede stop | Desligar o microfone no meio da frase |
| **Latência Percebida vs Real** | Sensação de rapidez (fluxo imediato) pode ser melhor que o tempo total | Fila que anda parece mais curta |
| **SSE (Server-Sent Events)** | Protocolo HTTP unidirecional servidor→cliente para enviar eventos contínuos | Rádio transmitindo em fluxo |
| **Streaming** | Enviar a resposta em pedaços conforme é gerada, em vez de esperar o fim | Narração ao vivo em vez de gravação editada |
| **TTFT** | Time To First Token: latência até o primeiro caractere aparecer | Tempo até a voz do narrador começar |
| **Wire Format SSE** | Mensagem 'data: ...' enviada pelo canal de eventos | Telegrama em blocos padronizados |

### Módulo 14 — 14 Cache

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Cache de Respostas** | Guardar saídas passadas para reusar em perguntas idênticas e cortar custo | Gabarito colado na parede para não recalcular |
| **Eviction Policy** | Regra de quais itens remover quando a cache está cheia | Estante lotada: tirar o menos usado |
| **LFU** | Least Frequently Used: remove o item menos acessado no total | Livro que ninguém folheia sai primeiro |
| **LRU** | Least Recently Used: remove o item há mais tempo não acessado | Quem pega por último fica na frente |
| **Model Routing** | Escolher modelo diferente conforme dificuldade/custo da requisição | Casos simples pro estagiário, complexos pro sênior |
| **Prompt Compression** | Reduzir o tamanho do prompt preservando sentido, cortando tokens/custo | Resumir o e-mail longo em duas linhas |

### Módulo 15 — 15 Skills

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Filtro de Pipeline** | Estágio que seleciona/transforma/pass adiante itens no fluxo | Peneira que só deixa grãos do tamanho certo |
| **Interface Padrão** | Contrato comum (entrada/saída) que torna skills intercambiáveis | Tomada universal: qualquer plugue encaixa |
| **Pipeline Composition** | Encadear várias skills em sequência para formar um fluxo maior | Linha de montagem passando de estação a estação |
| **Registry de Skills** | Catálogo central que lista skills disponíveis e suas versões | Almoxarifado com inventário de peças |
| **Skill** | Unidade modular de capacidade com interface padrão, versionada e plugável num agente | Peça Lego que encaixa em qualquer conjunto |
| **Versionamento Semântico** | Esquema MAJOR.MINOR.PATCH para comunicar compatibilidade entre versões | Etiqueta que avisa se a peça mudou de formato |

### Módulo 16 — 16 Operacoes

| Termo | Definição | Analogia |
|-------|-----------|----------|
| **Exponential Backoff** | Aumentar o tempo de espera entre tentativas após falha | Esperar 1s, 2s, 4s... antes de ligar de novo |
| **Jitter** | Variação aleatória somada ao backoff para evitar sincronia de retries | Escalonar horários para não formarem fila |
| **Logging Estruturado** | Registros em campos chave-valor (JSON) pesquisáveis, não texto solto | Planilha de ocorrências em vez de bilhetes |
| **Métricas Essenciais** | Indicadores de produção: latência, erro, custo, throughput | Velocímetro, conta-giros e tanque juntos |
| **Observabilidade** | Capacidade de inferir o estado interno do sistema por suas saídas (logs/métricas/traces) | Painel do carro mostrando temperatura e RPM |
| **Prompt Testing (A/B)** | Validar mudanças de prompt em produção comparando variantes | Trocar o aviso da vitrine e medir cliques |
| **Rollback Automático** | Reverter para a última versão boa quando uma nova degrada | Botão de desfazer após um deploy ruim |

---

📚 Voltar ao índice: [`README.md`](README.md) · Vocabulário ↔ código: [`PYTHON_BRIDGE.md`](PYTHON_BRIDGE.md)
