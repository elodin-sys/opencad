# gear-train-wheel — design brief

## 1. Intent and configuration

40-tooth spur wheel of the `gear-train` assembly (module 2, pressure angle 20 deg, profile shift 0, face width 8, D8 through bore), drafted in its own frame so the assembly can place it on the `wheelSpin` revolute joint (own-frame point [0, 0, 0], axis [0, 0, 1]) at the spec's wheel axis (60, 0). True involute flanks from the base circle to the tip circle, radial from the base circle to the root circle, tip and root arcs, no fillets; each tooth thinned 0.05 at the pitch circle. One tooth is centred on +x; the half-pitch rest angle belongs to the joint. `sources/gear-pair-spec.md` is the only source and is authoritative.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/gear-pair-spec.md | text | authoritative | 0acea6d35513df93499f95e7242721b64488c45819f6e58ebd09ed627fb09d87 | parameter table: module, pressure angle, shift, wheel row, face width, addendum/dedendum, backlash, tooth phase |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| tooth count | 40 | | spec, Wheel row | exact | stated |
| module | 2 | mm | spec, Module | 0.001 | stated |
| pressure angle | 20 | deg | spec | 0.01 | stated |
| profile shift | 0 | | spec | 0.001 | stated |
| face width, z = 0 to 8 | 8 | mm | spec, Face width | 0.01 | stated |
| bore, through on axis | D8 | mm | spec, Wheel row | 0.01 | stated |
| tip / root radius | 42 / 37.5 | mm | spec, Addendum / dedendum | 0.001 | stated (derived) |
| tooth thinning at pitch circle | 0.05 | mm | spec, Circular backlash | 0.001 | stated |
| involute flank, 12-16 samples | 14 | | spec / intent | 2 | stated range |
| tooth centred on +x | 0 | deg | intent | probes | stated |
| profile p95 vs involute <= 0.1; mesh sweep | | mm | spec | | open (assembly level) |

## 4. Coordinate frame, scale, and measurement method

Origin on the gear axis in the bottom face (z = 0); +z up the axis to the top face z = 8; +x through the centre of one tooth; +y completes a right-handed frame, and y = 0 is that tooth's mid-plane. Datums: A bottom face, B bore axis, C plane y = 0. No images or meshes; every value comes from the text table and involute geometry.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| toothCount | 40 | 0.01 | stated | spec Wheel row |
| gearModule | 2 | 0.001 | stated | spec Module |
| pressureAngle | 20 deg | 0.01 | stated | spec |
| profileShift | 0 | 0.001 | stated | spec |
| addendumCoef / dedendumCoef | 1.0 / 1.25 | 0.001 | stated | spec |
| faceWidth | 8 | 0.01 | stated | spec |
| boreDiameter | 8 | 0.01 | stated | spec |
| toothThinning | 0.05 | 0.001 | stated | spec backlash row |
| flankPoints | 14 | 2 | inferred | middle of the stated 12-16 range |
| pitchRadius | 40 | 0.001 | derived | gearModule * toothCount / 2 |
| baseRadius | 37.587705 | 0.001 | derived | pitchRadius * cos(pressureAngle) |
| tipRadius | 42 | 0.001 | derived | pitchRadius + (addendumCoef + profileShift) * gearModule |
| rootRadius | 37.5 | 0.001 | derived | pitchRadius - (dedendumCoef - profileShift) * gearModule |
| toothThickness | 3.091593 | 0.001 | derived | gearModule * (pi/2 + 2 profileShift tan(pressureAngle)) - toothThinning |
| half-tooth angle at base / tip | 0.053549 / 0.017486 rad | | derived | psi_b = s/(2 r_p) + inv(20 deg); psi(r) = psi_b - inv(acos(r_b/r)); tip land 1.469 |
| section area (z = 0.5, 4, 7.5; top face) | 4923.58 mm2 | 0.1 % | derived | pi r_f^2 + 40 * 2 int psi(r) r dr - pi 4^2, numeric; 12-16 point polylines lose 0.3-0.8 mm2 (< 0.02 %) |
| volume | 39388.63 mm3 | 0.1 % | derived | 4923.579 * 8 |
| surface area | 14163.76 mm2 | 0.5 % | derived | 2 * 4923.579 + 8 * (514.443 + 2 pi 4) |
| centre of mass | (0, 0, 4) | 0.05 | derived | 40-fold symmetry, half face width |
| faceWidth edit +2 | +9847.16 mm3, bbox +2 z | 1 % | derived | 4923.579 * 2; sweep 6, 8, 10 (feasible faceWidth > 0); infeasible -8 (faceWidth 0) |
| toothThinning edit +0.05 | -71.55 mm3, bbox 0 | 5 % | derived | flanks rotate rigidly: -40 * (0.05/40) * (42^2 - 37.5^2)/2 * 8; feasible while tip land > 0 (thinning < 1.449); infeasible +2.0 |
| probes | solid (±39, 0), (0, ±39); void (39.8767, ±3.1384) at z 4 | | derived | tooth centres; space centres at ±4.5 deg on r 40, about 1.5 mm from each flank |
| blockout band | 42000-44500 mm3 | | derived | tip-circle disc r 42 x 8 = 44334 (43932 with bore) |

## 6. Defaults retained

Envelope tolerance 0.05 and symmetry bands 0.1 max / 0.05 p95 follow the exemplar. Material, density and process stay null because the spec states none. Release status stays `reconstruction` from the template.

## 7. Unrepresentable or low-confidence features

The involute deviation against an independent involute (p95 <= 0.1 mm) has no reference mesh here. The rotation sweep (zero interference, flank gap <= 0.15 mm) needs the pinion. Both are assembly-level checks. In this contract, the section area (sensitive to 0.05 of tooth thickness), the mirror about y = 0, and the phase probes stand in for them. The bore fit class is not stated.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
