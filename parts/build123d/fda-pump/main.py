from pathlib import Path

from build123d import Axis, Kind, Location, import_step

housingWallThickness = 3.0
assert housingWallThickness > 0, "infeasible: housingWallThickness must be positive"

here = Path(__file__).resolve().parent


def load_solid(name):
    loaded = import_step(here / "inputs" / name)
    return loaded.solids()[0]


chamber = load_solid("chamber.step")
rotor = load_solid("rotor.step")


def housing_wall(fluid):
    # MakeThickSolid on the 40 um cutwater fillet is intermittent; a valid 3 mm wall is identical each time it succeeds.
    for _ in range(80):
        tool = fluid.moved(Location((0, 0, 0)))
        openings = list(tool.faces().filter_by(Axis.X))
        try:
            wall = tool.offset_3d(openings, housingWallThickness, kind=Kind.ARC)
        except RuntimeError:
            continue
        solids = wall.solids()
        if len(solids) == 1 and solids[0].is_valid:
            return solids[0]
    raise RuntimeError("housing offset failed")


housing = housing_wall(chamber)
blood = chamber - rotor
housing.label = "housing"
rotor.label = "rotor"
blood.label = "blood"

result = [housing, rotor, blood]
identity = [
    [1.0, 0.0, 0.0, 0.0],
    [0.0, 1.0, 0.0, 0.0],
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0],
]
placements = {
    "housing": identity,
    "rotor": identity,
    "blood": identity,
}
joints = {
    "rotorSpin": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "bloodFixed": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
}
