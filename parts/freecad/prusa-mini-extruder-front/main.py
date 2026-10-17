"""Compose the constructed Prusa MINI extruder front housing."""

from clamp import apply as apply_clamp
from datum import datum
from exterior import apply as apply_exterior
from fasteners import apply as apply_fasteners
from filament import apply as apply_filament
from keyhole import apply as apply_keyhole

result = apply_keyhole(apply_filament(apply_fasteners(apply_clamp(apply_exterior(datum)))))
