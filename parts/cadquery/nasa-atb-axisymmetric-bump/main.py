import cadquery as cq

cylinderDiameter = 152.4
bumpChord = 203.2
bumpHeight = 19.05
filletRadius = 183.0
upstreamX = -650.0073203536
downstreamX = 900.0029136304

assert cylinderDiameter > 0, "infeasible: cylinderDiameter must be positive"
assert bumpChord > 0, "infeasible: bumpChord must be positive"
assert bumpHeight > 0, "infeasible: bumpHeight must be positive"
assert filletRadius > 0, "infeasible: filletRadius must be positive"
assert bumpHeight * 2 < bumpChord, "infeasible: use the shallow upper circular-arc branch"
assert upstreamX < 0, "infeasible: keep a positive upstream cylinder span before the origin"
assert downstreamX > bumpChord, "infeasible: keep a positive downstream cylinder span"

cylinderRadius = cylinderDiameter / 2
halfChord = bumpChord / 2
mainRadius = (bumpHeight**2 + halfChord**2) / (2 * bumpHeight)
assert mainRadius > bumpHeight, "infeasible: main arc center must sit below the crown"
mainCenterY = cylinderRadius + bumpHeight - mainRadius
blendRadicand = 2.0 * (mainRadius + filletRadius) * bumpHeight - bumpHeight**2
assert blendRadicand > 0, "infeasible: leading blend has no real tangency"
blendHalfChord = blendRadicand**0.5
blendStartX = halfChord - blendHalfChord
blendEndX = blendStartX + filletRadius * blendHalfChord / (mainRadius + filletRadius)
assert blendStartX > upstreamX, "infeasible: keep a positive upstream cylinder span"
assert blendStartX < blendEndX, "infeasible: leading blend must have positive axial span"
assert blendEndX < bumpChord, "infeasible: blend must meet the main arc before the trailing join"
assert blendEndX - blendStartX < filletRadius, "infeasible: blend chord exceeds filletRadius"

blendMidX = 0.5 * (blendStartX + blendEndX)
blendMidY = cylinderRadius + filletRadius - (filletRadius**2 - (blendMidX - blendStartX) ** 2) ** 0.5
blendEndY = cylinderRadius + filletRadius - (filletRadius**2 - (blendEndX - blendStartX) ** 2) ** 0.5
crownY = cylinderRadius + bumpHeight

result = (
    cq.Workplane("XY")
    .moveTo(upstreamX, 0.0)
    .lineTo(upstreamX, cylinderRadius)
    .lineTo(blendStartX, cylinderRadius)
    .threePointArc((blendMidX, blendMidY), (blendEndX, blendEndY))
    .threePointArc((halfChord, crownY), (bumpChord, cylinderRadius))
    .lineTo(downstreamX, cylinderRadius)
    .lineTo(downstreamX, 0.0)
    .close()
    .revolve(360, (0, 0), (1, 0))
    .rotate((0, 0, 0), (1, 0, 0), 45)
    .faces("<X")
    .tag("upstreamCap")
    .end()
    .faces(">X")
    .tag("downstreamCap")
    .end()
)
