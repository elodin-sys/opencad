# disc-brake-disc — design brief

## 1. Intent and configuration

Half-thickness brake disc with its hub, one fused solid: the disc body of the assembly `disc-brake`, a rebuild of the COMSOL Multiphysics 6.3 Application Library model *Heat Generation in a Disc Brake* in COMSOL's coordinates converted to millimetres. Packet construction steps 1-2: disc cylinder radius 140, z = 0..13, fused with the coaxial hub cylinder radius 80, z = 13..23. The part's own frame has the rotation axis on +z through the origin and the symmetry face on z = 0; at rest it coincides with the assembly frame, and the assembly attaches it with the revolute joint `discSpin` at own-frame point [0, 0, 0], axis [0, 0, 1].

Faces the part provides: the symmetry face z = 0 (full radius-140 disc, the half-model cut plane); the rubbing face z = 13, the annulus r = 80..140 on which the pad rests (pad footprint r = 90.0..135.2 at 69..111 deg from +x); the outer rim cylinder r = 140 (z = 0..13); the hub side cylinder r = 80 (z = 13..23); the hub top z = 23. No bore, bolt holes, vents, chamfers or fillets (the reference model has none). The pad is a separate body of the assembly and is not part of this design.

`sources/comsol-brake-disc-packet.md` is authoritative; figures 1, 2, 3 and 5 are illustrative.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/comsol-brake-disc-packet.md | text | authoritative | 85535fc3210d6d0174945725ecf1a1f29351991bc272ba55fc138b0ad254638d | COMSOL 6.3 brake_disc transcription (accessed 2026-09-25), units m: model definition, Table 1 materials, geometry steps 1-4, physics, probe line |
| sources/figure-1-geometry.png | image | illustrative | 8c7faad09a9d6663c0a39fe6e18e5e721807c6750bf3b40b7ab67f95a36f5c54 | isometric render: thin disc, raised coaxial hub, pad at +y; axis ticks every 0.1 m, no dimension lines |
| sources/figure-2-velocity.png | image | illustrative | 05a0b5ceb2f81378a47ef8ac2b41edbf948dfe3c0c3392cb62b1c0ef8c56ccc1 | v(t): 25 m/s to t = 2 s, linear to 5 m/s at t = 4 s, then constant to 12 s; no geometry |
| sources/figure-3-acceleration.png | image | illustrative | bb3f0ef43eaca917061fb013edd68fece3342aebec4ef0244089d6216d71c2dd | a(t): -10 m/s^2 between t = 2 and 4 s with 0.2 s smoothed steps; no geometry |
| sources/figure-5-probe-line.png | image | illustrative | f3ffe42b7cc21121f49b80d52056b377c9aa4b90aec2d13ac0fbac1ecba5d0d5 | wireframe with the red radial probe line from the axis toward the pad, at z = 12.9 mm |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| disc radius (Cylinder 1) | 140 | mm | packet step 1, model definition | 0.01 | stated |
| disc thickness, base on z = 0 | 13 | mm | packet step 1, model definition | 0.01 | stated |
| hub radius (Cylinder 2), coaxial | 80 | mm | packet step 2 | 0.01 | stated |
| hub height, base at z = 13 | 10 | mm | packet step 2 | 0.01 | stated |
| disc and hub fused into one solid | 1 | solid | intent | exact | stated |
| symmetry face z = 0, full radius-140 disc | 61,575.2 | mm2 | packet (symmetry on the disc bottom), intent | 0.2 % | stated |
| rubbing face z = 13, annulus r = 80..140 | 41,469.0 | mm2 | intent | 0.2 % | stated |
| pad footprint on the rubbing face r = 90.0..135.2 at 69..111 deg | footprint | mm, deg | intent, packet step 3 | 1 mm probe clearance | stated (pad body) |
| outer rim cylinder r = 140, z = 0..13 | 11,435.4 | mm2 | intent | r, length 0.05 | stated |
| hub side cylinder r = 80, z = 13..23 | 5,026.5 | mm2 | intent | r, length 0.05 | stated |
| hub top z = 23 | 20,106.2 | mm2 | intent | 0.2 % | stated |
| no bore, bolt holes, vents, chamfers or fillets | none | - | intent | exact | stated |
| volume | 1,001,539.7 | mm3 | intent | 0.1 % | stated |
| bounding box | [-140, -140, 0]..[140, 140, 23] | mm | intent | 0.05 | stated |
| centroid | (0, 0, 8.809) | mm | intent | 0.05 | stated |
| revolute joint discSpin at [0, 0, 0], axis [0, 0, 1] | frame | - | orchestrator note | exact | stated |
| disc density | 7870 | kg/m3 | packet Table 1 | - | stated |
| material grade, bore, bolt circle | - | - | not in any source | - | open |

## 4. Coordinate frame, scale, and measurement method

Origin on the rotation axis at the centre of the symmetry face (disc bottom, z = 0), which is the COMSOL model origin and, at rest, the assembly origin. +x and +y are the COMSOL / assembly axes in the symmetry plane; the pad footprint is centred on +y and its angles (69..111 deg) are measured from +x toward +y. +z is the rotation axis, pointing from the symmetry face through the rubbing face (z = 13) to the hub top (z = 23). The packet's disc velocity field v_d = (v/R)(-y, x) is a counter-clockwise rotation about +z. Datums: A = symmetry face z = 0; B = rotation axis (z axis through the origin); C = rubbing face z = 13.

Scale: every dimension is quoted from the packet in metres and multiplied by 1000 (0.14 -> 140, 0.013 -> 13, 0.08 -> 80, 0.01 -> 10). No dimension was measured from an image. The figures carry only oblique axis ticks every 0.1 m and no dimension lines, so they were used for topology and as a cross-check:

- Figure 1: one thin disc, one raised coaxial hub on its top face, and the pad sitting on the rubbing annulus at +y. No holes, vents, chamfers or fillets are visible. Pixel check of the silhouettes (image 444 x 338 px, outline pixels < 120 grey on white, rows 150-163): disc x = 84..353 px (269 px), hub x = 142..296 px (154 px). The ratio 0.573 matches the stated 80 / 140 = 0.571 within the +-2 px outline uncertainty (about 1.3 %).
- Figure 5: the red probe line runs from the axis to (-47, 131.6, 12.9) mm, that is r = 139.74 mm at 109.7 deg from +x and 0.1 mm below z = 13. The line ends just inside the rim (r = 140) and just inside the rubbing face (z = 13), which is consistent with the stated disc.
- Figures 2 and 3: v(t) and a(t) only (25 -> 5 m/s at -10 m/s^2 from 2 to 4 s); no geometric content.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| discRadius | 140 mm | 0.01 | stated | packet step 1: Cylinder 1 radius 0.14 m; model definition: radius 0.14 m |
| discThickness | 13 mm | 0.01 | stated | packet step 1: Cylinder 1 height 0.013 m, base z = 0; model definition: thickness 0.013 m |
| hubRadius | 80 mm | 0.01 | stated | packet step 2: Cylinder 2 radius 0.08 m |
| hubHeight | 10 mm | 0.01 | stated | packet step 2: Cylinder 2 height 0.01 m at z = 0.013 (the hub stands on the rubbing face, z = discThickness..discThickness + hubHeight) |
| volume | 1,001,539.7 mm3 | 0.1 % | derived | pi (discRadius^2 discThickness + hubRadius^2 hubHeight) = pi (19,600 x 13 + 6,400 x 10) = 318,800 pi |
| surface area | 139,612.4 mm2 | 0.2 % | derived | pi 140^2 + 2 pi 140 x 13 + pi (140^2 - 80^2) + 2 pi 80 x 10 + pi 80^2 = (19,600 + 3,640 + 13,200 + 1,600 + 6,400) pi = 44,440 pi |
| centre of mass | (0, 0, 8.809) mm | 0.05 | derived | z = (19,600 x 13 x 6.5 + 6,400 x 10 x 18) / 318,800 = 2,808,200 / 318,800 = 8.8087; x = y = 0 by axisymmetry |
| mass | 7.882 kg | - | derived | 7870 kg/m3 x 1.0015397e-3 m3 (information only) |
| face symmetryFace (z = 0, -z) | 61,575.2 mm2 | 0.2 % | derived | pi discRadius^2 = 19,600 pi |
| face rubbingFace (z = 13, +z) | 41,469.0 mm2 | 0.2 % | derived | pi (discRadius^2 - hubRadius^2) = 13,200 pi |
| face hubTop (z = 23, +z) | 20,106.2 mm2 | 0.2 % | derived | pi hubRadius^2 = 6,400 pi |
| cylinder outerRim | r 140, length 13, t 0..13 | 0.05 | derived | discRadius, discThickness |
| cylinder hubSide | r 80, length 10, t 13..23 | 0.05 | derived | hubRadius, hubHeight, base at discThickness |
| section midDisc (z = 6.5) | 61,575.2 mm2, 1 loop, 0 holes | 0.2 % | derived | full disc circle; no bore, bolt holes or vents |
| section midHub (z = 18) | 20,106.2 mm2, 1 loop, 0 holes | 0.2 % | derived | full hub circle; no bore |
| section axialX (x = 0) | 5,240 mm2, 1 loop, 0 holes | 0.2 % | derived | 280 x 13 + 160 x 10 (placed at x = 0, away from the y = 0 cylinder seam) |
| dimensions | 13 (z = 0 to 13), 10 (z = 13 to 23), 23, 280, 280 mm | 0.05 | derived | discThickness, hubHeight, discThickness + hubHeight, 2 discRadius (bbox x and y) |
| planes symmetryPlane, padSeatPlane | z = 0 (-z), z = 13 (+z) at (0, 112.5) | envelope | derived | position-only interface pins (no area) so the radius and hub-height edits keep them; (0, 112.5) is the pad footprint centre, (90 + 135) / 2 on +y |
| probes padFootprintSolid / padSpaceVoid | (0, 91), (0, 134), (+-40, 105) at z = 12 / z = 16 | >= 1 mm clearance | derived | packet step 3 Bezier end points (0, 90), (0, 135), (+-40, 105) mm pulled 1 mm inside the outline; z = 12 is 1 mm under the rubbing face, z = 16 is mid-pad (pad z = 13..19.5) |
| probes axisSolid | (0, 0, 1 / 12 / 14 / 22) | >= 1 mm | derived | material on the axis through disc and hub: no bore |
| blockout band | 970,000..1,035,000 mm3 | band | derived | the primary solids that reach the envelope extremes are the whole part (disc reaches r = 140 and z = 0, hub reaches z = 23): 1,001,540 x (0.97..1.03), rounded |

Edit tests (all on stated parameters, the others held fixed):

- `discRadius` +5: dV = pi (145^2 - 140^2) x 13 = 18,525 pi = 58,198.0 mm3, bbox +10 in x and y. Feasible interval (hubRadius, inf) at part level, >= 135.2 so the pad stays supported; infeasible delta -70 (discRadius 70 < hubRadius) must fail an assert `discRadius > hubRadius`.
- `hubRadius` +5: dV = pi (85^2 - 80^2) x 10 = 8,250 pi = 25,918.1 mm3, bbox unchanged. Feasible interval (0, discRadius) at part level, and (0, 90) so the hub never reaches under the pad (inner edge r = 90). Sweep {60, 80, 85} lies inside both; infeasible delta +70 (hubRadius 150 > discRadius) must fail the same assert.
- `hubHeight` +2: dV = pi 80^2 x 2 = 12,800 pi = 40,212.4 mm3, bbox +2 in z. Feasible interval (0, inf); sweep {6, 10, 14}; infeasible delta -10 (hubHeight 0, no hub) must fail an assert `hubHeight > 0`.
- `discThickness` carries no edit test: it moves the rubbing face, which is the pinned pad seat (interface `padSeat`).

Interfaces and their pins: `discSpin` -> mirrorX, mirrorY, symmetryPlane; `symmetryBoundary` -> symmetryPlane; `padSeat` -> padSeatPlane. None of these moves or resizes under the three edit tests or the two sweeps.

## 6. Defaults retained

- Envelope and bbox tolerance 0.05 mm; cylinder radius and length tolerance 0.05 mm; dimension tolerance 0.05 mm; centre of mass 0.05 mm per axis. The geometry is two exact coaxial cylinders, so these reflect kernel and STEP round-trip precision, not source uncertainty.
- Parameter digital tolerance 0.01 mm (all four are exact quoted values).
- Volume tolerance 0.1 %, surface, face and section area tolerance 0.2 % (exact analytic values).
- Edit-test deltas (+5, +5, +2 mm) and tolerance_rel 0.02 follow the exemplar; the sweeps sit inside the feasible intervals in section 5.
- Blockout band plus or minus 3 % of the analytic volume.
- Symmetry bands (mirrorX, mirrorY) are left at the harness defaults; no source states a tighter band.
- Material density 7870 kg/m3 from packet Table 1 (stated); the grade is open.

## 7. Unrepresentable or low-confidence features

- The pad (packet steps 3-4, the weighted Bezier outline extruded 6.5 mm) is a separate body of the assembly; this contract only keeps its footprint clear of the disc (padSpaceVoid) and supported by it (padFootprintSolid, padSeatPlane).
- Physics (translational motion, heat flux, thermal contact, radiation, mesh, study) and the result probe line belong to the assembly and simulation, not to this geometry.
- The other half of the physical disc (mirror at z = 0) is not modelled; the half-model is the deliverable.
- A real disc's bore, bolt circle, hat, vents, chamfers and fillets are absent from the reference and deliberately not modelled (sections with 0 holes, axis probes, exact face areas and cylinder lengths enforce this).
- The angular orientation about z has no geometric feature; +x and +y are fixed by convention to the COMSOL / assembly axes.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
