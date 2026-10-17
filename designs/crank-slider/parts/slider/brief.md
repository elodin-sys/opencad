# crank-slider-slider — design brief

## 1. Intent and configuration

The slider body of the offset crank-slider mechanism (assembly `crank-slider`), drafted and modelled in its own frame. It is a 30 x 16 x 5 mm block, 30 along the guide, centred on one Ø6 through hole for the wrist pin B. The bottom face z = 0 slides on the ground's top face along +x (prismatic guide, no rotation); the top face z = 5 carries the connecting rod's bottom face at B (revolute about +z). One solid; the other three bodies (ground, crank, rod) are separate designs. The only source is `sources/crank-slider-spec.md` (text, authoritative); the intent restates its Slider row in this part's frame.

Assembly placement: the assembly attaches the joint `guide` at own-frame point [0, 0, 0] with axis [1, 0, 0] and the joint `wristPin` at own-frame point [0, 0, 5] with axis [0, 0, 1]. At rest the own frame is translated to B = (129.498744, 10, 0) with no rotation (the guide is parallel to +x, every pin axis parallel to +z).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/crank-slider-spec.md | text | authoritative | cd01ebc4dc4d7289a786bef3bca834eb565dd9f6109941bbcc2ec04b879c0d1c | parts table (Slider row), frame and layers, part frames, rest configuration, joints; mm, no revision stated |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| block length along the guide (x = -15..15) | 30 | mm | spec Slider row; intent | 0.01 (parameter), 0.05 (dimension lengthX) | stated |
| block width across the guide (y = -8..8) | 16 | mm | spec Slider row; intent | 0.01 / 0.05 (widthY) | stated |
| block thickness (z = 0..5, slider layer) | 5 | mm | spec Slider row and layers | 0.01 / 0.05 (thicknessZ) | stated |
| wrist-pin hole: one Ø6 through hole on the origin along z | 6 | mm | spec Slider row: Ø6 hole at B | cylinder pinBore, cylinder count d6Holes = 1 | stated |
| block centred on the hole | mirror planes x = 0, y = 0 | | spec: centred on B | symmetry mirrorX, mirrorY (default bands) | stated |
| guide interface: bottom face z = 0 slides along +x, no rotation | z = 0, normal -z | mm | spec joints; intent | face bottom (envelope tolerance) | stated |
| wrist-pin interface: top face z = 5 carries the rod at B, revolute about +z | z = 5, normal +z | mm | spec joints and layers (rod z 5..10); intent | face top, cylinder pinBore | stated |
| volume | 2258.63 | mm3 | intent (derived) | tolerance_rel 0.002 | derived |
| single solid (no fused bodies) | 1 | | spec: four separate solids | solid_count | stated |
| material, density, process | | | not stated | | open |
| pin fit and hole tolerance, edge breaks, guide running clearance | | | not stated | | open |

## 4. Coordinate frame, scale, and measurement method

Origin at the centre of the Ø6 hole on the bottom face (z = 0). +x along the guide and the 30 mm length, +y across the guide along the 16 mm width, +z along the wrist-pin axis up through the 5 mm thickness. Datums: A = bottom face z = 0 (guide face, normal -z); B = hole axis through the origin along +z; C = top face z = 5 (rod face, normal +z); D = mid-planes x = 0 and y = 0. This is the part frame the spec prescribes ("the slider's own origin is at its hole centre on its bottom face, its 30 mm length along +x") and the frame the assembly's joint frames reference.

No images, drawings or meshes: every value is read from the text. No scale or rectification was needed.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| blockLength | 30 mm | 0.01 | stated | Slider row "block 30 (along the guide)"; edit test +4: volume_delta = 4 * blockWidth * blockThickness = 320, bbox_delta [4, 0, 0] (grows symmetrically about the hole) |
| blockWidth | 16 mm | 0.01 | stated | Slider row "30 x 16 x 5"; edit test +2: volume_delta = 2 * blockLength * blockThickness = 300, bbox_delta [0, 2, 0] |
| blockThickness | 5 mm | 0.01 | stated | Slider row and layers (slider z 0..5); no edit test: it moves the top face (wrist-pin interface) into the rod layer z 5..10 |
| holeDiameter | 6 mm | 0.01 | stated | Slider row "Ø6 hole at B"; no edit test: the bore is the wrist-pin interface shared with the rod's Ø6 hole |
| volume | 2258.63 mm3 | rel 0.002 | derived | 30 * 16 * 5 - pi/4 * 6^2 * 5 = 2400 - 45 pi = 2258.628 |
| surface_area | 1457.70 mm2 | rel 0.005 | derived | 2 * (480 - 9 pi) + 2 * 5 * (30 + 16) + pi * 6 * 5 = 903.451 + 460 + 94.248 = 1457.699 |
| center_of_mass | (0, 0, 2.5) | 0.05 | derived | mirror planes x = 0, y = 0; prismatic through z = 0..5 |
| section midZ (z = 2.5) | area 451.726, 1 loop, 1 hole | default | derived | 30 * 16 - 9 pi |
| section acrossX (x = 1) | area 51.716, 2 loops, 0 holes | default | derived | 2 * 5 * (8 - sqrt(9 - 1)); placed 1 mm off the axis so the cut avoids the bore seam and tessellation vertices at x = 0 |
| faces bottom / top | z = 0 normal - / z = 5 normal +, centre (0, 0) | envelope 0.05 | stated | interface faces; no area on them because the length and width edits change their area (the area is checked by midZ) |
| cylinder pinBore | Ø6, axis (0, 0, z), length 5, t 0..5 | default | stated | Slider row and intent |
| dimensions lengthX / widthY / thicknessZ | 30 / 16 / 5 | 0.05 | stated | bbox extents; thicknessZ between faces bottom and top |
| probes inMaterial | (±9, ±4, 2.5) | | derived | one per quadrant, >= 2.5 mm from every face and > 6 mm from the bore |
| probes inBore | (0, 0, 1.5), (0, 0, 3.5), (-1.5, 0, 2.5) | | derived | >= 1.5 mm from the bore wall and from both faces |
| blockout band | 2200..2450 mm3 | | derived | covers the envelope box 2400 (no hole) and the finished 2258.63 with a few percent margin |

Edit-test feasibility (the part source must assert these):
- blockLength: feasible for blockLength > holeDiameter (a shorter block is cut apart by the hole). Sweep [20, 30, 40] stays inside; the infeasible delta -26 (blockLength = 4) must fail an assert. For the assembly, the slider's -x end must stay outside the crank's reach (radius 38 about O) at the folded position B_x = sqrt(70^2 - 10^2) = 69.282, so blockLength < 2 * (69.282 - 38) = 62.56; the sweep respects that too.
- blockWidth: feasible for blockWidth > holeDiameter (the hole must not break out of the sides). Sweep [10, 16, 22] stays inside; the infeasible delta -12 (blockWidth = 4) must fail an assert.
- Both edits keep the block centred on the hole, so the interface checks (bottom, top, pinBore, mirrorX, mirrorY) are unchanged by them.

## 6. Defaults retained

- Envelope tolerance 0.05 mm and parameter tolerances 0.01 mm: exact prismatic geometry, no image uncertainty.
- Volume tolerance_rel 0.002, surface area tolerance_rel 0.005, centre of mass 0.05 mm: analytic values of an exact B-rep; the looser area band absorbs tessellated bore area.
- Symmetry bands left at the evaluator defaults: the sources state the centring, not a tighter band.
- release_status `reconstruction`; material, density and process null (not stated; no mass claim).
- Sharp edges and a nominal 6.000 mm bore (no edge breaks or fit stated).

## 7. Unrepresentable or low-confidence features

- The prismatic guide has no physical realisation in the spec: no rail, slot or key on either body, so the no-rotation constraint is kinematic only (the assembly's joint), and no running clearance to the ground's top face is stated.
- The wrist pin itself is not a body in this design; only its Ø6 bore is encoded. The pin fit (clearance or press) is not stated.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
