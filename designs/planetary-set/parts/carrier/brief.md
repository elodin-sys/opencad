# planetary-set-carrier — design brief

## 1. Intent and configuration

Planet carrier of the fixed-ring planetary set (`sources/planetary-set-spec.md`, authoritative, text only). It is the output member: the sun is driven, the ring is held, and the carrier turns about the common axis at 24 / (24 + 48) of the sun's speed. The part is a flat D88 x 5 disc with a D10 centre hole on its axis and three D8 through holes on radius 36 at 0, 120 and 240 deg, one of them centred on +x at (36, 0). It is drafted in its own frame (axis +z through the origin, bottom face z = 0). In the assembly it lies on top of the gears at z 10..15, its bottom face resting on the top faces of the sun and the three planets. Each planet hole is coaxial with a planet's D8 bore and is the axis that planet turns on. Its rim (r 44) stays 2 mm inside the ring's tip circle (r 46), so the carrier never rests on the fixed ring.

Assembly joints that reference this frame (from the orchestrator): carrierSpin (revolute) attaches the carrier at own-frame [0, 0, 0], axis +z; planet1Spin, planet2Spin and planet3Spin (revolute) mount the planets at own-frame (36, 0, -10), (-18, 31.176915, -10) and (-18, -31.176915, -10), axis +z (each planet's own origin, its bottom face, lies 10 mm below the carrier's bottom face).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/planetary-set-spec.md | text | authoritative | 2a8bca0f4ffa01692bc1a5879aeb8b02a1d728b2cbe39448f181197d86ca14ca | Carrier row (Ø88 x 5, centre hole Ø10, three Ø8 holes on radius 36 at 0/120/240 deg), Part frames (planet hole on +x), Planet orbit row (radius 36), Frame (carrier bottom at assembly z = 10) |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| carrier disc diameter | 88 | mm | spec Carrier row; intent | 0.01 | stated |
| carrier thickness (own frame z 0..5; assembly z 10..15) | 5 | mm | spec Carrier row; intent | 0.01 | stated |
| centre hole on the axis | Ø10 through | mm | spec Carrier row; intent | 0.01 | stated |
| planet holes | 3 x Ø8 through | mm | spec Carrier row; intent | 0.01 | stated |
| planet hole pitch circle | r 36 | mm | spec Carrier and Planet orbit rows | 0.01 | stated |
| planet hole angles | 0, 120, 240 | deg | spec Carrier row; intent | 0.01 | stated |
| planet hole centres | (36, 0), (-18, 31.176915), (-18, -31.176915) | mm | intent | 0.05 (axis offset) | stated |
| a planet hole on +x | at (36, 0) | mm | spec Part frames; intent | 0.05 | stated |
| bottom face lies on the sun and planet top faces | z = 0 (assembly z = 10) | mm | spec Frame; intent | 0.05 | stated |
| planet holes coaxial with the planets' D8 bores | 3 axes | - | intent; spec Frame | 0.05 | stated (assembly check) |
| rim inside the ring tip circle | r 44 vs r 46 (2 mm) | mm | intent; spec Ring row (tip r 46) | 0.05 | stated |
| material, process, fits, edge breaks | - | - | not given | - | open |

## 4. Coordinate frame, scale, and measurement method

The frame is the part frame the spec prescribes ("every gear, the ring and the carrier have their axis along +z through their own origin and their bottom face at z = 0 ... the carrier has a planet hole centred on +x (at (36, 0))"). The origin is the centre of the bottom face, where the carrier axis meets z = 0. +x points from the axis to the centre of planet hole 1, +z points up the axis from the bottom face (z = 0) to the top face (z = 5), and +y = +z x +x puts planet hole 2 at (-18, +31.176915). Datums: A = bottom face z = 0 (seat on the gears), B = the carrier axis (centre-hole axis), C = the planet hole 1 axis (angular orientation). In the assembly the carrier sits at rest angle 0 deg, so the own frame and the assembly frame differ only by +10 mm in z.

There are no images, drawings or meshes. Every dimension is read directly from the spec text and the intent, and there is no scaling or rectification. Hole centres are polar: (planetOrbitRadius cos θ, planetOrbitRadius sin θ) with θ = planetHoleStartAngle + k * 360 / planetHoleCount, k = 0, 1, 2. That gives 36 cos 120° = -18 and 36 sin 120° = 31.176915, matching the intent's coordinates.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| carrierDiameter | 88 mm | 0.01 | stated | spec Carrier row "disc Ø88 x 5"; intent "rim (r 44)" |
| carrierThickness | 5 mm | 0.01 | stated | spec Carrier row "Ø88 x 5 over the gears (z 10..15)"; intent "z 0..5" |
| centreHoleDiameter | 10 mm | 0.01 | stated | spec Carrier row "centre hole Ø10" |
| planetHoleDiameter | 8 mm | 0.01 | stated | spec Carrier row "three Ø8 holes" |
| planetOrbitRadius | 36 mm | 0.01 | stated | spec Carrier row "on radius 36"; Planet orbit "36 = 24 + 12 = 48 - 12" |
| planetHoleCount | 3 | 0.01 | stated | spec Carrier row "three Ø8 holes ... at 0, 120 and 240 deg" |
| planetHoleStartAngle | 0 deg | 0.01 | stated | spec Part frames "a planet hole centred on +x (at (36, 0))" |
| envelope | [-44, -44, 0] .. [44, 44, 5] | 0.05 | derived | ± carrierDiameter / 2 in x and y, 0..carrierThickness in z; the holes stop at r 40 < 44 |
| volume | 29263.936 mm³ | rel 0.002 | derived | π (44² - 5² - 3·4²) · 5 = 9315 π |
| surface area | 13621.946 mm² | rel 0.005 | derived | 2·1863 π (top + bottom) + 2π·44·5 (rim) + 2π·5·5 (centre hole) + 3·2π·4·5 (planet holes) = 4336 π |
| centre of mass | (0, 0, 2.5) | 0.05 | derived | holes equally spaced on one circle plus one on the axis, so the plan centroid is on the axis; z = 5 / 2 |
| face `top` area (z = 5, +z) | 5852.787 mm² | rel 0.005 | derived | π (44² - 5² - 3·4²) = 1863 π; centroid (0, 0) |
| face `seat` (z = 0, -z) | position only | 0.05 | derived | datum A; no area so that neither edit test resizes the pinned face (its area is 1863 π at nominal) |
| section `midZ` (z = 2.5) | 5852.787 mm², 1 loop, 4 holes | rel 0.005 | derived | 1863 π; the four holes |
| section `cutX0` (x = 0) | 390 mm², 2 loops | rel 0.005 | derived | (88 - 10) · 5; the loops stay separate only if the centre hole runs through |
| section `cutX36` (x = 36) | 212.982 mm², 2 loops | rel 0.005 | derived | (2 √(44² - 36²) - 8) · 5 = (2·25.2982 - 8) · 5 |
| section `cutXm18` (x = -18) | 321.497 mm², 3 loops | rel 0.005 | derived | (2 √(44² - 18²) - 16) · 5 = (2·40.1497 - 16) · 5; holes 2 and 3 span y ±27.177..±35.177 |
| cylinder `centreHole` | Ø10 hole, axis (0, 0), +z | 0.05 axis | stated | datum B; no length so the thickness edit keeps it intact |
| cylinders `planetHole1..3` | Ø8 holes at (36, 0), (-18, ±31.176915), +z | 0.05 axis | stated | intent coordinates; no length for the same reason |
| cylinder `rim` | Ø88 pin, length 5, t 0..5 | 0.05 | stated | disc outside surface, r 44 |
| dimension `thickness` | 5 between seat and top | 0.05 | stated | carrierThickness |
| dimensions `spanX`, `spanY` | 88 | 0.05 | stated | carrierDiameter (bbox extents) |
| cylinder counts | 3 × Ø8 hole, 1 × Ø10 hole | exact | stated | spec Carrier row |
| probes `inMaterial` | solid at (20, 0), (-36, 0), (0, 36), r 42 at 0/120/240 deg, z 2.5 | ≥ 2 mm from walls | derived | web, the unholed 180° spot on the planet circle, and the 4 mm rim lands (r 40..44) outboard of each planet hole |
| probes `inHoles` | void on each hole axis, z 2.5 | ≥ 2.5 mm from walls | derived | hole axes |
| probes `insideRingTip` | void at r 45.5 at 45/135/225/315 deg, z 2.5 | 1.5 mm outside the rim | derived | air between the round rim (r 44) and the ring tip circle (r 46); a square blank would fail |
| blockout band | 29000 .. 31000 mm³ | - | derived | covers the unholed D88 x 5 blank 9680 π = 30410.617 and the finished 29263.936 |

Edit tests (other parameters held fixed):
- `carrierDiameter` -2 (to 86): ΔV = π (43² - 44²) · 5 = -435 π = -1366.593 mm³, bbox Δ [-2, -2, 0]. Sweep values 84, 86 and 88. The feasible interval is (80, 88]. Below 80 the planet holes (outer edge r 36 + 4 = 40) break through the rim, so the part must `assert carrierDiameter / 2 > planetOrbitRadius + planetHoleDiameter / 2`, and the infeasible delta -10 (to 78) must fail that assert. Above 88 the rim would come within 2 mm of the ring tip circle (r 46), so the assembly clearance keeps the sweep at or below 88.
- `carrierThickness` +1 (to 6): ΔV = 1863 π · 1 = +5852.787 mm³, bbox Δ [0, 0, 1]; the disc grows up from the fixed seat z = 0. Sweep values 4, 5 and 6. The feasible interval is (0, ∞) for the part; the part must `assert carrierThickness > 0`, and the infeasible delta -5 (to 0) must fail it.
- Neither edit moves the pinned interface items: the seat face (position only), the centre-hole axis and the three planet-hole axes (diameter and axis, no length).

## 6. Defaults retained

- Envelope and bbox tolerance 0.05 mm: the template default. It is ample for an exact analytic disc and stays well inside the 2 mm ring clearance.
- Parameter digital tolerance 0.01: stated values are exact.
- Volume tolerance rel 0.002, area rel 0.005: exact BRep geometry; these only absorb tessellation in the STL comparison.
- Material, density and process are null. Nothing is stated, and no mass claim is made.
- release_status `reconstruction`: the template default.

## 7. Unrepresentable or low-confidence features

- The 2 mm rim clearance to the ring tip circle and the coaxiality of each planet hole with a planet's D8 bore are assembly relations. In this part contract they are pinned through the rim cylinder (Ø88), the bbox, the `insideRingTip` void probes and the planet-hole cylinders at the stated centres. The assembly checks the relation itself.
- The part is mirror-symmetric about y = 0 and threefold rotationally symmetric. No `symmetry` entry is declared because the sources state no mirror plane, and the four hole cylinders already pin every hole's position.
- Hole fits, pins or axles, bearings, chamfers and fillets are not stated. The holes are nominal and every edge is sharp (see open questions).

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
