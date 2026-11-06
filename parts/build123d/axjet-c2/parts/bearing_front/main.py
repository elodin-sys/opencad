from build123d import Align, Cylinder, GeomType, Pos, chamfer

outerDiameter = 52.0
innerDiameter = 25.0
ringLength = 30.0
chamferSize = 0.5

assert outerDiameter > innerDiameter > 0, "infeasible: outerDiameter must exceed innerDiameter, both positive"
assert ringLength > 0, "infeasible: ringLength must be positive"
assert chamferSize > 0, "infeasible: chamferSize must be positive"
assert 2 * chamferSize < ringLength, "infeasible: chamfers meet along the axis"
assert 2 * chamferSize < (outerDiameter - innerDiameter) / 2, "infeasible: chamfers consume the radial wall"

bore_overrun = 0.05
outer = Cylinder(
    outerDiameter / 2,
    ringLength,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
bore = Pos(0, 0, -bore_overrun) * Cylinder(
    innerDiameter / 2,
    ringLength + 2 * bore_overrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
ring = outer - bore
result = chamfer(ring.edges().filter_by(GeomType.CIRCLE), chamferSize)
