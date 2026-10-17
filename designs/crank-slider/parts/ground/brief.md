# crank-slider-ground — design brief

## 1. Intent and configuration

Ground plate (body `ground`) of the offset crank-slider assembly `crank-slider`, modelled in its own frame, which is the
assembly frame: origin on the crank axis O on the plate's top face, z up, x parallel to the guide. A plain rectangular
plate 200 (x) x 70 (y) x 5 (z) from corner (-40, -30, -5) to (160, 40, 0) with one D6 through hole on the crank axis O at
(0, 0) along z; no rail, slot, boss or any other feature. One solid.

The top face z = 0 is the only mating face: it carries the crank's bottom face around O (revolute joint `crankPivot`, the
motor; the assembly mounts the crank at own-frame point [0, 0, 0], axis [0, 0, 1]) and the slider's bottom face sliding
along the guide line y = 10 parallel to +x (prismatic joint `guide`; mount point [0, 10, 0], axis [1, 0, 0]; the slider
spans x = 54..145 over a revolution). Authoritative source: `sources/crank-slider-spec.md` (text only; no images, no
reference model).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/crank-slider-spec.md | text | authoritative | cd01ebc4dc4d7289a786bef3bca834eb565dd9f6109941bbcc2ec04b879c0d1c | Ground row of the part table, frame, layers (ground z -5..0), joints, rest configuration; mm; no revision stated |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| plate length along x | 200 | mm | spec part table, Ground: plate 200 x 70 x 5 | 0.05 | stated |
| plate width along y | 70 | mm | spec part table, Ground | 0.05 | stated |
| plate thickness along z | 5 | mm | spec part table, Ground; layers: ground z -5..0 | 0.05 | stated |
| min corner | (-40, -30, -5) | mm | spec part table, Ground | 0.05 | stated |
| max corner | (160, 40, 0) | mm | spec part table, Ground | 0.05 | stated |
| pivot hole | D6 through, axis on O (0, 0) along z | mm | spec part table, Ground: D6 hole at the crank axis O | radius 0.02, axis 0.05 | stated |
| no other features (no rail, slot or boss) | none | - | intent | volume 20 mm3, face areas | stated |
| top face z = 0 carries the crank around O and the slider along y = 10 | z = 0 | mm | intent; spec joints and layers | 0.05 | stated |
| slider footprint on the plate over a revolution | x 54..145, y 2..18 | mm | intent (x span); spec slider 30 x 16 centred on B on the guide y = 10 (y span) | probes | stated / derived |
| separate solid | 1 | - | spec: four separate solids, no fused bodies | exact | stated |
| volume | 69858.63 | mm3 | intent (derived) | 20 | derived |
| material, density, process | - | - | not stated | - | open |
| hole fit, edge breaks | - | - | not stated | - | open |

Checks: the slider's wrist pin B stays within sqrt(70^2 - 10^2) = 69.28 to sqrt(130^2 - 10^2) = 129.61, so its 30 mm
block spans x = 54.28..144.61, inside the stated 54..145 and inside the plate (x up to 160). The crank's far end reaches
30 + 8 = 38 from O and overhangs the plate's -y edge (y = -30) by 8 mm at 270 deg; it lies in the layer above (z 0..5), so
that is no interference and needs no plate feature.

## 4. Coordinate frame, scale, and measurement method

- Origin: on the crank axis O on the plate's top face (the centre of the D6 hole at z = 0). This is the assembly frame, so
  the assembly places the plate with the identity transform.
- +x: parallel to the guide (the slider moves along +x); plate x = -40..160. +y: toward the guide offset; guide line
  y = 10; plate y = -30..40. +z: up, parallel to every pin axis; top face z = 0, bottom face z = -5.
- Datums: A = top face z = 0; B = crank axis O (x = 0, y = 0, along z); C = guide line y = 10, z = 0, parallel to +x.
- Scale and method: all values are read from the text table in millimetres; there are no images, drawings or meshes, so
  no pixel measurement or rectification was needed.
- Edit convention: the plate hangs below datum A (z = -plateThickness..0) and starts at plateXMin, plateYMin. A thickness
  edit moves only the bottom face; a length edit moves only the +x end face. Datums A, B and C never move.

## 5. Measurement and inference record

L = plateLength, W = plateWidth, T = plateThickness, r = pivotHoleDiameter / 2, V = volume.

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| plateLength | 200 mm | 0.01 | stated | spec Ground row: plate 200 x 70 x 5 |
| plateWidth | 70 mm | 0.01 | stated | spec Ground row |
| plateThickness | 5 mm | 0.01 | stated | spec Ground row; layers ground z -5..0 |
| plateXMin | -40 mm | 0.01 | stated | spec Ground row: corner (-40, -30, -5) |
| plateYMin | -30 mm | 0.01 | stated | spec Ground row: corner (-40, -30, -5) |
| pivotHoleDiameter | 6 mm | 0.01 | stated | spec Ground row: D6 hole at O (0, 0) |
| volume | 69858.63 mm3 | 20 | derived | L W T - pi r^2 T = 70000 - 45 pi (the hole is 141.37, so a missing hole fails) |
| surface area | 30737.70 mm2 | 5 | derived | 2 (L W - pi r^2) + 2 (L + W) T + 2 pi r T = 30700 + 12 pi |
| centre of mass | (60.1214, 5.0101, -2.5) | 0.05 | derived | x = L W T (plateXMin + L/2) / V = 4200000 / V; y = L W T (plateYMin + W/2) / V = 350000 / V; z = -T/2 |
| face bottom (z = -5, -z) | 13971.73 mm2 | rel 0.001 | derived | L W - pi r^2 = 14000 - 9 pi |
| face top (z = 0, +z) | position only | 0.05 | derived | pinned datum A; no area so the length edit leaves it intact |
| faces xMin / xMax (x = -40 / 160) | 350 mm2 each | rel 0.002 | derived | W T |
| faces yMin / yMax (y = -30 / 40) | 1000 mm2 each | rel 0.002 | derived | L T |
| dimensions lengthX / widthY / thicknessZ | 200 / 70 / 5 mm | 0.05 | stated | between the named face pairs |
| cylinder pivotHole | D6, axis (0, 0) along z, hole | r 0.02, axis 0.05 | stated | no length, so the thickness edit leaves this pinned item intact |
| cylinder count pivotHoles | 1 | exact | stated | only one D6 vertical hole |
| section midZ (z = -2.5) | 13971.73 mm2, 1 loop, 1 hole | rel 0.001 | derived | L W - pi r^2 |
| section pivotX (x = 0) | 320 mm2, 2 loops, 0 holes | rel 0.005 | derived | W T - 2 r T = 350 - 30 |
| section guideLine (y = 10) | 1 loop, 0 holes | exact | derived | one continuous strip under the guide; nominal area L T = 1000 left out because edits change it |
| probes inMaterial / guideSupport | solid | - | derived | (100, 10, -2.5), (-35, -25, -2.5), (155, 35, -2.5); slider footprint corners (54 / 145, 2 / 18, -2.5) |
| probe inPivotHole | void (0, 0, -2.5) | - | derived | 3 mm from the bore wall, 2.5 mm from both faces |
| edit plateThickness +1 | dV = +13971.73, bbox +[0, 0, 1] | rel 0.01 | derived | (L W - pi r^2) * 1; the plate grows downward, datum A stays at z = 0 |
| edit plateLength +10 | dV = +3500, bbox +[10, 0, 0] | rel 0.01 | derived | 10 W T; plateXMin stays -40, so the hole and the guide do not move |
| blockout band | 68000..71000 mm3 | - | derived | envelope-only plate L W T = 70000 fills the full bbox; the band also covers the finished 69858.63 |

Feasible intervals, sweeps and infeasible edits (the model must `assert` the infeasible cases, never build them):

- plateThickness: feasible T > 0. Sweep [4, 5, 6]. Infeasible delta -5 (T = 0): `assert plateThickness > 0`.
- plateLength: the hole must lie inside the plate, plateXMin + L > r (L > 43); the plate must still carry the slider's
  travel to x = 145, so L >= 185 for the assembly. Sweep [190, 200, 220] stays inside both. Infeasible delta -200 (L = 0,
  the hole falls outside the plate): `assert plateXMin + plateLength > pivotHoleDiameter / 2`.
- The hole must also stay inside the plate in y and behind O in x: plateYMin < -r < r < plateYMin + W and plateXMin < -r.

## 6. Defaults retained

- Envelope and dimension tolerance 0.05 mm, parameter tolerance 0.01 mm (template defaults): every dimension is stated
  exactly and measured on the exact B-rep.
- Volume tolerance 20 mm3 and surface-area tolerance 5 mm2: absorb tessellation of the D6 bore while staying well below
  the hole's own volume (141.37) and area contribution (37.70).
- Sharp edges: no fillet or chamfer is stated.
- Material, density and process null: none stated, and the contract makes no mass claim.
- release_status reconstruction (template default).

## 7. Unrepresentable or low-confidence features

- The guide is an interface only: the plate has no rail or slot along y = 10. It is pinned by datum face `top` and the
  `guideLine` section, and the slider footprint by the `guideSupport` probes. The prismatic constraint (no rotation, travel
  along +x) is enforced by the assembly, not by this part.
- No symmetry is declared: the plate rectangle is symmetric about x = 60 and y = 5, but the pivot hole at (0, 0) breaks
  both planes and the source states no mirror plane.
- The D6 hole's fit to its pivot pin (clearance or fit class) is not stated; it is modelled at nominal D6.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
