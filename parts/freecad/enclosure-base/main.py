import math

import FreeCAD
import Part
import Sketcher

outerWidth = 100.0
outerLength = 150.0
baseHeight = 47.0
wallThickness = 3.0
outerCornerRadius = 10.0
bottomEdgeRadius = 2.0
innerCornerRadius = outerCornerRadius - wallThickness
cavityWidth = outerWidth - 2 * wallThickness
cavityLength = outerLength - 2 * wallThickness
postInset = 12.0
postX = outerWidth / 2 - postInset
postY = outerLength / 2 - postInset
postOuterDiameter = 10.0
postBoreDiameter = 4.0

assert outerWidth > 0, "infeasible: outerWidth must be positive"
assert outerLength > 0, "infeasible: outerLength must be positive"
assert baseHeight > 0, "infeasible: baseHeight must be positive"
assert wallThickness > 0, "infeasible: wallThickness must be positive"
assert outerCornerRadius > wallThickness, "infeasible: outerCornerRadius must exceed wallThickness"
assert bottomEdgeRadius > 0, "infeasible: bottomEdgeRadius must be positive"
assert bottomEdgeRadius < wallThickness, "infeasible: bottomEdgeRadius must be less than wallThickness"
assert postOuterDiameter > postBoreDiameter, "infeasible: postBoreDiameter must be less than postOuterDiameter"
assert postBoreDiameter > 0, "infeasible: postBoreDiameter must be positive"
assert postInset > wallThickness + postOuterDiameter / 2, "infeasible: posts collide with side walls"
assert 2 * postX > postOuterDiameter, "infeasible: posts overlap along x"
assert 2 * postY > postOuterDiameter, "infeasible: posts overlap along y"
assert outerWidth > 2 * outerCornerRadius, "infeasible: outerWidth too small for outerCornerRadius"
assert outerLength > 2 * outerCornerRadius, "infeasible: outerLength too small for outerCornerRadius"


def _rounded_rect_face(width, length, radius, z=0.0):
    hw = width / 2.0
    hl = length / 2.0
    r = radius
    z = float(z)
    pts = [
        FreeCAD.Vector(-hw + r, -hl, z),
        FreeCAD.Vector(hw - r, -hl, z),
        FreeCAD.Vector(hw, -hl + r, z),
        FreeCAD.Vector(hw, hl - r, z),
        FreeCAD.Vector(hw - r, hl, z),
        FreeCAD.Vector(-hw + r, hl, z),
        FreeCAD.Vector(-hw, hl - r, z),
        FreeCAD.Vector(-hw, -hl + r, z),
    ]
    ctrs = [
        FreeCAD.Vector(hw - r, -hl + r, z),
        FreeCAD.Vector(hw - r, hl - r, z),
        FreeCAD.Vector(-hw + r, hl - r, z),
        FreeCAD.Vector(-hw + r, -hl + r, z),
    ]
    edges = [
        Part.makeLine(pts[0], pts[1]),
        Part.ArcOfCircle(Part.Circle(ctrs[0], FreeCAD.Vector(0, 0, 1), r), -math.pi / 2, 0).toShape(),
        Part.makeLine(pts[2], pts[3]),
        Part.ArcOfCircle(Part.Circle(ctrs[1], FreeCAD.Vector(0, 0, 1), r), 0, math.pi / 2).toShape(),
        Part.makeLine(pts[4], pts[5]),
        Part.ArcOfCircle(Part.Circle(ctrs[2], FreeCAD.Vector(0, 0, 1), r), math.pi / 2, math.pi).toShape(),
        Part.makeLine(pts[6], pts[7]),
        Part.ArcOfCircle(Part.Circle(ctrs[3], FreeCAD.Vector(0, 0, 1), r), math.pi, 3 * math.pi / 2).toShape(),
    ]
    return Part.Face(Part.Wire(edges))


def _edge_names_on_z(shape, z=0.0, tol=0.05):
    names = []
    for i, edge in enumerate(shape.Edges):
        bb = edge.BoundBox
        if abs(bb.ZMin - z) < tol and abs(bb.ZMax - z) < tol:
            names.append(f"Edge{i + 1}")
    return names


def _face_by_normal_center(shape, normal, center, n_tol=0.08, c_tol=2.0):
    n = FreeCAD.Vector(*normal)
    c = FreeCAD.Vector(*center)
    best = None
    best_d = 1e9
    for i, face in enumerate(shape.Faces):
        surf = face.Surface
        if not hasattr(surf, "Axis"):
            continue
        ax = FreeCAD.Vector(surf.Axis)
        if ax.Length < 1e-9:
            continue
        ax.normalize()
        if ax.dot(n) < 0:
            ax = ax.negative()
        if (ax - n).Length > n_tol:
            continue
        d = (FreeCAD.Vector(face.CenterOfMass) - c).Length
        if d < best_d:
            best_d = d
            best = f"Face{i + 1}"
    if best is None or best_d > c_tol:
        raise RuntimeError(f"face not found normal={normal} center={center} best_d={best_d}")
    return best


def _add_centered_rect(sketch, width, length):
    hw = width / 2.0
    hl = length / 2.0
    g0 = sketch.addGeometry(
        Part.LineSegment(FreeCAD.Vector(-hw, -hl, 0), FreeCAD.Vector(hw, -hl, 0)),
        False,
    )
    g1 = sketch.addGeometry(
        Part.LineSegment(FreeCAD.Vector(hw, -hl, 0), FreeCAD.Vector(hw, hl, 0)),
        False,
    )
    g2 = sketch.addGeometry(
        Part.LineSegment(FreeCAD.Vector(hw, hl, 0), FreeCAD.Vector(-hw, hl, 0)),
        False,
    )
    g3 = sketch.addGeometry(
        Part.LineSegment(FreeCAD.Vector(-hw, hl, 0), FreeCAD.Vector(-hw, -hl, 0)),
        False,
    )
    for a, b in ((g0, g1), (g1, g2), (g2, g3), (g3, g0)):
        sketch.addConstraint(Sketcher.Constraint("Coincident", a, 2, b, 1))
    sketch.addConstraint(Sketcher.Constraint("Horizontal", g0))
    sketch.addConstraint(Sketcher.Constraint("Vertical", g1))
    sketch.addConstraint(Sketcher.Constraint("Horizontal", g2))
    sketch.addConstraint(Sketcher.Constraint("Vertical", g3))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, g0, 1, -hw))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, g0, 1, -hl))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", g0, 1, g0, 2, width))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", g1, 1, g1, 2, length))


doc = FreeCAD.newDocument("enclosure_base")
body = doc.addObject("PartDesign::Body", "Body")
doc.recompute()

outer_solid = _rounded_rect_face(outerWidth, outerLength, outerCornerRadius).extrude(FreeCAD.Vector(0, 0, baseHeight))
outer_part = doc.addObject("Part::Feature", "OuterSolid")
outer_part.Shape = outer_solid
outer_body = body.newObject("PartDesign::FeatureBase", "OuterBody")
outer_body.BaseFeature = outer_part
doc.recompute()

bottom_fillet = body.newObject("PartDesign::Fillet", "BottomFillet")
bottom_fillet.Base = (outer_body, _edge_names_on_z(outer_body.Shape, z=0.0))
bottom_fillet.Radius = bottomEdgeRadius
doc.recompute()

top_face = _face_by_normal_center(bottom_fillet.Shape, (0.0, 0.0, 1.0), (0.0, 0.0, baseHeight))
cavity_sketch = body.newObject("Sketcher::SketchObject", "CavitySketch")
cavity_sketch.AttachmentSupport = [(bottom_fillet, top_face)]
cavity_sketch.MapMode = "FlatFace"
_add_centered_rect(cavity_sketch, cavityWidth, cavityLength)
doc.recompute()

cavity_pocket = body.newObject("PartDesign::Pocket", "CavityPocket")
cavity_pocket.Profile = cavity_sketch
cavity_pocket.Length = baseHeight - wallThickness
doc.recompute()

inner_verts = []
half_w = cavityWidth / 2.0
half_l = cavityLength / 2.0
for i, edge in enumerate(cavity_pocket.Shape.Edges):
    bb = edge.BoundBox
    dx = abs(bb.XMax - bb.XMin)
    dy = abs(bb.YMax - bb.YMin)
    dz = abs(bb.ZMax - bb.ZMin)
    if dz > baseHeight - wallThickness - 1.0 and dx < 0.05 and dy < 0.05:
        cx = (bb.XMin + bb.XMax) / 2.0
        cy = (bb.YMin + bb.YMax) / 2.0
        if abs(abs(cx) - half_w) < 0.1 and abs(abs(cy) - half_l) < 0.1:
            inner_verts.append(f"Edge{i + 1}")

cavity_fillet = body.newObject("PartDesign::Fillet", "CavityFillet")
cavity_fillet.Base = (cavity_pocket, inner_verts)
cavity_fillet.Radius = innerCornerRadius
doc.recompute()

floor_face = _face_by_normal_center(cavity_fillet.Shape, (0.0, 0.0, 1.0), (0.0, 0.0, wallThickness), c_tol=5.0)
post_sketch = body.newObject("Sketcher::SketchObject", "PostSketch")
post_sketch.AttachmentSupport = [(cavity_fillet, floor_face)]
post_sketch.MapMode = "FlatFace"
ro = postOuterDiameter / 2.0
ri = postBoreDiameter / 2.0
for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
    cx = sx * postX
    cy = sy * postY
    go = post_sketch.addGeometry(Part.Circle(FreeCAD.Vector(cx, cy, 0), FreeCAD.Vector(0, 0, 1), ro), False)
    gi = post_sketch.addGeometry(Part.Circle(FreeCAD.Vector(cx, cy, 0), FreeCAD.Vector(0, 0, 1), ri), False)
    post_sketch.addConstraint(Sketcher.Constraint("Radius", go, ro))
    post_sketch.addConstraint(Sketcher.Constraint("Radius", gi, ri))
    post_sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, go, 3, cx))
    post_sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, go, 3, cy))
    post_sketch.addConstraint(Sketcher.Constraint("Coincident", go, 3, gi, 3))
doc.recompute()

post_pad = body.newObject("PartDesign::Pad", "PostPad")
post_pad.Profile = post_sketch
post_pad.Length = baseHeight - wallThickness
post_pad.Refine = True
doc.recompute()

for feat in body.Group:
    if hasattr(feat, "Shape") and feat.Shape is not None and not feat.Shape.isNull():
        assert feat.Shape.isValid(), f"feature {feat.Name} is invalid after recompute"

result = body
