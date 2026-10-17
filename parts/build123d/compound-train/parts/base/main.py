from build123d import Align, Box, Compound, Cylinder, Pos

plateLength = 195.0
plateWidth = 100.0
plateThickness = 5.0
plateXMin = -25.0
pinionHoleDiameter = 6.0
idlerHoleDiameter = 8.0
outputHoleDiameter = 8.0
idlerX = 60.0
outputX = 120.0

assert plateLength > 0, "infeasible: plateLength must be positive"
assert plateWidth > 0, "infeasible: plateWidth must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert pinionHoleDiameter > 0, "infeasible: pinionHoleDiameter must be positive"
assert idlerHoleDiameter > 0, "infeasible: idlerHoleDiameter must be positive"
assert outputHoleDiameter > 0, "infeasible: outputHoleDiameter must be positive"
assert plateXMin < -pinionHoleDiameter / 2, "infeasible: pinion hole breaks through the -x end"
assert plateXMin + plateLength > pinionHoleDiameter / 2, "infeasible: pinion hole breaks through the +x end"
assert plateXMin < idlerX - idlerHoleDiameter / 2, "infeasible: idler hole breaks through the -x end"
assert plateXMin + plateLength > idlerX + idlerHoleDiameter / 2, "infeasible: idler hole breaks through the +x end"
assert plateXMin < outputX - outputHoleDiameter / 2, "infeasible: output hole breaks through the -x end"
assert plateXMin + plateLength > outputX + outputHoleDiameter / 2, "infeasible: output hole breaks through the +x end"
assert plateWidth / 2 > pinionHoleDiameter / 2, "infeasible: pinion hole breaks through the side"
assert plateWidth / 2 > idlerHoleDiameter / 2, "infeasible: idler hole breaks through the side"
assert plateWidth / 2 > outputHoleDiameter / 2, "infeasible: output hole breaks through the side"

plate = Pos(plateXMin, 0, 0) * Box(
    plateLength,
    plateWidth,
    plateThickness,
    align=(Align.MIN, Align.CENTER, Align.MAX),
)
hole_overrun = 0.05
hole_height = plateThickness + 2.0 * hole_overrun
holes = Compound(
    children=[
        Pos(0, 0, hole_overrun)
        * Cylinder(
            pinionHoleDiameter / 2,
            hole_height,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        ),
        Pos(idlerX, 0, hole_overrun)
        * Cylinder(
            idlerHoleDiameter / 2,
            hole_height,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        ),
        Pos(outputX, 0, hole_overrun)
        * Cylinder(
            outputHoleDiameter / 2,
            hole_height,
            align=(Align.CENTER, Align.CENTER, Align.MAX),
        ),
    ]
)
result = plate - holes
