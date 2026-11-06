import math

from build123d import (
    Align,
    Axis,
    Compound,
    Cylinder,
    Polyline,
    Pos,
    Rot,
    loft,
    make_face,
    revolve,
)

ringFrontZ = 58.0
ringRearZ = 80.0
casingOd = 200.0
flangeOd = 224.0
flangeThickness = 6.0
boltCount = 8.0
boltHoleDiameter = 5.5
boltPcd = 212.0
boltClockAngle = 0.0
outerFlowRadius = 90.0
stationBoreRadius = 90.25
outerFlowFrontZ = 59.0
outerFlowRearZ = 78.0
innerBandFrontZ = 59.0
hubFrontRadius = 66.5
hubRearRadius = 67.5
hubRampStartZ = 61.0
hubRampEndZ = 76.0
innerBoreRadius = 63.5
labyrinthToothCount = 2.0
labyrinthGrooveRadius = 64.5
labyrinthToothWidth = 1.0
labyrinthToothPitch = 4.0
labyrinthFrontZ = 62.0
labyrinthRearZ = 70.0
vaneCount = 47.0
vaneChord = 14.0
vaneLeZ = 61.0
inletMetalHub = 53.8
inletMetalMean = 48.9
inletMetalTip = 44.5
exitMetalAngle = -11.5
camberHub = inletMetalHub - exitMetalAngle
camberMean = inletMetalMean - exitMetalAngle
camberTip = inletMetalTip - exitMetalAngle
staggerHub = (inletMetalHub + exitMetalAngle) / 2.0
staggerMean = (inletMetalMean + exitMetalAngle) / 2.0
staggerTip = (inletMetalTip + exitMetalAngle) / 2.0
tmaxHub = 0.08
tmaxMean = 0.07
tmaxTip = 0.06
leRadius = 0.25
teThickness = 0.5
vaneMeanRadius = (hubFrontRadius + outerFlowRadius) / 2.0
vaneClockAngle = 0.0

assert casingOd < flangeOd, "infeasible: casingOd must be smaller than flangeOd"
assert casingOd / 2.0 > outerFlowRadius, "infeasible: casingOd does not clear the outer flow bore"
assert boltPcd / 2.0 + boltHoleDiameter / 2.0 < flangeOd / 2.0, "infeasible: bolt hole breaks the flange rim"
assert boltPcd / 2.0 - boltHoleDiameter / 2.0 > casingOd / 2.0, "infeasible: bolt hole cuts the casing barrel"
assert ringFrontZ < outerFlowFrontZ < ringFrontZ + flangeThickness, (
    "infeasible: outer flow front leaves the front flange"
)
assert ringRearZ - flangeThickness < outerFlowRearZ < ringRearZ, "infeasible: outer flow rear leaves the rear flange"
assert ringFrontZ + flangeThickness < ringRearZ - flangeThickness, "infeasible: the two flanges meet"
assert innerBandFrontZ > ringFrontZ, "infeasible: inner band covers the front mating face"
assert innerBandFrontZ < hubRampStartZ < hubRampEndZ < ringRearZ, "infeasible: hub ramp stations are out of order"
assert innerBoreRadius < labyrinthGrooveRadius < hubFrontRadius, (
    "infeasible: labyrinth groove radius leaves the band wall"
)
assert hubRearRadius > labyrinthGrooveRadius, "infeasible: hub flow surface meets the labyrinth"
assert hubRearRadius < outerFlowRadius, "infeasible: hub flow surface meets the outer bore"
assert 0.0 < labyrinthToothWidth < labyrinthToothPitch, "infeasible: labyrinth teeth overlap"
assert 1.5 < labyrinthToothCount < 2.5, "infeasible: the labyrinth is a two-tooth groove"
_lab_mid = (labyrinthFrontZ + labyrinthRearZ) / 2.0
_half_pitch = labyrinthToothPitch / 2.0
_half_tooth = labyrinthToothWidth / 2.0
_tooth_1_front = _lab_mid - _half_pitch - _half_tooth
_tooth_1_back = _lab_mid - _half_pitch + _half_tooth
_tooth_2_front = _lab_mid + _half_pitch - _half_tooth
_tooth_2_back = _lab_mid + _half_pitch + _half_tooth
assert innerBandFrontZ < labyrinthFrontZ < _tooth_1_front < _tooth_1_back, (
    "infeasible: labyrinth teeth do not fit in the groove"
)
assert _tooth_1_back < _tooth_2_front < _tooth_2_back < labyrinthRearZ < ringRearZ, (
    "infeasible: labyrinth teeth do not fit in the groove"
)
assert vaneLeZ + vaneChord * math.cos(math.radians(staggerTip)) <= hubRampEndZ, (
    "infeasible: vaneChord trailing edge passes the vane aft limit"
)
assert vaneChord > 2.0 * leRadius + teThickness, "infeasible: vaneChord cannot fit the nose and the trailing edge"
assert camberHub > 1.0 and camberMean > 1.0 and camberTip > 1.0, "infeasible: vane camber is degenerate"
assert vaneCount >= 3.0 and boltCount >= 3.0, "infeasible: pattern count"

# Seam sits between bolt holes so each end annulus stays one face.
_SEAM = math.radians(22.5)
# NACA 65-010 half-ordinates (x/c, yt/c). Half-thickness / tmax is yt/c divided by 0.10.
_NACA65 = (
    (0.0, 0.0),
    (0.005, 0.00772),
    (0.0075, 0.00932),
    (0.0125, 0.01169),
    (0.025, 0.01574),
    (0.05, 0.02177),
    (0.075, 0.02647),
    (0.10, 0.03040),
    (0.15, 0.03666),
    (0.20, 0.04143),
    (0.25, 0.04503),
    (0.30, 0.04760),
    (0.35, 0.04924),
    (0.40, 0.04996),
    (0.45, 0.04963),
    (0.50, 0.04812),
    (0.55, 0.04530),
    (0.60, 0.04146),
    (0.65, 0.03682),
    (0.70, 0.03156),
    (0.75, 0.02584),
    (0.80, 0.01987),
    (0.85, 0.01385),
    (0.90, 0.00807),
    (0.95, 0.00306),
    (1.0, 0.0),
)
_CHORD_STATIONS = (1.0, 0.92, 0.84, 0.76, 0.68, 0.58, 0.48, 0.38, 0.28, 0.20, 0.14)
_VANE_EMBED = 0.75


def _revolve_profile(rz_points):
    c, s = math.cos(_SEAM), math.sin(_SEAM)
    pts = [(r * c, r * s, z) for r, z in rz_points]
    return revolve(make_face(Polyline(*pts, close=True)), axis=Axis.Z)


def _hub_radius(z):
    if z <= hubRampStartZ:
        return hubFrontRadius
    if z >= hubRampEndZ:
        return hubRearRadius
    span = hubRampEndZ - hubRampStartZ
    return hubFrontRadius + (hubRearRadius - hubFrontRadius) * (z - hubRampStartZ) / span


def _naca65_half_frac(x):
    if x <= 0.0 or x >= 1.0:
        return 0.0
    for i in range(len(_NACA65) - 1):
        x0, y0 = _NACA65[i]
        x1, y1 = _NACA65[i + 1]
        if x <= x1:
            yt = y0 + (x - x0) / (x1 - x0) * (y1 - y0)
            return yt / 0.10
    return 0.0


def _thickness(x, tmax):
    t = 2.0 * _naca65_half_frac(x) * tmax
    if x >= 0.12:
        t = max(t, teThickness)
    return t


def _section_sz(stagger_deg, camber_deg, tmax_frac):
    """Closed (tangential, axial) airfoil: nose at z = vaneLeZ, area centroid on s = 0."""
    phi = math.radians(camber_deg)
    gamma = math.radians(stagger_deg)
    radius = vaneChord / (2.0 * math.sin(phi / 2.0))
    n_xi = (math.sin(gamma), math.cos(gamma))
    n_eta = (math.cos(gamma), -math.sin(gamma))
    tmax = tmax_frac * vaneChord

    def camber_sz(x):
        xi = x * vaneChord
        rad = math.sqrt(max(0.0, radius * radius - (xi - vaneChord / 2.0) ** 2))
        eta = -radius * math.cos(phi / 2.0) + rad
        return (xi * n_xi[0] + eta * n_eta[0], xi * n_xi[1] + eta * n_eta[1])

    def beta(x):
        xi = x * vaneChord
        rad = math.sqrt(max(1e-12, radius * radius - (xi - vaneChord / 2.0) ** 2))
        return gamma + math.atan(-(xi - vaneChord / 2.0) / rad)

    def side(x, sign):
        s, z = camber_sz(x)
        b = beta(x)
        n = (math.cos(b), -math.sin(b))
        ht = 0.5 * _thickness(x, tmax)
        return (s + sign * n[0] * ht, z + sign * n[1] * ht)

    b0 = beta(0.0)
    nose = camber_sz(0.0)
    tangent = (math.sin(b0), math.cos(b0))
    center = (nose[0] + leRadius * tangent[0], nose[1] + leRadius * tangent[1])
    nose_dir = (-tangent[0], -tangent[1])
    perp = (-nose_dir[1], nose_dir[0])
    arc = []
    n_arc = 9
    for i in range(n_arc):
        a = math.pi / 2.0 * (1.0 - 2.0 * i / (n_arc - 1))
        direction = (
            math.cos(a) * nose_dir[0] + math.sin(a) * perp[0],
            math.cos(a) * nose_dir[1] + math.sin(a) * perp[1],
        )
        arc.append((center[0] + leRadius * direction[0], center[1] + leRadius * direction[1]))
    pts = [side(x, 1.0) for x in _CHORD_STATIONS]
    pts.extend(arc)
    pts.extend(side(x, -1.0) for x in reversed(_CHORD_STATIONS))
    nose_pt = arc[n_arc // 2]
    area2 = cx = cy = 0.0
    n = len(pts)
    for i in range(n):
        s0, z0 = pts[i]
        s1, z1 = pts[(i + 1) % n]
        cross = s0 * z1 - s1 * z0
        area2 += cross
        cx += (s0 + s1) * cross
        cy += (z0 + z1) * cross
    ds = -cx / (3.0 * area2)
    dz = vaneLeZ - nose_pt[1]
    return [(s + ds, z + dz) for s, z in pts]


def _section_face(radius, stagger_deg, camber_deg, tmax_frac):
    pts = [(radius, s, z) for s, z in _section_sz(stagger_deg, camber_deg, tmax_frac)]
    return make_face(Polyline(*pts, close=True))


def _bolt_holes(z_start):
    holes = []
    radius = boltPcd / 2.0
    for i in range(round(boltCount)):
        ang = math.radians(boltClockAngle + 360.0 * i / boltCount)
        holes.append(
            Pos(radius * math.cos(ang), radius * math.sin(ang), z_start)
            * Cylinder(
                boltHoleDiameter / 2.0,
                flangeThickness + 0.1,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        )
    return holes


_r_flange = flangeOd / 2.0
_r_case = casingOd / 2.0
_z_front_back = ringFrontZ + flangeThickness
_z_rear_front = ringRearZ - flangeThickness
casing = _revolve_profile(
    [
        (stationBoreRadius, ringFrontZ),
        (_r_flange, ringFrontZ),
        (_r_flange, _z_front_back),
        (_r_case, _z_front_back),
        (_r_case, _z_rear_front),
        (_r_flange, _z_rear_front),
        (_r_flange, ringRearZ),
        (stationBoreRadius, ringRearZ),
        (stationBoreRadius, outerFlowRearZ),
        (outerFlowRadius, outerFlowRearZ),
        (outerFlowRadius, outerFlowFrontZ),
        (stationBoreRadius, outerFlowFrontZ),
    ]
)
casing = casing - Compound(_bolt_holes(ringFrontZ - 0.05) + _bolt_holes(_z_rear_front - 0.05))
band = _revolve_profile(
    [
        (_hub_radius(innerBandFrontZ), innerBandFrontZ),
        (_hub_radius(hubRampStartZ), hubRampStartZ),
        (_hub_radius(hubRampEndZ), hubRampEndZ),
        (_hub_radius(ringRearZ), ringRearZ),
        (innerBoreRadius, ringRearZ),
        (innerBoreRadius, labyrinthRearZ),
        (labyrinthGrooveRadius, labyrinthRearZ),
        (labyrinthGrooveRadius, _tooth_2_back),
        (innerBoreRadius, _tooth_2_back),
        (innerBoreRadius, _tooth_2_front),
        (labyrinthGrooveRadius, _tooth_2_front),
        (labyrinthGrooveRadius, _tooth_1_back),
        (innerBoreRadius, _tooth_1_back),
        (innerBoreRadius, _tooth_1_front),
        (labyrinthGrooveRadius, _tooth_1_front),
        (labyrinthGrooveRadius, labyrinthFrontZ),
        (innerBoreRadius, labyrinthFrontZ),
        (innerBoreRadius, innerBandFrontZ),
    ]
)
_vane = loft(
    [
        _section_face(hubFrontRadius - _VANE_EMBED, staggerHub, camberHub, tmaxHub),
        _section_face(vaneMeanRadius, staggerMean, camberMean, tmaxMean),
        _section_face(outerFlowRadius + _VANE_EMBED, staggerTip, camberTip, tmaxTip),
    ],
    ruled=True,
)
_pitch = 360.0 / vaneCount
_vanes = [Rot(0, 0, vaneClockAngle + i * _pitch) * _vane for i in range(round(vaneCount))]
result = casing.fuse(band, *_vanes)
