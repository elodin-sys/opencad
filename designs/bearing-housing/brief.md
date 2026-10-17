# bearing-housing — design brief

## 1. Intent and configuration

Cast oval flanged bearing housing (housing only, no bearing or screws), one connected solid in mm. Flange = convex hull of a Ø57 circle at the origin and two Ø22 lobes at (±38.25, 0), 11 thick; Ø57 boss to z = 26; every side face drafted inward 4° about the neutral plane z = 0; every edge of the drafted body rounded r = 1 before any hole is cut; Ø47 × 14 counterbore from the boss top over a Ø14 through bore; two Ø10 through mounting holes at (±38.25, 0). `sources/bearing-housing-spec.md` is authoritative (parameters, construction order, reference measurements); the three renders are illustrative. Fast regression case: outline parameters stay fixed, only the two hole diameters are edited.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/bearing-housing-spec.md | text | authoritative | d286e12f68d0 | parameter table, construction steps 1-6, reference measurements, edit tests, robustness note |
| sources/bearing-housing-iso.png | image | illustrative | 993e43deea9e | isometric: oval flange with two lobes, drafted boss, counterbore floor with bore, two mounting holes, rounded outer edges |
| sources/bearing-housing-top.png | image | illustrative | c47574c5ab70 | top view (+x right, +y up): tangent-hull outline, holes on the x axis, symmetric about x = 0 and y = 0 |
| sources/bearing-housing-section.png | image | illustrative | fe4ce0ff2989 | section y = 0 with mm axes: four loops, lobe ends x ≈ ±43..±49, boss halves x ≈ ±7..±33, walls to z = 26, floor z = 12, flange top z = 11 |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| one connected solid | 1 | | spec | exact | stated |
| overall height A | 26 | mm | spec Parameters | 0.01 | stated |
| flange thickness A1 | 11 | mm | spec Parameters | 0.01 | stated |
| boss / centre circle Db2 at z = 0 | 57 | mm | spec Parameters | 0.01 | stated |
| flange length H at z = 0 | 98.5 | mm | spec Parameters | 0.01 | stated |
| hole spacing J | 76.5 | mm | spec Parameters | 0.01 | stated |
| draft on every side face | 4 | deg | spec Parameters, step 3 | 0.01 | stated |
| edge round, before holes | 1 | mm | spec Parameters, step 4 | 0.01 | stated |
| counterbore Ø × depth | 47 × 14 | mm | spec Parameters | 0.01 | stated |
| through bore Ø (z 0..12) | 14 | mm | spec Parameters | 0.01 | stated |
| mounting holes Ø (z 0..11) at (±38.25, 0) | 10 | mm | spec Parameters | 0.01 | stated |
| symmetry about x = 0 and y = 0 | | | spec Frame and datums | 0.1 max / 0.05 p95 | stated |
| edit tests: mountingHoleDiameter +1, boreDiameter +1 only | | | spec Editability | 2 % | stated |

## 4. Coordinate frame, scale, and measurement method

Origin at the centre of the flat flange bottom (datum A, z = 0) on the bore axis (datum B, the z axis); +x along the mounting-hole line, +y across the flange, +z up out of the bore. Mirror planes x = 0 and y = 0 (datum C). No image measurement was needed: every dimension and acceptance value is stated in the spec. The section render's mm axes were read only to confirm consistency (lobe loops ≈ x 43..49, boss loops ≈ x 7..33, wall top z = 26, floor z = 12, flange top z = 11, drafted outer faces leaning inward).

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| overallHeight | 26 | 0.01 | stated | spec A |
| flangeThickness | 11 | 0.01 | stated | spec A1 |
| bossDiameter | 57 | 0.01 | stated | spec Db2 |
| flangeLength | 98.5 | 0.01 | stated | spec H |
| holeSpacing | 76.5 | 0.01 | stated | spec J |
| lobeDiameter | 22 | 0.01 | derived | flangeLength − holeSpacing |
| draftAngle | 4 deg | 0.01 | stated | spec |
| edgeRadius | 1 | 0.01 | stated | spec |
| counterboreDiameter | 47 | 0.01 | stated | spec |
| counterboreDepth | 14 | 0.01 | stated | spec (floor at z = 12) |
| boreDiameter | 14 | 0.01 | stated | spec; edit +1 → ΔV = −π(7.5² − 7²)·12 = −273.32 mm³, bbox unchanged |
| mountingHoleDiameter | 10 | 0.01 | stated | spec; edit +1 → ΔV = −π(5.5² − 5²)·11·2 = −362.85 mm³, bbox unchanged |
| envelope | ±49.1775 × ±28.4275 × 0..26 | 0.05 | measured (reference model) | spec 98.355 × 56.855 × 26 (bottom r = 1 round pulls extremes in from 98.5 × 57) |
| volume | 46881.3 mm³ | 0.5 % | measured (reference model) | spec; cross-check: drafted hull + boss (no rounds) 74850 − counterbore 24290 − bore 1847 − holes 1728 = 46986, rounds remove ~105 |
| section z = 5.5 | 3321.8 mm², 1 loop, 3 holes | 1 % | measured (reference model) | spec |
| section z = 15 | 632.4 mm², 1 loop, 1 hole | 1 % | measured (reference model) | spec |
| section z = 24 | 525.1 mm², 1 loop, 1 hole | 1 % | measured (reference model) | spec |
| section y = 0 | 844.4 mm², 4 loops | 1 % | measured (reference model) | spec; confirmed by the section render |
| bottom_face z = 0 (−z) | 3161.0 mm² | 2 % | measured (reference model) | spec; cross-check: hull at z = 0 3724 − bore − holes = 3413 minus the r = 1 round ring |
| counterbore_floor z = 12 (+z) | 1581.0 mm² | 0.1 %, plane ±0.01 | measured (reference model) | spec; analytic π(23.5² − 7²) = 1581.00 (both edges sharp, cut after the rounds), so no round allowance |
| flange_top_left/right z = 11 (+z) | 369.2 mm² each, centroid x = ∓34.38 | 2 % | measured (reference model) | spec |
| boss_top z = 26 (+z) | 348.0 mm² | 2 % | measured (reference model) | spec |
| draft flats (4) | 311.4 mm², normals (±0.4564, ±0.8870, 0.0698), centroids (±27.79, ±17.31, 5.64) | 3 %, 0.5° | measured (reference model) | spec; check: sin α = (28.5 − 11)/38.25, normal = (sin α cos 4°, cos α cos 4°, sin 4°) = (0.4564, 0.8870, 0.0698) |
| cylinders | counterbore Ø47 z 12..26; bore Ø14 z 0..12; holes Ø10 z 0..11 at x = ±38.25 | r 0.02, length 0.05 | stated | spec |
| blockout band | 72000 .. 80000 mm³ | | derived | drafted hull + boss without holes ≈ 74850; undrafted hull + boss shrunk to the bbox ≈ 78860 |

Probe points (all ≥ 1.8 mm from every declared surface): solid (±46, 0, 5.5) lobe outboard of holes; (0, ±25.3, 20) boss wall between r 23.5 and r ≈ 27.1; (15, 0, 6), (0, −15, 6) under the counterbore floor. Void (0, 0, 19), (15, 0, 19) counterbore; (0, 0, 6) bore; (±38.25, 0, 5.5) mounting holes; (±36, 0, 13) air above the flange tops beside the boss.

## 6. Defaults retained

- Symmetry bands max 0.1 mm / p95 0.05 mm (opencad defaults; the spec states the mirror planes but no band).
- Area tolerances 1 % (sections), 2 % (faces), 3 % (drafted flats); volume 0.5 %; envelope 0.05 mm; cylinder radius 0.02 mm, length 0.05 mm. The spec values are measurements of the exact reference, so these only absorb tessellation and round-edge bookkeeping.
- Material and density unknown (null); no mass claim.

## 7. Unrepresentable or low-confidence features

- The r = 1 rounds are encoded only through the bbox, face areas and volume; there is no fillet-radius acceptance item.
- Surface area and centre of mass are not declared (not in the spec; centre of mass is x = y = 0 by symmetry, z not computed).
- No edit tests or sweeps on the outline (overallHeight, flangeThickness, bossDiameter, flangeLength, holeSpacing, draftAngle, edgeRadius): the spec reports the drafted, rounded tangent hull fails to rebuild in OpenCascade for most other values.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
