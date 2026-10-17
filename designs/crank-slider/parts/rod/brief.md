# crank-slider-rod — design brief

## 1. Intent and configuration

Connecting rod of the offset crank-slider mechanism (body `rod` of the assembly `crank-slider`), modelled in its own frame
as one solid. It is a 5 mm stadium plate, 16 mm wide, with R8 semicircular ends centred on two D6 through bores 100 mm
apart: bore A (revolute crank pin, joint `crankPin`, own-frame point [0, 0, 0], axis +z) at the origin and bore B
(revolute wrist pin, joint `wristPin`, own-frame point [100, 0, 0], axis +z) at x = 100. The bottom face z = 0 lies on the
crank's top face at A and on the slider's top face at B. The rod is the crank's plate with a 100 mm centre distance
instead of 30 mm. The authoritative source is `sources/crank-slider-spec.md` (text only, no drawings or reference model).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/crank-slider-spec.md | text | authoritative | cd01ebc4dc4d7289a786bef3bca834eb565dd9f6109941bbcc2ec04b879c0d1c | part table (Crank row for the plate section, Connecting rod row "A to wrist pin B: 100; stadium plate as the crank"), Frame, Part frames, Rest configuration and Joints paragraphs |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| centre distance A to B | 100 | mm | spec part table, Connecting rod row; intent | 0.01 | stated |
| plate thickness (z = 0..5) | 5 | mm | Crank row "5 thick", reused by the rod row; intent | 0.01 | stated |
| plate width (y = -8..8) | 16 | mm | Crank row "16 wide"; intent | 0.01 | stated |
| semicircular ends centred on the holes | R8 | mm | Crank row; intent | 0.01 | stated (derived = width / 2) |
| bores A and B, through along z | D6 | mm | Crank row "Ø6 holes"; intent "both D6 through along z" | 0.01 | stated |
| bore A axis | (0, 0) | mm | intent; spec Part frames (first hole at the own origin) | 0.05 | stated |
| bore B axis | (100, 0) | mm | intent; spec Part frames (second hole on +x at its length) | 0.05 | stated |
| overall x extent | -8..108 | mm | intent | 0.05 | stated |
| bottom face z = 0 on the crank top (A) and the slider top (B) | z = 0 | mm | intent Interfaces; spec Frame layers (rod z 5..10 on top of both) | 0.05 | stated |
| volume | 8722.57 | mm3 | intent (derived from the crank with a 100 mm centre distance) | 0.1 % | stated |
| one separate solid | 1 | | spec "Four separate solids (no fused bodies)" | exact | stated |
| material, density, process | none | | not stated | | open |
| bore fit or tolerance class | none | | not stated | | open |
| edge breaks | none | | not stated | | open |

## 4. Coordinate frame, scale, and measurement method

Origin: centre of bore A on the bottom face. +x runs along the rod centre line from bore A toward bore B (x = 100); +z
runs along the pin axes up through the thickness (bottom face z = 0, top face z = 5); +y completes a right-handed frame
(y = z cross x) across the width, and y = 0 is the mirror plane through both pin axes. Datums: A = bottom face z = 0;
B = bore A axis (x = 0, y = 0); C = bore B axis (x = 100, y = 0). This is the part frame the spec prescribes ("the crank
and the rod have their first hole at their own origin, their second hole on +x at their length, and their bottom face at
z = 0") and the frame the assembly places the rod by: at rest the assembly maps it to A = (30, 0, 5) rotated 5.739170 deg
about z. No images, drawings or meshes exist; every dimension is quoted from text, so there is no scale or rectification
step and no measured value.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| centreDistance | 100 mm | 0.01 | stated | Connecting rod row "A to wrist pin B: 100"; no edit test because the wrist-pin interface (bore B at x = 100) and the assembly loop depend on it |
| plateWidth | 16 mm | 0.01 | stated | Crank row "16 wide", reused by the rod row |
| plateThickness | 5 mm | 0.01 | stated | Crank row "5 thick"; Frame layers rod z 5..10 |
| holeDiameter | 6 mm | 0.01 | stated | Crank row "Ø6 holes"; intent "D6 through" |
| endRadius | 8 mm | 0.01 | derived | plateWidth / 2 (the spec also states R8, consistent); the model must compute it from plateWidth so the width edit keeps the ends tangent |
| envelope | [-8, -8, 0]..[108, 8, 5] | 0.05 | derived | x = -endRadius..centreDistance + endRadius, y = ±plateWidth / 2, z = 0..plateThickness |
| net plate area (midZ section, deck face) | 1744.513 mm2 | 0.2 % | derived | centreDistance * plateWidth + pi * endRadius^2 - 2 * pi * (holeDiameter / 2)^2 = 1600 + 64 pi - 18 pi = 1600 + 46 pi |
| volume | 8722.566 mm3 | 0.1 % | derived | plateThickness * net area = 5 * 1744.513; matches the intent's 8722.57 |
| surface area | 4928.849 mm2 | 0.5 % | derived | 2 * 1744.513 + plateThickness * (2 * centreDistance + 2 pi * endRadius) + 2 pi * holeDiameter * plateThickness = 3489.027 + 1251.327 + 188.496 |
| center of mass | (50, 0, 2.5) | 0.05 | derived | uniform plate symmetric about x = centreDistance / 2, y = 0, z = plateThickness / 2 |
| webX section (x = 50) | 80 mm2, 1 loop, 0 holes | 0.2 % | derived | plateWidth * plateThickness |
| throughA / throughB sections (x = 1, x = 99) | 51.716 mm2, 2 loops, 0 holes | 0.2 % | derived | 2 * plateThickness * (plateWidth / 2 - sqrt((holeDiameter / 2)^2 - 1)) = 10 * (8 - 2 sqrt 2); planes 1 mm off the bore axes so they cut no cylinder seam and no flank-to-arc tangent edge |
| lengthX / widthY / thicknessZ | 116 / 16 / 5 mm | 0.05 | derived / stated / stated | centreDistance + 2 * endRadius; plateWidth; plateThickness between floor and deck |
| cylinders holeA, holeB | D6 at (0, 0) and (100, 0), axis z, concave | radius 0.02, axis 0.05 | stated | no length given, so the thickness edit leaves the pinned bores unchanged; through-ness is checked by the inBores probes, the deck area and the volume |
| cylinders endA, endB | R8 at (0, 0) and (100, 0), axis z, convex | radius 0.02 | stated | the semicircular ends are concentric with the bores |
| probes | see contract | | derived | solid: web centre (50, 0, 2.5) and 5.5 mm from each bore axis (2.5 mm from each wall); void: bore axes at z = 1.25 and 3.75 (1.25 mm from both faces, 3 mm from the bore wall); bbox corners (-6.8, ±6.8) and (106.8, ±6.8) at z = 2.5, 1.6 mm outside the R8 arcs and 1.2 mm inside the bbox faces |
| blockout band | 8700..9300 mm3 | | derived | stadium blank without bores 5 * (1600 + 64 pi) = 9005.310 ± 3 %; also admits the finished part (8722.57) and a square-ended 116 x 16 x 5 box (9280) |
| edit test plateWidth +2 | ΔV = +1267.035 mm3, bbox Δ [2, 2, 0] | 2 % | derived | endRadius follows to 9: ΔV = plateThickness * (centreDistance * 2 + pi * (9^2 - 8^2)) = 5 * (200 + 17 pi); sweep 12, 16, 20 inside the feasible interval plateWidth > holeDiameter (6 mm, below it the bores break through the flanks); infeasible delta -12 (4 mm wide) must fail an assert |
| edit test plateThickness +1 | ΔV = +1744.513 mm3, bbox Δ [0, 0, 1] | 2 % | derived | ΔV = net area * 1; sweep 3, 5, 8 inside the feasible interval plateThickness > 0; infeasible delta -5 (zero thickness) must fail an assert |
| interfaces crankPin, wristPin | holeA / holeB, floor, mirrorY | | stated | pinned items carry no size the edits change: the floor face has no area (the width edit resizes it) and the bores no length (the thickness edit lengthens them) |

## 6. Defaults retained

- Envelope tolerance 0.05 mm and parameter tolerances 0.01 mm (template defaults): the geometry is exact, text-stated and digital, so a tight comparison threshold is appropriate.
- `release_status: reconstruction` (template default).
- `material`, `density_kg_m3` and `process` stay null: the spec states none, so no mass claim is made.
- Symmetry band `max_deviation` 0.1 mm and `p95_deviation` 0.05 mm (the exemplar defaults; no source states a tighter band).
- Sharp edges everywhere: no edge break is stated.

## 7. Unrepresentable or low-confidence features

- The pins and the revolute joints themselves belong to the assembly contract; this part carries only the bores (axes, diameter) and the bearing face z = 0 that locate them.
- The centre distance has no edit test: moving bore B would break the pinned wrist-pin interface and the assembly loop closure (|AB| = 100).
- No feature is low-confidence: every dimension is stated. Only the bore fit, edge breaks and material are open (see the contract's `open_questions`).

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
