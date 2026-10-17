# nist-amb2022-01-bridge-mesh — design brief

## 1. Intent and configuration

Reconstruct the NIST AMB2022-01 individual bridge artifact as editable, parameterized KCL from the attached NIST description excerpts and figures; Figure 3 is the dimensioned plan and elevation drawing and is authoritative for every external dimension. Frame: x along the 75 mm length with x = 0 at the pointed (45 degree tapered) end and x increasing toward the far end, y across the 5 mm width with y = 0 at one long side face, z vertical from the build plate (z = 0) upward. Model the tapered nose, the tall solid end block, the twelve legs with their 45 degree overhangs merging into the solid bridge, the eleven 1 mm wide top tabs on a 7 mm pitch, and the hollow leg L10 with its 0.5 mm outer walls, 1 mm base, four 4 mm tall internal thin walls parallel to x, and flat ceiling, exactly as documented. Where the sources do not fix a dimension (the single- and double-track thin-wall widths), record it as an open question and use a clearly labelled inferred value with a wide tolerance rather than approximating silently. One solid; export STEP and STL. Reference geometry supplied by NIST is for inspection only: the deliverable must be editable construction, never an import.

Configuration: one individual nominal as-built bridge, before EDM separation and ridge skim cutting. No build plate, six-part build layout, recoater guide, reference import, scan-path texture, or annotation geometry is included. The downstream model must use editable KCL 2 construction in mm, expose every contract parameter as a literal top-level constant, retain one material solid, and export deterministic STEP plus STL. This task prepares the source bundle only; section 8 remains an empty checkpoint log.

Authority: Figure 3 controls external dimensions. The description and Figure 4 establish L10 topology, heights and scan-wall arrangement. The supplied STL and ingest files provide inspection evidence with `measured (reference model)` provenance. They cannot override the drawing or be imported as the deliverable.

The description’s 12 mm height is the main top; the 0.5 mm ridges make the envelope 12.5 mm high. The prose phrase “proceeds left” conflicts with the Figure 3 arrow; the user’s frame and that arrow resolve +x toward the far end.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| `sources/nist-amb2022-01-description.md` | text | authoritative | `ad20b8b64ceffc5122b055fd97c5e12b4b89b3cd2d52876ba74afb4d66cf2094` | Units: mm. Revision: NIST page inspected 2026-09-15; local geometry excerpts. Geometry excerpts; §§1, 2.1.3, 2.3 and process facts. Geometry is nominal as built, before EDM and skim cutting. |
| `sources/nist-figure3-drawing.png` | drawing | authoritative | `a2377f44a5d37ee5e2193817bc33f079d664fae8c9df7bd675480f9e97b37d49` | Units: mm. Revision: NIST Figure 3, updated 2023-09-20. External dimensions and their arrangement control. 3127x1821 pixels; original raster coordinates are recorded in §4. |
| `sources/nist-figure4-legs-thinwalls.png` | image | authoritative | `a55dce91299778420a4970d51478be5856a89b291644459d93b7cb71524b7417` | Units: mm. Revision: NIST Figure 4, Layer 50; revision date unspecified; supplied 2026-09-15. Leg numbering, four-wall topology and scan-line arrangement. Physical track widths and exact scan-to-surface datum are qualified by OQ1/OQ2. 3900x1771 pixels. |
| `sources/AMB2022-01-AMMT-PartCAD.STL` | mesh | illustrative | `d92f368a35952ff877624f3d15fb0e38c099e2528cfd96bf1d76a868a088e1f4` | Units: mm. Revision: NIST AMB2022-01 individual-part STL; revision unspecified; supplied 2026-09-15. Inspection-only NIST reference; all construction must be editable KCL. Explicit Figure 3 dimensions take precedence. Signed-shell inspection finds one outer shell and five inward pocket shells. |
| `reference/reference.json` | reference-model | illustrative | `04cecbfa70a33ff22219241703a4cad614239953b5adcc7932bfeab6f4f78dff` | Units: mm. Revision: Ingest generated 2026-09-15T16:44:16Z. Deterministic measurements with measured (reference model) provenance, identity axes, mm scale, min datum, and suggested fidelity bands. Sections use to_3d matrices; their local coordinates are not part coordinates. |
| `reference/reference.ply` | mesh | illustrative | `4ea678f069d6057ffc44cd324e975c35663bfd795184716f89d56ae305b00e94` | Units: mm. Revision: Ingest generated 2026-09-15T16:44:16Z. Normalized inspection/fidelity mesh produced by the ingest; never import into the deliverable. |
| `reference/reference-sections.png` | image | illustrative | `5cf02a12910b23264f1895ea5263171d248f98e3443155f82e64c7cdc04f7c8b` | Units: mm. Revision: Ingest generated 2026-09-15T16:44:16Z. Section sheet with z=3,6,9,12.3 and x=30.5; visual aid to reference.json, not an independent dimensional source. |
| `reference/silhouette-front.png` | image | illustrative | `f049d290879efb0e2e2b370c053c6179bd42888f833e87f7e6533dcb89cac90b` | Units: mm. Revision: Ingest generated 2026-09-15T16:44:16Z. Orthographic xz silhouette, 840x173 px, about 0.09375 mm per pixel with 20 px margins. |
| `reference/silhouette-right.png` | image | illustrative | `ef9e98ec528b46c02923a529facad0ac26727041648bb1494bc8bdf5dee78ff5` | Units: mm. Revision: Ingest generated 2026-09-15T16:44:16Z. Orthographic yz silhouette, 360x840 px, 0.015625 mm per pixel with 20 px margins. |
| `reference/silhouette-top.png` | image | illustrative | `b4c6d94ec479f4b6e63a0b7c71ec5b98cb365cfa618ed09b15ea8dad086a0504` | Units: mm. Revision: Ingest generated 2026-09-15T16:44:16Z. Orthographic xy silhouette, 840x93 px, about 0.09375 mm per pixel with 20 px margins. |

All ten files under `sources/` and `reference/` are listed above with full SHA-256 digests. Figures use displayed millimetre dimensions; pixels are measured in the original files, not the resized chat previews.

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|
| Frame and external envelope | min [0,0,0], max [75,5,12.5] | mm | User frame; Figure 3; reference anchor agrees | ±0.10 per bound | stated / derived |
| Main top / total height | 12 / 12.5 | mm | Description §§2.1.3, 2.3; Figure 3 12 and 0.5 callouts | body ±0.01; envelope ±0.10 | stated / derived |
| Nose | 2.5 axial length, 45 degree flanks in plan, 90 degree included tip | mm / deg | Figure 3; description §2.1.3 | length ±0.10; angle ±0.10 | derived / stated |
| End block | x=0..19 at its foot, solid to z=12 | mm | Derived from 75 minus four 14 mm triplets; Figure 3 pixels corroborate | ±0.15 axial end position | derived |
| Legs | Twelve numbered feet plus the separate end block; four each of x widths 5, 2.5, 0.5 | count / mm | Description; Figures 3 and 4 | count exact; widths ±0.10 | stated / measured |
| Gaps and overhangs | Twelve 2 mm gaps; roof rises 5 to 7 in +x at 45 degrees | mm / deg | Figure 3; description §2.3 | gap ±0.10; merge height ±0.01; angle ±0.10 | measured / stated / derived |
| Top tabs | Eleven, x width 1, pitch 7, rise 0.5; first at x=4, last ends at x=75 | count / mm | Description; Figure 3 | count exact; drawing dimensions ±0.10 | stated / measured / derived |
| Hollow L10 | Outer x=[28,33], y=[0,5]; four outer walls nominally 0.5 | mm | Figures 3 and 4; description §2.1.3 | walls ±0.10; derived x origin ±0.15 | stated / derived |
| Base, thin-wall height, ceiling | Base z=0..1, walls z=1..5, flat ceiling underside at z=5 | mm | Description §2.1.3; Figure 3 | base/wall height ±0.01; ceiling ±0.02 | stated / derived |
| Internal wall arrangement | Four x-parallel walls, single/double/single/double in +y | count / orientation | Description; Figure 4 labels and six scan lines grouped into four walls | count exact; y centers ±0.20 | stated / measured |
| Physical internal wall widths | Single 0.10 ±0.08; double 0.20 ±0.15 | mm | Necessary provisional values from spot-size scale; no physical-width dimension | As shown | inferred; OQ1 |
| L10 closure | Five sealed pockets; outer section one material loop with five holes | count | Description says completely sealed; four walls partition clear cavity | exact topology | derived |
| Material and process | LPBF metal alloy; alloy and density unspecified | — | Description §1 | — | process stated; OQ3 |
| Deliverables | Editable parameterized KCL 2, one solid, STEP and STL | — | User instruction | export volumes within 0.2% | required downstream |

Foot intervals below z=5 (L10 contains its pockets only above z=1):

| region | x interval (mm) | width (mm) | geometry at z=3 |
|---|---|---|---|
| Tall end block | [0,19] | 19 including the nose | Solid tapered footprint |
| L12 | [21,23.5] | 2.5 | Solid |
| L11 | [25.5,26] | 0.5 | Solid |
| L10 | [28,33] | 5 | Outer walls and four internal walls |
| L9 | [35,37.5] | 2.5 | Solid |
| L8 | [39.5,40] | 0.5 | Solid |
| L7 | [42,47] | 5 | Solid |
| L6 | [49,51.5] | 2.5 | Solid |
| L5 | [53.5,54] | 0.5 | Solid |
| L4 | [56,61] | 5 | Solid |
| L3 | [63,65.5] | 2.5 | Solid |
| L2 | [67.5,68] | 0.5 | Solid |
| L1 | [70,75] | 5 | Solid |

Gap left edges are `a = [19,23.5,26,33,37.5,40,47,51.5,54,61,65.5,68]` mm. Each void spans `a < x < a+gapWidth`, the full width, and `0 < z < gapLowHeight+(x-a)*tan(overhangAngle)`. This specifies the overhang direction without relying on visual perspective. Above z=7 the gaps have closed.

Top-tab x intervals are `[4,5], [11,12], [18,19], [25,26], [32,33], [39,40], [46,47], [53,54], [60,61], [67,68], [74,75]` mm.

Nominal sealed pockets all have x=[28.5,32.5] and z=[1,5]. Their y intervals are `[0.5,1.2], [1.3,1.9], [2.1,2.8], [2.9,3.5], [3.7,4.5]` mm. Internal wall width edits change these void intervals about the specified wall centers.

## 4. Coordinate frame, scale, and measurement method

**Reproducible frame.** Datum A is the common build-contact plane z=0. Datum B is the plane of the lower long side in the Figure 3 plan, y=0. Datum C is the plane perpendicular to the long axis through the pointed nose, x=0. Their intersection is the coordinate origin; it is outside material. The nose’s bottom tip itself is (0,2.5,0), not (0,0,0). +x runs from that tip toward the square far end, +y crosses the width toward the upper plan side, and +z points up. The far end is x=75. The datum descriptions and named planar contact faces are in the contract.

**Figure 3 pixel method.** Use zero-based `(u,v)` pixels from the upper-left of the original 3127×1821 raster. The 75 mm dimension has witness columns u=382 and 2936; scale is `(2936-382)/75 = 34.053333 px/mm`, so `x=(u-382)/34.053333`. The plan long-side strokes are centered near v=492 and 322, giving 34.0 px/mm from the 5 mm dimension, with `y=(492-v)/34.0`. Elevation base and body-top strokes are centered near v=1495 and 1085, giving `(1495-1085)/12 = 34.166667 px/mm`, with `z=(1495-v)/34.166667`. Separate horizontal/vertical calibration accounts for raster scaling; no perspective warp is applied to these orthographic views. Figure dimension labels determine nominal values; pixels confirm the correct witness lines and placements.

| pixel evidence in Figure 3 | readout and interpretation |
|---|---|
| Plan tip near (382,407); shoulders near (467,322) and (467,492) | Nose axial length 85/34.0533=2.496 mm; two equal flanks validate 45 degrees and centered tip. |
| Elevation base v≈1495, body top v≈1085, tab crests v≈1069 | Body 12 mm; tab pixel rise ≈0.47 mm corroborates the authoritative 0.5 callout; total height 12.5 mm. |
| Right roof low point near (2698,1325), high point near (2766,1255) | Gap run 68/34.0533≈1.997 mm; roof rise 70/34.1667≈2.049 mm, consistent with the 2 and 45-degree callouts. |
| Medium foot u≈2528..2613; small foot 2681..2698; large foot 2766..2936 | About 2.496, 0.499 and 4.992 mm; use the printed 2.5, 0.5 and 5 values. |
| Final triplet u≈2460..2936 | About 13.978 mm; printed 14 corroborates width sum plus three gaps. |
| End-block left/right foot edges u≈382..1030 | About 19.028 mm; use derived 19, independently corroborated by reference section bounds. |
| Tab edge pairs near 519/553, 757/792, 995/1030, 1235/1268, 1473/1506, 1710/1745, 1949/1983, 2188/2221, 2426/2460, 2664/2698, 2901/2936 | Eleven tabs; corresponding-edge pitch ≈238 px or 6.989 mm, with ≈34 px or 1 mm width. Colored overlays partly occlude strokes. |
| Bottom feet after end block at u≈1098..1182, 1251..1268, 1336..1506, 1575..1660, 1728..1745, 1813..1983, 2051..2136, 2204..2221, 2290..2460, 2528..2613, 2681..2698, 2766..2936 | Twelve numbered legs. A horizontal section below the cavity has thirteen outer loops when the solid end block is included. |
| L10 cavity horizontal dimension witnesses u≈1353 and 1490; vertical dashed floor/ceiling v≈1460 and 1325 | About 4.02 mm clear length and 3.95 mm height; the printed 4 and 4.0 values control. Base thickness from v≈1495 to 1460 is ≈1.02 mm, corroborating 1.0. Dashed diagram rectangle is schematic; its left offset is not a new outer-wall dimension. |

Most geometric strokes occupy 4–7 pixels (about 0.12–0.21 mm), with centerline uncertainty around 2–3 px; measured Figure 3 parameters therefore use ±0.10 mm, or ±0.15 mm for combined placements. Explicit prose values have smaller digital bands. Pixel checks do not introduce tolerances on the original NIST manufacturing specification.

**Figure 4 pixel method.** Use the original 3900×1771 raster. The left perspective sketch identifies L1 at the far end and L10 in the first large foot after the end block; perspective dimensions are not scaled. In the right scan plot, x-grid columns 1458, 1820, 2182, 2544 correspond to −6, −4, −2, 0 mm, approximately 181 px/mm. The L10 clear scan span between columns 1458 and 2182 corroborates 4 mm along x. y-grid rows near 734, 913, 1095, 1275, 1454, 1636 correspond to 33, 32, 31, 30, 29, 28 mm; endpoint scale is 180.4 px/mm. These are plotting coordinates, not the part’s x/y origin.

At u=1600 (also checked at u=1700 and 2000), the four internal members are visible as six scan lines. Single-line centers are v=1357 and 1068; the lower double uses centers 1211 and 1232, and the upper double 922 and 944. In increasing plotted y this is single, double, single, double. Outer hatch extremes have centers v=688.5 and 1572, with midpoint 1130.25. Center this extent within the known 5 mm width and use `partY = 2.5 + (1130.25-v)/180.4`. This gives about [1.243,1.994,2.845,3.593] mm; nominal placements rounded to 0.05 mm are [1.25,2.00,2.85,3.60] mm. The ±0.20 mm tolerance covers line-center uncertainty, rounding, and unknown hatch inset/scan-to-surface registration. OQ2 records this centering assumption. The thickness of the brown ink and spacing between a double’s tracks do not measure fused physical wall width.

**Reference measurements.** `reference/reference.json` records identity rotation, unit scale 1.0 mm, and min-datum translation approximately [−3.58e−15,0,0] mm, numerically zero. Reproduce this frame directly. Each section’s `bounds_2d` must be transformed using its own `to_3d` matrix. The z=3 section then yields the exact foot intervals in §3; z=12.3 yields the exact tab intervals. Ingest values are `measured (reference model)` evidence, not drawing measurements. The reference figure sheets and silhouettes were visually inspected. The original STL was read in memory with trimesh for a signed-shell check; no source, reference or geometry file was modified.

The six mesh components are one positive-volume exterior shell (3732.5 mm³) and five negative-volume cavity shells (sum −53.43999672 mm³), all watertight. This is compatible with one connected material solid containing five enclosed cavities; six triangle components must not become six positive CAD bodies. Reference inner wall centers are approximately [1.4241,2.1691,3.0241,3.7691] mm with widths [0.11,0.22,0.11,0.22] mm. Their ≈0.17 mm placement offset relative to the scan-plot estimate is disclosed in OQ2 and is within the adopted image band.

## 5. Measurement and inference record

All tolerances below are digital comparison bands in the shown units; count bands of 0.01 reject an off-by-one count. Inferred dimensions describe the chosen editable nominal model, with physical uncertainty separately disclosed. Angles in all trigonometric expressions are in degrees.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|
| `overallLength` | 75 mm | ±0.01 | stated | sources/nist-amb2022-01-description.md §2.1.3: "75 mm long"; Figure 3 top dimension. Tip-to-far-end distance; Figure 3 dimension 75 controls. |
| `overallWidth` | 5 mm | ±0.01 | stated | sources/nist-amb2022-01-description.md §2.1.3: "5 mm wide"; Figure 3 plan dimension 5. Distance from the lower long side in the plan to the upper long side. |
| `bodyHeight` | 12 mm | ±0.01 | stated | sources/nist-amb2022-01-description.md §2.1.3: "12 mm tall"; §Process facts: tabs begin at 12 mm; Figure 3 elevation dimension 12. Build plate to main bridge top, excluding the raised tabs. Tabs translate with this top. |
| `noseAngle` | 45 deg | ±0.1 | stated | sources/nist-amb2022-01-description.md §2.1.3: "45° taper"; Figure 3 left plan angle. Each nose flank makes 45 degrees with x in plan; the included tip angle is 90 degrees. |
| `noseLength` | 2.5 mm | ±0.1 | derived | `overallWidth / (2 * tan(noseAngle))`. Tip plane to full-width shoulder. Figure 3 explicitly labels this length 2.5. |
| `legCount` | 12 (count) | ±0.01 | stated | sources/nist-amb2022-01-description.md §1: "12 legs of varying size"; Figure 4 leg numbering. Twelve numbered feet L1-L12, excluding the tall tapered end block. |
| `largeLegWidth` | 5 mm | ±0.1 | measured | sources/nist-figure3-drawing.png elevation, far-right 5 callout; pixel columns 2766 to 2936, about 170 px. x width of L1, L4, L7 and hollow L10. |
| `mediumLegWidth` | 2.5 mm | ±0.1 | measured | sources/nist-figure3-drawing.png elevation, 2.5 callout; pixel columns 2528 to 2613, about 85 px. x width of L3, L6, L9 and L12. |
| `smallLegWidth` | 0.5 mm | ±0.1 | measured | sources/nist-figure3-drawing.png elevation, 0.5 callout; pixel columns 2681 to 2698, about 17 px. x width of L2, L5, L8 and L11; independent of the L10 outer-wall thickness. |
| `gapWidth` | 2 mm | ±0.1 | measured | sources/nist-figure3-drawing.png elevation, bottom 2 callout; pixel columns 2698 to 2766, about 68 px. x width of each of the twelve open-bottom gaps. |
| `overhangAngle` | 45 deg | ±0.1 | stated | sources/nist-amb2022-01-description.md §2.1.3: "45° overhangs"; Figure 3 elevation angle. Roof of each open-bottom gap rises toward +x; angle measured from x in elevation. |
| `legMergeHeight` | 7 mm | ±0.01 | stated | sources/nist-amb2022-01-description.md §2.3: "height of 7 mm", where the gaps between legs merge. z at the high end of the gap roofs, above which the bridge is continuous. |
| `gapLowHeight` | 5 mm | ±0.1 | derived | `legMergeHeight - gapWidth * tan(overhangAngle)`. z at the left/low end of every gap roof; corroborated by the Figure 3 right-hand 5 and 2 dimensions. |
| `legGroupCount` | 4 (count) | ±0.01 | derived | `legCount / 3`. Four triplets, each ordered medium, small, large when walking in +x. |
| `legGroupPitch` | 14 mm | ±0.15 | derived | `mediumLegWidth + smallLegWidth + largeLegWidth + 3 * gapWidth`. Triplet length including three gaps; corroborated by Figure 3 bottom 14 dimension, columns 2460 to 2936. |
| `endBlockLength` | 19 mm | ±0.15 | derived | `overallLength - legGroupCount * legGroupPitch`. End-block foot extends from x=0 to this position, before the first gap. Figure 3 columns 382 to 1030 corroborate about 19.03 mm. |
| `tabCount` | 11 (count) | ±0.01 | stated | sources/nist-amb2022-01-description.md §2.3: "11 tabs on top"; §3.4: "11 ridges"; counted in Figure 3. Eleven full-width raised metrology ridges. |
| `tabWidth` | 1 mm | ±0.1 | measured | sources/nist-figure3-drawing.png plan far-right 1 callout; columns 2901 to 2936, about 35 px. x width of every top tab. |
| `tabPitch` | 7 mm | ±0.1 | measured | sources/nist-figure3-drawing.png plan far-right 7 callout; columns 2698 to 2936, about 238 px. Pitch between corresponding edges of consecutive tabs. |
| `tabHeight` | 0.5 mm | ±0.1 | measured | sources/nist-figure3-drawing.png elevation left 0.5 callout; tab crests near row 1069, main top near row 1085. Tab rise above bodyHeight; this makes the total height 12.5 mm. |
| `firstTabX` | 4 mm | ±0.15 | derived | `overallLength - tabWidth - (tabCount - 1) * tabPitch`. Start of tab 1 counted from the nose. The final tab ends at overallLength. |
| `l10StartX` | 28 mm | ±0.15 | derived | `endBlockLength + mediumLegWidth + smallLegWidth + 3 * gapWidth`. Left boundary of hollow L10, the large foot of the first triplet after the end block. |
| `l10OuterWallThickness` | 0.5 mm | ±0.1 | stated | sources/nist-amb2022-01-description.md §2.1.3: "outer walls ... approximately 0.5 mm thick". Nominal thickness of all four L10 outer walls; source says approximately. Retain square external L10 footprint. |
| `l10BaseThickness` | 1 mm | ±0.01 | stated | sources/nist-amb2022-01-description.md §2.1.3: "solid base that is 1 mm thick"; Figure 3 1.0 callout. Solid base below every L10 pocket; cavity floors are at this z. |
| `thinWallHeight` | 4 mm | ±0.01 | stated | sources/nist-amb2022-01-description.md §2.1.3: "walls are built 4 mm high before a flat-bottomed ceiling"; Figure 3 4.0 callout. Height of four internal walls and five adjacent void pockets, measured above the solid base. |
| `l10CavityLength` | 4 mm | ±0.2 | derived | `largeLegWidth - 2 * l10OuterWallThickness`. Clear x length between L10 outer walls; matches the Figure 3 horizontal 4 callout. |
| `l10CavityWidth` | 4 mm | ±0.2 | derived | `overallWidth - 2 * l10OuterWallThickness`. Clear y width before installing internal thin walls. |
| `l10CavityStartX` | 28.5 mm | ±0.15 | derived | `l10StartX + l10OuterWallThickness`. Left end of all five void pockets and all four internal wall spans. |
| `l10CeilingZ` | 5 mm | ±0.02 | derived | `l10BaseThickness + thinWallHeight`. Flat downward-facing cavity ceiling; material continues into the overhang and bridge above it. |
| `thinWallCount` | 4 (count) | ±0.01 | stated | sources/nist-amb2022-01-description.md §2.1.3: "four thin-wall structures", two single-track and two double-track; Figure 4 labels. Four distinct physical walls: single, double, single, double in increasing y; two walls of each width. |
| `singleTrackWidth` | 0.1 mm | ±0.08 | inferred | The supplied description gives only a laser spot diameter on the order of 0.1 mm. Use 0.10 mm as a necessary editable starting value, with a wide ±0.08 mm digital band. Neither laser spot size nor raster stroke thickness fixes the fused-wall width. The inspection mesh uses about 0.11 mm, which is corroboration of scale only. Open question OQ1 remains. Provisional physical thickness of each single-track wall; not an as-built measurement. |
| `doubleTrackWidth` | 0.2 mm | ±0.15 | inferred | Use 0.20 mm as a necessary starting value, twice the nominal 0.10 mm spot scale, with a wide ±0.15 mm band. Track overlap and melt-pool width are unspecified, so this is not an enforced 2:1 relationship. The inspection mesh uses about 0.22 mm. Open question OQ1 remains. Provisional physical thickness of each double-track wall; independent of singleTrackWidth for editing. |
| `wall1CenterY` | 1.25 mm | ±0.2 | measured | sources/nist-figure4-legs-thinwalls.png 3900x1771 raster: single line centered at row 1357; y = overallWidth/2 + (1130.25 - row)/180.4, rounded to 0.05 mm; see brief §4. Center of internal wall 1 along y, measured from the lower long-side datum; single track. Graphical placement remains qualified by OQ2. |
| `wall2CenterY` | 2 mm | ±0.2 | measured | sources/nist-figure4-legs-thinwalls.png 3900x1771 raster: double lines centered at rows 1211 and 1232 (mean 1221.5); y = overallWidth/2 + (1130.25 - row)/180.4, rounded to 0.05 mm; see brief §4. Center of internal wall 2 along y, measured from the lower long-side datum; double track. Graphical placement remains qualified by OQ2. |
| `wall3CenterY` | 2.85 mm | ±0.2 | measured | sources/nist-figure4-legs-thinwalls.png 3900x1771 raster: single line centered at row 1068; y = overallWidth/2 + (1130.25 - row)/180.4, rounded to 0.05 mm; see brief §4. Center of internal wall 3 along y, measured from the lower long-side datum; single track. Graphical placement remains qualified by OQ2. |
| `wall4CenterY` | 3.6 mm | ±0.2 | measured | sources/nist-figure4-legs-thinwalls.png 3900x1771 raster: double lines centered at rows 922 and 944 (mean 933); y = overallWidth/2 + (1130.25 - row)/180.4, rounded to 0.05 mm; see brief §4. Center of internal wall 4 along y, measured from the lower long-side datum; double track. Graphical placement remains qualified by OQ2. |

Parameter provenance totals: stated=12, derived=11, measured=11, inferred=2. No parameter is copied solely from reference-model measurements, and no template geometric default is retained. Reference measurements appear below as independent comparison evidence.

**Analytic construction and first moments.** Define `A=overallWidth*(overallLength-noseLength/2)=368.75 mm²`, `k=tan(overhangAngle)=1`, `g=gapWidth=2`, `h0=gapLowHeight=5`, and `Q=g*(h0+legMergeHeight)/2=12 mm²`. The body prism volume is 4425 mm³. Eleven tabs add 27.5 mm³; twelve open-bottom gap prisms remove 720 mm³; the unpartitioned L10 cavity removes 64 mm³; the four ribs restore `l10CavityLength*thinWallHeight*(2*singleTrackWidth+2*doubleTrackWidth)=9.6 mm³`. Total nominal volume is **3678.10 mm³**.

| signed term | volume (mm³) | centroid formula / nominal location (mm) |
|---|---|---|
| Pentagonal body | +4425 | x=(overallWidth*overallLength²/2 − overallWidth*noseLength²/6)/A = 38.121468927; y=overallWidth/2; z=bodyHeight/2. |
| Each of 11 tabs | +2.5 | [firstTabX+i*tabPitch+tabWidth/2, overallWidth/2, bodyHeight+tabHeight/2], i=0..10. |
| Each of 12 gaps | −60 | [a+xg, overallWidth/2, zg], where a is the gap left edge; xg=(h0*g²/2+k*g³/3)/Q=1.055555556; zg=(h0²*g/2+h0*k*g²/2+k²*g³/6)/Q=3.027777778. |
| Gross L10 cavity | −64 | [l10CavityStartX+l10CavityLength/2, overallWidth/2, l10BaseThickness+thinWallHeight/2]=[30.5,2.5,3]. |
| Internal walls 1..4 | +[1.6,3.2,1.6,3.2] | [30.5,wallCenterY,3], with the four y positions in the parameter table. |

`C = Σ(vᵢ cᵢ)/Σvᵢ`. The signed first moments are `[135794.55,9195.73,24543.675] mm⁴`, giving **[36.919754765,2.500130502,6.672922161] mm**. The small y asymmetry follows the measured, non-symmetric wall positions. Since the schema’s `PointQuantity` has no `note` field, its formula is also retained in `acceptance.volume.note`.

**Surface area.** Let `P=2*(overallLength-noseLength)+overallWidth+2*sqrt(noseLength²+(overallWidth/2)²)=157.071067812 mm`. The uncut body area is `2*A+P*bodyHeight`; tabs add `2*tabCount*tabHeight*(overallWidth+tabWidth)`. Each gap changes area by `overallWidth*(gapLowHeight+legMergeHeight+sqrt(gapWidth²+(legMergeHeight-gapLowHeight)²)-gapWidth)-2*Q`. This gives exterior area **3170.058441227 mm²**. For five pocket widths q=[0.7,0.6,0.7,0.6,0.8] mm, sum each rectangular void’s six faces: `Svoid=2*((l10CavityLength+thinWallHeight)*Σq+(thinWallCount+1)*l10CavityLength*thinWallHeight)=214.4 mm²`. Total material boundary area, including sealed interiors, is **3384.458441227 mm²**.

**Acceptance values.** Section areas are total material areas; `loops` counts outer material boundaries and `holes` counts enclosed inner boundaries. Count probes use outer-loop counts, so the twelve feet plus end block give 13, and four ribs are verified by five holes and individual material probes. A section can have several islands while the 3D part remains one solid. All solid/void points avoid nominal boundaries.

| acceptance value | expected | tolerance / band | provenance | formula / evidence |
|---|---|---|---|
| envelope.min | [0,0,0] mm | ±0.10 mm per coordinate | stated frame | Intersection of the three datum planes; matches ingest min datum. |
| envelope.max | [75,5,12.5] mm | ±0.10 mm per coordinate | derived / stated | [overallLength,overallWidth,bodyHeight+tabHeight]; Figure 3. |
| acceptance.bbox_tolerance | 0.10 mm | Absolute bound comparison | defaulted digital policy | Matches reference.json suggested.envelope.tolerance and drawing raster uncertainty. |
| acceptance.volume | 3678.10 mm³ | ±0.2% = ±7.3562 mm³ | derived | Signed prism/cavity/rib sum above; exact nominal values, not a claim about fused-track manufacturing accuracy. |
| acceptance.surface_area | 3384.458441227 mm² | ±0.2% = ±6.768916882 mm² | derived | Exterior plus five pocket boundaries above. |
| acceptance.center_of_mass | [36.919754765,2.500130502,6.672922161] mm | ±0.25 mm per axis | derived | Signed first moments / total volume; digital band retained from the reference suggestion. |
| acceptance.solid_count | 1 | Exact | stated | User requirement; one connected material solid with five internal shells. |
| acceptance.blockout.volume_min | 4600.15625 mm³ | Lower bound | derived | 0.998*A*(bodyHeight+tabHeight). |
| acceptance.blockout.volume_max | 4618.59375 mm³ | Upper bound | derived | 1.002*A*(bodyHeight+tabHeight). |
| acceptance.deviation.p95_max | 0.20 mm | Maximum | measured (reference model) policy | reference.json suggested.acceptance.deviation.p95_max, used unchanged. |
| acceptance.deviation.hausdorff_max | 0.50 mm | Maximum | measured (reference model) policy | reference.json suggested.acceptance.deviation.hausdorff_max, used unchanged. |
| acceptance.deviation.silhouette_iou_min | 0.98 | Minimum | measured (reference model) policy | reference.json suggested.acceptance.deviation.silhouette_iou_min, used unchanged. |
| acceptance.export_volume_tolerance_rel | 0.002 | 0.2% relative agreement | defaulted digital policy | Retain the schema default for KCL/STEP/STL consistency. |
| section `feetBelowCavity` | z=0.5 mm; A=248.75 mm²; loops=13; holes=0 | Area ±1%; counts exact | derived | Derived: Aplan - legCount*gapWidth*overallWidth = 248.75 mm2. The end block and twelve separate feet give 13 outer loops; L10 is solid below its 1 mm cavity floor. |
| section `feetAndThinWalls` | z=3 mm; A=235.15 mm²; loops=13; holes=5 | Area ±1%; counts exact | derived | Derived: 248.75 - l10CavityLength*(l10CavityWidth - 2*singleTrackWidth - 2*doubleTrackWidth). L10 is one ring-and-ribs region with five holes; total outer loops remain 13. |
| section `overhangs` | z=6 mm; A=308.75 mm²; loops=13; holes=0 | Area ±1%; counts exact | derived | Derived: Aplan - legCount*overallWidth*(gapWidth - (6-gapLowHeight)/tan(overhangAngle)). At z=6 each gap has narrowed from 2 mm to 1 mm toward its +x end. |
| section `solidBridge` | z=9 mm; A=368.75 mm²; loops=1; holes=0 | Area ±1%; counts exact | derived | Derived: Aplan = overallWidth*(overallLength - noseLength/2). The entire pentagonal plan is solid above the 7 mm gap closure. |
| section `topTabs` | z=12.25 mm; A=55 mm²; loops=11; holes=0 | Area ±1%; counts exact | derived | Derived: tabCount*tabWidth*overallWidth = 55 mm2. Eleven disconnected section islands, each 1 by 5 mm, connected to the same body below. |
| section `l10Transverse` | x=30.5 mm; A=46.4 mm²; loops=1; holes=5 | Area ±1%; counts exact | derived | Derived: overallWidth*bodyHeight - thinWallHeight*(l10CavityWidth - 2*singleTrackWidth - 2*doubleTrackWidth). This cut misses the top tabs and exposes the four walls, solid base, flat ceiling, and five sealed holes. |
| section `longitudinalPocket` | y=2.5 mm; A=745.5 mm²; loops=1; holes=1 | Area ±1%; counts exact | derived | Derived: overallLength*bodyHeight + tabCount*tabWidth*tabHeight - legCount*Q - l10CavityLength*thinWallHeight; Q=gapWidth*(gapLowHeight+legMergeHeight)/2. This center plane passes through pocket 3 and the nose tip. |
| section `longitudinalSingleWall` | y=1.25 mm; A=746.5 mm²; loops=1; holes=0 | Area ±1%; counts exact | derived | Derived: (overallLength - abs(1.25-overallWidth/2)/tan(noseAngle))*bodyHeight + tabCount*tabWidth*tabHeight - legCount*Q. This plane lies in wall 1, so the L10 cavity is bridged by solid material at z=1..5. |
| face `buildPlateEndBlock` | z=0, normal -z; in-plane center [10.1103286385, 2.5]; A=88.75 mm² | Plane/center ±0.10 mm; area ±1% | derived | endBlockLength*overallWidth - noseLength*overallWidth/2; centroid x = (overallWidth*endBlockLength^2/2 - overallWidth*noseLength^2/6)/area. |
| face `buildPlateL1` | z=0, normal -z; in-plane center [72.5, 2.5]; A=25 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L1 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL2` | z=0, normal -z; in-plane center [67.75, 2.5]; A=2.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L2 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL3` | z=0, normal -z; in-plane center [64.25, 2.5]; A=12.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L3 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL4` | z=0, normal -z; in-plane center [58.5, 2.5]; A=25 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L4 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL5` | z=0, normal -z; in-plane center [53.75, 2.5]; A=2.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L5 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL6` | z=0, normal -z; in-plane center [50.25, 2.5]; A=12.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L6 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL7` | z=0, normal -z; in-plane center [44.5, 2.5]; A=25 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L7 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL8` | z=0, normal -z; in-plane center [39.75, 2.5]; A=2.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L8 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL9` | z=0, normal -z; in-plane center [36.25, 2.5]; A=12.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L9 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL10` | z=0, normal -z; in-plane center [30.5, 2.5]; A=25 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L10 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL11` | z=0, normal -z; in-plane center [25.75, 2.5]; A=2.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L11 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `buildPlateL12` | z=0, normal -z; in-plane center [22.25, 2.5]; A=12.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | (L12 x width)*overallWidth; centroid is the midpoint of its interval in §3. |
| face `sideDatumY0` | y=0, normal -y; A=731.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | (overallLength-noseLength)*bodyHeight - legCount*Q + tabCount*tabWidth*tabHeight. |
| face `oppositeSideY5` | y=5, normal +y; A=731.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | Same area as sideDatumY0 by external symmetry. |
| face `farEndX75` | x=75, normal +x; A=62.5 mm² | Plane/center ±0.10 mm; area ±1% | derived | overallWidth*(bodyHeight+tabHeight); last tab ends flush at the far end. |
| face `tabTop01` | z=12.5, normal +z; in-plane center [4.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop02` | z=12.5, normal +z; in-plane center [11.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop03` | z=12.5, normal +z; in-plane center [18.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop04` | z=12.5, normal +z; in-plane center [25.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop05` | z=12.5, normal +z; in-plane center [32.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop06` | z=12.5, normal +z; in-plane center [39.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop07` | z=12.5, normal +z; in-plane center [46.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop08` | z=12.5, normal +z; in-plane center [53.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop09` | z=12.5, normal +z; in-plane center [60.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop10` | z=12.5, normal +z; in-plane center [67.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `tabTop11` | z=12.5, normal +z; in-plane center [74.5, 2.5]; A=5 mm² | Plane/center ±0.10 mm; area ±1% | derived | tabWidth*overallWidth; center x=firstTabX+i*tabPitch+tabWidth/2, i counted from zero. |
| face `l10Pocket1Floor` | z=1, normal +z; in-plane center [30.5, 0.85]; A=2.8 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(1.2-0.5); cavity-facing base at z=l10BaseThickness. |
| face `l10Pocket1Ceiling` | z=5, normal -z; in-plane center [30.5, 0.85]; A=2.8 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(1.2-0.5); cavity-facing flat roof at z=l10CeilingZ. |
| face `l10Pocket2Floor` | z=1, normal +z; in-plane center [30.5, 1.6]; A=2.4 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(1.9-1.3); cavity-facing base at z=l10BaseThickness. |
| face `l10Pocket2Ceiling` | z=5, normal -z; in-plane center [30.5, 1.6]; A=2.4 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(1.9-1.3); cavity-facing flat roof at z=l10CeilingZ. |
| face `l10Pocket3Floor` | z=1, normal +z; in-plane center [30.5, 2.45]; A=2.8 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(2.8-2.1); cavity-facing base at z=l10BaseThickness. |
| face `l10Pocket3Ceiling` | z=5, normal -z; in-plane center [30.5, 2.45]; A=2.8 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(2.8-2.1); cavity-facing flat roof at z=l10CeilingZ. |
| face `l10Pocket4Floor` | z=1, normal +z; in-plane center [30.5, 3.2]; A=2.4 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(3.5-2.9); cavity-facing base at z=l10BaseThickness. |
| face `l10Pocket4Ceiling` | z=5, normal -z; in-plane center [30.5, 3.2]; A=2.4 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(3.5-2.9); cavity-facing flat roof at z=l10CeilingZ. |
| face `l10Pocket5Floor` | z=1, normal +z; in-plane center [30.5, 4.1]; A=3.2 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(4.5-3.7); cavity-facing base at z=l10BaseThickness. |
| face `l10Pocket5Ceiling` | z=5, normal -z; in-plane center [30.5, 4.1]; A=3.2 mm² | Plane/center ±0.10 mm; area ±1% | derived | l10CavityLength*(4.5-3.7); cavity-facing flat roof at z=l10CeilingZ. |

Named face centers use the remaining world axes in order: (x,y) on z planes, (x,z) on y planes, and (y,z) on x planes. Pocket floor normals point +z into the void; ceiling normals point −z. The two inclined nose faces are outside the schema’s axis-aligned `face` probe format and are instead covered by plan-section, bbox, and material/void probes.

**Blockout definition.** Use one primary pentagonal envelope prism with the same nose plan, extruded to `bodyHeight+tabHeight=12.5`. It fills all leg gaps, L10 voids and tab valleys, with no patterns or pocket operations. Its analytic volume is `A*12.5=4609.375 mm³`; the explicit ±0.2% band is [4600.15625,4618.59375] mm³. It reproduces the final bbox while postponing all small features. This is a blockout target, not the final-part volume.

**Independent reference comparison.** Values below come from `reference/reference.json` and have `measured (reference model)` provenance. The nominal analytic contract is derived independently from the source dimensions and disclosed assumptions.

| reference evidence | measured | nominal reconstruction | comparison / suggested tolerance |
|---|---|---|---|
| measurements.size / anchor | [75,5,12.5] mm | [75,5,12.5] mm | Exact nominal agreement; suggested envelope ±0.10 mm. |
| measurements.volume | 3679.060003280461 mm³ | 3678.10 mm³ | Reference minus nominal +0.96000328 mm³ (0.0261%); suggested reference-volume band ±1%. Difference follows the total track-width change 0.66−0.60 mm times 4×4 mm. |
| measurements.surface_area | 3383.498437946426 mm² | 3384.458441227157 mm² | Reference minus nominal −0.96000328 mm²; ingest supplies no separate area tolerance. |
| measurements.center_of_mass | [36.918079612,2.500633667,6.671963759] mm | [36.919754765,2.500130502,6.672922161] mm | Reference minus nominal [−0.001675152,+0.000503164,−0.000958402] mm; suggested ±0.25 mm per axis. |
| z=3 section | A=235.390000820 mm²; loops=13; holes=5 | A=235.15; loops=13; holes=5 | Area difference +0.240000820 mm² follows track widths; section topology agrees. |
| z=6 section | A=308.75 mm²; loops=13; holes=0 | Same | Agreement to floating-point precision. |
| z=9 section | A=368.75 mm²; loops=1; holes=0 | Same | Agreement to floating-point precision. |
| z=12.3 section | A=55 mm²; loops=11; holes=0 | A=55 at contract z=12.25 | Both cuts lie within tab height; exact nominal agreement. |
| x=30.5 section | A=46.640000820 mm²; loops=1; holes=5 | A=46.4; loops=1; holes=5 | Area difference +0.240000820 mm² follows track widths. |
| measurements.components / watertight | 6 / true | 1 material solid, 6 boundary shells | Signed-shell inspection resolves the five components as inward cavity shells, not five extra bodies. |

**Edit tests.** Rebuild each edit independently, with every other top-level parameter held fixed. No edit targets a derived parameter. Tabs must start at the current `bodyHeight`; they must not use a hard-coded z=12. The inferred widths are separate controls, so increasing the single-track value must not force a double-track change. Body height, tab height and track width do not invalidate any other derived parameter in this contract.

| parameter edit | expected volume change | direction | bbox-size change [x,y,z] (mm) | tolerance / formula |
|---|---|---|---|---|
| bodyHeight +1 mm | +368.75 mm³ | increase | [0,0,1] | ±2% on delta; ΔV=A*ΔbodyHeight. All tabs translate upward without changing their own volume. |
| tabHeight +0.25 mm | +13.75 mm³ | increase | [0,0,0.25] | ±2% on delta; ΔV=tabCount*tabWidth*overallWidth*ΔtabHeight. |
| singleTrackWidth +0.05 mm | +1.60 mm³ | increase | [0,0,0] | ±2% on delta; ΔV=2*l10CavityLength*thinWallHeight*ΔsingleTrackWidth. All five void intervals remain positive. |

Bbox edit deltas use the contract 0.10 mm absolute comparison threshold. Baseline release geometry and exports must remain unchanged by tests. Use only sanity assertions in KCL, never equality locks between independent parameters. Final geometry verification must include format, lint, engine analysis, and authoritative OpenCascade checks on deterministic STEP, then STL/STEP agreement and the declared reference deviation gates. No KCL, STEP, STL or hosted-engine validation is claimed by this bundle-drafting task.

**Bundle verification performed.** From `/Users/danieldriscoll/dual/opencad`, `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m opencad check-bundle /Users/danieldriscoll/dual/opencad/designs/.staging-nist-amb2022-01-bridge-mesh --name nist-amb2022-01-bridge-mesh` printed `ok:` with 36 parameters and 11 features. In-memory Python checks using YAML, hashlib, trimesh and Shapely confirmed all ten source/reference digests, the complete inventory, all eight section area/topology expectations, 108 material/void probes and all 37 face areas, centers and normal signs. Independent integration of horizontal sections gave volume 3678.0999999999995 mm³ versus expected 3678.10, and centroid [36.9197547646883,2.500130502161442,6.672922160898291] mm versus the rounded contract values. This is the centroid of uniform-density material with empty geometric pockets; it assigns no density to trapped powder. The inspected reference exterior area plus the independently summed nominal pocket faces gave 3384.4584412270656 mm² versus expected 3384.458441227157. The three integrated edit deltas were 368.75000000000045, 13.75000000000091 and 1.599999999999909 mm³ versus expected 368.75, 13.75 and 1.60, with the declared bbox changes. These are analytic and planar-geometry checks; downstream KCL and export validation are still required.

## 6. Defaults retained

- Units remain mm and deg; this is explicitly required by the sources and user. Schema version 1 and release status `reconstruction` remain appropriate.
- Material and density remain null because the supplied excerpts do not select an alloy or density. LPBF is explicitly stated. No mass is calculated.
- All geometric template dimensions were replaced. Counts use a nonzero 0.01 digital band to reject integer changes. Area probes use ±1%; nominal volume and total area use ±0.2%. These are computational comparison settings, not manufacturing allowances.
- Bbox ±0.10 mm, center-of-mass ±0.25 mm and deviation limits are retained from the ingest suggestion. The wider reference-volume suggestion ±1% is recorded for comparison; the analytic nominal-volume gate uses its own ±0.2% band.
- Export volume agreement retains the schema default 0.002. Edit-test volume changes use ±2%, with the bbox threshold as above. All features are required (`optional: false`); no cosmetic material geometry has been added.

## 7. Unrepresentable or low-confidence features

The single- and double-track widths are deliberately provisional. Laser spot diameter, path stroke thickness and track separation do not determine solid fused-wall thickness. Figure 4 positions are measurements of scan paths, with a disclosed registration assumption; the nominal reference-wall placement differs within the adopted band. Their widths and y positions stay editable. Neither issue justifies changing any external dimension from Figure 3.

The annotations, thermography rectangle, recoating arrow, leg labels and hatch strokes carry explanatory information and are not geometric relief. Melt-pool shape, roughness, trapped powder, EDM kerf, skim-cut removal and post-build distortion are not dimensioned in this geometry source bundle and are outside this nominal reconstruction. No undocumented fillets, radii or relief cuts are introduced. The axis-aligned face schema cannot name the sloped nose or overhang faces through a face-normal probe; their section and inside/outside tests encode the required shape.

- OQ1: What are the physical single-track and double-track wall widths? Pending a dimensional or melt-track source, use singleTrackWidth=0.10 ±0.08 mm and doubleTrackWidth=0.20 ±0.15 mm. The inspection mesh encodes about 0.11/0.22 mm, but does not establish as-built track widths.
- OQ2: What is the exact mapping from Figure 4 scan centerlines to the physical y-side datum? Use wall centers [1.25, 2.00, 2.85, 3.60] mm with ±0.20 mm image-measurement tolerance; the inspection mesh places them about 0.17 mm higher. The nominal mapping centers the shown hatch range within the 5 mm width.
- OQ3: Which alloy and density apply to this individual specimen? The supplied excerpts identify a metal-alloy LPBF bridge without selecting an alloy or density; both material and density remain unspecified.

Downstream KCL construction, one-solid STEP topology, actual exported area/volume/COM, all material and face probes, edit rebuilds, and reference-surface deviations remain to be verified after modeling. The current task verifies the contract schema, source inventory, pixel evidence and analytical consistency only.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [0.0, 0.0, 0.0] → [75.0, 5.0, 12.5] | 4609.374999999999 | pass | 2026-09-15T17:12:17Z: within envelope and band |
