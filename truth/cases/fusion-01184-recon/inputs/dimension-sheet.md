# Dimension sheet: 36938_ae684b66_0002_2

All values in mm, measured on the reference geometry in its native frame (no re-alignment). Datum: the bounding-box minimum corner is the reference frame origin offset listed below.

## Envelope and mass properties

- bbox min [100.0, 0.0, 70.0], max [110.0, 88.0, 120.0], size [10.0, 88.0, 50.0]
- solids 1, faces 14 (8 planar)
- volume 4863.73 mm3, surface area 3802.07 mm2, centre of mass [105.0, 18.856, 95.0]

## Axis-aligned planar faces (by level; faces smaller than the threshold omitted)

| normal | level | count | total area | per-face areas (largest first) | centroids (u,v in-plane) |
|---|---|---|---|---|---|
| -x | x = 100 | 1 | 100 | 100 | (5, 95) |
| +x | x = 110 | 1 | 100 | 100 | (5, 95) |
| -y | y = 0 | 1 | 100 | 100 | (105, 95) |
| +y | y = 10 | 2 | 90.27 | 45.14, 45.14 | (105, 81.28); (105, 108.72) |
| +y | y = 88 | 1 | 19.63 | 19.63 | (105, 95) |
| -z | z = 70 | 1 | 66.63 | 66.63 | (105, 5) |
| +z | z = 120 | 1 | 66.63 | 66.63 | (105, 5) |

## Cylindrical features (holes are concave, pins/bosses convex)

| kind | diameter | axis direction | axis passes through (centre of extent) | extent along axis | length | full 360 |
|---|---|---|---|---|---|---|
| hole | 5 | [0.0, 0.0, 1.0] | [105.0, 5.0, 95.0] | 70 .. 120 (from axis point [105.0, 5.0, 0.0]) | 50 | yes |
| pin | 8 | [-0.0, -0.0, 1.0] | [104.0, 4.0, 95.0] | 70 .. 120 (from axis point [104.0, 4.0, 0.0]) | 50 | partial |
| pin | 8 | [0.0, 0.0, 1.0] | [104.0, 6.0, 95.0] | 70 .. 120 (from axis point [104.0, 6.0, 0.0]) | 50 | partial |
| pin | 8 | [0.0, 0.0, 1.0] | [106.0, 4.0, 95.0] | 70 .. 120 (from axis point [106.0, 4.0, 0.0]) | 50 | partial |
| pin | 8 | [-0.0, -0.0, 1.0] | [106.0, 6.0, 95.0] | 70 .. 120 (from axis point [106.0, 6.0, 0.0]) | 50 | partial |
| pin | 5 | [-0.0, 1.0, 0.0] | [105.0, 48.854, 95.0] | 9.708 .. 88 (from axis point [105.0, 0.0, 95.0]) | 78.292 | yes |

Counts by kind and diameter: hole Ø5.0: 1; pin Ø5.0: 1; pin Ø8.0: 4

## Sections (solid material at the station)

| plane | area | outer loops | holes | regions (centroid, bbox size) |
|---|---|---|---|---|
| x = 105.0 | 640 | 2 | 0 | (1.25, 95) 2.5x50; (39.23, 95) 80.5x50 |
| y = 44.0 | 19.63 | 1 | 0 | (105, 95) 5x5 |
| z = 95.0 | 456.92 | 1 | 1 | (105, 42.56) 10x88 |
