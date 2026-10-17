"""Published STL meshes to STEP solids for analysis-mode machine cases (evaluator side): sew the triangles, make a solid, merge
coplanar facets. Units are kept as published (the case's worker states the scale).

    .venv/bin/python scripts/stl_to_step.py <out_dir> <file.stl> ...
"""

from __future__ import annotations

import sys
from pathlib import Path


def convert(stl: Path, step: Path) -> dict:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing
    from OCP.ShapeFix import ShapeFix_Solid
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    from OCP.StlAPI import StlAPI_Reader
    from OCP.TopAbs import TopAbs_SHELL
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS, TopoDS_Shape

    from opencad.backends.local import write_step
    from opencad.geomcheck import brep

    raw = TopoDS_Shape()
    if not StlAPI_Reader().Read(raw, str(stl)):
        raise RuntimeError(f"cannot read {stl}")
    sew = BRepBuilderAPI_Sewing(1e-6)
    sew.Add(raw)
    sew.Perform()
    exp = TopExp_Explorer(sew.SewedShape(), TopAbs_SHELL)
    mk = BRepBuilderAPI_MakeSolid()
    while exp.More():
        mk.Add(TopoDS.Shell_s(exp.Current()))
        exp.Next()
    fix = ShapeFix_Solid(mk.Solid())
    fix.Perform()
    unify = ShapeUpgrade_UnifySameDomain(fix.Solid(), True, True, True)
    unify.Build()
    solid = unify.Shape()
    write_step(solid, step, step.stem)
    info = brep.analyze_step(step)
    return {"stl": str(stl), "step": str(step), "valid": info.get("valid"), "solids": info.get("solids"), "volume": info.get("volume"),
            "faces": len(brep._explore(solid, __import__("OCP.TopAbs", fromlist=["TopAbs_FACE"]).TopAbs_FACE))}


def main(argv: list[str]) -> int:
    out = Path(argv[0])
    out.mkdir(parents=True, exist_ok=True)
    for f in argv[1:]:
        p = Path(f)
        print(convert(p, out / (p.stem.replace(" ", "-") + ".step")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
