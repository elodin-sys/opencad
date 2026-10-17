import FreeCAD
import Part
import Sketcher

plateWidth = 80.0
plateHeight = 80.0
plateThickness = 8.0
slotLength = 16.0
slotWidth = 6.0
slotDepth = 4.0
slotCentreX = 20.0
slotCentreY = 8.0
assert plateWidth > 0, "infeasible: plateWidth must be positive"
assert plateHeight > 0, "infeasible: plateHeight must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert slotLength > 0, "infeasible: slotLength must be positive"
assert slotWidth > 0, "infeasible: slotWidth must be positive"
assert slotDepth > 0, "infeasible: slotDepth must be positive"
assert slotDepth < plateThickness, "infeasible: slotDepth must leave a web below the floors"
assert abs(slotCentreX) + slotLength / 2 < plateWidth / 2, "infeasible: slot A/C would leave the plate in x"
assert abs(slotCentreY) + slotWidth / 2 < plateHeight / 2, "infeasible: slot A/C would leave the plate in y"
assert abs(slotCentreY) + slotWidth / 2 < plateWidth / 2, "infeasible: slot B/D would leave the plate in x"
assert abs(slotCentreX) + slotLength / 2 < plateHeight / 2, "infeasible: slot B/D would leave the plate in y"

doc = FreeCAD.newDocument("chiral-keyplate")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)

x0 = -plateWidth / 2
y0 = -plateHeight / 2
sketch = body.newObject("Sketcher::SketchObject", "BlankSketch")
sketch.AttachmentSupport = [(xy, "")]
sketch.MapMode = "FlatFace"
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x0, y0, 0), FreeCAD.Vector(-x0, y0, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(-x0, y0, 0), FreeCAD.Vector(-x0, -y0, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(-x0, -y0, 0), FreeCAD.Vector(x0, -y0, 0)), False)
sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x0, -y0, 0), FreeCAD.Vector(x0, y0, 0)), False)
sketch.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 1, 2, 2, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 2, 2, 3, 1))
sketch.addConstraint(Sketcher.Constraint("Coincident", 3, 2, 0, 1))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
sketch.addConstraint(Sketcher.Constraint("Horizontal", 2))
sketch.addConstraint(Sketcher.Constraint("Vertical", 1))
sketch.addConstraint(Sketcher.Constraint("Vertical", 3))
sketch.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, plateWidth))
sketch.addConstraint(Sketcher.Constraint("DistanceY", 0, 1, 3, 1, plateHeight))
sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, x0))
sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, y0))

pad = body.newObject("PartDesign::Pad", "PlateBlank")
pad.Profile = sketch
pad.Length = plateThickness
doc.recompute()


def add_rect(sk, cx, cy, dx, dy):
    xa = cx - dx / 2.0
    ya = cy - dy / 2.0
    xb = cx + dx / 2.0
    yb = cy + dy / 2.0
    g0 = sk.addGeometry(Part.LineSegment(FreeCAD.Vector(xa, ya, 0), FreeCAD.Vector(xb, ya, 0)), False)
    g1 = sk.addGeometry(Part.LineSegment(FreeCAD.Vector(xb, ya, 0), FreeCAD.Vector(xb, yb, 0)), False)
    g2 = sk.addGeometry(Part.LineSegment(FreeCAD.Vector(xb, yb, 0), FreeCAD.Vector(xa, yb, 0)), False)
    g3 = sk.addGeometry(Part.LineSegment(FreeCAD.Vector(xa, yb, 0), FreeCAD.Vector(xa, ya, 0)), False)
    sk.addConstraint(Sketcher.Constraint("Coincident", g0, 2, g1, 1))
    sk.addConstraint(Sketcher.Constraint("Coincident", g1, 2, g2, 1))
    sk.addConstraint(Sketcher.Constraint("Coincident", g2, 2, g3, 1))
    sk.addConstraint(Sketcher.Constraint("Coincident", g3, 2, g0, 1))
    sk.addConstraint(Sketcher.Constraint("Horizontal", g0))
    sk.addConstraint(Sketcher.Constraint("Horizontal", g2))
    sk.addConstraint(Sketcher.Constraint("Vertical", g1))
    sk.addConstraint(Sketcher.Constraint("Vertical", g3))
    sk.addConstraint(Sketcher.Constraint("DistanceX", g0, 1, g0, 2, dx))
    sk.addConstraint(Sketcher.Constraint("DistanceY", g0, 1, g3, 1, dy))
    sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, g0, 1, xa))
    sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, g0, 1, ya))


slot_sketch = body.newObject("Sketcher::SketchObject", "SlotSketch")
slot_sketch.AttachmentSupport = [(xy, "")]
slot_sketch.MapMode = "FlatFace"
slot_sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, plateThickness), FreeCAD.Rotation())
add_rect(slot_sketch, slotCentreX, slotCentreY, slotLength, slotWidth)
add_rect(slot_sketch, -slotCentreY, slotCentreX, slotWidth, slotLength)
add_rect(slot_sketch, -slotCentreX, -slotCentreY, slotLength, slotWidth)
add_rect(slot_sketch, slotCentreY, -slotCentreX, slotWidth, slotLength)

pockets = body.newObject("PartDesign::Pocket", "Slots")
pockets.Profile = slot_sketch
pockets.Type = "Length"
pockets.Length = slotDepth
pockets.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
pocketFloors = ("pocketFloorA", "pocketFloorB", "pocketFloorC", "pocketFloorD")
assert len(pocketFloors) == 4, "infeasible: expected four named pocket floors"
result = body
