# fusion-16418-recon — design brief

## 1. Intent and configuration

Reconstruct the mechanical part shown in the attached renders, sections and dimension sheet as editable, parameterized KCL in the part's own frame (bbox min [-10.242, 0.0, -10.242], size [20.483, 4.0, 20.483] mm). Declare every hole, boss and shaft as an acceptance cylinder and every planar face level as a named face; one solid; export STEP and STL. Held-out: the pipeline is frozen, the reference CAD is evaluator-only.

The part is a 36-tooth disc with a pointy-top hexagonal drive boss on +y, a hexagonal socket through the boss down to y = 1, and a Ø3.1 hole through the remaining 1 mm floor. Authoritative numbers come from `sources/dimension-sheet.md` (native-frame measurements of the held-out reference). Images confirm topology, tooth count and hex clocking. The reference CAD is evaluator-only and is not in this bundle. This stage writes the contract and brief only; it contains no KCL.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/part-brief.md | text | authoritative | 539d004699f714a06e332307d4492898bea539d8b99fece78c43e6232ce55adc | Prefix 539d004699f7. Names Fusion Gallery body 23309_76dcf100_0002_1 / joint_set_16418, native frame, one solid, STEP and STL. |
| sources/dimension-sheet.md | text | authoritative | 7d3413c8a07dd7a0739e4f0c2262587aed84b8baf2d2bdacf31f37bf758555f8 | Prefix 7d3413c8a07d. Envelope, mass properties, 8 face levels, 12 inclined planes, 38 cylinders, 3 sections. |
| sources/render-notes.md | text | illustrative | 5f9477cd2b1c1233b9eeae3aaac0558ca44c95df2c5321cfeed8111beb887114 | Prefix 5f9477cd2b1c. 4044-triangle render list; extents 20.483 x 4.000 x 20.483 mm. |
| sources/front.png | image | illustrative | 035beba138156d44c9f5edb73da5a823e0aa5f2a7fecac2aec2932b47ce5b374 | Prefix 035beba13815. Orthographic XZ, mm grid. |
| sources/top.png | image | illustrative | 8d47253523dcf7475880132e6a4e7632f6acf6f23351989d73de92f974d21cb7 | Prefix 8d47253523dc. Orthographic XY, mm grid. |
| sources/right.png | image | illustrative | 6197f27313adbba08e45760699a7ce0ec8c87a61ab2f1a8504048b9c9a6d1dfe | Prefix 6197f27313ad. Orthographic ZY, mm grid. |
| sources/iso.png | image | illustrative | f2be75464db1b2631d4ea1135d2dbeb626f582b0c93f052be4ae8906bf53dca6 | Prefix f2be75464db1. Circular y=0 face and hole. |
| sources/iso2.png | image | illustrative | 00701f6472fc7264c630b2507ca5b6d20cfb1c6d661d753be9f2109ab6c8874e | Prefix 00701f6472fc. Pointy-top hex boss. |
| sources/iso-below.png | image | illustrative | a47b41a08f125b259bf42f963273dc770acc596b9bb373ba3f98d5195447ce74 | Prefix a47b41a08f12. Underside. |
| sources/section-x0.png | image | illustrative | 787d1eb358fec02f11e3daeb045448041992f560a54951e7bc8c873654497280 | Prefix 787d1eb358fe. Two islands. |
| sources/section-y2.png | image | illustrative | 3c1ea5cb54a63bc61e197893d9f2c839a95644c1ec81bcecfae227485e947c19 | Prefix 3c1ea5cb54a6. 36 teeth + hex; caption 256.74 mm2. |
| sources/section-z0.png | image | illustrative | 2f796c1eeffdb9a891e789f839f84c3e894943642a3495a7e110e2f5a0d60761 | Prefix 2f796c1eeffd. Two islands; caption 46.23 mm2. |

The same nine PNGs live under `truth/cases/fusion-16418-recon/inputs/renders/` with identical SHA-256. No `reference/` ingest (`reference.json` / `profile.json`) was supplied. Held-out reference CAD is evaluator-only.

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| One solid; STEP and STL | 1 body; two exports | count / files | part-brief; user intent | exact topology | stated; solid_count, solids.gear |
| Native frame envelope | min [-10.242, 0, -10.242], max [10.242, 4, 10.242], size [20.483, 4, 20.483] | mm | part-brief; dimension-sheet | 0.05 bbox | stated; envelope, spanX/Y/Z. Size vs max-min 0.001 mm is open |
| Volume / area / COM | 827.65 / 963.43 / [0, 1.515, 0] | mm3 / mm2 / mm | dimension-sheet mass properties | 2 mm3; 5 mm2; 0.05 mm | stated |
| Face count (info) | 161 faces, 88 planar | count | dimension-sheet | not a gate | stated; 12 hex sides + 72 flanks + 4 y-faces = 88 |
| Axis-aligned face levels | x=±3.463, ±4.332; y=0,1,3,4 | mm | dimension-sheet face table | 0.02 mm | stated; 8 named faces |
| Hex socket | pointy-top, vertex R=4, flats ±3.463, floor y=1, through y=4 | mm | faces + inclined planes + sections + iso2.png | 0.02 mm | stated |
| Hex boss | pointy-top, vertex R=5, flats ±4.332, y=3..4 | mm | faces + inclined planes + top.png | 0.02 mm | stated |
| Floor bore | Ø3.1, y=0..1, axis [0,y,0] | mm | cylinder table | 0.02 mm | stated; boreHole, boreCount |
| Dedendum cylinder | Ø19 pin, partial, y=0..3 | mm | cylinder table | 0.02 mm | stated; rootCylinder. True root vs envelope is open |
| Tip fillets | 36 × Ø0.2 pins on r=10.142, 10 deg from +x, y=0..3 | mm / count | cylinder table; front.png count | 0.05 mm axis; exact count | stated |
| Tooth count | 36 | count | 36 tip pins; front.png and section-y2.png | exact | stated; gears.teeth |
| Tooth form | unspecified | — | images show straight-looking flanks, rounded tips | — | open |
| Sections | x=0 area 44.36 loops 2; y=2 area 256.75 loops 1 holes 1; z=0 area 46.23 loops 2 | mm2 / topology | dimension-sheet sections; section-*.png | 1–2% area | stated |
| Inclined hex walls | 8 planes (4 inner area 12, 4 outer area 5) | mm2 | dimension-sheet inclined table | 0.02 mm; 0.5 deg | stated |
| Listed tooth flanks | 4 planes area 2.45; 68 omitted | mm2 | dimension-sheet (below-threshold omitted) | 0.05 mm | stated (4); open (68) |
| Held-out reference | evaluator-only; no tuning | — | part-brief; orchestrator notes | — | stated; deviation null |

## 4. Coordinate frame, scale, and measurement method

Origin is the intersection of the common axis with the circular face at y = 0, [0,0,0]. The dimension sheet is already in this native frame (no re-alignment). +x toward the +x envelope (right in front.png); +y from the circular face toward the hex boss (up in top.png); +z completes the right-handed triad (up in front.png). Datum A is y = 0, outward −y. Datum B is the axis x = z = 0 along +y. Datum C is hex clocking: pointy-top hex, flats parallel to YZ, tooth 0 tip on +x.

All linear values used in the contract are transcribed from `sources/dimension-sheet.md`. Images were not used as a dimension source. They were opened and used as follows:

- Scale: every render is an orthographic plot with millimetre axes (front/top/right/section-y2 labelled x(mm), y(mm) or z(mm); grid 1 mm). Pixel-to-mm scale is the plotted axis, not an independent calibration. Line width is about 0.05–0.1 mm on the section outlines; that uncertainty is not used because numbers come from the sheet.
- front.png: counted 36 teeth around the silhouette; a tip sits on +x, +z, −x and −z; circular hole at the origin. Matches 36 Ø0.2 pins on r = 10.142 at k×10 deg.
- top.png: disc band y = 0..3 from x ≈ −10.24 to +10.24; raised hub y = 3..4 over |x| ≲ 4.3 (outer hex flats). Vertical stripes are tooth walls.
- right.png: same y steps viewed along x.
- iso.png / iso-below.png: circular y = 0 face and the through hole; no hex on this side.
- iso2.png: pointy-top hex boss; flats left/right, vertices toward ±z in the front view.
- section-y2.png: 36-tooth outer loop and inner hex hole; caption solid area 256.74 mm2 vs sheet 256.75; hex vertices at (0, ±4), vertical flats at x ≈ ±3.46.
- section-x0.png / section-z0.png: two islands; floor at y = 1; boss to y = 4; hex cut is longer in x=0 (vertices) than in z=0 (flats). section-z0 caption 46.23 mm2 matches the sheet.

Tip-fillet axes from the sheet lie on a circle of radius 10.1414–10.1421 mm (mean 10.1418). Polar angles sort to 0, 10, …, 350 deg with maximum error 0.0034 deg. The contract stores the sheet coordinates, not regenerated ones. tipOuterRadius = tipCircleRadius + tipFilletRadius = 10.242 mm matches |envelope min/max| on x and z.

Inner hex: flats at x = ±3.463, area 12 = 4 mm side × 3 mm depth (y = 1..4). Vertex radius 4 from the plane-table points at z = ±4. Outer hex: flats ±4.332, area 5 = 5 mm side × 1 mm height; vertex radius 5. Face-area checks: outer hex area (3√3/2)×25 = 64.952; inner (3√3/2)×16 = 41.569; ring 23.383 vs sheet y=4 area 23.38; hex-minus-hole 41.569 − π×1.55² = 34.022 vs y=1 area 34.02.

No mesh or coordinate-table ingest is present, so no `measured (reference model)` parameters.

## 5. Measurement and inference record

There are 29 parameters: 19 stated, 9 derived, 1 inferred; 0 measured, 0 measured (reference model), 0 defaulted. Each later KCL declaration must be a literal top-level constant with this identifier.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| envelopeMinX | -10.242 mm | 0.01 | stated | sources/dimension-sheet.md — Envelope and mass properties: bbox min [-10.242, 0.0, -10.242] |
| envelopeMinY | 0.0 mm | 0.01 | stated | sources/dimension-sheet.md — Envelope and mass properties: bbox min y = 0.0; axis-aligned face y = 0 |
| envelopeMinZ | -10.242 mm | 0.01 | stated | sources/dimension-sheet.md — Envelope and mass properties: bbox min [-10.242, 0.0, -10.242] |
| envelopeSizeX | 20.483 mm | 0.01 | stated | sources/dimension-sheet.md — Envelope and mass properties: size [20.483, 4.0, 20.483] |
| envelopeSizeY | 4.0 mm | 0.01 | stated | sources/dimension-sheet.md — Envelope and mass properties: size y = 4.0; face y = 4 |
| envelopeSizeZ | 20.483 mm | 0.01 | stated | sources/dimension-sheet.md — Envelope and mass properties: size [20.483, 4.0, 20.483] |
| discThickness | 3.0 mm | 0.01 | stated | sources/dimension-sheet.md — face +y at y = 3; pin Ø19 and Ø0.2 extent 0 .. 3 |
| hexFloorY | 1.0 mm | 0.01 | stated | sources/dimension-sheet.md — axis-aligned face +y at y = 1, area 34.02 |
| hexPocketFlat | 3.463 mm | 0.01 | stated | sources/dimension-sheet.md — axis-aligned faces x = ±3.463, area 12 each |
| hexBossFlat | 4.332 mm | 0.01 | stated | sources/dimension-sheet.md — axis-aligned faces x = ±4.332, area 5 each |
| hexPocketVertex | 4.0 mm | 0.02 | stated | sources/dimension-sheet.md — inclined planes: points (0.003, 3, 4.0) and (-0.003, 3, -4.0) |
| hexBossVertex | 5.0 mm | 0.02 | stated | sources/dimension-sheet.md — inclined planes: points (0.003, 3, 5.0) and (-0.003, 3, -5.0) |
| boreDiameter | 3.1 mm | 0.02 | stated | sources/dimension-sheet.md — cylindrical features: hole Ø3.1; counts hole Ø3.1: 1 |
| boreLength | 1.0 mm | 0.02 | stated | sources/dimension-sheet.md — hole Ø3.1 extent 0 .. 1 from [0,0,0], length 1 |
| rootDiameter | 19.0 mm | 0.02 | stated | sources/dimension-sheet.md — cylindrical features: pin Ø19, partial, length 3; counts pin Ø19.0: 1 |
| tipFilletDiameter | 0.2 mm | 0.02 | stated | sources/dimension-sheet.md — 36 pins Ø0.2, partial, length 3; counts pin Ø0.2: 36 |
| tipCircleRadius | 10.142 mm | 0.02 | stated | sources/dimension-sheet.md — Ø0.2 pin axes, e.g. [10.142, 0, 0] and [0, 0, ±10.142] |
| toothCount | 36.0  | 1e-06 | stated | sources/dimension-sheet.md — counts pin Ø0.2: 36; front.png and section-y2.png tooth count |
| toothPhase | 0.0 deg | 0.05 | stated | sources/dimension-sheet.md — tip pin at [10.142, 1.5, 0.0]; front.png tooth on +x and +z |
| hubHeight | 1.0 mm | 0.01 | derived | envelopeSizeY - discThickness |
| hexPocketDepth | 3.0 mm | 0.01 | derived | envelopeSizeY - hexFloorY |
| hexPocketAcross | 6.926 mm | 0.02 | derived | 2 * hexPocketFlat |
| hexBossAcross | 8.664 mm | 0.02 | derived | 2 * hexBossFlat |
| boreRadius | 1.55 mm | 0.01 | derived | boreDiameter / 2 |
| rootRadius | 9.5 mm | 0.01 | derived | rootDiameter / 2 |
| tipFilletRadius | 0.1 mm | 0.01 | derived | tipFilletDiameter / 2 |
| tipOuterRadius | 10.242 mm | 0.02 | derived | tipCircleRadius + tipFilletRadius |
| toothPitchDeg | 10.0 deg | 0.01 | derived | 360 / toothCount |
| gearModule | 0.569 mm | 0.05 | inferred | No module, pitch diameter or pressure angle is stated. 2*tipOuterRadius/toothCount = 0.569 mm is only the inspector tooth-count threshold (tipRadius - 0.6*module stays on the tooth body, above the Ø19 root). It is not a claim that the teeth are standard involute of this module. |

Cross-checks used only as evidence, not as extra parameters: y=0 area 290.77 = (y=2 area 256.75 + inner hex 41.569) − hole 7.548; y=3 area 233.37 = toothed outline 298.32 − outer hex 64.952.

Edit tests (analytic, not executed CAD):

| parameter change | expected volume_delta (mm3) | direction | expected bbox_delta (mm) | formula / safeguards |
|---|---|---|---|---|
| envelopeSizeY: 4 → 5 | 23.38 | increase | [0, 1, 0] | Grow the hex-boss cap in +y; ΔV = hexBossTop area × 1. Sweep [3.5, 4, 5]. Delta −4 yields height 0 and must assert. |
| hexFloorY: 1 → 0.8 | −6.804 | decrease | [0, 0, 0] | Lower the socket floor; ΔV = −34.02 × 0.2 (stated y=1 area). Sweep [0.6, 1.0, 1.4]. Delta −1.2 puts the floor below y=0; +3.1 puts it above the boss cap. |

Pinned interfaces keep the y=0 seat, bore axis, hex across-flats and diagonal walls, mid-disc section, and named root/cardinal tip cylinders. spanY / hexBossTop / hexFloor move with the matching edit and are not pinned as constants.

| acceptance value | value | tolerance / interpretation | provenance | formula / evidence |
|---|---|---|---|---|
| envelope.min | [-10.242, 0.0, -10.242] | 0.05 mm | stated | dimension-sheet envelope bbox min |
| envelope.max | [10.242, 4.0, 10.242] | 0.05 mm | stated | dimension-sheet envelope bbox max |
| acceptance.bbox_tolerance | 0.05 | mm | defaulted | Digital comparison band covering the 0.001 mm size/min-max rounding |
| volume.expected | 827.65 | 2.0 mm3 | stated | dimension-sheet mass properties |
| surface_area.expected | 963.43 | 5.0 mm2 | stated | dimension-sheet mass properties; 161 faces, 88 planar |
| center_of_mass.expected | [0.0, 1.515, 0.0] | 0.05 mm | stated | dimension-sheet mass properties; unit-density geometric centroid |
| solid_count | 1 | exact | stated | part-brief and dimension-sheet: solids 1 |
| sections.x0.plane/at | x = 0.0 | inside envelope | stated | dimension-sheet sections table |
| sections.x0.area | 44.36 | 0.02 rel | stated | dimension-sheet sections table |
| sections.x0.loops | 2 | exact | stated | dimension-sheet outer loops |
| sections.x0.holes | 0 | exact | stated | dimension-sheet holes |
| sections.y2.plane/at | y = 2.0 | inside envelope | stated | dimension-sheet sections table |
| sections.y2.area | 256.75 | 0.01 rel | stated | dimension-sheet sections table |
| sections.y2.loops | 1 | exact | stated | dimension-sheet outer loops |
| sections.y2.holes | 1 | exact | stated | dimension-sheet holes |
| sections.z0.plane/at | z = 0.0 | inside envelope | stated | dimension-sheet sections table |
| sections.z0.area | 46.23 | 0.02 rel | stated | dimension-sheet sections table |
| sections.z0.loops | 2 | exact | stated | dimension-sheet outer loops |
| sections.z0.holes | 0 | exact | stated | dimension-sheet holes |
| faces.hexBossLeft.plane/at/normal | x = -4.332, - | 0.02 mm | stated | dimension-sheet axis-aligned faces |
| faces.hexBossLeft.area | 5.0 | 0.02 rel | stated | dimension-sheet total area at that level (count 1) |
| faces.hexBossLeft.center | [3.5, 0.0] | in-plane (u,v) | stated | dimension-sheet centroids; x-faces (y,z), y-faces (x,z) |
| faces.hexBossLeft.mode | one | explicit | stated | one face at the level |
| faces.hexPocketLeft.plane/at/normal | x = -3.463, + | 0.02 mm | stated | dimension-sheet axis-aligned faces |
| faces.hexPocketLeft.area | 12.0 | 0.02 rel | stated | dimension-sheet total area at that level (count 1) |
| faces.hexPocketLeft.center | [2.5, 0.0] | in-plane (u,v) | stated | dimension-sheet centroids; x-faces (y,z), y-faces (x,z) |
| faces.hexPocketLeft.mode | one | explicit | stated | one face at the level |
| faces.hexPocketRight.plane/at/normal | x = 3.463, - | 0.02 mm | stated | dimension-sheet axis-aligned faces |
| faces.hexPocketRight.area | 12.0 | 0.02 rel | stated | dimension-sheet total area at that level (count 1) |
| faces.hexPocketRight.center | [2.5, 0.0] | in-plane (u,v) | stated | dimension-sheet centroids; x-faces (y,z), y-faces (x,z) |
| faces.hexPocketRight.mode | one | explicit | stated | one face at the level |
| faces.hexBossRight.plane/at/normal | x = 4.332, + | 0.02 mm | stated | dimension-sheet axis-aligned faces |
| faces.hexBossRight.area | 5.0 | 0.02 rel | stated | dimension-sheet total area at that level (count 1) |
| faces.hexBossRight.center | [3.5, 0.0] | in-plane (u,v) | stated | dimension-sheet centroids; x-faces (y,z), y-faces (x,z) |
| faces.hexBossRight.mode | one | explicit | stated | one face at the level |
| faces.discBottom.plane/at/normal | y = 0.0, - | 0.02 mm | stated | dimension-sheet axis-aligned faces |
| faces.discBottom.area | 290.77 | 0.01 rel | stated | dimension-sheet total area at that level (count 1) |
| faces.discBottom.center | [0.0, 0.0] | in-plane (u,v) | stated | dimension-sheet centroids; x-faces (y,z), y-faces (x,z) |
| faces.discBottom.mode | one | explicit | stated | one face at the level |
| faces.hexFloor.plane/at/normal | y = 1.0, + | 0.02 mm | stated | dimension-sheet axis-aligned faces |
| faces.hexFloor.area | 34.02 | 0.01 rel | stated | dimension-sheet total area at that level (count 1) |
| faces.hexFloor.center | [0.0, 0.0] | in-plane (u,v) | stated | dimension-sheet centroids; x-faces (y,z), y-faces (x,z) |
| faces.hexFloor.mode | one | explicit | stated | one face at the level |
| faces.discTop.plane/at/normal | y = 3.0, + | 0.02 mm | stated | dimension-sheet axis-aligned faces |
| faces.discTop.area | 233.37 | 0.01 rel | stated | dimension-sheet total area at that level (count 1) |
| faces.discTop.center | [0.0, 0.0] | in-plane (u,v) | stated | dimension-sheet centroids; x-faces (y,z), y-faces (x,z) |
| faces.discTop.mode | one | explicit | stated | one face at the level |
| faces.hexBossTop.plane/at/normal | y = 4.0, + | 0.02 mm | stated | dimension-sheet axis-aligned faces |
| faces.hexBossTop.area | 23.38 | 0.01 rel | stated | dimension-sheet total area at that level (count 1) |
| faces.hexBossTop.center | [0.0, 0.0] | in-plane (u,v) | stated | dimension-sheet centroids; x-faces (y,z), y-faces (x,z) |
| faces.hexBossTop.mode | one | explicit | stated | one face at the level |
| cylinders.boreHole.point | [0.0, 0.5, 0.0] | axis offset <= 0.02 mm | stated | dimension-sheet centre of extent |
| cylinders.boreHole.diameter/kind/length | Ø3.1 hole L=1.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.rootCylinder.point | [0.0, 1.5, 0.0] | axis offset <= 0.02 mm | stated | dimension-sheet centre of extent |
| cylinders.rootCylinder.diameter/kind/length | Ø19.0 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet0.point | [10.142, 1.5, 0.0] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet0.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet1.point | [9.988, 1.5, 1.761] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet1.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet2.point | [9.53, 1.5, 3.469] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet2.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet3.point | [8.783, 1.5, 5.071] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet3.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet4.point | [7.769, 1.5, 6.519] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet4.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet5.point | [6.519, 1.5, 7.769] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet5.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet6.point | [5.071, 1.5, 8.783] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet6.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet7.point | [3.468, 1.5, 9.53] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet7.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet8.point | [1.761, 1.5, 9.988] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet8.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet9.point | [-0.0, 1.5, 10.142] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet9.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet10.point | [-1.761, 1.5, 9.988] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet10.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet11.point | [-3.469, 1.5, 9.53] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet11.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet12.point | [-5.071, 1.5, 8.783] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet12.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet13.point | [-6.519, 1.5, 7.769] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet13.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet14.point | [-7.769, 1.5, 6.519] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet14.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet15.point | [-8.783, 1.5, 5.071] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet15.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet16.point | [-9.53, 1.5, 3.468] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet16.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet17.point | [-9.988, 1.5, 1.761] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet17.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet18.point | [-10.142, 1.5, -0.0] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet18.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet19.point | [-9.988, 1.5, -1.761] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet19.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet20.point | [-9.53, 1.5, -3.469] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet20.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet21.point | [-8.783, 1.5, -5.071] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet21.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet22.point | [-7.769, 1.5, -6.519] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet22.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet23.point | [-6.519, 1.5, -7.769] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet23.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet24.point | [-5.071, 1.5, -8.783] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet24.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet25.point | [-3.468, 1.5, -9.53] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet25.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet26.point | [-1.761, 1.5, -9.988] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet26.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet27.point | [0.0, 1.5, -10.142] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet27.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet28.point | [1.761, 1.5, -9.988] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet28.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet29.point | [3.469, 1.5, -9.53] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet29.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet30.point | [5.071, 1.5, -8.783] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet30.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet31.point | [6.519, 1.5, -7.769] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet31.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet32.point | [7.769, 1.5, -6.519] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet32.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet33.point | [8.783, 1.5, -5.071] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet33.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet34.point | [9.53, 1.5, -3.468] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet34.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| cylinders.tipFillet35.point | [9.988, 1.5, -1.761] | axis offset <= 0.05 mm | stated | dimension-sheet centre of extent |
| cylinders.tipFillet35.diameter/kind/length | Ø0.2 pin L=3.0 | radius 0.02; length 0.02 | stated | dimension-sheet cylindrical features |
| planes.hexPocket60.point/normal/area | [3.466, 3.0, 1.997] / [-0.5006, 0.0, -0.8657] / 12.0 | pos 0.02; 0.5 deg; area 0.02 rel | stated | dimension-sheet inclined planar faces |
| planes.hexPocket120.point/normal/area | [0.003, 3.0, 4.0] / [0.4994, 0.0, -0.8664] / 12.0 | pos 0.02; 0.5 deg; area 0.02 rel | stated | dimension-sheet inclined planar faces |
| planes.hexPocket240.point/normal/area | [-3.466, 3.0, -1.997] / [0.5006, 0.0, 0.8657] / 12.0 | pos 0.02; 0.5 deg; area 0.02 rel | stated | dimension-sheet inclined planar faces |
| planes.hexPocket300.point/normal/area | [-0.003, 3.0, -4.0] / [-0.4994, 0.0, 0.8664] / 12.0 | pos 0.02; 0.5 deg; area 0.02 rel | stated | dimension-sheet inclined planar faces |
| planes.hexBoss60.point/normal/area | [0.003, 3.0, 5.0] / [0.5005, 0.0, 0.8657] / 5.0 | pos 0.02; 0.5 deg; area 0.02 rel | stated | dimension-sheet inclined planar faces |
| planes.hexBoss120.point/normal/area | [-4.329, 3.0, 2.503] / [-0.4995, 0.0, 0.8663] / 5.0 | pos 0.02; 0.5 deg; area 0.02 rel | stated | dimension-sheet inclined planar faces |
| planes.hexBoss240.point/normal/area | [-0.003, 3.0, -5.0] / [-0.5005, 0.0, -0.8657] / 5.0 | pos 0.02; 0.5 deg; area 0.02 rel | stated | dimension-sheet inclined planar faces |
| planes.hexBoss300.point/normal/area | [4.329, 3.0, -2.503] / [0.4995, 0.0, -0.8663] / 5.0 | pos 0.02; 0.5 deg; area 0.02 rel | stated | dimension-sheet inclined planar faces |
| planes.toothFlankA.point/normal/area | [10.192, 0.0, -0.086] / [0.5061, 0.0, -0.8625] / 2.45 | pos 0.05; 1.0 deg; area 0.05 rel | stated | dimension-sheet inclined planar faces |
| planes.toothFlankB.point/normal/area | [-10.192, 0.0, 0.086] / [-0.5061, 0.0, 0.8625] / 2.45 | pos 0.05; 1.0 deg; area 0.05 rel | stated | dimension-sheet inclined planar faces |
| planes.toothFlankC.point/normal/area | [0.086, 0.0, 10.192] / [0.8625, 0.0, 0.5061] / 2.45 | pos 0.05; 1.0 deg; area 0.05 rel | stated | dimension-sheet inclined planar faces |
| planes.toothFlankD.point/normal/area | [-10.023, 0.0, 1.855] / [-0.3487, 0.0, 0.9372] / 2.45 | pos 0.05; 1.0 deg; area 0.05 rel | stated | dimension-sheet inclined planar faces |
| dimensions.spanX | 20.483 along x (bbox) | 0.05 mm | stated | Bbox extent along x (stated size). |
| dimensions.spanY | 4.0 along y between ('discBottom', 'hexBossTop') | 0.05 mm | stated | Bbox extent along y. |
| dimensions.spanZ | 20.483 along z (bbox) | 0.05 mm | stated | Bbox extent along z (stated size). |
| dimensions.discHeight | 3.0 along y between ('discBottom', 'discTop') | 0.02 mm | stated | Disc thickness. |
| dimensions.overallHeight | 4.0 along y between ('discBottom', 'hexBossTop') | 0.02 mm | stated | Circular face to hex-boss cap. |
| dimensions.hexPocketAcrossFlats | 6.926 along x between ('hexPocketLeft', 'hexPocketRight') | 0.02 mm | derived | Inner hex across-flats. |
| dimensions.hexBossAcrossFlats | 8.664 along x between ('hexBossLeft', 'hexBossRight') | 0.02 mm | derived | Outer hex across-flats. |
| solids.gear.contains_point | [6.0, 1.5, 0.0] | interior | derived witness | r=6, y=1.5, clear of hex and root |
| solids.gear.volume | 827.65 | 2.0 mm3 | stated | same as acceptance.volume |
| probes.discMaterial | solid [(6.0, 1.5, 0.0)] | clearance > wall tolerance | derived witness | Inside the disc rim, r=6, between hex vertex 4 and root 9.5. |
| probes.hubMaterial | solid [(3.9, 3.5, 0.0)] | clearance > wall tolerance | derived witness | Inside the hex-boss wall, between flats 3.463 and 4.332 at y=3.5. |
| probes.boreVoid | void [(0.0, 0.5, 0.0)] | clearance > wall tolerance | derived witness | On the bore axis, mid-floor. |
| probes.hexVoid | void [(0.0, 2.5, 0.0)] | clearance > wall tolerance | derived witness | On the axis inside the hex socket, above the floor. |
| probes.outsideVoid | void [(12.0, 1.5, 0.0)] | clearance > wall tolerance | derived witness | Outside the tip circle on +x. |
| cylinder_counts.boreCount | Ø3.1 hole expected 1 | radius 0.02 | stated | Single Ø3.1 floor bore. |
| cylinder_counts.rootCount | Ø19.0 pin expected 1 | radius 0.02 | stated | Single partial Ø19 dedendum cylinder. |
| cylinder_counts.tipFilletCount | Ø0.2 pin expected 36 | radius 0.02 | stated | One tip fillet per tooth. |
| gears.teeth | module 0.569, teeth 36, at y=2.0 | count exact; module inferred 0.05 | stated count; inferred module | Mid-disc tooth count. Module is the inferred counting aid, not a stated involute module. Phase: tip on +x. |
| blockout.volume_min | 969.221 | mm3 | derived | 0.92 * (π*(envelopeSizeX/2)^2*discThickness + (3√3/2)*hexBossVertex^2*hubHeight) |
| blockout.volume_max | 1137.781 | mm3 | derived | 1.08 * same envelope (disc cylinder + outer hex prism) |
| export_volume_tolerance_rel | 0.002 | rel | defaulted | schema KCL/STEP/STL agreement |
| deviation | null | n/a | source availability | no reference mesh in the bundle |

Blockout envelope is the unperforated disc cylinder of radius envelopeSizeX/2 and height discThickness, union the outer hex prism of vertex radius hexBossVertex and height hubHeight. That union reaches the finished bbox (teeth at the x/z extremes, boss at y=4). V_block = 1053.501 mm3. Band ±8%: 969.221 .. 1137.781 mm3. A bare disc without the hub would miss y=4.

## 6. Defaults retained

Length unit mm, angle unit deg, schema_version 1 and release_status reconstruction are retained. material, density_kg_m3 and process stay null. No seed plate geometry or seed volume from the template survives.

Digital comparison bands (not production fits): stated lengths generally 0.01 mm, cylinder diameters 0.02 mm, tip-fillet axes 0.05 mm (sheet rounding to 0.001 mm), hex vertices 0.02 mm, toothPhase 0.05 deg, integer toothCount 1e-6, inferred gearModule 0.05 mm, bbox 0.05 mm, face location 0.02 mm, section area 1–2%, volume 2 mm3, surface 5 mm2, COM 0.05 mm. export_volume_tolerance_rel 0.002 is the schema default. Blockout ±8% is a disclosed envelope band.

## 7. Unrepresentable or low-confidence features

- What tooth form is intended (involute spur, trapezoidal/sprocket, or another construction)? section-y2.png shows straight-looking flanks and rounded tips; no pressure angle, pitch diameter, addendum/dedendum factors or cutter is stated. gearModule 0.569 mm is only a tooth-count threshold.
- What are the 68 tooth-flank planes omitted from the dimension sheet as below the area threshold (4 listed at 2.45 mm2)? The 36 tip fillets and the y=2 section constrain the envelope, but individual omitted flanks are not named.
- The stated bbox size [20.483, 4.0, 20.483] is 0.001 mm short of max-min = [20.484, 4.0, 20.484] from the stated min/max ±10.242. Envelope uses the stated min/max; tipOuterRadius = 10.242 matches those bounds. Which rounding is authoritative?
- Is the Ø19 partial cylinder the true root/dedendum face, or a construction/envelope cylinder interrupted by the teeth? The sheet lists it as pin Ø19, length 3, full 360 = no.
- Does the Ø3.1 hole remain a 1 mm cylinder in the floor only, or should a modeller treat the hex socket plus bore as one through passage of mixed section? The sheet lists only the cylindrical 1 mm portion.
- What material, density and manufacturing process are intended? Unspecified; material, density_kg_m3 and process remain null. Volume and centre of mass are geometric (unit density), not a mass claim.
- How should evaluator-only surface deviation against the held-out reference CAD be reported? No reference mesh is in this bundle; acceptance.deviation is null.

Inclined-plane table x-offsets of ±0.003 mm on theoretically x=0 points are treated as extractor noise, not extra parameters. Sheet tip coordinates that print 3.468 vs 3.469 are stored verbatim. KCL, sanity asserts, exports and engine measurements remain for later stages.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-10.242, 0.0, -10.242] → [10.242, 4.0, 10.242] | 1053.5976036868838 | pass | 2026-09-19T06:09:08Z: within envelope and band |
