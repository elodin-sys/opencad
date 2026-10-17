import math
from pathlib import Path

from build123d import Location, Plane, import_step

here = Path(__file__).resolve().parent

BODY_ORDER = [
    "base",
    "motor",
    "motorGear",
    "stackedGear",
    "outputGear",
    "upperCase",
    "stator",
    "lid",
    "clamp",
    "rotor",
    "roller1",
    "roller2",
    "roller3",
    "tube",
]

STEP_FILES = {
    "base": "base.step",
    "motor": "motor.step",
    "motorGear": "motorGear.step",
    "stackedGear": "stackedGear.step",
    "outputGear": "outputGear.step",
    "upperCase": "upperCase.step",
    "stator": "stator.step",
    "lid": "lid.step",
    "clamp": "clamp.step",
    "rotor": "rotor.step",
    "roller1": "roller1.step",
    "roller2": "roller2.step",
    "roller3": "roller3.step",
    "tube": "peristaltic-pump-tube.step",
}

# parent, child, parent frame (origin, axis, ref), child frame, offset mm, angle deg
JOINTS = [
    (
        "motorMount",
        "base",
        "motor",
        ([-20.5, 0.0, -20.5], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
    (
        "motorSpin",
        "motor",
        "motorGear",
        ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        12.0,
        0.0,
    ),
    (
        "stackedSpin",
        "base",
        "stackedGear",
        ([-20.5, 12.0, -50.5], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        0.0,
        7.5,
    ),
    (
        "outputSpin",
        "base",
        "outputGear",
        ([-20.5, 23.0, -20.5], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        0.0,
        3.75,
    ),
    (
        "upperCaseMount",
        "base",
        "upperCase",
        ([-20.5, 12.0, -20.5], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]),
        ([-15.5, 0.0, -30.5], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
    (
        "rotorDrive",
        "outputGear",
        "rotor",
        ([0.0, 0.0, 44.125], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        ([-2.887, 0.0, -5.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
    (
        "statorMount",
        "upperCase",
        "stator",
        ([-15.5, 31.0, -30.5], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        ([-20.5, 5.0, -20.5], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
    (
        "lidMount",
        "stator",
        "lid",
        ([-20.5, 24.8, -20.5], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]),
        ([-20.5, 2.0, -20.5], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
    (
        "clampMount",
        "stator",
        "clamp",
        ([-46.0, 30.0, -20.5], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]),
        ([-16.5, 0.0, -5.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
    (
        "tubeSeat",
        "stator",
        "tube",
        ([-20.5, 29.8, -20.5], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
    (
        "roller1Pin",
        "rotor",
        "roller1",
        ([0.0, 0.675, 0.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
    (
        "roller2Pin",
        "rotor",
        "roller2",
        ([-8.66, 0.675, -5.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
    (
        "roller3Pin",
        "rotor",
        "roller3",
        ([0.0, 0.675, -10.0], [0.0, 1.0, 0.0], [1.0, 0.0, 0.0]),
        ([0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]),
        0.0,
        0.0,
    ),
]


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _scale(a, s):
    return (a[0] * s, a[1] * s, a[2] * s)


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _unit(v):
    n = math.sqrt(_dot(v, v))
    return (v[0] / n, v[1] / n, v[2] / n)


def _matvec(m, v):
    return (
        m[0][0] * v[0] + m[0][1] * v[1] + m[0][2] * v[2],
        m[1][0] * v[0] + m[1][1] * v[1] + m[1][2] * v[2],
        m[2][0] * v[0] + m[2][1] * v[1] + m[2][2] * v[2],
    )


def _matmul(a, b):
    return tuple(tuple(_dot(row, (b[0][j], b[1][j], b[2][j])) for j in range(3)) for row in a)


def _transpose(m):
    return tuple(tuple(m[j][i] for j in range(3)) for i in range(3))


def _rot_z(deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return ((c, -s, 0.0), (s, c, 0.0), (0.0, 0.0, 1.0))


def _basis(axis, ref):
    """Columns are ref, axis×ref, axis — the frame's x, y, z."""
    z = _unit(axis)
    x = _sub(ref, _scale(z, _dot(ref, z)))
    x = _unit(x)
    y = _cross(z, x)
    return (
        (x[0], y[0], z[0]),
        (x[1], y[1], z[1]),
        (x[2], y[2], z[2]),
    )


def _identity():
    return ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), (0.0, 0.0, 0.0)


def _child_pose(parent_pose, parent_frame, child_frame, offset, angle):
    parent_r, parent_t = parent_pose
    origin, axis, ref = parent_frame
    parent_origin = _add(_matvec(parent_r, origin), parent_t)
    parent_axis = _unit(_matvec(parent_r, axis))
    parent_ref = _matvec(parent_r, ref)
    child_origin, child_axis, child_ref = child_frame
    rotation = _matmul(
        _matmul(_basis(parent_axis, parent_ref), _rot_z(angle)), _transpose(_basis(child_axis, child_ref))
    )
    mapped_axis = _matvec(rotation, _unit(child_axis))
    assert _dot(mapped_axis, parent_axis) > 1.0 - 1e-9, "child axis is not parallel to the parent axis"
    translation = _sub(_add(parent_origin, _scale(parent_axis, offset)), _matvec(rotation, child_origin))
    joint_origin = _add(parent_origin, _scale(parent_axis, offset))
    return (rotation, translation), joint_origin, parent_axis


def _matrix(rotation, translation):
    return [
        [rotation[0][0], rotation[0][1], rotation[0][2], translation[0]],
        [rotation[1][0], rotation[1][1], rotation[1][2], translation[1]],
        [rotation[2][0], rotation[2][1], rotation[2][2], translation[2]],
        [0.0, 0.0, 0.0, 1.0],
    ]


def _location(rotation, translation):
    x_dir = (rotation[0][0], rotation[1][0], rotation[2][0])
    z_dir = (rotation[0][2], rotation[1][2], rotation[2][2])
    return Location(Plane(origin=translation, x_dir=x_dir, z_dir=z_dir))


def _load(name):
    shape = import_step(here / "inputs" / STEP_FILES[name])
    solids = shape.solids()
    if len(solids) != 1:
        raise RuntimeError(f"{name} step has {len(solids)} solids")
    return solids[0]


poses = {"base": _identity()}
joint_frames = {}
for name, parent, child, parent_frame, child_frame, offset, angle in JOINTS:
    pose, origin, axis = _child_pose(poses[parent], parent_frame, child_frame, offset, angle)
    poses[child] = pose
    joint_frames[name] = {"origin": [origin[0], origin[1], origin[2]], "axis": [axis[0], axis[1], axis[2]]}

placements = {name: _matrix(*poses[name]) for name in BODY_ORDER}
joints = joint_frames
result = [_load(name).moved(_location(*poses[name])) for name in BODY_ORDER]
