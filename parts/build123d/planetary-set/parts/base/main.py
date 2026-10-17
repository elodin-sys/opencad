from build123d import Align, Box, Cylinder, Pos

plateSizeX = 150.0
plateSizeY = 150.0
plateThickness = 5.0
holeDiameter = 10.0

assert plateSizeX > 0, "infeasible: plateSizeX must be positive"
assert plateSizeY > 0, "infeasible: plateSizeY must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert holeDiameter < plateSizeX, "infeasible: holeDiameter must be smaller than plateSizeX"
assert holeDiameter < plateSizeY, "infeasible: holeDiameter must be smaller than plateSizeY"

# Seat (datum A) is the top face at z = 0; the plate hangs below it.
plate = Box(
    plateSizeX,
    plateSizeY,
    plateThickness,
    align=(Align.CENTER, Align.CENTER, Align.MAX),
)
# Overrun both faces so the cutter is not coincident with the seat or the bottom.
cutterOverrun = 0.02
hole = Pos(0, 0, cutterOverrun) * Cylinder(
    holeDiameter / 2,
    plateThickness + 2 * cutterOverrun,
    align=(Align.CENTER, Align.CENTER, Align.MAX),
)
result = plate - hole
