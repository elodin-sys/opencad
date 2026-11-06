# axjet-c2-bearing_front — design brief

## 1. Intent and configuration

Front bearing pair of the AXJET-220 compressor module (assembly `axjet-c2`, body `bearing_front`): two 25 x 52 x 15 hybrid angular-contact bearings (Si3N4 balls, 15 deg contact, P4, back-to-back) modelled as one envelope ring. Own frame: axis +z through the origin, origin on the axis at the ring's front face (assembly z -72), x parallel to the assembly x. OD 52 sits line-to-line in the `inlet_frame` D52 H6 hub bore, ID 25 sits line-to-line on the `drum_shaft` D25 h5 journal, length 30 (z 0 ... 30 = assembly -72 ... -42), 0.5 x 45 deg chamfers on all four circular edges. The assembly places it with the rigid joint `bearingFrontInHub` at own-frame point [0, 0, 0], axis [0, 0, 1]. Authoritative source: the guide's section 14.1 body table (row `bearing-front`) and section 8.1 (front bearing and drum-shaft rows). Steel, 7800 kg/m3 (14.1 table). Single solid; no internal bearing geometry.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | 14.1 row `bearing-front`: ring OD 52, ID 25, length 30 (DB pair as one envelope ring), 0.5 mm chamfers, steel 7800, own origin at its front face (assembly z -72); 8.1: front bearing 2 x 25 x 52 x 15 hybrid, Si3N4, 15 deg, P4, back-to-back, O-ring squeeze-film damper; drum shaft D25 h5 journal z -75 ... -40; 14.1 `inlet-frame` row: hub bore D52 H6 z -75 ... -35 |

No images, drawings or reference meshes.

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| outer diameter (line-to-line in D52 H6 seat) | 52 | mm | intent; guide 14.1 bearing-front row | 0.01 | stated |
| inner diameter (line-to-line on D25 h5 journal) | 25 | mm | intent; guide 14.1 row; 8.1 drum shaft | 0.01 | stated |
| ring length (2 x 15 back-to-back) | 30 | mm | intent; guide 14.1 row | 0.01 | stated |
| chamfer, all four circular edges | 0.5 x 45 | mm x deg | intent; guide 14.1 row | 0.01 | stated |
| frame origin on the axis at the front face | assembly z -72 | mm | intent; guide 14.1 row | 0.05 | stated |
| z extent | 0 ... 30 (assembly -72 ... -42) | mm | intent | 0.05 | stated |
| x parallel to assembly x | - | - | intent | - | stated |
| joint `bearingFrontInHub` at [0, 0, 0], axis +z | - | - | orchestrator note | 0.05 | stated |
| material / density | steel, 7800 | kg/m3 | guide 14.1 row | - | stated |
| internal bearing geometry (races, balls, cage, split face) | not modelled | - | intent ("one envelope ring") | - | open |
| O-ring squeeze-film damper clearance and grooves (8.1) | not modelled | - | intent overrides (line-to-line) | - | open |

## 4. Coordinate frame, scale, and measurement method

Origin on the bearing axis at the ring's front face (the inlet side), which is assembly z = -72. +z runs along the rotor axis rearward (downstream), so the ring occupies z 0 ... 30 (assembly -72 ... -42). +x is parallel to the assembly +x (the +x inlet-strut direction), +y completes the right-handed frame. Datums: A = front face z = 0 (outward normal -z, the joint datum); B = bore axis (the z axis); C = D52 outer cylinder coaxial with B; D = rear face z = 30. All values are stated in text; no image scaling or mesh measurement was needed. The envelope is [-26, -26, 0] ... [26, 26, 30].

Construction intent for the modeller: revolve the chamfered rectangle (r 12.5 ... 26, z 0 ... 30) about z, or extrude the annulus from z = 0 to +ringLength and chamfer the four circular edges. Grow the ring from the front face toward +z so a ringLength edit never moves datum A. Asserts: `chamferSize > 0`, `2 * chamferSize < (outerDiameter - innerDiameter) / 2` (inner and outer chamfers on one end must not meet), `ringLength > 2 * chamferSize`, `innerDiameter > 0`, `outerDiameter > innerDiameter`.

Feasible intervals (other parameters at nominal): ringLength > 1.0 (swept over 15, 30, 45; infeasible delta -30 gives 0); chamferSize in (0, 6.75) (swept over 0.25, 0.5, 0.75; edit test to 1.0; infeasible deltas -1.0 and +7.0 give -0.5 and 7.5).

## 5. Measurement and inference record

Ro = outerDiameter/2 = 26, Ri = innerDiameter/2 = 12.5, L = ringLength = 30, c = chamferSize = 0.5.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| outerDiameter | 52 | 0.01 | stated | intent; guide 14.1 bearing-front row "ring OD 52" |
| innerDiameter | 25 | 0.01 | stated | intent; guide 14.1 row "ID 25"; 8.1 D25 h5 journal |
| ringLength | 30 | 0.01 | stated | intent "length 30 (z 0 ... 30)"; 14.1 row "length 30 (the DB pair as one envelope ring)" |
| chamferSize | 0.5 | 0.01 | stated | intent "0.5 x 45 deg chamfers on all four edges"; 14.1 row "0.5 mm chamfers" |
| volume | 48924.81 mm3 | rel 0.001 | derived | pi(Ro^2 - Ri^2)L - 2 pi c^2 (Ro + Ri) = 48985.28 - 60.48 (Pappus: each chamfer triangle c^2/2 at centroid radius Ro - c/3 or Ri + c/3; the c/3 terms cancel) |
| surface area | 10381.06 mm2 | rel 0.002 | derived | 2pi(Ro + Ri)(L - 2c) + 2pi((Ro - c)^2 - (Ri + c)^2) + 2pi c sqrt2 ((2Ro - c) + (2Ri + c)); 10522.76 without chamfers |
| centre of mass | (0, 0, 15) | 0.05 | derived | axisymmetric, equal chamfers both ends: on the axis at L/2 |
| mass | 0.3816 kg | - | derived | volume x 7800 kg/m3 |
| section mid_z (z 15) | 1632.84 mm2, 1 loop, 1 hole | rel 0.002 | derived | pi(Ro^2 - Ri^2) |
| sections front_chamfer (z 0.25), rear_chamfer (z 29.75) | 1572.37 mm2 | rel 0.005 | derived | pi((Ro - c + 0.25)^2 - (Ri + c - 0.25)^2) = pi(25.75^2 - 12.75^2); 1632.84 if unchamfered (3.7 % off) |
| section axial_x (x 0) | 809.0 mm2, 2 loops, 0 holes | rel 0.003 | derived | 2 x ((Ro - Ri)L - 4 c^2/2) = 2 x (405 - 0.5) |
| rearFace area (z 30) | 1511.89 mm2 | rel 0.005 | derived | pi((Ro - c)^2 - (Ri + c)^2) = pi(25.5^2 - 13^2) |
| frontFace (z 0, normal -z) | position only | 0.05 | stated | joint datum; area omitted so the chamferSize edit cannot break the pinned interface |
| cylinders bore / outerSeat | D25 hole / D52 pin, axis z | r 0.01, axis 0.02 | stated | line-to-line fits; lengths omitted (both edit tests change them) |
| dimensions | ringLengthDim 30 (frontFace to rearFace), spanX = spanY = 52 | 0.02 / 0.05 | stated | intent |
| edit ringLength +2 | dV = +3265.69 mm3, bbox +[0, 0, 2] | rel 0.02 | derived | pi(Ro^2 - Ri^2) x 2 (chamfers unchanged) |
| edit chamferSize +0.5 | dV = -181.43 mm3, bbox +[0, 0, 0] | rel 0.3 | derived | -2 pi (Ro + Ri)(1.0^2 - 0.5^2) = -57.75 pi |
| blockout band | 47500 ... 50500 mm3 | - | derived | plain annulus 48985.28 (envelope-only ring, bbox identical to the part) +- 3 %, also covering the chamfered 48924.81 |

Interfaces: `hubSeat` pins outerSeat, spanX, spanY; `journalBore` pins bore; `frontDatum` pins frontFace position. Neither edit test moves or resizes any of them.

## 6. Defaults retained

- `release_status: reconstruction` kept from the template (a design-guide part, not measured hardware).
- Envelope tolerance 0.05 mm and digital parameter tolerances 0.01 mm: template defaults, adequate for exact analytic BRep geometry.
- Volume tolerance_rel 0.001 (48.9 mm3): the checker's floor for derived values with chamfer features. It catches all four chamfers missing (60.5 mm3) but not one pair; the front_chamfer and rear_chamfer sections and the rearFace area catch partial chamfers.
- chamferSize edit-test band tolerance_rel 0.3: the checker's floor for blend features; the exact formula still separates it from an edit that moves only the outer chamfers (-120.7 mm3, outside -127.0 ... -235.9).

## 7. Unrepresentable or low-confidence features

- Bearing internals (inner and outer races, 15 deg contact geometry, Si3N4 balls, cage, the split face at z = 15 between the two bearings): not encoded; the intent asks for one envelope ring.
- O-ring squeeze-film damper (8.1: two Viton O-rings under the steel outer rings): implies a radial clearance and grooves; the intent's line-to-line OD overrides it.
- Fit tolerance bands (H6 bore, h5 journal, P4 rings): nominal diameters only.
- Real ring corner radii are replaced by the stated 0.5 x 45 deg chamfers.
- Mass is conservative (solid steel envelope 0.382 kg versus a hollow hybrid pair).
- Axial stack gaps (2 mm to the D25/D40 step at assembly z -40, 3 mm to the nose nut at z -75) are assembly-level and unresolved in the sources.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
