import FreeCAD
import Part
import Sketcher

stepHeight = 12.7
channelWidth = 152.4
downstreamHeight = 114.3
upstreamHeight = 101.6
roofAngle = 0.0
upstreamLength = 1333.5
downstreamLength = 635.0
assert stepHeight > 0, "infeasible: stepHeight must be positive"
assert channelWidth > 0, "infeasible: channelWidth must be positive"
assert downstreamHeight > 0, "infeasible: downstreamHeight must be positive"
assert upstreamHeight > 0, "infeasible: upstreamHeight must be positive"
assert upstreamLength > 0, "infeasible: upstreamLength must be positive"
assert downstreamLength > 0, "infeasible: downstreamLength must be positive"
assert downstreamHeight > stepHeight, "infeasible: downstreamHeight must exceed stepHeight"
assert abs(roofAngle) <= 0.001, "infeasible: this model is the zero-divergence roof"

doc = FreeCAD.newDocument("nasa-backstep-driver-seegmiller")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xz = next(f for f in body.Origin.OriginFeatures if "XZ" in f.Name and "Plane" in f.Name)

# Sketch u = +x, v = +z. inlet, upstreamFloor, stepFace, downstreamFloor, outlet, roof.
pts = [
    (-upstreamLength, stepHeight),
    (0.0, stepHeight),
    (0.0, 0.0),
    (downstreamLength, 0.0),
    (downstreamLength, downstreamHeight),
    (-upstreamLength, downstreamHeight),
]
sketch = body.newObject("Sketcher::SketchObject", "FlowDomainSketch")
sketch.AttachmentSupport = [(xz, "")]
sketch.MapMode = "FlatFace"
n = len(pts)
for i in range(n):
    a, b = pts[i], pts[(i + 1) % n]
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(a[0], a[1], 0), FreeCAD.Vector(b[0], b[1], 0)), False)
for i in range(n):
    sketch.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % n, 1))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, i, 1, pts[i][0]))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, i, 1, pts[i][1]))

# Reference dimension only; roof stays at downstreamHeight when either height is rewritten.
gauge = sketch.addGeometry(
    Part.LineSegment(
        FreeCAD.Vector(-upstreamLength / 2.0, stepHeight, 0),
        FreeCAD.Vector(-upstreamLength / 2.0, stepHeight + upstreamHeight, 0),
    ),
    True,
)
sketch.addConstraint(Sketcher.Constraint("Vertical", gauge))
sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gauge, 1, -upstreamLength / 2.0))
sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gauge, 1, stepHeight))
sketch.addConstraint(Sketcher.Constraint("DistanceY", gauge, 1, gauge, 2, upstreamHeight))

pad = body.newObject("PartDesign::Pad", "FlowDomain")
pad.Profile = sketch
pad.Length = channelWidth
# Origin XZ normal is -Y; reverse so the air occupies y = 0 .. channelWidth.
pad.Reversed = True
pad.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"

# Meshing names (gates bind these on the STEP by plane, outward normal, area, centre).
flowBoundaryNames = (
    "inlet",
    "outlet",
    "roof",
    "upstreamFloor",
    "stepFace",
    "downstreamFloor",
    "sideWallY0",
    "sideWallYMax",
)
assert len(flowBoundaryNames) == 8, "infeasible: expected eight meshing faces"
result = body
