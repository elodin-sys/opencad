"""Bottom-open cavity in the cap; the separate bottom cover is untouched."""

import FreeCAD
import Part
import Sketcher
from params import (
    floorTop,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    roofBottom,
    seamGap,
)


def apply(body):
    """Remove one rectangular cavity from upperShell and return the input tuple."""
    assert isinstance(body, tuple) and len(body) == 2, "shellCavity requires (upperShell, bottomCover)"
    upper_shell, bottom_cover = body
    doc = upper_shell.Document
    assert bottom_cover.Document is doc, "shellCavity bodies must share a document"

    cavity_length = innerXMax - innerXMin
    cavity_width = innerYMax - innerYMin
    cap_bottom = floorTop + seamGap
    overrun = 0.02
    assert cavity_length > 0.0 and cavity_width > 0.0, "infeasible: cavity spans must be positive"
    assert seamGap > overrun, "infeasible: cavity overrun must remain in the seam air"
    assert roofBottom > cap_bottom, "infeasible: cavity ceiling must be above the cap rim"

    stock = upper_shell.Shape.BoundBox
    assert stock.XMin < innerXMin < innerXMax < stock.XMax, "infeasible: cavity must retain both x walls"
    assert stock.YMin < innerYMin < innerYMax < stock.YMax, "infeasible: cavity must retain both y walls"
    assert stock.ZMin < roofBottom < stock.ZMax, "infeasible: cavity must retain a roof"

    previous_tip = upper_shell.Tip
    xy_plane = next(item for item in upper_shell.Origin.OriginFeatures if item.Name.startswith("XY_Plane"))
    ceiling = upper_shell.newObject("PartDesign::Plane", "ShellCavityCeilingPlane")
    ceiling.AttachmentSupport = [(xy_plane, "")]
    ceiling.MapMode = "FlatFace"
    ceiling.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, roofBottom), FreeCAD.Rotation())
    doc.recompute()
    assert ceiling.isValid(), "shell cavity ceiling plane must be valid"

    profile = upper_shell.newObject("Sketcher::SketchObject", "ShellCavityProfile")
    profile.AttachmentSupport = [(ceiling, "")]
    profile.MapMode = "FlatFace"
    corners = [
        (innerXMin, innerYMin),
        (innerXMax, innerYMin),
        (innerXMax, innerYMax),
        (innerXMin, innerYMax),
    ]
    for index, (x, y) in enumerate(corners):
        x_next, y_next = corners[(index + 1) % 4]
        profile.addGeometry(Part.LineSegment(FreeCAD.Vector(x, y, 0.0), FreeCAD.Vector(x_next, y_next, 0.0)), False)
        profile.addConstraint(Sketcher.Constraint("Horizontal" if index % 2 == 0 else "Vertical", index))
    for index in range(4):
        profile.addConstraint(Sketcher.Constraint("Coincident", index, 2, (index + 1) % 4, 1))
    profile.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, 0, 1, innerXMin))
    profile.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, 0, 1, innerYMin))
    profile.addConstraint(Sketcher.Constraint("Distance", 0, cavity_length))
    profile.addConstraint(Sketcher.Constraint("Distance", 1, cavity_width))
    doc.recompute()
    assert profile.isValid(), "shell cavity profile must be valid"
    assert profile.FullyConstrained, "shell cavity profile must be fully constrained"

    # One connected profile makes one tool. The blind ceiling is exact; only
    # the open end overruns the stock, stopping inside the air above the cover.
    cavity = upper_shell.newObject("PartDesign::Pocket", "ShellCavityPocket")
    cavity.Profile = profile
    cavity.Length = roofBottom - cap_bottom + overrun
    cavity.Reversed = False
    cavity.Refine = True
    upper_shell.Tip = cavity
    previous_tip.Visibility = False
    profile.Visibility = False
    ceiling.Visibility = False
    doc.recompute()

    assert cavity.isValid() and cavity.Shape.isValid(), "shell cavity Pocket must be valid"
    assert upper_shell.isValid() and upper_shell.Shape.isValid(), "upper shell must be valid"
    assert len(upper_shell.Shape.Solids) == 1, "upper shell must remain one connected solid"
    assert bottom_cover.isValid() and bottom_cover.Shape.isValid(), "bottom cover must remain valid"
    assert len(bottom_cover.Shape.Solids) == 1, "bottom cover must remain a separate solid"
    return body
