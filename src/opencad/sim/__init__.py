"""Backend-neutral simulation layer: reduced-order models, CalculiX/gmsh FEA and containerised OpenFOAM over exported assemblies.

Every adapter returns the same result shape (see opencad.assembly.simulate); these helpers build it. A missing solver or input
is `unavailable` with a reason, never a zero; a crash is `failed` with the error.

Numerical uncertainty of a prediction: `u_iteration` is the spread of a steady solution over the last TAIL of its iterations (its
value is that window's mean), `u_discretisation` the grid-convergence index of its mesh ladder, `u_numerical` their quadrature sum.
`resolved` says whether the ladder supports the value at all: a large u_numerical never makes a prediction acceptable."""

from __future__ import annotations

import math
from itertools import pairwise
from typing import Any

import numpy as np

TAIL = 0.2  # fraction of a steady run's iterations averaged into its value
DRIFT_MAX = 0.01  # the tail mean against the window before it
FORMAL_ORDER = 2.0
STUDY_KEYS = ("u_discretisation", "u_iteration", "resolved", "unresolved_because", "gci", "order", "fs", "extrapolated", "convergence", "mesh_levels",
              "cells", "u_iterations", "drift", "last")


def unavailable(reason: str, **extra: Any) -> dict[str, Any]:
    return {"status": "unavailable", "reason": reason, "observables": {}, **extra}


def failed(error: str, **extra: Any) -> dict[str, Any]:
    return {"status": "failed", "error": error[:3000], "observables": {}, **extra}


def observable(value: float | None, unit: str, *, case: str | None = None, u_numerical: float | None = None, levels: list[float] | None = None,
               **extra: Any) -> dict[str, Any]:
    if value is None:
        return {"status": "unavailable", "unit": unit, "case": case, **extra}
    return {"status": "ok", "value": float(value), "unit": unit, "case": case, "u_numerical": u_numerical, "levels": levels, **extra}


def tail(y: Any, frac: float = TAIL) -> dict[str, Any]:
    """Mean and standard deviation of the last `frac` of an iteration history, and how far that mean moved from the window before it."""
    y = np.asarray(y, float)
    n = max(1, round(len(y) * frac))
    last, prev = y[-n:], y[-2 * n:-n]
    mean = float(last.mean())
    drift = abs(mean - float(prev.mean())) / (abs(mean) or 1.0) if len(prev) == n else None
    return {"mean": mean, "std": float(last.std()), "drift": drift, "samples": n, "last": float(y[-1])}


def gci(values: list[float], ratios: list[float], formal_order: float = FORMAL_ORDER) -> dict[str, Any]:
    """Grid-convergence index of the finest of two or three solutions ordered coarse to fine (Celik et al. 2008, J. Fluids Eng. 130,
    078001), relative to it; ratios[i] = h_i / h_(i+1). Three monotone solutions give the observed order (used up to the formal
    order), the Richardson value and Fs 1.25; a pair, or three that oscillate or diverge, give Fs 3 at the formal order on the larger
    change."""
    f1, f2 = values[-1], values[-2]
    ref, e21, r21 = abs(f1) or 1.0, f2 - f1, ratios[-1]
    if min(ratios[-2:]) <= 1.0 + 1e-9:
        return {"convergence": "degenerate", "order": None, "fs": None, "gci": None, "extrapolated": None}
    if abs(e21) <= 1e-12 * ref:
        return {"convergence": "converged", "order": None, "fs": 1.25, "gci": 0.0, "extrapolated": f1}
    if len(values) < 3:
        rp = r21 ** formal_order
        return {"convergence": "pair", "order": None, "fs": 3.0, "gci": 3.0 * abs(e21) / ref / (rp - 1), "extrapolated": (rp * f1 - f2) / (rp - 1)}
    e32, r32 = values[-3] - f2, ratios[-2]
    ratio = e21 / e32 if e32 else math.inf
    if not 0 < ratio < 1:
        return {"convergence": "oscillatory" if ratio < 0 else "divergent", "order": None, "fs": 3.0,
                "gci": 3.0 * max(abs(e21), abs(e32)) / ref / (r21 ** formal_order - 1), "extrapolated": None}
    p = math.log(abs(e32 / e21)) / math.log(r21)
    for _ in range(100):
        q = math.log((r21 ** p - 1) / (r32 ** p - 1))
        p, prev = abs(math.log(abs(e32 / e21)) + q) / math.log(r21), p
        if abs(p - prev) < 1e-10 or p < 1e-6:
            break
    rp = r21 ** max(min(p, formal_order), 1e-6)
    return {"convergence": "monotone", "order": p, "fs": 1.25, "gci": 1.25 * abs(e21) / ref / (rp - 1), "extrapolated": (rp * f1 - f2) / (rp - 1)}


def ratio(coarse: dict[str, Any], fine: dict[str, Any]) -> tuple[float, str]:
    """(h_coarse / h_fine, step kind) between two levels of a ladder: a smaller factor refines everywhere (the ratio from the cell
    counts when both are known), more region levels refine only inside those regions (2 per level)."""
    if coarse["factor"] != fine["factor"]:
        n0, n1 = coarse.get("cells"), fine.get("cells")
        return ((n1 / n0) ** (1 / 3) if n0 and n1 else coarse["factor"] / fine["factor"]), "global"
    rc, rf = coarse.get("regions") or {}, fine.get("regions") or {}
    return 2.0 ** max(rf.get(k, 0) - rc.get(k, 0) for k in {*rc, *rf}), "regional"


def study(rows: list[dict[str, Any]], *, expected: int, tolerance: float, formal_order: float = FORMAL_ORDER) -> dict[str, Any]:
    """Numerical uncertainty of one prediction over its mesh ladder. `rows` are the finished levels coarse to fine, each with factor,
    regions, value and optionally cells, u_iteration (the tail spread) and drift. Resolved: every requested level finished, the finest
    three converge monotonically (or two differ little: Fs 3), GCI and u_numerical <= tolerance of the value, no level's tail mean still
    trending (drift beyond its own spread and DRIFT_MAX: a steady solution that oscillates without a trend is converged to within that
    spread, which u_iteration carries), and the finest steps refine everywhere (a step refined only inside regions is a sensitivity study
    of that region: it leaves the rest of the mesh unassessed)."""
    u_it = float(rows[-1].get("u_iteration") or 0.0) if rows else 0.0
    out: dict[str, Any] = {"mesh_levels": [r["label"] for r in rows], "values": [r["value"] for r in rows], "cells": [r.get("cells") for r in rows],
                           "drift": [r.get("drift") for r in rows], "last": [r.get("last") for r in rows], "u_iterations": [r.get("u_iteration") for r in rows],
                           "u_iteration": u_it}
    if expected < 2:
        return {**out, "u_discretisation": None, "u_numerical": u_it or None, "resolved": None, "unresolved_because": ["one mesh level: no discretisation estimate"]}
    if len(rows) < 2:
        return {**out, "u_discretisation": None, "u_numerical": u_it or None, "resolved": False,
                "unresolved_because": [f"{len(rows)} of {expected} mesh levels finished"]}
    use = rows[-3:]
    steps = [ratio(a, b) for a, b in pairwise(use)]
    g = gci([r["value"] for r in use], [s[0] for s in steps], formal_order)
    u_d = g["gci"] * (abs(use[-1]["value"]) or 1.0) if g["gci"] is not None else None
    why = []
    if len(rows) < expected:
        why.append(f"{expected - len(rows)} of {expected} mesh levels did not finish")
    if g["convergence"] in ("oscillatory", "divergent", "degenerate"):
        why.append(f"the finest levels are {g['convergence']}" + (" (a step does not add cells)" if g["convergence"] == "degenerate" else ""))
    if g["gci"] is not None and g["gci"] > tolerance:
        why.append(f"GCI {g['gci']:.3g} > {tolerance:g}")
    drifting = [r["label"] for r in use if r.get("drift") is not None and r["drift"] > max(DRIFT_MAX, (r.get("u_iteration") or 0.0) / (abs(r["value"]) or 1.0))]
    if drifting:
        why.append(f"the iteration mean still trends at levels {drifting}: it moved more than its own spread (and {DRIFT_MAX:g}) between the last two fifths")
    if any(kind == "regional" for _, kind in steps):
        why.append("a finest step refines only inside regions: the rest of the mesh is not assessed there")
    u_num = math.hypot(u_d, u_it) if u_d is not None else u_it or None
    if u_num is not None and u_d is not None and u_num / (abs(use[-1]["value"]) or 1.0) > tolerance >= g["gci"]:
        why.append(f"u_numerical {u_num / (abs(use[-1]['value']) or 1.0):.3g} of the value > {tolerance:g} (the iteration spread)")
    return {**out, **g, "ratios": [s[0] for s in steps], "steps": [s[1] for s in steps], "u_discretisation": u_d,
            "u_numerical": u_num, "resolved": not why, "unresolved_because": why}


def refinement(studies: dict[str, dict[str, Any]], tolerance: float, skipped: list[str] | None = None) -> dict[str, Any]:
    """A simulation's ladder verdict: ok when every prediction is resolved."""
    worst = max((s["gci"] for s in studies.values() if s.get("gci") is not None), default=None)
    return {"observables": studies, "gci_max": worst, "tolerance": tolerance, "skipped": skipped or [],
            "unresolved": sorted(k for k, s in studies.items() if not s.get("resolved")), "ok": bool(studies) and all(s.get("resolved") for s in studies.values())}


def predict(rows: list[dict[str, Any]], st: dict[str, Any], unit: str, case: str | None) -> dict[str, Any]:
    """The observable row: the finest finished level's value with its study's uncertainty."""
    return observable(rows[-1]["value"] if rows else None, unit, case=case, u_numerical=st.get("u_numerical"), levels=st.get("values"),
                      **{k: st.get(k) for k in STUDY_KEYS})
