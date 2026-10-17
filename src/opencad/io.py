"""Stage JSON contract, hashing, and provenance stamps."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from opencad import __version__
from opencad.paths import REPO_ROOT


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_tree(root: Path, include: tuple[str, ...] = (), exclude: tuple[str, ...] = ()) -> dict[str, str]:
    """Hash every regular file under root (sorted, relative posix paths); `exclude` names top-level entries to skip."""
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if exclude and p.relative_to(root).parts[0] in exclude:
            continue
        if p.is_file() and (not include or p.suffix in include):
            out[p.relative_to(root).as_posix()] = sha256_file(p)
    return out


def git_state() -> dict[str, Any]:
    def run(*args: str) -> str:
        try:
            return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            return ""

    head = run("rev-parse", "HEAD")
    dirty = bool(run("status", "--porcelain"))
    return {"head": head or None, "dirty": dirty}


def zoo_version() -> str:
    try:
        from opencad.backends.registry import get

        return get("zoo").engine.version()
    except Exception:
        try:
            return subprocess.run(["zoo", "version"], capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
        except Exception:
            return "unknown"


def engine_version(backend_id: str | None = None) -> str:
    try:
        from opencad.backends.registry import get

        return get(backend_id).engine.version()
    except Exception:
        return "unknown"


def provenance(extra: dict[str, Any] | None = None) -> dict[str, Any]:
    from opencad.backends.registry import current_id

    bid = current_id()
    ev = engine_version(bid)
    p = {
        "generated_at": utc_now(),
        "opencad_version": __version__,
        "backend": bid,
        "engine_version": ev,
        "zoo_version": ev if bid == "zoo" else zoo_version(),
        "host": platform.node(),
        "git": git_state(),
    }
    if extra:
        p.update(extra)
    return p


def dump_json(path: Path, data: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, sort_keys=False, default=_default) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def load_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_stage(results_dir: Path, stage: str, data: dict[str, Any], *, contract_path: Path | None = None) -> Path:
    """Write results/<part>/<stage>.json with an `ok` claim and provenance stamp."""
    body = dict(data)
    body.setdefault("stage", stage)
    body.setdefault("ok", False)
    body["provenance"] = provenance({"contract": str(contract_path) if contract_path else None, **body.get("provenance", {})})
    return dump_json(results_dir / f"{stage}.json", body)


def _default(o: Any) -> Any:
    if isinstance(o, Path):
        return str(o)
    if hasattr(o, "tolist"):
        return o.tolist()
    if hasattr(o, "model_dump"):
        return o.model_dump(mode="json")
    if isinstance(o, (set, tuple)):
        return list(o)
    raise TypeError(f"not JSON serialisable: {type(o).__name__}")
