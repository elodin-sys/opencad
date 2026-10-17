# crank-slider-crank — design brief

## 1. Intent and configuration

The crank link of the offset crank-slider mechanism (assembly `crank-slider`), drafted and modelled on its own in its
part frame. It is a 5 mm stadium plate, 16 wide, with semicircular R8 ends centred on two Ø6 through holes 30 apart:
hole O (the crank pivot on the ground's crank axis, driven by the motor) and hole A (the crank pin carrying the
connecting rod). The single authoritative source is `sources/crank-slider-spec.md` (text only, no drawings or images).
The assembly places this body by two joint frames, so the part frame is fixed by them: joint `crankPivot` (revolute) at
own-frame [0, 0, 0], axis [0, 0, 1]; joint `crankPin` (revolute, rod) at own-frame [30, 0, 5], axis [0, 0, 1]. In the
assembly the crank occupies layer z 0..5 above the ground (z -5..0) and below the rod (z 5..10).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/crank-slider-spec.md | text | authoritative | cd01ebc4dc4d7289a786bef3bca834eb565dd9f6109941bbcc2ec04b879c0d1c | parts table row "Crank", part-frame convention, layers, joints; mm |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| hole O to hole A centre distance | 30 | mm | spec table "O to crank pin A: 30" | 0.01 | stated |
| plate thickness (z = 0..5) | 5 | mm | spec table "stadium plate 5 thick"; layers "crank z 0..5" | 0.01 | stated |
| plate width (y = -8..8) | 16 | mm | spec table "16 wide" | 0.01 | stated |
| end radius, centred on the holes | 8 | mm | spec table "semicircular ends of radius 8 centred on its two holes" | 0.01 | stated |
| hole diameter, both holes, through along z | 6 | mm | spec table "Ø6 holes" | 0.01 | stated |
| part frame: O at origin on bottom face, A on +x, z along pins | - | - | spec "Part frames" paragraph | - | stated |
| bottom face z = 0 seats on ground top face, hole O on crank axis | - | - | spec layers and joint O; orchestrator joint crankPivot | - | stated |
| top face z = 5 carries rod bottom face at hole A | - | - | spec layers and joint A; orchestrator joint crankPin | - | stated |
| single solid (no fused bodies) | 1 | - | spec "Four separate solids" | - | stated |
| overall x extent -8..38 | 46 | mm | derived: crankLength + 2 endRadius | 0.05 | derived |
| volume | 3122.57 | mm3 | derived (section 5) | 0.2 % | derived |
| material, density, process | - | - | not stated | - | open |
| pin fit / clearance of the bores | - | - | not stated | - | open |

## 4. Coordinate frame, scale, and measurement method

Origin at the centre of hole O on the bottom face (z = 0). +x runs from hole O toward hole A (A at x = 30); +y runs
across the width, the stadium being mirror-symmetric about y = 0 and about x = 15; +z runs along both pin axes from the
bottom face (z = 0) to the top face (z = 5). Datums: A = bottom face z = 0 (seat on the ground), B = axis of hole O
(x = 0, y = 0), C = axis of hole A (x = 30, y = 0), D = top face z = 5 (rod seat). This is exactly the part frame the
spec prescribes for the crank and the frame the assembly joints are expressed in. There are no images or meshes: every
value is quoted from the text table or derived from quoted values by closed-form geometry, so no scale was established
and no pixel measurement was taken. Envelope: x -8..38, y -8..8, z 0..5, tolerance 0.05.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| crankLength | 30 mm | 0.01 | stated | spec table, Crank: "O to crank pin A: 30" |
| plateThickness | 5 mm | 0.01 | stated | spec table, Crank: "stadium plate 5 thick" |
| endRadius | 8 mm | 0.01 | stated | spec table, Crank: "semicircular ends of radius 8" |
| plateWidth | 16 mm | 0.01 | derived | 2 * endRadius (the spec also states "16 wide", consistent) |
| holeDiameter | 6 mm | 0.01 | stated | spec table, Crank: "Ø6 holes" |
| net plan area (section midZ) | 624.513 mm2 | 0.2 % | derived | crankLength * plateWidth + pi endRadius^2 - 2 pi (holeDiameter/2)^2 = 480 + 201.062 - 56.549 |
| volume | 3122.57 mm3 | 0.2 % | derived | plateThickness * 624.513 = 3122.566 |
| surface area | 1988.85 mm2 | 1 % | derived | 2 * 624.513 + 5 * (60 + 16 pi) + 5 * 2 * 6 pi = 1249.027 + 551.327 + 188.496 |
| centre of mass | (15, 0, 2.5) | 0.05 | derived | symmetry about x = crankLength/2 and y = 0; z = plateThickness/2 |
| section webX (x = 10) | 80 mm2, 1 loop, 0 holes | 0.2 % | derived | plateWidth * plateThickness = 16 * 5 |
| flank faces y = +-8 | 150 mm2 each | 0.5 % | derived | crankLength * plateThickness = 30 * 5 |
| cylinders holeO, holeA | D6, length 5, t 0..5 | r 0.01 | stated | axes (0, 0) and (30, 0) along z |
| cylinders endO, endA (convex) | R8, length 5, t 0..5 | r 0.01 | stated | end arcs centred on the holes |
| dimensions | thicknessZ 5, overallX 46, widthY 16 | 0.05 | derived | bottom-top, bbox x, flankNeg-flankPos |
| blockout band | 3050..3480 mm3 | - | derived | holed plate 3122.6 to un-holed stadium 5 * 681.062 = 3405.3, +2 %; a 46 x 16 x 5 box (3680) is outside |
| edit test endRadius +1 | +567.035 mm3, bbox +[2, 2, 0] | 2 % | derived | plateThickness * (2 * crankLength * 1 + pi * (9^2 - 8^2)) = 5 * (60 + 17 pi) |

Edit test and sweep: `endRadius` is the one edited parameter. Its feasible interval is endRadius > holeDiameter / 2
(3 mm, strictly: at 3 the ligament around each hole vanishes and the holes break out of the flanks); the model must
`assert endRadius > holeDiameter / 2`. The sweep values 6, 8, 10 lie inside it; the infeasible delta -6 (endRadius = 2)
must fail that assert. plateWidth follows as 2 * endRadius, so the edit widens the flanks and the arcs together and the
bbox grows by 2 in x and y. The edit moves none of the pinned items: the bottom and top faces (position and centroid
(15, 0) only, no area pinned), the hole O and hole A cylinders, the thickness dimension and the y = 0 mirror plane.

Probes: solid points at the web centre (15, 0, 2.5), the end ligaments (-5.5, 0, 2.5) and (35.5, 0, 2.5) (2.5 mm from
the bore and the arc), the flanks (15, +-6, 2.5); void points on both bore axes at mid-thickness (3 mm from the bore
wall) and at the four bbox corners (-7.5, +-6.5, 2.5), (37.5, +-6.5, 2.5), 1.9 mm outside the R8 arcs and 1.5 mm from
the flank planes, proving the ends are round.

## 6. Defaults retained

- `material`, `density_kg_m3` and `process` stay null: the spec states none, and no mass property is claimed.
- `release_status: reconstruction` kept from the template.
- Symmetry bands (max 0.1 mm, p95 0.05 mm) are the exemplar's defaults; the spec states no tighter band.
- Tolerances: 0.01 on every parameter (exact text values), 0.05 on the envelope and dimensions, 0.2 % on volume and
  section areas, 1 % on surface area.
- Only `endRadius` carries an edit test: `crankLength`, `plateThickness` and `holeDiameter` define the assembly
  interfaces (hole A position, top-face height, the pin bores), so editing them would break the pinned interfaces by
  construction.

## 7. Unrepresentable or low-confidence features

- No pin fit or running clearance is specified; both bores are nominal Ø6.
- No edge breaks (chamfers, fillets) are specified; none are modelled.
- No drive feature (key, flat, D-bore) for the motor at hole O is specified; it is a plain round bore.
- The assembly behaviour (full revolution, interference with the slider, which stays beyond x = 54) belongs to the
  assembly contract, not to this part.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
