"""Bounded service windows in the upper shell's three connector walls."""

import FreeCAD
import Part
import Sketcher
from params import (
    baseBoardThickness,
    carrierBottom,
    carrierTop,
    innerXMax,
    innerYMax,
    innerYMin,
    portMargin,
    wallThickness,
)


def _rectangle(low_u, high_u, low_z, high_z):
    assert low_u < high_u and low_z < high_z, "infeasible: service window must have positive spans"
    return [(low_u, low_z), (high_u, low_z), (high_u, high_z), (low_u, high_z)]


def _constrained_outline(sketch, points):
    """Dimension each orthogonal edge's position, including repeated levels."""
    first = sketch.GeometryCount
    count = len(points)
    for index, (u, z) in enumerate(points):
        next_u, next_z = points[(index + 1) % count]
        horizontal = abs(z - next_z) < 1e-9
        vertical = abs(u - next_u) < 1e-9
        assert horizontal != vertical, "infeasible: service outline edges must be nonzero and orthogonal"
        edge = sketch.addGeometry(
            Part.LineSegment(FreeCAD.Vector(u, z, 0.0), FreeCAD.Vector(next_u, next_z, 0.0)), False
        )
        sketch.addConstraint(Sketcher.Constraint("Horizontal" if horizontal else "Vertical", edge))
        sketch.addConstraint(
            Sketcher.Constraint("DistanceY" if horizontal else "DistanceX", -1, 1, edge, 1, z if horizontal else u)
        )
    for index in range(count):
        sketch.addConstraint(Sketcher.Constraint("Coincident", first + index, 2, first + (index + 1) % count, 1))


def _wall_pocket(shell, name, origin, rotation, outlines, depth):
    """Make the complete family tool in one sketch before one bounded Pocket."""
    doc = shell.Document
    previous_tip = shell.Tip
    xy_plane = next(item for item in shell.Origin.OriginFeatures if item.Name.startswith("XY_Plane"))
    plane = shell.newObject("PartDesign::Plane", name + "Plane")
    plane.AttachmentSupport = [(xy_plane, "")]
    plane.MapMode = "FlatFace"
    plane.AttachmentOffset = FreeCAD.Placement(origin, rotation)
    doc.recompute()
    assert plane.isValid(), name + " plane must be valid"

    profile = shell.newObject("Sketcher::SketchObject", name + "Profile")
    profile.AttachmentSupport = [(plane, "")]
    profile.MapMode = "FlatFace"
    for outline in outlines:
        _constrained_outline(profile, outline)
    doc.recompute()
    assert profile.isValid() and profile.FullyConstrained, name + " profile must be valid and fully constrained"

    pocket = shell.newObject("PartDesign::Pocket", name)
    pocket.Profile = profile
    pocket.Length = depth
    pocket.Reversed = False
    pocket.Refine = True
    shell.Tip = pocket
    doc.recompute()
    assert pocket.isValid() and pocket.Shape.isValid(), name + " Pocket must be valid"
    assert shell.isValid() and shell.Shape.isValid(), name + " shell must be valid"
    assert len(shell.Shape.Solids) == 1, name + " must retain one connected shell"
    previous_tip.Visibility = False
    plane.Visibility = False
    profile.Visibility = False


def apply(body):
    """Cut only upperShell and preserve the caller's (upperShell, bottomCover)."""
    assert isinstance(body, tuple) and len(body) == 2, "servicePorts requires (upperShell, bottomCover)"
    upper_shell, bottom_cover = body
    doc = upper_shell.Document
    assert bottom_cover.Document is doc, "servicePorts bodies must share a document"
    assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
    assert portMargin > 0.0, "infeasible: portMargin must be positive"
    assert baseBoardThickness > 0.0, "infeasible: baseBoardThickness must be positive"
    assert carrierTop > carrierBottom, "infeasible: carrier top must be above its underside"

    # These projections already include the nominal 1.5 mm allowance. Base
    # components follow the base PCB top; lower/upper carrier components follow
    # their respective mounting faces. No second nominal margin is added.
    dm = portMargin - 1.5
    base_shift = baseBoardThickness - 1.56
    carrier_lower_shift = carrierBottom - 11.56
    carrier_upper_shift = carrierTop - 13.13
    low_z = 0.06 + base_shift - dm
    header_top = 7.48 + base_shift + dm
    j9_low = 6.95 + carrier_lower_shift - dm
    j8_low = 6.69 + carrier_lower_shift - dm
    carrier_front_top = 13.06 + carrier_lower_shift + dm
    power_top = 17.74 + carrier_upper_shift + dm
    side_usb_top = 6.44 + base_shift + dm

    rear_left, rear_right = 6.58 - dm, 74.83 + dm
    front_left, front_right = 30.23 - dm, 76.68 + dm
    j9_left, j9_right = 40.66 - dm, 52.40 + dm
    j8_left, j8_right = 60.81 - dm, 72.75 + dm
    assert low_z < min(j9_low, j8_low), "infeasible: carrier windows must rise above the base window floor"
    assert max(j9_low, j8_low) < header_top < carrier_front_top, "infeasible: front windows must form one union"
    assert front_left < j9_left < j9_right < j8_left < j8_right < front_right, "infeasible: retain the front webs"
    assert power_top > header_top, "infeasible: merged power window must reach the upper carrier port"
    assert 18.21 + dm < 34.93 - dm, "infeasible: right service windows must remain separate"

    stock = upper_shell.Shape.BoundBox
    assert stock.ZMin + 0.1 < low_z, "infeasible: service windows must retain the shell's lower rim"
    assert max(power_top, carrier_front_top) <= 23.52 - 2.10, "infeasible: service tools approach thermal keep-outs"
    assert stock.XMin + 0.1 < rear_left < rear_right < innerXMax - 0.1, "infeasible: rear window reaches a corner"
    assert stock.XMin + 0.1 < front_left < front_right < innerXMax - 0.1, "infeasible: front window reaches a corner"
    assert innerYMin + 0.1 < 5.15 - dm < 46.87 + dm < innerYMax - 0.1, "infeasible: right windows reach a corner"

    overrun = 0.02
    depth = wallThickness + 2.0 * overrun
    # Local (u,z) = world (x,z); the sketch normal is -y, so a normal
    # Pocket cuts +y. Both ends overrun the wall by exactly 0.02 mm.
    xz_rotation = FreeCAD.Rotation(FreeCAD.Vector(1.0, 0.0, 0.0), 90.0)
    _wall_pocket(
        upper_shell,
        "RearHeaderWindow",
        FreeCAD.Vector(0.0, innerYMax - overrun, 0.0),
        xz_rotation,
        [_rectangle(rear_left, rear_right, low_z, header_top)],
        depth,
    )

    # This is the union boundary of the lower header/base-USB rectangle and
    # both overlapping carrier windows. The 8.41 mm nominal middle web remains.
    front_outline = [
        (front_left, low_z),
        (front_right, low_z),
        (front_right, header_top),
        (j8_right, header_top),
        (j8_right, carrier_front_top),
        (j8_left, carrier_front_top),
        (j8_left, header_top),
        (j9_right, header_top),
        (j9_right, carrier_front_top),
        (j9_left, carrier_front_top),
        (j9_left, header_top),
        (front_left, header_top),
    ]
    _wall_pocket(
        upper_shell,
        "FrontHeaderAndUsbWindows",
        FreeCAD.Vector(0.0, innerYMin - wallThickness - overrun, 0.0),
        xz_rotation,
        [front_outline],
        depth,
    )

    # Local (u,z) = world (y,z), normal +x: one inward Pocket uses both
    # profiles. The power/J10 profile is merged through its full height.
    yz_rotation = FreeCAD.Rotation(FreeCAD.Vector(1.0, 1.0, 1.0), 120.0)
    _wall_pocket(
        upper_shell,
        "PowerAndBaseSideUsbWindows",
        FreeCAD.Vector(innerXMax + wallThickness + overrun, 0.0, 0.0),
        yz_rotation,
        [
            _rectangle(5.15 - dm, 18.21 + dm, low_z, power_top),
            _rectangle(34.93 - dm, 46.87 + dm, low_z, side_usb_top),
        ],
        depth,
    )
    doc.recompute()
    assert bottom_cover.isValid() and bottom_cover.Shape.isValid(), "bottom cover must remain valid"
    assert len(bottom_cover.Shape.Solids) == 1, "bottom cover must remain a separate solid"
    return body
