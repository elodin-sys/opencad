"""Integral Sprite Aleph v2 sled in the carbon-frame assembly datum, mm.

The roof edge and upper-body facets use the measured shell clearance limits.
No shell or purchased bodies are output.
"""

import math

from build123d import Align, Box, Compound, Cone, Cylinder, Polyline, Pos, ThreePointArc, extrude, loft, make_face

baseWidth = 55.4
baseDepth = 69.3
baseThickness = 3.0
baseGap = 0.3
roofLipUndersideY = 34.5
shellInnerFacetOffset = 35.98
powerHoleDiameter = 27.0
clampOffset = 15.0
wallInnerX = 21.6
wallOuterX = 25.6
wallYMin = -27.0
wallYMax = 25.0
wallStartZ = 11.0
wallEndZ = 117.0
columnHalfY = 15.0
wallHoleDiameter = 2.5
wallHoleYLow = -24.75
wallHoleYHigh = 21.75
wallHoleZAft = 22.0
wallHoleZFore = 104.0
slideGap = 0.4
facetClipY = 24.6
flangeXMin = 8.0
flangeYMin = -31.0
flangeYMax = -28.5
keelChannelHeight = 20.0
trayHalfWidth = 25.5
trayFloorBottom = -25.0
trayFloorTop = -22.5
trayStartZ = 117.0
sledHeight = 202.0
lipInnerX = 24.0
lipTopY = -12.5
strapZAft = 145.0
strapZFore = 178.0
bulkheadEndZ = 119.0
bulkheadTopY = 19.5
notchXMin = -22.0
notchXMax = -6.0
notchBottomY = 10.0
pocketHalfY = 12.0
pocketStartZ = 109.0
padFaceX = 26.0
padSize = 9.0
insertHoleDiameter = 4.0
insertHoleDepth = 4.2
padLowZ = 14.0
padHighZ = 112.0
padHighY = -18.0
lowPortEndZ = 19.0
highPortStartZ = 107.5
ringInnerX = 26.5
ringTopZ = 10.0
shellPadInnerX = 26.4
bodyHalfWidth = 30.0
bodySideY = 23.4
bodyCrownX = 17.6
skinThickness = 2.0
keelStartZ = 125.0
keelStartY = -37.5
keelEndZ = 249.3
keelEndY = -22.9
keelEndSlope = 0.35
wallThickness = wallOuterX - wallInnerX
trayFloorThickness = trayFloorTop - trayFloorBottom
clampDiameter = 3.4
clampHeadDiameter = 6.0
clampHeadAngle = 90.0
strapSlotLength = 46.0
strapSlotWidth = 3.0
pocketWall = 1.2

# R7 is the construction used by the supplied v1 shell source; R6..R8 remains
# unspecified in the v2 text. Circular blends preserve true planar offsets.
bodyBlendRadius = 7.0
cutOverrun = 0.02

assert baseWidth > powerHoleDiameter > 0, "infeasible: power opening consumes base"
assert baseDepth > 2 * clampOffset > 0, "infeasible: clamp pattern outside base"
assert 0 < baseThickness < wallStartZ < wallEndZ <= trayStartZ < bulkheadEndZ < sledHeight, "infeasible: axial ordering"
assert wallInnerX < wallOuterX < padFaceX < ringInnerX, "infeasible: wall or ring clearance"
assert trayFloorBottom < trayFloorTop < lipTopY, "infeasible: tray section"
assert 0 < lipInnerX < trayHalfWidth, "infeasible: lip consumes floor"
assert 0 < strapSlotWidth < strapZFore - strapZAft, "infeasible: strap slots close or overlap"
assert 0 < strapSlotLength < 2 * lipInnerX, "infeasible: strap slots remove bridges"
assert trayStartZ < strapZAft - strapSlotWidth / 2, "infeasible: aft strap cuts bulkhead"
assert strapZFore + strapSlotWidth / 2 < sledHeight, "infeasible: forward strap cuts end"
assert 0 < pocketWall < min((notchXMax - notchXMin) / 2, trayStartZ - pocketStartZ), "infeasible: pocket cavity closes"
assert 0 < insertHoleDepth < padFaceX - wallInnerX, "infeasible: insert breaks through backing"
assert skinThickness + slideGap < bodyBlendRadius, "infeasible: blend offset radius"
assert 0 < roofLipUndersideY - slideGap < baseDepth, "infeasible: roof cut consumes base"
assert shellInnerFacetOffset - slideGap > 0.7509 * wallOuterX + 0.6604 * abs(wallHoleYLow), (
    "infeasible: measured facet shortens the lower Aleph hole axes"
)


def box(x0, x1, y0, y1, z0, z1):
    """Stock in assembly axes, never a face-local coordinate system."""
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN,) * 3)


def rounded_outline(vertices, radius, inset=0.0, z=0.0):
    """Circular tangent blends of a convex CCW polygon, then normal inset."""
    arcs = []
    for j, p in enumerate(vertices):
        a, b = vertices[j - 1], vertices[(j + 1) % len(vertices)]
        u, v = (a[0] - p[0], a[1] - p[1]), (b[0] - p[0], b[1] - p[1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        u, v = (u[0] / lu, u[1] / lu), (v[0] / lv, v[1] / lv)
        theta = math.acos(u[0] * v[0] + u[1] * v[1])
        bisector = (u[0] + v[0], u[1] + v[1])
        scale = radius / (math.sin(theta / 2) * math.hypot(*bisector))
        c = (p[0] + scale * bisector[0], p[1] + scale * bisector[1])
        tangent = radius / math.tan(theta / 2)
        ns = ((p[0] + tangent * u[0] - c[0]) / radius, (p[1] + tangent * u[1] - c[1]) / radius)
        ne = ((p[0] + tangent * v[0] - c[0]) / radius, (p[1] + tangent * v[1] - c[1]) / radius)
        diagonal = (p[0] - c[0], p[1] - c[1])
        length = math.hypot(*diagonal)
        nm = (diagonal[0] / length, diagonal[1] / length)
        arcs.append([(c[0] + (radius - inset) * n[0], c[1] + (radius - inset) * n[1]) for n in (ns, nm, ne)])
    edges = []
    for j, points in enumerate(arcs):
        edges.extend([ThreePointArc(*points), Polyline(points[-1], arcs[(j + 1) % len(arcs)][0])])
    return Pos(0, 0, z) * make_face(edges)


def body_vertices(width, crown, keel):
    side = bodySideY * width / bodyHalfWidth
    shoulder = bodyCrownX * width / bodyHalfWidth
    return [
        (width, -side),
        (width, side),
        (shoulder, crown),
        (-shoulder, crown),
        (-width, side),
        (-width, -side),
        (-shoulder, keel),
        (shoulder, keel),
    ]


# Preserve the original keel edge and crown arcs; trim only the roof-facing cap.
baseInset = skinThickness + baseGap
baseHalfDepth = baseDepth - (roofLipUndersideY - slideGap)
baseOutline = rounded_outline(
    body_vertices(baseWidth / 2 + baseInset, baseHalfDepth + baseInset, -baseHalfDepth - baseInset),
    bodyBlendRadius,
    baseInset,
)
base = extrude(baseOutline, amount=baseThickness)
base -= box(
    -baseWidth / 2 - cutOverrun,
    baseWidth / 2 + cutOverrun,
    roofLipUndersideY - slideGap,
    baseHalfDepth + cutOverrun,
    -cutOverrun,
    baseThickness + cutOverrun,
)


def hermite(z, z0, v0, z1, v1, end_slope):
    """Specified constant-then-Hermite law, with no extrapolation."""
    assert z <= z1, "infeasible: mating law evaluated past its domain"
    if z <= z0:
        return v0
    t = (z - z0) / (z1 - z0)
    return (2 * t**3 - 3 * t**2 + 1) * v0 + (3 * t**2 - 2 * t**3) * v1 + (t**3 - t**2) * (z1 - z0) * end_slope


def mating_outline(z):
    """Only the external mating tool; it never becomes a printed shell."""
    width = hermite(z, 202.0, bodyHalfWidth, 249.3, 13.1, -0.40)
    crown = hermite(z, 185.0, 37.5, 256.7, 7.8, -0.72)
    keel = hermite(z, keelStartZ, keelStartY, keelEndZ, keelEndY, keelEndSlope)
    return rounded_outline(body_vertices(width, crown, keel), bodyBlendRadius, skinThickness + slideGap, z)


column = box(wallInnerX, wallOuterX, -columnHalfY, columnHalfY, baseThickness, wallStartZ)
lowerClip = extrude(mating_outline(baseThickness - cutOverrun), amount=keelStartZ - baseThickness + 2 * cutOverrun)
wall = box(wallInnerX, wallOuterX, wallYMin, wallYMax, wallStartZ, wallEndZ) & lowerClip
flange = box(flangeXMin, wallOuterX, flangeYMin, flangeYMax, wallStartZ, wallEndZ) & lowerClip
bulkhead = box(-trayHalfWidth, trayHalfWidth, flangeYMin, bulkheadTopY, trayStartZ, bulkheadEndZ) & lowerClip
bulkhead -= box(
    notchXMin, notchXMax, notchBottomY, bulkheadTopY + cutOverrun, trayStartZ - cutOverrun, bulkheadEndZ + cutOverrun
)

# Cut the U-pocket before fusing it to the bulkhead: its cavity terminates at
# the actual aft face z117, so edits to pocketWall cannot erode the bulkhead.
pocket = box(notchXMin, notchXMax, -pocketHalfY, pocketHalfY, pocketStartZ, trayStartZ)
pocket -= box(
    notchXMin + pocketWall,
    notchXMax - pocketWall,
    -pocketHalfY - cutOverrun,
    pocketHalfY + cutOverrun,
    pocketStartZ + pocketWall,
    trayStartZ + cutOverrun,
)

# A small relief removes edge-only contact with the notch's two vertical edges.
pocket -= box(
    notchXMin - cutOverrun,
    notchXMax + cutOverrun,
    notchBottomY - cutOverrun,
    pocketHalfY + cutOverrun,
    trayStartZ - cutOverrun,
    trayStartZ + cutOverrun,
)

# The port supports reach base/bulkhead at x25.6; distinct 9x9 seating faces
# at x26 stay centred on the screw axes. Starboard pads thicken the wall.
pads = [
    box(-wallOuterX, -wallInnerX, -padSize / 2, padSize / 2, baseThickness, lowPortEndZ),
    box(-wallOuterX, -wallInnerX, padHighY - padSize / 2, padHighY + padSize / 2, highPortStartZ, wallEndZ),
]
for x0, x1 in ((-padFaceX, -wallInnerX), (wallInnerX, padFaceX)):
    pads.append(box(x0, x1, -padSize / 2, padSize / 2, padLowZ - padSize / 2, padLowZ + padSize / 2))
    pads.append(
        box(x0, x1, padHighY - padSize / 2, padHighY + padSize / 2, padHighZ - padSize / 2, padHighZ + padSize / 2)
    )

# A single smooth, section-driven clipping loft follows the evolving keel.
# The floor and lips retain exact planar seating and lateral interfaces.
trayStations = [trayStartZ, keelStartZ, 135.0, strapZAft, 160.0, strapZFore, 185.0, 195.0, sledHeight]
assert all(trayStations[i] < z for i, z in enumerate(trayStations[1:])), "infeasible: tray clipping stations unordered"
trayClip = loft([mating_outline(z) for z in trayStations], ruled=False)
floor = box(-trayHalfWidth, trayHalfWidth, trayFloorBottom, trayFloorTop, trayStartZ, sledHeight)
portLip = box(-trayHalfWidth, -lipInnerX, trayFloorTop, lipTopY, trayStartZ, sledHeight)
starboardLip = box(lipInnerX, trayHalfWidth, trayFloorTop, lipTopY, trayStartZ, sledHeight)
tray = (floor + portLip + starboardLip) & trayClip

# The stated facet coefficients are rounded measurements. Apply their exact
# limit to every upper feature, including the lower hole rims. The original
# rounded outline still supplies side/shoulder clearance and the evolving keel.
facetLimit = shellInnerFacetOffset - slideGap
facetOutline = make_face(
    Polyline(
        (facetLimit / 0.7509, 0),
        (0, facetLimit / 0.6604),
        (-facetLimit / 0.7509, 0),
        (0, -facetLimit / 0.6604),
        close=True,
    )
)
measuredFacetClip = Pos(0, 0, baseThickness - cutOverrun) * extrude(
    facetOutline, amount=sledHeight - baseThickness + 2 * cutOverrun
)
upperBody = column + wall + bulkhead + flange + tray + pocket
for pad in pads:
    upperBody += pad
result = base + (upperBody & measuredFacetClip)

sinkHeight = (clampHeadDiameter - clampDiameter) / (2 * math.tan(math.radians(clampHeadAngle / 2)))
assert 0 < sinkHeight < baseThickness, "infeasible: countersink consumes base thickness"
tools = [Pos(0, 0, baseThickness / 2) * Cylinder(powerHoleDiameter / 2, baseThickness + 2 * cutOverrun)]
for x in (-clampOffset, clampOffset):
    for y in (-clampOffset, clampOffset):
        tools.append(Pos(x, y, baseThickness / 2) * Cylinder(clampDiameter / 2, baseThickness + 2 * cutOverrun))
        tools.append(
            Pos(x, y, baseThickness - sinkHeight)
            * Cone(
                clampDiameter / 2,
                clampHeadDiameter / 2 + cutOverrun * math.tan(math.radians(clampHeadAngle / 2)),
                sinkHeight + cutOverrun,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
            )
        )
for y in (wallHoleYLow, wallHoleYHigh):
    for z in (wallHoleZAft, wallHoleZFore):
        tools.append(
            Pos((wallInnerX + wallOuterX) / 2, y, z)
            * Cylinder(wallHoleDiameter / 2, wallThickness + 2 * cutOverrun, rotation=(0, 90, 0))
        )
for sign in (-1.0, 1.0):
    boreCenterX = sign * (padFaceX - insertHoleDepth / 2 + cutOverrun / 2)
    for y, z in ((0.0, padLowZ), (padHighY, padHighZ)):
        tools.append(
            Pos(boreCenterX, y, z) * Cylinder(insertHoleDiameter / 2, insertHoleDepth + cutOverrun, rotation=(0, 90, 0))
        )
for station in (strapZAft, strapZFore):
    tools.append(
        box(
            -strapSlotLength / 2,
            strapSlotLength / 2,
            trayFloorBottom - cutOverrun,
            trayFloorTop + cutOverrun,
            station - strapSlotWidth / 2,
            station + strapSlotWidth / 2,
        )
    )
result -= Compound(tools)
assert len(result.solids()) == 1, "infeasible: sled disconnected"
assert result.is_valid, "kernel: invalid sled"
