"""Remove a nota '> 📌 **Nota:** Este material foi revisado...' do topo dos 8 materiais L1-L3.

Padrao identico: blockquote na linha 3 (03-viabilidade na linha 5, apos outro aviso), entre o
titulo '# ...' e o conteudo seguinte. Formato:

    > 📌 **Nota:** ...\n\n

Removemos a blockquote inteira + a linha em branco seguinte, preservando a separacao \n\n entre
o que vem antes e depois. Nao tocamos em nenhuma ancora 📖 Fonte. Edicao via Python UTF-8 por
causa do mount /mnt/z (edit tools corrompem emoji -> U+FFFD).
"""
from pathlib import Path

FILES = [
    "modules/02-primeiro-llm/MATERIAL.md",
    "modules/01-fundamentos/MATERIAL.md",
    "modules/03-viabilidade/MATERIAL.md",
    "modules/04-rag/MATERIAL.md",
    "modules/05-autoavaliacao/MATERIAL.md",
    "modules/06-tool-calling/MATERIAL.md",
    "modules/07-planejamento/MATERIAL.md",
    "modules/08-multiagente/MATERIAL.md",
]

NOTE = "> 📌 **Nota:** Este material foi revisado para focar nos conceitos essenciais. Seções marcadas como **🔬 Avançado — OPCIONAL** podem ser puladas na primeira leitura.\n\n"

for rel in FILES:
    p = Path(rel)
    text = p.read_text(encoding="utf-8")
    if text.count(NOTE) != 1:
        raise SystemExit(f"[ERRO] {rel}: nota match {text.count(NOTE)}x (esperado 1). Abortando.")
    text = text.replace(NOTE, "", 1)
    assert "\ufffd" not in text, f"[ERRO] {rel}: U+FFFD!"
    assert "Este material foi revisado para focar" not in text, f"[ERRO] {rel}: resíduo!"
    p.write_text(text, encoding="utf-8")
    print(f"[OK] {rel}")
