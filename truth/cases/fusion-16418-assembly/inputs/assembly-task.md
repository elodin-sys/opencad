# Assembly task: joint set joint_set_16418

Two parts are supplied as STEP files in their own local frames (millimetres): `23309_76dcf100_0002_1.step`
(body one, bbox size [20.483, 4.0, 20.483]) and `23309_76dcf100_0003_2.step` (body two, bbox size [23.0, 10.0, 69.0]).
They are joined by a Revolute joint named "Rev3". The machine-readable joint definition is `joint-task.json`
(same numbers as below).

- Body one's joint face: CylinderSurfaceType face, radius 1.55 mm, body-local bbox [-1.55, 0.0, -1.55] .. [1.55, 1.0, 1.55] mm; joint key point (StartKeyPoint) at body-local [0.0, 1.0, 0.0] mm on the face's axis, axis direction (body-local) [0.0, 1.0, 0.0].
- Body two's joint face: CylinderSurfaceType face, radius 1.55 mm, body-local bbox [9.95, 7.5, -39.55] .. [13.05, 10.0, -36.45] mm; joint key point (EndKeyPoint) at body-local [11.5, 7.5, -38.0] mm on the face's axis, axis direction (body-local) [0.0, 1.0, 0.0].
- Joint definition (Fusion 360 joint parameters, as designed): the two faces' axes are colinear in the assembled state;
  `is_flipped` = True: after placement body one's axis direction is ANTI-parallel to body two's;
  `offset` = -5.00 mm: the axial offset between the two key points, (K1' - K2') . d2' measured along body two's
  placed axis direction, equals -5.00 mm; the joint angle is 0.0000 rad in the dataset, but any rotation about a revolute
  axis is accepted.
- The evaluator (`opencad.truth.assembly_task.score`) applies your transforms in OpenCascade and checks: axis angle <= 2 deg,
  axis line distance <= 0.5 mm, |axial offset - -5.00| <= 0.5 mm, interference <= max(1 mm3, the dataset's own assembled
  interference + 1 mm3) (the dataset's pose may itself interpenetrate slightly; do not reject the key-point placement for that),
  and the bodies touch or nearly touch (gap <= 1 mm). `python -m opencad.truth assembly-check <work dir>` computes exactly
  these numbers from your `assembly.yaml` without the truth.

Deliverable: `assembly.yaml` with a placement for each body in one shared frame, e.g.

```yaml
bodies:
  23309_76dcf100_0002_1: {origin: [x, y, z], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}
  23309_76dcf100_0003_2: {origin: [0, 0, 0], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}
```

(or `matrix: 4x4` per body). Body two may stay at the identity. Do not modify the STEP files.
