# Enclosure base (lower body of a two-part box): design specification

One connected solid, millimetres. Build it as editable source for the selected backend, with the parameters below as
named top-level constants. The base only: no lid, no gasket, no hardware.

## Frame and datums

- Datum plane: the flat bottom face, z = 0. All material is at z >= 0.
- Origin at the centre of the footprint; +x along the 100 mm width, +y along the 150 mm length, +z up. The part is
  symmetric about the planes x = 0 and y = 0.

## Parameters

| Parameter | Value |
| --- | ---: |
| Outer width (x) | 100 |
| Outer length (y) | 150 |
| Height of the base, bottom face to rim | 47 |
| Wall thickness (side walls and floor) | 3 |
| Outer vertical corner radius | 10 |
| Outer bottom edge round | 2 |
| Inner (cavity) vertical corner radius | 7 (= 10 − 3) |
| Screw-post inset from the outer faces | 12 (post axes at x = ±38, y = ±63) |
| Screw-post outer diameter | 10 |
| Screw-post bore diameter | 4 |

The base is 47 tall: it is the lower part of a 50 mm enclosure split 4 mm below its top (the lid keeps the top 4 mm).
Do not build it 50 tall.

## Construction (the geometry to reproduce; which operations you use is up to you)

1. Outer body: a 100 × 150 footprint with r = 10 vertical corners, from z = 0 to z = 47; the bottom perimeter edge is
   rounded r = 2. The rim at z = 47 is flat and its edges are sharp (it is the parting plane with the lid).
2. Cavity: 94 × 144 (3 mm walls) with r = 7 vertical inner corners, from the floor top z = 3 up through the open top at
   z = 47. The floor is 3 thick (z 0 .. 3); the cavity floor edges are sharp.
3. Four screw posts, axes at (±38, ±63), Ø10 outside, standing on the floor from z = 3 to z = 47 and joined to it. They
   stand free of the walls.
4. Each post has a Ø4 bore from its top down to the floor top, z = 3. The bores stop at the floor: they do NOT go
   through the floor; there is solid floor under each bore.

Minimum material thickness is 3 everywhere: side walls, floor and post walls ((10 − 4) / 2).

## Reference measurements (measured on the reference model; use them for the acceptance values)

| Quantity | Value |
| --- | ---: |
| Volume | 118 431.5 mm³ |
| Bounding box (x × y × z) | 100 × 150 × 47 |
| Section z = 25 | area 1684.1 mm², 5 loops (the wall ring and four posts), 5 holes (the cavity and four bores) |
| Section z = 1.5 (floor) | area 14 883.5 mm², 1 loop, 0 holes |
| Bottom face, z = 0, facing −z | 13 961.1 mm² |
| Cavity floor, z = 3, facing +z | 13 179.8 mm² (one face, centroid at the origin) |
| Bore floors, z = 3, facing +z | four discs of 12.57 mm² at (±38, ±63) |
| Rim, z = 47, facing +z | 1420.2 mm² (the wall ring, centroid at the origin) |
| Post tops, z = 47, facing +z | four annuli of 65.97 mm² at (±38, ±63) |

## Scoring (the reference geometry is evaluator-only)

One valid connected solid after STEP re-import; envelope; volume; the faces above by level, area and centroid; the
sections above; the post and bore axes, diameters and extents (bores from z = 3 to z = 47); void points in the cavity and
in each bore; solid points in the floor (including under the bores), the walls and a post wall; a wall-thickness scan
(p05 of the inward thickness at least 2.9 mm).

## Editability

Declare edit tests on (a) the outer width, 100 → 110, with the wall thickness and the 12 mm post inset preserved (the
posts move to x = ±43): ΔV = 10 × 712.28 = 7122.83 mm³ (the x = 0 cross-section: a 150 × 3 floor strip less the two
r = 2 bottom-round corners, 448.28 mm², plus two 3 × 44 end walls, 264 mm²), bbox +10 in x; and (b) the post bore
diameter, Ø4 → Ø5 with the post axes unmoved: ΔV = −π (2.5² − 2²) · 44 · 4 = −1244.07 mm³, bbox unchanged.
