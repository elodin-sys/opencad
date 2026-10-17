# rack-pinion-rack — design brief

## 1. Intent and configuration

Straight module-2 rack of the `rack-pinion` assembly, drafted in its own frame (origin on the pitch line at mid-length, +x along the pitch line, +y toward the tooth tips, bottom face z = 0). A 200 x 9.5 x 8 solid bar (x = -100..100, y = -12..-2.5, z = 0..8) carries 32 straight-flank teeth (module 2, pitch 2 pi, 20 deg flanks, addendum 2, dedendum 2.5, tooth thickness p/2 - 0.05 on the pitch line) centred at x = (k + 1/2) p for k = -16..15, so a tooth space is centred on x = 0. The bottom face slides on the plate top (slider joint `rackSlide` at own-frame [0, 0, 0], axis +x); the flanks mesh with the 20-tooth pinion; the origin space receives the pinion tooth at rest. One solid, no holes. The only source, `sources/rack-pinion-spec.md`, is authoritative.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/rack-pinion-spec.md | text | authoritative | 87f6a8bbc15c559e23899017105cd36ee8b503a6238b00213d3b99103d903561 | assembly spec; rows Module, Pressure angle, Rack, Rack teeth, Rack body, Backlash; paragraphs Part frames and Rest configuration |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| module | 2 | mm | spec table, Module | 0.001 | stated |
| pitch p | 2 pi = 6.283185 | mm | spec table, Module | 0.0005 | stated (derived pi * m) |
| pressure angle / flank angle from the pitch-line normal | 20 | deg | spec table, Pressure angle and Rack teeth | 0.01 | stated |
| tooth count | 32 | - | spec table, Rack | exact | stated |
| tooth centres | x = (k + 1/2) p, k = -16..15; space centred on x = 0 | mm | spec, Part frames | 0.02 (flank planes) | stated |
| addendum / tip line | 2 / y = 2 | mm | spec table, Rack teeth | 0.05 | stated |
| dedendum / root line | 2.5 / y = -2.5 | mm | spec table, Rack teeth | 0.05 | stated |
| tooth thickness on the pitch line | p/2 - 0.05 = 3.091593 | mm | spec table, Rack teeth | 0.001 | stated |
| tip width / root width | 1.635712 / 4.911444 | mm | spec table, Rack teeth | 0.001 | stated |
| length / body span | 200 / x = -100..100 | mm | spec table, Rack; Part frames | 0.05 | stated |
| thickness | 8 (z 0..8) | mm | spec table, Rack | 0.05 | stated |
| body depth below root line / back face | 9.5 / y = -12 | mm | spec table, Rack body | 0.05 | stated |
| slide interface | bottom face z = 0 on the plate top, axis +x | - | spec, Frame and Rest configuration; orchestrator joint rackSlide | exact | stated |
| mesh interface | origin space receives the pinion tooth at rest | - | spec, Rest configuration | 0.02 | stated |
| single solid | 1 | - | spec, three separate solids (no fused bodies) | exact | stated |
| material, density, process | not given | - | - | - | open |

## 4. Coordinate frame, scale, and measurement method

Origin: on the pitch line (y = 0) at the middle of the length (x = 0), in the bottom face (z = 0). +x runs along the pitch line (the sliding direction), +y points toward the tooth tips, +z through the thickness. Datums: A = bottom face z = 0 (slide face), B = pitch line plane y = 0, C = mid-length mirror plane x = 0. This is the part frame the spec states for the rack; the assembly places it with its origin at (0, -20, 0), pitch line tangent to the pinion pitch circle. No images, drawings or meshes exist; every value is read from the text table or derived from it in closed form, so no scale or rectification was needed.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| gearModule | 2 mm | 0.001 | stated | spec table, Module |
| toothCount | 32 | 0.1 | stated | spec table, Rack |
| pressureAngle | 20 deg | 0.01 | stated | spec table, Pressure angle; Rack teeth |
| addendum | 2 mm | 0.01 | stated | spec table, Rack teeth |
| dedendum | 2.5 mm | 0.01 | stated | spec table, Rack teeth |
| backlashThinning | 0.05 mm | 0.005 | stated | spec table, Rack teeth (p/2 - 0.05) and Backlash |
| rackLength | 200 mm | 0.01 | stated | spec table, Rack; Part frames x = -100..100 |
| rackThickness | 8 mm | 0.01 | stated | spec table, Rack |
| bodyDepth | 9.5 mm | 0.01 | stated | spec table, Rack body |
| pitch | 6.283185 mm | 0.0005 | derived | pi * gearModule |
| toothThickness | 3.091593 mm | 0.001 | derived | pitch / 2 - backlashThinning |
| tipWidth | 1.635712 mm | 0.001 | derived | toothThickness - 2 * addendum * tan(pressureAngle) |
| rootWidth | 4.911444 mm | 0.001 | derived | toothThickness + 2 * dedendum * tan(pressureAngle) |
| backOffset | 12 mm | 0.01 | derived | dedendum + bodyDepth (agrees with the stated 12) |
| firstToothX | -97.389372 mm | 0.001 | derived | (0.5 - toothCount / 2) * pitch |
| endLand | 0.154906 mm | 0.001 | derived | rackLength / 2 + firstToothX - rootWidth / 2; must be >= 0 |
| volume | 18971.162 mm3 | rel 0.001 | derived | 8 * (200 * 9.5 + 32 * (1.635712 + 4.911444) / 2 * 4.5) = 8 * 2371.3952 |
| surface area | 9708.07 mm2 | rel 0.002 | derived | 2 * 2371.3952 + 1600 + 2 * 76 + 42.833798 * 8 + 32 * 1.635712 * 8 + 64 * (4.5 / cos 20) * 8 |
| centre of mass | (0, -5.933106, 4) | 0.05 | derived | bar centroid y = -7.25 (area 1900), tooth centroid y = -2.5 + 4.5 * (rw + 2 tw) / (3 (rw + tw)) = -0.625247 (area 471.3952) |
| section midZ (z = 4) | 2371.3952 mm2, 1 loop | rel 0.002 | derived | bar + 32 teeth |
| section pitchLineY (y = 0) | 791.4477 mm2, 32 loops | rel 0.005 | derived | 32 * 3.091593 * 8 |
| section bodyY (y = -5) | 1600 mm2 | rel 0.002 | derived | 200 * 8 |
| section spaceX (x = 0) | 76 mm2 | rel 0.005 | derived | 9.5 * 8 (space, not tooth) |
| section toothX (x = p/2) | 112 mm2 | rel 0.005 | derived | 14 * 8 |
| faces top / bottom | 2371.3952 mm2 at z = 8 / z = 0 | rel 0.002 | derived | profile area; bottom pinned without area |
| face back | 1600 mm2 at y = -12 | rel 0.002 | derived | 200 * 8 |
| faces endNeg / endPos | 76 mm2 at x = -+100 | rel 0.005 | derived | 9.5 * 8 |
| face tips (sum) | 418.7422 mm2 at y = 2 | rel 0.005 | derived | 32 * 1.635712 * 8 |
| face tipK0 | 13.085694 mm2, centre (3.141593, 4) | rel 0.01 | derived | 1.635712 * 8 |
| face rootLands (sum) | 342.6704 mm2 at y = -2.5 | rel 0.005 | derived | (200 - 32 * 4.911444) * 8, includes two 0.154906 end lands |
| face spaceRoot | 10.973932 mm2, centre (0, 4) | rel 0.01 | derived | (pitch - rootWidth) * 8 = 1.371741 * 8 |
| planes spaceFlankNeg / Pos | through (-+1.595796, 0), normals (+-0.939693, 0.342020, 0) | 0.02, 0.2 deg | derived | (pitch - toothThickness) / 2; normal (cos 20, sin 20) |
| planes endFlankNeg / Pos | through (-+98.935169, 0), area 38.3104 | 0.02, 0.2 deg | derived | 15.5 p + toothThickness / 2; flank area 4.5 / cos 20 * 8 |
| dimensions | length 200, depth 14, thickness 8, body 9.5, whole depth 4.5 | 0.05 | stated / derived | spec table |
| void probes | (0, 0, 4), (+-6.283185, 0, 4), (+-94.24778, 0, 4) | - | derived | space centres; 1.4996 mm from both flanks |
| blockout band | 18500 .. 22500 mm3 | - | derived | covers the finished rack (18971) and the full 200 x 14 x 8 box (22400) |

Edit tests (other parameters held fixed):

- `rackLength` +10: the bar grows 5 mm at each end, teeth stay centred: dV = 10 * bodyDepth * rackThickness = +760, bbox +[10, 0, 0]. Feasible for rackLength >= (toothCount - 1) * pitch + rootWidth = 199.6902 (endLand >= 0); sweep [200, 220, 250]; infeasible delta -10 (190: outer teeth overhang the ends) must fail an assert.
- `rackThickness` +2: dV = 2 * 2371.3952 = +4742.79, bbox +[0, 0, 2]. Feasible for rackThickness > 0; sweep [6, 8, 12]; infeasible delta -8 (zero thickness).
- `bodyDepth` +2: back face moves to y = -14: dV = rackLength * 2 * rackThickness = +3200, bbox +[0, 2, 0]. Feasible for bodyDepth > 0 (at 0 the teeth separate into 32 solids); infeasible delta -10.

The pinned interface items (bottom face without area, mirror plane x = 0, the origin-space flank planes without area) are unchanged by all three edits.

## 6. Defaults retained

- `material`, `density_kg_m3`, `process` stay null: the spec gives none and no mass claim is needed.
- `release_status: reconstruction` kept from the template.
- Envelope tolerance 0.05 mm; flank plane tolerance tightened to 0.02 mm because the straight-flank geometry is exact and a missing 0.05 backlash thinning shifts each flank by 0.025.
- Symmetry band for `mirrorX` kept at max 0.1 / p95 0.05 mm (default band, no tighter source).

## 7. Unrepresentable or low-confidence features

- No fillets, chamfers or tip relief are stated; sharp straight-flank corners and square ends are drafted.
- The 0.154906 mm root lands at each end are a consequence of the stated tooth positions and body span, not a stated feature; they are counted in the `rootLands` sum.
- The pinion mesh itself (zero interference through the stroke, transmission ratio 2 pi * 20 / 360 = 0.349066 mm/deg, travel 125.66 mm per revolution) is an assembly-level check and is not encoded in this single-part contract; a centred 200 mm rack offers only about 99.8 mm of teeth on each side of the pinion, so the full-revolution stroke is an open question for the assembly.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
