"""Convenção de pistas didáticas progressivas para os exercícios do curso.

Cada função ``test_*`` em um ``modules/*/exercises.py`` pode declarar uma pista
de direção no docstring, numa linha que comece com ``HINT:``::

    def test_02_cost_comparison():
        \"\"\"TODO: compare custos.

        HINT: custo mensal = custo por ticket x quantidade de tickets.
        \"\"\"

A pista **orienta sem entregar a solução**. Este módulo é a fonte única da
convenção: tanto o harness pytest (``conftest.py``) quanto o ``run_all()``
standalone de cada módulo consomem :func:`extract_hint`, para que o aluno veja
a mesma dica nos dois caminhos.
"""

from __future__ import annotations

_PREFIX = "HINT:"


def extract_hint(fn) -> str | None:
    """Retorna a pista declarada em ``HINT:`` no docstring de ``fn``.

    Aceita a marca no início de qualquer linha do docstring. Retorna ``None``
    quando não há pista — comportamento neutro para módulos ainda não anotados.
    """
    doc = getattr(fn, "__doc__", None) or ""
    for line in doc.splitlines():
        stripped = line.strip()
        if stripped.startswith(_PREFIX):
            return stripped[len(_PREFIX):].strip()
    return None


def format_hint(fn) -> str | None:
    """Monta a linha pronta para exibição: ``💡 Pista: ...`` ou ``None``."""
    hint = extract_hint(fn)
    if not hint:
        return None
    # Colapsa quebras de linha para caber numa única linha legível.
    one_line = " ".join(hint.split())
    return f"💡 Pista ({getattr(fn, '__name__', '?')}): {one_line}"
