"""Four integral bottom-cover compression pads with one closure-bore family."""

import FreeCAD
import Part
import Sketcher
from params import (
    basePadDiameter,
    floorThickness,
    floorTop,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    mountHoleDiameter,
    mountXHigh,
    mountXLow,
    mountYHigh,
    mountYLow,
)


def _circle_family(body, name, z, centers, diameter):
    """Constrain all four circles on a named plane attached to the body origin."""
    doc = body.Document
    xy_plane = next(item for item in body.Origin.OriginFeatures if item.Name.startswith("XY_Plane"))
    plane = body.newObject("PartDesign::Plane", name + "Plane")
    plane.AttachmentSupport = [(xy_plane, "")]
    plane.MapMode = "FlatFace"
    plane.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, z), FreeCAD.Rotation())
    doc.recompute()
    assert plane.isValid(), name + " plane must be valid"

    sketch = body.newObject("Sketcher::SketchObject", name + "Profile")
    sketch.AttachmentSupport = [(plane, "")]
    sketch.MapMode = "FlatFace"
    for x, y in centers:
        index = sketch.addGeometry(
            Part.Circle(FreeCAD.Vector(x, y, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), diameter / 2.0), False
        )
        sketch.addConstraint(Sketcher.Constraint("Diameter", index, diameter))
        sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, index, 3, x))
        sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, index, 3, y))
    doc.recompute()
    assert sketch.isValid(), name + " profile must be valid"
    assert sketch.FullyConstrained, name + " profile must be fully constrained"
    plane.Visibility = False
    return sketch


def apply(body):
    """Modify bottomCover only, preserving the supplied (upperShell, bottomCover)."""
    assert isinstance(body, tuple) and len(body) == 2, "lowerMounts requires (upperShell, bottomCover)"
    upper_shell, bottom_cover = body
    doc = bottom_cover.Document
    assert upper_shell.Document is doc, "lowerMounts bodies must share a document"

    seat_z = 0.0  # Fixed assembly datum: underside of the base PCB.
    overrun = 0.02
    cover_bottom = floorTop - floorThickness
    pad_radius = basePadDiameter / 2.0
    bore_radius = mountHoleDiameter / 2.0
    centers = (
        (mountXLow, mountYLow),
        (mountXHigh, mountYLow),
        (mountXHigh, mountYHigh),
        (mountXLow, mountYHigh),
    )
    assert floorThickness > overrun, "infeasible: floor must contain the pad attachment overlap"
    assert floorTop < seat_z, "infeasible: compression pads need positive height below the fixed PCB datum"
    assert pad_radius > bore_radius > 0.0, "infeasible: closure bores must fit within positive-diameter pads"
    assert pad_radius - bore_radius >= 2.0, "infeasible: lower pad radial ligament must be at least 2 mm"
    assert mountXHigh - mountXLow > basePadDiameter, "infeasible: left and right pads must remain separate"
    assert mountYHigh - mountYLow > basePadDiameter, "infeasible: front and rear pads must remain separate"
    for x, y in centers:
        clearance = min(
            x - pad_radius - innerXMin,
            innerXMax - x - pad_radius,
            y - pad_radius - innerYMin,
            innerYMax - y - pad_radius,
        )
        assert clearance >= 0.1, "infeasible: lower pads must stay clear of the upper-shell cavity walls"

    previous_tip = bottom_cover.Tip
    # Overlap existing floor stock by 0.02 mm; added material starts at floorTop.
    pad_profile = _circle_family(bottom_cover, "LowerSupportPads", floorTop - overrun, centers, basePadDiameter)
    pads = bottom_cover.newObject("PartDesign::Pad", "LowerSupportPads")
    pads.Profile = pad_profile
    pads.Length = seat_z - floorTop + overrun
    pads.Reversed = False
    pads.Refine = True
    bottom_cover.Tip = pads
    previous_tip.Visibility = False
    pad_profile.Visibility = False
    doc.recompute()
    assert pads.isValid() and pads.Shape.isValid(), "lower support Pad must be valid"
    assert len(pads.Shape.Solids) == 1, "lower support pads must join the single bottom-cover solid"

    # The four complete profiles form one cutting family and one Pocket. Both
    # ends extend into air, from 0.02 above the seats to 0.02 below the slab.
    bore_profile = _circle_family(bottom_cover, "BottomClosureBores", seat_z + overrun, centers, mountHoleDiameter)
    bores = bottom_cover.newObject("PartDesign::Pocket", "BottomClosureBores")
    bores.Profile = bore_profile
    bores.Length = seat_z - cover_bottom + 2.0 * overrun
    bores.Reversed = False
    bores.Refine = True
    bottom_cover.Tip = bores
    pads.Visibility = False
    bore_profile.Visibility = False
    doc.recompute()

    assert bores.isValid() and bores.Shape.isValid(), "bottom closure Pocket must be valid"
    assert bottom_cover.isValid() and bottom_cover.Shape.isValid(), "bottom cover must be valid"
    assert len(bottom_cover.Shape.Solids) == 1, "bottom cover must remain one connected solid"
    for feature in bottom_cover.Group:
        assert feature.isValid(), feature.Name + " must remain valid after lowerMounts"
    assert upper_shell.isValid() and upper_shell.Shape.isValid(), "upper shell must remain valid"
    return body
