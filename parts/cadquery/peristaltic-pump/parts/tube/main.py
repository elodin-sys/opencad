import cadquery as cq

tubeOuterDiameter = 3.0
tubeInnerDiameter = 1.0
trackRadius = 12.17
centrelineRadius = trackRadius - tubeOuterDiameter / 2.0
bendAngle = 180.0
legLength = 30.0

assert tubeOuterDiameter > 0.0, "infeasible: tubeOuterDiameter must be positive"
assert 0.0 < tubeInnerDiameter < tubeOuterDiameter, (
    "infeasible: tubeInnerDiameter must be positive and smaller than tubeOuterDiameter"
)
assert centrelineRadius > tubeOuterDiameter / 2.0, "infeasible: bend radius must exceed the outer tube radius"
assert bendAngle == 180.0, "infeasible: parallel legs tangent at x=0 require a 180-degree bend"
assert legLength > 0.0, "infeasible: legLength must be positive"

outerRadius = tubeOuterDiameter / 2.0
innerRadius = tubeInnerDiameter / 2.0


# Datum A: z=0; datum B: z axis; datum C: y=0.
# The tangent-continuous path runs from the outlet through +x to the inlet.
# Its circular arc gives the same analytic half-torus as a 180-degree revolve.
centreline = (
    cq.Workplane("XY")
    .moveTo(-legLength, -centrelineRadius)
    .lineTo(0.0, -centrelineRadius)
    .threePointArc((centrelineRadius, 0.0), (0.0, centrelineRadius))
    .lineTo(-legLength, centrelineRadius)
    .wire()
)

# A single annular sweep leaves open, planar mouths and a continuous bore.
# The path is symmetric about y=0 and the circular section about z=0.
result = (
    cq.Workplane("YZ", origin=(-legLength, -centrelineRadius, 0.0))
    .circle(outerRadius)
    .circle(innerRadius)
    .sweep(centreline, isFrenet=False, transition="transformed", clean=True)
)

assert result.solids().size() == 1, "construction failure: tube must be one solid"
assert result.val().isValid(), "construction failure: tube must be a valid solid"
