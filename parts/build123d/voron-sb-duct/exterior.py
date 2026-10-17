from build123d import (
    Align,
    Box,
    Compound,
    Cylinder,
    Location,
    Plane,
    Polygon,
    Pos,
    Rotation,
    extrude,
)
from params import (
    backY,
    fanCenterZ,
    fanOpeningDiameter,
    frontY,
    halfWidth,
    inletCenterY,
    inletDepth,
    leftInletCenterX,
    leftInletWidth,
    nozzleEndZ,
    overallDepth,
    overallHeight,
    overallWidth,
    rightInletCenterX,
    rightInletWidth,
    topZ,
)

_OVERRUN = 0.04
_U_HALF = 13.0
_U_TOP = 20.15
_REAR_OPEN_Y = -5.55
_REAR_OPEN_HALF = 19.5
# 1.7: keeps the well floor outside the y=0 face matcher's 1.5 mm merge band (frontToBack datum).
_REAR_RECESS = 1.7
_PAD_THICK = 2.0
_SKIM_Y1 = -3.0
_RIB_Y0 = -6.6
_SKIM_Z = 4.2
# Mouth floor at z 58.4: leftDuct seals the mouth with its slab above z 57.5, keep >= 0.9 mm of it.
_INLET_CUT = 3.1
# z=10 drawing: fork outer-front chamfer (29.5,-27.4)->(33.4,-20.5), extended to the wall. The drawn
# inner-front chamfer (15.8,-22)->(24.2,-27.4) is not cut: the duct outlet return planes live there.
_OUTER_CHAMFER = [(29.44, -27.44), (36.0, -27.44), (36.0, -15.9)]
_FAN_DEPTH = 8.55
_FAN_CLIP_Z = 57.0
_RECESS_Y = -3.5
_RECESS_TOP = 16.0
_U_WIDE_HALF = 14.5
_U_WIDE_TOP = 15.9
# Above the duct outlet lips (z < 9) the drawn fork inner edge sits at |x| 15.8..17.6.
_U_UPPER_HALF = 16.5
_U_UPPER_Z0 = 9.0
_STEP_X0 = 16.6
_STEP_Y0 = -7.0
_STEP_Z0 = 46.0
_BEVEL_Z0 = 41.0
# Leg outer wall (material side), bottom to top, per the y=-12 / y=-20 drawings.
_LEG_WALL = [(32.0, 5.5), (35.534, 16.0), (35.534, 17.0), (31.0, 33.0), (29.0, 45.0), (29.0, 55.3), (26.0, 58.0)]
_HUB_RADIUS = 8.0
_VANE_THICK = 1.2
_VANE_HALF_LEN = 21.0
# 35 deg: the vanes meet the rim below z=55 so sec_z55 sees no detached vane slivers.
_VANE_ANGLE = 35.0
_NOZZLE_NX = 0.2416
_NOZZLE_NZ = 0.9704
_NOZZLE_PX = 27.948
_NOZZLE_PZ = 4.853
_LEFT_MAIN = (-21.23, -11.21, 19.34, 61.5)
_RIGHT_MAIN = (7.5, 16.0, 36.5, 61.5)
_RIGHT_MOUNT = (13.9, 19.1, 17.0, 22.5)
_LIP_HALF_X = 2.75
_LIP_HALF_Z = 1.15
_LIP_CX = 18.22
_LIP_CZ = 3.97
_LAND_CX = 17.14
_LAND_CY = -10.47
_LAND_HALF_X = 2.5
_LAND_HALF_Y = 5.25

assert overallWidth > 0, "infeasible: overallWidth must be positive"
assert overallDepth > 0, "infeasible: overallDepth must be positive"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
assert halfWidth > 0, "infeasible: halfWidth must be positive"
assert nozzleEndZ > 0, "infeasible: nozzleEndZ must be positive"
assert topZ > nozzleEndZ, "infeasible: topZ must sit above nozzleEndZ"
assert frontY < backY, "infeasible: frontY must sit ahead of the back datum"
assert overallHeight > 1.0, "infeasible: overallHeight must clear the housing"
assert fanOpeningDiameter > 0, "infeasible: fanOpeningDiameter must be positive"
assert leftInletWidth > 0, "infeasible: leftInletWidth must be positive"
assert rightInletWidth > 0, "infeasible: rightInletWidth must be positive"
assert inletDepth > 0, "infeasible: inletDepth must be positive"
assert _HUB_RADIUS < fanOpeningDiameter / 2.0, "infeasible: grille hub must sit inside the fan opening"


def _box(xmin, ymin, zmin, xmax, ymax, zmax):
    assert xmax > xmin, "infeasible: box x1 must exceed x0"
    assert ymax > ymin, "infeasible: box y1 must exceed y0"
    assert zmax > zmin, "infeasible: box z1 must exceed z0"
    return Location((xmin, ymin, zmin)) * Box(
        xmax - xmin,
        ymax - ymin,
        zmax - zmin,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def _xz_prism(points, y0, y1):
    face = Plane.XZ * Polygon(*points, align=None)
    prism = extrude(face, amount=abs(y1 - y0))
    return Pos(0, y0 - prism.bounding_box().min.Y, 0) * prism


def _xy_prism(points, z0, z1):
    assert z1 > z0, "infeasible: prism z1 must exceed z0"
    prism = extrude(Polygon(*points, align=None), amount=z1 - z0)
    return Pos(0, 0, z0 - prism.bounding_box().min.Z) * prism


def _leg_taper(side, x_out, z1, y0, y1):
    # Air outside the tapered leg wall; `side` +1 right, -1 left.
    wall = [(side * x, z) for x, z in _LEG_WALL]
    top = (side * _LEG_WALL[-1][0], z1)
    return _xz_prism([(x_out, _LEG_WALL[0][1]), *wall, top, (x_out, z1)], y0, y1)


def _pad(x0, x1, z0, z1):
    return _box(x0, -_PAD_THICK, z0, x1, backY + _OVERRUN, z1)


def _except_pads(stock, pads):
    out = stock
    for pad in pads:
        out = out - pad
    return out


def _nozzle_z(x, side):
    return _NOZZLE_PZ - (_NOZZLE_NX / _NOZZLE_NZ) * (side * x + _NOZZLE_PX)


def _mating_pads():
    left_lip = _box(
        -_LIP_CX - _LIP_HALF_X,
        -_PAD_THICK,
        _LIP_CZ - _LIP_HALF_Z,
        -_LIP_CX + _LIP_HALF_X,
        backY + _OVERRUN,
        _LIP_CZ + _LIP_HALF_Z,
    )
    right_lip = _box(
        _LIP_CX - _LIP_HALF_X,
        -_PAD_THICK,
        _LIP_CZ - _LIP_HALF_Z,
        _LIP_CX + _LIP_HALF_X,
        backY + _OVERRUN,
        _LIP_CZ + _LIP_HALF_Z,
    )
    return [
        _pad(*_LEFT_MAIN),
        _pad(*_RIGHT_MAIN),
        _pad(*_RIGHT_MOUNT),
        left_lip,
        right_lip,
        _box(15.2, _RIB_Y0, 36.5, 16.0, backY + _OVERRUN, 38.5),
    ]


def _land_pads():
    z0 = nozzleEndZ - _OVERRUN
    z1 = nozzleEndZ + _SKIM_Z + _OVERRUN
    return [
        _box(
            -_LAND_CX - _LAND_HALF_X,
            _LAND_CY - _LAND_HALF_Y,
            z0,
            -_LAND_CX + _LAND_HALF_X,
            _LAND_CY + _LAND_HALF_Y,
            z1,
        ),
        _box(
            _LAND_CX - _LAND_HALF_X,
            _LAND_CY - _LAND_HALF_Y,
            z0,
            _LAND_CX + _LAND_HALF_X,
            _LAND_CY + _LAND_HALF_Y,
            z1,
        ),
    ]


def _tools():
    y0 = frontY - _OVERRUN
    y1 = backY + _OVERRUN
    z0 = nozzleEndZ - _OVERRUN
    z1 = topZ + _OVERRUN
    x0 = -halfWidth - _OVERRUN
    x1 = -halfWidth + overallWidth + _OVERRUN
    pads = _mating_pads()
    lands = _land_pads()

    u_cut = _box(-_U_HALF, y0, z0, _U_HALF, y1, _U_TOP)
    rear_slot = _except_pads(
        _box(-_REAR_OPEN_HALF, _REAR_OPEN_Y, _U_TOP - 0.2, _REAR_OPEN_HALF, y1, z1),
        pads,
    )
    well = _except_pads(_box(x0, -_REAR_RECESS, z0, x1, y1, z1), pads)
    # Fork back edge sits at y=-3.5 below the mount ledge; U inner edges at |x|=16 there.
    lip_backs = [
        _box(cx - _LIP_HALF_X, _RECESS_Y - 0.05, z0, cx + _LIP_HALF_X, y1, _RECESS_TOP + 0.05)
        for cx in (-_LIP_CX, _LIP_CX)
    ]
    back_recess = _except_pads(_box(x0, _RECESS_Y, z0, x1, y1, _RECESS_TOP), pads + lip_backs)
    u_wide = _except_pads(_box(-_U_WIDE_HALF, y0, z0, _U_WIDE_HALF, y1, _U_WIDE_TOP), lands + pads)
    u_upper = _except_pads(_box(-_U_UPPER_HALF, y0, _U_UPPER_Z0, _U_UPPER_HALF, y1, _U_WIDE_TOP), lands + pads)
    chamfers = [_xy_prism([(side * x, y) for x, y in _OUTER_CHAMFER], z0, z1) for side in (-1.0, 1.0)]

    left_z_wall = _nozzle_z(-halfWidth, 1.0)
    left_x_floor = -_NOZZLE_PX - (_NOZZLE_NZ / _NOZZLE_NX) * (nozzleEndZ - _NOZZLE_PZ)
    right_z_wall = _nozzle_z(halfWidth, -1.0)
    right_x_floor = _NOZZLE_PX + (_NOZZLE_NZ / _NOZZLE_NX) * (nozzleEndZ - _NOZZLE_PZ)
    left_wedge = _xz_prism(
        [
            (x0, z0),
            (left_x_floor, z0),
            (x0, left_z_wall),
        ],
        y0,
        y1,
    )
    right_wedge = _xz_prism(
        [
            (x1, z0),
            (right_x_floor, z0),
            (x1, right_z_wall),
        ],
        y0,
        y1,
    )
    skim = _except_pads(_box(x0, y0, z0, x1, _SKIM_Y1, nozzleEndZ + _SKIM_Z), lands)

    left_taper = _leg_taper(-1.0, x0, z1, y0, y1)
    right_taper = _leg_taper(1.0, x1, z1, y0, y1)
    # Right-rear top stepped down to z=46 (y=-5 / z=55 drawings).
    right_step = _except_pads(_box(_STEP_X0, _STEP_Y0, _STEP_Z0, x1, y1, z1), pads)
    # Back-left top corner bevel in plan, (-21.5, 0) -> (-29.5, -14), above z=41.
    back_bevel = _xy_prism([(-21.5, y1), (-29.5, -14.0), (x0, -14.0), (x0, y1)], _BEVEL_Z0, z1)

    ly0 = inletCenterY - inletDepth / 2.0
    ly1 = inletCenterY + inletDepth / 2.0
    left_inlet = _box(
        leftInletCenterX - leftInletWidth / 2.0,
        ly0,
        topZ - _INLET_CUT,
        leftInletCenterX + leftInletWidth / 2.0,
        ly1,
        z1,
    )
    right_inlet = _box(
        rightInletCenterX - rightInletWidth / 2.0,
        ly0,
        topZ - _INLET_CUT,
        rightInletCenterX + rightInletWidth / 2.0,
        ly1,
        z1,
    )
    fan_raw = (
        Location((0.0, y0, fanCenterZ))
        * Rotation(-90, 0, 0)
        * Cylinder(
            fanOpeningDiameter / 2.0,
            _FAN_DEPTH,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
    # Grille: hub boss plus two diagonal vanes left standing in the opening; the
    # vanes tie the hub to the rim because hotendCavity opens the bore floor behind it.
    grille_depth = _FAN_DEPTH + 2.0 * _OVERRUN
    hub = (
        Location((0.0, y0, fanCenterZ))
        * Rotation(-90, 0, 0)
        * Cylinder(_HUB_RADIUS, grille_depth, align=(Align.CENTER, Align.CENTER, Align.MIN))
    )
    vanes = [
        Location((0.0, y0, fanCenterZ))
        * Rotation(0, angle, 0)
        * Box(
            2.0 * _VANE_HALF_LEN,
            grille_depth,
            _VANE_THICK,
            align=(Align.CENTER, Align.MIN, Align.CENTER),
        )
        for angle in (_VANE_ANGLE, -_VANE_ANGLE)
    ]
    grille = Compound([hub, *vanes])
    fan = (fan_raw & _box(-18.9, y0, 24.0, 18.9, y0 + _FAN_DEPTH + _OVERRUN, _FAN_CLIP_Z)) - grille
    # hotendCavity's chin fill and ramp planes live inside this air; keep it.
    connector = _box(-_U_HALF, y0, _U_TOP - 0.2, _U_HALF, frontY + _FAN_DEPTH, 32.0)

    return [
        u_cut,
        rear_slot,
        well,
        left_wedge,
        right_wedge,
        skim,
        back_recess,
        u_wide,
        u_upper,
        *chamfers,
        left_taper,
        right_taper,
        right_step,
        back_bevel,
        left_inlet,
        right_inlet,
        fan,
        connector,
    ]


def apply(body):
    return body - Compound(_tools())
