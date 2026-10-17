"""Sliding Sprite Aleph v2 cover, millimetres, identity assembly placement."""

import math

from build123d import (
    Align,
    Box,
    Compound,
    Cylinder,
    Line,
    Plane,
    Pos,
    SkipClean,
    Spline,
    ThreePointArc,
    extrude,
    loft,
    make_face,
    mirror,
)

bodyWidth = 60.0
coverStartZ = 22.0
browZ = 256.7
bodySplitY = 22.0
crownStartZ = 185.0
crownY = 37.5
browY = 7.8
widthStartZ = 202.0
lipZ = 249.3
lipHalfWidth = 13.1
keelStartZ = 125.0
keelStartY = -37.5
lipKeelY = -22.9
facetSideY = 23.4
facetCrownX = 17.6
wallThickness = 2.0
skirtInnerX = 26.6
skirtThickness = 1.2
skirtBottomY = 15.0
ledgeThickness = 1.2
ledgeOuterX = 28.0
tongueOuterX = 29.1
tongueMinY = 16.05
tongueMaxY = 19.95
morphLength = 23.0
splitLength = 14.0
rearScrewZ = 25.5
frontScrewZ = 207.5
widthEndSlope = -0.4
crownEndSlope = -0.72
keelEndSlope = 0.35
cornerRadius = 7.0
pilotHoleDiameter = 1.1
rearPadHalfWidth = 6.0
frontBossHalfWidth = 3.2
frontBossSeatY = 31.75
tongueFilletRadius = 0.2
camEarClearRadius = 6.3
camEarClearHalfX = 12.4
camHingeAxisY = -2.28
camHingeAxisZ = 244.0
coverLength = browZ - coverStartZ
slideTravel = widthStartZ - coverStartZ
skirtOuterX = skirtInnerX + skirtThickness
ledgeTopY = bodySplitY + ledgeThickness
rearPadSeatY = 35.5
tongueHeight = tongueMaxY - tongueMinY
morphEndZ = widthStartZ + morphLength
splitEndZ = widthStartZ + splitLength

assert 0.0 < wallThickness < cornerRadius, "infeasible: positive skin below round radius"
assert 6.0 <= cornerRadius <= 8.0, "infeasible: body blend outside R6..R8"
assert coverStartZ < crownStartZ < widthStartZ < morphEndZ < lipZ < browZ, "infeasible: station order"
assert widthStartZ < splitEndZ < morphEndZ, "infeasible: split must finish within morph"
assert 0.0 < tongueFilletRadius <= 0.3, "infeasible: tongue round outside sliding range"
assert 2 * tongueFilletRadius < tongueHeight, "infeasible: tongue flats consumed"
assert tongueOuterX - skirtOuterX > tongueFilletRadius, "infeasible: tongue projection"
assert skirtInnerX < skirtOuterX < ledgeOuterX < tongueOuterX < bodyWidth / 2, "infeasible: rail order"
assert skirtBottomY < tongueMinY < tongueMaxY < bodySplitY < ledgeTopY, "infeasible: rail heights"
assert pilotHoleDiameter < 2 * frontBossHalfWidth, "infeasible: front pilot consumes support"
assert rearScrewZ - pilotHoleDiameter / 2 > coverStartZ, "infeasible: rear pilot outside cover"
assert camEarClearRadius > 0.0, "infeasible: camera ear relief radius must be positive"
assert 0.0 < camEarClearHalfX < bodyWidth / 2, "infeasible: camera ear relief span outside cover"


def box_at(x0, x1, y0, y1, z0, z1):
    return Pos(x0, y0, z0) * Box(x1 - x0, y1 - y0, z1 - z0, align=(Align.MIN, Align.MIN, Align.MIN))


def smoothstep(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3.0 - 2.0 * u)


def hermite(z, z0, v0, z1, v1, end_slope):
    t = max(0.0, min(1.0, (z - z0) / (z1 - z0)))
    return (2 * t**3 - 3 * t**2 + 1) * v0 + (3 * t**2 - 2 * t**3) * v1 + (t**3 - t**2) * (z1 - z0) * end_slope


def width(z):
    return hermite(z, widthStartZ, bodyWidth / 2, lipZ, lipHalfWidth, widthEndSlope)


def crown(z):
    return hermite(z, crownStartZ, crownY, browZ, browY, crownEndSlope)


def keel(z):
    # Common assembly law; no lower keel is added to this upper cover.
    return hermite(z, keelStartZ, keelStartY, lipZ, lipKeelY, keelEndSlope)


def rounded_segments(z, inset=0.0):
    """Five exact tangent segments of the upper starboard faceted outline."""
    w, c = width(z), crown(z)
    vertices = [(w, 0.0), (w, facetSideY * w / (bodyWidth / 2)), (facetCrownX * w / (bodyWidth / 2), c), (0.0, c)]
    arcs = []
    for j in (1, 2):
        p, a, b = vertices[j], vertices[j - 1], vertices[j + 1]
        u, v = (a[0] - p[0], a[1] - p[1]), (b[0] - p[0], b[1] - p[1])
        lu, lv = math.hypot(*u), math.hypot(*v)
        u, v = (u[0] / lu, u[1] / lu), (v[0] / lv, v[1] / lv)
        theta = math.acos(u[0] * v[0] + u[1] * v[1])
        bis = (u[0] + v[0], u[1] + v[1])
        scale = cornerRadius / (math.sin(theta / 2) * math.hypot(*bis))
        center = (p[0] + scale * bis[0], p[1] + scale * bis[1])
        tangent = cornerRadius / math.tan(theta / 2)
        start = (p[0] + tangent * u[0], p[1] + tangent * u[1])
        end = (p[0] + tangent * v[0], p[1] + tangent * v[1])
        a0 = math.atan2(start[1] - center[1], start[0] - center[0])
        a1 = math.atan2(end[1] - center[1], end[0] - center[0])
        arcs.append((center, a0, a1, cornerRadius - inset))
    c0, a0, a1, r0 = arcs[0]
    c1, b0, b1, r1 = arcs[1]
    p0 = (c0[0] + r0 * math.cos(a0), c0[1] + r0 * math.sin(a0))
    p1 = (c0[0] + r0 * math.cos(a1), c0[1] + r0 * math.sin(a1))
    p2 = (c1[0] + r1 * math.cos(b0), c1[1] + r1 * math.sin(b0))
    p3 = (c1[0] + r1 * math.cos(b1), c1[1] + r1 * math.sin(b1))
    return [((w - inset, 0.0), p0), arcs[0], (p1, p2), arcs[1], (p3, (0.0, c - inset))]


def segment_point(segment, t):
    if len(segment) == 2:
        a, b = segment
        return (a[0] * (1 - t) + b[0] * t, a[1] * (1 - t) + b[1] * t)
    center, a0, a1, radius = segment
    angle = a0 * (1 - t) + a1 * t
    return (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle))


def exact_edges(z, inset=0.0):
    edges = []
    for seg in rounded_segments(z, inset):
        if len(seg) == 2:
            edges.append(Line(*seg))
        else:
            edges.append(ThreePointArc(*(segment_point(seg, t) for t in (0.0, 0.5, 1.0))))
    return edges


# Compact source-defined brow outline (source own z225.75 +30 = assembly255.75).
# Only this local aperture station is retained; the new skin follows the laws.
browProfile = ((0.0, 8.42), (1.56, 8.34), (3.10, 8.08), (4.575, 7.60), (5.95, 6.875))
browInnerProfile = ((0.0, 7.68), (1.56, 7.645), (3.11, 7.515), (4.645, 7.245), (5.91, 6.875))
retainedStations = (
    (249.3, 13.1, 0.0, 0.0),
    (252.04, 9.69, 3.4375, 0.5),
    (255.75, 5.95, 6.875, 1.0),
    (256.25, 2.6775, 7.24625, 1.0),
    (256.7, 1.1, 7.4, 0.0),
)


def source_drop(fraction, profile=browProfile):
    # Lagrange interpolation in x squared preserves symmetry and crown tangent.
    xx = (fraction * profile[-1][0]) ** 2
    drop = 0.0
    for i, (x, y) in enumerate(profile):
        weight = 1.0
        for j, (xj, _) in enumerate(profile):
            if j != i:
                weight *= (xx - xj * xj) / (x * x - xj * xj)
        drop += weight * (profile[0][1] - y)
    return drop / (profile[0][1] - profile[-1][1])


def retained_point(z, theta):
    # The width and keel Hermite laws are never extrapolated past the lip.
    # Convert polar angle to ellipse parameter angle at the actual joining lip.
    theta = math.atan2(lipHalfWidth * math.sin(theta), crown(lipZ) * math.cos(theta))
    for i in range(len(retainedStations) - 1):
        a, b = retainedStations[i], retainedStations[i + 1]
        if z <= b[0] + 1e-7:
            t = max(0.0, min(1.0, (z - a[0]) / (b[0] - a[0])))
            values = []
            for column, start_slope in ((1, widthEndSlope), (2, 0.0)):
                slope = (b[column] - a[column]) / (b[0] - a[0])
                if i:
                    previous = retainedStations[i - 1]
                    before = (a[column] - previous[column]) / (a[0] - previous[0])
                    m0 = 2 * before * slope / (before + slope) if before * slope > 0 else 0.0
                else:
                    m0 = start_slope
                if i + 2 < len(retainedStations):
                    following = retainedStations[i + 2]
                    after = (following[column] - b[column]) / (following[0] - b[0])
                    m1 = 2 * after * slope / (after + slope) if after * slope > 0 else 0.0
                else:
                    m1 = slope
                values.append(
                    (2 * t**3 - 3 * t * t + 1) * a[column]
                    + (3 * t * t - 2 * t**3) * b[column]
                    + (t**3 - 2 * t * t + t) * (b[0] - a[0]) * m0
                    + (t**3 - t * t) * (b[0] - a[0]) * m1
                )
            hw, floor = values
            shape = a[3] * (1 - smoothstep(t)) + b[3] * smoothstep(t)
            f = math.cos(theta)
            ellipse_drop = 1 - math.sin(theta)
            drop = (1 - shape) * ellipse_drop + shape * source_drop(f)
            return (hw * f, crown(z) - (crown(z) - floor) * drop)
    return (0.0, browY)


def outline_point(z, segment, t):
    # Fixed correspondence beyond the morph avoids propagating a facet seam.
    anchor_z = min(z, morphEndZ)
    x, y = segment_point(rounded_segments(anchor_z)[segment], t)
    theta = math.atan2(y, x)
    if z > lipZ:
        return retained_point(z, theta)
    w, c = width(z), crown(z)
    radius = 1 / math.sqrt((math.cos(theta) / w) ** 2 + (math.sin(theta) / c) ** 2)
    blend = smoothstep((z - widthStartZ) / morphLength)
    facet_radius = math.hypot(x, y)
    radius = (1 - blend) * facet_radius + blend * radius
    return (radius * math.cos(theta), radius * math.sin(theta))


def outer_edges(z):
    if z <= widthStartZ:
        return exact_edges(z)
    return [Spline(*(outline_point(z, j, k / 6) for k in range(7))) for j in range(5)]


def filled_half(z):
    edges = outer_edges(z)
    side = outline_point(z, 0, 0.0)
    top = (0.0, crown(z))
    bottom = (0.0, side[1])
    return Pos(0.0, 0.0, z) * make_face(edges + [Line(top, bottom), Line(bottom, side)])


def surface_normal(z, segment, t):
    """Outward normal of the analytic three-dimensional skin, not a 2D inset."""
    dt, dz = 0.0001, 0.002
    a, b = max(0.0, t - dt), min(1.0, t + dt)
    p, q = outline_point(z, segment, a), outline_point(z, segment, b)
    xq, yq = (q[0] - p[0]) / (b - a), (q[1] - p[1]) / (b - a)
    a, b = z - dz, min(browZ, z + dz)
    p, q = outline_point(a, segment, t), outline_point(b, segment, t)
    xz, yz = (q[0] - p[0]) / (b - a), (q[1] - p[1]) / (b - a)
    n = (yq, -xq, xq * yz - yq * xz)
    if segment == 4 and t == 1.0:
        n = (0.0, -xq, xq * yz)
    if segment == 0 and t == 0.0 and z <= lipZ:
        n = (yq, 0.0, -yq * xz)
    length = math.sqrt(sum(v * v for v in n))
    return tuple(v / length for v in n)


def offset_source(z, segment, t):
    """Parallel-surface construction beyond its lip uses only the lip tangent.

    The outer skin remains source-defined beyond lipZ; this tangent extension
    only closes the trimmed inner offset at the open aperture boundary.
    """
    if z <= lipZ:
        return outline_point(z, segment, t), surface_normal(z, segment, t)
    dz = 0.002
    p = outline_point(lipZ, segment, t)
    q = outline_point(lipZ - dz, segment, t)
    tangent = tuple((a - b) / dz for a, b in zip(p, q))
    point = tuple(a + (z - lipZ) * b for a, b in zip(p, tangent))
    return point, surface_normal(lipZ - dz, segment, t)


def inner_point(z, segment, t, thickness=None):
    thickness = wallThickness if thickness is None else thickness
    if t == 1.0 and segment < 4:
        segment, t = segment + 1, 0.0
    if z <= crownStartZ:
        return segment_point(rounded_segments(z, thickness)[segment], t)
    if z <= lipZ:
        # Intersect the true parallel surface P - thickness*N with this z plane.
        # Re-solving the source z includes longitudinal crown/width slope.
        source_z = z
        for _ in range(12):
            _, n = offset_source(source_z, segment, t)
            source_z = z + thickness * n[2]
        (x, y), n = offset_source(source_z, segment, t)
        return (x - thickness * n[0], y - thickness * n[1])
    # Boundary treatment only: retain the source's thin local aperture contour.
    # The ordinary normal offset ends at the lip, never at a reduced ellipse.
    side = outline_point(z, 0, 0.0)
    hw, floor = side
    x, _ = outline_point(z, segment, t)
    fraction = max(0.0, min(1.0, x / hw))
    lip_inner = inner_point(lipZ, segment, t, thickness)
    base = (lip_inner[0] * hw / lipHalfWidth, floor + (crown(z) - floor) * lip_inner[1] / crown(lipZ))
    terminal = smoothstep((z - 255.75) / (browZ - 255.75))
    inner_width = hw * ((1 - terminal) * 5.91 / 5.95 + terminal * 0.8 / 1.1)
    gap = (1 - terminal) * (crown(z) - floor) * 0.74 / 1.545 + terminal * 0.2
    top = crown(z) - gap
    inner_floor = floor + 0.05 * terminal
    drop = (1 - terminal) * source_drop(fraction, browInnerProfile) + terminal * (
        1 - math.sqrt(max(0.0, 1 - fraction**2))
    )
    retained = (inner_width * fraction, top - (top - inner_floor) * drop)
    taper = smoothstep((z - lipZ) / (255.75 - lipZ))
    return tuple(a * (1 - taper) + b * taper for a, b in zip(base, retained))


def wall_half(z):
    section_z = z
    z = min(z, browZ)
    outer = outer_edges(z)
    if z <= crownStartZ:
        inner = exact_edges(z, wallThickness)
    else:
        inner = [Spline(*(inner_point(z, j, k / 6) for k in range(7))) for j in range(5)]
    outer_side = outline_point(z, 0, 0.0)
    inner_side = inner_point(z, 0, 0.0)
    outer_top = (0.0, crown(z))
    inner_top = inner_point(z, 4, 1.0)
    return Pos(0.0, 0.0, section_z) * make_face(
        outer + [Line(outer_top, inner_top)] + inner + [Line(inner_side, outer_side)]
    )


def split_y(z):
    return skirtBottomY * (1 - smoothstep((z - widthStartZ) / splitLength))


def split_tool(body_floor):
    # World YZ plane: local coordinates are (y,z), extrusion along global x.
    seam_z = widthStartZ - 0.005
    p = [(split_y(widthStartZ + splitLength * k / 8), widthStartZ + splitLength * k / 8) for k in range(9)]
    e = [
        Line((-10.0, seam_z), (skirtBottomY, seam_z)),
        Line((skirtBottomY, seam_z), p[0]),
        Spline(*p),
        Line(p[-1], (0.0, browZ + 0.02)),
        Line((0.0, browZ + 0.02), (-10.0, browZ + 0.02)),
        Line((-10.0, browZ + 0.02), (-10.0, seam_z)),
    ]
    forward = extrude(Pos(-bodyWidth, 0.0, 0.0) * (Plane.YZ * make_face(e)), amount=2 * bodyWidth, dir=(1.0, 0.0, 0.0))
    rear = box_at(-bodyWidth, bodyWidth, -10.0, body_floor, coverStartZ - 0.02, seam_z)
    return rear + forward


# One continuous, non-ruled loft from the exact crown into the local Sprite brow.
noseStations = (
    crownStartZ,
    186.0,
    190.0,
    196.0,
    widthStartZ,
    206.0,
    210.0,
    214.0,
    splitEndZ,
    218.0,
    222.0,
    morphEndZ,
    230.0,
    235.0,
    240.0,
    242.5,
    245.0,
    247.0,
    248.3,
    lipZ,
    250.5,
    252.04,
    253.5,
    254.5,
    255.75,
    256.0,
    256.25,
    browZ,
    browZ + 0.5,
)
body_half = extrude(wall_half(coverStartZ), amount=crownStartZ - coverStartZ)
nose_half = loft([wall_half(z) for z in noseStations], ruled=False)
assert nose_half.is_valid, "nose half loft must be valid before union"
skin_half = body_half + nose_half
assert skin_half.is_valid, "body to nose half union must be valid"
skin = skin_half + mirror(skin_half, Plane.YZ)
assert skin.is_valid, "mirrored skin must be valid before split"
skin -= box_at(-bodyWidth, bodyWidth, -bodyWidth, bodyWidth, browZ, browZ + 2.0)
skin -= split_tool(bodySplitY)
assert skin.is_valid, "normal-offset skin must be a valid B-rep"


def sliding_rail():
    """Continuous rail; the two outer tongue rounds retain all tangent flats."""
    x0, x1 = skirtOuterX, tongueOuterX
    y0, y1, radius = tongueMinY, tongueMaxY, tongueFilletRadius
    diagonal = radius / math.sqrt(2)
    edge = [
        Line((x0, y0), (x1 - radius, y0)),
        ThreePointArc((x1 - radius, y0), (x1 - radius + diagonal, y0 + radius - diagonal), (x1, y0 + radius)),
        Line((x1, y0 + radius), (x1, y1 - radius)),
        ThreePointArc((x1, y1 - radius), (x1 - radius + diagonal, y1 - radius + diagonal), (x1 - radius, y1)),
        Line((x1 - radius, y1), (x0, y1)),
        Line((x0, y1), (x0, y0)),
    ]
    tongue = extrude(Pos(0.0, 0.0, coverStartZ) * make_face(edge), amount=slideTravel + 0.005)
    skirt = box_at(skirtInnerX, skirtOuterX, skirtBottomY, bodySplitY, coverStartZ, widthStartZ + 0.005)
    ledge = box_at(skirtInnerX, ledgeOuterX, bodySplitY, ledgeTopY, coverStartZ, widthStartZ + 0.005)
    # Seal the 0.01 mm transition cap where the skirt meets the nose wall.
    cap = box_at(
        skirtOuterX,
        bodyWidth / 2 - wallThickness + 0.05,
        skirtBottomY,
        ledgeTopY,
        widthStartZ - 0.005,
        widthStartZ + 0.005,
    )
    return skirt + ledge + tongue + cap


rail = sliding_rail()
result = skin + rail + mirror(rail, Plane.YZ)
assert result.is_valid, "skin and uninterrupted sliding rails must be valid"
assert len(result.solids()) == 1, "skins, ledges and tongues must form one cover"


def inner_crown_at_x(z, x, thickness=2.0):
    """Solve the nominal normal-offset crown at a world-space x."""
    low, high = 0.0, 1.0
    for _ in range(28):
        t = (low + high) / 2
        px, _ = inner_point(z, 4, t, thickness)
        if px > abs(x):
            low = t
        else:
            high = t
    return inner_point(z, 4, (low + high) / 2, thickness)[1]


def front_pad_profile():
    """One extruded neck profile; buried ends avoid tangent boolean seams."""
    half_land = pilotHoleDiameter / 2 + 0.005
    rear_z, front_z = frontScrewZ - half_land, frontScrewZ + half_land
    # Keep the full pilot circle supported while clearing the highest neck point.
    land_y = max(frontBossSeatY, inner_crown_at_x(rear_z, 0.0) - 0.3 + 0.001)
    assert abs(land_y - frontBossSeatY) <= 0.1, "planar land outside front seat tolerance"

    def lower(z):
        rise = smoothstep((z - (frontScrewZ - 4.5)) / 2.0)
        fall = 1 - smoothstep((z - (frontScrewZ + 2.0)) / 3.5)
        depth = -0.08 + 0.38 * rise * fall
        return inner_crown_at_x(z, 0.0) - depth

    rear_stations = [frontScrewZ + d for d in (-4.5, -4.0, -3.5, -3.0, -2.5, -2.0, -1.5, -1.0)]
    rear_points = [(lower(z), z) for z in rear_stations] + [(land_y, rear_z)]
    front_stations = [frontScrewZ + d for d in (0.85, 1.25, 1.75, 2.0, 2.5, 3.25, 4.0, 4.75, 5.5)]
    front_points = [(land_y, front_z)]
    for z in front_stations:
        blend = smoothstep((z - front_z) / 1.25)
        front_points.append(((1 - blend) * land_y + blend * lower(z), z))
    top_stations = rear_stations + [rear_z, front_z] + front_stations
    top_points = [(inner_crown_at_x(z, 0.0) + 0.65, z) for z in top_stations]
    edges = [
        Spline(*rear_points),
        Line(rear_points[-1], front_points[0]),
        Spline(*front_points),
        Line(front_points[-1], top_points[-1]),
        Spline(*top_points),
        Line(top_points[0], rear_points[0]),
    ]
    face = Pos(-frontBossHalfWidth, 0.0, 0.0) * (Plane.YZ * make_face(edges))
    return extrude(face, amount=2 * frontBossHalfWidth, dir=(1.0, 0.0, 0.0))


rear_pad = box_at(-rearPadHalfWidth, rearPadHalfWidth, rearPadSeatY, crownY, coverStartZ, 2 * rearScrewZ - coverStartZ)
front_pad = front_pad_profile()
neck_at_screw = inner_crown_at_x(frontScrewZ, 0.0) - 0.3
assert abs(neck_at_screw - frontBossSeatY) < 0.1, "derived neck station must match approximate front seat"
result += rear_pad + front_pad
pilot_tools = Compound(
    [
        Pos(0.0, 31.0, z) * Cylinder(pilotHoleDiameter / 2, 14.0, rotation=(90.0, 0.0, 0.0))
        for z in (rearScrewZ, frontScrewZ)
    ]
)
result -= pilot_tools
assert result.is_valid, "two screw retention must leave a valid cover"
assert len(result.solids()) == 1, "the completed cover must remain one solid"

# Clear both camera plate ears about the fixed assembly hinge axis. The finite
# x span removes only the inner tip skin, retaining the analytic outer surface.
cam_ear_tool = Pos(0.0, camHingeAxisY, camHingeAxisZ) * Cylinder(
    camEarClearRadius, 2 * camEarClearHalfX, rotation=(0.0, 90.0, 0.0)
)
result -= cam_ear_tool
assert result.is_valid, "camera ear relief must leave a valid cover"
assert len(result.solids()) == 1, "camera ear relief must preserve one connected cover"

# Retain measurable seat/rail face patches when coplanar unions are cleaned.
# These are topological imprints only: the cut material is put back unchanged.
datum_patches = [
    box_at(
        -rearPadHalfWidth,
        rearPadHalfWidth,
        rearPadSeatY - 0.02,
        rearPadSeatY + 0.02,
        coverStartZ - 0.02,
        2 * rearScrewZ - coverStartZ,
    )
]
starboard_patches = [
    box_at(
        skirtInnerX - 0.02, skirtInnerX + 0.02, skirtBottomY - 0.02, bodySplitY, coverStartZ - 0.02, widthStartZ + 0.02
    ),
    box_at(skirtOuterX, ledgeOuterX, bodySplitY - 0.02, bodySplitY + 0.02, coverStartZ - 0.02, widthStartZ + 0.02),
    box_at(28.0, 28.8, tongueMinY - 0.02, tongueMinY + 0.02, coverStartZ - 0.02, widthStartZ + 0.02),
    box_at(28.0, 28.8, tongueMaxY - 0.02, tongueMaxY + 0.02, coverStartZ - 0.02, widthStartZ + 0.02),
]
datum_patches += starboard_patches + [mirror(patch, Plane.YZ) for patch in starboard_patches]
datum_tools = Compound(datum_patches)
datum_material = result & datum_tools
with SkipClean():
    result = (result - datum_tools) + datum_material
assert result.is_valid, "datum face imprints must preserve validity"
assert len(result.solids()) == 1, "datum face imprints must preserve one solid"
