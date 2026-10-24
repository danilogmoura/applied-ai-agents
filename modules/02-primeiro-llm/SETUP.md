# ⚙️ Setup Obrigatório — Antes de Começar

Antes de executar qualquer código deste módulo, siga estes passos.

---

## Passo 1: Instalar dependências

```bash
pip install openai rich python-dotenv tiktoken
```

| Pacote | Para que serve |
| -------- | --------------- |
| `openai` | SDK para chamar LLMs (GPT, etc.) |
| `rich` | Saída colorida e bonita no terminal |
| `python-dotenv` | Carrega variáveis de ambiente do arquivo `.env` |
| `tiktoken` | Conta tokens (usado pelo módulo `shared/cost.py`) |

---

## Passo 2: Obter API Key da OpenAI

1. Acesse [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Clique em **"Create new secret key"**
3. Copie a chave (começa com `sk-...`)

> ⚠️ **NUNCA compartilhe sua API key publicamente.**  
> Se uma chave vazar, exclua-a imediatamente na página da OpenAI.

---

## Passo 3: Configurar variável de ambiente

### Opção A — Arquivo `.env` (recomendado)

Crie um arquivo `.env` na **raiz do projeto** (`/mnt/z/github/applied-ai-agents/.env`) com:

```
OPENAI_API_KEY=sua_chave_aqui
```

Exemplo real (substitua pela sua chave):

```
OPENAI_API_KEY=sk-proj-abc123def456ghi789
```

### Opção B — Variável de ambiente no terminal

```bash
# Linux/macOS
export OPENAI_API_KEY="sua_chave_aqui"

# Windows (CMD)
set OPENAI_API_KEY=sua_chave_aqui

# Windows (PowerShell)
$env:OPENAI_API_KEY="sua_chave_aqui"
```

### O que é `.env`?

`.env` é um arquivo que armazena senhas e chaves sem colocá-las no código.  
É como um cofre: o código lê as chaves de lá, mas nunca as escreve hardcoded.

O arquivo `.env` **não deve ser comitado** no Git — ele já está no `.gitignore`.

---

## Passo 4: Validar instalação

Execute estes comandos para verificar se tudo está funcionando:

```bash
# Testa se o SDK OpenAI está instalado
python -c "from openai import OpenAI; print('✅ OpenAI SDK OK')"

# Testa se python-dotenv está instalado
python -c "from dotenv import load_dotenv; print('✅ python-dotenv OK')"

# Testa se shared/security funciona
python -c "from shared.security import get_required_secret; print('✅ shared/security OK')"
```

Se algum comando retornar erro, verifique se instalou tudo corretamente com `pip install`.

---

## 💰 Aviso de custo

Sua primeira chamada pode custar ~$0.001 (um décimo de centavo).  
Com 100 tickets: ~$0.10 (dez centavos).

Monitore seus gastos em [platform.openai.com/usage](https://platform.openai.com/usage).

Para este exercício, você gastará menos de $1.00 no total.

---

## ❓ Troubleshooting rápido

| Erro | Causa provável | Solução |
| ------ | --------------- | --------- |
| `ModuleNotFoundError: No module named 'openai'` | SDK não instalado | Execute `pip install openai` |
| `ValueError: OPENAI_API_KEY não definida` | `.env` ausente ou mal configurado | Verifique se `.env` está na raiz do projeto |
| `AuthenticationError: Incorrect API key` | Chave inválida ou expirada | Regenerue a chave em platform.openai.com/api-keys |
| `RateLimitError` | Muitas requisições muito rápido | Espere 5 segundos e tente novamente |
| `ModuleNotFoundError: No module named 'shared'` | Path incorreto | Execute o script a partir da raiz do projeto |
