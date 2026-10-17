"""CadQuery backend: local runner in the repository .venv."""

from __future__ import annotations

from opencad.backends.cadquery.lang import CadQueryLanguage
from opencad.backends.local import LocalPythonEngine
from opencad.backends.registry import register


class CadQueryEngine(LocalPythonEngine):
    def __init__(self):
        super().__init__("cadquery", "opencad.backends.cadquery.runner", "__version__")


class CadQueryBackend:
    id = "cadquery"
    language = CadQueryLanguage()
    engine = CadQueryEngine()
    independent_of_evaluator = False


register(CadQueryBackend())
