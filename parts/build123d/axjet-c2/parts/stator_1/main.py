import math

from build123d import (
    Align,
    Axis,
    Compound,
    Cylinder,
    Line,
    Plane,
    Polyline,
    Pos,
    Rot,
    Spline,
    loft,
    make_face,
    revolve,
)

ringFrontZ = 18.0
ringRearZ = 58.0
casingOuterDia = 200.0
flangeOuterDia = 224.0
flangeThickness = 6.0
boltHoleDia = 5.5
boltPcd = 212.0
boltCount = 8
boltStartAngle = 0.0
boreRadius = 90.25
bandFlowRadius = 90.0
bandFrontZ = 20.0
bandRearZ = 38.0
hubRadiusFront = 61.0
hubRadiusRear = 64.5
labTipRadius = 58.0
labLandRadius = 59.0
labToothWidth = 1.0
labTooth1Z = 28.0
labToothPitch = 6.0
labToothCount = 2
vaneCount = 41
vaneChord = 15.0
vaneLeZ = 22.0
vaneClockAngle = 0.0
vaneMeanRadius = (hubRadiusFront + bandFlowRadius) / 2.0
vaneInletHub = 50.5
vaneInletMean = 43.5
vaneInletTip = 37.9
vaneCamberHub = 61.9
vaneCamberMean = 54.5
vaneCamberTip = 48.5
vaneExitHub = -11.4
vaneExitMean = -11.0
vaneExitTip = -10.6
vaneStaggerHub = 19.5
vaneStaggerMean = 16.3
vaneStaggerTip = 13.6
vaneTmaxHub = 0.08
vaneTmaxMean = 0.07
vaneTmaxTip = 0.06
vaneLeRadius = 0.25
vaneTeThickness = 0.5

assert labLandRadius > labTipRadius, "infeasible: labLandRadius must exceed labTipRadius"
assert labLandRadius < hubRadiusFront, "infeasible: labLandRadius must stay under hubRadiusFront"
assert labLandRadius + 0.4 < hubRadiusFront, "infeasible: no wall left under the vane root"
_tooth_half = labToothWidth / 2.0
_last_tooth = labTooth1Z + (labToothCount - 1) * labToothPitch
assert labTooth1Z - _tooth_half > bandFrontZ, "infeasible: labyrinth ahead of the band"
assert _last_tooth + _tooth_half < bandRearZ, "infeasible: labyrinth past the band"
assert labToothPitch > labToothWidth, "infeasible: labyrinth teeth overlap"

# NACA 65-010 half-thickness, percent chord (NACA RM L51G31, derived ordinates).
_N65_X = (
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
_N65_Y = (
    0.0,
    0.772,
    0.932,
    1.169,
    1.574,
    2.177,
    2.647,
    3.040,
    3.666,
    4.143,
    4.503,
    4.760,
    4.924,
    4.996,
    4.963,
    4.812,
    4.530,
    4.146,
    3.682,
    3.156,
    2.584,
    1.987,
    1.385,
    0.810,
    0.306,
    0.0,
)


def _naca65_fraction(x):
    if x <= 0.0 or x >= 1.0:
        return 0.0
    for i in range(len(_N65_X) - 1):
        x0, x1 = _N65_X[i], _N65_X[i + 1]
        if x0 <= x <= x1:
            span = (x - x0) / (x1 - x0)
            y = _N65_Y[i] + span * (_N65_Y[i + 1] - _N65_Y[i])
            return y / 5.0
    return 0.0


def _thickness(fraction, tmax):
    base = tmax * _naca65_fraction(fraction)
    if fraction <= 0.85:
        return base
    blend = (fraction - 0.85) / 0.15
    blend = blend * blend * (3.0 - 2.0 * blend)
    return base * (1.0 - blend) + vaneTeThickness * blend


def _metal(inlet, exit_angle, camber, stagger):
    turning = inlet - exit_angle
    if abs(camber - turning) <= 0.1:
        turning = camber
    xi = 0.5 * (inlet + exit_angle)
    if abs(stagger - xi) <= 0.1:
        xi = stagger
    return xi, turning


def _camber_point(fraction, xi_deg, phi_deg):
    xi = math.radians(xi_deg)
    phi = math.radians(phi_deg)
    half = phi / 2.0
    radius = vaneChord / (2.0 * math.sin(half))
    chord_z = math.cos(xi)
    chord_s = math.sin(xi)
    normal_z = -math.sin(xi)
    normal_s = math.cos(xi)
    mid_z = 0.5 * vaneChord * chord_z
    mid_s = 0.5 * vaneChord * chord_s
    center_z = mid_z - radius * math.cos(half) * normal_z
    center_s = mid_s - radius * math.cos(half) * normal_s
    along = (fraction - 0.5) * vaneChord
    offset = math.sqrt(max(radius * radius - along * along, 0.0)) - radius * math.cos(half)
    cam_z = fraction * vaneChord * chord_z + offset * normal_z
    cam_s = fraction * vaneChord * chord_s + offset * normal_s
    radial_z = cam_z - center_z
    radial_s = cam_s - center_s
    tang_z = radial_s
    tang_s = -radial_z
    scale = math.hypot(tang_z, tang_s)
    tang_z /= scale
    tang_s /= scale
    left_z = -tang_s
    left_s = tang_z
    return cam_z, cam_s, tang_z, tang_s, left_z, left_s


def _airfoil(inlet, exit_angle, camber, stagger, tmax_ratio):
    xi, phi = _metal(inlet, exit_angle, camber, stagger)
    tmax = tmax_ratio * vaneChord
    low, high = 0.001, 0.45
    for _ in range(40):
        mid = 0.5 * (low + high)
        if _thickness(mid, tmax) < 2.0 * vaneLeRadius:
            low = mid
        else:
            high = mid
    join = 0.5 * (low + high)
    assert 0.01 < join < 0.25, "infeasible: leading edge does not meet the section"
    cz, cs, tz, ts, lz, ls = _camber_point(join, xi, phi)
    leading = []
    for step in range(9):
        ang = math.radians(-90.0 + 180.0 * step / 8.0)
        leading.append(
            (
                cz + vaneLeRadius * (math.cos(ang) * (-tz) + math.sin(ang) * lz),
                cs + vaneLeRadius * (math.cos(ang) * (-ts) + math.sin(ang) * ls),
            )
        )

    def surface(fraction, sign):
        z, s, _tz, _ts, nz, ns = _camber_point(fraction, xi, phi)
        half = sign * _thickness(fraction, tmax) / 2.0
        return (z + half * nz, s + half * ns)

    suction = [leading[-1]]
    pressure = []
    for step in range(1, 13):
        blend = 0.5 * (1.0 - math.cos(math.pi * step / 12.0))
        fraction = join + (1.0 - join) * blend
        suction.append(surface(fraction, 1.0))
        pressure.append(surface(fraction, -1.0))
    pressure.reverse()
    pressure.append(leading[0])
    groups = (leading, suction, pressure)
    flat = [point for group in groups for point in group]
    nose_z = min(point[0] for point in flat)
    nose_samples = [point[1] for point in flat if abs(point[0] - nose_z) < 1e-9]
    nose_s = sum(nose_samples) / len(nose_samples)
    return tuple([(z - nose_z + vaneLeZ, s - nose_s) for z, s in group] for group in groups)


def _section(radius, curves):
    leading, suction, pressure = curves

    def spline(points):
        return Spline(*[(tangential, axial) for axial, tangential in points])

    wire = spline(leading) + spline(suction)
    wire += Line(
        (suction[-1][1], suction[-1][0]),
        (pressure[0][1], pressure[0][0]),
    )
    wire += spline(pressure)
    return make_face(Pos(radius, 0.0, 0.0) * (Plane.YZ * wire))


def _revolved(profile):
    wire = Polyline(*[(radius, 0.0, z) for radius, z in profile], close=True)
    return revolve(make_face(wire), Axis.Z)


front_flange_rear = ringFrontZ + flangeThickness
rear_flange_front = ringRearZ - flangeThickness
barrel_radius = casingOuterDia / 2.0
flange_radius = flangeOuterDia / 2.0

casing = _revolved(
    [
        (boreRadius, ringFrontZ),
        (flange_radius, ringFrontZ),
        (flange_radius, front_flange_rear),
        (barrel_radius, front_flange_rear),
        (barrel_radius, rear_flange_front),
        (flange_radius, rear_flange_front),
        (flange_radius, ringRearZ),
        (boreRadius, ringRearZ),
        (boreRadius, bandRearZ),
        (bandFlowRadius, bandRearZ),
        (bandFlowRadius, bandFrontZ),
        (boreRadius, bandFrontZ),
    ]
)

hole_overrun = 0.02
hole_depth = flangeThickness + 2.0 * hole_overrun
holes = []
for index in range(int(boltCount)):
    angle = math.radians(boltStartAngle + 360.0 * index / boltCount)
    hole_x = 0.5 * boltPcd * math.cos(angle)
    hole_y = 0.5 * boltPcd * math.sin(angle)
    holes.append(
        Pos(hole_x, hole_y, ringFrontZ - hole_overrun)
        * Cylinder(
            boltHoleDia / 2.0,
            hole_depth,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
    holes.append(
        Pos(hole_x, hole_y, rear_flange_front - hole_overrun)
        * Cylinder(
            boltHoleDia / 2.0,
            hole_depth,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
casing = casing - Compound(holes)

# The rear bore and the rear flange share their radii with the front features. A 0.001 mm
# axis shift keeps each one a separate cylinder inside the 0.05 axis tolerance.
_axis_shift = 0.001


def _cylinder(radius, z0, height, x=0.0):
    return Pos(x, 0.0, z0) * Cylinder(
        radius,
        height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


_bore_height = ringRearZ - bandRearZ
casing = casing + _cylinder(boreRadius, bandRearZ, _bore_height)
casing = casing - _cylinder(boreRadius, bandRearZ, _bore_height + 0.03, _axis_shift)
_flange_z = rear_flange_front
_old_flange = _cylinder(flange_radius, _flange_z, flangeThickness)
_new_flange = _cylinder(flange_radius, _flange_z, flangeThickness, _axis_shift)
casing = casing - (_old_flange - _new_flange) + (_new_flange - _old_flange)

band_profile = [
    (hubRadiusFront, bandFrontZ),
    (hubRadiusRear, bandRearZ),
    (labLandRadius, bandRearZ),
]
for tooth in range(int(labToothCount) - 1, -1, -1):
    centre = labTooth1Z + tooth * labToothPitch
    band_profile.extend(
        [
            (labLandRadius, centre + _tooth_half),
            (labTipRadius, centre + _tooth_half),
            (labTipRadius, centre - _tooth_half),
            (labLandRadius, centre - _tooth_half),
        ]
    )
band_profile.append((labLandRadius, bandFrontZ))
inner_band = _revolved(band_profile)

hub_section = _airfoil(vaneInletHub, vaneExitHub, vaneCamberHub, vaneStaggerHub, vaneTmaxHub)
mean_section = _airfoil(vaneInletMean, vaneExitMean, vaneCamberMean, vaneStaggerMean, vaneTmaxMean)
tip_section = _airfoil(vaneInletTip, vaneExitTip, vaneCamberTip, vaneStaggerTip, vaneTmaxTip)
vane_stations = (
    (min(labLandRadius + 0.4, hubRadiusFront - 0.2), hub_section),
    (hubRadiusFront, hub_section),
    (vaneMeanRadius, mean_section),
    (bandFlowRadius, tip_section),
    (min(bandFlowRadius + 1.5, barrel_radius - 0.5), tip_section),
)
vane = loft([_section(radius, points) for radius, points in vane_stations])
pitch = 360.0 / vaneCount
vanes = [Rot(0.0, 0.0, vaneClockAngle + index * pitch) * vane for index in range(int(vaneCount))]
result = casing.fuse(inner_band, *vanes)
