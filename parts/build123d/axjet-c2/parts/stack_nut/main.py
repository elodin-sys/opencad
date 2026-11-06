from build123d import Align, Box, Compound, Cylinder, Pos, Rot

outerDiameter = 56.0
boreDiameter = 39.0
nutLength = 10.0
notchCount = 6.0
notchPitch = 360.0 / notchCount
notchPhase = 0.0
notchWidth = 6.0
notchDepth = 3.0

outerRadius = outerDiameter / 2.0
boreRadius = boreDiameter / 2.0
halfNotch = notchWidth / 2.0
floorRadius = outerRadius - notchDepth

assert outerDiameter > boreDiameter, "infeasible: OD must exceed the bore"
assert boreDiameter > 0.0, "infeasible: boreDiameter must be positive"
assert nutLength > 0.0, "infeasible: nutLength must be positive"
assert notchCount >= 1.0 and notchCount == int(notchCount), "infeasible: notchCount"
assert notchWidth > 0.0, "infeasible: notchWidth must be positive"
assert notchDepth > 0.0, "infeasible: notchDepth must be positive"
assert halfNotch < outerRadius, "infeasible: notch wider than the OD"
assert floorRadius > boreRadius, "infeasible: notch floor cuts the bore"
assert floorRadius**2 < outerRadius**2 - halfNotch**2, "infeasible: notch floor is outside the OD"

cutOverrun = 0.05

ring = Cylinder(
    outerRadius,
    nutLength,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
bore = Pos(0, 0, -cutOverrun) * Cylinder(
    boreRadius,
    nutLength + 2 * cutOverrun,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
annulus = ring - bore
notch_span = outerRadius - floorRadius + cutOverrun
notch_cutters = []
for index in range(int(notchCount)):
    angle = notchPhase + index * notchPitch
    block = Box(
        notch_span,
        notchWidth,
        nutLength + 2 * cutOverrun,
        align=(Align.MIN, Align.CENTER, Align.CENTER),
    )
    placed = Pos(floorRadius, 0.0, nutLength / 2.0) * block
    notch_cutters.append(Rot(0.0, 0.0, angle) * placed)
result = annulus - Compound(children=notch_cutters)
