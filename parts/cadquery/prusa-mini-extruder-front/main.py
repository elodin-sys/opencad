import cadquery as cq
from datum import datum
from exterior import apply as apply_exterior
from fasteners import apply as apply_fasteners
from filament import apply as apply_filament
from keyhole import apply as apply_keyhole
from sideClamp import apply as apply_sideClamp

result: cq.Workplane = apply_sideClamp(apply_keyhole(apply_filament(apply_fasteners(apply_exterior(datum)))))
