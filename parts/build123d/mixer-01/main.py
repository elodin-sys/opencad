from pathlib import Path

from build123d import Align, Box, Cylinder, Location, Pos, Rot, import_step

here = Path(__file__).resolve().parent

# Cap disks sit on the port planes. The annulus overruns the tube wall so the
# fuse overlaps material; the bore itself is not cut.
CAP_REACH = 8.0
WALL_OVERRUN = 0.05
SEED = (12.3, 5.7, 17.1)


def only_solid(shape):
    solids = list(shape.solids())
    if len(solids) != 1:
        raise RuntimeError(f"expected one solid, got {len(solids)}")
    return solids[0]


def load(name):
    return only_solid(import_step(here / "inputs" / name))


def cylinder_z(x, y, z, radius, height):
    return Pos(x, y, z) * Cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.MIN))


def cylinder_x(x, y, z, radius, height):
    return Pos(x, y, z) * Rot(0, 90, 0) * Cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.MIN))


def port_cap(place, bore_radius, plug_radius):
    outer = place(WALL_OVERRUN, CAP_REACH + WALL_OVERRUN, plug_radius)
    inner = place(WALL_OVERRUN + 0.1, CAP_REACH + WALL_OVERRUN + 0.2, bore_radius)
    disk = place(0.0, CAP_REACH, plug_radius)
    return (outer - inner) + disk


housing = load("mixer-01-housing.step")
impeller = load("mixer-01-impeller.step").move(Location((0.0, 0.0, 1.0)))
motor = load("motor.step").move(Location((0.0, 0.0, -3.0)))

housing_tool = load("mixer-01-housing.step")
impeller_tool = load("mixer-01-impeller.step").move(Location((0.0, 0.0, 1.0)))
bounds = housing_tool.bounding_box()
pad = 10.0
box = Pos(bounds.min.X - pad, bounds.min.Y - pad, bounds.min.Z - pad) * Box(
    (bounds.max.X - bounds.min.X) + 2.0 * pad,
    (bounds.max.Y - bounds.min.Y) + 2.0 * pad,
    (bounds.max.Z - bounds.min.Z) + 2.0 * pad,
    align=(Align.MIN, Align.MIN, Align.MIN),
)
inlet_cap = port_cap(
    lambda back, height, radius: cylinder_z(0.0, 0.0, 48.0 - back, radius, height),
    6.0,
    7.0,
)
outlet_cap = port_cap(
    lambda back, height, radius: cylinder_x(58.0 - back, 0.0, 12.5, radius, height),
    5.0,
    6.0,
)
complement = box - (housing_tool + inlet_cap + outlet_cap)
probe = Pos(*SEED) * Box(0.4, 0.4, 0.4)
cavity = None
for solid in complement.solids():
    hit = solid.intersect(probe)
    overlap = 0.0 if hit is None else sum(piece.volume for piece in hit.solids())
    if overlap > 0.0:
        cavity = solid
        break
if cavity is None:
    raise RuntimeError("fluid seed is outside the capped housing cavity")
water = only_solid(cavity - impeller_tool)

result = [housing, impeller, motor, water]
placements = {
    "housing": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
    "impeller": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 0.0, 1.0]],
    "motor": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, -3.0], [0.0, 0.0, 0.0, 1.0]],
    "water": [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]],
}
joints = {
    "motorMount": {"origin": [0.0, 0.0, -3.0], "axis": [0.0, 0.0, 1.0]},
    "impellerSpin": {"origin": [0.0, 0.0, 1.0], "axis": [0.0, 0.0, 1.0]},
    "waterFixed": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
}
