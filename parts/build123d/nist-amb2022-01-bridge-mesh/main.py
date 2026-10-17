import math

from build123d import Align, Box, Compound, Plane, Polygon, Pos, extrude

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

assert min(overallLength, overallWidth, bodyHeight, noseLength, tabHeight) > 0, (
    "infeasible: envelope extents must be positive"
)
assert 0.0 < noseAngle < 90.0, "infeasible: noseAngle must be an acute plan taper"
assert 0.0 < overhangAngle < 90.0, "infeasible: overhangAngle must be an acute rise"
assert min(legCount, tabCount, thinWallCount, legGroupCount) > 0, "infeasible: counts must be positive"
assert min(largeLegWidth, mediumLegWidth, smallLegWidth, gapWidth, legGroupPitch, endBlockLength) > 0, (
    "infeasible: leg extents must be positive"
)
assert min(tabWidth, tabPitch, firstTabX) > 0, "infeasible: tab extents must be positive"
assert (
    min(
        l10StartX,
        l10OuterWallThickness,
        l10BaseThickness,
        thinWallHeight,
        l10CavityLength,
        l10CavityWidth,
        l10CavityStartX,
    )
    > 0
), "infeasible: L10 extents must be positive"
assert min(legMergeHeight, gapLowHeight, l10CeilingZ) > 0, "infeasible: height stations must be positive"
assert min(singleTrackWidth, doubleTrackWidth, wall1CenterY, wall2CenterY, wall3CenterY, wall4CenterY) > 0, (
    "infeasible: thin-wall sizes must be positive"
)
assert bodyHeight > legMergeHeight, "infeasible: bodyHeight must clear the overhang merge"
assert tabWidth < tabPitch, "infeasible: tabWidth must leave a gap between tabs"
assert firstTabX > noseLength, "infeasible: first tab must sit behind the nose shoulder"
assert l10BaseThickness < l10CeilingZ, "infeasible: L10 base must sit below the cavity ceiling"
assert l10CeilingZ < legMergeHeight, "infeasible: cavity ceiling must sit below the merge plane"
assert l10CavityStartX > l10StartX, "infeasible: L10 cavity must start inside the wide-leg outer wall"
assert l10CavityStartX + l10CavityLength < l10StartX + largeLegWidth, (
    "infeasible: L10 cavity must end inside the wide-leg outer wall"
)
assert l10OuterWallThickness + l10CavityWidth < overallWidth, "infeasible: L10 cavity must leave a far-side outer wall"
assert int(legCount) == legCount, "infeasible: legCount must be an integer"
assert int(tabCount) == tabCount, "infeasible: tabCount must be an integer"
assert int(legGroupCount) == legGroupCount, "infeasible: legGroupCount must be an integer"
assert int(thinWallCount) == thinWallCount, "infeasible: thinWallCount must be an integer"

cut_overshoot = 0.05
roof_high = gapLowHeight + gapWidth * math.tan(math.radians(overhangAngle))
assert roof_high < bodyHeight, "infeasible: gap roof must stay below the bridge top"

footprint = Polygon(
    (0.0, overallWidth / 2.0),
    (noseLength, 0.0),
    (overallLength, 0.0),
    (overallLength, overallWidth),
    (noseLength, overallWidth),
)
body = extrude(footprint, amount=bodyHeight, dir=(0, 0, 1))
tabs = Compound(
    [
        Pos(firstTabX + i * tabPitch, 0.0, bodyHeight)
        * Box(tabWidth, overallWidth, tabHeight, align=(Align.MIN, Align.MIN, Align.MIN))
        for i in range(int(tabCount))
    ]
)
stock = body + tabs

gap_starts = []
for k in range(int(legGroupCount)):
    base = endBlockLength + k * legGroupPitch
    gap_starts.extend(
        [
            base,
            base + gapWidth + mediumLegWidth,
            base + 2.0 * gapWidth + mediumLegWidth + smallLegWidth,
        ]
    )
assert len(gap_starts) == int(legCount), "infeasible: twelve gaps required for twelve legs"
assert gap_starts[-1] + gapWidth < overallLength, "infeasible: last gap must finish before the far end"

gap_plane = Plane.XZ.offset(cut_overshoot)
gap_tools = []
for start in gap_starts:
    profile = gap_plane * Polygon(
        (start, -cut_overshoot),
        (start + gapWidth, -cut_overshoot),
        (start + gapWidth, roof_high),
        (start, gapLowHeight),
        align=None,
    )
    gap_tools.append(extrude(profile, amount=-(overallWidth + 2.0 * cut_overshoot)))
legged = stock - Compound(gap_tools)

cavity_y0 = l10OuterWallThickness
cavity_y1 = l10OuterWallThickness + l10CavityWidth
declared_walls = [
    (wall1CenterY, singleTrackWidth),
    (wall2CenterY, doubleTrackWidth),
    (wall3CenterY, singleTrackWidth),
    (wall4CenterY, doubleTrackWidth),
]
walls = sorted(declared_walls[: int(thinWallCount)], key=lambda item: item[0])
prev_hi = cavity_y0
wall_edges = [cavity_y0]
for center_y, width in walls:
    lo, hi = center_y - width / 2.0, center_y + width / 2.0
    assert lo > prev_hi, "infeasible: thin walls must not overlap or leave the cavity"
    assert hi < cavity_y1, "infeasible: thin walls must stay inside the L10 cavity"
    wall_edges.extend([lo, hi])
    prev_hi = hi
wall_edges.append(cavity_y1)
assert len(wall_edges) == 2 * int(thinWallCount) + 2, "infeasible: four internal walls must bound five pockets"

pocket_tools = []
for i in range(0, len(wall_edges), 2):
    y0, y1 = wall_edges[i], wall_edges[i + 1]
    assert y1 > y0, "infeasible: L10 pocket span must be positive"
    pocket_tools.append(
        Pos(l10CavityStartX, y0, l10BaseThickness)
        * Box(l10CavityLength, y1 - y0, thinWallHeight, align=(Align.MIN, Align.MIN, Align.MIN))
    )
result = legged - Compound(pocket_tools)
