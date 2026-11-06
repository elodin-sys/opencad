from build123d import Align, Cylinder, Pos

outerDiameter = 115.0
innerDiameter = 40.0
spacerLength = 14.0

assert outerDiameter > 0.0, "infeasible: outerDiameter must be positive"
assert innerDiameter > 0.0, "infeasible: innerDiameter must be positive"
assert innerDiameter < outerDiameter, "infeasible: innerDiameter must lie inside the OD"
assert spacerLength > 0.0, "infeasible: spacerLength must be positive"

# Cutter overruns both seats so the through-hole faces are not coincident with the tool.
boreOverrun = 0.05

ring = Cylinder(
    outerDiameter / 2.0,
    spacerLength,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
bore = Pos(0, 0, -boreOverrun) * Cylinder(
    innerDiameter / 2.0,
    spacerLength + 2.0 * boreOverrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = ring - bore
