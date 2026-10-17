# planetary-set-sun — design brief

## 1. Intent and configuration

Sun gear of the `planetary-set` assembly (sun driven, ring fixed, carrier output), drafted in its own frame. 24 external involute teeth, module 2, pressure angle 20 deg, zero profile shift; pitch radius 24, tip 26, root 21.5, base 22.553. Face width 10 (z 0..10), D10 through bore on the axis. Involute flanks (12-16 points per flank) from the base circle to the tip, a radial line from the base circle down to the root circle, no root fillet. Every tooth is thinned by 0.10 mm at the pitch circle (thickness 3.0416 mm), giving 0.20 mm circular backlash with each planet. A tooth is centred on +x (tooth centres at k x 15 deg). The bottom face stands on the base plate; the top face carries the carrier; the assembly attaches the part by the revolute joint `sunSpin` at [0, 0, 0], axis [0, 0, 1]. Authoritative source: `sources/planetary-set-spec.md` (text only). Single solid.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/planetary-set-spec.md | text | authoritative | 2a8bca0f4ffa01692bc1a5879aeb8b02a1d728b2cbe39448f181197d86ca14ca | parameter table (Sun row, module, pressure angle, shift, backlash rule), flank construction paragraph, part-frame paragraph; no images |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| tooth count | 24 | | spec table, intent | exact | stated |
| module | 2 | mm | spec table, intent | 0.001 | stated |
| pressure angle | 20 | deg | spec table, intent | 0.01 | stated |
| profile shift | 0 | | spec table, intent | 0.001 | stated |
| pitch / tip / root / base radius | 24 / 26 / 21.5 / 22.553 | mm | spec table, intent | 0.001 | stated (also derived) |
| face width, z 0..10 | 10 | mm | spec Sun row, intent | 0.01 | stated |
| bore, through on axis | D10 | mm | spec Sun row, intent | 0.01 | stated |
| tooth thinning at pitch circle | 0.10 | mm | spec backlash row, intent | 0.001 | stated |
| tooth thickness at pitch circle | 3.0416 | mm | intent | 0.001 | stated (derived) |
| flank points, base circle to tip | 12-16 | | spec flank paragraph, intent | range | stated range; 14 inferred |
| radial flank below base circle to root, no fillet | | | spec flank paragraph, intent | | stated |
| tooth centred on +x, centres at k x 15 deg | | deg | spec part-frame paragraph, intent | | stated |
| axis +z through origin, bottom face z = 0 | | | spec part-frame paragraph, intent | | stated |
| meshing with planets at centre distance 36, gap <= 0.2 mm, no interference | | mm | spec motion paragraph | | assembly-level (open question) |

## 4. Coordinate frame, scale, and measurement method

Origin on the gear axis in the bottom-face plane (z = 0). +z is the gear axis, up from the bottom face (on the base plate) to the top face (z = 10, under the carrier). +x passes through the centre line of one tooth; tooth centres sit at k x 15 deg (k = 0..23), so +y (k = 6), -x (k = 12) and -y (k = 18) also pass through tooth centres and the profile is mirror-symmetric about both x = 0 and y = 0. Datums: A = bottom face z = 0; B = bore axis (joint `sunSpin`, [0, 0, 0], axis [0, 0, 1]); C = the XZ plane through the +x tooth centre line. Envelope [-26, -26, 0] to [26, 26, 10]: tip lands at 0, 90, 180 and 270 deg reach radius 26 (a straight tip chord reaches 25.9916, inside the 0.05 tolerance). No images or meshes: every value is quoted or derived from the text; no pixel scale is involved.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| teeth | 24 | 0.5 | stated | spec Sun row |
| gearModule | 2 mm | 0.001 | stated | spec Module row |
| pressureAngle | 20 deg | 0.01 | stated | spec Pressure angle row |
| profileShift | 0 | 0.001 | stated | spec Profile shift row |
| faceWidth | 10 mm | 0.01 | stated | spec Sun row; edit test +2, sweep 8/10/12, infeasible -10 |
| toothThinning | 0.10 mm | 0.001 | stated | spec backlash row; edit test +0.1 |
| boreDiameter | 10 mm | 0.01 | stated | spec Sun row |
| pitchRadius | 24 mm | 0.001 | derived | teeth * gearModule / 2 |
| tipRadius | 26 mm | 0.001 | derived | pitchRadius + gearModule * (1 + profileShift) |
| rootRadius | 21.5 mm | 0.001 | derived | pitchRadius - gearModule * (1.25 - profileShift) |
| baseRadius | 22.5526 mm | 0.001 | derived | pitchRadius * cos(pressureAngle) = 22.552623 |
| toothThickness | 3.0416 mm | 0.001 | derived | pi * gearModule / 2 - toothThinning = 3.041593 |
| flankPoints | 14 | 2 | inferred | middle of the stated 12-16 range |
| half tooth angle at pitch psi_p | 0.0633665 rad | | derived | toothThickness / (2 * pitchRadius) |
| half tooth angle at base / below it psi_b | 0.0782709 rad | | derived | psi_p + inv(20 deg), inv(a) = tan a - a; radial flank at this angle down to the root |
| half tooth angle at tip psi_a | 0.0254378 rad | | derived | psi_b - inv(acos(baseRadius / tipRadius)); tip land 1.3228 mm, root space arc 2.2630 mm (both positive) |
| tooth area above the root circle | 13.0214 mm^2 | | derived | integral of 2 psi(r) r dr, r = 21.5..26 (numeric, 200000 strips) |
| section area A (midZ, topFace) | 1686.18 mm^2 | 0.5 % | derived | pi 21.5^2 + 24 * 13.0214 - pi 5^2 |
| volume | 16861.76 mm^3 | 0.5 % | derived | faceWidth * A |
| surface area | 6833.58 mm^2 | 2 % | derived | 2 A + 10 * P + 10 * pi * 10, P = 314.706 mm (24 x (root arc + 2 radial lines + 2 involutes of length baseRadius tan^2(a_tip)/2 + tip land)) |
| centre of mass | (0, 0, 5) | 0.05 | derived | 24-fold symmetry, mid face width |
| faceWidth edit, delta +2 | +3372.35 mm^3, bbox +2 in z | 2 % | derived | 2 * A; bottom face stays at z = 0 |
| toothThinning edit, delta +0.1 | -106.875 mm^3, bbox 0 | 5 % | derived | each flank turns by 0.1 / (2 pitchRadius) at every radius; area swept by turning a curve about the axis is (angle / 2)(r2^2 - r1^2), so dV = -teeth * (0.1 / pitchRadius) * (26^2 - 21.5^2) / 2 * faceWidth |
| blockout band | 20000..21300 mm^3 | | derived | tip-radius disc with bore 20451.77, without bore 21237.17; both fill the envelope |
| probes | see contract | | derived | tooth centres at r 24 (1.52 mm from each flank); tooth-space centres at +-7.5 deg, r 24.5 (about 1.7 mm from each flank); bore axis points z 2/5/8; hub points r 15 |

Feasible intervals: faceWidth in (0, inf), the sweep 8..12 stays inside it and faceWidth + (-10) = 0 must fail an assert; toothThinning in [0, 1.32) (the 1.3228 mm tip land shrinks by tipRadius / pitchRadius = 26/24 per mm of extra thinning and closes at about 1.32 mm), the edit to 0.20 stays inside it.

## 6. Defaults retained

- Material, density and process stay null: the sources state none and no mass claim is made.
- Symmetry deviation bands use the evaluator defaults (no source states a tighter band).
- Standard full-depth proportions (addendum 1.0 m, dedendum 1.25 m) are implied by the stated tip and root radii, not assumed independently.

## 7. Unrepresentable or low-confidence features

- The involute is a 12-16 point polyline per flank, not an exact curve; the chord error lowers the section area by about 0.25 mm^2 (0.015 %), well inside the volume tolerance.
- Meshing with the three planets (centre distance 36, flank gap at most 0.2 mm, zero interference, 0.20 mm circular backlash) cannot be checked on this single part; it belongs to the `planetary-set` assembly checks. The per-tooth thinning that produces the backlash is encoded here.
- No chamfers, edge breaks or keyway are given; none are modelled.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
