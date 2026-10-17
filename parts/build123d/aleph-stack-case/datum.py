"""Two envelope stocks in the aleph assembly frame, ordered cap then cover.

Nominal derived parameters remain literals in params.py. Compute the working
stock planes here so a wallThickness edit moves only the four exterior planes.
Feature modules preserve this two-body list and cut or add to the named body.
"""

from build123d import Align, Box, Pos
from params import (
    floorThickness,
    floorTop,
    heatsinkMargin,
    innerXMax,
    innerXMin,
    innerYMax,
    innerYMin,
    roofBottom,
    roofThickness,
    seamGap,
    wallThickness,
)

assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
assert roofThickness > 0.0, "infeasible: roofThickness must be positive"
assert floorThickness > 0.0, "infeasible: floorThickness must be positive"
assert heatsinkMargin > 0.0, "infeasible: heatsinkMargin must be positive"
assert seamGap > 0.0, "infeasible: the two bodies require a positive seam"
assert innerXMax > innerXMin, "infeasible: the cavity x span must be positive"
assert innerYMax > innerYMin, "infeasible: the cavity y span must be positive"

stockMinX = innerXMin - wallThickness
stockMaxX = innerXMax + wallThickness
stockMinY = innerYMin - wallThickness
stockMaxY = innerYMax + wallThickness
stockLength = stockMaxX - stockMinX
stockWidth = stockMaxY - stockMinY
coverBaseZ = floorTop - floorThickness
capBaseZ = floorTop + seamGap
capTopZ = roofBottom + roofThickness

assert coverBaseZ < floorTop < capBaseZ < roofBottom < capTopZ, (
    "infeasible: floor, seam, cap and roof planes must remain ordered"
)
assert floorTop < 0.0, "infeasible: the cover slab must remain below the PCB datum"

# Match the passed blockout: no cavity, apertures, bores, or support pads yet.
upperCap = Pos(stockMinX, stockMinY, capBaseZ) * Box(
    stockLength,
    stockWidth,
    capTopZ - capBaseZ,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
bottomCover = Pos(stockMinX, stockMinY, coverBaseZ) * Box(
    stockLength,
    stockWidth,
    floorThickness,
    align=(Align.MIN, Align.MIN, Align.MIN),
)

datum = [upperCap, bottomCover]
