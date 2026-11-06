# axjet-c2 — assembly brief

## 1. Intent and configuration

AXJET-220 two-stage transonic axial compressor module, machine 1 of section 14 of `sources/axjet_design_and_implementation_guide.md` (authoritative; section 14.1 is the build list, sections 3.2, 4, 8 and 9 give the dimensions). Bodies: bolt-on bellmouth lip, inlet frame with five struts, hub fairing and front bearing housing, nose cone with the starter, 29-blade rotor-1 blisk, 41-vane stator-1 ring, S1 seal spacer, 31-blade rotor-2 blisk, 47-vane OGV ring, the stacked casing rings (case_r1, stator_1, ogv_ring), the D40 drum shaft with the stack nut and the front bearing pair, and the derived air body. One revolute joint carries the spool on case_r1. Cases that matter: `cold` (8,000 rpm, 20,900 L/min) for the steady MRF geometry check on the air body, and `design` (44,000 rpm, held out) for the rotor-1 centrifugal displacement and modal cases. The hot section belongs to machine 2 (`axjet`) and is out of scope here.

Note (not a question): the installation envelope (224 x 665 mm bay of the BDXL airframe) is a design input pending measurement (section 2.1); the module geometry does not depend on it.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | AXJET-220 design guide; section 14.1 defines this module; the section drawing it references is not supplied |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| case_r1 | modelled (datum) | axjet-c2-case_r1 | 6061-T6, 2700 | 4.4, 14.1, rev 1 | z -18 ... 18, bore D180.5 with the abradable merged, OD 200, flanges OD 224 with 8 x D5.5 on PCD 212 |
| bellmouth | modelled | axjet-c2-bellmouth | 6061-T6, 2700 | 9, 14.1, rev 1 | z -95 ... -72, quarter-ellipse r 125 to r 95.8 closed by a 6 mm tangent quarter-round lip; 8 x M5 tapped from the rear |
| inlet_frame | modelled | axjet-c2-inlet_frame | 6061-T6, 2700 | 9, 14.1, rev 1 | duct z -72 ... -18, hub with the D52 bearing seat, fairing to z -11, seal sleeve D97, five 6 mm NACA 0020-type struts |
| nose_cone | modelled | axjet-c2-nose_cone | 6061-T6, 2700 | 8.3, 14.1 | own origin at assembly z -80; D64 cylinder and tangent ogive to z -165; starter bulkhead |
| rotor_1 | modelled | axjet-c2-rotor_1 | 2618-T61, 2760 | 4.3, 4.4, 14.1 | own origin at assembly z 0; 29 blades, tip r 90.0, seal arm to z -18 |
| stator_1 | modelled | axjet-c2-stator_1 | 6061-T6, 2700 | 4.3, 4.4, 14.1 | z 18 ... 58, 41 vanes z 22 ... 36, inner band r 58 labyrinth, bore r 90.25 over rotor 2 |
| seal_spacer | modelled | axjet-c2-seal_spacer | 2618-T61, 2760 | 4.4, 8.1, 14.1 | own origin at assembly z 24; OD 115 x ID 40 x 14 |
| rotor_2 | modelled | axjet-c2-rotor_2 | 2618-T61, 2760 | 4.3, 4.4, 14.1 | own origin at assembly z 42; 31 blades, rear sleeve OD 126 to z 70 |
| ogv_ring | modelled | axjet-c2-ogv_ring | 6061-T6, 2700 | 4.3, 4.4, 14.1 | z 58 ... 80, 47 vanes from z 61, inner band r 63.5 labyrinth |
| drum_shaft | modelled | axjet-c2-drum_shaft | 17-4PH H1025, 7800 | 8.1, 14.1, rev 1 | own origin at assembly z 0; z -90 ... 262, D25 journal, D36 neck, M39 thread z -18 ... -8, D40 seats, D46 shoulder z 62 ... 68, D60 flange |
| bearing_front | modelled | axjet-c2-bearing_front | steel, 7800 | 8.1, 14.1 | own origin at assembly z -72; DB pair as one OD 52 x ID 25 x 30 ring |
| stack_nut | modelled | axjet-c2-stack_nut | 17-4PH H1025, 7800 | 8.1, 14.1, rev 1 | own origin at assembly z -18; OD 56 x ID 39 x 10, six notches; clamps rotor_1 at z -8 |
| starter | purchased | - | - | 8.3, 14.1 | catalog cylinder D50 x 35 at z -143 ... -108 (own frame = assembly frame) |
| air | derived (fluid) | - | air, 1.204 | 14.1 | plenum r 150 z -220 ... -95 + bellmouth + duct + annulus to z 90 |

The guide's hyphenated names (`case-r1`, `rotor-1`, ...) become underscores because body names must be identifiers; the design leaves follow the body names.

## 4. Frames, joints and motion

Assembly frame (section 3) = the case_r1 frame: origin on the engine axis at the rotor-1 leading-edge plane, z along the axis with the flow, x up (the +x strut and the first hole of every flange), y right-handed. Every part frame has axes parallel to it; case_r1, bellmouth, inlet_frame, stator_1, ogv_ring and the starter catalog use it directly, the others translate along z: nose_cone -80, bearing_front -72, stack_nut -18, rotor_1 and drum_shaft 0, seal_spacer 24, rotor_2 42.

Rotor build sequence (revision 1): the vane rings, blisks and spacer go on stage by stage from the front against the drum shoulder at z 62 (rotor_2, the stator_1/ogv_ring stack, the seal spacer, rotor_1), the stack nut passes over the D36 neck and clamps the stack on the M39 thread at z -18 ... -8, then the front bearing pair and the nose nut follow.

| joint | kind | parent | child | parent frame origin | child frame origin | notes |
|---|---|---|---|---|---|---|
| rotorSpin | revolute | case_r1 | drum_shaft | (0, 0, 0), axis +z | (0, 0, 0), axis +z | drive motor, `case_value: speedRpm`; positive about +z (sense not stated) |
| rotor1OnDrum | rigid | drum_shaft | rotor_1 | z 0 | own origin | ref +x on both |
| spacerOnDrum | rigid | drum_shaft | seal_spacer | z 24 | own origin | |
| rotor2OnDrum | rigid | drum_shaft | rotor_2 | z 42 | own origin | |
| stackNutOnDrum | rigid | drum_shaft | stack_nut | z -18 | own origin | revision 1 (was z 62) |
| inletFrameOnCase | rigid | case_r1 | inlet_frame | z -18 | z -18 | flange plane |
| bellmouthOnFrame | rigid | inlet_frame | bellmouth | z -72 | z -72 | flange plane |
| stator1OnCase | rigid | case_r1 | stator_1 | z 18 | z 18 | flange plane |
| ogvOnCase | rigid | stator_1 | ogv_ring | z 58 | z 58 | bolted to the stator_1 rear flange (the casing stack) |
| noseOnInlet | rigid | inlet_frame | nose_cone | z -80 | own origin | hub front face |
| starterOnNose | rigid | nose_cone | starter | own z -28 (assembly -108) | z -108 | bulkhead front face |
| bearingFrontInHub | rigid | inlet_frame | bearing_front | z -72 | own origin | the drum journal turns in its bore |
| airFixed | rigid | case_r1 | air | origin | origin | |

All rest offsets and angles are zero and no joint has limits. No transmissions (single spool). Acceptance motion `spin`: rotorSpin over 0 ... 12.41 deg (one rotor-1 pitch, 360/29) in 12 steps, interference tolerance 0.05 mm3 per pair, default pairs (every rotating body against every stationary one; the closest are the 0.25 tip gaps, the 0.4 to 0.5 labyrinths and the line-to-line D25 journal in the bearing ring).

Clearances: from section 14.1, rotor1Tip (min 0.20), rotor2Tip (0.20), rotor1ToStator1 (3.9, see section 7), rotor1ToInletFrame (0.3), spacerSeal (0.4), sleeveSeal (0.4); added drumToInletFrame (min 1.0), stackNutToInletFrame (min 1.0, revision 1: the nut at r 28 against the inlet_frame kept outside r 30 behind z -35) and seat checks (max_gap 0.05) for every rigid interface: the four casing flange planes, the nose cone on the hub, the starter on the bulkhead, the bearing ring in the hub and on the journal, and the blisks, spacer and nut on the drum.

## 5. Fluid regions and named boundaries

Fluid volume `air` (body `air`, built in the assembly source): plenum cylinder r 150 over z -220 ... -95, the bellmouth interior, the inlet duct around the nose cone, hub and struts, and the compressor annulus to the outlet cap at z 90 (r 67.5 ... 90.25 over z 80 ... 90); seal cavities (under the stator inner bands, inside the fairing and the nose cone) excluded. Walls: bellmouth, inlet_frame, nose_cone, case_r1, stator_1, ogv_ring; minus: rotor_1, seal_spacer, rotor_2, drum_shaft. Caps: inletCap (0, 0, -220) normal -z, outletCap (0, 0, 90) normal +z. Seed (0, 0, -200), 35 mm ahead of the nose tip and 20 mm from the inlet cap. Volume 1.2e7 mm3 +/- 20 % (stated in 14.1); check: plenum pi 150^2 x 125 = 8.8e6, bellmouth and duct to z -18 about 1.9e6, compressor annulus about 1.3e6 after blade blockage, total about 1.2e7.

| boundary | role | body | selector | value |
|---|---|---|---|---|
| inlet | inlet | air | plane z -220, normal -z | area 70,686 mm2 (pi 150^2) +/- 2 % |
| outlet | outlet | air | plane z 90, normal +z | area 11,275 mm2 (pi (90.25^2 - 67.5^2), station 3 111 cm2) +/- 2 % |
| rotor1Wall | rotating_wall | air | touching rotor_1 | |
| rotor2Wall | rotating_wall | air | touching rotor_2 | |
| casingWall | wall | air | rest | plenum skin, bellmouth, inlet frame, nose cone, casings, vanes |
| rotor1Bore | fixed | rotor_1 | cylinder r 20 about z | the clamp of the CalculiX cases |

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| cold.speedRpm | 8,000 | rpm | stated | 14.1, split development |
| cold.flowLMin | 20,900 | L/min | stated | 14.1: 0.418 kg/s at 1.204 kg/m3 (2.30 kg/s x 8/44) |
| design.speedRpm | 44,000 | rpm | stated | 1, 14.1, split held_out, structural only |
| mrfCold fluidDensity | 1.204 | kg/m3 | stated | 14.1 |
| mrfCold fluidViscosity | 1.813e-5 | Pa s | stated | 14.1 |
| mrfCold settings | flow_key flowLMin, speed_key speedRpm, inlet D300, cell 6, surface level 3, 1500 iterations, 8 processes, timeout 36,000 s | - | stated | 14.1 |
| mrfCold regions tip1, tip2 | rotor_tip on rotor_1 / rotor_2: inside 1.0, outside 1.5, axial margin 3 | mm | stated | 14.1 |
| mrfCold ladder | factors 1.0, 0.8, 0.64, tip regions +1 on every level | - | stated, adjusted | 14.1; regions moved onto level 1 (section 7) |
| rotor_1.youngsModulus | 74.5e9 | Pa | stated | 14.1 (2618-T61) |
| rotor_1.poissonRatio | 0.33 | - | stated | 14.1 |
| rotor_1.density | 2760 | kg/m3 | stated | 14.1 |
| rotor1Stress settings | mesh 1.5 mm, fixed rotor1Bore, ladder 1.0 / 0.7 / 0.5 | - | stated | 14.1 |
| rotor1Modal settings | 6 modes, fixed rotor1Bore, mesh 1.5 mm, ladder 1.0 / 0.7 / 0.5 | - | modes stated; mesh and ladder defaulted | 14.1 states the modes only; mesh and ladder mirror rotor1Stress |
| dpCold | pressure_rise, static outlet minus inlet, steady | Pa | - | estimate about 2.9 kPa (class X, not a band) |
| torqueCold | torque, steady | N m | - | estimate about 1.5 N m: 215 kW x (8/44)^3 / 838 rad/s (not a band) |
| rotor1TipGrowth | max_displacement on rotor_1 at design, max 0.20 | mm | stated | 14.1 (expect 0.10 to 0.15) |
| rotor1Mode1 | natural_frequency_1, min 2,000 | Hz | stated | 13 step 7: first blade mode >= 2 kHz |

## 7. Defaults, open questions and unrepresentable features

Revision 1 (reviewer notes, approved by the design owner; supersedes the guide where they differ, each recorded as "Changed (revision 1, reviewer notes)" in the contract and the touched part contracts):
- Rotor stack loads from the front: drum shoulder D46 x 6 moved to z 62 ... 68 (rotor_2 rear stop), M39 thread (plain D39) to z -18 ... -8 behind a D36 neck z -40 ... -18, stack nut to z -18 ... -8 clamping rotor_1 (joint at drum z -18); the inlet_frame keeps outside r 30 behind z -35; clearance stackNutToInletFrame added.
- Casing flanges (case_r1, stator_1, ogv_ring front and rear, inlet_frame rear): OD 224 with 8 x D5.5 (M5 clearance) on PCD 212, one hole on +x, 45 deg pitch; an M5 head or nut at r 106 clears the ring wall and the rim by about 1.5 mm.
- Inlet struts: symmetric NACA 0020-type, 30 mm axial chord, 6 mm thick (the 12 % / 12 mm conflict is gone; blockage halves).
- Bellmouth: 6 mm quarter-round lip centred at (z -89, r 125), tangent to the ellipse and to the r 131 skin, part z -95 ... -72; 8 x M5 tapped blind holes from its rear face (D4.2 x 10), inlet_frame front flange 8 x D5.5 through, screws from behind.
- Air body: the bellmouth front moves from z -98 to -95 (the plenum still ends at z -95) and the struts thin; both change the air volume by well under 1 %, so the 1.2e7 mm3 +/- 20 % band and the envelope stand.

Resolved inconsistencies in the source (each also in the contract's `open_questions`):
- `rotor2ToOgv` (min_gap 4.0) cannot hold body to body: the rotor-2 rear sleeve runs 0.5 mm inside the OGV inner band. It is replaced by `sleeveSeal` (min 0.4); the 4 mm hub gap (rotor-2 trailing edge z 55 to the OGV band front face z 59) and the 6 mm blade-to-vane gap are part dimensions.
- `rotor1ToStator1` is exactly 4.0 by the stated geometry (rotor-1 rim to z 16, stator-1 inner band from z 20), so its min_gap is 3.9.
- The mrfCold ladder carries the tip regions on all three levels; the guide's bare 1.0 first level made step one both global and regional, which the ladder check rejects.
- Abradable liners are merged into case_r1 and stator_1 (finished bore D180.5), so the clearances and the CFD see the 0.25 mm cold tip gap rather than an open 0.5 mm recess.
- Drum bore D28 starts at z -30, not z -45 (z -45 would cut through the D25 journal, which ends at z -40).
- Stator labyrinth gap 0.5 (4.4) against 0.4 (8.1): 0.5 nominal, min_gap 0.4. OGV vanes z 61 ... 76 exceed the 14 mm chord: the leading edge stays at z 61.
- Cold flow 0.418 kg/s / 1.204 kg/m3 = 20,830 L/min; the stated 20,900 is used.

Inferred or defaulted (no source value): spool rotation positive about +z; casing flange thickness 6; OGV rear flange as the other casing flanges; OGV inner band front face z 59; rotor-2 front hub extension from z 41; inlet-frame front wall bore D40; seal-sleeve web ahead of z -19; bellmouth outer-skin profile; nose-cone screw pattern PCD 56 and starter pattern PCD 30; stack-nut notches 6 x 3; inlet turbulence intensity (adapter default 5 %); modal mesh and ladder; starter mass (catalog envelope only, no density).

Envelope: the contract envelope includes the derived air plenum ([-150, -150, -220] ... [150, 150, 262]); the solids alone span [-131, -131, -165] ... [131, 131, 262] (bellmouth skin r 131, nose tip z -165, drum flange z 262).

Not represented: the 10 um blisk interference fits and dowels, threads (plain cylinders), the bearing internals and their O-ring dampers, the nose nut and starter clutch, instrumentation (speed probes, taps, Kiel probe), the +x strut line passage and balance cuts. The cold MRF case is a geometry check; its result is not evidence until its mesh ladder resolves it. Hot-gas analyses belong to machine 2 and the analysis plan of section 13.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft (001) | assembly check ok | contract and brief drafted from section 14.1; 14 bodies, 13 joints, 2 cases, 3 simulations |
| asm-draft (002) | revision 1 | reviewer notes applied: front-loaded rotor stack, OD 224 casing flanges, 6 mm struts, tangent bellmouth lip with rear screws |
