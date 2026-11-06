import math

from build123d import (
    Align,
    Axis,
    Cylinder,
    Plane,
    Polyline,
    Pos,
    Rot,
    loft,
    make_face,
    revolve,
)

bladeCount = 31.0
firstBladeAngle = 0.0
hubRadiusLe = 64.8
hubRadiusTe = 66.5
hubTeZ = 13.0
hubExtFrontZ = -1.0
tipRadius = 90.0
discFrontZ = -4.0
discRearZ = 20.0
boreDiameter = 40.0
frontLandRadius = 57.5
sleeveOuterRadius = 63.0
sleeveInnerRadius = 30.0
sleeveRearZ = 28.0
rootFilletRadius = 1.5
tipMinThickness = 0.8
meanSectionRadius = 77.4
hubInletAngle = 66.7
meanInletAngle = 70.1
tipInletAngle = 73.1
hubExitAngle = 40.4
meanExitAngle = 56.5
tipExitAngle = 64.6
hubCamber = hubInletAngle - hubExitAngle
meanCamber = meanInletAngle - meanExitAngle
tipCamber = tipInletAngle - tipExitAngle
hubStagger = (hubInletAngle + hubExitAngle) / 2
meanStagger = (meanInletAngle + meanExitAngle) / 2
tipStagger = (tipInletAngle + tipExitAngle) / 2
hubChord = 22.0
meanChord = 20.0
tipChord = 18.0
hubThicknessRatio = 0.08
meanThicknessRatio = 0.05
tipThicknessRatio = 0.035
hubMaxThickness = hubThicknessRatio * hubChord
meanMaxThickness = meanThicknessRatio * meanChord
tipMaxThickness = max(tipThicknessRatio * tipChord, tipMinThickness)
leRadius = 0.3
teThickness = 0.5

assert bladeCount >= 3, "infeasible: bladeCount must be at least 3"
assert sleeveRearZ > discRearZ, "infeasible: sleeveRearZ must be behind the disc rear face"
assert discRearZ > hubTeZ, "infeasible: disc rear face must be behind the hub trailing edge"
assert hubTeZ > hubExtFrontZ, "infeasible: hub trailing edge must be behind the extension"
assert hubExtFrontZ > discFrontZ, "infeasible: hub extension must be behind the front face"
assert tipRadius > meanSectionRadius, "infeasible: tipRadius must exceed the mean section"
assert meanSectionRadius > hubRadiusLe, "infeasible: mean section must be outside the hub"
assert hubRadiusLe > frontLandRadius, "infeasible: hub must be outside the front land"
assert frontLandRadius > boreDiameter / 2, "infeasible: front land must clear the bore"
assert sleeveOuterRadius > sleeveInnerRadius, "infeasible: sleeve wall must have thickness"
assert sleeveInnerRadius > boreDiameter / 2, "infeasible: sleeve bore must clear the drum bore"
assert sleeveOuterRadius < hubRadiusTe, "infeasible: sleeve must step in from the hub"
assert rootFilletRadius > 0, "infeasible: root fillet radius must be positive"
assert leRadius > 0, "infeasible: leading-edge radius must be positive"
assert teThickness > 0, "infeasible: trailing-edge thickness must be positive"
assert tipMinThickness > 0, "infeasible: tip thickness must be positive"
assert hubChord > meanChord > tipChord, "infeasible: chord must taper hub to tip"

# NACA 65 half-ordinates, normalised so the peak is exactly half of tmax.
NACA65 = (
    (0.0, 0.0),
    (0.005, 0.0772),
    (0.0075, 0.0932),
    (0.0125, 0.1169),
    (0.025, 0.1574),
    (0.05, 0.2177),
    (0.075, 0.2647),
    (0.1, 0.304),
    (0.15, 0.3666),
    (0.2, 0.4143),
    (0.25, 0.4503),
    (0.3, 0.476),
    (0.35, 0.4924),
    (0.4, 0.4996),
    (0.45, 0.4963),
    (0.5, 0.4812),
    (0.55, 0.453),
    (0.6, 0.4146),
    (0.65, 0.3682),
    (0.7, 0.3156),
    (0.75, 0.2584),
    (0.8, 0.1987),
    (0.85, 0.1385),
    (0.9, 0.081),
    (0.95, 0.0306),
    (1.0, 0.0),
)
NACA65_PEAK = max(value for _, value in NACA65)
CHORD_STATIONS = (
    0.0,
    0.004,
    0.01,
    0.02,
    0.04,
    0.07,
    0.11,
    0.16,
    0.22,
    0.3,
    0.4,
    0.5,
    0.6,
    0.7,
    0.78,
    0.85,
    0.91,
    0.96,
    1.0,
)


def _naca_half_frac(xc):
    if xc <= 0.0 or xc >= 1.0:
        return 0.0
    for index in range(len(NACA65) - 1):
        x0, y0 = NACA65[index]
        x1, y1 = NACA65[index + 1]
        if xc <= x1:
            span = (xc - x0) / (x1 - x0)
            return (y0 + span * (y1 - y0)) * (0.5 / NACA65_PEAK)
    return 0.0


def _release_xc(chord, tmax):
    hold = min(leRadius, tmax / 2)
    xc = leRadius / chord
    while xc < 0.55:
        if _naca_half_frac(xc) * tmax >= hold:
            return xc
        xc += 0.002
    return xc


def _half_thickness(xc, chord, tmax, release):
    hold = min(leRadius, tmax / 2)
    if xc <= 0.0:
        return 0.0
    if xc < release:
        distance = xc * chord
        if distance < leRadius:
            disc_height = 2 * leRadius * distance - distance * distance
            if disc_height > 0.0:
                return math.sqrt(disc_height)
            return 0.0
        return hold
    thickness = _naca_half_frac(xc) * tmax
    if xc > 0.7:
        blend = (xc - 0.7) / 0.3
        thickness = max(thickness, (teThickness / 2) * blend * blend)
    if xc >= 0.999:
        return teThickness / 2
    return thickness


def _section_points(chord, stagger, camber, tmax):
    """Closed loop in unwrapped (z, +tangential) coordinates."""
    phi = math.radians(camber)
    gamma = math.radians(stagger)
    release = _release_xc(chord, tmax)
    half = phi / 2
    sine_half = math.sin(half) if abs(phi) > 1e-08 else None

    def point(xc, side):
        thickness = _half_thickness(xc, chord, tmax, release)
        if sine_half is None:
            xi = xc * chord
            eta = 0.0
            psi = 0.0
        else:
            radius = (chord / 2) / sine_half
            arg = max(-1.0, min(1.0, (xc - 0.5) * 2 * sine_half))
            psi = math.asin(arg)
            xi = chord / 2 + radius * math.sin(psi)
            eta = -radius * math.cos(half) + radius * math.cos(psi)
        z = xi * math.cos(gamma) - eta * math.sin(gamma)
        tangential = xi * math.sin(gamma) + eta * math.cos(gamma)
        tangent_z = math.cos(psi - gamma)
        tangent_m = -math.sin(psi - gamma)
        normal_z = -tangent_m
        normal_m = tangent_z
        return (
            z + side * thickness * normal_z,
            tangential + side * thickness * normal_m,
        )

    loop = [point(xc, 1.0) for xc in reversed(CHORD_STATIONS)]
    loop.extend(point(xc, -1.0) for xc in CHORD_STATIONS[1:])
    return loop


def _centroid(points):
    area = 0.0
    z_moment = 0.0
    m_moment = 0.0
    count = len(points)
    for index in range(count):
        z0, m0 = points[index]
        z1, m1 = points[(index + 1) % count]
        cross = z0 * m1 - z1 * m0
        area += cross
        z_moment += (z0 + z1) * cross
        m_moment += (m0 + m1) * cross
    assert abs(area) > 1e-06, "infeasible: blade section has no area"
    return (z_moment / (3 * area), m_moment / (3 * area))


def _place(points, radius, z_stack):
    """Stack on the centroid. Negate tangential so the chord runs toward -theta."""
    z_c, m_c = _centroid(points)
    placed = []
    for z, tangential in points:
        placed.append((radius, m_c - tangential, z + z_stack - z_c))
    return placed


bore_radius = boreDiameter / 2
meridian = [
    (bore_radius, discFrontZ),
    (frontLandRadius, discFrontZ),
    (frontLandRadius, hubExtFrontZ),
    (hubRadiusLe, hubExtFrontZ),
    (hubRadiusLe, 0.0),
    (hubRadiusTe, hubTeZ),
    (sleeveOuterRadius, hubTeZ),
    (sleeveOuterRadius, sleeveRearZ),
    (sleeveInnerRadius, sleeveRearZ),
    (sleeveInnerRadius, discRearZ),
    (bore_radius, discRearZ),
]
disc = revolve(make_face(Plane.XZ * Polyline(*meridian, close=True)), axis=Axis.Z)

hub_section = _section_points(hubChord, hubStagger, hubCamber, hubMaxThickness)
hub_z = [z for z, _tangential in hub_section]
z_stack = _centroid(hub_section)[0] + (hubTeZ - 0.12) - max(hub_z)
assert min(hub_z) + z_stack - _centroid(hub_section)[0] > hubExtFrontZ, (
    "infeasible: blade leading edge crosses the front hub step"
)

stations = (
    (hubRadiusLe - 6.0, hubChord, hubStagger, hubCamber, hubMaxThickness),
    (hubRadiusLe, hubChord, hubStagger, hubCamber, hubMaxThickness),
    (meanSectionRadius, meanChord, meanStagger, meanCamber, meanMaxThickness),
    (tipRadius + 0.8, tipChord, tipStagger, tipCamber, tipMaxThickness),
)
faces = [
    make_face(
        Polyline(
            *_place(_section_points(chord, stagger, camber, tmax), radius, z_stack),
            close=True,
        )
    )
    for radius, chord, stagger, camber, tmax in stations
]
mean_placed = _place(
    _section_points(meanChord, meanStagger, meanCamber, meanMaxThickness),
    meanSectionRadius,
    z_stack,
)
leading = min(mean_placed, key=lambda point: point[2])
trailing = max(mean_placed, key=lambda point: point[2])
assert leading[1] > 0.0, "blade hand: leading edge must lead in +theta"
assert trailing[1] < 0.0, "blade hand: chord must run toward -theta from LE to TE"

blade = loft(faces, ruled=True)
n_blades = round(bladeCount)
blades = [Rot(0, 0, firstBladeAngle + index * 360.0 / bladeCount) * blade for index in range(n_blades)]
result = disc.fuse(*blades)

# Root fillet omitted: the kernel rejects 1.5 mm and 0.4 mm on the hub edges.
cut_margin = 3.0
cut_z = discFrontZ - cut_margin
cut_height = sleeveRearZ - discFrontZ + 2 * cut_margin
tip_keep = Pos(0, 0, cut_z) * Cylinder(tipRadius, cut_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
tip_outside = Pos(0, 0, cut_z) * Cylinder(tipRadius + 25.0, cut_height, align=(Align.CENTER, Align.CENTER, Align.MIN))
result = result - (tip_outside - tip_keep)
