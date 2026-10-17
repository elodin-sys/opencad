import cadquery as cq

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
legCount = 12.0
tabCount = 11.0
outerWallThickness = 0.5
thinWallCount = 4.0
singleWallCount = 2.0
doubleWallCount = 2.0
overallHeight = 12.5
legMergeHeight = 7.0
legPatternCount = 4.0
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

assert bodyHeight > 0, "infeasible: bodyHeight must be positive"
assert tabHeight > 0, "infeasible: tabHeight must be positive"
assert singleWallWidth > 0, "infeasible: singleWallWidth must be positive"
assert doubleWallWidth > 0, "infeasible: doubleWallWidth must be positive"
assert tabWidth < tabPitch, "infeasible: tabWidth must leave a gap to the next tab"
assert (
    min(
        overallLength,
        bodyWidth,
        noseLength,
        legStraightHeight,
        overhangRise,
        gapWidth,
        wideLegWidth,
        mediumLegWidth,
        thinLegWidth,
        legPatternPitch,
        tabWidth,
        tabPitch,
        cavityLength,
        baseThickness,
        thinWallHeight,
        noseAngle,
        overhangAngle,
        legCount,
        tabCount,
        outerWallThickness,
        thinWallCount,
        singleWallCount,
        doubleWallCount,
        overallHeight,
        legMergeHeight,
        legPatternCount,
        endBlockLength,
        firstTabX,
        l10StartX,
        cavityStartX,
        cavityWidth,
        cavityCeilingZ,
    )
    > 0
), "infeasible: contract parameters must be positive"
assert int(tabCount) == tabCount, "infeasible: tabCount must be an integer"
assert int(legPatternCount) == legPatternCount, "infeasible: legPatternCount must be an integer"
assert int(legCount) == legCount, "infeasible: legCount must be an integer"

cutOverrun = 0.02

body = (
    cq.Workplane("XY")
    .polyline(
        [
            (0.0, bodyWidth / 2.0),
            (noseLength, 0.0),
            (overallLength, 0.0),
            (overallLength, bodyWidth),
            (noseLength, bodyWidth),
        ]
    )
    .close()
    .extrude(bodyHeight)
)

tabs = None
for i in range(int(tabCount)):
    tab = (
        cq.Workplane("XY")
        .box(tabWidth, bodyWidth, tabHeight, centered=(False, False, False))
        .translate((firstTabX + i * tabPitch, 0.0, bodyHeight))
    )
    tabs = tab if tabs is None else tabs.union(tab)

stock = body.union(tabs, clean=True)

gapStarts = []
for k in range(int(legPatternCount)):
    base = endBlockLength + k * legPatternPitch
    gapStarts.append(base)
    gapStarts.append(base + gapWidth + mediumLegWidth)
    gapStarts.append(base + 2.0 * gapWidth + mediumLegWidth + thinLegWidth)

gapTools = None
for a in gapStarts:
    gap = (
        cq.Workplane("XZ")
        .workplane(offset=-(bodyWidth + cutOverrun))
        .polyline(
            [
                (a, -cutOverrun),
                (a + gapWidth, -cutOverrun),
                (a + gapWidth, legMergeHeight),
                (a, legStraightHeight),
            ]
        )
        .close()
        .extrude(bodyWidth + 2.0 * cutOverrun)
    )
    gapTools = gap if gapTools is None else gapTools.union(gap)

legged = stock.cut(gapTools, clean=True)

pocketSpans = [
    (outerWallThickness, singleWall1Y - singleWallWidth / 2.0),
    (singleWall1Y + singleWallWidth / 2.0, doubleWall1Y - doubleWallWidth / 2.0),
    (doubleWall1Y + doubleWallWidth / 2.0, singleWall2Y - singleWallWidth / 2.0),
    (singleWall2Y + singleWallWidth / 2.0, doubleWall2Y - doubleWallWidth / 2.0),
    (doubleWall2Y + doubleWallWidth / 2.0, outerWallThickness + cavityWidth),
]
for y0, y1 in pocketSpans:
    assert y1 > y0, "infeasible: L10 internal walls overlap or invert a pocket"

pocketTools = None
for y0, y1 in pocketSpans:
    pocket = (
        cq.Workplane("XY")
        .box(cavityLength, y1 - y0, thinWallHeight, centered=(False, False, False))
        .translate((cavityStartX, y0, baseThickness))
    )
    pocketTools = pocket if pocketTools is None else pocketTools.union(pocket)

bridge = legged.cut(pocketTools, clean=True)

result = (
    bridge.faces(cq.NearestToPointSelector((10.0, bodyWidth / 2.0, 0.0)))
    .tag("buildContactEndBlock")
    .end()
    .faces(cq.NearestToPointSelector((72.5, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL01")
    .end()
    .faces(cq.NearestToPointSelector((67.75, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL02")
    .end()
    .faces(cq.NearestToPointSelector((64.25, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL03")
    .end()
    .faces(cq.NearestToPointSelector((58.5, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL04")
    .end()
    .faces(cq.NearestToPointSelector((53.75, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL05")
    .end()
    .faces(cq.NearestToPointSelector((50.25, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL06")
    .end()
    .faces(cq.NearestToPointSelector((44.5, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL07")
    .end()
    .faces(cq.NearestToPointSelector((39.75, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL08")
    .end()
    .faces(cq.NearestToPointSelector((36.25, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL09")
    .end()
    .faces(cq.NearestToPointSelector((30.5, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL10")
    .end()
    .faces(cq.NearestToPointSelector((25.75, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL11")
    .end()
    .faces(cq.NearestToPointSelector((22.25, bodyWidth / 2.0, 0.0)))
    .tag("buildContactL12")
    .end()
    .faces(cq.NearestToPointSelector((4.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop01")
    .end()
    .faces(cq.NearestToPointSelector((11.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop02")
    .end()
    .faces(cq.NearestToPointSelector((18.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop03")
    .end()
    .faces(cq.NearestToPointSelector((25.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop04")
    .end()
    .faces(cq.NearestToPointSelector((32.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop05")
    .end()
    .faces(cq.NearestToPointSelector((39.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop06")
    .end()
    .faces(cq.NearestToPointSelector((46.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop07")
    .end()
    .faces(cq.NearestToPointSelector((53.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop08")
    .end()
    .faces(cq.NearestToPointSelector((60.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop09")
    .end()
    .faces(cq.NearestToPointSelector((67.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop10")
    .end()
    .faces(cq.NearestToPointSelector((74.5, bodyWidth / 2.0, bodyHeight + tabHeight)))
    .tag("tabTop11")
    .end()
    .faces(cq.NearestToPointSelector((40.0, 0.0, bodyHeight / 2.0)))
    .tag("sideY0")
    .end()
    .faces(cq.NearestToPointSelector((40.0, bodyWidth, bodyHeight / 2.0)))
    .tag("sideY5")
    .end()
    .faces(cq.NearestToPointSelector((overallLength, bodyWidth / 2.0, (bodyHeight + tabHeight) / 2.0)))
    .tag("farEnd")
    .end()
)
