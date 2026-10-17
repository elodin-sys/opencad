"""sprite-drone-cam-mount-l: left camera mount (camMountL)."""

from __future__ import annotations

import math

from build123d import (
    Align,
    Axis,
    Box,
    Circle,
    Cylinder,
    GeomType,
    Location,
    Plane,
    Polyline,
    Pos,
    Rot,
    ShapeList,
    Sphere,
    ThreePointArc,
    extrude,
    fillet,
    make_face,
    make_hull,
    revolve,
)

# --- contract parameters (exact names / values) ---
glueFaceX = 10.0
plateThickness = 2.0
hubRadius = 6.0
leverTipRadius = 2.5
pinAxisY = -5.205
pinAxisZ = 244.5275
pinDiameter = 4.0
pinLength = 4.0
pinTipRadius = 0.5
linkHoleY = -14.965
linkHoleZ = 236.338
linkHoleDiameter = 1.5
bossHeight = 1.0
bossFilletRadius = 1.0
edgeFilletRadius = 1.0

# --- invariants ---
_dy = linkHoleY - pinAxisY
_dz = linkHoleZ - pinAxisZ
_lever_arm = math.hypot(_dy, _dz)
assert hubRadius >= 3.0, "infeasible: hubRadius must be >= 3.0"
assert hubRadius < _lever_arm + leverTipRadius, "infeasible: hubRadius too large for lever arm"
assert bossHeight >= 1.0, "infeasible: bossHeight must be >= 1.0"
assert pinDiameter > 0.0, "infeasible: pinDiameter must be positive"
assert linkHoleDiameter > 0.0, "infeasible: linkHoleDiameter must be positive"
assert pinTipRadius > 0.0 and pinTipRadius < pinDiameter / 2.0, "infeasible: pinTipRadius"
assert bossFilletRadius > 0.0, "infeasible: bossFilletRadius must be positive"
assert edgeFilletRadius > 0.0, "infeasible: edgeFilletRadius must be positive"
assert plateThickness > 0.0, "infeasible: plateThickness must be positive"
assert pinLength > 0.0, "infeasible: pinLength must be positive"

_pin_r = pinDiameter / 2.0
_hole_r = linkHoleDiameter / 2.0
_plate_face_x = glueFaceX + plateThickness
_tip_x = _plate_face_x + pinLength
_alpha = math.asin((hubRadius - leverTipRadius) / _lever_arm)
_fillet_stop = math.sqrt(max(2.0 * leverTipRadius * edgeFilletRadius - edgeFilletRadius**2, 0.0))


def _samples(edge):
    return [edge @ t for t in (0.0, 0.25, 0.5, 0.75, 1.0)]


def _on_plane_x(edge, x: float, tol: float = 0.06) -> bool:
    return all(abs(p.X - x) < tol for p in _samples(edge))


def _about_axis(edge, y0: float, z0: float, r: float, tol: float = 0.08) -> bool:
    return all(abs(math.hypot(p.Y - y0, p.Z - z0) - r) < tol for p in _samples(edge))


_hub = Pos(pinAxisY, pinAxisZ) * Circle(hubRadius)
_tip = Pos(linkHoleY, linkHoleZ) * Circle(leverTipRadius)
_local_face = make_face(make_hull([_hub.edges(), _tip.edges()]))
_to_world = Plane(origin=(glueFaceX, 0.0, 0.0), x_dir=(0.0, 1.0, 0.0), z_dir=(1.0, 0.0, 0.0))
plate = _to_world * extrude(_local_face, amount=plateThickness)

_flanks = [
    e for e in plate.edges() if _on_plane_x(e, _plate_face_x) and e.geom_type == GeomType.LINE and e.length > 5.0
]

# Tip-stop notches so OCC hub fillet (which G1-propagates into the flanks)
# stops short of the tip tangents — matching the reference's stopped flank round.
_notches = []
_tip_pts = []
for _e in _flanks:
    _p0, _p1 = _e @ 0.0, _e @ 1.0
    if math.hypot(_p0.Y - linkHoleY, _p0.Z - linkHoleZ) < math.hypot(_p1.Y - linkHoleY, _p1.Z - linkHoleZ):
        _tip_p, _hub_p = _p0, _p1
    else:
        _tip_p, _hub_p = _p1, _p0
    _tip_pts.append(_tip_p)
    _vy, _vz = _hub_p.Y - _tip_p.Y, _hub_p.Z - _tip_p.Z
    _L = math.hypot(_vy, _vz)
    _uy, _uz = _vy / _L, _vz / _L
    _cy = _tip_p.Y + _uy * (_fillet_stop * 0.35)
    _cz = _tip_p.Z + _uz * (_fillet_stop * 0.35)
    _pln = Plane(
        origin=(glueFaceX - 0.05, _cy, _cz),
        x_dir=(1.0, 0.0, 0.0),
        y_dir=(0.0, _uy, _uz),
    )
    _notches.append(
        _pln
        * Box(
            plateThickness + 0.2,
            0.12,
            2.0 * edgeFilletRadius + 0.6,
            align=(Align.MIN, Align.CENTER, Align.CENTER),
        )
    )
plate = plate - (_notches[0] + _notches[1])

_hub_edges = ShapeList(
    e
    for e in plate.edges()
    if _on_plane_x(e, _plate_face_x)
    and e.geom_type == GeomType.CIRCLE
    and _about_axis(e, pinAxisY, pinAxisZ, hubRadius, tol=0.2)
)
plate = fillet(_hub_edges, edgeFilletRadius)
# Restore the tip as a clean disk (not the notch remnant) so the boss-root
# blend and tip-corner balls can meet the edge round without a seam void.
_tip_disk = _to_world * extrude(make_face(Pos(linkHoleY, linkHoleZ) * Circle(leverTipRadius)), amount=plateThickness)
plate = plate + _tip_disk

boss = (
    Location((_plate_face_x, linkHoleY, linkHoleZ))
    * Rot(0.0, 90.0, 0.0)
    * Cylinder(leverTipRadius, bossHeight, align=(Align.CENTER, Align.CENTER, Align.MIN))
)
body = plate + boss

_bf = bossFilletRadius
_R = leverTipRadius
_face2d = make_face(
    [
        Polyline((0.0, _R), (0.0, _R + _bf)),
        ThreePointArc(
            (0.0, _R + _bf),
            (_bf - _bf * math.cos(math.pi / 4.0), (_R + _bf) - _bf * math.sin(math.pi / 4.0)),
            (_bf, _R),
        ),
        Polyline((_bf, _R), (0.0, _R)),
    ]
)
_ry = (pinAxisY - linkHoleY) / _lever_arm
_rz = (pinAxisZ - linkHoleZ) / _lever_arm
_bpln = Plane(
    origin=(_plate_face_x, linkHoleY, linkHoleZ),
    x_dir=(1.0, 0.0, 0.0),
    y_dir=(0.0, _ry, _rz),
)
_baxis = Axis((_plate_face_x, linkHoleY, linkHoleZ), (1.0, 0.0, 0.0))
_blend = revolve(_bpln * _face2d, _baxis, 360.0)
_clip = _to_world * extrude(_local_face, amount=plateThickness + bossFilletRadius + 0.05)
body = body + (_blend & _clip)

# Tip-tangent corner balls: plate-face convex round meets boss-root concave fillet.
for _tp in _tip_pts:
    _ny = (_tp.Y - linkHoleY) / leverTipRadius
    _nz = (_tp.Z - linkHoleZ) / leverTipRadius
    _cy = _tp.Y - _ny * edgeFilletRadius
    _cz = _tp.Z - _nz * edgeFilletRadius
    body = body + (Location((_plate_face_x - edgeFilletRadius, _cy, _cz)) * Sphere(edgeFilletRadius) & _clip)
    body = body + (Location((_plate_face_x, _cy, _cz)) * Sphere(edgeFilletRadius) & _clip)

pin = (
    Location((_plate_face_x, pinAxisY, pinAxisZ))
    * Rot(0.0, 90.0, 0.0)
    * Cylinder(_pin_r, pinLength, align=(Align.CENTER, Align.CENTER, Align.MIN))
)
body = body + pin
_pin_tip_edges = ShapeList(
    e
    for e in body.edges().filter_by(GeomType.CIRCLE)
    if _on_plane_x(e, _tip_x) and _about_axis(e, pinAxisY, pinAxisZ, _pin_r)
)
assert len(_pin_tip_edges) >= 1, "pin tip circle not found"
body = fillet(_pin_tip_edges, pinTipRadius)

_hole = (
    Location((glueFaceX - 0.05, linkHoleY, linkHoleZ))
    * Rot(0.0, 90.0, 0.0)
    * Cylinder(
        _hole_r,
        plateThickness + bossHeight + 0.1,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
)
result = body - _hole
