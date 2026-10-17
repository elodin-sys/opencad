import cadquery as cq

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

assert bodyWidth > 0.0, "infeasible: bodyWidth must be positive"
assert bodyDepth > 0.0, "infeasible: bodyDepth must be positive"
assert bodyHeight > 0.0, "infeasible: bodyHeight must be positive"
assert overallLength > bodyDepth, "infeasible: overallLength must exceed bodyDepth"
assert holeDiameter > 0.0, "infeasible: holeDiameter must be positive"
assert holeDiameter < bodyWidth, "infeasible: holeDiameter must be smaller than bodyWidth"
assert holeDiameter < bodyDepth, "infeasible: holeDiameter must be smaller than bodyDepth"
assert shaftDiameter > 0.0, "infeasible: shaftDiameter must be positive"
assert shaftDiameter < bodyWidth, "infeasible: shaftDiameter must be smaller than bodyWidth"
assert filletRadius > 0.0, "infeasible: filletRadius must be positive"
assert filletRadius * 2.0 < bodyWidth, "infeasible: filletRadius must leave a flat on the head width"
assert filletRadius * 2.0 < bodyDepth, "infeasible: filletRadius must leave a flat on the head depth"
assert xMax > xMin, "infeasible: xMax must be greater than xMin"
assert yHead > yMin, "infeasible: yHead must be greater than yMin"
assert zMax > zMin, "infeasible: zMax must be greater than zMin"
assert holeCenterX > xMin, "infeasible: holeCenterX must be inside the head in x"
assert holeCenterX < xMax, "infeasible: holeCenterX must be inside the head in x"
assert holeCenterY > yMin, "infeasible: holeCenterY must be above yMin"
assert shaftCenterZ > zMin, "infeasible: shaftCenterZ must be above zMin"

head = (
    cq.Workplane("XY")
    .transformed(offset=(xMin, yMin, zMin))
    .box(bodyWidth, bodyDepth, bodyHeight, centered=(False, False, False))
    .edges("|Z")
    .fillet(filletRadius)
)
# Start in the +y wall so the shaft does not sit proud of the −y fillets.
shaft = (
    cq.Workplane("XY")
    .transformed(offset=(holeCenterX, yHead - 1.0, shaftCenterZ), rotate=(-90, 0, 0))
    .circle(shaftDiameter / 2.0)
    .extrude(yMin + overallLength - (yHead - 1.0))
)
bore = (
    cq.Workplane("XY")
    .transformed(offset=(holeCenterX, holeCenterY, zMin - 0.05))
    .circle(holeDiameter / 2.0)
    .extrude(bodyHeight + 0.1)
)
result = head.union(shaft).cut(bore).clean()
