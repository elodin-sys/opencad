"""Peristaltic pump: rigid placements of the fourteen supplied STEP bodies.

Joint frames and rest values are from the AssemblyContract, in millimetres and
degrees. Inputs already have their final scale. No part geometry is constructed
or modified here; the base input frame is the assembly frame.
"""

import math
from pathlib import Path

import FreeCAD
import Part


def multiply(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def frame(origin, axis, ref):
    """Right-handed frame with columns (ref, axis cross ref, axis)."""
    tangent = (
        axis[1] * ref[2] - axis[2] * ref[1],
        axis[2] * ref[0] - axis[0] * ref[2],
        axis[0] * ref[1] - axis[1] * ref[0],
    )
    return [[ref[i], tangent[i], axis[i], origin[i]] for i in range(3)] + [[0.0, 0.0, 0.0, 1.0]]


def inverse_rigid(matrix):
    rotation = [[matrix[j][i] for j in range(3)] for i in range(3)]
    return [rotation[i] + [-sum(rotation[i][j] * matrix[j][3] for j in range(3))] for i in range(3)] + [
        [0.0, 0.0, 0.0, 1.0]
    ]


identity = [[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]]
x_axis = (1.0, 0.0, 0.0)
y_axis = (0.0, 1.0, 0.0)
z_axis = (0.0, 0.0, 1.0)
zero = (0.0, 0.0, 0.0)
placements = {"base": identity}
joints = {}


def mount(name, parent, child, parent_frame, child_frame, offset=0.0, angle=0.0):
    """M_child = M_parent F_parent Tz(offset) Rz(angle) inverse(F_child)."""
    world_frame = multiply(placements[parent], frame(*parent_frame))
    cosine, sine = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    rest = [
        [cosine, -sine, 0.0, 0.0],
        [sine, cosine, 0.0, 0.0],
        [0.0, 0.0, 1.0, offset],
        [0.0, 0.0, 0.0, 1.0],
    ]
    placements[child] = multiply(multiply(world_frame, rest), inverse_rigid(frame(*child_frame)))
    # Joint axes use the parent frame's origin, before the axial rest offset.
    joints[name] = {"origin": [row[3] for row in world_frame[:3]], "axis": [row[2] for row in world_frame[:3]]}


mount(
    "motorMount",
    "base",
    "motor",
    ((-20.5, 0.0, -20.5), y_axis, x_axis),
    (zero, z_axis, x_axis),
)
mount(
    "motorSpin",
    "motor",
    "motorGear",
    (zero, z_axis, x_axis),
    (zero, z_axis, x_axis),
    offset=12.0,
)
mount(
    "stackedSpin",
    "base",
    "stackedGear",
    ((-20.5, 12.0, -50.5), y_axis, x_axis),
    (zero, z_axis, x_axis),
    angle=7.5,
)
mount(
    "outputSpin",
    "base",
    "outputGear",
    ((-20.5, 23.0, -20.5), y_axis, x_axis),
    (zero, z_axis, x_axis),
    angle=3.75,
)
mount(
    "upperCaseMount",
    "base",
    "upperCase",
    ((-20.5, 12.0, -20.5), y_axis, z_axis),
    ((-15.5, 0.0, -30.5), y_axis, x_axis),
)
mount(
    "rotorDrive",
    "outputGear",
    "rotor",
    ((0.0, 0.0, 44.125), z_axis, x_axis),
    ((-2.887, 0.0, -5.0), y_axis, x_axis),
)
mount(
    "statorMount",
    "upperCase",
    "stator",
    ((-15.5, 31.0, -30.5), y_axis, x_axis),
    ((-20.5, 5.0, -20.5), y_axis, x_axis),
)
mount(
    "lidMount",
    "stator",
    "lid",
    ((-20.5, 24.8, -20.5), y_axis, z_axis),
    ((-20.5, 2.0, -20.5), y_axis, x_axis),
)
mount(
    "clampMount",
    "stator",
    "clamp",
    ((-46.0, 30.0, -20.5), y_axis, z_axis),
    ((-16.5, 0.0, -5.0), y_axis, x_axis),
)
mount(
    "tubeSeat",
    "stator",
    "tube",
    ((-20.5, 29.8, -20.5), y_axis, x_axis),
    (zero, z_axis, x_axis),
)
mount(
    "roller1Pin",
    "rotor",
    "roller1",
    ((0.0, 0.675, 0.0), y_axis, x_axis),
    (zero, z_axis, x_axis),
)
mount(
    "roller2Pin",
    "rotor",
    "roller2",
    ((-8.66, 0.675, -5.0), y_axis, x_axis),
    (zero, z_axis, x_axis),
)
mount(
    "roller3Pin",
    "rotor",
    "roller3",
    ((0.0, 0.675, -10.0), y_axis, x_axis),
    (zero, z_axis, x_axis),
)

# Keep export order identical to the contract body table.
input_files = (
    ("base", "inputs/base.step"),
    ("motor", "inputs/motor.step"),
    ("motorGear", "inputs/motorGear.step"),
    ("stackedGear", "inputs/stackedGear.step"),
    ("outputGear", "inputs/outputGear.step"),
    ("upperCase", "inputs/upperCase.step"),
    ("stator", "inputs/stator.step"),
    ("lid", "inputs/lid.step"),
    ("clamp", "inputs/clamp.step"),
    ("rotor", "inputs/rotor.step"),
    ("roller1", "inputs/roller1.step"),
    ("roller2", "inputs/roller2.step"),
    ("roller3", "inputs/roller3.step"),
    ("tube", "inputs/peristaltic-pump-tube.step"),
)

here = Path(__file__).resolve().parent
doc = FreeCAD.newDocument("peristaltic_pump")
result = []
for body_name, relative_path in input_files:
    imported_shape = Part.Shape()
    imported_shape.read(str(here / relative_path))
    assert len(imported_shape.Solids) == 1, f"{body_name}: expected one supplied solid"
    feature = doc.addObject("Part::Feature", body_name)
    feature.Shape = imported_shape
    transform = FreeCAD.Matrix(*[value for row in placements[body_name] for value in row])
    # Preserve any intrinsic STEP location while applying the declared transform.
    feature.Placement = FreeCAD.Placement(transform).multiply(feature.Placement)
    result.append(feature)

doc.recompute()
