"""Compose the two-piece Aleph stack enclosure in assembly millimetres.

Parameters stay in params.py. Feature modules preserve the ordered upper-cap
and bottom-cover pair; the two printed bodies are never fused together.
"""

from datum import datum
from exhaustWindows import apply as apply_exhaustWindows
from exterior import apply as apply_exterior
from lowerMounts import apply as apply_lowerMounts
from roofCuts import apply as apply_roofCuts
from serviceWindows import apply as apply_serviceWindows

# Dependency order: exterior -> exhaust -> lower mounts -> roof -> service.
result = apply_serviceWindows(apply_roofCuts(apply_lowerMounts(apply_exhaustWindows(apply_exterior(datum)))))
