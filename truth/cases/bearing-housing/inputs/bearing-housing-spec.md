# Cast bearing housing (oval flanged unit): design specification

One connected solid, millimetres and degrees. Build it as editable source for the selected backend, with the parameters
below as named top-level constants. The housing alone: no bearing, no screws.

## Frame and datums

- Datum plane: the flat bottom face of the flange, z = 0. The part sits on it; all material is at z >= 0.
- Reference axis: the bore axis, the z axis through the origin (0, 0), +z up out of the bore.
- The two mounting holes lie on the x axis, symmetric about the origin. The part is symmetric about the planes x = 0 and
  y = 0.

## Parameters

| Parameter | Symbol | Value |
| --- | --- | ---: |
| Overall height, flange bottom to boss top | A | 26 |
| Flange thickness | A1 | 11 |
| Boss and flange-centre diameter at z = 0 | Db2 | 57 |
| Flange length over the lobes at z = 0 | H | 98.5 |
| Mounting-hole spacing (holes at x = ±J/2, y = 0) | J | 76.5 |
| Lobe diameter at z = 0 (lobe centres = hole centres) | H − J | 22 |
| Draft angle on every side face | | 4 |
| Edge round radius on the drafted body | | 1 |
| Counterbore diameter | | 47 |
| Counterbore depth from the boss top (floor at z = 12) | | 14 |
| Through-bore diameter (z 0 .. 12) | | 14 |
| Mounting-hole diameter, through the flange (z 0 .. 11) | | 10 |

## Construction (the geometry to reproduce; which operations you use is up to you)

1. Flange: the plan outline at z = 0 is the convex hull of the Ø57 circle at the origin and two Ø22 circles at
   (±38.25, 0); straight tangent lines join each lobe to the central circle. Extrude it 11 (z 0 .. 11).
2. Boss: the Ø57 circle at z = 0 extruded to z = 26, united with the flange.
3. Draft: every side (non-horizontal) face of that union tapers inward by exactly 4° going up, about the neutral plane
   z = 0. The outline at z = 0 is the true size and shrinks by z · tan 4° at height z: at z = 11 the lobes are Ø20.46 and
   the boss Ø55.46; at z = 26 the boss is Ø53.36. Horizontal faces (bottom, flange top, boss top) stay horizontal.
4. Round every edge of the drafted body with r = 1 exactly: the outer bottom edge, the flange-top outer edge, the concave
   flange-to-boss edge and the boss-top outer edge. The rounds come BEFORE any hole is cut.
5. Counterbore Ø47 × 14 deep from the boss top face (floor at z = 12) and the Ø14 bore through the remaining 12 mm to the
   bottom face.
6. Two Ø10 mounting holes through the flange at (±38.25, 0).

The bore, counterbore and mounting-hole edges are sharp (cut after the rounds). The draft is a true 4° taper, not an
approximation, and every edge round is a true r = 1 round.

## Reference measurements (measured on the reference model; use them for the acceptance values)

| Quantity | Value |
| --- | ---: |
| Volume | 46 881.3 mm³ |
| Bounding box (x × y × z) | 98.355 × 56.855 × 26.000 (the r = 1 round on the drafted bottom edge pulls the extremes in from 98.5 × 57) |
| Section z = 5.5 (flange) | area 3321.8 mm², 1 loop, 3 holes (bore and both mounting holes) |
| Section z = 15 (boss annulus) | area 632.4 mm², 1 loop, 1 hole |
| Section z = 24 (boss annulus) | area 525.1 mm², 1 loop, 1 hole |
| Section y = 0 | area 844.4 mm², 4 separate loops (lobe ends and the two halves either side of the bore) |
| Bottom face, z = 0, facing −z | 3161.0 mm² (one face) |
| Counterbore floor, z = 12, facing +z | 1581.0 mm² (annulus Ø14 .. Ø47) |
| Flange tops, z = 11, facing +z | two faces of 369.2 mm², centroids at x = ±34.38 |
| Boss top, z = 26, facing +z | 348.0 mm² (annulus between the counterbore and the start of the r = 1 round) |
| Drafted tangent flats | four planar faces of 311.4 mm², outward normals (±0.4564, ±0.8870, 0.0698), centroids (±27.79, ±17.31, 5.64) |

## Scoring (the reference geometry is evaluator-only)

One valid connected solid after STEP re-import; envelope; volume; the horizontal faces above by level and area; the four
drafted flats by their normals; the sections above (the draft shows up as the boss annulus shrinking with height); the
axes, diameters and depths of the counterbore, bore and mounting holes; solid points in the flange, the boss wall and the
material under the counterbore floor; void points in the counterbore, the bore, both mounting holes and the air above the
flange beside the boss.

## Editability

Declare edit tests on (a) the mounting-hole diameter, Ø10 → Ø11 (ΔV = −π (5.5² − 5²) · 11 · 2 = −362.85 mm³, bbox
unchanged, the bore and counterbore unmoved) and (b) the through-bore diameter, Ø14 → Ø15 (ΔV = −π (7.5² − 7²) · 12 =
−273.32 mm³, bbox unchanged, the mounting holes unmoved). Both edits touch only holes cut after the rounds.

Robustness note: drafting this tangent hull and rounding every edge rebuilds in OpenCascade at the nominal outline above
but fails for most other values of J, H or Db2 (measured on the reference construction). Do not declare edit tests or
sweeps on the outline parameters (A, A1, Db2, H, J); they stay fixed in this case.
