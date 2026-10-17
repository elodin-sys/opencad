from build123d import (
    Align,
    Axis,
    Compound,
    Cylinder,
    Location,
    RectangleRounded,
    extrude,
    fillet,
)

outerWidth = 100.0
outerLength = 150.0
baseHeight = 47.0
wallThickness = 3.0
outerCornerRadius = 10.0
bottomEdgeRadius = 2.0
innerCornerRadius = outerCornerRadius - wallThickness
cavityWidth = outerWidth - 2 * wallThickness
cavityLength = outerLength - 2 * wallThickness
postInset = 12.0
postX = outerWidth / 2 - postInset
postY = outerLength / 2 - postInset
postOuterDiameter = 10.0
postBoreDiameter = 4.0

assert outerWidth > 0, "infeasible: outerWidth must be positive"
assert outerLength > 0, "infeasible: outerLength must be positive"
assert outerWidth > 2 * outerCornerRadius, "infeasible: outerWidth too small for outerCornerRadius"
assert outerLength > 2 * outerCornerRadius, "infeasible: outerLength too small for outerCornerRadius"
assert baseHeight > wallThickness, "infeasible: baseHeight must exceed wallThickness"
assert wallThickness > 0, "infeasible: wallThickness must be positive"
assert outerCornerRadius > wallThickness, "infeasible: outerCornerRadius must exceed wallThickness"
assert bottomEdgeRadius > 0, "infeasible: bottomEdgeRadius must be positive"
assert bottomEdgeRadius < wallThickness, "infeasible: bottomEdgeRadius must be less than wallThickness"
assert innerCornerRadius > 0, "infeasible: innerCornerRadius must be positive"
assert cavityWidth > 2 * innerCornerRadius, "infeasible: cavityWidth too small for corners"
assert cavityLength > 2 * innerCornerRadius, "infeasible: cavityLength too small for corners"
assert postInset > 0, "infeasible: postInset must be positive"
assert postOuterDiameter > postBoreDiameter, "infeasible: post must be thicker than bore"
assert postBoreDiameter > 0, "infeasible: postBoreDiameter must be positive"
assert postX > postOuterDiameter / 2, "infeasible: posts overlap across x=0"
assert postY > postOuterDiameter / 2, "infeasible: posts overlap across y=0"
assert abs(postX) + postOuterDiameter / 2 < cavityWidth / 2, "infeasible: post outside cavity in x"
assert abs(postY) + postOuterDiameter / 2 < cavityLength / 2, "infeasible: post outside cavity in y"

post_height = baseHeight - wallThickness
cut_overrun = 0.05

outer = extrude(
    RectangleRounded(outerWidth, outerLength, outerCornerRadius),
    amount=baseHeight,
)
body = fillet(outer.edges().group_by(Axis.Z)[0], bottomEdgeRadius)

cavity = Location((0, 0, wallThickness)) * extrude(
    RectangleRounded(cavityWidth, cavityLength, innerCornerRadius),
    amount=post_height + cut_overrun,
)
body = body - cavity

post_axes = (
    (postX, postY),
    (-postX, postY),
    (-postX, -postY),
    (postX, -postY),
)
posts = [
    Location((x, y, wallThickness))
    * Cylinder(
        postOuterDiameter / 2,
        post_height,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for x, y in post_axes
]
body = body + Compound(children=posts)

bores = [
    Location((x, y, wallThickness))
    * Cylinder(
        postBoreDiameter / 2,
        post_height + cut_overrun,
        align=(Align.CENTER, Align.CENTER, Align.MIN),
    )
    for x, y in post_axes
]
body = body - Compound(children=bores)

result = body
