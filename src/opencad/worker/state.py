"""Resumable-run state: results/<backend>/<part>/pipeline-state.json for one drive loop, results/<backend>/_campaign/worker-state.json for the campaign."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from opencad.io import dump_json, load_json, utc_now
from opencad.paths import RESULTS

STATE_FILE = "pipeline-state.json"
CAMPAIGN_STATE = RESULTS / "_campaign" / "worker-state.json"


def path(results_dir: Path) -> Path:
    return Path(results_dir) / STATE_FILE


def load(results_dir: Path) -> dict[str, Any] | None:
    p = path(results_dir)
    return load_json(p) if p.exists() else None


def save(results_dir: Path, data: dict[str, Any]) -> Path:
    data = {**data, "updated": utc_now()}
    return dump_json(path(results_dir), data)


def clear(results_dir: Path) -> None:
    path(results_dir).unlink(missing_ok=True)


def campaign_load() -> dict[str, Any]:
    return load_json(CAMPAIGN_STATE) if CAMPAIGN_STATE.exists() else {}


def campaign_save(data: dict[str, Any]) -> None:
    dump_json(CAMPAIGN_STATE, {**data, "updated": utc_now()})


def mark_codex_exhausted(reason: str, *, until_ts: float | None = None) -> None:
    d = campaign_load()
    d["codex_exhausted_until"] = until_ts or (time.time() + 6 * 3600)
    d["codex_exhausted_reason"] = reason[:500]
    d["codex_exhausted_at"] = utc_now()
    campaign_save(d)


def codex_exhausted() -> tuple[bool, dict[str, Any]]:
    d = campaign_load()
    until = d.get("codex_exhausted_until")
    return (bool(until) and time.time() < float(until)), d


def clear_codex_exhausted() -> None:
    d = campaign_load()
    for k in ("codex_exhausted_until", "codex_exhausted_reason", "codex_exhausted_at"):
        d.pop(k, None)
    campaign_save(d)
