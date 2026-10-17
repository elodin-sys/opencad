import math

from build123d import (
    Align,
    BuildLine,
    BuildSketch,
    CenterArc,
    Cylinder,
    Polyline,
    Pos,
    extrude,
    make_face,
)

gearModule = 2.0
toothCount = 20
pressureAngle = 20.0
pitchRadius = gearModule * toothCount / 2
tipRadius = pitchRadius + gearModule
rootRadius = pitchRadius - 1.25 * gearModule
baseRadius = pitchRadius * math.cos(math.radians(pressureAngle))
circularPitch = math.pi * gearModule
toothThinning = 0.05
toothThickness = circularPitch / 2 - toothThinning
faceWidth = 8.0
boreDiameter = 6.0
flankPoints = 14

assert faceWidth > 0, "infeasible: faceWidth must be positive"
assert boreDiameter > 0, "infeasible: boreDiameter must be positive"
assert gearModule > 0, "infeasible: gearModule must be positive"
assert toothCount >= 3, "infeasible: toothCount must be at least 3"
assert 0 < pressureAngle < 90, "infeasible: pressureAngle must be between 0 and 90 deg"
assert toothThickness > 0, "infeasible: toothThickness must be positive"
assert flankPoints >= 2, "infeasible: flankPoints must be at least 2"
assert rootRadius > boreDiameter / 2, "infeasible: bore does not fit inside the root circle"
assert tipRadius > baseRadius > rootRadius > 0, "infeasible: tip, base and root radii are out of order"


def _polar(radius, angle):
    return (radius * math.cos(angle), radius * math.sin(angle))


pressure_rad = math.radians(pressureAngle)
psi_pitch = toothThickness / (2 * pitchRadius)
psi_b = psi_pitch + math.tan(pressure_rad) - pressure_rad
phi_tip = math.acos(baseRadius / tipRadius)
roll_tip = math.tan(phi_tip)
psi_tip = psi_b - (roll_tip - math.atan(roll_tip))
tooth_pitch = 2 * math.pi / toothCount

assert psi_tip > 0, "infeasible: tooth tip half-angle is not positive"
assert tooth_pitch > 2 * psi_b, "infeasible: neighbouring teeth overlap at the root"

point_count = int(flankPoints)

with BuildSketch() as gear_sketch:
    with BuildLine():
        for tooth_index in range(int(toothCount)):
            center = tooth_index * tooth_pitch
            left = [_polar(rootRadius, center - psi_b)]
            right = []
            for sample in range(point_count):
                t_out = roll_tip * sample / (point_count - 1)
                t_in = roll_tip * (point_count - 1 - sample) / (point_count - 1)
                half_out = psi_b - (t_out - math.atan(t_out))
                half_in = psi_b - (t_in - math.atan(t_in))
                left.append(_polar(baseRadius * math.sqrt(1 + t_out * t_out), center - half_out))
                right.append(_polar(baseRadius * math.sqrt(1 + t_in * t_in), center + half_in))
            right.append(_polar(rootRadius, center + psi_b))
            Polyline(*left)
            CenterArc(
                (0, 0),
                tipRadius,
                math.degrees(center - psi_tip),
                math.degrees(2 * psi_tip),
            )
            Polyline(*right)
            CenterArc(
                (0, 0),
                rootRadius,
                math.degrees(center + psi_b),
                math.degrees(tooth_pitch - 2 * psi_b),
            )
    make_face()

gear_body = extrude(gear_sketch.sketch, amount=faceWidth, dir=(0, 0, 1))
bore_tool = Pos(0, 0, -0.05) * Cylinder(
    boreDiameter / 2,
    faceWidth + 0.1,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = gear_body - bore_tool
