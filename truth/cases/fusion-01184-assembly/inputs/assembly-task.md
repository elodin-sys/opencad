# Assembly task: joint set joint_set_01184

Two parts are supplied as STEP files in their own local frames (millimetres): `36938_ae684b66_0002_2.step`
(body one, bbox size [10.0, 88.0, 50.0]) and `36938_ae684b66_0001_2.step` (body two, bbox size [50.0, 3.0, 165.0]).
They are joined by a Revolute joint named "Rev3". The machine-readable joint definition is `joint-task.json`
(same numbers as below).

- Body one's joint face: CylinderSurfaceType face, radius 2.5 mm, body-local bbox [102.5, 9.708, 92.5] .. [107.5, 88.0, 97.5] mm; joint key point (StartKeyPoint) at body-local [105.0, 9.706, 95.0] mm on the face's axis, axis direction (body-local) [-0.0, 1.0, 0.0].
- Body two's joint face: CylinderSurfaceType face, radius 2.5 mm, body-local bbox [17.5, 0.0, 57.5] .. [22.5, 3.0, 62.5] mm; joint key point (StartKeyPoint) at body-local [20.0, 0.0, 60.0] mm on the face's axis, axis direction (body-local) [0.0, 1.0, 0.0].
- Joint definition (Fusion 360 joint parameters, as designed): the two faces' axes are colinear in the assembled state;
  `is_flipped` = False: after placement body one's axis direction is parallel to body two's;
  `offset` = -1.00 mm: the axial offset between the two key points, (K1' - K2') . d2' measured along body two's
  placed axis direction, equals -1.00 mm; the joint angle is 1.5708 rad in the dataset, but any rotation about a revolute
  axis is accepted.
- The evaluator (`opencad.truth.assembly_task.score`) applies your transforms in OpenCascade and checks: axis angle <= 2 deg,
  axis line distance <= 0.5 mm, |axial offset - -1.00| <= 0.5 mm, interference <= max(1 mm3, the dataset's own assembled
  interference + 1 mm3) (the dataset's pose may itself interpenetrate slightly; do not reject the key-point placement for that),
  and the bodies touch or nearly touch (gap <= 1 mm). `python -m opencad.truth assembly-check <work dir>` computes exactly
  these numbers from your `assembly.yaml` without the truth.

Deliverable: `assembly.yaml` with a placement for each body in one shared frame, e.g.

```yaml
bodies:
  36938_ae684b66_0002_2: {origin: [x, y, z], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}
  36938_ae684b66_0001_2: {origin: [0, 0, 0], x_axis: [1, 0, 0], y_axis: [0, 1, 0], z_axis: [0, 0, 1]}
```

(or `matrix: 4x4` per body). Body two may stay at the identity. Do not modify the STEP files.
