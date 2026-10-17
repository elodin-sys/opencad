"""Roof heat aperture and lower exhaust windows in the upper shell only."""

import FreeCAD
import Part
import Sketcher
from params import (
    heatsinkBottom,
    heatsinkCenterX,
    heatsinkCenterY,
    heatsinkLength,
    heatsinkMargin,
    heatsinkWidth,
    innerXMax,
    innerXMin,
    roofBottom,
    roofThickness,
    wallThickness,
)


def _rectangles_on_plane(body, name, support_prefix, offset, rectangles):
    """Fully constrained profiles on an offset named origin plane."""
    doc = body.Document
    support = next(item for item in body.Origin.OriginFeatures if item.Name.startswith(support_prefix))
    plane = body.newObject("PartDesign::Plane", name + "Plane")
    plane.AttachmentSupport = [(support, "")]
    plane.MapMode = "FlatFace"
    plane.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, offset), FreeCAD.Rotation())
    doc.recompute()
    assert plane.isValid(), name + " plane must be valid"

    sketch = body.newObject("Sketcher::SketchObject", name + "Profile")
    sketch.AttachmentSupport = [(plane, "")]
    sketch.MapMode = "FlatFace"
    for u_min, u_max, v_min, v_max in rectangles:
        first = sketch.GeometryCount
        corners = [(u_min, v_min), (u_max, v_min), (u_max, v_max), (u_min, v_max)]
        for index, (u, v) in enumerate(corners):
            next_u, next_v = corners[(index + 1) % 4]
            sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(u, v, 0.0), FreeCAD.Vector(next_u, next_v, 0.0)), False)
            sketch.addConstraint(Sketcher.Constraint("Horizontal" if index % 2 == 0 else "Vertical", first + index))
        for index in range(4):
            sketch.addConstraint(Sketcher.Constraint("Coincident", first + index, 2, first + (index + 1) % 4, 1))
        sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, first, 1, u_min))
        sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, first, 1, v_min))
        sketch.addConstraint(Sketcher.Constraint("Distance", first, u_max - u_min))
        sketch.addConstraint(Sketcher.Constraint("Distance", first + 1, v_max - v_min))
    doc.recompute()
    assert sketch.isValid(), name + " profile must be valid"
    assert sketch.FullyConstrained, name + " profile must be fully constrained"
    plane.Visibility = False
    return sketch


def _pocket(body, name, profile, depth, previous_tip):
    """Subtract one batched sketch tool for a complete cut family."""
    pocket = body.newObject("PartDesign::Pocket", name)
    pocket.Profile = profile
    pocket.Length = depth
    pocket.Reversed = False
    pocket.Refine = True
    body.Tip = pocket
    previous_tip.Visibility = False
    profile.Visibility = False
    body.Document.recompute()
    assert pocket.isValid() and pocket.Shape.isValid(), name + " must be valid"
    assert len(pocket.Shape.Solids) == 1, name + " must retain one connected upper shell"
    return pocket


def apply(body):
    """Cut both thermal families, preserving the input Body or body tuple."""
    upper_shell = body[0] if isinstance(body, tuple) else body
    doc = upper_shell.Document
    assert 3.5 <= heatsinkMargin <= 4.5, "infeasible: heatsinkMargin must lie in 3.5..4.5 mm"
    assert 2.8 <= wallThickness <= 4.0, "infeasible: wallThickness must lie in 2.8..4.0 mm"
    assert heatsinkLength > 0.0 and heatsinkWidth > 0.0, "infeasible: heatsink footprint must be positive"
    assert roofThickness > 0.0, "infeasible: roofThickness must be positive"
    assert roofBottom > heatsinkBottom, "infeasible: the exhaust must have positive height"

    # The heatOpening* literals are nominal witnesses, not driving dimensions.
    # In particular, editing heatsinkMargin regenerates all four aperture edges.
    opening_length = heatsinkLength + 2.0 * heatsinkMargin
    opening_width = heatsinkWidth + 2.0 * heatsinkMargin
    opening_x_min = heatsinkCenterX - opening_length / 2.0
    opening_x_max = heatsinkCenterX + opening_length / 2.0
    opening_y_min = heatsinkCenterY - opening_width / 2.0
    opening_y_max = heatsinkCenterY + opening_width / 2.0
    working_roof_top = roofBottom + roofThickness
    overrun = 0.02

    assert innerXMin < opening_x_min < opening_x_max < innerXMax, "infeasible: aperture must remain inside the x walls"
    previous_tip = upper_shell.Tip
    roof_profile = _rectangles_on_plane(
        upper_shell,
        "RoofHeatAperture",
        "XY_Plane",
        working_roof_top + overrun,
        [(opening_x_min, opening_x_max, opening_y_min, opening_y_max)],
    )
    roof_pocket = _pocket(upper_shell, "HeatsinkAperture", roof_profile, roofThickness + 2.0 * overrun, previous_tip)

    # The fixed 1.5 mm allowance belongs to heatsink size/centering uncertainty.
    # It is independent of both portMargin and the editable roof margin.
    uncertainty_allowance = 1.5
    exhaust_y_min = heatsinkCenterY - heatsinkWidth / 2.0 - uncertainty_allowance
    exhaust_y_max = heatsinkCenterY + heatsinkWidth / 2.0 + uncertainty_allowance
    outer_x_min = innerXMin - wallThickness
    outer_x_max = innerXMax + wallThickness

    # Two disjoint XY profiles form one Pocket tool restricted to the walls.
    # A transverse tool through the intervening air would approach the top-bore
    # keep-out probes within 1.6 mm, less than the required 2.10 mm tool clearance.
    # Overrun the inner and outer x faces into air, but keep the z limits exact:
    # the shared roof underside must not be overcut by an upward z allowance.
    exhaust_profile = _rectangles_on_plane(
        upper_shell,
        "SideExhaustWindows",
        "XY_Plane",
        roofBottom,
        [
            (outer_x_min - overrun, innerXMin + overrun, exhaust_y_min, exhaust_y_max),
            (innerXMax - overrun, outer_x_max + overrun, exhaust_y_min, exhaust_y_max),
        ],
    )
    _pocket(
        upper_shell,
        "SideExhaustWindows",
        exhaust_profile,
        roofBottom - heatsinkBottom,
        roof_pocket,
    )
    doc.recompute()
    for feature in upper_shell.Group:
        assert feature.isValid(), feature.Name + " must remain valid"
    assert upper_shell.isValid() and upper_shell.Shape.isValid(), "thermal vent upper shell must be valid"
    return body
