import cadquery as cq
from params import (
    backY,
    frontY,
    halfWidth,
    nozzleEndZ,
    overallDepth,
    overallHeight,
    overallWidth,
    topZ,
)

assert overallWidth > 0, "infeasible: overallWidth must be positive"
assert overallDepth > 0, "infeasible: overallDepth must be positive"
assert overallHeight > 0, "infeasible: overallHeight must be positive"
assert halfWidth > 0, "infeasible: halfWidth must be positive"
assert topZ > nozzleEndZ, "infeasible: topZ must sit above nozzleEndZ"
assert frontY < backY, "infeasible: frontY must be behind the back datum"

datum = (
    cq.Workplane("XY")
    .transformed(offset=(0.0, frontY, nozzleEndZ))
    .box(overallWidth, overallDepth, overallHeight, centered=(True, False, False))
)
