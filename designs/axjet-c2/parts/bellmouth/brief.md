# axjet-c2-bellmouth — design brief

## 1. Intent and configuration

Bolt-on test bellmouth lip of the AXJET-220 two-stage compressor module (assembly `axjet-c2`, body `bellmouth`), modelled in the assembly frame. One turned 6061-T6 solid of revolution about z spanning z -95 ... -72 (revision 1): a quarter-ellipse inner (flow) contour from r 95.752 at the rear face to its front point r 125 at z -95, closed there by a 6 mm quarter-round lip centred at (z -89, r 125) that is tangent to the ellipse and to the outer skin (no crease), a conical outer skin from r 131 at z -89 back to the flange OD edge, and a 5 mm rear flange (OD 224) with 8 x M5 tapped blind holes from the rear face on PCD 216 (one on +x), modelled as D4.2 tap-drill holes 10 deep. The M5 screws enter from behind the inlet-frame front flange, which carries 8 x D5.5 through holes. The rear face z -72 seats on the inlet-frame front flange (rigid joint `bellmouthOnFrame`, own-frame point [0, 0, -72], axis +z). Authoritative source: `sources/axjet_design_and_implementation_guide.md` (sections 2.4, 3, 3.2, 9, 11, 14.1), as amended by the revision 1 reviewer notes (change 4).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | mm; section 3 frame, 3.2 flow-path table (r 125 at z -95, r 95.8 at z -72), 2.4 inlet flange (OD 224, PCD 216), 9 inlet (ellipse to r 90.25 at z -45), 11 material, 14.1 bellmouth row (skin from r 131); the lip and the fastener scheme follow the revision 1 reviewer notes |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| axial extent | z -95 ... -72 | mm | revision 1 change 4 (guide 9, 14.1: z -98 ... -72) | 0.05 | stated (revision) |
| inner contour | quarter-ellipse centre (z -45, r 125), semi-axes 50 / 34.75 | mm | 9, 3.2 | 0.01 | stated |
| inner radius at the lip vertex z -95 | 125, radial tangent | mm | 3.2 | 0.01 | stated |
| inner radius at the rear face z -72 | 95.752 (text 95.8) | mm | 3.2, 2.4 | 0.06 | derived |
| lip | 6 mm quarter-round centred at (z -89, r 125), tangent to the ellipse at (z -95, r 125) and to the skin at (z -89, r 131) | mm | revision 1 change 4 (guide 14.1: 3 mm rounded lip) | 0.01 | stated (revision) |
| outer skin start | r 131 at z -89 | mm | 14.1 (r 131), revision 1 (station) | 0.01 | stated |
| outer skin profile | straight cone to (z -77, r 112) | mm | none | volume | inferred |
| rear flange | z -77 ... -72, OD 224 | mm | 2.4, 14.1 | 0.5 (thickness) | OD stated, thickness inferred |
| bolt holes | 8 x M5 tapped blind from the rear face, D4.2 x 10 deep, PCD 216, one on +x, 45 deg pitch | mm | revision 1 change 4 (guide 14.1: 8 x D5.5) | 0.02 | stated (revision; pitch assumed) |
| rear seat face | z -72, r 95.752 ... 112 | mm | 2.4 | 0.05 | stated |
| contour continuity | no step to the inlet-frame contour at z -72 | mm | 9 | 0.035 (area) | stated |
| material | 6061-T6, 2700 kg/m3 | - | 11, 14.1 | - | stated |

## 4. Coordinate frame, scale, and measurement method

Assembly frame of guide section 3: origin on the engine axis at the stage-1 rotor leading-edge plane; +z along the axis in the flow direction; +x up toward the dorsal intake; +y completes a right-handed frame. Radii are measured from the axis. Datum A is the rear face z -72 (joint `bellmouthOnFrame` at [0, 0, -72], axis +z), datum B the axis, datum C the +x bolt hole. No images or meshes were supplied; every value is read from the text, the tables and the revision 1 notes, so no pixel scaling was needed. The (z, r) profile is a closed loop: ellipse arc (z -72, r 95.752) -> (z -95, r 125); quarter circle centre (z -89, r 125), R6, from (z -95, r 125) to (z -89, r 131); straight line to (z -77, r 112); line to (z -72, r 112); line back to the start. Revolve 360 deg about z, then cut 8 x D4.2 holes from z -72 to a flat floor at z -82 (4.3 mm of wall to the flow contour and 9.8 mm under the skin at the floor).

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| ellipseCenterZ | -45 | 0.01 | stated | section 9 |
| ellipseCenterR | 125 | 0.01 | stated | sections 3.2, 9 |
| ellipseAxialSemiAxis | 50 | 0.01 | stated | section 9 (z -95 ... -45) |
| ellipseRadialSemiAxis | 34.75 | 0.01 | stated | section 9 (r 125 ... 90.25) |
| lipVertexZ | -95 | 0.01 | derived | ellipseCenterZ - ellipseAxialSemiAxis |
| lipRadius | 6 | 0.01 | stated | revision 1 change 4 (was 3) |
| lipFrontZ | -95 | 0.01 | derived | lipVertexZ (the lip is tangent to the ellipse at its vertex) |
| skinStartZ | -89 | 0.01 | derived | lipVertexZ + lipRadius |
| skinStartRadius | 131 | 0.01 | derived | ellipseCenterR + lipRadius (matches the stated r 131) |
| rearFaceZ | -72 | 0.01 | stated | sections 2.4, 3.2 |
| flangeThickness | 5 | 0.5 | inferred | mating inlet-frame flange is z -72 ... -67 (5 thick) |
| flangeFrontZ | -77 | 0.01 | derived | rearFaceZ - flangeThickness |
| flangeOuterDiameter | 224 | 0.01 | stated | sections 2.4, 14.1 |
| boltCircleDiameter | 216 | 0.01 | stated | sections 2.4, 14.1 |
| boltHoleDiameter | 4.2 | 0.01 | stated | revision 1 change 4: M5 tapped, modelled at the ISO tap-drill size (was D5.5) |
| boltHoleDepth | 10 | 0.05 | stated | revision 1 change 4 |
| boltCount | 8 | 0.01 | stated | sections 2.4, 14.1 |
| boltStartAngle | 0 deg | 0.1 | stated | one hole on +x |
| rearInnerRadius | 95.752 | 0.06 | derived | 125 - 34.75 sqrt(1 - (27/50)^2) |
| volume | 280229 | 0.5 % | derived | pi Int(r_o^2 - r_e^2) dz over z -95 ... -72, integrated numerically with r_o the quarter-round lip, the cone and the flange = 281337.6; minus 8 holes pi 2.1^2 10 = 1108.4 |
| surface area | 66730 | 2 % | derived | ellipse 26763 (Simpson on 2 pi r ds), lip 2 pi (125 + 12/pi) (3 pi) = 7628, cone 2 pi 121.5 sqrt(12^2 + 19^2) = 17155, flange OD 3519, rear face 10494, hole walls 1056, floors 111 |
| centre of mass | (0, 0, -84.05) | 0.15 | derived | first moment of the same numerical integration, holes at z -77 |
| section lipSection z -93 | 10919.7 | 1 % | derived | pi (129.472^2 - 115.270^2) |
| section skinMid z -83 | 13425.2 | 0.5 % | derived | pi (121.5^2 - 102.415^2) |
| section flangeMid z -74.5 | 9772.9 | 0.5 % | derived | pi (112^2 - 96.943^2) - 8 pi 2.1^2 |
| face rearFace z -72 | 10493.8 | 0.2 % | derived | pi (112^2 - 95.752^2) - 8 pi 2.1^2; 0.2 % pins the inner radius to about 0.035 mm |
| spanZ / spanX | 23 / 262 | 0.05 | derived | lip front to rear face; 2 skinStartRadius |
| blockout band | 264000 ... 298000 | - | derived | unholed profile 281338, about +/- 6 % |

Edit tests. `lipRadius` +0.5 (feasible 0 < lipRadius < 18, where the skin would start at the flange front; sweep 5.5, 6.0, 6.5; delta -6 gives 0 and must fail an assert): the lip centre moves to z -88.5 and the skin starts at r 131.5, volume +7541 by the same numerical integration; bbox +1 in x and y (r max 131.5), 0 in z (the front stays at the ellipse vertex z -95). `flangeThickness` +1 (feasible 0 < flangeThickness < 12): the flange band gains while the cone from z -89 lands 1 mm further forward, volume -7063; the hole depth is its own parameter, so the holes do not change; bbox unchanged. Neither edit moves the rear face, the flange OD radius, the hole axes or the z -74.5 section, which pin the interfaces; the pinned cylinders carry no length for that reason.

## 6. Defaults retained

- Envelope and acceptance tolerance 0.05 mm (template default); adequate for a turned part whose stated values are given to 0.05 mm or better.
- Symmetry band 0.1 / 0.05 mm about y = 0 (exemplar default); the part is exactly symmetric (axisymmetric with an 8-hole pattern clocked on +x).
- `release_status: prototype`: the guide is a new engine design, not a reconstruction of existing hardware.
- Tapped holes at the ISO tap-drill diameter (M5 x 0.8 as D4.2); the thread is cosmetic.

## 7. Unrepresentable or low-confidence features

- Changed (revision 1, reviewer notes): the 6 mm quarter-round lip removes the 90 deg concave crease that the stated R3 lip left against the ellipse's radial tangent, and the tapped holes from the rear replace the D5.5 holes that no screw could reach through the solid lip.
- Outer skin profile is inferred as a straight cone from the lip tangent point; it meets the lip with a convex kink on the outside (open question).
- Flange thickness 5 is inferred from the mating flange.
- Thread, chamfers, edge breaks, surface finish and the bellmouth delta-p taps of section 10 are not described dimensionally and are not modelled.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
