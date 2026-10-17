# 100 x 100 x 3 mm plate, XY-centred, bottom on z = 0.
import cadquery as cq

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
assert holeCentreY + holeDia / 2 < slotCentreY - slotRy, "infeasible: holeDia overlaps slot"
assert abs(holeCentreX) < plateWidth / 2, "infeasible: holeCentreX outside plate"
assert edgeHoleDia > 0, "infeasible: edgeHoleDia must be positive"
assert edgeHoleDepth > 0, "infeasible: edgeHoleDepth must be positive"
assert edgeHoleZ > 0, "infeasible: edgeHoleZ must be positive"
assert edgeHoleZ + edgeHoleDia / 2 < plateThickness, "infeasible: edgeHoleZ exceeds thickness"
assert abs(edgeHoleY) < plateHeight / 2, "infeasible: edgeHoleY outside plate"
assert pinDia > 0, "infeasible: pinDia must be positive"
assert pinCentreX > 0, "infeasible: pinCentreX must be positive"
assert pinCentreY > 0, "infeasible: pinCentreY must be positive"
assert pinCentreX + pinDia / 2 <= plateWidth / 2 + 0.05, "infeasible: pin exceeds +x"
assert pinCentreY + pinDia / 2 <= plateHeight / 2 + 0.05, "infeasible: pin exceeds +y"
assert chamferLeg > 0, "infeasible: chamferLeg must be positive"
assert topStrip > 0, "infeasible: topStrip must be positive"
assert midBridge > 0, "infeasible: midBridge must be positive"
assert slotRx > 0, "infeasible: slotRx must be positive"
assert slotRy > 0, "infeasible: slotRy must be positive"
assert abs(slotCentreX) < plateWidth / 2, "infeasible: slotCentreX outside plate"
assert slotCentreY + slotRy + topStrip <= plateHeight / 2 + 0.35, "infeasible: slot overlaps north edge"

cut_overshoot = 0.05

plate = cq.Workplane("XY").rect(plateWidth, plateHeight).extrude(plateThickness)
plate = plate.edges("|Z").edges("<Y").chamfer(chamferLeg)
plate = plate.edges("|Z").edges(">Y").fillet(pinDia / 2.0)

centre_tool = (
    cq.Workplane("XY")
    .workplane(offset=-cut_overshoot)
    .center(holeCentreX, holeCentreY)
    .circle(holeDia / 2.0)
    .extrude(plateThickness + 2.0 * cut_overshoot)
)
slot_tool = (
    cq.Workplane("XY")
    .workplane(offset=-cut_overshoot)
    .center(slotCentreX, slotCentreY)
    .ellipse(slotRx, slotRy)
    .extrude(plateThickness + 2.0 * cut_overshoot)
)
edge_neg = (
    cq.Workplane("YZ")
    .workplane(offset=-(plateWidth / 2.0) - cut_overshoot)
    .center(edgeHoleY, edgeHoleZ)
    .circle(edgeHoleDia / 2.0)
    .extrude(edgeHoleDepth + cut_overshoot)
)
edge_pos = (
    cq.Workplane("YZ")
    .workplane(offset=(plateWidth / 2.0) + cut_overshoot)
    .center(edgeHoleY, edgeHoleZ)
    .circle(edgeHoleDia / 2.0)
    .extrude(-(edgeHoleDepth + cut_overshoot))
)
cutters = centre_tool.union(slot_tool).union(edge_neg).union(edge_pos)
result = plate.cut(cutters).clean()
