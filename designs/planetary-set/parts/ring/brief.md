# planetary-set-ring — design brief

## 1. Intent and configuration

The fixed 48-tooth internal ring gear of the planetary-set assembly, drafted in its own frame: annulus r 46..58, z 0..10, with involute internal teeth (module 2, 20 deg, zero shift) whose spaces are widened 0.05 mm at the pitch circle (0.15 mm circular backlash with each planet). It sits rigidly on the base plate (joint ringFixed, own-frame origin, axis +z); three planets mesh inside it on radius 36. Authoritative source: `sources/planetary-set-spec.md`.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/planetary-set-spec.md | text | authoritative | 2a8bca0f4ffa01692bc1a5879aeb8b02a1d728b2cbe39448f181197d86ca14ca | Ring row, part frames, involute construction, backlash row |

## 3. Requirement record

| requirement | value | unit | source | tolerance | status |
|---|---|---|---|---|---|
| internal teeth | 48 | | spec Ring row | exact | stated |
| module / pressure angle / shift | 2 / 20 / 0 | mm / deg / | spec table | 0.001 / 0.01 / 0.001 | stated |
| pitch / tip / root / base radius | 48 / 46 / 50.5 / 45.105 | mm | spec Ring row, construction | 0.01 | stated |
| outside radius, face width | 58, 10 (z 0..10) | mm | spec Ring row | 0.01 | stated |
| space widening at pitch | 0.05 (space 3.1916, tooth 3.0916) | mm | spec backlash row | 0.001 | stated |
| tooth centred on +x | 0 | deg | spec part frames | 0.01 | stated |
| points per flank | 12-16 | | spec construction | range | stated |
| rigid on plate, concentric | bottom face z = 0, axis z | | spec frame, joint ringFixed | 0.05 | stated |

## 4. Coordinate frame, scale, and measurement method

Origin on the ring axis in the bottom face plane; +x through a tooth centre (teeth at k x 7.5 deg, spaces at 3.75 + k x 7.5 deg); +z along the axis to the top face z = 10. Datum A = bottom face, datum B = the axis. Text-only source: no images, no scaling. Areas computed by numerically integrating the involute tooth-space half-angle psi(r) = s/(2 rp) + inv(20 deg) - inv(acos(rb/r)), s = 3.1916, from r 46 to 50.5.

## 5. Measurement and inference record

| parameter | value | tolerance | provenance | source / formula / rationale |
|---|---|---|---|---|
| faceWidth | 10 | 0.01 | stated | spec Ring row |
| outerRadius | 58 | 0.01 | stated | spec Ring row |
| toothCount | 48 | 0.001 | stated | spec Ring row |
| gearModule | 2 | 0.001 | stated | spec table |
| pressureAngle | 20 | 0.01 | stated | spec table |
| profileShift | 0 | 0.001 | stated | spec table |
| pitchRadius | 48 | 0.01 | derived | gearModule * toothCount / 2 |
| tipRadius | 46 | 0.01 | derived | pitchRadius - gearModule |
| rootRadius | 50.5 | 0.01 | derived | pitchRadius + 1.25 gearModule |
| baseRadius | 45.1052 | 0.01 | derived | pitchRadius cos(pressureAngle) |
| spaceWidening | 0.05 | 0.001 | stated | spec backlash row |
| spaceWidth | 3.1916 | 0.001 | derived | pi gearModule / 2 + spaceWidening |
| toothThickness | 3.0916 | 0.001 | derived | pi gearModule / 2 - spaceWidening |
| pitchAngle | 7.5 | 0.001 | derived | 360 / toothCount |
| toothPhase | 0 | 0.01 | stated | tooth centred on +x |
| flankPoints | 14 | 2 | stated | range 12-16 |
| section area (z = 5) | 3294.075 mm2 | 0.2 % | derived | pi(58^2 - 46^2) - 48 x 13.0548 (one tooth space r 46..50.5) |
| volume | 32940.75 mm3 | 0.2 % | derived | 10 x section area |
| surface area | 16270.67 mm2 | 1 % | derived | 2 x 3294.075 + 2 pi 58 x 10 + 10 x 48 x (2 x 4.8137 + 1.8318 + 1.1205); flank = (50.5^2 - 46^2)/(2 rb) |
| centre of mass | (0, 0, 5) | 0.05 | derived | 48-fold symmetry, mid width |
| sections y = 0, x = 0 | 240 mm2 each | 0.5 % | derived | 2 x (58 - 46) x 10 through tooth centres |
| faceWidth edit +2 | +6588.15 mm3, bbox +[0,0,2] | 2 % | derived | 2 x 3294.075; feasible faceWidth > 0 (sweep 6, 10, 14; infeasible delta -10) |
| outerRadius edit +2 | +7414.16 mm3, bbox +[4,4,0] | 2 % | derived | pi (60^2 - 58^2) x 10; feasible outerRadius > rootRadius 50.5 (sweep 54, 58, 64; infeasible delta -8) |
| blockout band | 25000..39700 mm3 | | derived | annulus r 50.5..58 (25565) to annulus r 46..58 (39207) |

## 6. Defaults retained

Envelope tolerance 0.05 mm; probe radii chosen on the pitch circle (1.45 mm to the flanks for tooth centres, 1.5 mm for space centres) and 1.5 mm inside the tip / beyond the root. Material, density and process stay null (not stated; no mass claim).

## 7. Unrepresentable or low-confidence features

The 0.15 mm circular backlash with each planet and the planet orbit radius 36 are assembly-level mesh properties; this contract carries only the ring's share (spaceWidening, spaceWidth, volume). Flank accuracy below the 0.05 mm widening is not probed directly (probes need 1 mm clearance); the volume tolerance (about 66 mm3) is below the widening's effect (about 108 mm3). The gear inspector must read the teeth on the internal loop.

## 8. Blockout checkpoint log

| iteration | bbox measured | volume measured | verdict | adjustment |
|---|---|---|---|---|
