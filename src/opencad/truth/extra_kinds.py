"""Scorer support for the multi-body / interior observable kinds: solid, clearance, passage, thickness, probe.

A manifest may carry `hardware:` envelopes (box / cylinder / step) and `solid` observables that name
bodies by a contained point; `clearance` observables refer to those names or `all`.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from opencad.geomcheck import multibody


class ExtraScorer:
    def __init__(self, case: Path, manifest: Any, shape, stl: Path | None):
        self.case = case
        self.m = manifest
        self.shape = shape
        self.stl = stl
        self._hardware: dict[str, Any] | None = None
        self.solid_specs = [{"name": o.id, "contains_point": list(o.point)} for o in manifest.observables if o.kind == "solid" and o.point is not None]

    @property
    def hardware(self) -> dict[str, Any]:
        if self._hardware is None:
            self._hardware = multibody.build_hardware(list(getattr(self.m, "hardware", None) or []), base_dir=self.case)
        return self._hardware

    def score(self, o: Any, expected: Any = None) -> dict[str, Any]:
        if o.kind == "solid":
            exp = expected if expected is not None else o.expected
            r = multibody.check_solids(self.shape, [{"name": o.id, "contains_point": list(o.point), "volume": ({"expected": exp, "tolerance": o.tolerance, "tolerance_rel": o.tolerance_rel} if exp is not None else None)}])[o.id]
            return {"measured": {k: r.get(k) for k in ("volume", "bbox_min", "bbox_max", "center_of_mass")} if r["found"] else None, "found": r["found"], "checks": r.get("volume_check"), "ok": r["ok"]}
        if o.kind == "clearance":
            r = multibody.check_clearances(self.shape, [{"name": o.id, "a": o.a, "b": o.b, "min_gap": o.min_gap or 0.0, "max_gap": o.max_gap}], self.solid_specs, self.hardware)[o.id]
            return {"measured": {k: r.get(k) for k in ("gap", "interference_volume")}, "expected": {"min_gap": o.min_gap or 0.0, "max_gap": o.max_gap}, "error": r.get("error"), "ok": bool(r.get("ok"))}
        if o.kind == "passage":
            spec = {"name": o.id, "point_a": list(o.point), "point_b": list(o.point_b), "pitch": o.pitch or 0.5, "seal_radius": o.seal_radius, "plugs": o.plugs,
                    "expect_connected": o.expect_connected, "volume_min": o.volume_min, "volume_max": o.volume_max}
            r = multibody.check_passages(self.stl, [spec])[o.id]
            return {"measured": {k: r.get(k) for k in ("connected", "reaches_exterior", "passage_volume")}, "a_state": (r.get("a") or {}).get("state"), "b_state": (r.get("b") or {}).get("state"),
                    "checks": r.get("volume_check"), "expected": {"connected": o.expect_connected, "volume_min": o.volume_min, "volume_max": o.volume_max}, "error": r.get("error"), "ok": bool(r.get("ok"))}
        if o.kind == "thickness":
            r = multibody.check_thickness(self.stl, [{"name": o.id, "min": o.min, "stat": o.stat or "p05", "samples": o.samples or 6000, "region": o.region, "max_thickness": o.max_thickness}])[o.id]
            return {"measured": {k: r.get(k) for k in ("min", "p01", "p05", "p50")}, "stat": o.stat or "p05", "expected": {"min": o.min}, "thinnest_points": r.get("thinnest_points"), "error": r.get("error"), "ok": bool(r.get("ok"))}
        if o.kind == "probe":
            r = multibody.check_probes(self.shape, [{"name": o.id, "state": o.state, "points": o.points}])[o.id]
            return {"measured": r["states"], "expected": o.state, "ok": r["ok"]}
        raise ValueError(o.kind)
