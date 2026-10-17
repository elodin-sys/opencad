from pathlib import Path

from build123d import Box, Cone, Pos, import_step

here = Path(__file__).resolve().parent

AXIS_X = -400.0
AXIS_Z = 1515.0


def identity():
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 0.0],
        [0.0, 0.0, 0.0, 1.0],
    ]


def one_solid(shape, name):
    solids = list(shape.solids())
    assert len(solids) == 1, f"{name}: expected 1 solid, got {len(solids)}"
    return solids[0]


duct = one_solid(import_step(here / "inputs" / "duct.step"), "duct")
rotor = one_solid(import_step(here / "inputs" / "rotor.step"), "rotor")
shaft = one_solid(import_step(here / "inputs" / "shaft.step"), "shaft")
hub_disc = one_solid(import_step(here / "inputs" / "hubDisc.step"), "hubDisc")

# Mid-wall diffuser cone: r 251 at y -259 to r 276 at y -136. Overrun the cutter
# so its end faces are not coincident with the slab faces. Then remove the duct
# so the wall meets the duct's outer surface with no overlap.
wall_y0 = -259.0
wall_y1 = -159.0
cone_y0 = -259.0
cone_y1 = -136.0
cone_r0 = 251.0
cone_r1 = 276.0
cone_slope = (cone_r1 - cone_r0) / (cone_y1 - cone_y0)
overrun = 0.05
cut_y0 = wall_y0 - overrun
cut_y1 = wall_y1 + overrun


def cone_radius(y):
    return cone_r0 + (y - cone_y0) * cone_slope


slab = Pos(AXIS_X, (wall_y0 + wall_y1) / 2.0, AXIS_Z) * Box(1200.0, wall_y1 - wall_y0, 1200.0)
cutter = Pos(AXIS_X, (cut_y0 + cut_y1) / 2.0, AXIS_Z) * Cone(
    cone_radius(cut_y0),
    cone_radius(cut_y1),
    cut_y1 - cut_y0,
    rotation=(-90, 0, 0),
)
chamber_wall = one_solid((slab - cutter) - duct, "chamberWall")

box_x0 = -1000.0
box_x1 = 200.0
box_y0 = -1010.0
box_y1 = 364.0
box_z0 = 915.0
box_z1 = 2115.0
domain = Pos(
    (box_x0 + box_x1) / 2.0,
    (box_y0 + box_y1) / 2.0,
    (box_z0 + box_z1) / 2.0,
) * Box(box_x1 - box_x0, box_y1 - box_y0, box_z1 - box_z0)
air = domain
for body in (chamber_wall, duct, rotor, shaft, hub_disc):
    air = air - body
seed = (-388.9, -902.7, 1526.3)
kept = [solid for solid in air.solids() if solid.is_inside(seed)]
assert len(kept) == 1, f"air: seed is in {len(kept)} solids"
air = kept[0]

result = [duct, rotor, shaft, hub_disc, chamber_wall, air]
placements = {name: identity() for name in ("duct", "rotor", "shaft", "hubDisc", "chamberWall", "air")}
joints = {
    "rotorSpin": {"origin": [AXIS_X, -363.5, AXIS_Z], "axis": [0.0, 1.0, 0.0]},
    "shaftOnRotor": {"origin": [AXIS_X, -363.5, AXIS_Z], "axis": [0.0, 1.0, 0.0]},
    "hubDiscOnRotor": {"origin": [AXIS_X, -363.5, AXIS_Z], "axis": [0.0, 1.0, 0.0]},
    "chamberWallFixed": {"origin": [AXIS_X, -259.0, AXIS_Z], "axis": [0.0, 1.0, 0.0]},
    "airFixed": {"origin": [AXIS_X, -363.5, AXIS_Z], "axis": [0.0, 1.0, 0.0]},
}
