# 🐍 Ponte Python — do imperativo ao idiomático

> **Para quem é:** você sabe escrever `for`, `if` e funções em Python, mas trava ao ler o
> código dos módulos (`@dataclass`, `Optional[...]`, `[x for x in ...]`, `.get(k, default)`).
> Este apêndice **não ensina Python do zero** — ele faz a *tradução*: pega o código que você
> já escreveria "à moda antiga" e mostra o equivalente idiomático usado no curso, lado a lado.

Como usar: dê Ctrl+F pelo padrão que apareceu no módulo atual. Cada seção tem
**❌ como você escreveria → ✅ como o curso escreve → 🔎 onde aparece**.

---

## 🗺️ Quando consultar (mapa por módulo)

| Padrão | Seção | Módulos onde aparece com força |
|--------|-------|-------------------------------|
| `.get(chave, default)` e dicts aninhados | §1–2 | todos (respostas de LLM/config) |
| Compreensões (`[x for ...]`, `{k: v ...}`) | §3 | 04-rag, 10-avaliacao, 12-memoria, 14-cache |
| `@dataclass` + `field(default_factory=...)` | §4 | 03, 07, 10, 11, 12, 14, 15, 16 |
| Type hints (`Optional`, `List`, `Dict`) | §5 | 12, 13, 15, 16 |
| `Callable[[...], ...]` | §5 | 06-tool-calling, 15-skills, 16-operacoes |
| `Enum` | §6 | 07-planejamento, 11-seguranca, 15-skills, 16-operacoes |
| `assert` / `raise` / `try-except` | §7 | todos os `exercises.py` (testes) |
| Ternário + desempacotamento (`for a, b in`) | §8 | 12-memoria, 14-cache |
| `pathlib.Path` ler/salvar arquivo | §9 | 04-rag, 10-avaliacao, 15-skills |
| `async def` / `await` / `yield` / `async for` | §10 | 09-producao-api, 13-streaming |

---

## 1. Dicionários: acessar sem quebrar (`.get`)

Um dicionário (`dict`) é uma coleção chave→valor, como uma ficha com campos nomeados.
A forma ingênua de ler um campo **explode** se a chave não existir.

```python
# ❌ Frágil: KeyError se "severity" não estiver no dict
item = {"type": "pii", "value": "email"}
nivel = item["severity"]            # 💥 KeyError: 'severity'

# ✅ Idiomático: .get(chave, valor_padrao) nunca explode
nivel = item.get("severity", "LOW") # -> "LOW" (usou o default)
```

Regra de bolso: use `d[k]` quando a chave **deve** existir; use `d.get(k, default)`
quando pode faltar. No curso, respostas de LLM e configs vêm cheias de campos opcionais,
por isso `.get(...)` aparece em todo lugar (ex.: `msg.get("role")`, `result.get("id")`).

**Destruturando** vários campos de uma vez:

```python
# ✅ unpacking: lê várias chaves numa linha
name, score = data["name"], data["score"]
# vira, quando as chaves podem faltar:
name = data.get("name", "?")
score = data.get("score", 0.0)
```

---

## 2. Listas & dicionários aninhados (a resposta de um LLM)

Chamadas de API retornam listas de dicionários. O medo some quando você entende que é só
**caixinha dentro de caixinha**: indexe a lista por posição `[0]`, o dict por chave `["..."]`.

```python
resposta = {
    "choices": [
        {"message": {"role": "assistant", "content": "Olá!"}}
    ]
}

# ❌ copiar o caminho inteiro toda vez
texto = resposta["choices"][0]["message"]["content"]

# ✅ leia com segurança em cadeia
primeiro = resposta.get("choices", [{}])[0]      # [{}] evita IndexError se vazio
conteudo = primeiro.get("message", {}).get("content", "")
```

---

## 3. Compreensões: substituir o `for` que só acumula

Este é o salto nº 1 para iniciantes. Uma **list comprehension** é um `for` compacto que
constrói uma lista. Se o seu laço só faz `append`, ele quase sempre cabe numa linha.

```python
# ❌ estilo imperativo (funciona, mas é verboso)
nomes = []
for entry in scored:
    nomes.append(entry["name"])

# ✅ comprehension: mesma coisa, uma linha
nomes = [entry["name"] for entry in scored]

# ✅ + filtro: só quem passou
aprovados = [r for r in resultados if r["ok"]]

# ✅ dict comprehension: constrói um dict, não uma lista
custos = {m.name: m.price for m in models}       # -> {"gpt-4o": ..., "flash": ...}
```

Exemplo real do Módulo 12 (memória), normalizando um vetor:

```python
vec = [v / norm for v in vec]     # divide cada elemento pela norma
```

E filtrando top-k já ordenado:

```python
return [entry for _, entry in scored[:top_k]]   # descarta o score, fica só o entry
```

> 🧠 Como ler da direita para a esquerda: "`para cada entry em scored`, pega `entry['name']`".

---

## 4. `@dataclass`: classes que são só "fichas de dados"

Muitos objetos no curso servem apenas para agrupar campos (como um `dict`, mas com tipo e
autocomplete). Em vez de escrever `__init__` à mão, usa-se `@dataclass`.

```python
# ❌ boilerplate manual
class ActionRequest:
    def __init__(self, operation, target, reason, risk_level):
        self.operation = operation
        self.target = target
        self.reason = reason
        self.risk_level = risk_level

# ✅ mesmo resultado, o decorador gera o __init__ por você
from dataclasses import dataclass

@dataclass
class ActionRequest:
    """Solicitação de ação para aprovação humana."""
    operation: str          # O que o agente quer fazer
    target: str             # Alvo da operação
    reason: str             # Justificativa
    risk_level: RiskLevel   # Nível de risco
```

Depois você cria e acessa igualzinho:

```python
req = ActionRequest("deploy", "prod", "hotfix crítico", RiskLevel.HIGH)
print(req.target)          # "prod"
```

**Campos mutáveis precisam de `field(default_factory=...)`** — senão todas as instâncias
compartilham a mesma lista (bug clássico!):

```python
from dataclasses import dataclass, field

@dataclass
class Planner:
    steps: list = field(default_factory=list)   # ✅ lista nova por instância
    results: dict = field(default_factory=dict)
```

Convertendo entre dataclass e dict (útil para salvar JSON):

```python
from dataclasses import asdict
registro = asdict(req)      # ActionRequest -> {"operation": ..., "target": ...}
```

---

## 5. Type hints: ler sem ter medo

As anotações (`-> str`, `Optional[int]`) **não mudam a execução** — são documentação para o
editor e para você. Não travam seu código.

```python
def run(query: str, top_k: int = 3) -> list[dict]:
    ...
```

| Escrita no curso | Significa |
| ------------------ | ----------- |
| `x: str` | `x` é texto |
| `def f() -> None` | não retorna nada útil |
| `List[str]` / `list[str]` | lista de textos |
| `Dict[str, int]` / `dict[str, int]` | dict com chaves texto, valores int |
| `Optional[str]` | é um texto **ou** `None` |
| `Callable[[int], str]` | espera uma função `(int) -> str` |
| `Literal["low","high"]` | só aceita exatamente esses valores (string fixa) |

> Os dois primeiros (`typing.List`, `typing.Dict`) são a forma antiga; `list`/`dict` minúsculos
> são a moderna (Python 3.9+). O curso usa ambos — são equivalentes.

---

## 6. Enums: constantes nomeadas em vez de strings soltas

Em vez de comparar strings ("arriscado", erros de digitação), define-se um conjunto fechado.

```python
# ❌ string mágica espalhada
if nivel == "high": ...     # e alguém escreve "High" e quebra

# ✅ Enum: valores nomeados, conferidos pelo editor
from enum import Enum

class RiskLevel(Enum):
    LOW = "low"
    HIGH = "high"

if nivel == RiskLevel.HIGH: ...
```

---

## 7. Exceções: falhar cedo e claro

O curso valida pré-condições com `assert` e sobe erros específicos. Entenda os três papéis:

```python
# assert: "isso DEVE ser verdade, senão pare agora" (usado nos testes do curso)
assert len(respostas) == 3, f"esperava 3, veio {len(respostas)}"

# raise: sinaliza um erro de uso/configuração
if not api_key:
    raise ValueError("Defina OPENAI_API_KEY no .env")

# try/except: reage a um erro esperado, sem derrubar tudo
try:
    value = int(user_input)
except ValueError:
    value = 0     # plano B
```

> Nos exercícios, cada teste é um bloco `assert`. Quando falha, a mensagem depois da vírgula
> é o que você lê no terminal — por isso escreva mensagens úteis.

---

## 8. Expressões condicionais e desempacotamento rápidos

```python
# ternário: if/else numa linha
status = "ok" if resp.ok else "erro"

# desempacotar tupla num laço (muito comum com enumerate/dict)
for i, nome in enumerate(modelos):        # índice + valor
    print(i, nome)
for score, entry in scored:               # duas variáveis por item
    ...

# underscore descarta o que não interessa
_, ultimo = sorted_itens[0], sorted_itens[-1]
```

---

## 9. `pathlib.Path`: arquivos sem dor de cabeça

O curso lê/salva arquivos com `Path` (moderno) em vez de `open(os.path.join(...))` (antigo).

```python
from pathlib import Path

p = Path("data") / "amostras.json"     # junta caminhos com /
texto = p.read_text(encoding="utf-8")  # lê o arquivo inteiro
p.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")

if not p.exists():                     # checar antes
    p.parent.mkdir(parents=True, exist_ok=True)
```

---

## 10. Async: `async def` / `await` (Streaming e API)

Aparece nos Módulos 09 e 13. A ideia: uma função `async` pode **pausar** esperando rede sem
travar o resto do programa; `await` é essa pausa.

```python
# ❌ síncrono: bloqueia enquanto a API responde
resposta = client.chat.completions.create(...)

# ✅ assíncrono: libera a thread enquanto espera
async def stream():
    async for chunk in await client.chat.completions.create(stream=True):
        yield chunk.delta.content        # produz aos poucos

import asyncio
asyncio.run(stream())                    # ponto de entrada executa o laço async
```

> Você raramente precisa entender o motor por dentro — só reconhecer que `async for` consome
> um gerador assíncrono, e que `yield` transforma a função em um fluxo de pedaços.

---

## Como praticar

Pegue qualquer `run.py` de um módulo que você já rodou e reescreva **uma** função pequena
usando estes padrões (comprehension no lugar de `for`+append, `.get` no lugar de `[]`,
um `@dataclass` no lugar de dict solto). Depois rode `pytest -k <modulo>` para confirmar
que nada quebrou. É assim que tradução vira fluência.

📚 Voltar ao índice: [`README.md`](README.md) · Verificar exercícios: seção
*"✅ Como verificar seus exercícios"* em cada `MATERIAL.md`.
