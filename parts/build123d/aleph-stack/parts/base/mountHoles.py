from build123d import Compound, Cylinder, Pos
from params import holeDiameter, holeInset, holePitchX, holePitchY, pcbThickness

assert holeDiameter > 0, "infeasible: holeDiameter must be positive"
assert holeInset > 0, "infeasible: holeInset must be positive"
assert holePitchX > holeDiameter, "infeasible: holes overlap along x"
assert holePitchY > holeDiameter, "infeasible: holes overlap along y"
assert pcbThickness > 0, "infeasible: pcbThickness must be positive"


def apply(body):
    overrun = 0.05
    height = pcbThickness + 2 * overrun
    centers = (
        (holeInset, holeInset),
        (holeInset + holePitchX, holeInset),
        (holeInset + holePitchX, holeInset + holePitchY),
        (holeInset, holeInset + holePitchY),
    )
    tool = Compound([Pos(x, y, pcbThickness / 2) * Cylinder(holeDiameter / 2, height) for x, y in centers])
    return body - tool
