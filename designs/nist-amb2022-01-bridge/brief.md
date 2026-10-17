# nist-amb2022-01-bridge — design brief

## 1. Intent and configuration

Reconstruct the NIST AMB2022-01 individual bridge artifact as editable, parameterized KCL from the attached NIST description excerpts and figures; Figure 3 is the dimensioned plan and elevation drawing and is authoritative for every external dimension. Frame: x along the 75 mm length with x = 0 at the pointed (45 degree tapered) end and x increasing toward the far end, y across the 5 mm width with y = 0 at one long side face, z vertical from the build plate (z = 0) upward. Model the tapered nose, the tall solid end block, the twelve legs with their 45 degree overhangs merging into the solid bridge, the eleven 1 mm wide top tabs on a 7 mm pitch, and the hollow leg L10 with its 0.5 mm outer walls, 1 mm base, four 4 mm tall internal thin walls parallel to x, and flat ceiling, exactly as documented. Where the sources do not fix a dimension (the single- and double-track thin-wall widths), record it as an open question and use a clearly labelled inferred value with a wide tolerance rather than approximating silently. One solid; export STEP and STL. Reference geometry supplied by NIST is for inspection only: the deliverable must be editable construction, never an import.

This bundle specifies the nominal individual bridge before ridge skim cutting, EDM release, or distortion. It excludes the build plate, recoater guides, neighboring bridges, scan-path graphics, and colored measurement overlays. The documented dimensions are nominal geometry; contract tolerances are digital comparison thresholds, not manufacturing or as-built tolerances. No reference mesh or CAD file was supplied or ingested.

This drafting stage produces only `contract.yaml` and this brief. The later construction must declare all 40 contract parameters as editable top-level KCL constants, use native KCL sketches/features, produce one connected solid with five enclosed L10 void compartments, and export deterministic STEP and STL. Use the NIST reference geometry only for inspection if it is supplied later. The parameter inventory is **25 stated, 9 derived, 4 measured, 2 inferred; zero defaulted and zero measured from a reference model**.

The author read the `kcl-docs` and `zoo-tooling` skills before drafting. Future modeling must use the repository's KCL 2 construction conventions and run format, lint, physical-property analysis, and export verification. No KCL or exported model is part of this draft.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/nist-amb2022-01-description.md | text | authoritative | ad20b8b64ceffc5122b055fd97c5e12b4b89b3cd2d52876ba74afb4d66cf2094 | Geometry excerpts; NIST page inspected 2026-09-15. Units: mm; deg for angles. Supplied local geometry description, counts, L10 construction, and LPBF context. External dimensions defer to Figure 3. The text says recoating proceeds left; the supplied frame and Figure 3 arrow fix +x toward the far end. |
| sources/nist-figure3-drawing.png | drawing | authoritative | a2377f44a5d37ee5e2193817bc33f079d664fae8c9df7bd675480f9e97b37d49 | NIST Figure 3; updated 2023-09-20; supplied copy inspected 2026-09-15. Units: mm; deg for angles. Authoritative for every external dimension. Native image 3127 x 1821 pixels; explicit labels outrank raster scaling. |
| sources/nist-figure4-legs-thinwalls.png | image | authoritative | a55dce91299778420a4970d51478be5856a89b291644459d93b7cb71524b7417 | NIST Figure 4; revision not stated; supplied copy inspected 2026-09-15. Units: mm; deg for angles. Leg numbering and internal-wall topology; scan-path centerlines support only approximate transverse placements. Native image 3900 x 1771 pixels. Stroke width is not a finished-wall dimension. |
| sources/nist-figure1-overview.png | image | illustrative | 8cfc5aa92c73cb51cae87d1238b865d1c33565d5757e27244c19eb1e90e62142 | NIST Figure 1; revision not stated; supplied copy inspected 2026-09-15. Units: mm; deg for angles. Native image 3448 x 1708 pixels. Qualitative perspective check of leg labels, 14 mm repeats, pointed end, tabs, and hollow L10; no dimensional measurement from perspective. |

All four source-file hashes were computed from the supplied bytes and match the supplied SHA-256 prefixes. The supplied description is an excerpt of the NIST AM Bench geometry page, not a reference-model ingest. The authority order is Figure 3 for all external dimensions, the description for L10 construction and counts, Figure 4 for leg numbering/internal topology and approximate wall locations, and Figure 1 for qualitative confirmation. No entries under `reference/` exist.

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Part identity and construction | nist-amb2022-01 individual bridge; native editable KCL; STEP and STL | — | User intent | Exact configuration | required |
| Envelope and origin | [0,0,0] to [75,5,12.5]; actual nose bottom at [0,2.5,0] | mm | Figure 3; user frame | 0.02 per envelope coordinate | stated + derived |
| Body size | 75 long, 5 wide, 12 high excluding tabs | mm | Figure 3: 75, 5, 12 labels | 0.01 per parameter | stated |
| Plan taper | 2.5 axial length, two 45° flanks; full body height | mm; deg | Figure 3 plan | 0.01 mm; 0.1 deg | stated |
| Solid end block | x=0..19, including nose; solid before first underside gap | mm | 75 minus four 14 mm repeats; Figure 3 elevation | 0.01 on derived length | derived |
| Leg pattern | 12 legs; four repeats; +x sequence gap / 2.5 leg / gap / 0.5 leg / gap / 5 leg | count; mm | Description §1; Figures 1, 3, 4 | 0.01 on dimensions and counts; counts integral | stated + derived |
| Gap and overhang | 2 gap; ceiling rises from z=5 to z=7 toward +x at 45° | mm; deg | Figure 3 lower elevation; description Layer 175 | 0.01 mm; 0.1 deg | stated + derived |
| Tabs | 11 tabs, 1 wide along x, 7 pitch, full 5 width, 0.5 tall; first x=4, last x=74 | mm; count | Figure 3; description §2.3 | 0.01 per parameter | stated + derived |
| L10 outside and shell | x=28..33, y=0..5; four nominal 0.5 outer walls; all other legs solid | mm | Description §2.1.3; Figures 3 and 4 | 0.10 outer wall; 0.01 other values | stated + derived |
| L10 cavity and closure | x=28.5..32.5; y=0.5..4.5; z=1..5; sealed with a flat ceiling | mm | Figure 3 inset; description §2.1.3 | 0.01 stated x/z dimensions; 0.20 derived cavity width | stated + derived |
| Internal partitions | Four walls parallel to x, two single-track and two double-track; length 4, height 4 above the 1 base | mm; count | Description §2.1.3; Figure 4 | 0.01 stated dimensions/counts | stated |
| Internal wall widths | single 0.10; double 0.20; each double is one continuous wall | mm | No dimensioned source; description gives only nominal laser spot order | 0.075 single; 0.15 double | inferred; open |
| Internal wall centerlines | +y order S, D, S, D at 1.30, 2.05, 2.90, 3.65 | mm | Figure 4 native-pixel measurements; §4 below | 0.15 each | measured; exact values open |
| Topology | One connected material solid; five sealed L10 void compartments; 13 lower section islands including the end block | count | Source construction; derived topology | Exact integer topology | required |
| Measurement and build interfaces | Name all 11 tab tops, 13 build-contact patches, both long sides, and far end | — | Description §3.4; user build-plane frame | 0.02 face plane; 0.2% area | required |
| Process and mass metadata | LPBF; alloy and density unspecified | — | Description §1 and process facts | No mass acceptance without density | stated process; material open |

Construction relationships must stay explicit: `legPatternPitch = 3*gapWidth + mediumLegWidth + thinLegWidth + wideLegWidth`, `legCount = 3*legPatternCount`, `thinWallCount = singleWallCount + doubleWallCount`, `wideLegWidth = cavityLength + 2*outerWallThickness`, `2*noseLength*tan(noseAngle) = bodyWidth`, and `gapWidth*tan(overhangAngle) = overhangRise` (angles in degrees). All counts must remain positive integers. These are consistency constraints on the dimensioned design; conflicting independent edits must be rejected or accompanied by a coordinated redesign. The three specified edit tests avoid those conflicts.

Keep widths positive, wall bands separate and inside the cavity, the L10 roof below the body top, and every wall joined to both x-end shell walls, its base, and ceiling. No microscopic gap or detached body may be introduced at a nominally joined interface.

## 4. Coordinate frame, scale, and measurement method

**Reproducible frame.** Origin is the intersection of z=0 (build-contact plane), y=0 (extension of the lower long side in Figure 3 plan), and x=0 (plane through the pointed end). The datum origin itself is in air because the tip is centered across the width: its bottom point is [0,2.5,0]. +x runs rightward toward the square end at x=75; +y runs upward in Figure 3 plan from y=0 to y=5; +z runs upward in elevation. The nose is a vertical edge at x=0, y=2.5 from z=0 to z=12, not a conical or pyramidal point. Datum A is the thirteen z=0 contact patches, B is the y=0 long side behind x=2.5, C is the x=75 end face, and D is the z=12 body top between tabs.

**Drawing versus prose.** The description's “12 mm tall” denotes the body: the Figure 3 elevation separately dimensions the 0.5 mm tab projection. The overall envelope is therefore 12.5 mm tall. The text's “proceeds left” recoating phrase conflicts with the Figure 3 arrow and the explicit task frame; use +x from nose to far end, as required. The two 45° nose flank angles give a 90° included apex angle. Each underside ramp is a one-sided 45° ceiling rising toward +x, not a symmetric roof.

**Image method.** Pixel coordinates below are zero-based `(u,v)` in each original PNG, with u rightward and v downward. Read dimension labels first, then use pixels only to confirm feature identity, placement, count, and the four undocumented centerlines. No perspective rectification was applied to the orthographic Figure 3. Use separate plan/elevation scales because the raster has small anisotropic scale differences; never adjust an explicit dimension to fit that raster.

Figure 3 is 3127 × 1821 pixels. The tip datum line is near u=382, far-end outline center near u=2936: `(2936-382)/75 = 34.05333 px/mm` along x. Plan side-outline centers are near v=322 and 492: `170/5 = 34.0 px/mm` across y. Elevation body-top and build-plane centers are near v=1085 and 1495: `410/12 = 34.16667 px/mm` vertically. Black outlines are commonly 4–7 pixels thick, corresponding to roughly 0.12–0.21 mm. Pixel confirmations are approximate; the stated parameter thresholds do not imply that the raster supports 0.01 mm measurement accuracy.

| Figure 3 pixel evidence | scaled check / interpretation |
|---|---|
| Plan tip u≈382, shoulder u≈467, far end u≈2936 | Nose axial extent ≈2.496 mm; length datum label 75 is authoritative. |
| Plan sides v≈322,492; nose tip v≈407 | 5 mm width and centered tip y=2.5. |
| Elevation body top v≈1085, tab top v≈1069, base v≈1495 | 12 mm body; tab pixel rise ≈0.468 mm confirms the separate 0.5 label, which overrides the raster. |
| First tab edges u≈519,553; next start ≈757; last edges ≈2901,2936 | First start ≈4.02 mm, pitch ≈6.990 mm, last width ≈1.028 mm; derive exact starts 4+7*i from dimensions. |
| Eleven tab-start strokes u≈519,757,995,1235,1472.5,1710,1949,2188,2426,2663.5,2901 | Eleven repetitions; the dashed L10 inset stroke near u=1484 is not an additional tab. |
| First underside gap low-x edge u≈1030; high-x edge ≈1097.5 | First start ≈19.03 mm and gap ≈1.982 mm; exact dimensions yield x=19 and 2 mm gap. |
| Right repeat endpoints u≈2460.5 and 2936; medium-leg edges 2528,2613; thin-leg edges 2681,2698; wide-leg edges 2766,2936 | Approximate pitch 13.963, medium 2.496, thin 0.499, wide 4.992 mm; labels 14,2.5,0.5,5 govern. |
| Gap lower and upper ceiling levels v≈1325 and 1255; base 1495 | Approximately z=4.976 and 7.024; explicit 5+2 dimensions and 45° arrow establish exact nominal ramp. |
| L10 outside x-strokes u≈1336,1505; cavity dimension extension lines 1353,1490 | Outside ≈4.962 mm, inner ≈4.0239 mm; nominal x=28..33 and cavity x=28.5..32.5. |
| L10 cavity elevation v≈1325..1461, base 1495 | Cavity height ≈3.9805 mm and base≈0.9951 mm; labels 4.0 and 1.0 govern. |

Figure 4 is 3900 × 1771 pixels. The plot X ticks at u≈1458,1820,2182,2543,2903,3265 represent −6,−4,−2,0,2,4 mm, approximately 180.8 px/mm. The plot Y ticks v≈1636,1454,1275,1095,914,734 represent 28,29,30,31,32,33 mm, approximately 180.4 px/mm. These are build/plot coordinates, not the requested part origin. Register the L10 outline and cavity to the contract's L10; do not copy the plot's absolute axis offsets.

For each internal track, average the centers of gold-colored line runs over columns u=1650..1699, away from lettering and end turns. The single centers are v=1357 and 1068. Double pairs are v=(1211,1232) and (922,944), with mean centers 1221.5 and 933. The end-wall hatch changes from full-width to side-only at v≈767.5/786 above the cavity and 1493/1511.5 below it. Use transition midpoints `vTop=776.75`, `vBottom=1502.25` to register the known 4 mm cavity width; this gives 725.5/4=181.375 px/mm, consistent with the axis scale to about 0.6%. The part-frame transformation is:

`y = outerWallThickness + cavityWidth * (1502.25 - v) / (1502.25 - 776.75)`.

| wall in increasing +y order | native v center | unrounded y (mm) | contract y (mm) | digital tolerance (mm) |
|---|---|---|---|---|
| singleWall1Y | 1357 | 1.300827 | 1.30 | 0.15 |
| doubleWall1Y | 1221.5 | 2.047898 | 2.05 | 0.15 |
| singleWall2Y | 1068 | 2.894211 | 2.90 | 0.15 |
| doubleWall2Y | 933 | 3.638525 | 3.65 | 0.15 |

Round these centerline readings to 0.05 mm. The ±0.15 mm bands cover stroke width, roughly 20 px hatch spacing, uncertain scan-to-boundary registration, and the schematic nature of the source. Figure 4 depicts scan centerlines: neither gold stroke thickness nor double-track separation establishes a finished solid-wall width. This is why the four positions are `measured` and the two widths are `inferred`.

Figure 1 is 3448 × 1708 pixels and is a perspective overview. It confirms the twelve leg labels with L1 at the far end, L10 in the highlighted region, four 14 mm repeats, the eleven tabs, and the orientation of the tapered end. No length, angle, or wall thickness is measured from that perspective image. Colored thermography and thin-wall highlight boxes, direction arrows, labels, and scan paths are annotations, not part solids.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| overallLength | 75 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "75". Tip plane to far end along x. |
| bodyWidth | 5 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "5" (plan width). Distance between the two parallel long side planes y=0 and y=5. |
| bodyHeight | 12 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "12" (elevation). Build plane to the flat body top, excluding tabs. |
| noseLength | 2.5 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "2.5" (plan nose). Axial extent of the symmetric plan taper; shoulder at x=2.5. |
| legStraightHeight | 5 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "5" (lower elevation). Height at the low-x end of each sloping gap ceiling. |
| overhangRise | 2 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "2" (vertical rise). Rise across each 2 mm wide gap, from z=5 to z=7. |
| gapWidth | 2 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "2" (horizontal gap). Clear gap along x below the start of the overhang. |
| wideLegWidth | 5 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "5" (far-end leg). Base width along x of L1, L4, L7 and L10. |
| mediumLegWidth | 2.5 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "2.5" (elevation leg). Base width along x of L3, L6, L9 and L12. |
| thinLegWidth | 0.5 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "0.5" (elevation leg). Base width along x of L2, L5, L8 and L11. |
| legPatternPitch | 14 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "14". Repeat along x containing three gaps and one leg of each width. |
| tabWidth | 1 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "1" (plan). Each transverse top tab occupies 1 mm along x and the full body width. |
| tabPitch | 7 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "7" (plan). Pitch between corresponding tab edges along x. |
| tabHeight | 0.5 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "0.5" (upper elevation). Projection above bodyHeight; the drawing gives 12.5 mm total height. |
| cavityLength | 4 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "4" (thin-wall inset, elevation). Clear L10 cavity length along x before adding internal walls. |
| baseThickness | 1 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "1.0" (thin-wall inset, elevation). L10 sealed base extends from z=0 to z=1. |
| thinWallHeight | 4 mm | 0.01 mm | stated | sources/nist-figure3-drawing.png: dimension label "4.0" (thin-wall inset, elevation). Internal walls extend from z=1 to the flat cavity ceiling at z=5. |
| noseAngle | 45 deg | 0.1 deg | stated | sources/nist-figure3-drawing.png: "45°" at the pointed plan end. Angle of each taper flank to x in plan; included apex angle is 90 degrees. |
| overhangAngle | 45 deg | 0.1 deg | stated | sources/nist-figure3-drawing.png: "45°" in elevation; sources/nist-amb2022-01-description.md §2.1.3: "45° overhangs". Inclination of the gap ceiling in the x-z plane. |
| legCount | 12 (dimensionless) | 0.01 | stated | sources/nist-amb2022-01-description.md §1: "12 legs of varying size". Twelve numbered legs; the tall solid end block is additional. |
| tabCount | 11 (dimensionless) | 0.01 | stated | sources/nist-amb2022-01-description.md §2.3: "The 11 tabs on top". Eleven full-width tabs; the final tab ends flush with x=75. |
| outerWallThickness | 0.5 mm | 0.1 mm | stated | sources/nist-amb2022-01-description.md §2.1.3: "outer walls of the L10 leg are approximately 0.5 mm thick". Nominal thickness of all four vertical outer walls of L10; approximate wording retained. |
| thinWallCount | 4 (dimensionless) | 0.01 | stated | sources/nist-amb2022-01-description.md §2.1.3: "a hollow cavity with four thin-wall structures". Four internal partitions, creating five enclosed void compartments. |
| singleWallCount | 2 (dimensionless) | 0.01 | stated | sources/nist-amb2022-01-description.md §2.1.3: "two thin walls that are the width of a single laser track". Two single-track-equivalent solid partitions. |
| doubleWallCount | 2 (dimensionless) | 0.01 | stated | sources/nist-amb2022-01-description.md §2.1.3: "another two that are the width of a double laser track". Two double-track-equivalent solid partitions, each treated as one merged wall. |
| overallHeight | 12.5 mm | 0.01 mm | derived | Formula: bodyHeight + tabHeight Maximum z at the tab tops. |
| legMergeHeight | 7 mm | 0.01 mm | derived | Formula: legStraightHeight + overhangRise All inter-leg gaps close at z=7; agrees with Layer 175 in the text. |
| legPatternCount | 4 (dimensionless) | 0.01 | derived | Formula: legCount / 3 Four repeats; each has three leg widths and three gaps. |
| endBlockLength | 19 mm | 0.01 mm | derived | Formula: overallLength - legPatternCount * legPatternPitch Extent to the low-x edge of the first underside gap, including the 2.5 mm nose. |
| firstTabX | 4 mm | 0.01 mm | derived | Formula: overallLength - tabWidth - (tabCount - 1) * tabPitch Low-x edge of the first tab; all tabs are anchored to the far end. |
| l10StartX | 28 mm | 0.01 mm | derived | Formula: overallLength - wideLegWidth - 3 * legPatternPitch Low-x base edge of L10, the fourth wide leg counted back from L1. |
| cavityStartX | 28.5 mm | 0.01 mm | derived | Formula: l10StartX + outerWallThickness Low-x inner wall face of the L10 cavity. |
| cavityWidth | 4 mm | 0.2 mm | derived | Formula: bodyWidth - 2 * outerWallThickness Clear transverse cavity span y=0.5 to 4.5 before partitions. |
| cavityCeilingZ | 5 mm | 0.01 mm | derived | Formula: baseThickness + thinWallHeight Flat downward-facing ceiling of all five sealed pockets. |
| singleWall1Y | 1.3 mm | 0.15 mm | measured | sources/nist-figure4-legs-thinwalls.png: native 3900 x 1771 pixels, gold line centers in columns u=1650:1700; single track center v=1357. Cavity transition midpoints v=1502.25 (low y), 776.75 (high y). Read y=0.5+4*(1502.25-v)/725.5 mm and round to 0.05 mm; see brief §4. Transverse centerline in the contract frame; approximate scan-schematic reading, not a dimensioned finished-wall location. |
| doubleWall1Y | 2.05 mm | 0.15 mm | measured | sources/nist-figure4-legs-thinwalls.png: native 3900 x 1771 pixels, gold line centers in columns u=1650:1700; double track centers v=1211 and 1232; mean 1221.5. Cavity transition midpoints v=1502.25 (low y), 776.75 (high y). Read y=0.5+4*(1502.25-v)/725.5 mm and round to 0.05 mm; see brief §4. Transverse centerline in the contract frame; approximate scan-schematic reading, not a dimensioned finished-wall location. |
| singleWall2Y | 2.9 mm | 0.15 mm | measured | sources/nist-figure4-legs-thinwalls.png: native 3900 x 1771 pixels, gold line centers in columns u=1650:1700; single track center v=1068. Cavity transition midpoints v=1502.25 (low y), 776.75 (high y). Read y=0.5+4*(1502.25-v)/725.5 mm and round to 0.05 mm; see brief §4. Transverse centerline in the contract frame; approximate scan-schematic reading, not a dimensioned finished-wall location. |
| doubleWall2Y | 3.65 mm | 0.15 mm | measured | sources/nist-figure4-legs-thinwalls.png: native 3900 x 1771 pixels, gold line centers in columns u=1650:1700; double track centers v=922 and 944; mean 933. Cavity transition midpoints v=1502.25 (low y), 776.75 (high y). Read y=0.5+4*(1502.25-v)/725.5 mm and round to 0.05 mm; see brief §4. Transverse centerline in the contract frame; approximate scan-schematic reading, not a dimensioned finished-wall location. |
| singleWallWidth | 0.1 mm | 0.075 mm | inferred | Undocumented. Provisional 0.10 mm uses only the order-of-magnitude laser spot diameter stated in the supplied description; spot size is not a measurement of the finished wall. Keep editable and replace when documented. The wide tolerance is deliberate. Nominal rectangular width across y of each single-track internal wall. |
| doubleWallWidth | 0.2 mm | 0.15 mm | inferred | Undocumented. Provisional 0.20 mm is twice the nominal single-track assumption, used as one continuous equivalent wall. Actual track separation, overlap, and melt-pool width are unknown. This is an independent inferred parameter, not a derived formula. Nominal rectangular width across y of each merged double-track internal wall. |

### Placement schedule and construction formulas

The repeated gaps are anchored from the far end through `endBlockLength=overallLength-legPatternCount*legPatternPitch`. For `k=0..3`, let `b=endBlockLength+k*legPatternPitch`. Their low-x edges are `a=b+[0, gapWidth+mediumLegWidth, 2*gapWidth+mediumLegWidth+thinLegWidth]`. Nominal list: **19,23.5,26,33,37.5,40,47,51.5,54,61,65.5,68 mm**. Remove the x-z quadrilateral `[(a,0),(a+gapWidth,0),(a+gapWidth,legMergeHeight),(a,legStraightHeight)]` through the full y width. Every sloped gap ceiling is `z=legStraightHeight+(x-a)*overhangRise/gapWidth`. Its solid side is above this plane. The end block extends to x=19 below the ramp; solid material from z=7 upward spans every gap.

| leg | base x interval (mm) | base width (mm) | construction / named contact |
|---|---|---|---|
| L1 | [70,75] | 5 | Solid; buildContactL01 |
| L2 | [67.5,68] | 0.5 | Solid; buildContactL02 |
| L3 | [63,65.5] | 2.5 | Solid; buildContactL03 |
| L4 | [56,61] | 5 | Solid; buildContactL04 |
| L5 | [53.5,54] | 0.5 | Solid; buildContactL05 |
| L6 | [49,51.5] | 2.5 | Solid; buildContactL06 |
| L7 | [42,47] | 5 | Solid; buildContactL07 |
| L8 | [39.5,40] | 0.5 | Solid; buildContactL08 |
| L9 | [35,37.5] | 2.5 | Solid; buildContactL09 |
| L10 | [28,33] | 5 | Hollow shell, sealed base and partitions; buildContactL10 |
| L11 | [25.5,26] | 0.5 | Solid; buildContactL11 |
| L12 | [21,23.5] | 2.5 | Solid; buildContactL12 |

The tab intervals are `[4+7*i,5+7*i]`, i=0..10, spanning y=0..5 and z=12..12.5. Count them in increasing x order as tabTop01..tabTop11. The final tab's end face merges into the far-end plane x=75.

The L10 parent cavity occupies x=28.5..32.5, y=0.5..4.5, z=1..5. Keep four rectangular partitions spanning all 4 mm along x and all 4 mm in z: y=1.30±0.05,2.05±0.10,2.90±0.05,3.65±0.10 at the nominal inferred widths. The five remaining pockets have y intervals `[0.5,1.25]`, `[1.35,1.95]`, `[2.15,2.85]`, `[2.95,3.55]`, `[3.75,4.5]` and widths 0.75,0.60,0.70,0.60,0.75 mm. Every pocket is a closed 4×width×4 box. Both single and double walls meet the base, roof, and x-end outer walls, so they are connected to the one material solid. Count five void holes in either a horizontal cavity section or an x-normal transverse cavity section.

### Analytic acceptance calculation

Use these abbreviations only for calculation; they are expressions in the contract's top-level parameters, not additional undocumented dimensions:

- `L=overallLength`, `W=bodyWidth`, `H=bodyHeight`, `N=noseLength`.
- `g=gapWidth`, `h=legStraightHeight`, `r=overhangRise`, `n=legCount`.
- `nt=tabCount`, `tw=tabWidth`, `th=tabHeight`.
- `C=cavityLength`, `D=cavityWidth`, `J=thinWallHeight`, `T=singleWallCount*singleWallWidth+doubleWallCount*doubleWallWidth=0.6`.
- Pentagonal footprint `A=W*(L-N/2)=368.75 mm²`; perimeter `P=2*(L-N)+W+2*sqrt(N²+(W/2)²)=157.071067812 mm`.
- One gap x-z area `G=g*(h+r/2)=12 mm²`; total gap volume `n*W*G=720 mm³`.
- Blank body `Vb=A*H=4425`; one gap `Vg=W*G=60`; tabs `Vt=nt*tw*W*th=27.5`; parent cavity `Vc=C*D*J=64`; partitions `Vw=C*J*T=9.6`, all in mm³.

**Volume:** `V=Vb-n*Vg+Vt-Vc+Vw=3678.1 mm³`. This includes removal of 54.4 mm³ for the five sealed pockets. The envelope volume 4687.5 mm³ is not the part volume.

**Surface area:** start from the tapered prism `2*A+H*P`. Each through-width underside gap changes exposed area by `-g*W-2*G+W*(2*h+r+sqrt(g²+r²))`. Tabs add `2*nt*(tw+W)*th`; their top faces replace the covered body-top area, so horizontal areas cancel. This gives 3170.058441227 mm² external area. The five voids add `2*((C+J)*(D-T)+(thinWallCount+1)*C*J)=214.4 mm²`, for 3384.458441227 mm² total. Count the inside surfaces of sealed pockets and exclude material-material interfaces.

An independent face-area sum gives the same external result: top horizontal 368.75, bottom contacts 248.75, twelve inclined ceilings 169.705627485, vertical gap walls 720, both long sides 1463, far end 62.5, both nose flanks 84.852813742, and exposed x-normal tab walls 52.5 mm². The last tab's far-end strip is already included in the 62.5 mm² far end.

**Center of mass:** all centroids are geometric, equivalently uniform-density centroids. For the uncut tapered prism, `xb=(W*L²/2-W*N²/6)/A` and `zb=H/2`. For each gap beginning at `a_j`, `xg=a_j+g*(h/2+r/3)/(h+r/2)` and `zg=(h²+h*r+r²/3)/(2*(h+r/2))=3.027777778`. The gap's relative x centroid is 1.055555556. Tabs have `xt=firstTabX+(nt-1)*tabPitch/2+tw/2=39.5` and `zt=H+th/2=12.25`. Both cavity and partitions have `xc=cavityStartX+C/2=30.5` and `zc=baseThickness+J/2=3`. All exterior components and the parent cavity have y centroid W/2; partition y centroids are their measured centerlines.

`Mx=Vb*xb-Vg*sum(a_j+1.055555556)+Vt*xt-(Vc-Vw)*xc=135794.55 mm⁴` (use the unrounded formula above in evaluation).

`My=(Vb-n*Vg+Vt-Vc)*W/2+C*J*(singleWallWidth*(singleWall1Y+singleWall2Y)+doubleWallWidth*(doubleWall1Y+doubleWall2Y))=9196.21 mm⁴`.

`Mz=Vb*H/2-n*Vg*zg+Vt*(H+th/2)-(Vc-Vw)*zc=24543.675 mm⁴`.

`COM=[Mx,My,Mz]/V=[36.919754765,2.500261004,6.672922161] mm`. The tiny +y offset is intentional: measured alternating single/double placement is not mass-symmetric. The schema has no `center_of_mass.note` field, so these formulas are also included in `acceptance.volume.note`.

### Acceptance value ledger

All expected physical values are **analytic nominal predictions**, not measurements of a KCL model or NIST reference file. They are conditional on the stated idealization and inferred widths. Global comparison bands support digital validation; they do not certify as-built accuracy. A replacement for either inferred width requires recomputing all dependent predictions rather than relaxing the contract.

| acceptance value | expected | tolerance / band | provenance | formula / evidence |
|---|---|---|---|---|
| envelope.min | [0,0,0] mm | 0.02 mm per coordinate | derived frame | Tip plane, side datum and build plane. |
| envelope.max | [75,5,12.5] mm | 0.02 mm per coordinate | derived | [overallLength,bodyWidth,bodyHeight+tabHeight]. |
| acceptance.bbox_tolerance | 0.02 mm | Absolute per coordinate | digital validation setting | Preserve external dimensioned envelope; not a pixel-read claim. |
| acceptance.volume | 3678.1 mm³ | 0.3% = 11.0343 mm³ | derived | Vb-n*Vg+Vt-Vc+Vw; equation above and contract volume.note. |
| acceptance.surface_area | 3384.458441227 mm² | 0.5% = 16.922292206 mm² | derived | 3170.058441227 external +214.4 sealed internal; equation above. |
| acceptance.center_of_mass | [36.919754765,2.500261004,6.672922161] mm | 0.05 mm per axis | derived | Signed component first moments / final volume; equations above. |
| acceptance.solid_count | 1 | Exact count | derived topology | All feet connect above z=7; all partitions join L10 shell/base/ceiling. |
| acceptance.blockout.volume_min | 4450 mm³ | Lower band limit | derived | Nominal 4452.5 minus 2.5; uncut pentagonal body plus 11 top-tab prisms. |
| acceptance.blockout.volume_max | 4455 mm³ | Upper band limit | derived | Nominal 4452.5 plus 2.5; same blockout, before underside gaps and L10 cavities. |
| acceptance.deviation | null | Not applicable | no reference model | No mesh or deterministic reference measurements were supplied; no deviation band may be invented. |
| acceptance.export_volume_tolerance_rel | 0.002 | 0.2% = 7.3562 mm³ at nominal volume | retained validation default | Later KCL/STEP/STL volume agreement; use sufficient STL resolution. |

The blockout is explicitly the full-height pentagonal nose/body prism plus the eleven top tabs, **before** subtracting underside gaps or hollowing L10. Its envelope already matches the final envelope and its analytic volume is `A*bodyHeight+tabCount*tabWidth*bodyWidth*tabHeight=4452.5 mm³`. The band does not apply to the finished part or to a full rectangular bounding box.

Each section below records all acceptance fields together: plane, position, area, outer-loop count, hole count, and area tolerance. Section positions avoid coincident boundary planes. A loop means an outer material island; holes are additional inner loops. Thirteen lower islands are compatible with one three-dimensional solid because the islands join above the gaps.

| section id | plane | area | outer loops | holes | area tolerance | formula / evidence |
|---|---|---|---|---|---|---|
| legBases | z=0.5 mm | 248.75 mm² | 13 | 0 | 0.2% | Below the L10 base top: 12 numbered leg islands plus the solid end block. A=bodyWidth*(overallLength-noseLength/2-legCount*gapWidth). |
| l10Interior | z=3 mm | 235.15 mm² | 13 | 5 | 1% | Through all four internal walls: 13 outer loops and five holes in the L10 island. A=legBases area-cavityLength*(cavityWidth-2*singleWallWidth-2*doubleWallWidth). |
| l10Transverse | x=30.5 mm | 46.4 mm² | 1 | 5 | 5% | Central y-z section of L10, away from tabs. A=bodyWidth*bodyHeight-thinWallHeight*(cavityWidth-2*singleWallWidth-2*doubleWallWidth). Checks the 1 mm base, four 4 mm walls, and flat z=5 roof. |
| longitudinalCavity | y=2.5 mm | 745.5 mm² | 1 | 1 | 0.2% | x-z mid-width section passes through the middle sealed pocket, between internal walls. A=overallLength*bodyHeight-legCount*gapWidth*(legStraightHeight+overhangRise/2)+tabCount*tabWidth*tabHeight-cavityLength*thinWallHeight. |
| aboveCavity | z=5.25 mm | 263.75 mm² | 13 | 0 | 0.2% | Just above the sealed roof; all cavity holes have disappeared. A=footprint area-legCount*bodyWidth*gapWidth*(legMergeHeight-5.25)/overhangRise. |
| overhangMid | z=6 mm | 308.75 mm² | 13 | 0 | 0.2% | At half the overhang rise each remaining gap is 1 mm wide; slope probes distinguish direction. A=footprint area-legCount*bodyWidth*gapWidth/2. |
| solidBridge | z=8 mm | 368.75 mm² | 1 | 0 | 0.1% | Above the 7 mm merge plane and below tabs: full pentagonal footprint. A=bodyWidth*(overallLength-noseLength/2). |
| topTabs | z=12.25 mm | 55 mm² | 11 | 0 | 0.2% | Eleven separate tab sections, full 5 mm width. A=tabCount*tabWidth*bodyWidth. |

Named planar faces are listed individually below. All have plane-position tolerance 0.02 mm and area tolerance 0.2%. Face areas are nominal and derived. Use the spatial locator to distinguish repeated equal-area faces; the schema's plane/area test alone cannot distinguish a permutation of foot or tab names. Each named contact is one material patch on the same build datum, not the entire build plate. No fluid inlet or outlet exists.

| face name | plane and outward normal | area | tolerances | spatial locator / formula |
|---|---|---|---|---|
| buildContactEndBlock | z=0; normal -z | 88.75 mm² | 0.02 mm; 0.2% | Pentagonal end-block footprint x=0..19, y=0..5; W*(endBlockLength-N/2). |
| buildContactL01 | z=0; normal -z | 25 mm² | 0.02 mm; 0.2% | x=[70,75], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL02 | z=0; normal -z | 2.5 mm² | 0.02 mm; 0.2% | x=[67.5,68], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL03 | z=0; normal -z | 12.5 mm² | 0.02 mm; 0.2% | x=[63,65.5], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL04 | z=0; normal -z | 25 mm² | 0.02 mm; 0.2% | x=[56,61], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL05 | z=0; normal -z | 2.5 mm² | 0.02 mm; 0.2% | x=[53.5,54], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL06 | z=0; normal -z | 12.5 mm² | 0.02 mm; 0.2% | x=[49,51.5], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL07 | z=0; normal -z | 25 mm² | 0.02 mm; 0.2% | x=[42,47], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL08 | z=0; normal -z | 2.5 mm² | 0.02 mm; 0.2% | x=[39.5,40], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL09 | z=0; normal -z | 12.5 mm² | 0.02 mm; 0.2% | x=[35,37.5], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL10 | z=0; normal -z | 25 mm² | 0.02 mm; 0.2% | x=[28,33], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL11 | z=0; normal -z | 2.5 mm² | 0.02 mm; 0.2% | x=[25.5,26], y=[0,5]; (xMax-xMin)*bodyWidth. |
| buildContactL12 | z=0; normal -z | 12.5 mm² | 0.02 mm; 0.2% | x=[21,23.5], y=[0,5]; (xMax-xMin)*bodyWidth. |
| tabTop01 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[4,5], y=[0,5]; tabWidth*bodyWidth. |
| tabTop02 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[11,12], y=[0,5]; tabWidth*bodyWidth. |
| tabTop03 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[18,19], y=[0,5]; tabWidth*bodyWidth. |
| tabTop04 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[25,26], y=[0,5]; tabWidth*bodyWidth. |
| tabTop05 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[32,33], y=[0,5]; tabWidth*bodyWidth. |
| tabTop06 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[39,40], y=[0,5]; tabWidth*bodyWidth. |
| tabTop07 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[46,47], y=[0,5]; tabWidth*bodyWidth. |
| tabTop08 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[53,54], y=[0,5]; tabWidth*bodyWidth. |
| tabTop09 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[60,61], y=[0,5]; tabWidth*bodyWidth. |
| tabTop10 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[67,68], y=[0,5]; tabWidth*bodyWidth. |
| tabTop11 | z=12.5; normal +z | 5 mm² | 0.02 mm; 0.2% | x=[74,75], y=[0,5]; tabWidth*bodyWidth. |
| sideY0 | y=0; normal -y | 731.5 mm² | 0.02 mm; 0.2% | Straight long side behind nose shoulder; (L-N)*H-n*G+nt*tw*th. |
| sideY5 | y=5; normal +y | 731.5 mm² | 0.02 mm; 0.2% | Straight long side behind nose shoulder; (L-N)*H-n*G+nt*tw*th. |
| farEnd | x=75; normal +x | 62.5 mm² | 0.02 mm; 0.2% | Full far-end rectangle including last tab; bodyWidth*overallHeight. |

Feature verification additionally uses solid and void probes strictly inside the intended regions: all twelve low gaps at z=2.5, both sides of every slope at z=6, all eleven tabs at z=12.25, four L10 outer walls at z=3, all four partitions at z=3, and all five cavities below and above the z=5 roof. These complement aggregate volume and area checks. Non-axis-aligned nose flanks and ramp faces are verified by sections and probes because `FaceSpec` represents only axis-normal planes.

### Editability tests

Start each test from the original nominal parameters. Change only the named independent input by the stated delta; reevaluate derived constants and dependent feature placements. Do not accumulate edits between tests. Contract acceptance numbers describe the nominal part; an edit run compares the deltas below. All expected volume deltas use 1% relative comparison tolerance and all directions are `increase`.

| parameter edit | expected volume delta (mm³) | formula with other independent inputs held fixed | bbox size delta (mm) | resulting volume (mm³) |
|---|---|---|---|---|
| bodyHeight +1.00 | 368.75 | ΔV=A*ΔH=368.75*1. Tabs translate upward with the new body top; lower gaps and cavity dimensions stay fixed. | [0,0,1] | 4046.85 |
| tabHeight +0.25 | 13.75 | ΔV=tabCount*tabWidth*bodyWidth*Δth=11*1*5*0.25. | [0,0,0.25] | 3691.85 |
| singleWallWidth +0.05 | 1.60 | ΔV=singleWallCount*cavityLength*thinWallHeight*Δw=2*4*4*0.05. Centerlines stay fixed; doubleWallWidth is independent and stays 0.20. | [0,0,0] | 3679.70 |

These exercise a primary body dimension, all eleven repeated tabs, and a hidden internal feature. The width edit must visibly thicken both single walls while preserving four partitions and five pockets.

### Draft verification record

The source PNGs were inspected at native resolution, and color/outline run centers were read with Pillow/NumPy. Exact geometric formulas were evaluated with Python. An independent integration of analytic horizontal sections used Shapely polygon areas/centroids and three-point Gauss-Legendre quadrature over z intervals [0,1],[1,5],[5,7],[7,12],[12,12.5]. It returned volume 3678.0999999999995 mm³ and centroid [36.9197547646883,2.5002610043228843,6.672922160898291] mm, agreeing with the signed-volume calculation to floating-point roundoff. Its section areas/loop counts match the z-normal section ledger. This is a calculation check, not execution of a KCL model or measurement of a supplied reference.

The required bundle validation was run from `/Users/danieldriscoll/dual/opencad` and passed:

```sh
.venv/bin/python -m opencad check-bundle /Users/danieldriscoll/dual/opencad/designs/.staging-nist-amb2022-01-bridge --name nist-amb2022-01-bridge
```

The command printed `ok:` with 40 parameters, 15 features, and provenance counts `{stated: 25, derived: 9, measured: 4, inferred: 2}`. A subsequent in-memory audit checked all 9 derived parameter formulas, all 99 solid/void probes, all 8 section areas and loop/hole counts, the named face-area totals, and all 3 edit predictions. Independently integrated edit volume deltas were 368.75000000000045, 13.75000000000091, and 1.599999999999909 mm³, versus expected 368.75, 13.75, and 1.60 mm³; bbox deltas matched exactly. These are analytic checks of the contract, not CAD engine measurements. The bundle contains only the two draft files and the four unchanged sources. All eight brief headings remain, every parameter and acceptance item has a ledger row, and the section 8 log has no entries.

Future KCL verification must run format, lint, `zoo kcl analyze --format json`, section/point/name checks, the three edit tests, and STEP/STL volume agreement. STEP export must use `--deterministic`. Those future CAD checks are not performed in this contract-only stage.

## 6. Defaults retained


- `schema_version: 1` and `release_status: reconstruction` match this editable reconstruction task.
- Millimetres and degrees agree with Figure 3. The template's placeholder envelope, dimensions, frame, features, and example volume were replaced; no geometric parameter was retained as a default.
- `material: null` and `density_kg_m3: null` remain because the excerpts identify metal LPBF but do not identify an alloy or density. All reported mass-like quantities are geometric volume/centroid only; there is no mass prediction.
- One material solid is both the requested configuration and the retained count setting. The five sealed voids do not increase material solid count.
- The export agreement default of 0.002 (0.2%) is retained as a digital tessellation/conversion check. The 0.02 mm envelope/face tolerance, analytic comparison bands, section area bands, 1% edit-delta bands, and 0.05 mm centroid tolerance are explicitly chosen validation settings. They are not undocumented dimensions or process allowances.
- All sources are local immutable inputs. No reference-deviation setting is populated. Full hashes and supplied/unknown revision status are retained in the source table.
- Sharp planar edges, ideal rectangular wall cross-sections, and nominal uncut tab heights are the reconstruction convention. No fillet radius, rounding, powder volume, shrinkage, layer stair-stepping, or skim allowance is added.

## 7. Unrepresentable or low-confidence features


The two wall widths are intentionally inferred, with broad tolerance bands, and must remain visibly identified as such in later KCL comments. The nominal 0.10/0.20 mm rectangular sections do not assert actual melt-pool or as-built bead shape. Figure 4 only supports approximate centerlines and the distinction between one and two scan tracks. Double-track overlap and end-junction details are not dimensioned; representing each as a merged rectangular partition is an explicit provisional idealization. L10 outer walls are nominal 0.5 mm, while the text says “approximately.” Figure 3's stated 4 mm inner length and the task's nominal outer-wall requirement govern the ideal geometry.

The five sealed pockets include powder/gas in the physical build, but this contract models only the solid artifact geometry. It does not model contents, roughness, thermal distortion, residual stress, or layer scan paths. The red thermography field, dashed thin-wall highlights, leg labels, and direction arrows have no physical feature counterpart. Ridge skim cutting and post-build EDM are measurement/process context; no removal dimensions are provided, and the Figure 3 nominal form is the requested target.

The planar-face schema cannot directly encode the inclined nose/ramp normals, and repeated co-planar equal-area faces cannot be distinguished by plane/area alone. Explicit feature probes, section topology, and the spatial naming schedule above address these limits. A later modeler must independently inspect naming/locations and confirm actual one-solid topology, watertight exports, and internal closure. No rendered or exported reference was available for comparison in this draft.

Open questions recorded verbatim in the contract:

1. What are the nominal finished CAD widths of the single-track and double-track internal walls? They are not dimensioned. Pending documentation, singleWallWidth=0.10 mm (tolerance 0.075 mm) and doubleWallWidth=0.20 mm (tolerance 0.15 mm) are inferred rectangular merged-wall equivalents; laser spot diameter does not establish wall thickness.
2. Can NIST provide the exact transverse centerlines and end-junction profiles of the four L10 walls? Figure 4 gives approximate +y order single, double, single, double at y=1.30, 2.05, 2.90, 3.65 mm (each tolerance 0.15 mm). The scan schematic does not fix finished bead or junction profiles.
3. Which alloy and density apply to this individual artifact if a mass result is required? The supplied geometry excerpt gives neither; material and density remain null.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 0 | [0.0, 0.0, 0.0] → [75.0, 5.0, 12.5] | 4452.500000004801 | pass | 2026-09-15T15:57:22Z: STEP/OpenCascade remeasure after engine-bbox false fail |
