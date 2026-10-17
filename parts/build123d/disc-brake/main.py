from pathlib import Path

from build123d import import_step

here = Path(__file__).resolve().parent
disc = import_step(here / "inputs" / "disc-brake-disc.step")
pad = import_step(here / "inputs" / "disc-brake-pad.step")

# Both own frames already coincide with the assembly frame at rest.
result = [disc, pad]
placements = {
    "disc": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "pad": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
}
joints = {
    "discSpin": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
}
