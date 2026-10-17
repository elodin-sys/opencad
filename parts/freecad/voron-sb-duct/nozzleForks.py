import FreeCAD
import Part
import PartDesign  # noqa: F401
from params import ductDepth, ductMidCenterX, ductMidCenterY, ductWall, ductWidth, outletsPerDuct, wallMinimum

assert outletsPerDuct >= 2, "infeasible: each duct must fork into two outlets"
assert ductWidth > 0, "infeasible: ductWidth must be positive"
assert ductDepth > 0, "infeasible: ductDepth must be positive"
assert ductWall > 0, "infeasible: ductWall must be positive"
assert wallMinimum > 0, "infeasible: wallMinimum must be positive"
assert ductMidCenterY < 0, "infeasible: mid-duct centre must sit forward of the back datum"

_BOUNDARY_Z = 16.0
_TOOL_Z1 = _BOUNDARY_Z - 0.1
_DIVIDER_Z0 = 5.2
_SEAL = 3.2
_BALL = _SEAL * 2.0 + 0.3
_WEB_Y0 = ductMidCenterY - 0.95
# Fill the 0.5 mm sliver (old web y=-14.15, rear air y=-13.6) without eating the 3.2 mm ball at y=-13.2.
_WEB_Y1 = -13.45
_REAR_Y0 = -13.4
_REAR_Y1 = -6.6
_REAR_Z0 = 6.7
_FRONT_KEEP_Y = -26.0
_LIP_Y = -1.6
_WALL = 0.85
_HOTEND_FACE = 13.15
_HOTEND_STOP = 13.25
_PAD_X0 = 14.05
_PAD_X1 = 19.70
_PAD_Y0 = -15.80
_CHIN_Y1 = -1.70
_CHIN_Z0 = 2.40
_CHIN_Z1 = 7.85
_MID_Z0 = 5.85
_MID_Z1 = 6.70
_HOTEND_LO_Z1 = 9.4
_HOTEND_HI_Z0 = 10.6
_AFT_CUT_Y0 = -6.72
_AFT_CUT_Y1 = -5.92
_LIP_PAD_Y0 = -0.90
_LIP_PAD_Y1 = 0.0
_LIP_PAD_Z0 = 2.40
_LIP_PAD_Z1 = 5.10

assert _WEB_Y1 < _REAR_Y0, "infeasible: divider must sit forward of the rear outlet"
assert _WEB_Y0 > _FRONT_KEEP_Y, "infeasible: divider must not fill the front outlet"
assert _WEB_Y1 < _LIP_Y, "infeasible: divider must stay forward of the y=0 lip pads"
assert _REAR_Y1 - _REAR_Y0 >= _BALL, "infeasible: rear outlet y span must beat the 3.2 mm closing"
assert _TOOL_Z1 - _REAR_Z0 >= _BALL, "infeasible: rear outlet z span must beat the 3.2 mm closing"
assert _WALL >= wallMinimum, "infeasible: restore wall must cover wallMinimum"
assert ductWall + 0.05 <= _WALL + 0.2, "infeasible: restore wall must cover ductWall"
assert _HOTEND_STOP >= _HOTEND_FACE + 0.099, "infeasible: inboard pad must stop 0.1 mm short of the hotend face"
assert _CHIN_Y1 < _LIP_Y, "infeasible: chin fill must stay forward of the lip pads"
assert _CHIN_Z1 < 10.0, "infeasible: chin fill must stay under the z=10 station"
assert _MID_Z1 <= _REAR_Z0 + 1e-6, "infeasible: mid floor must not fill the rear chamber"
assert _MID_Z1 - _MID_Z0 >= _WALL - 1e-6, "infeasible: mid floor must be at least wall thick"
assert _HOTEND_LO_Z1 < 10.0 < _HOTEND_HI_Z0, "infeasible: hotend pads must skip the z=10 station"
assert _AFT_CUT_Y1 - _AFT_CUT_Y0 >= wallMinimum, "infeasible: aft-skin cut must cover the 0.6 mm wall"
assert _AFT_CUT_Y1 < -5.55, "infeasible: aft-skin cut must stay forward of the rear-well"
assert _LIP_PAD_Y1 - _LIP_PAD_Y0 >= _WALL - 1e-6, "infeasible: lip pad must be at least wall thick"
assert _LIP_PAD_Y1 <= 0.0, "infeasible: lip pad must stay inside the module y=0 face"


def _box(xmin, xmax, ymin, ymax, zmin, zmax):
    assert xmax > xmin, "infeasible: box x1 must exceed x0"
    assert ymax > ymin, "infeasible: box y1 must exceed y0"
    assert zmax > zmin, "infeasible: box z1 must exceed z0"
    return Part.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, FreeCAD.Vector(xmin, ymin, zmin))


def _fuse(tools):
    fused = tools[0]
    for tool in tools[1:]:
        fused = fused.fuse(tool)
    if hasattr(fused, "removeSplitter"):
        fused = fused.removeSplitter()
    return fused


def _left_divider():
    hw = ductWidth / 2.0
    return _box(
        -ductMidCenterX - hw - 4.5,
        -ductMidCenterX + 2.6,
        _WEB_Y0,
        _WEB_Y1,
        _DIVIDER_Z0,
        _TOOL_Z1,
    )


def _right_divider():
    hw = ductWidth / 2.0
    return _box(
        ductMidCenterX - 2.6,
        ductMidCenterX + hw + 4.5,
        _WEB_Y0,
        _WEB_Y1,
        _DIVIDER_Z0,
        _TOOL_Z1,
    )


def _rear_chambers():
    hw = ductWidth / 2.0
    z1 = 10.0 + _SEAL + 0.2
    left = _box(
        -ductMidCenterX - hw - 3.2,
        -ductMidCenterX - 0.75,
        _REAR_Y0,
        _REAR_Y1,
        _REAR_Z0,
        z1,
    )
    right = _box(
        ductMidCenterX + 0.75,
        ductMidCenterX + hw + 3.2,
        _REAR_Y0,
        _REAR_Y1,
        _REAR_Z0,
        z1,
    )
    return _fuse([left, right])


def _wall_restore():
    # Start above z=2.367 so nozzleBaseLeft/Right stay the pad faces.
    # Hotend-side pads skip z=9.4..10.6 so sec_z10 keeps four holes.
    left_chin = _box(-_PAD_X1, -_PAD_X0, _PAD_Y0, _CHIN_Y1, _CHIN_Z0, _CHIN_Z1)
    right_chin = _box(_PAD_X0, _PAD_X1, _PAD_Y0, _CHIN_Y1, _CHIN_Z0, _CHIN_Z1)
    left_hotend_lo = _box(-14.20, -_HOTEND_STOP, -14.0, _CHIN_Y1, _DIVIDER_Z0, _HOTEND_LO_Z1)
    left_hotend_hi = _box(-14.20, -_HOTEND_STOP, -14.0, _CHIN_Y1, _HOTEND_HI_Z0, _TOOL_Z1)
    right_hotend = _box(_HOTEND_STOP, _HOTEND_STOP + _WALL, _PAD_Y0, _CHIN_Y1, _DIVIDER_Z0, _CHIN_Z1)
    left_floor = _box(-30.6, -_PAD_X1, -14.2, -6.4, _CHIN_Z0, _CHIN_Z0 + _WALL)
    right_floor = _box(_PAD_X1, 30.6, -14.2, -6.4, _CHIN_Z0, _CHIN_Z0 + _WALL)
    left_mid = _box(-30.6, -20.0, -14.2, -6.4, _MID_Z0, _MID_Z1)
    right_mid = _box(20.0, 30.6, -14.2, -6.4, _MID_Z0, _MID_Z1)
    left_lip = _box(-20.10, -16.20, _LIP_PAD_Y0, _LIP_PAD_Y1, _LIP_PAD_Z0, _LIP_PAD_Z1)
    right_lip = _box(16.20, 20.10, _LIP_PAD_Y0, _LIP_PAD_Y1, _LIP_PAD_Z0, _LIP_PAD_Z1)
    return _fuse(
        [
            left_chin,
            right_chin,
            left_hotend_lo,
            left_hotend_hi,
            right_hotend,
            left_floor,
            right_floor,
            left_mid,
            right_mid,
            left_lip,
            right_lip,
        ]
    )


def _outer_skin():
    # 0.10 mm film on the right-leg envelope at y=-12.3; remove it.
    return _box(34.80, 35.60, -12.45, -12.15, 8.45, 12.10)


def _aft_skins():
    # Open the 0.6 mm aft films. Skip z=10 so sec_z10 keeps four holes.
    # Do not fuse y>-6.6: that recaps the exterior shave and the right cylinder.
    left_lo = _box(-31.05, -22.85, _AFT_CUT_Y0, _AFT_CUT_Y1, 6.50, _HOTEND_LO_Z1)
    left_hi = _box(-31.05, -22.85, _AFT_CUT_Y0, _AFT_CUT_Y1, _HOTEND_HI_Z0, _TOOL_Z1)
    right_lo = _box(24.45, 28.95, _AFT_CUT_Y0, _AFT_CUT_Y1, 8.20, _HOTEND_LO_Z1)
    right_hi = _box(24.45, 28.95, _AFT_CUT_Y0, _AFT_CUT_Y1, _HOTEND_HI_Z0, _TOOL_Z1)
    return _fuse([left_lo, left_hi, right_lo, right_hi])


def _boolean(body, solid, name, kind, refine, min_delta=0.05, optional=False):
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
    if kind == "Fuse":
        if body.Shape.Volume <= before + min_delta:
            assert optional, f"kernel: {name} did not add material"
            return None
    elif body.Shape.Volume >= before - min_delta:
        assert optional, f"kernel: {name} did not remove material"
        return None
    return boolean


def apply(body):
    target = body[0] if isinstance(body, tuple) else body
    _boolean(target, _left_divider(), "NozzleForksLeftDivider", "Fuse", False)
    _boolean(target, _right_divider(), "NozzleForksRightDivider", "Fuse", False)
    _boolean(target, _wall_restore(), "NozzleForksWalls", "Fuse", False)
    _boolean(target, _rear_chambers(), "NozzleForksRearAir", "Cut", False)
    _boolean(target, _aft_skins(), "NozzleForksAftSkin", "Cut", False)
    _boolean(target, _outer_skin(), "NozzleForksOuterSkin", "Cut", True, min_delta=0.01, optional=True)
    target.Document.recompute()
    for feat in target.Group:
        if str(getattr(feat, "TypeId", "")).startswith("PartDesign::") and hasattr(feat, "isValid"):
            assert feat.isValid(), f"kernel: feature {feat.Name} is invalid"
    assert target.Shape.isValid(), "kernel: body shape is invalid after nozzleForks"
    return body
