# axjet-c2-case_r1 — design brief

## 1. Intent and configuration

Compressor casing ring `case_r1` over rotor 1 of the AXJET-220 two-stage transonic compressor module (assembly `axjet-c2`, guide section 14.1), and the datum part of that module. It is a turned 6061-T6 ring, z −18 … 18 in the assembly frame. The bore is Ø180.5 over the full length; it is the rotor_1 tip shroud, so the tips at r 90.0 run at the 0.25 mm cold clearance. The ring OD is 200 between two flanges, each OD 224 (revision 1). The front flange (z −18 … −12) and the rear flange (z 12 … 18) each carry 8 × Ø5.5 (M5 clearance) holes on PCD 212 through the flange, one hole on +x, 45° pitch. The 0.5 mm sprayed Al-Si/polyester abradable that lines a recess over z −2 … 18 is modelled as part of this body and finished at Ø180.5 with the plain bore.

Mating parts:
- The front face (z −18) seats on the inlet_frame rear flange (joint `inletFrameOnCase`).
- The rear face (z 18) seats on the stator_1 front flange (joint `stator1OnCase`).
- The drum shaft spins about the bore axis (joint `rotorSpin`), and the derived air body is fixed to this part (joint `airFixed`), both at the origin.

The part is a single solid. Authoritative source: `sources/axjet_design_and_implementation_guide.md`, sections 4.4, 11 and 14.1. The two eddy-current probes over the rotor_1 tips are not modelled.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | AXJET-220/2 guide, mm. case-r1 row in section 14.1; casing paragraph in section 4.4; bore Ø180.5 H7 and the in-situ machined abradable in section 11; cold tip clearance 0.25 in sections 2.3, 4.1 and 8.2; inlet_frame rear flange z −24 … −18 (the basis for the flange thickness) in sections 9 and 14.1; eddy-current probes in section 10; compressor ring OD 200 / flanges 212 in section 3.2 |

No images, drawings, meshes or reference ingest outputs were supplied.

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| ring axial extent | z −18 … 18 | mm | 14.1, 4.4, intent | 0.05 | stated |
| bore over the full length (finished, lining included) | Ø180.5 (r 90.25) | mm | 4.4, 11, 14.1 | 0.01 on radius | stated |
| ring OD between the flanges | 200 | mm | 3.2, 4.4, 14.1 | 0.02 on radius | stated |
| flange OD (front and rear) | 224 | mm | revision 1 change 2 (guide 3.2, 4.4, 14.1: 212) | 0.02 on radius | stated (revision) |
| flange axial extents | z −18 … −12, 12 … 18 (6 thick) | mm | intent (inferred from the inlet_frame rear flange) | 0.5 | inferred |
| bolt holes per flange | 8 × Ø5.5 (M5 clearance) on PCD 212, through | – | revision 1 change 2 (guide 14.1: 8 × Ø6.4 on PCD 206) | 0.02 on radius, 0.05 axis | stated (revision) |
| bolt clocking | one hole on +x, 45° pitch, both flanges | deg | 14.1, intent | 0.05 mm axis | stated |
| abradable lining | 0.5 thick over z −2 … 18, merged into the body, finished at Ø180.5 | mm | 4.4, 14.1, intent | via bore cylinder | stated (not a separate surface) |
| rotor_1 cold tip clearance | 0.25 (tips r 90.0) | mm | 2.3, 4.1, 8.2 | min 0.20, max 0.30 | stated |
| front mating face | z −18, seats on the inlet_frame rear flange | mm | 9, 14.1 | 0.05 | stated |
| rear mating face | z 18, seats on the stator_1 front flange | mm | 14.1 | 0.05 | stated |
| material / density | 6061-T6, 2700 kg/m³ | – | 11, 14.1 | – | stated |
| eddy-current speed and clearance probes (2) | not modelled | – | 10, intent | – | open |

## 4. Coordinate frame, scale, and measurement method

The frame is the assembly frame, because the assembly places the part by these joint frames.

Origin and axes:
- The origin is on the engine axis (the bore axis) at the rotor_1 leading-edge plane, midway between the flange faces.
- +z points along the axis with the flow (inlet_frame side z < 0, stator_1 side z > 0).
- +x points up, through the centre of the first bolt hole of each flange.
- +y completes the right-handed set (y = z × x): looking downstream with +x up, +y points to the right.

Datums:
- A: front face, z = −18.
- B: the bore axis, which is the z axis.
- C: rear face, z = 18.
- D: the +x hole, which sets the clocking.

Joint frames, all with axis +z:
- `inletFrameOnCase` at [0, 0, −18].
- `stator1OnCase` at [0, 0, 18].
- `rotorSpin` and `airFixed` at [0, 0, 0].

No image or mesh measurement was used. Every dimension is read as text from the guide, and the acceptance values are derived analytically from them:
- Each Ø5.5 hole (r 103.25 … 108.75) lies wholly inside the r 100 … 112 flange land, so the hole areas are full circles π·2.75² = 23.758 mm².
- The bounding box in x and y is ±112 (the un-notched OD 224 rims).

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| frontFaceZ | −18 mm | 0.01 | stated | 14.1 / 4.4: case-r1 z −18 … 18 |
| rearFaceZ | 18 mm | 0.01 | stated | 14.1 / 4.4 |
| boreDiameter | 180.5 mm | 0.01 | stated | 4.4, 11 (Ø180.5 H7), 14.1 |
| ringOuterDiameter | 200 mm | 0.01 | stated | 3.2, 4.4, 14.1 |
| flangeOuterDiameter | 224 mm | 0.01 | stated | revision 1 change 2 (was 212, guide 3.2, 4.4, 14.1) |
| flangeThickness | 6 mm | 0.5 | inferred | the guide gives none for case-r1; intent: 6 to match the inlet_frame rear flange z −24 … −18 |
| boltCircleDiameter | 212 mm | 0.01 | stated | revision 1 change 2 (was 206) |
| boltHoleDiameter | 5.5 mm | 0.01 | stated | revision 1 change 2: M5 clearance (was 6.4) |
| boltHoleCount | 8 | 0.1 | stated | 4.4, 14.1 |
| boltStartAngle | 0° | 0.01 | stated | 14.1: one hole on +x |
| boltPitchAngle | 45° | 0.01 | derived | 360 / boltHoleCount (intent states 45°) |
| hole area | 23.758 mm² | – | derived | π·2.75², wholly inside the flange land |
| volume | 303414.2 mm³ | rel 0.002 | derived | π(100² − 90.25²)·36 + 2π(112² − 100²)·6 − 16·6·23.758 = 209787.3 + 95906.9 − 2280.8 |
| mass | 0.819 kg | – | derived | volume × 2700 kg/m³ |
| surface area | 88460.6 mm² | rel 0.005 | derived | bore 20414.07 + ring OD 15079.64 + flange ODs 8444.60 + faces 2·13629.60 + flange backs 2·7802.15 + 16 hole walls 2π·2.75·6 = 1658.76 |
| centre of mass | (0, 0, 0) | 0.05 | derived | axisymmetric, 8-fold holes, flanges symmetric about z = 0 |
| sections mid_ring (z −6), lining_zone (z 8) | 5827.46 mm², loops 1, holes 1 | rel 0.005 | derived | π(100² − 90.25²); an open recess r 90.75 would lose π(90.75² − 90.25²) = 284.3 |
| sections front/rear_flange_mid (z ∓15) | 13629.60 mm², loops 1, holes 9 | rel 0.005 | derived | π(112² − 90.25²) − 8·23.758; the bore plus 8 enclosed bolt holes |
| faces frontFlangeBack / rearFlangeBack | 7802.15 mm² | rel 0.005 | derived | π(112² − 100²) − 8·23.758 |
| frontFace / rearFace | z ∓18, no area pinned | 0.05 | stated | area 13629.60 is carried by the flange sections; it is left off the pinned faces because the flangeOuterDiameter edit changes it |
| bbox | ±112 × ±112 × ±18 | 0.05 | derived | flange OD 224 |
| rotor1TipClearance | 0.25 nominal | min 0.20, max 0.30 | derived | 90.25 − 90.0; 0.20 is the assembly rotor1Tip min_gap |
| ringWall thickness | 9.75 | min 9.5 (p05) | derived | 100 − 90.25, sampled over z −11 … 11 only |
| blockout band | 297300 … 313300 mm³ | – | derived | turned profile without holes 305694.2, finished part 303414.2; the earlier band shifted by the flange growth 2π(112² − 106²)·6 = 49310 |
| edit ringOuterDiameter +2 | ΔV +15155.04, bbox Δ (0, 0, 0) | rel 0.02 | derived | π(101² − 100²)·24; holes stay in the flanges. Feasible interval 180.5 < OD < 206.5 (holes start at r 103.25); sweep 196 / 200 / 204; infeasible −20 (OD 180 ≤ bore) must assert |
| edit flangeOuterDiameter +4 | ΔV +17040.0, bbox Δ (4, 4, 0) | rel 0.02 | derived | 12·π(114² − 112²); bbox from 224 to 228. Feasible OD > 212 + 5.5 for enclosed holes (> 200 for a flange at all); sweep 224 / 228 / 232; infeasible −26 (OD 198 < ring OD) must assert |

## 6. Defaults retained

- Envelope tolerance 0.05 mm (template default), suitable for a turned ring with stated nominal dimensions.
- `release_status: reconstruction` (template default); the guide is a design definition and no hardware has been measured.
- Parameter tolerances of 0.01 mm / 0.01° on stated values. The inferred flange thickness gets 0.5 mm, and the dependent flange-back face positions, flange thickness dimensions, flange OD lengths and hole lengths use the same 0.5 mm band.
- No fillets, chamfers or edge breaks, since none are stated.

## 7. Unrepresentable or low-confidence features

- **Changed (revision 1, reviewer notes): flanges OD 224 with 8 × Ø5.5 on PCD 212.** The guide's Ø6.4 holes on PCD 206 broke 0.2 mm out of the OD 212 rims and left no seat for an M6 head or nut. An M5 head or nut at r 106 now clears the ring wall and the rim by about 1.5 mm; the inlet_frame rear flange and the stator_1 front flange carry the same pattern.
- **Abradable lining.** The lining is merged into the body: the metal recess (r 90.75 over z −2 … 18) and the bond line are not modelled. The mass uses the 6061 density for the 0.5 mm lining as well.
- **Eddy-current probes.** The two speed and tip-clearance probes over the rotor_1 tips (section 10) are not modelled; their bosses and positions are not stated.
- **Centring.** No spigot or dowel is defined between the rings. Section 11 asks the bore to be concentric to the bearing bores within 0.03 TIR, which implies one.
- **Hole depth.** Each hole goes through its own flange only. One-pass drilling through both flanges would clear the ring OD by 3.25 mm, but the source does not state it.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
