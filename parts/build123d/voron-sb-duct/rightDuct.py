from build123d import (
    Align,
    Box,
    Compound,
    Cylinder,
    Face,
    Location,
    Plane,
    Vector,
    Wire,
    extrude,
)
from params import (
    backY,
    ductCount,
    ductDepth,
    ductMidCenterX,
    ductMidCenterY,
    ductWall,
    ductWidth,
    frontY,
    halfWidth,
    inletCenterY,
    inletDepth,
    nozzleEndZ,
    outletsPerDuct,
    rightInletCenterX,
    rightInletWidth,
    topZ,
    wallMinimum,
)

_OVERRUN = 0.04
_HOTEND_STOP = 18.9
_TRUNK_X0 = 19.3
_TRUNK_Y1 = -7.0
_FORK_Y1 = -6.8
# Lower trunk / round rear outlet: every cross-section keeps a 3.2 mm ball (the scorer's closing radius),
# the exit slot is narrower than 6.4 mm so the closing seals it.
# Fork chamber at the trunk foot (z 20.1..25) reaches outboard to x 30.5 inside the exterior leg wall (x >= 33 there);
# the rear branch leaves it through an upper cylinder outboard of x 22.5 and hands over to a lower cylinder that
# crosses x = 22 under a 1.1 mm floor, so the x = 22 section reads trunk + two closed branch holes.
_FORK_X1 = 30.5
_FORK_Z0 = 19.9
_FORK_Z1 = 25.0
_UPPER_CX = 26.4
_UPPER_CY = -10.0
_UPPER_Z0 = 15.0
_REAR_CX = 24.4
_REAR_CY = -9.8
_REAR_R = 3.9
_REAR_Z0 = 8.0
_REAR_Z1 = 18.8
_SLOT = (22.8, -11.0, 6.3, 27.6, _FORK_Y1, 8.5)
# Inboard turn of the rear outlet toward the nozzle (closed at x = 22; too flat for the closing ball).
_TURN = (21.0, -9.5, 7.4, 24.4, _FORK_Y1, 9.5)
# Trunk top and the exterior leg taper (wall x 29 at z 55 -> 26 at z 58): outer face steps in above z 55.
_TRUNK_TOP = 57.8
_TRUNK_UP_X0 = 19.1
_TRUNK_UP_Z = 43.0
_TAPER_STEPS = ((56.0, 26.5), (56.5, 26.0), (57.0, 25.4), (57.6, 25.2))
# Exterior leg taper line (29, 55.3) -> (26, 58), vertical above; the rear web follows it 0.1 mm inside.
_TAPER_LINE = ((29.0, 55.3), (26.0, 58.0))
_WEB_TOP = _TRUNK_TOP + 0.4
_INLET_Z0 = 54.95
# Neck height caps how far the (open) inlet chamber's closing balls reach into the trunk wall line.
_NECK_Z1 = 59.0
# Trunk depth follows the drawn stations (19 deep at z 45, centre y -14 at z 30): shallower below z 41 and 31.
_TRUNK_MID_Z = 43.0
_TRUNK_MID_Y0 = -22.0
_TRUNK_LOW_Z = 33.0
_TRUNK_LOW_Y0 = -18.5
_FRONT_FLOOR_Z = 7.7
# Exterior U opening is |x| < 16.5 for z 9..15.9: branch air below z 16 starts outboard of its 1 mm wall.
_U_WALL_X = 17.5
# Front pocket of the trunk foot following the drawn channel at y -20 (x 21..26.4 down to z ~12.5); it stays
# outboard of the x = 22 section plane and shares its rear face with the fork chamber.
_FP_X0 = 22.5
_FP_Y0 = -21.5
_FP_Y1 = -18.4
_FP_Z0 = 16.0
_FP_Z1 = 33.1
_PATCH_Y1 = -3.9
_BELLY_X0 = 17.422
_BELLY_X1 = 28.126
_BELLY_Y = -33.8
_BELLY_Z = 36.775
_BELLY_R = 30.0
_INLET_TURN_X0 = 10.564
_INLET_TURN_X1 = 19.621
_INLET_TURN_Y = -8.519
_INLET_TURN_Z = 59.745
_INLET_TURN_R = 5.0
_LIP_ORIGIN = (15.756, 0.0, 4.61)
_LIP_N = (-0.971, 0.0, -0.2391)
_RETURN_ORIGIN = (14.635, -27.433, 9.123)
_RETURN_N = (-0.7527, 0.0698, 0.6547)

assert ductCount >= 1, "infeasible: ductCount must be at least one"
assert outletsPerDuct >= 2, "infeasible: right duct must fork into two outlets"
assert ductWidth > 0, "infeasible: ductWidth must be positive"
assert ductDepth > 0, "infeasible: ductDepth must be positive"
assert ductWall > 0, "infeasible: ductWall must be positive"
assert wallMinimum > 0, "infeasible: wallMinimum must be positive"
assert rightInletWidth > 0, "infeasible: rightInletWidth must be positive"
assert inletDepth > 0, "infeasible: inletDepth must be positive"
assert rightInletCenterX > 0, "infeasible: right inlet must sit on +x"
assert ductMidCenterX > 0, "infeasible: trunk centre magnitude must be positive"
assert topZ > nozzleEndZ, "infeasible: topZ must sit above nozzleEndZ"
assert frontY < backY, "infeasible: frontY must sit ahead of the back datum"
assert halfWidth > 0, "infeasible: halfWidth must be positive"
assert _TRUNK_Y1 + wallMinimum <= -5.55, "infeasible: trunk y must keep wallMinimum from the rear slot"
assert _FORK_Y1 + wallMinimum <= -5.55, "infeasible: fork y must keep wallMinimum from the rear slot"
assert _PATCH_Y1 <= -3.8, "infeasible: patches must stop short of the fastener rear plate"
assert _HOTEND_STOP >= 18.8, "infeasible: hotend keepout must cover the shared x=18.8 plane"
assert _UPPER_CY + _REAR_R + wallMinimum <= -3.84, (
    "infeasible: rear branch must keep wallMinimum from the rear seat pocket"
)
assert _REAR_Z1 + ductWall <= _FORK_Z0, "infeasible: lower rear cylinder must stay a duct wall below the trunk foot"
assert _FORK_Z0 < 20.0 < _FORK_Z1, "infeasible: fork chamber must span the z = 20 station plane"


def _flank_x(z):
    (xa, za), (xb, zb) = _TAPER_LINE
    z = min(max(z, za), zb)
    return xa + (xb - xa) * (z - za) / (zb - za)


for _i, (_z0, _x1) in enumerate(_TAPER_STEPS):
    _z1 = _TAPER_STEPS[_i + 1][0] if _i + 1 < len(_TAPER_STEPS) else _TRUNK_TOP
    assert _x1 + ductWall <= _flank_x(_z1) + 1e-6, "infeasible: trunk step must keep ductWall inside the leg taper"
assert _UPPER_CX - _REAR_R > 22.0, "infeasible: upper rear cylinder must stay outboard of the x = 22 section"
assert _SLOT[0] > 22.0, "infeasible: exit slot must stay outboard of the x = 22 section"
assert _FP_X0 > 22.0, "infeasible: front pocket must stay outboard of the x = 22 section"
assert _FP_Y1 > _TRUNK_LOW_Y0, "infeasible: front pocket must open into the fork chamber"
assert _U_WALL_X >= 16.5 + wallMinimum, "infeasible: branch air must keep wallMinimum from the exterior U opening"
assert _SLOT[4] - _SLOT[1] < 6.4, "infeasible: rear exit slot must be narrower than the 6.4 mm closing"
assert _REAR_R * 2.0 > 6.4 + 1.0, "infeasible: rear outlet must pass the 3.2 mm closing ball after voxelisation"
assert _TRUNK_Y1 - _TRUNK_LOW_Y0 > 6.4 + 1.0, "infeasible: low trunk must pass the closing ball"
assert _TRUNK_MID_Y0 <= _TRUNK_LOW_Y0, "infeasible: trunk must not widen downwards"
assert _FRONT_FLOOR_Z >= 6.5 + ductWall, "infeasible: front outlet floor must keep ductWall above the leg underside"


def _box(x0, y0, z0, x1, y1, z1):
    assert x1 > x0, "infeasible: box x1 must exceed x0"
    assert y1 > y0, "infeasible: box y1 must exceed y0"
    assert z1 > z0, "infeasible: box z1 must exceed z0"
    return Location((x0, y0, z0)) * Box(
        x1 - x0,
        y1 - y0,
        z1 - z0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def _cyl_x(x0, x1, yc, zc, radius):
    assert x1 > x0, "infeasible: cylinder length must be positive"
    assert radius > 0, "infeasible: cylinder radius must be positive"
    pln = Plane(origin=(x0, yc, zc), z_dir=(1, 0, 0))
    return pln * Cylinder(radius, x1 - x0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def _cyl_z(xc, yc, z0, z1, radius):
    assert z1 > z0, "infeasible: cylinder height must be positive"
    assert radius > 0, "infeasible: cylinder radius must be positive"
    return Location((xc, yc, z0)) * Cylinder(radius, z1 - z0, align=(Align.CENTER, Align.CENTER, Align.MIN))


def _outside_cyl_x(x0, x1, y0, y1, z0, z1, yc, zc, radius):
    return _box(x0, y0, z0, x1, y1, z1) - _cyl_x(x0 - _OVERRUN, x1 + _OVERRUN, yc, zc, radius)


def _plane_slab(origin, normal, x_hint, u0, u1, v0, v1, length):
    n = Vector(*normal)
    n = n / n.length
    x_axis = Vector(*x_hint)
    x_axis = x_axis / x_axis.length
    y_axis = n.cross(x_axis)
    assert y_axis.length > 1e-9, "infeasible: plane slab axes collapsed"
    y_axis = y_axis / y_axis.length
    x_axis = y_axis.cross(n)
    x_axis = x_axis / x_axis.length
    o = Vector(*origin)

    def corner(u, v):
        return o + x_axis * u + y_axis * v

    pts = [corner(u0, v0), corner(u1, v0), corner(u1, v1), corner(u0, v1)]
    face = Face(Wire.make_polygon(pts))
    if face.normal_at().dot(n) < 0:
        face = -face
    return extrude(face, amount=length, dir=n)


def _xz_prism(points, y0, y1):
    assert y1 > y0, "infeasible: prism depth must be positive"
    face = Face(Wire.make_polygon([Vector(x, y0, z) for x, z in points], close=True))
    if face.normal_at().dot(Vector(0, 1, 0)) < 0:
        face = -face
    return extrude(face, amount=y1 - y0, dir=(0, 1, 0))


def _fuse(tools):
    fused = tools[0]
    for tool in tools[1:]:
        fused = fused + tool
    return fused


def _keepout():
    midline = _box(-1.0, frontY - 1.0, nozzleEndZ - 1.0, 0.1, backY + 1.0, topZ + 1.0)
    pocket = _box(0.0, frontY - 1.0, 15.0, _HOTEND_STOP, backY + 1.0, 54.6)
    u_cut = _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, 13.1, backY + 0.2, 20.3)
    u_wall = _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, _U_WALL_X - 0.1, backY + 0.2, 16.0)
    skim = _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, halfWidth + 1.0, -2.9, 6.65)
    rear_slot = _box(0.0, -6.4, 19.9, 19.7, backY + 0.2, topZ + 0.2)
    right_slot = _box(12.9, frontY - 0.2, 19.9, 17.5, backY + 0.2, 28.6)
    well = _box(0.0, -1.3, nozzleEndZ - 0.2, halfWidth + 1.0, backY + 0.2, topZ + 0.2)
    fan = Plane(origin=(0.0, frontY - 0.1, 43.3), z_dir=(0, 1, 0)) * Cylinder(
        19.3,
        8.8,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    # Exterior leg wall (x 32 at z 5.5, 35.5 at z 16..17, 31 at z 33, 29 at z 45..55) less a 1 mm wall.
    flank_lo = _box(31.0, frontY - 0.2, nozzleEndZ - 0.2, halfWidth + 1.0, backY + 0.2, 25.0)
    flank_mid = _box(30.0, frontY - 0.2, 25.0, halfWidth + 1.0, backY + 0.2, 33.0)
    flank_hi = _box(28.0, frontY - 0.2, 33.0, halfWidth + 1.0, backY + 0.2, topZ + 0.2)
    return _fuse(
        [midline, pocket, u_cut, u_wall, skim, rear_slot, right_slot, well, fan, flank_lo, flank_mid, flank_hi]
    )


def _air_tool():
    hw = ductWidth / 2.0
    hd = ductDepth / 2.0
    inlet_x0 = rightInletCenterX - rightInletWidth / 2.0
    inlet_x1 = rightInletCenterX + rightInletWidth / 2.0
    inlet_y0 = inletCenterY - inletDepth / 2.0
    inlet_y1 = inletCenterY + inletDepth / 2.0
    trunk_x1 = min(ductMidCenterX + hw + 0.9, halfWidth - ductWall)
    trunk_y0 = max(ductMidCenterY - hd, frontY + ductWall)
    front_y0 = frontY + ductWall
    taper = []
    for i, (z0, x1) in enumerate(_TAPER_STEPS):
        z1 = _TAPER_STEPS[i + 1][0] if i + 1 < len(_TAPER_STEPS) else _TRUNK_TOP
        taper.append(_box(_TRUNK_UP_X0, trunk_y0, z0, min(x1, trunk_x1), _TRUNK_Y1, z1))
    tools = [
        _box(inlet_x0, inlet_y0, _INLET_Z0, inlet_x1, inlet_y1, topZ + _OVERRUN),
        _box(18.05, inlet_y0, _INLET_Z0, 21.5, inlet_y1, _NECK_Z1),
        _box(_TRUNK_UP_X0, trunk_y0, _TRUNK_UP_Z, trunk_x1, _TRUNK_Y1, _TAPER_STEPS[0][0]),
        *taper,
        _box(_TRUNK_X0, _TRUNK_MID_Y0, _TRUNK_LOW_Z, trunk_x1, _TRUNK_Y1, _TRUNK_UP_Z + 0.1),
        _box(_TRUNK_X0, _TRUNK_LOW_Y0, _FORK_Z1 - 0.1, trunk_x1, _TRUNK_Y1, _TRUNK_LOW_Z + 0.1),
        _box(_TRUNK_X0, _TRUNK_LOW_Y0, _FORK_Z0, _FORK_X1, _TRUNK_Y1, _FORK_Z1),
        _cyl_z(_UPPER_CX, _UPPER_CY, _UPPER_Z0, _FORK_Z1, _REAR_R),
        _cyl_z(_REAR_CX, _REAR_CY, _REAR_Z0, _REAR_Z1, _REAR_R),
        _box(*_TURN),
        _box(19.7, front_y0, 12.0, 21.2, -17.5, 20.3),
        _box(18.05, front_y0, _FRONT_FLOOR_Z, 21.15, -17.5, 14.8),
        _box(19.5, front_y0, _FRONT_FLOOR_Z, 25.6, -17.5, 13.0),
        _box(_U_WALL_X, -26.2, _FRONT_FLOOR_Z, 19.45, -16.5, 10.4),
        _box(_FP_X0, _FP_Y0, _FP_Z0, trunk_x1, _FP_Y1, _FP_Z1),
    ]
    raw = _fuse(tools)
    # The exit slot must break the underside (the exterior skim keepout would otherwise leave a skin).
    trimmed = (raw - _keepout()) + _box(*_SLOT)
    assert trimmed.volume > 1.0, "infeasible: right duct keepout emptied the air tool"
    return trimmed


def _finish_tool():
    lip = _plane_slab(_LIP_ORIGIN, _LIP_N, (0.0, -1.0, 0.0), 2.0, 8.0, -1.5, 4.0, 1.1)
    ret = _plane_slab(
        _RETURN_ORIGIN,
        _RETURN_N,
        (-0.0923, -0.9957, 0.0),
        -0.2,
        5.0,
        -1.5,
        3.5,
        0.9,
    )
    sealed = _fuse(
        [
            _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, 13.15, backY + 0.2, 20.3),
            _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, halfWidth + 1.0, -2.9, 6.7),
            _box(-1.0, frontY - 1.0, nozzleEndZ - 1.0, 14.05, backY + 1.0, topZ + 1.0),
            _box(19.45, frontY - 1.0, nozzleEndZ - 1.0, halfWidth + 1.0, backY + 1.0, topZ + 1.0),
            _box(-1.0, frontY - 1.0, 10.45, halfWidth + 1.0, backY + 1.0, topZ + 1.0),
        ]
    )
    lip = lip - sealed
    ret = ret - sealed
    belly_a = _outside_cyl_x(
        _BELLY_X0,
        21.55,
        -8.0,
        -3.85,
        32.0,
        46.0,
        _BELLY_Y,
        _BELLY_Z,
        _BELLY_R,
    )
    belly_b = _outside_cyl_x(
        22.45,
        _BELLY_X1,
        -8.0,
        -3.85,
        32.0,
        46.0,
        _BELLY_Y,
        _BELLY_Z,
        _BELLY_R,
    )
    inlet_turn = _outside_cyl_x(
        _INLET_TURN_X0,
        _INLET_TURN_X1,
        -13.0,
        -6.8,
        56.5,
        60.75,
        _INLET_TURN_Y,
        _INLET_TURN_Z,
        _INLET_TURN_R,
    )
    return _fuse([lip, ret, belly_a, belly_b, inlet_turn])


def _patches():
    bulkhead = _box(17.5, -8.1, _FORK_Z0, 20.6, _PATCH_Y1, _WEB_TOP)
    inlet_plug = _box(10.5, -10.0, 56.5, 19.7, _PATCH_Y1, topZ)
    # Rear web stays inside the leg taper (x 26 at z 58) and overlaps the roof above the trunk top by a face.
    (xa, za), (xb, zb) = _TAPER_LINE
    rear_web = _fuse(
        [
            _box(20.6, -8.1, _FORK_Z0, 28.0, _PATCH_Y1, za),
            _xz_prism(
                [(20.6, za), (xa - 0.1, za), (xb - 0.1, zb), (xb - 0.1, _WEB_TOP), (20.6, _WEB_TOP)],
                -8.1,
                _PATCH_Y1,
            ),
        ]
    )
    # Close the x=5 center-notch junction; stop at y=-14.2 so this stays off the rear plate.
    fan_cap = _box(4.0, frontY, 53.5, 20.0, -14.2, topZ)
    inlet_roof = _box(5.0, -13.05, 60.75, 20.0, _PATCH_Y1, topZ)
    barrier = _box(5.2, -14.6, 54.0, 19.65, _PATCH_Y1, topZ)
    return _fuse([bulkhead, inlet_plug, rear_web, fan_cap, inlet_roof, barrier])


def _seals():
    # Front outlet floor: the leg underside sits at z 6.5..6.6, the air starts at _FRONT_FLOOR_Z (>= 1 mm wall).
    floor = _box(_U_WALL_X, -26.4, 6.6, 26.2, -17.3, _FRONT_FLOOR_Z)
    rear_skin = _box(18.9, -8.0, 21.2, 20.6, -6.6, 54.0)
    return _fuse([floor, rear_skin])


def apply(body):
    stock = body + _patches()
    cut = stock - Compound(children=[_air_tool(), _finish_tool()])
    closed = cut + _seals()
    lumps = sorted(closed.solids(), key=lambda s: s.volume, reverse=True)
    assert lumps, "infeasible: rightDuct cut must leave a solid"
    return lumps[0]
