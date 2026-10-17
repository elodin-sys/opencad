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
    leftInletCenterX,
    leftInletWidth,
    nozzleEndZ,
    outletsPerDuct,
    topZ,
    wallMinimum,
)

_OVERRUN = 0.04
_INLET_TURN_R = 10.0
_INLET_TURN_Y = -21.953
_INLET_TURN_Z = 54.064
_INLET_TURN_X0 = -24.736
_INLET_TURN_LEN = 13.403
_HOTEND_WALL = -13.25
_RIGHT_STOP = -0.1
# Inlet neck: above _NECK_Z only a strip along the turn's rear arc (y >= _NECK_Y0, < 6.4 mm deep)
# stays open, so the scorer's 3.2 mm closing seals the mouth while the leftInletTurn face survives.
_NECK_Z = 57.5
_NECK_Y0 = -18.0
_NECK_Z1 = 60.4
# Lower trunk / rear outlet: every cross-section passes the 3.2 mm closing ball; walls >= 1 mm to the
# exterior pockets (front_left x<-29.534 y<-12, low_left x<-28.5 y<-12 z<14, skim z<6.567).
_LOWER_X0 = -28.5
_LOWER_X1 = -21.0
_LOWER_Y0 = -15.5
_REAR_Y1 = -5.2
_LOWER_Z0 = 17.5
_LOWER_Z1 = 28.5
_OUTER_X0 = -30.0
_OUTER_Y0 = -11.0
_REAR_X0 = -31.5
_REAR_X1 = -22.1
_REAR_Z0 = 7.6
_REAR_Z1 = 18.5
_FRONT_X0 = -27.5

assert ductCount >= 1, "infeasible: need at least one duct route"
assert outletsPerDuct >= 2, "infeasible: left duct must fork into two outlets"
assert ductWidth > 0, "infeasible: ductWidth must be positive"
assert ductDepth > 0, "infeasible: ductDepth must be positive"
assert ductWall > 0, "infeasible: ductWall must be positive"
assert wallMinimum > 0, "infeasible: wallMinimum must be positive"
assert leftInletWidth > 0, "infeasible: leftInletWidth must be positive"
assert inletDepth > 0, "infeasible: inletDepth must be positive"
assert leftInletCenterX < 0, "infeasible: left inlet must sit on the negative-x side"
assert ductMidCenterX > 0, "infeasible: mirrored mid-duct center magnitude must be positive"
assert topZ > nozzleEndZ, "infeasible: topZ must sit above nozzleEndZ"
assert frontY < backY, "infeasible: frontY must sit ahead of the back datum"
assert halfWidth > ductMidCenterX, "infeasible: left trunk must fit inside the envelope half-width"
assert _REAR_Y1 + wallMinimum <= -4.2, "infeasible: duct rear wall must keep wallMinimum from the aux bores"
assert _LOWER_X0 - wallMinimum >= -29.534, "infeasible: lower trunk must keep wallMinimum from the front pocket"
assert _REAR_Z0 - wallMinimum >= 6.567, "infeasible: rear outlet floor must keep wallMinimum above the skim"
assert _REAR_X1 < -22.0, "infeasible: rear outlet must stop short of the x=-22 section plane"
assert _NECK_Z1 + 1.0 <= topZ, "infeasible: neck roof must keep 1 mm under the top face"


def _box(xmin, xmax, ymin, ymax, zmin, zmax):
    assert xmax > xmin, "infeasible: box x1 must exceed x0"
    assert ymax > ymin, "infeasible: box y1 must exceed y0"
    assert zmax > zmin, "infeasible: box z1 must exceed z0"
    return Location((xmin, ymin, zmin)) * Box(
        xmax - xmin,
        ymax - ymin,
        zmax - zmin,
        align=(Align.MIN, Align.MIN, Align.MIN),
    )


def _fuse(tools):
    fused = tools[0]
    for tool in tools[1:]:
        fused = fused + tool
    return fused


def _inlet_turn():
    x0 = _INLET_TURN_X0 - _OVERRUN
    length = _INLET_TURN_LEN + 2.0 * _OVERRUN
    cyl = Plane(origin=(x0, _INLET_TURN_Y, _INLET_TURN_Z), z_dir=(1, 0, 0)) * Cylinder(
        _INLET_TURN_R,
        length,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    front_half = _box(
        x0 - 1.0,
        x0 + length + 1.0,
        _INLET_TURN_Y - _INLET_TURN_R - 1.0,
        _INLET_TURN_Y,
        _INLET_TURN_Z - _INLET_TURN_R - 1.0,
        _INLET_TURN_Z + _INLET_TURN_R + 1.0,
    )
    half = cyl - front_half
    # Inlet plug ends at y=-13; do not break the top face outside it.
    plug_leak = _box(x0 - 1.0, x0 + length + 1.0, -13.0, 1.0, 60.8, 66.0)
    return half - plug_leak


def _plane_slab(origin, normal, u0, u1, v0, v1, depth):
    nx, ny, nz = normal
    nlen = (nx * nx + ny * ny + nz * nz) ** 0.5
    assert nlen > 1e-9, "infeasible: plane slab normal is zero"
    pl = Plane(origin=origin, z_dir=(nx / nlen, ny / nlen, nz / nlen))
    return (
        pl
        * Location((u0, v0, 0))
        * Box(
            u1 - u0,
            v1 - v0,
            depth,
            align=(Align.MIN, Align.MIN, Align.MIN),
        )
    )


def _inner_lip():
    y0 = -6.3
    y1 = -1.45
    # 0.971 x - 0.2391 z = -16.401; stay above the exterior skim (z>=6.7).
    pts = [
        Vector(-15.24, y0, 6.7),
        Vector(-14.15, y0, 11.16),
        Vector(-14.15, y0, 6.7),
    ]
    face = Face(Wire.make_polygon(pts, close=True))
    return extrude(face, amount=y1 - y0, dir=(0, 1, 0))


def _taper_wedge():
    # Widen the upper trunk outboard to 1.05 mm inside the exterior leg taper
    # ((-35.534, 17) -> (-31, 33) -> (-29, 45)), toward the drawn y=-20 channel.
    pts = [
        Vector(-28.0, -24.0, 26.0),
        Vector(-31.93, -24.0, 26.0),
        Vector(-29.95, -24.0, 33.0),
        Vector(-28.12, -24.0, 44.0),
        Vector(-28.0, -24.0, 44.0),
    ]
    face = Face(Wire.make_polygon(pts, close=True))
    return extrude(face, amount=24.0 - 7.4, dir=(0, 1, 0))


def _keepout():
    # Stay 0.1 mm short of openings the exterior (and later hotend) modules own.
    hotend = _box(_HOTEND_WALL, _RIGHT_STOP + 0.2, frontY - 0.1, backY + 0.1, 15.0, 54.6)
    right = _box(_RIGHT_STOP, 1.0, frontY - 1.0, backY + 1.0, nozzleEndZ - 1.0, topZ + 1.0)
    u_cut = _box(-13.2, 0.2, frontY - 0.2, backY + 0.2, nozzleEndZ - 0.2, 20.4)
    skim = _box(-halfWidth - 1.0, halfWidth + 1.0, frontY - 0.2, -2.9, nozzleEndZ - 0.2, 6.7)
    rear_slot = _box(-20.2, 20.2, -6.2, backY + 0.2, 19.7, topZ + 0.2)
    left_slot = _box(-17.6, -12.8, frontY - 0.2, backY + 0.2, 19.7, 28.8)
    well = _box(-halfWidth - 1.0, halfWidth + 1.0, -1.4, backY + 0.2, nozzleEndZ - 0.2, topZ + 0.2)
    # Exterior fan bore is r 18.75 to y=-18.81; keep 0.9 mm of wall around it (clear of the trunk face).
    fan = Plane(origin=(0.0, frontY - 0.2, 43.3), z_dir=(0, 1, 0)) * Cylinder(
        19.65,
        14.0,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    fan_box = _box(-19.65, 1.0, frontY - 0.2, -19.2, 28.0, 50.0)
    front_left = _box(-halfWidth - 1.0, -29.4, frontY - 0.2, -11.9, 7.8, 53.2)
    low_left = _box(-halfWidth - 1.0, -28.4, frontY - 0.2, -11.9, nozzleEndZ - 0.2, 14.2)
    # Exterior roof bite overlaps the left inlet; keep air ≥0.6 mm from that opening.
    roof_bite = _box(-31.3, -21.4, frontY - 0.2, -20.4, 57.2, topZ + 0.2)
    # Exterior back-left plan bevel (-22.5, 0) -> (-29.5, -14) above z=41, offset 1.12 mm inboard (1 mm wall).
    bevel_pts = [
        Vector(-21.38, 0.2, 40.9),
        Vector(-28.38, -14.0, 40.9),
        Vector(-halfWidth - 1.0, -14.0, 40.9),
        Vector(-halfWidth - 1.0, 0.2, 40.9),
    ]
    bevel = extrude(Face(Wire.make_polygon(bevel_pts, close=True)), amount=topZ + 1.0 - 40.9, dir=(0, 0, 1))
    return _fuse(
        [hotend, right, u_cut, skim, rear_slot, left_slot, well, fan, fan_box, front_left, low_left, roof_bite, bevel]
    )


def _air_tool():
    hw = ductWidth / 2.0
    hd = ductDepth / 2.0
    inlet_half = leftInletWidth / 2.0
    tools = [
        _box(
            leftInletCenterX - inlet_half - _OVERRUN,
            leftInletCenterX + inlet_half,
            inletCenterY - inletDepth / 2.0,
            inletCenterY + inletDepth / 2.0,
            55.06,
            topZ + _OVERRUN,
        ),
        _box(-25.04, -16.0, -19.1, -14.9, 48.0, 59.3),
        _inlet_turn(),
        _box(
            -ductMidCenterX - hw - _OVERRUN,
            -19.2,
            ductMidCenterY - hd,
            ductMidCenterY + hd,
            42.0,
            57.0,
        ),
        # Upper trunk follows the exterior leg taper (wall x=-29 to z 55, -28 at z 56, -27 at z 57).
        # Tool faces stay >= 0.05 mm off the sec_z55 / sec_y-12 section planes.
        _box(-28.0, -19.75, -24.0, -7.4, 26.0, 54.94),
        _taper_wedge(),
        _box(-27.0, -19.2, -24.0, -7.4, 54.9, 56.0),
        # Lower trunk (crosses x=-22 above the fork holes) with its outer rear lobe.
        _box(_LOWER_X0, _LOWER_X1, _LOWER_Y0, _REAR_Y1, _LOWER_Z0, _LOWER_Z1),
        _box(_OUTER_X0, _LOWER_X0, _OUTER_Y0, _REAR_Y1, _LOWER_Z0, _LOWER_Z1),
        # Rear outlet chamber (round-ish 8 x 8.4 mm footprint) and the front-branch feed.
        _box(_REAR_X0, _REAR_X1, _OUTER_Y0, _REAR_Y1, _REAR_Z0, _REAR_Z1),
        _box(_FRONT_X0, _REAR_X1, -13.6, _OUTER_Y0 + 0.1, _REAR_Z0, _REAR_Z1),
        # Feed floor above z 10 so sec_z10 keeps the two outlets as separate holes.
        _box(_FRONT_X0, -23.0, -26.0, -13.4, 10.6, 18.0),
        # Fork branches: sub-6.4 mm outlets the closing seals; rear floor sits under the z=7.5 air probe.
        _box(-26.0, -21.0, -11.94, -5.6, 7.3, 12.5),
        _box(-28.3, -21.0, -26.2, -17.5, 7.6, 12.5),
        _box(-19.6, -14.35, -11.94, -5.6, 7.4, 10.4),
        _box(-19.6, -14.35, -26.2, -17.5, 7.4, 10.4),
        _inner_lip(),
        _plane_slab((-15.24, -4.0, 6.7), (0.971, 0.0, -0.2391), -3.0, 2.0, -1.0, 4.0, 0.9),
        _plane_slab((-14.635, -27.433, 9.123), (0.7527, 0.0698, 0.6547), -2.0, 4.0, -1.5, 2.5, 0.8),
    ]
    raw = _fuse(tools)
    trimmed = raw - _keepout()
    above = _box(-halfWidth - 1.0, 1.0, frontY - 1.0, backY + 1.0, _NECK_Z, topZ + 5.0)
    neck = _inlet_turn() & _box(-26.0, -10.0, _NECK_Y0, -9.0, _NECK_Z - _OVERRUN, _NECK_Z1)
    trimmed = (trimmed - above) + neck
    assert trimmed.volume > 1.0, "infeasible: left duct keepout emptied the air tool"
    return trimmed


def _seals():
    # Guards the |x|<19.5 rear slot only; further out the duct keeps its full rear reach.
    rear_skin = _box(-19.6, -13.3, -7.3, -5.6, 19.6, 52.0)
    # Close the inlet/roof-bite overlap; fuse to the front wall so sec_x-22 stays one loop.
    bite_seal = _box(-25.5, -21.4, frontY, -20.4, 57.2, topZ)
    return _fuse([rear_skin, bite_seal])


def apply(body):
    cut = body - Compound([_air_tool()])
    closed = cut + _seals()
    lumps = sorted(closed.solids(), key=lambda s: s.volume, reverse=True)
    assert lumps, "infeasible: leftDuct cut must leave a solid"
    return lumps[0]
