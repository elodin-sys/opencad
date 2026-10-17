"""Eight fastener stacks, fused as one PartDesign tool before one subtraction.

All profiles attach to the named XZ plane. The two printable support layers
are clipped cavity / square, followed by the pilot; only pivot mouths taper.
The long square bridges deliberately do not follow either editable pilot.
"""

import math

import FreeCAD
import Part
import Sketcher
from params import (
    bridgeLayerHeight,
    counterboreDiameter,
    halfWidth,
    leftNutX,
    leftNutZ,
    leftPivotX,
    longCounterboreEnd,
    longCounterboreFullDepth,
    longPilotLength,
    longPilotStart,
    lowerLeftPilotDiameter,
    lowerLeftScrewX,
    lowerLeftScrewZ,
    lowerNutX,
    lowerNutZ,
    lugNutX,
    lugNutZ,
    nutAcrossFlats,
    nutCornerRadius,
    nutFullDepth,
    nutLeftFlatX,
    nutPilotStart,
    nutRectEnd,
    nutRightFlatX,
    pivotCounterboreStart,
    pivotMouthDiameter,
    pivotPilotEnd,
    plateThickness,
    rightCounterboreEnd,
    rightCounterboreFullDepth,
    rightPilotStart,
    rightPivotX,
    screwDiameter,
    upperLeftPilotDiameter,
    upperLeftScrewX,
    upperLeftScrewZ,
    upperRightScrewX,
    upperRightScrewZ,
)

_OVERRUN = 0.02
_LONG_BRIDGE_WIDTH = 3.5
_REGION_MIN = (-26.5, 0.0, -23.25)
_REGION_MAX = (23.25, 14.0, 31.25)


def _check(body, *features):
    body.Document.recompute()
    for feature in features:
        assert feature.isValid(), "kernel: invalid fastener feature " + feature.Name
        if feature.TypeId == "Sketcher::SketchObject":
            assert feature.FullyConstrained, "sketch: fastener profile is underconstrained: " + feature.Name
        else:
            assert not feature.Shape.isNull(), "kernel: null fastener feature " + feature.Name
            assert feature.Shape.isValid(), "kernel: invalid fastener shape " + feature.Name


def _sketch(body, name, y):
    plane = next(obj for obj in body.Origin.OriginFeatures if "XZ" in obj.Name and "Plane" in obj.Name)
    sketch = body.newObject("Sketcher::SketchObject", name)
    sketch.AttachmentSupport = [(plane, "")]
    sketch.MapMode = "FlatFace"
    # XZ has normal -y and sketch coordinates (x, z).
    sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, -y), FreeCAD.Rotation())
    return sketch


def _point_constraints(sketch, index, point_number, x, z):
    if x:
        sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, index, point_number, x))
    else:
        sketch.addConstraint(Sketcher.Constraint("Vertical", -1, 1, index, point_number))
    if z:
        sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, index, point_number, z))
    else:
        sketch.addConstraint(Sketcher.Constraint("Horizontal", -1, 1, index, point_number))


def _circle(sketch, x, z, diameter):
    index = sketch.addGeometry(
        Part.Circle(FreeCAD.Vector(x, z, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), diameter / 2.0), False
    )
    _point_constraints(sketch, index, 3, x, z)
    sketch.addConstraint(Sketcher.Constraint("Diameter", index, diameter))


def _line(first, last):
    return Part.LineSegment(FreeCAD.Vector(*first, 0.0), FreeCAD.Vector(*last, 0.0))


def _arc(x, z, radius, first, last):
    return Part.ArcOfCircle(Part.Circle(FreeCAD.Vector(x, z, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), radius), first, last)


def _closed(sketch, curves):
    indices = [sketch.addGeometry(curve, False) for curve in curves]
    for position, (index, curve) in enumerate(zip(indices, curves)):
        sketch.addConstraint(Sketcher.Constraint("Coincident", index, 2, indices[(position + 1) % len(indices)], 1))
        _point_constraints(sketch, index, 1, curve.StartPoint.x, curve.StartPoint.y)
        if isinstance(curve, Part.ArcOfCircle):
            sketch.addConstraint(Sketcher.Constraint("Radius", index, curve.Radius))


def _polygon(sketch, points):
    _closed(sketch, [_line(point, points[(index + 1) % len(points)]) for index, point in enumerate(points)])


def _square(sketch, x, z, width):
    half = width / 2.0
    _polygon(sketch, [(x - half, z - half), (x + half, z - half), (x + half, z + half), (x - half, z + half)])


def _circular_band(sketch, x, z, width):
    """Exact circle clipped by horizontal bridge edges, retaining circular ends."""
    radius = counterboreDiameter / 2.0
    angle = math.asin(width / counterboreDiameter)
    right = _arc(x, z, radius, -angle, angle)
    left = _arc(x, z, radius, math.pi - angle, math.pi + angle)
    _closed(
        sketch,
        [
            right,
            Part.LineSegment(right.EndPoint, left.StartPoint),
            left,
            Part.LineSegment(left.EndPoint, right.StartPoint),
        ],
    )


def _hexagon(sketch, x, z, left, right, clipped=False):
    radius = nutCornerRadius
    if clipped:
        half = screwDiameter / 2.0
        ratio = (radius - half) / (radius / 2.0)
        xl, xr = x + (left - x) * ratio, x + (right - x) * ratio
        points = [
            (xl, z - half),
            (xr, z - half),
            (right, z - radius / 2.0),
            (right, z + radius / 2.0),
            (xr, z + half),
            (xl, z + half),
            (left, z + radius / 2.0),
            (left, z - radius / 2.0),
        ]
    else:
        points = [
            (x, z - radius),
            (right, z - radius / 2.0),
            (right, z + radius / 2.0),
            (x, z + radius),
            (left, z + radius / 2.0),
            (left, z - radius / 2.0),
        ]
    _polygon(sketch, points)


def _pad(body, name, profile, length):
    _check(body, profile)
    pad = body.newObject("PartDesign::Pad", name)
    pad.Profile = profile
    pad.Length = length
    pad.Reversed = True
    pad.Refine = True
    _check(body, pad)
    return pad


def _nut_tools(tool):
    axes = (
        (leftNutX, leftNutZ, nutLeftFlatX, nutRightFlatX),
        (lugNutX, lugNutZ, lugNutX - nutAcrossFlats / 2.0, lugNutX + nutAcrossFlats / 2.0),
        (lowerNutX, lowerNutZ, lowerNutX - nutAcrossFlats / 2.0, lowerNutX + nutAcrossFlats / 2.0),
    )
    profile = _sketch(tool, "NutTrapProfiles", -_OVERRUN)
    for x, z, left, right in axes:
        _hexagon(profile, x, z, left, right)
    _pad(tool, "NutTrapCavities", profile, nutFullDepth + _OVERRUN)

    profile = _sketch(tool, "NutFirstBridgeProfiles", nutFullDepth)
    for x, z, left, right in axes:
        _hexagon(profile, x, z, left, right, clipped=True)
    _pad(tool, "NutFirstBridges", profile, nutRectEnd - nutFullDepth)

    profile = _sketch(tool, "NutSquareBridgeProfiles", nutRectEnd)
    for x, z, _, _ in axes:
        _square(profile, x, z, screwDiameter)
    _pad(tool, "NutSquareBridges", profile, nutPilotStart - nutRectEnd)

    profile = _sketch(tool, "NutPilotProfiles", nutPilotStart)
    for x, z, _, _ in axes:
        _circle(profile, x, z, screwDiameter)
    _pad(tool, "NutPilots", profile, plateThickness + _OVERRUN - nutPilotStart)


def _circular_tools(tool, name, axes, width, full_depth, band_end, pilot_start):
    profile = _sketch(tool, name + "CounterboreProfiles", -_OVERRUN)
    for x, z, _ in axes:
        _circle(profile, x, z, counterboreDiameter)
    _pad(tool, name + "Counterbores", profile, full_depth + _OVERRUN)

    profile = _sketch(tool, name + "FirstBridgeProfiles", full_depth)
    for x, z, _ in axes:
        _circular_band(profile, x, z, width)
    _pad(tool, name + "FirstBridges", profile, band_end - full_depth)

    profile = _sketch(tool, name + "SquareBridgeProfiles", band_end)
    for x, z, _ in axes:
        _square(profile, x, z, width)
    _pad(tool, name + "SquareBridges", profile, pilot_start - band_end)

    # Exact interface: an enlarged pilot must never cut into the square bridge.
    # Native additive features fuse the touching tool sections before stock is cut.
    profile = _sketch(tool, name + "PilotProfiles", pilot_start)
    for x, z, diameter in axes:
        _circle(profile, x, z, diameter)
    _pad(tool, name + "Pilots", profile, plateThickness + _OVERRUN - pilot_start)


def _pivot_tools(tool):
    profile = _sketch(tool, "PivotPilotProfiles", -_OVERRUN)
    for x in (leftPivotX, rightPivotX):
        _circle(profile, x, 0.0, screwDiameter)
    _pad(tool, "PivotPilots", profile, pivotPilotEnd + _OVERRUN)

    for name, x in (("Left", leftPivotX), ("Right", rightPivotX)):
        start = _sketch(tool, name + "PivotMouthStart", pivotPilotEnd)
        _circle(start, x, 0.0, screwDiameter)
        finish = _sketch(tool, name + "PivotMouthEnd", pivotCounterboreStart)
        _circle(finish, x, 0.0, pivotMouthDiameter)
        _check(tool, start, finish)
        loft = tool.newObject("PartDesign::AdditiveLoft", name + "PivotMouth")
        loft.Profile = start
        loft.Sections = [finish]
        loft.Ruled = True
        loft.Refine = True
        _check(tool, loft)

    profile = _sketch(tool, "PivotCounterboreAndSlotProfiles", pivotCounterboreStart)
    radius = counterboreDiameter / 2.0
    arc = _arc(leftPivotX, 0.0, radius, -math.pi / 2.0, math.pi / 2.0)
    left_top = (-halfWidth - _OVERRUN, radius)
    left_bottom = (-halfWidth - _OVERRUN, -radius)
    curves = [
        arc,
        _line((arc.EndPoint.x, arc.EndPoint.y), left_top),
        _line(left_top, left_bottom),
        _line(left_bottom, (arc.StartPoint.x, arc.StartPoint.y)),
    ]
    indices = [profile.addGeometry(curve, False) for curve in curves]
    for index, following in zip(indices, indices[1:] + indices[:1]):
        profile.addConstraint(Sketcher.Constraint("Coincident", index, 2, following, 1))
    # Constrain the semicircle by centre/radius and endpoint x coordinates.
    # Fixing both endpoints plus radius is singular at exactly 180 degrees.
    _point_constraints(profile, indices[0], 3, leftPivotX, 0.0)
    profile.addConstraint(Sketcher.Constraint("Radius", indices[0], radius))
    for endpoint in (1, 2):
        profile.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, indices[0], endpoint, leftPivotX))
    _point_constraints(profile, indices[2], 1, *left_top)
    _point_constraints(profile, indices[3], 1, *left_bottom)
    _circle(profile, rightPivotX, 0.0, counterboreDiameter)
    _pad(tool, "PivotCounterboresAndOpenSlot", profile, plateThickness + _OVERRUN - pivotCounterboreStart)


def _invariants():
    assert plateThickness > 0.0, "infeasible: plateThickness must be positive"
    assert upperLeftPilotDiameter > 0.0, "infeasible: upperLeftPilotDiameter must be positive"
    assert lowerLeftPilotDiameter > 0.0, "infeasible: lowerLeftPilotDiameter must be positive"
    assert 0.0 < screwDiameter < pivotMouthDiameter < counterboreDiameter, "infeasible: fastener diameters cross"
    assert max(upperLeftPilotDiameter, lowerLeftPilotDiameter, _LONG_BRIDGE_WIDTH) < counterboreDiameter, (
        "infeasible: long pilots and bridges must fit the counterbores"
    )
    assert nutLeftFlatX < leftNutX < nutRightFlatX, "infeasible: left nut centre must be between its flats"
    assert nutAcrossFlats > screwDiameter, "infeasible: nut flats must enclose the square bridge"
    assert nutCornerRadius < screwDiameter < 2.0 * nutCornerRadius, "infeasible: nut bridge misses hex shoulders"
    assert 0.0 < nutFullDepth < nutRectEnd < nutPilotStart < plateThickness, "infeasible: nut support depths cross"
    assert 0.0 < longCounterboreFullDepth < longCounterboreEnd < longPilotStart < plateThickness, (
        "infeasible: long support depths cross"
    )
    assert 0.0 < rightCounterboreFullDepth < rightCounterboreEnd < rightPilotStart < plateThickness, (
        "infeasible: right support depths cross"
    )
    assert 0.0 < pivotPilotEnd < pivotCounterboreStart < plateThickness, "infeasible: pivot depths cross"
    assert 0.0 < bridgeLayerHeight < min(nutFullDepth, longCounterboreFullDepth, rightCounterboreFullDepth), (
        "infeasible: bridgeLayerHeight must fit inside the cavity depths"
    )
    assert 0.0 < longPilotLength < plateThickness, "infeasible: longPilotLength must fit inside the plate"
    assert -halfWidth < leftPivotX < rightPivotX < halfWidth, "infeasible: pivot axes leave the envelope"


def apply(body):
    """Subtract the united tool once, retaining the input Body or input tuple."""
    _invariants()
    target = body[0] if isinstance(body, tuple) else body
    doc = target.Document
    tool = doc.addObject("PartDesign::Body", "FastenerTool")
    # These eight disconnected cutting stacks are consumed by the final Boolean;
    # they are construction geometry, never additional deliverable solids.
    tool.AllowCompound = True
    doc.recompute()
    _nut_tools(tool)
    _circular_tools(
        tool,
        "Long",
        (
            (upperLeftScrewX, upperLeftScrewZ, upperLeftPilotDiameter),
            (lowerLeftScrewX, lowerLeftScrewZ, lowerLeftPilotDiameter),
        ),
        _LONG_BRIDGE_WIDTH,
        longCounterboreFullDepth,
        longCounterboreEnd,
        longPilotStart,
    )
    _circular_tools(
        tool,
        "UpperRight",
        ((upperRightScrewX, upperRightScrewZ, screwDiameter),),
        screwDiameter,
        rightCounterboreFullDepth,
        rightCounterboreEnd,
        rightPilotStart,
    )
    _pivot_tools(tool)
    _check(tool, tool)
    assert len(tool.Shape.Solids) == 8, "kernel: expected eight united fastener tool stacks"

    # Tools may extend into air, but their intersection with stock must fit the
    # module's assigned material region. No boss or clamp restoration is made.
    removed = target.Shape.common(tool.Shape)
    bounds = removed.BoundBox
    for actual, limit in zip((bounds.XMin, bounds.YMin, bounds.ZMin), _REGION_MIN):
        assert actual >= limit - 1e-6, "partition: fastener removal extends below the assigned region"
    for actual, limit in zip((bounds.XMax, bounds.YMax, bounds.ZMax), _REGION_MAX):
        assert actual <= limit + 1e-6, "partition: fastener removal extends above the assigned region"

    cut = target.newObject("PartDesign::Boolean", "FastenerStacks")
    cut.Type = "Cut"
    cut.Group = [tool]
    cut.Refine = True
    _check(target, cut, target)
    assert len(target.Shape.Solids) == 1, "kernel: fasteners must leave one connected deliverable solid"
    for feature in (*target.Group, *tool.Group):
        assert feature.isValid(), "kernel: invalid feature after fastener subtraction: " + feature.Name
    doc.recompute()
    return body
