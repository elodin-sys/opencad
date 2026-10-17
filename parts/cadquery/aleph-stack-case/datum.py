# Two stock bodies in the original aleph-stack assembly frame, in millimetres.
import cadquery as cq
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

# params.py deliberately contains literals. Evaluate edit-sensitive stock bounds
# here so wallThickness changes both footprints without moving the cavity planes.
stockXMin = innerXMin - wallThickness
stockXMax = innerXMax + wallThickness
stockYMin = innerYMin - wallThickness
stockYMax = innerYMax + wallThickness
stockLength = stockXMax - stockXMin
stockWidth = stockYMax - stockYMin
stockFloorBottom = floorTop - floorThickness
stockShellBottom = floorTop + seamGap
stockRoofTop = roofBottom + roofThickness

assert wallThickness > 0.0, "infeasible: wallThickness must be positive"
assert floorThickness > 0.0, "infeasible: floorThickness must be positive"
assert roofThickness > 0.0, "infeasible: roofThickness must be positive"
assert heatsinkMargin > 0.0, "infeasible: heatsinkMargin must be positive"
assert seamGap > 0.0, "infeasible: the two case bodies require a positive seam"
assert innerXMax > innerXMin, "infeasible: cavity x span must be positive"
assert innerYMax > innerYMin, "infeasible: cavity y span must be positive"
assert stockFloorBottom < floorTop < stockShellBottom < roofBottom < stockRoofTop, (
    "infeasible: cover, seam and upper-cap planes must remain ordered"
)

# Rebuild the passed blockout; hollowing, pads and all apertures belong to modules.
upperCap = cq.Workplane("XY", origin=(stockXMin, stockYMin, stockShellBottom)).box(
    stockLength,
    stockWidth,
    stockRoofTop - stockShellBottom,
    centered=(False, False, False),
)
bottomCover = cq.Workplane("XY", origin=(stockXMin, stockYMin, stockFloorBottom)).box(
    stockLength,
    stockWidth,
    floorThickness,
    centered=(False, False, False),
)

# Stable body order for every apply(body): upper cap, then lower cover.
datum = [upperCap, bottomCover]
