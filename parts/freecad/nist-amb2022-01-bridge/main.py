import math

import FreeCAD
import Part
import Sketcher

overallLength = 75.0
bodyWidth = 5.0
bodyHeight = 12.0
noseLength = 2.5
legStraightHeight = 5.0
overhangRise = 2.0
gapWidth = 2.0
wideLegWidth = 5.0
mediumLegWidth = 2.5
thinLegWidth = 0.5
legPatternPitch = 14.0
tabWidth = 1.0
tabPitch = 7.0
tabHeight = 0.5
cavityLength = 4.0
baseThickness = 1.0
thinWallHeight = 4.0
noseAngle = 45.0
overhangAngle = 45.0
legCount = 12
tabCount = 11
outerWallThickness = 0.5
thinWallCount = 4
singleWallCount = 2
doubleWallCount = 2
overallHeight = 12.5
legMergeHeight = 7.0
legPatternCount = 4
endBlockLength = 19.0
firstTabX = 4.0
l10StartX = 28.0
cavityStartX = 28.5
cavityWidth = 4.0
cavityCeilingZ = 5.0
singleWall1Y = 1.3
doubleWall1Y = 2.05
singleWall2Y = 2.9
doubleWall2Y = 3.65
singleWallWidth = 0.1
doubleWallWidth = 0.2

assert overallLength > 0, "infeasible: overallLength must be positive"
assert bodyWidth > 0, "infeasible: bodyWidth must be positive"
assert bodyHeight > 0, "infeasible: bodyHeight must be positive"
assert noseLength > 0, "infeasible: noseLength must stay on the +x side of the tip"
assert noseLength < endBlockLength, "infeasible: noseLength must end before the first gap"
assert noseLength < overallLength, "infeasible: noseLength must stay inside overallLength"
assert tabWidth > 0, "infeasible: tabWidth must be positive"
assert tabPitch > 0, "infeasible: tabPitch must be positive"
assert tabWidth < tabPitch, "infeasible: tabWidth must leave a gap between tabs"
assert tabHeight > 0, "infeasible: tabHeight must be positive"
assert tabCount >= 1, "infeasible: tabCount must place at least one tab"
assert firstTabX >= 0, "infeasible: firstTabX must stay on the +x side of the tip"
assert firstTabX > noseLength, "infeasible: first tab must sit behind the nose shoulder"
assert firstTabX + (tabCount - 1) * tabPitch + tabWidth <= overallLength + 1e-9, (
    "infeasible: last tab would pass the far end"
)
assert singleWallWidth > 0, "infeasible: singleWallWidth must be positive"
assert doubleWallWidth > 0, "infeasible: doubleWallWidth must be positive"
assert 0 < noseAngle < 90, "infeasible: noseAngle must be an acute taper"
assert 0 < overhangAngle < 90, "infeasible: overhangAngle must be an acute rise"
assert math.tan(math.radians(overhangAngle)) > 0, "infeasible: overhangAngle must rise"
assert gapWidth > 0, "infeasible: gapWidth must be positive"
assert wideLegWidth > 0, "infeasible: wideLegWidth must be positive"
assert mediumLegWidth > 0, "infeasible: mediumLegWidth must be positive"
assert thinLegWidth > 0, "infeasible: thinLegWidth must be positive"
assert legStraightHeight > 0, "infeasible: legStraightHeight must be positive"
assert overhangRise > 0, "infeasible: overhangRise must be positive"
assert bodyHeight > legStraightHeight + overhangRise, "infeasible: bodyHeight must clear the overhang merge"
assert bodyHeight > legMergeHeight, "infeasible: bodyHeight must sit above the merge plane"
assert baseThickness > 0, "infeasible: baseThickness must be positive"
assert thinWallHeight > 0, "infeasible: thinWallHeight must be positive"
assert cavityCeilingZ > baseThickness, "infeasible: cavityCeilingZ must sit above the L10 base"
assert cavityLength > 0, "infeasible: cavityLength must be positive"
assert cavityWidth > 0, "infeasible: cavityWidth must be positive"
assert outerWallThickness > 0, "infeasible: outerWallThickness must be positive"
assert outerWallThickness + cavityWidth < bodyWidth, "infeasible: L10 outer walls must leave a cavity"
assert l10StartX > endBlockLength, "infeasible: L10 must sit after the end block"
assert cavityStartX > l10StartX, "infeasible: L10 cavity must sit inside the outer +x wall"
assert cavityStartX + cavityLength < l10StartX + wideLegWidth, "infeasible: L10 cavity must sit inside the far x-wall"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
# Tab tops follow bodyHeight+tabHeight; overallHeight is a published reference rewritten on its own.
actualTopZ = bodyHeight + tabHeight
assert actualTopZ > bodyHeight, "infeasible: tabHeight must raise the tab tops above the body"
assert actualTopZ > legMergeHeight, "infeasible: tab tops must sit above the merge plane"
assert legCount >= 1, "infeasible: legCount must place at least one leg"
assert legPatternCount >= 1, "infeasible: legPatternCount must place at least one repeat"
assert thinWallCount >= 1, "infeasible: thinWallCount must place at least one partition"
assert singleWallCount >= 1, "infeasible: singleWallCount must place at least one wall"
assert doubleWallCount >= 1, "infeasible: doubleWallCount must place at least one wall"


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


doc = FreeCAD.newDocument("nist-amb2022-01-bridge")
body = doc.addObject("PartDesign::Body", "Body")
body.AllowCompound = False
doc.recompute()
xy = next(f for f in body.Origin.OriginFeatures if "XY" in f.Name and "Plane" in f.Name)

half_w = bodyWidth / 2.0
body_sketch = body.newObject("Sketcher::SketchObject", "BodySketch")
body_sketch.AttachmentSupport = [(xy, "")]
body_sketch.MapMode = "FlatFace"
add_poly(
    body_sketch,
    [
        (0.0, half_w),
        (noseLength, 0.0),
        (overallLength, 0.0),
        (overallLength, bodyWidth),
        (noseLength, bodyWidth),
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
    add_rect(tab_sketch, firstTabX + i * tabPitch, 0.0, tabWidth, bodyWidth)

tab_pad = body.newObject("PartDesign::Pad", "TopTabs")
tab_pad.Profile = tab_sketch
tab_pad.Length = tabHeight
doc.recompute()

xz = next(f for f in body.Origin.OriginFeatures if "XZ" in f.Name and "Plane" in f.Name)
gap_starts = []
for k in range(int(legPatternCount)):
    b = endBlockLength + k * legPatternPitch
    gap_starts.extend(
        (
            b,
            b + gapWidth + mediumLegWidth,
            b + 2.0 * gapWidth + mediumLegWidth + thinLegWidth,
        )
    )
assert len(gap_starts) == int(legCount), "infeasible: gap count must match legCount"
assert gap_starts[-1] + gapWidth < overallLength, "infeasible: last gap would pass the far end"

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
            (a, legStraightHeight),
        ],
    )

gap_pocket = body.newObject("PartDesign::Pocket", "InterLegGaps")
gap_pocket.Profile = gap_sketch
gap_pocket.Type = "ThroughAll"
doc.recompute()

s1_lo = singleWall1Y - singleWallWidth / 2.0
s1_hi = singleWall1Y + singleWallWidth / 2.0
d1_lo = doubleWall1Y - doubleWallWidth / 2.0
d1_hi = doubleWall1Y + doubleWallWidth / 2.0
s2_lo = singleWall2Y - singleWallWidth / 2.0
s2_hi = singleWall2Y + singleWallWidth / 2.0
d2_lo = doubleWall2Y - doubleWallWidth / 2.0
d2_hi = doubleWall2Y + doubleWallWidth / 2.0
cavity_y0 = outerWallThickness
cavity_y1 = outerWallThickness + cavityWidth
pocket_spans = [
    (cavity_y0, s1_lo),
    (s1_hi, d1_lo),
    (d1_hi, s2_lo),
    (s2_hi, d2_lo),
    (d2_hi, cavity_y1),
]
assert len(pocket_spans) == 5, "infeasible: L10 must keep five sealed pockets"
for y0, y1 in pocket_spans:
    assert y1 > y0, "infeasible: L10 pocket span collapsed (walls overlap)"
    assert y0 >= 0, "infeasible: L10 pocket left the body"
    assert y1 <= bodyWidth, "infeasible: L10 pocket left the body"

cavity_sketch = body.newObject("Sketcher::SketchObject", "CavitySketch")
cavity_sketch.AttachmentSupport = [(xy, "")]
cavity_sketch.MapMode = "FlatFace"
cavity_sketch.AttachmentOffset = FreeCAD.Placement(FreeCAD.Vector(0, 0, baseThickness), FreeCAD.Rotation())
for y0, y1 in pocket_spans:
    add_rect(cavity_sketch, cavityStartX, y0, cavityLength, y1 - y0)

cavity_pocket = body.newObject("PartDesign::Pocket", "L10Pockets")
cavity_pocket.Profile = cavity_sketch
cavity_pocket.Type = "Length"
cavity_pocket.Length = thinWallHeight
cavity_pocket.Reversed = True
cavity_pocket.Refine = True
doc.recompute()

assert body.Shape.isValid(), "kernel: body shape is invalid after recompute"
assert body.Shape.Solids, "kernel: body has no solid"
buildPlateContacts = (
    "buildContactEndBlock",
    "buildContactL01",
    "buildContactL02",
    "buildContactL03",
    "buildContactL04",
    "buildContactL05",
    "buildContactL06",
    "buildContactL07",
    "buildContactL08",
    "buildContactL09",
    "buildContactL10",
    "buildContactL11",
    "buildContactL12",
)
displacementTabTops = tuple(f"tabTop{i:02d}" for i in range(1, int(tabCount) + 1))
frameSideAndEndFaces = ("sideY0", "sideY5", "farEnd")
assert len(buildPlateContacts) == 13, "infeasible: expected thirteen build-plate contacts"
assert len(displacementTabTops) == 11, "infeasible: expected eleven tab tops"
assert len(frameSideAndEndFaces) == 3, "infeasible: expected three frame faces"
result = body
