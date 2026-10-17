"""Performance scoring of a machine's predictions against sequestered references.

z = |prediction - reference| / sqrt(u_meas^2 + u_numerical^2 + u_input^2), accepted at z <= z_max (thresholds are set from evidence
and logged in truth/calibration-log.yaml before the final run). An exact reference uses an absolute `tolerance` instead. A
reference series is compared point by point on the prediction's series (linear interpolation), reported as RMS and max z.
An unavailable reference, or an extension (evidence X), is reported and never scored; a missing prediction fails. A prediction its
mesh ladder does not resolve (`resolved: false`) is `unresolved`: its z is reported but it neither passes nor fails, so a wide
u_numerical can never buy a pass, and a required one makes the verdict INCOMPLETE."""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Any

import numpy as np


def _series(path: Path, x_col: int, y_col: int, skip: int) -> tuple[np.ndarray, np.ndarray]:
    rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))[skip:]
    pts = [(float(r[x_col]), float(r[y_col])) for r in rows if len(r) > max(x_col, y_col) and r[x_col].strip() and r[y_col].strip()]
    arr = np.asarray(pts, float)
    return arr[:, 0], arr[:, 1]


NUMERICS = ("resolved", "u_iteration", "u_discretisation", "gci", "unresolved_because")


def check(p: Any, pred: dict[str, Any] | None, case_root: Path) -> dict[str, Any]:
    row = _check(p, pred, case_root)
    if row.get("status") == "scored" and (pred or {}).get("resolved") is False:
        return {**row, "status": "unresolved", "ok": None, "note": "not resolved by its mesh ladder: " + "; ".join(pred.get("unresolved_because") or [])}
    return row


def _check(p: Any, pred: dict[str, Any] | None, case_root: Path) -> dict[str, Any]:
    base = {"id": p.id, "kind": "performance", "quantity": p.quantity, "unit": p.unit, "case": p.case, "evidence": p.evidence, "split": p.split,
            "digitized": p.digitized, "required": p.required and p.status == "available" and p.evidence != "X",
            "simulation": (pred or {}).get("simulation"), **{k: (pred or {}).get(k) for k in NUMERICS if (pred or {}).get(k) is not None}}
    if p.status == "unavailable" or p.evidence == "X":
        return {**base, "status": "unavailable" if p.status == "unavailable" else "extension", "ok": None,
                "note": p.note or ("no reference measurement for this observable" if p.status == "unavailable" else "extension: reported, not validated")}
    if not pred or pred.get("status") != "ok" or pred.get("value") is None and not pred.get("series"):
        why = (pred or {}).get("status") or "missing"
        return {**base, "status": "no-prediction", "prediction_status": why, "ok": False, "note": (pred or {}).get("note") or (pred or {}).get("reason") or ""}
    u_num = float(pred.get("u_numerical") or 0.0)
    u_in = max(float(p.u_input or 0.0), float(pred.get("u_input") or 0.0))  # the reference's input uncertainty or the model's own, whichever is larger
    if p.series:
        x, y = _series(case_root / p.series, p.x_column, p.y_column, p.skip)
        ps = pred.get("series") or {}
        if not ps.get("x"):
            return {**base, "status": "no-prediction", "ok": False, "note": "the prediction carries no series for a series reference"}
        yp = np.interp(x, np.asarray(ps["x"], float), np.asarray(ps["y"], float))
        denom = math.sqrt((p.uncertainty or 0) ** 2 + u_num ** 2 + u_in ** 2)
        if denom > 0:
            z = np.abs(yp - y) / denom
            return {**base, "status": "scored", "points": int(len(x)), "z_rms": float(np.sqrt(np.mean(z ** 2))), "z_max_point": float(z.max()),
                    "z_max": p.z_max, "ok": bool(np.sqrt(np.mean(z ** 2)) <= p.z_max), "rms_error": float(np.sqrt(np.mean((yp - y) ** 2)))}
        err = float(np.max(np.abs(yp - y)))
        return {**base, "status": "scored", "points": int(len(x)), "max_error": err, "tolerance": p.tolerance, "ok": err <= (p.tolerance or 0)}
    v = float(pred["value"])
    err = v - float(p.value)
    if p.tolerance is not None and p.uncertainty is None:
        return {**base, "status": "scored", "prediction": v, "reference": p.value, "error": err, "tolerance": p.tolerance, "ok": abs(err) <= p.tolerance}
    denom = math.sqrt((p.uncertainty or 0) ** 2 + u_num ** 2 + u_in ** 2)
    z = abs(err) / denom if denom > 0 else math.inf
    return {**base, "status": "scored", "prediction": v, "reference": p.value, "error": err, "relative_error": err / p.value if p.value else None,
            "u_meas": p.uncertainty, "u_numerical": u_num, "u_input": u_in, "z": z, "z_max": p.z_max, "ok": z <= p.z_max}


def score(performance: list[Any], predictions: dict[str, dict[str, Any]], case_root: Path) -> list[dict[str, Any]]:
    return [check(p, predictions.get(p.id), case_root) for p in performance]


def verdict(geometry: list[dict[str, Any]], perf: list[dict[str, Any]]) -> str:
    """PASS: every required check passes. INCOMPLETE: nothing required failed on its merits, but a required prediction is
    unavailable because its analysis could not run, or is not resolved by its mesh ladder. FAIL otherwise."""
    geo_ok = all(c.get("ok") for c in geometry if c.get("required"))
    req = [c for c in perf if c.get("required")]
    failed = [c for c in req if c.get("ok") is False and c.get("status") != "no-prediction"]
    missing = [c for c in req if c.get("status") == "no-prediction"]
    if not geo_ok or failed or not all(c.get("prediction_status") == "unavailable" for c in missing):
        return "FAIL"
    if missing or any(c.get("status") == "unresolved" for c in req):
        return "INCOMPLETE"
    return "PASS"


def by_split(perf: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    """Required predictions per split: passed, failed, unresolved (reported, never passed) and missing."""
    out = {}
    for split in ("development", "held_out"):
        rows = [c for c in perf if c.get("split") == split and c.get("required")]
        out[split] = {"required": len(rows), "pass": sum(1 for c in rows if c.get("ok") is True),
                      "fail": sum(1 for c in rows if c.get("ok") is False and c.get("status") != "no-prediction"),
                      "unresolved": sum(1 for c in rows if c.get("status") == "unresolved"), "missing": sum(1 for c in rows if c.get("status") == "no-prediction")}
    return out
