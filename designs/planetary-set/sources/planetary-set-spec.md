# Planetary gear set with a fixed ring: design specification

Seven separate solids (no fused bodies): a base plate, an internal ring gear fixed to the plate, a sun gear, a carrier and
three identical planet gears on the carrier. The sun is driven; the ring is held; the carrier is the output.

| Parameter | Value |
| --- | ---: |
| Module | 2 mm |
| Pressure angle | 20 deg |
| Profile shift | 0 |
| Circular backlash | 0.20 mm at the sun meshes, 0.15 mm at the ring meshes: thin every external tooth by 0.10 mm at its pitch circle and widen every ring tooth space by 0.05 mm |
| Sun | 24 teeth, pitch radius 24, tip 26, root 21.5; face width 10 (z 0..10); bore Ø10 |
| Planets (3) | 12 teeth, pitch radius 12, tip 14, root 9.5; face width 10 (z 0..10); bore Ø8 |
| Ring | 48 internal teeth, pitch radius 48, internal tip radius 46, root radius 50.5, outside radius 58; face width 10 (z 0..10) |
| Carrier | disc Ø88 x 5 over the gears (z 10..15), centre hole Ø10, three Ø8 holes on radius 36 at 0, 120 and 240 deg |
| Base plate | 150 x 150 x 5 mm, corner (-75, -75, -5) to (75, 75, 0), centre hole Ø10 |
| Planet orbit | radius 36 = 24 + 12 (sun + planet) = 48 - 12 (ring - planet) |

Frame: z up (every axis parallel to +z), the sun, ring and carrier axis is the origin. Gears and ring stand on the plate
(plate top at z = 0); the carrier lies on top of them (its bottom face at z = 10). The ring is rigidly fixed to the plate;
the sun and the carrier turn about the origin; each planet turns about its own axis on the carrier.

Part frames (each part drafted and modelled on its own, one planet design used three times): every gear, the ring and the
carrier have their axis along +z through their own origin and their bottom face at z = 0. In its own frame the sun has a
tooth centred on +x, each planet has a tooth centred on +x, the ring has an internal tooth centred on +x, and the carrier
has a planet hole centred on +x (at (36, 0)).

Rest configuration (angles about +z, in the assembly): the carrier at 0 deg, so the planet axes are at (36, 0),
(-18, 31.176915) and (-18, -31.176915); the sun at 0 deg; the ring at 0 deg; every planet turned 15 deg (half its 30 deg
pitch), which puts a planet tooth space toward the sun and a planet tooth space toward the ring for all three planets
(24 + 48 = 72 is divisible by 3, so equal spacing assembles).

The ring's internal flanks are involutes of its base circle (48 x 2 x cos 20 deg / 2 = 45.105 mm) with the material outside:
an annulus r 46..58 minus a 48-tooth external involute gear of module 2 whose tips reach r 50.5 (the ring root) and whose
teeth are the ring's tooth spaces is one construction. External involute flanks: 12-16 points per flank from the base circle to
the tip; below the base circle (sun 22.553 mm, planet 11.276 mm, both above their root radii) each flank continues as a radial
line down to the root circle, with no fillet: the ring's tips reach that deep into the planet roots.

Motion: the sun is motor-driven; relative to the carrier the planets turn opposite to the sun at 24/12 of the sun's
relative speed and mesh with the fixed ring, so the carrier turns in the sun's sense at 24/(24 + 48) of its speed. The set
must turn with zero interference between any gears and a flank gap of at most 0.2 mm at the sun meshes.

Predictions (the evaluator measures them from the placed geometry): the carrier's transmission ratio (carrier angle over sun
angle) and the carrier's angle from rest after the sun has turned one revolution.
