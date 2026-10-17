# coupon — design brief

## 1. Intent and configuration

A 60 x 40 x 4 mm rectangular training coupon, the elementary part from section 10 of the
agentic CAD primer. It exists to prove the toolchain: contract, Codex-authored KCL,
independent verification, exports, gates, and report. Training-only; not an engineering
release.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| scratch/zoo_kittycad_agentic_cad_primer.md §10 | text | authoritative | (workspace scratch, not bundled) | dimensions, expected volume 9600 mm3 and centre [30, 20, 2] |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| length | 60 | mm | primer §10 | 0.01 | stated |
| width | 40 | mm | primer §10 | 0.01 | stated |
| thickness | 4 | mm | primer §10 | 0.01 | stated |
| single solid, no features | — | — | primer §10 | — | stated |

## 4. Coordinate frame, scale, and measurement method

Origin at the minimum corner; x along the length, y along the width, z through the
thickness. No image or mesh measurement was needed; all values are stated.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| width | 60 mm | 0.01 | stated | primer §10 |
| height | 40 mm | 0.01 | stated | primer §10 |
| thickness | 4 mm | 0.01 | stated | primer §10 |
| volume | 9600 mm3 | 0.1 % | derived | width * height * thickness |
| surface area | 5600 mm2 | 0.1 % | derived | 2(wh + wt + ht) |
| centre of mass | [30, 20, 2] | 0.02 | derived | half of each dimension |

## 6. Defaults retained

Density 2700 kg/m3 (aluminium) is assumed only so that a mass can be reported; the coupon
has no material requirement.

## 7. Unrepresentable or low-confidence features

None.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
| 1 | [0.0, 0.0, 0.0] → [60.0, 40.0, 4.0] | 9600.00033956021 | pass | 2026-09-15T06:44:42Z: within envelope and band |
