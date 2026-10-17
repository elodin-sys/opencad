import FreeCAD
import Part
import Sketcher

xMin = 100.0
yMin = 0.0
zMin = 70.0
bodyWidth = 10.0
bodyDepth = 10.0
bodyHeight = 50.0
overallLength = 88.0
holeDiameter = 5.0
shaftDiameter = 5.0
filletRadius = 4.0
xMax = 110.0
yHead = 10.0
zMax = 120.0
holeCenterX = 105.0
holeCenterY = 5.0
shaftCenterZ = 95.0

assert bodyWidth > 0, "infeasible: bodyWidth must be positive"
assert bodyDepth > 0, "infeasible: bodyDepth must be positive"
assert bodyHeight > 0, "infeasible: bodyHeight must be positive"
assert overallLength > bodyDepth, "infeasible: shaft must extend past the head"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert holeDiameter < bodyWidth, "infeasible: holeDiameter exceeds head width"
assert holeDiameter < bodyDepth, "infeasible: holeDiameter exceeds head depth"
assert shaftDiameter > 0, "infeasible: shaftDiameter must be positive"
assert shaftDiameter < bodyWidth, "infeasible: shaftDiameter exceeds head width"
assert shaftDiameter < bodyHeight, "infeasible: shaftDiameter exceeds head height"
assert filletRadius > 0, "infeasible: filletRadius must be positive"
assert filletRadius * 2 < bodyWidth, "infeasible: fillets consume the head width"
assert filletRadius * 2 < bodyDepth, "infeasible: fillets consume the head depth"
assert xMax > xMin, "infeasible: xMax must be greater than xMin"
assert zMax > zMin, "infeasible: zMax must be greater than zMin"
assert yMin + overallLength > yHead, "infeasible: shaft free end does not pass the head junction"
assert holeCenterY > yMin, "infeasible: bore centre left the head"

doc = FreeCAD.newDocument("fusion_01184_recon")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)

head_sketch = body.newObject("Sketcher::SketchObject", "HeadSketch")
head_sketch.AttachmentSupport = [(xy, "")]
head_sketch.MapMode = "FlatFace"
head_sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, zMin), FreeCAD.Rotation())
head_sketch.addGeometry(
    Part.LineSegment(FreeCAD.Vector(xMin, yMin, 0), FreeCAD.Vector(xMin + bodyWidth, yMin, 0)), False
)
head_sketch.addGeometry(
    Part.LineSegment(FreeCAD.Vector(xMin + bodyWidth, yMin, 0), FreeCAD.Vector(xMin + bodyWidth, yMin + bodyDepth, 0)),
    False,
)
head_sketch.addGeometry(
    Part.LineSegment(FreeCAD.Vector(xMin + bodyWidth, yMin + bodyDepth, 0), FreeCAD.Vector(xMin, yMin + bodyDepth, 0)),
    False,
)
head_sketch.addGeometry(
    Part.LineSegment(FreeCAD.Vector(xMin, yMin + bodyDepth, 0), FreeCAD.Vector(xMin, yMin, 0)), False
)
head_sketch.addConstraint(Sketcher.Constraint("Coincident", 0, 2, 1, 1))
head_sketch.addConstraint(Sketcher.Constraint("Coincident", 1, 2, 2, 1))
head_sketch.addConstraint(Sketcher.Constraint("Coincident", 2, 2, 3, 1))
head_sketch.addConstraint(Sketcher.Constraint("Coincident", 3, 2, 0, 1))
head_sketch.addConstraint(Sketcher.Constraint("Horizontal", 0))
head_sketch.addConstraint(Sketcher.Constraint("Horizontal", 2))
head_sketch.addConstraint(Sketcher.Constraint("Vertical", 1))
head_sketch.addConstraint(Sketcher.Constraint("Vertical", 3))
head_sketch.addConstraint(Sketcher.Constraint("DistanceX", 0, 1, 0, 2, bodyWidth))
head_sketch.addConstraint(Sketcher.Constraint("DistanceY", 0, 1, 3, 1, bodyDepth))
head_sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, xMin))
head_sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, yMin))

head = body.newObject("PartDesign::Pad", "Head")
head.Profile = head_sketch
head.Length = bodyHeight
doc.recompute()


def is_corner_edge(edge):
    if not isinstance(edge.Curve, Part.Line):
        return False
    a, b = edge.Vertexes[0].Point, edge.Vertexes[-1].Point
    if abs(a.x - b.x) > 1e-6 or abs(a.y - b.y) > 1e-6:
        return False
    on_x = min(abs(a.x - xMin), abs(a.x - (xMin + bodyWidth))) < 1e-6
    on_y = min(abs(a.y - yMin), abs(a.y - (yMin + bodyDepth))) < 1e-6
    return on_x and on_y


corner_edges = [f"Edge{i + 1}" for i, e in enumerate(head.Shape.Edges) if is_corner_edge(e)]
assert len(corner_edges) == 4, f"expected 4 vertical corner edges, found {len(corner_edges)}"

corner_fillets = body.newObject("PartDesign::Fillet", "CornerFillets")
corner_fillets.Base = (head, corner_edges)
corner_fillets.Radius = filletRadius
doc.recompute()

xz = next(f for f in body.Origin.OriginFeatures if "XZ" in f.Name and "Plane" in f.Name)
shaft_sketch = body.newObject("Sketcher::SketchObject", "ShaftSketch")
shaft_sketch.AttachmentSupport = [(xz, "")]
shaft_sketch.MapMode = "FlatFace"
# Start inside the head so the pin does not emerge at y = yMin; free end is yMin+overallLength.
# XZ local +z is −Y; negative offset places the sketch at y = holeCenterY.
shaft_sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, -holeCenterY), FreeCAD.Rotation())
shaft_gid = shaft_sketch.addGeometry(
    Part.Circle(FreeCAD.Vector(holeCenterX, shaftCenterZ, 0), FreeCAD.Vector(0, 0, 1), shaftDiameter / 2),
    False,
)
shaft_sketch.addConstraint(Sketcher.Constraint("Diameter", shaft_gid, shaftDiameter))
shaft_sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, shaft_gid, 3, holeCenterX))
shaft_sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, shaft_gid, 3, shaftCenterZ))

shaft = body.newObject("PartDesign::Pad", "Shaft")
shaft.Profile = shaft_sketch
shaft.Length = yMin + overallLength - holeCenterY
# XZ plane normal is -Y; reverse so the shaft occupies +y to the free end.
shaft.Reversed = True
doc.recompute()

bore_sketch = body.newObject("Sketcher::SketchObject", "BoreSketch")
bore_sketch.AttachmentSupport = [(xy, "")]
bore_sketch.MapMode = "FlatFace"
bore_sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, zMin), FreeCAD.Rotation())
bore_gid = bore_sketch.addGeometry(
    Part.Circle(FreeCAD.Vector(holeCenterX, holeCenterY, 0), FreeCAD.Vector(0, 0, 1), holeDiameter / 2),
    False,
)
bore_sketch.addConstraint(Sketcher.Constraint("Diameter", bore_gid, holeDiameter))
bore_sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, bore_gid, 3, holeCenterX))
bore_sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, bore_gid, 3, holeCenterY))

bore = body.newObject("PartDesign::Pocket", "Bore")
bore.Profile = bore_sketch
bore.Type = "ThroughAll"
# Sketch at zMin; reverse so the cut runs +z through the head.
bore.Reversed = True
bore.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
result = body
