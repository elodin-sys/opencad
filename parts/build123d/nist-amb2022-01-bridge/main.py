from build123d import Align, Axis, Box, Compound, Plane, Polygon, Pos, extrude

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

assert min(overallLength, bodyWidth, bodyHeight, noseLength) > 0, "infeasible: envelope extents must be positive"
assert min(legStraightHeight, overhangRise, gapWidth) > 0, "infeasible: gap extents must be positive"
assert min(wideLegWidth, mediumLegWidth, thinLegWidth, legPatternPitch) > 0, "infeasible: leg extents must be positive"
assert min(tabWidth, tabPitch, tabHeight) > 0, "infeasible: tab extents must be positive"
assert min(cavityLength, baseThickness, thinWallHeight, outerWallThickness) > 0, (
    "infeasible: L10 extents must be positive"
)
assert 0.0 < noseAngle < 90.0, "infeasible: noseAngle must be an acute plan taper"
assert 0.0 < overhangAngle < 90.0, "infeasible: overhangAngle must be an acute rise"
assert min(legCount, tabCount, thinWallCount, singleWallCount, doubleWallCount, legPatternCount) > 0, (
    "infeasible: counts must be positive"
)
assert min(overallHeight, legMergeHeight, endBlockLength, firstTabX, l10StartX) > 0, (
    "infeasible: derived extents must be positive"
)
assert min(cavityStartX, cavityWidth, cavityCeilingZ) > 0, "infeasible: cavity extents must be positive"
assert min(singleWall1Y, doubleWall1Y, singleWall2Y, doubleWall2Y, singleWallWidth, doubleWallWidth) > 0, (
    "infeasible: wall locations must be positive"
)
assert bodyHeight > legMergeHeight, "infeasible: bodyHeight must clear the overhang merge"
assert tabWidth < tabPitch, "infeasible: tabWidth must leave a gap between tabs"
assert firstTabX > noseLength, "infeasible: first tab must sit behind the nose shoulder"
assert baseThickness < cavityCeilingZ, "infeasible: L10 base must sit below the cavity ceiling"
assert cavityCeilingZ < legMergeHeight, "infeasible: cavity ceiling must sit below the merge plane"
assert cavityStartX > l10StartX, "infeasible: L10 cavity must start inside the wide-leg outer wall"
assert cavityStartX + cavityLength < l10StartX + wideLegWidth, (
    "infeasible: L10 cavity must end inside the wide-leg outer wall"
)
assert outerWallThickness + cavityWidth < bodyWidth, "infeasible: L10 cavity must leave a far-side outer wall"
assert int(legCount) == legCount, "infeasible: legCount must be an integer"
assert int(tabCount) == tabCount, "infeasible: tabCount must be an integer"
assert int(legPatternCount) == legPatternCount, "infeasible: legPatternCount must be an integer"
assert int(thinWallCount) == thinWallCount, "infeasible: thinWallCount must be an integer"
assert int(singleWallCount) == singleWallCount, "infeasible: singleWallCount must be an integer"
assert int(doubleWallCount) == doubleWallCount, "infeasible: doubleWallCount must be an integer"

cut_overshoot = 0.05

footprint = Polygon(
    (0.0, bodyWidth / 2.0),
    (noseLength, 0.0),
    (overallLength, 0.0),
    (overallLength, bodyWidth),
    (noseLength, bodyWidth),
)
body = extrude(footprint, amount=bodyHeight, dir=(0, 0, 1))
tabs = Compound(
    [
        Pos(firstTabX + i * tabPitch, 0.0, bodyHeight)
        * Box(tabWidth, bodyWidth, tabHeight, align=(Align.MIN, Align.MIN, Align.MIN))
        for i in range(int(tabCount))
    ]
)
stock = body + tabs

gap_starts = []
for k in range(int(legPatternCount)):
    base = endBlockLength + k * legPatternPitch
    gap_starts.extend(
        [
            base,
            base + gapWidth + mediumLegWidth,
            base + 2.0 * gapWidth + mediumLegWidth + thinLegWidth,
        ]
    )
assert gap_starts[-1] + gapWidth < overallLength, "infeasible: last gap must finish before the far end"

gap_plane = Plane.XZ.offset(cut_overshoot)
gap_tools = []
for start in gap_starts:
    profile = gap_plane * Polygon(
        (start, -cut_overshoot),
        (start + gapWidth, -cut_overshoot),
        (start + gapWidth, legMergeHeight),
        (start, legStraightHeight),
        align=None,
    )
    gap_tools.append(extrude(profile, amount=-(bodyWidth + 2.0 * cut_overshoot)))
legged = stock - Compound(gap_tools)

single_ys = (singleWall1Y, singleWall2Y)[: int(singleWallCount)]
double_ys = (doubleWall1Y, doubleWall2Y)[: int(doubleWallCount)]
wall_edges = [outerWallThickness]
for y in single_ys:
    wall_edges.extend([y - singleWallWidth / 2.0, y + singleWallWidth / 2.0])
for y in double_ys:
    wall_edges.extend([y - doubleWallWidth / 2.0, y + doubleWallWidth / 2.0])
wall_edges.append(outerWallThickness + cavityWidth)
wall_edges.sort()
assert len(wall_edges) == 2 * int(thinWallCount) + 2, "infeasible: four internal walls must bound five pockets"

pocket_tools = []
for i in range(0, len(wall_edges), 2):
    y0, y1 = wall_edges[i], wall_edges[i + 1]
    assert y1 > y0, "infeasible: L10 pocket span must be positive"
    pocket_tools.append(
        Pos(cavityStartX, y0, baseThickness)
        * Box(cavityLength, y1 - y0, thinWallHeight, align=(Align.MIN, Align.MIN, Align.MIN))
    )
result = legged - Compound(pocket_tools)

contact_names = {
    (endBlockLength / 2.0, 88.75): "buildContactEndBlock",
    (70.0 + wideLegWidth / 2.0, 25.0): "buildContactL01",
    (67.5 + thinLegWidth / 2.0, 2.5): "buildContactL02",
    (63.0 + mediumLegWidth / 2.0, 12.5): "buildContactL03",
    (56.0 + wideLegWidth / 2.0, 25.0): "buildContactL04",
    (53.5 + thinLegWidth / 2.0, 2.5): "buildContactL05",
    (49.0 + mediumLegWidth / 2.0, 12.5): "buildContactL06",
    (42.0 + wideLegWidth / 2.0, 25.0): "buildContactL07",
    (39.5 + thinLegWidth / 2.0, 2.5): "buildContactL08",
    (35.0 + mediumLegWidth / 2.0, 12.5): "buildContactL09",
    (l10StartX + wideLegWidth / 2.0, 25.0): "buildContactL10",
    (25.5 + thinLegWidth / 2.0, 2.5): "buildContactL11",
    (21.0 + mediumLegWidth / 2.0, 12.5): "buildContactL12",
}
named = 0
for face in result.faces().filter_by(Axis.Z):
    centre = face.center()
    area = face.area
    if abs(centre.Z) <= 0.05:
        for (x, target_area), name in contact_names.items():
            if abs(centre.X - x) < 0.6 and abs(area - target_area) < 0.2:
                face.label = name
                named += 1
                break
    elif abs(centre.Z - (bodyHeight + tabHeight)) <= 0.05 or abs(centre.Z - overallHeight) <= 0.05:
        idx = round((centre.X - firstTabX - tabWidth / 2.0) / tabPitch)
        if 0 <= idx < int(tabCount) and abs(area - tabWidth * bodyWidth) < 0.2:
            face.label = f"tabTop{idx + 1:02d}"
            named += 1
for face in result.faces().filter_by(Axis.Y):
    centre = face.center()
    if abs(centre.Y) <= 0.05 and abs(face.area - 731.5) < 2.0:
        face.label = "sideY0"
        named += 1
    elif abs(centre.Y - bodyWidth) <= 0.05 and abs(face.area - 731.5) < 2.0:
        face.label = "sideY5"
        named += 1
for face in result.faces().filter_by(Axis.X):
    centre = face.center()
    if abs(centre.X - overallLength) <= 0.05 and abs(face.area - bodyWidth * overallHeight) < 0.5:
        face.label = "farEnd"
        named += 1
assert named >= 13, "expected named build contacts, tab tops, and frame faces"
