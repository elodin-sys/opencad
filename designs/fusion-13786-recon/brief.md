# fusion-13786-recon — design brief

## 1. Intent and configuration

User intent, verbatim:

> Reconstruct the mechanical part shown in the attached renders, sections and dimension sheet as editable, parameterized KCL in the part's own frame (bbox min [-50.0, -50.0, -0.0], size [100.0, 100.0, 3.0] mm). Declare every hole, boss and shaft as an acceptance cylinder and every planar face level as a named face; one solid; export STEP and STL. Held-out: the pipeline is frozen, the reference CAD is evaluator-only.

The part is Fusion 360 Gallery body `84608_204c01e6_0008_1` (joint set `joint_set_13786`): a 100 × 100 × 3 mm plate in its native centred frame. Features, all through the 3 mm thickness unless noted:

- two 45° south-corner chamfers of leg 5 mm
- two Ø6 (R3) quarter-cylinder pins blending the north corners
- one Ø5 through-hole at the origin
- one elliptical through-slot centred near (0, 26), semi-axes about 35 × 14 mm
- two short Ø2 bores along x at y = 42, z = 1.5, each 5 mm deep from the ±x faces

Authoritative numbers are the dimension sheet (envelope, mass properties, named planar levels, inclined planes, cylinders, sections). Renders and section drawings confirm topology and supply the slot size, which the sheet never names. One connected solid; later export is STEP and STL. This drafting turn writes only the contract and brief.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| `sources/part-brief.md` | text | authoritative | `2996f2cd1a38ec182c89083d6f31db6ae63320cc65922ea89c3d094e3f437e99` | Held-out brief; native frame and one-solid / STEP+STL requirement. Prefix `2996f2cd1a38`. |
| `sources/dimension-sheet.md` | text | authoritative | `c4cd6838380b49927b9aec16481a3ceb634bde135f938fd2e2bf1382bd3b59f9` | Envelope, mass properties, 8 axis-aligned face levels, 2 chamfer planes, 4 cylinder rows, 3 sections. Prefix `c4cd6838380b`. |
| `sources/render-notes.md` | text | illustrative | `e843ea4b9fbd1a9ad59fda56da654bd1ab9f72c03bdcab66846ab4cf3c166662` | Names the nine views; 8240-triangle reference extents 100 × 100 × 3 mm. Prefix `e843ea4b9fbd`. |
| `sources/top.png` | image | authoritative | `d3469030e289763c536ca02dd90890de8b7e12b48ace93b867b1ff9d9a67769d` | Top ortho, mm grid; slot tips, centre hole, chamfers, north pins. Prefix `d3469030e289`. |
| `sources/section-z1.5.png` | drawing | authoritative | `807c6a6f70b4ae60f8a8b4b8033853bd1a579676ec9436c69e682fd58babf9f9` | Mid-plane outline; slot, both edge notches, pins, chamfers. Prefix `807c6a6f70b4`. |
| `sources/section-x0.png` | drawing | authoritative | `891a08ff25cb1842a76877229cb2f872a6ecbd9a4cf51b34b56df93833643454` | Three solid bars at x = 0; title area 200.82 mm². Prefix `891a08ff25cb`. |
| `sources/section-y0.png` | drawing | authoritative | `530c15ddb13ad3f0ff388f06f7f24a6c02d6632d5c43c4c3224020f646412c6c` | Two bars split by the Ø5 hole; title area 285.01 mm². Prefix `530c15ddb13a`. |
| `sources/front.png` | image | illustrative | `e3b05599a447ed2cae0a3b5576b6dc32ad2e0a0876634d9f0682737453811434` | Front ortho; 5 mm dark chamfer bar at x = −50..−45. Prefix `e3b05599a447`. |
| `sources/right.png` | image | illustrative | `4855a8d98972ec1c017ba93502daeef3fae4bcca20e568b37e4b4346098b6965` | Right ortho; south chamfer and north pin on x = 50. Prefix `4855a8d98972`. |
| `sources/iso.png` | image | illustrative | `25f71ed888f526805d40c9fec1cf8cc0d0adebdb32b6291e9b4999dad4732146` | Isometric; +x edge bore visible; caption 100.00 × 100.00 × 3.00 mm. Prefix `25f71ed888f5`. |
| `sources/iso2.png` | image | illustrative | `feb2b2e25ca9714b8db635000980ce33cdacbcbd0ef00335cd6a27eb51b5e3f2` | Second isometric, opposite corner. Prefix `feb2b2e25ca9`. |
| `sources/iso-below.png` | image | illustrative | `1f3cf8ee9d2c122426a1ad857d85ceb394bd0d0a93c4c1ce08648cf8fdc71c83` | Underside isometric; through-features and +x edge bore. Prefix `1f3cf8ee9d2c`. |

No `reference/` ingest, no mesh, no coordinate table. The same nine PNGs exist under `truth/cases/fusion-13786-recon/inputs/renders/` and were opened; they match the staging copies.

## 3. Requirement record

Digital comparison thresholds, not production tolerances.

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Envelope | min [−50, −50, 0], size 100 × 100 × 3 | mm | part-brief; dimension-sheet Envelope | ±0.05 | stated |
| Body count | 1 solid | count | part-brief; sheet "solids 1" | exact | stated |
| Exports | STEP and STL | — | user intent | KCL/STEP/STL volume ±0.2% | stated |
| Named planar levels | x = ±50, ±45; y = ±50; z = 0, 3 | mm | sheet Axis-aligned planar faces | plane ±0.05; areas as sheet | stated |
| South chamfers | two 45° planes through [±47.5, −47.5, 0], area 21.21 each | mm | sheet Inclined planar faces | angle ±0.5°; area ±2% | stated |
| Centre hole | Ø5 along z at (0, 0) | mm | sheet Cylinders | ±0.05 | stated |
| Edge bores | Ø2 along x at y = 42, z = 1.5 | mm | sheet Cylinders + faces x = ±45 | dia ±0.05; depth 5 ±0.15 | stated location; depth from faces (see open Q) |
| North pins | Ø6, axes (±47, 47), partial 360°, length 3 | mm | sheet Cylinders | ±0.05 | stated |
| Through-slot | ellipse, centre (0, 26), rx 35, ry 14 | mm | top.png, section-z1.5.png, section x = 0 regions | rx ±1.0; ry ±0.3 | measured / derived |
| Volume | 25187.47 | mm³ | sheet Envelope and mass properties | ±1% | stated |
| Surface area | 18523.05 | mm² | sheet | ±2% | stated |
| Centre of mass | (0, −4.716, 1.5) | mm | sheet | ±0.5 | stated |
| Section x = 0 | area 200.78, 3 loops, 0 holes | mm² | sheet Sections | area ±2% | stated |
| Section y = 0 | area 285, 2 loops, 0 holes | mm² | sheet Sections | area ±1% | stated |
| Section z = 1.5 | area 8391.82, 1 loop, 2 holes | mm² | sheet Sections | area ±2% | stated |
| Material / density / process | unspecified | — | no source | remain null | open |

## 4. Coordinate frame, scale, and measurement method

Origin at the centre of the bottom square: the plate occupies x = [−50, 50], y = [−50, 50], z = [0, 3]. In a top view looking from +z toward the bottom, +x is right and +y is up. +z goes from the bottom to the top. The elliptical slot lies in y > 0; the chamfers lie in y < 0. This is the dimension-sheet native frame (no re-alignment).

Datums: `bottomDatum` is z = 0 (outward −z); `topDatum` is z = 3 (outward +z); `xyCentre` is the Ø5 hole axis.

Images are orthographic millimetre plots (axes labelled `x(mm)`, `y(mm)`, `z(mm)`). One plot millimetre equals one model millimetre; no perspective correction. `section-z1.5.png` is 1600 × 1600 px. The data grid runs from x = −50 at column 282 to x = 50 at column 1413, and from y = 50 at row 218 to y = −50 at row 1349 (1131 px / 100 mm ≈ 11.31 px/mm), with 5 mm grid lines. `top.png` uses the same labelled millimetre grid.

Pixel / line evidence:

- Slot left and right tips sit on the x = ±35 grid lines of `top.png` and `section-z1.5.png` (columns 452 and 1244 on the z-section). That is `slotRx` = 35 mm, tolerance 1.0 mm (~11 px / line width).
- Slot is symmetric about x = 0 (`slotCentreX` = 0 ± 0.5 mm).
- At x = 0, `section-x0.png` and the sheet region table show three solid bars of height 47.5, 9.5 and 10 mm. Those place the slot at y = 12..40, so `slotRy` = 14 mm and `slotCentreY` = 26 mm.
- `section-z1.5.png` shows two rectangular notches at y ≈ 41..43, each about one 5 mm grid square deep from x = ±50. Combined with circular faces of area 3.14 at x = ±45 (centroids (42, 1.5)), the Ø2 feature is two 5 mm blind bores, not a through-slot. A through-hole of length 100 mm would split the z = 1.5 section into two regions; the drawing has one outer loop.
- Centre hole at (0, 0): white disk about 5 mm across on the 5 mm grid; matches the sheet Ø5.
- South corners: 45° cuts from (−50, −45) to (−45, −50) and the mirror; `front.png` shows a 5 mm dark bar at x = −50..−45.
- North corners: quarter-circles whose tangency points sit 3 mm in from x = ±50 and y = 50, matching pin axes at (±47, 47), Ø6.
- `iso.png`, `iso2.png` and `iso-below.png` show a small hole on the +x edge face and through-openings for the slot and centre hole. Caption: bbox 100.00 × 100.00 × 3.00 mm.

Stated sheet numbers are used as-is. Image-read values get wide tolerances. No quantity is `measured (reference model)` — there is no `reference.json`.

## 5. Measurement and inference record

Parameter provenance: 15 stated, 2 measured, 3 derived, 0 inferred, 0 defaulted, 0 measured (reference model).

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| `plateWidth` | 100 mm | ±0.05 mm | stated | Sheet envelope size [100, 100, 3]; part-brief. |
| `plateHeight` | 100 mm | ±0.05 mm | stated | Same. |
| `plateThickness` | 3 mm | ±0.05 mm | stated | Same; iso caption 3.00 mm. Edit +1 mm → ΔV ≈ 8412 mm³ (plan area of the extruded profile), bbox Δz = +1. Infeasible Δ = −3. |
| `holeDia` | 5 mm | ±0.05 mm | stated | Sheet cylinder table. Edit +1 mm → ΔV = −π(3²−2.5²)·3 = −25.918 mm³. Infeasible Δ = +20 (merges with the slot). |
| `holeCentreX` | 0 mm | ±0.05 mm | stated | Sheet axis through [0, 0, 1.5]. |
| `holeCentreY` | 0 mm | ±0.05 mm | stated | Same. |
| `edgeHoleDia` | 2 mm | ±0.05 mm | stated | Sheet cylinder table. |
| `edgeHoleY` | 42 mm | ±0.05 mm | stated | Sheet axis y = 42; x = ±45 face centroids (42, 1.5). |
| `edgeHoleDepth` | 5 mm | ±0.15 mm | stated | Distance from x = ±50 to the π-area faces at x = ±45. |
| `edgeHoleZ` | 1.5 mm | ±0.05 mm | derived | `plateThickness / 2`; sheet lists 1.5. |
| `pinDia` | 6 mm | ±0.05 mm | stated | Sheet pin diameter 6, partial 360°. |
| `pinCentreX` | 47 mm | ±0.05 mm | stated | Sheet pin axes x = ±47. |
| `pinCentreY` | 47 mm | ±0.05 mm | stated | Sheet pin axes y = 47. |
| `chamferLeg` | 5 mm | ±0.05 mm | stated | Chamfer planes through [±47.5, −47.5]; y = −50 area 270 = (100−10)·3. |
| `topStrip` | 10 mm | ±0.3 mm | stated | Sheet section x = 0 region 10×3 at centroid y = 45.02. |
| `midBridge` | 9.5 mm | ±0.3 mm | stated | Sheet section x = 0 region 9.5×3 at centroid y = 7.23. |
| `slotCentreX` | 0 mm | ±0.5 mm | measured | Slot symmetric on the x = 0 grid of top.png and section-z1.5.png. |
| `slotCentreY` | 26 mm | ±0.3 mm | derived | `holeCentreY + holeDia/2 + midBridge + slotRy` = 0+2.5+9.5+14. |
| `slotRx` | 35 mm | ±1.0 mm | measured | Tips on the x = ±35 grid lines (~11.31 px/mm). |
| `slotRy` | 14 mm | ±0.3 mm | derived | `(plateHeight/2 − topStrip − holeCentreY − holeDia/2 − midBridge) / 2` = 14. |

| acceptance value | nominal | digital criterion | provenance | formula / evidence |
|---|---|---|---|---|
| `envelope` | [−50, −50, 0] → [50, 50, 3] | ±0.05 mm | stated | Sheet bbox; (±plateWidth/2, ±plateHeight/2, 0..plateThickness). |
| `volume` | 25187.47 mm³ | ±1% | stated | Sheet mass properties. Analytic 35×14 ellipse + listed cuts ≈ 25205 mm³. |
| `surface_area` | 18523.05 mm² | ±2% | stated | Sheet mass properties. |
| `center_of_mass` | (0, −4.716, 1.5) mm | ±0.5 mm | stated | Sheet; y south of origin because the slot sits in +y. |
| `solid_count` | 1 | exact | stated | Sheet; user intent. |
| `sectionX0` | x = 0; 200.78 mm²; 3 loops; 0 holes | area ±2% | stated | Sheet; image title 200.82. |
| `sectionY0` | y = 0; 285 mm²; 2 loops; 0 holes | area ±1% | stated | Sheet; 2 × 47.5 × 3 = 285. |
| `sectionZMid` | z = 1.5; 8391.82 mm²; 1 loop; 2 holes | area ±2% | stated | Sheet; image title 8393.50. |
| faces x = ±50 | area 272.86 mm²; centre (0.53, 1.5) | area ±2%; plane ±0.05 | stated | (y = −45..47) × 3 − π·1². |
| faces x = ±45 | area 3.14 mm²; centre (42, 1.5) | area ±5%; plane ±0.15 | stated | Blind ends of the Ø2 bores, π·1². |
| face y = −50 | area 270 mm² | ±1% | stated | (100 − 2·5) × 3. |
| face y = 50 | area 282 mm² | ±1% | stated | (100 − 2·3) × 3; pins take 3 mm each side. |
| faces z = 0, 3 | area 8331.1 mm²; centres (0, −4.93/−4.94) | ±2% | stated | Sheet. |
| chamfer planes | area 21.21 mm² | ±2%; 0.5° | stated | 5√2 × 3. |
| cylinders | Ø5 hole; two Ø2 holes; two Ø6 pins | axis/radius as spec | stated | Sheet rows, with the Ø2 row split into two 5 mm bores. |
| `blockout` | 28800..30600 mm³ | band | derived | Envelope box 100×100×3 = 30000; ±4% / +2%. Pins are flush with z = 3, so the blockout is the plate envelope. |

Thickness edit: ΔV ≈ plan area of the through-profile × ΔT. With a 35×14 ellipse, two chamfers, two R3 corners and the Ø5 hole, that area is about 8412 mm²; edge bores do not scale with T. Hole-diameter edit holds every other parameter fixed: ΔV = −π((2.5+0.5)²−2.5²)·3.

## 6. Defaults retained

No template geometry remains. No parameter uses an inferred or defaulted nominal.

| setting | value | reason |
|---|---|---|
| schema_version / release_status | 1 / reconstruction | Held-out CAD reconstruction; no production release. |
| Units | mm, deg | Sheet and plot axes. |
| Material, density, process | null | Unspecified; no mass claim. |
| Stated-parameter digital tolerance | 0.05 mm (0.3 mm on section-region heights) | Sheet values look rounded to 0.01–0.5 mm. |
| Measured slot tolerances | 1.0 mm on `slotRx`, 0.5 mm on `slotCentreX` | Grid / line-width uncertainty at 11.31 px/mm. |
| Envelope / bbox / face plane | 0.05 mm | Seed absolute allowance. |
| Volume band | relative 0.01 | Covers sheet vs analytic ellipse (~0.07%) and section-title scatter. |
| Surface / busy section areas | relative 0.02 | Slot size is measured. |
| COM | 0.5 mm | Slot y is derived; a 1 mm slot shift moves COM y by ~0.09 mm. |
| Blockout | 28800–30600 mm³ | Envelope 30000 mm³, a few percent wide; pins do not add height. |
| Export agreement | 0.002 | Schema default. |
| `acceptance.deviation` | null | No reference mesh in the bundle. |
| Face mode | explicit `one` on every face | Each level has count 1; centres still recorded from the sheet. |
| Feature optionality | all required | Every listed cut is functional. |

## 7. Unrepresentable or low-confidence features

The slot is modelled as a true ellipse because `top.png` and `section-z1.5.png` show a continuously curved outline (not a stadium with straight sides). That choice is a measurement, not a quoted callout; a different oval of the same bounding box would still pass the wide slot tolerances but would move volume and COM.

The dimension sheet's single Ø2 cylinder of length 100 mm contradicts the z = 1.5 drawing and the x = ±45 circular faces. The contract splits that row into two 5 mm blind bores (`countHole2` expected 2). If the evaluator extracts coaxial holes as one cylinder, counts may disagree.

Sheet face count is 18 (10 planar). The contract names all 10 planar levels plus the two chamfers. Curved faces (hole walls, pin walls, slot wall) are not separately named; they are pinned by cylinders and the slot void probes. Whether the slot wall is one elliptical face or several splits is unknown.

No fillet, draft or tool radius is specified on the slot or hole rims; none is introduced. Image titles for section areas differ from the sheet in the second decimal to about 1.7 mm² (z = 1.5); the sheet values are the acceptance targets.

Open questions, identical to the contract:

- The dimension sheet lists one Ø2 hole of length 100 mm (extent x = -50..50), but section-z1.5.png shows only two ~5 mm edge notches and the x = ±45 faces of area π confirm blind ends. Are the two short bores the intended geometry (contract assumption), or is the sheet's single through-cylinder correct?
- The through-slot is an ellipse in the top and z = 1.5 views (continuously curved, tips on x = ±35). No document names the conic. Is it a true ellipse, a stadium (straight sides plus semicircles), or another oval? Semi-axes 35 × 14 mm are measured/derived, not quoted.
- Sheet volume 25187.47 mm³ and z = 1.5 area 8391.82 mm² differ by a few tenths of a percent from the image titles (8393.50 mm²) and from an analytic 35×14 ellipse (~25205 mm³). Which figure is the reconstruction target if they disagree?
- What material, density and manufacturing process apply? None is stated; all remain null and no mass is claimed.
- The sheet reports 18 faces (10 planar). Eight non-planar faces are not itemised beyond the four cylinders (five if the two edge bores are separate) and the slot wall. Are there additional blends or splits on the slot?

No model has been built on this turn; engine measurements remain unverified.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-50.0, -50.0, 0.0] → [50.0, 50.0, 3.0] | 29999.999999999993 | pass | 2026-09-19T06:08:44Z: within envelope and band |
