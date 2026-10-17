import FreeCAD
import Part
import PartDesign  # noqa: F401
from params import (
    backY,
    ductDepth,
    ductMidCenterX,
    ductMidCenterY,
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
    overallDepth,
    overallHeight,
    overallWidth,
    rightInletCenterX,
    rightInletWidth,
    topZ,
)

assert overallWidth > 0, "infeasible: overallWidth must be positive"
assert overallDepth > 0, "infeasible: overallDepth must be positive"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
assert halfWidth > 0, "infeasible: halfWidth must be positive"
assert topZ > nozzleEndZ, "infeasible: topZ must be above nozzleEndZ"
assert frontY < backY, "infeasible: frontY must sit forward of backY"
assert fanOpeningDiameter > 0, "infeasible: fanOpeningDiameter must be positive"
assert leftInletWidth > 0, "infeasible: leftInletWidth must be positive"
assert rightInletWidth > 0, "infeasible: rightInletWidth must be positive"
assert inletDepth > 0, "infeasible: inletDepth must be positive"
assert ductWidth > 0, "infeasible: ductWidth must be positive"
assert ductDepth > 0, "infeasible: ductDepth must be positive"
assert ductMidCenterX > 0, "infeasible: ductMidCenterX must be positive"

_OVERRUN = 0.04
_U_HALF = 13.0
_U_TOP = 16.2
_SLOT_IN = 6.0
_SLOT_OUT = 9.3
_SLOT_TOP = 28.4
_REAR_OPEN_Y = -5.4
_REAR_RECESS = 1.2
_PAD_THICK = 2.0
_FAN_DEPTH = 8.2
_INLET_CUT = 2.2
_SKIM_Z = 4.2
_HOTEND_CLEAR = 6.0
_SIDE_SHAVE = 4.0
_REAR_SHAVE = 7.3
_BEVEL_IN = 18.55
_TOP_CORNER = 30.4

_LEFT_MAIN = (-24.0, -10.5, 19.34, 61.5)
_RIGHT_MAIN = (7.5, 16.0, 36.5, 61.5)
_RIGHT_MOUNT = (13.9, 19.1, 17.0, 22.5)
_PAD_X = 2.5
_PAD_Y = 5.25
# Chin / rear-well stock the cutter must leave, so sec_x±22 stays one body.
_CHIN_X_IN = 20.2
_CHIN_X_OUT = 26.8
_CHIN_Y0 = -24.0
_CHIN_Y1 = -6.15
_CHIN_Z0 = 0.08
_CHIN_Z1 = 6.60
_WELL_X_IN = 19.0
_WELL_X_OUT = 26.0
_WELL_Y0 = -2.40
_WELL_Y1 = -0.06
_WELL_Z0 = 16.0
_WELL_Z1 = 19.52
# Fan grille: Ø16 hub centred 0.2 mm above the bore axis, four 45 deg spokes to the rim.
_HUB_R = 8.0
_HUB_DZ = 0.2
_VANE_T = 1.2
_VANE_R0 = 4.0
_VANE_R1 = 20.0

assert _HUB_R < fanOpeningDiameter / 2.0 - 4.0, "infeasible: hub must leave a 4 mm air ring inside the bore"
assert _VANE_R1 > fanOpeningDiameter / 2.0, "infeasible: vanes must reach past the bore rim"
assert _CHIN_X_IN > 19.7, "infeasible: chin keep must stay off the nozzle-base pads"
assert _CHIN_Y1 < -5.5, "infeasible: chin keep must not add stock on the y=-5 station"
assert _CHIN_Z1 <= 6.65, "infeasible: chin keep must stay 0.85 mm under leftDuctAir z=7.5"
assert _WELL_Y0 > -3.9, "infeasible: rear-well keep must stay off the 3.2 mm duct closing"
assert _WELL_Y1 < -0.04, "infeasible: rear-well keep must not grow the y=0 mating pads"
assert _WELL_Z0 < 16.5, "infeasible: rear-well keep must cover the sliver from z=16.5"


def _box(xmin, ymin, zmin, xmax, ymax, zmax):
    assert xmax > xmin, "infeasible: box x1 must exceed x0"
    assert ymax > ymin, "infeasible: box y1 must exceed y0"
    assert zmax > zmin, "infeasible: box z1 must exceed z0"
    return Part.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, FreeCAD.Vector(xmin, ymin, zmin))


def _prism_y(pts_xz, y0, y1):
    wire = [FreeCAD.Vector(x, y0, z) for x, z in pts_xz]
    wire.append(wire[0])
    try:
        face = Part.Face(Part.makePolygon(wire))
    except Exception:  # noqa: BLE001 — reversed winding if Face rejects the wire
        face = Part.Face(Part.makePolygon(list(reversed(wire))))
    return face.extrude(FreeCAD.Vector(0, y1 - y0, 0))


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


def _join(parts):
    tool = parts[0]
    for extra in parts[1:]:
        tool = tool.fuse(extra)
    return _largest(tool)


def _pad_box(x0, x1, z0, z1, y0, y1):
    return _box(x0, y0, z0, x1, y1, z1)


def _two_leg_tools():
    y0 = frontY - _OVERRUN
    y1 = backY + _OVERRUN
    z0 = nozzleEndZ - _OVERRUN
    # Through-splitters stay inside the hotend pocket. Do not slot the duct wall.
    left_slot = _box(-_SLOT_OUT, y0, _U_TOP - 0.15, -_SLOT_IN, y1, _SLOT_TOP)
    right_slot = _box(_SLOT_IN, y0, _U_TOP - 0.15, _SLOT_OUT, y1, _SLOT_TOP)
    return [
        _box(-_U_HALF, y0, z0, _U_HALF, y1, _U_TOP + 0.15),
        left_slot,
        right_slot,
        _box(
            -ductMidCenterX - ductWidth / 2.0,
            ductMidCenterY - ductDepth / 2.0,
            _U_TOP,
            -ductMidCenterX + ductWidth / 2.0,
            ductMidCenterY + ductDepth / 2.0,
            _SLOT_TOP,
        ),
        _box(
            ductMidCenterX - ductWidth / 2.0,
            ductMidCenterY - ductDepth / 2.0,
            _U_TOP,
            ductMidCenterX + ductWidth / 2.0,
            ductMidCenterY + ductDepth / 2.0,
            _SLOT_TOP,
        ),
    ]


def _rear_tools():
    left = _pad_box(*_LEFT_MAIN, -_PAD_THICK, backY + _OVERRUN)
    right = _pad_box(*_RIGHT_MAIN, -_PAD_THICK, backY + _OVERRUN)
    mount = _pad_box(*_RIGHT_MOUNT, -_PAD_THICK, backY + _OVERRUN)
    slot = _box(-_HOTEND_CLEAR, _REAR_OPEN_Y, _U_TOP - 0.15, _HOTEND_CLEAR, backY + _OVERRUN, topZ + _OVERRUN)
    slot = _largest(slot.cut(left).cut(right).cut(mount))
    well = _box(
        -halfWidth - _OVERRUN,
        -_REAR_RECESS,
        nozzleEndZ - _OVERRUN,
        halfWidth + _OVERRUN,
        backY + _OVERRUN,
        topZ + _OVERRUN,
    )
    well = _largest(well.cut(left).cut(right).cut(mount))
    return [slot, well]


def _nozzle_tools():
    y0 = frontY - _OVERRUN
    y1 = backY + _OVERRUN
    z0 = nozzleEndZ - _OVERRUN
    left_pts = (
        (-halfWidth - _OVERRUN, z0),
        (-_BEVEL_IN, z0),
        (-halfWidth - _OVERRUN, 6.80),
    )
    right_pts = (
        (halfWidth + _OVERRUN, z0),
        (_BEVEL_IN, z0),
        (halfWidth + _OVERRUN, 6.80),
    )
    skim = _box(-halfWidth - _OVERRUN, y0, z0, halfWidth + _OVERRUN, y1, nozzleEndZ + _SKIM_Z)
    lx, ly = -17.14, -10.47
    rx, ry = 17.14, -10.47
    left_pad = _box(lx - _PAD_X, ly - _PAD_Y, z0, lx + _PAD_X, ly + _PAD_Y, nozzleEndZ + _SKIM_Z + _OVERRUN)
    right_pad = _box(rx - _PAD_X, ry - _PAD_Y, z0, rx + _PAD_X, ry + _PAD_Y, nozzleEndZ + _SKIM_Z + _OVERRUN)
    skim = _largest(skim.cut(left_pad).cut(right_pad))
    return [
        _prism_y(left_pts, y0, y1),
        _prism_y(right_pts, y0, y1),
        skim,
    ]


def _outer_tools():
    y0 = frontY - _OVERRUN
    y1 = backY + _OVERRUN
    z0 = nozzleEndZ - _OVERRUN
    left_pad = _pad_box(*_LEFT_MAIN, -_PAD_THICK, backY + _OVERRUN)
    rear_y0 = -6.0
    return [
        _box(-halfWidth - _OVERRUN, y0, 54.0, -_TOP_CORNER, y1, topZ + _OVERRUN),
        _box(_TOP_CORNER, y0, 54.0, halfWidth + _OVERRUN, y1, topZ + _OVERRUN),
        _box(-halfWidth - _OVERRUN, y0, 8.0, -halfWidth + _SIDE_SHAVE, y1, 53.0),
        _box(halfWidth - _SIDE_SHAVE, y0, 8.0, halfWidth + _OVERRUN, y1, 53.0),
        _largest(
            _box(
                -halfWidth - _OVERRUN,
                rear_y0,
                8.0,
                -halfWidth + _SIDE_SHAVE + _REAR_SHAVE,
                y1,
                53.0,
            ).cut(left_pad)
        ),
        _box(
            halfWidth - _SIDE_SHAVE - _REAR_SHAVE,
            rear_y0,
            8.0,
            halfWidth + _OVERRUN,
            y1,
            53.0,
        ),
        _box(-halfWidth - _OVERRUN, y0, z0, -28.5, -12.0, 14.0),
        _box(28.5, y0, z0, halfWidth + _OVERRUN, -12.0, 14.0),
        _box(22.0, -7.0, 59.5, halfWidth + _OVERRUN, y1, topZ + _OVERRUN),
        _box(-halfWidth - _OVERRUN, y0, 48.0, -31.0, -8.0, 61.6),
        _box(31.0, y0, 48.0, halfWidth + _OVERRUN, -8.0, 61.6),
    ]


def _inlet_tools():
    z0 = topZ - _INLET_CUT
    z1 = topZ + _OVERRUN
    ly0 = inletCenterY - inletDepth / 2.0
    ly1 = inletCenterY + inletDepth / 2.0
    left = _box(
        leftInletCenterX - leftInletWidth / 2.0,
        ly0,
        z0,
        leftInletCenterX + leftInletWidth / 2.0,
        ly1,
        z1,
    )
    right = _box(
        rightInletCenterX - rightInletWidth / 2.0,
        ly0,
        z0,
        rightInletCenterX + rightInletWidth / 2.0,
        ly1,
        z1,
    )
    return [left, right]


def _front_tools():
    y0 = frontY - _OVERRUN
    y1 = frontY + _FAN_DEPTH
    fan = Part.makeCylinder(
        fanOpeningDiameter / 2.0,
        _FAN_DEPTH + _OVERRUN,
        FreeCAD.Vector(0, y0, fanCenterZ),
        FreeCAD.Vector(0, 1, 0),
    )
    fan = fan.common(_box(-20.0, y0, 24.0, 20.0, y1 + _OVERRUN, topZ - _INLET_CUT - 1.3))
    connector = _box(-_U_HALF, y0, _U_TOP, _U_HALF, y1, 32.0)
    return [fan, connector]


def _grille():
    y0 = frontY - 0.5
    depth = _FAN_DEPTH + 1.0
    zc = fanCenterZ + _HUB_DZ
    hub = Part.makeCylinder(_HUB_R, depth, FreeCAD.Vector(0.0, y0, zc), FreeCAD.Vector(0.0, 1.0, 0.0))
    span = _VANE_R1 - _VANE_R0
    vanes = []
    for angle in (45.0, 135.0, 225.0, 315.0):
        vane = Part.makeBox(span, depth, _VANE_T, FreeCAD.Vector(_VANE_R0, y0, zc - _VANE_T / 2.0))
        vane.rotate(FreeCAD.Vector(0.0, 0.0, zc), FreeCAD.Vector(0.0, 1.0, 0.0), angle)
        vanes.append(vane)
    return _join([hub, *vanes])


def _leg_keep():
    z0 = nozzleEndZ + _CHIN_Z0
    left_chin = _box(-_CHIN_X_OUT, _CHIN_Y0, z0, -_CHIN_X_IN, _CHIN_Y1, _CHIN_Z1)
    right_chin = _box(_CHIN_X_IN, _CHIN_Y0, z0, _CHIN_X_OUT, _CHIN_Y1, _CHIN_Z1)
    left_well = _box(-_WELL_X_OUT, _WELL_Y0, _WELL_Z0, -_WELL_X_IN, _WELL_Y1, _WELL_Z1)
    right_well = _box(_WELL_X_IN, _WELL_Y0, _WELL_Z0, _WELL_X_OUT, _WELL_Y1, _WELL_Z1)
    return _join([left_chin, right_chin, left_well, right_well])


def _exterior_tool():
    tool = _join(_two_leg_tools() + _rear_tools() + _nozzle_tools() + _outer_tools() + _inlet_tools() + _front_tools())
    tool = _largest(tool.cut(_leg_keep()))
    return _largest(tool.cut(_grille()))


def _boolean_cut(body, tool, name):
    doc = body.Document
    before = body.Shape.Volume
    host = doc.addObject("Part::Feature", name + "Cutter")
    host.Shape = tool
    tool_body = doc.addObject("PartDesign::Body", name + "ToolBody")
    tool_body.AllowCompound = False
    tool_body.BaseFeature = host
    doc.recompute()
    boolean = body.newObject("PartDesign::Boolean", name)
    boolean.addObjects([tool_body])
    boolean.Type = "Cut"
    boolean.Refine = True
    doc.recompute()
    assert boolean.isValid(), f"kernel: {name} is invalid after recompute"
    assert body.Shape.isValid(), f"kernel: body is invalid after {name}"
    assert body.Shape.Volume < before - 1.0, f"kernel: {name} did not remove material"
    return boolean


def apply(body):
    target = body[0] if isinstance(body, tuple) else body
    _boolean_cut(target, _exterior_tool(), "ExteriorCuts")
    for feat in target.Group:
        if str(getattr(feat, "TypeId", "")).startswith("PartDesign::") and hasattr(feat, "isValid"):
            assert feat.isValid(), f"kernel: feature {feat.Name} is invalid"
    target.Document.recompute()
    return body
