# gear-train-carrier — design brief

## 1. Intent and configuration

Carrier plate of the `gear-train` assembly (a 20-tooth pinion and a 40-tooth wheel, module 2, on revolute joints),
modelled in its own frame, which is the assembly (specification) frame: origin on the pinion axis in the top face,
+x toward the wheel axis, +z up. A 110 x 50 x 5 mm rectangular plate from corner (-25, -25, -5) to (85, 25, 0) with
sharp edges and two clearance holes along z through the full thickness: D6 on the pinion axis at (0, 0) and D8 on the
wheel axis at (60, 0). The top face z = 0 is the seat of both gears; the hole axes are the joint axes `pinionSpin`
(point (0, 0, 0), axis +z) and `wheelSpin` (point (60, 0, 0), axis +z). One solid. The only source,
`sources/gear-pair-spec.md`, is authoritative; the gears themselves are separate designs.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/gear-pair-spec.md | text | authoritative | 0acea6d35513df93499f95e7242721b64488c45819f6e58ebd09ed627fb09d87 | 'Carrier plate' row, pinion/wheel axis rows, 'Centre distance' row and the frame paragraph |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| plate size | 110 x 50 x 5 | mm | spec, 'Carrier plate' | 0.05 (envelope) | stated |
| plate corners | (-25, -25, -5) to (85, 25, 0) | mm | spec, 'Carrier plate' | 0.05 (envelope) | stated |
| pinion clearance hole | D6 on (0, 0), through z = -5..0 | mm | spec, 'Pinion' + 'Carrier plate' | 0.02 radius, 0.05 axis | stated |
| wheel clearance hole | D8 on (60, 0), through z = -5..0 | mm | spec, 'Wheel' + 'Carrier plate' | 0.02 radius, 0.05 axis | stated |
| centre distance | 60 | mm | spec, 'Centre distance' | 0.05 (wheel axis position) | stated |
| gear seat | top face z = 0, gears touch it | mm | spec, frame paragraph | 0.05 | stated |
| edges | sharp, no fillets or chamfers | | intent | | stated |
| solid count | 1 | | intent (separate bodies per design) | | stated |
| material / process | not given | | | | open |

## 4. Coordinate frame, scale, and measurement method

Origin: the centre of the D6 pinion hole in the top face (point (0, 0, 0)). +x runs from the pinion axis to the wheel
axis (x = 60), +z is up along both gear axes, +y completes the right-handed frame; the plate spans x = -25..85,
y = -25..25, z = -5..0. Datums: A = top face z = 0 (gear seat), B = pinion axis (x = 0, y = 0), C = wheel axis
(x = 60, y = 0). This is the frame the source and the assembly use, so the assembly places the part with the identity
transform. No images, drawings or meshes: every value is read from the text table; no scaling or rectification.

Build rules for the modeller: the plate is the rectangle x = plateXMin..plateXMin + plateLength,
y = -plateWidth/2..plateWidth/2, extruded **downward** from z = 0 to z = -plateThickness (the seat face never moves);
the holes are cut with cylinders that overrun both faces into air.

Feasible intervals of the edit-tested parameters (the source must `assert` them): plateThickness > 0 (sweep 3, 5, 8;
infeasible delta -5 gives 0); plateWidth > max(pinionBoreDiameter, wheelBoreDiameter) = 8 so the D8 hole does not split
the plate (sweep 40, 50, 60; infeasible delta -45 gives 5).

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| plateLength | 110 mm | 0.01 | stated | spec 'Carrier plate' 110 x 50 x 5 |
| plateWidth | 50 mm | 0.01 | stated | spec 'Carrier plate'; centred on y = 0 (corners y = -25..25) |
| plateThickness | 5 mm | 0.01 | stated | spec 'Carrier plate'; corners z = -5..0 |
| plateXMin | -25 mm | 0.01 | stated | spec corner (-25, -25, -5) |
| pinionBoreDiameter | 6 mm | 0.01 | stated | spec 'Pinion' bore D6, 'Carrier plate' D6 hole |
| wheelBoreDiameter | 8 mm | 0.01 | stated | spec 'Wheel' bore D8, 'Carrier plate' D8 hole |
| centerDistance | 60 mm | 0.01 | stated | spec wheel axis at (60, 0); (20 + 40) x 2 / 2 = 60 |
| volume | 27107.30 mm3 | rel 0.001 | derived | 110*50*5 - pi*(3^2 + 4^2)*5 = 27500 - 125*pi |
| surface area | 12662.83 mm2 | rel 0.002 | derived | 2*(5500 - 25*pi) + 320*5 + pi*(6 + 8)*5 = 12600 + 20*pi |
| centre of mass | (29.878, 0, -2.5) | 0.05 | derived | x = (27500*30 - 80*pi*60)/(27500 - 125*pi); y by symmetry; z = -5/2 |
| sections midZ / nearTop / nearBottom (z = -2.5, -0.5, -4.5) | 5421.46 mm2, 1 loop, 2 holes | rel 0.002 | derived | 5500 - 25*pi; through-holes open at both faces |
| section boreLine (y = 1) | 482.99 mm2, 3 loops | rel 0.005 | derived | 550 - 5*(2*sqrt(9 - 1) + 2*sqrt(16 - 1)) |
| bottom face area | 5421.46 mm2 | rel 0.002 | derived | 5500 - 25*pi |
| edit plateThickness +1 | dV = +5421.46, bbox +[0, 0, 1] | rel 0.02 | derived | (plateLength*plateWidth - pi/4*(6^2 + 8^2)) * 1; top stays at z = 0 |
| edit plateWidth +10 | dV = +5500, bbox +[0, 10, 0] | rel 0.02 | derived | 10 * plateLength * plateThickness; holes stay on y = 0 |
| blockout band | 26500..27600 mm3 | | derived | plain 110 x 50 x 5 box = 27500 reaches every envelope face; finished part 27107 |

Interfaces pin only items no edit test moves: `top` (plane z = 0, no area), `pinionBore` and `wheelBore` (axis and
diameter, no length), so the width and thickness edits leave them intact.

## 6. Defaults retained

- `release_status: reconstruction` from the template; material, density and process left null (not stated, no mass
  claim).
- Envelope tolerance 0.05 mm and parameter tolerances 0.01 mm (digital comparison of exact, stated values).
- Hole radius tolerance 0.02 mm: holes are exact cylinders in the STEP.

## 7. Unrepresentable or low-confidence features

- The plate is mirror-symmetric about y = 0, but the source states no mirror plane and both hole walls cross it, so no
  `symmetry` item is declared; the centre of mass y = 0 and the centred plate cover it.
- Running fit of the holes against pins or shafts is not stated; D6 and D8 are modelled at nominal.
- Gear teeth, backlash and the meshing sweep belong to the pinion and wheel designs and the assembly, not this part.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
