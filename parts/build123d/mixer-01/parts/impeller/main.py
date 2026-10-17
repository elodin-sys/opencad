from build123d import Align, Box, Cylinder, Pos, Rot

hubOuterDiameter = 12.0
hubHeight = 10.0
boreDiameter = 8.0
bladeCount = 4
bladeThickness = 2.0
bladeTipRadius = 20.0
bladeBottomZ = 1.0
bladeHeight = 8.0

assert hubOuterDiameter > boreDiameter > 0, "infeasible: hub must be larger than the bore"
assert hubHeight > 0, "infeasible: hubHeight must be positive"
assert bladeThickness > 0, "infeasible: bladeThickness must be positive"
assert bladeHeight > 0, "infeasible: bladeHeight must be positive"
assert bladeBottomZ >= 0, "infeasible: bladeBottomZ must sit on or above the hub bottom"
assert bladeTipRadius > hubOuterDiameter / 2.0, "infeasible: blade tip must lie outside the hub"
assert bladeCount >= 1, "infeasible: bladeCount must be at least one"

half = bladeThickness / 2.0
hub_r = hubOuterDiameter / 2.0
bore_r = boreDiameter / 2.0
root_x = (hub_r + bore_r) / 2.0
assert root_x * root_x + half * half < hub_r * hub_r, "infeasible: blade root misses the hub"
assert half < bladeTipRadius, "infeasible: blade thicker than the tip circle"

# Box runs past the tip cylinder so the arc is a clean intersection, not a coincident edge.
overshoot = 1.0
outer_x = bladeTipRadius + overshoot
center_z = bladeBottomZ + bladeHeight / 2.0
blank = Pos((root_x + outer_x) / 2.0, 0.0, center_z) * Box(outer_x - root_x, bladeThickness, bladeHeight)
tip = Pos(0.0, 0.0, center_z) * Cylinder(bladeTipRadius, bladeHeight + 2.0)
blade = blank & tip

hub = Cylinder(hub_r, hubHeight, align=(Align.CENTER, Align.CENTER, Align.MIN))
body = hub
for i in range(int(bladeCount)):
    body = body + Rot(0, 0, i * 360.0 / bladeCount) * blade
# Cut past both hub faces so the bore does not leave a coincident cap.
bore = Pos(0.0, 0.0, -0.05) * Cylinder(
    bore_r,
    hubHeight + 0.1,
    align=(Align.CENTER, Align.CENTER, Align.MIN),
)
result = body - bore
