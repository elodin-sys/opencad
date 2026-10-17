# compound-train — assembly brief

## 1. Intent and configuration

A compound spur-gear train of four separate solids built from `sources/compound-train-spec.md` (authoritative, text only,
no images): a 195 x 100 x 5 mm base plate (the datum body) carrying three gears on revolute joints about +z at the plate's
clearance holes: a motor-driven 20-tooth input pinion at (0, 0), a compound idler at (60, 0) with a 40-tooth gear (z 0..8)
and a 15-tooth gear (z 8..16) on one solid, and a 45-tooth output gear at (120, 0) with its bottom face at z = 8.5. Module 2,
pressure angle 20 deg, zero profile shift, 0.10 mm circular backlash per mesh. The pinion drives the idler's 40-tooth gear;
the idler's 15-tooth gear drives the output. The gears are phased at rest (pinion 0 deg, idler 4.5 deg, output 6.5 deg) so
both meshes engage. The machine is kinematic only: the spec states no operating case, speed, load or material, so there
are no operating cases and no simulations. Predictions, measured by the evaluator from the placed geometry: the whole
train's transmission ratio (`trainRatio`) and the output gear's angle after one pinion revolution (`outputAt360`).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/compound-train-spec.md | text | authoritative | e2734c43ae1d2aa36320d0b7680e21616422e902b471b3eb98295e3292296af5 | parameter table, assembly frame, part frames, rest tooth phasing, motion and the two predictions |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| base | modelled | compound-train-base | not stated | spec, Base plate row and Frame | datum; plate (-25, -50, -5) to (170, 50, 0); through holes D6 at (0, 0), D8 at (60, 0) and (120, 0) |
| pinion | modelled | compound-train-pinion | not stated | spec, Input pinion row | 20 teeth, face 8 (z 0..8), bore D6, a tooth on +x in its frame |
| idler | modelled | compound-train-idler | not stated | spec, Compound idler row | 40 teeth z 0..8 and 15 teeth z 8..16 on one solid, bore D8 through, both patterns with a tooth on +x |
| output | modelled | compound-train-output | not stated | spec, Output gear row | 45 teeth, face 8 (z 0..8 in its frame, 8.5..16.5 placed), bore D8, a tooth on +x |

Gear geometry (module 2, 20 deg, zero shift, addendum 1.0 m, dedendum 1.25 m; every tooth thinned 0.05 mm at its pitch
circle, circular tooth thickness pi m / 2 - 0.05 = 3.0916 mm):

| gear | teeth | pitch r | tip r | root r | base r | pitch angle | face (own frame) |
|---|---:|---:|---:|---:|---:|---:|---|
| pinion | 20 | 20 | 22 | 17.5 | 18.794 | 18 deg | z 0..8 |
| idler, large | 40 | 40 | 42 | 37.5 | 37.588 | 9 deg | z 0..8 |
| idler, small | 15 | 15 | 17 | 12.5 | 14.095 | 24 deg | z 8..16 |
| output | 45 | 45 | 47 | 42.5 | 42.286 | 8 deg | z 0..8 |

Involute flanks from the involute equations, 12-16 points per flank from the base circle to the tip, with a radial flank from
the base circle to the root circle; the 45-tooth base circle lies inside its root circle, so its involute starts at the root.
Tip-to-root radial clearance at both meshes: 60 - 22 - 37.5 = 60 - 47 - 12.5 = 0.5 mm (0.25 m).

## 4. Frames, joints and motion

Assembly frame = the base plate's own frame: origin on the pinion axis at the plate top face, +x from the pinion toward the
idler (60, 0) and output (120, 0) axes, +z up along every gear axis, +y completes a right-handed frame. Datums: A plate top
face z = 0; B pinion axis x = y = 0; C plane y = 0 through the three axes. Every gear's own frame: axis +z through its origin,
bottom face z = 0, a tooth centred on +x (both idler patterns).

Envelope at rest: the plate spans x -25..170, y -50..50, z -5..0; every gear lies inside the plate footprint (output tip
reaches x = 167.0 and |y| < 47); the top is the output's top face at z = 16.5 (idler top z = 16). Envelope
[-25, -50, -5] to [170, 50, 16.5], tolerance 0.1.

| joint | kind | parent -> child | parent frame (base) | child frame (own) | offset | rest angle | drive |
|---|---|---|---|---|---:|---:|---|
| pinionSpin | revolute | base -> pinion | origin (0, 0, 0), axis +z, ref +x | origin 0, axis +z, ref +x | 0 | 0 deg | motor, 6 rpm (defaulted) |
| idlerSpin | revolute | base -> idler | origin (60, 0, 0), axis +z, ref +x | origin 0, axis +z, ref +x | 0 | 4.5 deg | free (pinionIdler) |
| outputSpin | revolute | base -> output | origin (120, 0, 0), axis +z, ref +x | origin 0, axis +z, ref +x | 8.5 | 6.5 deg | free (idlerOutput) |

No limits: the gears turn continuously. The pinion and the idler stand on the plate top (offset 0); the output's bottom face
is 8.5 mm above it, 0.5 mm above the idler's 40-tooth gear top (z = 8).

Rest phasing (spec, "Tooth phase at rest"), checked against rolling contact: a tooth of gear 1 at angle p1 from the line of
centres needs a space of gear 2 at 180 - p1 r1 / r2. Mesh 1: pinion tooth at 0 deg needs an idler 40-tooth space at 180 deg;
idler teeth at 4.5 + 9k deg put spaces at 9k deg, so 180 deg is a space. Mesh 2: the idler's 15-tooth tooth at 4.5 deg needs
an output space at 180 - 4.5 x 15 / 45 = 178.5 deg; output teeth at 6.5 + 8k deg put spaces at 10.5 + 8k deg, and
178.5 = 10.5 + 8 x 21. Both meshes are conjugate at rest with the backlash split evenly: about 0.05 mm circular,
0.047 mm normal, on each flank.

| transmission | kind | driver -> driven | ratio | mesh check | basis |
|---|---|---|---:|---|---|
| pinionIdler | gear | pinionSpin -> idlerSpin | -0.5 | pitch 18 deg, 12 steps, backlash_max 0.15 | -20 / 40; the spec: half the pinion's speed, opposite sense |
| idlerOutput | gear | idlerSpin -> outputSpin | -1/3 | pitch 24 deg, 12 steps, backlash_max 0.15 | -15 / 45; the spec: a third of the idler's speed, opposite sense |

Whole train (-1/2) x (-1/3) = +1/6: the output turns in the pinion's sense at one sixth of its speed.

Acceptance motion `pinionTurn`: pinionSpin 0..36 deg (two pinion pitches), 24 steps; the idler turns -18 deg, the output
+6 deg; every pair in relative motion is checked for interference. Each mesh check sweeps its driver through one full
pitch (18 deg of pinion, 24 deg of idler), which covers the spec's "at least one pitch of their driving gear".

Clearances: pinionIdlerMesh and idlerOutputMesh (min 0, max 0.15: no interference, flank gap at most 0.15 mm);
pinionOutputApart (min 0.5); pinionSeat and idlerSeat on the base (min 0, max 0.01: seated on the plate top);
outputAbovePlate (8.4..8.6: bottom face 8.5 above the plate). Solid count 4.

## 5. Fluid regions and named boundaries

None. The machine is kinematic only: no fluid domain, no derived bodies, and no simulation loads, so no named boundaries.

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| gearModule | 2.0 | mm | stated | spec, Module (both stages) |
| pressureAngle | 20 | deg | stated | spec, Pressure angle |
| profile shift | 0 | - | stated | spec, Profile shift (every gear) |
| addendum / dedendum | 1.0 m / 1.25 m | - | stated | spec; tip r = pitch r + 2, root r = pitch r - 2.5 |
| circularBacklash | 0.10 | mm | stated | spec; per mesh, each tooth thinned 0.05 mm at its pitch circle |
| tooth counts | 20 / 40 + 15 / 45 | - | stated | spec, gear rows |
| pinionIdlerCentre | 60 | mm | stated | spec, Centre distances; gearModule x (20 + 40) / 2 |
| idlerOutputCentre | 60 | mm | stated | spec, Centre distances; gearModule x (15 + 45) / 2 |
| outputOffset | 8.5 | mm | stated | spec, Output gear row and Frame |
| axialClearance | 0.5 | mm | stated | spec, Frame; outputOffset - 8.0 |
| pinion rest angle | 0 | deg | stated | spec, Tooth phase at rest |
| idlerPhase | 4.5 | deg | stated | spec, Tooth phase at rest; 360 / 40 / 2 |
| outputPhase | 6.5 | deg | stated | spec, Tooth phase at rest; checked in section 4 |
| stage1Ratio | -0.5 | - | derived | -20 / 40 |
| stage2Ratio | -0.333333 | - | derived | -15 / 45 |
| overallRatio | +0.166667 | - | derived | stage1Ratio x stage2Ratio |
| mesh backlash_max | 0.15 | mm | stated | spec, Motion: flank gap at most 0.15 mm |
| motion range | 0..36 | deg | stated | user intent: two pinion pitches (2 x 360 / 20) |
| pinion drive speed | 6 | rpm | defaulted | the spec states none; animation timing only (output 1 rpm, 36 deg sweep in 1 s); no prediction depends on it |
| trainRatio (observable) | expected +1/6 +- 1e-5 | - | derived | transmission_ratio, whole train, no body; measured by the evaluator |
| outputAt360 (observable) | expected 60 +- 1e-3 | deg | derived | joint_value of outputSpin at pinion 360 deg; 360 x 1/6; measured by the evaluator |

No operating cases (the spec states no speed, load or condition) and no simulations (both predictions are kinematic and
measured by the evaluator).

## 7. Defaults, open questions and unrepresentable features

- No motor speed or operating case in the spec: the pinion's motor drive carries a defaulted 6 rpm (animation timing only:
  output 1 rpm, the 36 deg sweep in 1 s); both predictions are speed-independent.
- No material or density for any part: no mass or centre of mass is predicted.
- No shafts, bearings or fasteners: each gear turns on a revolute joint about its plate-hole axis; the output gear is held at
  z = 8.5 by its joint alone (nothing supports it physically).
- The tooth root below the base circle is not defined: the drafts use a radial flank from the base circle to the root
  circle (the 45-tooth involute starts at its root circle, r 42.5, outside its base circle, r 42.286).
- The 15 -> 45 mesh sits at the involute-interference limit: for a 3:1 full-depth pair at 20 deg the minimum pinion count is
  14.98, and the output's tip reaches 5.124 mm along the line of action against the 15-tooth interference point at
  5.130 mm. Only the idlerOutput mesh sweep can confirm zero interference.
- "Zero interference" is checked at the evaluator's default interference tolerance (numerical noise), not a literal 0 mm3.
- The motion sweep (36 deg of pinion) turns the idler 18 deg, 0.75 of its 15-tooth pitch; the second mesh's full-pitch
  coverage comes from the idlerOutput mesh sweep (24 deg of idler).
- Unrepresentable: the 0.5 mm axial gap between the output and the idler's 40-tooth gear cannot be banded on its own,
  because the idler-output pair's minimum distance is the mesh flank gap (about 0.047 mm); idlerOutputMesh (min 0) and the
  motion sweep check that the two never interpenetrate.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft | drafted | `python -m opencad assembly check designs/.staging-compound-train --name compound-train` |
