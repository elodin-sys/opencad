# benchy — design brief

## 1. Intent and configuration

User intent, verbatim:

> Create a CAD model for a standard benchy the tugboat, used by 3D printers for calibration checking. Once complete, I will print it and physically measure the features against a control I already have.

This is a 1:1 reconstruction of Creative Tools’ #3DBenchy calibration tugboat. Official caliper dimensions and labelled drawings fix overall size, selected openings, chimney bore, cargo-box cavity, bow overhang and roof slope. The finished printed volume is stated as 15.55 cm³. The hull outer mould line, cabin envelope, chimney height above the roof, and most interior details are not published; those become inferred build parameters with wide digital tolerances, or open questions.

Authoritative numbers come from the transcribed official specification and the Creative Tools brochure, cross-checked against the labelled dimension rasters. The user prompt quotes a subset of those sizes and a Bambu Lab 1:1 print that matched 60 × 31 × 48 mm. The supplied photograph is illustrative: it identifies features and openings; it is not a scale drawing. Print layer lines are not CAD.

The later CAD deliverable is one native parametric solid in millimetres, intended to print upright on the keel without supports, exported as STEP and STL in the contract frame. This drafting task supplies the contract and brief. Geometry, engine measurements and exports remain to be produced downstream. Initialization is a checkpoint, not part validation, and does not claim a match to the official STL or to the user’s physical control print.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| `sources/prompt.md` | text | illustrative | `12d7b59cdbd0098cf651597ab3cb1f544e38fd288f24a9719293280d614e6bfc` | User request; quotes overall 60 × 31 × 48 mm, roof 23 mm, cargo box 12.00 × 10.81 / 8.00 × 7.00 × 9.00 mm; cites 3dbenchy.com/dimensions/. |
| `sources/3dbenchy-spec.md` | text | authoritative | `8ad17ab0866082cc9fbd896869f8f70a53096b5aead5e8a16fb55043033d4da4` | Transcription of official dimensions, 15.55 cm³ volume, feature list, unstated items, and the reconstruction frame. Retrieved 2026-09-16. |
| `sources/3DBenchy_Broschure_3DBenchy.com_.pdf` | other | authoritative | `158913e9c9c4953dd6185a3892b5e88e78020d2e26e2fc32eb052970a87919d4` | Creative Tools brochure. Features page states 15.55 cm³; Measure and calibrate restates the twelve caliper items. |
| `sources/image.png` | image | illustrative | `8e1e2797e343c851a5a67402a2fab0ebb83f8cd42f572c0ef7ebae300f9ff8ad` | Photograph of a white 1:1 FFF print, three-quarter starboard-bow view. EXIF orientation applied. Used to count openings; no pixel dimensions taken as contract values. |
| `sources/3DBenchy_page_measure_main_image.png` | drawing | illustrative | `434af3f5c2cb7dde33a0069645383a0391df5bb825b91ce06521f5b690abe589` | Small overview; no numerical labels used. |
| `sources/Dimension_3DBenchy_Length.png` | drawing | authoritative | `44c31ba74acec27bd044728eaf9992e319b4d76437b11195ef417606e02d405b` | Overall length 60.00 mm. |
| `sources/Dimension_3DBenchy_Width.png` | drawing | authoritative | `4924ad2d84ac77dbe2f3aea479f6329afe4861c50694877ec5c5ff3429044aa6` | Overall beam 31.00 mm; top view used to resolve cargo-box axes. |
| `sources/Dimension_3DBenchy_Height.png` | drawing | authoritative | `91d7483fd6dbbe40181f0fe30e5dae876ac3b660134fe5cc4036fca483b8a2f3` | Overall height 48.00 mm; cargo-box top 15.50 mm. |
| `sources/Dimension_3DBenchy_Bridge_Roof.png` | drawing | authoritative | `cba450ed197bd0cc479c70571c1ad4a467436690f5460356d516b6c40a1b540c` | Parallel roof faces 23.00 mm apart. |
| `sources/Dimension_3DBenchy_Chimney.png` | drawing | authoritative | `070b0a9542ecd5108d7d7da0e38ef562c6cf7c7fc4524e6c5f3bce856dd4507b` | Chimney Ø3.00 / Ø7.00 mm, blind depth 11.00 mm. |
| `sources/Dimension_3DBenchy_Box.png` | drawing | authoritative | `602aa159e8848d5a2960b524a890296317130f8fe6030bc56c36a09cc8b73888` | Cargo box outside 12.00 × 10.81 mm, inside 8.00 × 7.00 mm, depth 9.00 mm. |
| `sources/Dimension_3DBenchy_Hawsepipe.png` | drawing | authoritative | `c892cf56e2cec6f9ec4367532f56cce5d7db822601518d5c04346fc69315e16f` | Hawsepipe inner Ø4.00 mm, flange 0.30 mm. |
| `sources/Dimension_3DBenchy_Bridge_Window.png` | drawing | authoritative | `da57e562c3371d0b1015d522152f27700b53f7d08145dacfcfe6bd6cbc215dc6` | Front window 10.50 × 9.50 mm. |
| `sources/Dimension_3DBenchy_Bridge_Rear_Window.png` | drawing | authoritative | `e2bd8ebe0fa152c324266b06580d803530cea2b8f34f7b1f14b865866706724f` | Stern window Ø9.00 / Ø12.00 mm, flange 0.30 mm. |
| `sources/Dimension_3DBenchy_Hull_Angle.png` | drawing | authoritative | `ccd2e256d1345ff8d10fcd00d0c86bd6ea189bb1906a522df19d795ba45a2db9` | Bow overhang 40° to horizontal. |
| `sources/Dimension_3DBenchy_Bridge_Roof_Angle.png` | drawing | authoritative | `86fe2ff3839e0fe1073380d5a4fa0eb33d32ee12f6382696bc749bde5c23e0af` | Bridge roof 5.5° to horizontal. |
| `sources/Dimension_3DBenchy_Nameplate.png` | drawing | authoritative | `a476deae31a86a9f4f832e1fcc5c092b8f46fb3b8aab36c04e0e75b98b14b516` | Stern nameplate extrusion 0.10 mm. |

No `reference/` ingest. No triangle mesh or coordinate table was supplied, so nothing is classified as measured (reference model). Native CAD / the official STL were not ingested.

## 3. Requirement record

All tolerances below are digital comparison thresholds, not printer or caliper production tolerances.

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| Overall length, bow to stern | 60.00 | mm | Spec B.3; Length drawing; user prompt | ±0.01 | stated |
| Overall width, port to starboard | 31.00 | mm | Spec B.4; Width drawing; user prompt | ±0.01 | stated |
| Overall height, keel to chimney top | 48.00 | mm | Spec B.5; Height drawing; user prompt | ±0.01 | stated |
| Bridge roof front-to-rear | 23.00 | mm | Spec B.1; Roof drawing | ±0.01 | stated |
| Chimney inner / outer diameter, blind depth | 3.00 / 7.00 / 11.00 | mm | Spec B.2; Chimney drawing | ±0.01 | stated |
| Cargo-box top above keel | 15.50 | mm | Spec B.5; Height drawing | ±0.01 | stated |
| Cargo-box outside (beam × length) | 12.00 × 10.81 | mm | Spec B.6; Box drawing (12/8 along beam, 10.81/7 along length) | ±0.01 | stated |
| Cargo-box inside and depth | 8.00 × 7.00 × 9.00 | mm | Spec B.6; Box drawing | ±0.01 | stated |
| Hawsepipe inner diameter / flange | 4.00 / 0.30 | mm | Spec B.7; Hawsepipe drawing | ±0.01 | stated |
| Front window | 10.50 × 9.50 | mm | Spec B.8; Front-window drawing | ±0.01 | stated |
| Rear window inner / outer / flange | 9.00 / 12.00 / 0.30 | mm | Spec B.9; Rear-window drawing | ±0.01 | stated |
| Bow overhang to horizontal | 40 | deg | Spec B.10; Hull-angle drawing | ±0.01 | stated |
| Bridge roof slope to horizontal | 5.5 | deg | Spec B.11; Roof-angle drawing | ±0.01 | stated |
| Nameplate extrusion | 0.10 | mm | Spec B.12; Nameplate drawing | ±0.01 | stated; geometry optional until outline is known |
| Finished solid volume | 15550 | mm³ | Spec C; brochure Features (15.55 cm³) | ±10% | stated |
| Port–starboard symmetry | mirror about y = 0 | — | Spec C | qualitative; paired sections | stated |
| Planar tops | deck, box, chimney parallel to keel | — | Spec C | named faces at z = 0, 15.50, 48 | stated |
| Body count | one connected solid | count | reconstruction intent | exact 1 | stated |
| Print attitude | upright on keel, 1:1, without supports | — | Spec C | process note | stated |
| Hull outer mould line | not published | mm | Spec E | inferred keel/sheer endpoints only | open / inferred |
| Cabin outer envelope | not published | mm | Spec E | inferred rectangular shell | open / inferred |
| Side openings | visible, undimensioned | mm | photograph; Spec E | inferred width/height | open / inferred |
| Wheel, fishing-rod holder, letters | visible or described, undimensioned | — | Spec C, E; photograph | deferred cosmetics | open |
| Material, density, print shrinkage | unspecified | — | none | no mass claim | open |

## 4. Coordinate frame, scale, and measurement method

No official CAD origin is published. The reconstruction frame is:

- Origin at the intersection of the finished sternmost bounding plane x = 0, the symmetry plane y = 0, and the keel contact plane z = 0. That intersection need not lie on material.
- +x from stern toward bow; bow at x = overallLength = 60 mm.
- +y toward port when facing the bow; starboard negative; beam centred, extrema y = ±15.5 mm.
- +z from keel toward chimney top; chimney top at z = overallHeight = 48 mm. Right-handed.

Datums: `keel` (z = 0), `centreline` (y = 0), `sternStation` (x = 0), `cargoTop` (z = 15.50 mm), `chimneyTop` (z = 48 mm).

Scale is one model millimetre per official millimetre (1:1). Official two-decimal millimetre values are taken as stated, not re-measured from pixels. The photograph was not used as a scale bar. Cargo-box A/B mapping (12/8 mm along y, 10.81/7 mm along x) is taken from the Box drawing together with the Width top view.

Inferred hull, cabin, chimney and opening stations are build scaffolding so a later solid can be constructed; they are not caliper truth. Digital tolerances on inferred lengths are 0.5–4 mm. Probe points are placed only where clearance exceeds those inferred tolerances.

## 5. Measurement and inference record

Forty-eight parameters: 23 stated, 25 inferred, zero measured, zero measured (reference model), zero derived, zero defaulted. Derived acceptance quantities are separate from the parameter list.

### Stated parameters

| parameter | value | tolerance | provenance | source / evidence |
|---|---|---|---|---|
| `overallLength` | 60.00 mm | ±0.01 mm | stated | Spec B.3; Length drawing. Edit test +3 mm, expected volume +550 mm³ ±10%, bbox delta (3, 0, 0). First-order hull estimate, not an analytic derivative. |
| `overallWidth` | 31.00 mm | ±0.01 mm | stated | Spec B.4; Width drawing. |
| `overallHeight` | 48.00 mm | ±0.01 mm | stated | Spec B.5; Height drawing. Edit test +2 mm, expected volume +270 mm³ ±10%, bbox delta (0, 0, 2), from provisional cabin-wall area. |
| `bridgeRoofLength` | 23.00 mm | ±0.01 mm | stated | Spec B.1; Roof drawing. Parallel front/rear roof faces. |
| `chimneyInnerDiameter` | 3.00 mm | ±0.01 mm | stated | Spec B.2; Chimney drawing. |
| `chimneyOuterDiameter` | 7.00 mm | ±0.01 mm | stated | Spec B.2; Chimney drawing. Upper collar; stem diameter is inferred separately. |
| `chimneyHoleDepth` | 11.00 mm | ±0.01 mm | stated | Spec B.2; Chimney drawing. Floor at z = 48 − 11 = 37 mm. |
| `cargoBoxTopHeight` | 15.50 mm | ±0.01 mm | stated | Spec B.5; Height drawing. Rim height, not deck height. |
| `cargoBoxOuterA` | 12.00 mm | ±0.01 mm | stated | Spec B.6; Box drawing. Outside beam along y. |
| `cargoBoxOuterB` | 10.81 mm | ±0.01 mm | stated | Spec B.6; Box drawing. Outside length along x. |
| `cargoBoxInnerA` | 8.00 mm | ±0.01 mm | stated | Spec B.6; Box drawing. Inside beam along y. |
| `cargoBoxInnerB` | 7.00 mm | ±0.01 mm | stated | Spec B.6; Box drawing. Inside length along x. |
| `cargoBoxDepth` | 9.00 mm | ±0.01 mm | stated | Spec B.6; Box drawing. Floor z = 15.50 − 9.00 = 6.50 mm. Edit +1 mm: volume −56 mm³ ±2% = −innerA × innerB × 1; bbox unchanged. |
| `hawsepipeInnerDiameter` | 4.00 mm | ±0.01 mm | stated | Spec B.7; Hawsepipe drawing. |
| `hawsepipeFlangeDepth` | 0.30 mm | ±0.01 mm | stated | Spec B.7; Hawsepipe drawing. |
| `frontWindowWidth` | 10.50 mm | ±0.01 mm | stated | Spec B.8; Front-window drawing. Along y. |
| `frontWindowHeight` | 9.50 mm | ±0.01 mm | stated | Spec B.8; Front-window drawing. Along z. |
| `rearWindowInnerDiameter` | 9.00 mm | ±0.01 mm | stated | Spec B.9; Rear-window drawing. |
| `rearWindowOuterDiameter` | 12.00 mm | ±0.01 mm | stated | Spec B.9; Rear-window drawing. |
| `rearWindowFlangeDepth` | 0.30 mm | ±0.01 mm | stated | Spec B.9; Rear-window drawing. |
| `bowOverhangAngle` | 40 deg | ±0.01 deg | stated | Spec B.10; Hull-angle drawing. Lower-bow tangent only. |
| `bridgeRoofAngle` | 5.5 deg | ±0.01 deg | stated | Spec B.11; Roof-angle drawing. Rises toward bow. |
| `nameplateThickness` | 0.10 mm | ±0.01 mm | stated | Spec B.12; Nameplate drawing. Outline deferred. |

### Inferred parameters (build-critical; wide tolerances)

| parameter | value | tolerance | provenance | rationale |
|---|---|---|---|---|
| `hullKeelLength` | 40 mm | ±4 mm | inferred | Finite keel footprint inside the 60 mm envelope. |
| `hullKeelWidth` | 20 mm | ±3 mm | inferred | Bottom beam narrower than maximum beam, for flare. |
| `hullKeelCenterX` | 25 mm | ±3 mm | inferred | Aft-biased keel station, room for the spoon bow. Nominal keel x ≈ 5–45 mm. |
| `hullSternWidth` | 22 mm | ±3 mm | inferred | Transom beam to close the loft. |
| `deckHeight` | 10 mm | ±1 mm | inferred | Horizontal deck below the 15.50 mm box rim and above the 6.50 mm pocket floor. |
| `sternGunwaleHeight` | 11.5 mm | ±1 mm | inferred | Low aft sheer above deck. |
| `bowGunwaleHeight` | 24 mm | ±2 mm | inferred | Raised bow below the roof; preserves the stated 40° lower tangent. |
| `hullWallThickness` | 1.6 mm | ±0.5 mm | inferred | Bulwark thickness around the open deck. |
| `cabinCenterX` | 31 mm | ±1.5 mm | inferred | Cabin station leaving an aft box and a forward well. |
| `cabinLength` | 20 mm | ±2 mm | inferred | Less than 23 mm roof length so the roof can overhang; rear/front ≈ x = 21 / 41 mm. |
| `cabinWidth` | 18 mm | ±2 mm | inferred | Must clear the 12 mm rear-window flange; sides y = ±9 mm. |
| `cabinWallThickness` | 2 mm | ±0.5 mm | inferred | Finite through-depths for openings; interior ≈ 16 × 14 mm. |
| `bridgeRoofWidth` | 20 mm | ±2 mm | inferred | Roof beam with a small side overhang. No slats from print layers. |
| `bridgeRoofThickness` | 2.5 mm | ±0.5 mm | inferred | Closed roof thick enough to keep the 11 mm chimney bore blind. |
| `chimneyCenterX` | 25 mm | ±1 mm | inferred | Vertical axis on the aft roof, y = 0. |
| `chimneyHeightAboveRoof` | 10 mm | ±1.5 mm | inferred | Roof at the chimney axis at z = 48 − 10 = 38 mm; slope from `bridgeRoofAngle`. |
| `chimneyStemDiameter` | 5.5 mm | ±0.5 mm | inferred | Narrower stem under the Ø7 collar, as in the chimney illustration. |
| `chimneyCollarHeight` | 2 mm | ±0.5 mm | inferred | Collar occupies approximately z = 46–48 mm. |
| `cargoBoxCenterX` | 15 mm | ±1 mm | inferred | Aft of the cabin; outer x ≈ 9.595–20.405 mm. |
| `hawsepipeCenterX` | 52 mm | ±1 mm | inferred | Forward transverse bore. |
| `hawsepipeCenterZ` | 18 mm | ±1 mm | inferred | Above deck, below the raised bow rim; axis parallel to y. |
| `hawsepipeOuterDiameter` | 6 mm | ±1 mm | inferred | Annular flange OD; only bore and 0.30 mm projection are stated. |
| `windowCenterHeight` | 27 mm | ±1 mm | inferred | Shared z for front and rear window centres. |
| `sideOpeningWidth` | 9 mm | ±1 mm | inferred | Longitudinal clear span of each side opening. |
| `sideOpeningHeight` | 22 mm | ±2 mm | inferred | Deck to arched crown; nominal crown z ≈ 32 mm. |

### Acceptance quantities

| acceptance value | nominal | digital criterion | provenance | formula / evidence |
|---|---|---|---|---|
| Envelope min / max | (0, −15.5, 0) → (60, 15.5, 48) mm | ±0.05 mm | derived from stated envelope and frame | Length along +x from stern; beam ±width/2; height 0 to 48. |
| bbox_tolerance | 0.05 mm | absolute | defaulted | Seed envelope comparison allowance. |
| Volume | 15550 mm³ | ±10% → 13995–17105 mm³ | stated | 15.55 cm³ × 1000. Wide band because the hull is not fully specified. |
| Surface area | omitted | — | unresolved | No closed-form hull. |
| Centre of mass | omitted | — | unresolved | No closed-form hull. |
| Solid count | 1 | exact | stated | One connected boat. |
| chimneyCollar | z = 47 mm; area 10π ≈ 31.416 mm²; 1 loop, 1 hole | area ±2% | derived annulus | π/4 × (7² − 3²). Only the chimney is solid at this height. |
| chimneyAxial | x = 25 mm | ≥1 island | inferred station | Inspect blind floor z = 37 mm. |
| cargoCavity | z = 9 mm; 1 loop, 1 hole | topology | inferred plane | Between pocket floor 6.50 and deck 10. Pocket area 56 mm² is not the whole section. |
| hawsepipeStation | x = 52 mm | ≥1 island | inferred station | Both hull mouths. |
| frontWindow | x = 40 mm; 1 hole | topology | derived wall mid | Clear area 10.50 × 9.50 = 99.75 mm² is the aperture, not solid area. |
| rearWindow | x = 22 mm; 1 hole | topology | derived wall mid | Aperture π × 9² / 4 ≈ 63.617 mm². |
| portSide / starboardSide | y = ±8 mm | ≥1 island each | inferred | Mirrored side openings. |
| centreline | y = 0 | ≥1 island | frame | Longitudinal profile. |
| keelBottom | z = 0, normal −z | ±0.01 mm | frame | Named print datum. |
| cargoBoxTop | z = 15.5, normal +z | ±0.01 mm | stated | Spec C planarity. |
| chimneyTop | z = 48, normal +z | ±0.01 mm | stated | Spec C planarity. |
| Deviation | omitted | — | not applicable | No reference mesh. |
| Blockout band | 20000–31000 mm³ | inclusive | inferred | Envelope-only (no holes). Known cavities cargo 504 + chimney ≈ 77.75 ≈ 582 mm³, plus estimated 6000–12000 mm³ cabin/well/openings, added to the finished-volume bounds and rounded out. The 89280 mm³ bounding prism is not the blockout solid. |
| Export volume agreement | 0.002 relative | KCL/STEP/STL | defaulted | Schema default; not accuracy against the official boat. |

Edit tests change one independent stated parameter, holding the others fixed. Length and height volume deltas are estimates with 10% relative tolerance; the cargo-box depth delta is analytic. Restore the nominal model after each edit.

## 6. Defaults retained

No template geometry remains. No parameter uses a defaulted nominal value.

| setting | value | reason |
|---|---|---|
| Schema and release status | schema_version 1; reconstruction | Source-defined reconstruction, not a production release. |
| Units | mm, deg | Official millimetres and stated angles. |
| Stated-parameter digital tolerance | 0.01 mm or 0.01 deg | Exact two-decimal official numbers; not print tolerance. |
| Envelope / bbox | ±0.05 mm | Seed absolute allowance. |
| Finished volume relative tolerance | 0.10 | Hull OML is unpublished. |
| Chimney-annulus area relative tolerance | 0.02 | Analytic circle pair. |
| Export volume agreement | 0.002 | Schema default for format agreement. |
| Material, density | null | Unspecified; no mass claim. |
| Process | FFF calibration print at 1:1, without supports | Official print intent; not a manufacturing tolerance. |
| Deviation | null | No reference mesh. |
| Surface area and centre of mass | omitted | Cannot be derived from stated numbers. |
| Nameplate, wheel, rod holder, bottom letters | deferred | Undimensioned cosmetics; `nameplateThickness` retained as a constant. |
| Interfaces | printDatum, bilateralSymmetry, caliperSet | Print attitude, y = 0 mirror, independent caliper constants. |

## 7. Unrepresentable or low-confidence features

The official sources do not uniquely define the spoon hull. Provisional keel, sheer and transom endpoints plus the 40° bow tangent do not fix NURBS. The later model must produce a smooth symmetric hull that hits the 60 × 31 × 48 mm envelope and the stated bow angle; it will not be a bitwise match to the official STL.

Cabin taper, roof slats (print layers, not CAD), gunwale bead, hawsepipe flange as a thin annulus, chimney fillets, cargo-box corner radii, the boat’s wheel, fishing-rod holder, stern nameplate letterforms, and bottom first-layer letters are either inferred with wide bands or deferred. Thin flanges and the roof slab do not have solid probes with enough clearance; those features rely on sections and named faces.

Probes and sections check selected topology (chimney bore, cargo pocket, windows, side openings, symmetry plane). Caliper spans, diameters, angles, flange projections and full mirrored surface identity still need STEP review after modelling.

Open questions, identical to the contract:

- Exact hull outer mould line, keel outline, transom rake, waterlines, sheer and NURBS/control points are unavailable. Provisional endpoints do not uniquely define the spoon hull or locate its 40 degree tangent.
- Deck height, gunwale section/radii and inner bow-well shape are unstated. Adopted heights/thickness are assumptions; no thin-gunwale solid probe has sufficient uncertainty clearance.
- Cabin outer envelope, taper, walls/interior and roof beam/thickness/overhangs are unspecified. Rectangular shell is provisional; roof solid probes lack clearance from uncertain slab placement.
- Side-opening sizes, exact arch, trim and positions are unstated. Two mirrored openings use inferred dimensions; the photograph provides no calibrated measurements.
- Front/rear window elevations, wall through-depths and front trim are unstated. Official clear sizes are retained; common height and wall stations are provisional.
- Chimney height above roof, station, stem diameter, collar height and fillets are unstated. The 11 mm bore must remain blind at z=37; section review is required because no robust floor/rim solid probe follows from stated dimensions.
- Hawsepipe station/elevation/direction, flange OD and projection convention against curved hull are unstated. A transverse mirrored pair is assumed; thin flanges lack safe solid-probe clearance.
- Cargo-box station and corner radii are unspecified. A centred rectangular pocket is adopted; clear dimensions and floor z=6.50 are constrained, rounded exterior unresolved.
- Stern nameplate outline, font, letterforms, placement and exact letter height (only less than 2 mm stated) are unresolved. Cosmetic geometry deferred; retain 0.10 mm extrusion if later specified, inside the finished envelope.
- Boat-wheel geometry, size and position are unspecified; cosmetic feature deferred.
- Fishing-rod-holder diameter, blind depth, slant and position, plus identities/counts of photographed deck fittings, are unresolved; cosmetic features deferred.
- Bottom lettering content, font, outlines and depth are unspecified; cosmetic first-layer details deferred. Print layer lines/apparent roof slats are not CAD geometry.
- Material, density and physical print tolerances are unknown; no mass, shrinkage compensation or guaranteed control-print match is claimed.
- Confirm whether 15.55 cm3 includes every cavity, wheel, holder, flange and letter as modelled. The 10% finished-volume and 20000..31000 mm3 filled-blockout bands allow reconstruction uncertainty, not shape identity.
- No reference mesh/coordinate table was ingested; surface area, centre of mass and deviation cannot be assigned. Official STL triangulation deviation 0.001 mm is not a reconstruction tolerance.
- Probes/sections establish selected topology only. Caliper spans/diameters, angles, flange projections and full mirrored surface symmetry require STEP review. Thin annular features lack safe solid probes. Add centres if later specifying repeated coplanar datum faces.
- The length edit's approximately +550 mm3 is a first-order hull estimate with 10% tolerance, not an analytic derivative. The height estimate depends on the provisional cabin; both await native-model verification.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [-0.0, -15.5, -0.0] → [60.0, 15.5, 48.0] | 27989.76278067471 | pass | 2026-09-16T15:36:29Z: within envelope and band |
