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

toothCount = 20.0
gearModule = 2.0
pressureAngle = 20.0
profileShift = 0.0
addendumCoeff = 1.0
dedendumCoeff = 1.25
faceWidth = 8.0
boreDiameter = 6.0
backlashThinning = 0.05
flankSamples = 14.0
pitchRadius = toothCount * gearModule / 2.0
baseRadius = pitchRadius * math.cos(math.radians(pressureAngle))
tipRadius = pitchRadius + (addendumCoeff + profileShift) * gearModule
rootRadius = pitchRadius - (dedendumCoeff - profileShift) * gearModule
pitchToothThickness = (
    math.pi * gearModule / 2.0
    + 2.0 * profileShift * gearModule * math.tan(math.radians(pressureAngle))
    - backlashThinning
)

assert faceWidth > 0.0, "infeasible: faceWidth must be positive"
assert boreDiameter > 0.0, "infeasible: boreDiameter must be positive"
assert boreDiameter < 2.0 * rootRadius, "infeasible: bore does not fit inside the root circle"
assert flankSamples >= 2.0, "infeasible: flankSamples must include the base and the tip"
assert tipRadius > baseRadius, "infeasible: tip circle must lie outside the base circle"


def _involute(phi):
    return math.tan(phi) - phi


pressure_rad = math.radians(pressureAngle)
psi_b = pitchToothThickness / (2.0 * pitchRadius) + _involute(pressure_rad)
phi_tip = math.acos(baseRadius / tipRadius)
psi_tip = psi_b - _involute(phi_tip)
assert psi_tip > 0.0, "infeasible: backlashThinning points the tooth tip"
tooth_pitch = 2.0 * math.pi / toothCount
assert tooth_pitch > 2.0 * psi_b, "infeasible: adjacent teeth overlap at the root"


def _polar(radius, angle):
    return (radius * math.cos(angle), radius * math.sin(angle))


n_teeth = round(toothCount)
n_flank = round(flankSamples)
roll_tip = math.sqrt((tipRadius / baseRadius) ** 2.0 - 1.0)
flank = []
for sample_index in range(n_flank):
    roll = roll_tip * sample_index / (n_flank - 1)
    radius = baseRadius * math.sqrt(1.0 + roll * roll)
    psi = psi_b - (roll - math.atan(roll))
    flank.append((radius, psi))
flank[0] = (baseRadius, psi_b)
flank[-1] = (tipRadius, psi_tip)

with BuildLine() as outline:
    for tooth_index in range(n_teeth):
        center = tooth_index * tooth_pitch
        left = [_polar(rootRadius, center - psi_b)]
        left += [_polar(radius, center - psi) for radius, psi in flank]
        Polyline(*left)
        CenterArc(
            (0.0, 0.0),
            tipRadius,
            math.degrees(center - psi_tip),
            math.degrees(2.0 * psi_tip),
        )
        right = [_polar(radius, center + psi) for radius, psi in reversed(flank)]
        right.append(_polar(rootRadius, center + psi_b))
        Polyline(*right)
        root_start = center + psi_b
        root_end = (tooth_index + 1) * tooth_pitch - psi_b
        CenterArc(
            (0.0, 0.0),
            rootRadius,
            math.degrees(root_start),
            math.degrees(root_end - root_start),
        )

blank = extrude(make_face(outline.wire()), amount=faceWidth)
cutter = Pos(0.0, 0.0, -0.05) * Cylinder(
    boreDiameter / 2.0,
    faceWidth + 0.1,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = blank - cutter
