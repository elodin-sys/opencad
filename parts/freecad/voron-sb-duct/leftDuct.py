import math

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
    leftInletCenterX,
    leftInletWidth,
    nozzleEndZ,
    outletsPerDuct,
    topZ,
    wallMinimum,
)

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
assert topZ > nozzleEndZ, "infeasible: topZ must be above nozzleEndZ"
assert frontY < backY, "infeasible: frontY must sit forward of backY"
assert halfWidth > ductMidCenterX, "infeasible: left trunk must fit inside the envelope half-width"
assert fanOpeningDiameter > 0, "infeasible: fanOpeningDiameter must be positive"

_OVERRUN = 0.04
_INLET_TURN_R = 10.0
_INLET_TURN_Y = -21.953
_INLET_TURN_Z = 54.064
_INLET_TURN_X0 = -24.736
_INLET_TURN_LEN = 13.403
_RIGHT_STOP = -0.1
# Inlet neck: above _NECK_Z only a strip along the turn's rear arc (y >= _NECK_Y0)
# stays open, so the 3.2 mm closing seals the mouth while leftInletTurn survives.
_NECK_Z = 57.5
_NECK_Y0 = -18.0
_NECK_Z1 = 60.4
_TRUNK_X0 = -27.2
_TRUNK_X1 = -19.75
_LOWER_X0 = -27.2
_LOWER_X1 = -21.0
_LOWER_Y0 = -15.5
_REAR_Y1 = -7.0
_LOWER_Z0 = 17.5
_LOWER_Z1 = 28.5
_REAR_X0 = -27.2
_REAR_X1 = -22.15
_REAR_Z0 = 7.8
_REAR_Z1 = 18.8
_FRONT_X0 = -27.2
_SHAVE_X = -30.5
_SHAVE_REAR_X = -23.2
_SHAVE_REAR_Y = -6.85
_HOTEND_AIR = -13.95
_LEG_SKIN = -27.7
_NEAR_WEB_Z0 = 7.7
_JOIN_X0 = -30.5
_JOIN_Z0 = 28.5
_JOIN_Z1 = 31.5
_TUNNEL_X0 = -28.6
_TUNNEL_Y0 = -13.4
_TUNNEL_Y1 = -6.6
_TUNNEL_Z0 = 14.0
_TUNNEL_Z1 = 22.6

assert _REAR_Y1 + wallMinimum <= -4.2, "infeasible: duct rear wall must keep wallMinimum from the aux bores"
assert _LOWER_X0 - wallMinimum >= -29.534, "infeasible: lower trunk must keep wallMinimum from the front pocket"
assert _REAR_Z0 - wallMinimum >= 6.567, "infeasible: rear outlet floor must keep wallMinimum above the skim"
assert _REAR_X1 < -22.0, "infeasible: rear outlet must stop short of the x=-22 section plane"
assert _NECK_Z1 + 1.0 <= topZ, "infeasible: neck roof must keep 1 mm under the top face"
assert _NECK_Z1 <= 60.7, "infeasible: neck roof must stay at or below 60.7"
assert _TRUNK_X0 >= -27.2, "infeasible: trunk air must keep 0.8 mm inside the x=-28 skin"
assert _SHAVE_X - wallMinimum >= -31.534, "infeasible: trunk must keep wallMinimum from the side shave"
assert _SHAVE_REAR_Y <= -6.0 - (wallMinimum + 0.1), (
    "infeasible: rear trunk must keep wallMinimum+0.1 from the rear shave"
)
assert _HOTEND_AIR <= -13.15 - wallMinimum, "infeasible: duct must keep wallMinimum from the hotend wall"
assert _LEG_SKIN >= -28.5 + wallMinimum, "infeasible: lower-leg air must keep wallMinimum inside x=-28.5"
assert _TUNNEL_X0 <= _REAR_X1 - 6.4, "infeasible: tunnel x-span must beat the 3.2 mm closing"
assert _TUNNEL_Y1 - _TUNNEL_Y0 >= 6.4, "infeasible: tunnel y-span must beat the 3.2 mm closing"
assert _TUNNEL_Z1 - _TUNNEL_Z0 >= 6.4, "infeasible: tunnel z-span must beat the 3.2 mm closing"
assert _TUNNEL_Z0 >= 14.0, "infeasible: tunnel must sit above the x=-28.5 lower-leg cut"
assert _JOIN_X0 >= _SHAVE_X, "infeasible: z=30 join must stay inside the side shave"


def _vnorm(vec):
    x, y, z = vec
    n = math.sqrt(x * x + y * y + z * z)
    assert n > 1e-9, "infeasible: zero direction"
    return (x / n, y / n, z / n)


def _box(xmin, xmax, ymin, ymax, zmin, zmax):
    assert xmax > xmin, "infeasible: box x1 must exceed x0"
    assert ymax > ymin, "infeasible: box y1 must exceed y0"
    assert zmax > zmin, "infeasible: box z1 must exceed z0"
    return Part.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, FreeCAD.Vector(xmin, ymin, zmin))


def _fuse(tools):
    solids = [t for t in tools if t is not None and not t.isNull() and t.Volume > 1e-9]
    assert solids, "infeasible: no duct tools to fuse"
    fused = solids[0]
    for tool in solids[1:]:
        fused = fused.fuse(tool)
    if hasattr(fused, "removeSplitter"):
        fused = fused.removeSplitter()
    return fused


def _inlet_turn():
    x0 = _INLET_TURN_X0 - _OVERRUN
    length = _INLET_TURN_LEN + 2.0 * _OVERRUN
    cyl = Part.makeCylinder(
        _INLET_TURN_R,
        length,
        FreeCAD.Vector(x0, _INLET_TURN_Y, _INLET_TURN_Z),
        FreeCAD.Vector(1, 0, 0),
    )
    front_half = _box(
        x0 - 1.0,
        x0 + length + 1.0,
        _INLET_TURN_Y - _INLET_TURN_R - 1.0,
        _INLET_TURN_Y,
        _INLET_TURN_Z - _INLET_TURN_R - 1.0,
        _INLET_TURN_Z + _INLET_TURN_R + 1.0,
    )
    half = cyl.cut(front_half)
    leak = _box(x0 - 1.0, x0 + length + 1.0, -13.0, 1.0, 60.7, 66.0)
    return half.cut(leak)


def _plane_slab(origin, normal, u0, u1, v0, v1, depth):
    n = _vnorm(normal)
    nv = FreeCAD.Vector(*n)
    helper = FreeCAD.Vector(0, 1, 0) if abs(n[1]) < 0.9 else FreeCAD.Vector(1, 0, 0)
    u = nv.cross(helper)
    assert u.Length > 1e-9, "infeasible: plane slab axes collapsed"
    u.normalize()
    v = nv.cross(u)
    v.normalize()
    o = FreeCAD.Vector(*origin)
    pts = [
        o + u * u0 + v * v0,
        o + u * u1 + v * v0,
        o + u * u1 + v * v1,
        o + u * u0 + v * v1,
    ]
    pts.append(pts[0])
    try:
        face = Part.Face(Part.makePolygon(pts))
    except Exception:  # noqa: BLE001 — reversed winding if Face rejects the wire
        face = Part.Face(Part.makePolygon(list(reversed(pts))))
    return face.extrude(nv * depth)


def _inner_lip():
    y0 = -6.3
    y1 = -1.45
    pts = [
        FreeCAD.Vector(-15.24, y0, 6.7),
        FreeCAD.Vector(-14.15, y0, 11.16),
        FreeCAD.Vector(-14.15, y0, 6.7),
    ]
    pts.append(pts[0])
    try:
        face = Part.Face(Part.makePolygon(pts))
    except Exception:  # noqa: BLE001 — reversed winding if Face rejects the wire
        face = Part.Face(Part.makePolygon(list(reversed(pts))))
    return face.extrude(FreeCAD.Vector(0, y1 - y0, 0))


def _lip_pad():
    island = _box(-20.27, -16.17, -0.65, 0.0, 2.425, 5.515)
    stem = _box(-20.27, -16.17, -1.5, -0.45, 5.0, 7.5)
    return _fuse([island, stem])


def _keepout():
    hotend = _box(_HOTEND_AIR, _RIGHT_STOP + 0.2, frontY - 0.1, backY + 0.1, 15.0, 54.6)
    right = _box(_RIGHT_STOP, 1.0, frontY - 1.0, backY + 1.0, nozzleEndZ - 1.0, topZ + 1.0)
    u_cut = _box(_HOTEND_AIR, 0.2, frontY - 0.2, backY + 0.2, nozzleEndZ - 0.2, 20.4)
    skim = _box(-halfWidth - 1.0, halfWidth + 1.0, frontY - 0.2, -2.9, nozzleEndZ - 0.2, 6.7)
    rear_slot = _box(-20.2, 20.2, -6.2, backY + 0.2, 19.7, topZ + 0.2)
    left_slot = _box(-17.6, -12.8, frontY - 0.2, backY + 0.2, 19.7, 28.8)
    well = _box(-halfWidth - 1.0, halfWidth + 1.0, -1.4, backY + 0.2, nozzleEndZ - 0.2, topZ + 0.2)
    fan = Part.makeCylinder(
        fanOpeningDiameter / 2.0 + 0.9,
        14.0,
        FreeCAD.Vector(0, frontY - 0.2, fanCenterZ),
        FreeCAD.Vector(0, 1, 0),
    )
    fan_box = _box(-19.65, 1.0, frontY - 0.2, -19.2, 28.0, 50.0)
    front_left = _box(-halfWidth - 1.0, _TRUNK_X0, frontY - 0.2, -11.9, _JOIN_Z1, 53.2)
    trunk_skin = _box(-halfWidth - 1.0, _TRUNK_X0, frontY - 0.2, backY + 0.2, 26.0, _JOIN_Z0)
    low_left = _box(-halfWidth - 1.0, _LEG_SKIN, frontY - 0.2, -11.9, nozzleEndZ - 0.2, 14.2)
    roof_bite = _box(-31.3, -21.4, frontY - 0.2, -20.4, 57.2, topZ + 0.2)
    side_shave = _box(-halfWidth - 1.0, _SHAVE_X, frontY - 0.2, backY + 0.2, 7.5, 53.5)
    rear_shave = _box(-halfWidth - 1.0, _SHAVE_REAR_X, _SHAVE_REAR_Y, backY + 0.2, 7.5, 53.5)
    bevel_pts = [
        FreeCAD.Vector(-21.38, 0.2, 40.9),
        FreeCAD.Vector(-28.38, -14.0, 40.9),
        FreeCAD.Vector(-halfWidth - 1.0, -14.0, 40.9),
        FreeCAD.Vector(-halfWidth - 1.0, 0.2, 40.9),
    ]
    bevel_pts.append(bevel_pts[0])
    try:
        bevel_face = Part.Face(Part.makePolygon(bevel_pts))
    except Exception:  # noqa: BLE001 — reversed winding if Face rejects the wire
        bevel_face = Part.Face(Part.makePolygon(list(reversed(bevel_pts))))
    bevel = bevel_face.extrude(FreeCAD.Vector(0, 0, topZ + 1.0 - 40.9))
    return _fuse(
        [
            hotend,
            right,
            u_cut,
            skim,
            rear_slot,
            left_slot,
            well,
            fan,
            fan_box,
            front_left,
            trunk_skin,
            low_left,
            roof_bite,
            side_shave,
            rear_shave,
            bevel,
        ]
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
        _box(_TRUNK_X0, _TRUNK_X1, -23.0, -7.4, 26.0, 54.94),
        # Joined outer bite at z=30 only: one left hole, 1 mm to the side-shave face.
        _box(_JOIN_X0, _TRUNK_X0, -23.0, -7.4, _JOIN_Z0, _JOIN_Z1),
        _box(-27.0, -20.0, -23.0, -7.4, 54.9, 56.0),
        _box(_LOWER_X0, _LOWER_X1, _LOWER_Y0, _REAR_Y1, _LOWER_Z0, _LOWER_Z1),
        _box(_REAR_X0, _REAR_X1, -13.6, -6.9, _REAR_Z0, _REAR_Z1),
        _box(_JOIN_X0, _REAR_X1, -12.0, -6.9, _REAR_Z0, _REAR_Z1),
        _box(_TUNNEL_X0, _REAR_X1, _TUNNEL_Y0, _TUNNEL_Y1, _TUNNEL_Z0, _TUNNEL_Z1),
        _box(_TUNNEL_X0, _LOWER_X1, _TUNNEL_Y0, _REAR_Y1, _LOWER_Z0, _TUNNEL_Z1),
        _box(_FRONT_X0, -23.0, -26.0, -13.4, 10.6, 18.0),
        _box(-26.0, -21.0, -11.94, -5.6, 7.3, 12.5),
        _box(_LEG_SKIN, -21.0, -26.2, -17.5, 7.6, 12.5),
        _box(-19.6, -14.35, -11.94, -5.6, _NEAR_WEB_Z0, 10.4),
        _box(-19.6, -14.35, -26.2, -17.5, _NEAR_WEB_Z0, 10.4),
        _inner_lip(),
        _plane_slab((-15.24, -4.0, 6.7), (0.971, 0.0, -0.2391), -3.0, 2.0, -1.0, 4.0, 0.9),
        _plane_slab((-14.635, -27.433, 9.123), (0.7527, 0.0698, 0.6547), -2.0, 4.0, -1.5, 2.5, 0.8),
    ]
    raw = _fuse(tools)
    trimmed = raw.cut(_keepout())
    above = _box(-halfWidth - 1.0, 1.0, frontY - 1.0, backY + 1.0, _NECK_Z, topZ + 5.0)
    neck = _inlet_turn().common(_box(-26.0, -10.0, _NECK_Y0, -9.0, _NECK_Z - _OVERRUN, _NECK_Z1))
    assert neck.Volume > 0.1, "infeasible: inlet neck common is empty"
    trimmed = trimmed.cut(above).fuse(neck)
    assert trimmed.Volume > 1.0, "infeasible: left duct keepout emptied the air tool"
    return trimmed


def _seals():
    # Guard the |x|<19.5 rear slot only; do not pad the top face (topInletRim).
    return _box(-19.6, -13.3, -7.3, -5.6, 19.6, 52.0)


def _boolean(body, solid, name, kind):
    doc = body.Document
    host = doc.addObject("Part::Feature", name + "Cutter")
    host.Shape = solid
    tool_body = doc.addObject("PartDesign::Body", name + "ToolBody")
    tool_body.AllowCompound = False
    tool_body.BaseFeature = host
    doc.recompute()
    boolean = body.newObject("PartDesign::Boolean", name)
    boolean.addObjects([tool_body])
    boolean.Type = kind
    boolean.Refine = True
    doc.recompute()
    assert boolean.isValid(), f"kernel: {name} is invalid after recompute"
    return boolean


def apply(body):
    target = body[0] if isinstance(body, tuple) else body
    _boolean(target, _air_tool(), "LeftCoolingDuct", "Cut")
    _boolean(target, _lip_pad(), "LeftOutletLipPad", "Fuse")
    _boolean(target, _seals(), "LeftDuctSeals", "Fuse")
    target.Document.recompute()
    for feat in target.Group:
        if str(getattr(feat, "TypeId", "")).startswith("PartDesign::") and hasattr(feat, "isValid"):
            assert feat.isValid(), f"kernel: feature {feat.Name} is invalid"
    assert target.Shape.isValid(), "kernel: body shape is invalid after leftDuct"
    return body
