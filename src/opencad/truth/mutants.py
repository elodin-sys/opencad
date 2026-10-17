"""Deliberately bad parts: prove the scorer rejects them before trusting a PASS.

A mutant is a known-wrong transform of a part that already passes a case (the latest handoff
STEP, or a truth STEP). Scoring it with the case manifest must return FAIL, and the checks that
caught it are recorded. Mutants are declared per case in `truth/cases/<case>/mutants.yaml`; they
are evaluator tests, not truth, so they are not pinned or sequestered.
"""

from __future__ import annotations

import math
import shutil
from pathlib import Path
from typing import Any

import yaml

from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCP.BRep import BRep_Builder
from OCP.gp import gp_Ax1, gp_Ax2, gp_Dir, gp_Pnt, gp_Trsf, gp_Vec
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer
from OCP.StlAPI import StlAPI_Writer
from OCP.TopoDS import TopoDS_Compound, TopoDS_Shape

from opencad.geomcheck import brep
from opencad.io import utc_now
from opencad.paths import RESULTS, results_dir
from opencad.truth import scorer
from opencad.truth.manifest import CaseManifest, case_dir


class MutantError(RuntimeError):
    pass


def _transform(shape: TopoDS_Shape, t: gp_Trsf) -> TopoDS_Shape:
    return BRepBuilderAPI_Transform(shape, t, True).Shape()


def _box(lo: list[float], hi: list[float]) -> TopoDS_Shape:
    return BRepPrimAPI_MakeBox(gp_Pnt(*lo), gp_Pnt(*hi)).Shape()


def _cylinder(point: list[float], direction: list[float], radius: float, t0: float, t1: float) -> TopoDS_Shape:
    d = brep._unit(direction)
    base = [p + t0 * x for p, x in zip(point, d)]
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*base), gp_Dir(*d)), radius, t1 - t0).Shape()


def _bbox_center(shape: TopoDS_Shape) -> list[float]:
    lo, hi = brep.bbox(shape)
    return [(a + b) / 2 for a, b in zip(lo, hi)]


def scale(shape: TopoDS_Shape, factor: float = 1.02, about: list[float] | None = None) -> TopoDS_Shape:
    """Uniform scale about a point (default: the bbox minimum corner, so the datum stays put)."""
    lo, _ = brep.bbox(shape)
    t = gp_Trsf()
    t.SetScale(gp_Pnt(*(about or lo)), factor)
    return _transform(shape, t)


def translate(shape: TopoDS_Shape, offset: list[float]) -> TopoDS_Shape:
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(*offset))
    return _transform(shape, t)


def mirror(shape: TopoDS_Shape, axis: str = "y", about: list[float] | None = None) -> TopoDS_Shape:
    """Mirror across the plane normal to `axis` through the bbox centre: same bbox and volume, opposite handedness."""
    c = about or _bbox_center(shape)
    n = [0.0, 0.0, 0.0]
    n["xyz".index(axis)] = 1.0
    t = gp_Trsf()
    t.SetMirror(gp_Ax2(gp_Pnt(*c), gp_Dir(*n)))
    return _transform(shape, t)


def rotate(shape: TopoDS_Shape, axis: str = "z", angle_deg: float = 1.0, about: list[float] | None = None) -> TopoDS_Shape:
    c = about or _bbox_center(shape)
    n = [0.0, 0.0, 0.0]
    n["xyz".index(axis)] = 1.0
    t = gp_Trsf()
    t.SetRotation(gp_Ax1(gp_Pnt(*c), gp_Dir(*n)), math.radians(angle_deg))
    return _transform(shape, t)


def fill_box(shape: TopoDS_Shape, min: list[float], max: list[float]) -> TopoDS_Shape:  # noqa: A002 - yaml keys
    """Fuse a block: fills a pocket, blocks a passage, bridges two bodies."""
    return BRepAlgoAPI_Fuse(shape, _box(min, max)).Shape()


def cut_box(shape: TopoDS_Shape, min: list[float], max: list[float]) -> TopoDS_Shape:  # noqa: A002
    """Cut a block: removes a pin or leg, thins a wall, opens a cavity."""
    return BRepAlgoAPI_Cut(shape, _box(min, max)).Shape()


def shift_hole(shape: TopoDS_Shape, near: list[float], offset: list[float], radius: float | None = None) -> TopoDS_Shape:
    """Fill the concave cylinder nearest `near` (optionally of a given radius) and re-cut it displaced by `offset`."""
    holes = [c for c in brep.cylinders(shape) if c["kind"] == "hole" and (radius is None or abs(c["radius"] - radius) <= 0.05)]
    if not holes:
        raise MutantError("no concave cylinder to shift")
    h = min(holes, key=lambda c: math.dist(c["center"], near))
    pad = 0.5
    # plug exactly the hole's extent (a protruding plug would read as a new pin); the radial excess lies inside existing material
    plug = _cylinder(h["point"], h["direction"], h["radius"] + 1e-4, h["t_min"], h["t_max"])
    filled = BRepAlgoAPI_Fuse(shape, plug).Shape()
    moved = [p + o for p, o in zip(h["point"], offset)]
    tool = _cylinder(moved, h["direction"], h["radius"], h["t_min"] - pad, h["t_max"] + pad)
    return BRepAlgoAPI_Cut(filled, tool).Shape()


def fuse_solids(shape: TopoDS_Shape) -> TopoDS_Shape:
    """Union every solid into one body (a gear pair that is really one mesh)."""
    sols = brep.solids(shape)
    if len(sols) < 2:
        raise MutantError("fewer than two solids to fuse")
    acc = sols[0]
    for s in sols[1:]:
        acc = BRepAlgoAPI_Fuse(acc, s).Shape()
    return acc


def translate_solid(shape: TopoDS_Shape, contains: list[float], offset: list[float]) -> TopoDS_Shape:
    """Move only the solid that contains a point (a mis-placed part of an assembly, a wrong centre distance)."""
    sols = brep.solids(shape)
    t = gp_Trsf()
    t.SetTranslation(gp_Vec(*offset))
    comp = TopoDS_Compound()
    b = BRep_Builder()
    b.MakeCompound(comp)
    moved = 0
    for s in sols:
        if brep.classify_points(s, [tuple(contains)])[0] == "in":
            b.Add(comp, _transform(s, t))
            moved += 1
        else:
            b.Add(comp, s)
    if not moved:
        raise MutantError(f"no solid contains {contains}")
    return comp


def remove_solid(shape: TopoDS_Shape, contains: list[float]) -> TopoDS_Shape:
    """Drop the solid that contains a point (a missing part of an assembly)."""
    sols = brep.solids(shape)
    keep = [s for s in sols if brep.classify_points(s, [tuple(contains)])[0] != "in"]
    if len(keep) == len(sols):
        raise MutantError(f"no solid contains {contains}")
    comp = TopoDS_Compound()
    b = BRep_Builder()
    b.MakeCompound(comp)
    for s in keep:
        b.Add(comp, s)
    return comp


OPS = {
    "scale": scale, "translate": translate, "mirror": mirror, "rotate": rotate,
    "fill_box": fill_box, "cut_box": cut_box, "shift_hole": shift_hole,
    "fuse_solids": fuse_solids, "remove_solid": remove_solid, "translate_solid": translate_solid,
}


def mutate_shape(shape: TopoDS_Shape, spec: dict[str, Any]) -> TopoDS_Shape:
    """Apply one mutant spec: {op: name, ...kwargs} or {ops: [spec, ...]} for a chain."""
    if "ops" in spec:
        for s in spec["ops"]:
            shape = mutate_shape(shape, s)
        return shape
    op = spec.get("op")
    if op not in OPS:
        raise MutantError(f"unknown mutant op {op!r}; known: {sorted(OPS)}")
    kwargs = {k: v for k, v in spec.items() if k not in ("op", "id", "note", "source", "expect_caught_by")}
    return OPS[op](shape, **kwargs)


def write_step(shape: TopoDS_Shape, path: Path) -> Path:
    w = STEPControl_Writer()
    w.Transfer(shape, STEPControl_AsIs)
    if w.Write(str(path)) != IFSelect_RetDone:
        raise MutantError(f"STEP write failed: {path}")
    return path


def write_stl(shape: TopoDS_Shape, path: Path, deflection: float = 0.02) -> Path:
    BRepMesh_IncrementalMesh(shape, deflection, False, 0.2, True)
    w = StlAPI_Writer()
    w.ASCIIMode = False
    w.Write(shape, str(path))
    return path


def load_mutants(case_id: str) -> list[dict[str, Any]]:
    p = case_dir(case_id) / "mutants.yaml"
    if not p.exists():
        return []
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return list(data.get("mutants") or [])


def resolve_source(case_id: str, m: CaseManifest, arm_id: str, source: str) -> Path:
    """`candidate` = the arm's handoff STEP; `truth` = the first STEP among truth files; else a path."""
    arm = next((a for a in m.arms if a.id == arm_id), None)
    if arm is None:
        raise MutantError(f"arm {arm_id} not in manifest {case_id}")
    if source == "candidate":
        p = results_dir(arm.design) / "handoff" / f"{arm.design}.step"
        if not p.exists():
            raise MutantError(f"no handoff STEP at {p}")
        return p
    if source == "truth":
        for t in m.truth:
            if Path(t.path).suffix.lower() in (".step", ".stp"):
                return case_dir(case_id) / t.path
        raise MutantError(f"{case_id} has no truth STEP")
    for p in (case_dir(case_id) / source, Path(source)):
        if p.exists():
            return p
    raise MutantError(f"source {source} does not exist")


def run_mutant(case_id: str, m: CaseManifest, arm_id: str, spec: dict[str, Any], *, source: str = "candidate",
               out_dir: Path | None = None, baseline: bool = True) -> dict[str, Any]:
    """Score one mutant; it must FAIL. Also scores the unmutated source (which must PASS) unless baseline=False."""
    case = case_dir(case_id)
    base_src = resolve_source(case_id, m, arm_id, source)
    # a mutant may bring its own wrong geometry (`source:`); the baseline is still the case's passing source
    src = resolve_source(case_id, m, arm_id, spec["source"]) if spec.get("source") else base_src
    mid = spec.get("id") or spec.get("op") or "mutant"
    out = out_dir or (RESULTS / "_mutants" / case_id / arm_id / mid)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    shape = brep.read_step(src)
    result: dict[str, Any] = {"id": mid, "spec": {k: v for k, v in spec.items() if k != "id"}, "source": str(src), "scored_at": utc_now()}
    if baseline:
        # mesh-based kinds (passage, thickness, deviation) need an STL: use the source's sibling STL or tessellate the STEP
        sib = base_src.with_suffix(".stl")
        base_stl = sib if sib.exists() else write_stl(brep.read_step(base_src), out / "baseline.stl")
        base_checks = scorer.score_checks(case, m, base_src, base_stl)
        base_failed = [c["id"] for c in base_checks if c["required"] and not c.get("ok")]
        result["baseline"] = {"verdict": "PASS" if not base_failed else "FAIL", "failed": base_failed}
    try:
        mutated = mutate_shape(shape, spec)
    except MutantError as e:
        result.update({"verdict": "ERROR", "error": str(e), "ok": False})
        return result
    step = write_step(mutated, out / f"{mid}.step")
    stl = write_stl(mutated, out / f"{mid}.stl")
    checks = scorer.score_checks(case, m, step, stl)
    caught = [c["id"] for c in checks if c["required"] and not c.get("ok")]
    result.update({
        "step": str(step), "stl": str(stl),
        "verdict": "FAIL" if caught else "PASS",
        "caught_by": caught,
        "summary": scorer.summarize_checks(checks),
        "checks": checks,
    })
    expect = spec.get("expect_caught_by")
    result["ok"] = bool(caught) and (not expect or any(e in caught for e in expect)) and result.get("baseline", {}).get("verdict", "PASS") == "PASS"
    return result
