from build123d import (
    Align,
    Axis,
    Compound,
    Cylinder,
    Ellipse,
    Location,
    Rectangle,
    Rot,
    chamfer,
    extrude,
    fillet,
)

plateWidth = 100.0
plateHeight = 100.0
plateThickness = 3.0
holeDia = 5.0
holeCentreX = 0.0
holeCentreY = 0.0
edgeHoleDia = 2.0
edgeHoleY = 42.0
edgeHoleDepth = 5.0
edgeHoleZ = 1.5
pinDia = 6.0
pinCentreX = 47.0
pinCentreY = 47.0
chamferLeg = 5.0
topStrip = 10.0
midBridge = 9.5
slotCentreX = 0.0
slotCentreY = 26.0
slotRx = 35.0
slotRy = 14.0

assert plateWidth > 0, "infeasible: plateWidth must be positive"
assert plateHeight > 0, "infeasible: plateHeight must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert holeDia > 0, "infeasible: holeDia must be positive"
assert holeDia < 20, "infeasible: holeDia too large for the plate"
assert edgeHoleDia > 0, "infeasible: edgeHoleDia must be positive"
assert edgeHoleDepth > 0, "infeasible: edgeHoleDepth must be positive"
assert edgeHoleZ > 0, "infeasible: edgeHoleZ must be positive"
assert pinDia > 0, "infeasible: pinDia must be positive"
assert pinCentreX > 0, "infeasible: pinCentreX must be positive"
assert pinCentreY > 0, "infeasible: pinCentreY must be positive"
assert chamferLeg > 0, "infeasible: chamferLeg must be positive"
assert topStrip > 0, "infeasible: topStrip must be positive"
assert midBridge > 0, "infeasible: midBridge must be positive"
assert slotRx > 0, "infeasible: slotRx must be positive"
assert slotRy > 0, "infeasible: slotRy must be positive"

_overshoot = 0.05

outline = Rectangle(plateWidth, plateHeight)
south = outline.vertices().filter_by_position(Axis.Y, -plateHeight / 2 - 0.1, -plateHeight / 2 + 0.1)
outline = chamfer(south, length=chamferLeg)
north = outline.vertices().filter_by_position(Axis.Y, plateHeight / 2 - 0.1, plateHeight / 2 + 0.1)
outline = fillet(north, radius=pinDia / 2)
plate = extrude(outline, amount=plateThickness)

centre = Location((holeCentreX, holeCentreY, -_overshoot)) * Cylinder(
    holeDia / 2,
    plateThickness + 2 * _overshoot,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
slot = extrude(
    Location((slotCentreX, slotCentreY, -_overshoot)) * Ellipse(slotRx, slotRy),
    amount=plateThickness + 2 * _overshoot,
)
edge_neg = (
    Location((-plateWidth / 2 - _overshoot, edgeHoleY, edgeHoleZ))
    * Rot(0, 90, 0)
    * Cylinder(
        edgeHoleDia / 2,
        edgeHoleDepth + _overshoot,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
)
edge_pos = (
    Location((plateWidth / 2 + _overshoot, edgeHoleY, edgeHoleZ))
    * Rot(0, -90, 0)
    * Cylinder(
        edgeHoleDia / 2,
        edgeHoleDepth + _overshoot,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
)

_ = (pinCentreX, pinCentreY, topStrip, midBridge)
result = plate - Compound([centre, slot, edge_neg, edge_pos])
