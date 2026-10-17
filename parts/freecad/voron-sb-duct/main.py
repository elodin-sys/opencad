import FreeCAD
import Part
import PartDesign  # noqa: F401
from datum import datum
from exterior import apply as apply_exterior
from fasteners import apply as apply_fasteners
from hotendCavity import apply as apply_hotendCavity
from leftDuct import apply as apply_leftDuct
from nozzleForks import apply as apply_nozzleForks
from params import (
    backY,
    fanCenterZ,
    fanOpeningDiameter,
    frontY,
    halfWidth,
    hotendCavityWidth,
    inletCenterY,
    inletDepth,
    leftInletCenterX,
    leftInletWidth,
    nozzleEndZ,
    rightInletCenterX,
    rightInletWidth,
    topBoreCylinderEndZ,
    topCounterboreDepth,
    topCounterboreDiameter,
    topHoleAx,
    topHoleAy,
    topHoleBx,
    topHoleBy,
    topPilotDiameter,
    topPilotLength,
    topPilotStartZ,
    topZ,
)
from rightDuct import apply as apply_rightDuct

_POCKET_HALF = hotendCavityWidth / 2 + 0.15
_WALL_OUTER = 15.85
_WALL_OVERLAP = 0.6
_LEFT_WALL_Y0 = -7.47
_LEFT_WALL_Y1 = 0.0
_LEFT_WALL_Z0 = 17.65
_LEFT_WALL_Z1 = 25.65
_RIGHT_WALL_Y0 = -8.41
_RIGHT_WALL_Y1 = -2.91
_RIGHT_WALL_Z0 = 17.52
_RIGHT_WALL_Z1 = 22.94
_HUB_R = 8.0
_VANE_R0 = 8.4
_VANE_R1 = fanOpeningDiameter / 2.0 - 0.4
_VANE_T = 1.25
_HUB_DZ = 0.2
_FAN_DEPTH = 8.2
# As-designed boss OD so a +0.2 mm bore sweep removes the annulus only.
_COLLAR_KEEP = 0.9
_COLLAR_OUTER_R = 2.7 / 2.0 + _COLLAR_KEEP
_COLLAR_Z0 = topPilotStartZ
_COLLAR_Z1 = topPilotStartZ + topPilotLength


def _box(xmin, xmax, ymin, ymax, zmin, zmax):
    assert xmax > xmin, "infeasible: box x1 must exceed x0"
    assert ymax > ymin, "infeasible: box y1 must exceed y0"
    assert zmax > zmin, "infeasible: box z1 must exceed z0"
    return Part.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, FreeCAD.Vector(xmin, ymin, zmin))


def _z_cyl(cx, cy, radius, z0, z1):
    assert radius > 0, "infeasible: cylinder radius must be positive"
    assert z1 > z0, "infeasible: cylinder z1 must exceed z0"
    return Part.makeCylinder(radius, z1 - z0, FreeCAD.Vector(cx, cy, z0), FreeCAD.Vector(0.0, 0.0, 1.0))


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
    return tool


def _boolean(body, solid, name, kind, refine=False, allow_compound=False):
    doc = body.Document
    before = body.Shape.Volume
    host = doc.addObject("Part::Feature", name + "Cutter")
    host.Shape = solid
    tool_body = doc.addObject("PartDesign::Body", name + "ToolBody")
    tool_body.AllowCompound = allow_compound
    tool_body.BaseFeature = host
    doc.recompute()
    boolean = body.newObject("PartDesign::Boolean", name)
    boolean.addObjects([tool_body])
    boolean.Type = kind
    boolean.Refine = refine
    doc.recompute()
    assert boolean.isValid(), f"kernel: {name} is invalid after recompute"
    assert body.Shape.isValid(), f"kernel: body is invalid after {name}"
    if kind == "Cut" and body.Shape.Volume >= before - 0.01:
        return None
    if kind == "Fuse" and body.Shape.Volume <= before + 0.01:
        return None
    return boolean


def _left_wall_pad():
    half = _POCKET_HALF
    return _box(-_WALL_OUTER, -half + _WALL_OVERLAP, _LEFT_WALL_Y0, _LEFT_WALL_Y1, _LEFT_WALL_Z0, _LEFT_WALL_Z1)


def _right_wall_pad():
    half = _POCKET_HALF
    return _box(half - _WALL_OVERLAP, _WALL_OUTER, _RIGHT_WALL_Y0, _RIGHT_WALL_Y1, _RIGHT_WALL_Z0, _RIGHT_WALL_Z1)


def _left_wall_cut():
    half = _POCKET_HALF
    return _box(-half, -(half - 1.15), _LEFT_WALL_Y0, _LEFT_WALL_Y1, _LEFT_WALL_Z0, _LEFT_WALL_Z1)


def _right_wall_cut():
    half = _POCKET_HALF
    return _box(half - 1.15, half, _RIGHT_WALL_Y0, _RIGHT_WALL_Y1, _RIGHT_WALL_Z0, _RIGHT_WALL_Z1)


def _rib_stitch():
    return _box(-19.55, -17.15, -4.85, 0.0, 31.70, 36.00)


def _x22_sliver():
    return _box(21.6, 22.4, -8.0, -0.2, 58.8, topZ)


def _y12_joins():
    # Foot joins and 0.85 mm envelopes (were 0.3/0.5 mm skins).
    return _join(
        [
            _box(-35.534, -28.5, -12.35, -10.5, 6.54, 14.0),
            _box(28.5, 35.534, -12.35, -10.5, 6.54, 14.0),
            _box(-24.0, -18.0, -12.3, -10.5, 2.37, 3.6),
            _box(18.0, 24.0, -12.3, -10.5, 2.37, 3.6),
            _box(-35.534, -35.25, -12.50, -11.65, 6.70, 8.05),
            _box(35.25, 35.534, -12.50, -11.65, 6.70, 8.05),
            _box(15.30, 19.55, -12.50, -11.65, 20.15, 21.00),
        ]
    )


def _y12_trims():
    # Drop the two leftover islands; shave the outer walls (no new holes).
    # 0.6 mm strip at x=-14.2 is filled air — remove it (also pays the 6% area band).
    return _join(
        [
            _box(-30.55, -28.55, -12.25, -11.75, 14.15, 18.85),
            _box(-27.75, -27.15, -12.25, -11.75, 13.35, 14.05),
            _box(-35.534, -34.62, -12.25, -11.75, 8.00, 50.00),
            _box(34.62, 35.534, -12.25, -11.75, 8.00, 50.00),
            _box(-14.20, -13.60, -13.90, -5.10, 8.00, 16.00),
            _box(-34.62, -34.38, -12.25, -11.75, 10.00, 24.00),
            _box(34.38, 34.62, -12.25, -11.75, 10.00, 24.00),
        ]
    )


def _y12_close():
    return _box(19.65, 20.25, -12.50, -11.65, 3.55, 6.62)


def _z20_joins():
    return _box(11.30, 12.20, -2.60, -1.20, 19.575, 20.425)


def _z55_close():
    # Meet the y=-19 inboard wall; grow to 0.85 mm in X and Z.
    return _box(15.00, 15.85, -19.35, -14.80, 54.575, 55.425)


def _z55_notch():
    # Pay the close wall plus the module-only 971 mm2 so sec_z55 stays under 944.89.
    return _join(
        [
            _box(28.50, 32.70, -27.40, -22.20, 54.575, 55.425),
            _box(-32.70, -28.50, -27.40, -22.20, 54.575, 55.425),
        ]
    )


def _z20_trims():
    # Grille strip at y=-19, 0.54 mm2 skin at y=-5.5, leftover wall-pad sliver,
    # and the X22_WEB floor below z=20.3 (top at 21.5 keeps sec_x22 closed).
    return _join(
        [
            _box(-6.10, 6.10, -19.25, -18.95, 19.85, 20.15),
            _box(2.35, 6.10, -5.62, -5.32, 19.85, 20.15),
            _box(-12.10, -9.20, -3.35, 0.05, 19.70, 20.30),
            _box(19.45, 22.40, -24.50, -7.30, 19.65, 20.35),
        ]
    )


def _film_cuts():
    # 0.15 mm Y-film at the cavity rear lip. Left-leg cut isolated a z=20 chip
    # and shaved auxLowerSeat; that skin stays (p05 already has margin).
    return _box(-6.20, 6.20, -5.72, -5.18, 17.50, 32.20)


def _back_left_right():
    # 1.6 mm flush, split around leftMountRail (x=-14.465) and gapped at z=30
    # so the left pad is not a third island on sec_z30.
    xs = ((-19.90, -14.80), (-14.15, -10.50))
    zs = ((26.00, 29.10), (31.20, 50.00))
    return _join([_box(x0, x1, -1.60, 0.0, z0, z1) for x0, x1 in xs for z0, z1 in zs])


def _pilot_collars():
    bore = topPilotDiameter / 2.0
    assert topPilotDiameter > 0, "infeasible: topPilotDiameter must be positive"
    assert bore < _COLLAR_OUTER_R, "infeasible: pilot bore must sit inside the collar"
    assert _COLLAR_Z1 > _COLLAR_Z0, "infeasible: collar z1 must exceed z0"
    tubes = []
    for cx, cy in ((topHoleAx, topHoleAy), (topHoleBx, topHoleBy)):
        outer = _z_cyl(cx, cy, _COLLAR_OUTER_R, _COLLAR_Z0, _COLLAR_Z1)
        inner = _z_cyl(cx, cy, bore, _COLLAR_Z0 - 0.1, _COLLAR_Z1 + 0.1)
        tubes.append(outer.cut(inner))
    return _join(tubes)


def _fastener_recuts():
    # After collars (and the rim) so a depth/diameter sweep removes the full annulus.
    bore = topPilotDiameter / 2.0
    cbore = topCounterboreDiameter / 2.0
    z0 = topPilotStartZ
    z1 = topPilotStartZ + topPilotLength
    floor = topBoreCylinderEndZ - topCounterboreDepth
    # Stop at the straight counterbore end (60.9); cutting to topZ merges the Ø5
    # entry and makes topCounterboreA 3.5 mm vs 2.9.
    top = topBoreCylinderEndZ + 0.05
    assert topPilotDiameter > 0, "infeasible: topPilotDiameter must be positive"
    assert topCounterboreDiameter > topPilotDiameter, "infeasible: topCounterboreDiameter must exceed topPilotDiameter"
    assert topCounterboreDepth > 0, "infeasible: topCounterboreDepth must be positive"
    assert z1 > z0, "infeasible: pilot recut z1 must exceed z0"
    assert top > floor, "infeasible: counterbore recut must sit above its floor"
    tools = []
    for cx, cy in ((topHoleAx, topHoleAy), (topHoleBx, topHoleBy)):
        tools.append(_z_cyl(cx, cy, bore, z0, z1))
        tools.append(_z_cyl(cx, cy, cbore, floor, top))
    return _join(tools)


def _lip_trim():
    # Drop the extra z=5.1..5.5 sliver so backRightOutletLip assigns the 10.4 mm2 face.
    return _join(
        [
            _box(16.15, 20.30, -0.05, 0.12, 5.10, 5.56),
            _box(-20.30, -16.15, -0.05, 0.12, 5.10, 5.56),
        ]
    )


def _hub():
    zc = fanCenterZ + _HUB_DZ
    y0 = -25.3
    y1 = -20.5
    assert y0 >= frontY, "infeasible: hub must sit inside the envelope front"
    hub = Part.makeCylinder(_HUB_R, y1 - y0, FreeCAD.Vector(0.0, y0, zc), FreeCAD.Vector(0.0, 1.0, 0.0))
    left = _box(-19.0, -7.8, -24.6, -21.4, zc - 0.6, zc + 0.6)
    right = _box(7.8, 19.0, -24.6, -21.4, zc - 0.6, zc + 0.6)
    return _join([hub, left, right])


def _spokes():
    y0 = frontY - 0.5
    depth = _FAN_DEPTH + 1.0
    zc = fanCenterZ + _HUB_DZ
    span = _VANE_R1 - _VANE_R0
    assert span > 0, "infeasible: spoke cut must sit inside the fan bore"
    tools = []
    for angle in (45.0, 135.0, 225.0, 315.0):
        vane = Part.makeBox(span, depth, _VANE_T, FreeCAD.Vector(_VANE_R0, y0, zc - _VANE_T / 2.0))
        vane.rotate(FreeCAD.Vector(0.0, 0.0, zc), FreeCAD.Vector(0.0, 1.0, 0.0), angle)
        tools.append(vane)
    return _join(tools)


def _z45_web():
    # Outer-leg grooves only — do not join the fan bore to the trunk holes.
    return _join(
        [
            _box(-34.8, -28.0, -20.0, -6.5, 44.4, 45.6),
            _box(28.0, 34.8, -20.0, -6.5, 44.4, 45.6),
        ]
    )


def _z30_bridge():
    assert nozzleEndZ < 30.0, "infeasible: z=30 bridge must sit above the nozzle end"
    return _box(-12.0, 12.0, -5.6, -1.5, 29.2, 31.0)


def _top_skim():
    return _box(-halfWidth - 0.2, halfWidth + 0.2, frontY - 0.2, backY + 0.2, topZ - 0.30, topZ + 0.30)


def _rim_plate():
    # 0.80 mm lid; stop short of y=-5 so sec_y-5 does not grow.
    raw = _box(-33.0, 32.2, -23.2, -5.15, topZ - 0.80, topZ)
    left = _box(
        leftInletCenterX - leftInletWidth / 2.0,
        leftInletCenterX + leftInletWidth / 2.0,
        inletCenterY - inletDepth / 2.0,
        inletCenterY + inletDepth / 2.0,
        topZ - 0.85,
        topZ + 0.06,
    )
    right = _box(
        rightInletCenterX - rightInletWidth / 2.0,
        rightInletCenterX + rightInletWidth / 2.0,
        inletCenterY - inletDepth / 2.0,
        inletCenterY + inletDepth / 2.0,
        topZ - 0.85,
        topZ + 0.06,
    )
    screw = _box(topHoleBx - 2.6, topHoleBx + 2.6, topHoleBy - 2.6, topHoleBy + 2.6, topZ - 0.85, topZ + 0.06)
    return _largest(raw.cut(_join([left, right, screw])))


def _solids(shape):
    return [s for s in getattr(shape, "Solids", []) if s.Volume > 1e-6]


def _drop_islands(body):
    extras = _solids(body.Shape)
    if len(extras) <= 1:
        return
    extras.sort(key=lambda s: s.Volume, reverse=True)
    trash = extras[1]
    for extra in extras[2:]:
        trash = trash.fuse(extra)
    _boolean(body, trash, "IntegrateDropIslands", "Cut", refine=True, allow_compound=True)


def apply_integrate(body):
    target = body[0] if isinstance(body, tuple) else body
    target.AllowCompound = True
    _boolean(
        target,
        _join(
            [
                _left_wall_pad(),
                _right_wall_pad(),
                _rib_stitch(),
                _x22_sliver(),
                _y12_joins(),
                _y12_close(),
                _z20_joins(),
                _z55_close(),
                _pilot_collars(),
                _back_left_right(),
            ]
        ),
        "IntegrateFuse",
        "Fuse",
        refine=True,
        allow_compound=True,
    )
    _boolean(
        target,
        _join(
            [
                _left_wall_cut(),
                _right_wall_cut(),
                _z30_bridge(),
                _spokes(),
                _z45_web(),
                _z20_trims(),
                _y12_trims(),
                _z55_notch(),
                _film_cuts(),
                _lip_trim(),
            ]
        ),
        "IntegrateCut",
        "Cut",
        allow_compound=True,
    )
    _boolean(target, _hub(), "IntegrateHub", "Fuse")
    _boolean(target, _top_skim(), "IntegrateTopSkim", "Cut")
    _boolean(target, _rim_plate(), "IntegrateRim", "Fuse")
    _boolean(target, _fastener_recuts(), "IntegrateRecut", "Cut")
    _drop_islands(target)
    target.Document.recompute()
    for feat in target.Group:
        if str(getattr(feat, "TypeId", "")).startswith("PartDesign::") and hasattr(feat, "isValid"):
            assert feat.isValid(), f"kernel: feature {feat.Name} is invalid"
    assert target.Shape.isValid(), "kernel: body shape is invalid after integrate"
    assert frontY < backY, "infeasible: frontY must sit forward of backY"
    assert halfWidth > 0, "infeasible: halfWidth must be positive"
    n = len(_solids(target.Shape))
    assert n == 1, f"kernel: integrate left {n} solids"
    return body


result = apply_integrate(
    apply_nozzleForks(apply_rightDuct(apply_leftDuct(apply_hotendCavity(apply_fasteners(apply_exterior(datum))))))
)
