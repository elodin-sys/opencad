# compound-train-output — design brief

## 1. Intent and configuration

Output spur gear of the compound-train assembly, drafted in its own frame: 45 teeth, module 2, 20 deg pressure angle, zero profile shift, addendum 1.0 m and dedendum 1.25 m, every tooth thinned by 0.05 mm at the pitch circle, face width 8 (z = 0..8), a tooth centred on +x and a plain 8 mm through bore. In the assembly it turns on the plate's D8 hole at (120, 0) through the revolute joint outputSpin (own-frame point [0, 0, 0], axis +z) with its bottom face at z = 8.5, and meshes with the idler's 15-tooth gear at 60 mm centre distance. Authoritative sources: the user intent and `sources/compound-train-spec.md`.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/compound-train-spec.md | text | authoritative | e2734c43ae1d2aa36320d0b7680e21616422e902b471b3eb98295e3292296af5 | gear standards rows, output gear row, part-frame and tooth-phase paragraphs |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| tooth count | 45 | | intent, spec table | 0.01 | stated |
| module | 2 | mm | intent, spec table | 0.001 | stated |
| pressure angle | 20 | deg | intent, spec table | 0.01 | stated |
| profile shift | 0 | | intent, spec table | 0.001 | stated |
| addendum / dedendum | 1.0 / 1.25 | m | intent, spec table | 0.001 | stated |
| tooth thinning at pitch circle | 0.05 | mm | intent, spec backlash row | 0.001 | stated |
| face width, bottom at z = 0 | 8 | mm | intent, spec table | 0.01 | stated |
| through bore | 8 | mm | intent ('D8'), spec ('bore Ø8') | 0.01 | stated |
| tooth centred on +x | 0 | deg | intent, spec part-frame paragraph | symmetry 0.1 | stated |
| points per flank | 12-16 | | intent, spec | 2 | stated range |
| single solid | 1 | | spec ('four separate solids') | exact | stated |

## 4. Coordinate frame, scale, and measurement method

Origin on the gear axis in the bottom face. +z is the gear axis (bottom face z = 0, top face z = 8), +x runs through the centre of one tooth, and +y completes a right-handed frame. Datums: A is the bottom face, B the bore axis, C the plane y = 0. There are no images or meshes. Every value is stated in text or derived from the involute equations. Areas and volumes come from the exact integral \( A = \pi r_f^2 + z \int_{r_f}^{r_a} 2\psi(r)\, r\, dr - \pi (d/2)^2 \), where \( \psi(r) = s/(2 r_p) + \mathrm{inv}(\alpha) - \mathrm{inv}(\arccos(r_b/r)) \), evaluated with Simpson's rule (20,000 steps). The bounding box comes from a dense outline, 401 points per flank.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| teeth | 45 | 0.01 | stated | intent, spec table |
| gearModule | 2 | 0.001 | stated | intent, spec table |
| pressureAngle | 20 | 0.01 | stated | intent, spec table |
| profileShift | 0 | 0.001 | stated | intent, spec table |
| addendumCoeff | 1.0 | 0.001 | stated | intent, spec table |
| dedendumCoeff | 1.25 | 0.001 | stated | intent, spec table |
| backlashThinning | 0.05 | 0.001 | stated | half of the 0.10 mm circular backlash per mesh |
| faceWidth | 8 | 0.01 | stated | intent z = 0..8 |
| boreDiameter | 8 | 0.01 | stated | intent 'D8', spec 'bore Ø8' |
| pitchRadius | 45 | 0.001 | derived | gearModule * teeth / 2 |
| tipRadius | 47 | 0.001 | derived | pitchRadius + (addendumCoeff + profileShift) * gearModule |
| rootRadius | 42.5 | 0.001 | derived | pitchRadius - (dedendumCoeff - profileShift) * gearModule |
| baseRadius | 42.2862 | 0.001 | derived | pitchRadius * cos(pressureAngle) |
| toothThickness | 3.0916 | 0.001 | derived | gearModule * (pi/2 + 2 profileShift tan(pressureAngle)) - backlashThinning |
| flankPoints | 14 | 2 | inferred | middle of the stated 12-16 range |
| volume | 50035.6 | 0.3 % | derived | 8 * 6254.445 (section above) |
| surface area | 17312.9 | 1 % | derived | 2 * 6254.445 + 8 * perimeter 600.498 (flank 4.762, tip arc 1.485, root arc 1.776 per tooth, bore 25.133) |
| centre of mass | (0, 0, 4) | 0.05 | derived | uniform pattern, mid face width |
| midZ section | 6254.4, 1 loop, 1 hole | 0.3 % | derived | integral above |
| phaseY0 section | 652, 2 loops | 1 % | derived | ((47 - 4) + (42.5 - 4)) * 8; 45 is odd, so a space is centred on -x |
| envelope | x -46.9315..47, y +-46.9914, z 0..8 | 0.1 (bbox 0.05) | derived | tip arc on +x; tip corners of the teeth at 176/184 deg and 88/272 deg (tooth tip half-angle 0.9054 deg) |
| tipSpanX / tipSpanY | 93.9315 / 93.9828 | 0.05 | derived | envelope extents |
| edit faceWidth +2 | +12508.9 mm3, bbox (0, 0, 2) | 1 % | derived | 2 * 6254.445; feasible faceWidth > 0; sweep 6, 8, 12; infeasible delta -10 |
| edit boreDiameter +2 | -226.2 mm3, bbox 0 | 5 % | derived | -pi/4 (10^2 - 8^2) * 8; feasible 0 < boreDiameter < 2 rootRadius = 85; sweep 6, 8, 10; infeasible delta +80 |
| edit backlashThinning +0.05 | -80.55 mm3, bbox 0 | 10 % | derived | -teeth * (0.05 / pitchRadius) * (tipRadius^2 - rootRadius^2) / 2 * faceWidth (each flank rotates by 0.05 / (2 pitchRadius)) |
| blockout band | 53000..56500 | | derived | tip-circle disc pi 47^2 8 = 55518 (55116 with the bore) |

## 6. Defaults retained

Material, density and process remain null because the sources state none, so no mass is claimed. The release status stays `reconstruction`. The envelope tolerance is 0.1, so a tip-circle disc blockout fits: it reaches x = -47, 0.069 beyond the part's -x extreme. The finished part uses a bbox tolerance of 0.05. The symmetry band uses the exemplar values (0.1 max, 0.05 p95).

## 7. Unrepresentable or low-confidence features

The contract encodes no root fillet and no tip or face edge breaks, because the sources state none. The mesh with the idler (zero interference, flank gap at most 0.15 mm over one pitch) and the 6.5 deg rest phase are assembly-level checks. Pinning the bore itself would conflict with the bore edit test, so the outputSpin interface pins the bottom face (centroid on the axis) and the y = 0 symmetry plane. The bore axis is still checked by `bore` (axis tolerance 0.02).

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
