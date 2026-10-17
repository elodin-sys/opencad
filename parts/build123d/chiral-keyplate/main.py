from build123d import Align, Axis, Box, Compound, Pos, Rot

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
assert slotDepth < plateThickness, "infeasible: slotDepth must leave a web below the floors"
assert abs(slotCentreX) + slotLength / 2.0 < plateWidth / 2.0, (
    "infeasible: slot A/C long axis must stay inside plateWidth"
)
assert abs(slotCentreY) + slotWidth / 2.0 < plateHeight / 2.0, (
    "infeasible: slot A/C short axis must stay inside plateHeight"
)
assert abs(slotCentreY) + slotLength / 2.0 < plateHeight / 2.0, (
    "infeasible: slot B/D long axis must stay inside plateHeight"
)
assert abs(slotCentreX) + slotWidth / 2.0 < plateWidth / 2.0, (
    "infeasible: slot B/D short axis must stay inside plateWidth"
)

plate = Box(
    plateWidth,
    plateHeight,
    plateThickness,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)

overshoot = 0.05
seed = Pos(slotCentreX, slotCentreY, plateThickness - slotDepth) * Box(
    slotLength,
    slotWidth,
    slotDepth + overshoot,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
pockets = Compound([Rot(0, 0, angle) * seed for angle in (0.0, 90.0, 180.0, 270.0)])
result = plate - pockets

floor_z = plateThickness - slotDepth
floor_names = {
    (slotCentreX, slotCentreY): "pocketFloorA",
    (-slotCentreY, slotCentreX): "pocketFloorB",
    (-slotCentreX, -slotCentreY): "pocketFloorC",
    (slotCentreY, -slotCentreX): "pocketFloorD",
}
named = 0
for face in result.faces().filter_by(Axis.Z):
    centre = face.center()
    if abs(centre.Z - floor_z) > 0.05:
        continue
    for (x, y), name in floor_names.items():
        if abs(centre.X - x) < 0.05 and abs(centre.Y - y) < 0.05:
            face.label = name
            named += 1
assert named == 4, "expected four named pocket floors"
