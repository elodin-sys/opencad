# Assembly task: joint set joint_set_12944

Two parts are supplied as STEP files in their own local frames (millimetres): `22303_e9723631_0014_1.step`
(body one, bbox size [126.701, 15.0, 108.0]) and `22303_e9723631_0013_1.step` (body two, bbox size [26.077, 68.0, 29.032]).
They are joined by a Revolute joint named "Rev15". The machine-readable joint definition is `joint-task.json`
(same numbers as below).

- Body one's joint face: CylinderSurfaceType face, radius 9.0 mm, body-local bbox [-9.0, 0.0, -9.0] .. [9.0, 15.0, 9.0] mm; joint key point (EndKeyPoint) at body-local [0.0, 15.0, 0.0] mm on the face's axis, axis direction (body-local) [0.0, -1.0, 0.0].
- Body two's joint face: CylinderSurfaceType face, radius 8.9635 mm, body-local bbox [-8.963, -59.0, -8.963] .. [8.963, 0.0, 8.963] mm; joint key point (MiddleKeyPoint) at body-local [0.0, -29.5, 0.0] mm on the face's axis, axis direction (body-local) [0.0, -1.0, 0.0].
- Joint definition (Fusion 360 joint parameters, as designed): the two faces' axes are colinear in the assembled state;
  `is_flipped` = True: after placement body one's axis direction is ANTI-parallel to body two's;
  `offset` = 0.00 mm: the axial offset between the two key points, (K1' - K2') . d2' measured along body two's
  placed axis direction, equals 0.00 mm; the joint angle is 3.1416 rad in the dataset, but any rotation about a revolute
  axis is accepted.
- The evaluator (`opencad.truth.assembly_task.score`) applies your transforms in OpenCascade and checks: axis angle <= 2 deg,
  axis line distance <= 0.5 mm, |axial offset - 0.00| <= 0.5 mm, interference <= max(1 mm3, the dataset's own assembled
  interference + 1 mm3) (the dataset's pose may itself interpenetrate slightly; do not reject the key-point placement for that),
  and the bodies touch or nearly touch (gap <= 1 mm). `python -m opencad.truth assembly-check <work dir>` computes exactly
  these numbers from your `assembly.yaml` without the truth.

Deliverable: `assembly.yaml` with a placement for each body in one shared frame, e.g.

```yaml
bodies:
  22303_e9723631_0014_1: {origin: [x, y, z], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}
  22303_e9723631_0013_1: {origin: [0, 0, 0], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}
```

(or `matrix: 4x4` per body). Body two may stay at the identity. Do not modify the STEP files.
