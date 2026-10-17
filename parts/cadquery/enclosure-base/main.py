import cadquery as cq

# Contract parameters (exact names; stated as literals, derived as formulas)
outerWidth = 100.0
outerLength = 150.0
baseHeight = 47.0
wallThickness = 3.0
outerCornerRadius = 10.0
bottomEdgeRadius = 2.0
innerCornerRadius = outerCornerRadius - wallThickness
cavityWidth = outerWidth - 2.0 * wallThickness
cavityLength = outerLength - 2.0 * wallThickness
postInset = 12.0
postX = outerWidth / 2.0 - postInset
postY = outerLength / 2.0 - postInset
postOuterDiameter = 10.0
postBoreDiameter = 4.0

assert outerWidth > 0, "infeasible: outerWidth must be positive"
assert outerLength > 0, "infeasible: outerLength must be positive"
assert baseHeight > wallThickness, "infeasible: baseHeight must exceed floor"
assert wallThickness > 0, "infeasible: wallThickness must be positive"
assert outerCornerRadius > wallThickness, "infeasible: outerCornerRadius must exceed wall"
assert bottomEdgeRadius > 0, "infeasible: bottomEdgeRadius must be positive"
assert bottomEdgeRadius < wallThickness, "infeasible: bottomEdgeRadius must be less than floor"
assert postInset > 0, "infeasible: postInset must be positive"
assert postOuterDiameter > 0, "infeasible: postOuterDiameter must be positive"
assert postBoreDiameter > 0, "infeasible: postBoreDiameter must be positive"
assert postBoreDiameter < postOuterDiameter, "infeasible: bore must leave post wall"
assert outerWidth > 2.0 * postInset + postOuterDiameter, "infeasible: posts would overlap"
assert outerLength > 2.0 * postInset + postOuterDiameter, "infeasible: posts would overlap in y"
assert innerCornerRadius > 0, "infeasible: innerCornerRadius must be positive"
assert cavityWidth > 2.0 * innerCornerRadius, "infeasible: cavity too narrow for corners"
assert cavityLength > 2.0 * innerCornerRadius, "infeasible: cavity too short for corners"

post_height = baseHeight - wallThickness
bore_overrun = 0.05  # past floor top into solid; keeps tool off the coplanar face
cavity_overrun = 0.05  # past rim into air

# [outerBody] rounded prism, then [bottomRound] on the bottom perimeter
body = (
    cq.Workplane("XY")
    .box(outerWidth, outerLength, baseHeight, centered=(True, True, False))
    .edges("|Z")
    .fillet(outerCornerRadius)
    .edges("<Z")
    .fillet(bottomEdgeRadius)
)

# [cavity] pocket from floor top through the open rim
cavity_tool = (
    cq.Workplane("XY")
    .workplane(offset=wallThickness)
    .box(
        cavityWidth,
        cavityLength,
        post_height + cavity_overrun,
        centered=(True, True, False),
    )
    .edges("|Z")
    .fillet(innerCornerRadius)
)
body = body.cut(cavity_tool)

# [posts] four free-standing screw posts on the floor
post_r = postOuterDiameter / 2.0
post_centers = (
    (postX, postY),
    (-postX, postY),
    (-postX, -postY),
    (postX, -postY),
)
posts = None
for cx, cy in post_centers:
    post = cq.Workplane("XY").workplane(offset=wallThickness).center(cx, cy).circle(post_r).extrude(post_height)
    posts = post if posts is None else posts.union(post)
body = body.union(posts)

# [bores] blind holes stop at the floor top (slight overrun into the floor)
bore_r = postBoreDiameter / 2.0
bores = None
for cx, cy in post_centers:
    bore = (
        cq.Workplane("XY")
        .workplane(offset=wallThickness - bore_overrun)
        .center(cx, cy)
        .circle(bore_r)
        .extrude(post_height + bore_overrun + cavity_overrun)
    )
    bores = bore if bores is None else bores.union(bore)
result = body.cut(bores).clean()
