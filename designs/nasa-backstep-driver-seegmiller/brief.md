# nasa-backstep-driver-seegmiller — design brief

## 1. Intent and configuration

Model the air volume (flow passage) of the Driver-Seegmiller backward-facing-step channel for the parallel-roof (0 degree divergence) case described in the attached NASA validation page, as ONE solid suitable for CFD meshing. Use the documented ratios and the step height H = 0.5 in = 12.7 mm: step height to tunnel exit (downstream) height 1:9, step height to tunnel width 1:12, so the upstream channel height is the downstream height minus H. Cover exactly the documented computational domain x/H = -105 to +50. Frame: +x streamwise with x = 0 at the step face (upstream is negative x), +y spanwise across the tunnel width with y = 0 at one side wall, +z vertical with z = 0 at the downstream floor (the upstream floor therefore sits at z = H). Expose H, the width, the two channel heights, the roof angle, and the upstream/downstream domain lengths as named parameters, and name the flow-boundary faces (inlet, outlet, roof, upstream floor, step face, downstream floor, side walls) in the contract so the mesher can find them. The measured reattachment location is a downstream validation target, not a geometry input; do not tune anything to it.

The authoritative geometry is the supplied NASA text together with the user's explicit frame and full-width, three-dimensional air-volume requirement. The nominal result is a sharp, six-edge stepped profile swept through the full 152.4 mm width: one connected solid and eight external planar faces. NASA's published calculation used a two-dimensional grid; the requested span comes directly from its documented experimental width ratio.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| `sources/nasa-backstep-study01.md` | text | authoritative | `2aca80462b8cd0fd2554c59a156e6a1149921d26b51fbe763e393f3a065e05b2` | Supplied offline reproduction of [NASA Glenn Backstep: Study #1](https://www.grc.nasa.gov/WWW/wind/valid/backstep/backstep01/backstep01.html), created 1998-12-11 and last updated 2021-02-10. Introduction fixes ratios and roof configuration; Grid fixes H and x/H limits. Original units include inches, degrees, and dimensionless ratios. The described grid uses feet, but no grid coordinates were supplied. Figures are omitted. |

This is the only supplied source file. There is no `reference/` ingest, mesh, coordinate table, drawing, or image. The hash above was computed from the supplied bytes and matches the supplied prefix `2aca80462b8c`. The papers cited within the text are bibliography, not additional attached references. The user requirement is reproduced verbatim in section 1 and `contract.yaml`.

## 3. Requirement record

Tolerances below are digital comparison bands for ideal CAD geometry; the source supplies no manufacturing or experimental dimension uncertainty.

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Modeled region and topology | Air volume; one connected, watertight solid | body count | User intent | Exactly 1 body | stated |
| Step height H | 0.5 in = 12.7 | mm | NASA Grid; user intent | ±0.01 mm | stated |
| Step height : downstream exit height | 1:9; downstream height 114.3 | ratio; mm | NASA Introduction | Ratio defines nominal value; height ±0.01 mm | stated ratio; derived height |
| Step height : tunnel width | 1:12; full width 152.4 | ratio; mm | NASA Introduction | Ratio defines nominal value; width ±0.01 mm | stated ratio; derived width |
| Upstream channel height | 114.3 − 12.7 = 101.6 | mm | Common parallel roof and floor drop; user intent | ±0.01 mm | derived |
| Roof divergence | 0 | deg | NASA Introduction; user selection | ±0.001 deg | stated |
| Computational domain | x/H = −105 to +50; x = −1333.5 to +635 | dimensionless; mm | NASA Grid | Length parameters ±0.01 mm; finished bounds ±0.05 mm | stated limits; derived coordinates |
| Origin and axes | Step/downstream-floor/y = 0 corner; +x downstream, +y across width, +z up | frame | User intent | Finished bounds ±0.05 mm | stated |
| Floors and roof | Upstream floor z = 12.7; downstream floor z = 0; roof z = 114.3 | mm | User frame, H, and parallel-roof geometry | Face planes ±0.05 mm | stated datums; derived roof |
| Named CFD boundaries | `inlet`, `outlet`, `roof`, `upstreamFloor`, `stepFace`, `downstreamFloor`, `sideWallY0`, `sideWallYMax` | 8 faces | User intent | One planar face per name; area ±0.2%; plane ±0.05 mm | required; identifiers assigned |
| Step and through-flow opening | One sharp floor drop; no internal face at x = 0 above H; no internal holes | topology | Backward-facing step and single air-solid intent | Section loops = 1, holes = 0 | derived |
| Experimental reattachment | x_r/H = 6.26, corresponding to x = 79.502 mm | dimensionless; mm | NASA Comparisons, Experiment row | No geometry tolerance or probe; source does not give validation uncertainty | stated validation target only |

All requested geometric dimensions are fixed by these requirements. There are no unresolved geometry questions and no inferred dimensions.

## 4. Coordinate frame, scale, and measurement method

Place the origin at the lower corner of the vertical step face on the y = 0 side wall: the intersection of x = 0, downstream floor z = 0, and y = 0. Positive x is downstream, positive y goes from that side wall across the tunnel, and positive z is upward. The inlet is at x = −105H, the outlet at x = 50H, and the second side wall at y = 12H. Upstream air begins at z = H; downstream air begins at z = 0. The common roof is at z = 9H. Do not recenter either x or y. The reproducible datums are named in `frame.datums`.

Use millimetres and degrees. Convert the stated half-inch height using the exact identity 1 in = 25.4 mm, then multiply H by the stated nondimensional ratios and domain extents. No image scale, pixel evidence, rectification, or mesh measurement exists for this task. The source's feet units apply to its unprovided grid files, not to these text-derived dimensions.

The closed nominal air domain is the union of two touching rectangular reaches:

- Upstream: −1333.5 ≤ x ≤ 0, 0 ≤ y ≤ 152.4, 12.7 ≤ z ≤ 114.3.
- Downstream: 0 ≤ x ≤ 635, 0 ≤ y ≤ 152.4, 0 ≤ z ≤ 114.3.

The x-z outline, in boundary order, is (−1333.5, 12.7), (0, 12.7), (0, 0), (635, 0), (635, 114.3), (−1333.5, 114.3), closed to the start. A later model can extrude this single primary outline across y to obtain one solid without an internal interface. The step face exists only for 0 ≤ z ≤ H. All face normals point outward from the air. For `acceptance.faces[].center`, the in-plane coordinate order is (y,z) for an x plane, (x,z) for a y plane, and (x,y) for a z plane.

In feature probes, `solid` means inside the air volume; `void` means outside that modeled air volume, including the excluded region below the upstream floor. Probe coordinates avoid boundaries. The closest probes to the step/floor boundary have 6.35 mm clearance, greater than both the 0.01 mm parameter tolerance and 0.05 mm geometric tolerance. No inferred walls are involved.

## 5. Measurement and inference record

Seven named parameters are exposed: two stated and five derived; none are measured, measured from a reference model, inferred, or defaulted. Every value is nominal. The source ratios 9 and 12 and domain multipliers 105 and 50 are evidence constants in the formulas, not additional adjustable geometry parameters.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| `stepHeight` | 12.7 mm | ±0.01 mm | stated | NASA Grid: “H is 0.5 inches.” Exact unit conversion: 0.5 × 25.4 = 12.7 mm; user explicitly supplies the same value. |
| `channelWidth` | 152.4 mm | ±0.01 mm | derived | `12 * stepHeight`; NASA Introduction states H:width = 1:12. |
| `downstreamHeight` | 114.3 mm | ±0.01 mm | derived | `9 * stepHeight`; NASA Introduction states H:exit-height = 1:9. |
| `upstreamHeight` | 101.6 mm | ±0.01 mm | derived | `downstreamHeight - stepHeight`; the parallel roof stays at one elevation while the upstream floor is raised by H. |
| `roofAngle` | 0 deg | ±0.001 deg | stated | NASA Introduction specifies “zero degree divergence of the top wall”; user selects this case. |
| `upstreamLength` | 1333.5 mm | ±0.01 mm | derived | `105 * stepHeight`; NASA Grid gives x/H = −105 at the inlet; the length parameter is positive. |
| `downstreamLength` | 635 mm | ±0.01 mm | derived | `50 * stepHeight`; NASA Grid gives x/H = +50 at the outlet. |

For the acceptance formulas, let H = `stepHeight`, W = `channelWidth`, U = `upstreamHeight`, D = `downstreamHeight`, Lu = `upstreamLength`, Ld = `downstreamLength`, and L = Lu + Ld = 1968.5 mm. Let Au = Lu·U = 135483.6 mm², Ad = Ld·D = 72580.5 mm², and A = Au + Ad = 208064.1 mm². These are analytic helper quantities, not extra contract parameters. All formulas assume the specified 0 degree roof and nominal U = D − H.

| acceptance value | expected | tolerance | provenance | formula / evidence |
|---|---|---|---|---|
| `envelope.min` | [−1333.5, 0, 0] mm | ±0.05 mm per coordinate | derived | [−Lu, 0, 0], from the inlet and two origin datums. |
| `envelope.max` | [635, 152.4, 114.3] mm | ±0.05 mm per coordinate | derived | [Ld, W, D]. |
| Envelope size | [1968.5, 152.4, 114.3] mm | Bounds tested at ±0.05 mm | derived | [Lu + Ld, W, D]. |
| `acceptance.bbox_tolerance` | 0.05 mm | Absolute comparison band | defaulted | Retained template digital tolerance; not physical dimensional uncertainty. |
| `acceptance.volume` | 31708968.84 mm³ | ±0.2% = ±63417.93768 mm³ | derived | V = W·A = W·(Lu·U + Ld·D); upstream volume 20647700.64 plus downstream volume 11061268.2 mm³. Independent check: W·L·D − W·Lu·H. |
| `acceptance.surface_area` | 1050965.64 mm² | ±0.2% = ±2101.93128 mm² | derived | S = 2A + W·(2L + U + D + H). Equals the sum of the eight external face areas below. |
| `acceptance.center_of_mass` | [−323.406976744186, 76.2, 61.2848837209302] mm | ±0.05 mm per axis | derived | Cx = [Au·(−Lu/2) + Ad·(Ld/2)]/A; Cy = W/2; Cz = [Au·(H + U/2) + Ad·(D/2)]/A. This is a uniform-volume centroid; density is not needed. |
| `acceptance.solid_count` | 1 | Exact integer | stated | User requires ONE CFD-meshable air solid. |
| `acceptance.sections.upstreamMid` | x = −666.75 mm; area 15483.84 mm²; loops 1; holes 0; islands_min 1 | Area ±0.2%; topology exact | derived | Plane x = −Lu/2; rectangular area W·U. |
| `acceptance.sections.downstreamMid` | x = 317.5 mm; area 17419.32 mm²; loops 1; holes 0; islands_min 1 | Area ±0.2%; topology exact | derived | Plane x = Ld/2; rectangular area W·D. |
| `acceptance.sections.spanMid` | y = 76.2 mm; area 208064.1 mm²; loops 1; holes 0; islands_min 1 | Area ±0.2%; topology exact | derived | Plane y = W/2; stepped-profile area A. |
| `acceptance.sections.belowStep` | z = 6.35 mm; area 96774 mm²; loops 1; holes 0; islands_min 1 | Area ±0.2%; topology exact | derived | Plane z = H/2; downstream footprint area W·Ld. |
| `acceptance.sections.aboveStep` | z = 63.5 mm; area 299999.4 mm²; loops 1; holes 0; islands_min 1 | Area ±0.2%; topology exact | derived | Plane z = H + U/2; full passage footprint area W·L. |
| `acceptance.blockout.volume_min` | 31645550.90232 mm³ | Inclusive lower bound | derived | 0.998·V, for the primary stepped extrusion without any secondary details. |
| `acceptance.blockout.volume_max` | 31772386.77768 mm³ | Inclusive upper bound | derived | 1.002·V, the same ±0.2% digital band used for nominal volume. |
| `acceptance.export_volume_tolerance_rel` | 0.002 | Relative comparison band | defaulted | Retained schema/template KCL-versus-STEP-versus-STL agreement threshold. |

The blockout is the complete stepped primary envelope, expressible as one profile extrusion or the two primary reaches. Its volume is V because there are no secondary features. A full bounding cuboid would contain 34289931.42 mm³, including 2580962.58 mm³ below the upstream floor that is outside the flow passage; it is not the specified primary outline and must fail the blockout band.

The table below records every field needed to identify the eight boundary faces. Every face uses `mode: one`, plane tolerance ±0.05 mm, and area tolerance ±0.2%. Centers are supplied for all faces, although none of the eight intended faces repeat on the same oriented plane. Each named boundary is one face; no implicit area sum is requested. The centers are analytic face centroids in the in-plane coordinate convention from section 4.

| acceptance face | plane; outward normal | area (mm²) | in-plane center (mm) | formula / evidence |
|---|---|---|---|---|
| `inlet` | x = −1333.5; −x | 15483.84 | [76.2, 63.5] | x = −Lu; area W·U; center [W/2, H + U/2]. |
| `outlet` | x = 635; +x | 17419.32 | [76.2, 57.15] | x = Ld; area W·D; center [W/2, D/2]. |
| `roof` | z = 114.3; +z | 299999.4 | [−349.25, 76.2] | z = D; area W·L; center [(Ld − Lu)/2, W/2]. |
| `upstreamFloor` | z = 12.7; −z | 203225.4 | [−666.75, 76.2] | z = H; area W·Lu; center [−Lu/2, W/2]. |
| `stepFace` | x = 0; −x | 1935.48 | [76.2, 6.35] | Lower step boundary, 0 ≤ z ≤ H; area W·H; center [W/2, H/2]. |
| `downstreamFloor` | z = 0; −z | 96774 | [317.5, 76.2] | Downstream floor datum; area W·Ld; center [Ld/2, W/2]. |
| `sideWallY0` | y = 0; −y | 208064.1 | [−323.406976744186, 61.2848837209302] | Span datum; area A; center [Cx, Cz] from the stepped-profile centroid. |
| `sideWallYMax` | y = 152.4; +y | 208064.1 | [−323.406976744186, 61.2848837209302] | y = W; area A; center [Cx, Cz]. |

Edit tests are temporary diagnostic variants. Each overrides only the listed derived parameter's nominal formula while all six other parameter values remain fixed. A later KCL author must declare all seven contract parameters as literal top-level constants, document their nominal formulas, and avoid equality locks between parameters. These three geometric degrees of freedom are chosen because width and either reach length can change independently without disturbing the linked floor/height geometry or the selected parallel-roof case. The stated H and roof angle are therefore not used for isolated edit tests. Changing the linked heights or selecting a divergent roof is a different configuration and has no acceptance claim here.

| edited parameter | added delta | expected volume delta (mm³) | direction | expected bbox size delta (mm) | formula and placement |
|---|---|---|---|---|---|
| `channelWidth` | +12.7 mm | 2642414.07 | increase | [0, 12.7, 0] | ΔV = ΔW·(Lu·U + Ld·D) = 12.7·A. Keep y = 0 fixed and move the second wall to y = 165.1. |
| `upstreamLength` | +12.7 mm | 196644.768 | increase | [12.7, 0, 0] | ΔV = ΔLu·W·U. Keep x = 0 and the outlet fixed; move the inlet from −1333.5 to −1346.2. |
| `downstreamLength` | +12.7 mm | 221225.364 | increase | [12.7, 0, 0] | ΔV = ΔLd·W·D. Keep x = 0 and the inlet fixed; move the outlet from 635 to 647.7. |

Each expected volume delta has a ±0.2% relative tolerance; bbox size deltas use the 0.05 mm contract band. The final deliverable retains the nominal source dimensions and documented x/H endpoints. No edit test changes or uses reattachment data.

## 6. Defaults retained

The template's `release_status: reconstruction` remains appropriate for reconstructing a documented validation geometry. Its 0.05 mm envelope/centroid comparison tolerance, 0.01 mm length-parameter tolerance, and 0.002 relative volume agreement band are retained as digital checks. The same 0.002 area band is assigned to the simple analytic planar sections and faces; the roof-angle band is 0.001 deg. These bands permit numerical comparisons and do not claim experimental uncertainty. Section counts and the one-body requirement are exact integers. No seeded geometry dimensions or defaulted dimension parameters are retained.

Material is air, as requested; `density_kg_m3` stays null because no thermodynamic state or density is specified and this bundle makes no mass claim. The process is a CFD flow domain with no manufacturing. Every geometric feature is required, so the schema default `optional: false` is retained. Face matching is explicitly `mode: one` for all boundaries. `acceptance.deviation` is omitted because no reference mesh exists. There are no inferred/defaulted geometric dimensions and `open_questions` is empty.

## 7. Unrepresentable or low-confidence features

All requested geometry is representable using planar boundaries; no requested geometric feature has low-confidence dimensional evidence. The following source details are recorded without introducing extra geometry:

| source detail | treatment and reason |
|---|---|
| NASA's single-zone hole/fringe implementation of the step | A grid boundary technique, not a physical interior hole. The CAD air domain has the specified sharp floor step and no internal section holes. |
| 238 × 185 grid, clustering, y+ targets, and near-wall point counts | Meshing instructions and resolution data, not CAD dimensions or features. |
| First 12 Jmax points treated as inviscid; remaining roof treated as viscous | Boundary-condition assignment on a grid. The supplied text gives no physical split coordinate. The user requests a named roof face, so this contract provides one full roof boundary and assigns no invented split. Reproducing that numerical assignment would require grid data in a separate CFD setup task. |
| Inflow/outflow and viscous-wall conditions; two-dimensional calculation | Geometric faces are named for later CFD setup. No flow fields, wall-law values, or three-dimensional side-wall solver conditions are inferred. |
| Experimental reattachment x_r/H = 6.26 and model-dependent predictions | Validation results only. The experimental dimensional location 6.26 × 12.7 = 79.502 mm is recorded as context; it sets no dimension, face, refinement zone, probe, or edit test. The source gives no validation uncertainty band. |
| Omitted figures and unprovided Plot3d/common grid files | No pixel measurements, mesh deviations, or reference-model measurements can be claimed. Text and explicit user intent fully determine the requested ideal geometry. |
| Real wall thickness, roughness, step-edge rounding, or divergent-roof variants | Outside the requested ideal air-domain configuration. No dimensions, fillets, chamfers, shell thicknesses, or nonzero roof angles are invented. |

There are no open questions for this contract's geometry scope. This drafting task provides analytic acceptance targets; it creates no KCL or CAD artifact. Engine measurements, STEP topology/face verification, actual edit rebuilds, and a blockout verdict remain for the modeling pipeline. Section 8 is intentionally left with no log entries until a blockout is measured.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-1333.5, 0.0, 0.0] → [635.0, 152.4, 114.3] | 31708968.839999992 | pass | 2026-09-16T08:17:36Z: within envelope and band |
