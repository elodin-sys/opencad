"""Two envelope pads in the Aleph assembly frame, adapted from the passed blockout.

Feature modules receive (upperShell, bottomCover), modify only their assigned
material, and return the same tuple. No stack hardware belongs to these bodies.
"""

import FreeCAD
import Part
import Sketcher
from params import (
    floorThickness,
    floorTop,
    heatsinkMargin,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    roofBottom,
    roofThickness,
    seamGap,
    wallThickness,
)

# params.py preserves every contract value as a literal. Derive geometry here
# from independent controls so a wall edit moves only the outer x/y planes.
stock_x_min = innerXMin - wallThickness
stock_x_max = innerXMax + wallThickness
stock_y_min = innerYMin - wallThickness
stock_y_max = innerYMax + wallThickness
stock_length = stock_x_max - stock_x_min
stock_width = stock_y_max - stock_y_min
cover_bottom = floorTop - floorThickness
cap_bottom = floorTop + seamGap
cap_top = roofBottom + roofThickness

assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
assert heatsinkMargin > 0.0, "infeasible: heatsinkMargin must be positive"
assert roofThickness > 0.0, "infeasible: roofThickness must be positive"
assert floorThickness > 0.0, "infeasible: floorThickness must be positive"
assert seamGap > 0.0, "infeasible: seamGap must separate the two bodies"
assert innerXMax > innerXMin and innerYMax > innerYMin, "infeasible: cavity spans must be positive"
assert stock_length > 0.0 and stock_width > 0.0, "infeasible: envelope footprint must be positive"
assert cover_bottom < floorTop < cap_bottom < roofBottom < cap_top, "infeasible: case height planes are out of order"

doc = FreeCAD.newDocument("AlephStackCaseDatum")


def envelope_body(name, z_bottom, z_top):
    """Pad one fully constrained rectangle upward from its named XY plane."""
    assert z_top > z_bottom, "infeasible: envelope pad height must be positive"
    body = doc.addObject("PartDesign::Body", name)
    xy_plane = next(item for item in body.Origin.OriginFeatures if item.Name.startswith("XY_Plane"))
    sketch = body.newObject("Sketcher::SketchObject", name + "Outline")
    sketch.AttachmentSupport = [(xy_plane, "")]
    sketch.MapMode = "FlatFace"
    sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, z_bottom), FreeCAD.Rotation())

    corners = [
        (stock_x_min, stock_y_min),
        (stock_x_max, stock_y_min),
        (stock_x_max, stock_y_max),
        (stock_x_min, stock_y_max),
    ]
    for index, (x, y) in enumerate(corners):
        x_next, y_next = corners[(index + 1) % 4]
        sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(x, y, 0.0), FreeCAD.Vector(x_next, y_next, 0.0)), False)
        sketch.addConstraint(Sketcher.Constraint("Horizontal" if index % 2 == 0 else "Vertical", index))
    for index in range(4):
        sketch.addConstraint(Sketcher.Constraint("Coincident", index, 2, (index + 1) % 4, 1))
    sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, stock_x_min))
    sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, stock_y_min))
    sketch.addConstraint(Sketcher.Constraint("Distance", 0, stock_length))
    sketch.addConstraint(Sketcher.Constraint("Distance", 1, stock_width))
    doc.recompute()
    assert sketch.isValid(), name + " outline must be valid"
    assert sketch.FullyConstrained, name + " outline must be fully constrained"

    pad = body.newObject("PartDesign::Pad", name + "Envelope")
    pad.Profile = sketch
    pad.Length = z_top - z_bottom
    pad.Refine = True
    body.Tip = pad
    sketch.Visibility = False
    doc.recompute()
    assert pad.isValid() and pad.Shape.isValid(), name + " pad must be valid"
    assert body.isValid() and body.Shape.isValid(), name + " body must be valid"
    assert len(body.Shape.Solids) == 1, name + " must contain exactly one solid"
    return body


upperShell = envelope_body("upperShell", cap_bottom, cap_top)
bottomCover = envelope_body("bottomCover", cover_bottom, floorTop)
doc.recompute()
datum = (upperShell, bottomCover)
