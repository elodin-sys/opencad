import cadquery as cq
from params import (
    bodyTopZ,
    bottomZ,
    halfWidth,
    leftFootX,
    leftShoulderZ,
    lugBossDiameter,
    lugMaxZ,
    lugNutX,
    lugNutZ,
    lugWebPeakX,
    overallHeight,
    plateThickness,
    plateWidth,
)

assert plateWidth > 0, "infeasible: plateWidth must be positive"
assert halfWidth > 0, "infeasible: halfWidth must be positive"
assert plateThickness > 0, "infeasible: plateThickness must be positive"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
assert bottomZ < leftShoulderZ < bodyTopZ < lugMaxZ, "infeasible: housing levels must be ordered"
assert -halfWidth < leftFootX < halfWidth, "infeasible: foot must lie within the plate width"
assert lugBossDiameter > 0, "infeasible: lugBossDiameter must be positive"
assert -halfWidth < lugNutX - lugBossDiameter / 2.0, "infeasible: lug crosses the left envelope"
assert lugNutX + lugBossDiameter / 2.0 < halfWidth, "infeasible: lug crosses the right envelope"
assert lugNutZ - lugBossDiameter / 2.0 < bodyTopZ, "infeasible: lug must intersect the plate"
assert bodyTopZ < lugNutZ + lugBossDiameter / 2.0 <= lugMaxZ, "infeasible: lug must fit below the web peak"
assert lugNutX < lugWebPeakX < halfWidth, "infeasible: rear web must fit beside the lug"

# Rebuild the passed blockout: plate and square foot, circular lug, rear-half web.
# XZ has normal -Y; negative extrusion puts the back at y=0 and the front at y=14.
# Exterior sculpting and all functional cavities belong to the later modules.
plateOutline = [
    (-halfWidth, leftShoulderZ),
    (leftFootX, leftShoulderZ),
    (leftFootX, bottomZ),
    (halfWidth, bottomZ),
    (halfWidth, bodyTopZ),
    (-halfWidth, bodyTopZ),
]
plate = cq.Workplane("XZ").polyline(plateOutline).close().extrude(-plateThickness)

upperLug = cq.Workplane("XZ", origin=(lugNutX, 0.0, lugNutZ)).circle(lugBossDiameter / 2.0).extrude(-plateThickness)

rearWebDepth = plateThickness / 2.0
rearWebOutline = [
    (lugNutX, bodyTopZ),
    (lugWebPeakX, bodyTopZ),
    (lugWebPeakX, lugMaxZ),
    (lugNutX, lugMaxZ),
]
rearWeb = cq.Workplane("XZ").polyline(rearWebOutline).close().extrude(-rearWebDepth)

datum = plate.union(upperLug, clean=True).union(rearWeb, clean=True)
