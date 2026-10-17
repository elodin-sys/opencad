"""Per-cell engine cost: local kernels are free; Zoo is the credit-balance delta."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from opencad.io import utc_now

_STAGE_FILES = ("blockout.json", "verify.json", "export.json", "inspect.json", "edit.json")


def _pick(billing: dict[str, Any]) -> dict[str, Any]:
    return {
        "known": True,
        "remaining_total": billing.get("remaining_total"),
        "monetary_value": billing.get("monetary_value"),
        "plan": billing.get("plan"),
        "pay_as_you_go_price": billing.get("pay_as_you_go_price"),
    }


def mark_cell_start(results_dir: Path, *, reset: bool) -> None:
    """Remember when this cell started so later cost totals skip ledgers from older runs."""
    path = Path(results_dir) / "cell-start.json"
    tag = os.environ.get("OPENCAD_TAG") or ""
    if not reset and path.exists():
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old = {}
        if old.get("tag") == tag:
            return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"tag": tag, "ts": time.time(), "utc": utc_now()}) + "\n", encoding="utf-8")


def begin_credits(results_dir: Path, billing: dict[str, Any] | None, *, reset: bool) -> None:
    """Write credits-before.json. reset replaces it (a blockout starts the cell); otherwise keep this tag's snapshot."""
    if not billing or not billing.get("known"):
        return
    path = results_dir / "credits-before.json"
    tag = os.environ.get("OPENCAD_TAG") or ""
    if not reset and path.exists():
        try:
            old = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            old = {}
        if old.get("tag") == tag:
            return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({**_pick(billing), "tag": tag, "ts": utc_now()}, indent=2) + "\n", encoding="utf-8")


def credit_delta(before: dict[str, Any] | None, after: dict[str, Any] | None) -> dict[str, Any]:
    if not before or not after or before.get("remaining_total") is None or after.get("remaining_total") is None:
        return {"zoo_credits_delta": None, "zoo_monetary_delta": None}
    return {
        "zoo_credits_delta": before["remaining_total"] - after["remaining_total"],
        "zoo_monetary_delta": round((before.get("monetary_value") or 0) - (after.get("monetary_value") or 0), 6),
    }


def ledger_totals(results_dir: Path) -> tuple[int, float]:
    """Worker engine-ledger.jsonl rows plus the stage JSONs' engine_calls."""
    calls = 0
    seconds = 0.0
    if not results_dir.exists():
        return 0, 0.0
    since = _cell_started(results_dir)
    for path in results_dir.rglob("engine-ledger.jsonl"):
        if _current(path, since):
            calls, seconds = _add_rows(calls, seconds, _jsonl(path))
    for name in _STAGE_FILES:
        for path in results_dir.rglob(name):
            if not _current(path, since):
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            rows = data.get("engine_calls") if isinstance(data, dict) else None
            if isinstance(rows, list):
                calls, seconds = _add_rows(calls, seconds, rows)
    return calls, round(seconds, 2)


def _cell_started(results_dir: Path) -> float | None:
    path = results_dir / "cell-start.json"
    if not path.exists():
        return None
    try:
        return float(json.loads(path.read_text(encoding="utf-8")).get("ts") or 0) or None
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return None


def _current(path: Path, since: float | None) -> bool:
    if since is None:
        return True
    try:
        return path.stat().st_mtime + 1 >= since
    except OSError:
        return False


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return rows
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _add_rows(calls: int, seconds: float, rows: list[dict[str, Any]]) -> tuple[int, float]:
    for row in rows:
        calls += 1
        seconds += float(row.get("seconds") or 0)
    return calls, seconds


def write_cell_cost(results_dir: Path, *, backend_id: str, billing_after: dict[str, Any] | None = None, fetch: bool = True) -> dict[str, Any]:
    """Refresh credits-after.json and cost.json from the before-snapshot and the ledgers."""
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    tag = os.environ.get("OPENCAD_TAG") or ""
    if billing_after is None and fetch and backend_id == "zoo":
        from opencad.backends.zoo.engine import credits

        billing_after = credits()
    after = None
    if billing_after and billing_after.get("known"):
        after = {**_pick(billing_after), "tag": tag, "ts": utc_now()}
        (results_dir / "credits-after.json").write_text(json.dumps(after, indent=2) + "\n", encoding="utf-8")
    before = None
    before_path = results_dir / "credits-before.json"
    if before_path.exists():
        try:
            before = json.loads(before_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            before = None
        if before and tag and before.get("tag") not in (tag, "", None):
            before = None
    calls, seconds = ledger_totals(results_dir)
    delta = credit_delta(before, after)
    cost = {
        "backend": backend_id,
        "tag": tag or None,
        "calls": calls,
        "seconds": seconds,
        "engine_usd": None if backend_id == "zoo" else 0,
        **delta,
    }
    (results_dir / "cost.json").write_text(json.dumps(cost, indent=2) + "\n", encoding="utf-8")
    return cost
