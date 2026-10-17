# planetary-set — assembly brief

## 1. Intent and configuration

A planetary gear set with a fixed ring, built from `sources/planetary-set-spec.md` (the only source; authoritative, text only). It has seven separate solids, not fused, made from five part designs:

- a 150 x 150 x 5 base plate (the datum);
- a 48-tooth internal ring, rigidly fixed on the plate;
- a 24-tooth sun and a D88 x 5 carrier, both turning about the common z axis;
- three identical 12-tooth planets (the design `planetary-set-planet`, placed three times) turning on the carrier at radius 36.

All gears are module 2, pressure angle 20 deg, zero profile shift. Every external tooth is thinned by 0.10 mm and every ring tooth space widened by 0.05 mm at the pitch circle, which gives a circular backlash of 0.20 mm at the three sun meshes and 0.15 mm at the three ring meshes.

At rest the sun, ring and carrier are at 0 deg and every planet is turned 15 deg, so all six meshes engage. The sun is motor-driven and the ring is held. Each planet follows the sun and the ring through two epicyclic meshes relative to the carrier, and the free carrier (the output) is set by those loops.

One motion sweep of the sun (one full mesh cycle, 22.5 deg) checks that the set turns with zero interference and a flank gap of at most 0.2 mm at the sun meshes. The evaluator measures two predictions from the placed geometry: the carrier ratio (carrier angle over sun angle, expected 1/3) and the carrier angle after one sun revolution (expected 120 deg).

The spec is purely kinematic. It has no operating cases, fluid regions, loads or physical simulations, so the contract declares none.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| `sources/planetary-set-spec.md` | text | authoritative | `2a8bca0f4ffa01692bc1a5879aeb8b02a1d728b2cbe39448f181197d86ca14ca` | parameter table (module, pressure angle, backlash, sun, planets, ring, carrier, base plate, planet orbit), frame and part frames, rest configuration, flank construction, motion, predictions |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| base | modelled | `planetary-set-base` | not stated | spec table, Base plate | datum; plate from (-75, -75, -5) to (75, 75, 0), D10 centre hole; top face z = 0 is the seat for the ring, the sun and the planets |
| ring | modelled | `planetary-set-ring` | not stated | spec table, Ring; flank paragraph | 48 internal teeth, pitch r 48, internal tip r 46, root r 50.5, outside r 58, face 10; involute flanks of base r 45.105; tooth spaces widened 0.05 mm; internal tooth on +x; rigidly fixed on the plate |
| sun | modelled | `planetary-set-sun` | not stated | spec table, Sun; flank paragraph | 24 teeth, pitch r 24, tip r 26, root r 21.5, base r 22.553, face 10, D10 bore; teeth thinned 0.10 mm; radial flank below the base circle, no fillet; tooth on +x; motor-driven |
| carrier | modelled | `planetary-set-carrier` | not stated | spec table, Carrier | D88 x 5 disc (own z 0..5, assembly z 10..15), D10 centre hole, three D8 holes on r 36 at 0/120/240 deg; planet hole on +x; free output |
| planet1 | modelled | `planetary-set-planet` | not stated | spec table, Planets; flank paragraph | 12 teeth, pitch r 12, tip r 14, root r 9.5, base r 11.276, face 10, D8 bore; teeth thinned 0.10 mm; radial flank below the base circle, no fillet; tooth on +x; on carrier hole (36, 0) |
| planet2 | modelled | `planetary-set-planet` | not stated | as planet1 | same design; on carrier hole (-18, 31.176915) |
| planet3 | modelled | `planetary-set-planet` | not stated | as planet1 | same design; on carrier hole (-18, -31.176915) |

No purchased or derived bodies: the spec has no shafts, pins, bearings, fasteners or fluid.

## 4. Frames, joints and motion

**Assembly frame.** The assembly frame is the base plate's own frame. The origin is on the common sun, ring and carrier axis, in the plate top face (z = 0). z points up along every gear axis. x points toward planet 1 at (36, 0), and y completes a right-handed frame. Datums: A is the plate top z = 0 (the ring, sun and planets stand on it); B is the axis x = y = 0; C is the carrier bottom face z = 10 (on the gear tops).

**Part frames.** The spec fixes these, and each part is drafted and modelled on its own:

- The ring, the sun, the planet and the carrier each have their axis along +z through their own origin and their bottom face at z = 0.
- In its own frame the sun has a tooth centred on +x, and so does the planet. The ring has an internal tooth centred on +x. The carrier has a planet hole centred on +x, at (36, 0).
- The base plate's own frame is the assembly frame.

**Joints.** They form a tree rooted at `base`. Frames are given in each body's own frame; every axis is +z and every ref is +x. No offsets are needed because the frame origins carry the axial positions. No limits are set: every rotation is continuous.

| joint | kind | parent → child | parent frame origin | child frame origin | rest angle | drive |
|---|---|---|---|---|---|---|
| `ringFixed` | rigid | base → ring | (0, 0, 0) | (0, 0, 0) | 0 deg | — |
| `sunSpin` | revolute | base → sun | (0, 0, 0) | (0, 0, 0) | 0 deg | motor, 10 rpm (defaulted; the spec states no speed) |
| `carrierSpin` | revolute | base → carrier | (0, 0, 10) | (0, 0, 0) | 0 deg | free (set by the planet loops) |
| `planet1Spin` | revolute | carrier → planet1 | (36, 0, -10) | (0, 0, 0) | 15 deg | free |
| `planet2Spin` | revolute | carrier → planet2 | (-18, 31.176915, -10) | (0, 0, 0) | 15 deg | free |
| `planet3Spin` | revolute | carrier → planet3 | (-18, -31.176915, -10) | (0, 0, 0) | 15 deg | free |

The planet frames sit 10 below the carrier's own origin because each planet's bottom face stands on the plate (assembly z = 0) while the carrier's bottom face is at z = 10. Each planet axis is at radius 36 = m (24 + 12) / 2 = m (48 - 12) / 2, at 0, 120 and 240 deg; for example 36 sin 120 deg = 31.176915.

**Phasing.** Why all six meshes engage at rest:

- **Sun.** Its teeth sit at k x 15 deg, so it has a tooth pointing at each planet (0, 120 and 240 deg are multiples of 15).
- **Ring.** Its internal teeth sit at k x 7.5 deg, so it also has a tooth pointing at each planet.
- **Planets.** Each planet is turned 15 deg, so its teeth sit at 15 + k x 30 deg. For planet 1 that puts a tooth space at 180 deg (toward the sun) and at 0 deg (toward the ring). Planets 2 and 3 get the same arrangement, because 120 and 240 deg are multiples of the 30 deg planet pitch.
- **Equal spacing.** The three planets can be spaced equally because (24 + 48) / 3 = 24 is an integer.

**Transmissions.** Each ratio is the driven displacement over the driver displacement, relative to the carrier (the carrier's joint is `carrierSpin`):

| transmission | driver → driven | ratio | mesh check | from the sources |
|---|---|---|---|---|
| `sunPlanet1`, `sunPlanet2`, `sunPlanet3` | `sunSpin` → `planetNSpin` | -2.0 | pitch 15 deg (sun), 12 steps, backlash ≤ 0.2 mm | -24/12: external mesh, opposite sense (spec, Motion: "opposite to the sun at 24/12") |
| `ringPlanet1`, `ringPlanet2`, `ringPlanet3` | `ringFixed` (rigid) → `planetNSpin` | +4.0 | none: a mesh sweep needs two rotating joints; the `sunTurn` sweep and the `ringPlanetNMesh` clearances cover these meshes | +48/12: internal mesh, same sense |

**Kinematics.** Write θs for the sun angle, θc for the carrier angle and θp for a planet's angle on the carrier. The two meshes give two equations:

- Sun mesh: θp = -2 (θs - θc).
- Ring mesh: θp = 4 (0 - θc).

Solving them gives θc = θs / 3, which matches the spec's 24 / (24 + 48). Then θp = -4 θs / 3 on the carrier, and each planet turns at -θs absolutely. When the sun turns one revolution (360 deg), the carrier turns 120 deg.

**Motion sweep.** The acceptance motion is `sunTurn`: `sunSpin` over 0..22.5 deg in 12 steps, covering one full mesh cycle of all six meshes. Over it:

- the carrier turns 7.5 deg, which is one ring pitch relative to the carrier;
- the sun turns 15 deg relative to the carrier, which is one sun pitch;
- each planet turns -30 deg on the carrier, which is one planet pitch.

The default pairs are checked: every pair in relative motion.

**Clearances.**

| clearance | pair | min gap | max gap | why |
|---|---|---|---|---|
| `sunPlanetNMesh` (x3) | sun, planetN | 0.0 | 0.2 | zero interference and a flank gap of at most 0.2 mm at the sun meshes (stated) |
| `ringPlanetNMesh` (x3) | ring, planetN | 0.0 | 0.2 | zero interference (stated); engagement bound inferred (design backlash 0.15 mm) |
| `carrierClearsRing` | carrier, ring | 1.9 | — | carrier rim at r 44 inside the ring tip circle at r 46: 2.0 mm, less 0.1 mm for tessellation |
| `ringSeat`, `sunSeat`, `planetNSeat` (x3) | body, base | 0.0 | 0.01 | stands on the plate top z = 0 (stated) |
| `carrierOnSun`, `carrierOnPlanetN` (x3) | carrier, body | 0.0 | 0.01 | carrier bottom face z = 10 lies on the gears (stated) |

**Envelope.** At rest the assembly spans (-75, -75, -5) to (75, 75, 15): the plate sets x, y and the bottom, the ring's outside radius 58 stays inside the plate, and the carrier top at z = 15 sets the top. `solid_count` is 7.

## 5. Fluid regions and named boundaries

None. The spec defines no fluid, loads, supports or thermal conditions, so there are no `fluid_volumes`, `boundaries` or derived bodies.

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| gearModule | 2 | mm | stated | spec table, Module |
| pressureAngle | 20 | deg | stated | spec table, Pressure angle |
| profile shift | 0 | — | stated | spec table, Profile shift (in the part intents) |
| sunTeeth / planetTeeth / ringTeeth | 24 / 12 / 48 | — | stated | spec table |
| faceWidth | 10 | mm | stated | spec table, face width 10 (z 0..10) |
| sunBacklash | 0.20 | mm | stated | spec table, Circular backlash: each external tooth thinned 0.10 mm at pitch |
| ringBacklash | 0.15 | mm | stated | spec table, Circular backlash: each ring tooth space widened 0.05 mm |
| planetOrbitRadius | 36 | mm | derived | gearModule x (sunTeeth + planetTeeth) / 2 = gearModule x (ringTeeth - planetTeeth) / 2 |
| carrierBottomZ | 10 | mm | stated | spec, Frame |
| planetRestAngle | 15 | deg | stated | spec, Rest configuration (half the 30 deg planet pitch) |
| sunPlanetRatio | -2 | — | derived | -sunTeeth / planetTeeth, relative to the carrier |
| ringPlanetRatio | +4 | — | derived | ringTeeth / planetTeeth, relative to the carrier |
| carrierRatio | 1/3 | — | derived | sunTeeth / (sunTeeth + ringTeeth) (spec, Motion) |
| sun mesh flank gap bound | 0.2 | mm | stated | spec, Motion: "a flank gap of at most 0.2 mm at the sun meshes" |
| ring mesh flank gap bound | 0.2 | mm | inferred | the spec states no ring bound; the design backlash is 0.15 mm, and 0.2 mm serves as an engagement check at rest in the `ringPlanetNMesh` clearances (open question) |
| observable `carrierRatio` | expected 0.333333333333 ± 1e-4 | — | derived | `transmission_ratio` with `body: carrier`, measured by the evaluator (no simulation) |
| observable `carrierAt360` | expected 120 ± 0.01 | deg | derived | `joint_value` of `carrierSpin` at `at: 360` (sun one revolution), measured by the evaluator (no simulation); 360 x 24 / 72 |
| sun drive speed | 10 | rpm | defaulted | the spec states no speed; the value only sets the animation's time scale (sun 60 deg/s, carrier 20 deg/s), and no prediction depends on it (open question) |

There are no operating cases, because the spec states none and both predictions are displacement ratios. There are no simulations, because both observables are kinematic and the evaluator measures them from the placed geometry.

## 7. Defaults, open questions and unrepresentable features

**Open questions** (the same as the contract's):

- The spec states no drive speed. The sun's motor drive carries a defaulted 10 rpm for the animation only, and neither prediction depends on it (both are displacement ratios).
- The spec states no materials or densities, so no mass or centre of mass is declared.
- The spec names no fastening between the ring and the plate. The ring is a rigid joint standing on the plate top (z = 0), concentric with the axis.
- The spec has no shafts, pins or bearings. The sun and the carrier turn about the common axis of their D10 holes, and each planet about its D8 bore (coaxial with a carrier hole), as kinematic joints only.
- The spec bounds the flank gap (0.2 mm) only at the sun meshes. The ring mesh clearances carry the same 0.2 mm bound as an engagement check at rest; their design circular backlash is 0.15 mm. The ring transmissions have no mesh sweep, because the ring is on a rigid joint; the `sunTurn` motion checks their interference over one full mesh cycle.
- The gears stand on the plate (z = 0) and carry the carrier (z = 10) face to face with no axial clearance, as specified. Those pairs touch with zero interference volume while they turn.
- After one sun revolution the carrier has turned 120 deg, which is one of its three-fold symmetry angles, so the posed set matches the rest pose with the planets permuted. The carrier angle must be tracked through the motion, not registered from the posed shape.

**Defaults and inferences.**

- The sun drive speed is 10 rpm, defaulted for the animation only.
- The ring-mesh engagement bound is 0.2 mm (clearance max_gap at rest).
- The carrier-to-ring minimum gap is 1.9 mm, derived from the dimensions.
- The seat bound is max_gap 0.01 mm, for faces the spec places in contact.
- The expected-value bands are 1e-4 on the ratio and 0.01 deg on the angle, both wider than 1e-5 of the value.
- The sun mesh sweeps and the `sunTurn` motion use 12 steps.

**Unrepresentable features.** The contract cannot state the involute flank construction or the backlash allowances as assembly geometry; they live in the ring, sun and planet part intents. The same goes for the radial flank continuation below the base circle, with no root fillet, which lets the ring's tips (r 46) reach within 0.5 mm of the planet root circle.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft | ok | `python -m opencad assembly check designs/.staging-planetary-set --name planetary-set` |
