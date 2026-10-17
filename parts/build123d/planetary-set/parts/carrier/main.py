import math

from build123d import Align, Compound, Cylinder, Pos

carrierDiameter = 88.0
carrierThickness = 5.0
centreHoleDiameter = 10.0
planetHoleDiameter = 8.0
planetOrbitRadius = 36.0
planetHoleCount = 3
planetHoleStartAngle = 0.0

assert carrierThickness > 0, "infeasible: carrierThickness must be positive"
assert carrierDiameter > 0, "infeasible: carrierDiameter must be positive"
assert centreHoleDiameter > 0, "infeasible: centreHoleDiameter must be positive"
assert planetHoleDiameter > 0, "infeasible: planetHoleDiameter must be positive"
assert planetOrbitRadius > 0, "infeasible: planetOrbitRadius must be positive"
assert planetHoleCount >= 1, "infeasible: planetHoleCount must be at least 1"
assert carrierDiameter / 2 > planetOrbitRadius + planetHoleDiameter / 2, (
    "infeasible: carrierDiameter / 2 must exceed planetOrbitRadius + planetHoleDiameter / 2"
)

overrun = 0.05
disc = Cylinder(
    carrierDiameter / 2,
    carrierThickness,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
cutters = [
    Pos(0, 0, -overrun)
    * Cylinder(
        centreHoleDiameter / 2,
        carrierThickness + 2 * overrun,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
]
for index in range(planetHoleCount):
    angle = math.radians(planetHoleStartAngle + index * 360.0 / planetHoleCount)
    cutters.append(
        Pos(
            planetOrbitRadius * math.cos(angle),
            planetOrbitRadius * math.sin(angle),
            -overrun,
        )
        * Cylinder(
            planetHoleDiameter / 2,
            carrierThickness + 2 * overrun,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        )
    )
result = disc - Compound(cutters)
