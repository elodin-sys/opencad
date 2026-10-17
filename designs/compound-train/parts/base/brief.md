# compound-train-base — design brief

## 1. Intent and configuration

Base plate of the compound spur-gear train (assembly `compound-train`), drafted in its own frame, which is the assembly
frame: origin on the pinion axis at the plate top face, +x toward the idler and output axes, +z up. A rectangular plate
195 (x) x 100 (y) x 5 (z) mm from corner (-25, -50, -5) to (170, 50, 0); the top face z = 0 is the seat on which the
pinion and the idler stand. Three clearance holes through the full thickness (z = -5..0), axes along +z: D6 at (0, 0) on
the pinion axis, D8 at (60, 0) on the idler axis and D8 at (120, 0) on the output axis. No other features.

The assembly mounts the gears on this part's own-frame joint points: pinionSpin at (0, 0, 0), idlerSpin at (60, 0, 0) and
outputSpin at (120, 0, 0), all with axis (0, 0, 1). Authoritative source: `sources/compound-train-spec.md` (text only;
Base plate row and Frame paragraph). One solid; the gears are separate designs.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/compound-train-spec.md | text | authoritative | e2734c43ae1d2aa36320d0b7680e21616422e902b471b3eb98295e3292296af5 | Base plate row (size, corners, holes) and Frame paragraph (z up, origin on the pinion axis, plate top at z = 0); unversioned, mm |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| plate size x / y / z | 195 / 100 / 5 | mm | spec Base plate row; intent | 0.05 (envelope) | stated |
| plate corners | (-25, -50, -5) to (170, 50, 0) | mm | spec Base plate row; intent | 0.05 (envelope) | stated |
| top face is the gear seat | z = 0 | mm | spec Frame paragraph; intent | 0.05 | stated |
| pinion clearance hole | D6 at (0, 0), through z = -5..0, axis +z | mm | spec Base plate row; intent | 0.02 on radius, 0.05 axis | stated |
| idler clearance hole | D8 at (60, 0), through, axis +z | mm | spec Base plate row; intent | 0.02 on radius, 0.05 axis | stated |
| output clearance hole | D8 at (120, 0), through, axis +z | mm | spec Base plate row; intent | 0.02 on radius, 0.05 axis | stated |
| no other features | exactly 3 holes, 1 solid | - | intent | exact counts | stated |
| material, density, process | not given | - | - | - | open |
| hole fit class | not given | - | - | - | open |

Acceptance mapping: size and corners by `envelope`, `lengthX`, `widthY`, `thicknessZ`; the seat by face `top` (interface
`seat`); each hole by its `cylinders` entry (interface `jointAxes`), its void probe and its x-section (two strips prove the
hole is through); "no other features" by `volume`, `surface_area`, `midZ` (holes: 3), `holesD6` / `holesD8` and
`solid_count: 1`.

## 4. Coordinate frame, scale, and measurement method

Frame is the assembly frame stated by the spec and the intent: origin on the pinion axis (centre of the D6 hole) in the
top face; +x from the pinion toward the idler (x = 60) and output (x = 120) axes; +y completes the right-handed set and the
plate is centred on y = 0 (corners y = -50 and 50); +z up, parallel to every gear axis. Datum A is the top face z = 0,
datum B the pinion axis, datum C the idler and output axes.

No images, drawings or reference meshes exist; every value is quoted from text, so there is no pixel scale or
rectification. Consistency check: plateXMin + plateLength = -25 + 195 = 170 matches the stated corner; the y corners
(-50, 50) equal +-plateWidth/2, so the width is modelled centred on the hole row.

Parametric behaviour the model must keep: the plate spans z = -plateThickness..0 (a thickness edit grows it downward and
leaves the seat at z = 0) and x = plateXMin..plateXMin + plateLength (a length edit moves only the +x end). The hole axes
are at x = 0, idlerX and outputX on y = 0.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| plateLength | 195 mm | 0.01 | stated | spec Base plate row "195 x 100 x 5 mm"; intent |
| plateWidth | 100 mm | 0.01 | stated | spec Base plate row; intent |
| plateThickness | 5 mm | 0.01 | stated | spec Base plate row; intent |
| plateXMin | -25 mm | 0.01 | stated | corner (-25, -50, -5) |
| pinionHoleDiameter | 6 mm | 0.01 | stated | "clearance holes Ø6 at (0, 0)" |
| idlerHoleDiameter | 8 mm | 0.01 | stated | "Ø8 at (60, 0)" |
| outputHoleDiameter | 8 mm | 0.01 | stated | "Ø8 at ... (120, 0)" |
| idlerX | 60 mm | 0.01 | stated | idler axis (60, 0); centre distance 60 mm |
| outputX | 120 mm | 0.01 | stated | output axis (120, 0); second centre distance 60 mm |
| volume | 96855.97 mm3 | 10 | derived | 195*100*5 - pi/4*(36 + 64 + 64)*5 = 97500 - 205*pi |
| surface area | 42037.96 mm2 | 10 | derived | 2*(19500 - 41*pi) + 2*(195 + 100)*5 + pi*(6 + 8 + 8)*5 |
| centre of mass | (72.515, 0, -2.5) | 0.05 | derived | x = (97500*72.5 - 5*pi*(9*0 + 16*60 + 16*120)) / 96855.97; y, z by symmetry |
| section midZ (z = -2.5) | 19371.19 mm2, 1 loop, 3 holes | 0.2 % | derived | 19500 - 41*pi |
| section pinionAxisX (x = 0) | 470 mm2, 2 loops | 0.2 % | derived | (100 - 6)*5 |
| section idlerAxisX (x = 60) | 460 mm2, 2 loops | 0.2 % | derived | (100 - 8)*5 |
| section outputAxisX (x = 120) | 460 mm2, 2 loops | 0.2 % | derived | (100 - 8)*5 |
| face bottom (z = -5, -z) | 19371.19 mm2 | 0.2 % | derived | same plan area as midZ |
| face top (z = 0, +z) | position only | 0.05 | stated | seat; no area so the length edit keeps the pinned check valid |
| dimensions | 195 / 100 / 5 | 0.05 | stated | bbox x, bbox y, bottom-to-top |
| blockout band | 94500..97600 mm3 | - | derived | envelope box 97500 (plus 0.1 %) down to about 3 % below it; the finished part (96855.97) lies inside |

Edit tests and feasible intervals:

- `plateThickness` +1: the added layer z = -6..-5 has the holed plan area, volume delta = 19500 - 41*pi = +19371.19,
  bbox delta (0, 0, 1). Feasible for plateThickness > 0; sweep 4, 5, 6; infeasible delta -5 (thickness 0) must fail an
  assert.
- `plateLength` +10: the added strip x = 170..180 carries no hole, volume delta = 10*100*5 = +5000, bbox delta (10, 0, 0).
  Feasible while the output hole stays inside the plate, plateXMin + plateLength > outputX + outputHoleDiameter/2, i.e.
  plateLength > 149; sweep 185, 195, 205; infeasible delta -50 (plateLength 145, +x end at 120 through the output hole)
  must fail an assert.
- Neither edit moves the seat face or any hole axis or diameter, so interfaces `seat` (face `top`) and `jointAxes`
  (cylinders `pinionHole`, `idlerHole`, `outputHole`) are pinned. The cylinder entries carry no length because the
  thickness edit changes the hole length; the x-sections and void probes prove the holes run through.

## 6. Defaults retained

- Envelope and dimension tolerance 0.05 mm, parameter tolerance 0.01 mm, hole radius tolerance 0.02 mm: digital
  comparison thresholds for exact B-rep geometry, not manufacturing tolerances.
- Volume and surface-area tolerance 10 (about 0.01 % and 0.02 %): tight enough that a missing D6 hole (141 mm3 of volume,
  38 mm2 of area) or a D6/D8 swap (110 mm3) fails.
- Material, density and process left null: the sources do not state them, so no mass claim is made.
- `release_status: reconstruction` kept from the template.

## 7. Unrepresentable or low-confidence features

- None of the stated geometry is unrepresentable; every value is stated in text.
- Hole fit class, the shafts or pins in the holes, and any edge breaks are not specified; the holes are nominal diameter and
  the edges sharp (open questions).
- The gears, their bores and the joint motion belong to the separate designs and the `compound-train` assembly, not to this
  part.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
