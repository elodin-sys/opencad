import cadquery as cq

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

assert bodyHeight > 0, "infeasible: bodyHeight must be positive"
assert tabHeight > 0, "infeasible: tabHeight must be positive"
assert overallLength > 0, "infeasible: overallLength must be positive"
assert overallWidth > 0, "infeasible: overallWidth must be positive"
assert noseLength > 0, "infeasible: noseLength must be positive"
assert singleTrackWidth > 0, "infeasible: singleTrackWidth must be positive"
assert doubleTrackWidth > 0, "infeasible: doubleTrackWidth must be positive"
assert 0.0 < noseAngle < 90.0, "infeasible: noseAngle must be an acute plan taper"
assert 0.0 < overhangAngle < 90.0, "infeasible: overhangAngle must be an acute rise"
assert (
    min(
        legCount,
        largeLegWidth,
        mediumLegWidth,
        smallLegWidth,
        gapWidth,
        legMergeHeight,
        gapLowHeight,
        legGroupCount,
        legGroupPitch,
        endBlockLength,
        tabCount,
        tabWidth,
        tabPitch,
        firstTabX,
        l10StartX,
        l10OuterWallThickness,
        l10BaseThickness,
        thinWallHeight,
        l10CavityLength,
        l10CavityWidth,
        l10CavityStartX,
        l10CeilingZ,
        thinWallCount,
        wall1CenterY,
        wall2CenterY,
        wall3CenterY,
        wall4CenterY,
    )
    > 0
), "infeasible: contract parameters must be positive"
assert tabWidth < tabPitch, "infeasible: tabWidth must leave a gap to the next tab"
assert l10CeilingZ > l10BaseThickness, "infeasible: L10 ceiling must sit above the solid base"
assert l10CavityStartX > l10StartX, "infeasible: L10 cavity must start inside the outer wall"
assert l10CavityStartX + l10CavityLength < l10StartX + largeLegWidth, (
    "infeasible: L10 cavity must end inside the outer wall"
)
assert int(tabCount) == tabCount, "infeasible: tabCount must be an integer"
assert int(legGroupCount) == legGroupCount, "infeasible: legGroupCount must be an integer"
assert int(legCount) == legCount, "infeasible: legCount must be an integer"
assert int(thinWallCount) == thinWallCount, "infeasible: thinWallCount must be an integer"

cutOverrun = 0.02

stock = (
    cq.Workplane("XY")
    .polyline(
        [
            (0.0, overallWidth / 2.0),
            (noseLength, 0.0),
            (overallLength, 0.0),
            (overallLength, overallWidth),
            (noseLength, overallWidth),
        ]
    )
    .close()
    .extrude(bodyHeight + tabHeight)
)

valleyTools = (
    cq.Workplane("XY")
    .box(
        firstTabX + cutOverrun,
        overallWidth + 2.0 * cutOverrun,
        tabHeight + cutOverrun,
        centered=(False, False, False),
    )
    .translate((-cutOverrun, -cutOverrun, bodyHeight))
)
for i in range(int(tabCount) - 1):
    x0 = firstTabX + i * tabPitch + tabWidth
    x1 = firstTabX + (i + 1) * tabPitch
    valley = (
        cq.Workplane("XY")
        .box(
            x1 - x0,
            overallWidth + 2.0 * cutOverrun,
            tabHeight + cutOverrun,
            centered=(False, False, False),
        )
        .translate((x0, -cutOverrun, bodyHeight))
    )
    valleyTools = valleyTools.union(valley)

tabbed = stock.cut(valleyTools, clean=True)

gapStarts = []
for k in range(int(legGroupCount)):
    base = endBlockLength + k * legGroupPitch
    gapStarts.append(base)
    gapStarts.append(base + gapWidth + mediumLegWidth)
    gapStarts.append(base + 2.0 * gapWidth + mediumLegWidth + smallLegWidth)

gapTools = None
for a in gapStarts:
    gap = (
        cq.Workplane("XZ")
        .workplane(offset=-(overallWidth + cutOverrun))
        .polyline(
            [
                (a, -cutOverrun),
                (a + gapWidth, -cutOverrun),
                (a + gapWidth, legMergeHeight),
                (a, gapLowHeight),
            ]
        )
        .close()
        .extrude(overallWidth + 2.0 * cutOverrun)
    )
    gapTools = gap if gapTools is None else gapTools.union(gap)

legged = tabbed.cut(gapTools, clean=True)

wallSpecs = (
    (wall1CenterY, singleTrackWidth),
    (wall2CenterY, doubleTrackWidth),
    (wall3CenterY, singleTrackWidth),
    (wall4CenterY, doubleTrackWidth),
)
assert len(wallSpecs) == int(thinWallCount), "infeasible: thinWallCount must match the four internal walls"

cavityY0 = l10OuterWallThickness
pocketSpans = []
yCursor = cavityY0
for center, width in wallSpecs:
    low = center - width / 2.0
    high = center + width / 2.0
    pocketSpans.append((yCursor, low))
    yCursor = high
pocketSpans.append((yCursor, cavityY0 + l10CavityWidth))
for y0, y1 in pocketSpans:
    assert y1 > y0, "infeasible: L10 internal walls overlap or invert a pocket"

pocketTools = None
for y0, y1 in pocketSpans:
    pocket = (
        cq.Workplane("XY")
        .box(l10CavityLength, y1 - y0, thinWallHeight, centered=(False, False, False))
        .translate((l10CavityStartX, y0, l10BaseThickness))
    )
    pocketTools = pocket if pocketTools is None else pocketTools.union(pocket)

bridge = legged.cut(pocketTools, clean=True)

tagged = bridge
endBlockX = (endBlockLength + noseLength) / 2.0
tagged = tagged.faces(cq.NearestToPointSelector((endBlockX, overallWidth / 2.0, 0.0))).tag("buildPlateEndBlock").end()
for k in range(int(legGroupCount)):
    base = endBlockLength + k * legGroupPitch
    mediumX = base + gapWidth + mediumLegWidth / 2.0
    smallX = base + 2.0 * gapWidth + mediumLegWidth + smallLegWidth / 2.0
    largeX = base + 3.0 * gapWidth + mediumLegWidth + smallLegWidth + largeLegWidth / 2.0
    # L12..L1: each group is medium, small, large walking +x, numbered from the far end.
    names = (
        f"buildPlateL{12 - 3 * k}",
        f"buildPlateL{11 - 3 * k}",
        f"buildPlateL{10 - 3 * k}",
    )
    for name, xMid in zip(names, (mediumX, smallX, largeX), strict=True):
        tagged = tagged.faces(cq.NearestToPointSelector((xMid, overallWidth / 2.0, 0.0))).tag(name).end()

for i in range(int(tabCount)):
    tabX = firstTabX + i * tabPitch + tabWidth / 2.0
    tagged = (
        tagged.faces(cq.NearestToPointSelector((tabX, overallWidth / 2.0, bodyHeight + tabHeight)))
        .tag(f"tabTop{i + 1:02d}")
        .end()
    )

pocketMidX = l10CavityStartX + l10CavityLength / 2.0
for i, (y0, y1) in enumerate(pocketSpans):
    yMid = (y0 + y1) / 2.0
    n = i + 1
    tagged = (
        tagged.faces(cq.NearestToPointSelector((pocketMidX, yMid, l10BaseThickness)))
        .tag(f"l10Pocket{n}Floor")
        .end()
        .faces(cq.NearestToPointSelector((pocketMidX, yMid, l10CeilingZ)))
        .tag(f"l10Pocket{n}Ceiling")
        .end()
    )

result = (
    tagged.faces(cq.NearestToPointSelector((overallLength / 2.0, 0.0, bodyHeight / 2.0)))
    .tag("sideDatumY0")
    .end()
    .faces(cq.NearestToPointSelector((overallLength / 2.0, overallWidth, bodyHeight / 2.0)))
    .tag("oppositeSideY5")
    .end()
    .faces(cq.NearestToPointSelector((overallLength, overallWidth / 2.0, (bodyHeight + tabHeight) / 2.0)))
    .tag("farEndX75")
    .end()
)
