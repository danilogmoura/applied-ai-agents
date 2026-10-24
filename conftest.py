"""Integração pytest <-> exercícios dos módulos.

Este conftest NÃO define fixtures globais (os módulos têm nomes colidentes).
Em vez disso, registra um plugin que transforma cada módulo em testes pytest.

Dois modos:

1. Regressão do gabarito (roda SEMPRE):
   - Coleta ``modules/*/exercises_solution.py`` e valida que a solução oficial
     do curso passa em todos os próprios testes. Isso garante que o material
     nunca é publicado com um gabarito quebrado.

2. Verificação do aluno (roda só com CHECK_MY_EXERCISES=1):
   - Coleta ``modules/*/exercises.py`` para o aluno checar se os TODOs que ele
     implementou passam. Como o esqueleto tem placeholders, isso falha até o
     aluno completar — por isso fica atrás de uma flag explícita.

Uso:
    pytest                                   # só regressão do gabarito + tests/
    CHECK_MY_EXERCISES=1 pytest              # inclui seus exercises.py
    pytest -k "solution and 04"              # solution do módulo 04
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.resolve()
MODULES_DIR = ROOT / "modules"

# Arquivos que NÃO devem ser coletados pelo mecanismo padrão do pytest
# (têm funções test_* mas exigem contexto próprio / chamam API real).
collect_ignore_glob = ["modules/*"]


def _load_module_from_path(path: Path):
    """Importa um .py isoladamente, com nome único p/ evitar colisão."""
    mod_name = f"{path.parent.name}__{path.stem}"
    # Garante que a raiz do projeto está no path (imports 'shared.*').
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(mod_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module
    spec.loader.exec_module(module)
    return module


class ExercisePlugin:
    """Executa as funções test_* de cada arquivo de exercício como subtestes."""

    def __init__(self, module_obj) -> None:
        self._module = module_obj

    def run(self) -> None:
        test_fns = [
            getattr(self._module, name)
            for name in dir(self._module)
            if name.startswith("test_") and callable(getattr(self._module, name))
        ]
        assert test_fns, f"Nenhum teste encontrado em {self._module.__name__}"
        for fn in test_fns:
            # Executa cada teste individualmente; qualquer AssertionError/erro
            # propagado faz o teste pai falhar com o nome da função visível.
            try:
                fn()
            except AssertionError as exc:
                pytest.fail(f"{fn.__name__}: {exc}")
            except Exception as exc:  # noqa: BLE001
                pytest.fail(f"{fn.__name__}: erro inesperado — {exc!r}")


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "exercise: teste vindo de um módulo do curso"
    )


def pytest_collection_modifyitems(session, config, items):
    """Nada a fazer — parametrização acontece via collect_file abaixo."""


@pytest.fixture(scope="session")
def check_my_exercises() -> bool:
    return os.getenv("CHECK_MY_EXERCISES", "").strip().lower() in ("1", "true", "yes")


def _exercise_files(kind: str) -> list[Path]:
    pattern = f"*/{kind}.py"
    return sorted(MODULES_DIR.glob(pattern))
