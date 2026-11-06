# axjet-c2-stack_nut — design brief

## 1. Intent and configuration

Stack nut of the AXJET-220 compressor module (assembly `axjet-c2`, body `stack_nut`). Revision 1 (reviewer notes): it passes over the drum's D36 neck, threads onto the M39 x 1.5 section at assembly z -18 ... -8 and clamps the rotor stack (blisk 1, seal spacer, blisk 2) from the front against the drum's D46 shoulder at z 62: its rear face (assembly z -8) seats on the rotor_1 disc front face. Geometry (unchanged): ring OD 56, ID 39 (thread modelled as a plain D39 bore on the drum's plain D39 thread section), length 10, six parallel-sided spanner notches in the OD (6 wide x 3 deep, through the length, one centred on +x, 60 deg pitch). The OD (r 28) sits 16 mm inside the rotor_1 seal arm (r 44, assembly z -18 ... -8) and 2 mm inside the inlet_frame keep-out (r 30); the tool enters axially from the front through the seal arm. Material 17-4PH H1025, 7800 kg/m3. Authoritative source: `sources/axjet_design_and_implementation_guide.md`, sections 8.1 and 14.1. The assembly places the nut by joint `stackNutOnDrum` (rigid) at own point [0, 0, 0], axis [0, 0, 1].

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | section 3: assembly frame (z downstream, x up); 8.1: drum thread M39 x 1.5 at z 62 ... 72, stack nut z 62 ... 72 behind blisk 2; 14.1: stack-nut row (OD 56, ID 39, length 10, 6 spanner notches, 17-4PH), rotor-2 row (disc to assembly z 62, sleeve OD 126 x ID 60 at z 62 ... 70), drum-shaft row (17-4PH, 7800), joint stackNutOnDrum at z 62 |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| outside diameter | 56 | mm | 14.1 stack-nut row | 0.01 | stated |
| bore (M39 x 1.5 as plain bore) | 39 | mm | 14.1 stack-nut row; 8.1 drum thread | 0.01 | stated |
| length, own z 0 ... 10 (assembly -18 ... -8) | 10 | mm | 14.1 stack-nut row; revision 1 | 0.01 | stated |
| spanner notches | 6 | – | 14.1 stack-nut row | exact | stated |
| notch pitch | 60 | deg | intent (equal spacing) | 0.01 | derived |
| notch clocking, one on +x | 0 | deg | intent | 0.5 | inferred |
| notch width | 6 | mm | intent (marked inferred) | 0.5 | inferred |
| notch depth | 3 | mm | intent (marked inferred) | 0.5 | inferred |
| rear face clamps the rotor_1 disc front face | own z 10 = assembly z -8 | mm | revision 1 change 1 | 0.05 | stated (faces `front`, `rear`, dimension `length`, interface `clampFace`) |
| OD 16 mm inside the rotor_1 seal arm (r 44) | gap 16.0 | mm | revision 1, rotor_1 intent | min 15.9 | derived (hardware `rotor1SealArm`, clearance `armGap`, cylinder `od`) |
| joint frame | point [0,0,0], axis +z | – | 14.1 joints | – | stated (interfaces `clampFace`, `threadBore`) |
| material / density | 17-4PH H1025, 7800 | kg/m3 | 14.1 (drum-shaft, coupling-hub rows) | – | stated for the material |

## 4. Coordinate frame, scale, and measurement method

Own frame per the intent and joint `stackNutOnDrum`: origin on the nut axis at the front face, assembly point (0, 0, -18); +z along the engine axis downstream (flow direction), so the rear (clamp) face is z = 10 and assembly z = own z - 18; +x parallel to the assembly x (engine up), with one notch centred on +x; +y completes the right-handed frame. Datums: A = front face z = 0 (outward normal -z), B = the z axis (bore and OD axis), C = plane y = 0 through the +x notch centre. No images, drawings or reference meshes: every value is read from the guide's text tables (no scaling or rectification). Notch geometry convention: each notch is the region within notchWidth/2 of its radial centreline and beyond radius outerDiameter/2 - notchDepth along it (flat floor perpendicular to the centreline at r 25), through the full length. The +x notch walls meet the OD at x = sqrt(28^2 - 3^2) = 27.8388, which sets the bbox x extent; the y extent is the un-notched OD at 90/270 deg (±28).

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| outerDiameter | 56 mm | 0.01 | stated | 14.1 stack-nut row "ring OD 56" |
| boreDiameter | 39 mm | 0.01 | stated | 14.1 "ID 39"; revision 1: thread M39 x 1.5 at assembly z -18 ... -8 |
| nutLength | 10 mm | 0.01 | stated | 14.1 "length 10"; revision 1: nut at assembly z -18 ... -8; no edit test (it would move the clamp face) |
| notchCount | 6 | 0.01 | stated | 14.1 "6 spanner notches" |
| notchPitch | 60 deg | 0.01 | derived | 360 / notchCount |
| notchPhase | 0 deg | 0.5 | inferred | intent: one notch centred on +x; guide's "one on +x" pattern convention |
| notchWidth | 6 mm | 0.5 | inferred | intent value; guide silent |
| notchDepth | 3 mm | 0.5 | inferred | intent value; leaves a 5.5 mm ligament to the bore |
| notch area Anotch | 17.678 mm2 | – | derived | a*sqrt(R^2 - a^2) + R^2*asin(a/R) - w*(R - d), R 28, a 3, w 6, d 3 |
| section area (mid, z 5) | 1162.350 mm2 | 0.5 % | derived | pi/4*(56^2 - 39^2) = 1268.418 minus 6 * 17.678 = 106.068; 1 loop, 1 hole |
| section cutXZ (y 0) | 110 mm2 | 1 % | derived | 2 * (25 - 19.5) * 10, 2 loops |
| section cutYZ (x 0) | 170 mm2 | 1 % | derived | 2 * (28 - 19.5) * 10, 2 loops |
| volume | 11623.50 mm3 | 0.3 % | derived | 1162.350 * 10 (mass 90.7 g at 7800 kg/m3) |
| surface area | 5649.18 mm2 | 1 % | derived | 2 * 1162.350 + pi*39*10 (1225.221) + OD arcs (2*pi*28 - 12*28*asin(3/28))*10 (1398.600) + 6 * (60 + 2 * 28.388) (700.659) |
| centre of mass | (0, 0, 5) | 0.05 | derived | six-fold symmetry about z, prismatic in z |
| bbox | x ±27.8388, y ±28, z 0 ... 10 | 0.05 | derived | x limited by the ±x notch walls: sqrt(28^2 - 3^2) |
| notch floors | r 25, area 60 each | 2 % | derived | 28 - 3; 6 * 10; faces at x ±25, planes at 60/120/240/300 deg |
| notch walls (+x notch) | y ±3, area 28.388 each, centre x 26.4194 | 2 % | derived | (27.8388 - 25) * 10 |
| edit notchDepth +1 | dV -360, bbox 0 | 2 % | derived | -6 * notchWidth * 1 * nutLength (the strip r 24 ... 25 lies inside the OD); sweep [2, 3, 4, 5] in the feasible interval 0 < notchDepth < (56 - 39)/2 = 8.5; infeasible delta +6 (depth 9 cuts into the bore and splits the ring) |
| edit notchWidth +2 | dV -333.46, bbox x -0.2520 | 3 % | derived | -6 * (Anotch(8) 23.236 - Anotch(6) 17.678) * 10; x extent 2*sqrt(28^2 - 4^2) - 2*sqrt(28^2 - 3^2); feasible 0 < notchWidth < 2*sqrt(28^2 - 25^2) = 25.2 |
| blockout band | 11300 ... 12800 mm3 | – | derived | notched ring 11623.5 up to the plain ring trimmed to |x| <= 27.8388 (12671.3); a plain D56 ring (x ±28) overshoots the envelope x by 0.16 |
| seal-arm clearance | min gap 15.9 (nominal 16.0) | – | derived | 44 - 28 against hardware cylinder r 48.1 minus r 44, own z 0 ... 10 (revision 1) |

## 6. Defaults retained

- `release_status: reconstruction` and units mm/deg from the template.
- Envelope tolerance 0.05 mm and stated-parameter tolerance 0.01 mm: digital thresholds for exact analytic geometry, not manufacturing tolerances.
- Inferred notch dimensions carry a wide 0.5 mm (0.5 deg for clocking) tolerance; every probe sits at least 1.5 mm from a notch floor or wall.
- Process "turning, notches milled" is nominal (the guide's manufacturing table covers the drum shaft and other 17-4PH turned parts, not the nut by name).

## 7. Unrepresentable or low-confidence features

- M39 x 1.5 internal thread: modelled as a plain D39 bore (line-to-line with the drum's plain D39 section); thread form, minor diameter and thread-start chamfer are omitted.
- Spanner notch width, depth, form and clocking are inferred (the guide only says "6 spanner notches").
- Tool access (revision 1): the nut sits inside the rotor_1 seal arm with 16 mm radial room; a slotted socket enters axially from the front before the front bearing pair and the inlet_frame are fitted.
- Changed (revision 1, reviewer notes): the nut moved from assembly z 62 ... 72 to z -18 ... -8 and clamps rotor_1 with its rear face; geometry unchanged, nutLength edit test withdrawn.
- No locking feature, edge breaks or chamfers are stated; none are modelled.
- Interface pins avoid items that edit tests move: `front` has no area (notch edits change it), `bore` and `od` have no length.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
