from build123d import Align, Box, Cylinder, Pos

blockLength = 30.0
blockWidth = 16.0
blockThickness = 5.0
holeDiameter = 6.0

assert blockLength > 0.0, "infeasible: blockLength must be positive"
assert blockWidth > 0.0, "infeasible: blockWidth must be positive"
assert blockThickness > 0.0, "infeasible: blockThickness must be positive"
assert holeDiameter > 0.0, "infeasible: holeDiameter must be positive"
assert blockLength > holeDiameter, "infeasible: blockLength must clear the wrist-pin bore"
assert blockWidth > holeDiameter, "infeasible: blockWidth must clear the wrist-pin bore"

block = Box(
    blockLength,
    blockWidth,
    blockThickness,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
# Overrun both faces so the cutter is not coincident with z = 0 or z = blockThickness.
bore = Pos(0, 0, blockThickness / 2) * Cylinder(holeDiameter / 2, blockThickness + 0.04)
result = block - bore
