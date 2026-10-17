import math

import cadquery as cq

gearModule = 2.0
pressureAngle = 20.0
profileShift = 0.0
pinionTeeth = 20.0
wheelTeeth = 40.0
pinionBoreDiameter = 6.0
wheelBoreDiameter = 8.0
centerDistance = 60.0
gearFaceWidth = 8.0
addendumFactor = 1.0
dedendumFactor = 1.25
totalBacklash = 0.1
pinionPhase = 0.0
pinionAxisX = 0.0
pinionAxisY = 0.0
wheelAxisY = 0.0
gearBaseZ = 0.0
carrierLength = 110.0
carrierWidth = 50.0
carrierThickness = 5.0
carrierMinX = -25.0
carrierMinY = -25.0
wheelPhase = 4.5

assert gearModule > 0, "infeasible: gearModule must be positive"
assert 0 < pressureAngle < 90, "infeasible: pressureAngle must be between 0 and 90"
assert pinionTeeth >= 3, "infeasible: at least three pinion teeth are required"
assert wheelTeeth >= 3, "infeasible: at least three wheel teeth are required"
assert abs(pinionTeeth - math.floor(pinionTeeth)) < 1e-9, "infeasible: pinionTeeth must be an integer"
assert abs(wheelTeeth - math.floor(wheelTeeth)) < 1e-9, "infeasible: wheelTeeth must be an integer"
assert pinionBoreDiameter > 0, "infeasible: pinionBoreDiameter must be positive"
assert wheelBoreDiameter > 0, "infeasible: wheelBoreDiameter must be positive"
assert centerDistance > 0, "infeasible: centerDistance must be positive"
assert gearFaceWidth > 0, "infeasible: gearFaceWidth must be positive"
assert addendumFactor + profileShift > 0, "infeasible: effective addendum must be positive"
assert dedendumFactor - profileShift > 0, "infeasible: effective dedendum must be positive"
assert totalBacklash >= 0, "infeasible: totalBacklash must be nonnegative"
assert carrierLength > 0, "infeasible: carrierLength must be positive"
assert carrierWidth > 0, "infeasible: carrierWidth must be positive"
assert carrierThickness > 0, "infeasible: carrierThickness must be positive"
assert abs(pinionPhase) < 1e6, "infeasible: pinionPhase must be finite"
assert abs(wheelPhase) < 1e6, "infeasible: wheelPhase must be finite"

_alpha = math.radians(pressureAngle)
_tooth_thickness = math.pi * gearModule / 2.0 + 2.0 * gearModule * profileShift * math.tan(_alpha) - totalBacklash / 2.0
assert _tooth_thickness > 0, "infeasible: totalBacklash erases tooth thickness"


def _polar(radius, theta):
    return (radius * math.cos(theta), radius * math.sin(theta))


def _involute_xy(t, h0, base, tooth_angle, side):
    h = h0 - t + math.atan(t)
    theta = tooth_angle + side * h
    radius = base * math.sqrt(1.0 + t * t)
    return (radius * math.cos(theta), radius * math.sin(theta))


def _t_samples(t_root, t_pitch, t_tip, half=10):
    ts = [t_root + (t_pitch - t_root) * i / half for i in range(half + 1)]
    ts.extend(t_pitch + (t_tip - t_pitch) * i / half for i in range(1, half + 1))
    return ts


def _arc_xy(radius, a0, a1, segments):
    span = a1 - a0
    if span <= 0.0:
        span += 2.0 * math.pi
    return [_polar(radius, a0 + span * i / segments) for i in range(segments + 1)]


def _dedupe(pts, eps=1e-9):
    out = []
    for p in pts:
        if not out or (p[0] - out[-1][0]) ** 2 + (p[1] - out[-1][1]) ** 2 > eps * eps:
            out.append(p)
    if len(out) > 1 and (out[0][0] - out[-1][0]) ** 2 + (out[0][1] - out[-1][1]) ** 2 <= eps * eps:
        out.pop()
    return out


def _gear_invariants(teeth, bore):
    pitch = gearModule * teeth / 2.0
    base = pitch * math.cos(_alpha)
    tip = pitch + gearModule * (addendumFactor + profileShift)
    root = pitch - gearModule * (dedendumFactor - profileShift)
    h0 = _tooth_thickness / (2.0 * pitch) + math.tan(_alpha) - _alpha
    t_root = math.sqrt(max(0.0, (root / base) ** 2 - 1.0))
    t_pitch = math.tan(_alpha)
    t_tip = math.sqrt((tip / base) ** 2 - 1.0)
    h_root = h0 - t_root + math.atan(t_root)
    h_tip = h0 - t_tip + math.atan(t_tip)
    assert root > bore / 2.0, "infeasible: bore leaves no root web"
    assert tip > pitch > root, "infeasible: tip/pitch/root order is inverted"
    assert base > 0, "infeasible: base radius must be positive"
    assert h_tip > 0, "infeasible: backlash or shift erased the tooth tip"
    assert h_root < math.pi / teeth, "infeasible: tooth root closes the adjacent tooth space"
    assert t_pitch > t_root, "infeasible: root-to-pitch involute interval is degenerate"
    assert t_tip > t_pitch, "infeasible: pitch-to-tip involute interval is degenerate"
    return pitch, base, tip, root, h0, t_root, t_pitch, t_tip, h_root, h_tip


def _gear_outline(teeth, phase_deg):
    _pitch, base, tip, root, h0, t_root, t_pitch, t_tip, h_root, _h_tip = _gear_invariants(teeth, 0.0)
    ts = _t_samples(t_root, t_pitch, t_tip)
    phase = math.radians(phase_deg)
    step = 2.0 * math.pi / teeth
    pts = []
    tooth = 0.0
    while tooth < teeth:
        mid = phase + tooth * step
        if root < base:
            pts.append(_polar(root, mid - h_root))
        pts.extend(_involute_xy(t, h0, base, mid, -1.0) for t in ts)
        tip_arc = _arc_xy(tip, mid - (h0 - t_tip + math.atan(t_tip)), mid + (h0 - t_tip + math.atan(t_tip)), 8)
        pts.extend(tip_arc[1:])
        pts.extend(_involute_xy(t, h0, base, mid, 1.0) for t in reversed(ts[:-1]))
        if root < base:
            pts.append(_polar(root, mid + h_root))
        pts.extend(_arc_xy(root, mid + h_root, mid + step - h_root, 8)[1:])
        tooth += 1.0
    return _dedupe(pts)


def _bore_tool(axis_x, axis_y, z0, height, diameter):
    return cq.Workplane("XY", origin=(axis_x, axis_y, z0 - 0.05)).circle(diameter / 2.0).extrude(height + 0.10)


def _gear_solid(teeth, bore, axis_x, axis_y, phase_deg):
    _gear_invariants(teeth, bore)
    pts = _gear_outline(teeth, phase_deg)
    assert len(pts) > 16, "infeasible: gear outline collapsed"
    blank = (
        cq.Workplane("XY", origin=(axis_x, axis_y, gearBaseZ))
        .moveTo(pts[0][0], pts[0][1])
        .polyline(pts[1:], includeCurrent=True)
        .close()
        .extrude(gearFaceWidth)
    )
    return blank.cut(_bore_tool(axis_x, axis_y, gearBaseZ, gearFaceWidth, bore), clean=True)


_gear_invariants(pinionTeeth, pinionBoreDiameter)
_gear_invariants(wheelTeeth, wheelBoreDiameter)
assert pinionAxisX - pinionBoreDiameter / 2.0 > carrierMinX, "infeasible: pinion hole breaks carrier left wall"
assert pinionAxisX + pinionBoreDiameter / 2.0 < carrierMinX + carrierLength, (
    "infeasible: pinion hole breaks carrier right wall"
)
assert pinionAxisY - pinionBoreDiameter / 2.0 > carrierMinY, "infeasible: pinion hole breaks carrier front wall"
assert pinionAxisY + pinionBoreDiameter / 2.0 < carrierMinY + carrierWidth, (
    "infeasible: pinion hole breaks carrier back wall"
)
assert pinionAxisX + centerDistance - wheelBoreDiameter / 2.0 > carrierMinX, (
    "infeasible: wheel hole breaks carrier left wall"
)
assert pinionAxisX + centerDistance + wheelBoreDiameter / 2.0 < carrierMinX + carrierLength, (
    "infeasible: wheel hole breaks carrier right wall"
)
assert wheelAxisY - wheelBoreDiameter / 2.0 > carrierMinY, "infeasible: wheel hole breaks carrier front wall"
assert wheelAxisY + wheelBoreDiameter / 2.0 < carrierMinY + carrierWidth, (
    "infeasible: wheel hole breaks carrier back wall"
)

carrier_blank = (
    cq.Workplane("XY", origin=(0.0, 0.0, gearBaseZ))
    .moveTo(carrierMinX, carrierMinY)
    .rect(carrierLength, carrierWidth, centered=False)
    .extrude(-carrierThickness)
)
carrier_bores = _bore_tool(
    pinionAxisX, pinionAxisY, gearBaseZ - carrierThickness, carrierThickness, pinionBoreDiameter
).union(
    _bore_tool(
        pinionAxisX + centerDistance, wheelAxisY, gearBaseZ - carrierThickness, carrierThickness, wheelBoreDiameter
    )
)
carrier = carrier_blank.cut(carrier_bores, clean=True)

pinion = _gear_solid(pinionTeeth, pinionBoreDiameter, pinionAxisX, pinionAxisY, pinionPhase)
wheel = _gear_solid(wheelTeeth, wheelBoreDiameter, pinionAxisX + centerDistance, wheelAxisY, wheelPhase)
result = [pinion, wheel, carrier]
