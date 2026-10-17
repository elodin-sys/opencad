import FreeCAD
import Part
import PartDesign  # noqa: F401
from params import (
    backY,
    ductCount,
    ductDepth,
    ductMidCenterX,
    ductMidCenterY,
    ductWall,
    ductWidth,
    fanCenterZ,
    fanOpeningDiameter,
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
_TRUNK_X0 = 19.6
_TRUNK_Y1 = -7.0
_FORK_Y1 = -6.8
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
_TURN = (21.0, -9.5, 7.4, 24.4, _FORK_Y1, 9.5)
_TRUNK_TOP = 57.8
_TRUNK_UP_X0 = 19.4
_TRUNK_SKIN = (19.4, -25.85, 43.2, 19.55, -20.15, 45.05)
_TRUNK_UP_Z = 43.0
_TAPER_STEPS = ((56.0, 26.5), (56.5, 26.0), (57.0, 25.4), (57.6, 25.2))
_TAPER_LINE = ((29.0, 55.3), (26.0, 58.0))
_WEB_TOP = _TRUNK_TOP + 0.4
_INLET_Z0 = 54.95
_NECK_Z1 = 58.7
_TRUNK_MID_Z = 43.0
_TRUNK_MID_Y0 = -22.0
_TRUNK_LOW_Z = 33.0
_TRUNK_LOW_Y0 = -18.5
_FRONT_FLOOR_Z = 7.7
_U_WALL_X = 17.5
_FP_X0 = 22.5
_FP_Y0 = -21.5
_FP_Y1 = -18.4
_FP_Z0 = 16.0
_FP_Z1 = 33.1
_PATCH_Y1 = -4.7
_SEAT_Y = -3.8
_BELLY_X0 = 17.422
_BELLY_X1 = 28.126
_BELLY_Y = -33.8
_BELLY_Z = 36.775
_BELLY_R = 30.0
_BELLY_STOCK_X0 = 24.2
_BELLY_STOCK_Z1 = 41.5
_X22_WEB = (19.5, -27.15, 19.7, 22.35, -6.5, 21.5)
_CHIN_JOIN = (21.6, -14.2, 3.55, 22.4, -6.4, 5.25)
_INLET_TURN_X0 = 10.564
_INLET_TURN_X1 = 19.621
_INLET_TURN_Y = -8.519
_INLET_TURN_Z = 59.745
_INLET_TURN_R = 5.0
_LIP_ORIGIN = (15.756, 0.0, 4.61)
_LIP_N = (-0.971, 0.0, -0.2391)
_RETURN_ORIGIN = (14.635, -27.433, 9.123)
_RETURN_N = (-0.7527, 0.0698, 0.6547)
_KEEPOUT_MARGIN = 0.85

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
assert fanOpeningDiameter > 0, "infeasible: fanOpeningDiameter must be positive"
assert _TRUNK_Y1 + wallMinimum <= -5.55, "infeasible: trunk y must keep wallMinimum from the rear slot"
assert _FORK_Y1 + wallMinimum <= -5.55, "infeasible: fork y must keep wallMinimum from the rear slot"
assert _PATCH_Y1 <= _SEAT_Y - 0.85, "infeasible: patches must stay 0.85 mm short of the rightRearSeat plane"
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
assert _TRUNK_MID_Z > 0, "infeasible: trunk mid station must be positive"
assert _X22_WEB[0] < 22.0 < _X22_WEB[3], "infeasible: x=22 web must cross the section plane"
assert _X22_WEB[3] <= 22.4, "infeasible: x=22 web must leave a 6.4 mm bypass outboard of x=22.4"
assert _CHIN_JOIN[0] < 22.0 < _CHIN_JOIN[3], "infeasible: chin joiner must cross x=22"
assert _BELLY_STOCK_X0 < _BELLY_X1, "infeasible: belly stock must extend along the pin axis"
assert _TRUNK_UP_X0 >= _HOTEND_STOP + 0.5, "infeasible: upper trunk must keep wall from the hotend keep-out"
assert _TRUNK_SKIN[0] >= _TRUNK_UP_X0 - 1e-6, "infeasible: trunk skin must start at the upper-trunk inboard face"
assert _TRUNK_X0 >= _HOTEND_STOP + 0.5, "infeasible: mid trunk must keep wall from the hotend keep-out"
assert _NECK_Z1 + 0.8 <= topZ, "infeasible: neck roof must keep 0.8 mm under the top face"


def _box(x0, y0, z0, x1, y1, z1):
    assert x1 > x0, "infeasible: box x1 must exceed x0"
    assert y1 > y0, "infeasible: box y1 must exceed y0"
    assert z1 > z0, "infeasible: box z1 must exceed z0"
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, FreeCAD.Vector(x0, y0, z0))


def _cyl_x(x0, x1, yc, zc, radius):
    assert x1 > x0, "infeasible: cylinder length must be positive"
    assert radius > 0, "infeasible: cylinder radius must be positive"
    return Part.makeCylinder(radius, x1 - x0, FreeCAD.Vector(x0, yc, zc), FreeCAD.Vector(1, 0, 0))


def _cyl_z(xc, yc, z0, z1, radius):
    assert z1 > z0, "infeasible: cylinder height must be positive"
    assert radius > 0, "infeasible: cylinder radius must be positive"
    return Part.makeCylinder(radius, z1 - z0, FreeCAD.Vector(xc, yc, z0), FreeCAD.Vector(0, 0, 1))


def _cyl_y(xc, y0, zc, radius, length):
    assert length > 0, "infeasible: cylinder length must be positive"
    assert radius > 0, "infeasible: cylinder radius must be positive"
    return Part.makeCylinder(radius, length, FreeCAD.Vector(xc, y0, zc), FreeCAD.Vector(0, 1, 0))


def _norm(vec):
    x, y, z = vec
    mag = (x * x + y * y + z * z) ** 0.5
    assert mag > 1e-9, "infeasible: zero-length axis"
    return (x / mag, y / mag, z / mag)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _plane_slab(origin, normal, x_hint, u0, u1, v0, v1, length):
    n = _norm(normal)
    x_axis = _norm(x_hint)
    y_axis = _norm(_cross(n, x_axis))
    x_axis = _norm(_cross(y_axis, n))
    ox, oy, oz = origin

    def corner(u, v):
        return FreeCAD.Vector(
            ox + u * x_axis[0] + v * y_axis[0],
            oy + u * x_axis[1] + v * y_axis[1],
            oz + u * x_axis[2] + v * y_axis[2],
        )

    pts = [corner(u0, v0), corner(u1, v0), corner(u1, v1), corner(u0, v1), corner(u0, v0)]
    try:
        face = Part.Face(Part.makePolygon(pts))
    except Exception:  # noqa: BLE001 — reversed winding if Face rejects the wire
        face = Part.Face(Part.makePolygon(list(reversed(pts))))
    return face.extrude(FreeCAD.Vector(n[0] * length, n[1] * length, n[2] * length))


def _xz_prism(points, y0, y1):
    assert y1 > y0, "infeasible: prism depth must be positive"
    pts = [FreeCAD.Vector(x, y0, z) for x, z in points]
    pts.append(pts[0])
    try:
        face = Part.Face(Part.makePolygon(pts))
    except Exception:  # noqa: BLE001 — reversed winding if Face rejects the wire
        face = Part.Face(Part.makePolygon(list(reversed(pts))))
    return face.extrude(FreeCAD.Vector(0, y1 - y0, 0))


def _fuse(solids):
    out = solids[0]
    for extra in solids[1:]:
        out = out.fuse(extra)
    return out


def _outside_cyl_x(x0, x1, y0, y1, z0, z1, yc, zc, radius):
    return _box(x0, y0, z0, x1, y1, z1).cut(_cyl_x(x0 - _OVERRUN, x1 + _OVERRUN, yc, zc, radius))


def _fastener_keepout():
    # 0.85 mm from fastener-owned void probes; do not refill those bores/seats.
    return _fuse(
        [
            _cyl_y(12.7, -6.2, 55.424, 2.3 + _KEEPOUT_MARGIN, 8.0),
            _cyl_y(16.25, -8.2, 19.301, 1.7 + _KEEPOUT_MARGIN, 10.0),
            _cyl_z(3.939, -6.963, 56.0, 62.0, 2.5 + _KEEPOUT_MARGIN),
            _box(
                16.25 - 2.0 - _KEEPOUT_MARGIN,
                -26.0 - _KEEPOUT_MARGIN,
                19.301 - 2.0 - _KEEPOUT_MARGIN,
                16.25 + 2.0 + _KEEPOUT_MARGIN,
                -7.4,
                19.301 + 2.0 + _KEEPOUT_MARGIN,
            ),
            _box(13.15, _SEAT_Y - 0.1, 13.5, 30.2, 0.2, 39.0),
        ]
    )


def _keepout():
    fan = Part.makeCylinder(
        fanOpeningDiameter / 2.0 + 0.55,
        8.8,
        FreeCAD.Vector(0.0, frontY - 0.1, fanCenterZ),
        FreeCAD.Vector(0, 1, 0),
    )
    return _fuse(
        [
            _box(-1.0, frontY - 1.0, nozzleEndZ - 1.0, 0.1, backY + 1.0, topZ + 1.0),
            _box(0.0, frontY - 1.0, 15.0, _HOTEND_STOP, backY + 1.0, 54.6),
            _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, 13.1, backY + 0.2, 20.3),
            _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, _U_WALL_X - 0.1, backY + 0.2, 16.0),
            _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, halfWidth + 1.0, -2.9, 6.65),
            _box(0.0, -6.4, 19.9, 19.7, backY + 0.2, topZ + 0.2),
            _box(12.9, frontY - 0.2, 19.9, 17.5, backY + 0.2, 28.6),
            _box(0.0, -1.3, nozzleEndZ - 0.2, halfWidth + 1.0, backY + 0.2, topZ + 0.2),
            fan,
            _box(31.0, frontY - 0.2, nozzleEndZ - 0.2, halfWidth + 1.0, backY + 0.2, 25.0),
            _box(30.0, frontY - 0.2, 25.0, halfWidth + 1.0, backY + 0.2, 33.0),
            _box(28.0, frontY - 0.2, 33.0, halfWidth + 1.0, backY + 0.2, topZ + 0.2),
        ]
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
    trimmed = raw.cut(_keepout()).fuse(_box(*_SLOT))
    assert trimmed.Volume > 1.0, "infeasible: right duct keepout emptied the air tool"
    return trimmed


def _finish_tool():
    sealed = _fuse(
        [
            _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, 13.15, backY + 0.2, 20.3),
            _box(0.0, frontY - 0.2, nozzleEndZ - 0.2, halfWidth + 1.0, -2.9, 6.7),
            _box(-1.0, frontY - 1.0, nozzleEndZ - 1.0, 14.05, backY + 1.0, topZ + 1.0),
            _box(19.45, frontY - 1.0, nozzleEndZ - 1.0, halfWidth + 1.0, backY + 1.0, topZ + 1.0),
            _box(-1.0, frontY - 1.0, 10.45, halfWidth + 1.0, backY + 1.0, topZ + 1.0),
        ]
    )
    lip = _plane_slab(_LIP_ORIGIN, _LIP_N, (0.0, -1.0, 0.0), 2.0, 8.0, -1.5, 4.0, 1.1).cut(sealed)
    ret = _plane_slab(
        _RETURN_ORIGIN,
        _RETURN_N,
        (-0.0923, -0.9957, 0.0),
        -0.2,
        5.0,
        -1.5,
        3.5,
        0.9,
    ).cut(sealed)
    # Open through the rear well so this is a notch, not a third enclosed hole at z=45.
    belly_a = _outside_cyl_x(_BELLY_X0, 21.55, -5.55, _OVERRUN, 31.82, 46.0, _BELLY_Y, _BELLY_Z, _BELLY_R)
    belly_b = _outside_cyl_x(22.45, _BELLY_X1, -5.55, _OVERRUN, 31.82, 46.0, _BELLY_Y, _BELLY_Z, _BELLY_R)
    inlet_turn = _outside_cyl_x(
        _INLET_TURN_X0,
        _INLET_TURN_X1,
        -13.0,
        -6.8,
        56.5,
        60.7,
        _INLET_TURN_Y,
        _INLET_TURN_Z,
        _INLET_TURN_R,
    )
    return _fuse([lip, ret, belly_a, belly_b, inlet_turn])


def _patches():
    (xa, za), (xb, zb) = _TAPER_LINE
    # Skip z=40..52 so the z=45 section does not pick up the thick rear web.
    raw = _fuse(
        [
            _box(18.1, -8.1, _FORK_Z0, 20.6, _PATCH_Y1, 40.0),
            _box(18.1, -8.1, 52.0, 20.6, _PATCH_Y1, _WEB_TOP),
            _box(10.5, -10.0, 56.5, 19.7, _PATCH_Y1, topZ),
            _box(20.6, -8.1, _FORK_Z0, 28.0, _PATCH_Y1, 40.0),
            _box(20.6, -8.1, 52.0, 28.0, _PATCH_Y1, za),
            _xz_prism(
                [(20.6, za), (xa - 0.1, za), (xb - 0.1, zb), (xb - 0.1, _WEB_TOP), (20.6, _WEB_TOP)],
                -8.1,
                _PATCH_Y1,
            ),
            _box(4.0, frontY, 53.5, 20.0, -14.2, topZ),
            _box(5.0, -13.05, 60.75, 20.0, _PATCH_Y1, topZ),
            _box(5.2, -14.6, 54.0, 19.65, _PATCH_Y1, topZ),
        ]
    )
    trimmed = raw.cut(_fastener_keepout())
    # Rear well has no stock past x=24.2 at the r=30 pin; add it after the seat keep-out.
    belly_stock = _box(_BELLY_STOCK_X0, -5.55, 32.0, _BELLY_X1, _OVERRUN, _BELLY_STOCK_Z1)
    filled = trimmed.fuse(belly_stock)
    assert filled.Volume > 1.0, "infeasible: fastener keepout emptied the right-duct patches"
    return filled


def _seals():
    raw = _fuse(
        [
            _box(_U_WALL_X, -26.4, 6.6, 26.2, -17.3, _FRONT_FLOOR_Z),
            _box(18.9, -8.0, 21.2, 20.6, -6.6, 54.0),
            # Floor at z=20.2..21.5 on x=22; bypass stays open for x>22.35 (CadQuery web).
            _box(*_X22_WEB),
            _box(*_CHIN_JOIN),
            # 0.15 mm inboard skin at z=43.2..45 only; do not pinch the z=55 probe.
            _box(*_TRUNK_SKIN),
            # 0.8 mm lid on the right ear; do not cover the inlet mouth (x<18.5).
            _box(21.8, -23.3, topZ - 0.8, 32.3, -5.0, topZ),
        ]
    )
    return raw.cut(_fastener_keepout())


def _lip_pad():
    island = _box(16.17, -0.65, 2.425, 20.27, 0.0, 5.515)
    stem = _box(16.17, -1.5, 5.0, 20.27, -0.45, 7.5)
    return _fuse([island, stem])


def _boolean(body, solid, name, kind, min_delta=1.0, refine=False):
    doc = body.Document
    before = body.Shape.Volume
    host = doc.addObject("Part::Feature", name + "Cutter")
    host.Shape = solid
    tool_body = doc.addObject("PartDesign::Body", name + "ToolBody")
    tool_body.AllowCompound = False
    tool_body.BaseFeature = host
    doc.recompute()
    boolean = body.newObject("PartDesign::Boolean", name)
    boolean.addObjects([tool_body])
    boolean.Type = kind
    boolean.Refine = refine
    doc.recompute()
    assert boolean.isValid(), f"kernel: {name} is invalid after recompute"
    assert body.Shape.isValid(), f"kernel: body is invalid after {name}"
    if kind == "Cut":
        assert body.Shape.Volume < before - min_delta, f"kernel: {name} did not remove material"
    else:
        assert body.Shape.Volume > before + min_delta, f"kernel: {name} did not add material"
    return boolean


def apply(body):
    target = body[0] if isinstance(body, tuple) else body
    _boolean(target, _patches(), "RightDuctPatches", "Fuse")
    _boolean(target, _fuse([_air_tool(), _finish_tool()]), "RightDuctAir", "Cut")
    _boolean(target, _fuse([_seals(), _lip_pad()]), "RightDuctSeals", "Fuse", refine=True)
    target.Document.recompute()
    for feat in target.Group:
        if str(getattr(feat, "TypeId", "")).startswith("PartDesign::") and hasattr(feat, "isValid"):
            assert feat.isValid(), f"kernel: feature {feat.Name} is invalid"
    assert target.Shape.isValid(), "kernel: body shape is invalid after rightDuct"
    return body
