# planetary-set-base — design brief

## 1. Intent and configuration

Base plate of the planetary gear set with a fixed ring (assembly `planetary-set`), drafted in its own frame, which is
the assembly frame. It is a 150 x 150 x 5 mm plate from corner (-75, -75, -5) to (75, 75, 0), edges along x and y,
with a D10 through hole on the z axis (x = y = 0). Its top face z = 0 is the seat the ring, the sun and the three
planets stand on; the ring is fixed rigidly on it, concentric with the hole. No other features.

The assembly places the other bodies on this frame: joint `ringFixed` (rigid) at point [0, 0, 0], axis +z; joint
`sunSpin` (revolute) at [0, 0, 0], axis +z; joint `carrierSpin` (revolute) at [0, 0, 10], axis +z. The plate is one
solid; every other body of the set is a separate design.

Authoritative source: `sources/planetary-set-spec.md` (text only; no images, drawings or reference models).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/planetary-set-spec.md | text | authoritative | 2a8bca0f4ffa01692bc1a5879aeb8b02a1d728b2cbe39448f181197d86ca14ca | parameter table row "Base plate: 150 x 150 x 5 mm, corner (-75, -75, -5) to (75, 75, 0), centre hole Ø10"; Frame paragraph (z up, plate top at z = 0, ring rigidly fixed to the plate) |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| plate size along x | 150 (x = -75..75) | mm | intent; spec table | 0.05 (envelope, `spanX`, `sideXPlus`/`sideXMinus`) | stated |
| plate size along y | 150 (y = -75..75) | mm | intent; spec table | 0.05 (envelope, `spanY`, `sideYPlus`/`sideYMinus`) | stated |
| plate thickness | 5 (z = -5..0) | mm | intent; spec table | 0.05 (`thicknessZ` between `bottom` and `top`) | stated |
| edges along x and y | four side faces on x = ±75, y = ±75 | - | intent | 0.05 plane position | stated |
| D10 through hole on the z axis | Ø10 at x = y = 0, z = -5..0 | mm | intent; spec table ("centre hole Ø10") | cylinder `centreHole`, `midX` loops 2, `midZ` holes 1, `holeVoid`, `d10Holes` = 1 | stated |
| seat = top face z = 0 | plane z = 0, normal +z | mm | intent; spec Frame ("plate top at z = 0") | face `top`, interface `seat` | stated |
| ring fixed concentric with the hole | hole axis = frame z axis | - | intent; orchestrator joint list | cylinder `centreHole` axis, symmetry `mirrorX`/`mirrorY`, interface `axis` | stated |
| no other features | volume, area, one solid, one hole | - | intent ("No other features") | volume ±50 mm³, area ±0.1 %, `solid_count` 1, section loop counts, `d10Holes` = 1 | stated |
| material, density, process | not given | - | - | - | open |

## 4. Coordinate frame, scale, and measurement method

Origin at the centre of the top face (the seat) on the hole axis: x = y = 0 at the hole centre, z = 0 at the top face.
This is the assembly origin (the sun, ring and carrier axis) stated by the spec's Frame paragraph and the intent.
+x and +y run along the plate edges (the plate spans -75..75 on both); +x is also the rest direction on which the sun,
the planets and the ring each centre a tooth. +z is up along the hole axis; the plate occupies z = -5..0 and the gears
stand above it. Datums: A = top face z = 0 (seat); B = hole axis x = y = 0 along +z; C = the mirror planes x = 0 and
y = 0.

Scale: every value is a millimetre number quoted from the text source; no image or mesh was measured, so no pixel
scale or rectification was needed.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| plateSizeX | 150 mm | 0.01 | stated | intent and spec table, Base plate row; centred, x = -plateSizeX/2 .. plateSizeX/2 |
| plateSizeY | 150 mm | 0.01 | stated | intent and spec table, Base plate row; centred, y = -plateSizeY/2 .. plateSizeY/2 |
| plateThickness | 5 mm | 0.01 | stated | intent (corner z = -5 to top z = 0) and spec table; the plate hangs below the seat |
| holeDiameter | 10 mm | 0.01 | stated | intent "D10 through hole on the z axis"; spec table "centre hole Ø10" |
| volume | 112107.30 mm³ | ±50 | derived | 150·150·5 − π/4·10²·5 = 112500 − 125π |
| surface area | 48000 mm² | ±0.1 % | derived | 2·(22500 − 25π) + 4·750 + 2π·5·5 = 48000.00 (with r = h = 5 the hole wall exactly replaces the two removed discs, so area alone does not detect the hole; volume, sections and the cylinder do) |
| centre of mass | (0, 0, −2.5) | ±0.05 | derived | mirror symmetry about x = 0 and y = 0; uniform slab z = −5..0 |
| section `midZ` (z = −2.5) | 22421.46 mm², 1 loop, 1 hole | ±0.2 % | derived | 22500 − 25π |
| section `midX` (x = 0) | 700 mm², 2 loops, 0 holes | ±0.2 % | derived | two 70 × 5 rectangles, y = −75..−5 and 5..75 |
| face `top` (z = 0, +) | position only, centroid (0, 0) | 0.05 | stated | seat; no area so size and hole edits leave the pinned check intact |
| face `bottom` (z = −5, −) | 22421.46 mm², centroid (0, 0) | ±0.2 % | derived | 22500 − 25π |
| faces `sideXPlus`/`sideXMinus`/`sideYPlus`/`sideYMinus` | 750 mm² each | ±0.2 % | derived | 150 × 5 |
| cylinder `centreHole` | Ø10, axis (0, 0, z), length 5, t 0..5 from (0, 0, −5) | defaults | stated | through hole z = −5..0 |
| dimensions `thicknessZ`, `spanX`, `spanY` | 5, 150, 150 | 0.05 | stated | between `bottom`/`top`; bbox extents |
| blockout band | 108000 .. 113000 mm³ | - | derived | envelope box 150·150·5 = 112500 (and the finished 112107) inside a ~4 % band |

Edit tests (other parameters held fixed):

| parameter | delta | volume delta | bbox delta | formula |
|---|---|---|---|---|
| plateThickness | +1 | +22421.46 (increase) | [0, 0, 1] | (plateSizeX·plateSizeY − π/4·holeDiameter²)·1; the bottom moves to z = −6, the seat stays at z = 0 |
| holeDiameter | +2 | −172.79 (decrease) | [0, 0, 0] | −π/4·(12² − 10²)·5 = −55π |
| plateSizeX | +10 | +7500 (increase) | [10, 0, 0] | 10·plateSizeY·plateThickness; grows 5 mm on each side, the hole stays on the axis |

Feasible intervals and sweeps: plateThickness ∈ (0, ∞) (sweep [3, 5, 8], kept ≥ 3 so the z = −2.5 section still cuts
the plate); holeDiameter ∈ (0, min(plateSizeX, plateSizeY)) = (0, 150) (sweep [8, 10, 12], kept near the Ø10 the sun
bore and the carrier centre hole share). Infeasible deltas the
part must refuse with an `assert`: plateThickness −5 (zero thickness); holeDiameter −10 (zero diameter) and +150
(Ø160 is wider than the plate, which would split it into four corner pieces); plateSizeX −145 (a 5 mm plate is
narrower than the Ø10 hole).

Pinned interfaces: `seat` checks face `top` (position and centroid only); `axis` checks `mirrorX` and `mirrorY`. None
of the three edit tests moves the seat plane or breaks either mirror plane, so these checks survive every edit.

## 6. Defaults retained

- Envelope tolerance 0.05 mm and parameter tolerances 0.01 mm: digital comparison thresholds for a text-stated,
  exactly dimensioned part.
- Symmetry bands 0.1 mm max / 0.05 mm p95: generous against tessellation of an exact B-rep with one Ø10 hole.
- Material, density and process left null: the source states none and no mass claim is made.
- Sharp edges everywhere: the intent says "No other features", so no chamfers or fillets are added.

## 7. Unrepresentable or low-confidence features

- The ring's attachment (bolts, dowels or bonding) is not described; the contract encodes only the flat seat and the
  concentric axis, and no fastener holes.
- The hole's fit class (for example a clearance fit for a shaft through the plate) is not stated; the nominal Ø10 is
  used with default cylinder tolerances.
- Nothing else is low-confidence: every dimension is stated in both the intent and the spec table.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
