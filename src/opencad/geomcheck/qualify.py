"""Supplied CAD qualification: a reference STEP must be valid, closed, positively oriented solids before any boolean uses it.
`qualify` reports; `repair` applies ShapeFix, a sewing tolerance sweep (one solid per closed shell) and orientation, then
re-qualifies and records every step. OpenCascade only."""

from __future__ import annotations

from typing import Any

from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.BRepLib import BRepLib
from OCP.GProp import GProp_GProps
from OCP.ShapeAnalysis import ShapeAnalysis_Shell
from OCP.ShapeFix import ShapeFix_Shape, ShapeFix_Solid
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL
from OCP.TopoDS import TopoDS, TopoDS_Compound

from opencad.geomcheck import brep

SEW_TOLERANCES = (0.01, 0.02, 0.05, 0.1, 0.2, 0.5)  # mm, smallest first: the first that closes every shell wins
MIN_VOLUME = 1e-9  # mm3; a solid at or below it is empty or inside-out


def _volume(shape: Any) -> float:
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props, 1e-7)
    return float(props.Mass())


def _compound(shapes: list[Any]) -> Any:
    from OCP.BRep import BRep_Builder

    if len(shapes) == 1:
        return shapes[0]
    c, b = TopoDS_Compound(), BRep_Builder()
    b.MakeCompound(c)
    for s in shapes:
        b.Add(c, s)
    return c


def qualify(shape: Any) -> dict[str, Any]:
    """Validity, solid count, free and badly oriented edges, and each solid's signed volume (negative: inside-out)."""
    sols = brep.solids(shape)
    volumes = [_volume(s) for s in sols]
    sas = ShapeAnalysis_Shell()
    sas.LoadShells(shape)
    sas.CheckOrientedShells(shape, True)
    free = len(brep._explore(sas.FreeEdges(), TopAbs_EDGE)) if sas.HasFreeEdges() else 0
    bad = len(brep._explore(sas.BadEdges(), TopAbs_EDGE)) if sas.HasBadEdges() else 0
    invalid = [i for i, s in enumerate(sols) if not BRepCheck_Analyzer(s).IsValid()]
    inverted = [i for i, v in enumerate(volumes) if v <= MIN_VOLUME]
    valid = bool(BRepCheck_Analyzer(shape).IsValid())
    problems = ([] if sols else ["no solid (faces or shells only)"]) + ([] if valid else ["BRepCheck reports an invalid shape"])
    problems += [f"{free} free edges (open shell)"] if free else []
    problems += [f"{bad} edges shared with inconsistent orientation"] if bad else []
    problems += [f"solid {i} is not valid" for i in invalid] + [f"solid {i} is inside-out or empty (volume {volumes[i]:.6g} mm3)" for i in inverted]
    return {"ok": not problems, "valid": valid, "solids": len(sols), "shells": len(brep._explore(shape, TopAbs_SHELL)),
            "faces": len(brep._explore(shape, TopAbs_FACE)), "free_edges": free, "bad_edges": bad, "volumes": volumes,
            "invalid_solids": invalid, "inverted": inverted, "problems": problems}


def _sew(shape: Any, tol: float) -> Any:
    sew = BRepBuilderAPI_Sewing(tol)
    for f in brep._explore(shape, TopAbs_FACE):
        sew.Add(f)
    sew.Perform()
    out = []
    for sh in brep._explore(sew.SewedShape(), TopAbs_SHELL):
        fix = ShapeFix_Solid(BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(sh)).Solid())
        fix.Perform()
        out.append(fix.Solid())
    return _compound(out) if out else sew.SewedShape()


def _orient(shape: Any) -> Any:
    out = []
    for s in brep.solids(shape):
        BRepLib.OrientClosedSolid_s(s)
        out.append(s.Reversed() if _volume(s) < 0 else s)
    return _compound(out)


def bake(shape: Any) -> Any:
    """Each solid rebuilt from its faces as seen from the root, so an orientation held only on the solid or shell (which STEP
    export drops) is carried by the faces themselves."""
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Shell

    out = []
    for s in brep.solids(shape):
        shell, b = TopoDS_Shell(), BRep_Builder()
        b.MakeShell(shell)
        for f in brep._explore(s, TopAbs_FACE):
            b.Add(shell, f)
        shell.Closed(True)
        out.append(BRepBuilderAPI_MakeSolid(shell).Solid())
    return _compound(out) if out else shape


def repair(shape: Any) -> tuple[Any, dict[str, Any]]:
    """The shape made valid where OpenCascade can, with the record of what was done and the qualification before and after."""
    before = qualify(shape)
    if before["ok"]:
        baked = bake(shape)  # valid in memory can still hold its orientation on a flag the STEP writer drops
        return baked, {"ok": True, "steps": [], "before": before, "after": qualify(baked)}
    steps: list[str] = []
    fix = ShapeFix_Shape(shape)
    fix.Perform()
    cur, q = fix.Shape(), None
    steps.append("ShapeFix_Shape")
    q = qualify(cur)
    if not q["solids"] or q["free_edges"] or q["invalid_solids"]:
        for tol in SEW_TOLERANCES:
            cand = _sew(cur, tol)
            qc = qualify(cand)
            if qc["solids"] and not qc["free_edges"]:
                cur, q = cand, qc
                steps.append(f"sewn at {tol:g} mm, one solid per closed shell (ShapeFix_Solid)")
                break
    if q["solids"] and (q["inverted"] or q["bad_edges"]):
        cur = _orient(cur)
        steps.append("inside-out solids re-oriented (BRepLib::OrientClosedSolid, reversed where the volume stayed negative)")
        q = qualify(cur)
    if q["solids"]:
        cur = bake(cur)
        q = qualify(cur)
    return cur, {"ok": q["ok"], "steps": steps, "before": before, "after": q}
