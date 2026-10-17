"""Multi-solid deliverables: every local runner keeps every body (rpi5-enclosure base + lid, gear-pair three solids)."""

from __future__ import annotations

import math
from pathlib import Path

import pytest
from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCP.gp import gp_Pnt
from OCP.TopoDS import TopoDS_Compound

from opencad.backends.freecad import runner as fc_runner
from opencad.backends.local import result_shape
from opencad.backends.registry import get
from opencad.geomcheck import brep, mesh, multibody


def _box(z0: float, side: float = 10.0, t: float = 2.0):
    return BRepPrimAPI_MakeBox(gp_Pnt(0, 0, z0), gp_Pnt(side, side, z0 + t)).Shape()


class _Wrapped:
    def __init__(self, shape):
        self.wrapped = shape


class _Stack:
    """Duck-typed cq.Workplane: `vals()` is the stack, `val()` only its first item."""

    def __init__(self, *items):
        self._items = items

    def vals(self):
        return list(self._items)

    def val(self):
        return self._items[0]


class _Builder:
    """Duck-typed build123d BuildPart."""

    def __init__(self, shape):
        self.part = _Wrapped(shape)


def test_result_shape_keeps_every_stack_solid():
    a, b, c = _box(0), _box(5), _box(10)
    comp = result_shape(_Stack(_Wrapped(a), _Wrapped(b)))
    assert isinstance(comp, TopoDS_Compound) and len(brep.solids(comp)) == 2
    assert abs(brep.volume_props(comp)["volume"] - 400.0) < 1e-6
    # list/tuple of shapes, stacks and builders, N deep, not hard-coded to two
    assert len(brep.solids(result_shape([_Wrapped(a), _Stack(_Wrapped(b)), _Builder(c)]))) == 3
    assert len(brep.solids(result_shape((_Wrapped(a), (_Wrapped(b), _Wrapped(c)))))) == 3
    # a lone shape is returned as is, so single-solid STEP output is unchanged
    assert result_shape(_Wrapped(a)).IsSame(a)
    assert result_shape(_Stack(_Wrapped(a))).IsSame(a)
    assert result_shape(_Builder(a)).IsSame(a)
    with pytest.raises(ValueError, match="no OCC shape"):
        result_shape([])
    with pytest.raises(ValueError):
        result_shape(_Stack(object(), object()))  # a stack of points, not solids


# --- FreeCAD runner: pure-Python parts, no freecadcmd needed ---------------------------------------


class _V:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class _Box:
    def __init__(self, lo, hi):
        (self.XMin, self.YMin, self.ZMin), (self.XMax, self.YMax, self.ZMax) = lo, hi


class _Solid:
    def __init__(self, lo, hi):
        self.BoundBox = _Box(lo, hi)
        dx, dy, dz = (h - l for l, h in zip(lo, hi))
        self.Volume = dx * dy * dz
        self.Area = 2 * (dx * dy + dy * dz + dx * dz)
        self.CenterOfMass = _V(*[(l + h) / 2 for l, h in zip(lo, hi)])
        self.Solids = [self]


class _CompoundShape:
    """A Body.Shape that is a Compound (Body.AllowCompound) holding solids."""

    def __init__(self, *solids):
        self.Solids = list(solids)


class _Body:
    TypeId = "PartDesign::Body"

    def __init__(self, shape):
        self.Shape = shape


class _Feat:
    TypeId = "Part::Feature"

    def __init__(self, shape):
        self.Shape = shape


def test_freecad_result_bodies_accepts_one_or_many():
    base, lid = _Body(_Solid((0, 0, 0), (10, 10, 2))), _Body(_Solid((0, 0, 5), (10, 10, 7)))
    assert fc_runner.result_bodies(base) == [base]
    assert fc_runner.result_bodies((base, lid)) == [base, lid]
    assert fc_runner.result_bodies([base, lid, base]) == [base, lid, base]
    with pytest.raises(RuntimeError, match="PartDesign::Body"):
        fc_runner.result_bodies((base, object()))
    with pytest.raises(RuntimeError, match="empty"):
        fc_runner.result_bodies([])


def test_freecad_result_bodies_accepts_part_feature():
    feat = _Feat(_Solid((0, 0, 0), (10, 10, 2)))
    assert fc_runner.result_bodies(feat) == [feat]
    assert fc_runner.result_bodies((feat, feat)) == [feat, feat]


def test_freecad_analyze_bodies_sums_volume_and_weights_centroid():
    base = _Body(_Solid((0, 0, 0), (10, 10, 2)))
    lid = _Body(_CompoundShape(_Solid((0, 0, 5), (10, 10, 7))))
    one = fc_runner.analyze_bodies([base])
    assert one["volume_mm3"] == 200 and one["com"] == [5, 5, 1] and one["bbox_max"] == [10, 10, 2]
    both = fc_runner.analyze_bodies([base, lid])
    assert both["volume_mm3"] == 400 and both["surface_area_mm2"] == 560
    assert both["com"] == [5, 5, 3.5]
    assert both["bbox_min"] == [0, 0, 0] and both["bbox_max"] == [10, 10, 7] and both["bbox_size"] == [10, 10, 7]


# --- engines end to end -------------------------------------------------------------------------

CQ_TWO = """import cadquery as cq

boxSide = 10.0
gap = 3.0
base = cq.Workplane("XY").box(boxSide, boxSide, 2.0, centered=(False, False, False))
lid = cq.Workplane("XY").box(boxSide, boxSide, 2.0, centered=(False, False, False)).translate((0, 0, 2.0 + gap))
result = base.add(lid)
"""

CQ_THREE = """import cadquery as cq

boxSide = 10.0
gap = 3.0
base = cq.Workplane("XY").box(boxSide, boxSide, 2.0, centered=(False, False, False))
lid = base.translate((0, 0, 2.0 + gap))
cap = base.translate((0, 0, 2 * (2.0 + gap)))
result = [base, lid, cap]
"""

B3D_TWO = """from build123d import Align, Box, Pos

boxSide = 10.0
gap = 3.0
base = Box(boxSide, boxSide, 2.0, align=(Align.MIN, Align.MIN, Align.MIN))
lid = Pos(0, 0, 2.0 + gap) * Box(boxSide, boxSide, 2.0, align=(Align.MIN, Align.MIN, Align.MIN))
result = [base, lid]
"""

FC_TWO = """import FreeCAD
import Part
import Sketcher

boxSide = 10.0
gap = 3.0
plateThickness = 2.0
assert boxSide > 0, "infeasible: boxSide must be positive"

doc = FreeCAD.newDocument("twobody")


def plate(name, z0):
    body = doc.addObject("PartDesign::Body", name)
    xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)
    sketch = body.newObject("Sketcher::SketchObject", name + "Sketch")
    sketch.AttachmentSupport = [(xy, "")]
    sketch.MapMode = "FlatFace"
    sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, z0), FreeCAD.Rotation())
    pts = [(0, 0), (boxSide, 0), (boxSide, boxSide), (0, boxSide)]
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(*a, 0), FreeCAD.Vector(*b, 0)), False)
    for i in range(4):
        sketch.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
    sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
    sketch.addConstraint(Sketcher.Constraint("Horizontal", 2))
    sketch.addConstraint(Sketcher.Constraint("Vertical", 1))
    sketch.addConstraint(Sketcher.Constraint("Vertical", 3))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, boxSide))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", 0, 1, 3, 1, boxSide))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, 0.0))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, 0.0))
    pad = body.newObject("PartDesign::Pad", name + "Pad")
    pad.Profile = sketch
    pad.Length = plateThickness
    pad.Refine = True
    return body


base = plate("Base", 0.0)
lid = plate("Lid", plateThickness + gap)
doc.recompute()
result = (base, lid)
"""

# gear-pair seating idiom: the lid sits on the base (zero gap) and both carry the same through hole, so the coincident
# faces at z = 2 share the hole's vertex ring
FC_TOUCHING = """import FreeCAD
import Part
import Sketcher

boxSide = 10.0
lidSide = 6.0
holeDiameter = 3.0
plateThickness = 2.0
assert lidSide < boxSide, "infeasible: the lid must sit inside the base footprint"

doc = FreeCAD.newDocument("touching")


def plate(name, side, z0):
    body = doc.addObject("PartDesign::Body", name)
    xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)
    sketch = body.newObject("Sketcher::SketchObject", name + "Sketch")
    sketch.AttachmentSupport = [(xy, "")]
    sketch.MapMode = "FlatFace"
    sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, z0), FreeCAD.Rotation())
    lo, hi = (boxSide - side) / 2, (boxSide + side) / 2
    pts = [(lo, lo), (hi, lo), (hi, hi), (lo, hi)]
    for i in range(4):
        a, b = pts[i], pts[(i + 1) % 4]
        sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(*a, 0), FreeCAD.Vector(*b, 0)), False)
    for i in range(4):
        sketch.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % 4, 1))
    sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
    sketch.addConstraint(Sketcher.Constraint("Horizontal", 2))
    sketch.addConstraint(Sketcher.Constraint("Vertical", 1))
    sketch.addConstraint(Sketcher.Constraint("Vertical", 3))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, side))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", 0, 1, 3, 1, side))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, lo))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, lo))
    centre = FreeCAD.Vector(boxSide / 2, boxSide / 2, 0)
    sketch.addGeometry(Part.Circle(centre, FreeCAD.Vector(0, 0, 1), holeDiameter / 2), False)
    sketch.addConstraint(Sketcher.Constraint("Diameter", 4, holeDiameter))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 4, 3, boxSide / 2))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 4, 3, boxSide / 2))
    pad = body.newObject("PartDesign::Pad", name + "Pad")
    pad.Profile = sketch
    pad.Length = plateThickness
    pad.Refine = True
    return body


base = plate("Base", boxSide, 0.0)
lid = plate("Lid", lidSide, plateThickness)
doc.recompute()
result = (base, lid)
"""

HOLE = math.pi * 1.5**2 * 2.0
TOUCHING_SOLIDS = [
    {"name": "base", "contains_point": [1, 1, 1], "volume": {"expected": 200.0 - HOLE, "tolerance_rel": 0.001}},
    {"name": "lid", "contains_point": [3, 3, 3], "volume": {"expected": 72.0 - HOLE, "tolerance_rel": 0.001}},
]

SOLIDS = [
    {"name": "base", "contains_point": [5, 5, 1], "volume": {"expected": 200.0, "tolerance_rel": 0.001}},
    {"name": "lid", "contains_point": [5, 5, 6], "volume": {"expected": 200.0, "tolerance_rel": 0.001}},
]


def _check_exports(backend: str, entry: Path, n: int, out: Path) -> None:
    eng = get(backend).engine
    total = 200.0 * n
    a = eng.analyze(entry)
    assert abs(a["volume_mm3"] - total) < 1e-6
    assert a["bbox_min"] == pytest.approx([0, 0, 0]) and a["bbox_max"] == pytest.approx([10, 10, 5 * n - 3])
    assert a["com"][2] == pytest.approx((5 * n - 3) / 2)  # compound centroid, not the first body's
    step = eng.export(entry, out, "step")[0]
    s = brep.analyze_step(step)
    assert s["solids"] == n and s["valid"] and abs(s["volume"] - total) < 1e-6
    found = multibody.check_solids(brep.read_step(step), SOLIDS)
    assert found["base"]["ok"] and found["lid"]["ok"], found
    m = mesh.analyze_mesh(eng.export(entry, out, "stl")[0])
    assert m["components"] == n and m["solids_watertight"] and abs(m["volume"] - total) < 1e-3


CQ_PLACEMENTS = """import cadquery as cq

boxSide = 10.0
gap = 3.0
base = cq.Workplane("XY").box(boxSide, boxSide, 2.0, centered=(False, False, False))
lid = cq.Workplane("XY").box(boxSide, boxSide, 2.0, centered=(False, False, False)).translate((0, 0, 2.0 + gap))
result = [base, lid]
placements = {
    "base": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
    "lid": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 5.0], [0, 0, 0, 1]],
}
"""

B3D_PLACEMENTS = """from build123d import Align, Box, Pos

boxSide = 10.0
gap = 3.0
base = Box(boxSide, boxSide, 2.0, align=(Align.MIN, Align.MIN, Align.MIN))
lid = Pos(0, 0, 2.0 + gap) * Box(boxSide, boxSide, 2.0, align=(Align.MIN, Align.MIN, Align.MIN))
result = [base, lid]
placements = {
    "base": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
    "lid": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 5.0], [0, 0, 0, 1]],
}
"""


@pytest.mark.parametrize(
    "backend,src,n", [("cadquery", CQ_TWO, 2), ("cadquery", CQ_THREE, 3), ("build123d", B3D_TWO, 2)]
)
def test_multi_solid_result_exports_every_solid(backend, src, n, tmp_path):
    entry = tmp_path / backend / "main.py"
    entry.parent.mkdir()
    entry.write_text(src)
    _check_exports(backend, entry, n, tmp_path / backend / "out")


@pytest.mark.parametrize("backend,src", [("cadquery", CQ_PLACEMENTS), ("build123d", B3D_PLACEMENTS)])
def test_placements_passthrough(backend, src, tmp_path):
    import json

    entry = tmp_path / backend / "main.py"
    entry.parent.mkdir()
    entry.write_text(src)
    out = tmp_path / backend / "out"
    get(backend).engine.export(entry, out, "step")
    plc = json.loads((out / "placements.json").read_text())
    assert plc["lid"][2][3] == 5.0 and plc["base"][0][0] == 1.0


def test_freecad_two_bodies_if_installed(tmp_path, monkeypatch):
    from opencad.backends.freecad import freecadcmd

    if not Path(freecadcmd()).exists():
        pytest.skip("freecadcmd not installed")
    monkeypatch.setenv("OPENCAD_ENGINE_CACHE", str(tmp_path / "cache"))
    entry = tmp_path / "freecad" / "main.py"
    entry.parent.mkdir()
    entry.write_text(FC_TWO)
    _check_exports("freecad", entry, 2, tmp_path / "freecad" / "out")


def test_freecad_touching_bodies_keep_closed_shells_if_installed(tmp_path, monkeypatch):
    """Meshing the Bodies as one compound welds the shared seating face and tears both shells open
    (gear-pair: 5 torn components, 1158 open edges); one mesh per Body keeps each shell closed."""
    from opencad.backends.freecad import freecadcmd

    if not Path(freecadcmd()).exists():
        pytest.skip("freecadcmd not installed")
    monkeypatch.setenv("OPENCAD_ENGINE_CACHE", str(tmp_path / "cache"))
    entry = tmp_path / "freecad" / "main.py"
    entry.parent.mkdir()
    entry.write_text(FC_TOUCHING)
    eng = get("freecad").engine
    out = tmp_path / "freecad" / "out"
    total = 272.0 - 2 * HOLE
    step = eng.export(entry, out, "step")[0]
    s = brep.analyze_step(step)
    assert s["solids"] == 2 and s["valid"] and abs(s["volume"] - total) < 1e-6
    found = multibody.check_solids(brep.read_step(step), TOUCHING_SOLIDS)
    assert found["base"]["ok"] and found["lid"]["ok"], found
    m = mesh.analyze_mesh(eng.export(entry, out, "stl")[0])
    assert m["components"] == 2 and m["solids_watertight"] and m["open_edges"]["count"] == 0, m
    assert abs(m["volume"] - total) / total < 1e-3  # chordal error on the Ø3 hole only
