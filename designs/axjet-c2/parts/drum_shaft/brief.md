# axjet-c2-drum_shaft — design brief

## 1. Intent and configuration

Drum shaft of the AXJET-220 compressor module (body `drum_shaft` of the assembly `axjet-c2`): a turned 17-4PH H1025 hollow shaft (density 7800 kg/m³) that carries rotor_1, the seal spacer, rotor_2 and the stack nut, runs in the front bearing pair on a D25 journal, and bolts to the coupling hub of the full engine at its D60 rear flange. Authoritative source: `sources/axjet_design_and_implementation_guide.md`, section 8.1 (drum shaft and rotor stack rows) and the section 14.1 parts table and joint list. One solid, axisymmetric except the six flange holes. Threads are plain cylinders at their major diameter (M20 → D20, M39 → D39); fits are nominal (D25 h5 → 25.0, D40 h6 → 40.0, D44 H7 → 44.0).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | §3 assembly frame; §8.1 drum shaft and rotor stack rows; §11 material and process; §12 mass budget; §14.1 drum-shaft row (own frame, 17-4PH, 7800) and joints `rotorSpin`, `rotor1OnDrum`, `spacerOnDrum`, `rotor2OnDrum`, `stackNutOnDrum` |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| overall axial extent | z −90 … 262 (352) | mm | §8.1, §14.1 | 0.1 | stated |
| nose thread M20 × 1 LH (plain D20) | z −90 … −75 | mm | §8.1 | 0.01 | stated |
| front bearing journal D25 h5 | z −75 … −40 | mm | §8.1 | 0.01 | stated |
| journal/neck step (bearing spacer abutment) | z −40 | mm | §8.1 rotor stack, revision 1 | 0.01 | stated |
| neck D36 | z −40 … −18 | mm | revision 1 change 1 | 0.01 | stated (revision) |
| stack-nut thread M39 × 1.5 (plain D39) | z −18 … −8 | mm | revision 1 change 1 (was §8.1 z 62 … 72) | 0.01 | stated (revision) |
| drum D40 h6 seats / aft drum | z −8 … 62 / 68 … 254 | mm | §8.1, revision 1 | 0.01 | stated |
| shoulder D46 × 6 (rotor_2 rear stop) | z 62 … 68 | mm | revision 1 change 1 (was §8.1 z −14 … −8) | 0.01 | stated (revision) |
| seats rotor_1 / seal spacer / rotor_2 | z −8 … 24 / 24 … 38 / 38 … 62 | mm | §8.1 rotor stack, §14.1 | 0.05 | stated |
| rear flange D60 × 8 | z 254 … 262 | mm | §8.1 | 0.01 | stated |
| flange holes | 6 × M5 tapped on PCD 50 | mm | §8.1 | 0.01 | stated (diameter, depth, clocking open) |
| coupling recess D44 H7 × 2 in the flange rear face | z 260 … 262 | mm | §8.1 | 0.01 | stated |
| bore D28 | from z −30 through the flange | mm | §8.1 (D28), intent (start) | 1.0 on the start | stated diameter, inferred start |
| joint frames | rotorSpin and rotor1OnDrum at z 0, spacerOnDrum z 24, rotor2OnDrum z 42, stackNutOnDrum z −18 (revision 1), all axis +z | mm | §14.1 joints, revision 1 | 0.1 | stated |
| material / density | 17-4PH H1025, 7800 | kg/m³ | §11, §14.1 | – | stated |

## 4. Coordinate frame, scale, and measurement method

Own frame of the part, identical to the assembly frame shifted to the rotor_1 leading-edge plane: origin on the spin axis at assembly z 0; +z along the axis in the flow direction (nose thread at z −90, flange at z 262); +x parallel to the assembly x (engine up), bolt hole 1 on +x; +y completes a right-handed frame. Datums: A the spin axis (D25 journal and D40 seat), B the shoulder front face z 62 (rotor_2 stop), C the journal step z −40 (bearing spacer), D the flange rear face z 262 (coupling hub), E the rigid mount stations z −18, 0, 24, 42. No images or meshes: every value is read from the text; there is no scaling or rectification.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| shaftFrontZ | −90 mm | 0.01 | stated | §8.1 thread z −90 … −75 |
| journalFrontZ | −75 mm | 0.01 | stated | §8.1 journal z −75 … −40 |
| journalRearZ | −40 mm | 0.01 | stated | §8.1 journal end; revision 1: spacer against the D25/D36 step at z −40 |
| shoulderFrontZ | 62 mm | 0.01 | stated | revision 1 change 1: shoulder z 62 … 68, rotor_2 rear stop |
| shoulderRearZ | 68 mm | 0.01 | stated | revision 1 change 1 |
| nutThreadFrontZ | −18 mm | 0.01 | stated | revision 1 change 1: M39 thread z −18 … −8 |
| nutThreadRearZ | −8 mm | 0.01 | stated | revision 1 change 1; rotor_1 front face plane |
| neckDia | 36 mm | 0.01 | stated | revision 1 change 1: D36 z −40 … −18 so the nut passes |
| flangeFrontZ | 254 mm | 0.01 | stated | §8.1 flange z 254 … 262 |
| shaftRearZ | 262 mm | 0.01 | stated | §8.1 flange rear face; §14.1 coupling flange z 262 |
| boreStartZ | −30 mm | 1.0 | inferred | intent; the source's z −45 would cut through the D25 journal (r 12.5 < bore r 14) and split the shaft |
| noseThreadDia | 20 mm | 0.01 | stated | §8.1 M20 × 1 LH, plain D20 per intent |
| journalDia | 25 mm | 0.01 | stated | §8.1 D25 h5 |
| drumDia | 40 mm | 0.01 | stated | §8.1 D40 h6 |
| shoulderDia | 46 mm | 0.01 | stated | §8.1 D46 × 6 |
| nutThreadDia | 39 mm | 0.01 | stated | §8.1 M39 × 1.5, plain D39 per intent |
| flangeDia | 60 mm | 0.01 | stated | §8.1 D60 × 8 |
| boreDia | 28 mm | 0.01 | stated | §8.1 tube D40 × D28 |
| recessDia | 44 mm | 0.01 | stated | §8.1 D44 H7 × 2 |
| recessDepth | 2 mm | 0.01 | stated | §8.1 |
| boltCircleDia | 50 mm | 0.01 | stated | §8.1 6 × M5 on PCD 50 |
| boltCount | 6 | 0.01 | stated | §8.1 |
| boltHoleDia | 4.2 mm | 0.1 | defaulted | ISO 2306 tap drill for M5 × 0.8; thread form cosmetic |
| boltStartAngle | 0° | 1.0 | inferred | guide convention: one flange hole on +x (case-r1, comb-outer-case) |
| volume | 228,247.9 mm³ | 0.2 % | derived | outer revolve π·Σr²L = 410,522.1 (segments r 10×15, 12.5×35, 18×22, 19.5×10, 20×70, 23×6, 20×186, 30×8) − bore π·14²·292 − recess annulus π·(22²−14²)·2 − holes 6·π·2.1²·8 |
| surface area | 74,668.4 mm² | 0.5 % | derived | outer cylinders 2π·Σ r·L; annular end/step faces (z −90, −75, −40, −18, −8, 62, 68, 254, 260, 262, bore floor); bore 2π·14·290, recess wall 2π·22·2, holes 6·2π·2.1·8 |
| centre of mass | (0, 0, 99.928) mm | 0.1 | derived | x = y = 0 by the 6-fold pattern; z = Σ V_i z_i / V with the same solids and voids |
| mass (information) | 1.780 kg | – | derived | 228,247.9 mm³ × 7800 kg/m³ |
| sections z −82.5 / −57.5 / −35 | 314.159 / 490.874 / 1017.876 mm², no holes | 0.5 % | derived | π·10², π·12.5², π·18² (solid D36 web ahead of the bore floor) |
| sections z −24 / −13 / 10 / 65 / 160 | 402.124 / 578.838 / 640.885 / 1046.150 / 640.885 mm², 1 hole | 0.5 % | derived | π·(18²−14²), π·(19.5²−14²), π·(20²−14²), π·(23²−14²), π·(20²−14²) |
| sections z 257 / 261 | 2128.555 / 1223.776 mm², 7 holes | 0.5 % | derived | π·(30²−14²) − 6π·2.1²; π·(30²−22²) − 6π·2.1² |
| faces | frontEnd 314.159, threadStep 176.715, journalStep 527.002, boreFloor 615.752, nutThreadFront 176.715, seatStep 62.046, shoulderStop/Rear 405.265, flangeFront 1487.670, recessFloor 904.779, flangeRear 1223.776 mm² | 0.5–1 % | derived | annuli π·(R²−r²), flange faces net of 6 holes |
| edit boreDia +2 | ΔV −26,420.8 mm³, bbox 0 | 2 % | derived | −π/4·(30²−28²)·290 (bore z −30 … 260; the recess covers 260 … 262) |
| edit boreStartZ +10 | ΔV +6,157.5 mm³, bbox 0 | 2 % | derived | π·14²·10 |
| blockout band | 390,000 … 431,000 mm³ | – | derived | solid outer revolve (no bore, recess or holes) 410,522.1 ± ~5 %; it touches all six envelope faces (nose end z −90, flange r 30 and z 262) |

Feasible intervals and guards (the source must `assert` them): `boreDia` in (0, `neckDia`) — sweep 24, 28, 32 (2 mm neck wall at 32); infeasible delta +12 (40, through the D36 neck and the drum wall). `neckDia` < `nutThreadDia` so the ID 39 nut passes over the neck. `boreStartZ` in (`journalRearZ`, `shaftRearZ` − `recessDepth`) — sweep −35, −30, −20; infeasible delta −15 (−45, the source's literal value, which breaks through the journal and splits the shaft). Also assert `flangeDia` > `boltCircleDia` + `boltHoleDia` and `boltCircleDia` − `boltHoleDia` > `recessDia` so the holes stay inside the flange and clear of the recess.

## 6. Defaults retained

- `boltHoleDia` 4.2 mm: ISO tap-drill size for M5 × 0.8; a tapped hole's material boundary is its minor diameter, and the thread is cosmetic. Changes only 0.3 % of the volume against a D5 representation.
- Through holes in the 8 mm flange: the space ahead of the flange (r 20 … 30) is open, so a through tapped hole is the plain reading of "6 × M5 on PCD 50".
- Flat bore floor at z −30 and sharp edges everywhere: no chamfer, fillet, undercut or drill-point dimension is given.
- Envelope tolerance 0.1 mm; cylinder radius tolerance 0.02 mm, tight enough to tell the D39 thread band from the D40 drum.

## 7. Unrepresentable or low-confidence features

- Thread forms (M20 × 1 LH, M39 × 1.5, 6 × M5) are not modelled; plain cylinders at the major diameter (external) and tap-drill holes (internal) stand in.
- Fit tolerances (h5, h6, H7) and the 10 µm rotor interference are not representable at nominal geometry; mating bores and seats will be coincident in the assembly.
- Bore start z −30 is inferred (source conflict at z −45); the bolt-pattern clocking is inferred; hole depth is assumed through.
- Thread run-outs, grinding reliefs at the journal and seat steps, and edge chamfers are omitted.
- The bolt-hole edge (r 22.9) sits 0.9 mm outside the recess wall (r 22); thin but valid.
- Mass 1.78 kg exceeds the guide's 1.6 kg group budget for "drum shaft, nuts, spacers" (an estimate); recorded, not reconciled.
- Changed (revision 1, reviewer notes): front-loaded rotor stack. Shoulder D46 × 6 moved to z 62 … 68, M39 thread to z −18 … −8, D36 neck z −40 … −18, stackNutOnDrum at z −18; the build sequence (blisks and spacer from the front against the shoulder, nut over the neck) is now possible.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
