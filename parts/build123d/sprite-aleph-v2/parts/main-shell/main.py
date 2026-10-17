"""Open-bottom Sprite Aleph v2 main shell; identity assembly coordinates, mm."""

import math

from build123d import (
    Align,
    Bezier,
    Box,
    Circle,
    Compound,
    Cone,
    Cylinder,
    Location,
    Plane,
    Polyline,
    Rot,
    Spline,
    ThreePointArc,
    extrude,
    loft,
    make_face,
    mirror,
)

shellHeight = 249.3
footprint = 188.0
bodyHalfWidth = 30.0
bodyHalfHeight = 37.5
facetShoulderY = 23.4
facetCrownHalfWidth = 17.6
wallThickness = 2.0
innerWidth = 56.0
innerHeight = 71.0
prismaticEndZ = 125.0
roofEndZ = 22.0
pocketCeilingY = 35.5
pocketHalfWidth = 3.55
pocketStartZ = 9.45
rearTabEndZ = 28.95
rearScrewZ = 25.5
ribStartZ = 3.0
ribEndZ = 10.0
ribThickness = 1.5
ribInnerX = 26.5
ribSideHalfY = 20.5
ribKeelHalfX = 14.0
grooveInnerX = 28.0
grooveOuterX = 29.2
grooveBottomY = 16.0
grooveTopY = 20.0
wallEndZ = 202.0
bodySplitY = 22.0
grilleStartZ = 33.0
grilleEndZ = 93.0
grilleBottomY = -16.0
grilleTopY = 14.0
louverRearStartZ = 21.0
louverRearEndZ = 32.0
louverFrontStartZ = 94.0
louverFrontEndZ = 105.0
louverBottomY = -14.0
louverTopY = 14.0
screwBoreDiameter = 3.4
padDiameter = 9.0
padInnerX = 26.4
lowScrewY = 0.0
lowScrewZ = 14.0
highScrewY = -18.0
highScrewZ = 112.0
countersinkAngle = 90.0
sledPadX = 26.0
screwLength = 8.0
screwTipX = 22.0
insertEngagement = 4.0
armFairingWall = 0.82
armFairingHalfWidth = 6.0
armFairingRidgeZ = 25.0
nacelleOffset = 80.0
nacelleOuterDiameter = 17.09
nacelleRingZ = 30.0
hingeRibStartZ = 242.0
hingeRibEndZ = 246.0
hingeInnerX = 12.6
hingeOuterX = 16.2
hingeNotchWidth = 4.1
hingeRadius = 2.0
hingeSeatY = -2.28
hingeSeatZ = 244.0
hingeFloorY = -4.29
camEarClearRadius = 6.3
camEarClearHalfX = 12.4
servoLedgeZ = 214.85
widthStartZ = 202.0
widthEndZ = 249.3
tipHalfWidth = 13.1
widthEndSlope = -0.4
crownStartZ = 185.0
crownEndZ = 256.7
browY = 7.8
crownEndSlope = -0.72
keelStartZ = 125.0
keelEndZ = 249.3
tipKeelY = -22.9
keelEndSlope = 0.35
morphLength = 23.0
splitStartY = 15.0
splitLength = 14.0
fanDiameter = 38.0
fanCenterY = 3.6
fanCenterZ = 63.0
fanPlenumMin = 4.0
alephToSkinMin = 3.0
shellSlideTravel = 250.0
coverSlideTravel = 180.0
skirtBandInnerX = 26.4
skirtBandOuterX = 29.2
skirtBandBottomY = 14.8
skirtBandTopY = 22.2
cornerRadius = 7.0
grilleBarWidth = 1.2
grillePitch = 6.0
grilleBarOffset = 6.5
louverBarWidth = 1.2
roofUndersideY = 34.5
padTotalThickness = 3.6
slidePadGap = 0.4

assert 0 < wallThickness < cornerRadius, "infeasible: skin consumes corner blend"
assert 6.0 <= cornerRadius <= 8.0, "infeasible: body blend outside R6..R8"
assert 0 < ribThickness < wallThickness, "infeasible: rib thickness"
assert 0 < ribStartZ < ribEndZ < roofEndZ < prismaticEndZ < wallEndZ < shellHeight, "infeasible: axial order"
assert grooveInnerX < grooveOuterX < bodyHalfWidth, "infeasible: groove consumes skin"
assert grilleTopY < grooveBottomY < grooveTopY < bodySplitY, "infeasible: vent/groove separation"
assert 0 < grilleBarWidth < grillePitch, "infeasible: grille bars close openings"
assert 0 < louverBarWidth < min(louverRearEndZ - louverRearStartZ, louverFrontEndZ - louverFrontStartZ) / 3, (
    "infeasible: louver bars close openings"
)
assert 0 < screwBoreDiameter < 6.4 < padDiameter, "infeasible: countersink bearing land"
assert 0 < armFairingWall < armFairingHalfWidth, "infeasible: fairing wall"
assert padInnerX < bodyHalfWidth - wallThickness, "infeasible: pad is outside cavity"
assert hingeRadius < camEarClearRadius, "infeasible: camera ear relief is smaller than the pin seat"
assert 0 < camEarClearHalfX < min(hingeInnerX, tipHalfWidth), "infeasible: camera relief consumes the hinge or lip"


def _box(x0, x1, y0, y1, z0, z1):
    return Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN)).moved(Location((x0, y0, z0)))


def _hermite(z, z0, v0, z1, v1, m1):
    assert z <= z1 + 1e-6, "infeasible: analytic law extrapolated beyond endpoint"
    t = max(0.0, (z - z0) / (z1 - z0))
    return (2 * t**3 - 3 * t * t + 1) * v0 + (3 * t * t - 2 * t**3) * v1 + (t**3 - t * t) * (z1 - z0) * m1


def _laws(z):
    return (
        _hermite(z, widthStartZ, bodyHalfWidth, widthEndZ, tipHalfWidth, widthEndSlope),
        _hermite(z, crownStartZ, bodyHalfHeight, crownEndZ, browY, crownEndSlope),
        _hermite(z, keelStartZ, -bodyHalfHeight, keelEndZ, tipKeelY, keelEndSlope),
    )


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def _corners(z):
    w, c, k = _laws(z)
    shoulder = facetShoulderY * w / bodyHalfWidth
    cx = facetCrownHalfWidth * w / bodyHalfWidth
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


def _facet(z, inset=0.0):
    arcs = []
    for c, ns, nm, ne in _corners(z):
        arcs.append(
            [(c[0] + (cornerRadius - inset) * n[0], c[1] + (cornerRadius - inset) * n[1]) for n in (ns, nm, ne)]
        )
    edges = []
    for j, pts in enumerate(arcs):
        edges.extend([ThreePointArc(*pts), Polyline(pts[-1], arcs[(j + 1) % len(arcs)][0])])
    return make_face(edges).moved(Location((0, 0, z)))


# Exact rounded polygon in the prismatic region; moving crown/keel vertices
# continue to the wall end without scaling the side ordinates before z202.
_body_stations = (prismaticEndZ, 145.0, 165.0, crownStartZ, 195.0, wallEndZ)
_body_outer = extrude(_facet(0.0), amount=prismaticEndZ)
_body_outer += loft([_facet(z) for z in _body_stations], ruled=False)
_body_inner = extrude(_facet(-0.02, wallThickness), amount=prismaticEndZ + 0.02)
_body_inner += loft([_facet(z, wallThickness) for z in _body_stations], ruled=False)
fuselage = _body_outer - _body_inner
fuselage -= _box(-40, 40, bodySplitY, 45, roofEndZ, wallEndZ + 0.02)


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
        shoulder = facetShoulderY * w / bodyHalfWidth
        return (n[0] * w + n[1] * shoulder) / (n[0] * cs + n[1] * ss)
    if a >= a4:
        return h / ss
    cc = sc if a < a2 else kc
    dot = cc[0] * cs + cc[1] * ss
    return dot + math.sqrt(max(0.0, dot * dot - cc[0] ** 2 - cc[1] ** 2 + cornerRadius**2))


def _nose_xy(z, a):
    w, c, k = _laws(z)
    b = _smooth((z - widthStartZ) / morphLength)
    h = c if a < 0 else -k
    re = 1 / math.sqrt((math.cos(a) / w) ** 2 + (math.sin(a) / h) ** 2)
    r = (1 - b) * _facet_radius(z, a) + b * re
    return r * math.cos(a), -r * math.sin(a)


def _nose_point(z, a, inset=0.0):
    x, y = _nose_xy(z, a)
    if not inset:
        return x, y
    d = 0.00001
    p0, p1 = _nose_xy(z, a - d), _nose_xy(z, a + d)
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ll = math.hypot(dx, dy)
    # Compensate section-normal inset for the skin's longitudinal slope.
    # End derivatives are one-sided: W is never evaluated beyond its tip.
    za, zb = max(widthStartZ, z - 0.001), min(widthEndZ, z + 0.001)
    pa, pb = _nose_xy(za, a), _nose_xy(zb, a)
    vn = ((pb[0] - pa[0]) * dy - (pb[1] - pa[1]) * dx) / ((zb - za) * ll)
    correction = math.sqrt(1 + _smooth((z - widthStartZ) / 4.0) * vn * vn)
    return x + inset * correction * dy / ll, y - inset * correction * dx / ll


def _half_edges(z, inset=0.0, side=1):
    w, h, sc, kc, n, _, angles = _quarter(z)
    radius = cornerRadius - inset
    top = (side * (w - inset), w * math.tan(math.pi / 6))
    if z <= widthStartZ:
        p1 = (side * (sc[0] + radius), -sc[1])
        p2 = (side * (sc[0] + radius * n[0]), -sc[1] - radius * n[1])
        p3 = (side * (kc[0] + radius * n[0]), -kc[1] - radius * n[1])
        p4 = (side * kc[0], -h + inset)
        angle = math.atan2(n[1], n[0])
        m1 = (side * (sc[0] + radius * math.cos(angle / 2)), -sc[1] - radius * math.sin(angle / 2))
        a2 = (angle + math.pi / 2) / 2
        m2 = (side * (kc[0] + radius * math.cos(a2)), -kc[1] - radius * math.sin(a2))
        end = (0, -h + inset)
        return [
            Polyline(top, p1),
            ThreePointArc(p1, m1, p2),
            Polyline(p2, p3),
            ThreePointArc(p3, m2, p4),
            Polyline(p4, end),
        ], top
    limits = [-math.pi / 6, *angles, math.pi / 2]
    edges = []
    for j in range(len(limits) - 1):
        a, b = limits[j], limits[j + 1]
        points = [_nose_point(z, a + (b - a) * i / 8, inset) for i in range(9)]
        points = [(side * x, y) for x, y in points]
        tangents = []
        for aa in (a, b):
            pa, pb = _nose_point(z, aa - 0.0001, inset), _nose_point(z, aa + 0.0001, inset)
            vx, vy = side * (pb[0] - pa[0]), pb[1] - pa[1]
            length = math.hypot(vx, vy)
            tangents.append((vx / length, vy / length))
        edges.append(Spline(*points, tangents=tangents))
    tx, ty = _nose_point(z, limits[0], inset)
    return edges, (side * tx, ty)


def _nose_wall(z, inset=wallThickness):
    ro, rt = _half_edges(z)
    lo, lt = _half_edges(z, side=-1)
    ri, rit = _half_edges(z, inset)
    li, lit = _half_edges(z, inset, side=-1)
    return make_face([*ro, *lo, *ri, *li, Polyline(rt, rit), Polyline(lt, lit)]).moved(Location((0, 0, z)))


# One continuous, non-ruled wall loft. Analytic points are generated from the
# Hermite/radial laws, never traced from a CAD or mesh reference.
_nose_stations = (wallEndZ, 210.0, 218.0, 225.0, 235.0, 245.0, shellHeight)
_nose_skin = loft([_nose_wall(z) for z in _nose_stations], ruled=False)
# Exact cubic Bezier for S(z)=15*(1-smoothstep((z-202)/14)). The tool
# includes all y>S, including the constant zero split after z216.
_split_end = wallEndZ + splitLength
_split_curve = Bezier(
    (splitStartY, wallEndZ),
    (splitStartY, wallEndZ + splitLength / 3),
    (0, _split_end - splitLength / 3),
    (0, _split_end),
)
_split_face = Plane.YZ * make_face(
    [
        _split_curve,
        Polyline(
            (0, _split_end), (0, shellHeight + 0.02), (60, shellHeight + 0.02), (60, wallEndZ), (splitStartY, wallEndZ)
        ),
    ]
)
_split_tool = extrude(_split_face, amount=120, dir=(1, 0, 0)).moved(Location((-60, 0, 0)))
_nose_skin -= _split_tool
fuselage += _nose_skin
assert fuselage.is_valid, "body/nose skin union must be valid"

# V1 arm-plane seed. This is the sole source-to-assembly z conversion.
_seed_lift = 10.0
_seed_floor = -10.0
_seed_ridge = armFairingRidgeZ - _seed_lift
_arm_flare_s = 97.0


def _tent_hw(z):
    if z <= -10.0:
        return armFairingHalfWidth
    if z <= -5.0:
        t = (z + 10) / 5
        return armFairingHalfWidth * (1 - t) + 5.77 * t
    if z <= 2.0:
        t = (z + 5) / 7
        return 5.77 * (1 - t) + 4.67 * t
    if z <= 8.0:
        t = (z - 2) / 6
        return 4.67 * (1 - t) + 2.97 * t
    t = min(1.0, (z - 8) / (_seed_ridge - 8))
    return 2.97 * (1 - t) + 0.35 * t


def _nac_radius(z):
    t = (z - _seed_floor) / (nacelleRingZ - _seed_lift - _seed_floor)
    r0 = footprint / 2 - nacelleOffset
    a, b = -5.40691608, 0.24735126
    c = nacelleOuterDiameter / 2 - r0 - a - b
    return max(0.02, r0 + a * t * t + b * t**3 + c * t**4)


def _arm_plan(z, width, radius, root=28.0, root_blend=False):
    sn = math.sqrt(2) * nacelleOffset
    jx = sn - radius * 0.8
    jy = radius * math.sqrt(1 - 0.8**2)
    shoulder = max(root + 0.1, min(_arm_flare_s, jx - 4))
    if root_blend:
        start = [
            Polyline((root, -width), (root, width)),
            Spline((root, width), (32, width + 7.58), (35, width + 1.85), (37, width + 0.40), (40, width)),
            Polyline((40, width), (shoulder, width)),
        ]
    else:
        start = [Polyline((root, -width), (root, width), (shoulder, width))]
    edges = start + [
        Spline((shoulder, width), (shoulder + 0.45 * (jx - shoulder), width + 0.2 * (jy - width)), (jx, jy)),
        ThreePointArc((jx, jy), (sn + radius, 0), (jx, -jy)),
        Spline((jx, -jy), (shoulder + 0.45 * (jx - shoulder), -width - 0.2 * (jy - width)), (shoulder, -width)),
        Polyline((shoulder, -width), (root, -width)),
    ]
    return make_face(edges).moved(Location((0, 0, z + _seed_lift)))


_arm_outer = loft(
    [
        _arm_plan(z, max(_tent_hw(z), 0.06), _nac_radius(z), root_blend=True)
        for z in (_seed_floor, -5.0, 2.0, 8.0, 13.0, _seed_ridge)
    ],
    ruled=False,
)
_sn = math.sqrt(2) * nacelleOffset
_arm_outer += loft(
    [Circle(_nac_radius(z)).moved(Location((_sn, 0, z + _seed_lift))) for z in (15.0, 20.0, 25.0, 30.0, 34.0, 36.8759)],
    ruled=False,
)
_arm_outer += loft(
    [
        _arm_plan(z, 0.04, _nac_radius(z) - 0.08, root=root)
        for z, root in (
            (14.8, 95.5),
            (15.76, 98.6887),
            (18.0, 101.5088),
            (20.0, 103.2072),
            (23.0, 105.274),
            (25.0, 106.4485),
            (27.0, _sn - _nac_radius(27.0) + 0.2),
        )
    ],
    ruled=False,
)
# Retained v1 open fairing cavity, bottom web and rising root ridge.
_arm_inner = loft(
    [
        _arm_plan(z, width, _nac_radius(z) - armFairingWall)
        for z, width in (
            (_seed_floor, armFairingHalfWidth - armFairingWall),
            (-5.0, 5.77 - armFairingWall),
            (2.0, 4.67 - armFairingWall),
            (8.0, 2.12),
            (12.0, 0.534),
            (13.1842, 0.02),
        )
    ],
    ruled=False,
)
_arm_inner += loft(
    [
        Circle(max(_nac_radius(z) - armFairingWall - 0.006 * max(0, z - 14), 0.04)).moved(
            Location((_sn, 0, z + _seed_lift))
        )
        for z in (13.1842, 15.0, 20.0, 25.0, 30.0, 34.0, 35.4)
    ],
    ruled=False,
)
_web_trim = Box(250, 80, 0.92, align=(Align.CENTER, Align.CENTER, Align.MIN)).moved(Location((_sn / 2, 0, -0.12)))
_web_trim -= Cylinder(
    _nac_radius(_seed_floor) - armFairingWall, 1.2, align=(Align.CENTER, Align.CENTER, Align.MIN)
).moved(Location((_sn, 0, -0.15)))
_arm_inner -= _web_trim
_one_fairing = _arm_outer - _arm_inner


def _root_envelope(z):
    w = -0.52 * (z - _seed_ridge)
    upper = [(32 + j * 8 / 6, w + 0.0148 * (8 - j * 8 / 6) ** 3) for j in range(7)]
    return make_face([Spline(*upper), Polyline(upper[-1], (40, -12), (32, -12), upper[0])]).moved(
        Location((0, 0, z + _seed_lift))
    )


_root_cap = loft([_root_envelope(z) for z in (13.0, 24.0)], ruled=False)
_root_gate_face = Plane.YZ * make_face(Polyline((-1.56, 22), (20, 22), (20, 34), (4.68, 34), (-1.56, 22)))
_root_gate = extrude(_root_gate_face, amount=20, dir=(1, 0, 0)).moved(Location((28, 0, 0)))
_root_cap &= _root_gate
_body_clip = extrude(_facet(0.0, 0.3), amount=60.0)
for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1)):
    angle = math.degrees(math.atan2(sy, sx))
    arm = _one_fairing if sx * sy > 0 else mirror(_one_fairing, about=Plane.XZ)
    cap = _root_cap if sx * sy > 0 else mirror(_root_cap, about=Plane.XZ)
    fuselage += (Rot(0, 0, angle) * (arm + cap)) - _body_clip

# Clear the cover skin at the upper arm roots, inside its grown body outline.
# The existing skin is below y22 here; the lower fairings never enter this tool.
_root_clear_x = bodyHalfWidth + 0.2
_root_clear_y = bodyHalfHeight + 0.2
_root_clear_shoulder = (38.17 - 0.7509 * _root_clear_x) / 0.6604
_root_clear_crown_x = (38.17 - 0.6604 * _root_clear_y) / 0.7509
_root_clear_face = make_face(
    Polyline(
        (_root_clear_x, 22.2),
        (_root_clear_x, _root_clear_shoulder),
        (_root_clear_crown_x, _root_clear_y),
        (-_root_clear_crown_x, _root_clear_y),
        (-_root_clear_x, _root_clear_shoulder),
        (-_root_clear_x, 22.2),
        (_root_clear_x, 22.2),
    )
).moved(Location((0, 0, roofEndZ)))
_root_clear_tool = extrude(_root_clear_face, amount=shellHeight - roofEndZ + 0.02)
fuselage -= _root_clear_tool

# Clip the normal-offset rib to straight bearing segments, clear of the sled
# shoulders and facets. Cutting bounds overrun only the existing rib stock.
assert 0 < ribSideHalfY < abs(_corners(0.0)[0][0][1]), "infeasible: side rib reaches a shoulder arc"
assert 0 < ribKeelHalfX < _corners(0.0)[7][0][0], "infeasible: keel rib reaches a facet blend"
_rib_outer = extrude(_facet(ribStartZ, wallThickness - 0.02), amount=ribEndZ - ribStartZ)
_rib_void = extrude(_facet(ribStartZ - 0.02, wallThickness + ribThickness), amount=ribEndZ - ribStartZ + 0.04)
_rib_side_keep = _box(ribInnerX - 0.02, bodyHalfWidth, -ribSideHalfY, ribSideHalfY, ribStartZ - 0.02, ribEndZ + 0.02)
_rib_keel_keep = _box(
    -ribKeelHalfX,
    ribKeelHalfX,
    -bodyHalfHeight,
    -bodyHalfHeight + wallThickness + ribThickness + 0.02,
    ribStartZ - 0.02,
    ribEndZ + 0.02,
)
_rib_keep = Compound(children=[_rib_side_keep, mirror(_rib_side_keep, about=Plane.YZ), _rib_keel_keep])
fuselage += (_rib_outer - _rib_void) & _rib_keep

# Retained thickened crown shoulder and open-forward round-ended glue pocket.
_roof_pad = _box(-bodyHalfWidth, bodyHalfWidth, roofUndersideY, bodyHalfHeight - 0.2, 0.0, roofEndZ) & _body_outer
fuselage += _roof_pad
_pr = pocketHalfWidth
_pocket_shoulder = pocketStartZ + _pr
_pocket_face = Plane.XZ * make_face(
    [
        Polyline((_pr, roofEndZ + 0.02), (_pr, _pocket_shoulder)),
        ThreePointArc((_pr, _pocket_shoulder), (0, pocketStartZ), (-_pr, _pocket_shoulder)),
        Polyline((-_pr, _pocket_shoulder), (-_pr, roofEndZ + 0.02), (_pr, roofEndZ + 0.02)),
    ]
)
_pocket_face = _pocket_face.moved(Location((0, roofUndersideY - 0.02, 0)))
fuselage -= extrude(_pocket_face, amount=pocketCeilingY - roofUndersideY + 0.02, dir=(0, 1, 0))

# Circular inward pads, united to the skin and (at z14) the bearing ring.
_pad_length = bodyHalfWidth - wallThickness - padInnerX
_fastener_tools = []
for _y, _z in ((lowScrewY, lowScrewZ), (highScrewY, highScrewZ)):
    _pad = (
        Rot(0, 90, 0) * Cylinder(padDiameter / 2, _pad_length + 0.02, align=(Align.CENTER, Align.CENTER, Align.MIN))
    ).moved(Location((padInnerX, _y, _z)))
    fuselage += _pad + mirror(_pad, about=Plane.YZ)
    _bore = (
        Rot(0, 90, 0)
        * Cylinder(
            screwBoreDiameter / 2, bodyHalfWidth - padInnerX + 0.04, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
    ).moved(Location((padInnerX - 0.02, _y, _z)))
    _sink_r = 3.2
    _sink_tan = math.tan(math.radians(countersinkAngle / 2))
    _sink_depth = (_sink_r - screwBoreDiameter / 2) / _sink_tan
    _sink = (
        Rot(0, 90, 0)
        * Cone(
            screwBoreDiameter / 2,
            _sink_r + 0.02 * _sink_tan,
            _sink_depth + 0.02,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    ).moved(Location((bodyHalfWidth - _sink_depth, _y, _z)))
    _fastener_tools.extend([_bore, _sink, mirror(_bore, about=Plane.YZ), mirror(_sink, about=Plane.YZ)])
fuselage -= Compound(children=_fastener_tools)

# Cut the spaces between the retained seed bars, clipping the ten grille
# centres to the new sixty-mm opening. Nine complete bars and the 0.1-mm
# terminal stub at z92.9..93 are intentional; gross fan coverage is not porosity.
_vent_tools = []


def _vent_spaces(z0, z1, y0, y1, centres, width):
    previous = z0
    for centre in centres:
        before = max(z0, centre - width / 2)
        after = min(z1, centre + width / 2)
        if before > previous:
            _vent_tools.append(
                _box(-bodyHalfWidth - 0.02, -bodyHalfWidth + wallThickness + 0.02, y0, y1, previous, min(before, z1))
            )
        previous = max(previous, after)
    if previous < z1:
        _vent_tools.append(_box(-bodyHalfWidth - 0.02, -bodyHalfWidth + wallThickness + 0.02, y0, y1, previous, z1))


_vent_spaces(
    grilleStartZ,
    grilleEndZ,
    grilleBottomY,
    grilleTopY,
    [grilleStartZ + grilleBarOffset + i * grillePitch for i in range(10)],
    grilleBarWidth,
)
for _z0, _z1 in ((louverRearStartZ, louverRearEndZ), (louverFrontStartZ, louverFrontEndZ)):
    _vent_spaces(_z0, _z1, louverBottomY, louverTopY, [_z0 + (_z1 - _z0) * i / 3 for i in (1, 2)], louverBarWidth)
fuselage -= Compound(children=_vent_tools)

# The rail channel and the inboard skirt sweep are independent tools. The
# latter removes the small inward excursion of the rounded upper side corner.
_groove = _box(grooveInnerX - 0.02, grooveOuterX, grooveBottomY, grooveTopY, roofEndZ, wallEndZ + 0.02)
_skirt = _box(skirtBandInnerX - 0.02, grooveInnerX, skirtBandBottomY, skirtBandTopY, roofEndZ, wallEndZ)
fuselage -= Compound(children=[_groove, mirror(_groove, about=Plane.YZ), _skirt, mirror(_skirt, about=Plane.YZ)])


# Same analytic envelope as the single wall loft, used only to trim the
# locally retained nose interfaces. It never extends W beyond shellHeight.
def _nose_envelope_face(z, inset=0.0):
    right, rt = _half_edges(z, inset)
    left, lt = _half_edges(z, inset, side=-1)
    return make_face([*right, *left, Polyline(rt, lt)]).moved(Location((0, 0, z)))


# Keep trimming faces inside the existing skin; exact coincidence between two
# independently parameterized lofts produces tessellation slivers at the keel.
_nose_envelope = loft([_nose_envelope_face(z, 0.1) for z in _nose_stations], ruled=False)
# Source glue ledges are retained on the lower shell, following its new keel;
# the VTX joint in empty space above the split does not create a shell boss.
_servo_step = extrude(_nose_wall(servoLedgeZ, wallThickness + 1.0), amount=-1.5)
_servo_step &= _box(-40, 40, -40, -22.5, servoLedgeZ - 1.5, servoLedgeZ + 0.02)
fuselage += _servo_step & _nose_envelope
_vtx_start = 203.0
_vtx_ledge = 212.0 - 4.05
_vtx_step = extrude(_nose_wall(_vtx_ledge, wallThickness + 1.0), amount=_vtx_start - _vtx_ledge)
_vtx_step &= _box(-40, 40, -40, -12, _vtx_start, _vtx_ledge + 0.02)
fuselage += _vtx_step & _nose_envelope

# The inherited camera U-rib inner fit, inline from the v1 local feature seed
# at source z235 (assembly z245). The outer stock is trimmed to the v2 nose.
_camera_inner = [(12.5, 0), (12.5, -4.5), (12.5, -9), (11.999, -13.5), (9.596, -18), (5.18, -21.375), (0, -22.5)]
_camera_right = _camera_inner[:4]
_camera_back = _camera_inner[3:] + [(-x, y) for x, y in reversed(_camera_inner[3:-1])]
_camera_left = [(-x, y) for x, y in reversed(_camera_inner[:4])]
_camera_void_face = make_face(
    [Spline(*_camera_right), Spline(*_camera_back), Spline(*_camera_left), Polyline(_camera_left[-1], _camera_right[0])]
).moved(Location((0, 0, hingeRibStartZ - 0.04)))
_camera_void = extrude(_camera_void_face, amount=hingeRibEndZ - hingeRibStartZ + 0.08)
_camera_stock = (_nose_envelope & _box(-20, 20, -35, 0, hingeRibStartZ - 0.02, hingeRibEndZ + 0.02)) - _camera_void
fuselage += _camera_stock
_hinge_z0 = hingeSeatZ - hingeNotchWidth / 2 - 0.0415
_hinge_back = hingeSeatY + 0.12303
_hinge_opening = _box(
    -hingeOuterX - wallThickness, hingeOuterX + wallThickness, _hinge_back, 0.05, _hinge_z0, _hinge_z0 + hingeNotchWidth
)
_hinge_seat = (Rot(0, 90, 0) * Cylinder(hingeRadius, 2 * (hingeOuterX + wallThickness))).moved(
    Location((0, hingeSeatY, hingeSeatZ))
)
# The camera plate ears rotate about X inside the nose. Stop the relief at
# its specified X faces so the outer lip and the outboard hinge seats remain.
_cam_ear_relief = (Rot(0, 90, 0) * Cylinder(camEarClearRadius, 2 * camEarClearHalfX)).moved(
    Location((0, hingeSeatY, hingeSeatZ))
)
fuselage -= Compound(children=[_hinge_opening, _hinge_seat, _cam_ear_relief])
assert (fuselage & _cam_ear_relief).volume < 0.00001, "camera ear swept disc contains shell material"

# Construction-side exact B-rep check of the entire forbidden band, with only
# the two specified lips subtracted from each test volume. The assembly's
# independent exported-STEP and sled sweep gates remain separate obligations.
_band = _box(skirtBandInnerX, skirtBandOuterX, skirtBandBottomY, skirtBandTopY, roofEndZ, wallEndZ)
_lips = Compound(
    children=[
        _box(grooveInnerX, grooveOuterX, skirtBandBottomY, grooveBottomY, roofEndZ, wallEndZ),
        _box(grooveInnerX, grooveOuterX, grooveTopY, skirtBandTopY, roofEndZ, wallEndZ),
    ]
)
_forbidden_band = _band - _lips
for _band_tool in (_forbidden_band, mirror(_forbidden_band, about=Plane.YZ)):
    assert (fuselage & _band_tool).volume < 0.00001, "skirt band contains forbidden shell material"
assert (fuselage & _split_tool).volume < 0.00001, "nose material exceeds the analytic split"

# Geometric inclusion of all required section profiles, both outer and normal
# offset inner outlines. This is a station check, not a translated assembly
# sweep or a certification of the continuous interpolated loft between them.
for _inset in (0.0, wallThickness):
    _previous = None
    for _station in _nose_stations:
        _profile = extrude(
            _nose_envelope_face(_station, _inset).moved(Location((0, 0, -_station))),
            amount=0.1,
            dir=(0, 0, 1),
        )
        assert _profile.is_valid, f"invalid nose profile at {_station}, inset {_inset}"
        if _previous is not None:
            assert (_profile - _previous).volume < 0.00001, f"nose profiles not nested at {_station}, inset {_inset}"
        _previous = _profile

result = fuselage
assert result.is_valid, "shell must be a valid B-rep"
assert len(result.solids()) == 1, "shell must be one connected solid"
assert abs(result.bounding_box().min.Z) < 0.05, "open-rim datum moved"
assert abs(result.bounding_box().max.Z - shellHeight) < 0.05, "nose tip moved"

for _probe in ((0, 0, 1), (0, 6, 12), (0, 0, 63), (0, 0, 160)):
    assert not result.is_inside(_probe), "open sleeve centre must remain void"

for _side in (-1, 1):
    for _probe in ((26.5, 27.0, 23.5), (27.0, 26.5, 24.5), (25.0, -25.0, 6.5), (25.0, 25.0, 6.5)):
        assert not result.is_inside((_side * _probe[0], _probe[1], _probe[2])), "slide clearance is obstructed"
    for _probe in ((29.5, 28.5, 23.5), (27.2, 15.0, 6.5), (27.2, -15.0, 6.5), (8.0, -34.7, 6.5)):
        assert result.is_inside((_side * _probe[0], _probe[1], _probe[2])), "retained fairing or rib stock is missing"
    for _probe in ((11.2, -3.0, 249.0), (11.8, -5.0, 247.0), (12.2, -7.0, 245.0)):
        assert not result.is_inside((_side * _probe[0], _probe[1], _probe[2])), "camera ear clearance is obstructed"
    for _probe in ((13.0, -6.0, 247.0), (13.5, -7.5, 245.0), (12.75, -3.0, 249.0)):
        assert result.is_inside((_side * _probe[0], _probe[1], _probe[2])), "outer camera-tip wall is missing"
