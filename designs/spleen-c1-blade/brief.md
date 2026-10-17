# spleen-c1-blade — design brief

## 1. Intent and configuration

**User intent, verbatim:**

> Reconstruct one SPLEEN C1 turbine cascade blade as editable KCL. Build the closed airfoil profile from the attached coordinate table (sheet SPLEENC1_Coord: pressure side x,y in columns A-B and suction side x,y in columns C-D, both in metres, both running from the leading edge at the origin to the shared trailing-edge point), keeping the table's axes, origin, scale and orientation exactly: x axial, y pitchwise, leading edge at (0, 0), trailing edge at (47.614, -21.600) mm, so the chord sits at the documented 24.4 degree stagger. Extrude the profile straight along +z from z = 0 over the documented cascade span (165.0 mm, Table 2.1). Preserve the leading edge, the suction-side curvature and the trailing-edge closure as given; do not substitute a generic airfoil, do not smooth or re-fit the shape beyond what a faithful curve through the published points requires, and do not add a root, platform, fillets or a display stand. The coordinate table is authoritative over any CAD file (the database's v1 CAD had a wrong stagger angle). One solid; export STEP and STL.

The configuration is one complete blade of constant cross-section, with two planar span-end caps. The workbook supplies the profile and the text excerpt supplies the 165.0 mm span. The exact coordinate endpoint is **(47.6144470215, -21.59972305301) mm**; the three-decimal endpoint in the intent is a rounded description. Preserve the workbook digits in the reconstruction. The published positive stagger is a magnitude; the signed angle in these axes is negative.

This bundle defines the subsequent editable KCL 2 model and its STEP/STL verification. This drafting task changes only `contract.yaml` and `brief.md`. It does not create KCL, exports, a blockout, or CAD-engine evidence. Release status is `reconstruction`.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| `sources/SPLEENC1_Geometry_Airfoil_2D_v1.xlsx` | table | authoritative | `eb02e45c1ff8b6f94fcb7a91209f5b0113c96b1ffa27f9cbaff18133cb37a4f2` | Coordinate workbook v1, identified as correct by database v5. `SPLEENC1_Coord`: metres, two header rows, 1001 rows per side in A-B/C-D. `Features`: mm and deg. Coordinates govern geometry over rounded summaries and CAD files. |
| `sources/spleen-c1-geometry-excerpt.md` | text | authoritative | `f3e30892ac891e29e7b6483e6456b6d7e2364fdf719a08a28e0f13ada6fc18e8` | Database v5 excerpt of `Geometry_TestSection_Info_v2.pdf`, Table 2.1; v2 update dated 25/11/2022. Units mm and deg, with coordinate commentary in m. Supplies span and the wrong-stagger v1 CAD warning. Attribution: Lavagnoli, Lopes, Simonassi, Torre, von Karman Institute; Zenodo record 13712768, DOI 10.5281/zenodo.13712768, CC-BY-4.0. Original PDF and CAD files were not supplied. |
| `reference/profile.json` | reference-model | authoritative | `0566d60bccac41d4dcbb77698128b45c40ce94b7256b153278998cc265e371e7` | Deterministic coordinate ingest, generated 2026-09-15T17:56:12Z. Units mm, mm² and deg. Authority is limited to correctly defined derivative evidence: `points_mm`, area, perimeter and bounds, subordinate to the workbook. Chord/stagger use a farthest-pair definition; centroid is a boundary-point mean. These three fields are excluded from physical chord/stagger/COM acceptance. No reference mesh or suggested tolerance fields exist. |
| `reference/profile.png` | image | illustrative | `882cb4e073a2d8c3fb8beab93ed9095e96565fffff2ad9ef81c1596dde6d75dd` | 900 × 606 px generated profile plot from the same ingest revision. Undimensioned, approximately 17.509964 px/mm. Used for visual orientation and contour evidence; no dimensions inferred from pixels. |

All four file hashes were computed from the supplied bytes. The workbook and excerpt hashes match the prefixes in the task. No source file was changed. The erroneous v1 CAD is not a reconstruction source.

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Configuration | One SPLEEN C1 blade, one solid | count | User intent | Exact topology | stated |
| Profile data | 1001 PS points and 1001 SS points; 2000 unique vertices after shared LE/TE deduplication | count | `SPLEENC1_Coord!A3:D1003`; independently compared with `points_mm` | Retain every row; source point to model boundary ≤0.001 mm | stated / independently checked |
| Side ordering | PS LE→TE, SS LE→TE in workbook; reverse SS when closing | — | Workbook and excerpt | Exact ordering | stated |
| Length conversion | Multiply coordinate values by 1000 | mm/m | Workbook row 2 headers | Exact unit conversion | stated |
| Leading-edge landmark | (0, 0) at z = 0 | mm | `SPLEENC1_Coord!A3:D3`; user intent | 0.001 mm point tolerance | stated |
| Shared trailing-edge landmark | (47.6144470215, -21.59972305301) | mm | `SPLEENC1_Coord!A1003:D1003` | 0.001 mm per coordinate; retain full precision | stated |
| True chord | 52.284640202739865 | mm | Endpoint distance; `Features!B7` states 52.285; Table 2.1 states 52.28 | 0.001 mm for coordinate-derived target; rounded Table 2.1 agrees within 0.005 mm | derived / stated cross-check |
| Stagger | Signed -24.40085023652175; documented magnitude 24.4 | deg | Endpoint vector; `Features!B4`; Table 2.1 | 0.005 deg for derived target; magnitude agrees with document within 0.01 deg | derived / stated cross-check |
| Span | 165.0, from z = 0 to z = 165.0 | mm | Excerpt Table 2.1, “Cascade span [mm]” | 0.01 mm | stated |
| Trailing-edge radius | 0.435 nominal | mm | `Features!B9`; Table 2.1 | 0.005 mm documentary cross-check; coordinates govern contour | stated |
| Leading edge and both side curves | Retain original nose, pressure side, suction-side crown and terminal curvature | — | All coordinate rows; user intent | No generic airfoil, smoothing or point reduction; ≤0.001 mm at supplied points | stated |
| Extrusion | Constant XY section, straight +z, two planar caps | — | User intent | Six section checks, cap checks and 0.01 mm bbox tolerance | stated |
| Added features | No root, platform, extra fillets or stand; no hole/cavity is specified | count | User intent and complete solid profile | Zero additions; zero section holes | stated |
| Export | STEP and STL, same frame, scale and one-solid geometry | — | User intent | Relative volume agreement ≤0.002 | stated / verification default |
| Cascade context | Pitch 32.95073899 (`Features!B8`), rounded 32.95 (Table 2.1); throat opening 19.40 | mm | Workbook and excerpt | Documentary values only; no cascade array or flow passage is modeled | stated, outside single-blade geometry |
| Angle context | Inlet 37.30, outlet 53.80 | deg | `Features!B2:B3` and Table 2.1 | Documentary values only; do not impose tangents on table points | stated, not independent shape constraints |
| Test-section context | Upstream test-section height 225 | mm | Excerpt span clarification | Documentary only; blade span remains 165.0 | stated, outside blade geometry |
| Material, density, process | Unspecified | — | No supplied requirement | No assumed value or mass | open |
| Original between-point interpolation | Unspecified degree, knots and continuity | — | Not present in workbook/excerpt | Faithful passage through all points required | open; supplied point geometry is fixed |

The workbook calls its inlet/outlet entries “flow angle”; the excerpt calls them “metal angle.” No tangent or flow-domain requirement is inferred from that terminology difference. Cascade pitch, throat, inlet/outlet angles and pitch-to-chord ratio describe the surrounding cascade and do not create additional blade features.

## 4. Coordinate frame, scale, and measurement method

**Reproducible frame.** Place the shared LE coordinate at (0, 0, 0) on `spanStart`. Positive x follows increasing axial x in workbook columns A/C. Positive y follows increasing pitchwise y in columns B/D. Positive z completes the right-handed frame and is the straight span direction. `spanStart` is the z = 0 plane with outward normal -z; `spanEnd` is z = 165 with outward normal +z. The construction datum y = 0 contains the axial and span directions, and x = 0 contains the pitchwise and span directions. The chord datum connects the two shared LE/TE coordinates. It is already staggered in the source frame.

The origin is a shared boundary landmark; the nose extends to x = -0.19685863578579998 mm. Likewise, the rounded trailing edge extends past the shared TE to x = 47.77582706417 mm and y = -21.6984059788506 mm. Preserve those extrema. Apply only metre-to-millimetre conversion at baseline; do not center, mirror, rotate or fit the profile to an axial/chord bounding box.

**Table measurements.** Read `SPLEENC1_Coord`, skip rows 1-2, and multiply A-D by 1000. Trace PS rows 3 through 1003, followed by SS rows 1002 down through 4, then close to row 3. This yields the same 2000 vertices as `profile.json` with exact floating-point array equality. Both endpoints match exactly between sides. The points are finite and unique, and the closed polygon is counterclockwise, simple and valid, with one outer ring and no holes. Shapely independently checked polygon validity, centroid, probe classifications and diagnostic intersections.

`closed_input: false` records omission of a repeated closing vertex; it does not indicate an intended gap. Include the final segment to LE in area, perimeter and closure. The maximum input segment length is 0.0660915780030579 mm. No resampling or decimation was performed in this draft.

Compute signed area by the cyclic shoelace sum, perimeter by cyclic segment lengths, and area centroid by first moments. Bounds come directly from coordinate minima/maxima. For the axial diagnostic sections, intersect each table segment with the stated x plane by linear interpolation, then multiply the resulting y interval by span. These are polygonal baselines for the future faithful interpolating CAD curve.

**Definition corrections.** Ingest `measurements.chord = 52.987829613124575 mm` and `stagger_deg = -26.18651302333979 deg` use the farthest boundary-vertex pair, whose endpoints are (0.185515547835101, 1.9389149018278302) and (47.7347947086235, -21.444329920029897) mm. They are not the shared LE/TE landmarks. The true landmark chord is 52.284640202739865 mm at -24.40085023652175 deg. Ingest `measurements.centroid = (25.447679478227002, -2.918990906912219) mm` is an unweighted boundary-vertex mean. The filled-area centroid is (20.619657984838426, 1.0449253890203034) mm and is the correct uniform-prism COM in XY. No rotation or geometry change is warranted by these different definitions. The ingest's farthest-chord thickness bins are also not adopted as blade dimensions.

**Raster evidence.** No dimensioned image was attached. The generated `profile.png` was inspected: one continuous outline, two side contours, a rounded left nose, a high suction-side crown, a rounded lower-right termination, and no visible internal loops. It has no dimension lines. Its image origin is the upper-left corner and pixel y increases downward. The ingest plot uses scale `840 / 47.972685699955804 = 17.5099640085561 px/mm`, or 0.0571103401189950 mm/px, with 30 px nominal margins. For coordinate (x,y), the plotted location is `px = 30 + (x - xMin)*scale`, `py = 606 - 30 - (y - yMin)*scale`.

| feature evidence | approximate pixel location (px, py) | interpretation |
|---|---|---|
| Shared LE | (33.45, 196.06) | Left boundary landmark; actual nose extends farther left |
| Minimum x | (30.00, 185.26) | Rounded nose at negative source x |
| Suction-side maximum y | (281.60, 29.47) | High crown above the LE in source coordinates |
| Shared TE | (867.17, 574.27) | Lower-right landmark, consistent with negative signed stagger |
| Maximum x | (870.00, 568.18) | Rounded terminal contour beyond the shared TE |
| Minimum y | (862.52, 576.00) | Terminal contour below the shared TE |

These pixel locations are projections of authoritative coordinates used to corroborate the view, not independent measurements. The 2 px outline alone spans about 0.114 mm, with larger point markers; it cannot justify the contract's finer numerical tolerances. Consequently there are **zero image-measured parameters**.

## 5. Measurement and inference record

All values below are nominal. Digital tolerances define comparison bands; they are not manufacturing tolerances or permission to round the input coordinates. No suggested tolerance fields were present in the reference ingest, so the bands are explicitly selected and justified in section 6.

**Parameters — exactly the seven entries in `contract.yaml`.**

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| `span` | 165.0 mm | ±0.01 mm | stated | Excerpt Table 2.1: “Cascade span [mm]”, 165.0; extrusion starts at z = 0. |
| `axialChord` | 47.6144470215 mm | ±0.001 mm | stated | `SPLEENC1_Coord!A1003/C1003` = 0.0476144470215 m; `Features!B6` = 47.6144470215 mm. This is endpoint x, not total bbox width. |
| `trailingEdgeY` | -21.59972305301 mm | ±0.001 mm | stated | `SPLEENC1_Coord!B1003/D1003` = -0.02159972305301 m. |
| `trailingEdgeRadius` | 0.435 mm | ±0.005 mm | stated | `Features!A9:B9`: “Trailing edge radius [mm]”, 0.435. Documentary contour cross-check; no additional fillet or radius fit. |
| `profilePerimeter` | 123.78447524923155 mm | ±0.05 mm | measured (reference model) | `reference/profile.json: measurements.perimeter`; cyclic sum of segment lengths, including closure. |
| `trueChord` | 52.284640202739865 mm | ±0.001 mm | derived | `sqrt(axialChord^2 + trailingEdgeY^2)`. |
| `signedStagger` | -24.40085023652175 deg | ±0.005 deg | derived | `atan2(trailingEdgeY, axialChord)*180/pi`; signed from +x toward +y. |

Provenance count: **4 stated; 1 measured (reference model); 2 derived; 0 measured from images; 0 inferred; 0 defaulted**. Reference-only constants document the nominal geometry and must not equality-lock independent edits. Declare all seven as literal top-level KCL constants in the later model, per the repository rules. Use only sanity assertions; exact nominal relationships must not prevent rebuilding an edited copy.

**Analytic definitions.** Let `p_i = (x_i,y_i)` be the 2000 nominal points in cyclic order and `d_i = x_i*y_(i+1) - x_(i+1)*y_i`.

- `A = 0.5*sum(d_i)` for the counterclockwise loop; the ingest baseline is 230.63711778179277 mm².
- `P = sum(sqrt((x_(i+1)-x_i)^2 + (y_(i+1)-y_i)^2)) = profilePerimeter`.
- `Cx = sum((x_i+x_(i+1))*d_i)/(6*A)` and `Cy = sum((y_i+y_(i+1))*d_i)/(6*A)`.
- `V = A*span`; `S = 2*A + P*span`; `COM = (Cx, Cy, span/2)` for a uniform solid.
- At an axial cut `x = a`, crossing segments give `y = y_i + (a-x_i)*(y_(i+1)-y_i)/(x_(i+1)-x_i)`. The single material interval `[yLow,yHigh]` gives section area `(yHigh-yLow)*span`.

The schema does not allow a `note` field under `center_of_mass`. Its formula is therefore recorded in `acceptance.volume.note` as well as here.

**Reference baselines and acceptance values.** Lengths are mm, areas mm², volumes mm³. “Exact” below applies to discrete topology or sign, rather than a zero numeric parameter tolerance.

| parameter / acceptance value | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| Reference area `A` | 230.63711778179277 | Acceptance section band ±0.002 relative | measured (reference model) | `profile.json: measurements.area`; shoelace area of the closed loop. This baseline is not an additional contract parameter. |
| `envelope.min` | (-0.19685863578579998, -21.6984059788506, 0) | ±0.01 per coordinate | measured (reference model), plus stated z origin | `measurements.bbox_min`; user specifies z = 0. |
| `envelope.max` | (47.77582706417, 9.51390836469706, 165) | ±0.01 per coordinate | measured (reference model), plus stated span | `measurements.bbox_max`; z max = span. |
| Envelope size, diagnostic | (47.972685699955804, 31.21231434354766, 165) | Endpoint comparisons govern | derived | `envelope.max - envelope.min`; matches `measurements.size` in XY. |
| `acceptance.bbox_tolerance` | 0.01 mm | Positive absolute comparison threshold | defaulted verification policy | Small allowance for a faithful interpolating boundary's between-point extrema. |
| `acceptance.volume` | 38055.12443399581 | ±0.002 relative = ±76.110248867992 | derived | `A*span`. |
| `acceptance.surface_area` | 20885.71265168679 | ±0.002 relative = ±41.771425303374 | derived | `2*A + profilePerimeter*span`. |
| `acceptance.center_of_mass` | (20.619657984838426, 1.0449253890203034, 82.5) | ±0.01 per coordinate | derived | Polygon first moments in XY; `span/2` in z. The point mean is excluded. |
| `acceptance.solid_count` | 1 | Exact | stated | User requests one solid. |
| `sections.nearSpanStart` plane | z = 16.5 | Fixed interior probe plane | derived | `span/10`. |
| `sections.nearSpanStart` area | 230.63711778179277 | ±0.002 relative | derived | Constant extrusion section = `A`. |
| `sections.nearSpanStart` loops / holes | 1 / 0 | Exact | derived | Valid single closed source polygon; no cavities. |
| `sections.midSpan` plane | z = 82.5 | Fixed interior probe plane | derived | `span/2`. |
| `sections.midSpan` area | 230.63711778179277 | ±0.002 relative | derived | Constant extrusion section = `A`. |
| `sections.midSpan` loops / holes | 1 / 0 | Exact | derived | Same source polygon. |
| `sections.nearSpanEnd` plane | z = 148.5 | Fixed interior probe plane | derived | `9*span/10`. |
| `sections.nearSpanEnd` area | 230.63711778179277 | ±0.002 relative | derived | Constant extrusion section = `A`. |
| `sections.nearSpanEnd` loops / holes | 1 / 0 | Exact | derived | Same source polygon. |
| `sections.axialLeadingEdge` plane | x = 0.1 | Fixed interior probe plane | defaulted probe placement | Close to the LE landmark and crossing both sides; a verification location, not an invented dimension. |
| `sections.axialLeadingEdge` area | 306.8773636067 | ±0.01 relative | derived | `(1.7590876768653476 - (-0.1007751328722282))*span`, from `points_mm` intersections. |
| `sections.axialLeadingEdge` loops / holes | 1 / 0 | Exact | derived | One continuous y interval × span. |
| `sections.axialCrown` plane | x = 14.0 | Fixed interior probe plane | defaulted probe placement | Crosses the pressure and suction sides near the crown; not a part dimension. |
| `sections.axialCrown` area | 1061.785915064893 | ±0.01 relative | derived | `(9.513101801269778 - 3.0780356493613352)*span`, from `points_mm` intersections. |
| `sections.axialCrown` loops / holes | 1 / 0 | Exact | derived | One continuous y interval × span. |
| `sections.axialTrailingEdge` plane | x = 47.6 | Fixed interior probe plane | defaulted probe placement | Exposes the terminal closure without cutting exactly through the TE landmark. |
| `sections.axialTrailingEdge` area | 120.18396505371327 | ±0.01 relative | derived | `(-20.881728932852354 - (-21.610116599844556))*span`, from `points_mm` intersections. |
| `sections.axialTrailingEdge` loops / holes | 1 / 0 | Exact | derived | One continuous y interval × span. |
| `faces.spanStart` plane / normal | z = 0 / -z | ±0.01 plane position; exact outward sign | stated / derived | Starting extrusion cap; outward normal opposite extrusion. |
| `faces.spanStart` area | 230.63711778179277 | ±0.002 relative | derived | Source airfoil area `A`. |
| `faces.spanStart` in-plane center | (20.619657984838426, 1.0449253890203034) | Center supplied for face identification; no separate center-tolerance field | derived | Same polygon area centroid `(Cx,Cy)`; face tolerance is 0.01 mm. |
| `faces.spanEnd` plane / normal | z = 165 / +z | ±0.01 plane position; exact outward sign | stated / derived | End cap at `span`; outward normal along extrusion. |
| `faces.spanEnd` area | 230.63711778179277 | ±0.002 relative | derived | Source airfoil area `A`. |
| `faces.spanEnd` in-plane center | (20.619657984838426, 1.0449253890203034) | Center supplied for face identification; no separate center-tolerance field | derived | Constant section gives the same `(Cx,Cy)`; face tolerance is 0.01 mm. |
| `acceptance.blockout.volume_min` | 37674.57318965585 | Lower bound | derived | `0.99*A*span`; primary solid is the full airfoil extrusion. |
| `acceptance.blockout.volume_max` | 38435.67567833576 | Upper bound | derived | `1.01*A*span`; no subtractive features are present. |
| `acceptance.deviation` | null | Not applicable | derived applicability decision | The supplied reference is a 2D coordinate table, with no reference mesh or mesh-distance tolerance. |
| `acceptance.export_volume_tolerance_rel` | 0.002 | Maximum relative volume disagreement | defaulted verification policy | Agreement among analyzed KCL, STEP and STL; template threshold retained. |

The defaulted items in this acceptance table are digital thresholds or probe positions. They introduce no defaulted geometric parameters. The blockout is the one primary airfoil extrusion: it contains the full outer contour and no detail additions or subtractions, so its analytic nominal volume equals the final nominal volume.

**Feature probes.** All listed XY probes are at z = 82.5 mm unless stated otherwise. Shapely classified them against the exact table polygon. The smallest boundary clearance among the listed solid/void probes is 0.0909344363 mm, greater than the 0.01 mm envelope tolerance. Void probes describe exterior space and do not introduce a hole or cavity.

| feature | solid probes (x,y) | exterior void probes (x,y) | additional verification |
|---|---|---|---|
| Complete profile | (10,6), (25,3), (40,-12.2) | (20,0), (25,7) | Mid-span area, one loop, zero holes, full bbox |
| Pressure side | (30,-3), (40,-13) | (25,-1) | Axial crown section |
| Suction-side crown | (14,9.3) | (14,9.7) | Axial crown section and y maximum |
| Leading edge | (-0.1,0.5), (0.1,0.4) | (-0.3,0.7), (-0.05,-0.2) | Axial LE section and negative-x nose bound |
| Trailing edge | (47.55,-21.3) | (47.9,-21.3) | Axial TE section, one loop, x maximum and y minimum |
| Span | (25,3) at z = 1 and z = 164 | — | Three constant-area z sections, full bbox and both planar caps |

**Edit tests.** Use independent one-parameter edits in temporary copies of the later KCL model. Restore the nominal parameter between tests. These tests deliberately alter geometry to prove editability; the delivered baseline retains the exact table scale and orientation.

The coordinate mapping is `x = (1000*xTable)*axialChord/47.6144470215`, `y = (1000*yTable)*trailingEdgeY/(-21.59972305301)`, with extrusion `0 <= z <= span`. At nominal values both XY factors are exactly one. Reference-only `trueChord`, `signedStagger`, `trailingEdgeRadius` and `profilePerimeter` literals must not constrain the edit drivers back to their nominal values. Derived chord and angle describe the nominal part; the edited geometry's corresponding diagnostics can be recomputed separately.

| edited parameter | delta | expected volume delta | direction | expected bbox size delta (x,y,z) | formula with other parameters held fixed |
|---|---|---|---|---|---|
| `span` | +10 mm | +2306.3711778179277 mm³ | increase | (0, 0, 10) mm | `DeltaV = A*10`; cap start remains z = 0. |
| `axialChord` | +1 mm | +799.2348292276137 mm³ | increase | (1.0075237391351841, 0, 0) mm | Stretch x alone by `(axialChord+1)/axialChord`; `DeltaV = A*span/axialChord`; `DeltaBBoxX = (xMax-xMin)/axialChord`. All y coordinates and span stay fixed. |

Both volume deltas have relative tolerance 0.002. Bbox delta checks use the 0.01 mm contract tolerance. Neither edit operates on a derived parameter, and no equality assertions may prevent either edit. The axial edit moves both x extrema proportionally about x = 0; bbox-size increase is therefore slightly larger than the +1 mm TE-x edit.

**Independent numerical verification of the draft.**

| quantity | independently computed from workbook / polygon | contract or source target | difference |
|---|---|---|---|
| Ordered closed-loop vertices | 2000 finite, unique vertices; exact array equality | `profile.json: points_mm`, 2000 vertices | 0 coordinate differences |
| Polygon validity | Simple, valid polygon; one outer ring, zero holes | Required one closed profile | Pass |
| Area | 230.63711778196614 mm² by direct cross-product sum | 230.63711778179277 mm² ingest baseline | 1.734 × 10^-10 mm², summation roundoff |
| Perimeter | 123.78447524923155 mm | 123.78447524923155 mm | 0 at displayed precision |
| LE-to-TE chord | 52.284640202739865 mm | Derived parameter; documentary 52.285 mm | 0 versus derived target; -0.000359797260135 mm versus rounded workbook value |
| Signed stagger | -24.40085023652175 deg | Derived parameter; documentary magnitude 24.4 deg | 0 versus derived target; magnitude difference +0.00085023652175 deg |
| Extrusion volume | 38055.124434024416 mm³ | 38055.12443399581 mm³ | 2.861 × 10^-8 mm³, propagated summation roundoff |
| Surface area | 20885.712651687136 mm² | 20885.71265168679 mm² | 3.46 × 10^-10 mm², propagated summation roundoff |
| COM | (20.619657984838426, 1.0449253890203034, 82.5) mm | Same contract target | 0 at displayed precision |
| Full bbox | (-0.19685863578579998, -21.6984059788506, 0) to (47.77582706417, 9.51390836469706, 165) mm | Same envelope | 0 per axis |

These are source-derived analytic checks. No `zoo kcl analyze`, OpenCascade STEP measurement, STL measurement or CAD edit rebuild has occurred in this drafting task. Later verification must format and lint KCL, analyze it, export deterministic STEP and STL, and compare authoritative STEP measurements with these fixed acceptance values. Do not relax the contract to match a model.

## 6. Defaults retained

- Units are mm and deg; the source metres are converted exactly. No seed plate dimensions, feature dimensions or inferred manufacturing geometry are retained.
- `release_status: reconstruction` is retained because this task reconstructs published geometry.
- `material`, `density_kg_m3` and `process` remain null. Geometry and geometric COM are computable without assigning material; mass is unclaimed.
- Relative volume and export-agreement tolerance 0.002 is retained from the template. Surface area, transverse-section areas, cap areas and edit volume deltas also use 0.002. These allow small numerical/interpolation differences while preserving the source-derived nominal values.
- The 0.01 mm bbox/COM/cap-plane tolerance is an explicit drafting choice. It is smaller than the supplied point spacing and far smaller than either nose/terminal extent; it accounts for modest between-point extrema changes in a faithful curve. Coordinate landmarks and supplied-point fidelity are tighter at 0.001 mm.
- The documentary TE-radius tolerance 0.005 mm and perimeter tolerance 0.05 mm allow comparison of the stated nominal radius and dense polygonal baseline with a faithful curve. They do not authorize replacing the coordinates with a fitted primitive.
- Axial-section area tolerance is 0.01 relative because a small local interpolation difference at a highly curved nose or terminal contour changes a thin section more strongly than it changes total area. Spanwise full-profile area remains at 0.002 relative.
- The blockout band is explicitly ±1% of `A*span`, the one envelope-defining primary extrusion. It is an early scale/frame check; final volume tolerance remains ±0.2%.
- Interior section/probe positions are chosen verification locations, not inferred part dimensions. No optional cosmetic feature is added. Mesh deviation is null because no reference mesh exists.

## 7. Unrepresentable or low-confidence features

The entire published contour is required. No visible geometric feature is intentionally omitted. The authoritative data fully fix the points and span, but do not specify the original mathematical interpolation between rows. A future model must preserve all points, local curvature and shared endpoints without generic-airfoil replacement, smoothing or point reduction. The exact original spline degree, knots and continuity remain unknown. The stated 0.435 mm trailing-edge radius is documentary evidence; the contour remains authoritative if an independent radius check differs.

The schema's `FaceSpec` supports planar faces only. It can verify `spanStart` and `spanEnd`; it cannot name or classify arbitrary curved pressure-side and suction-side wall groups. The contract records these identities under features and interfaces. Later modeling must preserve source-side traceability even if one side generates several CAD faces. No inlet/outlet flow-domain or platform mating faces are introduced.

BBox, integrated quantities, sparse probes and six sections cannot alone prove passage through every source point or guarantee every local curve segment. Full source-point-to-boundary verification at ≤0.001 mm, plus contour review for between-point excursions, remains required downstream. Mesh deviation is not fabricated from the 2D plot. Engine properties, authoritative exported STEP geometry, STL agreement, named faces and edited KCL rebuilds remain unverified until the modeling stage.

**Bundle validation.** The required command is:

```sh
cd /Users/danieldriscoll/dual/opencad
.venv/bin/python -m opencad check-bundle /Users/danieldriscoll/dual/opencad/designs/.staging-spleen-c1-blade --name spleen-c1-blade
```

The bundle passes the repository validator, which accepts the generated `reference/profile.png` alongside `reference/profile.json`. The image remains an illustrative reference with its original hash. The required command exits 0 and prints `ok:` with 7 parameters, 7 features and provenance counts of 4 stated, 1 measured (reference model), and 2 derived.

The completed contract passed `PartContract` loading and cross-reference validation. Inline `.venv/bin/python -` checks also passed for all four source hashes, the exact intent text, all eight brief headings, the empty checkpoint log, 2000 source points, 18 solid/void probes, six section areas, both named-cap definitions, and the two edit-delta calculations. Only the six originally supplied bundle files are present.

**Open questions, matching the contract:**

1. What material, density and manufacturing process, if any, should be assigned? The supplied sources establish geometry only; these fields remain null and no mass claim is made.
2. Is a specific original interpolation law required between published points? No spline degree, knot vector or continuity convention is supplied. The reconstruction must retain every point within 0.001 mm and preserve the contour without smoothing; exact between-point authoring geometry remains unspecified.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-0.1969, -21.6984, 0.0] → [47.7758, 9.5139, 165.0] | 38055.12510178579 | pass | 2026-09-15T18:40:41Z: within envelope and band |
