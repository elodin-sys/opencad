"""Rotor-1 blisk: solid disc, front labyrinth, 29 circular-arc blades."""

import math

from build123d import (
    Axis,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    Rot,
    fillet,
    loft,
    make_face,
    revolve,
)

bladeCount = 29
bladePitch = 360.0 / bladeCount
bladeClockingAngle = 0.0
hubRadius = 57.6
hubRadiusTe = 61.0
frontFaceZ = -8.0
hubLeZ = 0.0
hubTeZ = 16.0
tipRadius = 90.0
meanRadius = 73.8
rootFilletRadius = 1.5
minTipThickness = 0.8
hubInletMetalAngle = 62.0
meanInletMetalAngle = 67.3
tipInletMetalAngle = 71.4
hubCamber = 32.7
meanCamber = 14.0
tipCamber = 7.6
hubExitMetalAngle = hubInletMetalAngle - hubCamber
meanExitMetalAngle = meanInletMetalAngle - meanCamber
tipExitMetalAngle = tipInletMetalAngle - tipCamber
hubStagger = (hubInletMetalAngle + hubExitMetalAngle) / 2.0
meanStagger = (meanInletMetalAngle + meanExitMetalAngle) / 2.0
tipStagger = (tipInletMetalAngle + tipExitMetalAngle) / 2.0
hubChord = 24.0
meanChord = 22.0
tipChord = 20.0
hubThicknessRatio = 0.08
meanThicknessRatio = 0.05
tipThicknessRatio = 0.035
tipMaxThickness = max(tipThicknessRatio * tipChord, minTipThickness)
leRadius = 0.3
teThickness = 0.5
boreRadius = 20.0
rearFaceZ = 24.0
spigotRadius = 50.0
sealArmInnerRadius = 44.0
sealToothTipRadius = 48.1
sealArmFrontZ = -18.0
sealToothCount = 3
sealArmLandRadius = 46.1
sealToothWidth = 0.8
sealToothPitch = 3.0
firstToothZ = -16.0

assert 17 <= bladeCount <= 47, "infeasible: bladeCount outside 17..47"
assert 0 < hubThicknessRatio <= 0.12, "infeasible: hubThicknessRatio outside (0, 0.12]"
assert tipRadius > hubRadiusTe, "infeasible: tipRadius"
assert boreRadius > 0, "infeasible: boreRadius"
assert leRadius > 0, "infeasible: leRadius"
assert teThickness > 0, "infeasible: teThickness"
assert rootFilletRadius >= 0, "infeasible: rootFilletRadius"
assert sealToothCount >= 1, "infeasible: sealToothCount"

# NACA 65-010 half-thickness ordinates (y/c), peak 0.04996 at 40% chord.
_NACA65_X = (
    0.0,
    0.005,
    0.0075,
    0.0125,
    0.025,
    0.05,
    0.075,
    0.1,
    0.15,
    0.2,
    0.25,
    0.3,
    0.35,
    0.4,
    0.45,
    0.5,
    0.55,
    0.6,
    0.65,
    0.7,
    0.75,
    0.8,
    0.85,
    0.9,
    0.95,
    1.0,
)
_NACA65_YT = (
    0.0,
    0.00772,
    0.00932,
    0.01169,
    0.01574,
    0.02177,
    0.02647,
    0.0304,
    0.03666,
    0.04143,
    0.04503,
    0.0476,
    0.04924,
    0.04996,
    0.04963,
    0.04812,
    0.0453,
    0.04146,
    0.03682,
    0.03156,
    0.02584,
    0.01987,
    0.01385,
    0.0081,
    0.00306,
    0.0,
)
_NACA65_HALF_MAX = 0.04996


def naca65_shape(x):
    """Half-thickness as a fraction of the half-maximum, 0 at the edges, 1 at 40% chord."""
    if x <= 0.0 or x >= 1.0:
        return 0.0
    for i in range(1, len(_NACA65_X)):
        if x <= _NACA65_X[i]:
            span = _NACA65_X[i] - _NACA65_X[i - 1]
            mix = (x - _NACA65_X[i - 1]) / span
            yt = _NACA65_YT[i - 1] + mix * (_NACA65_YT[i] - _NACA65_YT[i - 1])
            return yt / _NACA65_HALF_MAX
    return 0.0


def half_width(arc_s, arc_length, tmax):
    """Half-thickness along the camber arc: LE circle, then NACA-65, blunt TE."""
    x = 0.0 if arc_length <= 0.0 else min(1.0, max(0.0, arc_s / arc_length))
    body = 0.5 * tmax * naca65_shape(x)
    # The NACA tail necks below the blunt trailing edge; hold that thickness aft.
    if x > 0.45:
        body = max(body, 0.5 * teThickness)
    if arc_s <= leRadius:
        rise = leRadius - arc_s
        return math.sqrt(max(0.0, leRadius * leRadius - rise * rise))
    # The specified nose is blunter than the NACA ordinate; hold it until the body catches up.
    if x < 0.35 and body < leRadius:
        return leRadius
    return body


def section_loop(chord, tmax, camber_deg, stagger_deg):
    """Closed (y, z) airfoil. Index 0 is the nose. +y is +theta (pressure side)."""
    phi = math.radians(camber_deg)
    xi = math.radians(stagger_deg)
    radius = chord / (2.0 * math.sin(phi / 2.0))
    psi_le = -phi / 2.0
    arc_length = radius * phi
    stations = [leRadius * i / 4.0 for i in range(5)]
    for i in range(1, 13):
        stations.append(leRadius + (arc_length - leRadius) * i / 12.0)
    suction = []
    pressure = []
    for arc_s in stations:
        psi = psi_le + arc_s / radius
        u = chord / 2.0 + radius * math.sin(psi)
        n = radius * (math.cos(psi) - math.cos(phi / 2.0))
        normal_u = math.sin(psi)
        normal_n = math.cos(psi)
        width = half_width(arc_s, arc_length, tmax)
        for sign, bucket in ((1.0, suction), (-1.0, pressure)):
            ou = u + sign * width * normal_u
            on = n + sign * width * normal_n
            y = -ou * math.sin(xi) - on * math.cos(xi)
            z = ou * math.cos(xi) - on * math.sin(xi)
            bucket.append((y, z))
    te_mid = (
        (suction[-1][0] + pressure[-1][0]) / 2.0,
        (suction[-1][1] + pressure[-1][1]) / 2.0,
    )
    return suction + [te_mid] + list(reversed(pressure[1:]))


def area_centroid(pts):
    signed = 0.0
    cy = 0.0
    cz = 0.0
    count = len(pts)
    for i in range(count):
        y1, z1 = pts[i]
        y2, z2 = pts[(i + 1) % count]
        cross = y1 * z2 - y2 * z1
        signed += cross
        cy += (y1 + y2) * cross
        cz += (z1 + z2) * cross
    signed *= 0.5
    if abs(signed) < 1e-9:
        return 0.0, 0.0, 0.0
    return cy / (6.0 * signed), cz / (6.0 * signed), signed


def place_section(pts, z_stack):
    """Put the area centroid on y = 0 and z = z_stack. z_stack None anchors the foremost point at z = 0."""
    cy, cz, _area = area_centroid(pts)
    if z_stack is None:
        dz = -min(p[1] for p in pts)
        z_stack = cz + dz
    else:
        dz = z_stack - cz
    return [(y - cy, z + dz) for y, z in pts], z_stack


def root_junctions(part, z_limit):
    """Blade-hub edges on the cone, clear of the rim face and the front hub corner."""
    picked = []
    span = hubTeZ - hubLeZ
    for edge in part.edges():
        center = edge.center()
        z = center.Z
        if z <= hubLeZ + 0.5 or z >= z_limit - 0.5:
            continue
        radius = math.hypot(center.X, center.Y)
        r_hub = hubRadius + (z - hubLeZ) / span * (hubRadiusTe - hubRadius)
        if abs(radius - r_hub) > 0.7:
            continue
        length = edge.length
        # The LE and TE are thinner than 2 * rootFilletRadius; keep the long flanks.
        if length < 6.0 or length > 50.0:
            continue
        picked.append(edge)
    return picked


def lerp_loop(start, end, mix):
    return [((1.0 - mix) * y1 + mix * y2, (1.0 - mix) * z1 + mix * z2) for (y1, z1), (y2, z2) in zip(start, end)]


def section_face(pts, x_plane):
    _cy, _cz, signed = area_centroid(pts)
    loop = list(pts)
    if signed < 0.0:
        loop = list(reversed(loop))
        loop = [loop[-1], *loop[:-1]]
    # One edge per station so the ruled loft cannot twist the seam.
    wire = Polyline(*[(y, z) for y, z in loop], close=True)
    return Plane.YZ.offset(x_plane) * make_face(wire)


def disc_profile():
    pts = [
        (boreRadius, frontFaceZ),
        (boreRadius, rearFaceZ),
        (spigotRadius, rearFaceZ),
        (spigotRadius, hubTeZ),
        (hubRadiusTe, hubTeZ),
        (hubRadius, hubLeZ),
        (hubRadius, frontFaceZ),
        (sealArmLandRadius, frontFaceZ),
    ]
    i = sealToothCount - 1
    while i >= 0:
        # rewritten counts arrive as floats; range() rejects them
        center = firstToothZ + i * sealToothPitch
        aft = center + sealToothWidth / 2.0
        fore = center - sealToothWidth / 2.0
        pts.extend(
            [
                (sealArmLandRadius, aft),
                (sealToothTipRadius, aft),
                (sealToothTipRadius, fore),
                (sealArmLandRadius, fore),
            ]
        )
        i -= 1
    pts.extend(
        [
            (sealArmLandRadius, sealArmFrontZ),
            (sealArmInnerRadius, sealArmFrontZ),
            (sealArmInnerRadius, frontFaceZ),
        ]
    )
    return pts


def polygon_area(pts):
    signed = 0.0
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        signed += x1 * y2 - x2 * y1
    return 0.5 * signed


profile = disc_profile()
assert abs(polygon_area(profile)) > 100.0, "disc profile is degenerate"
disc = revolve(Plane.XZ * make_face(Polyline(*profile, close=True)), axis=Axis.Z)

hub_tmax = hubThicknessRatio * hubChord
mean_tmax = meanThicknessRatio * meanChord
hub_raw = section_loop(hubChord, hub_tmax, hubCamber, hubStagger)
mean_raw = section_loop(meanChord, mean_tmax, meanCamber, meanStagger)
tip_raw = section_loop(tipChord, tipMaxThickness, tipCamber, tipStagger)
hub_pts, z_stack = place_section(hub_raw, None)
mean_pts, _ = place_section(mean_raw, z_stack)
tip_pts, _ = place_section(tip_raw, z_stack)
assert abs(area_centroid(hub_pts)[2]) > 1.0, "hub section is degenerate"
assert abs(z_stack - hubLeZ) > 1.0, "hub stack collapsed onto the leading edge"

tip_y = max(abs(y) for y, _z in tip_pts)
tip_limit = tipRadius - 0.4
x_tip = math.sqrt(max(tip_limit * tip_limit - tip_y * tip_y, 0.0)) - 0.3
x_ext = tipRadius + 2.0
x_root = hubRadius - 6.0
assert x_root > boreRadius + 4.0, "blade root embed meets the bore"
assert meanRadius < x_tip < tipRadius < x_ext, "tip trim planes are out of order"

# 0.2 mm gap: a blade face on z = 16 merges into the rim rear annulus.
z_clip = hubTeZ - 0.2
# The exposed root is already off the hub metal; fade 20% toward the mean there.
hub_exposed = lerp_loop(hub_pts, mean_pts, 0.2)
sections = [
    section_face(hub_pts, x_root),
    section_face(hub_exposed, hubRadius),
    section_face(mean_pts, meanRadius),
    section_face(tip_pts, x_tip),
    section_face(tip_pts, x_ext),
]
assert all(4.0 < face.area < 80.0 for face in sections), "section face is not the airfoil"
raw_blade = loft(sections, ruled=True)
assert raw_blade.volume > 80.0, "loft collapsed"
# One axial cylinder clips the trailing edge and leaves a cylindrical tip.
trim = Pos(0, 0, (z_clip - 2.0) / 2.0) * Cylinder(tipRadius, z_clip + 2.0)
blade = raw_blade & trim
assert 80.0 < blade.volume < 8000.0, "trimmed blade volume"
pattern = []
i = 0
while i < bladeCount:
    pattern.append(Rot(0, 0, bladeClockingAngle + i * bladePitch) * blade)
    i += 1
result = disc
for item in pattern:
    result = result + item
junctions = root_junctions(result, z_clip)
if junctions:
    try:
        blended = fillet(junctions, rootFilletRadius)
    except (RuntimeError, ValueError):
        blended = None
    # A 1.5 mm fillet cannot fit where the airfoil is thinner than about 3 mm.
    if blended is not None and abs(blended.volume - result.volume) < 5000.0:
        result = blended
