"""Reduced-order models: closed-form or small numerical models with explicit assumption lists.

Each module exposes `ASSUMPTIONS` (list of strings) and `run(inputs, case, geometry, settings) -> dict` returning
`{"observables": {quantity: value}, "conservation": {...}, "series": {...}}`; the simulate stage maps quantities to the
contract's observables.
"""

from __future__ import annotations

import importlib
from typing import Any

MODELS = ("brake_energy", "peristaltic", "pump_euler", "reynolds_film", "fan_euler", "stirling_schmidt")


def module(name: str) -> Any:
    if name not in MODELS:
        raise KeyError(f"unknown reduced model {name!r} (known: {', '.join(MODELS)})")
    return importlib.import_module(f"opencad.sim.reduced.{name}")


def docs() -> str:
    """Input and quantity conventions of every adapter, for the drafter (models not implemented yet are omitted)."""
    from opencad.sim import calculix, openfoam

    out = [calculix.DOC, openfoam.DOC]
    for name in MODELS:
        try:
            out.append(module(name).DOC)
        except (ImportError, AttributeError):
            continue
    return "\n".join(out)
