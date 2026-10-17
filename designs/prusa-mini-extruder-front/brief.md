# prusa-mini-extruder-front — design brief

## 1. Intent and configuration

Reconstruct the Original Prusa MINI extruder front housing (MINI-extruder-front) as editable, parameterized KCL from the attached renders, section drawings and dimension sheet. Frame: x across the plate (-26.5 to 26.5), y through the thickness with the back mating face at y = 0 and the front face at y = 14, z vertical from the bottom face z = -30 to the top lug at z = 33.72. Assembly-governing geometry must be exact: the keyhole central opening (Ø22.5 x 3 recess, Ø16 bore, Ø26 x 6 counterbore on the axis x = -2, z = 0; Ø12 x 3 recess, Ø16 bore and Ø14 counterbore on x = -2, z = 16.4), every Ø3.4 through hole with its Ø6.5 / Ø3.5 counterbore or heat-set trap, the Ø4 filament holes, the hotend clamp channel bores along z at x ~ 25.6, and the mating planes (y = 0, y = 14, z = -30, x = -26.5). Declare each hole as an acceptance cylinder and the mating planes as interfaces with checks. The fan-duct lobe, top-lug fillet and embossed text are cosmetic (optional features). One solid; export STEP and STL. The reference CAD is evaluator-only; the deliverable must be construction, never an import.

This is a reconstruction draft, not a modeled or manufactured part. Future output is editable KCL 2 construction, one solid, deterministic STEP and STL. Do not import evaluator-only CAD or a reference mesh. This task produces only the contract and brief.

The user's datum frame and functional scope govern. The detailed dimension table, corroborated by section drawings, supplies the provisional numerical geometry where the prose contradicts it. Orthographic pixels supply only dimensions otherwise unlisted. Isometrics explain form. Q1 keeps the keyhole conflict visible; incompatible hole stacks must not be combined.

Table-supported lower axis x=-2,z=0: Ø22.5 over y=0..3; taper to Ø14 at y=10.361; Ø14 over y=10.361..14. Upper axis x=-2,z=16.4: Ø12 over y=0..3, Ø16 over y=3..8, Ø26 over y=8..14. The table has one Ø16 cylindrical surface. A taper passing through diameter 16 is not another Ø16 cylindrical bore.

## 2. Sources

All 20 supplied files are registered with full SHA-256. No reference/ directory or ingest outputs were supplied. No evaluator-only geometry or scoring data was read. Numbers quoted from dimension-sheet.md have stated provenance, although its author measured reference CAD; measured (reference model) is reserved for actual ingest outputs. Every file has mm units and an unspecified upstream revision.

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/back.png | drawing | authoritative | 0082b3fc7dba786305b2403e8d454471030bf13072317f94c55cd314add6fc85 | Plots -x horizontally; shows the y=14 counterbore side. |
| sources/bottom.png | drawing | authoritative | ffcb4f042cf21f1af12962ce8e25164d444a06b3949523f7b80853c5112764d8 | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/dimension-sheet.md | table | authoritative | 8114a967a9bfa8f1b8cb70e979bda39f2e6a02b28eee8c3c2a906a5389d6e93c | Detailed coordinates, surfaces and sections; numbers are stated document values, not agent reference-ingest measurements. |
| sources/front.png | drawing | authoritative | 5eb8d869e83a8b6fda807d1a89c6a2340416e9fcc6ba7e9156e5ad9090891415 | Plots +x horizontally; shows the y=0 pocket and marking side. |
| sources/iso-below.png | image | illustrative | a88b88b12b762c2f233eb945e824d56e66618b4595732be098034a98fea0f4e7 | Spatial interpretation only; no metric measurements from isometric projection. |
| sources/iso.png | image | illustrative | b020791e7cac6906a7849143eacd5a451367a29067b7005ef9ba6031fb40490b | Spatial interpretation only; no metric measurements from isometric projection. |
| sources/iso2.png | image | illustrative | 71fc8bd6986eeaaaa6ca80f0bc33b3263ab695c169a03c11adc27834e2366dfe | Spatial interpretation only; no metric measurements from isometric projection. |
| sources/left.png | drawing | authoritative | 0e619ab6438f959e407e5c85024d515dcf7893d28a4f4442300eaaf2ec8ec392 | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/prusa-extruder-front-description.md | text | authoritative | 68bb9d8de0d472b48ee4d006368d8317942fb1662c46fa57ca40444a3270e3fc | Functional scope and frame; conflicting keyhole axis assignments retained as Q1. |
| sources/render-notes.md | text | authoritative | d55bcc4dd15907bcbd350f4f13f8203ae1108e811702c8146c8dc571529e1728 | Orthographic mm-grid convention, mesh-render metadata and envelope. |
| sources/right.png | drawing | authoritative | 058b38e8a33e018052f9ecce5dad1dc4ac49d7f09475300dd7760bb47516e15c | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/section-x-18.5.png | drawing | authoritative | 631dc2ecc85bb8d7ecf1ae2592d716be3f79226a496944f9649ad8422b637881 | Table/drawing topology conflict Q3. |
| sources/section-x0.png | drawing | authoritative | 5948745dc3a39d6be9f315b77bff89c305a1ed817e0db31efa3a9b66e811dba8 | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/section-y1.5.png | drawing | authoritative | 35f64ab977673fb8c50df3c20af3c5bff32470d319d67c36e77518ef06675a51 | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/section-y12.png | drawing | authoritative | 2adcdb2843aec7741582b66c0e07c3a6a955b5ea989eb2a9ec0a9c94e3004a83 | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/section-y7.png | drawing | authoritative | 010bf57ad6582553c9cf903435bc324dd6629f191dd1ab16d90c258a4cca497d | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/section-z-20.png | drawing | authoritative | 4525f85f7d8aad2c964b1d88a2abe5ed4e5086bdff8103449b6e88ac4c28ab8b | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/section-z0.png | drawing | authoritative | 21d566609ed38ef40a873d62e8b99c37fb9ab24a897ebb55fc724db4aef8094a | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/section-z17.png | drawing | authoritative | 09015d9730b123e12ab2950371d63cd2cdcf87d9b8ff6fb5ea037df1333d5016 | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |
| sources/top.png | drawing | authoritative | 723eafa804a379697e33524c77c45951f601d3515f889ef73cd459437721c335 | Orthographic mm grid/material outline; pixel readings carry wider tolerance than tabulated coordinates. |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Envelope | [-26.5,0,-30] to [26.5,14,33.72] | mm | user frame; description; render notes | .03 per limit | required; nominal y=14 |
| Solid count | 1 | count | sources/dimension-sheet.md | exact | required |
| Cylindrical surfaces | 33 concave + 7 convex = 40 | count | sources/dimension-sheet.md cylinder table | axis .03; radius .025; length .05 mm | required; partial and angled included |
| Keyhole stacks | lower Ø22.5/taper/Ø14; upper Ø12/Ø16/Ø26 | mm | table and sections | per cylinder/plane | provisional Q1 |
| Screw pattern | (-23.92,0),(-22,15),(-18.5,22),(-17,-20),(8,28),(12,-17),(19.92,0),(20,17) | x,z mm | sources/dimension-sheet.md | axis .03 mm | 8 axes: 6 Ø3.4,2 Ø3.5 pilots |
| Counterbores / traps | 5 Ø6.5 recesses,3 point-up hex traps, support steps | mm | sources/dimension-sheet.md | per acceptance item | required |
| Filament | 2 Ø4 passages; +y and [0.9538,0.3003,0] axes | mm | sources/dimension-sheet.md cylinder rows 24–25 | per cylinder | required |
| Half-clamp | individual axial, tilted and 45° bores/lips | mm | sources/dimension-sheet.md and right/top/section images | per surface | required |
| Datums | A y=0; B y=14; C z=-30; D x=-26.5; named +x patches | mm | sources/dimension-sheet.md face table | .03 for principal datums | required, with interface checks |
| Mid-plate | 2186.59; 1 outer loop; 11 holes | mm2 / count | sources/dimension-sheet.md y=7 section | 1% area; topology exact | required |
| Optional styling | fan-lobe blend, lug fillet, R1, arrow | — | sources/prusa-extruder-front-description.md | retain envelope and functional geometry | optional |
| Exports | constructed KCL 2; STEP and STL | — | user intent | .002 relative volume agreement | future model stage |
| Diagnostics | V = 29833.56; S = 11557.87; C = [-.703,6.989,-2.703] | mm3 / mm2 / mm | sources/dimension-sheet.md mass table | nonbinding | not analytic predictions |
| Material / density | unknown | — | not supplied | not applicable | open Q7 |

Digital comparison tolerances do not specify print accuracy, press fits or hardware clearances.

## 4. Coordinate frame, scale, and measurement method

The point [0,0,0] is on the y=0 mating plane, halfway between the x envelope limits and 30 mm above the z=-30 bottom plane. It lies in the central opening, not necessarily in material. The lower opening axis meets y=0 at [-2,0,0].

+x points toward the half-clamp; +y from y=0 to 14; +z upward. Datums A–D are the contract planes. In-plane face centroids use (y,z) for x faces, (x,z) for y faces and (x,y) for z faces. Cylinder t ranges start at the listed axis point, not the extent center, and use a normalized direction.

Pixel coordinates are zero-based (u right,v down) on original PNG files, not resized chat images. Orthographic mm grids establish scale without perspective correction. Anti-aliased edges/line widths contribute 2–4 pixels; measured parameters use .15–.25 mm tolerances.

| image evidence | original pixels read | scale / interpretation | uncertainty / use |
|---|---|---|---|
| front.png / back.png | 1800×2118; grid x columns 188,316,443,…,954,…,1720; z rows 192,319,…,1085,…,1851; colored bbox 277..1630,224..1850 | Origin≈(954,1085); 1532 px/60 mm=25.53 px/mm. Back horizontal axis is -x. | Table fixes nominal envelope; raster width 1354/25.53≈53.03 mm. |
| Front silhouette | Peak pixels v224,u1378..1382; knee≈(337,1650); foot≈(393,1712) | Peak x≈16.75; knee≈(-24.15,-22.13); foot top z≈-24.55. | ±.20–.25 mm; exact plane intersections take precedence. |
| top.png / bottom.png | 1800×617; top colored bbox 319..1588,112..447; bottom y pixels 156..491 | 1270 px/53 mm≈23.96 px/mm; 336 px/14 mm=24 px/mm. | Thickness and open side groove; approximately ±.15 mm. |
| section-z0.png | 1800×658; x0 at u954,y0 at v490; 24 px/mm. Lower opening bounds at y0:636,1176; y14:738,1074 | Widths 22.5 and 14 mm. Ramp starts v418 (y3), ends near 241 (y10.375). | Table taper endpoint 10.361 takes precedence; disproves prose lower Ø26 placement. |
| section-z0 pivot mouth | At y8.5,v≈286, right-pilot edges u≈1385 and 1479 | 94/24≈3.92 mm → pivotMouthDiameter = 3.9. | ±.15 mm; shoulder area 21.24 independently yields sqrt(6.5²−4×21.24/π)≈3.8995. |
| section-z17.png | 1800×658; 24 px/mm; upper opening bounds y0≈762,1049; y3..8≈714,1097; y8..14≈594,1217 | Chords≈11.97,15.96,25.96 mm at z17, .6 mm above axis z16.4. | Confirms upper Ø12/Ø16/Ø26; dimensions use table. |
| section-y1.5 / y7 / y12 | 1800×2085/2207/2104; x0 columns 954/997/961; 5-mm pitch 117/124/118 px | 23.4/24.78/23.62 px/mm. Counted outer/holes:1/9,1/11,1/7. | Three hex traps at y1.5; two straight plus one diagonal retaining slot at y7. |
| section-x0 / x-18.5 | 1800×5202; y0 column 510; 5-mm pitch 317 px; z0 row 2486 | 63.4 px/mm; exposes shoulders 3,8, taper and printable support steps. | x−18.5 title 2 regions conflicts with table 3; Q3. |
| section-z-20.png | 1800×658; 24 px/mm; upper material walls u318..504 and 587..1590; left screw split u468/623 at y0 | Two outer material regions, one inner clamp-slot loop. | Table 584.60 versus mesh label 584.66 mm2. |
| left/right and iso/iso2/iso-below | Side views show channel, lug/web, axial slots and diagonal slot; isometrics show both pocket stacks | Eight screw axes, one connected keyhole, three hex pockets and five counterbores identified across views. | Isometrics used only for spatial interpretation; no guessed blend radii. |

Section-image labels (mm2) versus table: y1.5 2204.22/2203.29; y7 2188.15/2186.59; y12 2149.22/2148.31; x0 333.47/333.46; x−18.5 662.94/662.84; z0 336.78/336.53; z17 355.76/355.45; z−20 584.66/584.60. Area differences are below 0.1%; the 1% band covers them. Integer topology cannot be reconciled by an area tolerance.

## 5. Measurement and inference record

Every parameter is a future top-level KCL constant. Derived formulas explain dependencies; nominal literals may be needed by the model harness. Do not add equality locks between parameters. Direction cosines are unitless and normalized for construction.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| plateWidth | 53 mm | 0.02 | stated | sources/prusa-extruder-front-description.md; '53 x 14 x 63.72 mm'; Overall x span. |
| plateThickness | 14 mm | 0.02 | stated | sources/prusa-extruder-front-description.md; 'front face at y = 14'; Nominal separation of y=0 and y=14; do not replace with bbox artifact 14.001. |
| bottomZ | -30 mm | 0.02 | stated | sources/prusa-extruder-front-description.md; 'flat bottom face at z = -30'; Bottom datum. |
| lugMaxZ | 33.72 mm | 0.02 | stated | sources/prusa-extruder-front-description.md; 'z vertical (-30 .. +33.72)'; Highest rear web/lug point; the Ø10 lug alone reaches z=33. |
| bodyTopZ | 28 mm | 0.02 | stated | sources/dimension-sheet.md; planar +z faces at z=28; Main top ledge. |
| leftTopChamferZ | 24 mm | 0.02 | stated | sources/dimension-sheet.md; inclined point [-26.5,0,24]; Upper left bevel starts here. |
| rightTopChamferX | 22.5 mm | 0.02 | stated | sources/dimension-sheet.md; inclined point [22.5,0,28]; Upper right bevel starts here. |
| leftFootX | -21.95 mm | 0.02 | stated | sources/dimension-sheet.md; -x planar face at x=-21.95; Lower left vertical foot. |
| leftShoulderZ | -21.925 mm | 0.02 | stated | sources/dimension-sheet.md; inclined point [-26.5,0,-21.925]; Lower left shallow bevel anchor. |
| leftDiagonalAnchorX | -22.946 mm | 0.02 | stated | sources/dimension-sheet.md; inclined point [-22.946,0,-23.45]; Lower left diagonal plane anchor x. |
| leftDiagonalAnchorZ | -23.45 mm | 0.02 | stated | sources/dimension-sheet.md; inclined point [-22.946,0,-23.45]; Lower left diagonal plane anchor z. |
| rightBottomChamferZ | -22.75 mm | 0.02 | stated | sources/dimension-sheet.md; inclined point [26.5,0,-22.75]; Lower right bevel anchor at x=26.5. |
| halfWidth | 26.5 mm | 0.02 | derived | plateWidth / 2; Overall half width. |
| overallHeight | 63.72 mm | 0.02 | derived | lugMaxZ - bottomZ; Overall height. |
| leftKneeX | -24.15 mm | 0.2 | measured | sources/front.png; original pixel (337,1650); origin (954,1085), scale 25.53 px/mm; Raster lower left bevel-junction x. Exact table planes take precedence over raster intersections. |
| leftKneeZ | -22.13 mm | 0.2 | measured | sources/front.png; original pixel (337,1650); origin (954,1085), scale 25.53 px/mm; Raster lower left bevel-junction z. Exact table planes take precedence over raster intersections. |
| leftFootTopZ | -24.55 mm | 0.2 | measured | sources/front.png; original pixel (393,1712); origin (954,1085), scale 25.53 px/mm; Raster top of the lower left vertical foot. Exact table planes take precedence over raster intersections. |
| lugWebPeakX | 16.75 mm | 0.25 | measured | sources/front.png; original pixel u=1378..1382,v=224; origin (954,1085), scale 25.53 px/mm; Raster x of the highest web point. Exact table planes take precedence over raster intersections. |
| keyUpperCounterboreDiameter | 26 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 1, hole Ø26, axis point [-2.0, 0.0, 16.4], extent [8.0, 14.0]; Diameter for keyUpperFrontCounterbore. |
| keyAxisX | -2 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 1, hole Ø26, axis point [-2.0, 0.0, 16.4], extent [8.0, 14.0]; Axis x coordinate for keyUpperFrontCounterbore. |
| keyUpperZ | 16.4 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 1, hole Ø26, axis point [-2.0, 0.0, 16.4], extent [8.0, 14.0]; Axis z coordinate for keyUpperFrontCounterbore. |
| keyMiddleEnd | 8 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 1, hole Ø26, axis point [-2.0, 0.0, 16.4], extent [8.0, 14.0]; Signed start extent for keyUpperFrontCounterbore, from the stated axis point. |
| keyLowerRecessDiameter | 22.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 2, hole Ø22.5, axis point [-2.0, 0.0, 0.0], extent [0.0, 3.0]; Diameter for keyLowerBackRecess. |
| keyBackDepth | 3 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 2, hole Ø22.5, axis point [-2.0, 0.0, 0.0], extent [0.0, 3.0]; Signed end extent for keyLowerBackRecess, from the stated axis point. |
| keyUpperBoreDiameter | 16 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 3, hole Ø16, axis point [-2.0, 0.0, 16.4], extent [3.0, 8.0]; Diameter for keyUpperMiddleBore. |
| keyLowerExitDiameter | 14 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 4, hole Ø14, axis point [-2.0, 0.0, 0.0], extent [10.361, 14.0]; Diameter for keyLowerFrontCounterbore. |
| keyLowerExitStart | 10.361 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 4, hole Ø14, axis point [-2.0, 0.0, 0.0], extent [10.361, 14.0]; Signed start extent for keyLowerFrontCounterbore, from the stated axis point. |
| clampCornerOuterDiameter | 12.684 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 5, hole Ø12.684, axis point [22.922, 7.0, -22.922], extent [-3.975, -0.975]; Diameter for clampCornerOuterCut. |
| clampCornerAxisX | 22.922 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 5, hole Ø12.684, axis point [22.922, 7.0, -22.922], extent [-3.975, -0.975]; Axis x coordinate for clampCornerOuterCut. |
| clampCenterY | 7 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 5, hole Ø12.684, axis point [22.922, 7.0, -22.922], extent [-3.975, -0.975]; Axis y coordinate for clampCornerOuterCut. |
| clampCornerAxisZ | -22.922 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 5, hole Ø12.684, axis point [22.922, 7.0, -22.922], extent [-3.975, -0.975]; Axis z coordinate for clampCornerOuterCut. |
| clampCornerStart | -3.975 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 5, hole Ø12.684, axis point [22.922, 7.0, -22.922], extent [-3.975, -0.975]; Signed start extent for clampCornerOuterCut, from the stated axis point. |
| clampCornerEnd | -0.975 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 5, hole Ø12.684, axis point [22.922, 7.0, -22.922], extent [-3.975, -0.975]; Signed end extent for clampCornerOuterCut, from the stated axis point. |
| clampOuterDiameter | 12.63 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 6, hole Ø12.63, axis point [25.618, 7.0, 0.0], extent [-9.0, 24.0]; Diameter for clampAxialOuterCut. |
| clampAxisX | 25.618 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 6, hole Ø12.63, axis point [25.618, 7.0, 0.0], extent [-9.0, 24.0]; Axis x coordinate for clampAxialOuterCut. |
| clampStartZ | -9 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 6, hole Ø12.63, axis point [25.618, 7.0, 0.0], extent [-9.0, 24.0]; Signed start extent for clampAxialOuterCut, from the stated axis point. |
| clampEndZ | 24 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 6, hole Ø12.63, axis point [25.618, 7.0, 0.0], extent [-9.0, 24.0]; Signed end extent for clampAxialOuterCut, from the stated axis point. |
| keyUpperRecessDiameter | 12 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 7, hole Ø12, axis point [-2.0, 0.0, 16.4], extent [0.0, 3.0]; Diameter for keyUpperBackRecess. |
| clampReliefDiameter | 11.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 8, hole Ø11.5, axis point [28.665, 7.0, -5.054], extent [-26.345, -4.081]; Diameter for clampTiltOuterCut. |
| clampTiltAxisX | 28.665 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 8, hole Ø11.5, axis point [28.665, 7.0, -5.054], extent [-26.345, -4.081]; Axis x coordinate for clampTiltOuterCut. |
| clampTiltAxisZ | -5.054 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 8, hole Ø11.5, axis point [28.665, 7.0, -5.054], extent [-26.345, -4.081]; Axis z coordinate for clampTiltOuterCut. |
| clampTiltDirX | 0.1736 (unitless) | 0.0002 | stated | sources/dimension-sheet.md; Cylindrical features row 8, hole Ø11.5, axis point [28.665, 7.0, -5.054], extent [-26.345, -4.081]; Rounded axis-direction x component; normalize the vector before use. |
| clampTiltDirZ | 0.9848 (unitless) | 0.0002 | stated | sources/dimension-sheet.md; Cylindrical features row 8, hole Ø11.5, axis point [28.665, 7.0, -5.054], extent [-26.345, -4.081]; Rounded axis-direction z component; normalize the vector before use. |
| clampTiltStart | -26.345 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 8, hole Ø11.5, axis point [28.665, 7.0, -5.054], extent [-26.345, -4.081]; Signed start extent for clampTiltOuterCut, from the stated axis point. |
| clampTiltEnd | -4.081 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 8, hole Ø11.5, axis point [28.665, 7.0, -5.054], extent [-26.345, -4.081]; Signed end extent for clampTiltOuterCut, from the stated axis point. |
| clampUpperReliefX | 28.75 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 9, hole Ø11.5, axis point [28.75, 7.0, 0.0], extent [0.0, 27.506]; Axis x coordinate for clampUpperRelief. |
| clampUpperReliefEnd | 27.506 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 9, hole Ø11.5, axis point [28.75, 7.0, 0.0], extent [0.0, 27.506]; Signed end extent for clampUpperRelief, from the stated axis point. |
| clampOffsetDiameter | 9.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 10, hole Ø9.5, axis point [25.171, 5.5, 0.0], extent [-9.0, 24.0]; Diameter for clampNearOffsetCut. |
| clampOffsetX | 25.171 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 10, hole Ø9.5, axis point [25.171, 5.5, 0.0], extent [-9.0, 24.0]; Axis x coordinate for clampNearOffsetCut. |
| clampNearY | 5.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 10, hole Ø9.5, axis point [25.171, 5.5, 0.0], extent [-9.0, 24.0]; Axis y coordinate for clampNearOffsetCut. |
| clampFarY | 8.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 11, hole Ø9.5, axis point [25.171, 8.5, 0.0], extent [-9.0, 24.0]; Axis y coordinate for clampFarOffsetCut. |
| clampCornerOffsetDiameter | 8.787 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 12, hole Ø8.787, axis point [22.504, 5.143, -22.504], extent [-3.975, -0.975]; Diameter for clampCornerNearCut. |
| clampCornerOffsetX | 22.504 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 12, hole Ø8.787, axis point [22.504, 5.143, -22.504], extent [-3.975, -0.975]; Axis x coordinate for clampCornerNearCut. |
| clampCornerNearY | 5.143 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 12, hole Ø8.787, axis point [22.504, 5.143, -22.504], extent [-3.975, -0.975]; Axis y coordinate for clampCornerNearCut. |
| clampCornerOffsetZ | -22.504 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 12, hole Ø8.787, axis point [22.504, 5.143, -22.504], extent [-3.975, -0.975]; Axis z coordinate for clampCornerNearCut. |
| clampCornerFarY | 8.857 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 13, hole Ø8.787, axis point [22.504, 8.857, -22.504], extent [-3.975, -0.975]; Axis y coordinate for clampCornerFarCut. |
| clampInnerDiameter | 8 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 14, hole Ø8, axis point [27.777, 5.5, -4.898], extent [-19.018, -16.249]; Diameter for clampTiltNearCut. |
| clampTiltInnerX | 27.777 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 14, hole Ø8, axis point [27.777, 5.5, -4.898], extent [-19.018, -16.249]; Axis x coordinate for clampTiltNearCut. |
| clampTiltInnerZ | -4.898 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 14, hole Ø8, axis point [27.777, 5.5, -4.898], extent [-19.018, -16.249]; Axis z coordinate for clampTiltNearCut. |
| clampTiltNearStart | -19.018 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 14, hole Ø8, axis point [27.777, 5.5, -4.898], extent [-19.018, -16.249]; Signed start extent for clampTiltNearCut, from the stated axis point. |
| clampTiltNearEnd | -16.249 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 14, hole Ø8, axis point [27.777, 5.5, -4.898], extent [-19.018, -16.249]; Signed end extent for clampTiltNearCut, from the stated axis point. |
| clampTiltFarStart | -23.376 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 15, hole Ø8, axis point [27.777, 8.5, -4.898], extent [-23.376, -4.407]; Signed start extent for clampTiltFarCut, from the stated axis point. |
| clampTiltFarEnd | -4.407 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 15, hole Ø8, axis point [27.777, 8.5, -4.898], extent [-23.376, -4.407]; Signed end extent for clampTiltFarCut, from the stated axis point. |
| clampUpperInnerX | 27.849 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 16, hole Ø8, axis point [27.849, 5.5, 0.0], extent [0.0, 19.625]; Axis x coordinate for clampUpperNearCut. |
| clampUpperNearEnd | 19.625 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 16, hole Ø8, axis point [27.849, 5.5, 0.0], extent [0.0, 19.625]; Signed end extent for clampUpperNearCut, from the stated axis point. |
| clampUpperFarEnd | 24.712 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 17, hole Ø8, axis point [27.849, 8.5, 0.0], extent [0.0, 24.712]; Signed end extent for clampUpperFarCut, from the stated axis point. |
| counterboreDiameter | 6.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 18, hole Ø6.5, axis point [-23.92, 0.0, 0.0], extent [8.5, 14.0]; Diameter for leftPivotCounterbore. |
| leftPivotX | -23.92 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 18, hole Ø6.5, axis point [-23.92, 0.0, 0.0], extent [8.5, 14.0]; Axis x coordinate for leftPivotCounterbore. |
| pivotCounterboreStart | 8.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 18, hole Ø6.5, axis point [-23.92, 0.0, 0.0], extent [8.5, 14.0]; Signed start extent for leftPivotCounterbore, from the stated axis point. |
| upperLeftScrewX | -18.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 19, hole Ø6.5, axis point [-18.5, 0.0, 22.0], extent [0.0, 9.8]; Axis x coordinate for upperLeftCounterbore. |
| upperLeftScrewZ | 22 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 19, hole Ø6.5, axis point [-18.5, 0.0, 22.0], extent [0.0, 9.8]; Axis z coordinate for upperLeftCounterbore. |
| longCounterboreEnd | 9.8 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 19, hole Ø6.5, axis point [-18.5, 0.0, 22.0], extent [0.0, 9.8]; Signed end extent for upperLeftCounterbore, from the stated axis point. |
| lowerLeftScrewX | -17 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 20, hole Ø6.5, axis point [-17.0, 0.0, -20.0], extent [0.0, 9.8]; Axis x coordinate for lowerLeftCounterbore. |
| lowerLeftScrewZ | -20 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 20, hole Ø6.5, axis point [-17.0, 0.0, -20.0], extent [0.0, 9.8]; Axis z coordinate for lowerLeftCounterbore. |
| rightPivotX | 19.92 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 21, hole Ø6.5, axis point [19.92, 0.0, 0.0], extent [8.5, 14.0]; Axis x coordinate for rightPivotCounterbore. |
| upperRightScrewX | 20 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 22, hole Ø6.5, axis point [20.0, 0.0, 17.0], extent [0.0, 7.8]; Axis x coordinate for upperRightCounterbore. |
| upperRightScrewZ | 17 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 22, hole Ø6.5, axis point [20.0, 0.0, 17.0], extent [0.0, 7.8]; Axis z coordinate for upperRightCounterbore. |
| rightCounterboreEnd | 7.8 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 22, hole Ø6.5, axis point [20.0, 0.0, 17.0], extent [0.0, 7.8]; Signed end extent for upperRightCounterbore, from the stated axis point. |
| sideScallopDiameter | 5.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 23, hole Ø5.5, axis point [22.088, 0.0, -15.0], extent [0.0, 4.649]; Diameter for sideScallopBore. |
| sideScallopX | 22.088 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 23, hole Ø5.5, axis point [22.088, 0.0, -15.0], extent [0.0, 4.649]; Axis x coordinate for sideScallopBore. |
| sideScallopZ | -15 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 23, hole Ø5.5, axis point [22.088, 0.0, -15.0], extent [0.0, 4.649]; Axis z coordinate for sideScallopBore. |
| sideScallopEnd | 4.649 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 23, hole Ø5.5, axis point [22.088, 0.0, -15.0], extent [0.0, 4.649]; Signed end extent for sideScallopBore, from the stated axis point. |
| filamentDiameter | 4 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 24, hole Ø4, axis point [14.708, 0.0, 30.0], extent [0.0, 9.242]; Diameter for filamentTransverseBore. |
| filamentTransverseX | 14.708 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 24, hole Ø4, axis point [14.708, 0.0, 30.0], extent [0.0, 9.242]; Axis x coordinate for filamentTransverseBore. |
| filamentZ | 30 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 24, hole Ø4, axis point [14.708, 0.0, 30.0], extent [0.0, 9.242]; Axis z coordinate for filamentTransverseBore. |
| filamentTransverseEnd | 9.242 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 24, hole Ø4, axis point [14.708, 0.0, 30.0], extent [0.0, 9.242]; Signed end extent for filamentTransverseBore, from the stated axis point. |
| filamentEntryAxisX | -1.248 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 25, hole Ø4, axis point [-1.248, 3.964, 30.0], extent [20.136, 24.991]; Axis x coordinate for filamentAngledBore. |
| filamentEntryAxisY | 3.964 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 25, hole Ø4, axis point [-1.248, 3.964, 30.0], extent [20.136, 24.991]; Axis y coordinate for filamentAngledBore. |
| filamentDirX | 0.9538 (unitless) | 0.0002 | stated | sources/dimension-sheet.md; Cylindrical features row 25, hole Ø4, axis point [-1.248, 3.964, 30.0], extent [20.136, 24.991]; Rounded axis-direction x component; normalize the vector before use. |
| filamentDirY | 0.3003 (unitless) | 0.0002 | stated | sources/dimension-sheet.md; Cylindrical features row 25, hole Ø4, axis point [-1.248, 3.964, 30.0], extent [20.136, 24.991]; Rounded axis-direction y component; normalize the vector before use. |
| filamentEntryStart | 20.136 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 25, hole Ø4, axis point [-1.248, 3.964, 30.0], extent [20.136, 24.991]; Signed start extent for filamentAngledBore, from the stated axis point. |
| filamentEntryEnd | 24.991 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 25, hole Ø4, axis point [-1.248, 3.964, 30.0], extent [20.136, 24.991]; Signed end extent for filamentAngledBore, from the stated axis point. |
| upperLeftPilotDiameter | 3.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 26, hole Ø3.5, axis point [-18.5, 0.0, 22.0], extent [10.1, 14.0]; Diameter for upperLeftPilot. Edit only the final y=10.1..14 cylinder; keep the preceding square bridge fixed. |
| longPilotStart | 10.1 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 26, hole Ø3.5, axis point [-18.5, 0.0, 22.0], extent [10.1, 14.0]; Signed start extent for upperLeftPilot, from the stated axis point. |
| lowerLeftPilotDiameter | 3.5 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 27, hole Ø3.5, axis point [-17.0, 0.0, -20.0], extent [10.1, 14.0]; Diameter for lowerLeftPilot. Edit only the final y=10.1..14 cylinder; keep the preceding square bridge fixed. |
| screwDiameter | 3.4 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 28, hole Ø3.4, axis point [-23.92, 0.0, 0.0], extent [0.0, 7.813]; Diameter for leftPivotPilot. |
| pivotPilotEnd | 7.813 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 28, hole Ø3.4, axis point [-23.92, 0.0, 0.0], extent [0.0, 7.813]; Signed end extent for leftPivotPilot, from the stated axis point. |
| leftNutX | -22 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 29, hole Ø3.4, axis point [-22.0, 0.0, 15.0], extent [4.6, 14.0]; Axis x coordinate for leftNutPilot. |
| leftNutZ | 15 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 29, hole Ø3.4, axis point [-22.0, 0.0, 15.0], extent [4.6, 14.0]; Axis z coordinate for leftNutPilot. |
| nutPilotStart | 4.6 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 29, hole Ø3.4, axis point [-22.0, 0.0, 15.0], extent [4.6, 14.0]; Signed start extent for leftNutPilot, from the stated axis point. |
| lugNutX | 8 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 30, hole Ø3.4, axis point [8.0, 0.0, 28.0], extent [4.6, 14.0]; Axis x coordinate for lugNutPilot. |
| lugNutZ | 28 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 30, hole Ø3.4, axis point [8.0, 0.0, 28.0], extent [4.6, 14.0]; Axis z coordinate for lugNutPilot. |
| lowerNutX | 12 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 31, hole Ø3.4, axis point [12.0, 0.0, -17.0], extent [4.6, 14.0]; Axis x coordinate for lowerNutPilot. |
| lowerNutZ | -17 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 31, hole Ø3.4, axis point [12.0, 0.0, -17.0], extent [4.6, 14.0]; Axis z coordinate for lowerNutPilot. |
| rightPilotStart | 8.1 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 33, hole Ø3.4, axis point [20.0, 0.0, 17.0], extent [8.1, 14.0]; Signed start extent for upperRightPilot, from the stated axis point. |
| upperLeftBossDiameter | 11 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 34, pin Ø11, axis point [-18.5, 0.0, 22.0], extent [8.0, 14.0]; Diameter for upperLeftBoss. |
| lugBossDiameter | 10 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 35, pin Ø10, axis point [8.0, 0.0, 28.0], extent [0.0, 14.0]; Diameter for lugBoss. |
| clampCornerLipDiameter | 9.184 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 36, pin Ø9.184, axis point [22.922, 7.0, -22.922], extent [-3.975, -0.975]; Diameter for clampCornerLip. |
| clampAxialLipDiameter | 9.13 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 37, pin Ø9.13, axis point [25.618, 7.0, 0.0], extent [-9.0, 24.0]; Diameter for clampAxialLip. |
| clampFarLipDiameter | 6 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 38, pin Ø6, axis point [25.171, 8.5, 0.0], extent [-8.242, 24.0]; Diameter for clampFarLip. |
| clampFarLipStart | -8.242 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 38, pin Ø6, axis point [25.171, 8.5, 0.0], extent [-8.242, 24.0]; Signed start extent for clampFarLip, from the stated axis point. |
| clampCornerOffsetLipDiameter | 5.287 mm | 0.02 | stated | sources/dimension-sheet.md; Cylindrical features row 39, pin Ø5.287, axis point [22.504, 5.143, -22.504], extent [-3.975, -0.975]; Diameter for clampCornerNearLip. |
| nutLeftFlatX | -24.8 mm | 0.02 | stated | sources/dimension-sheet.md; +x face at x=-24.8; Left x flat of the trap centered at x=-22. |
| nutRightFlatX | -19.2 mm | 0.02 | stated | sources/dimension-sheet.md; -x face at x=-19.2; Right x flat of the trap centered at x=-22. |
| nutFullDepth | 4 mm | 0.02 | stated | sources/dimension-sheet.md; six -y faces at y=4; First support ledges stop the hex corner regions. |
| nutRectEnd | 4.3 mm | 0.02 | stated | sources/dimension-sheet.md; six -y faces at y=4.3; Second support ledges end the rectangular bridge. |
| longCounterboreFullDepth | 9.5 mm | 0.02 | stated | sources/dimension-sheet.md; four -y faces at y=9.5; Circular recess depth before support steps at the two left screws. |
| rightCounterboreFullDepth | 7.5 mm | 0.02 | stated | sources/dimension-sheet.md; two -y faces at y=7.5; Circular recess depth before support steps at (20,17). |
| nutAcrossFlats | 5.6 mm | 0.03 | derived | nutRightFlatX - nutLeftFlatX; Common width of the three point-up hex nut traps. |
| nutCornerRadius | 3.233161507 mm | 0.03 | derived | nutAcrossFlats / sqrt(3); Hex circumradius. |
| bridgeLayerHeight | 0.3 mm | 0.03 | derived | nutRectEnd - nutFullDepth; Printable bridge increment; no equality lock between independent dimensions. |
| lowerTransitionLength | 7.361 mm | 0.03 | derived | keyLowerExitStart - keyBackDepth; Lower keyhole tapered length. |
| longPilotLength | 3.9 mm | 0.03 | derived | plateThickness - longPilotStart; Straight pilot length used by the diameter edit tests. |
| pivotMouthDiameter | 3.9 mm | 0.15 | measured | sources/section-z0.png; v≈286, right pilot edges u≈1385 and 1479; 24 px/mm; Raster diameter of the tapered pivot-pilot mouth at y=8.5. |

Acceptance ledger: one row per acceptance quantity or named item; all vector/cylinder components are grouped in their item's row. Table values are stated document evidence, not agent measurements of reference geometry.

| acceptance item | expected value | tolerance | evidence / formula |
|---|---|---|---|
| envelope / bbox | min[-26.5,0,-30],max[26.5,14,33.72]; size[53,14,63.72] | .03 mm per limit | User frame; render notes; table 14.001 differs from nominal datum14. |
| solid_count | 1 | exact | Description and table. |
| volume | null; diagnostic29833.56 mm3 | nonbinding | Table quote; formal V=∫A(y)dy. Sparse sections and optional exterior do not define A(y), so no exact analytic target is invented. |
| surface_area | null; diagnostic11557.87 mm2 | nonbinding | Table quote; formal S=Σ∫surface dA; freeform surfaces are not fixed. |
| center_of_mass | null; diagnostic[-.703,6.989,-2.703] mm | nonbinding | Table quote; formal C=(1/V)∫volume[x,y,z]dV. Unknown exterior prevents an exact integral; no density-based mass claim. |
| deviation | null | not applicable | No reference mesh supplied. |
| export_volume_tolerance_rel | 0.002 | relative | Retained digital cross-format agreement, separate from reference fidelity. |
| blockout.volume_min | 42000 | mm3 lower band | Primary envelope-only plate53×58×14 plus cap(22.5−(8−10/2))×(33.72−28)×14=44597.56 mm3. |
| blockout.volume_max | 47500 | mm3 upper band | Band42000..47500 is about±6% around44597.56 and includes full-envelope47280.24 mm3. The cap is an intentionally overfilled blockout, not the final web. Every bbox limit must still match. |
| section.midPlate | y=7.0; area 2186.59 mm2;  outer 1; holes 11 | area 1%; topology exact | Stated table section y = 7.0: solid area 2186.59 mm2, 1 outer loops, 11 holes. |
| section.backPocketSection | y=1.5; area 2203.29 mm2;  outer 1; holes 9 | area 1%; topology exact | Stated table section y = 1.5: solid area 2203.29 mm2, 1 outer loops, 9 holes. |
| section.frontPocketSection | y=12.0; area 2148.31 mm2;  outer 1; holes 7 | area 1%; topology exact | Stated table section y = 12.0: solid area 2148.31 mm2, 1 outer loops, 7 holes. |
| section.keyholeDepthSection | x=0.0; area 333.46 mm2;  outer 2; holes 0 | area 1%; topology exact | Stated table section x = 0.0: solid area 333.46 mm2, 2 outer loops, 0 holes. |
| section.leftScrewDepthSection | x=-18.5; area 662.84 mm2;  outer 3; holes 0 | area 1%; topology exact | Stated table section x = -18.5: solid area 662.84 mm2, 3 outer loops, 0 holes. Mesh drawing title instead says two regions; unresolved Q3, draft uses table topology. |
| section.pivotDepthSection | z=0.0; area 336.53 mm2;  outer 4; holes 0 | area 1%; topology exact | Stated table section z = 0.0: solid area 336.53 mm2, 4 outer loops, 0 holes. |
| section.upperBoreDepthSection | z=17.0; area 355.45 mm2;  outer 4; holes 0 | area 1%; topology exact | Stated table section z = 17.0: solid area 355.45 mm2, 4 outer loops, 0 holes. |
| section.lowerScrewClampSection | z=-20.0; area 584.6 mm2;  outer 2; holes 1 | area 1%; topology exact | Stated table section z = -20.0: solid area 584.6 mm2, 2 outer loops, 1 holes. |
| face.leftDatum | x=-26.5,normal-; area 607.2; modeone | position 0.03 mm; area 1% | sources/dimension-sheet.md; axial row 1, quoted area 607.2, centroid[6.75, 1.1]; unique functional face |
| face.leftNutFlatLeft | x=-24.8,normal+; area 13.9; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 2, quoted area 13.9, centroid[2.15, 15]; unique functional face |
| face.leftNutBridgeLeft | x=-23.7,normal+; area 1.02; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 3, quoted area 1.02, centroid[4.45, 15]; unique functional face |
| face.leftFootSide | x=-21.95,normal-; area 76.48; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 4, quoted area 76.48, centroid[7, -27.27]; unique functional face |
| face.leftNutBridgeRight | x=-20.3,normal-; area 1.02; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 5, quoted area 1.02, centroid[4.45, 15]; unique functional face |
| face.upperLeftBridgeLeft | x=-20.25,normal+; area 1.05; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 6, quoted area 1.05, centroid[9.95, 22]; unique functional face |
| face.leftNutFlatRight | x=-19.2,normal-; area 13.9; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 7, quoted area 13.9, centroid[2.15, 15]; unique functional face |
| face.lowerLeftBridgeLeft | x=-18.75,normal+; area 1.05; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 8, quoted area 1.05, centroid[9.95, -20]; unique functional face |
| face.upperLeftBridgeRight | x=-16.75,normal-; area 1.05; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 10, quoted area 1.05, centroid[9.95, 22]; unique functional face |
| face.lowerLeftBridgeRight | x=-15.25,normal-; area 1.05; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 11, quoted area 1.05, centroid[9.95, -20]; unique functional face |
| face.lugNutFlatLeft | x=5.2,normal+; area 13.9; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 17, quoted area 13.9, centroid[2.15, 28]; unique functional face |
| face.lugNutBridgeLeft | x=6.3,normal+; area 1.02; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 18, quoted area 1.02, centroid[4.45, 28]; unique functional face |
| face.lowerNutFlatLeft | x=9.2,normal+; area 13.9; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 19, quoted area 13.9, centroid[2.15, -17]; unique functional face |
| face.lugNutBridgeRight | x=9.7,normal-; area 1.02; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 20, quoted area 1.02, centroid[4.45, 28]; unique functional face |
| face.lowerNutBridgeLeft | x=10.3,normal+; area 1.02; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 21, quoted area 1.02, centroid[4.45, -17]; unique functional face |
| face.lugNutFlatRight | x=10.8,normal-; area 13.9; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 22, quoted area 13.9, centroid[2.15, 28]; unique functional face |
| face.lowerNutBridgeRight | x=13.7,normal-; area 1.02; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 23, quoted area 1.02, centroid[4.45, -17]; unique functional face |
| face.lowerNutFlatRight | x=14.8,normal-; area 13.9; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 24, quoted area 13.9, centroid[2.15, -17]; unique functional face |
| face.upperRightBridgeLeft | x=18.3,normal+; area 1.02; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 25, quoted area 1.02, centroid[7.95, 17]; unique functional face |
| face.upperRightBridgeRight | x=21.7,normal-; area 1.02; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 26, quoted area 1.02, centroid[7.95, 17]; unique functional face |
| face.sideScallopEndFace | x=23.14,normal+; area 7.41; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 27, quoted area 7.41, centroid[0.89, -20.57]; unique functional face |
| face.clampLowerSideFace | x=24.0,normal+; area 12.89; modeone; center[1.11, -8.23] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 28, quoted area 12.89, centroid[1.11, -8.23]; individual repeated-face identity |
| face.clampUpperSideFace | x=24.0,normal+; area 10.2; modeone; center[1.12, 22.5] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 28, quoted area 10.2, centroid[1.12, 22.5]; individual repeated-face identity |
| face.rightSideFrontPanel | x=26.5,normal+; area 64.91; modeone; center[13.24, 2.77] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 29, quoted area 64.91, centroid[13.24, 2.77]; individual repeated-face identity |
| face.rightSideBackPanel | x=26.5,normal+; area 41.94; modeone; center[0.86, 7.53] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 29, quoted area 41.94, centroid[0.86, 7.53]; individual repeated-face identity |
| face.backDatum | y=0,normal-; area 2166.04; modesum | position 0.03 mm; area 4% | sources/dimension-sheet.md; axial row 30; intentional combined area 2163.69+2.35=2166.04. Do not require the optional tiny text island separately. |
| face.clampCornerBackLedge | y=0.75,normal+; area 1.5; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 31, quoted area 1.5, centroid[20.93, -24.43]; unique functional face |
| face.clampCornerPocketFloor | y=2.5,normal-; area 6.1; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 34, quoted area 6.1, centroid[20.61, -25.97]; unique functional face |
| face.clampUpperBackFloor | y=2.731,normal-; area 5.16; modeone; center[24.45, 22.5] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 35, quoted area 5.16, centroid[24.45, 22.5]; individual repeated-face identity |
| face.clampLowerBackFloor | y=2.731,normal-; area 1.76; modeone; center[24.24, -6.26] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 35, quoted area 1.76, centroid[24.24, -6.26]; individual repeated-face identity |
| face.keyUpperBackShoulder | y=3.0,normal+; area 66.24; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 36, quoted area 66.24, centroid[-2, 18.48]; unique functional face |
| face.lowerNutTopLedge | y=4.0,normal-; area 4.07; modeone; center[12, -14.79] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 37, quoted area 4.07, centroid[12, -14.79]; individual repeated-face identity |
| face.leftNutBottomLedge | y=4.0,normal-; area 4.07; modeone; center[-22, 12.79] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 37, quoted area 4.07, centroid[-22, 12.79]; individual repeated-face identity |
| face.leftNutTopLedge | y=4.0,normal-; area 4.07; modeone; center[-22, 17.21] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 37, quoted area 4.07, centroid[-22, 17.21]; individual repeated-face identity |
| face.lugNutTopLedge | y=4.0,normal-; area 4.07; modeone; center[8, 30.21] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 37, quoted area 4.07, centroid[8, 30.21]; individual repeated-face identity |
| face.lowerNutBottomLedge | y=4.0,normal-; area 4.07; modeone; center[12, -19.21] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 37, quoted area 4.07, centroid[12, -19.21]; individual repeated-face identity |
| face.lugNutBottomLedge | y=4.0,normal-; area 4.07; modeone; center[8, 25.79] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 37, quoted area 4.07, centroid[8, 25.79]; individual repeated-face identity |
| face.lugNutLeftLedge | y=4.3,normal-; area 3.73; modeone; center[5.75, 28] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 38, quoted area 3.73, centroid[5.75, 28]; individual repeated-face identity |
| face.leftNutLeftLedge | y=4.3,normal-; area 3.73; modeone; center[-24.25, 15] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 38, quoted area 3.73, centroid[-24.25, 15]; individual repeated-face identity |
| face.lugNutRightLedge | y=4.3,normal-; area 3.73; modeone; center[10.25, 28] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 38, quoted area 3.73, centroid[10.25, 28]; individual repeated-face identity |
| face.leftNutRightLedge | y=4.3,normal-; area 3.73; modeone; center[-19.75, 15] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 38, quoted area 3.73, centroid[-19.75, 15]; individual repeated-face identity |
| face.lowerNutLeftLedge | y=4.3,normal-; area 3.73; modeone; center[9.75, -17] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 38, quoted area 3.73, centroid[9.75, -17]; individual repeated-face identity |
| face.lowerNutRightLedge | y=4.3,normal-; area 3.73; modeone; center[14.25, -17] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 38, quoted area 3.73, centroid[14.25, -17]; individual repeated-face identity |
| face.upperRightTopLedge | y=7.5,normal-; area 6.07; modeone; center[20, 19.33] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 39, quoted area 6.07, centroid[20, 19.33]; individual repeated-face identity |
| face.upperRightBottomLedge | y=7.5,normal-; area 6.07; modeone; center[20, 14.67] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 39, quoted area 6.07, centroid[20, 14.67]; individual repeated-face identity |
| face.upperRightLeftLedge | y=7.8,normal-; area 4.74; modeone; center[17.6, 17] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 40, quoted area 4.74, centroid[17.6, 17]; individual repeated-face identity |
| face.upperRightRightLedge | y=7.8,normal-; area 4.46; modeone; center[22.36, 17] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 40, quoted area 4.46, centroid[22.36, 17]; individual repeated-face identity |
| face.keyUpperFrontShoulder | y=8.0,normal+; area 286.25; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 41, quoted area 286.25, centroid[-3.52, 19.17]; unique functional face |
| face.leftPivotShoulder | y=8.5,normal+; area 21.41; modeone; center[-23.86, 0] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 42, quoted area 21.41, centroid[-23.86, 0]; individual repeated-face identity |
| face.rightPivotShoulder | y=8.5,normal+; area 21.24; modeone; center[19.92, 0] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 42, quoted area 21.24, centroid[19.92, 0]; individual repeated-face identity |
| face.upperLeftTopLedge | y=9.5,normal-; area 5.79; modeone; center[-18.5, 24.36] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 43, quoted area 5.79, centroid[-18.5, 24.36]; individual repeated-face identity |
| face.lowerLeftTopLedge | y=9.5,normal-; area 5.79; modeone; center[-17, -17.64] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 43, quoted area 5.79, centroid[-17, -17.64]; individual repeated-face identity |
| face.lowerLeftBottomLedge | y=9.5,normal-; area 5.79; modeone; center[-17, -22.36] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 43, quoted area 5.79, centroid[-17, -22.36]; individual repeated-face identity |
| face.upperLeftBottomLedge | y=9.5,normal-; area 5.79; modeone; center[-18.5, 19.64] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 43, quoted area 5.79, centroid[-18.5, 19.64]; individual repeated-face identity |
| face.lowerLeftRightLedge | y=9.8,normal-; area 4.67; modeone; center[-14.57, -20] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 44, quoted area 4.67, centroid[-14.57, -20]; individual repeated-face identity |
| face.upperLeftRightLedge | y=9.8,normal-; area 4.67; modeone; center[-16.07, 22] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 44, quoted area 4.67, centroid[-16.07, 22]; individual repeated-face identity |
| face.upperLeftLeftLedge | y=9.8,normal-; area 4.67; modeone; center[-20.93, 22] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 44, quoted area 4.67, centroid[-20.93, 22]; individual repeated-face identity |
| face.lowerLeftLeftLedge | y=9.8,normal-; area 4.67; modeone; center[-19.43, -20] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 44, quoted area 4.67, centroid[-19.43, -20]; individual repeated-face identity |
| face.clampCornerFrontLedge | y=11.5,normal+; area 3.21; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 45, quoted area 3.21, centroid[20.91, -25.1]; unique functional face |
| face.clampCornerFrontFloor | y=13.25,normal-; area 9.0; modeone; center[21.81, -25.31] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 46, quoted area 9.0, centroid[21.81, -25.31]; individual repeated-face identity |
| face.clampLowerFrontFloor | y=13.25,normal-; area 3.99; modeone; center[25.84, -7.5] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 46, quoted area 3.99, centroid[25.84, -7.5]; individual repeated-face identity |
| face.clampUpperFrontFloor | y=13.25,normal-; area 3.99; modeone; center[25.84, 22.5] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 46, quoted area 3.99, centroid[25.84, 22.5]; individual repeated-face identity |
| face.frontDatum | y=14.0,normal+; area 2279.29; modeone | position 0.03 mm; area 3% | sources/dimension-sheet.md; axial row 47, quoted area 2279.29, centroid[1.43, -3.91]; unique functional face |
| face.bottomDatum | z=-30.0,normal-; area 573.52; modeone | position 0.03 mm; area 2% | sources/dimension-sheet.md; axial row 48, quoted area 573.52, centroid[-1.47, 7]; unique functional face |
| face.lowerLeftBridgeBottom | z=-21.75,normal+; area 2.69; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 54, quoted area 2.69, centroid[-17, 9.77]; unique functional face |
| face.lowerNutBridgeBottom | z=-18.7,normal+; area 2.61; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 55, quoted area 2.61, centroid[12, 4.27]; unique functional face |
| face.lowerLeftBridgeTop | z=-18.25,normal-; area 2.69; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 56, quoted area 2.69, centroid[-17, 9.77]; unique functional face |
| face.lowerNutBridgeTop | z=-15.3,normal-; area 2.61; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 58, quoted area 2.61, centroid[12, 4.27]; unique functional face |
| face.clampLowerSlotBottom | z=-9.0,normal+; area 27.19; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 59, quoted area 27.19, centroid[21.88, 7.62]; unique functional face |
| face.clampLowerSlotTop | z=-6.0,normal-; area 27.69; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 60, quoted area 27.69, centroid[21.94, 7.7]; unique functional face |
| face.clampLowerBackStep | z=-4.625,normal-; area 5.69; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 61, quoted area 5.69, centroid[25.13, 1.17]; unique functional face |
| face.leftPivotSlotBottom | z=-3.25,normal+; area 14.19; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 62, quoted area 14.19, centroid[-25.21, 11.25]; unique functional face |
| face.leftPivotSlotTop | z=3.25,normal-; area 14.19; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 63, quoted area 14.19, centroid[-25.21, 11.25]; unique functional face |
| face.leftNutBridgeBottom | z=13.3,normal+; area 2.61; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 64, quoted area 2.61, centroid[-22, 4.27]; unique functional face |
| face.upperRightBridgeBottom | z=15.3,normal+; area 2.68; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 65, quoted area 2.68, centroid[20, 7.76]; unique functional face |
| face.leftNutBridgeTop | z=16.7,normal-; area 2.61; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 66, quoted area 2.61, centroid[-22, 4.27]; unique functional face |
| face.upperRightBridgeTop | z=18.7,normal-; area 2.68; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 67, quoted area 2.68, centroid[20, 7.76]; unique functional face |
| face.clampUpperBackStep | z=19.625,normal+; area 5.91; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 68, quoted area 5.91, centroid[25.14, 1.21]; unique functional face |
| face.upperLeftBridgeBottom | z=20.25,normal+; area 2.69; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 69, quoted area 2.69, centroid[-18.5, 9.77]; unique functional face |
| face.clampUpperSlotBottom | z=21.0,normal+; area 27.99; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 70, quoted area 27.99, centroid[21.99, 7.74]; unique functional face |
| face.upperLeftBridgeTop | z=23.75,normal-; area 2.69; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 71, quoted area 2.69, centroid[-18.5, 9.77]; unique functional face |
| face.upperLeftBossLedge | z=24.0,normal+; area 17.26; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 72, quoted area 17.26, centroid[-25.06, 11]; unique functional face |
| face.clampUpperSlotTop | z=24.0,normal-; area 27.99; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 73, quoted area 27.99, centroid[21.99, 7.74]; unique functional face |
| face.clampUpperBackRim | z=25.375,normal-; area 3.05; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 74, quoted area 3.05, centroid[24.56, 1.36]; unique functional face |
| face.lugNutBridgeBottom | z=26.3,normal+; area 2.61; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 75, quoted area 2.61, centroid[8, 4.27]; unique functional face |
| face.topLeftLedge | z=28.0,normal+; area 204.0; modeone; center[-9.75, 4] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 76, quoted area 204.0, centroid[-9.75, 4]; individual repeated-face identity |
| face.topRightLedge | z=28.0,normal+; area 79.87; modeone; center[18.75, 5.15] | position 0.1 mm; area 2%; centroid same mm tolerance | sources/dimension-sheet.md; axial row 76, quoted area 79.87, centroid[18.75, 5.15]; individual repeated-face identity |
| face.lugNutBridgeTop | z=29.7,normal-; area 2.61; modeone | position 0.05 mm; area 2% | sources/dimension-sheet.md; axial row 77, quoted area 2.61, centroid[8, 4.27]; unique functional face |
| cylinder.keyUpperFrontCounterbore | hole; Ø26.0; point[-2.0, 0.0, 16.4]; dir[0.0, 1.0, 0.0]; t[8.0, 14.0]; length 6.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 1; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.keyLowerBackRecess | hole; Ø22.5; point[-2.0, 0.0, 0.0]; dir[0.0, 1.0, 0.0]; t[0.0, 3.0]; length 3.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 2; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.keyUpperMiddleBore | hole; Ø16.0; point[-2.0, 0.0, 16.4]; dir[0.0, 1.0, 0.0]; t[3.0, 8.0]; length 5.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 3; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.keyLowerFrontCounterbore | hole; Ø14.0; point[-2.0, 0.0, 0.0]; dir[0.0, 1.0, 0.0]; t[10.361, 14.0]; length 3.639 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 4; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampCornerOuterCut | hole; Ø12.684; point[22.922, 7.0, -22.922]; dir[0.7071, 0.0, 0.7071]; t[-3.975, -0.975]; length 3.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 5; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampAxialOuterCut | hole; Ø12.63; point[25.618, 7.0, 0.0]; dir[0.0, 0.0, 1.0]; t[-9.0, 24.0]; length 33.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 6; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.keyUpperBackRecess | hole; Ø12.0; point[-2.0, 0.0, 16.4]; dir[0.0, 1.0, 0.0]; t[0.0, 3.0]; length 3.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 7; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampTiltOuterCut | hole; Ø11.5; point[28.665, 7.0, -5.054]; dir[0.1736, 0.0, 0.9848]; t[-26.345, -4.081]; length 22.264 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 8; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampUpperRelief | hole; Ø11.5; point[28.75, 7.0, 0.0]; dir[0.0, 0.0, 1.0]; t[0.0, 27.506]; length 27.506 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 9; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampNearOffsetCut | hole; Ø9.5; point[25.171, 5.5, 0.0]; dir[0.0, 0.0, 1.0]; t[-9.0, 24.0]; length 33.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 10; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampFarOffsetCut | hole; Ø9.5; point[25.171, 8.5, 0.0]; dir[0.0, 0.0, 1.0]; t[-9.0, 24.0]; length 33.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 11; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampCornerNearCut | hole; Ø8.787; point[22.504, 5.143, -22.504]; dir[0.7071, 0.0, 0.7071]; t[-3.975, -0.975]; length 3.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 12; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampCornerFarCut | hole; Ø8.787; point[22.504, 8.857, -22.504]; dir[0.7071, 0.0, 0.7071]; t[-3.975, -0.975]; length 3.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 13; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampTiltNearCut | hole; Ø8.0; point[27.777, 5.5, -4.898]; dir[0.1736, 0.0, 0.9848]; t[-19.018, -16.249]; length 2.768 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 14; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampTiltFarCut | hole; Ø8.0; point[27.777, 8.5, -4.898]; dir[0.1736, 0.0, 0.9848]; t[-23.376, -4.407]; length 18.97 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 15; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampUpperNearCut | hole; Ø8.0; point[27.849, 5.5, 0.0]; dir[0.0, 0.0, 1.0]; t[0.0, 19.625]; length 19.625 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 16; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampUpperFarCut | hole; Ø8.0; point[27.849, 8.5, 0.0]; dir[0.0, 0.0, 1.0]; t[0.0, 24.712]; length 24.712 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 17; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.leftPivotCounterbore | hole; Ø6.5; point[-23.92, 0.0, 0.0]; dir[0.0, 1.0, 0.0]; t[8.5, 14.0]; length 5.5 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 18; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.upperLeftCounterbore | hole; Ø6.5; point[-18.5, 0.0, 22.0]; dir[0.0, 1.0, 0.0]; t[0.0, 9.8]; length 9.8 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 19; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.lowerLeftCounterbore | hole; Ø6.5; point[-17.0, 0.0, -20.0]; dir[0.0, 1.0, 0.0]; t[0.0, 9.8]; length 9.8 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 20; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.rightPivotCounterbore | hole; Ø6.5; point[19.92, 0.0, 0.0]; dir[0.0, 1.0, 0.0]; t[8.5, 14.0]; length 5.5 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 21; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.upperRightCounterbore | hole; Ø6.5; point[20.0, 0.0, 17.0]; dir[0.0, 1.0, 0.0]; t[0.0, 7.8]; length 7.8 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 22; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.sideScallopBore | hole; Ø5.5; point[22.088, 0.0, -15.0]; dir[0.0, 1.0, 0.0]; t[0.0, 4.649]; length 4.649 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 23; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.filamentTransverseBore | hole; Ø4.0; point[14.708, 0.0, 30.0]; dir[0.0, 1.0, 0.0]; t[0.0, 9.242]; length 9.242 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 24; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.filamentAngledBore | hole; Ø4.0; point[-1.248, 3.964, 30.0]; dir[0.9538, 0.3003, 0.0]; t[20.136, 24.991]; length 4.854 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 25; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.upperLeftPilot | hole; Ø3.5; point[-18.5, 0.0, 22.0]; dir[0.0, 1.0, 0.0]; t[10.1, 14.0]; length 3.9 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 26; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.lowerLeftPilot | hole; Ø3.5; point[-17.0, 0.0, -20.0]; dir[0.0, 1.0, 0.0]; t[10.1, 14.0]; length 3.9 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 27; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.leftPivotPilot | hole; Ø3.4; point[-23.92, 0.0, 0.0]; dir[0.0, 1.0, 0.0]; t[0.0, 7.813]; length 7.813 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 28; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.leftNutPilot | hole; Ø3.4; point[-22.0, 0.0, 15.0]; dir[0.0, 1.0, 0.0]; t[4.6, 14.0]; length 9.4 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 29; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.lugNutPilot | hole; Ø3.4; point[8.0, 0.0, 28.0]; dir[0.0, 1.0, 0.0]; t[4.6, 14.0]; length 9.4 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 30; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.lowerNutPilot | hole; Ø3.4; point[12.0, 0.0, -17.0]; dir[0.0, 1.0, 0.0]; t[4.6, 14.0]; length 9.4 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 31; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.rightPivotPilot | hole; Ø3.4; point[19.92, 0.0, 0.0]; dir[0.0, 1.0, 0.0]; t[0.0, 7.813]; length 7.813 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 32; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.upperRightPilot | hole; Ø3.4; point[20.0, 0.0, 17.0]; dir[0.0, 1.0, 0.0]; t[8.1, 14.0]; length 5.9 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 33; yes angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.upperLeftBoss | pin; Ø11.0; point[-18.5, 0.0, 22.0]; dir[0.0, 1.0, 0.0]; t[8.0, 14.0]; length 6.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 34; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.lugBoss | pin; Ø10.0; point[8.0, 0.0, 28.0]; dir[0.0, 1.0, 0.0]; t[0.0, 14.0]; length 14.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 35; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampCornerLip | pin; Ø9.184; point[22.922, 7.0, -22.922]; dir[0.7071, 0.0, 0.7071]; t[-3.975, -0.975]; length 3.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 36; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampAxialLip | pin; Ø9.13; point[25.618, 7.0, 0.0]; dir[0.0, 0.0, 1.0]; t[-9.0, 24.0]; length 33.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 37; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampFarLip | pin; Ø6.0; point[25.171, 8.5, 0.0]; dir[0.0, 0.0, 1.0]; t[-8.242, 24.0]; length 32.242 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 38; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampCornerNearLip | pin; Ø5.287; point[22.504, 5.143, -22.504]; dir[0.7071, 0.0, 0.7071]; t[-3.975, -0.975]; length 3.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 39; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| cylinder.clampCornerFarLip | pin; Ø5.287; point[22.504, 8.857, -22.504]; dir[0.7071, 0.0, 0.7071]; t[-3.975, -0.975]; length 3.0 | axis .03 mm; radius .025 mm; length .05 mm | sources/dimension-sheet.md cylindrical row 40; partial angular coverage. Normalize direction; rounded endpoint subtraction may differ from stated length by .001. |
| plane.leftLowerBevel | point[-22.946, 0.0, -23.45]; outward[-0.7373, 0.0, -0.6756]; area 45.71 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 1, stated point[-22.946, 0.0, -23.45], outward normal[-0.7373, 0.0, -0.6756], area 45.71. |
| plane.leftUpperBevel | point[-26.5, 0.0, 24.0]; outward[-0.7071, 0.0, 0.7071]; area 45.25 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 2, stated point[-26.5, 0.0, 24.0], outward normal[-0.7071, 0.0, 0.7071], area 45.25. |
| plane.rightUpperBevel | point[22.5, 0.0, 28.0]; outward[0.7071, 0.0, 0.7071]; area 44.94 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 3, stated point[22.5, 0.0, 28.0], outward normal[0.7071, 0.0, 0.7071], area 44.94. |
| plane.clampTiltWall | point[25.721, 12.259, -8.679]; outward[0.3368, -0.9397, -0.0594]; area 35.38 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 4, stated point[25.721, 12.259, -8.679], outward normal[0.3368, -0.9397, -0.0594], area 35.38. |
| plane.clampCornerUpperWall | point[17.704, 7.0, -23.326]; outward[0.7071, -0.0, 0.7071]; area 33.85 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 5, stated point[17.704, 7.0, -23.326], outward normal[0.7071, -0.0, 0.7071], area 33.85. |
| plane.leftShallowBevel | point[-26.5, 0.0, -21.925]; outward[-0.0872, -0.0, -0.9962]; area 32.94 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 6, stated point[-26.5, 0.0, -21.925], outward normal[-0.0872, -0.0, -0.9962], area 32.94. |
| plane.clampCornerLowerWall | point[19.825, 7.0, -21.205]; outward[-0.7071, 0.0, -0.7071]; area 31.99 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 7, stated point[19.825, 7.0, -21.205], outward normal[-0.7071, 0.0, -0.7071], area 31.99. |
| plane.keyNeckLeft | point[-8.566, 0.0, 5.18]; outward[0.9659, -0.0, -0.2588]; area 21.24 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 8, stated point[-8.566, 0.0, 5.18], outward normal[0.9659, -0.0, -0.2588], area 21.24. |
| plane.keyNeckRight | point[2.594, 0.0, 12.54]; outward[-0.9659, -0.0, -0.2588]; area 21.24 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 9, stated point[2.594, 0.0, 12.54], outward normal[-0.9659, -0.0, -0.2588], area 21.24. |
| plane.upperLeftBossBevel | point[-16.5, 14.0, 28.0]; outward[0.766, -0.0, 0.6428]; area 21.12 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 10, stated point[-16.5, 14.0, 28.0], outward normal[0.766, -0.0, 0.6428], area 21.12. |
| plane.rightLowerBevel | point[26.5, 0.0, -22.75]; outward[0.7071, 0.0, -0.7071]; area 23.31 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 11, stated point[26.5, 0.0, -22.75], outward normal[0.7071, 0.0, -0.7071], area 16.06. Add coplanar row 25 area 7.25; the plane inspector sums both faces. |
| plane.lugHexUpperRight | point[8.0, 0.0, 31.233]; outward[-0.5, -0.0, -0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 12, stated point[8.0, 0.0, 31.233], outward normal[-0.5, -0.0, -0.866], area 12.98. |
| plane.leftHexUpperLeft | point[-24.8, 0.0, 16.617]; outward[0.5, -0.0, -0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 13, stated point[-24.8, 0.0, 16.617], outward normal[0.5, -0.0, -0.866], area 12.98. |
| plane.lugHexLowerLeft | point[8.0, 0.0, 24.767]; outward[0.5, -0.0, 0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 14, stated point[8.0, 0.0, 24.767], outward normal[0.5, -0.0, 0.866], area 12.98. |
| plane.leftHexUpperRight | point[-22.0, 0.0, 18.233]; outward[-0.5, -0.0, -0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 15, stated point[-22.0, 0.0, 18.233], outward normal[-0.5, -0.0, -0.866], area 12.98. |
| plane.lowerHexLowerLeft | point[12.0, 0.0, -20.233]; outward[0.5, -0.0, 0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 16, stated point[12.0, 0.0, -20.233], outward normal[0.5, -0.0, 0.866], area 12.98. |
| plane.lugHexLowerRight | point[10.8, 0.0, 26.383]; outward[-0.5, -0.0, 0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 17, stated point[10.8, 0.0, 26.383], outward normal[-0.5, -0.0, 0.866], area 12.98. |
| plane.lowerHexLowerRight | point[14.8, 0.0, -18.617]; outward[-0.5, -0.0, 0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 18, stated point[14.8, 0.0, -18.617], outward normal[-0.5, -0.0, 0.866], area 12.98. |
| plane.lowerHexUpperRight | point[12.0, 0.0, -13.767]; outward[-0.5, -0.0, -0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 19, stated point[12.0, 0.0, -13.767], outward normal[-0.5, -0.0, -0.866], area 12.98. |
| plane.leftHexLowerLeft | point[-22.0, 0.0, 11.767]; outward[0.5, -0.0, 0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 20, stated point[-22.0, 0.0, 11.767], outward normal[0.5, -0.0, 0.866], area 12.98. |
| plane.leftHexLowerRight | point[-19.2, 0.0, 13.383]; outward[-0.5, -0.0, 0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 21, stated point[-19.2, 0.0, 13.383], outward normal[-0.5, -0.0, 0.866], area 12.98. |
| plane.lugHexUpperLeft | point[5.2, 0.0, 29.617]; outward[0.5, -0.0, -0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 22, stated point[5.2, 0.0, 29.617], outward normal[0.5, -0.0, -0.866], area 12.98. |
| plane.lowerHexUpperLeft | point[9.2, 0.0, -15.383]; outward[0.5, -0.0, -0.866]; area 12.98 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 23, stated point[9.2, 0.0, -15.383], outward normal[0.5, -0.0, -0.866], area 12.98. |
| plane.clampCornerBackBevel | point[21.107, -2.5, -24.608]; outward[0.7071, 0.0, -0.7071]; area 8.42 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 24, stated point[21.107, -2.5, -24.608], outward normal[0.7071, 0.0, -0.7071], area 8.42. |
| plane.clampCornerBottomWall | point[20.842, -0.0, -28.408]; outward[0.7071, -0.0, 0.7071]; area 6.25 | .04 mm; .2°; area 3% | sources/dimension-sheet.md; inclined row 26, stated point[20.842, -0.0, -28.408], outward normal[0.7071, -0.0, 0.7071], area 6.25. |
| dimension.overallWidth | x:53 mm; bbox extent | 0.03 | plateWidth; source envelope. |
| dimension.overallThickness | y:14 mm; bbox extent | 0.03 | Nominal y span; table 14.001 differs by only .001. |
| dimension.overallHeight | z:63.72 mm; bbox extent | 0.03 | lugMaxZ - bottomZ. |
| dimension.matingFaceSeparation | y:14 mm; ['backDatum', 'frontDatum'] | 0.03 | 14 - 0. |
| dimension.leftFootOffset | x:4.55 mm; ['leftDatum', 'leftFootSide'] | 0.04 | leftFootX + halfWidth = -21.95 +26.5. |
| dimension.upperRecessDepth | y:3 mm; ['backDatum', 'keyUpperBackShoulder'] | 0.04 | keyBackDepth. |
| dimension.upperBoreLength | y:5 mm; ['keyUpperBackShoulder', 'keyUpperFrontShoulder'] | 0.04 | keyMiddleEnd - keyBackDepth =8-3. |
| dimension.upperCounterboreDepth | y:6 mm; ['keyUpperFrontShoulder', 'frontDatum'] | 0.04 | plateThickness - keyMiddleEnd =14-8. |
| dimension.pivotCounterboreDepth | y:5.5 mm; ['rightPivotShoulder', 'frontDatum'] | 0.04 | plateThickness - pivotCounterboreStart =14-8.5. |
| dimension.nutTrapWidth | x:5.6 mm; ['leftNutFlatLeft', 'leftNutFlatRight'] | 0.04 | nutAcrossFlats = -19.2 -(-24.8). |
| dimension.lowerClampSlotHeight | z:3 mm; ['clampLowerSlotBottom', 'clampLowerSlotTop'] | 0.04 | Table face levels -6 -(-9). |
| dimension.upperClampSlotHeight | z:3 mm; ['clampUpperSlotBottom', 'clampUpperSlotTop'] | 0.04 | Table face levels 24-21. |

Edit tests use two independent final pilot diameters. A thickness/global-scale edit would move pinned datums and alter the table's partial cylinders; a table-derived chord edit is inappropriate. Each chosen pilot is isolated over y=10.1..14, so material removal has an analytic response. Small, nonzero edits stay within the declared cylinder-radius band and preserve unrelated interfaces.

| edited parameter | change | expected volume change | bbox / refusal |
|---|---|---|---|
| upperLeftPilotDiameter | 3.50 → 3.54 mm; sweep 3.48,3.50,3.52 | −π/4×((3.50+.04)²−3.50²)×(plateThickness−longPilotStart)=−0.862555679 mm3; decrease | [0,0,0] mm; assert diameter>0; infeasible delta−4 gives−.5 and must refuse |
| lowerLeftPilotDiameter | 3.50 → 3.54 mm; sweep 3.48,3.50,3.52 | −π/4×((3.50+.04)²−3.50²)×(plateThickness−longPilotStart)=−0.862555679 mm3; decrease | [0,0,0] mm; assert diameter>0; infeasible delta−4 gives−.5 and must refuse |

Keep the preceding y=9.8..10.1 square support stage fixed during those edits. Delta-volume tolerance is 3% of the delta, not of the whole housing. Use physical sanity assertions (positive diameters, ordered depth stations, remaining wall thickness), never nominal-value equality locks.

Probe evidence: solid points [-10,7,-25],[-24,6,-10],[8,7,31] are in the visible core with millimetres of boundary clearance. Keyhole voids lie on its documented axes or connecting neck [-2,7,8]. Fastener voids lie on open axes with at least 1.7 mm radial clearance. No near-wall probe is placed at the raster-measured pivot mouth, guessed blends or partial bores whose axes lie outside the housing. Partial surfaces are checked with cylinder and section specifications.

All nine interfaces list explicit acceptance checks. The four datums, +x patches, keyhole, fastener pattern, two filament passages and all clamp bores/lips are pinned. Optional styling cannot erase these items.

## 6. Defaults retained

- Units mm and deg; reconstruction release status retained. Solid count 1 is stated.
- Material and density remain null. The source says printed, so process is 3D printing with unspecified settings. No mass is claimed.
- Export-volume agreement retains 0.002 relative. STEP is authoritative; engine/STL agreement is separate.
- Explicit digital policy: table parameters generally ±.02 mm, direction components ±.0002; cylinder axes ±.03 mm, radii ±.025 mm, lengths ±.05 mm. These accommodate rounding, not physical fits.
- Repeated-face centers use ±.10 mm; principal datum positions ±.03 mm. Area bands are 1–4% as listed. Combined back-area 4% allows optional lettering/arrow omission; no typographic face is mandatory.
- Volume, area and centroid remain diagnostic quotes, with formal integrals in section 5. Schema 1 lacks a diagnostic-only quantity flag, so null fields avoid turning diagnostics into release gates.
- No geometric parameter is defaulted or inferred to fill a template. Five raster parameters have explicit measurement uncertainty. Missing blend radii and hardware details remain questions.

## 7. Unrepresentable or low-confidence features

The required bundle check was attempted during drafting. It rejects a pre-existing top-level main.kcl (28 bytes, modified 2026-09-16), which is outside this task's two-file edit scope. The PartContract content and source-coverage audits pass; bundle packaging cannot pass until the orchestrator removes or relocates that file. No KCL was written or modified in this task.

Tabulated surfaces constrain functional geometry but do not uniquely specify all angular trims, freeform lobe/web blends or lettering. Optional features receive only shared-envelope probes; those do not validate typography or fillet radii. The tabulated Ø5.5 scallop remains a located cylinder even when its surrounding cosmetic blend is simplified.

Face coverage omits typography/arrow-only axial rows 9,12–16,32–33,49–53,57 (one-based data-row numbers). Inclined rows 27–32 describe cosmetic lobe/lug and marking details and are not required planes. Inclined row 25 is combined with coplanar row 11. All 40 cylinder rows are included. Only the back contact uses explicit summed coplanar area; repeated functional faces otherwise have separate centers.

- Q1 — Keyhole conflict: prose places Ø26 at z=0 and Ø14 at z=16.4 and implies a lower Ø16 cylinder; the dimension table and sections reverse those counterbores and show a lower taper. Which is intended? Draft checks provisionally follow the table and sections; intent is preserved verbatim.
- Q2 — View naming: front.png shows the y=0 hex-pocket/marking side, although the frame calls y=14 the front. Are these camera labels only? This draft uses numerical coordinates and the requested datum definitions.
- Q3 — Topology: the table gives three outer loops at x=-18.5, while the section drawing says two regions. Which is authoritative? Draft acceptance uses the table's 662.84 mm2 and three loops; the drawing says 662.94 mm2 and two regions.
- Q4 — Construction: exact angular trims and connecting blends of the partial clamp surfaces are not tabulated. Can further drawings resolve them? All 40 cylinders and functional planes are specified; surrounding blends remain underdetermined, and the pivot-mouth Ø3.9 is only raster measured.
- Q5 — Diagnostics: quoted volume 29833.56 mm3, area 11557.87 mm2 and centroid [-0.703,6.989,-2.703] mm lack a complete analytic exterior. Should they ever become mandatory gates? They remain nonbinding; schema 1 cannot label these acceptance quantities diagnostic-only, so their fields are null.
- Q6 — Cosmetics: exact fan-lobe outline, lug fillet radius and R1/arrow outlines are unspecified; embossed versus recessed is also unclear. May they remain omitted or approximate? Shared envelope and functional checks still apply.
- Q7 — Manufacturing: material, density, print settings and physical fit tolerances are unspecified; trap hardware is called both nut and heat-set hardware. Which material and fasteners/inserts are intended? Only documented geometry and digital tolerances are specified.
- Q8 — Thickness: the table bbox reaches y=14.001 but the face and renders give 14.000. Is the extra 0.001 intentional? This draft retains the requested y=14 datum with a 0.03 mm envelope tolerance.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-26.5, 0.0, -30.0] → [26.5, 14.0, 33.72] | 43989.43499999393 | pass | 2026-09-17T14:21:40Z: within envelope and band |
