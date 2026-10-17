"""Simulate stage: every contract simulation through its adapter (reduced model, CalculiX, OpenFOAM), then every observable
read from its simulation (or from kinematics/domains) and checked against the requirement the contract states.

Adapter contract: `run(sim, observables, geometry, cases) -> {"status": ok|unavailable|failed, "observables": {id: {"value",
"unit", "u_numerical", "levels", "case"}}, "conservation": {name: {"value", "tolerance", "ok"}}, "refinement": {...}, "series",
"assumptions", "solver"}`. A solver that is not installed returns `unavailable`; nothing is ever zero-filled."""

from __future__ import annotations

import math
import shutil
import time
import traceback
from functools import cached_property
from pathlib import Path
from typing import Any

import numpy as np

from opencad.assembly import AsmCtx
from opencad.assembly import joints as jm
from opencad.geomcheck import brep
from opencad.io import load_json


class Geometry:
    """What an adapter may read: placed bodies at rest (assembly frame, mm), boundaries, fluid regions, part parameters, joints."""

    def __init__(self, actx: AsmCtx):
        self.actx = actx
        self.contract = actx.contract
        self._shapes: dict[str, Any] = {}

    def step(self, body: str) -> Path:
        derived = self.actx.results_dir / "export" / "bodies" / f"{body}-derived.step"
        p = self.actx.placed_step(body)
        return p if p.exists() else derived

    def shape(self, body: str) -> Any:
        if body not in self._shapes:
            self._shapes[body] = brep.read_step(self.step(body))
        return self._shapes[body]

    def stl(self, body: str, deflection: float = 0.05) -> Path:
        from opencad.backends.local import write_stl

        out = self.work_dir("geometry") / f"{body}.stl"
        if not out.exists():
            write_stl(self.shape(body), out, deflection=deflection)
        return out

    def work_dir(self, name: str) -> Path:
        d = self.actx.results_dir / "sim" / name
        d.mkdir(parents=True, exist_ok=True)
        return d

    def previous_dir(self, name: str) -> Path:
        """The last attempt's work directory, set aside when the stage restarted; an adapter may adopt runs from it."""
        return self.actx.results_dir / "sim.prev" / name

    @cached_property
    def domains(self) -> dict[str, Any]:
        return self.actx.load_stage("domains") or {}

    def boundaries(self, body: str) -> dict[str, Any]:
        return (self.domains.get("boundaries") or {}).get(body) or {}

    def boundary_faces(self, body: str, label: str) -> list[int]:
        return ((self.boundaries(body).get("labels") or {}).get(label) or {}).get("faces") or []

    def fluid(self, name: str) -> dict[str, Any]:
        return (self.domains.get("fluids") or {}).get(name) or {}

    def part_contract(self, body: str) -> Any:
        from opencad.contract import load_contract
        from opencad.paths import design_dir

        p = self.contract.part(body)
        if p.kind != "modelled" or not (design_dir(p.design) / "contract.yaml").exists():
            return None
        return load_contract(design_dir(p.design))

    def parameter(self, body: str, name: str) -> float | None:
        c = self.part_contract(body)
        if c is None:
            return None
        try:
            return float(c.parameter(name).value)
        except KeyError:
            return None

    def asm_parameter(self, name: str) -> float | None:
        return next((float(p.value) for p in self.contract.parameters if p.name == name), None)

    @cached_property
    def placements(self) -> dict[str, np.ndarray]:
        from opencad.backends.placements import read_placements

        raw = read_placements(self.actx.results_dir / "export" / "placements.json") or {}
        out = {k: np.asarray(v, float) for k, v in raw.items()}
        for p in self.contract.parts:
            out.setdefault(p.name, np.eye(4))
        return out

    def joint_axis(self, joint: str) -> tuple[np.ndarray, np.ndarray]:
        return jm.world_axes(self.contract, self.placements)[joint]

    def joint_of(self, body: str) -> Any:
        return jm.tree_joint(self.contract, body)

    def volume(self, body: str) -> float:
        return float(brep.volume_props(self.shape(body))["volume"])

    def bbox(self, body: str) -> tuple[list[float], list[float]]:
        return brep.bbox(self.shape(body))

    def radial_extent(self, body: str, joint: str | None = None, *, band: tuple[float, float] | None = None, beyond: float | None = None) -> tuple[float, float]:
        """(min, max) distance of the body's surface from a joint axis (default its own), sampled on the tessellation; `band` keeps
        points whose axial coordinate lies in it, `beyond` keeps points farther than that radius."""
        import trimesh

        o, a = self.joint_axis(joint or self.joint_of(body).name)
        m = trimesh.load(self.stl(body), force="mesh")
        w = np.asarray(m.vertices) - o
        t = w @ a
        r = np.linalg.norm(w - np.outer(t, a), axis=1)
        keep = np.ones(len(r), bool)
        if band is not None:
            keep &= (t >= band[0]) & (t <= band[1])
        if beyond is not None:
            keep &= r > beyond
        r = r[keep] if keep.any() else r
        return float(r.min()), float(r.max())

    def axial_extent(self, body: str, joint: str) -> tuple[float, float]:
        import trimesh

        o, a = self.joint_axis(joint)
        t = (np.asarray(trimesh.load(self.stl(body), force="mesh").vertices) - o) @ a
        return float(t.min()), float(t.max())


def value(inputs: dict[str, Any], key: str, default: float | None = None) -> float:
    """An input's value in SI as declared; KeyError names the missing input when there is no default."""
    if key in inputs:
        return float(inputs[key].value)
    if default is not None:
        return default
    raise KeyError(f"simulation input {key!r} is missing")


def adapter(solver: str) -> Any:
    if solver.startswith("reduced:"):
        from opencad.sim.reduced import module

        return module(solver.split(":", 1)[1])
    if solver == "calculix":
        from opencad.sim import calculix

        return calculix
    if solver == "openfoam":
        from opencad.sim import openfoam

        return openfoam
    raise KeyError(solver)


def requirement(o: Any, v: float | None, u: float | None = None) -> dict[str, Any] | None:
    """The source requirement judged over the prediction's numerical band v +- 2 u: met when the whole band meets it, failed when the
    whole band misses it, undetermined (None) otherwise, so a wider uncertainty can make a requirement harder to meet, never easier."""
    if o.min is None and o.max is None and o.expected is None:
        return None
    if v is None:
        return {"ok": None, "note": "no prediction"}
    lo, hi = v - 2 * (u or 0.0), v + 2 * (u or 0.0)
    req_lo, req_hi = o.min if o.min is not None else -math.inf, o.max if o.max is not None else math.inf
    out: dict[str, Any] = {"min": o.min, "max": o.max, "value_band": [lo, hi]}
    if o.expected is not None:
        _, band = o.expected.within(v)
        req_lo, req_hi = max(req_lo, o.expected.expected - band), min(req_hi, o.expected.expected + band)
        out.update(expected=o.expected.expected, band=band)
    ok = True if req_lo <= lo and hi <= req_hi else (False if hi < req_lo or lo > req_hi else None)
    return {**out, "ok": ok, **({"note": "undetermined: the numerical band straddles the requirement"} if ok is None else {})}


KINEMATIC = ("joint_value", "joint_range", "point_x", "point_y", "point_z")
SERIES_STEP = 1.0  # deg or mm between the drive values of a kinematic series


def measured_contract(a: Any, kin: dict[str, Any]) -> tuple[Any, str | None]:
    """The contract with every transmission's declared ratio replaced by the evaluator's measurement (tooth counts, rack pitch)."""
    trans = kin.get("transmissions") or {}
    out = []
    for t in a.transmissions:
        m = (trans.get(t.name) or {}).get("ratio_measured")
        if m is None:
            return None, f"transmission {t.name} has no measured ratio"
        out.append(t.model_copy(update={"ratio": float(m)}))
    return a.model_copy(update={"transmissions": out}), None


def _input(a: Any, o: Any) -> tuple[str | None, tuple[float, float] | None]:
    """The drive of a kinematic observable (its motion's, or the only motor) and the motion's range."""
    if o.motion is not None:
        m = next(m for m in a.acceptance.motions if m.name == o.motion)
        return m.drive, (float(m.range[0]), float(m.range[1]))
    motors = [j.name for j in a.joints if j.drive is not None and j.drive.kind == "motor"]
    return (motors[0], None) if len(motors) == 1 else (None, None)


def _grid(q0: float, q1: float) -> list[float]:
    return [float(q) for q in np.linspace(q0, q1, max(2, int(np.ceil(abs(q1 - q0) / SERIES_STEP)) + 1))]


def kinematic(actx: AsmCtx, o: Any, kin: dict[str, Any]) -> dict[str, Any]:
    """joint_value / joint_range / point_* from the placed bodies, the contract's joint frames and the measured transmission
    ratios, solved by continuation from rest (a loop keeps its assembled branch)."""
    a, why = measured_contract(actx.contract, kin)
    if a is None:
        return {"status": "unavailable", "note": why}
    drive, span = _input(a, o)
    if drive is None:
        return {"status": "unavailable", "note": "name the input with `motion` (the contract has no single motor)"}
    if o.at is None and span is None:
        return {"status": "unavailable", "note": "state `at` (a drive value) or `motion` (a series over its range)"}
    if o.quantity == "joint_range" and span is None:
        return {"status": "unavailable", "note": "joint_range needs `motion`"}
    if o.quantity.startswith("joint_") and o.joint is None or o.quantity.startswith("point_") and (o.body is None or o.location is None):
        return {"status": "unavailable", "note": f"{o.quantity} needs " + ("`joint`" if o.quantity.startswith("joint_") else "`body` and `location`")}
    placements, _ = load_placements(actx)
    over = o.at is None or o.quantity == "joint_range"
    lead = _grid(0.0, span[0])[:-1] if over else []  # from rest to the start of the range, so the loop keeps its branch
    qs = lead + (_grid(*span) if over else _grid(0.0, o.at))
    path = jm.solve_path(a, placements, [{drive: q} for q in qs])
    if not all(info["ok"] for _, info in path):
        bad = next((q, info) for q, (_, info) in zip(qs, path) if not info["ok"])
        return {"status": "failed", "note": f"the mechanism does not solve at {drive} = {bad[0]:g} (closure {bad[1]['closure_mm']:.3g} mm, free {bad[1]['free']})"}
    if o.quantity.startswith("joint_"):
        ys = np.array([jm.displacement(a, placements, v, o.joint) for v, _ in path])
        if a.joint(o.joint).closure and a.joint(o.joint).rotates:
            ys = np.degrees(np.unwrap(np.radians(ys)))
    else:
        axis = "xyz".index(o.quantity[-1])
        rest = np.linalg.inv(placements[o.body])
        loc = np.array([*o.location, 1.0])
        ys = np.array([(jm.poses(a, placements, v)[o.body] @ rest @ loc)[axis] for v, _ in path])
    ys = ys[len(lead):]
    src = f"kinematics: {drive} solved by continuation with measured transmission ratios"
    if o.quantity == "joint_range":
        return {"status": "ok", "value": float(ys.max() - ys.min()), "unit": o.unit, "source": src, "range": [float(ys.min()), float(ys.max())]}
    if o.at is not None:
        return {"status": "ok", "value": float(ys[-1]), "unit": o.unit, "source": f"{src}, at {drive} = {o.at:g}"}
    return {"status": "ok", "value": None, "series": {"x": qs[len(lead):], "y": ys.tolist()}, "unit": o.unit, "source": f"{src}, over motion {o.motion}"}


def load_placements(actx: AsmCtx) -> tuple[dict[str, np.ndarray], bool]:
    from opencad.backends.placements import read_placements

    raw = read_placements(actx.results_dir / "export" / "placements.json") or {}
    out = {k: np.asarray(v, float) for k, v in raw.items()}
    for p in actx.contract.parts:
        out.setdefault(p.name, np.eye(4))
    return out, bool(raw)


def geometric(actx: AsmCtx, o: Any) -> dict[str, Any]:
    kin = actx.load_stage("kinematics") or {}
    dom = actx.load_stage("domains") or {}
    if o.quantity in KINEMATIC:
        return kinematic(actx, o, kin)
    if o.quantity == "transmission_ratio" and o.body is not None:
        a, why = measured_contract(actx.contract, kin)
        j = jm.tree_joint(actx.contract, o.body)
        drive, _ = _input(actx.contract, o)
        if a is None or j is None or drive is None:
            return {"status": "unavailable", "note": why or (f"{o.body} is not on a joint" if j is None else "name the input with `motion`")}
        placements, _ = load_placements(actx)
        (lo, _), (hi, _) = jm.solve(a, placements, {drive: -1.0}), jm.solve(a, placements, {drive: 1.0})
        return {"status": "ok", "value": (hi[j.name] - lo[j.name]) / 2.0, "unit": o.unit,
                "source": f"kinematics: d {j.name} / d {drive} at rest with the measured transmission ratios"}
    if o.quantity == "transmission_ratio":
        trans = kin.get("transmissions") or {}
        by_driven = {t["driven"]: (name, t) for name, t in trans.items()}

        def train(joint: str) -> tuple[float | None, list[str]]:
            """Product of measured ratios walking back from `joint` to the motor-driven joint."""
            ratio, path, cur = 1.0, [], joint
            while cur in by_driven:
                name, t = by_driven[cur]
                if t.get("ratio_measured") is None:
                    return None, [*path, name]
                ratio *= t["ratio_measured"]
                path.append(name)
                cur = t["driver"]
            return ratio, path

        drivers = {t["driver"] for t in trans.values()}  # the whole train: from each last driven joint back to its motor; the longest one
        ends = [t["driven"] for t in trans.values() if t["driven"] not in drivers]
        chains = sorted((train(e) for e in ends), key=lambda c: len(c[1]), reverse=True)
        if not chains:
            return {"status": "unavailable", "note": "no transmission in the contract"}
        ratio, path = chains[0]
        if ratio is None:
            return {"status": "unavailable", "note": f"transmission {path[-1]} has no measured tooth ratio"}
        return {"status": "ok", "value": ratio, "unit": o.unit, "source": f"kinematics.json product of measured ratios along {list(reversed(path))}"}
    if o.quantity == "fluid_volume":
        for name, f in (dom.get("fluids") or {}).items():
            if f.get("volume") is not None:
                return {"status": "ok", "value": f["volume"], "unit": o.unit, "source": f"domains.json fluids.{name}.volume"}
    return {"status": "unavailable", "note": f"no evaluator measurement for quantity {o.quantity!r}"}


def run(actx: AsmCtx) -> dict[str, Any]:
    geom = Geometry(actx)
    cases = {c.id: c for c in actx.contract.operating_cases}
    sims: dict[str, Any] = {}
    for s in actx.contract.simulations:
        obs = [o for o in actx.contract.observables if o.id in s.outputs]
        t0 = time.time()
        print(f"== simulate {s.id} ({s.solver}, {s.physics}) ==", flush=True)
        try:
            r = adapter(s.solver).run(s, obs, geom, cases)
        except Exception as e:  # a crashed adapter is a failed analysis, recorded; never a prediction
            r = {"status": "failed", "error": f"{type(e).__name__}: {e}"[:3000], "traceback": traceback.format_exc()[-3000:]}
        r["wall_s"] = round(time.time() - t0, 2)
        sims[s.id] = r
        print(f"   {s.id}: {r['status']} in {r['wall_s']:.1f} s" + (f" ({r.get('error') or r.get('reason')})" if r["status"] != "ok" else ""), flush=True)
    shutil.rmtree(actx.results_dir / "sim.prev", ignore_errors=True)
    observables: dict[str, Any] = {}
    for o in actx.contract.observables:
        if o.simulation is not None:
            sr = sims.get(o.simulation) or {}
            row = dict((sr.get("observables") or {}).get(o.id) or {"status": sr.get("status") if sr.get("status") != "ok" else "missing"})
            row.setdefault("status", "ok" if row.get("value") is not None else "missing")
        else:
            row = geometric(actx, o)
        row.update(quantity=o.quantity, unit=o.unit, case=o.case, simulation=o.simulation)
        row["requirement"] = requirement(o, row.get("value") if row.get("status") == "ok" else None, row.get("u_numerical"))
        observables[o.id] = row
    failed = [k for k, v in sims.items() if v["status"] == "failed"]
    unmet = [k for k, v in observables.items() if (v.get("requirement") or {}).get("ok") is False]
    return {"ok": not failed and not unmet, "applicable": bool(actx.contract.simulations or actx.contract.observables), "simulations": sims,
            "observables": observables, "failed": failed, "unmet": unmet}


def previous(actx: AsmCtx) -> dict[str, Any]:
    p = actx.stage_file("simulate")
    return load_json(p) if p.exists() else {}
