# axjet-c2-rotor_2 — design brief

## 1. Intent and configuration

Rotor-2 blisk of the AXJET-220 compressor module (assembly `axjet-c2`, body `rotor_2`), drawn in its own frame so the assembly can attach it by the rigid joint `rotor2OnDrum` at the own-frame origin with axis +z. 31 blades on a revolved disc: hub flow surface r 64.8 → 66.5 over z 0 … 13, flat tips at r 90.0, D40.0 bore on the drum, front face against the seal spacer, rear seal sleeve OD 126 × ID 60 running inside the OGV inner-band labyrinth, rear face bearing on the drum D46 shoulder at assembly z 62 (revision 1; the stack nut now clamps the stack from the front). 2618-T61 (2760 kg/m³), about 1.0 kg. The authoritative source is `sources/axjet_design_and_implementation_guide.md` (sections 2.3, 3.2, 4.1–4.4, 8.1, 14.1); the orchestrator's intent resolves the own frame and the stator_1 / OGV interfaces.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | 3.2 flow-path radii (R2 LE r 64.8 at z 42, TE r 66.5 at z 55); 4.1/4.2 blade count, chords, section radii; 4.3 R2 metal angles, t/c, LE radius, TE thickness; 4.4 blisk geometry; 8.1 rotor stack; 14.1 body table (own frame, sleeve OD 126 × ID 60) |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| blade count | 31 | – | guide 4.1, 4.4 | exact | stated |
| hub flow surface | r 64.8 at z 0 → r 66.5 at z 13, straight | mm | guide 3.2, 4.4 | 0.01 | stated |
| front hub extension | r 64.8, z −1 … 0 | mm | intent | 0.1 | inferred |
| tip | flat at r 90.0 | mm | guide 4, 4.4 | 0.01 | stated |
| minimum tip thickness | 0.8 | mm | guide 2.3, 4.4 | 0.01 | stated (governs the tip section) |
| root fillet | r 1.5 on the hub | mm | guide 2.3, 4.4 | 0.01 | stated |
| sections | r 64.8 / 77.4 / 90.0; inlet 66.7 / 70.1 / 73.1°; exit 40.4 / 56.5 / 64.6°; camber 26.3 / 13.6 / 8.5°; chord 22 / 20 / 18; t/c 8 / 5 / 3.5 % | mm, deg | guide 4.2, 4.3 | 0.01 mm / 0.05° | stated |
| section shape | circular-arc camber, NACA-65 thickness, LE r 0.3, TE 0.5 | mm | guide 4.3, 14 | 0.01 | stated |
| stacking | radial on section centroids, no lean or sweep | – | guide 4.4 | – | stated |
| disc extent | z −4 … 20 | mm | guide 4.4, 8.1 | 0.01 | stated |
| bore | D40.0 (H6 on h6 drum, line-to-line) | mm | guide 4.4, 8.1; intent | 0.02 | stated |
| front face | z −4 over r 20 … 57.5 (seal spacer) | mm | intent; guide 8.1 | 0.05 | stated |
| front keep-out | nothing outside r 57.5 ahead of z −1 | mm | intent | 0.4 gap | stated |
| rear sleeve | OD 126 × ID 60, z 20 … 28; r 63.0 from z 13 | mm | guide 4.4, 14.1 | 0.02 | stated |
| OGV labyrinth gap | 0.5 to r 63.5 | mm | guide 4.4 | 0.4 floor | stated |
| rear clamp face | z 20 (assembly 62) on the drum D46 shoulder over r 20 … 23 (revision 1; the stack nut moved to the front of the stack) | mm | intent; guide 8.1; revision 1 change 1 | 0.05 | stated |
| tip clearance | 0.25 to bore r 90.25 | mm | guide 2.3, 4.4 | 0.15 floor | stated |
| mass | about 1.0 | kg | guide 4.4, 12 | volume ±2 % | stated |

## 4. Coordinate frame, scale, and measurement method

Origin on the rotor axis in the blade leading-edge plane at the hub (assembly z 42); +z along the axis in the flow direction (the spool turns positively about +z); +x parallel to the assembly x; +y = z × x. Every own-frame z is the assembly z minus 42. Datum A is the bore axis, datum B the front face z −4, datum C the clocking of blade 0 (stacking line on +x, then every 360/31° counter-clockwise about +z). No images or meshes: every number is read from the guide's tables or the intent, in millimetres and degrees from axial.

Blade construction: each section is built in its own (axial, tangential) plane at r 64.8 / 77.4 / 90.0. The camber line is a circular arc from the inlet to the exit metal angle (stagger = mean of the two); thickness is the NACA-65 distribution scaled to the section maximum, with LE radius 0.3 and a 0.5 mm TE. Rotation is +z, so the relative flow runs from +θ toward −θ: the LE is on the +θ side and the TE on the −θ side, and the camber bulges toward −z / −θ (the suction side faces against rotation). Hand (revision 3): the LE leads in the direction of rotation (+θ) and the concave pressure surface faces +θ (the chord runs toward −θ from LE to TE), the same hand as rotor_1. The `blades` feature checks it with solid probes at [77.34, 3.039, 3.0] and [77.373, 2.026, 3.5] and void probes at their −y mirror images. All three section centroids lie on the radial stacking line. The hub section is placed so its axial extent is z 0 … 13; 22 × cos 53.55° = 13.07, consistent within the LE/TE rounding. The stacking line therefore sits near z 5.5. The tip is trimmed on the r 90.0 cylinder, and blade roots sunk below the hub surface must not protrude through the step faces at z −1 and z 13.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| bladeCount | 31 | 0.1 | stated | guide 4.1, 4.4 |
| firstBladeAngle | 0° | 0.1 | inferred | no clocking in the guide; blade 0 on +x for reproducibility |
| hubRadiusLe | 64.8 | 0.01 | stated | guide 3.2 / 4.4 |
| hubRadiusTe | 66.5 | 0.01 | stated | guide 3.2 / 4.4 |
| hubTeZ | 13 | 0.01 | stated | guide 3.2 (55 − 42); intent |
| hubExtFrontZ | −1 | 0.1 | inferred | intent: 3 mm behind the stator_1 inner band end (assembly 38), as R1 sits 3 mm behind its fairing |
| tipRadius | 90.0 | 0.01 | stated | guide 4, 4.4 |
| discFrontZ / discRearZ | −4 / 20 | 0.01 | stated | guide 4.4, 8.1 (assembly 38 … 62) |
| boreDiameter | 40.0 | 0.01 | stated | guide 4.4, 8.1 |
| frontLandRadius | 57.5 | 0.01 | stated | intent; seal spacer OD 115 (guide 8.1) |
| sleeveOuterRadius / sleeveInnerRadius | 63.0 / 30.0 | 0.01 | stated | guide 4.4 / 14.1 (OD 126 × ID 60) |
| sleeveRearZ | 28 | 0.01 | stated | guide 14.1 (assembly 70) |
| rootFilletRadius | 1.5 | 0.01 | stated | guide 2.3, 4.4 |
| tipMinThickness | 0.8 | 0.01 | stated | guide 2.3, 4.4 |
| meanSectionRadius | 77.4 | 0.01 | stated | guide 4.2 |
| hub/mean/tip InletAngle | 66.7 / 70.1 / 73.1° | 0.05 | stated | guide 4.3 |
| hub/mean/tip ExitAngle | 40.4 / 56.5 / 64.6° | 0.05 | stated | guide 4.3 |
| hub/mean/tip Camber | 26.3 / 13.6 / 8.5° | 0.05 | derived | inlet − exit (equals the 4.3 column) |
| hub/mean/tip Stagger | 53.55 / 63.3 / 68.85° | 0.1 | derived | (inlet + exit)/2 (4.3: about 53.6 / 63.3 / 68.8) |
| hub/mean/tip Chord | 22 / 20 / 18 | 0.01 | stated | guide 4.1, 4.2 item 4 |
| hub/mean/tip ThicknessRatio | 0.08 / 0.05 / 0.035 | 0.001 | stated | guide 4.3 |
| hubMaxThickness / meanMaxThickness | 1.76 / 1.0 | 0.01 | derived | ratio × chord |
| tipMaxThickness | 0.8 | 0.01 | derived | max(0.035 × 18 = 0.63, tipMinThickness) |
| leRadius / teThickness | 0.3 / 0.5 | 0.01 | stated | guide 4.3 |
| volume | 367,800 mm³ | ±2 % | derived | disc profile 354,638 (27,391 + 11,935 + 159,694 + 78,486 + 77,132) + blades 31 × ~403 (NACA-65 area 0.65 t c + TE allowance; Simpson over r 64.8/77.4/90.0; span above hub 24.35) + fillets 31 × 21.5 (0.483 mm² × 44.5 mm) |
| mass | 1.015 kg | – | derived | 367,800 mm³ × 2760 kg/m³ (stated about 1.0 kg) |
| surface area | 71,400 mm² | ±6 % | derived | revolved faces 41,932 + 31 × ~951 (flanks 2 × 1.01 × 20 × 24.35 + tip ~11.6 + TE 12.2 − root footprint 27.9 − fillet saving 28.7) |
| centre of mass | (0, 0, 11.4) | 0.3 | derived | cyclic pattern → on axis; z = ΣV·z/V with disc regions at −2.5, −0.5, 6.56, 16.5, 24 and blades near 5.5 |
| frontSection z −2.5 | 9,130.2 mm² | 0.5 % | derived | π(57.5² − 20²) |
| bladeSection z 6.5 | 14,100 mm² | 5 % | derived | π(65.65² − 20²) = 12,283 + 31 blade cuts × (24.35 span × 2.0–2.6 tangential width) ≈ 1,770 + fillets 50 |
| discMid z 16.5 | 11,212.3 mm² | 0.5 % | derived | π(63² − 20²) |
| sleeveSection z 24 | 9,641.6 mm² | 0.5 % | derived | π(63² − 30²) |
| tipCut x 87 | 3 loops | – | derived | x = 87 reaches r 90 at ±14.8°; blades 0, ±1 (±11.61°) are cut, blades ±2 (±23.2°, nearest edge ≥ 17°) are not |
| faces | 9,130.2 / 2,804.8 / 1,423.9 / 1,570.8 / 9,641.6 mm² | 1–3 % | derived | π(57.5²−20²), π(64.8²−57.5²), π(66.5²−63²), π(30²−20²), π(63²−30²) |
| tipSpanY | 180 | 0.1 | derived | blades 8 (92.9°) and 23 (267.1°) span ±90° with their tips |
| sleeveRearZ edit +2 | +19,283.2 mm³, bbox z +2 | 2 % | derived | 2 × π(63² − 30²) |
| bladeCount edit +2 | +850 mm³ | 35 % | derived | 2 × (403 blade + 21.5 fillet) |
| tipRadius edit −1 | decrease, bbox (−2, −2, 0) | – | derived | 31 tip slices of ~11.6 mm² removed |

Feasible intervals: `sleeveRearZ` in (20, 38] (it must stay behind the disc rear face z 20 and inside the OGV band, which ends at own z 38). The sweep 24 / 28 / 32 lies inside this interval; the infeasible delta −10 (z 18) must fail an `assert sleeveRearZ > discRearZ`. `bladeCount` stays odd and within 17 … 47 (guide 2.3). `tipRadius` ≤ 90.0 keeps the 0.25 mm cold clearance.

## 6. Defaults retained

- Envelope tolerance 0.5 mm. The finished part reaches x −89.99 … 90.0; the looser band lets an envelope-only blockout with simple blade stand-ins meet the ±x/±y extremes. The z faces, dimensions and cylinders carry their own 0.05 mm tolerances.
- Tip clearance floor 0.15 mm (nominal 0.25), to absorb tessellation of the r 90.25 keep-out. Band gap floors are 0.4 mm (nominal 0.5), matching the assembly's seal clearances.
- Density 2760 kg/m³ for 2618-T61 (guide 14.1).
- Blockout band 355,000 … 390,000 mm³: the disc profile plus blade stand-ins that reach r 90.

## 7. Unrepresentable or low-confidence features

- **Disc web relief:** "web 10 thick at the bore, 6 under the rim" is not modelled. The full-annulus front face, the rear face inside the sleeve and the solid OD 126 × ID 60 sleeve leave only internal undercuts for a relief. The solid section gives 1.015 kg, which matches the stated 1.0 kg (open question).
- **Tip thickness:** 3.5 % of 18 mm (0.63 mm) violates the 0.8 mm minimum, so the tip section is thickened to 0.8 mm. No acceptance item can measure the section maximum directly (a ray-cast thickness would be dominated by the 0.3 mm LE radius and the 0.5 mm TE), so the plan's section construction carries this requirement.
- **Root fillet:** it is not measurable by volume (+0.18 %) or area, and has no probe placement robust to the stacking-line uncertainty. It may stop at the LE and TE, where the hub ends at the z −1 and z 13 steps.
- **Tip profile:** the transonic tip (M_rel 1.20) keeps the intent's circular-arc camber; guide 4.3 suggests MCA profiles above 1.1.
- **Not modelled:** dowels (2 × D4), the balance land at r 45, and the 10 µm interference fit.
- **Blade sections:** the sections may be planar at r or wrapped on cylinders. The volume (±2 %) and blade-section (±5 %) tolerances cover either construction.
- **Changed (revision 3, reviewer notes):** the blade hand is now stated and probed (two solid points on blade 0's +θ side near the LE, two void points at their mirror images). The built rotor_2 was mirrored: in mrfCold it pumped against the stream (Uz −28.7 m/s at z 48, 6.35 N m, inlet 11.6 kPa above the outlet), and the earlier probes could not tell the hand. No stated value changes.
- **Neighbouring parts:** the hardware keep-outs (stator_1 inner band, OGV inner band, casing bore) are derived from those designs in the guide. The OGV band's front end at own z 16 is inferred.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
