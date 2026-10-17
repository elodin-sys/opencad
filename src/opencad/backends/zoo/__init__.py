"""Zoo/KCL backend: hosted CLI engine + KCL language."""

from __future__ import annotations

from opencad.backends.registry import register
from opencad.backends.zoo.engine import ZooEngine
from opencad.backends.zoo.kcl import ZooLanguage


class ZooBackend:
    id = "zoo"
    language = ZooLanguage()
    engine = ZooEngine()
    independent_of_evaluator = True


register(ZooBackend())
