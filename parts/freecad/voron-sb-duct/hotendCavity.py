import math

import FreeCAD
import Part
import PartDesign  # noqa: F401
from params import (
    backY,
    fanCenterZ,
    fanOpeningDiameter,
    frontY,
    hotendCavityBottomZ,
    hotendCavityHeight,
    hotendCavityTopZ,
    hotendCavityWidth,
    nozzleEndZ,
    topHoleAx,
    topHoleAy,
    topHoleBx,
    topHoleBy,
    topPilotDiameter,
    topZ,
)

assert hotendCavityWidth > 0, "infeasible: hotendCavityWidth must be positive"
assert hotendCavityHeight > 0, "infeasible: hotendCavityHeight must be positive"
assert hotendCavityBottomZ > nozzleEndZ, "infeasible: cavity bottom must sit above the nozzle end"
assert hotendCavityTopZ > hotendCavityBottomZ, "infeasible: cavity top must sit above its bottom"
assert fanOpeningDiameter > 0, "infeasible: fanOpeningDiameter must be positive"
assert fanCenterZ > nozzleEndZ, "infeasible: fan center must sit above the nozzle end"
assert fanCenterZ < topZ, "infeasible: fan center must sit below the housing top"
assert backY > frontY, "infeasible: back datum must sit behind the front face"

_OVERRUN = 0.04
# Source walls at ±13.15 (hotendWallSpacing 26.3); driven by the 26 mm cavity width.
_POCKET_HALF = hotendCavityWidth / 2 + 0.15
_REAR_ROOF_Z = 54.0
_BRIDGE_BOTTOM_Z = 27.8
_BRIDGE_TOP_Z = 29.0
_LOWER_RELIEF_R = 11.25
_UPPER_RELIEF_R = 10.2
_DIAG_R = 8.0
_DIAG_U = 0.7071
_DIAG_ORIGIN_Y = -14.542
_DIAG_ORIGIN_Z = 14.544
_DIAG_START_T = 0.989
_LEFT_DIAG_LEN = 17.759
_RIGHT_DIAG_LEN = 15.981
_LEFT_DIAG_END = _DIAG_START_T + _LEFT_DIAG_LEN
_FAN_MEET_Y = -16.0
_BLEND_R = 8.0
_BLEND_X = 10.658
_BLEND_Z = 40.871
_WALL_OUTER = 15.85
_WALL_OVERLAP = 0.6
_LEFT_WALL_Y0 = -7.47
# Stop 0.1 mm short of the exterior y=0 back face.
_LEFT_WALL_Y1 = -0.12
_LEFT_WALL_Z0 = 17.65
_LEFT_WALL_Z1 = 25.65
_RIGHT_WALL_Y0 = -8.41
_RIGHT_WALL_Y1 = -2.91
_RIGHT_WALL_Z0 = 17.52
_RIGHT_WALL_Z1 = 22.94
# Solid chin under the front mouth (x=0 / y=-20): no air chamber behind the bore floor.
_CHIN_R = 15.82
_CHIN_AXIS_Z = 13.58
_CHIN_TOP_Z = 29.4
_CHIN_END_Y = -12.6
_RAMP_C = 39.9
_RR_HALF = 15.5
_RR_TOP_Z = 57.0
_RR_CORNER = 12.0
_CAVITY_HALF = 12.7
_CAVITY_TOP_Z = 54.4
_CAVITY_CORNER = 5.5
_ROOF_START_Y = -8.6
_FRONT_STOP_Y = frontY + 0.2
# Roof: stop 0.8 mm under the fasteners pads (z=54). Rear slot skin at z 32..50 is opened (y to -5.25), not thickened: a full-width 0.8 mm wall at y=-6.2 joins sec_z30.
_REAR_CUT_Y = -6.2
_REAR_OPEN_Y = -5.25
_REAR_WALL_Y = -5.55
_ROOF_CUT_Z = 53.2
_MID_FRONT_Y = -19.0
_SLOT_Z0 = 32.0
_MID_FLOOR_Z = 17.05
_INNER_MARGIN = 1.15
_PILOT_COLLAR_R = 2.45
_PILOT_COLLAR_Z0 = 53.5
_PILOT_COLLAR_Z1 = 54.9
_FLOOR_SKIN_Y0 = -19.4
_FLOOR_SKIN_Y1 = -18.55

assert _POCKET_HALF > 0, "infeasible: pocket half-width must be positive"
assert _BRIDGE_BOTTOM_Z > hotendCavityBottomZ, "infeasible: bridge must sit above the cavity bottom"
assert _BRIDGE_TOP_Z > _BRIDGE_BOTTOM_Z, "infeasible: bridge must have positive thickness"
assert _REAR_ROOF_Z > hotendCavityTopZ, "infeasible: rear roof must sit above the front cavity top"
assert _LOWER_RELIEF_R < _POCKET_HALF, "infeasible: lower relief must stay inside the pocket walls"
assert _UPPER_RELIEF_R < _POCKET_HALF, "infeasible: upper relief must stay inside the pocket walls"
assert _FAN_MEET_Y > frontY, "infeasible: fan mouth must start forward of the bridge"
assert _LEFT_DIAG_END > _DIAG_START_T, "infeasible: left diagonal must have positive length"
assert _WALL_OUTER > _POCKET_HALF, "infeasible: wall pad must sit outside the pocket"
assert _CHIN_TOP_Z > _BRIDGE_TOP_Z, "infeasible: chin top must clear the bridge top"
assert _CHIN_TOP_Z < fanCenterZ - fanOpeningDiameter / 4.0, "infeasible: chin must stay below the fan mouth"
assert _RR_HALF > _CAVITY_HALF, "infeasible: rear mouth must be wider than the pocket"
assert abs(_CHIN_AXIS_Z + _CHIN_R - _CHIN_TOP_Z) < 1e-6, "infeasible: chin arc must be tangent to the chin flat"
assert _CHIN_R > _FAN_MEET_Y - _FRONT_STOP_Y, "infeasible: chin arc must reach the front face"
assert 2.0 * _RR_CORNER < _RR_TOP_Z - _CHIN_TOP_Z, "infeasible: mouth corner radius must fit its height"
assert 2.0 * _CAVITY_CORNER < 2.0 * _CAVITY_HALF, "infeasible: pocket corner radius must fit its width"
assert _REAR_OPEN_Y > -5.4, "infeasible: rear opener must cut through the y=-5.4 slot skin"
assert _REAR_WALL_Y < _REAR_OPEN_Y, "infeasible: remaining rear wall must sit inward of the slot opening"
assert _ROOF_CUT_Z <= 53.2, "infeasible: roof cut must leave 0.8 mm under the z=54 pads"
assert _ROOF_CUT_Z > _BRIDGE_TOP_Z, "infeasible: roof cut must sit above the bridge"
assert _SLOT_Z0 > _BRIDGE_TOP_Z, "infeasible: rear-slot opener must sit above the bridge"
assert topPilotDiameter > 0, "infeasible: topPilotDiameter must be positive"
assert topPilotDiameter / 2.0 + 0.8 <= _PILOT_COLLAR_R, (
    "infeasible: pilot collar must leave >= 0.8 mm wall around the bore"
)
assert _PILOT_COLLAR_Z1 <= 55.0, "infeasible: pilot collar must stay in the module z<=55 region"
assert _MID_FLOOR_Z >= 16.25 + 0.75, "infeasible: mid-pocket floor must leave >= 0.8 mm over the duct air"
assert _FLOOR_SKIN_Y1 - _FLOOR_SKIN_Y0 >= 0.8, "infeasible: fan-bore floor pad must be >= 0.8 mm thick"


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


def _cyl(radius, origin, direction, t0, t1):
    d = FreeCAD.Vector(*_vnorm(direction))
    p0 = FreeCAD.Vector(*origin) + d * t0
    return Part.makeCylinder(radius, t1 - t0, p0, d)


def _prism_yz(points_yz, xmin, xmax):
    vecs = [FreeCAD.Vector(xmin, p[0], p[1]) for p in points_yz]
    vecs.append(vecs[0])
    wire = Part.makePolygon(vecs)
    try:
        face = Part.Face(wire)
    except Exception:  # noqa: BLE001 — reversed winding if Face rejects the wire
        vecs = list(reversed(vecs))
        face = Part.Face(Part.makePolygon(vecs))
    return face.extrude(FreeCAD.Vector(xmax - xmin, 0, 0))


def _largest(shape):
    solids = [s for s in getattr(shape, "Solids", []) if s.Volume > 1e-8]
    if not solids:
        return shape
    out = solids[0]
    for extra in solids[1:]:
        out = out.fuse(extra)
    if hasattr(out, "removeSplitter"):
        out = out.removeSplitter()
    return out


def _fuse_tools(tools):
    fused = tools[0]
    for tool in tools[1:]:
        fused = fused.fuse(tool)
    return _largest(fused)


def _rounded_y_prism(xmin, xmax, ymin, ymax, zmin, zmax, radius):
    r = radius
    assert xmax - xmin > 2.0 * r, "infeasible: rounded prism too narrow for its radius"
    assert zmax - zmin > 2.0 * r, "infeasible: rounded prism too short for its radius"
    core = _box(xmin + r, xmax - r, ymin, ymax, zmin, zmax)
    mid = _box(xmin, xmax, ymin, ymax, zmin + r, zmax - r)
    corners = [
        _cyl(r, (x, ymin, z), (0.0, 1.0, 0.0), 0.0, ymax - ymin)
        for x in (xmin + r, xmax - r)
        for z in (zmin + r, zmax - r)
    ]
    return _fuse_tools([core, mid, *corners])


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


def _right_blend():
    # Stop 0.1 mm short of y=0 so the pin does not merge into backRightMain.
    pin = _cyl(_BLEND_R, (_BLEND_X, 0.0, _BLEND_Z), (0.0, 1.0, 0.0), -3.8, -0.1)
    return pin.common(_box(-16.0, _POCKET_HALF + 0.02, -3.85, backY - 0.1, 32.8, 48.9))


def _wall_fills():
    half = _POCKET_HALF
    left = _box(-_WALL_OUTER, -half + _WALL_OVERLAP, _LEFT_WALL_Y0, _LEFT_WALL_Y1, _LEFT_WALL_Z0, _LEFT_WALL_Z1)
    right = _box(half - _WALL_OVERLAP, _WALL_OUTER, _RIGHT_WALL_Y0, _RIGHT_WALL_Y1, _RIGHT_WALL_Z0, _RIGHT_WALL_Z1)
    return _fuse_tools([left, right])


def _chin():
    profile = [
        (_FRONT_STOP_Y, 23.5),
        (_FRONT_STOP_Y, _CHIN_TOP_Z),
        (_CHIN_END_Y, _CHIN_TOP_Z),
        (_CHIN_END_Y, _CHIN_END_Y + _RAMP_C),
        (23.5 - _RAMP_C, 23.5),
    ]
    # Reach |x|=13.25 so the chin fuses onto the exterior connector walls at ±13.
    prism = _prism_yz(profile, -13.25, 13.25)
    arc = _cyl(_CHIN_R, (0.0, _FAN_MEET_Y, _CHIN_AXIS_Z), (1.0, 0.0, 0.0), -13.6, 13.6)
    front = prism.common(arc)
    back = prism.common(_box(-13.30, 13.30, _FAN_MEET_Y - 0.05, _CHIN_END_Y + 0.1, 23.0, 29.02))
    chin = _fuse_tools([front, back])
    assert chin.Volume > 50.0, "kernel: chin fill is empty"
    return chin


def _pilot_keepout(z0=_PILOT_COLLAR_Z0, z1=_PILOT_COLLAR_Z1):
    return _fuse_tools(
        [
            _cyl(_PILOT_COLLAR_R, (topHoleAx, topHoleAy, 0.0), (0.0, 0.0, 1.0), z0, z1),
            _cyl(_PILOT_COLLAR_R, (topHoleBx, topHoleBy, 0.0), (0.0, 0.0, 1.0), z0, z1),
        ]
    )


def _pilot_collars():
    bore = topPilotDiameter / 2.0
    keep = _pilot_keepout()
    holes = _fuse_tools(
        [
            _cyl(bore, (topHoleAx, topHoleAy, 0.0), (0.0, 0.0, 1.0), _PILOT_COLLAR_Z0 - 0.1, _PILOT_COLLAR_Z1 + 0.1),
            _cyl(bore, (topHoleBx, topHoleBy, 0.0), (0.0, 0.0, 1.0), _PILOT_COLLAR_Z0 - 0.1, _PILOT_COLLAR_Z1 + 0.1),
        ]
    )
    return keep.cut(holes)


def _floor_and_side_pads():
    # 0.8 mm floor over the y=-19.4 skins; stop under z=20 and short of the right inlet at x=11.75.
    # Left wall at x=-13.2 only; a pad at x=+12 filled the right inlet and sealed those passages.
    return _fuse_tools(
        [
            _box(-12.20, 10.00, _FLOOR_SKIN_Y0, _FLOOR_SKIN_Y1, 16.30, 19.70),
            _box(-12.20, 10.00, _FLOOR_SKIN_Y0, _FLOOR_SKIN_Y1, 15.45, 16.30),
            _box(-13.20, -12.40, -19.30, -12.20, 14.30, 20.80),
            _box(-13.20, -12.40, -11.80, -8.60, 14.30, 20.80),
            _box(-1.50, 3.50, -24.50, -23.60, 18.20, 19.05),
        ]
    )


def _cavity_fills():
    half = _POCKET_HALF
    bore = topPilotDiameter / 2.0
    roof = _box(-12.0, 12.0, -7.5, _REAR_CUT_Y, _ROOF_CUT_Z, _REAR_ROOF_Z).cut(
        _fuse_tools(
            [
                _cyl(bore, (topHoleAx, topHoleAy, 0.0), (0.0, 0.0, 1.0), _ROOF_CUT_Z - 0.1, _REAR_ROOF_Z + 0.1),
                _cyl(bore, (topHoleBx, topHoleBy, 0.0), (0.0, 0.0, 1.0), _ROOF_CUT_Z - 0.1, _REAR_ROOF_Z + 0.1),
            ]
        )
    )
    bridge = _box(-13.15, 10.93, -10.3, -6.74, _BRIDGE_BOTTOM_Z, _BRIDGE_TOP_Z)
    # y=-12 waist only: keep z>27.8 so hotendBridgeBottom stays the y=-10.3 pad.
    waist = _box(-13.15, 10.93, -12.15, -10.25, 28.05, _BRIDGE_TOP_Z)
    lower_ramp = _prism_yz(
        [(-24.4, 18.97), (-24.4, 25.2), (-19.3, 25.2), (-19.3, 20.82)],
        -half + 0.3,
        half - 0.3,
    )
    bridge_ramp = _prism_yz(
        [(-19.4, -19.4 + _RAMP_C), (-19.4, 26.5), (-15.5, 26.5), (-15.5, -15.5 + _RAMP_C)],
        -half + 0.5,
        half - 0.5,
    )
    front_lip = _prism_yz(
        [(-27.2, 19.70), (-27.2, 24.2), (-23.9, 24.2), (-23.9, 19.156)],
        -half + 0.3,
        half - 0.3,
    )
    return _fuse_tools(
        [
            roof,
            bridge,
            waist,
            lower_ramp,
            bridge_ramp,
            front_lip,
            _chin(),
            _side_spans(),
            _floor_and_side_pads(),
            _pilot_collars(),
        ]
    )


def _side_spans():
    # Exterior side slots (13<|x|<17.4, z 16..28.4) are solid at y=-12/-20.
    # y=-12 foot-to-wall web stays inside |x|<=16 and 0.85 mm from lowerMountAccessAir.
    return _fuse_tools(
        [
            _box(-15.40, -13.05, _FRONT_STOP_Y, -8.55, 16.15, 29.15),
            _box(-15.95, -15.40, _FRONT_STOP_Y, -8.55, 16.15, 18.40),
            _box(-15.95, -15.40, _FRONT_STOP_Y, -8.55, 20.20, 29.15),
            _box(13.05, 15.40, _FRONT_STOP_Y, -8.55, 16.15, 29.15),
            _box(15.40, 15.95, _FRONT_STOP_Y, -8.55, 16.15, 18.40),
            _box(15.40, 15.95, _FRONT_STOP_Y, -8.55, 20.20, 29.15),
            _box(-15.90, -13.05, -12.35, -10.50, 2.40, 6.90),
        ]
    )


def _bridge_top_right():
    # 7.5 x 3.32 mm pad at the contract centre (3, -10.41); fused after the split.
    return _box(-0.75, 6.75, -12.08, -8.76, 28.92, 29.06)


def _bridge_top_split():
    return _fuse_tools(
        [
            _box(-13.2, -10.3, -10.35, -6.7, 28.95, 29.08),
            _box(-5.8, -0.75, -10.35, -6.7, 28.95, 29.08),
            _box(6.75, 11.0, -10.35, -6.7, 28.95, 29.08),
            _box(-10.3, -5.8, -10.35, -9.72, 28.95, 29.08),
            _box(-10.3, -5.8, -7.28, -6.7, 28.95, 29.08),
            _box(-0.75, 6.75, -8.70, -6.7, 28.95, 29.08),
        ]
    )


def _cut_batches():
    half = _POCKET_HALF
    inner = half - _INNER_MARGIN
    keep = _pilot_keepout()
    # Lower access only: do not open z>24.65 behind the fan floor (y=-19.2).
    mid_low = _box(-inner - 0.2, inner + 0.2, _MID_FRONT_Y, _REAR_WALL_Y, _MID_FLOOR_Z, 24.65)
    mid_upper = _box(-7.2, 7.2, _MID_FRONT_Y, _REAR_WALL_Y, 24.65 - _OVERRUN, _BRIDGE_BOTTOM_Z - _OVERRUN)
    # Pocket starts at the mouth meet (y=-16); ahead of it only the rounded mouth.
    pocket_front = _rounded_y_prism(
        -_CAVITY_HALF,
        _CAVITY_HALF,
        _FAN_MEET_Y - 0.05,
        _ROOF_START_Y,
        _BRIDGE_TOP_Z + _OVERRUN,
        _CAVITY_TOP_Z,
        _CAVITY_CORNER,
    ).cut(keep)
    pocket_rear = _box(-inner, inner, _ROOF_START_Y - _OVERRUN, _REAR_WALL_Y, _BRIDGE_TOP_Z + _OVERRUN, 50.55)
    rear_open = _box(-inner, inner, _REAR_WALL_Y, _REAR_OPEN_Y, _SLOT_Z0, 50.55)
    roof_pocket = _box(-inner, inner, -6.95, _REAR_CUT_Y, 50.55, _ROOF_CUT_Z)
    mouth_rear = _rounded_y_prism(
        -_RR_HALF,
        _RR_HALF,
        -19.3,
        _FAN_MEET_Y + 0.1,
        _CHIN_TOP_Z,
        _RR_TOP_Z,
        _RR_CORNER,
    ).common(_box(-_RR_HALF - 1.0, _RR_HALF + 1.0, -19.4, _FAN_MEET_Y + 0.2, _CHIN_TOP_Z - 0.1, _ROOF_CUT_Z))
    boxes = _fuse_tools(
        [
            mid_low,
            mid_upper,
            pocket_rear,
            rear_open,
            roof_pocket,
            _box(-half, -inner, _LEFT_WALL_Y0, _LEFT_WALL_Y1, _LEFT_WALL_Z0, _LEFT_WALL_Z1),
            _box(inner, half, _RIGHT_WALL_Y0, _RIGHT_WALL_Y1, _RIGHT_WALL_Z0, _RIGHT_WALL_Z1),
        ]
    )
    mouth = _fuse_tools([pocket_front, mouth_rear]).cut(_box(-0.85, 6.85, -12.15, -8.70, 28.80, 29.20))
    # Overrun the bridge faces; stay off y=0 so the back patches survive.
    lower = _cyl(_LOWER_RELIEF_R, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), _BRIDGE_BOTTOM_Z - 0.65, 29.36).common(
        _box(-_LOWER_RELIEF_R - 0.3, _LOWER_RELIEF_R + 0.3, -8.70, _REAR_WALL_Y, 27.10, 29.42)
    )
    upper = _cyl(_UPPER_RELIEF_R, (0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 50.55, _ROOF_CUT_Z).common(
        _box(
            -_UPPER_RELIEF_R - 1.0,
            _UPPER_RELIEF_R + 1.0,
            -8.0,
            _REAR_CUT_Y,
            50.5,
            _ROOF_CUT_Z,
        )
    )
    mid = _box(-15.8, 15.8, -18.8, -1.20, 15.45, 29.4)
    left_diag = _cyl(
        _DIAG_R,
        (-5.15, _DIAG_ORIGIN_Y, _DIAG_ORIGIN_Z),
        (0.0, _DIAG_U, _DIAG_U),
        _DIAG_START_T - _OVERRUN,
        _LEFT_DIAG_END + _OVERRUN,
    ).common(mid)
    right_diag = _cyl(
        _DIAG_R,
        (5.15, _DIAG_ORIGIN_Y, _DIAG_ORIGIN_Z),
        (0.0, _DIAG_U, _DIAG_U),
        _DIAG_START_T - _OVERRUN,
        _RIGHT_DIAG_LEN + _OVERRUN,
    ).common(_box(-3.0, 15.8, -18.8, _REAR_WALL_Y, 15.45, 29.2))
    return [
        ("HotendLowerRelief", lower),
        ("HotendCavityBoxes", boxes),
        ("HotendMouthCuts", mouth),
        ("HotendUpperRelief", upper),
        ("HotendLeftDiag", left_diag),
        ("HotendRightDiag", right_diag),
    ]


def apply(body):
    target = body[0] if isinstance(body, tuple) else body
    before_walls = target.Shape.Volume
    _boolean(target, _wall_fills(), "HotendWallFill", "Fuse")
    assert target.Shape.Volume > before_walls + 1.0, "kernel: HotendWallFill did not add material"
    for name, tool in _cut_batches():
        if getattr(tool, "Volume", 0) < 1e-3:
            continue
        _boolean(target, tool, name, "Cut")
    _boolean(target, _cavity_fills(), "HotendCavityFill", "Fuse")
    _boolean(target, _bridge_top_split(), "HotendBridgeSplit", "Cut")
    _boolean(target, _bridge_top_right(), "HotendBridgeTopRight", "Fuse")
    blend = _right_blend()
    if getattr(blend, "Volume", 0) > 1e-3:
        _boolean(target, blend, "RightCavityBlend", "Fuse")
    for feat in target.Group:
        if str(getattr(feat, "TypeId", "")).startswith("PartDesign::") and hasattr(feat, "isValid"):
            assert feat.isValid(), f"kernel: feature {feat.Name} is invalid"
    assert target.Shape.isValid(), "kernel: body shape is invalid after hotendCavity"
    solids = [s for s in target.Shape.Solids if s.Volume > 1e-6]
    if len(solids) > 1:
        solids.sort(key=lambda s: s.Volume, reverse=True)
        trash = solids[1]
        for extra in solids[2:]:
            trash = trash.fuse(extra)
        _boolean(target, trash, "HotendDropIslands", "Cut")
    assert target.Shape.isValid(), "kernel: body shape is invalid after hotendCavity"
    assert target.Shape.Volume > 1000.0, "kernel: hotendCavity volume collapsed"
    return body
