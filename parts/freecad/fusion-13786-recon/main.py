import FreeCAD
import Part
import PartDesign
import Sketcher

plateWidth = 100.0
plateHeight = 100.0
plateThickness = 3.0
holeDia = 5.0
holeCentreX = 0.0
holeCentreY = 0.0
edgeHoleDia = 2.0
edgeHoleY = 42.0
edgeHoleDepth = 5.0
edgeHoleZ = 1.5
pinDia = 6.0
pinCentreX = 47.0
pinCentreY = 47.0
chamferLeg = 5.0
topStrip = 10.0
midBridge = 9.5
slotCentreX = 0.0
slotCentreY = 26.0
slotRx = 35.0
slotRy = 14.0

assert plateWidth > 0, "infeasible: plateWidth must be positive"
assert plateHeight > 0, "infeasible: plateHeight must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert holeDia > 0, "infeasible: holeDia must be positive"
assert holeCentreY + holeDia / 2.0 < slotCentreY - slotRy, "infeasible: holeDia collides with the slot"
assert abs(holeCentreX) < plateWidth, "infeasible: holeCentreX outside the plate"
assert abs(slotCentreX) < plateWidth, "infeasible: slotCentreX outside the plate"
assert edgeHoleDia > 0, "infeasible: edgeHoleDia must be positive"
assert edgeHoleDepth > 0, "infeasible: edgeHoleDepth must be positive"
assert edgeHoleDepth < plateWidth / 2.0, "infeasible: edgeHoleDepth reaches past the mid-plane"
assert 0 < edgeHoleY < plateHeight, "infeasible: edgeHoleY outside the plate"
assert edgeHoleZ > 0, "infeasible: edgeHoleZ must be positive"
assert pinDia > 0, "infeasible: pinDia must be positive"
assert pinCentreX > 0, "infeasible: pinCentreX must be positive"
assert pinCentreY > 0, "infeasible: pinCentreY must be positive"
assert chamferLeg > 0, "infeasible: chamferLeg must be positive"
assert chamferLeg * 2.0 < plateWidth, "infeasible: chamferLeg consumes the south edge"
assert chamferLeg * 2.0 < plateHeight, "infeasible: chamferLeg consumes the side edges"
assert topStrip > 0, "infeasible: topStrip must be positive"
assert midBridge > 0, "infeasible: midBridge must be positive"
assert slotRx > 0, "infeasible: slotRx must be positive"
assert slotRy > 0, "infeasible: slotRy must be positive"

_ = PartDesign

doc = FreeCAD.newDocument("part")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()

xy_plane = next(feat for feat in body.Origin.OriginFeatures if feat.Name.endswith("XY_Plane"))


def attach_xy(sketch):
    if hasattr(sketch, "AttachmentSupport"):
        sketch.AttachmentSupport = [(xy_plane, "")]
    else:
        sketch.Support = [(xy_plane, "")]
    sketch.MapMode = "FlatFace"


def vertical_edges_at(feat, x, y):
    names = []
    for i, edge in enumerate(feat.Shape.Edges):
        if not isinstance(edge.Curve, Part.Line):
            continue
        a, b = edge.Vertexes[0].Point, edge.Vertexes[-1].Point
        if abs(a.x - b.x) > 1e-6 or abs(a.y - b.y) > 1e-6:
            continue
        if abs(a.x - x) < 1e-6 and abs(a.y - y) < 1e-6:
            names.append(f"Edge{i + 1}")
    return names


def make_plane(name, origin, x_dir, y_dir, normal):
    plane = body.newObject("PartDesign::Plane", name)
    plane.MapMode = "Deactivated"
    plane.Placement = FreeCAD.Placement(origin, FreeCAD.Rotation(x_dir, y_dir, normal, "ZXY"))
    return plane


def add_circle(sk, cx, cy, diameter):
    gid = sk.addGeometry(
        Part.Circle(FreeCAD.Vector(cx, cy, 0), FreeCAD.Vector(0, 0, 1), diameter / 2.0),
        False,
    )
    sk.addConstraint(Sketcher.Constraint("Diameter", gid, diameter))
    sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gid, 3, cx))
    sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gid, 3, cy))
    return gid


sketch = body.newObject("Sketcher::SketchObject", "PlateSketch")
attach_xy(sketch)

half_w = plateWidth / 2.0
half_h = plateHeight / 2.0
sketch.addGeometry(
    Part.LineSegment(FreeCAD.Vector(-half_w, -half_h, 0), FreeCAD.Vector(half_w, -half_h, 0)),
    False,
)
sketch.addGeometry(
    Part.LineSegment(FreeCAD.Vector(half_w, -half_h, 0), FreeCAD.Vector(half_w, half_h, 0)),
    False,
)
sketch.addGeometry(
    Part.LineSegment(FreeCAD.Vector(half_w, half_h, 0), FreeCAD.Vector(-half_w, half_h, 0)),
    False,
)
sketch.addGeometry(
    Part.LineSegment(FreeCAD.Vector(-half_w, half_h, 0), FreeCAD.Vector(-half_w, -half_h, 0)),
    False,
)
sketch.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 1, 2, 2, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 2, 2, 3, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 3, 2, 0, 1))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
sketch.addConstraint(Sketcher.Constraint("Vertical", 1))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 2))
sketch.addConstraint(Sketcher.Constraint("Vertical", 3))
sketch.addConstraint(Sketcher.Constraint("DistanceX", 3, 1, 1, 1, plateWidth))
sketch.addConstraint(Sketcher.Constraint("DistanceY", 0, 1, 2, 1, plateHeight))
sketch.addConstraint(Sketcher.Constraint("DistanceX", 3, 1, -1, 1, half_w))
sketch.addConstraint(Sketcher.Constraint("DistanceY", 0, 1, -1, 1, half_h))

pad = body.newObject("PartDesign::Pad", "Pad")
pad.Profile = sketch
pad.Length = plateThickness
pad.Midplane = False
pad.Reversed = False
doc.recompute()

south_edges = vertical_edges_at(pad, -half_w, -half_h) + vertical_edges_at(pad, half_w, -half_h)
assert len(south_edges) == 2, f"expected 2 south corner edges, found {south_edges}"

chamfers = body.newObject("PartDesign::Chamfer", "SouthChamfers")
chamfers.Base = (pad, south_edges)
chamfers.ChamferType = "Equal distance"
chamfers.Size = chamferLeg
chamfers.Angle = 45.0
doc.recompute()

north_edges = vertical_edges_at(chamfers, -half_w, half_h) + vertical_edges_at(chamfers, half_w, half_h)
assert len(north_edges) == 2, f"expected 2 north corner edges, found {north_edges}"

pins = body.newObject("PartDesign::Fillet", "NorthFillets")
pins.Base = (chamfers, north_edges)
pins.Radius = pinDia / 2.0
doc.recompute()

hole_sketch = body.newObject("Sketcher::SketchObject", "HoleSketch")
attach_xy(hole_sketch)
hole_g = hole_sketch.addGeometry(
    Part.Circle(FreeCAD.Vector(holeCentreX, holeCentreY, 0), FreeCAD.Vector(0, 0, 1), holeDia / 2.0),
    False,
)
hole_sketch.addConstraint(Sketcher.Constraint("Diameter", hole_g, holeDia))
hole_sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, hole_g, 3, holeCentreX))
hole_sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, hole_g, 3, holeCentreY))

centre_hole = body.newObject("PartDesign::Pocket", "CentreHole")
centre_hole.Profile = hole_sketch
centre_hole.Type = "ThroughAll"
centre_hole.Reversed = True
doc.recompute()

slot_sketch = body.newObject("Sketcher::SketchObject", "SlotSketch")
attach_xy(slot_sketch)
slot_g = slot_sketch.addGeometry(
    Part.Ellipse(FreeCAD.Vector(slotCentreX, slotCentreY, 0), slotRx, slotRy),
    False,
)
slot_sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, slot_g, 3, slotCentreX))
slot_sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, slot_g, 3, slotCentreY))

slot = body.newObject("PartDesign::Pocket", "OvalSlot")
slot.Profile = slot_sketch
slot.Type = "ThroughAll"
slot.Reversed = True
doc.recompute()

plane_neg = make_plane(
    "EdgePlaneNeg",
    FreeCAD.Vector(-half_w, 0, 0),
    FreeCAD.Vector(0, 1, 0),
    FreeCAD.Vector(0, 0, 1),
    FreeCAD.Vector(1, 0, 0),
)
edge_neg_sketch = body.newObject("Sketcher::SketchObject", "EdgeHoleNegSketch")
if hasattr(edge_neg_sketch, "AttachmentSupport"):
    edge_neg_sketch.AttachmentSupport = [(plane_neg, "")]
else:
    edge_neg_sketch.Support = [(plane_neg, "")]
edge_neg_sketch.MapMode = "FlatFace"
add_circle(edge_neg_sketch, edgeHoleY, edgeHoleZ, edgeHoleDia)
edge_neg = body.newObject("PartDesign::Pocket", "EdgeHoleNeg")
edge_neg.Profile = edge_neg_sketch
edge_neg.Type = "Length"
edge_neg.Length = edgeHoleDepth
edge_neg.Reversed = True
doc.recompute()

plane_pos = make_plane(
    "EdgePlanePos",
    FreeCAD.Vector(half_w, 0, 0),
    FreeCAD.Vector(0, 1, 0),
    FreeCAD.Vector(0, 0, 1),
    FreeCAD.Vector(1, 0, 0),
)
edge_pos_sketch = body.newObject("Sketcher::SketchObject", "EdgeHolePosSketch")
if hasattr(edge_pos_sketch, "AttachmentSupport"):
    edge_pos_sketch.AttachmentSupport = [(plane_pos, "")]
else:
    edge_pos_sketch.Support = [(plane_pos, "")]
edge_pos_sketch.MapMode = "FlatFace"
add_circle(edge_pos_sketch, edgeHoleY, edgeHoleZ, edgeHoleDia)
edge_pos = body.newObject("PartDesign::Pocket", "EdgeHolePos")
edge_pos.Profile = edge_pos_sketch
edge_pos.Type = "Length"
edge_pos.Length = edgeHoleDepth
edge_pos.Reversed = False
edge_pos.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
result = body
