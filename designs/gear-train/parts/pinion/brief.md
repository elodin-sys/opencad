# gear-train-pinion — design brief

## 1. Intent and configuration

Spur pinion (body `pinion` of the `gear-train` assembly), modelled alone in its own frame: 20 teeth, module 2, pressure angle 20 deg, profile shift 0, face width 8 from z = 0 to z = 8, D6 through bore on the axis. Flanks are true involutes of the base circle (r = 18.794) from the base circle to the tip circle (r = 22), sampled at 14 points per flank, continued radially down to the root circle (r = 17.5); tip arcs on r = 22, root arcs on r = 17.5, no fillets. Each tooth is thinned 0.05 at the pitch circle (0.025 per flank) for backlash, giving a pitch-circle tooth thickness of 3.0916. One tooth is centred on +x. The bottom face seats on the carrier top, the bore axis is the `pinionSpin` revolute joint axis (own-frame point [0, 0, 0], axis [0, 0, 1]), and the flanks mesh with the 40-tooth wheel at centre distance 60. The only authoritative source is `sources/gear-pair-spec.md`; the wheel and the carrier plate are separate designs.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/gear-pair-spec.md | text | authoritative | 0acea6d35513df93499f95e7242721b64488c45819f6e58ebd09ed627fb09d87 | parameter table for the pinion, wheel and carrier; only the pinion rows and the shared gear rows apply here |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| tooth count | 20 | | spec table, Pinion | exact | stated |
| module | 2 | mm | spec table | 0.001 | stated |
| pressure angle | 20 | deg | spec table | 0.001 | stated |
| profile shift | 0 | | spec table | 0.001 | stated |
| addendum / dedendum | 1.0 m / 1.25 m | | spec table | 0.001 | stated |
| face width, z = 0 to 8 | 8 | mm | spec table | 0.01 | stated |
| bore on axis | 6 | mm | spec table, Pinion bore D6 | 0.01 | stated |
| backlash thinning at pitch circle | 0.05 | mm | spec table, Circular backlash | 0.001 | stated |
| tooth centred on +x | phase 0 deg | deg | spec table, Tooth phase | symmetry y = 0 plus probes | stated |
| involute flank, 12-16 samples base to tip | 14 | | spec frame paragraph and intent | 2 | stated range, value defaulted |
| three solids, no fused bodies | 1 solid for this body | | spec header | exact | stated (assembly-level) |
| mesh with wheel at centre distance 60, zero interference, flank gap <= 0.15 | | mm | spec Motion row | | open (assembly-level) |
| tooth profile vs independent involute p95 <= 0.1 | 0.1 | mm | spec scoring paragraph | | scorer-side, not encoded |

## 4. Coordinate frame, scale, and measurement method

Origin at the bottom-face centre on the gear axis. +z is the gear axis (bottom face z = 0 to top face z = 8); +x runs through the centre line of the tooth centred on +x (toward the wheel axis in the assembly); +y completes the right-handed frame. Datum A is the bottom face z = 0, datum B the bore axis x = y = 0, datum C the plane y = 0 (the +x tooth's mirror plane). This is the spec's own frame (pinion axis at the origin, +x toward the wheel, z up, gear bottoms at z = 0), so the assembly joint places the part with the identity. No images or meshes: every value is read from the text table or derived from it.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| toothCount | 20 | 0.001 | stated | spec table |
| gearModule | 2 | 0.001 | stated | spec table |
| pressureAngle | 20 | 0.001 | stated | spec table |
| profileShift | 0 | 0.001 | stated | spec table |
| addendumCoeff | 1.0 | 0.001 | stated | spec table |
| dedendumCoeff | 1.25 | 0.001 | stated | spec table |
| faceWidth | 8 | 0.01 | stated | spec table; edit test +2 gives volume +2 x 1193.388 = +2386.78, bbox z +2; sweep 6, 8, 10 (feasible faceWidth > 4 keeps the z = 4 checks inside the part; the part itself needs faceWidth > 0, delta -8 must fail an assert) |
| boreDiameter | 6 | 0.01 | stated | spec table |
| backlashThinning | 0.05 | 0.001 | stated | spec table; edit test +0.05 rotates each flank a further 0.05 / 40 = 0.00125 rad, volume change = -toothCount x 0.00125 x (tipRadius^2 - rootRadius^2) x faceWidth = -20 x 0.00125 x 177.75 x 8 = -35.55; feasible 0 <= backlashThinning < 1.2634 (tip land 2 psiTip tipRadius > 0), delta +1.5 must fail an assert |
| flankSamples | 14 | 2 | defaulted | middle of the stated 12-16 range; a spline through the samples is recommended |
| pitchRadius | 20 | 0.001 | derived | toothCount x gearModule / 2 |
| baseRadius | 18.79385 | 0.001 | derived | pitchRadius x cos(pressureAngle) |
| tipRadius | 22 | 0.001 | derived | pitchRadius + (addendumCoeff + profileShift) x gearModule |
| rootRadius | 17.5 | 0.001 | derived | pitchRadius - (dedendumCoeff - profileShift) x gearModule |
| pitchToothThickness | 3.09159 | 0.001 | derived | pi x gearModule / 2 + 2 x profileShift x gearModule x tan(pressureAngle) - backlashThinning |
| half tooth angle at pitch psiP | 0.077290 rad | | derived | pitchToothThickness / (2 pitchRadius) |
| half tooth angle at base psiB | 0.092194 rad | | derived | psiP + inv(pressureAngle), inv(a) = tan a - a; the radial segment below the base circle sits at +-psiB |
| half tooth angle at tip psiTip | 0.030335 rad | | derived | psiB - inv(acos(baseRadius / tipRadius)); tip land 1.3348 |
| section area at z = 4 | 1193.388 | 0.2 % | derived | pi 17.5^2 - pi 3^2 + 20 x 12.9775 (tooth area above the root circle, numerical integral of 2 psi(r) r dr) |
| volume | 9547.10 | 20 | derived | faceWidth x section area; the 20 mm^3 band still catches a missing backlash (35.55) |
| surface area | 4642.0 | 1 % | derived | 2 x 1193.388 + 8 x 281.904 (perimeter: 40 flanks of 1.29385 radial + 3.4797 involute arc, 20 tip arcs of 1.3348, 20 root arcs of 1.8912, bore 18.850) |
| centre of mass | [0, 0, 4] | 0.05 | derived | balanced polar pattern, mid face width |
| envelope | [-22, -22, 0] to [22, 22, 8] | 0.05 | derived | teeth sit on 0, 90, 180 and 270 deg (multiples of 18 deg), so tip arcs reach +-22 in x and y |
| blockout band | 9300 to 12170 | | derived | from the finished gear (9547) minus about 2.5 % up to a full tip-radius disk (12164.25; 11938.05 with the bore) |
| probes | teeth (20, 0, 4) etc., spaces (19.7538, +-3.1287, 4) | | derived | pitch-circle points on tooth and space centre lines; about 1.5 mm from the nearest flank, 4 mm from the end faces |

## 6. Defaults retained

- flankSamples = 14, the middle of the stated 12-16 range; the scorer compares the flank against an independent involute (p95 <= 0.1), so a spline through the samples is safer than a polyline.
- Material, density and process stay null: the spec states none and no mass claim is made.
- Symmetry band on y = 0 uses the pipeline default (no tighter band is stated).

## 7. Unrepresentable or low-confidence features

- The mesh with the wheel (centre distance 60, zero interference and a flank gap of at most 0.15 over a full pitch, tip clearance 0.5) needs the wheel body and is checked at assembly level, not in this contract.
- The scorer's tooth-profile comparison against an independently generated involute (p95 <= 0.1) is evaluator-only; the contract encodes the flank through the section area, volume, surface area, tooth/space probes and the tooth count.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
