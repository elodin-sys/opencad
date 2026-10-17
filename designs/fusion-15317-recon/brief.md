# fusion-15317-recon — design brief

## 1. Intent and configuration

Reconstruct Fusion Gallery body `22337_e2f65ed2_0003_1` (joint set `joint_set_15317`) as editable, parameterized KCL in the part's own native frame. The solid is a Ø88.9 mm flange disk (y = 106.298 .. 125.348) with a through U-slot and two stepped X-axis arm bores, sitting on a Ø50.8 mm hub (y = 92.804 .. 106.298) that has a revolved concave waist. One solid; export STEP and STL. The pipeline is frozen and the reference CAD is evaluator-only: do not import it, and do not tune the contract after the run.

Authoritative sources are `sources/part-brief.md` (intent and frame) and `sources/dimension-sheet.md` (envelope, planar faces, cylinders, sections, mass properties). Orthographic and isometric PNGs plus the three section drawings confirm feature counts and supply the hub-waist polyline that the sheet does not dimension.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/part-brief.md | text | authoritative | fea46397ecd044590030f38633e3e60c28abea496e851cbc4baa47889d535a69 | Native-frame bbox and reconstruction rules |
| sources/dimension-sheet.md | table | authoritative | 055b0252cd087bedcd08c49afaaa4f9ef6fd05ba7f0d3834e70d8b336417e9ef | Envelope, 12 planar faces, 8 cylinders, 3 sections, mass properties |
| sources/render-notes.md | text | illustrative | 46cf083458c3f2a1ac64c26c809f10ab559471b94192782a9291f9dfa1da8ff6 | Render list; 9590-triangle extents |
| sources/front.png | image | illustrative | 851b92e727e9151808661f83ccb064bf2f58d2db633f6f80d85c68a1be22a6d5 | +Y ortho; concentric Ø88.9 / Ø50.8 |
| sources/top.png | image | illustrative | 3ebe6a6196abf14994269b4f6601334eb288c4a70d7bac339644d70eca04ddbc | +Z ortho; U-slot, bore breakouts, rim hole |
| sources/right.png | image | illustrative | 97c7ca216278f6f537f33bf4dbdfb995a2f58a3f26aeeba72086db3daa846c4e | +X ortho; two bore circles and hub waist |
| sources/iso.png | image | illustrative | 90103a8151088b33e7c6537ba1bdaba890f61b929c5699bc3e4e16c6d255617b | Hub-side iso |
| sources/iso2.png | image | illustrative | 901ea7a39121072db27b185b6d2d2da6daceae1785d4c85e207703b4e5a5ae46 | Slot-side iso |
| sources/iso-below.png | image | illustrative | 85f3d7eddfaa93a6ef089e4a4a55db753289472b8ef7212850061cc365274503 | Underside iso |
| sources/section-x0.png | drawing | illustrative | 1de58db74d5b158a3a307c7bb60b4222ebb8a77ed6de9198d106294f94223b9e | x = 0 material outline |
| sources/section-y109.076.png | drawing | illustrative | bd136eaae5c4e3b66eab7c7d466fc945dc9fc84173bea851848d008b67af7e8a | y = 109.076 material outline |
| sources/section-z0.png | drawing | illustrative | 16661511e33e3572ab42ccffec13991ffc2ed70a5435c6f83cdecac84e928351 | z = 0 material outline; waist polyline |

The nine PNGs under `truth/cases/fusion-15317-recon/inputs/renders/` are byte-identical to the staging copies (same sha256).

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| envelope min | [-44.45, 92.804, -44.45] | mm | sources/dimension-sheet.md; sources/part-brief.md | 0.05 | stated |
| envelope size | [88.9, 32.544, 88.9] | mm | sources/dimension-sheet.md | 0.05 | stated |
| solid count | 1 | | sources/dimension-sheet.md; intent | 0 | stated |
| volume | 93854.25 | mm3 | sources/dimension-sheet.md | 0.002 rel | stated |
| surface area | 23161.97 | mm2 | sources/dimension-sheet.md | 0.01 rel | stated |
| centre of mass | [0.004, 110.098, -0.001] | mm | sources/dimension-sheet.md | 0.1 | stated |
| planar face levels | 12 faces at the sheet's (normal, level) rows | mm | sources/dimension-sheet.md | 0.05 / 1% area | stated |
| cylinders | hole Ø11.113×2, Ø7.938×2, Ø2.261×2; pin Ø88.9, Ø50.8 | mm | sources/dimension-sheet.md | 0.05 | stated |
| section x = 0 | area 1201.08, 1 loop, 0 holes | mm2 | sources/dimension-sheet.md | 0.01 rel | stated |
| section y = 109.076 | area 6171.07, 1 loop, 0 holes | mm2 | sources/dimension-sheet.md | 0.01 rel | stated |
| section z = 0 | area 1826.08, 1 loop, 0 holes | mm2 | sources/dimension-sheet.md | 0.01 rel | stated |
| export | STEP and STL | | sources/part-brief.md | | stated |
| hub waist profile | revolve of section-z0 silhouette | mm | sources/section-z0.png | 0.4 | measured / open |
| material / process | unspecified | | | | open |

## 4. Coordinate frame, scale, and measurement method

Origin is the native reference-model origin: the Y axis of the hub and flange, at y = 0, which is 92.804 mm below the hub bottom. Do not move the bbox minimum to the origin. +Y runs from the hub toward the slotted arm tops. +X points at the +X arm (slot walls at x = ±19.844). +Z completes the right-handed disk plane; front.png plots x horizontal and z vertical.

The dimension sheet is already in this frame. Image measurements used the millimetre grid printed on every PNG and were locked to sheet-stated corners before any unknown was read:

- On `section-z0.png` (1600×725), the black outline of the flange OD sits at plot x = ±44.45 and the slot walls at x = ±19.844, giving 12.72 px/mm in x. The slot-floor stroke is at y = 112.648 and the flange-bottom stroke at y = 106.298, giving 12.76 px/mm in y (the matplotlib axes are not square). Pixel-to-mm conversion used centre x = 847.5 px and slot-floor row = 309 px.
- Hub-waist (r, y) samples are those outline pixels after the plot box and axis strokes are ignored. The neck is r = 21.1 mm at y = 102.2; the profile meets the hub OD again at y = 94.5. Line-width and grid-alignment uncertainty is ±0.4 mm (about 5 px).
- Feature counts were read from the renders, not inferred: two arm-bore circles in right.png and on the slot walls in iso2.png; two rim-hole notches in section-y109.076.png and a single visible rim hole in top.png / iso.png / iso-below.png; U-slot in top.png, iso2.png and section-z0.png; hub waist in right.png, iso.png, iso-below.png, section-z0.png and section-x0.png.

Several sheet values are inch conversions (Ø88.9 = 3.5 in, Ø50.8 = 2 in, 19.05 = 0.75 in, 12.7 = 0.5 in, 11.113 = 7/16 in, 7.938 = 5/16 in). The contract keeps the millimetre figures the sheet prints.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| flangeDia | 88.9 mm | 0.02 | stated | sources/dimension-sheet.md pin Ø88.9; bbox x and z |
| hubDia | 50.8 mm | 0.02 | stated | sources/dimension-sheet.md pin Ø50.8 |
| hubYMin | 92.804 mm | 0.02 | stated | sources/dimension-sheet.md bbox min y / face y = 92.804 |
| flangeYMin | 106.298 mm | 0.02 | stated | sources/dimension-sheet.md face y = 106.298; pin extent |
| flangeYMax | 125.348 mm | 0.02 | stated | sources/dimension-sheet.md bbox max y / face y = 125.348 |
| slotY | 112.648 mm | 0.02 | stated | sources/dimension-sheet.md face y = 112.648 |
| slotHalf | 19.844 mm | 0.02 | stated | sources/dimension-sheet.md faces x = ±19.844 |
| grooveY | 103.917 mm | 0.02 | stated | sources/dimension-sheet.md face y = 103.917 |
| grooveFaceArea | 414.95 mm2 | 0.5 | stated | sources/dimension-sheet.md area of that face |
| holeMajorDia | 11.113 mm | 0.02 | stated | sources/dimension-sheet.md hole Ø11.113 |
| holeMinorDia | 7.938 mm | 0.02 | stated | sources/dimension-sheet.md hole Ø7.938 |
| holeY | 118.204 mm | 0.05 | stated | sources/dimension-sheet.md −Z major and both minor axes |
| holeZ | 19.05 mm | 0.05 | stated | sources/dimension-sheet.md |
| holeMajorPosY | 118.139 mm | 0.05 | stated | sources/dimension-sheet.md +Z Ø11.113 axis |
| holeMajorPosZ | 18.923 mm | 0.05 | stated | sources/dimension-sheet.md +Z Ø11.113 axis |
| rimHoleDia | 2.261 mm | 0.02 | stated | sources/dimension-sheet.md hole Ø2.261 |
| rimHoleY | 109.594 mm | 0.05 | stated | sources/dimension-sheet.md |
| rimHoleX | −5.077 mm | 0.05 | stated | sources/dimension-sheet.md; both holes |
| rimHoleZ | 39.746 mm | 0.05 | stated | sources/dimension-sheet.md \|z\| of centres of extent |
| rimHoleLen | 8.763 mm | 0.05 | stated | sources/dimension-sheet.md |
| xFace | 36.512 mm | 0.02 | stated | sources/dimension-sheet.md faces x = ±36.512 |
| hubNeckRadius | 21.1 mm | 0.4 | measured | sources/section-z0.png outline; min \|x\| ≈ 21.11 at y ≈ 102.2 |
| hubNeckY | 102.2 mm | 0.4 | measured | sources/section-z0.png |
| hubWaistY | 94.5 mm | 0.5 | measured | sources/section-z0.png; profile returns to r = 25.4 |
| flangeRadius | 44.45 mm | 0.02 | derived | flangeDia / 2 |
| hubRadius | 25.4 mm | 0.02 | derived | hubDia / 2 |
| flangeThick | 19.05 mm | 0.02 | derived | flangeYMax − flangeYMin |
| hubLen | 13.494 mm | 0.02 | derived | flangeYMin − hubYMin |
| slotDepth | 12.7 mm | 0.02 | derived | flangeYMax − slotY |
| slotWidth | 39.688 mm | 0.02 | derived | 2 * slotHalf |
| overallY | 32.544 mm | 0.02 | derived | flangeYMax − hubYMin |
| grooveInnerRadius | 22.651 mm | 0.05 | derived | sqrt(hubRadius² − grooveFaceArea / π) |
| volume | 93854.25 mm3 | 0.002 rel | stated | sources/dimension-sheet.md |
| surface area | 23161.97 mm2 | 0.01 rel | stated | sources/dimension-sheet.md |
| COM | [0.004, 110.098, −0.001] | 0.1 | stated | sources/dimension-sheet.md |
| secX0 area | 1201.08 | 0.01 rel | stated | sources/dimension-sheet.md |
| secYWeb area | 6171.07 | 0.01 rel | stated | sources/dimension-sheet.md |
| secZ0 area | 1826.08 | 0.01 rel | stated | sources/dimension-sheet.md |
| blockout volume | 145597 mm3 | 138000–153000 | derived | π·44.45²·19.05 + π·25.4²·13.494 (envelope cylinders only) |

Edit-test volume formulas (other parameters held fixed):

- `flangeYMax += 2`: ΔV = (arm-top area sum 2799.88) × 2 = 5599.76; bbox Δ = [0, 2, 0].
- `hubYMin += −2`: ΔV = (hub-bottom area 2026.83) × 2 = 4053.66, adding a full-Ø50.8 cylinder on the −Y end; bbox Δ = [0, 2, 0].
- `slotY += −1`: ΔV = −(slot-floor area 3407.28) × 1 = −3407.28; bbox unchanged.
- Infeasible: `hubYMin + 14` makes hub length negative (`assert hubYMin < flangeYMin`); `slotY − 7` drives the floor through the flange underside (`assert slotY > flangeYMin`).

Face-area checks used to identify the solids: hub-bottom 2026.83 = π·25.4²; flange-bottom 4180.34 = π·44.45² − π·25.4²; arm tops 2 × 1399.94 = π·44.45² − 3407.28; slot floor 3407.28 is the \|x\| ≤ 19.844 strip of the Ø88.9 disk.

## 6. Defaults retained

- `material`, `density_kg_m3` and `process` stay null: no alloy or manufacturing route is stated.
- `units` remain mm and deg, matching the sheet and the part-brief.
- `release_status` remains `reconstruction`.
- `acceptance.deviation` stays null: the bundle has no `reference/` ingest (held-out).
- Envelope digital tolerance 0.05 mm is the reconstruction comparison band, wider than the sheet's 0.001 mm printout.
- Face `area_tolerance_rel` is 0.01 except the four 25.73 mm² bore-shoulder faces (0.05), which are small and possibly clipped.
- Cylinder `radius_tolerance` 0.05 mm is the inspector default.

## 7. Unrepresentable or low-confidence features

- The hub waist is a smooth revolve with one planar shoulder. It is not a listed cylinder (no Ø42.2 pin) and is not a single-radius fillet. KCL should revolve the section-z0 / section-x0 profile rather than invent an R-value.
- The axial step between Ø11.113 and Ø7.938 is not drawn. The four x = ±36.512 faces are the only planar evidence of a shoulder; whether a chamfer sits between 35.718 and 36.512 is unknown.
- The +Z major-bore axis is 0.14 mm from the +Z minor-bore axis. Both cylinders are declared; do not force them onto one line without an assert that the model can still pass the inspector's 0.05 mm default axis band.
- Rim-hole clocking (both at x = −5.077) is real in the sheet and matches COM x = 0.004, but no angular callout exists.
- Cosmetic shading bands on the hub in iso.png are the waist, not a second groove or a thread.
- 25 of the 37 reference faces are non-planar (cylinders, waist torus, bore intersections). They are scored as cylinders or left to the waist revolve, not as named planes.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-44.45, 92.804, -44.45] → [44.45, 125.348, 44.45] | 145596.56698265628 | pass | 2026-09-19T06:08:56Z: within envelope and band |
