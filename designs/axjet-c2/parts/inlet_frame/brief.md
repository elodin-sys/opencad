# axjet-c2-inlet_frame — design brief

## 1. Intent and configuration

The inlet frame of the AXJET-220 two-stage compressor module (body `inlet_frame` of the assembly `axjet-c2`) is one 6061-T6 body (2700 kg/m³) modelled in the assembly frame. It is the duct from the bolt-on bellmouth flange (z −72) to the case_r1 seat (z −18), the hub that houses the front bearing pair, the hub fairing that carries the front seal sleeve around the rotor_1 seal arm, and five radial struts. The authoritative source is `sources/axjet_design_and_implementation_guide.md`: section 2.4 (inlet flange), 3.2 (flow-path radii), 4.4 (rotor_1 seal arm and casing), 8.1 (rotor stack and front bearing), 9 (inlet), 11 (material and process) and 14.1 (the `inlet-frame` row and joints), together with the orchestrator's intent for this body (bellmouth ellipse, duct outer wall, front wall, nose screws, seal-sleeve web, all marked inferred there).

The assembly places the frame by four rigid joints in its own frame (the assembly frame): `inletFrameOnCase` at [0, 0, −18] +z, `bellmouthOnFrame` at [0, 0, −72] +z, `noseOnInlet` at [0, 0, −80] +z and `bearingFrontInHub` at [0, 0, −72] +z. Only this body is drafted here; the bellmouth, nose cone, bearing, rotor_1, drum shaft and case_r1 are separate designs.

Construction notes for the modeller:

- Revolve two profiles about z. The duct profile is the front flange, outer wall r 100, rear flange and the inner contour (ellipse, then r 90.25). The hub profile is the front wall, hub ring, fairing shell and seal sleeve; its vertices are listed in section 4.
- Pattern the struts at 72° with the first on +x. Each strut is a NACA 0020-type symmetric section (closed trailing edge, 6 mm on the 30 mm chord, revision 1) in the plane normal to its radial direction. It is extruded radially from r 29 (inside the hub ring, clear of the r 26 bore) to r `ductOuterRadius − 1.5` (inside the wall, never through r 100).
- Cut the hole patterns with cutters overrun into air.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | AXJET-220 guide, mm. Sections 2.4, 3.2, 4.4, 8.1, 9, 11 and 14.1 define the inlet frame and its neighbours. No images and no reference mesh. |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| front flange (bellmouth face z −72) | z −72 … −67, OD 224 | mm | intent; guide 2.4, 14.1 | 0.01 | stated |
| front flange holes | 8 × D5.5 through on PCD 216, one on +x; M5 screws from behind into the bellmouth | – | revision 1 change 4 (guide 2.4: 8 × M5 tapped) | 0.05 | stated (revision) |
| inner contour | quarter-ellipse centre (z −45, r 125), semi-axes 50 axial and 34.75 radial, from r 95.75 at z −72 to r 90.25 at z −45 | mm | intent; guide 9 | 0.01 | stated |
| contour at the flange face | r 95.8 (ellipse gives 95.752) | mm | guide 2.4 | 0.06 | stated / derived |
| cylindrical bore | r 90.25, z −45 … −18 | mm | intent; guide 3.2 | 0.01 | stated |
| duct outer wall | r 100, z −67 … −24 | mm | intent (as the casing rings) | 0.5 | inferred |
| rear flange (case seat z −18) | z −24 … −18, OD 224 | mm | revision 1 change 2 (guide 9: OD 212) | 0.01 | stated (revision) |
| rear flange holes | 8 × D5.5 (M5 clearance) on PCD 212, one on +x | mm | revision 1 change 2 (guide 14.1: 8 × D6.4 on PCD 206) | 0.01 | stated (revision) |
| hub | r 32, z −80 … −40 | mm | intent; guide 3.2 | 0.01 | stated |
| bearing seat | D52 H6 (modelled 52.0), z −75 … −35; bearing at z −72 … −42 | mm | intent; guide 9 | 0.01 | stated |
| front wall | z −80 … −75, D40 bore | mm | intent | 1.0 | inferred |
| nose-cone screws | 4 × M3 on PCD 56 | mm | guide 14.1 (count); intent (PCD) | 1.0 | stated count, inferred PCD |
| drum and stack-nut keep-out | nothing inside r 30 behind z −35 (the stack nut, r 28, spins at z −18 … −8) | mm | revision 1 change 1 (was r 22) | – | stated (clearance drumClearance) |
| fairing | 3 mm shell, r 32 at z −40 straight to r 57.6 at z −15, cylinder to z −11 | mm | intent; guide 9 | 0.01 | stated |
| rotor_1 axial gap | rear face z −11, 3 mm ahead of rotor_1 (z −8) | mm | guide 4.4, 9 | 0.1 | stated (clearance rotorAxialGap) |
| seal sleeve | bore D97, z −21 … −11, joined to the fairing by a web | mm | intent; guide 4.4, 9 | 0.01 | stated bore; inferred wall and web |
| seal arm clearance | 0.4 mm radial, ≥ 1 mm axial to the seal arm r 44 … 48.1, z −18 … −8 | mm | intent; guide 4.4 | 0.05 | stated (clearance sealRadialGap; void probe at z −18.5) |
| struts | 5, z −70 … −40 (chord 30), symmetric NACA 0020-type section 6 mm max, radial r 32 to the wall, 72° pitch, one on +x (solid) | mm, deg | revision 1 change 3 (guide 9, 14.1: 12 mm) | 0.01 | stated (revision) |
| flow path continuity | bellmouth at z −72, nose cone r 32 at z −80, case_r1 r 90.25 at z −18 | mm | intent | – | pinned by bellmouthFace, hubOuter, ductBore |
| material | 6061-T6, 2700 kg/m³ | – | guide 11, 14.1 | – | stated |

## 4. Coordinate frame, scale, and measurement method

The frame is the axjet-c2 assembly frame (guide section 3). The origin is on the engine axis at the stage-1 rotor leading-edge plane. +z runs along the axis with the flow, +x points up toward the dorsal intake, and +y completes a right-handed frame. Datums:

- A: the rear flange face, z −18.
- B: the engine axis.
- C: the bellmouth face, z −72.
- D: the hub front face, z −80.
- E: the +x clocking of the first strut and the first hole of each bolt pattern.

The part spans x, y ±112 (front flange OD 224) and z −80 … −11. The strut pattern (0°, ±72°, ±144°), the 8-hole patterns (0°, ±45°, ±90°, ±135°, 180°) and the nose screws (±45°, ±135°) are all symmetric about the plane y = 0 (symmetry `mirrorY`).

No images and no reference mesh were supplied. Every value is read from the text; there is no scale or rectification step.

Derived geometry, in profile coordinates (r, z):

- **Ellipse:** r(z) = 125 − 34.75 · √(1 − ((z + 45)/50)²). It gives r 95.752 at z −72, 95.318 at z −71, 94.906 at z −70, 93.795 at z −67 and 90.952 at z −55.
- **Fairing outer cone:** from (32, −40) to (57.6, −15), slope dr/dz = 1.024, half-angle 45.67°.
- **Fairing inner surface:** the 3 mm normal offset. The inner cone passes (29.904, −37.854) with r_in(z) = 29.904 + 1.024 (z + 37.854). The inner cylinder is r 54.6 from z −13.736. The inner cone meets r 51.5 at z −16.764 and r 48.5 at z −19.694, and lies at r 47.162 at z −21 and r 32.826 at z −35.
- **Hub-fairing-sleeve profile, closed polygon:** (20, −80) → (32, −80) → (32, −40) → (57.6, −15) → (57.6, −11) → (54.6, −11) → (54.6, −13.736) → (51.5, −16.764) → (51.5, −11) → (48.5, −11) → (48.5, −21) → (47.162, −21) → (32.826, −35) → (26, −35) → (26, −75) → (20, −75).
  - The region between the hub ring and the inner cone ahead of z −35 is solid.
  - The bearing bore is open to the rear at z −35.
  - A 3.1 mm annular slot (r 51.5 … 54.6) opens at z −11 between the sleeve and the fairing. Its bottom is at z −16.764, where the sleeve runs into the cone; that overlap is the web.
- **Duct profile, closed:** (95.752, −72) → (112, −72) → (112, −67) → (100, −67) → (100, −24) → (112, −24) → (112, −18) → (90.25, −18) → (90.25, −45), then along the ellipse back to (95.752, −72).
- **Strut half-thickness:** h(ξ) = 5 · (6/30) · 30 · (0.2969√ξ − 0.1260ξ − 0.3516ξ² + 0.2843ξ³ − 0.1036ξ⁴), with ξ = (z + 70)/30. The maximum is 3.0 at ξ = 0.3 (z −61). The section area is 0.68088 · t · c = 122.56 mm².

## 5. Measurement and inference record

Parameters:

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| frontFlangeFrontZ | −72 | 0.01 | stated | intent; guide 2.4, 14.1 |
| frontFlangeRearZ | −67 | 0.01 | stated | intent; guide 2.4, 14.1 |
| frontFlangeDia | 224 | 0.01 | stated | intent; guide 2.4 |
| frontBoltPcd | 216 | 0.01 | stated | intent; guide 2.4 |
| frontBoltCount | 8 | 0.01 | stated | intent; guide 2.4 |
| frontBoltDia | 5.5 | 0.05 | stated | revision 1 change 4: M5 clearance through holes (was the defaulted D4.2 tap drill) |
| ellipseCentreZ | −45 | 0.01 | stated | intent; guide 9 |
| ellipseCentreR | 125 | 0.01 | stated | intent; guide 9 |
| ellipseAxial | 50 | 0.01 | stated | intent |
| ellipseRadial | 34.75 | 0.01 | stated | intent |
| frontContourRadius | 95.752 | 0.06 | derived | ellipseCentreR − ellipseRadial · √(1 − ((frontFlangeFrontZ − ellipseCentreZ)/ellipseAxial)²); the guide's 95.8 is within 0.05 |
| ductRadius | 90.25 | 0.01 | stated | intent; guide 3.2, 9 |
| ductOuterRadius | 100 | 0.5 | inferred | intent: as the casing rings (OD 200, guide 4.4) |
| rearFlangeFrontZ | −24 | 0.01 | stated | intent; guide 9 |
| rearFlangeRearZ | −18 | 0.01 | stated | intent; guide 9, 14.1 |
| rearFlangeDia | 224 | 0.01 | stated | revision 1 change 2 (was 212) |
| rearBoltPcd | 212 | 0.01 | stated | revision 1 change 2 (was 206) |
| rearBoltCount | 8 | 0.01 | stated | intent; guide 14.1 |
| rearBoltDia | 5.5 | 0.01 | stated | revision 1 change 2 (was 6.4) |
| hubRadius | 32 | 0.01 | stated | intent; guide 3.2, 9 |
| hubFrontZ | −80 | 0.01 | stated | intent; guide 3.2 |
| fairingStartZ | −40 | 0.01 | stated | intent; guide 9 |
| bearingBoreDia | 52 | 0.01 | stated | intent; guide 9 (H6, modelled 52.0) |
| bearingBoreFrontZ | −75 | 0.01 | stated | intent; guide 9 |
| bearingBoreRearZ | −35 | 0.01 | stated | intent; guide 9 |
| frontWallBoreDia | 40 | 1.0 | inferred | intent: clears the M20 nose thread and the nose nut |
| noseScrewPcd | 56 | 1.0 | inferred | intent; between the D52 bore and r 32 |
| noseScrewCount | 4 | 0.01 | stated | guide 14.1 nose-cone row |
| noseScrewTapDia | 2.5 | 0.05 | defaulted | ISO tap drill for M3 × 0.5 |
| noseScrewDepth | 6 | 1.0 | inferred | 1.5 d thread plus run-out; floor z −74 inside the hub ring |
| noseScrewClock | 45 | 5 | inferred | off the +x wire path; keeps the y = 0 mirror |
| fairingThickness | 3 | 0.01 | stated | intent; guide 9 (normal shell thickness) |
| fairingRadius | 57.6 | 0.01 | stated | intent; guide 3.2, 9 |
| fairingShoulderZ | −15 | 0.01 | stated | intent; guide 3.2, 9 |
| fairingRearZ | −11 | 0.01 | stated | intent; guide 4.4, 9 |
| sealBoreDia | 97 | 0.01 | stated | intent; guide 4.4, 9 |
| sealFrontZ | −21 | 0.01 | stated | intent; guide 9 |
| sealSleeveWall | 3 | 0.5 | inferred | matches the fairing shell; the merge with the cone is the web |
| strutCount | 5 | 0.01 | stated | intent; guide 9, 14.1 |
| strutPitch | 72 | 0.01 | derived | 360 / strutCount (the intent states 72°) |
| strutLeadZ | −70 | 0.01 | stated | intent; guide 3.2, 9 |
| strutChord | 30 | 0.01 | stated | intent; guide 9 |
| strutTrailZ | −40 | 0.01 | derived | strutLeadZ + strutChord |
| strutThickness | 6 | 0.01 | stated | revision 1 change 3: NACA 0020-type, 6 mm on 30 mm (was 12) |

Provenance count, 44 parameters in total:

- 33 stated.
- 3 derived: frontContourRadius, strutPitch, strutTrailZ.
- 6 inferred: ductOuterRadius, frontWallBoreDia, noseScrewPcd, noseScrewDepth, noseScrewClock, sealSleeveWall.
- 2 defaulted: frontBoltTapDia, noseScrewTapDia.

The strut profile form is also inferred, but it lives in the feature text rather than in a parameter.

Acceptance values. All are derived by plain-Python integration of the profiles above; no CAD was built.

| item | value | tolerance | provenance | formula / evidence |
|---|---|---|---|---|
| volume | 501,106 mm³ (1.353 kg) | 1 % | derived | See the breakdown after this table (revision 1). Consistent with the guide's 1.5 kg for inlet frame plus nose cone. |
| surface area | 170,569 mm² | 2 % | derived | See the breakdown after this table (revision 1). |
| centre of mass | (0, 0, −44.233) | 0.3 | derived | z from the first moments of the same decomposition (strut centroid z −57.46, rear flange z −21, front holes z −69.5); x = y = 0 by the 5-, 8- and 4-fold patterns. |
| section ductStruts z −55 | 8,081.8 mm², 1 loop, 6 holes | 3 % | derived | π(100² − 90.952²) + π(32² − 26²) + 5 × 312.13 (strut: t = 5.286 at mid chord, from r 32 to 90.952). |
| section frontFlange z −71 | 11,768.5 mm², 2 loops, 10 holes | 0.5 % | derived | π(112² − 95.318²) − 8π·2.75² + π(32² − 26²). |
| section ductFairing z −30 | 6,909.1 mm², 2 loops, 2 holes | 0.5 % | derived | π(100² − 90.25²) + π(42.24² − 37.946²). |
| section sealSleeve z −13 | 1,999.9 mm², 2 loops, 2 holes | 0.5 % | derived | π(57.6² − 54.6²) + π(51.5² − 48.5²). |
| section frontWall z −77 | 1,940.7 mm², 1 loop, 5 holes | 0.5 % | derived | π(32² − 20²) − 4π·1.25². |
| face bellmouthFace z −72 (−) | 10,414.5 mm² | 0.5 % | derived | π(112² − 95.752²) − 8π·2.75² |
| face frontFlangeBack z −67 (+) | 7,802.1 mm² | 0.5 % | derived | π(112² − 100²) − 8π·2.75² |
| face caseFace z −18 (+) | 13,629.6 mm² | 0.5 % | derived | π(112² − 90.25²) − 8π·2.75² (revision 1 rear flange) |
| face noseFace z −80 (−) | 1,940.7 mm² | 0.5 % | derived | π(32² − 20²) − 4π·1.25² |
| face bearingShoulder z −75 (+) | 867.08 mm² | 0.5 % | derived | π(26² − 20²) |
| face hubRearFace z −35 (+) | 1,261.5 mm² | 1 % | derived | π(32.826² − 26²) |
| face rearFaces z −11 (+, sum) | 1,999.9 mm² | 0.5 % | derived | Fairing ring π(57.6² − 54.6²) plus sleeve ring π(51.5² − 48.5²). |
| dimensions | axialLength 69, outerDiameter 224, flangeSpan 54, noseToBellmouth 8 | 0.05–0.1 | derived | from the stated planes |
| cylinders | 31 entries: bores, rims, fairing, sleeve, 8 + 8 + 4 holes | default | stated / derived | Positions are r · (cos θ, sin θ). θ = 45k° for both bolt patterns (r 108 and r 106, all D5.5); θ = 45° + 90k° for the nose screws (r 28). |
| clearances | sealRadialGap 0.35 … 0.45 (nominal 0.4); rotorAxialGap 2.9 … 3.1 (nominal 3.0); drumClearance ≥ 0.5 to a r 29.5 keep-out from z −34 (nominal ≥ 1.0 to the hub ring rear face, 3.3 to the fairing cone) | – | stated | rotor_1 seal arm r ≤ 48.1, z −18 … −8; rotor_1 face z −8; drum and stack-nut keep-out r 30 behind z −35 (revision 1) |
| thickness fairingShell | p05 ≥ 2.8, max 3.3 | – | stated | 3 mm normal shell, sampled only in z −34 … −24, away from the hub and sleeve junctions. Near z −22 a ray exits through the D97 bore at 2.76 mm, which is why the region stops at z −24. |
| blockout band | 383,000 … 588,000 mm³ | – | derived | The earlier band (0.9 × the hole- and strut-free revolve 442,010 up to about 1.17 × the full part) shifted by the revision 1 net volume change −12,001. |

Volume breakdown (501,106 mm³, revision 1):

- Pappus on the duct profile: 350,327.1, plus the OD 224 rear flange ring 2π(112² − 106²)·6 = 24,655.0.
- Pappus on the hub-fairing-sleeve profile: 91,683.0.
- Plus 5 struts × 7,329.9 (NACA 0020-type, 6 mm). Each strut's exposed volume is ∫ [F(r_d(z), h) − F(32, h)] dz, where F(R, h) = h√(R² − h²) + R² asin(h/R); F ≈ 2Rh − h³/(3R), so at h ≤ 3 the volume is within about 0.2 % of half the 12 mm value 14,659.7.
- Minus 8 front D5.5 through holes × π·2.75²·5 = 118.79 each.
- Minus 8 rear D5.5 holes × π·2.75²·6 = 142.55 each (wholly inside the flange land).
- Minus 4 M3 holes × π·1.25²·6 = 29.45 each.

Surface area breakdown (170,569 mm², revision 1):

- Pappus over each profile segment: duct 98,087.8 plus the OD 224 rear flange growth 8,653.2 (rim, faces and enclosed hole walls; the same per-flange change as case_r1), hub 45,547.0.
- Plus 5 struts × 3,508.2 net: the two sides (NACA 0020 perimeter 62.72 against 68.09 at 12 mm, × span 59.81) minus the footprints (2 × 122.6) on the hub cylinder and on the duct surface.
- Plus 8 front holes × (2π·2.75·5 − 2π·2.75²).
- Plus 4 M3 holes × 2π·1.25·6.

Edit tests and sweeps:

- **strutThickness, +2 mm (6 → 8):** expected ΔV = +12,260.7 mm³ (the strut volume is nearly linear in t, about 1,226 mm³ per mm per strut; computed with the NACA form). The tolerance is 10 % because the asin terms make the change slightly nonlinear. No bbox change.
  - Feasible interval: 2 … 20 mm (the struts are 40 mm apart at the hub).
  - Sweep: [4, 6, 8].
  - Infeasible delta: −6 (t = 0), which must fail an assert.
- **ductOuterRadius, +1 mm:** expected ΔV = π(101² − 100²) × 43 = +27,152.8 mm³ over the wall z −67 … −24. The rear holes are cut through the flange only, and the struts stay embedded. No bbox change.
  - Feasible interval: 97.5 … 105. The lower bound is set by the strut tip at r ductOuterRadius − 1.5, which must stay above the contour r 94.906 at the strut leading edge. The upper bound stays below the rear bolt holes, which start at r 103.25 on the r 112 flange.
  - Sweep: [98, 100, 102].
  - Infeasible delta: −7 (r 93 lies inside the contour r 93.795 at z −67), which must fail an assert.

Interfaces: none of the edit tests moves or resizes any pinned item.

| interface | pinned items |
|---|---|
| caseJoint | caseFace, ductBore, rearFlangeRim, rearBolt0 |
| bellmouthJoint | bellmouthFace, frontFlangeRim, frontBolt0, flangeSpan |
| noseJoint | noseFace, hubOuter, noseScrew0 |
| bearingSeat | bearingBore, bearingShoulder |
| rotorSeal | sealBore, rearFaces |
| clocking | mirrorY |

## 6. Defaults retained

- **Tap-drill diameter for the tapped holes (M3 as D2.5; the front M5 holes are D5.5 clearance holes since revision 1).** This is the usual cosmetic-thread convention; the threads themselves are purchased-process detail, not geometry.
- **Default symmetry bands (max 0.1, p95 0.05 mm).** No source states a tighter band.
- **Material and density 6061-T6 / 2700 kg/m³.** Taken from guide sections 11 and 14.1. The guide's AlSi10Mg printed-strut option is not modelled; it would change only the strut density.
- **Sharp edges everywhere.** No fillet or chamfer is stated, so none is added.

## 7. Unrepresentable or low-confidence features

- **Changed (revision 1, reviewer notes).** Rear flange OD 224 with 8 × D5.5 on PCD 212 (the guide's D6.4 on PCD 206 broke the OD 212 rim and left no seat for a head or nut); struts NACA 0020-type, 6 mm (the guide's 12 % and 12 mm disagreed, and 12 mm blocked about 16 % of the annulus); front flange 8 × D5.5 through holes with the M5 screws from behind into the bellmouth (the bellmouth lip covered the flange face); keep-out r 30 behind z −35 for the stack nut (already met by the geometry). Section ductStruts keeps its 3 % area tolerance for the inferred NACA form.
- **+x strut passages.** The oil-mist, starter and instrumentation lines through the +x strut are not dimensioned; the strut stays solid (revision 1 confirms).
- **Seal-sleeve web.** Taken as the merge of a 3 mm sleeve wall into the fairing cone (z −21 … −16.76). A literal web "ahead of z −19" would need a sleeve wall under 0.8 mm. The requirement it serves (≥ 1 mm axial clearance ahead of the seal arm) is met with 3 mm.
- **Bearing retention.** The rear retainer of the front bearing and the 3 mm gap ahead of it are not specified. The bore is left open to the rear.
- **Nose-cone screw pattern.** Inferred (PCD 56, 45° clocking, 6 mm deep); the nose cone needs lugs to reach r 28.
- **Front wall bore.** The D40 bore is inferred; the nose nut OD that must pass through it is not stated.
- **Out of scope.** The air body, labyrinth teeth (they are on rotor_1), the O-ring damper grooves and the starter wiring are not part of this body.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
