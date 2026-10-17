"""Content-addressed cache for evaluator results (inspect, edit) keyed by the hashes of what they measure.

A retry or an ECR re-measures only what changed; `--from-stage verify` on an unchanged part costs no hosted
calls. `OPENCAD_NO_CACHE=1` disables it; `OPENCAD_CACHE_DIR` relocates it.
"""

from __future__ import annotations

import functools
import hashlib
import json
import os
from pathlib import Path
from typing import Any

from opencad.io import load_json, sha256_file

VERSION = "3"  # bump when a stage's output shape or verdict logic changes (3: edit-mode interface preservation rules)
_PACKAGE = Path(__file__).resolve().parent
MEASURING_CODE = ("geomcheck/*.py", "stages/inspect_stage.py", "stages/edit.py", "stages/common.py", "gates.py")


@functools.lru_cache(maxsize=1)
def code_digest() -> str:
    """Digest of the evaluator code the cached results depend on, so a fix to a check re-measures unchanged parts."""
    h = hashlib.sha256()
    for f in sorted(p for pattern in MEASURING_CODE for p in _PACKAGE.glob(pattern)):
        h.update(f.name.encode() + b":" + f.read_bytes())
    return h.hexdigest()[:16]


def root() -> Path:
    return Path(os.environ.get("OPENCAD_CACHE_DIR") or (Path.home() / ".cache" / "opencad" / "evaluator"))


def enabled() -> bool:
    return os.environ.get("OPENCAD_NO_CACHE", "") not in ("1", "true", "yes")


def key(kind: str, *files: Path, extra: str = "") -> str:
    h = hashlib.sha256()
    h.update(f"{kind}:{VERSION}:{code_digest()}:{extra}".encode())
    for f in files:
        f = Path(f)
        h.update(b"|" + f.name.encode() + b":" + (sha256_file(f).encode() if f.exists() else b"missing"))
    return h.hexdigest()


def get(kind: str, k: str) -> dict[str, Any] | None:
    if not enabled():
        return None
    p = root() / kind / f"{k}.json"
    if not p.exists():
        return None
    try:
        return load_json(p)
    except json.JSONDecodeError:
        return None


def put(kind: str, k: str, data: dict[str, Any]) -> None:
    if not enabled():
        return
    p = root() / kind / f"{k}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    body = {kk: v for kk, v in data.items() if kk not in ("provenance", "engine_calls", "stage", "cached")}
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(body, default=str), encoding="utf-8")
    tmp.replace(p)
