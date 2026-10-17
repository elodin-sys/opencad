from build123d import (
    Align,
    Axis,
    BuildPart,
    BuildSketch,
    Circle,
    Compound,
    Cylinder,
    GridLocations,
    Plane,
    Pos,
    draft,
    extrude,
    fillet,
    make_hull,
)

overallHeight = 26.0
flangeThickness = 11.0
bossDiameter = 57.0
flangeLength = 98.5
holeSpacing = 76.5
lobeDiameter = flangeLength - holeSpacing
draftAngle = 4.0
edgeRadius = 1.0
counterboreDiameter = 47.0
counterboreDepth = 14.0
boreDiameter = 14.0
mountingHoleDiameter = 10.0

assert overallHeight > flangeThickness, "infeasible: overallHeight must exceed flangeThickness"
assert flangeThickness > 0, "infeasible: flangeThickness must be positive"
assert bossDiameter > 0, "infeasible: bossDiameter must be positive"
assert flangeLength > holeSpacing, "infeasible: flangeLength must exceed holeSpacing"
assert holeSpacing > 0, "infeasible: holeSpacing must be positive"
assert lobeDiameter > 0, "infeasible: lobeDiameter must be positive"
assert draftAngle > 0, "infeasible: draftAngle must be positive"
assert edgeRadius > 0, "infeasible: edgeRadius must be positive"
assert edgeRadius < flangeThickness / 2, "infeasible: edgeRadius too large for flange"
assert counterboreDiameter > boreDiameter, "infeasible: counterbore must exceed bore"
assert counterboreDiameter < bossDiameter, "infeasible: counterbore exceeds boss"
assert counterboreDepth > 0, "infeasible: counterboreDepth must be positive"
assert counterboreDepth < overallHeight, "infeasible: counterboreDepth exceeds height"
assert boreDiameter > 0, "infeasible: boreDiameter must be positive"
assert mountingHoleDiameter > 0, "infeasible: mountingHoleDiameter must be positive"
assert mountingHoleDiameter < lobeDiameter, "infeasible: mounting hole exceeds lobe"

half_span = holeSpacing / 2.0
r_boss = bossDiameter / 2.0
r_lobe = lobeDiameter / 2.0

with BuildPart() as housing:
    with BuildSketch() as plan:
        housing_circle = Circle(r_boss)
        with GridLocations(holeSpacing, 0, 2, 1):
            Circle(r_lobe)
        make_hull()
    extrude(amount=flangeThickness)
    extrude(housing_circle, amount=overallHeight)
    side_faces = housing.faces().filter_by(Axis.Z, reverse=True)
    draft(side_faces, Plane.XY, draftAngle)
    fillet(housing.edges(), edgeRadius)

body = housing.part
over = 0.05
cb_floor = overallHeight - counterboreDepth
tools = Compound(
    children=[
        Pos(0, 0, cb_floor)
        * Cylinder(
            counterboreDiameter / 2,
            counterboreDepth + over,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ),
        Pos(0, 0, -over)
        * Cylinder(
            boreDiameter / 2,
            cb_floor + 2 * over,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ),
        Pos(half_span, 0, -over)
        * Cylinder(
            mountingHoleDiameter / 2,
            flangeThickness + 2 * over,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ),
        Pos(-half_span, 0, -over)
        * Cylinder(
            mountingHoleDiameter / 2,
            flangeThickness + 2 * over,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ),
    ]
)
result = body - tools
