"""Measurement helpers shared by blockout, verify, gates."""

from __future__ import annotations

from typing import Any

from opencad.schemas import PartContract


def bbox_check(contract: PartContract, bbox_min: list[float], bbox_max: list[float]) -> dict[str, Any]:
    tol = contract.bbox_tolerance
    err_min = [abs(a - e) for a, e in zip(bbox_min, contract.envelope.min)]
    err_max = [abs(a - e) for a, e in zip(bbox_max, contract.envelope.max)]
    return {
        "expected_min": list(contract.envelope.min), "expected_max": list(contract.envelope.max),
        "measured_min": [round(v, 4) for v in bbox_min], "measured_max": [round(v, 4) for v in bbox_max],
        "max_error": round(max(err_min + err_max), 4), "tolerance": tol,
        "ok": max(err_min + err_max) <= tol,
    }


def volume_band_check(volume: float, lo: float, hi: float) -> dict[str, Any]:
    return {"measured": round(volume, 3), "band": [round(lo, 3), round(hi, 3)], "ok": lo <= volume <= hi}


def quantity_check(q, actual: float | None) -> dict[str, Any]:
    if q is None:
        return {"declared": False, "ok": True}
    if actual is None:
        return {"declared": True, "expected": q.expected, "measured": None, "ok": False, "error": "no measurement"}
    ok, band = q.within(actual)
    return {"declared": True, "expected": q.expected, "measured": round(actual, 4), "error": round(abs(actual - q.expected), 4), "band": round(band, 4), "ok": ok}


def point_check(pq, actual: list[float] | None) -> dict[str, Any]:
    if pq is None:
        return {"declared": False, "ok": True}
    if not actual or any(v is None for v in actual):
        return {"declared": True, "expected": list(pq.expected), "measured": None, "ok": False, "error": "no measurement"}
    ok, errs = pq.within(tuple(actual))
    return {"declared": True, "expected": list(pq.expected), "measured": [round(v, 4) for v in actual], "errors": [round(e, 4) for e in errs], "tolerance": pq.tolerance, "ok": ok}
