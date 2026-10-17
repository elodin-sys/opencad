"""Independent geometry checks: OpenCascade (OCP) on STEP, trimesh on STL. No Zoo calls."""

from __future__ import annotations

import os
from typing import Any


def pool_context() -> Any:
    """Start method for the geometry worker pools (OPENCAD_MESH_START, default forkserver). A worker forked from a parent whose
    OpenCascade thread pool is running (build123d turns parallel booleans on) inherits the pool without its threads and waits
    forever on its first parallel call; the fork server is a fresh interpreter that has run no OpenCascade operation."""
    import multiprocessing

    method = os.environ.get("OPENCAD_MESH_START", "forkserver")
    if method not in multiprocessing.get_all_start_methods():
        return None
    ctx = multiprocessing.get_context(method)
    if method == "forkserver":
        ctx.set_forkserver_preload(["opencad.geomcheck.assembly", "opencad.geomcheck.gears"])  # never __main__: a CLI must not re-run
    return ctx
