from build123d import Align, Axis, Box, Cylinder, Pos, Rot, fillet

xMin = 100.0
yMin = 0.0
zMin = 70.0
bodyWidth = 10.0
bodyDepth = 10.0
bodyHeight = 50.0
overallLength = 88.0
holeDiameter = 5.0
shaftDiameter = 5.0
filletRadius = 4.0
xMax = 110.0
yHead = 10.0
zMax = 120.0
holeCenterX = 105.0
holeCenterY = 5.0
shaftCenterZ = 95.0

assert bodyWidth > 0, "infeasible: bodyWidth must be positive"
assert bodyDepth > 0, "infeasible: bodyDepth must be positive"
assert bodyHeight > 0, "infeasible: bodyHeight must be positive"
assert overallLength > bodyDepth, "infeasible: overallLength must extend past the head"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert holeDiameter < bodyWidth, "infeasible: holeDiameter exceeds head width"
assert holeDiameter < bodyDepth, "infeasible: holeDiameter exceeds head depth"
assert shaftDiameter > 0, "infeasible: shaftDiameter must be positive"
assert filletRadius > 0, "infeasible: filletRadius must be positive"
assert xMax > xMin, "infeasible: xMax must exceed xMin"
assert yHead > yMin, "infeasible: yHead must exceed yMin"
assert zMax > zMin, "infeasible: zMax must exceed zMin"
assert holeCenterY > yMin, "infeasible: holeCenterY must sit above yMin"

head = Pos(xMin, yMin, zMin) * Box(
    bodyWidth,
    bodyDepth,
    bodyHeight,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
head = fillet(head.edges().filter_by(Axis.Z), filletRadius)
shaft = (
    Pos(holeCenterX, (holeCenterY + yMin + overallLength) / 2, shaftCenterZ)
    * Rot(90, 0, 0)
    * Cylinder(shaftDiameter / 2, (yMin + overallLength) - holeCenterY)
)
bore = Pos(holeCenterX, holeCenterY, zMin + bodyHeight / 2) * Cylinder(holeDiameter / 2, bodyHeight + 0.1)
result = (head + shaft) - bore
