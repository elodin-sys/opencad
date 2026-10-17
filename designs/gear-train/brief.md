# gear-train — assembly brief

## 1. Intent and configuration

Spur-gear pair on a carrier plate, from `sources/gear-pair-spec.md` (the only source: text, authoritative). The machine has
three separately designed bodies: a 20-tooth pinion and a 40-tooth wheel (module 2, pressure angle 20 deg, no profile
shift, face width 8, 0.10 total circular backlash), each on a revolute joint on a 110 x 50 x 5 carrier plate. The pinion
is the motor-driven joint; the wheel follows through a gear transmission at ratio -0.5 (half the pinion's speed, opposite
sense). Each gear is drafted and modelled in its own frame (axis +z through its own origin, bottom face z = 0); the carrier
is modelled in the specification's frame, which is the assembly frame.

The acceptance is kinematic: one pinion pitch (18 deg) of rotation with zero interference and a flank gap of at most 0.15,
and the transmission ratio measured from the placed geometry. The spec defines no operating cases, loads or materials, so
the contract declares no operating cases and no simulations.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/gear-pair-spec.md | text | authoritative | 0acea6d35513df93499f95e7242721b64488c45819f6e58ebd09ed627fb09d87 | parameter table (module, pressure angle, profile shift, teeth, bores, axes, centre distance, face width, addendum/dedendum, backlash, tooth phase, carrier plate, motion) and the frame paragraph; its reference involutes are evaluator-only |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| carrier | modelled | gear-train-carrier | not stated | spec, Carrier plate row | datum part; 110 x 50 x 5 plate from (-25, -25, -5) to (85, 25, 0); D6 clearance hole at (0, 0) and D8 at (60, 0), through; top face z = 0 seats both gears |
| pinion | modelled | gear-train-pinion | not stated | spec, Pinion, Face width, Addendum/dedendum, Backlash, Tooth phase rows | 20 teeth; pitch r 20, base r 18.794, tip r 22, root r 17.5; face z = 0..8; D6 bore; a tooth centred on its own +x |
| wheel | modelled | gear-train-wheel | not stated | spec, Wheel, Face width, Addendum/dedendum, Backlash, Tooth phase rows | 40 teeth; pitch r 40, base r 37.588, tip r 42, root r 37.5; face z = 0..8; D8 bore; a tooth centred on its own +x |

Shared tooth form (both gears): module 2, pressure angle 20 deg, profile shift 0, addendum 1.0 m, dedendum 1.25 m (tip
clearance 0.5). Each flank is a true involute of the base circle from the base circle to the tip (12-16 sample points,
per the spec's recommendation), continued radially down to the root circle; tip and root are arcs, no fillets. Tooth
thickness at the pitch circle is pi m / 2 - 0.05 = 3.0916 on both gears (thinned 0.05, 0.025 per flank), so the pair has
0.10 total circular backlash. Derived tooth angles: pinion tooth half-angle 5.282 deg at the base circle and 1.738 deg at
the tip (tip land 1.335); wheel 3.068 deg and 1.002 deg (tip land 1.469).

## 4. Frames, joints and motion

Assembly frame (= carrier frame = spec frame): origin on the pinion axis in the carrier top face; +x from the pinion
axis toward the wheel axis; +z up along the gear axes; y completes a right-handed frame. Datums: A carrier top face
z = 0, B pinion axis x = y = 0, C wheel axis (60, 0).

Part frames: carrier as above. Pinion and wheel: axis +z through the part origin, bottom face z = 0, top face z = 8,
the +x axis through the centre of one tooth (the tooth's symmetry line). The +x axis of each gear is its joint `ref`.

| joint | kind | parent / child | parent frame (carrier) | child frame (own) | offset | rest angle | drive |
|---|---|---|---|---|---|---|---|
| pinionSpin | revolute | carrier / pinion | origin (0, 0, 0), axis +z, ref +x | origin (0, 0, 0), axis +z, ref +x | 0 | 0 deg | motor, 1 rpm (defaulted: the spec states no speed) |
| wheelSpin | revolute | carrier / wheel | origin (60, 0, 0), axis +z, ref +x | origin (0, 0, 0), axis +z, ref +x | 0 | 4.5 deg (`wheelPhase`) | free, through gearPair |

Both joints have no limits (continuous rotation). The offset 0 puts both gear bottoms on the carrier top face z = 0
(touching but separate, as the spec states).

Rest phase: the spec puts a pinion tooth centred on +x and a wheel tooth space centred toward the pinion ("rotate its
pattern half a pitch, pi/40"). The wheel part keeps a tooth on its own +x like the pinion, and wheelSpin's rest angle
of half a wheel pitch (180 / 40 = 4.5 deg) makes the placed wheel's teeth lie at 4.5 + 9k deg and its spaces at 9k deg,
so a space is centred on 180 deg (toward the pinion); because 40 is even, one is also centred on 0 deg. The pinion
tooth on +x then sits centred in that wheel space on the line of centres, with the backlash split equally: 0.05 circular
per side at the pitch circle, 0.047 normal (0.05 cos 20 deg).

Transmission `gearPair`: pinionSpin drives wheelSpin, ratio -0.5 = -pinionTeeth / wheelTeeth = -20/40 (the spec's
Motion row: half the pinion's speed, opposite sense). Mesh check over one pinion pitch, 360 / 20 = 18 deg, in 18 steps,
`backlash_max` 0.15 (the spec's maximum flank gap). Mesh numbers for the reviewer: centre distance 60 = 2 (20 + 40) / 2,
line of action 60 sin 20 deg = 20.52, contact ratio 1.64; the wheel tip meets the pinion involute down to r 18.88, above
the pinion base circle 18.79 (no involute interference); tip clearance 0.5 both ways.

Motion `onePitch`: pinionSpin from 0 to 18 deg in 18 steps; the wheel follows from 0 to -9 deg. Every pair is in
relative motion (pinion and wheel, each gear and the carrier), so the sweep checks all three.

Clearances: `pinionSeat` and `wheelSeat` (each gear against the carrier, 0 to 0.01: touching but separate) and
`flankGap` (pinion against wheel at rest, 0 to 0.15: zero interference, designed 0.047).

Envelope at rest: carrier x -25..85, y -25..25, z -5..0; pinion tip r 22 about (0, 0), z 0..8; wheel tip r 42 about
(60, 0), z 0..8. The wheel's teeth nearest +x and +-y are 4.5 deg off those axes and their tip lands span +-1.002 deg, so
the wheel reaches 60 + 42 cos 3.498 deg = 101.92 in x and +-41.92 in y. Envelope [-25, -41.92, -5] to [101.92, 41.92, 8],
tolerance 0.1; three solids.

## 5. Fluid regions and named boundaries

None. The spec defines no fluid, loads, supports or heat paths, and the only prediction (the transmission ratio) is
kinematic, so no fluid region and no named boundary is needed.

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| gearModule | 2 | mm | stated | spec, Module row |
| pressureAngle | 20 | deg | stated | spec, Pressure angle row |
| pinionTeeth | 20 | - | stated | spec, Pinion row |
| wheelTeeth | 40 | - | stated | spec, Wheel row |
| faceWidth | 8 | mm | stated | spec, Face width row (both gears z = 0..8) |
| circularBacklash | 0.10 (band 0.05) | mm | stated | spec, Circular backlash row: total, each tooth thinned 0.05 at its pitch circle; the band reaches the Motion row's 0.15 maximum |
| centreDistance | 60 (band 0.01) | mm | stated | spec, Centre distance row; = gearModule (pinionTeeth + wheelTeeth) / 2 |
| pinionPitch | 18 | deg | derived | 360 / pinionTeeth |
| wheelPhase | 4.5 | deg | derived | 180 / wheelTeeth = pi/40 rad (spec, Tooth phase row); the wheelSpin rest angle |
| gearRatio | -0.5 | - | derived | -pinionTeeth / wheelTeeth; spec, Motion row (half the speed, opposite sense) |
| mesh backlash_max, flankGap max_gap | 0.15 | mm | stated | spec, Motion row (flank gap at most 0.15) |
| observable gearRatio | transmission_ratio, expected -0.5 +- 1e-5 | - | derived | measured by the evaluator from the placed geometry; no simulation |
| pinionSpin drive speed | 1 | rpm | defaulted | the spec states no speed; the unit animation speed, used only to animate (the ratio and the mesh sweep are speed-independent) |
| operating cases | none | - | - | the spec states no speed, load or duty |
| simulations | none | - | - | the only prediction is kinematic |

## 7. Defaults, open questions and unrepresentable features

Defaults chosen here (the spec is silent):
- Root form: each flank continues radially from the base circle to the root circle, with no root fillet and no tip
  rounding (the pinion root 17.5 is 1.29 below its base circle 18.79; the wheel root 37.5 is 0.09 below 37.59).
- Backlash split: "thin each tooth by 0.05 mm at its pitch circle" is a pitch-circle tooth thickness of
  pi m / 2 - 0.05 = 3.0916 on both gears, 0.025 per flank; the two gears together give the stated 0.10.
- Phase convention: both gear parts carry a tooth on their own +x; the spec's half-pitch wheel rotation is the wheelSpin
  rest angle (4.5 deg), so the placed pair matches the spec's phasing.
- The carrier plate has sharp edges; its two holes are through clearance holes of the stated diameters.
- Pinion drive speed 1 rpm (the unit animation speed): the spec states none and no prediction depends on it.

Open questions (as in the contract):
- The spec states no materials or densities; none is declared and the assembly mass is not checked.
- The spec states no pinion speed and no operating case; the pinion drive speed is defaulted to 1 rpm for the animation
  only (the ratio and the mesh sweep do not depend on speed).
- The spec gives no root fillet or tip rounding; the flanks continue radially from the base circle to the root circle
  with sharp tip and root corners.
- The backlash reading above (3.0916 pitch-circle tooth thickness on both gears, 0.025 per flank).
- The spec names no shafts, pins or bearings; the gears are located only by their revolute joints on the D6 and D8
  carrier holes, whose fit is not stated.

Unrepresentable: the spec asks for one editable KCL file holding three solids. Here each body is its own build123d part
design and the assembly source places the three exported solids into one STEP, which carries the same three solids.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft | ok | `python -m opencad assembly check designs/.staging-gear-train --name gear-train` |
