# four-bar-coupler — design brief

## 1. Intent and configuration

The coupler link of the planar crank-rocker four-bar linkage (assembly `four-bar`), drafted and modelled in its own frame. Hole A (pin A, the joint to the crank) is at the origin, hole B (pin B, the joint to the rocker and the loop's closing joint) is at (100, 0, 0), the bottom face is z = 0, the top face z = 5, and both hole axes run along +z. The body is the same stadium plate as the crank: the tangent hull of two R8 circles centred on (0, 0) and (100, 0), 16 wide (y -8..8), extruded z = 0..5, overall x -8..108, with two Ø6 through holes at (0, 0) and (100, 0). One solid, no other features. The coupler point P at (50, 30) in this frame's xy lies outside the plate and adds no material; it is recorded as a datum only.

Interfaces: joint `pinA` (revolute, axis +z through (0, 0, 0)) where the bottom face around hole A seats on the crank's top face, and joint `pinB` (revolute, axis +z through (100, 0, 5)) where the top face around hole B carries the rocker's second hole. The assembly places this part by these two frames, so the contract frame is the part's own frame from the intent, not the assembly frame (in the assembly at rest the coupler sits in the z 5..10 layer, rotated 53.130102 deg about +z at A = (40, 0)).

Authoritative source: `sources/four-bar-spec.md` (text). The work-order intent is consistent with it in every number.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/four-bar-spec.md | text | authoritative | aececd85a2ba8a2e020775f05a44f1bd1c3a505c8c8c5ed634606d975490bf17 | Linkage spec: coupler row (A to B 100, stadium plate as the crank: 5 thick, 16 wide, R8 ends centred on the holes, Ø6 holes), part-frame rule (first hole at the origin, second on +x, bottom face z = 0), coupler point P (50, 30). No images, drawings or reference models. |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| hole A centre (pin A) at the frame origin | (0, 0) | mm | intent; spec part-frame rule | 0.05 axis offset | stated |
| hole B centre on +x at the link length | (100, 0) | mm | intent; spec table (A to B 100) | 0.05 axis offset | stated |
| bottom and top faces | z = 0 and z = 5 | mm | intent; spec (5 thick) | 0.05 | stated |
| hole axes | +z | - | intent; spec (every pin axis parallel to +z) | - | stated |
| stadium section: tangent hull of two R8 circles on (0, 0) and (100, 0) | R8 | mm | intent; spec (semicircular ends of radius 8 centred on the holes) | 0.05 | stated |
| width | 16 (y -8..8) | mm | intent; spec | 0.05 | stated |
| overall length | 116 (x -8..108) | mm | intent | 0.05 | stated |
| two through holes along z | Ø6 at (0, 0) and (100, 0) | mm | intent; spec | 0.05 | stated |
| one solid, no other features | 1 | - | intent; spec (four separate solids, no fused bodies) | - | stated |
| interface pin A: bottom face around hole A seats on the crank's top face | revolute, +z at (0, 0, 0) | - | intent; orchestrator joint list | 0.05 | stated |
| interface pin B: top face around hole B seats the rocker (closing joint) | revolute, +z at (100, 0, 5) | - | intent; orchestrator joint list | 0.05 | stated |
| coupler point P, reference only | (50, 30) in xy | mm | intent; spec | - | stated (datum, no material) |
| material, density, process | - | - | not stated | - | open |
| pin fit of the Ø6 holes | - | - | not stated | - | open |
| edge breaks | none | - | not stated | - | open |

## 4. Coordinate frame, scale, and measurement method

Origin: centre of hole A on the bottom face (x = y = z = 0). +x runs along the link from hole A toward hole B (B at (100, 0, 0)); +y runs across the 16 mm width toward the coupler point P (to the left of A->B); +z runs up the hole axes from the bottom face (seats on the crank) to the top face (carries the rocker). Datums: `bottomFace` z = 0, `topFace` z = 5, `axisA` (x = 0, y = 0, +z), `axisB` (x = 100, y = 0, +z), `pointP` (50, 30) in xy.

This is the frame the spec prescribes for every link ("first hole at its own origin, second hole on +x at the link length, bottom face at z = 0") and the frame the assembly's joint list uses. All values are read from text in millimetres; there are no images to scale and no reference mesh, so nothing is measured.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| linkLength | 100 mm | 0.01 | stated | spec table (Coupler: A to B 100); intent (B at (100, 0, 0)) |
| endRadius | 8 mm | 0.01 | stated | intent (tangent hull of two R8 circles, 16 wide y -8..8); spec (semicircular ends of radius 8, 16 wide) |
| plateThickness | 5 mm | 0.01 | stated | intent (bottom z = 0, top z = 5); spec (stadium plate 5 thick) |
| holeDiameter | 6 mm | 0.01 | stated | intent (two Ø6 through holes); spec (Ø6 holes) |
| stadium area | 1801.062 mm² | - | derived | 2 * endRadius * linkLength + pi * endRadius² = 1600 + 201.062 |
| section midZ (z = 2.5) | 1744.513 mm², 1 loop, 2 holes | rel 0.002 | derived | 1801.062 - 2 * pi * 3² (56.549) |
| volume | 8722.566 mm³ | rel 0.002 | derived | plateThickness * 1744.513 |
| surface area | 4928.849 mm² | rel 0.005 | derived | 2 * 1744.513 + 5 * (200 + 16 * pi) (1251.327) + 2 * pi * 6 * 5 (188.496) |
| centre of mass | (50, 0, 2.5) | 0.05 | derived | symmetric about x = linkLength / 2 and y = 0; z = plateThickness / 2 |
| envelope | (-8, -8, 0) to (108, 8, 5) | 0.05 | derived | x -endRadius..linkLength + endRadius, y ±endRadius, z 0..plateThickness |
| lengthX / widthY / thicknessZ | 116 / 16 / 5 mm | 0.05 | derived | linkLength + 2 * endRadius; 2 * endRadius; top minus bottom face |
| cylinders holeA, holeB | Ø6 hole, axis +z at (0, 0) and (100, 0), length 5 | default | stated | intent and spec |
| cylinders endA, endB | R8 convex half cylinder concentric with each hole, length 5 | default | stated | tangent hull of R8 circles centred on the holes |
| cylinder count pinHoles | 2 Ø6 holes along z | - | stated | intent (two through holes, no other features) |
| void probes outsideRoundedEnds | (-6.5, ±6.5, 2.5), (106.5, ±6.5, 2.5) | - | derived | radius 9.19 from each hole centre, 1.19 mm outside the R8 arc, 1.5 mm inside the bbox faces |
| solid probes | (50, 0, 2.5), (-5.5, 0, 2.5), (105.5, 0, 2.5) | - | derived | mid-plate and the 5 mm webs between each hole (r 3) and its end (r 8), 2.5 mm from both |
| blockout band | 8700..9300 mm³ | - | derived | covers the holeless stadium blank 5 * 1801.062 = 9005.3 (fills the whole envelope), the finished part 8722.6 and the envelope box 116 * 16 * 5 = 9280 |

Edit test (endRadius, delta +1): the outline grows, the holes and both seat faces stay. Expected volume delta = plateThickness * (2 * linkLength * 1 + pi * (9² - 8²)) = 5 * (200 + 17 * pi) = 1267.04 mm³ (increase), bbox delta (2, 2, 0), tolerance_rel 0.02. The face centroids stay at (50, 0) by symmetry, so the pinned `bottom` and `top` faces carry no area (their area changes with this edit; the midZ section checks the area instead).

Sweep: endRadius values 5, 8, 12. Feasible interval: endRadius > holeDiameter / 2 = 3 mm (the hole must stay inside its rounded end); there is no upper limit that the part itself needs, and the sweep stays at or below 12. Infeasible delta -6 (endRadius 2 < hole radius 3: the Ø6 hole would break out of the end): the model must refuse it with `assert endRadius > holeDiameter / 2`, never build a broken-out outline.

Only endRadius carries an edit test: linkLength moves hole B (pinB), plateThickness moves the top face and the pinB joint frame at z = 5, and holeDiameter resizes both pin holes, so each of those edits would move a pinned interface.

## 6. Defaults retained

- Digital parameter tolerance 0.01 mm and envelope/bbox tolerance 0.05 mm: every value is an exact text number, so tight digital thresholds apply.
- Volume tolerance_rel 0.002, surface area tolerance_rel 0.005, centre of mass 0.05 mm per axis: the part is prismatic with exact analytic values; the bands only absorb export and tessellation noise.
- Cylinder radius, axis and length tolerances default to the envelope tolerance (0.05 mm).
- Material, density and process stay null (not stated; no mass claim).
- release_status `reconstruction` kept from the template.

## 7. Unrepresentable or low-confidence features

- Coupler point P (50, 30): a reference point outside the plate with no material; it is the `pointP` datum only. The assembly carries it for the P trajectory predictions; a void probe there would lie outside the envelope and add nothing the bbox does not already enforce.
- The assembly placement (coupler in the z 5..10 layer, 53.130102 deg at rest) belongs to the assembly contract, not to this part.
- Mirror symmetry about y = 0 and x = 50 is implied by the geometry but not stated as a requirement, so no `acceptance.symmetry` is declared; the centre of mass (50, 0, 2.5), the midZ section and the four corner probes pin the centring.
- Pin fit and edge breaks are not stated (open questions); Ø6 is modelled as the nominal bore with sharp edges.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
