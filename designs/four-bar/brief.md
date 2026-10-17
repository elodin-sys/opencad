# four-bar — assembly brief

## 1. Intent and configuration

A planar crank-rocker four-bar linkage built as four separately designed solids (no fused bodies): a ground plate and three
stadium links, the crank (40 between hole centres), the coupler (100) and the rocker (80). Each part is drafted and modelled in
its own frame as the specification states. Four revolute pins about +z join them into one closed loop. Three pins (O2, A, O4)
form the joint tree from the ground, and the fourth (B) is the loop's closing joint. The crank at O2 is motor-driven through one
full revolution from the open rest configuration; the rocker swings back and forth. The only source is
`sources/four-bar-spec.md` (text, authoritative); there are no drawings, images or CAD files.

The linkage satisfies Grashof with the crank as the shortest link: 40 + 100 = 140 <= 180 = 100 + 80, so the crank turns fully.
The layers keep the links apart except at their pins: ground z -5..0, crank 0..5, coupler 5..10, rocker 10..15.

Rest configuration (assembly frame, angles about +z):

| link | rest angle | holes at rest |
|---|---|---|
| crank | 0 deg | O2 (0, 0), A (40, 0) |
| coupler | 53.130102 deg (atan2(80, 60), exactly 53.13010235415598) | A (40, 0), B (100, 80) |
| rocker | 90 deg from O4 | O4 (100, 0), B (100, 80) |

The triangle A, O4, B has sides 60, 80 and 100, with its right angle at O4. The machine is kinematic only: there are no operating
cases, loads, fluids or simulations. Every prediction is measured by the evaluator from the placed geometry over the crank
revolution.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/four-bar-spec.md | text | authoritative | aececd85a2ba8a2e020775f05a44f1bd1c3a505c8c8c5ed634606d975490bf17 | link table, layers, part frames, rest configuration, pins, coupler point P, motion, predictions |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| ground | modelled | four-bar-ground | not stated | spec table, Ground | plate 160 x 60 x 5, corner (-30, -30, -5) to (130, 30, 0); Ø6 through holes at O2 (0, 0) and O4 (100, 0); datum part, frame = assembly frame |
| crank | modelled | four-bar-crank | not stated | spec table, Crank | stadium 5 thick, 16 wide, R8 ends on Ø6 holes at (0, 0) and (40, 0); layer z 0..5 |
| coupler | modelled | four-bar-coupler | not stated | spec table, Coupler | stadium as the crank, Ø6 holes at (0, 0) and (100, 0); layer z 5..10; carries the reference point P (50, 30) |
| rocker | modelled | four-bar-rocker | not stated | spec table, Rocker | stadium as the crank, Ø6 holes at (0, 0) and (80, 0); layer z 10..15 |

There are four solids (`acceptance.solid_count: 4`) and no purchased or derived bodies. The pins are joints only; they are not bodies.

## 4. Frames, joints and motion

**Assembly frame** (the ground's frame): the origin is pivot O2 on the ground plate's top face, +x points from O2 toward O4,
+z points up along every pin axis, and +y completes a right-handed frame (the rest coupler and rocker lie toward +y). Datums:
`groundTop` is z = 0, `axisO2` is x = y = 0, and `axisO4` is x = 100, y = 0. At rest the envelope is (-30, -30, -5) to
(130, 88, 15). The ground plate sets x and the lower y and z; the coupler and rocker ends (B at y = 80 plus R8) set y = 88, and
the rocker's top face sets z = 15.

**Part frames**: every link has its first hole at its own origin, its second hole on +x at the link length, and its bottom face
at z = 0 (top face at z = 5). The crank runs O2 to A (40), the coupler A to B (100), the rocker O4 to B (80). The ground is
modelled in the assembly frame.

Every joint frame below is given in the named body's own frame, with every axis along +z.

| joint | kind | parent → child | parent frame | child frame | offset | rest angle | drive |
|---|---|---|---|---|---|---|---|
| pinO2 | revolute | ground → crank | (0, 0, 0), ref +x | (0, 0, 0), ref +x | 0 | 0 deg | motor, 60 rpm (defaulted) |
| pinA | revolute | crank → coupler | (40, 0, 5) = crank top face at A, ref +x | (0, 0, 0), ref +x | 0 | 53.13010235415598 deg | free |
| pinO4 | revolute | ground → rocker | (100, 0, 0) = ground top face at O4, ref +x | (0, 0, 0), ref +x | 10 (rocker layer bottom) | 90 deg | free |
| pinB | revolute, `closure: true` | coupler → rocker | (100, 0, 5) = coupler top face at B | (80, 0, 0) = rocker bottom face at B | coincident | from the loop (no ref) | — |

The rest placements (assembly frame) follow from the tree:
- crank: identity;
- coupler: Rz(53.130102 deg), then translate (40, 0, 5);
- rocker: Rz(90 deg), then translate (100, 0, 10).

Loop check at rest: B through the coupler is (40 + 100 cos 53.130102°, 100 sin 53.130102°, 5 + 5) = (100, 80, 10), and B
through the rocker is (100 + 80 cos 90°, 80 sin 90°, 10) = (100, 80, 10). The closure frames coincide. At rest the rocker's
angle from the coupler is 90 - 53.130102 = 36.869898 deg; this is left to the loop solver, so pinB has no ref.

**Transmissions**: none. The four-bar has no constant ratio; the evaluator couples pinA and pinO4 to pinO2 by solving the
closure at pinB at every pose.

**Motion** `crankTurn`: pinO2 from 0 to 360 deg (positive about +z, counter-clockwise seen from +z) in 360 steps of 1 deg. The loop
stays on the open branch throughout because the transmission angle (the angle at B between the coupler and the rocker) stays
between 36.870 and 101.537 deg, never reaching 0 or 180, so there is no dead point. The step count was chosen so that the
sampled rocker swing stays within 6.4e-5 deg of the analytic extremes; 72 steps would under-read it by 0.017 deg.

**Clearances at rest**: the pinned, adjacent-layer pairs seat face to face (`min_gap` 0, `max_gap` 0.01): crank on ground,
coupler on crank at A, and rocker on coupler at B. The other pairs never touch: coupler to ground has 5 (min_gap 4.9), rocker to
crank has at least 5 (min_gap 4.9; actually 44.3 at rest, with no xy overlap), and rocker to ground has 10 across the O4 pin
(min_gap 9.9). The layer gaps do not change during the planar motion, so the sweep's pairwise interference is zero volume.
Across the whole sweep the envelope grows to x -48..130, y -48..88, because the crank end reaches radius 48 about O2.

## 5. Fluid regions and named boundaries

None. The machine is purely kinematic: there is no fluid, heat, load or support, so it has no `fluid_volumes`, `boundaries` or
derived bodies.

## 6. Operating cases, observables and simulation inputs

The spec states no operating conditions (no speed, torque, load or material), so the contract has no `operating_cases` and no
`simulations`. All four predictions are kinematic observables that the evaluator measures from the placed geometry over
`crankTurn`.

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| groundLength (O2 to O4) | 100 | mm | stated | spec table, Ground |
| crankLength (O2 to A) | 40 | mm | stated | spec table, Crank |
| couplerLength (A to B) | 100 | mm | stated | spec table, Coupler |
| rockerLength (O4 to B) | 80 | mm | stated | spec table, Rocker |
| linkThickness / linkWidth / end radius | 5 / 16 / 8 | mm | stated | spec table, Crank ("stadium plate 5 thick, 16 wide, semicircular ends of radius 8") |
| holeDiameter | 6 | mm | stated | spec table (Ø6 holes) |
| layer bottoms: crank / coupler / rocker | 0 / 5 / 10 | mm | stated | spec Frame paragraph |
| crankRestAngle | 0 | deg | stated | spec Rest configuration |
| couplerRestAngle | 53.13010235415598 | deg | derived | degrees(atan2(rockerLength, groundLength - crankLength)); the spec rounds it to 53.130102 |
| rockerRestAngle | 90 | deg | stated | spec Rest configuration |
| crank speed (pinO2 drive) | 60 | rpm | defaulted | the spec states no speed; one revolution per second only paces the animation, and no prediction depends on it |
| coupler point P, coupler frame | (50, 30) | mm | stated | spec Coupler point P |
| coupler point P, assembly at rest | (46, 58, 7.5) | mm | derived | A + Rz(53.130102°)·(50, 30) = (40 + 30 - 24, 40 + 18); z = 7.5 is the coupler mid-plane (a choice, see section 7) |
| observable `rockerAngle` | series | deg | measured by the evaluator | joint_value of pinO4 (parent ground) from rest over `crankTurn` |
| observable `rockerSwing` | scalar | deg | measured by the evaluator | joint_range of pinO4 over `crankTurn` |
| observable `couplerX` | series | mm | measured by the evaluator | point_x of `coupler` at location (46, 58, 7.5) over `crankTurn` |
| observable `couplerY` | series | mm | measured by the evaluator | point_y of `coupler` at location (46, 58, 7.5) over `crankTurn` |

The contract states no `expected` values for the observables. The analytic values below come from the stated link lengths by
position analysis (law of cosines, open branch). They are for review only and are not contract requirements:
- The rocker ranges from -11.536959 deg (at crank 34.048 deg, crank and coupler extended: O2B = 140) to +53.130102 deg (at crank
  233.130 deg, crank and coupler folded: O2B = 60). That is an absolute rocker angle of 78.463041 to 143.130102 deg.
- The swing is arccos(-0.2) - arccos(0.8) = 64.667061 deg.
- Samples: at crank 90, 180 and 270 deg the rocker is at +5.8595, +45.5847 and +49.4623 deg from rest. P is at (34.042, 87.341),
  (-15.368, 52.851) and (-7.998, 17.758).
- The coupler point P traces x -19.613..57.787 and y 17.670..87.374 over the revolution.

## 7. Defaults, open questions and unrepresentable features

- **Material**: the spec states no material, density or mass. None is declared, and there is no mass or centre-of-mass
  acceptance; the kinematic predictions do not depend on them.
- **Crank speed**: the spec states none. The motor drive on pinO2 defaults to 60 rpm (one revolution per second) only to pace
  the animation; every prediction is a function of the crank angle, not of time.
- **Pins**: joints only. The spec defines four solids and no pin, washer, spacer or fastener bodies. So the O4 pin spans an empty
  10 gap between the ground's top face (z 0) and the rocker (z 10..15), and no pin head at O2 is modelled. A physical O2 head
  above z 5 would lie under the coupler's path near the folded pose, because the coupler passes over O2 at crank 233 deg.
- **Fit**: no pin diameter or fit is stated for the Ø6 holes. The joints are ideal and no running clearance is modelled.
- **Coupler point P**: it lies 30 off the coupler's centreline, outside its 16-wide plate. It is a reference point fixed in the
  coupler frame, not a feature, and the coupler draft must add no material for it. Its assembly z (7.5, the coupler mid-plane)
  is a choice; the motion is planar, so x and y do not depend on it.
- **Coupler rest angle**: the spec rounds it to 53.130102 deg. The contract uses the exact 53.13010235415598 so the loop closes
  exactly at rest (the rounding would move B by 6e-7).
- **Unrepresentable**: nothing the spec states is left out. The crank-rocker coupling has no constant ratio, so it is carried by
  the closure joint pinB rather than by a `transmissions[]` entry.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft (order 001) | ok | `python -m opencad assembly check designs/.staging-four-bar --name four-bar` |
