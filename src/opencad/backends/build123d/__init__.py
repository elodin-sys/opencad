"""build123d backend: local runner in the repository .venv."""

from __future__ import annotations

from opencad.backends.build123d.lang import Build123dLanguage
from opencad.backends.local import LocalPythonEngine
from opencad.backends.registry import register


class Build123dEngine(LocalPythonEngine):
    def __init__(self):
        super().__init__("build123d", "opencad.backends.build123d.runner", "__version__")


class Build123dBackend:
    id = "build123d"
    language = Build123dLanguage()
    engine = Build123dEngine()
    independent_of_evaluator = False


register(Build123dBackend())
