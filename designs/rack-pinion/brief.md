# rack-pinion — assembly brief

## 1. Intent and configuration

A rack and pinion on a base plate, built from `sources/rack-pinion-spec.md`, the only source (text, authoritative; no
drawings, renders or CAD). The machine is three separate solids with no fused bodies:

- `base`: a 240 x 80 x 5 plate from corner (-120, -50, -5) to (120, 30, 0), with a D6 clearance hole on the pinion axis.
  It is the datum part, and its frame is the assembly frame.
- `pinion`: a 20-tooth involute spur pinion, module 2, pressure angle 20 deg (pitch radius 20, tip 22, root 17.5, face 8,
  D6 bore). It sits on a revolute joint about +z at the origin and is the motor-driven joint.
- `rack`: a 32-tooth straight-flank rack, module 2, 200 long and 8 thick. It sits on a slider joint along +x with its
  pitch line on y = -20, tangent to the pinion pitch circle, and its teeth point +y toward the pinion.

At rest the pinion is at 0 deg, so its tooth at -90 deg points into the rack's tooth space at x = 0, and the rack's
origin is at (0, -20, 0). The pinion turns one full revolution. The rack follows through the gear transmission
`rackDrive` by the pitch circle's arc per degree, 20 pi / 180 = 0.3490659 mm/deg; positive rotation about +z moves the
rack toward +x. The pair must run the whole revolution with zero interference.

The machine is scored on two predictions, both measured by the evaluator from the placed geometry (no simulation):
`rackRatio`, the rack's transmission ratio in mm per degree of pinion rotation, and `rackTravel`, the rack's slider
range over the one-revolution motion `pinionTurn`. There are no operating cases, because the sources state no speed or
load and both predictions are kinematic. The motor's 10 rpm is a default that only paces the animation.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/rack-pinion-spec.md | text | authoritative | 87f6a8bbc15c559e23899017105cd36ee8b503a6238b00213d3b99103d903561 | parameter table, assembly frame, part frames, rest configuration, motion and predictions |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| base | modelled | rack-pinion-base | not stated | spec table row "Base plate"; frame paragraph | datum part; its own frame is the assembly frame; the top face z = 0 carries the pinion and the rack |
| pinion | modelled | rack-pinion-pinion | not stated | spec table rows "Module", "Pressure angle", "Pinion", "Backlash"; part-frames paragraph | 20 teeth, involute flanks, every tooth thinned 0.05 at the pitch circle; a tooth centred on +x |
| rack | modelled | rack-pinion-rack | not stated | spec table rows "Module", "Pressure angle", "Rack", "Rack teeth", "Rack body"; part-frames paragraph | 32 teeth at x = (k + 1/2) p, k = -16 to 15; tooth thickness p/2 - 0.05 on the pitch line |

The spec lists exactly these three bodies. It names no shaft, bearing, guide, fastener or motor body, so there are no
purchased or derived parts. `acceptance.solid_count` is 3.

## 4. Frames, joints and motion

**Assembly frame (the base's frame).** The origin is on the pinion axis at the plate's top face. x runs along the rack
pitch line (the rack's travel), y from the rack toward the pinion, and z up along the pinion axis. Datums: A is the plate
top z = 0, B is the pinion axis x = y = 0, and C is the rack pitch line y = -20. The envelope at rest is
(-120, -50, -5) to (120, 30, 8). The plate sets x, y and the bottom z; the pinion and the rack both reach z = 8. The
pinion spans x and y from -22 to 22, and the rack spans x -100 to 100, y -32 to -18.

**Part frames.**

- `base`: the assembly frame. The box runs (-120, -50, -5) to (120, 30, 0), with a D6 hole through at (0, 0).
- `pinion`: axis +z through its origin, bottom face z = 0, face z = 0 to 8, a tooth centred on +x. With 20 teeth there
  is a tooth every 18 deg, so one also sits at -90 deg.
- `rack`: origin on the pitch line at mid-length, +x along the pitch line, +y toward the tooth tips, bottom face z = 0.
  The tip line is y = 2, the root line y = -2.5, the back face y = -12, and the body runs x -100 to 100. A tooth space is
  centred on x = 0.

**Joints.** Both joints are children of the datum part, so the tree is `base` to `pinion` and `base` to `rack`.

| joint | kind | parent to child | parent frame (base frame) | child frame (own frame) | rest | limits | drive |
|---|---|---|---|---|---|---|---|
| pinionSpin | revolute | base to pinion | origin (0, 0, 0), axis +z, ref +x | origin (0, 0, 0), axis +z, ref +x | offset 0, angle 0 deg | none (continuous) | motor, 10 rpm (defaulted; the spec states no speed) |
| rackSlide | slider | base to rack | origin (0, -20, 0), axis +x, ref +y | origin (0, 0, 0), axis +x, ref +y | offset 0, angle 0 deg | none stated | free, through rackDrive |

The revolute refs fix the mesh phase. At angle 0 the pinion's +x tooth lies on the base +x, and its -90 deg tooth is
centred in the rack's tooth space at x = 0. The pinion's tooth thickness at the pitch circle is 3.091593 and the rack's
space width on the pitch line is p - 3.091593 = 3.191593. That leaves 0.05 mm of tangential backlash on each flank, a
normal gap of 0.05 cos 20 deg = 0.047 mm. The slider refs keep the rack's +y (its tooth tips) on the base +y, so the rack
only translates.

**Transmission.** `rackDrive` is a gear transmission with driver `pinionSpin` and driven `rackSlide`. Its ratio is
+0.3490658503988659 mm/deg, which is pinionPitchRadius x pi / 180: the spec states that the pitch point carries the rack
by the pitch circle's arc per degree. The sign follows from the pitch point (0, -20, 0): under a positive rotation about
+z it moves along +x, which is the slider's parent axis. One pinion pitch is 360 / 20 = 18 deg. The transmission has
no `mesh` check, because a gear mesh check needs two rotating joints and the rack is on a slider. The `pinionTurn` sweep
checks the mesh for interference instead.

**Motion.** `pinionTurn` drives pinionSpin from 0 to 360 deg in 72 steps of 5 deg. Because 5 and 18 share no factor, the
steps land on all 18 whole-degree phases of the 18 deg pitch. Over the revolution the rack moves
2 pi x 20 = 125.664 mm along +x. The rack's last tooth sits at x = -15.5 p = -97.39 at rest, so it leaves the mesh at about
280 to 295 deg. For the rest of the revolution the pinion turns out of mesh: its tip circle (y >= -22) stays 0.5 mm above
the rack's root line (y = -22.5), so no pair interferes. The rack's right end reaches x = 225.7, past the plate end at
x = 120.

**Clearances at rest.**

- `pinionRackMesh` (pinion and rack): gap 0 to 0.15 mm, meshed with no interference and no stand-off.
- `pinionOnBase` and `rackOnBase`: gap 0 to 0.01 mm. Both bottom faces stand on the plate top z = 0.

## 5. Fluid regions and named boundaries

None. The sources describe no fluid, load, heat or support conditions, and no analysis needs a named patch. The contract
declares no `fluid_volumes[]` and no `boundaries[]`.

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| gearModule | 2.0 | mm | stated | spec table row "Module" |
| circularPitch | 6.283185307 | mm | derived | pi x gearModule (the spec gives 6.283185) |
| pressureAngle | 20.0 | deg | stated | spec table row "Pressure angle" |
| pinionPitchRadius | 20.0 | mm | stated | spec table row "Pinion" (= gearModule x 20 / 2) |
| pitchLineOffset | 20.0 | mm | stated | spec frame paragraph: rack pitch line on y = -20, tangent to the pitch circle |
| backlashPerMesh | 0.10 | mm | stated | spec table row "Backlash": 0.05 thinning on every pinion tooth plus 0.05 on every rack tooth |
| rackTransmissionRatio (rackDrive ratio) | 0.3490658504 | mm/deg | derived | pinionPitchRadius x pi / 180 (the spec's motion paragraph) |
| rackRatio (observable) | expected 0.3490658504, tolerance_rel 1e-4 | mm/deg | derived | quantity transmission_ratio, body rack; measured by the evaluator, no simulation |
| rackTravel (observable) | expected 125.6637061, tolerance_rel 1e-4 | mm | derived | quantity joint_range, joint rackSlide, motion pinionTurn (0 to 360 deg); 2 pi x 20; measured by the evaluator, no simulation |
| pinionSpin motor speed | 10.0 | rpm | defaulted | the spec states no speed; one revolution in 6 s (rack 20.94 mm/s) paces the animation only, since both predictions are speed-independent; uncertainty irrelevant to the predictions |

Both observables are analytic identities of the stated geometry. Their bands are 1e-4 relative, ten times the 1e-5
floor, because the evaluator measures rack pitch and positions on tessellated sections. There is no `simulations[]`
entry and no material input: the spec states no material, density or physical load.

## 7. Defaults, open questions and unrepresentable features

- **No speed or operating case.** The spec states neither, and both predictions are kinematic. So pinionSpin's motor
  drive carries a defaulted 10 rpm (one revolution in 6 s, rack 20.94 mm/s) that only paces the animation, and the
  contract declares no operating cases or simulations.
- **Idealised joints.** No shaft, bearing, guide or retention is specified. The pinion's D6 bore and the plate's D6
  clearance hole are coaxial, but no pin is modelled, and the rack only stands on the plate top.
- **The rack runs out of mesh.** One revolution moves the rack 125.66 mm, more than its 100 mm half-length. The last rack
  tooth leaves the mesh at about 280 to 295 deg, so the pinion finishes the revolution out of mesh, with its tips 0.5 mm
  above the rack's root line. The rack's right end reaches x = 225.7, past the plate end at x = 120. The motion stays
  at one revolution because the spec and the task both state it, and the transmission couples the joints over the whole
  range.
- **No material.** The spec gives no material or density, so there is no mass or centre-of-mass check.
- **Inferred and defaulted bands.** max_gap 0.15 mm (pinionRackMesh) is an inferred band above the stated 0.10 mm
  backlash per mesh. The seat max_gap of 0.01 mm (pinionOnBase, rackOnBase) is a defaulted numerical band for faces that
  touch. A rack drive takes no gear mesh check, so the backlash is bounded only at rest by pinionRackMesh, and
  interference over the mesh only by the pinionTurn sweep. The zero-interference requirement uses the evaluator's
  default interference tolerance.
- **No joint limits.** None are stated. The revolute is continuous and the slider is unlimited; the one-revolution
  motion needs 0 to 125.66 mm.
- **Pinion flank below the base circle.** The spec does not define the flank between the root circle (r 17.5) and the
  base circle (r 18.794). The part drafter chooses it (a radial line or a fillet), and the pinionTurn sweep checks that
  it clears the rack's tip corners. The rack tip line (y = -18) passes 0.5 mm outside the pinion root circle.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft | ok | `python -m opencad assembly check designs/.staging-rack-pinion --name rack-pinion` passes with no warnings, after three fixes: a `tolerance` on every parameter, no `mesh` check on the rack drive (it needs two rotating joints), and a defaulted motor speed |
