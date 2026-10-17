# compound-train-pinion — design brief

## 1. Intent and configuration

Input spur pinion of the `compound-train` assembly (motor-driven, revolute joint `pinionSpin` about +z at the assembly origin), drafted in its own frame: axis +z through the origin, bottom face z = 0, top face z = 8. 20 teeth, module 2, pressure angle 20 deg, zero profile shift, addendum 1.0 m and dedendum 1.25 m (pitch radius 20, tip radius 22, root radius 17.5, base radius 18.794). Involute flanks from the involute equations (12-16 points per flank, base circle to tip), radial flanks from the base circle down to the root circle, every tooth thinned by 0.05 mm at the pitch circle (circular tooth thickness 3.0916 mm, 0.10 mm backlash per mesh), a tooth centred on +x, and a D6 through bore on the axis. It stands on the base plate top over the plate's D6 hole and meshes with the idler's 40-tooth gear at 60 mm centre distance. Authoritative source: `sources/compound-train-spec.md` (text only, no drawings). Single solid.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/compound-train-spec.md | text | authoritative | e2734c43ae1d2aa36320d0b7680e21616422e902b471b3eb98295e3292296af5 | whole-train spec; pinion row, gear rules (module, pressure angle, shift, addendum/dedendum, backlash), part-frame rules and tooth phase |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| tooth count | 20 | - | spec table, Input pinion | exact | stated |
| module | 2 | mm | spec table, Module | 0.001 | stated |
| pressure angle | 20 | deg | spec table | 0.01 | stated |
| profile shift | 0 | - | spec table | 0.001 | stated |
| addendum / dedendum | 1.0 m / 1.25 m | - | spec table | 0.001 | stated |
| tooth thinning at pitch circle | 0.05 (0.10 backlash per mesh) | mm | spec table, Circular backlash | 0.001 | stated |
| face width, z 0..8 | 8 | mm | spec table, Input pinion; part-frame rule | 0.01 | stated |
| bore, through on axis | D6 | mm | spec table, Input pinion | 0.01 | stated |
| involute flank points | 12-16 per flank | - | spec, flank construction paragraph | range | stated (range) |
| radial flank base to root | yes | - | intent | - | stated |
| tooth centred on +x (own frame) | 0 | deg | spec part-frame rule and tooth phase | probes + mirror planes | stated |
| frame: axis +z through origin, bottom face z = 0 | - | - | spec part-frame rule; joint pinionSpin at [0, 0, 0] axis [0, 0, 1] | - | stated |
| single solid | 1 | - | spec "four separate solids", this is one of them | exact | stated |
| mesh with idler 40T at 60 mm centre distance | 60 | mm | spec table, Centre distances | assembly-level | stated (checked in the assembly) |
| material, process, bore fit | - | - | not stated | - | open |

## 4. Coordinate frame, scale, and measurement method

Origin on the gear axis in the bottom-face plane; +z along the axis from the bottom face (z = 0) to the top face (z = 8); +x radial through the centre of one tooth; +y = +z × +x. Datum A is the bottom face (seat on the plate), datum B the axis, datum C the plane y = 0 through the tooth on +x. This is the part frame the spec prescribes for every gear and the frame the assembly joint `pinionSpin` uses ([0, 0, 0], axis [0, 0, 1]). With 20 teeth at 18 deg pitch, teeth are also centred on -x, +y and -y (90 deg = 5 pitches), so the envelope is exactly [-22, -22, 0] to [22, 22, 8] and the tooth pattern is mirror-symmetric about x = 0 and y = 0. No images or meshes: every value is stated in the text or derived from stated values by the standard involute relations.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| teethCount | 20 | 0.01 | stated | spec table |
| gearModule | 2 mm | 0.001 | stated | spec table |
| pressureAngle | 20 deg | 0.01 | stated | spec table |
| profileShift | 0 | 0.001 | stated | spec table |
| addendumCoeff | 1.0 | 0.001 | stated | spec table |
| dedendumCoeff | 1.25 | 0.001 | stated | spec table |
| toothThinning | 0.05 mm | 0.001 | stated | spec table (half of 0.10 mm backlash) |
| faceWidth | 8 mm | 0.01 | stated | spec table; edit test +2, sweep 6/8/10, infeasible -8 (zero width) |
| boreDiameter | 6 mm | 0.01 | stated | spec table; edit test +2, sweep 4/6/8, infeasible +30 (36 > root diameter 35) |
| flankPoints | 14 | 2 | inferred | spec states 12-16; mid value, tolerance covers the range |
| pitchRadius | 20 mm | 0.001 | derived | gearModule * teethCount / 2 |
| tipRadius | 22 mm | 0.001 | derived | pitchRadius + (addendumCoeff + profileShift) * gearModule |
| rootRadius | 17.5 mm | 0.001 | derived | pitchRadius - (dedendumCoeff - profileShift) * gearModule |
| baseRadius | 18.793852 mm | 0.001 | derived | pitchRadius * cos(pressureAngle) |
| toothThickness | 3.091593 mm | 0.001 | derived | pi * gearModule / 2 + 2 x m tan(alpha) - toothThinning |
| half tooth angle at base circle psi_b | 0.092194 rad | - | derived | toothThickness / (2 pitchRadius) + inv(20 deg), inv(a) = tan a - a = 0.014904 |
| tip half angle psi_a / tip land | 0.030335 rad / 1.3348 mm | - | derived | psi_b - inv(acos(rb / ra)); tooth is not pointed |
| one tooth area above the root circle | 12.9775 mm² | - | derived | psi_b (rb² - rf²) + integral from rb to ra of 2 psi(r) r dr (Simpson, 20000 steps) |
| section area at z = 4 (and top face) | 1193.39 mm² | 0.5 % | derived | pi 17.5² + 20 * 12.9775 - pi 3² |
| volume | 9547.1 mm³ | 0.5 % | derived | 8 * 1193.388 |
| surface area | 4642.0 mm² | 1 % | derived | 2 * 1193.388 + 8 * (263.054 + 6 pi); per-tooth outline = tip 1.3348 + 2 * 1.2939 radial + 2 * 3.4796 involute (rb t²/2, t = 0.6085) + root arc 2.2710 |
| centre of mass | (0, 0, 4) | 0.05 | derived | 20-fold polar symmetry, faceWidth / 2 |
| bbox spans x, y | 44, 44 | 0.05 | derived | 2 * tipRadius (teeth centred on the axes; a chord tip would give 43.980) |
| probes | teeth (±20, 0, 4), (0, ±20, 4) solid; spaces (19.7538, ±3.1287, 4) void; hub (10, 0, 4), (0, 10, 4) solid; bore (0, 0, 4) void | - | derived | pitch points at 1.45 mm (tooth) and 1.50 mm (space) from the flanks |
| faceWidth edit +2 | +2386.78 mm³, bbox +[0, 0, 2] | 2 % | derived | 2 * 1193.388 |
| boreDiameter edit +2 | -175.93 mm³, bbox 0 | 2 % | derived | -pi/4 (8² - 6²) * 8 |
| blockout band | 11700-12250 mm³ | - | derived | gear blank pi 22² * 8 = 12164.25 (11938.05 with the bore) |

Feasible intervals: faceWidth > 0 (sweep 6-10 keeps the z = 4 section inside the part); 0 < boreDiameter < 2 * rootRadius = 35 (sweep 4-8). The model must assert both.

## 6. Defaults retained

- Envelope and dimension tolerance 0.05 mm: covers a chord tip (0.010 mm inside the tip circle) and tessellation.
- Volume and section-area tolerance 0.5 %: covers polyline or spline flanks through 12-16 points (area change well under 1 mm² per section).
- Symmetry bands (mirrorX, mirrorY) left at the evaluator defaults; the source states no tighter band.
- Material, density and process left null: no mass property is claimed.

## 7. Unrepresentable or low-confidence features

- Meshing with the idler (60 mm centre distance, ratio, backlash at most 0.15 mm, zero interference) is an assembly property; this contract pins it through the module, tooth count, tip span, tooth thinning and tooth phase, and the assembly contract checks the mesh itself.
- The exact flank discretisation (12-16 points, polyline or spline) is not encoded beyond `flankPoints`; the gear check and the area tolerances accept any value in the stated range.
- No root fillet, chamfer or bore fit is stated; none is encoded.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
