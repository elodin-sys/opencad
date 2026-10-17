from build123d import (
    Align,
    Box,
    Compound,
    Cylinder,
    Location,
    Plane,
    Polygon,
    Pos,
    extrude,
    loft,
)
from params import (
    backY,
    ductWall,
    fanCenterZ,
    fanOpeningDiameter,
    frontY,
    hotendCavityBottomZ,
    hotendCavityHeight,
    hotendCavityTopZ,
    hotendCavityWidth,
    nozzleEndZ,
    rearCableNotchDiameter,
    topHoleBx,
    topPilotDiameter,
    topZ,
    wallMinimum,
)

_OVERRUN = 0.04
_WALL = hotendCavityWidth / 2 + 0.15
_INNER = hotendCavityWidth / 2 - 1.0
_ROOF_Z = 54.0
_BRIDGE_BOT = 27.8
_BRIDGE_TOP = 29.0
_LOWER_R = 11.25
_UPPER_R = 10.2
_DIAG_R = 8.0
_DIAG_U = 0.7071
_DIAG_ORIGIN_Y = -14.542
_DIAG_ORIGIN_Z = 14.544
_DIAG_START = 0.989
_LEFT_DIAG_LEN = 17.759
_RIGHT_DIAG_LEN = 15.981
_LEFT_DIAG_PRE = 1.24
_U_TOP = 20.15
_REAR_OPEN_Y = -5.55
_LIP = 1.0
# Pilot bore B and the rear cable notch both floor onto the roof lips at z=54: the
# back lip clears the notch, the front lip (which must stay continuous to keep the
# rightDuct's z=54 barrier a separate face) thickens under the bore. Fixed sizes
# keep the topPilotDiameter edit test clean.
_NOTCH_CLEAR_R = 2.3
_PILOT_PAD_HALF = 1.7
_PILOT_PAD_DEPTH = 0.9
# Fan-to-pocket transition behind the exterior's bore floor (y=-18.85): the drawn
# arch at y=-20 (flat bottom ±6 at z=29, ±14.9 walls z 38..46, top arc) shrunk to
# the y=-18 widths (z30: ±8.6, z45: ±14.2) lofted to the pocket box at y=-11.5.
_TRANS_FRONT_Y = -18.95
_TRANS_BACK_Y = -11.5
_TRANS_FRONT = [
    (6.2, 29.0),
    (8.6, 30.0),
    (10.1, 31.0),
    (11.2, 32.0),
    (12.1, 33.0),
    (12.8, 34.0),
    (13.8, 36.0),
    (14.4, 38.0),
    (14.5, 40.0),
    (14.5, 46.0),
    (14.1, 48.0),
    (13.5, 50.0),
    (12.3, 52.0),
    (11.3, 53.88),
]
_TRANS_BACK = [
    (8.0, 29.0),
    (9.6, 30.0),
    (10.8, 31.0),
    (11.3, 32.0),
    (11.6, 33.0),
    (11.9, 34.0),
    (11.9, 36.0),
    (11.9, 38.0),
    (11.9, 40.0),
    (11.9, 46.0),
    (11.9, 48.0),
    (11.9, 50.0),
    (11.0, 52.0),
    (9.0, 53.95),
]

assert hotendCavityWidth > 0, "infeasible: hotendCavityWidth must be positive"
assert hotendCavityHeight > 0, "infeasible: hotendCavityHeight must be positive"
assert hotendCavityBottomZ > nozzleEndZ, "infeasible: cavity bottom must sit above the nozzle end"
assert hotendCavityTopZ > hotendCavityBottomZ, "infeasible: cavity top must sit above its bottom"
assert fanOpeningDiameter > 0, "infeasible: fanOpeningDiameter must be positive"
assert fanCenterZ > nozzleEndZ, "infeasible: fan center must sit above the nozzle end"
assert fanCenterZ < topZ, "infeasible: fan center must sit below the housing top"
assert backY > frontY, "infeasible: back datum must sit behind the front face"
assert ductWall > 0, "infeasible: ductWall must be positive"
assert _WALL > _INNER, "infeasible: pocket walls must sit outside the inner cavity"
assert _BRIDGE_BOT > hotendCavityBottomZ, "infeasible: bridge must sit above the cavity bottom"
assert _BRIDGE_TOP > _BRIDGE_BOT, "infeasible: bridge must have positive thickness"
assert _ROOF_Z > hotendCavityTopZ, "infeasible: rear roof must sit above the front cavity top"
assert _LEFT_DIAG_PRE > 0, "infeasible: left diagonal must start before the documented origin"
assert _TRANS_FRONT_Y > frontY, "infeasible: fan transition must start forward of the front face"
assert _TRANS_BACK_Y > _TRANS_FRONT_Y, "infeasible: fan transition must run backward into the pocket"
assert max(x for x, _ in _TRANS_FRONT) < fanOpeningDiameter / 2, (
    "infeasible: fan transition must stay inside the fan mouth"
)
assert _TRANS_FRONT[0][1] > fanCenterZ - fanOpeningDiameter / 2, (
    "infeasible: fan transition floor must sit above the fan mouth bottom"
)
assert _TRANS_FRONT[-1][1] < fanCenterZ + fanOpeningDiameter / 2, (
    "infeasible: fan transition top must sit below the fan mouth top"
)
assert _TRANS_FRONT[-1][1] <= _ROOF_Z, "infeasible: fan transition must stay below the rear roof"
assert _TRANS_BACK[-1][1] < _ROOF_Z, "infeasible: fan transition must stay below the pocket ceiling"
assert _LIP >= wallMinimum, "infeasible: roof lips must be at least the minimum wall"
assert _PILOT_PAD_DEPTH >= wallMinimum, "infeasible: lip under the pilot bore must be a full wall"
assert _PILOT_PAD_HALF > topPilotDiameter / 2, "infeasible: lip pad must cover the pilot bore"
assert _NOTCH_CLEAR_R > rearCableNotchDiameter / 2, "infeasible: roof lip must clear the cable notch"


def _box(x0, x1, y0, y1, z0, z1):
    assert x1 > x0, "infeasible: box x1 must exceed x0"
    assert y1 > y0, "infeasible: box y1 must exceed y0"
    assert z1 > z0, "infeasible: box z1 must exceed z0"
    return Location((x0, y0, z0)) * Box(
        x1 - x0,
        y1 - y0,
        z1 - z0,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def _cyl(radius, origin, direction, t0, t1):
    assert t1 > t0, "infeasible: cylinder length must be positive"
    p0 = (
        origin[0] + t0 * direction[0],
        origin[1] + t0 * direction[1],
        origin[2] + t0 * direction[2],
    )
    return Plane(origin=p0, z_dir=direction) * Cylinder(
        radius,
        t1 - t0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )


def _yz_prism(points_yz, x0, x1):
    face = Plane.YZ * Polygon(*points_yz, align=None)
    return Pos(x0, 0, 0) * extrude(face, amount=x1 - x0)


def _xz_face(half_profile, y):
    right = list(half_profile)
    left = [(-x, z) for x, z in reversed(right)]
    plane = Plane(origin=(0, y, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
    return plane * Polygon(*right, *left, align=None)


def _transition():
    front = _xz_face(_TRANS_FRONT, _TRANS_FRONT_Y)
    back = _xz_face(_TRANS_BACK, _TRANS_BACK_Y)
    return loft([front, back], ruled=True)


def _below_plane(ny, nz, py, pz, y0, y1, x0, x1, zmin):
    def z_at(y):
        return pz - (ny / nz) * (y - py)

    z0 = z_at(y0)
    z1 = z_at(y1)
    assert z0 > zmin, "infeasible: ramp plane must sit above the cut floor"
    assert z1 > zmin, "infeasible: ramp plane must sit above the cut floor"
    return _yz_prism([(y0, zmin), (y1, zmin), (y1, z1), (y0, z0)], x0, x1)


def _structure_fills():
    inner = _INNER
    upper_stock = _box(-_UPPER_R - 0.2, _UPPER_R + 0.2, -_UPPER_R - 0.2, backY, 50.616, _ROOF_Z)
    front = _box(-inner, inner, frontY, -12.20, 19.50, _BRIDGE_TOP)
    return [upper_stock, front]


def _named_pads():
    wall = _WALL
    # Stop 0.1 mm short of fasteners left rail at x=-14.465.
    left_wall = _box(-14.36, -wall - 0.07, -7.44, backY, 17.63, 25.67)
    right_wall = _box(wall + 0.07, 18.70, -8.66, -2.66, 17.75, 22.72)
    roof = _box(-13.03, 13.27, -6.91, -1.55, _ROOF_Z, _ROOF_Z + 0.40)
    bridge = _box(-13.15, 9.20, -10.10, -6.30, _BRIDGE_BOT, _BRIDGE_TOP)
    return [left_wall, right_wall, roof, bridge]


def _roof_frame():
    # Solid lips around the 141 mm2 pad so later z=54 adds stay separate faces;
    # they rise to the pad top so the fastener roof blocks fuse onto them.
    x0, x1 = -13.03 - _LIP, 13.27 + _LIP
    z0, z1 = 53.70, _ROOF_Z + 0.40
    notch = _cyl(_NOTCH_CLEAR_R, (0.0, backY, z0), (0.0, 0.0, 1.0), -_OVERRUN, z1 - z0 + _OVERRUN)
    front = _box(x0, x1, -6.91 - _LIP, -6.91, z0, z1)
    under_pilot = _box(
        topHoleBx - _PILOT_PAD_HALF,
        topHoleBx + _PILOT_PAD_HALF,
        -6.91 - _LIP,
        -6.91,
        _ROOF_Z - _PILOT_PAD_DEPTH,
        z1,
    )
    back = _box(x0, x1, -1.55, -1.55 + _LIP, z0, z1) - notch
    left = _box(x0, -13.03, -6.91, -1.55, z0, z1)
    right = _box(13.27, x1, -6.91, -1.55, z0, z1)
    return [front, under_pilot, back, left, right]


def _main_cutters():
    wall = _WALL
    inner = _INNER
    y_front = frontY - _OVERRUN
    y_back = backY + _OVERRUN

    clear_walls = _box(-wall + 0.01, wall - 0.01, -8.70, y_back, 17.60, 25.70)
    # Inset under the roof pad so the pad seals a 141 mm2 island.
    roof_erase = _box(-12.88, 13.12, -6.76, -1.70, 53.96, 54.05)
    mid_upper = _box(-inner, inner, -16.0, _REAR_OPEN_Y, _BRIDGE_TOP, _ROOF_Z)
    mid_lower = _box(-inner, inner, -12.20, _REAR_OPEN_Y, _U_TOP, _BRIDGE_BOT)
    transition = _transition()

    upper_relief = _cyl(
        _UPPER_R,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        50.616 - _OVERRUN,
        _ROOF_Z,
    ) & _box(-_UPPER_R - 1.0, _UPPER_R + 1.0, -_UPPER_R - 1.0, y_back, 50.50, _ROOF_Z)

    mid = _box(-15.8, 15.8, -18.8, -1.20, 15.45, 29.40)
    left_mid = _box(-15.8, 15.8, -18.8, -1.20, 14.20, 29.40)
    left_diag = (
        _cyl(
            _DIAG_R,
            (-5.15, _DIAG_ORIGIN_Y, _DIAG_ORIGIN_Z),
            (0.0, _DIAG_U, _DIAG_U),
            _DIAG_START - _LEFT_DIAG_PRE,
            _LEFT_DIAG_LEN + _OVERRUN,
        )
        & left_mid
    )
    right_diag = (
        _cyl(
            _DIAG_R,
            (5.15, _DIAG_ORIGIN_Y, _DIAG_ORIGIN_Z),
            (0.0, _DIAG_U, _DIAG_U),
            _DIAG_START - _OVERRUN,
            _RIGHT_DIAG_LEN + _OVERRUN,
        )
        & mid
    )

    ramps = [
        _below_plane(0.342, -0.9397, -20.256, 20.625, y_front, -12.20, -inner, inner, 1.0),
        _below_plane(0.7071, -0.7071, -19.557, 20.843, y_front, -12.20, -inner, inner, 1.0),
        _below_plane(-0.1762, -0.9844, -15.748, 17.818, y_front, -12.20, -inner, inner, 1.0),
    ]
    return [
        clear_walls,
        roof_erase,
        mid_upper,
        mid_lower,
        transition,
        upper_relief,
        left_diag,
        right_diag,
        *ramps,
    ]


def _bridge_cutters():
    wall = _WALL
    y_back = backY + _OVERRUN
    lower_relief = _cyl(
        _LOWER_R,
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        _BRIDGE_BOT - 0.02,
        29.362 + _OVERRUN,
    ) & _box(-_LOWER_R - 1.0, _LOWER_R + 1.0, -6.50, y_back, _BRIDGE_BOT - 0.2, 29.50)
    top_skim = _box(-wall - 0.2, wall + 0.2, -12.30, -5.00, 28.95, _BRIDGE_TOP + _OVERRUN)
    keep_right = _box(0.20, 6.20, -12.20, -8.10, 28.90, _BRIDGE_TOP + 0.10)
    keep_left = _box(-10.70, -5.40, -9.70, -7.30, 28.90, _BRIDGE_TOP + 0.10)
    return [lower_relief, top_skim - Compound([keep_right, keep_left])]


def apply(body):
    filled = body + Compound(_structure_fills())
    cut = filled - Compound(_main_cutters())
    padded = cut + Compound(_named_pads() + _roof_frame())
    done = padded - Compound(_bridge_cutters())
    lumps = sorted(done.solids(), key=lambda s: s.volume, reverse=True)
    assert lumps, "infeasible: hotendCavity cut must leave a solid"
    return lumps[0]
