# bracket — design brief

## 1. Intent and configuration

An 80 x 50 x 6 mm aluminium mounting plate with four 4.5 mm clearance holes (10 mm inset
from each edge) and R5 fillets on the four vertical corner edges. It is the smoke-test
bracket from `smoke/README.md`, chosen because every acceptance number has a closed-form
answer while the geometry exercises fillets, holes, sections, probe points and edit tests.
Training-only; no manufacturing release.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| smoke/README.md (Parts section) | text | authoritative | (workspace file, not bundled) | dimensions, analytic volume 23489.5 mm3 |
| smoke/parts/bracket/main.kcl | text | illustrative | (workspace file, not bundled) | an earlier hand-written KCL; not an input to Codex |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| blank | 80 x 50 x 6 | mm | README | 0.01 | stated |
| holes | 4 x 4.5 through, 10 from each edge | mm | README | 0.01 | stated |
| corner fillets | R5 on the four vertical edges | mm | README | 0.01 | stated |
| hole pattern must not move | 70 x 30 centred | mm | README | — | stated (interface) |

## 4. Coordinate frame, scale, and measurement method

Origin at the minimum corner of the unfilleted blank; x along 80, y along 50, z through
the thickness. All values are stated; no image or mesh measurement.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| plateWidth | 80 mm | 0.01 | stated | README |
| plateHeight | 50 mm | 0.01 | stated | README |
| plateThickness | 6 mm | 0.01 | stated | README |
| holeDiameter | 4.5 mm | 0.01 | stated | README (M4 clearance) |
| holeInset | 10 mm | 0.01 | stated | README |
| cornerRadius | 5 mm | 0.01 | stated | README |
| volume | 23489.535 mm3 | 0.1 % | derived | 24000 - 4(25 - 25pi/4)6 - 4 pi 2.25^2 6 |
| surface area | 9677.63 mm2 | 0.1 % | derived | 2 x 3914.92 + (220 + 10 pi) 6 + 4 pi 4.5 x 6 |
| section z = 3 | 3914.923 mm2, 1 loop, 4 holes | 0.2 % | derived | plate outline minus holes |
| section x = 10 | 246 mm2, 3 loops | 0.2 % | derived | 50 x 6 minus two 4.5 x 6 slots |
| thickness +1 mm | +3914.923 mm3 | 0.5 % | derived | volume / 6 |
| holeDiameter +1 mm | -188.496 mm3 | 1 % | derived | -4 pi 6 (2.75^2 - 2.25^2) |

## 6. Defaults retained

Density 2700 kg/m3 (aluminium 6061) for mass reporting only.

## 7. Unrepresentable or low-confidence features

None. Known engine behaviour recorded in `smoke/README.md`: `hole::` `cutAt` is read in
the target face's local frame (on the END face of an XY extrusion `[a, b]` lands at global
`(b, a)`); the probe points in the contract will expose a swapped pattern only if it is
asymmetric, so the mid-plane section and the x = 10 section are the checks that matter.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [0.0, 0.0, 0.0] → [80.0, 50.0, 6.0] | 23999.999029911123 | pass | 2026-09-15T06:58:00Z: within envelope and band |
