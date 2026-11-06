# axjet-c2-stator_1 — design brief

## 1. Intent and configuration

Stator-1 of the AXJET-220 two-stage compressor module (assembly `axjet-c2`): one 6061-T6 body made of the casing ring z 18 ... 58 (OD 200, front and rear flanges OD 224 with 8 x D5.5 on PCD 212, one hole on +x, as case_r1; revision 1), the outer band (flow surface r 90.0, z 20 ... 38) integral with it, 41 circular-arc vanes (chord 15, LE at z 22, radial stacking, metal angles of guide section 4.3) and the inner band (flow surface r 61.0 at z 20 rising straight to r 64.5 at z 38) whose underside carries a two-tooth labyrinth with tips at r 58.0 facing the seal spacer (OD 115) at 0.5 mm. The bore is r 90.25 over z 18 ... 20 and z 38 ... 58; the rotor-2 abradable (z 40 ... 58) is modelled as ring material finished at r 90.25. Frame = assembly frame: joints stator1OnCase at [0, 0, 18] and ogvOnCase at [0, 0, 58], both axis +z. Authoritative: `sources/axjet_design_and_implementation_guide.md`.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa235 | sections 3.2 flow path, 4.1 counts/chord, 4.3 S1 metal angles, 4.4 casing/bands/seals, 11 material, 14.1 body table, joints and clearances; Appendix B angle convention |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| ring axial extent | z 18 ... 58 | mm | 4.4, 14.1 | 0.05 | stated |
| barrel OD / flange OD | 200 / 224 | mm | 4.4; revision 1 change 2 (was 212) | 0.05 | stated |
| flange thickness | 6 (z 18 ... 24, 52 ... 58) | mm | intent | 0.05 (checks) | inferred |
| bolt holes | 8 x D5.5 (M5 clearance) per flange on PCD 212, hole 0 on +x | mm | revision 1 change 2 (was 8 x D6.4 on PCD 206) | 0.05 | stated |
| bore | r 90.25, z 18 ... 20 and z 38 ... 58 | mm | intent, 4.4 | 0.05 | stated |
| outer band flow surface | r 90.0, z 20 ... 38 | mm | 4.4, 3.2 | 0.05 | stated |
| inner band flow surface | r 61.0 (z 20) -> 64.5 (z 38), straight | mm | intent, 3.2 | probes | stated |
| inner band faces | z 20 and z 38 | mm | intent | 0.05 | stated |
| labyrinth | 2 teeth, tips r 58.0, 0.5 gap to spacer OD 115 | mm | intent, 4.4 | 0.05 | stated |
| nothing inside r 58.0 | keep-out | mm | intent | 0.05 | stated |
| vanes | 41, chord 15, LE z 22, radial stacking | mm | 4.1, intent | section | stated |
| S1 sections hub/mean/tip | inlet 50.5/43.5/37.9, camber 61.9/54.5/48.5, exit -11.4/-11.0/-10.6, stagger 19.5/16.3/13.6, t/c 8/7/6 % | deg, - | 4.3 | 0.05 deg | stated |
| LE radius / TE thickness | 0.25 / 0.5 | mm | 4.3 | 0.01 | stated |
| rotor-2 tip gap | 0.25 (tips r 90.0, z 42 ... 55) | mm | intent, 4.1 | 0.2 ... 0.3 | stated |
| axial row gaps | 4 to rotor-1 hub TE (z 16), 3 to rotor-2 hub (z 41) | mm | intent | 0.05 | stated |
| material | 6061-T6, 2700 kg/m3 | - | 11, 14.1 | - | stated |

## 4. Coordinate frame, scale, and measurement method

Origin on the engine axis at assembly z = 0 (rotor-1 leading-edge plane); +z downstream along the axis; +x radial through the centre of hole 0 of each flange; +y = z x x. Datums: A front face z 18 (seats on case_r1), B the engine axis, C rear face z 58 (carries ogv_ring). No images or meshes: every value is read from the guide text and tables in millimetres and degrees. Vane angles follow Appendix B: measured from the axial direction, positive in the direction of rotation, taken as positive about +z (the rotorSpin axis). Each section's camber line is a circular arc from the inlet metal angle at the LE to the exit metal angle at the TE (chord at the stagger angle); thickness is NACA-65 scaled to t/c with LE radius 0.25 and a 0.5 mm TE; the forward-most LE point of every section lies at z 22 on a radial line, vane 0 at polar angle 0. Sections sit at r 61.0, 75.5 and 90.0 (rotor-1 exit hub/mean/tip, where the 4.2 stator inlet angles apply); the vane is extended into both bands and fused, never protruding below the land or into the bore.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| ringFrontZ / ringRearZ | 18 / 58 | 0.01 | stated | 4.4, 14.1 |
| casingOuterDia / flangeOuterDia | 200 / 224 | 0.01 | stated | 4.4; revision 1 change 2 |
| flangeThickness | 6 | 0.5 | inferred | intent "6 thick, inferred"; inlet-frame rear flange z -24 ... -18 |
| boltHoleDia / boltPcd / boltCount / boltStartAngle | 5.5 / 212 / 8 / 0 | 0.01 | stated | revision 1 change 2; 14.1 case-r1 row for count and clocking |
| boreRadius / bandFlowRadius | 90.25 / 90.0 | 0.01 | stated | intent, 4.4 |
| bandFrontZ / bandRearZ | 20 / 38 | 0.01 | stated | intent |
| hubRadiusFront / hubRadiusRear | 61.0 / 64.5 | 0.01 | stated | intent, 3.2 |
| labTipRadius / labToothCount | 58.0 / 2 | 0.01 | stated | intent, 4.4 |
| labLandRadius | 59.0 | 0.2 | inferred | tooth height 1.0 not stated; feasible 58.2 ... 60.0 (assert labTipRadius + 0.2 <= labLandRadius <= hubRadiusFront - 1.0); sweep 58.5 ... 60.0; deltas -1.0 and +2.0 must fail the assert |
| labToothWidth / labTooth1Z / labToothPitch | 1.0 / 28 / 6 | 0.2 | inferred | teeth inside the seal-spacer span z 24 ... 38 |
| vaneCount / vaneChord / vaneLeZ | 41 / 15 / 22 | 0.01 | stated | 4.1, intent |
| vaneClockAngle | 0 | 0.5 | inferred | no clocking stated |
| vaneMeanRadius | 75.5 | 0.01 | derived | (hubRadiusFront + bandFlowRadius) / 2 |
| vane inlet / camber / exit / stagger / tmax (hub, mean, tip) | see section 3 | 0.05 deg, 0.1 deg stagger, 0.001 t/c | stated | 4.3 S1 rows; camber = inlet - exit; stagger ~ (inlet + exit) / 2 |
| vaneLeRadius / vaneTeThickness | 0.25 / 0.5 | 0.01 | stated | 4.3 |
| volume | 369300 | 3000 | derived | casing pi(100^2-90.25^2)*22 + pi(100^2-90^2)*18 + 2 pi(112^2-100^2)*6 - 16*23.758*6 = 329272 (revision 1: +25044 per flange); band pi*18/3*(61^2+61*64.5+64.5^2) - pi*59^2*18 + 2 pi(59^2-58^2)*1 = 26611; vanes 41 x 327.0 = 13407 (NACA-65 area 0.650 t c + TE wedge 1.875 mm2, span hub surface -> 90) |
| surface area | 144600 | 5 % | derived | casing 93106 (revision 1: +8653 per flange) + band 17740 + vanes 41 x 824 |
| centre of mass | (0, 0, 37.06) | 0.3 | derived | rotational symmetry; sum(V z)/V, the flange growth centred on z 38 |
| section z 21 | 14599.8, 2 loops, 10 holes | 0.5 % | derived | pi(112^2-90^2) - 8*23.758 + pi(61.194^2-59^2); holes = casing bore, 8 bolt holes, band bore |
| section z 29 | 8598, 1 loop, 42 holes | 3 % | derived | pi(100^2-90^2) + pi(62.75^2-59^2) + 41 x 29.1 (t/cos(stagger) x span) |
| section z 45 / z 55 | 5827.46 / 13629.60 (9 holes) | 0.2 % / 0.3 % | derived | pi(100^2-90.25^2); pi(112^2-90.25^2) - 8*23.758 |
| faces z 18, 58 / z 24, 52 | 13629.60 / 7802.15 | 0.3 % / 0.5 % | derived | hole area pi*2.75^2 = 23.758, wholly inside the flange land |
| faces z 20 / z 38 (sum) | 895.55 / 2275.49 | 0.5 % | derived | band face pi(61^2-59^2) or pi(64.5^2-59^2) + bore step pi(90.25^2-90^2) = 141.57 on the same plane |
| edit casingOuterDia +2 | +17681.4 | 2 % | derived | pi(101^2-100^2) x 28 (barrel z 24 ... 52 only) |
| edit labLandRadius +0.5 | -2978.2 | 2 % | derived | -pi(59.5^2-59^2) x (18 - 2 x 1.0) |
| blockout | 319300 ... 379300 | - | derived | revolved ring with OD 224 flanges 331553, with inner band 358164 (the earlier band shifted by the flange growth 49310) |

## 6. Defaults retained

Release status `reconstruction` from the seed. Envelope tolerance 0.05 mm (machined part). Face and section area tolerances are 0.2 ... 0.5 % where the geometry is analytic and 3 % where vane thickness construction enters.

## 7. Unrepresentable or low-confidence features

- Changed (revision 1, reviewer notes): flanges OD 224 with 8 x D5.5 on PCD 212; the guide's D6.4 holes on PCD 206 broke through the OD 212 rim and grazed the barrel, leaving no seat for a head or nut.
- The trailing edges reach z 36.14 ... 36.58, past the nominal z 36, because chord 15 and LE z 22 are kept.
- Labyrinth tooth geometry (height, width, pitch, positions) is inferred.
- Rotation direction, vane clocking and section radii are inferred; the conical inner band flow surface and the vane surfaces are checked only by probes, sections and clearances (no cone spec in the schema).
- The outer band (r 90.0 ... 93.5) and the rotor-2 abradable are ring material; neither has its own surface.
- The swirl-option and multiple-circular-arc tip sections of 4.2/4.3 are not modelled (baseline only).

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
