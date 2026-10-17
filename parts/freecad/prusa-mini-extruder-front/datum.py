"""Shared PartDesign envelope copied from the passed blockout, in millimetres.

Subsequent modules sculpt this pad and add the functional pockets and channels.
The XZ sketch and its parameter-driven vertex constraints preserve the datums.
"""

import FreeCAD
import Part
import Sketcher
from params import (
    bodyTopZ,
    bottomZ,
    halfWidth,
    leftFootTopZ,
    leftFootX,
    lowerLeftPilotDiameter,
    lugBossDiameter,
    lugMaxZ,
    lugNutX,
    lugWebPeakX,
    overallHeight,
    plateThickness,
    plateWidth,
    upperLeftPilotDiameter,
)

assert plateWidth > 0, "infeasible: plateWidth must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
assert halfWidth > 0, "infeasible: halfWidth must be positive"
assert lugBossDiameter > 0, "infeasible: lugBossDiameter must be positive"
assert upperLeftPilotDiameter > 0, "infeasible: upperLeftPilotDiameter must be positive"
assert lowerLeftPilotDiameter > 0, "infeasible: lowerLeftPilotDiameter must be positive"
assert bottomZ < leftFootTopZ < bodyTopZ < lugMaxZ, "infeasible: envelope levels must be ordered"
assert -halfWidth < leftFootX < halfWidth, "infeasible: foot must lie inside the plate width"

lugLeftX = lugNutX - lugBossDiameter / 2.0
assert -halfWidth < lugLeftX < lugWebPeakX < halfWidth, "infeasible: lug/web must lie inside the plate width"

doc = FreeCAD.newDocument("PrusaMiniExtruderFrontDatum")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xz = next(f for f in body.Origin.OriginFeatures if "XZ" in f.Name and "Plane" in f.Name)

# XZ sketch: u = +x, v = +z, normal = -y. Square envelope steps only;
# the lower foot and upper lug/web allowance are part of this primary profile.
pts = [
    (leftFootX, bottomZ),
    (halfWidth, bottomZ),
    (halfWidth, bodyTopZ),
    (lugWebPeakX, bodyTopZ),
    (lugWebPeakX, lugMaxZ),
    (lugLeftX, lugMaxZ),
    (lugLeftX, bodyTopZ),
    (-halfWidth, bodyTopZ),
    (-halfWidth, leftFootTopZ),
    (leftFootX, leftFootTopZ),
]
sketch = body.newObject("Sketcher::SketchObject", "EnvelopeSketch")
sketch.AttachmentSupport = [(xz, "")]
sketch.MapMode = "FlatFace"
n = len(pts)
for i in range(n):
    a, b = pts[i], pts[(i + 1) % n]
    sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(a[0], a[1], 0), FreeCAD.Vector(b[0], b[1], 0)), False)
for i in range(n):
    sketch.addConstraint(Sketcher.Constraint("Coincident", i, 2, (i + 1) % n, 1))
    # Pin every vertex to the sketch origin with parameter-driven dimensions.
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, i, 1, pts[i][0]))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, i, 1, pts[i][1]))
doc.recompute()
assert sketch.isValid(), "kernel: envelope sketch is invalid after recompute"
assert sketch.FullyConstrained, "sketch: envelope must have zero remaining degrees of freedom"

pad = body.newObject("PartDesign::Pad", "HousingEnvelope")
pad.Profile = sketch
pad.Length = plateThickness
pad.Reversed = True  # Extrude from the back datum y=0 toward the front datum y=14.
pad.Refine = True
doc.recompute()
for feature in (sketch, pad, body):
    assert feature.isValid(), "kernel: invalid feature " + feature.Name
assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
assert len(body.Shape.Solids) == 1, "kernel: envelope must be one connected solid"
datum = body
