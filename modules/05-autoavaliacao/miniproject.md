# 🏗️ Mini-Projeto Integrador — Self-Evaluation

> **Objetivo:** Construir um sistema que gera e auto-avalia respostas iterativamente.

## O que você vai construir

Um gerador `self_eval_generator.py` (classe `SelfEvaluatingAgent`) que:

1. **Gera** resposta inicial para uma pergunta
2. **Avalia** a resposta (clareza, precisão, completude)
3. **Refina** se nota < threshold
4. **Acumula** custo total das iterações

## Requisitos

```python
class SelfEvaluatingAgent:
    def generate_response(self, question: str) -> dict:
        """Gerar resposta inicial."""
        ...
    
    def evaluate(self, response: str, criteria: list = None) -> dict:
        """Avaliar resposta por critérios (claridade, precisão, etc.)."""
        ...
    
    def refine(self, response: str, feedback: dict) -> str:
        """Refinar resposta baseado no feedback."""
        ...
    
    def run_iteration_loop(self, question: str, max_iterations: int = 5, 
                           threshold: float = 0.8) -> dict:
        """Loop: gerar → avaliar → refinar até threshold ou max_iter."""
        ...
```

## 📖 Guia Passo a Passo

### Passo 1 — Crie a classe base com geração simulada

Como ainda não estamos chamando LLMs reais, simule respostas com templates:

```python
import random

class SelfEvaluatingAgent:
    def __init__(self):
        self.iteration_log = []
    
    def generate_response(self, question: str) -> dict:
        """Gera resposta inicial (simulada)."""
        # Templates variados para respostas diferentes
        templates = [
            f"{question}? Isso é uma pergunta interessante. Vou explicar de forma simples.",
            f"Para entender '{question}', precisamos primeiro compreender os conceitos básicos.",
            f"A resposta para '{question}' envolve múltiplos fatores.",
        ]
        
        response = random.choice(templates)
        
        return {
            "response": response,
            "tokens_estimated": len(response.split()),
            "iteration": 0,
        }
```

### Passo 2 — Implemente a avaliação com Pydantic-like schema

Avalie em 3 dimensões com scores 1-10. Em produção real, isso seria feito por um LLM com structured output:

```python
def evaluate(self, response: str, criteria: list = None) -> dict:
    """Avalia resposta por critérios."""
    if criteria is None:
        criteria = ["claridade", "precisao", "completude"]
    
    # Simula scores baseados no tamanho da resposta
    # Respostas maiores tendem a ser mais completas
    word_count = len(response.split())
    
    clarity_score = min(10, max(1, word_count // 5))
    precision_score = min(10, max(1, word_count // 8))
    completeness_score = min(10, max(1, word_count // 4))
    
    issues = []
    if clarity_score < 5:
        issues.append("Resposta muito curta ou confusa")
    if completeness_score < 5:
        issues.append("Faltam detalhes importantes")
    if precision_score < 5:
        issues.append("Pouco específica")
    
    scores = {
        "claridade": clarity_score,
        "precisao": precision_score,
        "completude": completeness_score,
    }
    
    avg_score = sum(scores.values()) / len(scores)
    
    return {
        "scores": scores,
        "average": round(avg_score, 2),
        "issues": issues,
        "needs_improvement": avg_score < 7,
    }
```

### Passo 3 — Implemente o refinamento

Use o feedback para melhorar a resposta:

```python
def refine(self, response: str, feedback: dict) -> str:
    """Refina resposta baseado no feedback."""
    improved = response
    
    issues = feedback.get("issues", [])
    for issue in issues:
        if "curta" in issue:
            improved += " Além disso, este ponto é fundamental porque afeta diretamente o resultado final."
        elif "detalhes" in issue:
            improved += " Para aprofundar: existem pelo menos três aspectos principais que merecem atenção."
        elif "específica" in issue:
            improved += " Um exemplo prático: imagine um cenário onde isso faz diferença imediata."
    
    return improved
```

### Passo 4 — Monte o loop de iteração

O coração do sistema: gera → avalia → refina até atingir threshold:

```python
def run_iteration_loop(self, question: str, max_iterations: int = 5, 
                       threshold: float = 0.8) -> dict:
    """Loop iterativo de geração e autoavaliação."""
    current_response = question
    total_tokens = 0
    history = []
    
    for iteration in range(max_iterations):
        # Gera resposta
        result = self.generate_response(current_response)
        response = result["response"]
        tokens = result["tokens_estimated"]
        total_tokens += tokens
        
        # Avalia
        evaluation = self.evaluate(response)
        
        # Registra histórico
        entry = {
            "iteration": iteration + 1,
            "response": response,
            "evaluation": evaluation,
            "tokens": tokens,
        }
        history.append(entry)
        
        print(f"Iteração {iteration + 1}: score={evaluation['average']:.2f}")
        
        # Se atingiu threshold, para
        if not evaluation["needs_improvement"]:
            print(f"✅ Aprovado na iteração {iteration + 1}!")
            break
        
        # Refina para próxima iteração
        current_response = self.refine(response, evaluation)
    
    return {
        "final_response": history[-1]["response"],
        "total_iterations": len(history),
        "total_tokens": total_tokens,
        "history": history,
        "converged": history[-1]["evaluation"]["average"] >= threshold,
    }
```

### Passo 5 — Adicione CLI

```python
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Gerador com autoavaliação")
    parser.add_argument("--question", default="Explique o que é machine learning")
    parser.add_argument("--max-iters", type=int, default=3)
    parser.add_argument("--threshold", type=float, default=0.7)
    args = parser.parse_args()
    
    generator = SelfEvaluatingAgent()
    result = generator.run_iteration_loop(
        args.question,
        max_iterations=args.max_iters,
        threshold=args.threshold,
    )
    
    print("\n=== Resultado Final ===")
    print(result["final_response"])
    print(f"\nTotal de iterações: {result['total_iterations']}")
    print(f"Tokens gastos: {result['total_tokens']}")
    print(f"Convergiu: {result['converged']}")
```

## ✅ Critérios de Sucesso

Marque cada item **só se conseguir fazer sem olhar o material**:

- [ ] `generate_response()` produz uma resposta inicial para a pergunta
- [ ] `evaluate()` pontua a resposta por critérios (claridade, precisão, completude)
- [ ] `refine()` melhora a resposta usando o feedback da avaliação
- [ ] `run_iteration_loop()` repete gerar→avaliar→refinar até `threshold` ou `max_iterations`
- [ ] O loop reporta nº de iterações, tokens gastos e se convergiu
- [ ] CLI aceita `--question`, `--max-iters` e `--threshold`

> ⚠️ Se marcou menos de 3 itens, releia as seções correspondentes antes de prosseguir.

## Teste seu código

```bash
python self_eval_generator.py --question "Explique transformers" --max-iters 3
python self_eval_generator.py --batch questions.json --output results.json
```

## 🪨 Travei? Pistas em camadas

Funciona igualzinho às pistas dos exercícios: quando um requisito travar, abra **só o próximo nível** que você precisar — nunca todos de uma vez. O objetivo é destravar o raciocínio, não entregar a resposta mastigada.

> **Nível 1 — Direção.** Cada requisito mapeia para um `Passo` do guia acima. Antes de descer de nível, releia o Passo correspondente; na maioria das vezes ele já tem o esqueleto da função.

<details>
<summary><b>Nível 2 — A ideia por requisito</b> (clique para abrir)</summary>

- **`generate_response()`:** produza uma resposta inicial (real via LLM ou simulada) e retorne um dict com o texto. É o ponto de partida do loop, não precisa ser boa — só precisa existir para ser avaliada.
- **`evaluate()`:** pontue a resposta por critérios (claridade, precisão...). Se usar LLM, peça JSON com nota por critério e um score agregado; senão, heurísticas (comprimento, presença de palavras-chave).
- **`refine()`:** receba o `feedback` e reescreva mirando os pontos fracos apontados — tipicamente chamando o LLM com a resposta anterior + críticas no prompt.
- **`run_iteration_loop()`:** é o coração: `for i in range(max_iterations)` → generate/evaluate → se score >= threshold pare, senão refine e repita. Guarde o histórico de scores.
- **threshold & parada:** a condição de saída é dupla — atingiu `threshold` (sucesso) OU esgotou `max_iterations` (melhor esforço). Sempre retorne a melhor resposta vista, não só a última.

</details>

<details>
<summary><b>Nível 3 — Quase solução</b> (abra só se o nível 2 não bastou)</summary>

```python
def run_iteration_loop(self, question, max_iterations=5, threshold=0.8):
    resp = self.generate_response(question)["text"]
    best = resp
    for _ in range(max_iterations):
        ev = self.evaluate(resp)
        if ev["score"] >= threshold:
            return {"answer": resp, "score": ev["score"]}
        resp = self.refine(resp, ev)
    return {"answer": resp, "score": self.evaluate(resp)["score"], "stopped": "max_iter"}
```

`generate` → `evaluate` → `refine` são três engrenagens que o loop apenas gira: cada iteração realimenta a saída de uma na entrada da outra até o threshold.

</details>

## Desafios extras

- [ ] Critérios configuráveis por domínio
- [ ] Comparar qualidade vs custo (tokens gastos)
- [ ] Exportar histórico de iterações
- [ ] Modo "teacher" com rubric predefined
