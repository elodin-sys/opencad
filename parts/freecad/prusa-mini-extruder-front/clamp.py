"""Partial clamp channel tools, clipped to the module region, cut as one family."""

import math

import FreeCAD
import Part
import PartDesign  # noqa: F401
import Sketcher
from params import (
    bodyTopZ,
    bottomZ,
    clampAxialLipDiameter,
    clampAxisX,
    clampCenterY,
    clampCornerAxisX,
    clampCornerAxisZ,
    clampCornerEnd,
    clampCornerFarY,
    clampCornerLipDiameter,
    clampCornerNearY,
    clampCornerOffsetDiameter,
    clampCornerOffsetLipDiameter,
    clampCornerOffsetX,
    clampCornerOffsetZ,
    clampCornerOuterDiameter,
    clampCornerStart,
    clampEndZ,
    clampFarLipDiameter,
    clampFarLipStart,
    clampFarY,
    clampInnerDiameter,
    clampNearY,
    clampOffsetDiameter,
    clampOffsetX,
    clampOuterDiameter,
    clampReliefDiameter,
    clampStartZ,
    clampTiltAxisX,
    clampTiltAxisZ,
    clampTiltDirX,
    clampTiltDirZ,
    clampTiltEnd,
    clampTiltFarEnd,
    clampTiltFarStart,
    clampTiltInnerX,
    clampTiltInnerZ,
    clampTiltNearEnd,
    clampTiltNearStart,
    clampTiltStart,
    clampUpperFarEnd,
    clampUpperInnerX,
    clampUpperNearEnd,
    clampUpperReliefEnd,
    clampUpperReliefX,
    counterboreDiameter,
    halfWidth,
    pivotCounterboreStart,
    pivotPilotEnd,
    plateThickness,
    rightBottomChamferZ,
    rightPilotStart,
    rightPivotX,
    screwDiameter,
    sideScallopDiameter,
    sideScallopEnd,
    sideScallopX,
    sideScallopZ,
    upperRightScrewX,
    upperRightScrewZ,
)

assert clampOuterDiameter > clampAxialLipDiameter, "infeasible: axial cut must exceed the lip"
assert clampCornerOuterDiameter > clampCornerLipDiameter, "infeasible: corner cut must exceed the lip"
assert clampOffsetDiameter > clampFarLipDiameter, "infeasible: offset cut must exceed the far lip"
assert clampCornerOffsetDiameter > clampCornerOffsetLipDiameter, "infeasible: corner offset cut must exceed the lip"
assert clampReliefDiameter > clampInnerDiameter, "infeasible: relief must exceed the inner cut"
assert clampOuterDiameter > 0, "infeasible: clampOuterDiameter must be positive"
assert clampInnerDiameter > 0, "infeasible: clampInnerDiameter must be positive"
assert sideScallopDiameter > 0, "infeasible: sideScallopDiameter must be positive"
assert clampEndZ > clampStartZ, "infeasible: clamp z extent must be positive"
assert clampCornerEnd > clampCornerStart, "infeasible: corner t extent must be positive"

_SQ2 = 2.0**0.5
_E_U = (1.0 / _SQ2, 0.0, 1.0 / _SQ2)
_E_V = (1.0 / _SQ2, 0.0, -1.0 / _SQ2)
_OV = 0.05


def _vnorm(vec):
    x, y, z = vec
    n = math.sqrt(x * x + y * y + z * z)
    assert n > 1e-9, "infeasible: zero direction"
    return (x / n, y / n, z / n)


def _solid_shape(shape):
    if shape is None or shape.isNull() or not shape.Solids:
        return None
    assert shape.isValid(), "kernel: invalid construction tool"
    return shape


def _common(a, b):
    if a is None or b is None:
        return None
    return _solid_shape(a.common(b))


def _cut_shape(stock, cutter):
    if stock is None or cutter is None:
        return stock
    return _solid_shape(stock.cut(cutter))


def _fuse_all(shapes):
    tools = [shape for shape in shapes if shape is not None]
    assert tools, "kernel: empty clamp family"
    merged = tools[0].multiFuse(tools[1:]).removeSplitter() if len(tools) > 1 else tools[0]
    assert merged.isValid(), "kernel: clamp tool union is invalid"
    return merged


def _orient(shape, origin, x_dir, z_dir):
    x = FreeCAD.Vector(*x_dir)
    x.normalize()
    z = FreeCAD.Vector(*z_dir)
    z.normalize()
    y = z.cross(x)
    y.normalize()
    x = y.cross(z)
    x.normalize()
    shape.Placement = FreeCAD.Placement(origin, FreeCAD.Rotation(x, y, z))
    return shape


def _cyl(ox, oy, oz, dx, dy, dz, radius, t0, t1, extra=0.02, extra0=None):
    ux, uy, uz = _vnorm((dx, dy, dz))
    lead = extra if extra0 is None else extra0
    start = t0 - lead
    height = (t1 - t0) + lead + extra
    origin = FreeCAD.Vector(ox + ux * start, oy + uy * start, oz + uz * start)
    return Part.makeCylinder(radius, height, origin, FreeCAD.Vector(ux, uy, uz))


def _annulus(ox, oy, oz, dx, dy, dz, r_outer, r_inner, t0, t1, extra=0.02, extra0=None):
    outer = _cyl(ox, oy, oz, dx, dy, dz, r_outer, t0, t1, extra=extra, extra0=extra0)
    inner = _cyl(ox, oy, oz, dx, dy, dz, r_inner, t0, t1, extra=0.0)
    return _cut_shape(outer, inner)


def _box(xmin, xmax, ymin, ymax, zmin, zmax):
    return Part.makeBox(xmax - xmin, ymax - ymin, zmax - zmin, FreeCAD.Vector(xmin, ymin, zmin))


def _keep(shape, xmin, xmax, ymin, ymax, zmin, zmax):
    return _common(shape, _box(xmin, xmax, ymin, ymax, zmin, zmax))


def _uvy(u, v, y):
    return FreeCAD.Vector((u + v) / _SQ2, y, (u - v) / _SQ2)


def _uv_box(u0, u1, v0, v1, y0, y1):
    return _orient(
        Part.makeBox(v1 - v0, y1 - y0, u1 - u0),
        _uvy(u0, v0, y0),
        _E_V,
        _E_U,
    )


def _plane_tool(point, normal, depth=50.0, span=80.0):
    n = FreeCAD.Vector(*_vnorm(normal))
    arb = FreeCAD.Vector(0, 1, 0) if abs(n.y) < 0.85 else FreeCAD.Vector(1, 0, 0)
    x = n.cross(arb)
    if x.Length < 1e-9:
        x = n.cross(FreeCAD.Vector(0, 0, 1))
    x.normalize()
    raw = Part.makeBox(span, span, depth, FreeCAD.Vector(-span / 2.0, -span / 2.0, 0.0))
    return _orient(raw, FreeCAD.Vector(*point), (x.x, x.y, x.z), (n.x, n.y, n.z))


def _subtract(shape, cutter):
    return _cut_shape(shape, cutter)


def _install_tool(body, tool):
    """One unified construction tool, clipped by an editable PartDesign envelope."""
    doc = body.Document
    raw_body = doc.addObject("PartDesign::Body", "ClampRawToolBody")
    raw_body.AllowCompound = True
    base = raw_body.newObject("PartDesign::Feature", "ClampToolBase")
    base.Label = "Unified partial channels, lips, slots and scallop tool"
    base.Shape = tool
    doc.recompute()
    assert base.isValid() and raw_body.isValid(), "kernel: invalid clamp tool body"

    tool_body = doc.addObject("PartDesign::Body", "ClampToolBody")
    tool_body.AllowCompound = True
    plane = next(obj for obj in tool_body.Origin.OriginFeatures if "XY" in obj.Name and "Plane" in obj.Name)
    sketch = tool_body.newObject("Sketcher::SketchObject", "ClampRegionSketch")
    sketch.AttachmentSupport = [(plane, "")]
    sketch.MapMode = "FlatFace"
    sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0.0, 0.0, bottomZ - 0.02), FreeCAD.Rotation())
    points = [
        (15.0, -0.02),
        (halfWidth + 0.02, -0.02),
        (halfWidth + 0.02, plateThickness + 0.02),
        (15.0, plateThickness + 0.02),
    ]
    for index, point in enumerate(points):
        following = points[(index + 1) % len(points)]
        sketch.addGeometry(Part.LineSegment(FreeCAD.Vector(*point, 0.0), FreeCAD.Vector(*following, 0.0)), False)
    for index, point in enumerate(points):
        sketch.addConstraint(Sketcher.Constraint("Coincident", index, 2, (index + 1) % len(points), 1))
        sketch.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, index, 1, point[0]))
        sketch.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, index, 1, point[1]))
    doc.recompute()
    assert sketch.isValid() and sketch.FullyConstrained, "sketch: clamp region must be fully constrained"
    pad = tool_body.newObject("PartDesign::Pad", "ClampRegionEnvelope")
    pad.Profile = sketch
    pad.Length = bodyTopZ - 0.1 - (bottomZ - 0.02)
    pad.Refine = True
    doc.recompute()
    assert pad.isValid(), "kernel: invalid clamp region envelope"
    clipped = tool_body.newObject("PartDesign::Boolean", "ClampRegionIntersection")
    clipped.Type = "Common"
    clipped.Group = [raw_body]
    clipped.Refine = True
    doc.recompute()
    assert clipped.isValid(), "kernel: invalid clipped clamp tool"
    feature = body.newObject("PartDesign::Boolean", "ClampChannels")
    feature.Type = "Cut"
    feature.Group = [tool_body]
    feature.Refine = True
    doc.recompute()
    assert feature.isValid(), "kernel: clamp Boolean is invalid"
    return feature


def _fastener_clearance():
    """Reserve 0.1 mm around the two neighbouring stepped bore families."""
    clearance = 0.1
    cb_radius = counterboreDiameter / 2.0 + clearance
    pilot_radius = screwDiameter / 2.0 + clearance
    return _fuse_all(
        [
            _cyl(
                rightPivotX,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                cb_radius,
                pivotCounterboreStart - clearance,
                plateThickness + 0.02,
                extra=0.0,
            ),
            _cyl(rightPivotX, 0.0, 0.0, 0.0, 1.0, 0.0, pilot_radius, -0.02, pivotPilotEnd + clearance, extra=0.0),
            _cyl(
                upperRightScrewX,
                0.0,
                upperRightScrewZ,
                0.0,
                1.0,
                0.0,
                pilot_radius,
                rightPilotStart - clearance,
                plateThickness + 0.02,
                extra=0.0,
            ),
        ]
    )


def apply(body):
    if isinstance(body, tuple):
        for item in body:
            apply(item)
        return body
    assert halfWidth > 15.0, "infeasible: clamp region leaves the plate"
    assert plateThickness > clampCornerFarY > clampCornerNearY > 0.0, "infeasible: corner axes leave the plate"
    assert bottomZ < clampStartZ < clampEndZ < bodyTopZ, "infeasible: clamp slots leave the plate"
    assert clampTiltEnd > clampTiltStart, "infeasible: reversed tilted channel"
    assert clampTiltNearEnd > clampTiltNearStart, "infeasible: reversed near tilted cut"
    assert clampTiltFarEnd > clampTiltFarStart, "infeasible: reversed far tilted cut"
    assert clampUpperReliefEnd > clampUpperFarEnd > clampUpperNearEnd > 0.0, "infeasible: upper channels are reversed"
    assert 0.0 < sideScallopEnd < plateThickness, "infeasible: scallop depth leaves the plate"
    assert counterboreDiameter > screwDiameter > 0.0, "infeasible: neighbouring bore diameters are reversed"
    original = body.Shape.copy()
    extra = 0.02
    air = 0.03
    corner_dx = 0.7071
    corner_dz = 0.7071
    tilt_dx = clampTiltDirX
    tilt_dz = clampTiltDirZ

    ax0, ax1 = 20.4, 32.0
    cx0 = 16.55
    y0, y1 = -3.05, 14.05
    z0, z1 = -30.2, 27.6

    r_axial = clampOuterDiameter / 2.0
    r_axial_lip = clampAxialLipDiameter / 2.0
    r_corner = clampCornerOuterDiameter / 2.0
    r_corner_lip = clampCornerLipDiameter / 2.0
    r_offset = clampOffsetDiameter / 2.0
    r_far_lip = clampFarLipDiameter / 2.0
    r_corner_off = clampCornerOffsetDiameter / 2.0
    r_corner_off_lip = clampCornerOffsetLipDiameter / 2.0
    r_inner = clampInnerDiameter / 2.0
    r_relief = clampReliefDiameter / 2.0
    r_scallop = sideScallopDiameter / 2.0

    def groove_parts(zlo, zhi, far_xmax, y_lo=2.0, y_hi=11.6):
        ring = _annulus(clampAxisX, clampCenterY, 0.0, 0.0, 0.0, 1.0, r_axial, r_axial_lip, zlo, zhi, extra=0.0)
        near_cut = _subtract(
            _annulus(clampOffsetX, clampNearY, 0.0, 0.0, 0.0, 1.0, r_offset, 0.01, zlo, zhi, extra=0.0),
            _cyl(clampAxisX, clampCenterY, 0.0, 0.0, 0.0, 1.0, r_axial_lip, zlo, zhi, extra=0.05),
        )
        far_cut = _subtract(
            _annulus(clampOffsetX, clampFarY, 0.0, 0.0, 0.0, 1.0, r_offset, 0.01, zlo, zhi, extra=0.0),
            _cyl(clampAxisX, clampCenterY, 0.0, 0.0, 0.0, 1.0, r_axial_lip, zlo, zhi, extra=0.05),
        )
        return [
            _keep(ring, cx0, 23.50, y_lo, y_hi, z0, z1),
            _keep(ring, 23.35, clampAxisX, y_lo, 2.42, z0, z1),
            _keep(ring, 23.35, clampAxisX, 2.80, y_hi, z0, z1),
            _keep(near_cut, cx0, clampAxisX, 0.9, 2.0, z0, z1),
            _keep(far_cut, cx0, far_xmax, 11.60, 13.19, z0, z1),
        ]

    u0, u1 = clampCornerStart, clampCornerEnd
    v_o = clampCornerOffsetX * _SQ2
    v_c = (halfWidth - rightBottomChamferZ) / _SQ2
    # Run the diagonal mouth through the exterior bevel; a finite stop
    # inside that plane leaves an unsupported skin.
    v_stop = v_c + _OV
    u_bw = -5.35
    dy = clampCenterY - clampCornerNearY
    dist = ((clampCornerAxisX * _SQ2 - v_o) ** 2 + dy * dy) ** 0.5
    y_ledge = clampCornerNearY - r_corner_off
    y_front = clampCornerFarY + r_corner_off
    y_floor = clampCornerNearY - r_corner_off_lip
    y_fledge = clampCornerFarY + r_corner_off_lip
    y_t = r_corner * dy / dist
    y_ct = r_corner_lip * dy / dist
    assert y_floor > y_ledge and y_front > y_fledge, "infeasible: corner ledges must be ordered"

    def c_cyl(y, radius, *, offset=False, lead=0.0):
        ax = clampCornerOffsetX if offset else clampCornerAxisX
        az = clampCornerOffsetZ if offset else clampCornerAxisZ
        return _cyl(ax, y, az, corner_dx, 0.0, corner_dz, radius, u0, u1, extra=lead, extra0=lead)

    disc_corner = _common(
        c_cyl(clampCenterY, r_corner),
        _uv_box(u0 - 0.1, u1 + 0.1, 20.0, v_stop, clampCenterY - y_t, clampCenterY + y_t),
    )
    outer = _fuse_all(
        [
            disc_corner,
            _common(
                c_cyl(clampCornerNearY, r_corner_off, offset=True),
                _uv_box(u0 - 0.2, u1 + 0.2, v_o - 2.0, v_stop, y_ledge - 0.2, y_front + 0.2),
            ),
            _common(
                c_cyl(clampCornerFarY, r_corner_off, offset=True),
                _uv_box(u0 - 0.2, u1 + 0.2, v_o - 2.0, v_stop, y_ledge - 0.2, y_front + 0.2),
            ),
            _uv_box(u0, u1, v_o, v_c + _OV, y_ledge, y_front),
        ]
    )
    boss = _fuse_all(
        [
            _common(
                c_cyl(clampCenterY, r_corner_lip, lead=0.1),
                _uv_box(u0 - 0.2, u1 + 0.2, 20.0, 45.0, clampCenterY - y_ct, clampCenterY + y_ct),
            ),
            c_cyl(clampCornerNearY, r_corner_off_lip, offset=True, lead=0.1),
            c_cyl(clampCornerFarY, r_corner_off_lip, offset=True, lead=0.1),
            _uv_box(u0 - 0.1, u1 + 0.1, v_o, v_stop + 0.12, y_floor, y_fledge),
        ]
    )
    corner_cuts = [
        _subtract(outer, boss),
        _uv_box(u_bw, u1 + 0.12, v_o + 0.5, v_stop, -0.08, 1.30),
        _uv_box(u_bw, u1 + 0.30, v_o + 0.5, v_c + _OV, 1.30, y_floor),
        _common(
            _uv_box(u1 - 0.08, 6.0, v_o + 0.5, v_stop, -0.08, y_floor), _box(15.0, 30.0, -0.12, 3.05, -30.0, -22.5)
        ),
    ]

    tilt_cyl = _cyl(
        clampTiltAxisX,
        clampCenterY,
        clampTiltAxisZ,
        tilt_dx,
        0.0,
        tilt_dz,
        r_relief,
        clampTiltStart,
        clampTiltEnd,
        extra=0.0,
        extra0=0.0,
    )
    relief_cyl = _cyl(
        clampUpperReliefX,
        clampCenterY,
        0.0,
        0.0,
        0.0,
        1.0,
        r_relief,
        0.0,
        clampUpperReliefEnd,
        extra=0.0,
        extra0=0.04,
    )
    wall_n = (0.3368, -0.9397, -0.0594)
    # Join the outer cut to the tangent wall without leaving a sliver.
    y_tan = clampFarY - r_inner * wall_n[1]
    tilt_wall = _common(
        _common(_plane_tool((25.721, 12.259, -8.679), wall_n, depth=2.5), _uv_box(u1, 30.0, 20.0, v_stop, y_tan, y1)),
        _box(15.0, 27.1, -0.1, 14.1, -30.0, -9.0),
    )
    tilt_ext = _subtract(
        _keep(
            _cyl(
                clampTiltAxisX, clampCenterY, clampTiltAxisZ, tilt_dx, 0.0, tilt_dz, 5.70, clampTiltEnd, 0.46, extra=0.0
            ),
            cx0,
            ax1,
            3.5,
            12.7,
            -8.8,
            -4.6,
        ),
        _common(
            _cyl(
                clampOffsetX,
                clampFarY,
                0.0,
                0.0,
                0.0,
                1.0,
                r_far_lip,
                clampFarLipStart,
                clampEndZ,
                extra=0.1,
                extra0=0.0,
            ),
            _box(0.0, 40.0, 7.8, 14.1, -40.0, 40.0),
        ),
    )
    tilt_far = _subtract(
        _keep(
            _cyl(
                clampTiltInnerX,
                clampFarY,
                clampTiltInnerZ,
                tilt_dx,
                0.0,
                tilt_dz,
                r_inner,
                clampTiltFarStart,
                clampTiltFarEnd,
                extra=extra,
            ),
            cx0,
            ax1,
            y0,
            12.26,
            z0,
            z1,
        ),
        _box(22.5, 26.0, 10.5, 13.3, clampStartZ - 0.04, -8.0),
    )

    keep_pivot = _cyl(rightPivotX, 0.0, 0.0, 0.0, 1.0, 0.0, 3.4, -0.05, 14.05, extra=0.0)
    keep_screw = _cyl(upperRightScrewX, 0.0, upperRightScrewZ, 0.0, 1.0, 0.0, 3.4, -0.05, 14.05, extra=0.0)

    guarded = [
        *groove_parts(clampStartZ, -6.0, 25.0),
        _box(24.9, 25.3, 11.55, 12.6, -8.0, -7.0),
        *groove_parts(21.0, clampEndZ, 24.3),
        _box(24.2, 26.6, 11.55, 12.5, 22.0, 23.0),
        _keep(
            _cyl(clampAxisX, clampCenterY, 0.0, 0.0, 0.0, 1.0, r_axial_lip, -6.0, clampEndZ, extra=extra),
            clampAxisX - 0.02,
            ax1,
            4.5,
            9.5,
            -6.15,
            23.98,
        ),
        _keep(
            _cyl(
                clampOffsetX,
                clampFarY,
                0.0,
                0.0,
                0.0,
                1.0,
                r_offset,
                clampStartZ,
                clampFarLipStart,
                extra=extra,
                extra0=0.0,
            ),
            ax0,
            21.3,
            7.9,
            11.2,
            z0,
            z1,
        ),
        _keep(
            _annulus(
                clampOffsetX, clampFarY, 0.0, 0.0, 0.0, 1.0, r_offset, r_far_lip, clampFarLipStart, -6.0, extra=0.0
            ),
            ax0,
            ax1,
            7.9,
            11.2,
            z0,
            z1,
        ),
        _keep(
            _annulus(clampOffsetX, clampFarY, 0.0, 0.0, 0.0, 1.0, r_offset, r_far_lip, 21.0, clampEndZ, extra=0.0),
            ax0,
            ax1,
            7.9,
            11.2,
            z0,
            z1,
        ),
        _keep(
            _cyl(
                clampTiltInnerX,
                clampNearY,
                clampTiltInnerZ,
                tilt_dx,
                0.0,
                tilt_dz,
                r_inner,
                clampTiltNearStart,
                clampTiltNearEnd,
                extra=extra,
            ),
            ax0,
            ax1,
            y0,
            y1,
            z0,
            z1,
        ),
        _keep(
            _cyl(sideScallopX, 0.0, sideScallopZ, 0.0, 1.0, 0.0, r_scallop, 0.0, sideScallopEnd, extra=air),
            20.4,
            32.0,
            -0.05,
            sideScallopEnd + air,
            sideScallopZ - r_scallop - 0.2,
            sideScallopZ + r_scallop + 0.2,
        ),
        _box(23.14, 27.2, -0.05, sideScallopEnd + air, sideScallopZ - r_scallop, sideScallopZ + r_scallop),
        _box(23.14, 26.6, -0.05, 1.78, -22.65, -18.49),
        _box(24.0, 27.20, -0.08, 2.52, -11.59, -4.625),
        _box(26.37, 26.60, -0.08, 2.52, -5.00, -4.50),
        _box(23.59, 24.9, 2.52, 2.731, -6.94, -5.58),
        _box(24.0, 26.55, -0.08, 2.66, 19.625, 21.0),
        _box(23.59, 25.31, 0.88, 2.731, 21.0, 24.0),
        _box(24.0, 26.55, -0.08, 0.88, 21.0, 24.0),
        _box(24.0, 24.28, -0.08, 2.76, 24.00, 25.375),
        # Open the upper rim and slot through the exterior roof.
        _box(24.0, halfWidth + extra, -0.08, 0.88, 24.00, 25.375),
        _box(24.28, halfWidth + extra, 0.88, 2.76, 24.00, 25.375),
        _box(25.14, halfWidth + extra, -0.08, 2.66, 21.0, 24.10),
        _box(24.26, 25.14, 1.45, 1.55, 23.98, 24.12),
        _box(17.80, 19.80, -0.08, 0.65, -25.40, -22.80),
        _box(25.17, 26.55, 11.0, 13.25, -9.0, -6.0),
        _box(25.17, 26.55, 11.0, 13.25, 21.0, 24.0),
        _box(26.12, halfWidth + extra, 1.76, 12.24, -9.18, 23.85),
        _box(23.20, halfWidth - 0.1, 11.62, 12.38, -3.40, 3.40),
        _box(23.20, halfWidth - 0.1, 11.62, 12.38, 15.40, 18.80),
        _box(26.48, 27.70, 12.50, 14.10, -30.05, -23.20),
        # Lower-slot lead-in leaves the crescent as one continuous floor.
        _box(19.20, 19.50, 5.20, 8.80, -9.12, -8.88),
        # Continue the side opening into the lower exterior bevel.
        _box(26.28, 27.70, 11.88, 12.60, -30.10, -26.40),
        # Join the diagonal slot mouth to the back opening.
        _box(21.95, 23.40, 0.80, 2.25, -28.15, -25.80),
        # End the upper slot mouth at the inclined exterior roof.
        _box(24.30, 26.40, 3.45, 5.55, 24.08, 26.40),
    ]
    guarded.extend(
        [
            # Open the side of both slots and the scallop transition into exterior air.
            _box(halfWidth - 0.2, halfWidth + extra, -extra, 3.6, -22.8, clampStartZ + extra),
            _box(halfWidth - 0.2, halfWidth + extra, -extra, 5.55, 21.0 - extra, clampEndZ + extra),
        ]
    )
    # Overlap the lower slot exit with the tilted opening; no isolated side skin.
    guarded.append(_box(26.12, halfWidth + extra, 12.20, 12.28, clampStartZ - 0.18, clampStartZ + extra))
    open_tools = [
        *corner_cuts,
        tilt_wall,
        _keep(
            _cyl(clampOffsetX, clampFarY, 0.0, 0.0, 0.0, 1.0, r_far_lip + 0.02, -8.3, 0.0, extra=0.0),
            clampAxisX - 0.02,
            ax1,
            7.8,
            11.3,
            z0,
            z1,
        ),
        _keep(tilt_cyl, cx0, ax1, 3.5, 10.5, z0, z1),
        _keep(tilt_cyl, cx0, ax1, y0, y_tan, z0, -12.0 + _OV),
        tilt_ext,
        tilt_far,
        _keep(relief_cyl, ax0, ax1, 2.90, 11.10, -0.05, clampUpperReliefEnd),
        # The complete circular exit begins after the last D8 surface.
        _keep(relief_cyl, ax0, ax1, y0, y1, clampUpperFarEnd + extra, clampUpperReliefEnd),
        _keep(relief_cyl, 22.20, 24.30, 2.90, 4.15, 23.80, 27.56),
        _keep(relief_cyl, 22.20, 24.30, 9.20, 11.10, 23.80, 27.56),
        _keep(relief_cyl, 21.55, 23.40, 5.35, 6.70, 23.80, 27.56),
        _keep(relief_cyl, 21.55, 23.40, 7.40, 8.65, 23.80, 27.56),
        _keep(
            _cyl(clampUpperInnerX, clampNearY, 0.0, 0.0, 0.0, 1.0, r_inner, 0.0, clampUpperNearEnd, extra=extra),
            ax0,
            ax1,
            y0,
            y1,
            z0,
            z1,
        ),
        _keep(
            _cyl(clampUpperInnerX, clampFarY, 0.0, 0.0, 0.0, 1.0, r_inner, 0.0, clampUpperFarEnd, extra=extra),
            ax0,
            ax1,
            y0,
            y1,
            z0,
            z1,
        ),
    ]

    # Slot cutters preserve neighbouring fastener walls. The open relief
    # intersects the upper-right counterbore, as required by both sections.
    tools = [_subtract(_subtract(tool, keep_pivot), keep_screw) for tool in guarded]
    tools.extend(open_tools)
    clearance = _fastener_clearance()
    tool = _subtract(_fuse_all(tools), clearance)
    assert tool is not None, "kernel: clamp family misses the region"
    _install_tool(body, tool)
    body.Document.recompute()
    assert body.Shape.isValid(), "kernel: body shape is invalid after clamp"
    removed = original.cut(body.Shape)
    assert removed.Volume > 0.0, "kernel: clamp removed no material"
    # Standard bounds overestimate trimmed oblique cylinders; use OCCT's
    # optimal bounds for the actual finite removed solids.
    box = removed.optimalBoundingBox(False, False)
    assert box.XMin >= 15.0 - 1e-6 and box.XMax <= halfWidth + 1e-6, f"spatial: clamp cut leaves its x region: {box}"
    assert box.YMin >= -1e-6 and box.YMax <= plateThickness + 1e-6, "spatial: clamp cut leaves its y region"
    assert box.ZMin >= bottomZ - 1e-6 and box.ZMax <= bodyTopZ - 0.1 + 1e-6, (
        "spatial: clamp cut reaches the filament region"
    )
    assert body.Shape.cut(original).Volume < 1e-7, "spatial: clamp refilled an existing void"
    assert removed.common(clearance).Volume < 1e-7, "spatial: clamp cut enters fastener face clearance"
    assert len(body.Shape.Solids) == 1, "kernel: clamp must preserve one solid"
    for obj in body.Group:
        if hasattr(obj, "isValid"):
            assert obj.isValid(), "kernel: invalid clamp feature " + obj.Name
    return body
