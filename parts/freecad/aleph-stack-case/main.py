"""Compose the two-piece Aleph stack case in its original assembly frame."""

from datum import datum
from lowerMounts import apply as apply_lowerMounts
from servicePorts import apply as apply_servicePorts
from shellCavity import apply as apply_shellCavity
from thermalVents import apply as apply_thermalVents
from topMounts import apply as apply_topMounts

result = apply_topMounts(apply_thermalVents(apply_servicePorts(apply_lowerMounts(apply_shellCavity(datum)))))
