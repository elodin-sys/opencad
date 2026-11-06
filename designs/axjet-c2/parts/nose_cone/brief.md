# axjet-c2-nose_cone — design brief

## 1. Intent and configuration

Nose cone of the AXJET-220 compressor module (assembly `axjet-c2`, body `nose_cone`), drafted in its own frame so the assembly can place it by the joints `noseOnInlet` (own [0, 0, 0], axis +z, on the inlet-frame hub front face at assembly z -80) and `starterOnNose` (own [0, 0, -28], axis +z, the starter seat). It is a 2 mm 6061-T6 shell of revolution: a D64 cylinder (own z 0 ... -50) and a tangent ogive (arc radius 35.140625) to a closed sharp tip at z -85. It houses the Ø50 x 35 starter motor, which bolts to the front face of an internal 3 mm bulkhead (z -28 ... -25, D12 shaft hole, 4 x M3 on PCD 30). An inner rear lip (z -3 ... 0, r 26 to the wall) carries 4 x M3 clearance holes on PCD 56 into the hub. The authoritative source is the AXJET design and implementation guide (sections 3.2, 8.3, 11, 14.1). Single solid, turned and milled.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/axjet_design_and_implementation_guide.md | text | authoritative | c40b531fa23522311faeef914583f07ccabf09f123bd24fbb9fe16b467501490 | 3.2 flow-path stations (tip -165, cylinder Ø64 -130 ... -80, hub r 32); 8.3 starter (Ø50 x 35 body z -143 ... -108, bulkhead z -108 ... -105, clutch z -105 ... -95); 11 material 6061-T6, turning + milling; 14.1 nose-cone row (2 mm wall, 3 mm bulkhead, Ø12 shaft hole, 4 x M3 motor pattern, 4 x M3 to the hub) and joints |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| outer cylinder diameter, flush with hub r 32 | 64 | mm | guide 3.2, 14.1 | 0.01 | stated |
| cylinder span (assembly -80 ... -130) | 0 ... -50 | mm | guide 3.2, 14.1 | 0.01 | stated |
| tangent ogive to the tip (assembly -165) | -50 ... -85 | mm | guide 3.2, 14.1 | 0.01 | stated |
| wall thickness, closed tip | 2 | mm | guide 14.1 | 0.01 | stated |
| bulkhead (assembly -108 ... -105) | z -28 ... -25 | mm | guide 8.3, 14.1 | 0.01 | stated |
| starter shaft hole | Ø12 | mm | guide 14.1 | 0.01 | stated |
| starter mounting pattern | 4 x M3 (D3.4 on PCD 30) | mm | guide 14.1 (count, thread); size and PCD inferred | 0.1 / 0.5 | stated count, inferred size |
| hub screws | 4 x M3 (D3.4 on PCD 56) | mm | guide 14.1 (count, thread); size and PCD inferred | 0.1 / 0.5 | stated count, inferred size |
| rear lip | z -3 ... 0, r 26 to the wall | mm | intent (inferred) | 0.2 / 0.5 | inferred |
| starter keep-out | Ø50 x 35, own z -63 ... -28 | mm | guide 8.3, 14.1 | 0.01 | stated |
| inner wall clear of the starter | >= 2 | mm | intent | min_gap 2.0 | stated |
| material, density | 6061-T6, 2700 | kg/m3 | guide 11, 14.1 | - | stated |

## 4. Coordinate frame, scale, and measurement method

Origin on the engine axis at the rear face (the face on the inlet-frame hub front face, assembly z -80). Axes parallel to the assembly axes: +x up, +y completing the right-handed set, +z along the axis rearward with the flow, so the cone occupies z -85 ... 0 and assembly z = own z - 80. Datums: A = rear face z 0; B = engine axis; C = bulkhead front face z -28. No images or meshes exist; every number is transcribed from the guide's text and tables with the -80 mm frame shift, and the ogive radius is computed from the tangent-ogive relation rho = (R^2 + L^2) / (2R) with R = 32, L = 35. The ogive arc centre lies at r = R - rho = -3.140625 (across the axis) and z = -50, so the arc meets the axis at z -85 and is tangent to the cylinder at z -50. The inner ogive is the same arc offset 2 mm inward (radius 33.140625, same centre); it reaches the axis at z -82.991, leaving a solid tip 2.009 mm long. Bolt patterns are clocked with their first hole on +x (the guide's convention for flanges and struts).

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| outerDiameter | 64 | 0.01 | stated | guide 3.2 / 14.1 |
| cylinderLength | 50 | 0.01 | stated | -80 - (-130); edit +10 adds pi(32^2 - 30^2) 10 = 3895.57 mm3, bbox z +10; sweep 50 / 55 / 60 inside the feasible interval [49.66, inf) (starter clearance >= 2); infeasible -30 (20 mm: the bulkhead plane z -28 lies past the cylinder and the starter pierces the ogive), the part asserts cylinderLength >= -bulkheadFrontZ |
| ogiveLength | 35 | 0.01 | stated | -130 - (-165) |
| ogiveRadius | 35.140625 | 0.001 | derived | ((outerDiameter / 2)^2 + ogiveLength^2) / outerDiameter = 2249 / 64 |
| wallThickness | 2 | 0.01 | stated | guide 14.1; edit -0.5 removes pi(30.5^2 - 30^2) 44 = 4181.5 from the two exposed bore spans plus 3000.7 from the inner ogive growing (same centre, radius 33.640625, quadrature of pi r(z)^2) = -7182.2 mm3, bbox unchanged; bulkhead and lip fill to the wall so they add nothing; infeasible -2 (no wall) and +6 (inner r 24 inside the starter r 25), the part asserts wallThickness > 0 and outerDiameter/2 - wallThickness - starterDiameter/2 >= starterClearance |
| bulkheadFrontZ | -28 | 0.01 | stated | guide 8.3: -108 + 80 |
| bulkheadThickness | 3 | 0.01 | stated | guide 14.1 (-105 - (-108)) |
| shaftHoleDiameter | 12 | 0.01 | stated | guide 14.1; edit +2 removes pi(7^2 - 6^2) 3 = 122.52 mm3 |
| starterBoltCount | 4 | 0.5 | stated | guide 14.1 |
| starterBoltDiameter | 3.4 | 0.1 | inferred | M3 clearance, ISO 273 medium |
| starterBoltPcd | 30 | 0.5 | inferred | typical M3 face pattern of a Ø50 outer-rotor motor (intent: inferred) |
| rimBoltCount | 4 | 0.5 | stated | guide 14.1 |
| rimBoltDiameter | 3.4 | 0.1 | inferred | M3 clearance, ISO 273 medium |
| rimBoltPcd | 56 | 0.5 | inferred | centred on the hub face between its Ø52 bore and r 32; hole spans r 26.3 ... 29.7 inside the lip |
| lipThickness | 3 | 0.2 | inferred | intent z -3 ... 0 |
| lipInnerDiameter | 52 | 0.5 | inferred | intent r 26, equal to the hub bore Ø52 H6 |
| starterDiameter | 50 | 0.01 | stated | guide 8.3 (assert input only) |
| starterLength | 35 | 0.01 | stated | guide 8.3: -108 - (-143) (assert input only) |
| starterClearance | 2 | 0.01 | stated | intent (assert input only) |

| acceptance value | expected | formula / evidence |
|---|---|---|
| volume | 42110.98 mm3 | wall pi(32^2 - 30^2) 50 = 19477.87; ogive shell 72833.74 - 60236.89 = 12596.85 (pi integral of r^2, r = sqrt(rho^2 - x^2) + R - rho); bulkhead 3 pi(30^2 - 6^2 - 4 x 1.7^2) = 8034.06; lip 3 pi(30^2 - 26^2 - 4 x 1.7^2) = 2002.20 |
| surface area | 38892.07 mm2 | outer cylinder 2 pi 32 50 = 10053.10; outer ogive 2 pi rho (L + (R - rho) theta) = 6700.64; inner ogive (same formula, rho - 2, x_tip 32.991) = 5904.59; bores 2 pi 30 44 = 8293.81; bulkhead 2 x 2678.02 + hole walls 36 pi + 40.8 pi = 5597.31; lip faces 667.40 + 1056.96 + bore 2 pi 26 3 + hole walls 40.8 pi = 2342.62 |
| centre of mass | (0, 0, -36.547) | moments: wall -25, bulkhead -26.5, lip -1.5, ogive shell by quadrature; four-fold patterns keep x = y = 0 |
| mass | 0.114 kg | 42110.98 mm3 x 2700 kg/m3 (guide budget: inlet frame + nose cone 1.5 kg) |
| s_cyl (z -40) | 389.56 mm2, 1 loop, 1 hole | pi(32^2 - 30^2) |
| s_bulk (z -26.5) | 3067.58 mm2, 1 loop, 5 holes | pi(32^2 - 6^2 - 4 x 1.7^2) |
| s_lip (z -1.5) | 1056.96 mm2, 1 loop, 5 holes | pi(32^2 - 26^2 - 4 x 1.7^2) |
| s_ogive (z -70) | 380.31 mm2, 1 loop, 1 hole | outer r 25.753, inner r 23.285 |
| s_tip (z -84) | 103.50 mm2, 1 loop, 0 holes | solid disc r 5.740 (cavity ends at z -82.991) |
| faces | rearFace z 0 + 1056.96; bulkheadFront z -28 - (position only, pinned); bulkheadRear z -25 + 2678.02; lipFront z -3 - 667.40 | annulus areas minus the holes |
| starter clearance | 2.142 mm (>= 2.0) | corner (r 25, z -63) to the inner arc: 33.140625 - sqrt(28.140625^2 + 13^2); radial gap 2.344; 5.0 at the bore; hardware cylinder stops at z -30.5 so the bolted seat is not scored |
| blockout band | 226700 ... 240700 mm3 | envelope-only solid of revolution of the outer profile: pi 32^2 50 + 72833.74 = 233683 mm3, +-3 %; it fills the full bbox (-32 ... 32, -32 ... 32, -85 ... 0) |

## 6. Defaults retained

- Envelope tolerance 0.05 mm and section/face area tolerances of 1 % (2-3 % at the ogive and tip sections, where small areas amplify tessellation error) are digital comparison thresholds, not manufacturing tolerances.
- Wall thickness check at p05 >= 1.9 mm: the 0.1 mm allowance absorbs ray sampling at hole edges and the tip; the model itself is 2.0 mm.
- Volume tolerance 0.5 %, surface area 1 %, centre of mass 0.2 mm: the geometry is fully analytic.
- release_status `reconstruction` kept from the template.

## 7. Unrepresentable or low-confidence features

- Starter wire passage through the bulkhead (guide 8.3) is not dimensioned and not modelled.
- Hole sizes, both pitch circles, the rear lip and the hole clocking are inferred (see section 5); the hub and motor drawings must confirm them.
- The lip bore D52 is assumed to clear the nose nut, clutch cup (assembly z -95 ... -75) and needle clutch (z -105 ... -95, behind the bulkhead), whose diameters the guide does not give.
- No tip radius, hub pilot spigot, screw counterbores or edge breaks are stated; the tip is sharp and all edges are square.
- The 2 mm starter clearance is met with only 0.14 mm margin at the starter's front corner; edits that shorten the cylinder below 49.66 mm or thicken the wall break it.
- Changed (revision 2, reviewer notes): the starterBolts feature verifies the s_bulk section (1 loop, 5 holes) instead of a `count` of 5 on it, which scored loops and contradicted the section; no geometry, parameter or intent change.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
