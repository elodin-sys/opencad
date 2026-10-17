"""Exterior sculpting, with a shared analytic surface-normal offset evaluator.

The incoming datum bounds the available stock. No repair pad is added to hide
its z203.5 minimum or its coarse silhouette. Integration must resolve those
stock/partition limitations before claiming a full mating-contour acceptance.
"""

import math

from build123d import (
    Align,
    Box,
    CenterArc,
    Compound,
    Line,
    Plane,
    Polyline,
    Pos,
    Spline,
    extrude,
    loft,
    make_face,
    mirror,
)
from params import (
    bodyBlendRadius,
    crownEndSlope,
    crownEndValue,
    crownEndZ,
    crownStartValue,
    crownStartZ,
    envelopeHalfWidth,
    envelopeMaxY,
    envelopeMinY,
    facetEndX,
    facetSideY,
    keelEndSlope,
    keelEndValue,
    keelEndZ,
    keelStartValue,
    keelStartZ,
    ledgeInset,
    ledgeStartY,
    morphEndZ,
    morphStartZ,
    mountMinZ,
    notchCornerRadius,
    notchFloorY,
    notchHalfWidth,
    perimeterClearance,
    plateThickness,
    plateTopZ,
    shoulderCornerRadius,
    shoulderY,
    skinWall,
    skirtMaxX,
    skirtThresholdY,
    stepY,
    topLayerThickness,
    widthEndSlope,
    widthEndValue,
    widthEndZ,
    widthStartValue,
    widthStartZ,
)


def hermite(z, start_z, start_value, end_z, end_value, end_slope):
    """Zero start slope; constant before start; never extrapolate past end."""
    assert end_z > start_z, "Hermite stations must be ordered"
    assert z <= end_z, "mating law is undefined beyond its endpoint"
    t = max(0.0, (z - start_z) / (end_z - start_z))
    return (
        (2 * t**3 - 3 * t**2 + 1) * start_value
        + (3 * t**2 - 2 * t**3) * end_value
        + (t**3 - t**2) * (end_z - start_z) * end_slope
    )


def crown(z):
    return hermite(z, crownStartZ, crownStartValue, crownEndZ, crownEndValue, crownEndSlope)


def _laws(z):
    return (
        hermite(z, widthStartZ, widthStartValue, widthEndZ, widthEndValue, widthEndSlope),
        crown(z),
        hermite(z, keelStartZ, keelStartValue, keelEndZ, keelEndValue, keelEndSlope),
    )


def _cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def _rounded_radius(angle, z):
    """Ray intersection with the analytic R7-rounded eight-facet section."""
    w, c, k = _laws(z)
    side, end = facetSideY * w / widthStartValue, facetEndX * w / widthStartValue
    vertices = [(w, -side), (w, side), (end, c), (-end, c), (-w, side), (-w, -side), (-end, k), (end, k)]
    ray = (math.cos(angle), math.sin(angle))
    corners = []
    candidates = []
    for j, p in enumerate(vertices):
        before, after = vertices[j - 1], vertices[(j + 1) % len(vertices)]
        a = (before[0] - p[0], before[1] - p[1])
        b = (after[0] - p[0], after[1] - p[1])
        la, lb = math.hypot(*a), math.hypot(*b)
        a, b = (a[0] / la, a[1] / la), (b[0] / lb, b[1] / lb)
        theta = math.acos(max(-1.0, min(1.0, a[0] * b[0] + a[1] * b[1])))
        tangent = bodyBlendRadius / math.tan(theta / 2)
        assert tangent < min(la, lb) / 2, "facet blend consumes adjacent straight"
        bis = (a[0] + b[0], a[1] + b[1])
        factor = bodyBlendRadius / (math.sin(theta / 2) * math.hypot(*bis))
        center = (p[0] + factor * bis[0], p[1] + factor * bis[1])
        p0 = (p[0] + tangent * a[0], p[1] + tangent * a[1])
        p1 = (p[0] + tangent * b[0], p[1] + tangent * b[1])
        corners.append((p0, p1, center))
    for j, (p0, p1, center) in enumerate(corners):
        next_p = corners[(j + 1) % len(corners)][0]
        segment = (next_p[0] - p1[0], next_p[1] - p1[1])
        determinant = _cross(ray, segment)
        if abs(determinant) > 1e-12:
            radius = _cross(p1, segment) / determinant
            fraction = _cross(p1, ray) / determinant
            if radius > 0 and -1e-10 <= fraction <= 1 + 1e-10:
                candidates.append(radius)
        projection = center[0] * ray[0] + center[1] * ray[1]
        discriminant = projection**2 - (center[0] ** 2 + center[1] ** 2 - bodyBlendRadius**2)
        if discriminant >= 0:
            n0 = (p0[0] - center[0], p0[1] - center[1])
            n1 = (p1[0] - center[0], p1[1] - center[1])
            for radius in (projection - math.sqrt(discriminant), projection + math.sqrt(discriminant)):
                normal = (radius * ray[0] - center[0], radius * ray[1] - center[1])
                if radius > 0 and _cross(n0, normal) >= -1e-8 and _cross(normal, n1) >= -1e-8:
                    candidates.append(radius)
    assert candidates, "rounded section ray must intersect"
    return min(candidates)


def outer_point(angle, z):
    """Specified radial morph of rounded facets into two half-ellipses."""
    w, c, k = _laws(z)
    u = max(0.0, min(1.0, (z - morphStartZ) / (morphEndZ - morphStartZ)))
    blend = u * u * (3 - 2 * u)
    co, si = math.cos(angle), math.sin(angle)
    height = c if si >= 0 else -k
    ellipse = 1 / math.sqrt((co / w) ** 2 + (si / height) ** 2)
    radius = ellipse if blend == 1.0 else (1 - blend) * _rounded_radius(angle, z) + blend * ellipse
    return (radius * co, radius * si, z)


def surface_normal(angle, z):
    """Outward 3D skin normal, including the longitudinal taper derivative."""
    h = 0.0001
    ta, tb = outer_point(angle - h, z), outer_point(angle + h, z)
    za, zb = outer_point(angle, z - h), outer_point(angle, z + h)
    dx, dy = (tb[0] - ta[0]) / (2 * h), (tb[1] - ta[1]) / (2 * h)
    xz, yz = (zb[0] - za[0]) / (2 * h), (zb[1] - za[1]) / (2 * h)
    n = (dy, -dx, dx * yz - dy * xz)
    length = math.sqrt(sum(v * v for v in n))
    return tuple(v / length for v in n)


def normal_offset_point(angle, z, distance=None):
    """Intersect the actual surface-normal offset with a requested z plane.

    Public helper for insertSeat. `distance` includes wall and mating clearance.
    Solving the original surface station avoids a coordinate-wise wall shrink.
    """
    if distance is None:
        distance = skinWall + perimeterClearance
    source_z = z
    for _ in range(15):
        n = surface_normal(angle, source_z)
        next_z = z + distance * n[2]
        if abs(next_z - source_z) < 1e-10:
            break
        source_z = next_z
    p = outer_point(angle, source_z)
    n = surface_normal(angle, source_z)
    assert abs(p[2] - distance * n[2] - z) < 1e-7, "normal-offset station did not converge"
    return (p[0] - distance * n[0], p[1] - distance * n[1], z)


def crown_offset(z, clearance=None):
    """Cover-facing crown ordinate at the assembly z station."""
    return normal_offset_point(math.pi / 2, z, skinWall + (perimeterClearance if clearance is None else clearance))[1]


def clearance_section(z, clearance=perimeterClearance):
    # Quarter boundaries preserve exact mirror correspondence in the loft.
    edges = []
    for quadrant in range(4):
        points = [normal_offset_point((quadrant + i / 32) * math.pi / 2, z, skinWall + clearance) for i in range(33)]
        edges.append(Spline(*points))
    return make_face(edges)


def clearance_loft(z0, z1, clearance=perimeterClearance):
    return loft([clearance_section(z0 + (z1 - z0) * i / 8, clearance) for i in range(9)], ruled=False)


def _box(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def apply(body):
    assert plateThickness > topLayerThickness > 0, "plate layers must have positive thickness"
    assert 0 < notchCornerRadius < notchHalfWidth, "notch must retain a flat floor"
    assert 0 < shoulderCornerRadius < envelopeHalfWidth, "shoulder radius must fit"
    assert 0 < perimeterClearance and 0 < skinWall, "skin and clearance must be positive"
    assert ledgeInset >= 0, "ledge inset cannot be negative"
    assert morphEndZ > morphStartZ, "morph stations must be ordered"
    under = plateTopZ - plateThickness
    ledge = plateTopZ - topLayerThickness
    # Retain the source's 0.01 mm transition allowance: a cutter ending
    # exactly on z210 makes that section include the two coplanar ledge
    # underside boundaries as extra loops. Keep the nominal section inside
    # the continuous upper layer, within the ledge face's 0.05 mm tolerance.
    layer_cut_top = ledge - 0.01
    overrun = 0.03
    x0, x1 = -envelopeHalfWidth - overrun, envelopeHalfWidth + overrun
    y0, y1 = envelopeMinY - overrun, envelopeMaxY + overrun
    z0, z1 = mountMinZ - overrun, plateTopZ + overrun
    surrounding = _box(x0, x1, y0, y1, z0, z1)
    mating = clearance_loft(z0, z1)
    tools = [surrounding - mating]
    # Exact normal inset on the lower ledge; intentionally below y0 only.
    lower = _box(x0, x1, y0, ledgeStartY, under - overrun, layer_cut_top)
    inset = clearance_loft(under - overrun, ledge + overrun, perimeterClearance + ledgeInset)
    tools.append(lower - inset)
    tools.append(_box(x0, x1, y0, stepY, under - overrun, layer_cut_top))
    # Fork relief stays inside its prescribed x/y bounds.
    h, r, floor = notchHalfWidth, notchCornerRadius, notchFloorY
    notch = make_face(
        [
            Polyline((-h, y0), (h, y0), (h, floor - r)),
            CenterArc((h - r, floor - r), r, 0, 90),
            Line((h - r, floor), (-h + r, floor)),
            CenterArc((-h + r, floor - r), r, 90, 90),
            Line((-h, floor - r), (-h, y0)),
        ]
    )
    tools.append(Pos(0, 0, under - overrun) * extrude(notch, plateThickness + 2 * overrun))
    # Corner tools only touch the shoulder outboard of both detail regions.
    for sign in (-1, 1):
        r = shoulderCornerRadius
        cx, cy = envelopeHalfWidth - r, shoulderY - r
        corner = make_face(
            [
                Polyline(
                    (cx, shoulderY),
                    (cx, shoulderY + overrun),
                    (envelopeHalfWidth + overrun, shoulderY + overrun),
                    (envelopeHalfWidth + overrun, cy),
                    (envelopeHalfWidth, cy),
                ),
                CenterArc((cx, cy), r, 0, 90),
            ]
        )
        if sign < 0:
            corner = mirror(corner, Plane.YZ)
        tools.append(Pos(0, 0, under - overrun) * extrude(corner, plateThickness + 2 * overrun))
        if sign > 0:
            tools.append(_box(skirtMaxX, x1, skirtThresholdY, y1, z0, z1))
        else:
            tools.append(_box(x0, -skirtMaxX, skirtThresholdY, y1, z0, z1))
    # Batch the local cutters after trimming the mating perimeter.
    # Apply the mating trim separately: fusing it with the ledge cutters can
    # lose one side of their coincident boundary on the amended datum stock.
    sculpted = body - tools[0]
    combined = tools[1].fuse(*tools[2:])
    if isinstance(combined, list):
        combined = Compound(combined)
    sculpted = sculpted - combined
    assert sculpted.is_valid, "exterior subtraction produced an invalid shape"
    assert len(sculpted.solids()) == 1, "exterior must preserve one connected body"
    return sculpted
