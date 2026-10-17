"""Four roof attachment bores, cut as one family in the upper shell only."""

import FreeCAD
import Part
import Sketcher
from params import (
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    mountHoleDiameter,
    mountXHigh,
    mountXLow,
    mountYHigh,
    mountYLow,
    roofBottom,
    roofThickness,
)


def apply(body):
    """Return the original (upperShell, bottomCover) after one roof-only Pocket."""
    assert isinstance(body, tuple) and len(body) == 2, "topMounts requires (upperShell, bottomCover)"
    upper_shell, bottom_cover = body
    doc = upper_shell.Document
    assert bottom_cover.Document is doc, "topMounts bodies must share a document"

    overrun = 0.02
    radius = mountHoleDiameter / 2.0
    roof_top = roofBottom + roofThickness
    centers = (
        (mountXLow, mountYLow),
        (mountXHigh, mountYLow),
        (mountXHigh, mountYHigh),
        (mountXLow, mountYHigh),
    )
    assert roofThickness > 0.0, "infeasible: roofThickness must be positive"
    assert radius > 0.0, "infeasible: mountHoleDiameter must be positive"
    assert mountXHigh - mountXLow > mountHoleDiameter, "infeasible: left and right bores must remain separate"
    assert mountYHigh - mountYLow > mountHoleDiameter, "infeasible: front and rear bores must remain separate"
    for x, y in centers:
        clearance = min(
            x - radius - innerXMin,
            innerXMax - x - radius,
            y - radius - innerYMin,
            innerYMax - y - radius,
        )
        assert clearance >= 0.1, "infeasible: roof bore tools must remain clear of the cavity walls"

    previous_tip = upper_shell.Tip
    cover_tip = bottom_cover.Tip
    xy_plane = next(item for item in upper_shell.Origin.OriginFeatures if item.Name.startswith("XY_Plane"))
    plane = upper_shell.newObject("PartDesign::Plane", "TopStandoffBoresPlane")
    plane.AttachmentSupport = [(xy_plane, "")]
    plane.MapMode = "FlatFace"
    plane.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, roof_top + overrun), FreeCAD.Rotation())
    doc.recompute()
    assert plane.isValid(), "roof bore plane must be valid"

    profile = upper_shell.newObject("Sketcher::SketchObject", "TopStandoffBoresProfile")
    profile.AttachmentSupport = [(plane, "")]
    profile.MapMode = "FlatFace"
    for x, y in centers:
        index = profile.addGeometry(
            Part.Circle(FreeCAD.Vector(x, y, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), radius), False
        )
        profile.addConstraint(Sketcher.Constraint("Diameter", index, mountHoleDiameter))
        profile.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, index, 3, x))
        profile.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, index, 3, y))
    doc.recompute()
    assert profile.isValid(), "roof bore profile must be valid"
    assert profile.FullyConstrained, "roof bore profile must be fully constrained"

    # The four disjoint profiles form one Pocket tool. Both ends overrun into
    # air by 0.02 mm; material is removed only from roofBottom..roof_top.
    pocket = upper_shell.newObject("PartDesign::Pocket", "TopStandoffBores")
    pocket.Profile = profile
    pocket.Length = roofThickness + 2.0 * overrun
    pocket.Reversed = False
    pocket.Refine = True
    upper_shell.Tip = pocket
    previous_tip.Visibility = False
    plane.Visibility = False
    profile.Visibility = False
    doc.recompute()

    assert pocket.isValid() and pocket.Shape.isValid(), "roof bore Pocket must be valid"
    assert bottom_cover.Tip is cover_tip, "topMounts must preserve the bottom-cover feature history"
    for current_body in body:
        assert current_body.isValid() and current_body.Shape.isValid(), current_body.Name + " must remain valid"
        assert len(current_body.Shape.Solids) == 1, current_body.Name + " must remain one connected solid"
        for feature in current_body.Group:
            assert feature.isValid(), feature.Name + " must remain valid after topMounts"
    return body
