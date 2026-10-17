# rack-pinion-base — design brief

## 1. Intent and configuration

Base plate of the `rack-pinion` assembly, modelled in the assembly frame: a 240 x 80 x 5 mm box from corner (-120, -50, -5) to (120, 30, 0) with a D6 clearance hole through its thickness on the pinion axis at (0, 0). The pinion stands on the flat top face z = 0 centred on the origin (revolute joint `pinionSpin`, point [0, 0, 0], axis +z); the rack slides on the same face along +x with its footprint y = -32 .. -18 (slider joint `rackSlide`, point [0, -20, 0], axis +x). The D6 hole is coaxial with the pinion's D6 bore. One solid; the pinion and rack are separate designs. Authoritative source: `sources/rack-pinion-spec.md` (text only, no images).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/rack-pinion-spec.md | text | authoritative | 87f6a8bbc15c559e23899017105cd36ee8b503a6238b00213d3b99103d903561 | 'Base plate' table row, frame paragraph (plate top z = 0, rack pitch line y = -20), rack footprint from the rack rows |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| plate size | 240 x 80 x 5 | mm | spec 'Base plate' row | 0.05 bbox | stated |
| plate corners | (-120, -50, -5) to (120, 30, 0) | mm | spec 'Base plate' row, intent | 0.05 | stated |
| clearance hole | D6 through the thickness at (0, 0), axis z | mm | spec 'Base plate' row | 0.02 radius | stated |
| deck | flat top face z = 0 carrying pinion and rack | mm | spec frame paragraph, intent | 0.05 | stated |
| rack footprint on the deck | y = -32 .. -18 (pitch line -20, back face 12 below, tips 2 above) | mm | intent; spec rack rows | n/a (other part) | stated |
| hole coaxial with pinion bore | axis (0, 0), +z | mm | intent | 0.05 axis | stated |
| separate solid | 1 solid, not fused | | spec first paragraph | exact | stated |
| material, process, edge finish | not given | | | | open |

## 4. Coordinate frame, scale, and measurement method

Origin on the pinion axis at the plate's top face (centre of the D6 hole at z = 0); this is the assembly frame, so the plate is placed with the identity transform. +x along the rack's travel, +y from the rack toward the pinion, +z up along the pinion axis. Datum A is the deck z = 0, datum B the hole axis, datum C the mirror plane x = 0 (the stated corners are symmetric in x and the hole lies at x = 0). All values are read from text; there are no images or reference meshes, so no scaling or rectification was needed.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| plateLength | 240 mm | 0.01 | stated | 'Base plate' row; centred on x = 0 (corners x = +/-120) |
| plateWidth | 80 mm | 0.01 | stated | 'Base plate' row |
| plateThickness | 5 mm | 0.01 | stated | 'Base plate' row; bottom at z = -plateThickness |
| plateYMin | -50 mm | 0.01 | stated | corner (-120, -50, -5) |
| plateYMax | 30 mm | 0.01 | derived | plateYMin + plateWidth; matches corner (120, 30, 0) |
| holeDiameter | 6 mm | 0.01 | stated | 'clearance hole D6 at (0, 0)' |
| volume | 95858.63 mm^3 | rel 0.0005 | derived | 240 x 80 x 5 - pi x 3^2 x 5 = 96000 - 141.37 |
| surface area | 41637.70 mm^2 | rel 0.001 | derived | 2(240x80 + 240x5 + 80x5) - 2 pi 3^2 + 2 pi 3 x 5 = 41600 - 56.55 + 94.25 |
| centre of mass | (0, -10.015, -2.5) | 0.05 | derived | box centroid (0, -10, -2.5), hole removed at (0, 0, -2.5): y = -10 x 96000 / 95858.63 |
| section midZ (z = -2.5) | 19171.73 mm^2, 1 loop, 1 hole | rel 0.001 | derived | 240 x 80 - pi x 3^2 |
| section axisX (x = 0) | 370 mm^2, 2 loops | rel 0.002 | derived | (80 - 6) x 5 |
| faces bottom / front, back / left, right | 19171.73 / 1200 / 400 mm^2 | rel 0.001 | derived | plan less hole; 240 x 5; 80 x 5 |
| edit plateThickness +1 | +19171.73 mm^3, bbox [0, 0, 1] | rel 0.01 | derived | (L W - pi r^2) x 1; the plate grows downward, the deck stays at z = 0 |
| edit plateLength +20 | +8000 mm^3, bbox [20, 0, 0] | rel 0.01 | derived | 20 x W x T; grows 10 mm at each end, symmetric about x = 0 |
| blockout band | 92000 .. 96100 mm^3 | | derived | the envelope box without the hole is 96000 |

Feasible intervals: plateThickness > 0 (sweep 3, 5, 8; infeasible delta -5 gives 0, the model must assert plateThickness > 0). plateLength > holeDiameter (sweep 200, 240, 280; infeasible delta -236 gives 4 < 6, where the hole would cut the plate in two, so the model must assert plateLength > holeDiameter). Neither edit moves the pinned items: the deck face position, the hole axis and diameter, and the mirror plane x = 0.

## 6. Defaults retained

- Sharp edges everywhere (no chamfers or fillets are stated).
- material, density and process left null: no mass claim is made.
- release_status `reconstruction` from the template.
- The hole cylinder check carries no length because its length follows plateThickness; through-ness is checked by the two void probes, the sections and the volume.

## 7. Unrepresentable or low-confidence features

- The hole's fit class, chamfer or counterbore, and the part passing through it, are not described.
- Over one pinion revolution the rack travels 125.66 mm, so it overhangs the plate ends x = +/-120 (up to 42.8 mm for a -180..180 deg sweep); the plate length is stated, so it is kept. This is an assembly observation, not a plate feature.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
