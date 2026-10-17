# four-bar-crank — design brief

## 1. Intent and configuration

The crank link of the planar crank-rocker four-bar linkage (assembly `four-bar`), drafted in its own frame. It is a stadium plate, 5 thick and 16 wide: the tangent hull of two R8 circles centred on hole O2 at the origin and hole A at (40, 0, 0), extruded z = 0..5 (overall x -8..48, y -8..8). Two Ø6 through holes run along z at (0, 0) and (40, 0). One solid; no other features.

The only source, `sources/four-bar-spec.md`, is authoritative. The part frame follows its rule "every link has its first hole at its own origin, its second hole on +x at the link length, and its bottom face at z = 0".

Configuration in the assembly: joint pinO2 (revolute, the motor) attaches the crank at own-frame point (0, 0, 0), axis +z, with the bottom face seated on the ground plate's top face. Joint pinA (revolute) mounts the coupler's first hole at own-frame point (40, 0, 5), axis +z, on the crank's top face. The crank occupies layer z 0..5 of the stack (ground -5..0, coupler 5..10, rocker 10..15). At rest the crank is at 0 deg, so A sits at (40, 0).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/four-bar-spec.md | text | authoritative | aececd85a2ba8a2e020775f05a44f1bd1c3a505c8c8c5ed634606d975490bf17 | link table (crank O2-A 40, stadium 5 thick, 16 wide, R8 ends, Ø6 holes), part-frame rule, layer stack; units mm; no revision stated |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| frame origin at hole O2 centre on the bottom face | (0, 0, 0) | mm | spec part-frame rule; intent | 0.05 | stated |
| hole A centre on +x | (40, 0, 0) | mm | spec link table "O2 to A: 40"; intent | 0.05 | stated |
| bottom face / top face | z = 0 / z = 5 | mm | spec "5 thick", layer "crank z 0..5"; intent | 0.05 | stated |
| stadium width, straight sides | 16; y = -8 and y = 8 from x = 0 to x = 40 | mm | spec "16 wide"; intent | 0.05 | stated |
| semicircular ends | R8 centred on both holes | mm | spec "semicircular ends of radius 8"; intent | 0.05 | stated |
| overall extents | x -8..48, y -8..8, z 0..5 | mm | intent | 0.05 | stated |
| through holes along z | 2 x Ø6 at (0, 0) and (40, 0) | mm | spec "Ø6 holes"; intent | 0.05 | stated |
| solid count | 1 | – | intent "one solid"; spec "four separate solids" | exact | stated |
| interface pivot O2 | bottom face around O2 seats on the ground's top face; motor joint axis at (0, 0), +z | – | intent; orchestrator joint pinO2 | 0.05 | stated |
| interface pin A | top face z = 5 around A seats the coupler; joint axis at (40, 0), +z, point (40, 0, 5) | – | intent; orchestrator joint pinA | 0.05 | stated |
| no other features | – | – | intent | – | stated |
| material, density, process | not given | – | – | – | open |
| hole fit class, edge breaks | not given | – | – | – | open |

## 4. Coordinate frame, scale, and measurement method

The origin is the centre of hole O2 on the bottom face. +x runs from O2 toward A along the link centreline, with A at x = 40. +y runs across the 16 mm width; the straight sides are at y = +-8 and y = 0 is a mirror plane. +z runs up along the pin axes, from the bottom face z = 0 to the top face z = 5. Datums: A is the bottom face z = 0 (the ground seat); B is the O2 bore axis (pinO2); C is the A bore axis (pinA); D is the top face z = 5 (the coupler seat). This is the part frame that the source prescribes and that the assembly's joint frames use.

No images, drawings or meshes are supplied. Every dimension is quoted from the text, so no pixel scale or rectification applies. Acceptance values are computed analytically from the stated parameters.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| linkLength | 40 mm | 0.01 | stated | spec link table "Crank: O2 to A: 40"; intent "A at (40, 0, 0)" |
| linkWidth | 16 mm | 0.01 | stated | spec "stadium plate 5 thick, 16 wide"; intent "y = -8 and y = 8" |
| endRadius | 8 mm | 0.01 | derived | linkWidth / 2 (a tangent hull of two circles is 2R wide); also stated as R8 |
| plateThickness | 5 mm | 0.01 | stated | spec "5 thick", layer "crank z 0..5"; intent "z = 0 .. z = 5" |
| holeDiameter | 6 mm | 0.01 | stated | spec "Ø6 holes"; intent "Two Ø6 through holes" |
| volume | 3922.566 mm³ | rel 0.002 | derived | t (W L + pi R² - 2 pi (d/2)²) = 5 (640 + 64 pi - 18 pi) = 3200 + 230 pi |
| surface area | 2408.850 mm² | rel 0.005 | derived | faces 2 (640 + 46 pi) + outer wall 5 (80 + 16 pi) + bores 2 x 5 x 6 pi = 1680 + 232 pi |
| centre of mass | (20, 0, 2.5) | 0.05 | derived | mirror symmetric about x = L/2 = 20 (identical holes and ends) and y = 0; z = t/2 |
| section midZ (z = 2.5) | 784.513 mm², 1 loop, 2 holes | rel 0.01 | derived | 640 + 46 pi |
| section webX (x = 20) | 80 mm², 1 loop, 0 holes | rel 0.01 | derived | W t = 16 x 5 |
| faces bottom / top | z = 0 (-z) / z = 5 (+z), centroid (20, 0) | 0.05 | stated | area left to midZ, so the seats stay pinnable under both edit tests |
| faces sideNegY / sidePosY | y = -8 / y = 8, area 200 mm² each | rel 0.01 | derived | L t = 40 x 5 |
| cylinders holeO2 / holeA | Ø6 hole, axis (0, 0) / (40, 0), +z, length 5, t 0..5 | 0.05 | stated | through bores |
| cylinders endO2 / endA | R8 convex half cylinders, axes (0, 0) / (40, 0), length 5 | 0.05 | stated | the semicircular ends |
| dimensions thicknessZ / widthY / lengthX | 5 / 16 / 56 mm | 0.05 | stated / stated / derived | lengthX = L + 2R = 40 + 16 |
| cylinder count bores | 2 x Ø6 holes along z | exact | stated | "Two Ø6 through holes" |
| probes | solid: web, beside and outboard of each bore; void: each bore, 1.5 off axis; void: four bbox corners outside the R8 ends | – | derived | every void point is at least 1.19 mm from any declared surface (corner points: 9.19 from the end axis vs R8) |
| symmetry mirrorY | plane y = 0, max 0.1, p95 0.05 | – | stated | sides y = +-8 and holes on y = 0 |
| blockout band | 3850..4300 mm³ | – | derived | plain stadium 3200 + 320 pi = 4205.3 (with bores 3922.6); the 56 x 16 x 5 box (4480) is excluded on purpose |
| edit linkWidth +2 | dV = +667.035 mm³, bbox +[2, 2, 0], increase | rel 0.02 | derived | t (dW L + pi (9² - 8²)) = 5 (80 + 17 pi) = 400 + 85 pi; endRadius follows linkWidth / 2 |
| edit holeDiameter +1 | dV = -102.102 mm³, bbox 0, decrease | rel 0.02 | derived | -t 2 pi (3.5² - 3²) = -32.5 pi |

Feasible intervals and infeasible edits (the model must `assert` these):

- `linkWidth` needs holeDiameter < linkWidth (6 < linkWidth) so that material surrounds each bore. The sweep 12, 16, 20 stays inside this interval. Delta -11 (width 5) is infeasible: the bores would break out through the sides and ends.
- `holeDiameter` needs 0 < holeDiameter < linkWidth (16). The sweep 4, 6, 8 stays inside. Delta +11 (Ø17) is infeasible because the bore would be wider than the link.
- `endRadius` is always linkWidth / 2. It is never an independent literal.

The interfaces pin only items that neither edit test moves or resizes: the bottom and top planes (no area), the thicknessZ dimension and the mirrorY symmetry. The joint axes are verified by holeO2 and holeA but left unpinned, because the holeDiameter edit resizes them and the schema requires a diameter on every cylinder.

## 6. Defaults retained

- Material, density and process are left null, because the source states none. Mass properties use unit density, and nothing in the linkage kinematics depends on mass.
- Holes are modelled at nominal Ø6, with no fit allowance and no chamfers. All edges are sharp. The source states no edge breaks.
- Digital parameter tolerance is 0.01 mm and the envelope tolerance is 0.05 mm, as in the template. The symmetry band (max 0.1, p95 0.05) matches the exemplar's defaults.

## 7. Unrepresentable or low-confidence features

None on this part. Every feature is stated exactly. The following belong to the assembly contract, not to this part: the pin hardware (the joints are ideal revolute pins), the coupler point P, the rest angles and the motion predictions (rocker angle series, swing, P path).

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
