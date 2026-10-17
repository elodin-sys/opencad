import math

from build123d import (
    Align,
    BuildLine,
    CenterArc,
    Cylinder,
    Polyline,
    Pos,
    extrude,
    make_face,
)

teeth = 24
gearModule = 2.0
pressureAngle = 20.0
profileShift = 0.0
faceWidth = 10.0
toothThinning = 0.1
boreDiameter = 10.0
pitchRadius = teeth * gearModule / 2.0
tipRadius = pitchRadius + gearModule * (1.0 + profileShift)
rootRadius = pitchRadius - gearModule * (1.25 - profileShift)
baseRadius = pitchRadius * math.cos(math.radians(pressureAngle))
toothThickness = math.pi * gearModule / 2.0 - toothThinning
flankPoints = 14

assert faceWidth > 0, "infeasible: faceWidth must be positive"
assert toothThickness > 0, "infeasible: tooth thickness must be positive"
assert boreDiameter > 0, "infeasible: boreDiameter must be positive"
assert rootRadius > boreDiameter / 2.0, "infeasible: bore must fit inside the root circle"
assert tipRadius > baseRadius > rootRadius > 0, "infeasible: root, base and tip radii are out of order"
assert flankPoints >= 2, "infeasible: flankPoints must be at least 2"

_pressure = math.radians(pressureAngle)
_inv_pressure = math.tan(_pressure) - _pressure
_half_pitch_angle = toothThickness / (2.0 * pitchRadius)


def _psi(radius):
    # Below the base circle the flank is radial, so the half-angle stays at the base value.
    if radius <= baseRadius:
        return _half_pitch_angle + _inv_pressure
    alpha = math.acos(baseRadius / radius)
    return _half_pitch_angle + _inv_pressure - (math.tan(alpha) - alpha)


_psi_root = _psi(rootRadius)
_psi_tip = _psi(tipRadius)
_tooth_pitch = 2.0 * math.pi / int(teeth)
assert _psi_tip > 0, "infeasible: tip land has closed"
assert 2.0 * _psi_root < _tooth_pitch, "infeasible: adjacent teeth overlap at the root"


def _polar(radius, angle):
    return (radius * math.cos(angle), radius * math.sin(angle))


def _flank_radii():
    count = int(flankPoints)
    span = tipRadius - baseRadius
    radii = [baseRadius + i * span / (count - 1) for i in range(count)]
    radii[0] = baseRadius
    radii[-1] = tipRadius
    return radii


def _profile_wire():
    radii = _flank_radii()
    with BuildLine() as profile:
        for k in range(int(teeth)):
            center = k * _tooth_pitch
            left = [_polar(rootRadius, center - _psi_root)]
            left.extend(_polar(radius, center - _psi(radius)) for radius in radii)
            Polyline(*left)
            CenterArc(
                (0, 0),
                tipRadius,
                math.degrees(center - _psi_tip),
                math.degrees(2.0 * _psi_tip),
            )
            right = [_polar(radius, center + _psi(radius)) for radius in reversed(radii)]
            right.append(_polar(rootRadius, center + _psi_root))
            Polyline(*right)
            next_center = (k + 1) * _tooth_pitch
            CenterArc(
                (0, 0),
                rootRadius,
                math.degrees(center + _psi_root),
                math.degrees(next_center - center - 2.0 * _psi_root),
            )
    return profile.wire()


_blank = extrude(make_face(_profile_wire()), faceWidth)
_cutter = Pos(0, 0, -0.02) * Cylinder(
    boreDiameter / 2.0,
    faceWidth + 0.04,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = _blank - _cutter
