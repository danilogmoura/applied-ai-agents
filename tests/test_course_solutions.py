"""Regressão dos gabaritos + verificação opcional dos exercícios do aluno.

Os testes vivem aqui (não no conftest.py) porque o pytest não coleta funções
definidas dentro de um conftest quando ele é alcançado via testpaths=".".

- test_solutions_pass: roda SEMPRE. Garante que a solução oficial de cada
  módulo passa nos próprios testes. Protege contra publicar gabarito quebrado.
- test_student_exercises: só com CHECK_MY_EXERCISES=1. Valida o exercises.py
  que o aluno preencheu (os TODOs). Desligado por padrão porque o esqueleto
  tem placeholders que falhariam de propósito.

Uso:
    pytest                                   # regressão do gabarito
    CHECK_MY_EXERCISES=1 pytest              # + seus exercises.py
    pytest -k "solutions and 04"             # solution do módulo 04
"""

from __future__ import annotations

from pathlib import Path

import pytest

# Helpers definidos no conftest da raiz (loader isolado + plugin executor).
from conftest import ExercisePlugin, _exercise_files, _load_module_from_path


@pytest.mark.parametrize(
    "sol_path",
    _exercise_files("exercises_solution"),
    ids=lambda p: p.parent.name,
)
def test_solutions_pass(sol_path: Path) -> None:
    """A solução oficial do curso deve passar em todos os próprios testes."""
    module = _load_module_from_path(sol_path)
    ExercisePlugin(module).run()


@pytest.mark.parametrize(
    "ex_path",
    _exercise_files("exercises"),
    ids=lambda p: p.parent.name,
)
def test_student_exercises(ex_path: Path, check_my_exercises: bool) -> None:
    """Valida o exercises.py do aluno (TODOs preenchidos). Desligado por padrão."""
    if not check_my_exercises:
        pytest.skip("defina CHECK_MY_EXERCISES=1 para validar seus exercícios")
    module = _load_module_from_path(ex_path)
    ExercisePlugin(module).run()
