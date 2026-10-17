from pathlib import Path

from build123d import Plane, import_step

here = Path(__file__).resolve().parent


def matrix(origin, x_dir, y_dir):
    ox, oy, oz = origin
    xx, xy, xz = x_dir
    yx, yy, yz = y_dir
    return [
        [xx, yx, 0.0, ox],
        [xy, yy, 0.0, oy],
        [xz, yz, 1.0, oz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def place(solid, origin, x_dir, y_dir):
    placement = matrix(origin, x_dir, y_dir)
    if origin == (0.0, 0.0, 0.0) and x_dir == (1.0, 0.0, 0.0):
        return solid, placement
    plane = Plane(origin=origin, x_dir=x_dir, z_dir=(0.0, 0.0, 1.0))
    return solid.moved(plane.location), placement


ground_solid = import_step(here / "inputs" / "four-bar-ground.step")
crank_solid = import_step(here / "inputs" / "four-bar-crank.step")
coupler_solid = import_step(here / "inputs" / "four-bar-coupler.step")
rocker_solid = import_step(here / "inputs" / "four-bar-rocker.step")

ground, ground_placement = place(ground_solid, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
crank, crank_placement = place(crank_solid, (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0))
# atan2(80, 60): cos = 0.6, sin = 0.8; origin is pin A on the crank top face
coupler, coupler_placement = place(coupler_solid, (40.0, 0.0, 5.0), (0.6, 0.8, 0.0), (-0.8, 0.6, 0.0))
# 90 deg about +z, 10 mm above the ground top face at O4
rocker, rocker_placement = place(rocker_solid, (100.0, 0.0, 10.0), (0.0, 1.0, 0.0), (-1.0, 0.0, 0.0))

result = [ground, crank, coupler, rocker]
placements = {
    "ground": ground_placement,
    "crank": crank_placement,
    "coupler": coupler_placement,
    "rocker": rocker_placement,
}
joints = {
    "pinO2": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    "pinA": {"origin": [40.0, 0.0, 5.0], "axis": [0.0, 0.0, 1.0]},
    "pinO4": {"origin": [100.0, 0.0, 10.0], "axis": [0.0, 0.0, 1.0]},
    "pinB": {"origin": [100.0, 80.0, 10.0], "axis": [0.0, 0.0, 1.0]},
}
