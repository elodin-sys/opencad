import math

from build123d import (
    Box,
    Compound,
    Cylinder,
    Face,
    Plane,
    Polyline,
    Pos,
    Rot,
    Spline,
    ThreePointArc,
    Wire,
    loft,
    mirror,
)

rimZ = -6.0
coneDepth = 86.065
wallThickness = 0.8
pilotHoleDiameter = 1.1
pilotHoleZ = -10.0
drilledHoleDiameter = 2.2
mirrorPlaneY = -0.083
armTipReach = 96.9
armTipWidth = 10.98
armKeelDepth = 18.0
pocketWidth = 15.74
pocketFloorZ = -24.24
rearMountWidth = 50.0
rearMountLength = 73.19
fitDepth = 15.0
stadiumHalfWidth917 = 4.65
stadiumHalfLength917 = 17.23
stadiumHalfWidth888 = 5.98
stadiumHalfLength888 = 18.57
stadiumHalfWidth832 = 8.41
stadiumHalfLength832 = 20.99
stadiumHalfWidth752 = 11.53
stadiumHalfLength752 = 24.11
slotWidth = 45.0
slotHeight = 10.0
slotCenterZ = -22.0
slotCount = 2.0
escBayHalfX = 28.0
escBayHalfY = 36.5
armUndersideWidth = 12.0
socketReachY = 38.3
plugReachY = 46.5
pcbReliefOuterX = 24.0
pcbReliefZMin = -21.8
pcbReliefZMax = -17.8

assert wallThickness > 0, "infeasible: wallThickness must be positive"
assert coneDepth > rimZ - pocketFloorZ, "infeasible: coneDepth shallower than the pocket floor"
assert pilotHoleDiameter > 0, "infeasible: pilotHoleDiameter must be positive"
assert pilotHoleDiameter < drilledHoleDiameter, "infeasible: pilot hole must stay below the drilled size"
assert armKeelDepth > wallThickness, "infeasible: arm keel shallower than the wall"
assert fitDepth > wallThickness, "infeasible: fit depth shallower than the wall"
assert armTipReach > armTipWidth, "infeasible: arm tip reach shorter than the tip width"
assert stadiumHalfWidth917 > 0, "infeasible: stadiumHalfWidth917 must be positive"
assert stadiumHalfLength917 > stadiumHalfWidth917, "infeasible: stadium half length must exceed half width"


assert slotWidth > 0.0, "infeasible: slotWidth must be positive"
assert slotHeight > 0.0, "infeasible: slotHeight must be positive"
assert slotCount == 2.0, "infeasible: exactly two connector slots are required"
assert slotWidth / 2 < pcbReliefOuterX < escBayHalfX - wallThickness, "infeasible: relief consumes inlet walls"
assert slotCenterZ - slotHeight / 2 < pcbReliefZMin < pcbReliefZMax < slotCenterZ + slotHeight / 2, (
    "infeasible: PCB relief must retain both slot-end bridges"
)
assert slotCenterZ + slotHeight / 2 < pilotHoleZ - pilotHoleDiameter / 2, "infeasible: slot consumes pilots"
assert escBayHalfY < socketReachY < plugReachY, "infeasible: connector reaches are reversed"
assert armUndersideWidth > 2 * wallThickness, "infeasible: arm underside has no trough"

nominalConeDepth = 86.065
nominalWallThickness = 0.8
nominalTip = rimZ - nominalConeDepth
tipZ = rimZ - coneDepth
anchorZ = pocketFloorZ
fitZ = rimZ - fitDepth
rimOuterHalfX = rearMountWidth / 2 + nominalWallThickness
rimOuterHalfY = rearMountLength / 2 + nominalWallThickness
fitOuterHalfX = rearMountWidth / 2 - 1.0 + nominalWallThickness
fitOuterHalfY = 35.7 + nominalWallThickness
pocketAmpRim = 0.03
armRootHalf = armUndersideWidth / 2
rMid = 36.178 * math.sqrt(2)
pilotFromMirror = 37.038

# Stadium end radii, half-lengths and side-rib crowns from the contract stations.
# The straight portion of each stadium is about 25.16 mm long.
coneStations = [
    (nominalTip, stadiumHalfWidth917 - 0.168, stadiumHalfLength917 - 0.168, 0.0),
    (-91.70, stadiumHalfWidth917, stadiumHalfLength917, 0.0),
    (-88.79, stadiumHalfWidth888, stadiumHalfLength888, 0.0),
    (-83.17, stadiumHalfWidth832, stadiumHalfLength832, 0.0),
    (-75.23, stadiumHalfWidth752, stadiumHalfLength752, 0.0),
    (-70.549, 13.199, 25.782, 0.0),
    (-65.50, 14.87, 27.451, 15.60 - 14.87),
    (-54.65, 18.0, 30.58, 20.98 - 18.0),
    (-49.032, 19.38, 31.963, 23.21 - 19.38),
    (-43.42, 20.61, 33.185, 25.08 - 20.61),
    (-32.56, 22.56, 35.115, 27.69 - 22.56),
    (-27.516, 23.24, 35.827, 28.473 - 23.24),
    (pocketFloorZ, 23.639, 36.219, 28.83 - 23.639),
    (-22.84, 23.795, 36.375, 28.96 - 23.795),
    (fitZ, fitOuterHalfX - 0.88, fitOuterHalfY, 29.1 - (fitOuterHalfX - 0.88)),
    (-14.89, 24.42, 37.0, 29.29 - 24.42),
    (-9.28, rimOuterHalfX - 0.985, rimOuterHalfY, 29.14 - (rimOuterHalfX - 0.985)),
    (-6.37, rimOuterHalfX - 0.985, rimOuterHalfY, 29.015 - (rimOuterHalfX - 0.985)),
    (rimZ, rimOuterHalfX - 0.985, rimOuterHalfY, 29.0 - (rimOuterHalfX - 0.985)),
]


def world_z(z_nom):
    if z_nom >= anchorZ:
        return z_nom
    return tipZ + (z_nom - nominalTip) * (anchorZ - tipZ) / (anchorZ - nominalTip)


def pocket_amp(z_nom):
    return pocketAmpRim * max(0.0, (z_nom - pocketFloorZ) / (rimZ - pocketFloorZ))


def section_face(z_nom, radius, half_length, rib, inset=0.0, z_override=None):
    z = world_z(z_nom) if z_override is None else z_override
    straight = half_length - radius
    shoulders = [
        (-70.549, 1.8, 7.8),
        (-49.032, 1.8, 8.3),
        (-43.42, 2.2, 9.3),
        (-32.56, 3.0, 10.5),
        (-27.516, 3.5, 11.4),
        (-22.84, 4.0, 12.0),
        (-14.89, 5.0, 12.5),
        (-9.28, 6.0, 12.5),
        (rimZ, 6.0, 12.5),
    ]
    shoulder0, shoulder1 = shoulders[0][1:]
    for index in range(len(shoulders) - 1):
        (z0, a0, b0), (z1, a1, b1) = shoulders[index], shoulders[index + 1]
        if z_nom >= z0:
            t = min(1.0, (z_nom - z0) / (z1 - z0))
            shoulder0, shoulder1 = a0 + t * (a1 - a0), b0 + t * (b1 - b0)
    quarter = []
    # One side rib: flat crown, fair shoulder, straight stadium side, round end.
    quarter.append([(radius + rib - inset, 0.0), (radius + rib - inset, shoulder0)])
    shoulder = []
    for i in range(9):
        t = i / 8
        y = shoulder0 + (shoulder1 - shoulder0) * t
        blend = 1 - 3 * t * t + 2 * t * t * t
        slope = rib * (-6 * t + 6 * t * t) / (shoulder1 - shoulder0)
        norm = math.sqrt(1 + slope * slope)
        shoulder.append((radius + rib * blend - inset / norm, y + inset * slope / norm))
    quarter.append(shoulder)
    quarter.append([(radius - inset, shoulder1), (radius - inset, straight)])
    cap = []
    bump = pocket_amp(z_nom)
    for i in range(17):
        t = math.pi * i / 32
        x = (radius - inset) * math.cos(t)
        y = straight + (radius - inset) * math.sin(t)
        if bump and x < pocketWidth / 2:
            y += bump * (1 + math.cos(math.pi * x / (pocketWidth / 2))) / 2
        cap.append((x, y))
    quarter.append(cap)
    edges = []
    for sx, sy, reverse in ((1, 1, False), (-1, 1, True), (-1, -1, False), (1, -1, True)):
        segments = list(reversed(quarter)) if reverse else quarter
        for segment in segments:
            points = list(reversed(segment)) if reverse else segment
            points3 = [(sx * x, mirrorPlaneY + sy * y, z) for x, y in points]
            if len(points3) == 2:
                edge = Polyline(*points3)
            elif len(points3) == 17 and not bump:
                edge = ThreePointArc(points3[0], points3[8], points3[-1])
            else:
                edge = Spline(*points3)
            edges.extend(edge.edges())
    return Face(Wire.combine(edges)[0])


outer_sections = []
void_sections = []
for index, (z_nom, radius, half_length, rib) in enumerate(coneStations):
    left = coneStations[max(0, index - 1)]
    right = coneStations[min(len(coneStations) - 1, index + 1)]
    slope = (right[1] - left[1]) / (world_z(right[0]) - world_z(left[0]))
    inset = wallThickness * math.sqrt(1 + slope * slope)
    try:
        outer_sections.append(section_face(z_nom, radius, half_length, rib))
    except Exception as error:
        raise RuntimeError(f"outer station {index}: {error}") from error
    z_void = world_z(z_nom)
    if index == 0:
        z_void -= 0.05
        radius -= slope * 0.05
        half_length -= slope * 0.05
    elif index == len(coneStations) - 1:
        z_void += 0.05
    try:
        void_sections.append(section_face(z_nom, radius, half_length, rib, inset, z_void))
    except Exception as error:
        raise RuntimeError(f"inner station {index}: {error}") from error
# Keep each upper transition interpolated within its own station band.
split = 12
cone = loft(outer_sections[: split + 1], ruled=False, clean=False) + loft(
    outer_sections[split:], ruled=False, clean=False
)
cone_void = loft(void_sections[: split + 1], ruled=False, clean=False) + loft(
    void_sections[split:], ruled=False, clean=False
)


def arm_depth(radius):
    knots = [
        (18.0, 1.38 * armKeelDepth),
        (28.0, 1.28 * armKeelDepth),
        (40.0, 1.06 * armKeelDepth),
        (rMid, armKeelDepth),
        (66.0, armKeelDepth),
        (80.0, 0.9005 * armKeelDepth),
        (90.0, 0.7334 * armKeelDepth),
        (armTipReach, 0.566 * armKeelDepth),
    ]
    if radius <= knots[0][0]:
        return knots[0][1]
    if radius >= knots[-1][0]:
        return knots[-1][1]
    for index in range(len(knots) - 1):
        (r0, d0), (r1, d1) = knots[index], knots[index + 1]
        if r0 <= radius <= r1:
            t = (radius - r0) / (r1 - r0)
            return d0 + (d1 - d0) * t
    return knots[-1][1]


def arm_half_width(radius):
    return armRootHalf


def arm_roundness(radius):
    t = max(0.0, min(1.0, (radius - 70.0) / 20.0))
    return t * t * (3.0 - 2.0 * t)


def root_keel_radius(radius):
    return min(0.9 * armRootHalf, max(0.0, 1.5 * (44.0 - radius) / 16.0))


def flank_point(half_width, depth, roundness, u, inset=0.0, keel_radius=0.0, keel_gain=0.09):
    # A circular bottom joins the two large circular flanks tangentially at
    # the root. Its inward normal keeps the root keel a shell, not a wedge.
    radius = (half_width**2 + depth**2 - 2 * depth * keel_radius) / (2 * (half_width - keel_radius))
    angle = math.pi * u / 2
    d = depth * math.sin(angle)
    center_distance = math.hypot(radius - half_width, depth - keel_radius)
    tangent_depth = radius * (depth - keel_radius) / center_distance
    if keel_radius and d > tangent_depth:
        local_d = d - (depth - keel_radius)
        q = math.sqrt(max(0.0, keel_radius**2 - local_d**2))
        ny, nd = q / keel_radius, local_d / keel_radius
    else:
        root = math.sqrt(max(0.0, radius**2 - d**2))
        q = half_width - radius + root
        ny, nd = root / radius, d / radius
    if roundness:
        power = 2.1
        dd = depth * math.pi / 2 * math.cos(angle)
        fraction = d / depth
        base = max(1.0e-16, 1 - fraction**power)
        oval = half_width * base ** (1 / power)
        oval_slope = -half_width / depth * fraction ** (power - 1) * base ** (1 / power - 1)
        dq = (-(1 - roundness) * d / math.sqrt(radius**2 - d**2) + roundness * oval_slope) * dd
        q = (1 - roundness) * q + roundness * oval
        normal = math.hypot(dq, dd)
        ny, nd = dd / normal, -dq / normal
    offset = inset * (1 + keel_gain * (d / depth) ** 4 * (1 - roundness))
    return q - offset * ny, d - offset * nd


def arm_chain(half_width, depth, z_top, roundness=0.0, inset=0.0, keel_radius=0.0, keel_gain=0.09):
    # Circular V flanks blend to the rounded terminal profile. Offset along
    # the analytic normal, then trim both inner flanks at their common keel.
    low, high = 0.0, 1.0
    for _ in range(40):
        mid = (low + high) / 2
        if flank_point(half_width, depth, roundness, mid, inset, keel_radius, keel_gain)[0] > 0:
            low = mid
        else:
            high = mid
    end = (low + high) / 2 if inset else 1.0
    left = []
    for i in range(17):
        q, d = flank_point(half_width, depth, roundness, end * i / 16, inset, keel_radius, keel_gain)
        left.append((-q, z_top - d))
    left[-1] = (0.0, left[-1][1])
    return left + [(-y, z) for y, z in left[-2::-1]]


def arm_profile_chain(radius, inset=0.0):
    width = arm_half_width(radius)
    flare = min(4.0, max(0.0, 2.0 * (40.0 - radius) / 6.0))
    keel_gain = 0.09 + 0.02 * max(0.0, min(1.0, (radius - 34.0) / 10.0))
    args = (arm_depth(radius), rimZ, arm_roundness(radius), inset, root_keel_radius(radius), keel_gain)
    left = arm_chain(width, *args)
    right = arm_chain(width + flare, *args)
    return left[:17] + right[17:]


def chain_face(radius, chain):
    pts = [(radius, y, z) for y, z in chain]
    edges = [*Spline(*pts[:17]).edges(), *Spline(*pts[16:]).edges(), *Polyline(pts[-1], pts[0]).edges()]
    return Face(Wire.combine(edges)[0])


arm_radii = [24.0, 28.0, 34.0, 40.0, 44.0, rMid, 60.0, 70.0, 80.0, 90.0, armTipReach, armTipReach + 2.0]
arm_sections = [chain_face(r, arm_profile_chain(r)) for r in arm_radii]
arm_along = loft(arm_sections, ruled=False)
# The terminal skin curves down from the rim; its inset forms the closed tip below the opening.
end_radius = 86.0
end_center = armTipReach - (armRootHalf - armTipWidth / 2) - end_radius
end_outer = Pos(end_center, 0, rimZ - 4.0) * Rot(90, 0, 0) * Cylinder(end_radius, 40)
arm_along = arm_along & end_outer

void_radii = [16.0, *arm_radii]
void_sections_arm = []
for radius in void_radii:
    src = min(radius, armTipReach)
    root_blend = max(0.0, min(1.0, (rMid - src) / (rMid - 28.0)))
    normal_projection = 1.0 + 0.04 * root_blend
    chain = arm_profile_chain(src, wallThickness * normal_projection)
    # Keep the slot open through the rim land and through the square tip.
    chain[0] = (chain[0][0] - 0.026, rimZ + 0.55)
    chain[-1] = (chain[-1][0] + 0.026, rimZ + 0.55)
    void_sections_arm.append(chain_face(radius, chain))
arm_void_along = loft(void_sections_arm, ruled=False)
end_inner = Pos(end_center, 0, rimZ - 4.0) * Rot(90, 0, 0) * Cylinder(end_radius - wallThickness, 40)
arm_void_along = arm_void_along & end_inner
notch_half_width = armRootHalf - wallThickness
notch_profiles = []
for r in (armTipReach - 3.0, armTipReach + 1.0):
    outline = Polyline(
        (r, -notch_half_width, rimZ + 0.55),
        (r, -notch_half_width, rimZ - 4.1),
        (r, notch_half_width, rimZ - 4.1),
        (r, notch_half_width, rimZ + 0.55),
        close=True,
    )
    notch_profiles.append(Face(Wire.combine(outline.edges())[0]))
end_opening = loft(notch_profiles, ruled=True)

arm_void_along = arm_void_along + end_opening

ne_arm = Rot(0, 0, 45) * arm_along
ne_void = Rot(0, 0, 45) * arm_void_along
nw_arm = mirror(ne_arm, Plane.YZ)
nw_void = mirror(ne_void, Plane.YZ)
plane_y = Plane(origin=(0, mirrorPlaneY, 0), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
south_arm = mirror(ne_arm + nw_arm, plane_y)
south_void = mirror(ne_void + nw_void, plane_y)
arms = ne_arm + nw_arm + south_arm
arm_voids = ne_void + nw_void + south_void

outer = cone + arms
pilot_r = pilotHoleDiameter / 2
hole_pos = Pos(0, mirrorPlaneY + pilotFromMirror, pilotHoleZ) * Rot(90, 0, 0) * Cylinder(pilot_r, 8)
hole_neg = Pos(0, mirrorPlaneY - pilotFromMirror, pilotHoleZ) * Rot(90, 0, 0) * Cylinder(pilot_r, 8)
result = outer - Compound([cone_void, arm_voids, hole_pos, hole_neg])


# Two opposed XZ slots. Their inner tool faces are in cavity air; their outer
# faces overrun the skin. The x bounds leave the source inlet walls intact.
slotInnerY = armUndersideWidth / 2
slotOuterY = plugReachY + wallThickness + 0.05
slotToolDepth = slotOuterY - slotInnerY
slotToolCenterY = (slotInnerY + slotOuterY) / 2
slot_tools = [
    Pos(0, mirrorPlaneY + side * slotToolCenterY, slotCenterZ) * Box(slotWidth, slotToolDepth, slotHeight)
    for side in (-1, 1)
]
assert len(slot_tools) == slotCount, "infeasible: exactly two slot cuts are required"
result = result - Compound(slot_tools)


# Four small extensions of the slot ends admit the off-centre PCB. Overlap
# the existing slot by 0.02 mm to avoid coincident Boolean tool faces while
# keeping its floor, roof and nominal x-side planes outside this z band.
reliefOverlap = 0.02
reliefInnerX = slotWidth / 2 - reliefOverlap
reliefWidth = pcbReliefOuterX - reliefInnerX
reliefCenterX = (pcbReliefOuterX + reliefInnerX) / 2
reliefHeight = pcbReliefZMax - pcbReliefZMin
reliefCenterZ = (pcbReliefZMax + pcbReliefZMin) / 2
relief_tools = [
    Pos(sx * reliefCenterX, mirrorPlaneY + sy * slotToolCenterY, reliefCenterZ)
    * Box(reliefWidth, slotToolDepth, reliefHeight)
    for sx in (-1, 1)
    for sy in (-1, 1)
]
assert len(relief_tools) == 4, "infeasible: all four symmetric PCB reliefs are required"
result = result - Compound(relief_tools)

assert len(result.solids()) == 1, "infeasible: shell must remain one connected solid"
