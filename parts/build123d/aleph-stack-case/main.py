"""Two-piece Aleph stack enclosure in the original assembly datum frame."""

from cavity import apply as apply_cavity
from coolingPorts import apply as apply_coolingPorts
from datum import datum
from lowerMounts import apply as apply_lowerMounts
from servicePorts import apply as apply_servicePorts
from topMounts import apply as apply_topMounts

result = apply_topMounts(apply_servicePorts(apply_lowerMounts(apply_coolingPorts(apply_cavity(datum)))))
