from bottomDevices import apply as apply_bottomDevices
from datum import datum
from topHeaders import apply as apply_topHeaders

result = apply_topHeaders(apply_bottomDevices(datum))
