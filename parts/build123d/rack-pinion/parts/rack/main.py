import math

from build123d import Polyline, extrude, make_face

gearModule = 2.0
toothCount = 32.0
pressureAngle = 20.0
addendum = 2.0
dedendum = 2.5
backlashThinning = 0.05
rackLength = 200.0
rackThickness = 8.0
bodyDepth = 9.5

pitch = math.pi * gearModule
toothThickness = pitch / 2 - backlashThinning
tipWidth = toothThickness - 2 * addendum * math.tan(math.radians(pressureAngle))
rootWidth = toothThickness + 2 * dedendum * math.tan(math.radians(pressureAngle))
backOffset = dedendum + bodyDepth
firstToothX = (0.5 - toothCount / 2) * pitch
endLand = rackLength / 2 + firstToothX - rootWidth / 2

assert rackLength > 0, "infeasible: rackLength must be positive"
assert rackThickness > 0, "infeasible: rackThickness must be positive"
assert bodyDepth > 0, "infeasible: bodyDepth must be positive"
assert gearModule > 0, "infeasible: gearModule must be positive"
assert toothCount >= 1, "infeasible: toothCount must be at least 1"
assert toothCount == int(toothCount), "infeasible: toothCount must be a whole number"
assert 0 < pressureAngle < 90, "infeasible: pressureAngle must be between 0 and 90 degrees"
assert addendum > 0, "infeasible: addendum must be positive"
assert dedendum > 0, "infeasible: dedendum must be positive"
assert backlashThinning >= 0, "infeasible: backlashThinning must be non-negative"
assert toothThickness > 0, "infeasible: tooth thickness on the pitch line must be positive"
assert tipWidth > 0, "infeasible: tip width must stay positive"
assert endLand >= 0, "infeasible: outermost teeth must lie inside the body"

half_length = rackLength / 2
root_y = -dedendum
tip_y = addendum
back_y = -backOffset
count = int(toothCount)

# CCW from +Z: back edge, right end, teeth right-to-left, left end.
points = [(-half_length, back_y), (half_length, back_y), (half_length, root_y)]
for i in range(count - 1, -1, -1):
    cx = (-toothCount / 2 + i + 0.5) * pitch
    points.append((cx + rootWidth / 2, root_y))
    points.append((cx + tipWidth / 2, tip_y))
    points.append((cx - tipWidth / 2, tip_y))
    points.append((cx - rootWidth / 2, root_y))
points.append((-half_length, root_y))

profile = Polyline(*points, close=True)
face = make_face(profile.edges())
result = extrude(face, amount=rackThickness, dir=(0, 0, 1))
