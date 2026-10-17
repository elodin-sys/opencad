# Full case in the original aleph-stack frame; keep cap and cover separate.
import cadquery as cq
from capCavity import apply as apply_capCavity
from datum import datum
from lowerMounts import apply as apply_lowerMounts
from roofOpenings import apply as apply_roofOpenings
from wallWindows import apply as apply_wallWindows

result: list[cq.Workplane] = apply_wallWindows(apply_roofOpenings(apply_lowerMounts(apply_capCavity(datum))))
