from build123d import Align, Box, Compound, Cylinder, Pos

blockLength = 61.0
blockWidth = 40.0
blockHeight = 15.0
holeX = 21.6
holeY = 14.4
holeDiameter = 2.5
holeDepth = 5.0
fanRecessDiameter = 38.5
fanRecessDepth = 1.0

assert blockLength > 0, "infeasible: blockLength must be positive"
assert blockWidth > 0, "infeasible: blockWidth must be positive"
assert blockHeight > holeDepth, "infeasible: blockHeight must exceed holeDepth"
assert blockHeight > fanRecessDepth, "infeasible: blockHeight must exceed fanRecessDepth"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert holeDepth > 0, "infeasible: holeDepth must be positive"
assert holeX + holeDiameter / 2 < blockLength / 2, "infeasible: screw holes must stay inside the length"
assert holeY + holeDiameter / 2 < blockWidth / 2, "infeasible: screw holes must stay inside the width"
assert 0 < fanRecessDiameter < blockWidth, "infeasible: fanRecessDiameter must stay under blockWidth"

# Past the open mouth so the cutter cap is not coplanar with the stock face.
cutterOverrun = 0.02

block = Box(
    blockLength,
    blockWidth,
    blockHeight,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)

screwHoles = [
    Pos(sx * holeX, sy * holeY, -cutterOverrun)
    * Cylinder(
        holeDiameter / 2,
        holeDepth + cutterOverrun,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for sx in (-1.0, 1.0)
    for sy in (-1.0, 1.0)
]

fanIntake = Pos(0, 0, blockHeight - fanRecessDepth) * Cylinder(
    fanRecessDiameter / 2,
    fanRecessDepth + cutterOverrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)

result = block - Compound([*screwHoles, fanIntake])
