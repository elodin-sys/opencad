from pathlib import Path

from build123d import Pos, Rot, import_step

here = Path(__file__).resolve().parent

base_top = 1.56
standoff_len = 10.0
carrier_z = base_top + standoff_len

# moduleMount: 180 deg about z puts module (3, 42, 0) on carrier (75.8, 4, 8.13).
module_x = 75.8 + 3.0
module_y = 4.0 + 42.0
module_z = carrier_z + 8.13

# heatsinkMount: origin on the module SoC lid, same 180 deg turn.
heatsink_x = module_x - 34.8
heatsink_y = module_y - 24.81
heatsink_z = module_z + 3.83


def load(filename):
    return import_step(here / "inputs" / filename)


def rigid(x, y, z, half_turn=False):
    if half_turn:
        location = Pos(x, y, z) * Rot(0, 0, 180)
        matrix = [
            [-1.0, 0.0, 0.0, x],
            [0.0, -1.0, 0.0, y],
            [0.0, 0.0, 1.0, z],
            [0.0, 0.0, 0.0, 1.0],
        ]
    else:
        location = Pos(x, y, z)
        matrix = [
            [1.0, 0.0, 0.0, x],
            [0.0, 1.0, 0.0, y],
            [0.0, 0.0, 1.0, z],
            [0.0, 0.0, 0.0, 1.0],
        ]
    return location, matrix


bodies = {
    "base": (load("aleph-stack-base.step"), *rigid(0.0, 0.0, 0.0)),
    "carrier": (load("aleph-stack-carrier.step"), *rigid(0.0, 0.0, carrier_z)),
    "module": (load("aleph-stack-module.step"), *rigid(module_x, module_y, module_z, True)),
    "heatsink": (load("aleph-stack-heatsink.step"), *rigid(heatsink_x, heatsink_y, heatsink_z, True)),
    "standoff1": (load("standoff1.step"), *rigid(3.0, 3.0, base_top)),
    "standoff2": (load("standoff2.step"), *rigid(85.0, 3.0, base_top)),
    "standoff3": (load("standoff3.step"), *rigid(85.0, 49.5, base_top)),
    "standoff4": (load("standoff4.step"), *rigid(3.0, 49.5, base_top)),
}

order = ["base", "carrier", "module", "heatsink", "standoff1", "standoff2", "standoff3", "standoff4"]
result = [bodies[name][0].moved(bodies[name][1]) for name in order]
placements = {name: bodies[name][2] for name in order}

joints = {
    "carrierMount": {"origin": [3.0, 3.0, carrier_z], "axis": [0.0, 0.0, 1.0]},
    "moduleMount": {"origin": [75.8, 4.0, module_z], "axis": [0.0, 0.0, 1.0]},
    "heatsinkMount": {"origin": [heatsink_x, heatsink_y, heatsink_z], "axis": [0.0, 0.0, 1.0]},
    "standoff1Mount": {"origin": [3.0, 3.0, base_top], "axis": [0.0, 0.0, 1.0]},
    "standoff2Mount": {"origin": [85.0, 3.0, base_top], "axis": [0.0, 0.0, 1.0]},
    "standoff3Mount": {"origin": [85.0, 49.5, base_top], "axis": [0.0, 0.0, 1.0]},
    "standoff4Mount": {"origin": [3.0, 49.5, base_top], "axis": [0.0, 0.0, 1.0]},
}
