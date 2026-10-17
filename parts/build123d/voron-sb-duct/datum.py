from build123d import Align, Box, Location
from params import (
    backY,
    frontY,
    halfWidth,
    nozzleEndZ,
    overallDepth,
    overallHeight,
    overallWidth,
    topBoreCylinderEndZ,
    topCounterboreDepth,
    topCounterboreDiameter,
    topPilotDiameter,
    topPilotStartZ,
    topZ,
)

assert overallWidth > 0, "infeasible: overallWidth must be positive"
assert overallDepth > 0, "infeasible: overallDepth must be positive"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
assert halfWidth > 0, "infeasible: halfWidth must be positive"
assert nozzleEndZ > 0, "infeasible: nozzleEndZ must be positive"
assert topZ > nozzleEndZ, "infeasible: topZ must sit above nozzleEndZ"
assert frontY < backY, "infeasible: frontY must sit ahead of the back datum"
assert topPilotDiameter > 0, "infeasible: topPilotDiameter must be positive"
assert topCounterboreDiameter > 0, "infeasible: topCounterboreDiameter must be positive"
assert topPilotDiameter < topCounterboreDiameter, "infeasible: topPilotDiameter must stay inside the counterbore"
assert topCounterboreDepth > 0, "infeasible: topCounterboreDepth must be positive"
assert topCounterboreDepth < topBoreCylinderEndZ - topPilotStartZ, "infeasible: topCounterboreDepth consumes the pilot"
assert topPilotStartZ > 0, "infeasible: topPilotStartZ must be positive"
assert topBoreCylinderEndZ > topPilotStartZ, "infeasible: top bore stack must have positive length"

datum = Location((-halfWidth, frontY, nozzleEndZ)) * Box(
    overallWidth,
    overallDepth,
    overallHeight,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
