# planetary-set-planet — design brief

## 1. Intent and configuration

Planet gear of the fixed-ring planetary set: one design, placed three times (bodies planet1, planet2, planet3 of the
assembly `planetary-set`, revolute joints planet1Spin..planet3Spin at own-frame point [0, 0, 0], axis +z). 12 external
involute teeth, module 2, pressure angle 20 deg, zero profile shift, face width 10, D8 through bore. Each tooth is
thinned by 0.10 mm at the pitch circle for backlash, and a tooth is centred on +x. The bottom face stands on the base
plate and the top face touches the carrier; the gear meshes with the sun and inside the ring at centre distance 36.
The only authoritative source is `sources/planetary-set-spec.md` (text; no images, no reference model).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/planetary-set-spec.md | text | authoritative | 2a8bca0f4ffa01692bc1a5879aeb8b02a1d728b2cbe39448f181197d86ca14ca | parameter table (planet row, backlash row), part frames, rest configuration, flank construction |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| tooth count | 12 | | spec table, Planets | exact | stated |
| module | 2 | mm | spec table | 0.001 | stated |
| pressure angle | 20 | deg | spec table | 0.01 | stated |
| profile shift | 0 | | spec table | 0.001 | stated |
| pitch / tip / root radius | 12 / 14 / 9.5 | mm | spec table | 0.05 (bbox, cylinders) | stated |
| base radius | 11.276 | mm | spec flank paragraph | 0.001 | stated |
| face width | 10 (z 0..10) | mm | spec table | 0.05 | stated |
| bore | D8 through, on the axis | mm | spec table | 0.05 | stated |
| tooth thinning at the pitch circle | 0.10 (thickness 3.0416) | mm | spec backlash row | 0.001 | stated |
| flank construction | involute, 12-16 points base to tip; radial line base to root; no fillet | | spec flank paragraph | | stated |
| tooth phase | tooth centred on +x, centres at k x 30 deg | deg | spec part frames | 0.01 | stated |
| frame | axis +z through origin, bottom face z = 0 | | spec part frames | | stated |
| mates | bottom on base plate, top on carrier, bore coaxial with carrier planet hole | | spec frame paragraph | | stated |
| material, density, process | not given | | | | open |

## 4. Coordinate frame, scale, and measurement method

Origin at the centre of the bottom face on the gear axis. +z is the gear and bore axis (bottom face z = 0, top face
z = 10). +x runs through the centre line of one tooth (tooth centres at k x 30 deg), +y completes a right-handed frame,
and y = 0 is a mirror plane of the gear. Datums: A is the bottom face, B is the bore axis, C is the tooth centre plane
y = 0. No images or meshes: every value is quoted from the text or derived from it by standard involute gear formulas,
so no scale was set.

Tooth half-angle at radius r (base circle to tip): psi(r) = s / (2 rp) + inv(20 deg) - inv(acos(rb / r)), with
s = 3.041593, rp = 12, rb = 11.276311, inv(a) = tan a - a. This gives psi_b = 0.141637 rad (8.1152 deg) at the base
circle and psi_a = 0.040183 rad (2.3023 deg) at the tip, so the tip land is 1.1248 mm wide. Between the base and root
circles each flank is the radial line at +/-psi_b.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| gearModule | 2 mm | 0.001 | stated | spec table |
| toothCount | 12 | 0.01 | stated | spec table |
| pressureAngle | 20 deg | 0.01 | stated | spec table |
| profileShift | 0 | 0.001 | stated | spec table |
| faceWidth | 10 mm | 0.01 | stated | spec table; edit +2 gives dV = 2 x 377.009 = +754.02, bbox +2 in z; feasible faceWidth > 0 (sweep 8/10/12; delta -10 must assert) |
| toothThinning | 0.10 mm | 0.001 | stated | spec backlash row; edit +0.10 turns every flank by 0.1 / 24 rad, so dA = -12 x (0.1 / 24) x (14^2 - 9.5^2) = -5.2875 and dV = -52.875 with no bbox change; feasible -2.78 < toothThinning < 1.064 (the root space closes at -2.78, the tip becomes pointed at 1.064; no sweep; delta +1.0 must assert) |
| boreDiameter | 8 mm | 0.01 | stated | spec table |
| toothPhase | 0 deg | 0.01 | stated | spec part frames: tooth centred on +x |
| flankPoints | 14 | 2 | inferred | stated range 12-16; midpoint, and the tolerance spans the range |
| toothPitchAngle | 30 deg | 0.001 | derived | 360 / toothCount |
| pitchRadius | 12 mm | 0.001 | derived | gearModule x toothCount / 2 (also stated) |
| tipRadius | 14 mm | 0.001 | derived | pitchRadius + gearModule x (1 + profileShift) (also stated) |
| rootRadius | 9.5 mm | 0.001 | derived | pitchRadius - gearModule x (1.25 - profileShift) (also stated) |
| baseRadius | 11.276311 mm | 0.001 | derived | pitchRadius x cos(pressureAngle) (also stated) |
| pitchToothThickness | 3.041593 mm | 0.001 | derived | pi x gearModule / 2 + 2 x profileShift x gearModule x tan(pressureAngle) - toothThinning |
| profile area | 427.274 mm2 | | derived | pi rf^2 + 12 [psi_b (rb^2 - rf^2) + int from rb to ra of 2 psi(r) r dr]; polyline flanks give 427.173 (12 points) to 427.219 (16 points) |
| net section area (mid, nearBottom, nearTop, top face) | 377.009 mm2 | 0.5 % | derived | 427.274 - pi x 4^2 |
| volume | 3770.09 mm3 | +/-6 | derived | 10 x 377.009; the 12-point polyline gives 3769.07 |
| surface area | 2573.28 mm2 | 1 % | derived | 2 x 377.009 + 10 x (156.793 + 8 pi); perimeter per tooth: 2 x 3.0526 involute + 2 x 1.7763 radial + 1.1250 tip + 3.3037 root |
| centre of mass | (0, 0, 5) | 0.05 | derived | 12-fold symmetry, mid-plane |
| radial flank planes (+x tooth) | point (10.284131, +/-1.466437, 5), normal (-0.141164, +/-0.989986, 0), area 17.763 | 1 % | derived | mid radius (rf + rb) / 2 at +/-psi_b; area (rb - rf) x 10 |
| probes | solid (13, 0, 5): 1.15 mm inside the flanks; void (11.5911, 3.1058, 5) at r 12 in the 15 deg space: 1.6 mm from the flanks; void (10.2388, 2.7435, 5) at r 10.6: 1.1 mm above the root and 1.27 mm from the radial flanks | | derived | psi(13) = 0.0888 rad; space half-angle at r 10.6 is 15 - 8.115 = 6.885 deg |
| blockout band | 5400..6300 mm3 | | derived | tip-circle blank r 14 x 10: 6157.5 (5654.9 with the bore) |

## 6. Defaults retained

- Material, density and process are left null: the spec gives none and no mass is claimed.
- Edges are sharp (no chamfers or root fillet): the spec forbids a root fillet and states no edge breaks.
- Symmetry band on mirrorY is left at the pipeline defaults: no source states a tighter band.
- release_status stays `reconstruction` from the template.

## 7. Unrepresentable or low-confidence features

- The spec says 12-16 points per flank but not whether they are joined by a spline or a polyline; the volume, area
  and section tolerances cover both.
- The mesh requirements (zero interference, a sun-mesh flank gap of at most 0.2 mm, 0.5 mm radial clearance between
  the ring tips at r 10 and the planet root) belong to the placed assembly; this contract only fixes the tooth geometry
  that produces them (root radius 9.5, no fillet, 0.10 mm thinning).
- The tip circle is checked as a cylinder (12 coaxial patches; any one identifies the radius). The root circle is not
  a cylinder check, because a hole of radius 9.5 on the axis would contradict the hub solid probes. The radial flank
  plane areas ((rb - rf) x 10 = 17.763) pin the root radius instead, backed by the section area and the r 10.6 void
  probe.
- The bore cylinder has no length so that the faceWidth edit keeps the spinAxis interface check. The through length is
  checked by the nearBottom and nearTop sections and the void probes in the bore.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
