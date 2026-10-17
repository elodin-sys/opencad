# four-bar-ground — design brief

## 1. Intent and configuration

Ground plate (link 1) of the planar crank-rocker four-bar linkage `four-bar`: one rectangular plate 160 (x) x 60 (y) x 5 (z)
from corner (-30, -30, -5) to (130, 30, 0) with two Ø6 through holes along z at the pivots O2 (0, 0) and O4 (100, 0)
(ground length 100). It is drafted and modelled in its own frame, which is the assembly frame (origin at O2 on the top
face, +x toward O4, +z up along the pin axes), because the assembly mounts the crank on joint pinO2 (point (0, 0, 0),
axis +z) and the rocker on joint pinO4 (point (100, 0, 0), axis +z). The top face z = 0 around O2 is the crank's seat
(crank on z = 0..5); the rocker runs at z = 10..15, so nothing seats at O4. No other features; one solid. The only
source, `sources/four-bar-spec.md` (text), is authoritative.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/four-bar-spec.md | text | authoritative | aececd85a2ba8a2e020775f05a44f1bd1c3a505c8c8c5ed634606d975490bf17 | link table (Ground row), frame, layer stack, pins; mm |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| plate size x, y, z | 160 x 60 x 5 | mm | spec, Ground row | 0.01 | stated |
| plate corners | (-30, -30, -5) to (130, 30, 0) | mm | spec, Ground row | 0.05 (envelope) | stated |
| top face / bottom face | z = 0 / z = -5 | mm | spec, layers (ground z -5..0) | 0.05 | stated |
| O2 hole | Ø6 through along z at (0, 0) | mm | spec, Ground row | 0.02 axis, 0.02 radius | stated |
| O4 hole | Ø6 through along z at (100, 0) | mm | spec, Ground row | 0.02 axis, 0.02 radius | stated |
| ground length O2-O4 | 100 | mm | spec, Ground row | 0.01 | stated |
| frame | origin O2 on top face, +x to O4, +z up the pin axes | - | spec, Frame; orchestrator joint frames | - | stated |
| pinO2 interface | O2 axis + top face seat (crank z 0..5) | - | intent, joint pinO2 | - | stated |
| pinO4 interface | O4 axis (rocker z 10..15, no seat) | - | intent, joint pinO4 | - | stated |
| bodies | one solid, no other features | - | intent | exact | stated |
| material, density, process | not given | - | - | - | open |
| hole fit to pins, edge breaks | not given | - | - | - | open |

## 4. Coordinate frame, scale, and measurement method

Origin at pivot O2 where the O2 hole axis meets the top face (x = y = z = 0). +x runs along the ground line from O2 to
O4 (O4 at x = 100); +y crosses the 60 mm width (right-handed), with both hole axes on y = 0; +z is up along the pin
axes, normal to the plate, so the plate hangs below its top face (z = -5..0) and the links stack above it. Datums: A =
top face z = 0 (crank seat, primary), B = O2 axis, C = O4 axis (B to C is +x). This is the assembly frame of `four-bar`,
so the part needs no placement transform. The source is text only: there are no images, no pixel scale and no
reference mesh; every value is read verbatim from the Ground row and the Frame paragraph. The plate is centred on
y = 0 (y = -plateWidth/2 .. +plateWidth/2) and starts at x = plateXMin, running to plateXMin + plateLength.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| plateLength | 160 mm | 0.01 | stated | Ground row "plate 160 x 60 x 5" |
| plateWidth | 60 mm | 0.01 | stated | Ground row; corner y -30..30, centred on y = 0 |
| plateThickness | 5 mm | 0.01 | stated | Ground row; layers "ground z -5..0" |
| plateXMin | -30 mm | 0.01 | stated | Ground row corner (-30, -30, -5) |
| groundLength | 100 mm | 0.01 | stated | Ground row "O2 (0, 0) and O4 (100, 0): ground length 100" |
| holeDiameter | 6 mm | 0.01 | stated | Ground row "Ø6 holes at O2 and O4" |
| volume | 47717.257 mm³ | 10 | derived | 160·60·5 - 2·π·3²·5 = 48000 - 90π |
| surface area | 21475.398 mm² | 0.2 % | derived | 2(9600 - 18π) + 2(160 + 60)·5 + 2·π·6·5 = 19086.903 + 2200 + 188.496 |
| centre of mass | (50, 0, -2.5) | 0.05 | derived | plate centroid (plateXMin + plateLength/2, 0, -plateThickness/2); holes symmetric about x = 50, y = 0 |
| section midZ (z = -2.5) | 9543.451 mm², 1 loop, 2 holes | 0.2 % | derived | 9600 - 18π |
| sections throughO2 / throughO4 (x = 1 / 101) | 271.716 mm², 2 loops, 0 holes | 0.5 % | derived | 60·5 - 5·2√(3² - 1²) = 300 - 10√8; two islands prove the hole is through |
| face bottom (z = -5, -z) | 9543.451 mm², centre (50, 0) | 0.2 % | derived | 9600 - 18π; proves both holes open at the bottom |
| face top (z = 0, +z) | plane only | 0.05 | stated | crank seat; area deliberately unpinned (the plateWidth edit changes it) |
| cylinders holeO2 / holeO4 | Ø6, axes (0, 0) / (100, 0) along z | 0.02 | stated | no length: the plateThickness edit changes it |
| dimensions lengthX / widthY / thicknessZ | 160 / 60 / 5 | 0.05 / 0.05 / 0.02 | stated | bbox extents; thicknessZ between bottom and top |
| cylinder count Ø6 holes along z | 2 | exact | stated | O2 and O4 |
| blockout band | 46500 .. 48500 mm³ | - | derived | full-envelope plate 48000 (holes optional, 47717); about ±2 % |
| edit plateThickness +1 | ΔV = +9543.451, Δbbox (0, 0, 1) | 2 % | derived | (plateLength·plateWidth - 2π(holeDiameter/2)²)·1; plate grows down, top face and hole axes stay |
| edit plateWidth +10 | ΔV = +8000, Δbbox (0, 10, 0) | 2 % | derived | plateLength·10·plateThickness; plate stays centred on y = 0, holes unchanged |

Feasible intervals the part must assert (an out-of-range value fails an `assert`, never builds distorted geometry):
plateThickness > 0 (sweep 3, 5, 8; infeasible delta -5 gives 0); plateWidth > holeDiameter = 6 so the holes stay inside
the long edges (sweep 40, 60, 80; infeasible delta -56 gives 4); plateXMin < -holeDiameter/2 and
plateXMin + plateLength > groundLength + holeDiameter/2 (plateLength > 133 at the stated values); 0 < holeDiameter <
groundLength so the two holes stay separate.

## 6. Defaults retained

Envelope tolerance 0.05 mm and parameter tolerances 0.01 mm are the template's digital defaults; the plate is a stated
rectangle with exact analytic acceptance values, so they are adequate. Material, density and process stay null (not
stated; no mass claim). Edges stay sharp and holes nominal Ø6 (no chamfer, fillet or fit allowance is stated).
`release_status: reconstruction` is kept from the seed. When plateLength changes, plateXMin stays fixed, so only the
+x end moves; plateLength is not edit-tested, so this default only governs later edits.

## 7. Unrepresentable or low-confidence features

The pins, the motor at O2 and the other links are separate designs or assembly items, not part of this body. The plate
is symmetric about y = 0 (and about x = 50) because of its stated corners, but the spec does not call out a mirror
plane. No `acceptance.symmetry` is declared: the y = 0 hole axes and the bbox already pin the placement. The hole length
(5) is not a cylinder check because the plateThickness edit changes it. Through-ness is checked instead by the two
x-sections (two islands each), the bottom-face area and the volume. How the O4 pin spans the 10 mm gap up to the rocker
layer is left to the assembly.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
