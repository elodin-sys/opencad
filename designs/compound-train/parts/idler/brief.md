# compound-train-idler — design brief

## 1. Intent and configuration

Compound idler of the `compound-train` assembly: one solid carrying a 40-tooth spur gear over z = 0..8 and a 15-tooth spur gear over z = 8..16, both module 2, 20 deg pressure angle, zero profile shift, addendum 1.0 m, dedendum 1.25 m. Involute flanks from the base circle to the tip (12-16 points per flank), a radial flank from the base circle to the root, every tooth thinned by 0.05 mm at its pitch circle (circular tooth thickness 3.0916 mm). Both patterns have a tooth centred on +x. D8 bore through. The 40-tooth gear meshes with the 20-tooth pinion and the 15-tooth gear with the 45-tooth output gear, each at 60 mm centre distance; the bottom face stands on the base plate over its D8 hole at (60, 0). Authoritative source: `sources/compound-train-spec.md`.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/compound-train-spec.md | text | authoritative | e2734c43ae1d2aa36320d0b7680e21616422e902b471b3eb98295e3292296af5 | parameter table, part-frame paragraph, tooth phase and backlash rows |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| one solid | 1 | | spec, intro | exact | stated |
| module, both gears | 2 | mm | spec table | 0.001 | stated |
| pressure angle | 20 | deg | spec table | 0.01 | stated |
| profile shift | 0 | | spec table | 0.001 | stated |
| addendum / dedendum | 1.0 m / 1.25 m | | spec table | 0.001 | stated |
| large gear | 40 teeth, z 0..8 | | spec table | exact | stated |
| small gear | 15 teeth, z 8..16 | | spec table | exact | stated |
| tooth thinning at pitch circle | 0.05 | mm | spec backlash row | 0.001 | stated |
| tooth centred on +x, both patterns | 0 | deg | spec part frames | probes | stated |
| bore | D8 through, z 0..16 | mm | spec table | 0.01 | stated |
| flank points | 12-16 per flank | | spec, flank note | range | stated (14 defaulted) |
| mesh centre distances | 60 and 60 | mm | spec table | assembly | stated (assembly-level) |

## 4. Coordinate frame, scale, and measurement method

Origin on the gear axis at the bottom face (z = 0). +z is the gear axis, up through the shoulder (z = 8) to the top face (z = 16). +x is radial through the centre line of one tooth of each pattern; +y = z cross x. Datums: A bottom face z = 0 (seats on the plate), B the bore axis (joint idlerSpin, own-frame point [0, 0, 0], axis +z), C the plane y = 0 (tooth phase). No images or meshes: every value is stated or derived from the text, no scaling was needed.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| gearModule | 2 mm | 0.001 | stated | spec table |
| pressureAngle | 20 deg | 0.01 | stated | spec table |
| profileShift | 0 | 0.001 | stated | spec table |
| addendumCoeff / dedendumCoeff | 1.0 / 1.25 | 0.001 | stated | spec table |
| backlashThinning | 0.05 mm | 0.001 | stated | spec backlash row |
| gear40Teeth / gear15Teeth | 40 / 15 | 0.1 | stated | spec idler row |
| gear40FaceWidth / gear15FaceWidth | 8 / 8 mm | 0.01 | stated | spec idler row |
| boreDiameter | 8 mm | 0.01 | stated | spec idler row |
| flankPoints | 14 | 2 | defaulted | middle of the recommended 12-16 |
| pitchRadius40 / 15 | 40 / 15 mm | 0.001 | derived | gearModule * teeth / 2 |
| tipRadius40 / 15 | 42 / 17 mm | 0.001 | derived | pitch radius + addendumCoeff * gearModule |
| rootRadius40 / 15 | 37.5 / 12.5 mm | 0.001 | derived | pitch radius - dedendumCoeff * gearModule |
| baseRadius40 / 15 | 37.5877 / 14.0954 mm | 0.001 | derived | pitch radius * cos(pressureAngle) |
| toothThickness | 3.0916 mm | 0.001 | derived | pi * gearModule / 2 - backlashThinning |
| totalHeight | 16 mm | 0.01 | derived | gear40FaceWidth + gear15FaceWidth |
| S40 (profile area, no bore) | 4973.84 mm2 | | derived | root disc + 40 teeth; tooth half-angle psi(r) = s/(2 rp) + inv(20 deg) - inv(acos(rb/r)), psi_b = 0.053549 rad, psi_t = 0.017486 rad; arcs at tip and root |
| S15 | 679.05 mm2 | | derived | same, psi_b = 0.117957 rad, psi_t = 0.036945 rad (tip land 1.26 mm) |
| perimeters P40 / P15 | 514.44 / 197.13 mm | | derived | 2 involute arcs + 2 radial flanks + tip arc + root arc per tooth |
| gear40Mid section (z = 4) | 4923.58 mm2, tol 0.1 % | | derived | S40 - 16 pi; 12-point polylines lose 0.8, chord tips and roots 1.6, no thinning adds 8.94 |
| gear15Mid section (z = 12) | 628.79 mm2, tol 0.4 % | | derived | S15 - 16 pi; chords lose 1.5, no thinning adds 3.32 |
| phaseY0 section (y = 0) | 780 mm2, 2 loops | | derived | (42-4)*8*2 + (17-4)*8 + (12.5-4)*8 |
| faces floor / shoulder40 / top15 | 4923.58 / 4294.79 / 628.79 mm2 | | derived | S40 - 16 pi, S40 - S15, S15 - 16 pi |
| volume | 44418.9 mm3, tol 45 | | derived | 8 (S40 - 16 pi) + 8 (S15 - 16 pi); missing thinning adds 98, polyline/chord variants lose at most 25 |
| surface area | 15941.8 mm2, tol 1 % | | derived | 2 S40 - 32 pi + 8 (P40 + P15) + 128 pi |
| centre of mass | [0, 0, 4.906], tol 0.05 | | derived | (39388.6 * 4 + 5030.3 * 12) / 44418.9 |
| envelope | [-42, -42, 0] .. [42, 42, 16] | 0.05 | derived | 40-tooth teeth centred at 0, 90, 180, 270 deg reach the tip radius 42 |
| edit gear40FaceWidth +1 | +4923.58 mm3, bbox [0, 0, 1] | 2 % | derived | the small gear rides up; volume grows by the z = 4 section |
| edit gear15FaceWidth +1 | +628.79 mm3, bbox [0, 0, 1] | 2 % | derived | volume grows by the z = 12 section; sweep 6, 8, 10 (feasible interval (0, 20]); delta -8 (zero width) must fail an assert |
| void probes in tooth spaces | (40.874, 3.217, 4), (15.650, 3.327, 12), (-16, 0, 12) | | derived | space centres at 4.5 deg r 41, 12 deg r 16, 180 deg r 16; at least 1.8 mm from every flank |
| blockout band | 49000 .. 53000 mm3 | | derived | tip discs pi*42^2*8 + pi*17^2*8 = 51597.5, with bore 50793.3, plus or minus about 3 % |

## 6. Defaults retained

- `flankPoints` = 14: the spec recommends 12-16; any value in that band gives section areas within the tolerances (16-point polylines lose 0.4 mm2 on the large gear).
- Tip and root lands as arcs about the axis: the spec does not say; chords are inside the section tolerances.
- No material, density or process: not stated, so no mass claim.

## 7. Unrepresentable or low-confidence features

- The meshes with the pinion and output gear (60 mm centre distance, flank gap at most 0.15 mm, zero interference) belong to the assembly contract; this part pins the tooth form with the `gear40Mid` / `gear15Mid` sections, the `gears` entries and the phase probes.
- 15 teeth is below the 17-tooth undercut limit; the spec's radial flank below the base circle replaces a generated undercut. The involute contact check (45-tooth tip reaches 5.125 mm along the line of action against the 5.130 mm limit) passes narrowly, so the assembly sweep must confirm clearance.
- The y = 0 mirror symmetry is implied by symmetric teeth but not stated, so it is not declared; tooth phase is checked by probes and the `phaseY0` section instead.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
