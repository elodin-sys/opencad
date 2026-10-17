import math

from build123d import Cylinder, Polyline, Pos, extrude, make_face

teeth = 45.0
gearModule = 2.0
pressureAngle = 20.0
profileShift = 0.0
addendumCoeff = 1.0
dedendumCoeff = 1.25
backlashThinning = 0.05
faceWidth = 8.0
boreDiameter = 8.0
pitchRadius = gearModule * teeth / 2
tipRadius = pitchRadius + (addendumCoeff + profileShift) * gearModule
rootRadius = pitchRadius - (dedendumCoeff - profileShift) * gearModule
baseRadius = pitchRadius * math.cos(math.radians(pressureAngle))
toothThickness = (
    gearModule * (math.pi / 2 + 2 * profileShift * math.tan(math.radians(pressureAngle))) - backlashThinning
)
flankPoints = 14.0

assert faceWidth > 0, "infeasible: faceWidth must be positive"
assert 0 < boreDiameter < 2 * rootRadius, "infeasible: boreDiameter must be positive and smaller than the root diameter"
assert toothThickness > 0, "infeasible: tooth thickness must be positive"
assert tipRadius > rootRadius > baseRadius > 0, "infeasible: tip, root and base radii are out of order"
assert flankPoints >= 2, "infeasible: flankPoints must be at least 2"


def _involute(angle):
    return math.tan(angle) - angle


def _flank_half_angle(radius):
    # Polar half-width of the thinned involute, measured from the tooth centreline.
    pressure = math.radians(pressureAngle)
    transverse = math.acos(baseRadius / radius)
    return toothThickness / (2 * pitchRadius) + _involute(pressure) - _involute(transverse)


def _polar(radius, angle):
    return (radius * math.cos(angle), radius * math.sin(angle))


def _profile_points():
    count = round(teeth)
    samples = round(flankPoints)
    radii = [rootRadius + (tipRadius - rootRadius) * i / (samples - 1) for i in range(samples)]
    points = []
    for tooth in range(count):
        center = 2 * math.pi * tooth / count
        for radius in radii:
            points.append(_polar(radius, center - _flank_half_angle(radius)))
        points.append(_polar(tipRadius, center))
        for radius in reversed(radii):
            points.append(_polar(radius, center + _flank_half_angle(radius)))
        next_center = 2 * math.pi * (tooth + 1) / count
        root_start = center + _flank_half_angle(rootRadius)
        root_end = next_center - _flank_half_angle(rootRadius)
        points.append(_polar(rootRadius, (root_start + root_end) / 2))
    return points


gear_face = make_face(Polyline(*_profile_points(), close=True))
gear_body = extrude(gear_face, amount=faceWidth)
# Cut past both faces so the tool is not coincident with the blank.
bore_tool = Pos(0, 0, faceWidth / 2) * Cylinder(boreDiameter / 2, faceWidth + 0.04)
result = gear_body - bore_tool
