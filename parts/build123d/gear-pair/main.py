import math

from build123d import (
    Align,
    Circle,
    Line,
    Pos,
    Rectangle,
    ThreePointArc,
    extrude,
    make_face,
)

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

assert math.isfinite(gearModule), "infeasible: gearModule must be finite"
assert math.isfinite(pressureAngle), "infeasible: pressureAngle must be finite"
assert math.isfinite(profileShift), "infeasible: profileShift must be finite"
assert math.isfinite(pinionTeeth), "infeasible: pinionTeeth must be finite"
assert math.isfinite(wheelTeeth), "infeasible: wheelTeeth must be finite"
assert math.isfinite(totalBacklash), "infeasible: totalBacklash must be finite"
assert gearModule > 0, "infeasible: gearModule must be positive"
assert 0 < pressureAngle < 90, "infeasible: pressureAngle must be between 0 and 90 deg"
assert pinionBoreDiameter > 0, "infeasible: pinionBoreDiameter must be positive"
assert wheelBoreDiameter > 0, "infeasible: wheelBoreDiameter must be positive"
assert centerDistance > 0, "infeasible: centerDistance must be positive"
assert gearFaceWidth > 0, "infeasible: gearFaceWidth must be positive"
assert addendumFactor + profileShift > 0, "infeasible: effective addendum must be positive"
assert dedendumFactor - profileShift > 0, "infeasible: effective dedendum must be positive"
assert totalBacklash >= 0, "infeasible: backlash must be nonnegative"
assert pinionTeeth >= 3, "infeasible: at least three pinion teeth are required"
assert wheelTeeth >= 3, "infeasible: at least three wheel teeth are required"
assert abs(pinionTeeth - round(pinionTeeth)) < 1e-8, "infeasible: pinionTeeth must be an integer"
assert abs(wheelTeeth - round(wheelTeeth)) < 1e-8, "infeasible: wheelTeeth must be an integer"
assert carrierLength > 0, "infeasible: carrierLength must be positive"
assert carrierWidth > 0, "infeasible: carrierWidth must be positive"
assert carrierThickness > 0, "infeasible: carrierThickness must be positive"
assert math.isfinite(pinionPhase), "infeasible: pinionPhase must be finite"
assert math.isfinite(wheelPhase), "infeasible: wheelPhase must be finite"
assert math.isfinite(pinionAxisX), "infeasible: pinionAxisX must be finite"
assert math.isfinite(pinionAxisY), "infeasible: pinionAxisY must be finite"
assert math.isfinite(wheelAxisY), "infeasible: wheelAxisY must be finite"
assert math.isfinite(gearBaseZ), "infeasible: gearBaseZ must be finite"
assert math.isfinite(carrierMinX), "infeasible: carrierMinX must be finite"
assert math.isfinite(carrierMinY), "infeasible: carrierMinY must be finite"

_alpha = math.radians(pressureAngle)
_tooth_thickness = math.pi * gearModule / 2.0 + 2.0 * gearModule * profileShift * math.tan(_alpha) - totalBacklash / 2.0
assert _tooth_thickness > 0, "infeasible: circular tooth thickness must be positive"


def _polar(radius, theta):
    return (radius * math.cos(theta), radius * math.sin(theta))


def _involute_xy(t, h0, rb, tooth_phase, side):
    h = h0 - t + math.atan(t)
    return _polar(rb * math.sqrt(1.0 + t * t), tooth_phase + side * h)


def _gear_data(n_teeth, bore):
    pitch = gearModule * n_teeth / 2.0
    base = pitch * math.cos(_alpha)
    tip = pitch + gearModule * (addendumFactor + profileShift)
    root = pitch - gearModule * (dedendumFactor - profileShift)
    assert root > bore / 2.0, "infeasible: bore must leave a positive root web"
    assert root < pitch < tip, "infeasible: root, pitch and tip radii are out of order"
    assert base > 0, "infeasible: base radius must be positive"
    h0 = _tooth_thickness / (2.0 * pitch) + math.tan(_alpha) - _alpha
    t_root = math.sqrt(max(0.0, (root / base) ** 2 - 1.0))
    t_pitch = math.tan(_alpha)
    t_tip = math.sqrt((tip / base) ** 2 - 1.0)
    h_root = h0 - t_root + math.atan(t_root)
    h_tip = h0 - t_tip + math.atan(t_tip)
    assert h_tip > 0, "infeasible: backlash or shift erased the tooth tip"
    assert h_root < math.pi / n_teeth, "infeasible: tooth root closes the adjacent tooth space"
    assert t_pitch - t_root > 1e-8, "infeasible: root-to-pitch fitting interval is degenerate"
    assert t_tip - t_pitch > 1e-8, "infeasible: pitch-to-tip fitting interval is degenerate"
    return {
        "pitch": pitch,
        "base": base,
        "tip": tip,
        "root": root,
        "h0": h0,
        "t_root": t_root,
        "t_pitch": t_pitch,
        "t_tip": t_tip,
        "h_root": h_root,
        "h_tip": h_tip,
    }


def _t_samples(g):
    ts = []
    for i in range(7):
        ts.append(g["t_root"] + (g["t_pitch"] - g["t_root"]) * i / 6.0)
    for i in range(1, 7):
        ts.append(g["t_pitch"] + (g["t_tip"] - g["t_pitch"]) * i / 6.0)
    return ts


def _involute_arcs(ts, g, phi, side):
    edges = []
    for i in range(len(ts) - 1):
        t0, t1 = ts[i], ts[i + 1]
        tm = 0.5 * (t0 + t1)
        edges.append(
            ThreePointArc(
                _involute_xy(t0, g["h0"], g["base"], phi, side),
                _involute_xy(tm, g["h0"], g["base"], phi, side),
                _involute_xy(t1, g["h0"], g["base"], phi, side),
            )
        )
    return edges


def _gear_profile(n_teeth, bore, phase_deg):
    g = _gear_data(n_teeth, bore)
    n = round(n_teeth)
    phase = math.radians(phase_deg)
    da = 2.0 * math.pi / n_teeth
    ts = _t_samples(g)
    ts_rev = list(reversed(ts))
    edges = []
    for i in range(n):
        phi = phase + i * da
        if g["root"] < g["base"]:
            edges.append(
                Line(
                    _polar(g["root"], phi - g["h_root"]),
                    _involute_xy(g["t_root"], g["h0"], g["base"], phi, -1.0),
                )
            )
        edges.extend(_involute_arcs(ts, g, phi, -1.0))
        edges.append(
            ThreePointArc(
                _involute_xy(g["t_tip"], g["h0"], g["base"], phi, -1.0),
                _polar(g["tip"], phi),
                _involute_xy(g["t_tip"], g["h0"], g["base"], phi, 1.0),
            )
        )
        edges.extend(_involute_arcs(ts_rev, g, phi, 1.0))
        if g["root"] < g["base"]:
            edges.append(
                Line(
                    _involute_xy(g["t_root"], g["h0"], g["base"], phi, 1.0),
                    _polar(g["root"], phi + g["h_root"]),
                )
            )
        edges.append(
            ThreePointArc(
                _polar(g["root"], phi + g["h_root"]),
                _polar(g["root"], phi + da / 2.0),
                _polar(g["root"], phi + da - g["h_root"]),
            )
        )
    return make_face(edges) - Circle(bore / 2.0)


def _gear_solid(n_teeth, bore, phase_deg, axis_x, axis_y):
    return Pos(axis_x, axis_y, gearBaseZ) * extrude(
        _gear_profile(n_teeth, bore, phase_deg),
        amount=gearFaceWidth,
    )


_pinion_data = _gear_data(pinionTeeth, pinionBoreDiameter)
_wheel_data = _gear_data(wheelTeeth, wheelBoreDiameter)
_wheel_axis_x = pinionAxisX + centerDistance
for _ax, _ay, _rad in (
    (pinionAxisX, pinionAxisY, pinionBoreDiameter / 2.0),
    (_wheel_axis_x, wheelAxisY, wheelBoreDiameter / 2.0),
):
    assert _ax - _rad > carrierMinX, "infeasible: hole breaks carrier left wall"
    assert _ax + _rad < carrierMinX + carrierLength, "infeasible: hole breaks carrier right wall"
    assert _ay - _rad > carrierMinY, "infeasible: hole breaks carrier front wall"
    assert _ay + _rad < carrierMinY + carrierWidth, "infeasible: hole breaks carrier back wall"
_shaft = math.hypot(centerDistance, wheelAxisY - pinionAxisY)
assert _shaft > (pinionBoreDiameter + wheelBoreDiameter) / 2.0, "infeasible: carrier holes overlap"
assert _shaft - _pinion_data["tip"] - _wheel_data["root"] > 0.002, "infeasible: pinion tip collides with wheel root"
assert _shaft - _wheel_data["tip"] - _pinion_data["root"] > 0.002, "infeasible: wheel tip collides with pinion root"
assert _shaft > _pinion_data["base"] + _wheel_data["base"], "infeasible: no real working pressure angle"
_working = math.acos((_pinion_data["base"] + _wheel_data["base"]) / _shaft)
_path = (
    math.sqrt(_pinion_data["tip"] ** 2 - _pinion_data["base"] ** 2)
    + math.sqrt(_wheel_data["tip"] ** 2 - _wheel_data["base"] ** 2)
    - _shaft * math.sin(_working)
)
assert _path / (math.pi * gearModule * math.cos(_alpha)) > 1.0, "infeasible: contact ratio must exceed one"

carrier_face = (
    Pos(carrierMinX, carrierMinY) * Rectangle(carrierLength, carrierWidth, align=(Align.MIN, Align.MIN))
    - Pos(pinionAxisX, pinionAxisY) * Circle(pinionBoreDiameter / 2.0)
    - Pos(_wheel_axis_x, wheelAxisY) * Circle(wheelBoreDiameter / 2.0)
)
carrier = Pos(0.0, 0.0, gearBaseZ) * extrude(carrier_face, amount=-carrierThickness)
pinion = _gear_solid(pinionTeeth, pinionBoreDiameter, pinionPhase, pinionAxisX, pinionAxisY)
wheel = _gear_solid(wheelTeeth, wheelBoreDiameter, wheelPhase, _wheel_axis_x, wheelAxisY)
result = [pinion, wheel, carrier]
