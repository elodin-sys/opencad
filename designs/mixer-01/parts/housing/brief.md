# mixer-01-housing — design brief

## 1. Intent and configuration

Housing of the mixer-01 sealed magnetic-drive paddle mixer, one polypropylene solid (900 kg/m3) modelled in the assembly frame. A closed cylindrical chamber (inner radius 25.0, z 0..25) with a 3.0 side wall (outer radius 28.0, z -3..28), a 3.0 sealed floor (z -3..0) and a 3.0 lid (z 25..28); an axial D16/D12 inlet tube z 28..48 whose D12 bore continues through the lid (z 25..48); a radial D14/D10 outlet tube on y = 0, z = 12.5 from the side wall's outer face to x = 58 whose D10 bore continues through the side wall; a fixed D6 pin on the axis from z = 0 to a flat top at z = 12, fused into the same solid. No fillets or chamfers. `sources/mixer-01-spec.md` is authoritative. The impeller, motor and water are separate designs of the assembly `mixer-01`; this contract only locates their joints (impellerSpin at [0, 0, 1], motorMount at [0, 0, -3], waterFixed at [0, 0, 0], all axis +z).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/mixer-01-spec.md | text | authoritative | 7c08f09900a1078122226978351d2ff7878b3adda1dc49b70bada1a4dcf2a8a1 | Frame, Dimensions, Placement, Motion and Fluid sections; mm |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| one solid | 1 | - | spec, Bodies 1 | exact | stated |
| chamber inner radius / height | 25 / 25 (z 0..25) | mm | spec, Dimensions | 0.05 | stated |
| side wall, floor, lid thickness | 3 / 3 / 3 | mm | spec, Dimensions | 0.05 | stated |
| inlet tube ID / OD, z range, open end | 12 / 16, z 28..48, z = 48 | mm | spec, Dimensions | 0.05 | stated |
| outlet tube ID / OD, axis, open end | 10 / 14, y = 0 z = 12.5, x = 58 | mm | spec, Dimensions | 0.05 | stated |
| pin diameter, z range | 6, z 0..12 | mm | spec, Dimensions | 0.05 | stated |
| sealed floor (no shaft through it) | full disk at z -1.5 | - | spec, intro and Fluid | loops 1 holes 0 | stated |
| impeller space clear (tips r 20, hub z 1..11, 1.0 on the pin) | void probes | mm | spec, Placement and Motion | >= 1 mm from walls | stated |
| water path inlet -> chamber -> outlet | connected | - | spec, Fluid | voxel pitch 1.0 | stated |
| bounding box | x -28..58, y -28..28, z -3..48 | mm | intent | 0.05 | stated |
| volume | about 31076 | mm3 | intent | 0.2 % | stated, re-derived 31075.58 |

## 4. Coordinate frame, scale, and measurement method

Origin at the centre of the chamber floor's inside face; +z up the impeller axis; +x toward the outlet; +y completes a right-handed frame, and the part is mirror-symmetric about y = 0. Datums: A the chamber floor z = 0, B the axis x = y = 0, C the floor underside z = -3 (motor seat), D the mirror plane y = 0. Every dimension is quoted from the text specification; there are no images or reference meshes, so no scaling or rectification was needed.

Modelling recipe (for the model worker): outer cylinder of radius `outerRadius` from z = -`floorThickness` to `chamberHeight` + `lidThickness`, plus the D`inletOuterDiameter` cylinder from the lid top to `inletTopZ`, plus the D`outletOuterDiameter` cylinder along +x on (y 0, z `outletAxisZ`) from inside the wall (x about `chamberRadius`) to `outletEndX`; subtract the chamber (radius `chamberRadius`, z 0..`chamberHeight`), the inlet bore (z from just inside the chamber to past `inletTopZ`) and the outlet bore (from x about 20, i.e. inside the chamber but clear of the pin at r 3, to past `outletEndX`); then add the pin (z from just below 0 into the floor, to `pinHeight`). The inlet tube spans from the lid top to the fixed port plane `inletTopZ`, so `lidThickness` edits keep z = 48. Asserts: `wallThickness > 0`, `lidThickness > 0`, `chamberHeight + lidThickness < inletTopZ`, `outletOuterDiameter > outletBoreDiameter`, `inletOuterDiameter > inletBoreDiameter`, `pinDiameter < 2 * chamberRadius`.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| chamberRadius | 25 | 0.01 | stated | spec: inner diameter 50.0 (radius 25.0) |
| chamberHeight | 25 | 0.01 | stated | spec: inner height 25.0, z 0..25 |
| wallThickness | 3 | 0.01 | stated | spec: side wall 3.0 thick |
| floorThickness | 3 | 0.01 | stated | spec: floor 3.0 thick, z -3..0 |
| lidThickness | 3 | 0.01 | stated | spec: lid 3.0 thick, z 25..28 |
| outerRadius | 28 | 0.01 | derived | chamberRadius + wallThickness (spec also states 28.0) |
| inletBoreDiameter | 12 | 0.01 | stated | spec: inlet inner diameter 12.0, bore through the lid |
| inletOuterDiameter | 16 | 0.01 | stated | spec: inlet outer diameter 16.0 |
| inletTopZ | 48 | 0.01 | stated | spec: inlet open at z = 48 (inlet port plane) |
| outletBoreDiameter | 10 | 0.01 | stated | spec: outlet inner diameter 10.0 |
| outletOuterDiameter | 14 | 0.01 | stated | spec: outlet outer diameter 14.0 |
| outletAxisZ | 12.5 | 0.01 | stated | spec: outlet axis y = 0, z = 12.5 |
| outletEndX | 58 | 0.01 | stated | spec: outlet open end x = 58 (outlet port plane) |
| pinDiameter | 6 | 0.01 | stated | spec: pin diameter 6.0 |
| pinHeight | 12 | 0.01 | stated | spec: pin from z = 0 to z = 12 |
| volume | 31075.58 | 0.2 % | derived | pi*28^2*31 - pi*25^2*25 + pi*(64-36)*20 - pi*36*3 + pi*9*12 + [58*pi*49 - I(7,28)] - [58*pi*25 - I(5,25)], I(a,R) = integral over the disk of radius a of sqrt(R^2 - y^2) dA (Gauss-Legendre, 400 nodes); I(7,28) = pi*1361.196, I(5,25) = pi*621.859 |
| surface area | 22331.07 | 1 % | derived | outer wall 2*pi*28*31 - J(7,28), floor underside pi*784, lid top pi*720, inlet outer pi*320, inlet end pi*28, inlet bore pi*276, lid underside pi*589, chamber wall 2*pi*25*25 - J(5,25), chamber floor pi*616, pin side pi*72, pin top pi*9, outlet outer and bore laterals integral of (58 - sqrt(R^2 - a^2 sin^2 phi)) a dphi, outlet end pi*24; J(a,R) = integral of 2 sqrt(a^2 - y^2) R / sqrt(R^2 - y^2) dy |
| center of mass | (2.951, 0, 13.720) | 0.1 | derived | x = pi*[(58^2-28^2)*49 + 7^4/4 - (58^2-25^2)*25 - 5^4/4]/2 / V; z = [12.5*(V/pi - 560) + 38*560 - 26.5*108 + 6*108] / (V/pi); y = 0 by symmetry |
| section midY (y = 0) | 692, 2 loops, 0 holes | 1 % | derived | floor 56*3 + walls 25*3 + 15*3 + lid 44*3 + inlet walls 2*2*20 + outlet walls 2*2*30 + pin 6*12 |
| section pinLevel (z = 3) | 527.79, 2 loops, 1 hole | 1 % | derived | pi*(28^2 - 25^2 + 3^2) |
| section floorSeal (z = -1.5) | 2463.01, 1 loop, 0 holes | 1 % | derived | pi*28^2 |
| section lidLevel (z = 26.5) | 2349.91, 1 loop, 1 hole | 1 % | derived | pi*(28^2 - 6^2) |
| section inletTube (z = 38) | 87.96, 1 loop, 1 hole | 1 % | derived | pi*(8^2 - 6^2) |
| section outletWall (x = 26.5) | 482.04, 1 loop, 1 hole | 1 % | derived | 2*sqrt(28^2 - 26.5^2)*31 - pi*5^2 |
| section outletTube (x = 45) | 75.40, 1 loop, 1 hole | 1 % | derived | pi*(7^2 - 5^2) |
| faces chamberFloor / lidUnderside / lidTop / inletEnd / outletEnd / pinTop | 1935.22 / 1850.40 / 2261.95 / 87.96 / 75.40 / 28.27 | 1 % | derived | pi*(25^2-3^2), pi*(25^2-6^2), pi*(28^2-8^2), pi*(8^2-6^2), pi*(7^2-5^2), pi*3^2 |
| cylinder outletOuter t_range | 27.11..58 (length 30.89) | 0.3 | derived | sqrt(28^2 - 7^2) = 27.111 at y = +-7 |
| cylinder outletBore t_range | 24.49..58 (length 33.51) | 0.3 | derived | sqrt(25^2 - 5^2) = 24.495 at y = +-5 |
| passage void volume | 50000..57500 | band | derived | chamber pi*25^2*25 - pin pi*9*12 + inlet bore pi*36*23 + outlet bore 58*pi*25 - I(5,25) = 53951, less about 190 under the two mouth plugs |
| blockout band | 80000..89000 | band | derived | solid envelope: pi*28^2*31 + pi*8^2*20 + [58*pi*49 - I(7,28)] = 85026.6 |
| edit wallThickness +1 | +5396.07, bbox +[1, 2, 0] | 2 % | derived | vol(R = 29) - vol(R = 28) = pi*(29^2-28^2)*31 - [I(7,29) - I(7,28)]; x min moves -28 -> -29, y +-28 -> +-29; sweep 2 / 3 / 5 give 25874.4 / 31075.6 / 42062.6; feasible interval 0 < wallThickness <= 20, sweep kept inside it; -3 (zero wall) must assert |
| edit lidThickness +1 | +2261.95, bbox +[0, 0, 0] | 2 % | derived | annulus r 8..28 over z 28..29 becomes lid: pi*(28^2 - 8^2)*1; inlet top stays at inletTopZ; sweep 2 / 3 / 5 give 28813.6 / 31075.6 / 35599.5; feasible interval 0 < lidThickness < inletTopZ - chamberHeight = 23, sweep kept inside it; -3 (zero lid) must assert |

## 6. Defaults retained

- Envelope and bbox tolerance 0.05 mm, parameter tolerance 0.01 mm, cylinder radius tolerance 0.05 mm: the geometry is analytic (planes and cylinders), so the exported STEP should reproduce it to rounding.
- Mirror symmetry about y = 0 uses the default deviation band; the sources state no tighter band.
- Passage voxel pitch 1.0 mm: the narrowest passage is the D10 outlet bore, 10 voxels across.
- `process` is recorded as nominal moulding; the spec states only the material and density.

## 7. Unrepresentable or low-confidence features

- The magnetic coupling through the floor is not modelled (spec); only the sealed floor (section floorSeal, no hole) and the motor seat face are encoded.
- The impeller's swept envelope is encoded as void probes (tips r 20, hub bottom z 1, 1.0 above the floor, r 5 at z 1.5 beside the pin) rather than a hardware keep-out; the assembly stage checks the real impeller clearances.
- The water body and port planes are derived later from the placed housing and impeller; here the port planes are pinned as the tube end faces (inletEnd z = 48, outletEnd x = 58).

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
