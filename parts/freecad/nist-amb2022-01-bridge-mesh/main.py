import math

import FreeCAD
import Part
import Sketcher

overallLength = 75.0
overallWidth = 5.0
bodyHeight = 12.0
noseAngle = 45.0
noseLength = 2.5
legCount = 12.0
largeLegWidth = 5.0
mediumLegWidth = 2.5
smallLegWidth = 0.5
gapWidth = 2.0
overhangAngle = 45.0
legMergeHeight = 7.0
gapLowHeight = 5.0
legGroupCount = 4.0
legGroupPitch = 14.0
endBlockLength = 19.0
tabCount = 11.0
tabWidth = 1.0
tabPitch = 7.0
tabHeight = 0.5
firstTabX = 4.0
l10StartX = 28.0
l10OuterWallThickness = 0.5
l10BaseThickness = 1.0
thinWallHeight = 4.0
l10CavityLength = 4.0
l10CavityWidth = 4.0
l10CavityStartX = 28.5
l10CeilingZ = 5.0
thinWallCount = 4.0
singleTrackWidth = 0.1
doubleTrackWidth = 0.2
wall1CenterY = 1.25
wall2CenterY = 2.0
wall3CenterY = 2.85
wall4CenterY = 3.6

assert overallLength > 0, "infeasible: overallLength must be positive"
assert overallWidth > 0, "infeasible: overallWidth must be positive"
assert bodyHeight > 0, "infeasible: bodyHeight must be positive"
assert noseLength > 0, "infeasible: noseLength must stay on the +x side of the tip"
assert noseLength < overallLength, "infeasible: noseLength must stay inside overallLength"
assert noseLength < endBlockLength, "infeasible: noseLength must end before the first gap"
assert 0 < noseAngle < 90, "infeasible: noseAngle must be an acute taper"
assert math.tan(math.radians(noseAngle)) > 0, "infeasible: noseAngle must produce a forward taper"
assert 0 < overhangAngle < 90, "infeasible: overhangAngle must be an acute rise"
assert math.tan(math.radians(overhangAngle)) > 0, "infeasible: overhangAngle must rise"
assert gapLowHeight > 0, "infeasible: gapLowHeight must be positive"
assert gapLowHeight < legMergeHeight, "infeasible: gap roof must rise toward +x"
assert bodyHeight > legMergeHeight, "infeasible: bodyHeight must sit above the merge plane"
assert bodyHeight > gapLowHeight, "infeasible: bodyHeight must sit above the gap roofs"
assert legCount >= 1, "infeasible: legCount must place at least one leg"
assert largeLegWidth > 0, "infeasible: largeLegWidth must be positive"
assert mediumLegWidth > 0, "infeasible: mediumLegWidth must be positive"
assert smallLegWidth > 0, "infeasible: smallLegWidth must be positive"
assert gapWidth > 0, "infeasible: gapWidth must be positive"
assert legGroupCount >= 1, "infeasible: legGroupCount must place at least one repeat"
assert legGroupPitch > 0, "infeasible: legGroupPitch must be positive"
assert endBlockLength > 0, "infeasible: endBlockLength must be positive"
assert tabCount >= 1, "infeasible: tabCount must place at least one tab"
assert tabWidth > 0, "infeasible: tabWidth must be positive"
assert tabPitch > 0, "infeasible: tabPitch must be positive"
assert tabWidth < tabPitch, "infeasible: tabWidth must leave a gap between tabs"
assert tabHeight > 0, "infeasible: tabHeight must be positive"
assert firstTabX >= 0, "infeasible: firstTabX must stay on the +x side of the tip"
assert firstTabX > noseLength, "infeasible: first tab must sit behind the nose shoulder"
assert firstTabX + (tabCount - 1) * tabPitch + tabWidth <= overallLength + 1e-9, (
    "infeasible: last tab would pass the far end"
)
assert l10StartX > endBlockLength, "infeasible: L10 must sit after the end block"
assert l10OuterWallThickness > 0, "infeasible: l10OuterWallThickness must be positive"
assert l10BaseThickness > 0, "infeasible: l10BaseThickness must be positive"
assert thinWallHeight > 0, "infeasible: thinWallHeight must be positive"
assert l10CavityLength > 0, "infeasible: l10CavityLength must be positive"
assert l10CavityWidth > 0, "infeasible: l10CavityWidth must be positive"
assert l10CavityStartX > l10StartX, "infeasible: L10 cavity must sit inside the outer +x wall"
assert l10CavityStartX + l10CavityLength < l10StartX + largeLegWidth, (
    "infeasible: L10 cavity must sit inside the far x-wall"
)
assert l10CeilingZ > l10BaseThickness, "infeasible: l10CeilingZ must sit above the L10 base"
assert thinWallCount >= 1, "infeasible: thinWallCount must place at least one partition"
assert singleTrackWidth > 0, "infeasible: singleTrackWidth must be positive"
assert doubleTrackWidth > 0, "infeasible: doubleTrackWidth must be positive"
assert 0 < wall1CenterY < overallWidth, "infeasible: wall1CenterY must stay inside the width"
assert 0 < wall2CenterY < overallWidth, "infeasible: wall2CenterY must stay inside the width"
assert 0 < wall3CenterY < overallWidth, "infeasible: wall3CenterY must stay inside the width"
assert 0 < wall4CenterY < overallWidth, "infeasible: wall4CenterY must stay inside the width"
assert wall1CenterY < wall2CenterY < wall3CenterY < wall4CenterY, "infeasible: internal walls must stay ordered in +y"
assert l10OuterWallThickness + l10CavityWidth < overallWidth, "infeasible: L10 outer walls must leave a cavity"


def add_poly(sk, pts):
    n = len(pts)
    gids = []
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        gids.append(
            sk.addGeometry(Part.LineSegment(FreeCAD.Vector(a[0], a[1], 0), FreeCAD.Vector(b[0], b[1], 0)), False)
        )
    for i in range(n):
        sk.addConstraint(Sketcher.Constraint("Coincident", gids[i], 2, gids[(i + 1) % n], 1))
        sk.addConstraint(Sketcher.Constraint("DistanceX", -1, 1, gids[i], 1, pts[i][0]))
        sk.addConstraint(Sketcher.Constraint("DistanceY", -1, 1, gids[i], 1, pts[i][1]))


def add_rect(sk, x0, y0, dx, dy):
    add_poly(sk, [(x0, y0), (x0 + dx, y0), (x0 + dx, y0 + dy), (x0, y0 + dy)])


doc = FreeCAD.newDocument("nist-amb2022-01-bridge-mesh")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)

body_sketch = body.newObject("Sketcher::SketchObject", "BodySketch")
body_sketch.AttachmentSupport = [(xy, "")]
body_sketch.MapMode = "FlatFace"
add_poly(
    body_sketch,
    [
        (0.0, overallWidth / 2.0),
        (noseLength, 0.0),
        (overallLength, 0.0),
        (overallLength, overallWidth),
        (noseLength, overallWidth),
    ],
)

body_pad = body.newObject("PartDesign::Pad", "BodyPrism")
body_pad.Profile = body_sketch
body_pad.Length = bodyHeight
doc.recompute()

tab_sketch = body.newObject("Sketcher::SketchObject", "TabSketch")
tab_sketch.AttachmentSupport = [(xy, "")]
tab_sketch.MapMode = "FlatFace"
tab_sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, bodyHeight), FreeCAD.Rotation())
for i in range(int(tabCount)):
    add_rect(tab_sketch, firstTabX + i * tabPitch, 0.0, tabWidth, overallWidth)

tab_pad = body.newObject("PartDesign::Pad", "TopTabs")
tab_pad.Profile = tab_sketch
tab_pad.Length = tabHeight
doc.recompute()

xz = next(f for f in body.Origin.OriginFeatures if "XZ" in f.Name and "Plane" in f.Name)
gap_starts = []
for k in range(int(legGroupCount)):
    b = endBlockLength + k * legGroupPitch
    gap_starts.extend(
        (
            b,
            b + gapWidth + mediumLegWidth,
            b + 2.0 * gapWidth + mediumLegWidth + smallLegWidth,
        )
    )
assert len(gap_starts) >= 1, "infeasible: expected at least one inter-leg gap"
assert gap_starts[-1] + gapWidth < overallLength, "infeasible: last gap would pass the far end"
assert gap_starts[-1] + gapWidth + largeLegWidth <= overallLength + 1e-9, (
    "infeasible: last large foot would pass the far end"
)

gap_sketch = body.newObject("Sketcher::SketchObject", "GapSketch")
gap_sketch.AttachmentSupport = [(xz, "")]
gap_sketch.MapMode = "FlatFace"
for a in gap_starts:
    add_poly(
        gap_sketch,
        [
            (a, 0.0),
            (a + gapWidth, 0.0),
            (a + gapWidth, legMergeHeight),
            (a, gapLowHeight),
        ],
    )

gap_pocket = body.newObject("PartDesign::Pocket", "InterLegGaps")
gap_pocket.Profile = gap_sketch
gap_pocket.Type = "ThroughAll"
doc.recompute()

cavity_y0 = l10OuterWallThickness
cavity_y1 = l10OuterWallThickness + l10CavityWidth
w1_lo = wall1CenterY - singleTrackWidth / 2.0
w1_hi = wall1CenterY + singleTrackWidth / 2.0
w2_lo = wall2CenterY - doubleTrackWidth / 2.0
w2_hi = wall2CenterY + doubleTrackWidth / 2.0
w3_lo = wall3CenterY - singleTrackWidth / 2.0
w3_hi = wall3CenterY + singleTrackWidth / 2.0
w4_lo = wall4CenterY - doubleTrackWidth / 2.0
w4_hi = wall4CenterY + doubleTrackWidth / 2.0
assert thinWallCount >= 1, "infeasible: expected internal walls"
pocket_spans = [
    (cavity_y0, w1_lo),
    (w1_hi, w2_lo),
    (w2_hi, w3_lo),
    (w3_hi, w4_lo),
    (w4_hi, cavity_y1),
]
assert len(pocket_spans) == 5, "infeasible: L10 must keep five sealed pockets"
for y0, y1 in pocket_spans:
    assert y1 > y0, "infeasible: L10 pocket span collapsed (walls overlap)"
    assert y0 >= 0, "infeasible: L10 pocket left the body"
    assert y1 <= overallWidth, "infeasible: L10 pocket left the body"

cavity_sketch = body.newObject("Sketcher::SketchObject", "CavitySketch")
cavity_sketch.AttachmentSupport = [(xy, "")]
cavity_sketch.MapMode = "FlatFace"
cavity_sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, l10BaseThickness), FreeCAD.Rotation())
for y0, y1 in pocket_spans:
    add_rect(cavity_sketch, l10CavityStartX, y0, l10CavityLength, y1 - y0)

cavity_pocket = body.newObject("PartDesign::Pocket", "L10Pockets")
cavity_pocket.Profile = cavity_sketch
cavity_pocket.Type = "Length"
cavity_pocket.Length = thinWallHeight
cavity_pocket.Reversed = True
cavity_pocket.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
assert body.Shape.Solids, "kernel: body has no solid"
for feat in body.Group:
    if hasattr(feat, "isValid"):
        assert feat.isValid(), f"kernel: {feat.Name} is invalid after recompute"
buildPlateContacts = (
    "buildPlateEndBlock",
    "buildPlateL1",
    "buildPlateL2",
    "buildPlateL3",
    "buildPlateL4",
    "buildPlateL5",
    "buildPlateL6",
    "buildPlateL7",
    "buildPlateL8",
    "buildPlateL9",
    "buildPlateL10",
    "buildPlateL11",
    "buildPlateL12",
)
metrologyTabTops = tuple(f"tabTop{i:02d}" for i in range(1, int(tabCount) + 1))
sideAndEndDatums = ("sideDatumY0", "oppositeSideY5", "farEndX75")
sealedL10Pockets = (
    "l10Pocket1Floor",
    "l10Pocket1Ceiling",
    "l10Pocket2Floor",
    "l10Pocket2Ceiling",
    "l10Pocket3Floor",
    "l10Pocket3Ceiling",
    "l10Pocket4Floor",
    "l10Pocket4Ceiling",
    "l10Pocket5Floor",
    "l10Pocket5Ceiling",
)
assert len(buildPlateContacts) == 13, "infeasible: expected thirteen build-plate contacts"
assert len(metrologyTabTops) == int(tabCount), "infeasible: tab-top names must match tabCount"
assert len(sideAndEndDatums) == 3, "infeasible: expected three frame faces"
assert len(sealedL10Pockets) == 10, "infeasible: expected ten L10 pocket faces"
result = body
