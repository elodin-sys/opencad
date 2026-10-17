import cadquery as cq

plateWidth = 80.0
plateHeight = 80.0
plateThickness = 8.0
slotLength = 16.0
slotWidth = 6.0
slotDepth = 4.0
slotCentreX = 20.0
slotCentreY = 8.0

assert plateWidth > 0, "infeasible: plateWidth must be positive"
assert plateHeight > 0, "infeasible: plateHeight must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert slotLength > 0, "infeasible: slotLength must be positive"
assert slotWidth > 0, "infeasible: slotWidth must be positive"
assert slotDepth > 0, "infeasible: slotDepth must be positive"
assert slotCentreX > 0, "infeasible: slotCentreX must be positive for the specified pinwheel seed"
assert slotCentreY > 0, "infeasible: slotCentreY must be positive for the specified pinwheel seed"
assert slotDepth < plateThickness, "infeasible: slotDepth must leave a web below the floors"
assert abs(slotCentreX) + slotLength / 2 < plateWidth / 2, "infeasible: slot A/C long extent reaches an x-edge"
assert abs(slotCentreY) + slotWidth / 2 < plateHeight / 2, "infeasible: slot A/C short extent reaches a y-edge"
assert abs(slotCentreY) + slotLength / 2 < plateHeight / 2, "infeasible: slot B/D long extent reaches a y-edge"
assert abs(slotCentreX) + slotWidth / 2 < plateWidth / 2, "infeasible: slot B/D short extent reaches an x-edge"

floorZ = plateThickness - slotDepth
cutOverrun = 0.02

plateBlank = cq.Workplane("XY").rect(plateWidth, plateHeight).extrude(plateThickness)

# Slot A seed; B/C/D are +90/+180/+270 deg about +z: R(x, y) = (-y, x).
slotA = (
    cq.Workplane("XY")
    .workplane(offset=floorZ)
    .center(slotCentreX, slotCentreY)
    .rect(slotLength, slotWidth)
    .extrude(slotDepth + cutOverrun)
)
slotB = (
    cq.Workplane("XY")
    .workplane(offset=floorZ)
    .center(-slotCentreY, slotCentreX)
    .rect(slotWidth, slotLength)
    .extrude(slotDepth + cutOverrun)
)
slotC = (
    cq.Workplane("XY")
    .workplane(offset=floorZ)
    .center(-slotCentreX, -slotCentreY)
    .rect(slotLength, slotWidth)
    .extrude(slotDepth + cutOverrun)
)
slotD = (
    cq.Workplane("XY")
    .workplane(offset=floorZ)
    .center(slotCentreY, -slotCentreX)
    .rect(slotWidth, slotLength)
    .extrude(slotDepth + cutOverrun)
)
slotTools = slotA.union(slotB).union(slotC).union(slotD)

result = (
    plateBlank.cut(slotTools, clean=True)
    .faces(cq.NearestToPointSelector((slotCentreX, slotCentreY, floorZ)))
    .tag("pocketFloorA")
    .end()
    .faces(cq.NearestToPointSelector((-slotCentreY, slotCentreX, floorZ)))
    .tag("pocketFloorB")
    .end()
    .faces(cq.NearestToPointSelector((-slotCentreX, -slotCentreY, floorZ)))
    .tag("pocketFloorC")
    .end()
    .faces(cq.NearestToPointSelector((slotCentreY, -slotCentreX, floorZ)))
    .tag("pocketFloorD")
    .end()
)
