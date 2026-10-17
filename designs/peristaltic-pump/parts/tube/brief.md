# peristaltic-pump-tube — design brief

## 1. Intent and configuration

Silicone peristaltic tube of the Behrens et al. open-source 3D-printed peristaltic pump (Sci. Rep. 10, 1543, 2020):
3.0 mm OD, 1.0 mm ID (1.0 mm wall), durometer 50 A, lying uncompressed in the 3 mm stator track. It is the body `tube`
of the assembly `peristaltic-pump`, placed by the rigid joint `tubeSeat` at its own-frame point [0, 0, 0], axis
[0, 0, 1]. Centreline: a 180 deg arc of radius 10.67 about the pump axis through +x, from (0, -10.67) to (0, 10.67),
continued by two straight legs along -x from x = 0 to x = -30 (through the stator's tube slots and under the clamp).
Open ends at x = -30: inlet at y = +10.67, outlet at y = -10.67. Constant annular section, no fittings, one solid.
Authoritative: the user intent (all dimensions) and `sources/behrens-pump-packet.md` (tubing sizes); the stator STEP is
the origin of the 12.17 mm track radius.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/behrens-pump-packet.md | text | authoritative | bdab3462725e | tubing 3 mm OD / 1 mm ID, 50 A; test condition 108 rpm, water |
| sources/6.1-peristaltic-pump-stator-3mm.step | cad | authoritative | 6b531c2802d6 | stator track (radius 12.17 mm after x10) and tube slots; STL units cm |
| sources/8-peristaltic-pump-clamp.step | cad | illustrative | f948d46506a7 | clamp over the legs; context only |
| sources/7.1-peristaltic-pump-lid-3mm.step | cad | illustrative | a1a12d254562 | lid for the 3 mm tube; context only |
| sources/9-peristaltic-pump-rotor.step | cad | illustrative | 996c2325ecae | rotor and roller pins; context only |
| sources/1-gear-box-base.step | cad | illustrative | d63eaba9c1df | gearbox base; assembly context |
| sources/2-small-gear-with-shelf.step | cad | illustrative | 943cf69986d0 | motor gear; assembly context |
| sources/3-stacked-gear.step | cad | illustrative | 971d50c72c09 | stacked gear; assembly context |
| sources/4-gear-box-upper-case.step | cad | illustrative | 41f6a7878274 | gearbox upper case; assembly context |
| sources/5-large-gear.step | cad | illustrative | 47a710ed2061 | output gear; assembly context |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| outer diameter | 3.0 | mm | intent; packet | 0.01 | stated |
| inner diameter | 1.0 | mm | intent; packet | 0.01 | stated |
| wall | 1.0 | mm | intent '(wall 1.0)' = (OD - ID) / 2 | 0.01 | stated |
| durometer | 50 A | - | intent; packet | - | stated (material note only) |
| track radius (outer surface touches it) | 12.17 | mm | intent (stator STEP x10) | 0.01 | stated |
| bend centreline radius | 10.67 | mm | trackRadius - OD / 2 | 0.01 | derived |
| bend angle, through +x | 180 | deg | intent | 0.01 | stated |
| leg length along -x (x = 0 to -30) | 30 | mm | intent | 0.01 | stated |
| inlet end (x = -30, y = +10.67), outlet end (x = -30, y = -10.67) | - | mm | intent | 0.05 | stated |
| constant section, open ends, no fittings, uncompressed | - | - | intent | - | stated |
| frame: origin on pump axis in mid-plane, +z pump axis, +x open side | - | - | intent; joint tubeSeat | - | stated |
| density | - | kg/m3 | not given | - | open |

## 4. Coordinate frame, scale, and measurement method

Own frame from the intent (the assembly places the tube by it): origin on the pump axis at the centre of the bend,
in the tube's mid-plane; +z along the pump axis; +x toward the pump's open side (bend apex at x = +10.67); +y
completes the right-handed frame, so the inlet leg is at y = +10.67 and the outlet leg at y = -10.67. Datums: A = mid-plane
z = 0, B = pump axis (z axis), C = mirror plane y = 0. The part is mirror-symmetric about y = 0 and z = 0 by
construction. No image or mesh was measured for dimensions: every length is stated in the intent. The stator STEP is in
the published STL units (cm; the assembly places it at scale 10); its file axes differ from this frame (bounding box
x -5.1..0, y 0.5..3.7, z -4.1..0 cm, stator axis along file y through (x, z) = (-2.05, -2.05) cm). A cross-check slice
normal to file y at y = 1.2, 2.1 and 3.0 cm put the track polygon vertices at r = 1.2139-1.2150 cm, i.e. 12.14-12.15 mm,
0.02-0.03 mm inside the stated 12.17; the stated value is kept and the gap is an open question.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| tubeOuterDiameter | 3.0 mm | 0.01 | stated | intent 'OD 3.0'; packet '3 mm OD' |
| tubeInnerDiameter | 1.0 mm | 0.01 | stated | intent 'ID 1.0'; packet '1 mm ID' |
| trackRadius | 12.17 mm | 0.01 | stated | intent 'track radius 12.17' (stator STEP x10) |
| centrelineRadius | 10.67 mm | 0.01 | derived | trackRadius - tubeOuterDiameter / 2 = 12.17 - 1.5 |
| bendAngle | 180 deg | 0.01 | stated | intent '180 deg arc' from -90 to +90 deg through +x |
| legLength | 30 mm | 0.01 | stated | intent 'from x = 0 to x = -30' |
| annulus area A | 6.28319 mm2 | - | derived | pi/4 (3.0^2 - 1.0^2) = 2 pi |
| centreline length L | 93.52079 mm | - | derived | pi * 10.67 + 2 * 30 |
| volume | 587.608 mm3 | rel 0.002 | derived | A * L (Pappus; annulus centroid on the centreline) |
| surface area | 1187.783 mm2 | rel 0.01 | derived | pi (3.0 + 1.0) L + 2 A |
| centre of mass | (-7.1754, 0, 0) | 0.05 | derived | x = [2 (R^2 A + pi/4 (1.5^4 - 0.5^4)) - 15 * 2 A * 30] / V = (1438.521 - 5654.867) / 587.608 |
| envelope | [-30, -12.17, -1.5] .. [12.17, 12.17, 1.5] | 0.05 | derived | x: -legLength .. trackRadius; y: +-trackRadius; z: +-OD/2 |
| section midPlane (z = 0) | 187.042 mm2, 2 loops, 0 holes | rel 0.01 | derived | 2 * wall * L; the bore splits it into inner and outer U strips |
| section legs (x = -15) | 12.566 mm2, 2 loops, 2 holes | rel 0.01 | derived | 2 A |
| section apex (y = 0) | 6.283 mm2, 1 loop, 1 hole | rel 0.01 | derived | A |
| faces inlet / outlet (x = -30, normal -x) | 6.283 mm2 each, centres (y, z) = (+-10.67, 0) | rel 0.01 | derived | A |
| cylinders inletOuter / outletOuter | pin r 1.5, axis y = +-10.67, z = 0, along x | 0.01 | stated | OD / 2; no length so the leg-length edit keeps them pinned |
| cylinders inletBore / outletBore | hole r 0.5, t 0..30 from x = -30 | 0.01 / 0.05 | stated | ID / 2, legLength |
| spanX / spanY / spanZ | 42.17 / 24.34 / 3.0 mm | 0.05 | derived | legLength + trackRadius; 2 trackRadius; OD |
| wall thickness | min 0.9 (p05) | - | derived | (OD - ID) / 2 = 1.0 less tessellation allowance |
| symmetry mirrorY, mirrorZ | max 0.1, p95 0.05 | - | derived | inlet/outlet legs mirror about y = 0; circular section centred on z = 0 |
| blockout band | 570 .. 690 mm3 | - | derived | covers the tube (587.6) and the solid U rod pi 1.5^2 L = 661.1 |
| edit tubeInnerDiameter -0.2 | dV = +26.442, bbox 0 | rel 0.02 | derived | (pi/4 (3.0^2 - 0.8^2) - A) * L = 0.28274 * 93.52079 |
| edit legLength +5 | dV = +62.832, bbox [5, 0, 0] | rel 0.02 | derived | 2 A * 5 |

Edit feasibility: tubeInnerDiameter is feasible on 0 < ID < OD = 3.0 (sweep 0.8, 1.0, 1.2; infeasible deltas +2.5 ->
ID 3.5 > OD and -1.0 -> ID 0, both refused by sanity asserts). legLength is feasible on legLength > 0 (sweep 20, 30, 40;
infeasible delta -35 -> -5). Neither edit moves the tubeSeat checks (mirrorY, mirrorZ, spanY, spanZ, inletOuter,
outletOuter). Suggested construction: revolve the annulus 180 deg about z (bend) and add two straight tubes along -x
(legs) as one fused solid, or sweep the annulus along the U centreline; both give analytic cylinder and torus faces.

## 6. Defaults retained

- `export_volume_tolerance_rel: 0.02`: the 0.5 mm bore tessellates coarsely in STL, so KCL/STEP/STL agreement is
  loosened to 2 % (the STEP volume itself is held to 0.2 %).
- Section and face area tolerances 1 %, cylinder radius 0.01 mm and envelope 0.05 mm: exact analytic geometry.
- Symmetry bands 0.1 / 0.05 mm follow the exemplar defaults.
- `density_kg_m3: null`: not stated; no mass claim is made.

## 7. Unrepresentable or low-confidence features

- The tube is uncompressed: roller occlusion, stretch over the rollers and the clamp squeeze are not modelled.
- The real tube continues past the clamp to fittings; the model stops at x = -30 as the intent states.
- No void probe or passage inside the bore: its 0.5 mm radius cannot hold a point 1 mm from the wall. Bore patency is
  pinned by the midPlane section (two separate strips end to end), the legs/apex section holes and the bore cylinders.
- Silicone density (typically 1100-1200 kg/m3) is unknown.
- Track radius: the stated 12.17 mm is 0.02-0.03 mm larger than the stator STEP track vertices measured at three
  heights (12.14-12.15 mm); the tube may overlap the track by up to 0.03 mm in the assembly.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
