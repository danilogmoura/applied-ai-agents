# ⚙️ Setup de Produção — Guia de Transição (antes do Módulo 09)

> **Para quem é:** você concluiu os Módulos 01–08 (rodou scripts Python com uma API de LLM) e está
> prestes a entrar no **Arco 4 — Produção e Operações (Módulos 09–16)**. A partir daqui o curso pede
> ferramentas que vão além de "escrever um script": **um servidor web, um container e controle de
> versão**. Este guia existe para eliminar esse pré-requisito oculto. Faça uma vez, antes do Módulo 09.

Nada aqui exige que você *domine* essas ferramentas — só que tenha elas **instaladas e verificadas**,
e entenda o mínimo conceitual. Cada módulo 09–16 explica a fundo o que usa.

---

## 🗺️ O que muda do Módulo 08 em diante

| Antes (Módulos 01–08) | Agora (Módulos 09–16) |
| ----------------------- | ----------------------- |
| Você roda um script: `python run.py` | Você sobe um **serviço**: `uvicorn ...` que fica escutando |
| O programa termina sozinho | O servidor **não termina** — espera requisições (Ctrl+C para parar) |
| Roda só na sua máquina | Empacotado em **Docker**, roda igual em qualquer máquina |
| Você edita e testa direto | Mudanças passam por **git** + testes + deploy |

> 💡 **Analogia:** até o 08 você escrevia uma calculadora de mão. Do 09 em diante você abre uma
> loja: precisa de endereço (porta), vitrine (endpoint), e um padrão de funcionamento (container)
> para que atenda todo mundo igual, não só você.

---

## Passo 1: Git básico (controle de versão)

Git guarda o histórico do seu código e permite voltar atrás. Você vai usar 5 comandos o curso inteiro:

```bash
git init                 # cria um repositório na pasta atual (uma vez)
git status               # o que mudou desde a última gravação
git add arquivo.py       # marca mudanças para serem gravadas
git commit -m "mensagem" # grava um ponto na história
git log --oneline        # mostra os pontos gravados
```

| Comando | O que faz | Analogia |
| --------- | ----------- | ---------- |
| `git add` | Coloca itens na "caixa" do envio | Separar roupas pra lavar |
| `git commit` | Lacra e registra a caixa com legenda | Etiquetar a caixa com data |
| `git status` | Olha o que ainda está fora da caixa | Conferir se esqueceu algo |

**Verificação:** rode `git --version`. Se mostrar uma versão (ex.: `git version 2.x`), está pronto.

> ⚠️ **Nunca commite sua API key.** O arquivo `.env` deve estar no `.gitignore`. Se vazar uma chave,
> revogue-a imediatamente na plataforma do provedor.

---

## Passo 2: Docker (empacotar sua aplicação)

Docker empacota seu app **junto com tudo que ele precisa** (Python, libs, config) numa **imagem**.
Rodar a imagem cria um **container** — uma cópia isolada e reproduzível. Resolve o clássico
"funciona na minha máquina".

Instale o **Docker Desktop** (Windows/Mac) ou **docker-engine** (Linux): <https://docs.docker.com/get-docker/>

Conceitos mínimos que aparecem nos Módulos 09 e 16:

| Termo | O que é | Analogia |
| ------- | --------- | ---------- |
| **Imagem** | Receita/template empacotada (.exe de app) | A planta de uma casa |
| **Container** | Instância rodando a partir da imagem | A casa construída |
| **Dockerfile** | Texto que diz como montar a imagem | A lista de ingredientes + passos |
| **docker-compose** | Arquivo YAML que sobe vários containers juntos | O capataz que ergue várias casas em ordem |
| **Porta (`-p 8000:8000`)** | Mapeia porta do container ↔ sua máquina | Ramal de telefone: de fora disca X, toca dentro em Y |

**Verificação obrigatória** (roda um container de teste minúsculo):

```bash
docker --version          # deve mostrar a versão
docker run hello-world    # deve imprimir "Hello from Docker!"
```

Se `hello-world` funcionar, você está apto para o Módulo 09.

---

## Passo 3: Servidor local com uvicorn + FastAPI

No Módulo 09 você expõe seu agente como **API REST**. A ferramenta é o **FastAPI** (framework web)
rodado pelo **uvicorn** (servidor). Conceitos:

| Termo | O que é |
| ------- | --------- |
| **Endpoint / rota** | Um endereço (`POST /chat`) que recebe JSON e devolve JSON |
| **HTTP verb** | `GET` (ler), `POST` (enviar/processar) — o "tipo de pedido" |
| **JSON request/response** | O corpo da conversa cliente↔servidor (você já viu JSON no Módulo 01) |
| **`localhost:8000`** | Sua própria máquina escutando na porta 8000 |
| **Swagger `/docs`** | Página automática do FastAPI para testar endpoints no navegador |

Comando típico que você vai ver (note o `--app-dir`, porque o app mora em `modules/09-producao-api/`):

```bash
uvicorn --app-dir modules/09-producao-api app.main:app --reload
```

**Verificação:** após subir o servidor, abra `http://localhost:8000/docs` no navegador. Se aparecer a
documentação interativa do FastAPI, o ambiente de produção está funcionando.

---

## ✅ Checklist de transição (só siga para o Módulo 09 quando marcar tudo)

- [ ] `git --version` responde e eu sei fazer `add` → `commit` → `status`
- [ ] Meu `.env` está no `.gitignore` (chave nunca vai pro git)
- [ ] `docker --version` responde
- [ ] `docker run hello-world` imprimiu "Hello from Docker!"
- [ ] Sei o que é imagem vs. container vs. Dockerfile
- [ ] Entendo que `uvicorn` sobe um servidor que **fica rodando** (parar = Ctrl+C)
- [ ] Sei que um endpoint é um endereço que recebe/devolve JSON

> 💡 Se travou em algum item, **não avance no susto**: refaça o passo correspondente. Produzir é onde
> a maioria dos iniciantes desiste justamente por pular esse onboarding.
