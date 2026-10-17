# Assembly task: joint set joint_set_13786

Two parts are supplied as STEP files in their own local frames (millimetres): `84608_204c01e6_0008_1.step`
(body one, bbox size [100.0, 100.0, 3.0]) and `84608_204c01e6_0008_2.step` (body two, bbox size [16.2, 4.0, 4.0]).
They are joined by a Revolute joint named "Rev9". The machine-readable joint definition is `joint-task.json`
(same numbers as below).

- Body one's joint face: CylinderSurfaceType face, radius 1.0 mm, body-local bbox [45.0, 41.0, 0.5] .. [50.0, 43.0, 2.5] mm; joint key point (EndKeyPoint) at body-local [50.0, 42.0, 1.5] mm on the face's axis, axis direction (body-local) [-1.0, 0.0, 0.0].
- Body two's joint face: CylinderSurfaceType face, radius 2.0 mm, body-local bbox [0.733, 39.629, 48.8] .. [15.0, 41.129, 50.3] mm; joint key point (StartKeyPoint) at body-local [15.0, 40.3792, 49.5496] mm on the face's axis, axis direction (body-local) [1.0, 0.0, 0.0].
- Joint definition (Fusion 360 joint parameters, as designed): the two faces' axes are colinear in the assembled state;
  `is_flipped` = True: after placement body one's axis direction is ANTI-parallel to body two's;
  `offset` = -4.00 mm: the axial offset between the two key points, (K1' - K2') . d2' measured along body two's
  placed axis direction, equals -4.00 mm; the joint angle is 0.0000 rad in the dataset, but any rotation about a revolute
  axis is accepted.
- Motion limits in the dataset: {'rotation_limits': {'minimum_value': -2.707005669843205, 'maximum_value': 0.0, 'rest_value': -0.5235987755982988, 'is_minimum_value_enabled': True, 'is_maximum_value_enabled': True}} (radians / mm).
- The evaluator (`opencad.truth.assembly_task.score`) applies your transforms in OpenCascade and checks: axis angle <= 2 deg,
  axis line distance <= 0.5 mm, |axial offset - -4.00| <= 0.5 mm, interference <= max(1 mm3, the dataset's own assembled
  interference + 1 mm3) (the dataset's pose may itself interpenetrate slightly; do not reject the key-point placement for that),
  and the bodies touch or nearly touch (gap <= 1 mm). `python -m opencad.truth assembly-check <work dir>` computes exactly
  these numbers from your `assembly.yaml` without the truth.

Deliverable: `assembly.yaml` with a placement for each body in one shared frame, e.g.

```yaml
bodies:
  84608_204c01e6_0008_1: {origin: [x, y, z], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}
  84608_204c01e6_0008_2: {origin: [0, 0, 0], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}
```

(or `matrix: 4x4` per body). Body two may stay at the identity. Do not modify the STEP files.
