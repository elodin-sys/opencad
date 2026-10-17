"""Shared envelope stock, rebuilt from the passed blockout in millimetres."""

from build123d import Align, Box, Circle, Plane, Polygon, Pos, extrude
from params import (
    bodyTopZ,
    bottomZ,
    halfWidth,
    leftFootTopZ,
    leftFootX,
    lowerLeftPilotDiameter,
    lugBossDiameter,
    lugMaxZ,
    lugNutX,
    lugNutZ,
    lugWebPeakX,
    overallHeight,
    plateThickness,
    plateWidth,
    upperLeftPilotDiameter,
)

# Passed-blockout allowances, not dimensions of the finished rear web.
blockout_web_width = 10.0
blockout_web_thickness = 7.0

assert plateWidth > 0.0, "infeasible: plateWidth must be positive"
assert plateThickness > 0.0, "infeasible: plateThickness must be positive"
assert halfWidth > 0.0, "infeasible: halfWidth must be positive"
assert overallHeight > 0.0, "infeasible: overallHeight must be positive"
assert bottomZ < leftFootTopZ < bodyTopZ < lugMaxZ, "infeasible: foot, plate and web heights must be ordered"
assert -halfWidth < leftFootX < 0.0, "infeasible: the lower foot must lie inside the left envelope"
assert lugBossDiameter > 0.0, "infeasible: lugBossDiameter must be positive"
assert -halfWidth < lugNutX - lugBossDiameter / 2.0, "infeasible: lug exceeds the left envelope"
assert lugNutX + lugBossDiameter / 2.0 < halfWidth, "infeasible: lug exceeds the right envelope"
assert lugNutZ - lugBossDiameter / 2.0 < bodyTopZ, "infeasible: lug must overlap the main plate"
assert lugNutZ + lugBossDiameter / 2.0 <= lugMaxZ, "infeasible: lug exceeds the top envelope"
assert blockout_web_width > 0.0, "infeasible: rear web width must be positive"
assert 0.0 < blockout_web_thickness <= plateThickness, "infeasible: rear web must fit within the plate thickness"
assert -halfWidth < lugWebPeakX - blockout_web_width / 2.0, "infeasible: rear web exceeds the left envelope"
assert lugWebPeakX + blockout_web_width / 2.0 < halfWidth, "infeasible: rear web exceeds the right envelope"
assert upperLeftPilotDiameter > 0.0, "infeasible: upperLeftPilotDiameter must be positive"
assert lowerLeftPilotDiameter > 0.0, "infeasible: lowerLeftPilotDiameter must be positive"

# Plane.XZ maps sketch y to world z. Explicit +y extrusion keeps datum A
# at y=0 and datum B at y=14, irrespective of the camera filenames.
housing_outline = Plane.XZ * Polygon(
    (leftFootX, bottomZ),
    (halfWidth, bottomZ),
    (halfWidth, bodyTopZ),
    (-halfWidth, bodyTopZ),
    (-halfWidth, leftFootTopZ),
    (leftFootX, leftFootTopZ),
    align=None,
)
main_plate = extrude(housing_outline, amount=plateThickness, dir=(0.0, 1.0, 0.0))

lug_outline = Plane.XZ * Pos(lugNutX, lugNutZ) * Circle(lugBossDiameter / 2.0)
top_lug = extrude(lug_outline, amount=plateThickness, dir=(0.0, 1.0, 0.0))

# Keep the blockout's conservative 10 x 7 rear-web stock and full z=33.72
# peak. The exterior module must finish the web and its filament-path support.
rear_web = Pos(lugWebPeakX - blockout_web_width / 2.0, 0.0, bodyTopZ) * Box(
    blockout_web_width,
    blockout_web_thickness,
    lugMaxZ - bodyTopZ,
    align=(Align.MIN, Align.MIN, Align.MIN),
)

datum = main_plate + top_lug + rear_web
