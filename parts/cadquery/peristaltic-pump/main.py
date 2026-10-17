"""Rigid placement of the fourteen supplied peristaltic-pump STEP bodies."""

from pathlib import Path

import cadquery as cq

here = Path(__file__).resolve().parent
origin = (0.0, 0.0, 0.0)
x_axis = (1.0, 0.0, 0.0)
y_axis = (0.0, 1.0, 0.0)
z_axis = (0.0, 0.0, 1.0)


def frame(point, axis=y_axis, ref=x_axis):
    """Own-frame joint coordinates: local z is the axis, local x the ref."""
    return cq.Location(cq.Plane(origin=point, xDir=ref, normal=axis))


locations = {"base": cq.Location()}
joints = {}


def place(name, parent, child, parent_frame, child_frame, offset=0.0, angle=0.0):
    """Compose the joint from the datum outward; angles are right-handed."""
    world_frame = locations[parent] * parent_frame
    rest = cq.Location((0.0, 0.0, offset), z_axis, angle)
    locations[child] = world_frame * rest * child_frame.inverse
    transform = world_frame.wrapped.Transformation()
    joints[name] = {
        "origin": [transform.Value(row, 4) for row in (1, 2, 3)],
        "axis": [transform.Value(row, 3) for row in (1, 2, 3)],
    }


place(
    "motorMount",
    "base",
    "motor",
    frame((-20.5, 0.0, -20.5)),
    frame(origin, z_axis),
)
place(
    "motorSpin",
    "motor",
    "motorGear",
    frame(origin, z_axis),
    frame(origin, z_axis),
    offset=12.0,
)
place(
    "stackedSpin",
    "base",
    "stackedGear",
    frame((-20.5, 12.0, -50.5)),
    frame(origin, z_axis),
    angle=7.5,
)
place(
    "outputSpin",
    "base",
    "outputGear",
    frame((-20.5, 23.0, -20.5)),
    frame(origin, z_axis),
    angle=3.75,
)
place(
    "upperCaseMount",
    "base",
    "upperCase",
    frame((-20.5, 12.0, -20.5), ref=z_axis),
    frame((-15.5, 0.0, -30.5)),
)
place(
    "rotorDrive",
    "outputGear",
    "rotor",
    frame((0.0, 0.0, 44.125), z_axis),
    frame((-2.887, 0.0, -5.0)),
)
place(
    "statorMount",
    "upperCase",
    "stator",
    frame((-15.5, 31.0, -30.5)),
    frame((-20.5, 5.0, -20.5)),
)
place(
    "lidMount",
    "stator",
    "lid",
    frame((-20.5, 24.8, -20.5), ref=z_axis),
    frame((-20.5, 2.0, -20.5)),
)
place(
    "clampMount",
    "stator",
    "clamp",
    frame((-46.0, 30.0, -20.5), ref=z_axis),
    frame((-16.5, 0.0, -5.0)),
)
place(
    "tubeSeat",
    "stator",
    "tube",
    frame((-20.5, 29.8, -20.5)),
    frame(origin, z_axis),
)
place(
    "roller1Pin",
    "rotor",
    "roller1",
    frame((0.0, 0.675, 0.0)),
    frame(origin, z_axis),
)
place(
    "roller2Pin",
    "rotor",
    "roller2",
    frame((-8.66, 0.675, -5.0)),
    frame(origin, z_axis),
)
place(
    "roller3Pin",
    "rotor",
    "roller3",
    frame((0.0, 0.675, -10.0)),
    frame(origin, z_axis),
)


# Input units are already millimetres. This insertion order is the body order.
inputs = {
    "base": "inputs/base.step",
    "motor": "inputs/motor.step",
    "motorGear": "inputs/motorGear.step",
    "stackedGear": "inputs/stackedGear.step",
    "outputGear": "inputs/outputGear.step",
    "upperCase": "inputs/upperCase.step",
    "stator": "inputs/stator.step",
    "lid": "inputs/lid.step",
    "clamp": "inputs/clamp.step",
    "rotor": "inputs/rotor.step",
    "roller1": "inputs/roller1.step",
    "roller2": "inputs/roller2.step",
    "roller3": "inputs/roller3.step",
    "tube": "inputs/peristaltic-pump-tube.step",
}

result = []
placements = {}
for body, relative_path in inputs.items():
    solids = cq.importers.importStep(str(here / relative_path)).solids().vals()
    assert len(solids) == 1, f"Expected one supplied solid for {body}; found {len(solids)}"
    # Relative movement retains any native STEP location; no geometry is rebuilt.
    result.append(solids[0].moved(locations[body]))
    transform = locations[body].wrapped.Transformation()
    placements[body] = [[transform.Value(row, col) for col in (1, 2, 3, 4)] for row in (1, 2, 3)] + [
        [0.0, 0.0, 0.0, 1.0]
    ]
