"""VTX mount in the identity assembly frame."""

from datum import datum
from exterior import apply as apply_exterior
from insertSeat import apply as apply_insertSeat
from vtxLattice import apply as apply_vtxLattice

result = apply_vtxLattice(apply_insertSeat(apply_exterior(datum)))

assert result.is_valid, "composed VTX mount must be a valid solid"
assert len(result.solids()) == 1, "composed VTX mount must remain one connected body"
