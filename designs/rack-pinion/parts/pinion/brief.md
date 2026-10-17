# rack-pinion-pinion — design brief

## 1. Intent and configuration

The driven spur pinion of the rack-pinion machine (base plate, pinion, rack; three separate solids). Drafted in its own
frame: axis +z through the origin, bottom face z = 0, face width 8, a tooth centred on +x. 20 teeth, module 2, pressure
angle 20 deg, pitch radius 20, tip 22, root 17.5, base circle 18.794; involute flanks (12-16 points per flank from the
base circle to the tip); every tooth thinned 0.05 mm at the pitch circle (tooth thickness 3.091593); D6 through bore on
the axis. The assembly attaches it by the revolute joint pinionSpin at own-frame point [0, 0, 0], axis +z; it stands on
the plate top, its bore is coaxial with the plate's D6 hole, and at rest its tooth at -90 deg points into the rack's
tooth space at x = 0. The only source, `sources/rack-pinion-spec.md`, is authoritative. One solid.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/rack-pinion-spec.md | text | authoritative | 87f6a8bbc15c559e23899017105cd36ee8b503a6238b00213d3b99103d903561 | parameter table, part frames, rest configuration, backlash rule; no images |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| module | 2 | mm | spec table | 0.001 | stated |
| tooth count | 20 | - | spec table | exact | stated |
| pressure angle | 20 | deg | spec table | 0.01 | stated |
| pitch / tip / root radius | 20 / 22 / 17.5 | mm | spec table | 0.01 | stated |
| base circle | 18.794 | mm | intent (20 cos 20 deg) | 0.001 | stated |
| involute flanks, 12-16 points per flank, base to tip | 14 | points | spec text, intent | 2 | stated range |
| tooth thinning at pitch circle | 0.05 (thickness 3.091593) | mm | spec table (Backlash) | 0.001 | stated |
| face width | 8 (z 0..8) | mm | spec table | 0.01 | stated |
| bore | D6 through, on the axis | mm | spec table | 0.01 | stated |
| tooth centred on +x; tooth at -90 deg | phase | - | spec part frames, rest configuration | symmetry y = 0 | stated |
| bottom face on plate top | z = 0 | mm | spec frame | 0.05 | stated |
| one separate solid | 1 | - | spec ("three separate solids") | exact | stated |
| root shape below the base circle | radial, no fillet | - | not stated | volume 1 % | open |

## 4. Coordinate frame, scale, and measurement method

Origin on the pinion axis in the bottom face; +z along the axis (bottom face z = 0, top z = 8); +x along the centre line of
the phase-reference tooth; +y completes a right-handed frame. Datums: A bottom face z = 0 (seat on the plate), B bore axis
(z axis), C phase plane y = 0. Tooth pitch is 18 deg, so teeth are centred on 0, 90, 180 and -90 deg and spaces on
+-9 deg, +-81 deg, +-99 deg; the bounding box is [-22, -22, 0] to [22, 22, 8] (tips on both axes). All values come from
the text source; there are no images or reference meshes, so nothing was scaled from pixels.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| gearModule | 2 | 0.001 | stated | spec table |
| toothCount | 20 | 0.01 | stated | spec table |
| pressureAngle | 20 deg | 0.01 | stated | spec table |
| pitchRadius | 20 | 0.001 | derived | gearModule * toothCount / 2 (spec states 20) |
| tipRadius | 22 | 0.01 | derived | pitchRadius + gearModule (spec states 22) |
| rootRadius | 17.5 | 0.01 | derived | pitchRadius - 1.25 * gearModule (spec states 17.5) |
| baseRadius | 18.793852 | 0.001 | derived | pitchRadius * cos(pressureAngle) |
| circularPitch | 6.283185 | 0.0001 | derived | pi * gearModule |
| toothThinning | 0.05 | 0.001 | stated | spec Backlash row |
| toothThickness | 3.091593 | 0.0005 | derived | circularPitch / 2 - toothThinning |
| faceWidth | 8 | 0.01 | stated | spec table |
| boreDiameter | 6 | 0.01 | stated | spec table |
| flankPoints | 14 | 2 | inferred | middle of the stated 12-16 range |
| half-angle at pitch / base / tip | 0.077290 / 0.092194 / 0.030335 rad | - | derived | psiP = toothThickness / (2 pitchRadius); psiB = psiP + inv(20 deg), inv(20 deg) = 0.014904; psi(r) = psiB - inv(acos(baseRadius / r)) |
| tip land | 1.335 | - | derived | 2 tipRadius psi(tipRadius); tooth is not pointed |
| tooth area above root | 12.9775 mm2 | - | derived | psiB (rb^2 - rf^2) + integral(rb..ra) 2 psi(r) r dr (numeric) |
| section area A | 1193.39 mm2 | 1 % | derived | pi 17.5^2 + 20 * 12.9775 - pi 3^2 |
| volume | 9547.1 mm3 | 1 % | derived | faceWidth * A |
| surface area | 4642.0 mm2 | 5 % | derived | 2 A + 8 (263.05 outer perimeter + 18.85 bore); per tooth 2 (1.294 radial + 3.479 involute) + 1.335 tip + 2.271 root |
| centre of mass | (0, 0, 4) | 0.05 | derived | rotational symmetry; faceWidth / 2 |
| blockout band | 11700..12300 mm3 | - | derived | tip-radius disc 8 thick: 12164.2 without bore, 11938.1 with the bore |
| edit faceWidth +2 | +2386.78 mm3, bbox +2 z | 2 % | derived | 2 * A; sweep 6, 8, 10 (feasible faceWidth > 0); infeasible -8 (zero width, must assert) |
| edit toothThinning +0.05 | -35.55 mm3, bbox 0 | 10 % | derived | every flank turns by 0.05 / (2 pitchRadius) = 0.00125 rad: 0.00125 (22^2 - 17.5^2) * 20 * 8; feasible thinning below 1.263 (tip land vanishes) |
| probes | teeth at 0, 90, 180, -90 deg on r = 20; spaces at +-9, -81, -99 deg on r = 20 | - | derived | 1.45 mm from the flanks in the tooth, 1.50 mm in the space; r = 18.6 space probe 1.1 mm above the root; r = 16.5 hub probe; bore centre |

Mesh check (analysis, not a contract item): the rack's addendum 2 is below r_p sin^2(20 deg) = 2.34, so the rack flank
reaches the pinion only down to r = 18.82 (above the base circle); tracing the rack tip corner (tip half-width 0.818) in the
pinion frame with the driving flank in contact, it touches the flank between r = 18.82 and the base circle and moves
into the space below it, so radial flanks below the base circle do not interfere.

## 6. Defaults retained

- Root shape: flanks continue radially from the base circle to the root circle, no fillet (not stated; the simplest
  shape that clears the rack; a small fillet stays inside the 1 % volume and 5 % area tolerances).
- flankPoints 14, inside the stated 12-16.
- Material, density and process left null (not stated; no mass claim).
- Symmetry band for y = 0 left at the evaluator defaults (the sources state no band).

## 7. Unrepresentable or low-confidence features

- The involute profile itself is checked indirectly (section area, gear tooth count/module, probes, symmetry); the
  zero-interference revolution with the rack is an assembly-level check, not part of this contract.
- The joint phase is pinned by the y = 0 mirror symmetry and the solid/void probes on the teeth and spaces, not by an
  angle measurement.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
