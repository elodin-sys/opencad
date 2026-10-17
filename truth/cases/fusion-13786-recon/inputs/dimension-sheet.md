# Dimension sheet: 84608_204c01e6_0008_1

All values in mm, measured on the reference geometry in its native frame (no re-alignment). Datum: the bounding-box minimum corner is the reference frame origin offset listed below.

## Envelope and mass properties

- bbox min [-50.0, -50.0, -0.0], max [50.0, 50.0, 3.0], size [100.0, 100.0, 3.0]
- solids 1, faces 18 (10 planar)
- volume 25187.47 mm3, surface area 18523.05 mm2, centre of mass [-0.0, -4.716, 1.5]

## Axis-aligned planar faces (by level; faces smaller than the threshold omitted)

| normal | level | count | total area | per-face areas (largest first) | centroids (u,v in-plane) |
|---|---|---|---|---|---|
| -x | x = -50 | 1 | 272.86 | 272.86 | (0.53, 1.5) |
| -x | x = -45 | 1 | 3.14 | 3.14 | (42, 1.5) |
| +x | x = 45 | 1 | 3.14 | 3.14 | (42, 1.5) |
| +x | x = 50 | 1 | 272.86 | 272.86 | (0.53, 1.5) |
| -y | y = -50 | 1 | 270 | 270 | (-0, 1.5) |
| +y | y = 50 | 1 | 282 | 282 | (-0, 1.5) |
| -z | z = 0 | 1 | 8331.1 | 8331.1 | (-0, -4.93) |
| +z | z = 3 | 1 | 8331.1 | 8331.1 | (-0, -4.94) |

## Inclined planar faces

| outward normal | point on plane | area | centroid |
|---|---|---|---|
| [-0.7071, -0.7071, 0.0] | [-47.5, -47.5, 0.0] | 21.21 | [-47.5, -47.5, 1.5] |
| [0.7071, -0.7071, 0.0] | [47.5, -47.5, 0.0] | 21.21 | [47.5, -47.5, 1.5] |

## Cylindrical features (holes are concave, pins/bosses convex)

| kind | diameter | axis direction | axis passes through (centre of extent) | extent along axis | length | full 360 |
|---|---|---|---|---|---|---|
| hole | 5 | [-0.0, -0.0, 1.0] | [0.0, 0.0, 1.5] | 0 .. 3 (from axis point [0.0, 0.0, 0.0]) | 3 | yes |
| hole | 2 | [1.0, -0.0, -0.0] | [0.0, 42.0, 1.5] | -50 .. 50 (from axis point [0.0, 42.0, 1.5]) | 100 | yes |
| pin | 6 | [0.0, 0.0, 1.0] | [-47.0, 47.0, 1.5] | 0 .. 3 (from axis point [-47.0, 47.0, 0.0]) | 3 | partial |
| pin | 6 | [0.0, 0.0, 1.0] | [47.0, 47.0, 1.5] | 0 .. 3 (from axis point [47.0, 47.0, 0.0]) | 3 | partial |

Counts by kind and diameter: hole Ø2.0: 1; hole Ø5.0: 1; pin Ø6.0: 2

## Sections (solid material at the station)

| plane | area | outer loops | holes | regions (centroid, bbox size) |
|---|---|---|---|---|
| x = 0.0 | 200.78 | 3 | 0 | (-26.25, 1.5) 47.5x3; (7.23, 1.5) 9.5x3; (45.02, 1.5) 10x3 |
| y = 0.0 | 285 | 2 | 0 | (-26.25, 1.5) 47.5x3; (26.25, 1.5) 47.5x3 |
| z = 1.5 | 8391.82 | 1 | 2 | (0, -4.75) 100x100 |
