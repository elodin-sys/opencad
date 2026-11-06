"""Place axjet-c2. Modelled bodies are input STEPs; rig skins and air are built here."""

from pathlib import Path

from build123d import Align, Box, Cylinder, Location, Pos, import_step

here = Path(__file__).resolve().parent

ORDER = (
    "case_r1",
    "bellmouth",
    "inlet_frame",
    "nose_cone",
    "rotor_1",
    "stator_1",
    "seal_spacer",
    "rotor_2",
    "ogv_ring",
    "drum_shaft",
    "bearing_front",
    "stack_nut",
    "starter",
    "air",
    "rigPlenum",
    "rigExit",
    "rigExitPlug",
)

STEP = {
    "case_r1": "axjet-c2-case_r1.step",
    "bellmouth": "axjet-c2-bellmouth.step",
    "inlet_frame": "axjet-c2-inlet_frame.step",
    "nose_cone": "axjet-c2-nose_cone.step",
    "rotor_1": "axjet-c2-rotor_1.step",
    "stator_1": "axjet-c2-stator_1.step",
    "seal_spacer": "axjet-c2-seal_spacer.step",
    "rotor_2": "axjet-c2-rotor_2.step",
    "ogv_ring": "axjet-c2-ogv_ring.step",
    "drum_shaft": "axjet-c2-drum_shaft.step",
    "bearing_front": "axjet-c2-bearing_front.step",
    "stack_nut": "axjet-c2-stack_nut.step",
    "starter": "starter.step",
}

# Child translation along z. Every other STEP is already in the assembly frame.
SHIFT = {
    "case_r1": 0.0,
    "bellmouth": 0.0,
    "inlet_frame": 0.0,
    "nose_cone": -80.0,
    "rotor_1": 0.0,
    "stator_1": 0.0,
    "seal_spacer": 24.0,
    "rotor_2": 42.0,
    "ogv_ring": 0.0,
    "drum_shaft": 0.0,
    "bearing_front": -72.0,
    "stack_nut": -18.0,
    "starter": 0.0,
}

# Blades and exit skins before the casings. A fused stack drops face-to-face
# flanges, and cutting a casing after both neighbours returns the raw box.
CUT_ORDER = (
    "rotor_1",
    "rotor_2",
    "stator_1",
    "ogv_ring",
    "rigExit",
    "rigExitPlug",
    "seal_spacer",
    "drum_shaft",
    "stack_nut",
    "bearing_front",
    "case_r1",
    "inlet_frame",
    "bellmouth",
    "nose_cone",
    "starter",
    "rigPlenum",
)

CAP_IN = -220.0
CAP_OUT = 90.0
SEED = (0.0, 0.0, -200.0)
BOX_HALF = 160.0
AIR_VOLUME = 12170000.0
AIR_VOLUME_TOL = 0.05


def one_solid(shape, name):
    solids = list(shape.solids())
    if len(solids) != 1:
        raise RuntimeError(f"{name}: expected 1 solid, got {len(solids)}")
    return solids[0]


def tube(inner_r, outer_r, z0, z1):
    height = z1 - z0
    outer = Pos(0.0, 0.0, z0) * Cylinder(outer_r, height, align=(Align.CENTER, Align.CENTER, Align.MIN))
    # Overrun the bore so the cutter is not coplanar with the annulus ends.
    cutter = Pos(0.0, 0.0, z0 - 1.0) * Cylinder(inner_r, height + 2.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return one_solid(outer - cutter, "tube")


def rig_plenum():
    # 0.05 mm overlap gives the fuse a volume contact at the lip plane.
    wall = tube(150.0, 155.0, -225.0, -94.95)
    rear = tube(125.0, 155.0, -95.0, -90.0)
    return one_solid(wall + rear, "rigPlenum")


def rig_exit():
    return tube(90.25, 95.0, 80.0, 95.0)


def rig_exit_plug():
    return tube(20.0, 67.5, 80.0, 95.0)


def volume_of(shape):
    if shape is None:
        return 0.0
    if type(shape).__name__ == "ShapeList" or isinstance(shape, (list, tuple)):
        return sum(volume_of(item) for item in shape)
    if type(shape).__name__ == "Solid":
        return float(shape.volume)
    solids = list(shape.solids()) if hasattr(shape, "solids") else []
    if solids:
        return sum(float(solid.volume) for solid in solids)
    volume = getattr(shape, "volume", None)
    if volume is None:
        return 0.0
    return float(volume)


def solids_of(shape):
    if shape is None:
        return []
    found = list(shape.solids())
    if found:
        return found
    return [shape]


def contains_point(solid, point):
    box = solid.bounding_box()
    x, y, z = point
    if x < box.min.X or x > box.max.X or y < box.min.Y or y > box.max.Y:
        return False
    if z < box.min.Z or z > box.max.Z:
        return False
    probe = solid.intersect(Pos(x, y, z) * Box(0.2, 0.2, 0.2))
    return volume_of(probe) > 1e-09


def load_body(name):
    loaded = import_step(here / "inputs" / STEP[name])
    if isinstance(loaded, (list, tuple)):
        return loaded[0]
    return loaded


def place(shape, tz):
    if tz == 0.0:
        return shape
    return shape.moved(Location((0.0, 0.0, tz)))


def matrix(tz):
    return [
        [1.0, 0.0, 0.0, 0.0],
        [0.0, 1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, tz],
        [0.0, 0.0, 0.0, 1.0],
    ]


def load_placed():
    return {name: place(load_body(name), SHIFT[name]) for name in STEP}


def air_from(named):
    """Padded box minus the walls and minus-bodies, clipped at the caps, seed piece.

    Cuts run one body at a time. A single fuse of the stack drops the flange joints
    (coincident faces, no shared volume), and the next fuse then voids the solid.
    Each cut removes exactly that body's volume, including joints that only touch.
    """
    height = CAP_OUT - CAP_IN
    space = Pos(0.0, 0.0, (CAP_IN + CAP_OUT) / 2.0) * Box(
        2.0 * BOX_HALF,
        2.0 * BOX_HALF,
        height,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    )
    for name, shape in named:
        before = volume_of(space)
        try:
            space = space - shape
        except Exception as exc:
            raise RuntimeError(f"cut failed on {name}") from exc
        removed = before - volume_of(space)
        part = volume_of(shape)
        if removed > part + 1000.0 or removed < -1000.0:
            raise RuntimeError(f"cut {name} removed {removed:.1f}, part volume {part:.1f}")
        print(
            f"cut {name} removed={removed:.1f} part={part:.1f} n={len(solids_of(space))}",
            flush=True,
        )
    raw = space
    hits = [solid for solid in solids_of(raw) if contains_point(solid, SEED)]
    if len(hits) != 1:
        volumes = [round(volume_of(solid), 1) for solid in solids_of(raw)]
        raise RuntimeError(f"seed in {len(hits)} of {len(volumes)} solids, volumes={volumes}")
    air = hits[0]
    box = air.bounding_box()
    reach = max(abs(box.min.X), abs(box.max.X), abs(box.min.Y), abs(box.max.Y))
    volume = volume_of(air)
    if reach > 151.0 or box.min.Z < CAP_IN - 0.05 or box.max.Z > CAP_OUT + 0.05:
        raise RuntimeError(
            f"air leaked: bbox ({box.min.X:.2f},{box.min.Y:.2f},{box.min.Z:.2f})"
            f"..({box.max.X:.2f},{box.max.Y:.2f},{box.max.Z:.2f}) vol={volume:.1f}"
        )
    low = AIR_VOLUME * (1.0 - AIR_VOLUME_TOL)
    high = AIR_VOLUME * (1.0 + AIR_VOLUME_TOL)
    if not low <= volume <= high:
        raise RuntimeError(f"air volume {volume:.1f} outside {low:.1f}..{high:.1f}")
    return air


def build():
    rigs = {
        "rigPlenum": rig_plenum(),
        "rigExit": rig_exit(),
        "rigExitPlug": rig_exit_plug(),
    }
    loaded = load_placed()
    loaded.update(rigs)
    named = [(name, loaded[name]) for name in CUT_ORDER]
    air = air_from(named)
    del loaded
    placed = load_placed()
    placed.update(rigs)
    placed["air"] = air
    rows = {name: matrix(SHIFT[name]) for name in STEP}
    rows["air"] = matrix(0.0)
    rows["rigPlenum"] = matrix(0.0)
    rows["rigExit"] = matrix(0.0)
    rows["rigExitPlug"] = matrix(0.0)
    joint_rows = {
        "rotorSpin": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
        "rotor1OnDrum": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
        "spacerOnDrum": {"origin": [0.0, 0.0, 24.0], "axis": [0.0, 0.0, 1.0]},
        "rotor2OnDrum": {"origin": [0.0, 0.0, 42.0], "axis": [0.0, 0.0, 1.0]},
        "stackNutOnDrum": {"origin": [0.0, 0.0, -18.0], "axis": [0.0, 0.0, 1.0]},
        "inletFrameOnCase": {"origin": [0.0, 0.0, -18.0], "axis": [0.0, 0.0, 1.0]},
        "bellmouthOnFrame": {"origin": [0.0, 0.0, -72.0], "axis": [0.0, 0.0, 1.0]},
        "stator1OnCase": {"origin": [0.0, 0.0, 18.0], "axis": [0.0, 0.0, 1.0]},
        "ogvOnCase": {"origin": [0.0, 0.0, 58.0], "axis": [0.0, 0.0, 1.0]},
        "noseOnInlet": {"origin": [0.0, 0.0, -80.0], "axis": [0.0, 0.0, 1.0]},
        "starterOnNose": {"origin": [0.0, 0.0, -108.0], "axis": [0.0, 0.0, 1.0]},
        "bearingFrontInHub": {"origin": [0.0, 0.0, -72.0], "axis": [0.0, 0.0, 1.0]},
        "airFixed": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
        "rigPlenumFixed": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
        "rigExitFixed": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
        "rigExitPlugFixed": {"origin": [0.0, 0.0, 0.0], "axis": [0.0, 0.0, 1.0]},
    }
    missing = [name for name in ORDER if name not in placed]
    if missing:
        raise RuntimeError(f"missing bodies: {missing}")
    return [placed[name] for name in ORDER], rows, joint_rows


result = []
placements = {}
joints = {}
if __name__ != "diagnostic":
    result, placements, joints = build()
