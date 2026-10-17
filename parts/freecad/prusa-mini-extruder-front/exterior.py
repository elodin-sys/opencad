"""Exterior stock and bosses, before any functional pocket families.

The six exterior planes come from the dimension sheet. Finished datum areas
and the right bevel areas depend on the later fastener/keyhole/clamp cuts.
The web is a ruled, dimension-supported allowance for the filament group;
no filament bore, nut trap, cosmetic fillet, R1 or arrow is cut here.
"""

import math

import FreeCAD
import Part
import Sketcher
from params import (
    bodyTopZ,
    bottomZ,
    filamentDiameter,
    filamentDirX,
    filamentDirY,
    filamentEntryAxisX,
    filamentEntryAxisY,
    filamentEntryEnd,
    filamentEntryStart,
    filamentTransverseX,
    filamentZ,
    halfWidth,
    keyMiddleEnd,
    leftDiagonalAnchorX,
    leftDiagonalAnchorZ,
    leftFootX,
    leftShoulderZ,
    leftTopChamferZ,
    lugBossDiameter,
    lugMaxZ,
    lugNutX,
    lugNutZ,
    lugWebPeakX,
    plateThickness,
    rightBottomChamferZ,
    rightTopChamferX,
    upperLeftBossDiameter,
    upperLeftScrewX,
    upperLeftScrewZ,
)

_OVERRUN = 0.02
# Stated outward plane normals, dimension-sheet rows 1, 6, 10 and 28.
_LOWER_NX = -0.7373
_LOWER_NZ = -0.6756
_SHALLOW_NX = -0.0872
_SHALLOW_NZ = -0.9962
_BOSS_NX = 0.766
_BOSS_NZ = 0.6428
_WEB_NX = 0.2876
_WEB_NY = -0.9135
_WEB_NZ = 0.2876


def _sketch(body, name, plane_name, offset):
    plane = next(obj for obj in body.Origin.OriginFeatures if plane_name in obj.Name and "Plane" in obj.Name)
    sketch = body.newObject("Sketcher::SketchObject", name)
    sketch.AttachmentSupport = [(plane, "")]
    sketch.MapMode = "FlatFace"
    sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, offset), FreeCAD.Rotation())
    return sketch


def _closed(sketch, geometry):
    """One closed wire, origin dimensions at every vertex and arc radii.

    Endpoint coordinates plus the radius determine each arc, without fixed
    geometry or a solver-dependent unconstrained circle centre.
    """
    ids = [sketch.addGeometry(curve, False) for curve in geometry]
    for position, (index, curve) in enumerate(zip(ids, geometry)):
        following = ids[(position + 1) % len(ids)]
        sketch.addConstraint(Sketcher.Constraint("Coincident", index, 2, following, 1))
        start = curve.StartPoint
        sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, index, 1, start.x))
        sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, index, 1, start.y))
        if isinstance(curve, Part.ArcOfCircle):
            sketch.addConstraint(Sketcher.Constraint("Radius", index, curve.Radius))


def _line(a, b):
    return Part.LineSegment(FreeCAD.Vector(*a, 0.0), FreeCAD.Vector(*b, 0.0))


def _polygon(sketch, points):
    _closed(
        sketch,
        [_line(point, points[(index + 1) % len(points)]) for index, point in enumerate(points)],
    )


def _arc(cx, cz, radius, first, last):
    return Part.ArcOfCircle(
        Part.Circle(FreeCAD.Vector(cx, cz, 0.0), FreeCAD.Vector(0.0, 0.0, 1.0), radius),
        first,
        last,
    )


def _check(body, *features):
    body.Document.recompute()
    for feature in features:
        assert feature.isValid(), "kernel: invalid exterior feature " + feature.Name
        if feature.TypeId == "Sketcher::SketchObject":
            assert feature.FullyConstrained, "sketch: unconstrained exterior profile " + feature.Name
        else:
            assert feature.Shape.isValid(), "kernel: invalid exterior shape " + feature.Name
            assert len(feature.Shape.Solids) == 1, "kernel: exterior must remain one connected solid"


def _pocket(body, name, sketch, length):
    _check(body, sketch)
    pocket = body.newObject("PartDesign::Pocket", name)
    pocket.Profile = sketch
    pocket.Length = length
    # XZ's normal is -y; a non-reversed Pocket removes material toward +y.
    pocket.Reversed = False
    pocket.Refine = True
    _check(body, pocket)
    return pocket


def _perimeter(body):
    """Batch the four corner tools and the lug crown into one Pocket."""
    shallow_slope = -_SHALLOW_NX / _SHALLOW_NZ
    lower_slope = -_LOWER_NX / _LOWER_NZ
    shallow_intercept = leftShoulderZ + shallow_slope * halfWidth
    lower_intercept = leftDiagonalAnchorZ - lower_slope * leftDiagonalAnchorX
    knee_x = (lower_intercept - shallow_intercept) / (shallow_slope - lower_slope)
    knee_z = shallow_intercept + shallow_slope * knee_x
    foot_z = lower_intercept + lower_slope * leftFootX
    assert -halfWidth < knee_x < leftFootX, "infeasible: lower-left bevel intersection leaves the foot"
    assert bottomZ < foot_z < knee_z < leftShoulderZ, "infeasible: lower-left exterior levels cross"

    profile = _sketch(body, "ExteriorPerimeterSketch", "XZ", _OVERRUN)
    left = -halfWidth - _OVERRUN
    right = halfWidth + _OVERRUN
    low = bottomZ - _OVERRUN
    high = bodyTopZ + _OVERRUN
    _polygon(
        profile,
        [
            (left, low),
            (leftFootX, low),
            (leftFootX, foot_z),
            (knee_x, knee_z),
            (left, shallow_intercept + shallow_slope * left),
        ],
    )
    _polygon(
        profile,
        [(right, low), (right, rightBottomChamferZ + _OVERRUN), (halfWidth + low - rightBottomChamferZ, low)],
    )
    _polygon(
        profile,
        [(left, leftTopChamferZ - _OVERRUN), (-halfWidth + high - leftTopChamferZ, high), (left, high)],
    )
    _polygon(
        profile,
        [(right, bodyTopZ - (right - rightTopChamferX)), (right, high), (rightTopChamferX - _OVERRUN, high)],
    )

    radius = lugBossDiameter / 2.0
    # The root chord reserves stock for the mandatory transverse Ø4 surface.
    # Its direction is the line between the two stated cylinder axes. The
    # filament module, not this one, removes the concave circular segment.
    root_angle = math.atan2(filamentZ - lugNutZ, filamentTransverseX - lugNutX)
    crown = _arc(lugNutX, lugNutZ, radius, root_angle, math.pi)
    crown_start = (crown.StartPoint.x, crown.StartPoint.y)
    crown_end = (crown.EndPoint.x, crown.EndPoint.y)
    outer_left = lugNutX - radius - _OVERRUN
    # Reach beyond the passed rectangular allowance; the final peak is set
    # by the stated planes rather than this raster blockout coordinate.
    outer_right = max(filamentTransverseX, lugNutX + radius, lugWebPeakX) + _OVERRUN
    points = [
        crown_end,
        (outer_left, lugNutZ),
        (outer_left, lugMaxZ + _OVERRUN),
        (outer_right, lugMaxZ + _OVERRUN),
        (outer_right, bodyTopZ),
        (filamentTransverseX, bodyTopZ),
        crown_start,
    ]
    _closed(profile, [crown] + [_line(point, points[index + 1]) for index, point in enumerate(points[:-1])])
    return _pocket(body, "ExteriorPerimeter", profile, plateThickness + 2.0 * _OVERRUN)


def _web(body):
    """Ruled allowance bounded by the two stated inclined support planes.

    At z=28 the web starts on the angled filament axis projection. Above the
    future bore's tangent it follows dimension-sheet plane 28. The loft leaves
    material for that finite bore through x≈18..23; its outer end is the 45°
    right bevel. The unmeasured crown blend is a straight transition.
    """
    direction_length = math.hypot(filamentDirX, filamentDirY)
    dx = filamentDirX / direction_length
    dy = filamentDirY / direction_length
    radius = filamentDiameter / 2.0
    transverse_normal = -_WEB_NX * dy + _WEB_NY * dx
    normal_length = math.hypot(transverse_normal, _WEB_NZ)
    tangent_u = -radius * transverse_normal / normal_length
    tangent_z = filamentZ - radius * _WEB_NZ / normal_length
    slope = -transverse_normal / _WEB_NZ
    roof_intercept = rightTopChamferX + bodyTopZ
    assert bodyTopZ < tangent_z < lugMaxZ, "infeasible: filament support tangent leaves the web"
    assert dx > 0.0 and slope > 0.0, "infeasible: angled filament direction reverses the web"

    def front_y(x, u):
        return filamentEntryAxisY + (dy * (x - filamentEntryAxisX) + u) / dx

    levels = (
        (bodyTopZ - _OVERRUN, 0.0),
        (bodyTopZ, 0.0),
        (tangent_z, tangent_u),
        (lugMaxZ, tangent_u + (lugMaxZ - tangent_z) / slope),
    )
    sections = []
    for index, (level, u) in enumerate(levels):
        right = roof_intercept - level + _OVERRUN
        assert lugNutX < right < halfWidth, "infeasible: web roof leaves the plate"
        assert 0.0 < front_y(lugNutX, u) < front_y(right, u) < plateThickness, (
            "infeasible: web section leaves the plate thickness"
        )
        sketch = _sketch(body, "RearWebSection" + str(index), "XY", level)
        _polygon(
            sketch,
            [
                (lugNutX, front_y(lugNutX, u)),
                (right, front_y(right, u)),
                (right, plateThickness),
                (lugNutX, plateThickness),
            ],
        )
        _check(body, sketch)
        sections.append(sketch)
    loft = body.newObject("PartDesign::AdditiveLoft", "RearWebAllowance")
    loft.Profile = sections[0]
    loft.Sections = sections[1:]
    loft.Ruled = True
    loft.Refine = True
    _check(body, loft)

    # Exact 45° roof and max z take precedence over the raster x=16.75 peak.
    # No unmeasured lug fillet radius is introduced at this transition.
    peak_x = roof_intercept - lugMaxZ
    crown_z = lugNutZ + lugBossDiameter / 2.0
    assert lugNutX < peak_x, "infeasible: rear-web peak overlaps the lug centre"
    assert crown_z < lugMaxZ, "infeasible: lug crown exceeds the envelope"
    top_slope = (lugMaxZ - crown_z) / (peak_x - lugNutX)
    left = lugNutX - _OVERRUN
    right = halfWidth + _OVERRUN
    profile = _sketch(body, "RearWebCrownSketch", "XZ", _OVERRUN)
    _polygon(
        profile,
        [
            (left, crown_z),
            (lugNutX, crown_z),
            (peak_x, crown_z + top_slope * (peak_x - lugNutX)),
            (right, roof_intercept - right),
            (right, lugMaxZ + 2.0 * _OVERRUN),
            (left, lugMaxZ + 2.0 * _OVERRUN),
        ],
    )
    return _pocket(body, "RearWebCrown", profile, plateThickness + 2.0 * _OVERRUN)


def _upper_boss(body):
    radius = upperLeftBossDiameter / 2.0
    normal_length = math.hypot(_BOSS_NX, _BOSS_NZ)
    nx, nz = _BOSS_NX / normal_length, _BOSS_NZ / normal_length
    # Stated row-10 anchor (-16.5, 28), 2 mm right of the screw axis.
    anchor_x = upperLeftScrewX + 2.0
    anchor_z = bodyTopZ
    distance = nx * (anchor_x - upperLeftScrewX) + nz * (anchor_z - upperLeftScrewZ)
    assert 0.0 < distance < radius, "infeasible: upper-left boss bevel misses its circle"
    assert 0.0 < leftTopChamferZ - upperLeftScrewZ < radius, "infeasible: boss ledge misses the boss"
    first = math.atan2(nz, nx) + math.acos(distance / radius)
    last = math.pi - math.asin((leftTopChamferZ - upperLeftScrewZ) / radius)
    assert first < last, "infeasible: upper-left boss arc is reversed"
    arc = _arc(upperLeftScrewX, upperLeftScrewZ, radius, first, last)
    # End this exterior relief within the future upper counterbore, clear of
    # its cylindrical wall. That family alone establishes the curved opening.
    low_z = upperLeftScrewZ
    end_x = anchor_x + nz * (anchor_z - low_z) / nx
    right = lugNutX - lugBossDiameter / 2.0
    high = lugMaxZ + _OVERRUN
    left = -halfWidth - _OVERRUN
    points = [
        (arc.EndPoint.x, arc.EndPoint.y),
        (left, leftTopChamferZ),
        (left, high),
        (right, high),
        (right, low_z),
        (end_x, low_z),
        (arc.StartPoint.x, arc.StartPoint.y),
    ]
    profile = _sketch(body, "UpperLeftBossReliefSketch", "XZ", -keyMiddleEnd)
    _closed(profile, [arc] + [_line(point, points[index + 1]) for index, point in enumerate(points[:-1])])
    return _pocket(body, "UpperLeftBossRelief", profile, plateThickness - keyMiddleEnd + _OVERRUN)


def apply(body):
    """Add the exterior PartDesign feature families and return the input Body."""
    assert plateThickness > keyMiddleEnd > 0.0, "infeasible: boss depth lies outside the plate"
    assert upperLeftBossDiameter > 0.0 and lugBossDiameter > 0.0, "infeasible: boss diameters must be positive"
    assert filamentDiameter > 0.0, "infeasible: filament diameter must be positive"
    assert 0.0 < filamentEntryStart < filamentEntryEnd, "infeasible: angled filament extent is reversed"
    assert math.hypot(filamentDirX, filamentDirY) > 0.0, "infeasible: zero filament direction"
    assert bottomZ < rightBottomChamferZ < leftTopChamferZ < bodyTopZ, "infeasible: perimeter levels cross"
    assert lugNutX < filamentTransverseX < rightTopChamferX < halfWidth, "infeasible: lug/web x levels cross"
    _perimeter(body)
    _web(body)
    last = _upper_boss(body)
    last.Refine = True
    _check(body, body, *body.Group)
    return body
