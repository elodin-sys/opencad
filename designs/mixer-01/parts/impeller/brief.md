# mixer-01-impeller — design brief

## 1. Intent and configuration

Four-blade paddle impeller of the sealed magnetic-drive mixer `mixer-01`, one acetal solid (1410 kg/m3) modelled in its own frame. A D12.0 x 10.0 hub carries a D8.0 through bore that rides on the housing's fixed D6.0 pin (1.0 radial clearance); four flat radial blades, 2.0 thick and centred on their radius lines at 0, 90, 180 and 270 deg, run from the hub (roots merged at radius 6.0) to arc tips on radius 20.0 over z 1..9. The bore and the bottom face run on the pin; the whole outer surface is the rotating wetted wall of the water domain. The assembly joint `impellerSpin` (revolute) attaches at own-frame [0, 0, 0], axis [0, 0, 1]. Authoritative source: `sources/mixer-01-spec.md`. No fillets or chamfers are stated.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/mixer-01-spec.md | text | authoritative | 7c08f09900a1078122226978351d2ff7878b3adda1dc49b70bada1a4dcf2a8a1 | Dimensions table (impeller hub and blades rows), Frame, Placement, Motion; units mm |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| one solid | 1 | count | intent | exact | stated |
| hub outer diameter, z range | 12.0, z 0..10 | mm | spec Dimensions, Impeller hub | 0.01 | stated |
| through bore on the axis | D8.0 | mm | spec Dimensions, Impeller hub | 0.01 | stated |
| radial clearance on the D6.0 pin | 1.0 | mm | spec Dimensions / intent | 0.1 (clearance band) | stated |
| bottom face above the housing floor when placed | 1.0 | mm | spec Placement / intent | 0.1 (clearance band) | stated |
| blades: count and angles | 4 at 0, 90, 180, 270 | deg | spec Dimensions, Impeller blades | exact | stated |
| blade thickness (tangential, centred) | 2.0 | mm | spec Dimensions, Impeller blades | 0.01 | stated |
| blade span | r 6.0 (merged root) to tip arc r 20.0 | mm | spec Dimensions, Impeller blades | 0.01 | stated |
| blade z range | z 1..9 (8.0 tall) | mm | spec Dimensions, Impeller blades | 0.01 | stated |
| bounding box | x -20..20, y -20..20, z 0..10 | mm | intent | 0.05 | stated |
| volume | about 1525.6 (hub 628.3, blade 224.3 each) | mm3 | intent | 0.2 % | stated, re-derived |
| fillets or chamfers | none stated | | intent | | open |

## 4. Coordinate frame, scale, and measurement method

Origin at the centre of the hub's bottom face on the rotation axis; +z along the rotation axis from the bottom face (z = 0) to the top face (z = 10); +x along blade 1's radius line (blade 1 centred on y = 0, tip at x = 20); +y right-handed, blade 2 along +y. Datums: A the hub bottom face z = 0, B the bore axis x = y = 0, C the blade 1 mid-plane y = 0. This is the impeller frame stated in the spec's Frame section; the assembly places it at assembly (0, 0, 1). The only source is text: every dimension is quoted from the spec's Dimensions table, no image or mesh was measured and no scale was established. The pin and floor keep-outs are the spec's housing geometry transformed into this frame (z_impeller = z_assembly - 1).

## 5. Measurement and inference record

Notation: A(R, w) = w*sqrt(R^2 - w^2) + R^2*asin(w/R), the area of the strip |y| <= w inside radius R for x > 0; blade plan area = A(20, 1) - A(6, 1) = 39.98333 - 11.94421 = 28.03912.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| hubOuterDiameter | 12.0 mm | 0.01 | stated | spec Dimensions, Impeller hub |
| hubHeight | 10.0 mm | 0.01 | stated | spec Dimensions, Impeller hub (z 0..10); edit +1: volume +20*pi = +62.832, bbox [0, 0, +1], blades held at z 1..9 |
| boreDiameter | 8.0 mm | 0.01 | stated | spec Dimensions, Impeller hub |
| bladeCount | 4 | 0.1 | stated | spec Dimensions, Impeller blades (0, 90, 180, 270 deg) |
| bladeThickness | 2.0 mm | 0.01 | stated | spec Dimensions, Impeller blades; edit +1: 4*8*[A(20,1.5) - A(6,1.5) - 28.03912] = 4*8*14.09388 = +451.00, bbox unchanged (tips stay on R20); feasible 0 < t < 6*sqrt(2) = 8.49 (adjacent blades must meet inside the hub); sweep [1.5, 2.0, 3.0]; infeasible delta -2 (t = 0) |
| bladeTipRadius | 20.0 mm | 0.01 | stated | spec Dimensions, Impeller blades; edit +1: 4*8*[A(21,1) - A(20,1)] = 32*2.00079 = +64.03, bbox [+2, +2, 0]; feasible R > hubOuterDiameter/2 = 6 (24 leaves 1.0 to the D50 chamber); sweep [14, 20, 24]; infeasible delta -15 (R = 5 inside the hub) |
| bladeBottomZ | 1.0 mm | 0.01 | stated | spec Dimensions, Impeller blades (z 1..9) |
| bladeHeight | 8.0 mm | 0.01 | stated | spec Dimensions, Impeller blades (8.0 tall) |
| volume | 1525.57 mm3 | 0.2 % | derived | hub pi*(36-16)*10 = 628.32 + 4*8*28.03912 = 897.25; intent says about 1525.6 |
| surface area | 1877.79 mm2 | 1 % | derived | hub outer 120*pi - 4*96*asin(1/6) = 312.69; bore 80*pi = 251.33; hub annuli 40*pi = 125.66; per blade 2*28.039 + 16*(sqrt(399) - sqrt(35)) + 320*asin(0.05) = 297.03, x4 = 1188.11 |
| centre of mass | (0, 0, 5) | 0.05 | derived | four-fold symmetry; hub and blades both centred at z = 5 |
| section midZ (z = 5) | 174.988, 1 loop, 1 hole | 1 % | derived | 20*pi + 4*28.03912 |
| sections lowZ (z = 0.5), highZ (z = 9.5) | 62.832, 1 loop, 1 hole | 1 % | derived | hub annulus only (blades are z 1..9) |
| section bladeCutX (x = 13) | 16.0, 1 loop | 1 % | derived | 2.0 * 8.0 |
| section axialY (y = 0.5) | 264.444, 2 loops | 1 % | derived | 2*(10*(sqrt(35.75) - sqrt(15.75)) + 8*(sqrt(399.75) - sqrt(35.75))); the through bore splits it |
| faces hubBottom / hubTop | z 0 (-) / z 10 (+), 62.832 each, centre (0, 0) | 1 % | derived | hub annulus 20*pi |
| faces bladeTopPx / bladeBottomPx | z 9 (+) / z 1 (-), 28.039, centre (12.982, 0) | 1 % | derived | centroid x = 364 / 28.03912 (first moment of the blade strip = 182*2) |
| faces bladeTops / bladeBottoms (sum) | 112.156 each | 1 % | derived | 4 * 28.03912 |
| cylinder bore | D8.0 hole on the axis | default | stated | no length pinned so the hubHeight edit leaves the interface intact; through-ness from axialY and lowZ/highZ |
| cylinder hubOuter | D12.0 pin, z 0..10 | default | stated | spec |
| cylinder bladeTips | R20.0 pin, z 1..9 | default | stated | spec (tips on radius 20.0) |
| dimensions tipSpanX / tipSpanY | 40.0 | 0.05 | derived | 2 * bladeTipRadius |
| dimensions hubSpanZ / bladeSpanZ | 10.0 / 8.0 | 0.05 | stated | spec |
| clearances pinClearance / floorGap | 1.0 (band 0.9..1.1) | 0.1 | stated | bore radius 4 - pin radius 3; floor top at impeller z = -1 |
| thickness wall | p05 >= 1.9 | | derived | blades 2.0, hub wall (12 - 8)/2 = 2.0 |
| symmetry mirrorX / mirrorY | x = 0, y = 0, default bands | | derived | blades centred on their radius lines at 0/90/180/270 deg |
| blockout band | 1480..2100 mm3 | | derived | solid hub pi*36*10 = 1130.97 + blades 897.25 = 2028.2; with bore 1525.6 |

## 6. Defaults retained

- Digital tolerances 0.01 mm on parameters and 0.05 mm on the envelope, plane positions and dimensions: the spec states no manufacturing tolerances.
- Clearance bands 0.9..1.1 around the stated 1.0 gaps, to absorb tessellation of the D8 bore.
- Thickness floor 1.9 at the 5th percentile for the stated 2.0 walls (chordal tessellation error).
- `process` left null (not stated); `release_status: reconstruction` kept from the template.

## 7. Unrepresentable or low-confidence features

- The wetted-wall role (the whole outer surface rotating) is a CFD boundary designation, not a geometric check; the `wettedWall` interface pins only the balance symmetry.
- The pin clearance and floor gap are assembly facts; they are encoded as keep-outs in the impeller frame assuming the spec's placement at assembly (0, 0, 1).
- Tip shape is inferred from "tips on radius 20.0" and the stated per-blade volume (arc tip 224.31 vs flat tip 224.45); the difference is below the volume tolerance, so the `bladeTips` cylinder is what enforces it.
- No edge breaks are modelled (none stated).

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
