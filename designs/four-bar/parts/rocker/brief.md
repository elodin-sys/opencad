# four-bar-rocker — design brief

## 1. Intent and configuration

Rocker link of the planar crank-rocker four-bar linkage (`four-bar` assembly, body `rocker`), drafted and modelled in its own frame. It is a stadium plate 5 thick and 16 wide: the tangent hull of two R8 circles centred on O4 (0, 0) and B (80, 0), extruded z = 0..5, overall x -8..88, y -8..8, with two Ø6 through holes along z at O4 and B (80 between hole centres). One solid, no other features.

Interfaces: O4 is the ground pivot (joint `pinO4`, revolute about +z at own-frame [0, 0, 0]); the rocker's bottom face runs 10 above the ground's top face there, so nothing seats on it. The bottom face around B seats on the coupler's top face (joint `pinB`, revolute about +z at own-frame [80, 0, 0]). In the assembly the rocker occupies layer z 10..15 and rests at 90 deg about O4 (B at (100, 80)); that placement is the assembly's job, not this part's.

Authoritative source: `sources/four-bar-spec.md` (text, the only source). No images, drawings or reference models.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/four-bar-spec.md | text | authoritative | aececd85a2ba8a2e020775f05a44f1bd1c3a505c8c8c5ed634606d975490bf17 | link table (Rocker O4 to B: 80; stadium plate 5 thick, 16 wide, R8 ends, Ø6 holes), layer stack, part-frame rule, pins; mm; no revision stated |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| hole centre distance O4 to B | 80 | mm | spec link table; intent | 0.01 (digital) | stated |
| first hole O4 at the origin, B on +x | (0, 0, 0), (80, 0, 0) | mm | spec part-frame rule; intent | 0.05 axis offset | stated |
| bottom face z = 0, top face z = 5 (plate thickness) | 5 | mm | spec "5 thick"; intent | 0.01 | stated |
| stadium end radius (semicircular ends centred on the holes) | 8 | mm | spec; intent "two R8 circles" | 0.01 | stated |
| width (y -8..8) | 16 | mm | spec "16 wide"; intent | 0.01 | stated (= 2 * endRadius) |
| overall x extent -8..88 | 96 | mm | intent | 0.05 | stated |
| pin holes along z at O4 and B, through | Ø6 | mm | spec; intent | 0.01 | stated |
| one solid, no other features | 1 | - | intent | exact | stated |
| O4 = ground pivot (joint pinO4), nothing seats on the bottom face there | - | - | intent; orchestrator joint frames | - | stated |
| bottom face around B seats on the coupler's top face (joint pinB) | z = 0 | mm | intent; orchestrator joint frames | 0.05 | stated |
| material, density, process | - | - | not given | - | open |
| hole fit class, edge breaks | - | - | not given | - | open |

## 4. Coordinate frame, scale, and measurement method

Frame (the part frame the spec prescribes for every link, and the frame the assembly joints use): origin at the O4 hole centre on the bottom face; +x along the link centreline from O4 toward B (B hole centre at x = 80); +y across the 16 mm width, mirror plane y = 0; +z up along both pin axes, bottom face z = 0 to top face z = 5. Datums: A = bottom face z = 0; B = O4 hole axis (x = 0, y = 0, along z); C = B hole axis (x = 80, y = 0, along z).

Scale and measurement: all values are quoted from the text source in mm; nothing was read from pixels or meshes, so no scale or rectification applies. Acceptance values are analytic, computed from the stated parameters.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| linkLength | 80 mm | 0.01 | stated | spec "Rocker, O4 to B: 80"; intent "B at (80, 0, 0)" |
| endRadius | 8 mm | 0.01 | stated | spec "semicircular ends of radius 8 centred on its two holes" |
| linkWidth | 16 mm | 0.01 | derived | 2 * endRadius; matches the spec's "16 wide" |
| linkThickness | 5 mm | 0.01 | stated | spec "stadium plate 5 thick"; intent z = 0..5 |
| holeDiameter | 6 mm | 0.01 | stated | spec "Ø6 holes" |
| envelope | [-8, -8, 0] to [88, 8, 5] | 0.05 | derived | x: -endRadius..linkLength + endRadius; y: ±endRadius; z: 0..linkThickness |
| stadium section area | 1481.062 mm² | - | derived | 2 * endRadius * linkLength + pi * endRadius² = 1280 + 201.062 |
| bore area (each) | 28.274 mm² | - | derived | pi * (holeDiameter / 2)² |
| mid_z section (z = 2.5) | 1424.513 mm², 1 loop, 2 holes | 0.5 % | derived | 1481.062 - 2 * 28.274 |
| off_axis_y section (y = 1) | 422.804 mm², 3 loops, 0 holes | 0.5 % | derived | length (80 + 2 * sqrt(8² - 1²)) - 4 * sqrt(3² - 1²) = 95.875 - 11.314 = 84.561, times 5; 1 mm off y = 0 so the plane misses the bore axes and cylinder seams |
| web_x section (x = 40) | 80 mm², 1 loop, 0 holes | 0.5 % | derived | 16 * 5 |
| volume | 7122.566 mm³ | 0.2 % | derived | 5 * 1424.513 |
| surface area | 4088.849 mm² | 1 % | derived | top + bottom 2 * 1424.513 = 2849.027; outer wall 5 * (2 * 80 + 2 * pi * 8) = 1051.327; bores 2 * pi * 6 * 5 = 188.496 |
| centre of mass | (40, 0, 2.5) | 0.05 | derived | symmetric about x = linkLength / 2 and y = 0; z = linkThickness / 2 |
| face top (z = 5, +z) | 1424.513 mm², centre (40, 0) | 0.5 % | derived | net section area |
| face bottom (z = 0, -z) | centre (40, 0), no area | 0.05 plane | derived | area left out on purpose: the face is pinned by pinO4/pinB and the endRadius edit changes its area |
| cylinders holeO4, holeB | Ø6 hole, axes (0, 0) and (80, 0) along z | 0.05 axis | stated | no length on purpose: pinned by the interfaces, and the thickness edit changes the bore length; through-ness is proven by off_axis_y (3 islands) and the void probes at z = 1.5 and 3.5 |
| cylinders endO4, endB | R8 convex, axes (0, 0) and (80, 0), length 5, t 0..5 | 0.05 axis | stated | the two semicircular stadium ends |
| dimensions lengthX, widthY, thicknessZ | 96, 16, 5 mm | 0.05 | derived / stated | linkLength + 2 * endRadius; 2 * endRadius; bottom-to-top |
| cylinder count pinBores | 2 Ø6 holes along z | exact | stated | - |
| symmetry mirrorY | plane y = 0, default bands | - | derived | stadium and bores are centred on y = 0 (intent "y -8..8", circles on y = 0); pinned by the centreline interface |
| blockout band | 7050..7500 mm³ | - | derived | envelope-only primary solid = the stadium blank without bores, 5 * 1481.062 = 7405.310 (fills the whole bbox); band also admits the bored plate 7122.566; a 96 x 16 x 5 box (7680) is outside it, so the blockout must be the stadium outline |

Edit tests (independent stated parameters that leave both pin frames, the bores and the bottom face intact):

- `linkThickness` +1: volume delta = 1424.513 * 1 = +1424.513 mm³, bbox delta [0, 0, 1], increase. Sweep values [3, 5, 8]; feasible interval linkThickness > 0 (the model asserts it); infeasible delta -5 (thickness 0).
- `endRadius` +1 (linkWidth follows as 2 * endRadius): volume delta = 5 * (2 * 80 * 1 + pi * (9² - 8²)) = 5 * (160 + 53.407) = +1067.035 mm³, bbox delta [2, 2, 0], increase. Sweep values [5, 8, 11]; feasible interval endRadius > holeDiameter / 2 = 3 (the model asserts it; overlapping end circles past 40 still hull to a valid plate); infeasible delta -6 (endRadius 2, the bore breaks out through the end).
- No edit test on `linkLength` or `holeDiameter`: either would move or resize the pinned B bore and break the assembly joints `pinB` / `pinO4` bore fit.

## 6. Defaults retained

- `release_status: reconstruction` (template default).
- Digital tolerances 0.01 mm on parameters and 0.05 mm on the envelope, axes and planes (template defaults); the spec states no manufacturing tolerances.
- Symmetry band left at the checker defaults (the spec states no tighter band).
- Material, density and process left null (not stated); the analyzer's default density is not a mass claim.

## 7. Unrepresentable or low-confidence features

- Pins, pin retention and any spacer at O4 (the rocker runs 10 mm above the ground's top face there) are assembly hardware not described by the spec; this part carries only the bores.
- The rest angle (90 deg about O4), layer placement (z 10..15) and the kinematic predictions (rocker angle series, swing, coupler point P) belong to the assembly, not to this part contract.
- Hole fit class and edge breaks are not stated; bores are nominal Ø6 and edges sharp.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
