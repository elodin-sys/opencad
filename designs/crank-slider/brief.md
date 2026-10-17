# crank-slider — assembly brief

## 1. Intent and configuration

An offset crank-slider built from `sources/crank-slider-spec.md`, the only source (text, authoritative). It has four separate solids (no fused bodies), each drafted and modelled in its own frame, stacked in 5 mm layers:

- ground plate, z -5..0;
- crank and slider block, z 0..5 (they share the layer and never meet, because the slider stays beyond x = 54);
- connecting rod, z 5..10, on top of both.

Three revolute pins and one prismatic guide close one loop:

- pin O joins the ground and the crank; it is the motor-driven joint;
- pin A joins the crank and the rod;
- pin B joins the rod and the slider;
- the guide joins the ground and the slider, along +x on the line y = 10 (offset e = 10 from the crank axis).

The joint tree runs from the ground through `crankPivot` (O), `crankPin` (A) and `guide`; the wrist pin `wristPin` (B) is the loop's closing joint.

Rest configuration: crank at 0 deg (A at (30, 0)), B at (129.498744, 10) on the guide, rod at 5.739170 deg from +x, slider centred on B.

Motion: the crank turns one full revolution from rest (0 to 360 deg), and the loop must stay closed and interference-free. The predictions are measured by the evaluator from the placed geometry: the slider's travel along the guide from rest, as a series over the revolution, and its stroke. There are no operating cases, fluids or simulations.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/crank-slider-spec.md | text | authoritative | cd01ebc4dc4d7289a786bef3bca834eb565dd9f6109941bbcc2ec04b879c0d1c | part table, frame and layers, part frames, rest configuration, joints, motion and predictions; no images or CAD |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| ground | modelled | crank-slider-ground | not stated | spec, Ground row | plate 200 x 70 x 5 from (-40, -30, -5) to (160, 40, 0), D6 hole at O; own frame = assembly frame; the datum part; volume 69858.63 mm3 |
| crank | modelled | crank-slider-crank | not stated | spec, Crank row | stadium 5 thick, 16 wide, R8 ends; D6 holes O (0, 0) and A (30, 0); bbox (-8, -8, 0)..(38, 8, 5); volume 3122.57 mm3 |
| rod | modelled | crank-slider-rod | not stated | spec, Connecting rod row | stadium as the crank; D6 holes A (0, 0) and B (100, 0); bbox (-8, -8, 0)..(108, 8, 5); volume 8722.57 mm3 |
| slider | modelled | crank-slider-slider | not stated | spec, Slider row | block 30 (x) x 16 (y) x 5 (z) centred on its D6 hole; origin at the hole on the bottom face; bbox (-15, -8, 0)..(15, 8, 5); volume 2258.63 mm3 |

`acceptance.solid_count` is 4. There are no purchased or derived bodies, and no physical pins, since the spec asks for exactly four solids.

## 4. Frames, joints and motion

**Assembly frame** (the ground's own frame):

- origin: the crank axis O on the ground's top face;
- x: parallel to the guide, from O toward the slider;
- y: from O toward the guide line y = 10;
- z: up, with every pin axis parallel to +z.

Datums are `groundTop` (z = 0), `crankAxis` (x = y = 0) and `guideLine` (y = 10, z = 0, parallel to +x).

Envelope at rest: (-40, -30, -5) to (160, 40, 10), tolerance 0.1. The ground sets x and y; z runs from the ground's underside to the rod's top.

**Part frames** (from the spec):

- crank and rod: first hole (O for the crank, A for the rod) at the own origin, second hole on +x at the link length, bottom face at z = 0;
- slider: origin at its hole centre on its bottom face, its 30 mm length along +x;
- ground: modelled directly in the assembly frame.

**Rest poses** in the assembly frame:

| body | rest pose |
|---|---|
| crank | origin (0, 0, 0), 0 deg |
| rod | origin (30, 0, 5), rotated 5.739170477 deg about +z |
| slider | origin (129.498743711, 10, 0), unrotated |

**Joints** (frames in each body's own frame):

| joint | kind | parent -> child | parent frame | child frame | rest | drive |
|---|---|---|---|---|---|---|
| crankPivot | revolute | ground -> crank | origin (0, 0, 0), axis +z, ref +x | origin (0, 0, 0), axis +z, ref +x | offset 0, angle 0 deg | motor, 60 rpm (defaulted, animation only) |
| crankPin | revolute | crank -> rod | origin (30, 0, 5) (crank top face at A), axis +z, ref +x | origin (0, 0, 0) (rod bottom face at A), axis +z, ref +x | offset 0, angle 5.739170477 deg = rodRestAngle | none (solved by the loop) |
| guide | slider | ground -> slider | origin (0, 10, 0) on the guide line, axis +x, ref +z | origin (0, 0, 0), axis +x, ref +z | offset 129.498743711 = restSliderX, angle 0 (no rotation) | none (solved by the loop) |
| wristPin | revolute, `closure: true` | rod -> slider | origin (100, 0, 0) (rod bottom face at B), axis +z, no ref | origin (0, 0, 5) (slider top face at B), axis +z, no ref | coincident at rest: both frames at (129.498744, 10, 5) | none |

Derivations:

- restSliderX = crankLength + sqrt(rodLength^2 - guideOffset^2) = 30 + sqrt(9900) = 129.498743711;
- rodRestAngle = asin(guideOffset / rodLength) = asin(0.1) = 5.739170477 deg.

At rest the rod's B frame maps to (30 + 100 cos 5.739170477 deg, 100 sin 5.739170477 deg, 5) = (129.498744, 10, 5). The slider's (0, 0, 5) frame maps to the same point, so the closure frames coincide.

Every pin frame lies on its two layer faces, so every offset is 0. The ground has two tree children (the crank and the slider), as a four-bar's ground carries the crank and the rocker.

**Motion:** `crankTurn` drives `crankPivot` from 0 to 360 deg in 360 steps of 1 deg. The evaluator solves `crankPin`, `guide` and `wristPin` at every step and checks interference for every pair in relative motion. There are no transmissions: the linkage couples the joints through the closure, and its ratio is not constant.

**Kinematics** (for the reviewer; the evaluator measures them from the placed geometry):

- slider position: x_B(theta) = r cos(theta) + sqrt(L^2 - (e - r sin(theta))^2), with r = 30, L = 100, e = 10;
- extended dead centre: x_B = sqrt(130^2 - 10^2) = 129.614814, at crank 4.41 deg;
- folded dead centre: x_B = sqrt(70^2 - 10^2) = 69.282032, at crank 188.21 deg;
- travel from rest: -60.216711 to +0.116070 mm;
- stroke: 60.332782 mm. The 1 deg sampling reads 60.331625, which is 0.0012 mm inside the 0.01 band.

**Clearances at rest:**

| clearance | pair | min_gap | max_gap | why |
|---|---|---|---|---|
| crankOnGround | crank, ground | 0 | 0.05 | seat at z = 0 |
| sliderOnGround | slider, ground | 0 | 0.05 | seat at z = 0 |
| rodOnCrank | rod, crank | 0 | 0.05 | seat at z = 5 |
| rodOnSlider | rod, slider | 0 | 0.05 | seat at z = 5 |
| crankClearOfSlider | crank, slider | 1.0 | | same layer; the crank reaches x <= 38 and the slider starts at x >= 54.28 |
| rodClearOfGround | rod, ground | 4.9 | | 5 mm layer gap |

## 5. Fluid regions and named boundaries

None: the machine has no fluid domain and no analysis that loads named patches, so there are no `fluid_volumes` or `boundaries`.

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| crankLength (O to A) | 30 | mm | stated | spec, Crank row |
| rodLength (A to B) | 100 | mm | stated | spec, Connecting rod row |
| guideOffset e (guide line y = 10) | 10 | mm | stated | spec, Guide row |
| layerThickness | 5 | mm | stated | spec, Frame: ground z -5..0, crank and slider z 0..5, rod z 5..10 |
| link width / end radius / hole diameter | 16 / 8 / 6 | mm | stated | spec, Crank and Connecting rod rows |
| slider block | 30 x 16 x 5 | mm | stated | spec, Slider row |
| ground plate | 200 x 70 x 5, (-40, -30, -5)..(160, 40, 0) | mm | stated | spec, Ground row |
| restSliderX | 129.498743711 | mm | derived | crankLength + sqrt(rodLength^2 - guideOffset^2); spec states 129.498744 |
| rodRestAngle | 5.739170477 | deg | derived | asin(guideOffset / rodLength); spec states 5.739170 |
| crankTurn range | 0 to 360, 360 steps | deg | stated (steps defaulted) | spec, Motion; 1 deg steps chosen so the sampled dead centres fall within 0.0012 mm |
| crankPivot motor speed | 60 | rpm | defaulted | the spec states no speed; one revolution per second sets the animation timing only, and no prediction depends on it |
| observable sliderTravel | joint_value of `guide` over `crankTurn` (series) | mm | measured by the evaluator | spec, Predictions; no simulation |
| observable stroke | joint_range of `guide` over `crankTurn`; expected 60.332782 +/- 0.01 | mm | derived (analytic identity) | sqrt((L + r)^2 - e^2) - sqrt((L - r)^2 - e^2) |

There are no operating cases, simulations or material inputs, because both predictions are kinematic.

## 7. Defaults, open questions and unrepresentable features

- The spec states no materials or densities. None is needed for the kinematic predictions, so no material, mass or centre of mass is declared.
- The spec states no crank speed. The motor drive defaults to 60 rpm (one revolution per second) for the animation only, because the sweep and both predictions are displacement-driven.
- No physical pins, bushings or retainers are specified (four separate solids). Each revolute joint is the common axis of two D6 holes. The ground plate has no rail or slot, so the guide exists only as the prismatic joint on the line y = 10: nothing physical restrains the slider laterally.
- Several values are drafter choices; the spec gives exact layers but no tolerances. These are the seat bands (max_gap 0.05), the crank-to-slider min_gap 1.0, the rod-to-ground min_gap 4.9, the 1 deg sweep step and the 0.01 mm stroke band.
- Near a crank angle of 270 deg, the crank's R8 end at A reaches y = -38 and overhangs the ground's y = -30 edge by 8 mm. This causes no interference.
- The slider always stays on the plate (x = 54.28..144.61, y = 2..18).

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft | drafted | contract and brief drafted from sources/crank-slider-spec.md; see the assembly check result |
