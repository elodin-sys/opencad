"""Sprite Aleph v2 servo mount, unchanged seed servo features in assembly coordinates."""

import math

from build123d import Axis, Box, Compound, Cylinder, Polyline, Pos, Spline, extrude, fillet, loft, make_face

rearZ = 214.844
frontZ = 229.0
tabFaceX = 0.0
plateXMin = -16.0
plateYMax = 13.781
plateThickness = 1.95
plateCornerRadius = 8.5
postWidth = 4.13
postYMin = 9.781
postCornerRadius = 1.0
bossWidth = 7.13
bossTopY = -14.21
bossFilletRadius = 1.0
chordTopY = -19.45
chordThickness = 1.0
skinThickness = 1.03
windowCornerRadius = 1.0
lowerHoleDiameter = 2.1
lowerHoleY = -15.804
lowerHoleZ = 222.788
upperHoleDiameter = 1.8
upperHoleY = 11.185
upperHoleZ = 222.912
sideClearance = 0.3
shellWall = 2.0
ledgeZ = 214.85
widthStartZ = 202.0
widthStartValue = 30.0
widthEndZ = 249.3
widthEndValue = 13.1
widthEndSlope = -0.4
crownStartZ = 185.0
crownStartValue = 37.5
crownEndZ = 256.7
crownEndValue = 7.8
crownEndSlope = -0.72
keelStartZ = 125.0
keelStartValue = -37.5
keelEndZ = 249.3
keelEndValue = -22.9
keelEndSlope = 0.35
morphStartZ = 202.0
morphEndZ = 225.0
splitStartY = 15.0
splitStartZ = 202.0
splitEndZ = 216.0

# R7 is the mating shell's retained R6..R8 rounded-facet choice.
cornerRadius = 7.0
facetShoulderY = 23.4
facetCrownHalfWidth = 17.6
seedHalfWidth = 18.4707
glueGap = 0.03
glueSideRelief = 0.18
_SINK = 0.02
_PAST = 0.05

assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert bossWidth > 0, "infeasible: bossWidth must be positive"
assert postWidth > 0, "infeasible: postWidth must be positive"
assert chordThickness > 0, "infeasible: chordThickness must be positive"
assert skinThickness > 0, "infeasible: skinThickness must be positive"
assert windowCornerRadius >= 0, "infeasible: windowCornerRadius must be non-negative"
assert bossTopY > chordTopY, "infeasible: lower boss has no height"
assert postYMin < plateYMax, "infeasible: upper post has no height"
assert plateCornerRadius < tabFaceX - plateXMin, "infeasible: plate corner consumes the plate"
assert plateCornerRadius < plateYMax - chordTopY, "infeasible: plate corner consumes the plate"
assert postCornerRadius < plateYMax - postYMin, "infeasible: post round consumes the post"
assert postCornerRadius < frontZ - rearZ, "infeasible: post round consumes the post"
assert bossFilletRadius < bossTopY - chordTopY, "infeasible: boss fillet consumes the boss"
assert lowerHoleDiameter > 0, "infeasible: lowerHoleDiameter must be positive"
assert upperHoleDiameter > 0, "infeasible: upperHoleDiameter must be positive"
assert lowerHoleY + lowerHoleDiameter / 2 < bossTopY, "infeasible: lower hole breaks through the boss top"
assert lowerHoleY - lowerHoleDiameter / 2 > chordTopY + bossFilletRadius, "infeasible: lower hole meets the boss fillet"
assert lowerHoleZ - lowerHoleDiameter / 2 > rearZ, "infeasible: lower hole breaks the rear face"
assert lowerHoleZ + lowerHoleDiameter / 2 < frontZ, "infeasible: lower hole breaks the front face"
assert upperHoleY - upperHoleDiameter / 2 > postYMin, "infeasible: upper hole breaks the post underside"
assert upperHoleY + upperHoleDiameter / 2 < plateYMax - postCornerRadius, "infeasible: upper hole breaks the post top"

assert rearZ < frontZ < widthEndZ, "infeasible: mount beyond nose law"
assert 0 < shellWall < cornerRadius, "infeasible: shell offset consumes blend"
assert 0 < sideClearance < 1, "infeasible: side clearance"
assert 0 < chordThickness < 3, "infeasible: chord consumes window"
assert 0 < skinThickness < 3, "infeasible: skin consumes window"
assert morphStartZ < morphEndZ, "infeasible: morph station order"


def _hermite(z, z0, v0, z1, v1, m1):
    assert z <= z1 + 1e-6, "infeasible: analytic law extrapolated beyond endpoint"
    t = max(0.0, (z - z0) / (z1 - z0))
    return (2 * t**3 - 3 * t * t + 1) * v0 + (3 * t * t - 2 * t**3) * v1 + (t**3 - t * t) * (z1 - z0) * m1


def _laws(z):
    return (
        _hermite(z, widthStartZ, widthStartValue, widthEndZ, widthEndValue, widthEndSlope),
        _hermite(z, crownStartZ, crownStartValue, crownEndZ, crownEndValue, crownEndSlope),
        _hermite(z, keelStartZ, keelStartValue, keelEndZ, keelEndValue, keelEndSlope),
    )


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _corners(z):
    w, c, k = _laws(z)
    shoulder = facetShoulderY * w / widthStartValue
    cx = facetCrownHalfWidth * w / widthStartValue
    vs = [(w, -shoulder), (w, shoulder), (cx, c), (-cx, c), (-w, shoulder), (-w, -shoulder), (-cx, k), (cx, k)]
    out = []
    for j, p in enumerate(vs):
        a, b = vs[j - 1], vs[(j + 1) % len(vs)]
        u = (a[0] - p[0], a[1] - p[1])
        v = (b[0] - p[0], b[1] - p[1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        u = (u[0] / lu, u[1] / lu)
        v = (v[0] / lv, v[1] / lv)
        theta = math.acos(u[0] * v[0] + u[1] * v[1])
        bis = (u[0] + v[0], u[1] + v[1])
        scale = cornerRadius / (math.sin(theta / 2) * math.hypot(*bis))
        center = (p[0] + scale * bis[0], p[1] + scale * bis[1])
        t = cornerRadius / math.tan(theta / 2)
        start = (p[0] + t * u[0], p[1] + t * u[1])
        end = (p[0] + t * v[0], p[1] + t * v[1])
        ns = ((start[0] - center[0]) / cornerRadius, (start[1] - center[1]) / cornerRadius)
        ne = ((end[0] - center[0]) / cornerRadius, (end[1] - center[1]) / cornerRadius)
        nm = (p[0] - center[0], p[1] - center[1])
        lm = math.hypot(*nm)
        out.append((center, ns, (nm[0] / lm, nm[1] / lm), ne))
    return out


def _quarter(z, lower=True):
    w, c, k = _laws(z)
    corners = _corners(z)
    sc, sn, _, se = corners[0 if lower else 1]
    kc, kn, _, ke = corners[7 if lower else 2]
    n = sn if lower else se
    m = ke if lower else kn
    sc = (sc[0], abs(sc[1]))
    kc = (kc[0], abs(kc[1]))
    n = (n[0], abs(n[1]))
    m = (m[0], abs(m[1]))
    points = [
        (w, sc[1]),
        (sc[0] + cornerRadius * n[0], sc[1] + cornerRadius * n[1]),
        (kc[0] + cornerRadius * m[0], kc[1] + cornerRadius * m[1]),
        (kc[0], -k if lower else c),
    ]
    angles = [math.atan2(y, x) for x, y in points]
    return w, (-k if lower else c), sc, kc, n, points, angles


def _facet_radius(z, a):
    w, h, sc, kc, n, _, angles = _quarter(z, a >= 0)
    a = abs(a)
    cs, ss = math.cos(a), math.sin(a)
    a1, a2, a3, a4 = angles
    if a <= a1:
        return w / cs
    if a2 <= a <= a3:
        shoulder = facetShoulderY * w / widthStartValue
        return (n[0] * w + n[1] * shoulder) / (n[0] * cs + n[1] * ss)
    if a >= a4:
        return h / ss
    cc = sc if a < a2 else kc
    dot = cc[0] * cs + cc[1] * ss
    return dot + math.sqrt(max(0.0, dot * dot - cc[0] ** 2 - cc[1] ** 2 + cornerRadius**2))


def _nose_xy(z, a):
    w, c, k = _laws(z)
    b = _smooth((z - morphStartZ) / (morphEndZ - morphStartZ))
    h = c if a < 0 else -k
    re = 1 / math.sqrt((math.cos(a) / w) ** 2 + (math.sin(a) / h) ** 2)
    r = re if b >= 1 else (1 - b) * _facet_radius(z, a) + b * re
    return r * math.cos(a), -r * math.sin(a)


def _offset_point(z, a):
    """True 3D surface-normal offset; solve source z to land on section z.

    Tangents of the analytic radial surface include the longitudinal taper.
    No K+2 shortcut or inherited glue ellipses are used.
    """
    source_z = z
    offset = shellWall + glueGap + glueSideRelief * math.cos(a) ** 2
    for _ in range(5):
        x, y = _nose_xy(source_z, a)
        d = 0.0001
        pa, pb = _nose_xy(source_z, a - d), _nose_xy(source_z, a + d)
        xa, ya = (pb[0] - pa[0]) / (2 * d), (pb[1] - pa[1]) / (2 * d)
        pa, pb = _nose_xy(source_z - d, a), _nose_xy(source_z + d, a)
        xz, yz = (pb[0] - pa[0]) / (2 * d), (pb[1] - pa[1]) / (2 * d)
        nx, ny, nz = ya, -xa, xa * yz - ya * xz
        length = math.sqrt(nx * nx + ny * ny + nz * nz)
        source_z = z - offset * nz / length
    return x + offset * nx / length, y + offset * ny / length


def _surface_at_x(z, x, inset=0.0):
    w, _, k = _laws(z)
    sx = 1 - inset / (w - shellWall)
    sy = 1 - inset / (-k - shellWall)
    lo, hi = 0.0, math.pi / 2
    for _ in range(32):
        a = (lo + hi) / 2
        px, py = _offset_point(z, a)
        if px * sx > x:
            lo = a
        else:
            hi = a
    return py * sy


def _intersection_width(z, y, inset=0.0):
    w, _, k = _laws(z)
    sx = 1 - inset / (w - shellWall)
    sy = 1 - inset / (-k - shellWall)
    lo, hi = 0.0, math.pi / 2
    for _ in range(32):
        a = (lo + hi) / 2
        x, py = _offset_point(z, a)
        if py * sy > y:
            lo = a
        else:
            hi = a
    return x * sx


def _section(z, y_top, inset=0.0):
    if inset:
        half = _intersection_width(z, y_top, inset)
    else:
        # Retained rear clipping; taper only where the new inner outline narrows.
        half = min(seedHalfWidth, _intersection_width(z, y_top) - sideClearance)
    points = [(half * j / 12, _surface_at_x(z, half * j / 12, inset)) for j in range(13)]
    right = Spline(*points)
    left = Spline(*[(-x, y) for x, y in reversed(points)])
    end = points[-1]
    if inset:
        top = Polyline(end, (-end[0], end[1]))
    else:
        top = Polyline(end, (half, y_top), (-half, y_top), (-end[0], end[1]))
    return Pos(0, 0, z) * make_face([right, top, left])


# Smooth, non-ruled sections from analytic construction, not mesh samples.
_stations = (rearZ, 218.0, 222.0, 225.0, frontZ)
saddle = loft([_section(z, chordTopY) for z in _stations], ruled=False)

window_top = chordTopY - chordThickness
window = loft([_section(z, window_top, skinThickness) for z in _stations], ruled=False)
window_rails = [
    edge
    for edge in window.edges()
    if abs(edge.center().Y - window_top) < 0.05 and edge.bounding_box().max.Z - edge.bounding_box().min.Z > 1.0
]
assert len(window_rails) == 2, "window top rails missing"
if windowCornerRadius > 0:
    window = fillet(window_rails, windowCornerRadius)
window_ends = window.faces().sort_by(Axis.Z)
window = window + extrude(window_ends[0], _PAST) + extrude(window_ends[-1], _PAST)
saddle = saddle - window


def _chord_fillet(x_wall, outward, z0, z1):
    center_x = x_wall + outward * bossFilletRadius
    center_y = chordTopY + bossFilletRadius
    x_in = x_wall - outward * _SINK
    y_in = chordTopY - _SINK
    span_z = z1 - z0
    block = Pos((x_in + center_x) / 2, (y_in + center_y) / 2, (z0 + z1) / 2) * Box(
        abs(center_x - x_in),
        center_y - y_in,
        span_z,
    )
    pin = Pos(center_x, center_y, (z0 + z1) / 2) * Cylinder(bossFilletRadius, span_z + 0.2)
    return block - pin


plate_center_y = (chordTopY - _SINK + plateYMax) / 2
plate = Pos(
    (plateXMin + tabFaceX) / 2,
    plate_center_y,
    rearZ + plateThickness / 2,
) * Box(tabFaceX - plateXMin, plateYMax - (chordTopY - _SINK), plateThickness)
arc_x = plateXMin + plateCornerRadius
arc_y = plateYMax - plateCornerRadius
corner = Pos(
    plateXMin + (plateCornerRadius - _PAST) / 2,
    plateYMax - (plateCornerRadius - _PAST) / 2,
    rearZ + plateThickness / 2,
) * Box(plateCornerRadius + _PAST, plateCornerRadius + _PAST, plateThickness + 0.2)
corner_pin = Pos(arc_x, arc_y, rearZ + plateThickness / 2) * Cylinder(plateCornerRadius, plateThickness + 0.4)
plate = plate - (corner - corner_pin)

post = Pos(
    (tabFaceX - postWidth) / 2,
    (postYMin + plateYMax) / 2,
    (rearZ + frontZ) / 2,
) * Box(postWidth, plateYMax - postYMin, frontZ - rearZ)
post_edge = [
    edge for edge in post.edges() if abs(edge.center().Y - plateYMax) < 1e-4 and abs(edge.center().Z - frontZ) < 1e-4
]
assert len(post_edge) == 1, "post corner edge missing"
post = fillet(post_edge, postCornerRadius)

boss = Pos(
    (tabFaceX - bossWidth) / 2,
    (chordTopY - _SINK + bossTopY) / 2,
    (rearZ + frontZ) / 2,
) * Box(bossWidth, bossTopY - (chordTopY - _SINK), frontZ - rearZ)

body = saddle + plate + post + boss
body = body + _chord_fillet(tabFaceX, 1.0, rearZ, frontZ)
body = body + _chord_fillet(tabFaceX - bossWidth, -1.0, rearZ, frontZ)

# Covers the rear of the post side so that face matches postSide without
# shortening the underside or the section at z=218.4.
cheek_reach = 1.0
cheek_width = 0.4
cheek_inset = 0.15
plate_front_z = rearZ + plateThickness
cheek = Pos(
    tabFaceX - postWidth - (cheek_width - _SINK) / 2,
    (postYMin + plateYMax) / 2,
    plate_front_z + (cheek_reach - _SINK) / 2,
) * Box(
    cheek_width + _SINK,
    plateYMax - postYMin - 2 * cheek_inset,
    cheek_reach + _SINK,
)
body = body + cheek

hole_over = 0.1
lower_hole = Pos(tabFaceX - bossWidth / 2, lowerHoleY, lowerHoleZ) * Cylinder(
    lowerHoleDiameter / 2,
    bossWidth + hole_over,
    rotation=(0, 90, 0),
)
upper_hole = Pos(tabFaceX - postWidth / 2, upperHoleY, upperHoleZ) * Cylinder(
    upperHoleDiameter / 2,
    postWidth + hole_over,
    rotation=(0, 90, 0),
)
body = body - Compound([lower_hole, upper_hole])

# Preserve the seed rear clipping and suppress smooth-loft side overshoot.
envelope_x = 18.4707
body = body & Pos(0, (chordTopY + plateYMax) / 2, (rearZ + frontZ) / 2) * Box(
    envelope_x * 2,
    (plateYMax - chordTopY) + 80.0,
    (frontZ - rearZ) + 10.0,
)
result = body
assert result.is_valid, "invalid completed mount"
assert len(result.solids()) == 1, "mount must be one connected solid"
assert abs(result.bounding_box().min.Z - rearZ) < 0.001, "rear datum moved"
assert abs(result.bounding_box().max.Z - frontZ) < 0.001, "front datum moved"
