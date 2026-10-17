# nist-am-test-artifact — design brief

## 1. Intent and configuration

Reconstruct the NIST Additive Manufacturing Test Artifact (Moylan et al. 2014, Fig. 8) as editable, parameterized KCL from the attached drawing, paper excerpts, renders, section drawings and dimension sheet. Frame: origin at the centre of the top surface, z = 0 on the top surface with +z toward the pin tips (the base extends to z = -10, features to z = +7), the Ø10 centre hole on the z axis, +x toward the Ø4 hole at x = +60; the four rows of Ø4 pins (20, 30, 40, 50) and the four Ø4 holes (60) lie on the +-x and +-y axes; the diamond base is a 100 mm square rotated 45 deg (corners on the axes at 70.71). Model every feature at its stated size and position: centre hole and two concentric central cylinders, 16 pins and 4 holes, both L-shaped staircases with 1 mm steps and 10 mm treads, the 1-in-25 ramp with 2.5 mm landings, the lateral cavities and bosses on one side, the five fine pins and five fine holes (Ø2 to Ø0.25, 2 mm tall/deep) and the fine rectangular bosses and slots. Small features are scored individually: a correct base cannot compensate for a missing pin. One solid; export STEP and STL. The reference CAD is evaluator-only; the deliverable must be construction, never an import.

This is a reconstruction contract and construction plan, not an executed CAD model. The later deliverable is native editable KCL 2 in mm with literal top-level contract parameters, sanity assertions, one solid, and STEP plus STL exports. Reference geometry must never be imported. No KCL is included in this bundle. The exact paper excerpt, drawing and supplied dimension sheet take precedence over raster edge estimates.

The contract has 64 parameters: 49 stated, 3 derived, 9 measured, 3 inferred. Its 79 mandatory feature records include all 35 cylindrical features, all ten treads and all twenty fine rectangles. No geometric feature is marked optional.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/bottom.png | image | authoritative | ceb5cdd1206fb513dce32d2ad6a0cb9726362b0504ac337b413cfe832d80194e | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/dimension-sheet.md | table | authoritative | d1b8dbd3cd46b0d46b810689e5733a61618acb6adecb7db69d85bfba65bd7e8f | Supplied evaluator-prepared rounded measurements, quoted as document evidence; no evaluator CAD access. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/drawing-01.png | drawing | authoritative | 3182a3cc45c1744cd958d468f37e86a19659dd9fe65b72d5443a45663766460d | Fig.8 first page: layout, A-A lateral features, B-B stations, C-C ramp, D-D fine sizes; xx are unspecified GD&T. Units: mm. Revision: Supplied bundle revision identified by SHA-256; NIST Fig.8 (2014) |
| sources/drawing-02.png | drawing | authoritative | bded7754aafa4bd02d41c7c6a3cf2d44564dd776a3849b4631550a78b7966266 | Fig.8 second page: E-E fine rectangle ordinates and F-F/G-G tread levels. Units: mm. Revision: Supplied bundle revision identified by SHA-256; NIST Fig.8 (2014) |
| sources/front.png | image | authoritative | 038b4d1d2f98a39efa54b4510737a981040f10f2e785d9e775170385f9394f44 | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/iso-below.png | image | illustrative | f126217d09341105dbfda7789291939dbb44303e425fd545fb07ef767a67cdec | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/iso.png | image | illustrative | fd1a1925f86e9141c26bcb4ae3fc7db93f5b06ffabafba854b6b8f2fe5d62b14 | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/iso2.png | image | illustrative | ad5fc1ef468fa300e27cc9779d73aef3bac447c0e7675d43c47b421cc238bcd9 | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/nist-am-artifact-description.md | text | authoritative | 1e10b2e09e840f8749668fd84c61cd15e4aed51dbb5f362ae3df49ad7e8a94e0 | Published excerpts and explicit reconstruction frame; geometric requirements. Units: mm. Revision: Supplied bundle revision identified by SHA-256; NIST Fig.8 (2014) |
| sources/render-notes.md | text | illustrative | 7b26cf394c9cc12942de018502fe780bb9fc3f296dd18e2036bd2430cfc828ef | Render mesh has 9536 triangles; confirms units, envelope and file list. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/right.png | image | authoritative | cc85285ba084e23beab536aaf406127648712889281f4b3c6ce3500c5061a329 | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/section-x0.png | image | authoritative | 42907681cc27f37d3ec993270ba52a02512bcfcd1c50379ff8c1e5a82f6b4ab0 | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/section-y0.png | image | authoritative | ce3ec33a6f3d6e2e3e4acd471ef9e44789bb65a828ec22dae405ea7128544fc1 | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/section-z-1.png | image | authoritative | c6ff32ad0cc2ac247168af91278b9e4795740f179ee286f6e2dad39f3c6738fe | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/section-z-5.png | image | authoritative | 8fb3dcded9d28b5ad432ef6f8318fd16142b9cc0132481030d1f6a4978c048da | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/section-z1.png | image | authoritative | a28c0e6ed943fc71a5316b535257f83a7b5bc6106dc44fef5697ac28961ae749 | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/section-z5.png | image | authoritative | 5f955f4a0a805278d61e7d006633a1145b08819cd6f1aa6f835ed2150a46bb45 | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |
| sources/top.png | image | authoritative | dca24515a54a5c2508e3047778d7fe087437fa4aaf305b9ec5af65a189df5713 | Orthographic visual evidence; use the mm grid for position and topology, with mesh/line-width uncertainty. Units: mm. Revision: Supplied bundle revision identified by SHA-256 |

All 18 supplied files are registered with their complete SHA-256. No reference mesh, profile.json or reference.json was supplied. Values quoted from dimension-sheet.md use stated provenance because they are supplied document statements; they are not measurements performed by this worker. Its underlying measurements are explicitly labelled as evaluator measurements. No hidden reference CAD or scorer files were read.

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Frame | Top-centre origin; +x to (60,0), +y to (0,60), +z to tips | mm | sources/nist-am-artifact-description.md datum frame | 0.03 digital | stated |
| Diamond blank | 100 square rotated 45; z=-10..0 | mm,deg | sources/nist-am-artifact-description.md; B-B | 0.01 size;0.02 angle | stated |
| Envelope | [141.4213562373095,141.4213562373095,17] | mm | sources/dimension-sheet.md envelope | 0.03 | derived/corroborated |
| Centre bore and bosses | Ø10 through; Ø20 height 4; Ø15 added height 3 | mm | sources/dimension-sheet.md cylinders | 0.005 radius;0.02 axis/length | stated |
| Main pin rows | 16×Ø4×7 at radii 20,30,40,50 on ±x/±y | mm | sources/nist-am-artifact-description.md §7.3; B-B | individual cylinders and caps | stated |
| Main through holes | 4×Ø4 at radius 60 on ±x/±y | mm | sources/nist-am-artifact-description.md §7.3; B-B | individual cylinders | stated |
| Staircases | Five 10×10 treads each; levels 3,5,7,6,4 along the L; negative mirrored in y | mm | sources/drawing-02.png F-F/G-G; sources/dimension-sheet.md | individual faces,0.03–0.05 | stated |
| Ramp | Width 5; r15..45;25 run, 1 rise,2.5 landings; end heights2 and1 | mm | sources/nist-am-artifact-description.md §7.7; C-C; sheet planes | width/start ±0.3 mm from pixels; plane ±0.03 | mixed evidence |
| Lateral profiles | Eight blind cavities, stations 40,30,20,10,0,-10,-20,-30; z=-5 | mm | sources/drawing-01.png A-A; sheet; section-z-5.png | pixel dimensions ±0.3; named exact planes | interpretation/Q2–Q3 |
| Fine circular features | Five pins and five holes: Ø2,1.5,1,0.5,0.25; height/depth 2 | mm | sources/drawing-01.png D-D; sources/dimension-sheet.md | radius ±0.005;axis ±0.015 | stated |
| Fine rectangles | Ten bosses and ten slots; two per width 2,1.5,1,0.5,0.25; lengths 3×width | mm | sources/drawing-02.png E-E; sheet cap/floor areas | per-face area1%;centroid0.025 | stated/inferred ratio |
| Cylinder inventory | 35=1 centre+2 central bosses+16 pins+4 base holes+10 fine circles+2 lateral holes | count | sources/dimension-sheet.md full cylinder table | exact presence per item | summary count conflict/Q1 |
| Connectivity and exports | One connected solid; native KCL; STEP and STL |  | User intent; sources/dimension-sheet.md | solid count exact; export volume0.2% | required |
| GD&T and manufacturing | xx boxes; material/density/process unspecified |  | sources/drawing-01.png and sources/drawing-02.png | not manufacturing tolerances | open/Q5 |

The 1 mm staircase increment describes the sorted nominal levels 3,4,5,6,7. It does not imply a monotonic 3,4,5,6,7 traversal along an L: the source face locations require 3,5,7 along the x arm and 7,6,4 along the y arm. Each positive tread is checked separately, as is each negative floor.

## 4. Coordinate frame, scale, and measurement method

Intersection of the Ø10 centre-hole axis with datum A, the original flat top surface of the diamond base. This point is [0,0,0], even though the hole removes material there.

- +x: In datum A, from the centre-hole axis toward the right-hand Ø4 through hole at [60,0,0] in top.png.
- +y: In datum A, toward the Ø4 through hole at [0,60,0], upward in top.png; x cross y gives +z.
- +z: Normal to datum A toward the pin tips; top surface z=0, base bottom z=-10, tallest original features z=7.

Datum A is the unraised top, B is the centre-bore axis, and C is the right-hand base-hole axis as specified by the paper excerpts. The minimum bounding-box corner is [-70.710678,-70.710678,-10]; it is not the modelling origin. The sheet wording about a bounding-box origin offset is interpreted through its explicit signed coordinates and the user-specified frame. Dimensions here preserve that native frame.

Use diagonal coordinates u=(x+y)/sqrt(2), v=(x-y)/sqrt(2). For fine features, u points toward the NE edge and v toward +x,-y. Fine round pins lie at u=35, v=5,10,15,20,25; holes use the negative v stations. The literal rounded first-axis parameters give an equivalent grid within 0.001 mm. Fine rectangles end at u=49. The ramp uses u=0 and r=v from 15 to 45. On the NW side use t=u and q=v: the outer face is q=-50 and positive q points into the base. Convert with x=(t+q)/sqrt(2), y=(t-q)/sqrt(2). Profiles are in (t,z); do not reinterpret this pair of scalar diagonals as a right-handed 3D frame.

Pixel coordinates below refer to the original source files, with (0,0) at the upper-left, and are approximate readings of line centres rather than anti-aliased edges. Each view is scaled independently; the drawing sheets do not use one universal pixels/mm scale.

| source | pixel evidence | scale / interpretation |
|---|---|---|
| top.png / bottom.png,1800×1800 | Origin≈(954,882); ±80 mm grid borders≈x180,1728 and y108,1656; diamond tips≈(270,882),(1638,882),(954,198),(954,1566). | 1548px/160mm=9.675px/mm; coordinates x=(px-954)/9.675,y=(882-py)/9.675. Corner radius≈70.71, not100. |
| top.png | Axis-hole centres≈(373.5,882),(1534.5,882),(954,301.5),(954,1462.5); central opening diameter≈96.8px; main pin/hole diameters≈38.7px. | Centres at±60; boreØ10; rows visibly have four pins per arm at 20, 30, 40, 50. Exact sizes/stations come from text and table. |
| top.png | Raised L footprint x≈548..838,y≈476..766; negative L uses same x and y≈998..1288; individual tread edges differ by≈96.8px. | Extents x=-42..-12,y=12..42 and reflected negative y; tread 10. Face table supplies exact elevations. |
| top.png / section-z1.png | Ramp end centres≈(1057,985),(1262,1190) in top.png; perpendicular width≈48.4px; length≈290px. | Width5±0.3,radius15..45. C-C fixes25 run plus2.5+2.5 landings; sheet landing areas12.5 corroborate width5. |
| drawing-01.png,1870×2420,A-A | Side outline≈x330..964,y1300..1364; eight opening centres≈394,458,521,584,647,710,774,837 at y1331. | Use side100mm and thickness10mm:≈6.34px/mm horizontally and6.4px/mm vertically. Stations descend40..-30; pitch10±0.3. |
| drawing-01.png,A-A | Small diamond≈19px across/high; large diamond/tall rhombus≈38px high; wide rhombus≈26px high. Square width/height callouts3 and6; circle calloutsØ3 depth3,Ø6 depth5; rhombus angle labels60°. | Measured diagonals3,6; rhombus heights6,4 with±0.3mm uncertainty. The table confirms large back areas18,10.39,13.86 and planar normals. |
| drawing-02.png,1870×2420,E-E | Read the printed positive edges2,4,6,8,11,12.5,14,15.5,17.5,18.5,19.5,20.5,22,22.5,23,23.5,24.5,24.75,25,25.25; negative half mirrors them. | Ten intervals on each side of the zero line; two per width. These are stated dimensions, not measurements of tiny raster teeth. |
| drawing-02.png,F-F/G-G | Printed level labels3,4,5,6,7, with the central highest/deepest level7. | Read labels and use the table centroids to assign the five levels; do not infer levels from isometric shading. |
| section-x0.png / section-y0.png,1800×434 | z=0≈y199; base bottom≈y290; pin caps≈y136. About90px between10mm ticks. Four material regions, including the two corner remnants. | ≈9px/mm; base10, pin7, total17. Table gives area1513.21 and4 outer loops. |
| section-z-1.png | One diamond region, one L pocket, four axial holes, centre bore, five fine holes and ten fine rectangular slots. | 21 inner loops. Image area9320.10 differs slightly from analytic/table9319.88 because the render uses a 9536-triangle mesh. |
| section-z-5.png / iso2.png | Eight NW-side notches/openings are visible; no feature extends outside the diamond side. Small-third notch terminates near q=-47; large notches near q=-45. | Supports blind-cavity interpretation and small diamond depth3±0.3. Exact-face section area/loops are not portable: see Q4. |
| section-z1.png / section-z5.png | Upper slice shows individual fine features; higher slice shows16 main pins, centre annulus and remaining stair. Cap-coincident loop counts differ from the table. | Use offset analytic slices and individual caps/cylinders. A 0.25 mm width is only≈2.4px in top.png, so fine sizes are never estimated from raster width. |
| front.png / right.png / iso.png / iso-below.png | Orthographic profiles agree with z=-10..7; underside has exactly five through openings; iso views confirm the staircase/ramp arrangement. | Orientation and topology cross-checks only; no dimensions taken from perspective-looking shaded edges. |

Digital tolerances are comparison thresholds. Stated dimensions generally use 0.01 mm, fine diameters 0.005 mm, rounded table axes 0.015–0.02mm, and raster dimensions 0.3 mm. The nearest probe to an uncertain wall is farther than that wall uncertainty: the small-diamond axis probe has at least 1.06 mm lateral clearance; its back probe is 0.6 mm behind the bottom; fine rectangle centres have at least 0.375 mm radial clearance versus at most 0.2375 mm combined inset/aspect uncertainty, and radial outside probes are 0.4 mm clear. Fine circular centres are at least 0.125 mm from their stated walls. No probe is placed on a surface.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| baseSide | 100 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md; datum frame: "100 mm square"; Edge length before rotating about z. |
| baseRotation | 45 deg | 0.02 deg | stated | sources/nist-am-artifact-description.md; datum frame: "rotated 45 deg about z"; Diamond rotation; all diagonal directions use this angle. |
| baseThickness | 10 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.1; sources/drawing-01.png B-B: 10; Top is fixed at z=0; edit moves the bottom and extends only through holes. |
| baseHalfDiagonal | 70.710678119 mm | 0.02 mm | derived | baseSide / sqrt(2); Corner distance along each global axis. |
| mainPinDiameter | 4 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.3: "sixteen Ø4 pins"; All sixteen axis-row pins. |
| mainPinHeight | 7 mm | 0.01 mm | stated | sources/drawing-01.png B-B: 7; sources/dimension-sheet.md cylindrical features: 0 .. 7; Independent pin height; changing this does not move the stair treads or central bosses. |
| pinFirstRadius | 20 mm | 0.01 mm | stated | sources/drawing-01.png B-B: 20; sources/nist-am-artifact-description.md §7.3; Innermost pin centre on each signed axis. |
| pinPitch | 10 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.3: "20, 30, 40 and 50 mm"; Uniform axis-row pitch. |
| pinsPerArm | 4  | 0.01  | stated | sources/nist-am-artifact-description.md §7.3: four stated stations per signed axis |
| mainHoleDiameter | 4 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.3: "four Ø4 holes"; Through the base. |
| mainHoleRadius | 60 mm | 0.01 mm | stated | sources/drawing-01.png B-B: 60; sources/nist-am-artifact-description.md §7.3; Radial position on each signed axis. |
| centerHoleDiameter | 10 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.2: "Ø10 through hole"; Single uninterrupted bore through the base and both central bosses. |
| lowerBossDiameter | 20 mm | 0.01 mm | stated | sources/dimension-sheet.md cylindrical features: pin diameter 20, extent 0 .. 4 |
| lowerBossHeight | 4 mm | 0.01 mm | stated | sources/dimension-sheet.md cylindrical features: pin diameter 20, length 4 |
| upperBossDiameter | 15 mm | 0.01 mm | stated | sources/dimension-sheet.md cylindrical features: pin diameter 15, extent 4 .. 7 |
| upperBossHeight | 3 mm | 0.01 mm | stated | sources/dimension-sheet.md cylindrical features: pin diameter 15, length 3; Added above lowerBossHeight; upper cap is at z=7. |
| stairInnerOffset | 12 mm | 0.01 mm | stated | sources/dimension-sheet.md axis-aligned faces: x=-12, y=±12; Nearest edges of both L footprints to the coordinate axes. |
| stairTread | 10 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.4: "10 mm squares"; Width and length of each of the five treads in each staircase. |
| stairFirstHeight | 3 mm | 0.01 mm | stated | sources/drawing-02.png F-F and G-G: 3, 4, 5, 6, 7; Smallest absolute level; negative stair has the same depths. |
| stairIncrement | 1 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.4: "distance between steps (1 mm)"; Increment between the five nominal levels, not a monotonic walk along the L. |
| rampLowHeight | 1 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.7; sources/drawing-01.png C-C: 1 at the low landing |
| rampRise | 1 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.7: "1 mm rise over a 25 mm run"; Low landing stays fixed. High landing rises with this parameter. |
| rampRun | 25 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.7; sources/drawing-01.png C-C: 25; Horizontal length of the inclined portion, measured along (1,-1,0)/sqrt(2). |
| rampLanding | 2.5 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.7; sources/drawing-01.png C-C: 2.50 at both ends |
| rampWidth | 5 mm | 0.3 mm | measured | sources/top.png; sources/section-z1.png; sources/dimension-sheet.md z=1 and z=2 landing areas 12.5; Perpendicular width; 48.4 px at 9.675 px/mm; independently 12.5/2.5=5. |
| rampStartRadius | 15 mm | 0.3 mm | measured | sources/top.png; sources/dimension-sheet.md high-end plane centroid [10.607,-10.607,1]; High end nearest the centre; radial coordinate r=(x-y)/sqrt(2). End radius is 45. |
| fineHeightDepth | 2 mm | 0.01 mm | stated | sources/nist-am-artifact-description.md §7.9: "All features are 2 mm tall or deep"; sources/drawing-01.png D-D; sources/drawing-02.png E-E |
| fineSizeA | 2 mm | 0.005 mm | stated | sources/drawing-01.png D-D diameter/width labels; sources/drawing-02.png E-E; Round diameter and corresponding rectangular width. |
| fineSizeB | 1.5 mm | 0.005 mm | stated | sources/drawing-01.png D-D diameter/width labels; sources/drawing-02.png E-E; Round diameter and corresponding rectangular width. |
| fineSizeC | 1 mm | 0.005 mm | stated | sources/drawing-01.png D-D diameter/width labels; sources/drawing-02.png E-E; Round diameter and corresponding rectangular width. |
| fineSizeD | 0.5 mm | 0.005 mm | stated | sources/drawing-01.png D-D diameter/width labels; sources/drawing-02.png E-E; Round diameter and corresponding rectangular width. |
| fineSizeE | 0.25 mm | 0.005 mm | stated | sources/drawing-01.png D-D diameter/width labels; sources/drawing-02.png E-E; Round diameter and corresponding rectangular width. |
| fineFirstX | 28.284 mm | 0.005 mm | stated | sources/dimension-sheet.md cylindrical features: Ø2 pin axis [28.284,21.213,0]; Fine pin A x coordinate; fine hole A is the reflected point. |
| fineFirstY | 21.213 mm | 0.005 mm | stated | sources/dimension-sheet.md cylindrical features: Ø2 pin axis [28.284,21.213,0]; Fine pin A y coordinate. |
| finePitch | 5 mm | 0.05 mm | inferred | Successive stated axes differ by approximately (3.536,-3.535) mm. Their distances round to 5 mm; one pitch preserves the straight row without treating table rounding as irregular spacing.; Centre pitch along (1,-1,0)/sqrt(2); holes are reflected across x=y. |
| rectOuterInset | 1 mm | 0.05 mm | inferred | Transform the stated cap/floor centroids to u=(x+y)/sqrt(2) and add half the length inferred from area/width. All twenty ends give u=49 within 0.01 mm, hence 50-49=1 mm.; Distance of every fine rectangle outer end from the NE side plane u=baseSide/2. |
| rectLengthRatio | 3  | 0.05  | inferred | Supplied individual face areas 12, 6.75, 3, 0.75 and 0.19 mm2 (rounded) divided by the stated widths squared imply a common ratio of 3. The smallest exact nominal area is then 0.1875 mm2. Section outlines corroborate 3:1 rectangles.; Rectangular length divided by width. |
| rectStartV1 | 2 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 2; Inner signed-v edge of boss 1; the matching slot reflects v to -v. |
| rectStartV2 | 6 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 6; Inner signed-v edge of boss 2; the matching slot reflects v to -v. |
| rectStartV3 | 11 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 11; Inner signed-v edge of boss 3; the matching slot reflects v to -v. |
| rectStartV4 | 14 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 14; Inner signed-v edge of boss 4; the matching slot reflects v to -v. |
| rectStartV5 | 17.5 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 17.5; Inner signed-v edge of boss 5; the matching slot reflects v to -v. |
| rectStartV6 | 19.5 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 19.5; Inner signed-v edge of boss 6; the matching slot reflects v to -v. |
| rectStartV7 | 22 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 22; Inner signed-v edge of boss 7; the matching slot reflects v to -v. |
| rectStartV8 | 23 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 23; Inner signed-v edge of boss 8; the matching slot reflects v to -v. |
| rectStartV9 | 24.5 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 24.5; Inner signed-v edge of boss 9; the matching slot reflects v to -v. |
| rectStartV10 | 25 mm | 0.01 mm | stated | sources/drawing-02.png E-E: positive ordinate 25; Inner signed-v edge of boss 10; the matching slot reflects v to -v. |
| lateralCenterZ | -5 mm | 0.01 mm | stated | sources/dimension-sheet.md cylindrical feature axes and inclined-plane centroids at z=-5; Fixed relative to datum A, including during the base-thickness edit. |
| lateralFirstStation | 40 mm | 0.3 mm | measured | sources/drawing-01.png A-A: first centre x≈394 px, edge x≈330 px, opposite edge x≈964 px; sources/dimension-sheet.md Ø3 axis point [28.284,28.284,-5]; Side coordinate t=(x+y)/sqrt(2); first centre is 10 mm from the +y corner. |
| lateralPitch | 10 mm | 0.3 mm | measured | sources/drawing-01.png A-A: eight centres ≈394,458,521,584,647,710,774,837 px; sources/dimension-sheet.md located side axes/centroids; Successive feature stations decrease t by 10 mm. |
| lateralSmallDiameter | 3 mm | 0.01 mm | stated | sources/drawing-01.png A-A: Ø3 depth 3 |
| lateralSmallDepth | 3 mm | 0.01 mm | stated | sources/drawing-01.png A-A: Ø3 depth 3; sources/dimension-sheet.md square roof/floor area 9 and width 3; Depth for the small round and square cavities. |
| lateralLargeDiameter | 6 mm | 0.01 mm | stated | sources/drawing-01.png A-A: Ø6 depth 5 |
| lateralLargeDepth | 5 mm | 0.01 mm | stated | sources/drawing-01.png A-A: Ø6 depth 5; sources/dimension-sheet.md large polygon backs at q=-45 and mouths at q=-50; Depth for the large round, square, diamond and two rhombi. |
| lateralSmallSquare | 3 mm | 0.01 mm | stated | sources/drawing-01.png A-A: square width and height 3 |
| lateralLargeSquare | 6 mm | 0.01 mm | stated | sources/drawing-01.png A-A: square width and height 6 |
| lateralSmallDiamond | 3 mm | 0.3 mm | measured | sources/drawing-01.png A-A: small diamond around (521,1331) px, ≈19 px diagonals at 6.34 px/mm; Equal horizontal and vertical diagonals; straight edges. |
| lateralSmallDiamondDepth | 3 mm | 0.3 mm | measured | sources/section-z-5.png: third lateral notch reaches q≈-47; sources/drawing-01.png A-A small-feature group; Depth of the small diamond; source does not explicitly label it. |
| lateralLargeDiamond | 6 mm | 0.3 mm | measured | sources/drawing-01.png A-A: large diamond around (710,1331) px, ≈38 px diagonals; sources/dimension-sheet.md back area 18 and 45-degree wall normals; Equal horizontal and vertical diagonals. |
| lateralTallHeight | 6 mm | 0.3 mm | measured | sources/drawing-01.png A-A: tall rhombus around (774,1331) px, ≈38 px high; sources/dimension-sheet.md wall vertices z=-8 and z=-2; Tall rhombus vertical diagonal. |
| lateralWideHeight | 4 mm | 0.3 mm | measured | sources/drawing-01.png A-A: wide rhombus around (837,1331) px, ≈26 px high; sources/dimension-sheet.md wall vertices z=-7 and z=-3; Wide rhombus vertical diagonal; edges are planar, not arcs. |
| lateralApexAngle | 60 deg | 0.1 deg | stated | sources/drawing-01.png A-A: 60.000° labels at the tall and wide rhombi; Acute included angle; tall profile has its acute tips along z, wide profile along t. |
| lateralTallWidth | 3.464101615 mm | 0.3 mm | derived | lateralTallHeight * tan(lateralApexAngle / 2); Tall rhombus horizontal diagonal. |
| lateralWideWidth | 6.92820323 mm | 0.3 mm | derived | lateralWideHeight / tan(lateralApexAngle / 2); Wide rhombus horizontal diagonal. |

**Construction tables and formulas.** Build the base at z=-baseThickness..0. Drill the centre through the combined base/boss height and the four main holes through the full thickness. Attach all positive features to the top datum; subtract all negative features from it. Preserve the datum when thickness changes. Use table-driven patterns for rows, with a separate body operation for each nominal feature; do not omit the small0.25mm members. Derived parameter formulas document the baseline; do not lock independent inputs together with equality assertions.

| tread | centre (x,y) | height/depth | footprint |
|---|---|---|---|
| outerX | [-37,17] | +3; mirrored y gives -3 | 10×10, centred at stated point |
| middleX | [-27,17] | +5; mirrored y gives -5 | 10×10, centred at stated point |
| elbow | [-17,17] | +7; mirrored y gives -7 | 10×10, centred at stated point |
| middleY | [-17,27] | +6; mirrored y gives -6 | 10×10, centred at stated point |
| outerY | [-17,37] | +4; mirrored y gives -4 | 10×10, centred at stated point |

Each rectangular boss i occupies u=[49-3*w,49], v=[rectStartVi,rectStartVi+w], z=[0,2]. The slot reflects v to negative and uses z=[-2,0]. The ten intervals and width assignments are explicit:

| index | width | length | positive v interval | negative v interval |
|---|---|---|---|---|
| 1 | 2 | 6 | [2,4] | [-4,-2] |
| 2 | 2 | 6 | [6,8] | [-8,-6] |
| 3 | 1.5 | 4.5 | [11,12.5] | [-12.5,-11] |
| 4 | 1.5 | 4.5 | [14,15.5] | [-15.5,-14] |
| 5 | 1 | 3 | [17.5,18.5] | [-18.5,-17.5] |
| 6 | 1 | 3 | [19.5,20.5] | [-20.5,-19.5] |
| 7 | 0.5 | 1.5 | [22,22.5] | [-22.5,-22] |
| 8 | 0.5 | 1.5 | [23,23.5] | [-23.5,-23] |
| 9 | 0.25 | 0.75 | [24.5,24.75] | [-24.75,-24.5] |
| 10 | 0.25 | 0.75 | [25,25.25] | [-25.25,-25] |

Lateral profiles are extruded inward from q=-50. In the following table T=t-station and Z=z+5. Square vertices are (±size/2,±size/2); diamond/rhombus vertices are (0,±H/2),(±W/2,0), with straight edges. All eight are blind voids in the baseline interpretation.

| lateral feature | t station | profile in (T,Z) | depth | profile area |
|---|---|---|---|---|
| smallRound | 40 | circleR1.5 | 3 | 7.068583471 |
| smallSquare | 30 | square3×3 | 3 | 9 |
| smallDiamond | 20 | diamond W=H=3 | 3 | 4.5 |
| largeRound | 10 | circleR3 | 5 | 28.274333882 |
| largeSquare | 0 | square6×6 | 5 | 36 |
| largeDiamond | -10 | diamond W=H=6 | 5 | 18 |
| tallRhombus | -20 | rhombus H6,W=6*tan30° | 5 | 10.392304845 |
| wideRhombus | -30 | rhombus H4,W=4/tan30° | 5 | 13.856406461 |

**Analytic acceptance quantities.** Athrough=π/4*(10²+4*4²)=128.805298797mm². Fine area per sign is π/4*Σ[2,1.5,1,0.5,0.25]² + 2*3*Σ[2,1.5,1,0.5,0.25]²=51.314573611mm². Each staircase has volume 100*(3+4+5+6+7)=2500mm³. Positive/negative stairs and fine sets cancel in the volume sum only; their independent probes forbid omission.

Analytic signed primitives: baseSide^2*baseThickness - pi/4*(centerHoleDiameter^2+4*mainHoleDiameter^2)*baseThickness + 16*pi*mainPinDiameter^2*mainPinHeight/4 + pi/4*(lowerBossDiameter^2-centerHoleDiameter^2)*lowerBossHeight + pi/4*(upperBossDiameter^2-centerHoleDiameter^2)*upperBossHeight + rampWidth*(rampRun/2+rampLanding)*(2*rampLowHeight+rampRise) - sum(lateral profile area*depth). The equal positive/negative stairs and fine-feature volumes cancel algebraically, but every member remains individually mandatory. Lateral subtraction=594.320976353 mm3. Independent supplied table value=100987.06 mm3.

2*baseSide^2 + 4*baseSide*baseThickness - 2*Athrough + pi*(centerHoleDiameter+4*mainHoleDiameter)*baseThickness + 16*pi*mainPinDiameter*mainPinHeight + pi*(lowerBossDiameter*lowerBossHeight+upperBossDiameter*upperBossHeight+centerHoleDiameter*(lowerBossHeight+upperBossHeight)) + 2*640 + rampExcessArea + fineWallArea + lateralWallArea. Athrough=pi/4*(centerHoleDiameter^2+4*mainHoleDiameter^2); rampExcessArea=105.099960032; fineWallArea=401.973445725; lateralWallArea=538.112803658 mm2. The attached sheet gives 28904.43 mm2.

Signed first moments / analytic volume. Sum V_i*[cx_i,cy_i,cz_i], subtract cavities; use centre z=h/2 for additions and z=-d/2 for top pockets. Base centroid [0,0,-baseThickness/2]. Side cavity centroid xyz(t,-baseSide/2+depth/2,lateralCenterZ). Ramp volume 225 and centroid [19.854641796,-19.854641796,0.787037037] from integrating r*h(r), h(r)^2/2. Net moments [26383.551236997,87572.096143311,-468274.931965609] mm4. Rounded table COM [0.261,0.867,-4.637].

The ramp height is2 on r15..17.5, 2-(r-17.5)/25 on r17.5..42.5, and1 on r42.5..45. Integrate width*h(r) for volume, width*r*h(r) for the radial first moment and width*h(r)²/2 for the z first moment. The two staircase vertical wall areas are 640 mm² each. Fine walls sum 65.973445725 mm² from the ten circles and 336 mm² from the twenty rectangles. Lateral wall area isΣ(perimeter*depth)=538.112803658mm²; each removed mouth area is replaced by its equal blind back area. This gives an independent analytic surface area without importing geometry.

| acceptance value | expected | tolerance | provenance / formula / evidence |
|---|---|---|---|
| bbox.min | [-70.71067811865474,-70.71067811865474,-10] | 0.03mm | [-baseSide/sqrt(2),-baseSide/sqrt(2),-baseThickness] |
| bbox.max | [70.71067811865474,70.71067811865474,7] | 0.03mm | [baseSide/sqrt(2),baseSide/sqrt(2),max feature level] |
| volume | 100987.061651834 | 0.05% | Signed primitive formula above; sheet100987.06; difference 0.001651834mm³. |
| surface_area | 28904.433778012 | 0.1% | Exposed boundary formula above; sheet28904.43; difference 0.003778012mm². |
| center_of_mass | [0.2612567472054772,0.8671615423887392,-4.636979473470043] | 0.02mm per axis | Signed moments above; sheet[0.261,0.867,-4.637]; all rounding differences<0.001mm. |
| solid_count | 1 | exact | User requirement and supplied sheet. Section islands do not change final solid count. |
| blockout.volume_min | 100768.9 | lower bound | Envelope-only primary solids that reach the envelope extremes: unperforated 100×100×10 diamond prism (100000 mm³) plus the solid Ø20×4 and Ø15×3 central boss blanks (1256.637061 + 530.143760 mm³, top at z = 7) = 101786.780822 mm³; band −1 %. |
| blockout.volume_max | 102804.6 | upper bound | Same solids, +1 %. The bare prism alone (100000 mm³, z-max 0) cannot reach bbox.max z = 7 and is outside the band on purpose. Excludes pins, stair/ramp additions and every cut. |
| export_volume_tolerance_rel | 0.002 | 0.2% | Retained STEP/STL/KCL agreement threshold; exact STEP geometry is the final geometric authority. |
| deviation | None | not applicable | No reference mesh was supplied. Do not fabricate a deviation band. |

**Sections.** Areas are solid material in mm². Loops count outer boundaries, and holes count inner boundaries separately. Non-coplanar stations avoid the supplied table/image cap-boundary conflict.

| section | plane/station | area | loops / holes | area tolerance | formula / evidence |
|---|---|---|---|---|---|
| axisX | x=0 | 1513.213562373 | 4 / 0 | 0.001 | 100*sqrt(2)*10 - 2*4*10 - 10*10 + 8*4*7 + (20-10)*4 + (15-10)*3; sources/dimension-sheet.md x=0:1513.21,4,0. |
| axisY | y=0 | 1513.213562373 | 4 / 0 | 0.001 | Same formula as axisX; sources/dimension-sheet.md y=0:1513.21,4,0. |
| belowFine | z=-1 | 9319.880127592 | 1 / 21 | 0.001 | baseSide^2 - through-hole area - 5*stairTread^2 - fine hole/slot areas; sources/dimension-sheet.md z=-1:9319.88,1,21. |
| bottomInterior | z=-8.5 | 9871.194701203 | 1 / 5 | 0.001 | baseSide^2 - through-hole area. Below every blind cavity and above z=-10. |
| positiveLow | z=0.5 | 1137.99595246 | 34 / 1 | 0.001 | 16*pi*(mainPinDiameter/2)^2 + central annulus area with outer radius 10 + 5*stairTread^2 + fine area 51.314573611 + ramp section 150; no cap lies at z=0.5. |
| rampMid | z=1.5 | 1062.99595246 | 34 / 1 | 0.001 | 16*pi*(mainPinDiameter/2)^2 + central annulus area with outer radius 10 + 5*stairTread^2 + fine area 51.314573611 + ramp section 75; no cap lies at z=1.5. |
| stepsAbove3 | z=3.5 | 836.681378849 | 18 / 1 | 0.001 | 16*pi*(mainPinDiameter/2)^2 + central annulus area with outer radius 10 + 4*stairTread^2 + fine area 0.000000000 + ramp section 0; no cap lies at z=3.5. |
| stepsAbove4 | z=4.5 | 599.236700254 | 18 / 1 | 0.001 | 16*pi*(mainPinDiameter/2)^2 + central annulus area with outer radius 7.5 + 3*stairTread^2 + fine area 0.000000000 + ramp section 0; no cap lies at z=4.5. |
| stepsAbove5 | z=5.5 | 499.236700254 | 18 / 1 | 0.001 | 16*pi*(mainPinDiameter/2)^2 + central annulus area with outer radius 7.5 + 2*stairTread^2 + fine area 0.000000000 + ramp section 0; no cap lies at z=5.5. |
| stepsAbove6 | z=6.5 | 399.236700254 | 18 / 1 | 0.001 | 16*pi*(mainPinDiameter/2)^2 + central annulus area with outer radius 7.5 + 1*stairTread^2 + fine area 0.000000000 + ramp section 0; no cap lies at z=6.5. |
| lateralAndDeepStair | z=-5.5 | 9522.71450207 | 1 / 6 | 0.001 | baseSide^2 - through-hole area - 2*stairTread^2 - sum(horizontal cavity width at z+5=-0.5 times depth). Circle width=2*sqrt(R^2-dz^2); rhombus width=W*(1-2*abs(dz)/H). Eight lateral notches join the exterior, leaving five through holes and one remaining rectangular stair pocket. |

**Named faces.** In-plane centres are(y,z) for x faces,(x,z) for y faces,and(x,y) for z faces. Every repeated cap/floor is mode=one and has an explicit centroid; no implicit area summation is used.

| face | plane / normal | centre | area | position/centre tol; area tol | formula / evidence |
|---|---|---|---|---|---|
| datumTop | z=0 / + | [2.02,-0.01] | 8181.884175132 | 0.05mm; 0.002 | sources/dimension-sheet.md z=0: area 8181.88, centroid (2.02,-0.01); analytic footprint subtraction. |
| baseBottom | z=-10 / - | [0,0] | 9871.194701203 | 0.03mm; 0.002 | baseSide^2 - pi/4*(centerHoleDiameter^2 + 4*mainHoleDiameter^2); sources/dimension-sheet.md z=-10: 9871.19 |
| lowerBossShoulder | z=4 / + | [0,0] | 137.444678595 | 0.03mm; 0.002 | pi/4*(lowerBossDiameter^2-upperBossDiameter^2); sources/dimension-sheet.md z=4 area 137.44 |
| upperBossCap | z=7 / + | [0,0] | 98.174770425 | 0.03mm; 0.002 | pi/4*(upperBossDiameter^2-centerHoleDiameter^2); sources/dimension-sheet.md z=7 area 98.17 |
| pin_px_20_cap | z=7 / + | [20,0] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_px_30_cap | z=7 / + | [30,0] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_px_40_cap | z=7 / + | [40,0] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_px_50_cap | z=7 / + | [50,0] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_nx_20_cap | z=7 / + | [-20,0] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_nx_30_cap | z=7 / + | [-30,0] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_nx_40_cap | z=7 / + | [-40,0] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_nx_50_cap | z=7 / + | [-50,0] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_py_20_cap | z=7 / + | [0,20] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_py_30_cap | z=7 / + | [0,30] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_py_40_cap | z=7 / + | [0,40] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_py_50_cap | z=7 / + | [0,50] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_ny_20_cap | z=7 / + | [0,-20] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_ny_30_cap | z=7 / + | [0,-30] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_ny_40_cap | z=7 / + | [0,-40] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| pin_ny_50_cap | z=7 / + | [0,-50] | 12.566370614 | 0.03mm; 0.002 | pi*mainPinDiameter^2/4; individual location from sources/dimension-sheet.md |
| raisedTread_outerX | z=3 / + | [-37,17] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=3: area 100, centroid (-37,17); stairTread^2. |
| raisedTread_middleX | z=5 / + | [-27,17] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=5: area 100, centroid (-27,17); stairTread^2. |
| raisedTread_elbow | z=7 / + | [-17,17] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=7: area 100, centroid (-17,17); stairTread^2. |
| raisedTread_middleY | z=6 / + | [-17,27] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=6: area 100, centroid (-17,27); stairTread^2. |
| raisedTread_outerY | z=4 / + | [-17,37] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=4: area 100, centroid (-17,37); stairTread^2. |
| recessedTread_outerX | z=-3 / + | [-37,-17] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=-3: area 100, centroid (-37,-17); stairTread^2. |
| recessedTread_middleX | z=-5 / + | [-27,-17] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=-5: area 100, centroid (-27,-17); stairTread^2. |
| recessedTread_elbow | z=-7 / + | [-17,-17] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=-7: area 100, centroid (-17,-17); stairTread^2. |
| recessedTread_middleY | z=-6 / + | [-17,-27] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=-6: area 100, centroid (-17,-27); stairTread^2. |
| recessedTread_outerY | z=-4 / + | [-17,-37] | 100 | 0.03mm; 0.002 | sources/dimension-sheet.md z=-4: area 100, centroid (-17,-37); stairTread^2. |
| raisedX42 | x=-42 / - | [17,1.5] | 30 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| recessedX42 | x=-42 / + | [-17,-1.5] | 30 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| raisedX32 | x=-32 / - | [17,4] | 20 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| recessedX32 | x=-32 / + | [-17,-4] | 20 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| raisedX22 | x=-22 / - | [28.67,3.17] | 120 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| recessedX22 | x=-22 / + | [-28.67,-3.17] | 120 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| raisedX12 | x=-12 / + | [25.24,2.97] | 170 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| recessedX12 | x=-12 / - | [-25.24,-2.97] | 170 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| raisedY12 | y=12 / - | [-24.33,2.77] | 150 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| recessedY12 | y=-12 / - | [-24.33,-2.77] | 150 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| raisedY22Long | y=22 / + | [-30.75,2.13] | 80 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| raisedY22Riser | y=22 / + | [-17,6.5] | 10 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| recessedY22Long | y=-22 / + | [-30.75,-2.12] | 80 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| recessedY22Riser | y=-22 / + | [-17,-6.5] | 10 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| raisedY32 | y=32 / + | [-17,5] | 20 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| recessedY32 | y=-32 / + | [-17,-5] | 20 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| raisedY42 | y=42 / + | [-17,2] | 40 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| recessedY42 | y=-42 / + | [-17,-2] | 40 | 0.05mm; 0.002 | sources/dimension-sheet.md axis-aligned face row; individual area and rounded centroid. |
| rampHighLanding | z=2 / + | [11.490485194,-11.490485194] | 12.5 | 0.03mm; 0.002 | rampWidth*rampLanding; centre r=rampStartRadius+rampLanding/2; sources/dimension-sheet.md z=2 area 12.5 |
| rampLowLanding | z=1 / + | [30.935921677,-30.935921677] | 12.5 | 0.03mm; 0.002 | rampWidth*rampLanding; centre r=rampStartRadius+rampLanding+rampRun+rampLanding/2; sources/dimension-sheet.md z=1 area 12.5 |
| finePinA_cap | z=2 / + | [28.284271247,21.213203436] | 3.141592654 | 0.02mm; 0.01 | pi*fineSizeA^2/4; sources/dimension-sheet.md individual fine feature centre. |
| fineHoleA_floor | z=-2 / + | [21.213203436,28.284271247] | 3.141592654 | 0.02mm; 0.01 | pi*fineSizeA^2/4; sources/dimension-sheet.md individual fine feature centre. |
| finePinB_cap | z=2 / + | [31.819805153,17.67766953] | 1.767145868 | 0.02mm; 0.01 | pi*fineSizeB^2/4; sources/dimension-sheet.md individual fine feature centre. |
| fineHoleB_floor | z=-2 / + | [17.67766953,31.819805153] | 1.767145868 | 0.02mm; 0.01 | pi*fineSizeB^2/4; sources/dimension-sheet.md individual fine feature centre. |
| finePinC_cap | z=2 / + | [35.355339059,14.142135624] | 0.785398163 | 0.02mm; 0.01 | pi*fineSizeC^2/4; sources/dimension-sheet.md individual fine feature centre. |
| fineHoleC_floor | z=-2 / + | [14.142135624,35.355339059] | 0.785398163 | 0.02mm; 0.01 | pi*fineSizeC^2/4; sources/dimension-sheet.md individual fine feature centre. |
| finePinD_cap | z=2 / + | [38.890872965,10.606601718] | 0.196349541 | 0.02mm; 0.01 | pi*fineSizeD^2/4; sources/dimension-sheet.md individual fine feature centre. |
| fineHoleD_floor | z=-2 / + | [10.606601718,38.890872965] | 0.196349541 | 0.02mm; 0.01 | pi*fineSizeD^2/4; sources/dimension-sheet.md individual fine feature centre. |
| finePinE_cap | z=2 / + | [42.426406871,7.071067812] | 0.049087385 | 0.02mm; 0.01 | pi*fineSizeE^2/4; sources/dimension-sheet.md individual fine feature centre. |
| fineHoleE_floor | z=-2 / + | [7.071067812,42.426406871] | 0.049087385 | 0.02mm; 0.01 | pi*fineSizeE^2/4; sources/dimension-sheet.md individual fine feature centre. |
| rectBoss1_cap | z=2 / + | [34.648232278,30.405591591] | 12 | 0.025mm; 0.01 | Width 2, length 6; centre u=49-3*width/2, v=3.0; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot1_floor | z=-2 / + | [30.405591591,34.648232278] | 12 | 0.025mm; 0.01 | Width 2, length 6; centre u=49-3*width/2, v=-3.0; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectBoss2_cap | z=2 / + | [37.476659403,27.577164466] | 12 | 0.025mm; 0.01 | Width 2, length 6; centre u=49-3*width/2, v=7.0; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot2_floor | z=-2 / + | [27.577164466,37.476659403] | 12 | 0.025mm; 0.01 | Width 2, length 6; centre u=49-3*width/2, v=-7.0; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectBoss3_cap | z=2 / + | [41.365746699,24.748737342] | 6.75 | 0.025mm; 0.01 | Width 1.5, length 4.5; centre u=49-3*width/2, v=11.75; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot3_floor | z=-2 / + | [24.748737342,41.365746699] | 6.75 | 0.025mm; 0.01 | Width 1.5, length 4.5; centre u=49-3*width/2, v=-11.75; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectBoss4_cap | z=2 / + | [43.487067043,22.627416998] | 6.75 | 0.025mm; 0.01 | Width 1.5, length 4.5; centre u=49-3*width/2, v=14.75; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot4_floor | z=-2 / + | [22.627416998,43.487067043] | 6.75 | 0.025mm; 0.01 | Width 1.5, length 4.5; centre u=49-3*width/2, v=-14.75; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectBoss5_cap | z=2 / + | [46.315494168,20.859650045] | 3 | 0.025mm; 0.01 | Width 1, length 3; centre u=49-3*width/2, v=18.0; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot5_floor | z=-2 / + | [20.859650045,46.315494168] | 3 | 0.025mm; 0.01 | Width 1, length 3; centre u=49-3*width/2, v=-18.0; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectBoss6_cap | z=2 / + | [47.72970773,19.445436483] | 3 | 0.025mm; 0.01 | Width 1, length 3; centre u=49-3*width/2, v=20.0; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot6_floor | z=-2 / + | [19.445436483,47.72970773] | 3 | 0.025mm; 0.01 | Width 1, length 3; centre u=49-3*width/2, v=-20.0; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectBoss7_cap | z=2 / + | [49.851028074,18.384776311] | 0.75 | 0.025mm; 0.01 | Width 0.5, length 1.5; centre u=49-3*width/2, v=22.25; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot7_floor | z=-2 / + | [18.384776311,49.851028074] | 0.75 | 0.025mm; 0.01 | Width 0.5, length 1.5; centre u=49-3*width/2, v=-22.25; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectBoss8_cap | z=2 / + | [50.558134855,17.67766953] | 0.75 | 0.025mm; 0.01 | Width 0.5, length 1.5; centre u=49-3*width/2, v=23.25; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot8_floor | z=-2 / + | [17.67766953,50.558134855] | 0.75 | 0.025mm; 0.01 | Width 0.5, length 1.5; centre u=49-3*width/2, v=-23.25; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectBoss9_cap | z=2 / + | [51.795571722,16.970562748] | 0.1875 | 0.025mm; 0.01 | Width 0.25, length 0.75; centre u=49-3*width/2, v=24.625; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot9_floor | z=-2 / + | [16.970562748,51.795571722] | 0.1875 | 0.025mm; 0.01 | Width 0.25, length 0.75; centre u=49-3*width/2, v=-24.625; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectBoss10_cap | z=2 / + | [52.149125113,16.617009358] | 0.1875 | 0.025mm; 0.01 | Width 0.25, length 0.75; centre u=49-3*width/2, v=25.125; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| rectSlot10_floor | z=-2 / + | [16.617009358,52.149125113] | 0.1875 | 0.025mm; 0.01 | Width 0.25, length 0.75; centre u=49-3*width/2, v=-25.125; area=rectLengthRatio*width^2. sources/dimension-sheet.md individual z=±2 face. |
| lateral_smallSquare_wall1 | z=-6.5 / + | [-13.081475452,55.507882323] | 9 | 0.05mm; 0.01 | Extruded smallSquare profile edge (-1.5, -1.5) to (1.5, -1.5) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_smallSquare_wall3 | z=-3.5 / - | [-13.081475452,55.507882323] | 9 | 0.05mm; 0.01 | Extruded smallSquare profile edge (1.5, 1.5) to (-1.5, 1.5) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_largeSquare_wall1 | z=-8 / + | [-33.587572106,33.587572106] | 30 | 0.05mm; 0.01 | Extruded largeSquare profile edge (-3.0, -3.0) to (3.0, -3.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_largeSquare_wall3 | z=-2 / - | [-33.587572106,33.587572106] | 30 | 0.05mm; 0.01 | Extruded largeSquare profile edge (3.0, 3.0) to (-3.0, 3.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |

**Individual cylindrical observables.** Points define the axis; extents are signed distances from that point along the listed direction. All 35 are required. Diameter tolerances are encoded as a 0.005 mm radius tolerance; axial extent length tolerance is 0.02 mm.

| cylinder | kind | axis point | direction | diameter | length / t-range | axis tolerance | evidence |
|---|---|---|---|---|---|---|---|
| centerBore | hole | [0,0,0] | [0,0,1] | 10 | 17 / [-10,7] | 0.02 | sources/dimension-sheet.md Ø10 hole axis and extent |
| lowerCentralBoss | pin | [0,0,0] | [0,0,1] | 20 | 4 / [0,4] | 0.02 | sources/dimension-sheet.md Ø20 pin 0 .. 4 |
| upperCentralBoss | pin | [0,0,0] | [0,0,1] | 15 | 3 / [4,7] | 0.02 | sources/dimension-sheet.md Ø15 pin 4 .. 7 |
| pin_px_20 | pin | [20,0,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_px_30 | pin | [30,0,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_px_40 | pin | [40,0,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_px_50 | pin | [50,0,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| hole_px | hole | [60,0,0] | [0,0,1] | 4 | 10 / [-10,0] | 0.02 | sources/dimension-sheet.md individual Ø4 through-hole axis, diameter and extent |
| pin_nx_20 | pin | [-20,0,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_nx_30 | pin | [-30,0,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_nx_40 | pin | [-40,0,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_nx_50 | pin | [-50,0,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| hole_nx | hole | [-60,0,0] | [0,0,1] | 4 | 10 / [-10,0] | 0.02 | sources/dimension-sheet.md individual Ø4 through-hole axis, diameter and extent |
| pin_py_20 | pin | [0,20,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_py_30 | pin | [0,30,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_py_40 | pin | [0,40,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_py_50 | pin | [0,50,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| hole_py | hole | [0,60,0] | [0,0,1] | 4 | 10 / [-10,0] | 0.02 | sources/dimension-sheet.md individual Ø4 through-hole axis, diameter and extent |
| pin_ny_20 | pin | [0,-20,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_ny_30 | pin | [0,-30,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_ny_40 | pin | [0,-40,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| pin_ny_50 | pin | [0,-50,0] | [0,0,1] | 4 | 7 / [0,7] | 0.02 | sources/dimension-sheet.md individual Ø4 pin axis, diameter and extent |
| hole_ny | hole | [0,-60,0] | [0,0,1] | 4 | 10 / [-10,0] | 0.02 | sources/dimension-sheet.md individual Ø4 through-hole axis, diameter and extent |
| finePinA | pin | [28.284271247,21.213203436,0] | [0,0,1] | 2 | 2 / [0,2] | 0.015 | sources/dimension-sheet.md individual Ø2 fine pin axis and extent |
| fineHoleA | hole | [21.213203436,28.284271247,0] | [0,0,1] | 2 | 2 / [-2,0] | 0.015 | sources/dimension-sheet.md individual Ø2 fine hole axis and extent |
| finePinB | pin | [31.819805153,17.67766953,0] | [0,0,1] | 1.5 | 2 / [0,2] | 0.015 | sources/dimension-sheet.md individual Ø1.5 fine pin axis and extent |
| fineHoleB | hole | [17.67766953,31.819805153,0] | [0,0,1] | 1.5 | 2 / [-2,0] | 0.015 | sources/dimension-sheet.md individual Ø1.5 fine hole axis and extent |
| finePinC | pin | [35.355339059,14.142135624,0] | [0,0,1] | 1 | 2 / [0,2] | 0.015 | sources/dimension-sheet.md individual Ø1 fine pin axis and extent |
| fineHoleC | hole | [14.142135624,35.355339059,0] | [0,0,1] | 1 | 2 / [-2,0] | 0.015 | sources/dimension-sheet.md individual Ø1 fine hole axis and extent |
| finePinD | pin | [38.890872965,10.606601718,0] | [0,0,1] | 0.5 | 2 / [0,2] | 0.015 | sources/dimension-sheet.md individual Ø0.5 fine pin axis and extent |
| fineHoleD | hole | [10.606601718,38.890872965,0] | [0,0,1] | 0.5 | 2 / [-2,0] | 0.015 | sources/dimension-sheet.md individual Ø0.5 fine hole axis and extent |
| finePinE | pin | [42.426406871,7.071067812,0] | [0,0,1] | 0.25 | 2 / [0,2] | 0.015 | sources/dimension-sheet.md individual Ø0.25 fine pin axis and extent |
| fineHoleE | hole | [7.071067812,42.426406871,0] | [0,0,1] | 0.25 | 2 / [-2,0] | 0.015 | sources/dimension-sheet.md individual Ø0.25 fine hole axis and extent |
| lateral_smallRound | hole | [28.284271247,28.284271247,-5] | [0.707106781,-0.707106781,0] | 3 | 3 / [-50,-47] | 0.02 | sources/dimension-sheet.md Ø3 lateral bore, full 360°, exact axis and depth |
| lateral_largeRound | hole | [7.071067812,7.071067812,-5] | [0.707106781,-0.707106781,0] | 6 | 5 / [-50,-45] | 0.02 | sources/dimension-sheet.md Ø6 lateral bore, full 360°, exact axis and depth |

**Inclined and side planes.** Normal vectors are outward from solid material, including inward toward cavity space for cavity walls. Plane checks sum all coplanar hits; the two lateral back-plane entries explicitly request the combined back area. Separate feature probes locate each cavity.

| plane | point | outward normal | area | position/angle/area tolerances | formula / evidence |
|---|---|---|---|---|---|
| sideSouthWest | [-70.710678119,0,-5] | [-0.707106781,-0.707106781,0] | 1000 | 0.03mm / 0.1deg / 0.001 | Plain area baseSide*baseThickness; NW subtracts eight lateral opening areas. sources/dimension-sheet.md inclined planar faces. |
| sideSouthEast | [0,-70.710678119,-5] | [0.707106781,-0.707106781,0] | 1000 | 0.03mm / 0.1deg / 0.001 | Plain area baseSide*baseThickness; NW subtracts eight lateral opening areas. sources/dimension-sheet.md inclined planar faces. |
| sideNorthEast | [0,70.710678119,-5] | [0.707106781,0.707106781,0] | 1000 | 0.03mm / 0.1deg / 0.001 | Plain area baseSide*baseThickness; NW subtracts eight lateral opening areas. sources/dimension-sheet.md inclined planar faces. |
| sideNorthWest | [-70.710678119,0,-5] | [-0.707106781,0.707106781,0] | 872.908371341 | 0.03mm / 0.1deg / 0.001 | Plain area baseSide*baseThickness; NW subtracts eight lateral opening areas. sources/dimension-sheet.md inclined planar faces. |
| rampSlope | [21.213203436,-21.213203436,1.5] | [0.028261671,-0.028261671,0.999200959] | 125.099960032 | 0.03mm / 0.1deg / 0.001 | z=2-(r-17.5)/25 for 17.5<=r<=42.5; area=rampWidth*sqrt(rampRun^2+rampRise^2). sources/dimension-sheet.md slope centroid and normal. |
| rampSidePositive | [22.980970389,-19.445436483,1] | [0.707106781,0.707106781,0] | 45 | 0.03mm / 0.1deg / 0.002 | Positive transverse side at u=2.5; integral h(r) dr = 45. |
| rampSideNegative | [19.445436483,-22.980970389,1] | [-0.707106781,-0.707106781,0] | 45 | 0.03mm / 0.1deg / 0.002 | Negative transverse side at u=-2.5; integral h(r) dr = 45. |
| rampHighEnd | [10.606601718,-10.606601718,1] | [-0.707106781,0.707106781,0] | 10 | 0.03mm / 0.1deg / 0.002 | Near end r=15; area=rampWidth*(rampLowHeight+rampRise). |
| rampLowEnd | [31.819805153,-31.819805153,0.5] | [0.707106781,-0.707106781,0] | 5 | 0.03mm / 0.1deg / 0.002 | Far end r=45; area=rampWidth*rampLowHeight. |
| lateralSmallBacks | [-12.02081528,54.447222151,-5] | [-0.707106781,0.707106781,0] | 20.568583471 | 0.05mm / 0.1deg / 0.01 | Combined area on q=-47 of the three small cavity backs: pi*3^2/4+3^2+3^2/2. Plane probes sum all coplanar hits; individual void/solid probes locate each cavity. |
| lateralLargeBacks | [-31.819805153,31.819805153,-5] | [-0.707106781,0.707106781,0] | 106.523045188 | 0.05mm / 0.1deg / 0.003 | Combined area on q=-45 of five large cavity backs: pi*6^2/4+6^2+6^2/2+6*(6*tan(30deg))/2+4*(4/tan(30deg))/2. |
| lateral_smallSquare_wall2 | [-12.02081528,56.568542495,-5.0] | [-0.707106781,-0.707106781,0.0] | 9 | 0.05mm / 0.1deg / 0.01 | Extruded smallSquare profile edge (1.5, -1.5) to (1.5, 1.5) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_smallSquare_wall4 | [-14.142135624,54.447222151,-5.0] | [0.707106781,0.707106781,0.0] | 9 | 0.05mm / 0.1deg / 0.01 | Extruded smallSquare profile edge (-1.5, 1.5) to (-1.5, -1.5) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_smallDiamond_wall1 | [-19.622213178,48.967144597,-5.75] | [-0.5,-0.5,0.707106781] | 6.363961031 | 0.08mm / 0.1deg / 0.02 | Extruded smallDiamond profile edge (0, -1.5) to (1.5, 0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_smallDiamond_wall2 | [-19.622213178,48.967144597,-4.25] | [-0.5,-0.5,-0.707106781] | 6.363961031 | 0.08mm / 0.1deg / 0.02 | Extruded smallDiamond profile edge (1.5, 0) to (0, 1.5) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_smallDiamond_wall3 | [-20.68287335,47.906484425,-4.25] | [0.5,0.5,-0.707106781] | 6.363961031 | 0.08mm / 0.1deg / 0.02 | Extruded smallDiamond profile edge (0, 1.5) to (-1.5, 0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_smallDiamond_wall4 | [-20.68287335,47.906484425,-5.75] | [0.5,0.5,0.707106781] | 6.363961031 | 0.08mm / 0.1deg / 0.02 | Extruded smallDiamond profile edge (-1.5, 0) to (0, -1.5) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_largeSquare_wall2 | [-31.466251763,35.70889245,-5.0] | [-0.707106781,-0.707106781,0.0] | 30 | 0.05mm / 0.1deg / 0.01 | Extruded largeSquare profile edge (3.0, -3.0) to (3.0, 3.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_largeSquare_wall4 | [-35.70889245,31.466251763,-5.0] | [0.707106781,0.707106781,0.0] | 30 | 0.05mm / 0.1deg / 0.01 | Extruded largeSquare profile edge (-3.0, 3.0) to (-3.0, -3.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_largeDiamond_wall1 | [-39.597979746,27.577164466,-6.5] | [-0.5,-0.5,0.707106781] | 21.213203436 | 0.05mm / 0.1deg / 0.01 | Extruded largeDiamond profile edge (0, -3.0) to (3.0, 0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_largeDiamond_wall2 | [-39.597979746,27.577164466,-3.5] | [-0.5,-0.5,-0.707106781] | 21.213203436 | 0.05mm / 0.1deg / 0.01 | Extruded largeDiamond profile edge (3.0, 0) to (0, 3.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_largeDiamond_wall3 | [-41.71930009,25.455844123,-3.5] | [0.5,0.5,-0.707106781] | 21.213203436 | 0.05mm / 0.1deg / 0.01 | Extruded largeDiamond profile edge (0, 3.0) to (-3.0, 0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_largeDiamond_wall4 | [-41.71930009,25.455844123,-6.5] | [0.5,0.5,0.707106781] | 21.213203436 | 0.05mm / 0.1deg / 0.01 | Extruded largeDiamond profile edge (-3.0, 0) to (0, -3.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_tallRhombus_wall1 | [-47.117335294,20.057808918,-6.5] | [-0.612372436,-0.612372436,0.5] | 17.320508076 | 0.05mm / 0.1deg / 0.01 | Extruded tallRhombus profile edge (0, -3.0) to (1.7320508075688767, 0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_tallRhombus_wall2 | [-47.117335294,20.057808918,-3.5] | [-0.612372436,-0.612372436,-0.5] | 17.320508076 | 0.05mm / 0.1deg / 0.01 | Extruded tallRhombus profile edge (1.7320508075688767, 0) to (0, 3.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_tallRhombus_wall3 | [-48.342080166,18.833064047,-3.5] | [0.612372436,0.612372436,-0.5] | 17.320508076 | 0.05mm / 0.1deg / 0.01 | Extruded tallRhombus profile edge (0, 3.0) to (-1.7320508075688767, 0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_tallRhombus_wall4 | [-48.342080166,18.833064047,-6.5] | [0.612372436,0.612372436,0.5] | 17.320508076 | 0.05mm / 0.1deg / 0.01 | Extruded tallRhombus profile edge (-1.7320508075688767, 0) to (0, -3.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_wideRhombus_wall1 | [-53.576030671,13.599113542,-6.0] | [-0.353553391,-0.353553391,0.866025404] | 20 | 0.05mm / 0.1deg / 0.01 | Extruded wideRhombus profile edge (0, -2.0) to (3.4641016151377553, 0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_wideRhombus_wall2 | [-53.576030671,13.599113542,-4.0] | [-0.353553391,-0.353553391,-0.866025404] | 20 | 0.05mm / 0.1deg / 0.01 | Extruded wideRhombus profile edge (3.4641016151377553, 0) to (0, 2.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_wideRhombus_wall3 | [-56.025520413,11.149623799,-4.0] | [0.353553391,0.353553391,-0.866025404] | 20 | 0.05mm / 0.1deg / 0.01 | Extruded wideRhombus profile edge (0, 2.0) to (-3.4641016151377553, 0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |
| lateral_wideRhombus_wall4 | [-56.025520413,11.149623799,-6.0] | [0.353553391,0.353553391,0.866025404] | 20 | 0.05mm / 0.1deg / 0.01 | Extruded wideRhombus profile edge (-3.4641016151377553, 0) to (0, -2.0) in (t-centre,z+5); area=edge length*depth; outward material normal points into the cavity. Supported by A-A and sources/dimension-sheet.md. |

**Distances.** Only actual bbox spans or separations of named axis-aligned faces use DimensionSpec. Diagonal lengths use explicit construction coordinates and plane/face checks, not a misleading global-axis distance.

| dimension | axis | expected | between faces or bbox | tolerance | formula / evidence |
|---|---|---|---|---|---|
| spanX | x | 141.421356237 | bbox span | 0.03 | sqrt(2)*baseSide; sources/dimension-sheet.md bbox size 141.421 |
| spanY | y | 141.421356237 | bbox span | 0.03 | sqrt(2)*baseSide; sources/dimension-sheet.md bbox size 141.421 |
| totalHeight | z | 17 | bbox span | 0.03 | baseThickness + max(mainPinHeight,lowerBossHeight+upperBossHeight,stairFirstHeight+4*stairIncrement). |
| baseThicknessCheck | z | 10 | ["baseBottom","datumTop"] | 0.03 | baseThickness; top datum stays fixed. |
| raisedTread_outerX_level | z | 3 | ["datumTop","raisedTread_outerX"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| raisedTread_middleX_level | z | 5 | ["datumTop","raisedTread_middleX"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| raisedTread_elbow_level | z | 7 | ["datumTop","raisedTread_elbow"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| raisedTread_middleY_level | z | 6 | ["datumTop","raisedTread_middleY"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| raisedTread_outerY_level | z | 4 | ["datumTop","raisedTread_outerY"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| recessedTread_outerX_level | z | 3 | ["datumTop","recessedTread_outerX"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| recessedTread_middleX_level | z | 5 | ["datumTop","recessedTread_middleX"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| recessedTread_elbow_level | z | 7 | ["datumTop","recessedTread_elbow"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| recessedTread_middleY_level | z | 6 | ["datumTop","recessedTread_middleY"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| recessedTread_outerY_level | z | 4 | ["datumTop","recessedTread_outerY"] | 0.03 | Absolute level from datum A; order along the L is 3,5,7,6,4. |
| stairXTreadPitch | x | 10 | ["raisedX42","raisedX32"] | 0.03 | One 10 mm tread between consecutive riser planes. |
| stairYTreadPitch | y | 10 | ["raisedY32","raisedY42"] | 0.03 | One 10 mm tread between consecutive riser planes. |
| rampRiseCheck | z | 1 | ["rampHighLanding","rampLowLanding"] | 0.03 | Landing level difference equals rampRise. |

**Edit tests.** Apply one edit at a time, with all independent parameters held fixed. Through-hole lengths follow the changed thickness; lateral z centres stay fixed; raised stair and central boss levels do not follow mainPinHeight. These tests are planned expectations, not executed geometry results.

| parameter edit | expected volume change | direction | bbox size change | formula |
|---|---|---|---|---|
| baseThickness +1 | 9871.194701203 | increase | [0,0,1] | delta*(baseSide²-π/4*(centerHoleDiameter²+4*mainHoleDiameter²)) |
| mainPinHeight +1 | 201.06192983 | increase | [0,0,1] | delta*16*π*mainPinDiameter²/4 |
| rampRise +0.5 | 37.5 | increase | [0,0,0] | delta*rampWidth*(rampLanding+rampRun/2); low landing remains1 |

The edit volume tolerance is 0.5%. For baseThickness+1 the expected ΔV is 9871.194701203 mm³ and Δbbox=[0,0,1]; for mainPinHeight+1 it is 201.06192983 mm³ and [0,0,1]; for rampRise+0.5 it is 37.5 mm³ and [0,0,0]. Interface checks distinguish invariant datum/fine/stair faces from interfaces whose heights or through lengths intentionally change.

## 6. Defaults retained

No seeded geometric value was retained without source evidence. Units are mm and deg, release_status is reconstruction, and solid_count is 1 because the task explicitly requires them. Material, density and process remain null because the source does not supply them; therefore no mass is claimed. The STEP/STL/KCL volume-agreement threshold is 0.002. Digital comparison thresholds are engineering comparison defaults documented in the parameter/acceptance tables; they are not replacements for the drawing’s unspecified GD&T. Small table-rounding differences are preserved in evidence rather than interpreted as intended asymmetry. No fillets, chamfers, surface texture or mesh-deviation limits are invented. No optional geometry is used.

## 7. Unrepresentable or low-confidence features

- Q1. The task summary says 34 cylindrical features, but the supplied table enumerates 35 (12 holes and 23 pins/bosses). Is 34 a counting error? This contract requires all 35 located cylinders.
- Q2. The prose mentions lateral bosses, a hexagon and a lens; A-A, the inclined-plane table and z=-5 outline instead support eight blind cavities: two circles, two squares, two diamonds and two straight-edged rhombi. Are the alternative terms descriptive only? These eight cavities reproduce the supplied volume, area and COM; no extra unsupported boss or curved lens is added.
- Q3. The small lateral diamond has no explicit diagonal or depth callout. Are its 3 mm diagonals and 3 mm depth nominal? They are measured from A-A and the section, use ±0.3 mm parameter tolerances, and agree with the aggregate table properties.
- Q4. Exact-face sections disagree: at z=1 the table gives 1138 mm2/35 loops but the image gives 1124.79/34; at z=5 they give 599.24/19 versus 498.76/18; at z=-5 they give 9502.23/2 versus 9402.44/1. Confirm the intended coplanar-section convention if those exact stations are needed. Acceptance uses non-coplanar z=0.5,1.5,3.5,4.5,5.5,6.5,-5.5 instead.
- Q5. Numeric GD&T values, material, density, manufacturing process, surface finish and edge-break requirements are not supplied. What values apply for fabrication? The drawing xx boxes remain unspecified; this contract uses digital reconstruction tolerances and makes no mass or manufacturability claim.

The native geometry and export checks await the subsequent modelling stage. This drafting task has not executed a CAD engine or created STEP/STL. The analytic totals are independently derived from the stated construction and compared to the supplied sheet; they are not a claim that a future implementation passes. The exact-face raster discrepancies, unspecified fabrication tolerances and the small lateral diamond are disclosed above. All required feature families are encoded, including each smallest fine member. The obsolete main.kcl entry was only a settings-line stub; it was removed because KCL is not an allowed entry in a design bundle.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 2 | [-70.7107, -70.7107, -10.0] → [70.7107, 70.7107, 0.0] | 100000.005321248 | FAIL | 2026-09-17T12:35:42Z: see results/nist-am-test-artifact/blockout.json |
