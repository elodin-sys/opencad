# disc-brake-pad — design brief

## 1. Intent and configuration

Brake pad of the COMSOL 6.3 Application Library model *Heat Generation in a Disc Brake*, rebuilt in millimetres as one solid in its own frame, which is the assembly frame of `disc-brake` (the pad is the fixed datum; the disc spins about the z axis through the origin). Packet construction steps 3-4: a closed outline of four cubic Bezier curves (B1 and B4 rational, weight 2.5 on (+-50, 130)) in the work plane z = 13, extruded +z by 6.5 to z = 19.5. Faces: contact face z = 13 (rests on the disc rubbing face), top face z = 19.5, outer side wall (B1, B4) and inner side wall (B2, B3), both parallel to z. No backing plate, chamfers or fillets. `sources/comsol-brake-disc-packet.md` is authoritative; figures 1, 2, 3 and 5 are illustrative.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/comsol-brake-disc-packet.md | text | authoritative | 85535fc3210d6d0174945725ecf1a1f29351991bc272ba55fc138b0ad254638d | geometry steps 3-4 (control points in m), Table 1 pad material |
| sources/figure-1-geometry.png | image | illustrative | 8c7faad09a9d6663c0a39fe6e18e5e721807c6750bf3b40b7ab67f95a36f5c54 | isometric render, disc + hub + pad on +y; no dimension lines |
| sources/figure-2-velocity.png | image | illustrative | 05a0b5ceb2f81378a47ef8ac2b41edbf948dfe3c0c3392cb62b1c0ef8c56ccc1 | v(t): 25 m/s to 5 m/s over t = 2..4 s; no geometry |
| sources/figure-3-acceleration.png | image | illustrative | bb3f0ef43eaca917061fb013edd68fece3342aebec4ef0244089d6216d71c2dd | a(t): -10 m/s2 over t = 2..4 s; no geometry |
| sources/figure-5-probe-line.png | image | illustrative | f3ffe42b7cc21121f49b80d52056b377c9aa4b90aec2d13ac0fbac1ecba5d0d5 | wireframe, red radial probe line on the disc surface toward the pad's -x side |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| outline B1 | (0, 135), (20, 135), (50, 130) w 2.5, (40, 105) | mm | packet step 3 | 0.01 | stated |
| outline B2 | (40, 105), (30, 80), (35, 90), (0, 90) | mm | packet step 3 | 0.01 | stated |
| outline B3, B4 | x-mirrors of B2, B1 (w 2.5 on (-50, 130)) | mm | packet step 3 | 0.01 | stated |
| work plane (contact face) | z = 13 | mm | packet step 3 | 0.01 | stated |
| extrusion | 6.5 along +z (top z = 19.5) | mm | packet step 4 | 0.01 | stated |
| mirror plane | x = 0 | mm | packet step 3 (mirrored control points) | 0.1 max deviation | stated |
| one solid, no fillets/chamfers/backing plate | 1 | - | intent | - | stated |
| density | 2000 | kg/m3 | packet Table 1 | - | stated |
| volume | 23038.51 | mm3 | derived from outline | 0.2 % | derived |
| bbox | [-44.694, 88.025, 13]..[44.694, 135, 19.5] | mm | derived from outline | 0.05 | derived |
| radius span from z axis | 90.000..135.225 | mm | derived from outline | - | derived (inside hub r 80 / disc r 140) |

## 4. Coordinate frame, scale, and measurement method

Frame = COMSOL global coordinates converted m -> mm (x 1000). Origin on the disc rotation axis in the disc symmetry plane z = 0 (the pad does not contain it). +x, +y: COMSOL global axes, the pad lies on +y and is mirror-symmetric about x = 0. +z: disc rotation axis, from the disc symmetry plane through the rubbing face (z = 13) into the pad. Datums: A = contact face z = 13 (normal -z); B = mirror plane x = 0; C = rotation axis x = y = 0.

No image measurement is used: every dimension is a packet coordinate. The figures were read only for topology: figure 1 shows one bean-shaped slab on the upper rubbing face at the back-left (+y per the axis triad, y pointing to the upper left), about half the disc thickness tall, inner edge outside the raised hub; figure 5 shows the same outline as wire edges with the probe line running from the disc centre to (-47, 131.6) under the pad's -x end. Acceptance values were computed by sampling each rational Bezier densely (200,001 points per curve, C(t) = sum(w_i B_i P_i) / sum(w_i B_i)), then shoelace area / centroid, polyline perimeter, and line crossings for sections. The intent's summary numbers (area 3544.4, centroid y 111.91, x +-44.69, y 88.03..135, r 90.00..135.23, volume 23038.5) were reproduced to the stated precision.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| padBaseZ | 13 | 0.01 | stated | step 3: work plane z = 0.013 m |
| padThickness | 6.5 | 0.01 | stated | step 4: extrude 0.0065 m. Edit +1: dV = area x 1 = 3544.39, bbox [0, 0, 1]. Feasible interval (0, inf); sweep 4.5 / 6.5 / 8.5; infeasible delta -6.5 (thickness 0, assert padThickness > 0) |
| outerApexY | 135 | 0.01 | stated | B1 P0 = B4 P3 (0, 0.135) |
| outerCtrlAx, outerCtrlAy | 20, 135 | 0.01 | stated | B1 P1 (0.02, 0.135); B4 P2 mirrored |
| outerCtrlBx, outerCtrlBy | 50, 130 | 0.01 | stated | B1 P2 (0.05, 0.13); B4 P1 mirrored |
| outerCtrlBWeight | 2.5 | 0.001 | stated | weight of B1 control point 3 and B4 control point 2. Edit +0.5 (w = 3.0): area 3571.717, dV = 27.331 x 6.5 = 177.65, x max 44.694 -> 45.258 so bbox [1.127, 0, 0]; y extents unchanged (apex and inner dip do not depend on w) |
| cornerX, cornerY | 40, 105 | 0.01 | stated | B1 P3 = B2 P0 (0.04, 0.105); mirrored. Junction is tangent-continuous (both tangents along (-10, -25)) |
| innerCtrlAx, innerCtrlAy | 30, 80 | 0.01 | stated | B2 P1 (0.03, 0.08); B3 P2 mirrored |
| innerCtrlBx, innerCtrlBy | 35, 90 | 0.01 | stated | B2 P2 (0.035, 0.09); B3 P1 mirrored |
| innerApexY | 90 | 0.01 | stated | B2 P3 = B3 P0 (0, 0.09); horizontal tangent on x = 0 |
| volume | 23038.51 | 0.2 % | derived | outline area 3544.386 x 6.5 |
| surface area | 8613.89 | 0.5 % | derived | 2 x 3544.386 + (outer 134.156 + inner 100.479) x 6.5 |
| centre of mass | (0, 111.905, 16.25) | 0.05 | derived | outline centroid; z = 13 + 6.5 / 2 |
| envelope | x +-44.694 (at y 121.47), y 88.025 (at x +-27.79)..135, z 13..19.5 | 0.05 | derived | sampled extrema |
| section midZ (z 16.25) | 3544.39, 1 loop | 0.2 % | derived | outline area |
| section axialX0 (x 0) | 292.5, 1 loop | 0.5 % | derived | (135 - 90) x 6.5 |
| section widthY120 | 579.98, 1 loop | 0.5 % | derived | crossings x = +-44.614, 89.228 x 6.5 |
| section widthY100 | 494.02, 1 loop | 0.5 % | derived | crossings x = +-38.001, 76.003 x 6.5 |
| section innerDipY89 | 177.89, 2 loops | 2 % | derived | inner wall dips to 88.025 below the apex at 90: islands x = 18.12..31.81 and mirror, 2 x 13.684 x 6.5 |
| faces contactFace / topFace | 3544.39 each, centre (0, 111.905) | 0.2 % | derived | outline area at z = 13 (-z) and z = 19.5 (+z) |
| dimensions | spanX 89.388, spanY 46.975, thicknessZ 6.5 | 0.05 / 0.05 / 0.02 | derived | envelope and padThickness |
| probes | solid 3.25+ mm inside every face (in-plane clearance >= 4.8 mm); void >= 1.5 mm outside | - | derived | point-to-outline distances computed on the sampled curves |
| blockout band | 21000..25000 | - | derived | the pad is the only primary solid (23038.5, about +-9 %); a full envelope box (27288) is excluded |

## 6. Defaults retained

- Envelope tolerance 0.05 mm and parameter tolerances 0.01 mm (0.001 on the weight): digital comparison thresholds for exactly stated coordinates.
- Symmetry band max 0.1 mm / p95 0.05 mm, sourced to the packet's mirrored control points.
- Process recorded as a simulation solid domain: the packet describes a thermal model, not a manufactured pad.

## 7. Unrepresentable or low-confidence features

- The side walls are rational Bezier sweeps, not planes or cylinders; they are checked through sections (widths at y = 100, 120, the two-island cut at y = 89), the envelope, and solid/void probes instead of face specs.
- The interface pins `contactPlane` (a plane spec without area) rather than `contactFace`, because the weight edit changes the contact area by 0.77 %.
- Not encoded here (assembly or disc concerns): the thermal-contact boundary number 11, the mirrored pad below z = 0 implied by the symmetry plane, the result probe line at z = 12.9 on the disc, the velocity/acceleration profiles, and the thermal physics settings.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
