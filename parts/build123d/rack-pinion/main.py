from pathlib import Path

from build123d import Location, import_step

here = Path(__file__).resolve().parent

base = import_step(here / "inputs" / "rack-pinion-base.step")
pinion = import_step(here / "inputs" / "rack-pinion-pinion.step")
rack = import_step(here / "inputs" / "rack-pinion-rack.step").move(Location((0.0, -20.0, 0.0)))

result = [base, pinion, rack]
placements = {
    "base": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "pinion": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "rack": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, -20.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
}
joints = {
    "pinionSpin": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "rackSlide": {"origin": [0.0, -20.0, 0.0], "axis": [1.0, 0.0, 0.0]},
}
