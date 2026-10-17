"""Backend selection: `--backend`, `OPENCAD_BACKEND`, recorded on every run."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from opencad.paths import DEFAULT_BACKEND

if TYPE_CHECKING:
    from opencad.backends.base import Backend

ENV_VAR = "OPENCAD_BACKEND"

_REGISTRY: dict[str, Backend] = {}
_LOADED: set[str] = set()


def register(backend: Backend) -> Backend:
    _REGISTRY[backend.id] = backend
    return backend


def current_id() -> str:
    return os.environ.get(ENV_VAR) or DEFAULT_BACKEND


def set_backend(backend_id: str) -> str:
    get(backend_id)
    os.environ[ENV_VAR] = backend_id
    return backend_id


def available() -> list[str]:
    _load("zoo")
    for name in ("cadquery", "build123d", "freecad"):
        try:
            _load(name)
        except Exception:
            continue
    return sorted(_REGISTRY)


def get(backend_id: str | None = None) -> Backend:
    bid = backend_id or current_id()
    _load(bid)
    try:
        return _REGISTRY[bid]
    except KeyError as e:
        known = ", ".join(sorted(_REGISTRY)) or "none loaded"
        raise KeyError(f"unknown backend {bid!r} (known: {known})") from e


def _load(backend_id: str) -> None:
    if backend_id in _LOADED:
        return
    _LOADED.add(backend_id)
    if backend_id == "zoo":
        from opencad.backends import zoo as _zoo  # noqa: F401
    elif backend_id == "cadquery":
        from opencad.backends import cadquery as _cq  # noqa: F401
    elif backend_id == "build123d":
        from opencad.backends import build123d as _b3d  # noqa: F401
    elif backend_id == "freecad":
        from opencad.backends import freecad as _fc  # noqa: F401
