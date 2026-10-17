# chiral-keyplate — design brief

## 1. Intent and configuration

User intent, verbatim:

> Model the square key plate described in the attached text spec as one solid. Frame: origin at the plate centre in XY, z = 0 on the bottom face, +z through the thickness, +x and +y along the plate edges. Cut four identical rectangular slots from the top as 4 mm-deep pockets in a C4 pinwheel whose first slot is centred at (20, 8) mm with its long axis along x; the other three are 90 degree rotations about z. The pinwheel is chiral — do not emit the mirrored arrangement, a centred cross, or any pattern with a mirror plane. Name the four pocket floors. One solid; export STEP and STL.

The authoritative text defines an 80 × 80 × 8 mm square plate with four sharp rectangular blind pockets, each 16 × 6 × 4 mm. The intended key is identified by its signed pocket positions and orientations. The nominal model has C4 rotational symmetry and no mirror plane. All eight source parameters are independent, stated dimensions; no geometric dimension needs inference.

The later CAD deliverable is one native parametric solid, with four individually named pocket floors, exported as STEP and STL in the contract frame and in millimetres. This drafting task supplies the contract and brief. Geometry, named-face persistence, engine measurements and exports remain to be produced and verified downstream.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| `sources/chiral-keyplate-spec.md` | text | authoritative | `0036c51f5df296508a684f749dc85a5e789cc0b325273221082d1a28eff95798` | Millimetres; unversioned supplied text, with this full hash identifying the revision. Matches the supplied prefix `0036c51f5df2`. Lines 3–5 define the blank/frame; 7–15 define all four pockets; 17–20 fix handedness; 22–26 require parameters, edit tests and named floors. |

This is the only file under `sources/`; there is no `reference/` input. No images, dimensioned raster drawings, meshes, coordinate-table ingest or reference measurements were supplied. STEP and STL export requirements come directly from the user intent above. The schema and seed template determine document structure, not additional part geometry.

## 3. Requirement record

All tolerances below are digital comparison thresholds. The source gives exact nominal dimensions without production tolerances. Parameter evidence and acceptance formulas appear in section 5.

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Plate envelope | 80 × 80 × 8; x/y centred, bottom at zero | mm | Spec lines 3–5, 22 | Parameters ±0.01; bbox ±0.05 | stated |
| Coordinate system | Right-handed; +x/+y along edges, +z from bottom to top | mm, deg | Spec lines 4–5, 11–15; user intent | Signed frame fixed | stated |
| Pocket count and form | Four identical sharp rectangular blind pockets | count | Spec lines 7–9 | Exactly 4 | stated |
| Pocket dimensions | Length 16, width 6, depth 4 | mm | Spec lines 7–8, 23 | ±0.01 each | stated |
| Slot A | Centre (20, 8), long side parallel to x | mm | Spec line 11 | Centre parameters ±0.01 | stated |
| Slot B | Centre (-8, 20), long side parallel to y; A rotated +90 | mm, deg | Spec lines 12–13 | Signed rotation exact; floor centre ±0.05 | stated |
| Slot C | Centre (-20, -8), long side parallel to x; A rotated +180 | mm, deg | Spec line 14 | Signed rotation exact; floor centre ±0.05 | stated |
| Slot D | Centre (8, -20), long side parallel to y; A rotated +270 | mm, deg | Spec line 15 | Signed rotation exact; floor centre ±0.05 | stated |
| Chirality | Specified pinwheel; no mirrored pattern, centred cross or mirror plane | — | Spec lines 17–20; user intent | Required; signed probes and four face centres | stated |
| Bottom web | Intact under all pockets; thickness 8 - 4 = 4 | mm | Spec lines 7–8; thickness and depth | Section area ±0.2%; solid probes | stated; dimension derived |
| Named floors | `pocketFloorA`, `pocketFloorB`, `pocketFloorC`, `pocketFloorD`; z = 4, outward normal +z; distinct centres | mm | Spec lines 25–26 | Plane/centre ±0.05; each area ±0.2% | stated; identifiers assigned |
| Body count | One connected solid | count | Spec line 22; user intent | Exactly 1 | stated |
| Editable constants | `plateWidth`, `plateHeight`, `plateThickness`, `slotLength`, `slotWidth`, `slotDepth`, `slotCentreX`, `slotCentreY` | mm | Spec lines 22–24 | Eight literal top-level constants | stated |
| Edit demonstrations | Independently change plateThickness and slotLength by +2 | mm | Spec lines 24–25 prefer these parameters; increments chosen here | Volume delta ±0.2%; specified bbox deltas | stated preference; test design |
| Exports | STEP and STL; one solid, preserved frame and mm scale | — | User intent | Volume agreement ±0.2% | stated |
| Material and density | Unspecified; remain null | —, kg/m³ | No source assignment | No mass claim | open |
| Manufacturing process and production tolerances | Unspecified; process remains null | — | No source assignment | Digital tolerances do not supply these | open |

## 4. Coordinate frame, scale, and measurement method

Place the origin at the centre of the bottom square. The nominal plate occupies x = [-40, 40], y = [-40, 40], z = [0, 8]. In a top view looking from +z toward the bottom, +x points right and +y points up. +z points from the bottom toward the top. Slot A lies in the positive-x, positive-y quadrant, with its 16 mm side along x. These conventions fix the coordinate signs and distinguish the required handedness.

The primary datum `bottomDatum` is the intact bottom plane z = 0, outward normal -z. `xCentreDatum` is the vertical centre plane x = 0 and `yCentreDatum` is y = 0; their positive sides contain slot A's centre. `topDatum` is the remaining top plane z = plateThickness, outward normal +z. Measure slotDepth downward from the top; the floors are at z = plateThickness - slotDepth. Positive rotations about +z are counter-clockwise when viewed from +z.

Read nominal numbers directly from the text, using one model millimetre per stated millimetre and degrees for rotations. There is no image scale, perspective correction, pixel feature or line-width uncertainty to record. No quantity is classified as measured or measured (reference model). Digital tolerances are documented choices, not measurement uncertainty.

Use R(x, y) = (-y, x) to rotate both the centre and rectangular footprint of A through successive positive quarter turns. These bounds follow analytically from the stated dimensions; each pocket occupies z = [4, 8] and opens upward.

| slot / named floor | rotation from A | centre (x, y), mm | long axis | x bounds, mm | y bounds, mm |
|---|---|---|---|---|---|
| A / `pocketFloorA` | 0 deg | (20, 8) | x | [12, 28] | [5, 11] |
| B / `pocketFloorB` | +90 deg | (-8, 20) | y | [-11, -5] | [12, 28] |
| C / `pocketFloorC` | +180 deg | (-20, -8) | x | [-28, -12] | [-11, -5] |
| D / `pocketFloorD` | +270 deg | (8, -20) | y | [5, 11] | [-28, -12] |

The plate is square at nominal values; do not equality-lock plateWidth to plateHeight. Keep the eight parameters as literal top-level constants in the later KCL model. Obtain pocket positions, bounds and floor height from expressions using them. C4 repetition means four total pockets including A. Preserve the pattern's handedness when dimensions are edited. Appropriate sanity conditions include positive lengths, slotLength greater than slotWidth, 0 < slotDepth < plateThickness, and non-overlapping pockets inside the plate.

Chirality is checked in this fixed frame using distinct floor centres and complementary material/cavity probes. Volume, bbox, centre of mass, principal inertia, horizontal section area/counts and exterior silhouette cannot distinguish the reflected pinwheel. The x-reflected pocket centres (-20, 8), (8, 20), (20, -8), (-8, -20) at z = 6 must remain solid, while the four intended centres at z = 6 must be void. The axis-arm points (20, 0), (0, 20), (-20, 0), (0, -20) at z = 6 must remain solid as guards against a centred cross. No reference mesh exists, so deviation p95, Hausdorff distance, silhouette IoU and `not_matching` against a mirrored mesh cannot be established from this bundle.

## 5. Measurement and inference record

The parameter record contains exactly eight stated parameters, zero measured, zero measured (reference model), zero derived, zero inferred and zero defaulted parameters. Derived acceptance quantities are separate from the parameter list. Formula abbreviations are W = plateWidth, H = plateHeight, T = plateThickness, L = slotLength, w = slotWidth, d = slotDepth, a = slotCentreX, b = slotCentreY; these are explanatory aliases, not additional required constants.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| `plateWidth` | 80 mm | ±0.01 mm | stated | Spec line 22: "plateWidth (80 mm)"; x span. |
| `plateHeight` | 80 mm | ±0.01 mm | stated | Spec line 22: "plateHeight (80 mm)"; y span. |
| `plateThickness` | 8 mm | ±0.01 mm | stated | Spec line 22: "plateThickness (8 mm)"; bottom-to-top span. |
| `slotLength` | 16 mm | ±0.01 mm | stated | Spec line 23: "slotLength (16 mm)"; line 11 fixes A's long side parallel to x. |
| `slotWidth` | 6 mm | ±0.01 mm | stated | Spec line 23: "slotWidth (6 mm)". |
| `slotDepth` | 4 mm | ±0.01 mm | stated | Spec line 23: "slotDepth (4 mm)"; lines 7–8 require a blind pocket. |
| `slotCentreX` | 20 mm | ±0.01 mm | stated | Spec line 23: "slotCentreX (20 mm)"; line 11 gives A at (20, 8). |
| `slotCentreY` | 8 mm | ±0.01 mm | stated | Spec line 24: "slotCentreY (8 mm, the centre of slot A)"; signed positive y offset. |

For these acceptance quantities, V0 = W × H × T = 51,200 mm³ is the envelope-only blank and Vr = 4 × L × w × d = 1,536 mm³ is the removed volume. The four pockets are disjoint, wholly inside the outline, and leave a 4 mm continuous web.

| acceptance value | nominal value | digital tolerance / criterion | provenance | formula / evidence |
|---|---|---|---|---|
| `envelope.min` | (-40, -40, 0) mm | ±0.05 mm per coordinate | derived | (-W/2, -H/2, 0), using the stated bottom-centred frame. |
| `envelope.max` | (40, 40, 8) mm | ±0.05 mm per coordinate | derived | (W/2, H/2, T); pockets do not intersect outside faces. |
| `acceptance.bbox_tolerance` | 0.05 mm | Absolute coordinate threshold | defaulted | Retained envelope comparison allowance; not a production tolerance. Bbox size is (80, 80, 8) mm. |
| `acceptance.volume` | 49,664 mm³ | ±0.2% = ±99.328 mm³ | derived | V = W × H × T - 4 × L × w × d = V0 - Vr. |
| `acceptance.surface_area` | 16,064 mm² | ±0.2% = ±32.128 mm² | derived | 2 × (W × H + W × T + H × T) + 4 × 2 × (L + w) × d = 15,360 + 704. Removed top area 384 mm² is replaced by equal floor area. |
| `acceptance.center_of_mass` | (0, 0, 382/97) = (0, 0, 3.9381443298969074) mm | ±0.05 mm per axis | derived | Equal pocket volumes and centre sum (0, 0) give x = y = 0. z = [V0 × T/2 - Vr × (T - d/2)] / (V0 - Vr) = 195,584 / 49,664. Uniform-density geometric centroid; no mass assignment. |
| `acceptance.solid_count` | 1 | Exact | stated | Spec line 22. Four blind pockets leave one connected plate. |
| `sections.lowerWeb` | z = 2 mm; area 6,400 mm²; loops 1; holes 0 | Area ±0.2% = ±12.8 mm²; topology exact | derived | Plane at (T - d)/2; area W × H beneath all floors. |
| `sections.pocketBand` | z = 6 mm; area 6,016 mm²; loops 1; holes 4 | Area ±0.2% = ±12.032 mm²; topology exact | derived | Plane at T - d/2; area W × H - 4 × L × w. Each cavity supplies one inner boundary. |
| `sections.slotALongitudinal` | y = 8 mm; area 576 mm²; loops 1; holes 0 | Area ±0.2% = ±1.152 mm²; topology exact | derived | Plane at b, through A only; area W × T - L × d = 640 - 64. The top-open notch belongs to the outer boundary. |
| `sections.slotATransverse` | x = 20 mm; area 616 mm²; loops 1; holes 0 | Area ±0.2% = ±1.232 mm²; topology exact | derived | Plane at a, through A only; area H × T - w × d = 640 - 24. The top-open notch belongs to the outer boundary. |
| `faces.pocketFloorA` | z = 4 mm; normal +z; area 96 mm²; in-plane centre (20, 8) mm; mode one | Plane/centre distance ±0.05 mm; area ±0.2% = ±0.192 mm² | stated position/normal; derived area | z = T - d, area L × w, centre (a, b). Spec lines 11, 25–26. |
| `faces.pocketFloorB` | z = 4 mm; normal +z; area 96 mm²; in-plane centre (-8, 20) mm; mode one | Plane/centre distance ±0.05 mm; area ±0.2% = ±0.192 mm² | stated position/normal; derived area | z = T - d, area L × w, centre (-b, a). Spec lines 12–13, 25–26. |
| `faces.pocketFloorC` | z = 4 mm; normal +z; area 96 mm²; in-plane centre (-20, -8) mm; mode one | Plane/centre distance ±0.05 mm; area ±0.2% = ±0.192 mm² | stated position/normal; derived area | z = T - d, area L × w, centre (-a, -b). Spec lines 14, 25–26. |
| `faces.pocketFloorD` | z = 4 mm; normal +z; area 96 mm²; in-plane centre (8, -20) mm; mode one | Plane/centre distance ±0.05 mm; area ±0.2% = ±0.192 mm² | stated position/normal; derived area | z = T - d, area L × w, centre (b, -a). Spec lines 15, 25–26. |
| `acceptance.blockout.volume_min` | 51,097.6 mm³ | Lower bound, inclusive | derived with chosen band | V0 × (1 - 0.002); blockout is the whole plate blank before pockets. |
| `acceptance.blockout.volume_max` | 51,302.4 mm³ | Upper bound, inclusive | derived with chosen band | V0 × (1 + 0.002). Finished pocketed volume is outside this envelope-only band. |
| `acceptance.export_volume_tolerance_rel` | 0.002 | KCL/STEP/STL volume agreement within 0.2% | defaulted | Retained schema threshold; the exact STEP solid is authoritative downstream. |
| `acceptance.deviation` | null | No deviation, Hausdorff or silhouette threshold | not applicable | No reference mesh or ingest measurements exist. No invented reference acceptance. |

The schema's section `loops` count is the number of outer solid loops, excluding holes. The `count` feature probe therefore expects one loop in both horizontal sections. The four-pocket count is encoded as `pocketBand.expect.holes: 4`, the four named floor specifications and `chiralPinwheel.count: 4`. Each floor uses `mode: one` and its own in-plane centroid so one measured face cannot satisfy multiple identities.

Probe construction is analytic. For A, void probes at z = 6 include the centre, x = 13 and 27 at y = 8, and y = 6 and 10 at x = 20. These span both pocket dimensions while staying at least 1 mm from a wall. Solid probes sit below the floor at (20, 8, 2) and 1 mm outside the four plan walls at z = 6: (11, 8), (29, 8), (20, 4), (20, 12). The B/C/D probes are the +90/+180/+270 degree rotations of these points. Other probes check central and outer blank material, mirrored pocket centres and axis arms. Every probe is strictly inside its intended solid or void region, with minimum boundary clearance at least 1 mm, larger than the 0.01 mm parameter and 0.05 mm position allowances. No inferred wall is involved. Named-face centroids are intentional surface specifications rather than interior probes.

Edit tests change one independent parameter at a time, holding every other parameter fixed. Formula-derived geometry follows the edit; tabulated section coordinates and face positions describe the nominal configuration. Rebuild edit variants for delta checks and restore the nominal model for its full acceptance checks.

| parameter edit | expected volume delta | direction | expected bbox size delta, mm | formula and resulting geometry |
|---|---|---|---|---|
| `plateThickness`: 8 → 10 mm, delta +2 | +12,800 mm³, tolerance ±25.6 mm³ | increase | (0, 0, 2) | ΔV = W × H × ΔT because d is fixed. Edited volume 62,464 mm³; bbox min (-40, -40, 0), max (40, 40, 10). Top rises to z = 10, floors to z = 6, web thickness to 6 mm; pocket removal stays 1,536 mm³. |
| `slotLength`: 16 → 18 mm, delta +2 | -192 mm³, tolerance ±0.384 mm³ | decrease | (0, 0, 0) | ΔV = -4 × w × d × ΔL = -4 × 6 × 4 × 2. Edited volume 49,472 mm³; centres, depth, floor height and plate bbox stay fixed. Each pocket grows 1 mm at both long ends; pockets remain disjoint and inside the outline. |

## 6. Defaults retained

No template geometry remains, and no parameter uses an inferred or defaulted nominal value. The following document and digital-comparison settings are retained or explicitly selected:

| setting | value | reason |
|---|---|---|
| Schema and release status | schema_version 1; reconstruction | A source-defined CAD reconstruction contract, without a production-release claim. |
| Units | mm, deg | Match source millimetres and stated quarter-turn rotations. |
| Parameter digital tolerance | 0.01 mm for every parameter | Retains the seed's nonzero threshold for exact text dimensions. No pixel uncertainty exists. |
| Envelope / bbox / COM tolerance | 0.05 mm | Retains the seed's absolute allowance for fixed-frame comparisons. |
| Global volume and export agreement | Relative 0.002 | Retains the seed volume band and schema export agreement default. |
| Surface, section and floor areas | Relative 0.002 | Selected for exact planar analytic geometry; the wider schema area defaults are not used. |
| Floor plane and centre tolerance | 0.05 mm, explicitly set | Same absolute position allowance for four repeated coplanar faces; each is assigned separately. |
| Blockout band | Envelope blank volume ±0.2% | Compares the primary uncut 51,200 mm³ prism with a small digital allowance. |
| Edit increments and tolerance | +2 mm independently; relative delta tolerance 0.002 | Clear, nonzero volume changes within valid geometry, using the preferred source parameters. |
| Feature optionality | All six features required | Blank, four pockets and their C4 relationship are functional requirements. No cosmetic feature is specified. |
| Face matching mode | Explicit `one` for every floor | Preserves four named identities on z = 4; combined area is not requested. |
| Material, density, process | null | Unspecified; none is necessary to reconstruct geometry. No mass claim. |
| External interfaces | Empty list | No mating component or additional mating-face requirement is supplied; requested floors are in acceptance. |
| Reference deviation | null | No reference geometry establishes a numerical band. |

## 7. Unrepresentable or low-confidence features

All specified geometry is representable by one square prism and four rectangular blind cuts. The text supplies every required dimension and signed pocket position. Rectangular pockets are interpreted literally with straight walls, flat floors and sharp corners; no fillet, chamfer, draft or manufacturing tool radius is specified or introduced. No image-derived or low-confidence geometric feature remains unresolved.

The schema encodes chirality through fixed-frame probes and four separately matched floor centroids; it has no independent "no mirror plane" field. Section/global metrics support these checks and cannot establish handedness alone. Deviation p95 and `not_matching` against a mirrored reference are unavailable because this bundle has no reference mesh. Geometric face matching also does not prove that names survive a particular export format; the later CAD worker must create the four named face handles and verify STEP face identities and STL shape. The contract intent and this brief carry the STEP/STL requirement because PartContract has no dedicated export-format field.

Open questions, identical to the contract:

- What material and density, if any, should be assigned for physical mass reporting? Neither is specified; both remain null and no mass is claimed.
- What manufacturing process and physical production tolerances, if any, apply? They are not specified; process remains null and digital comparison tolerances are not manufacturing tolerances.

These questions do not prevent the specified geometric reconstruction. No model has been built for this drafting task; engine measurements, STEP/STL validity and actual edit-test rebuilds remain unverified downstream.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-40.0, -40.0, 0.0] → [40.0, 40.0, 8.0] | 51199.999999999985 | pass | 2026-09-16T09:06:25Z: within envelope and band |
