# Compound spur-gear train on a base plate: design specification

Four separate solids (no fused bodies): a base plate, an input pinion, a compound idler (two gears on one body) and an
output gear. The pinion drives the idler's large gear; the idler's small gear drives the output.

| Parameter | Value |
| --- | ---: |
| Module | 2 mm, both stages |
| Pressure angle | 20 deg |
| Profile shift | 0 (every gear) |
| Addendum / dedendum | 1.0 m / 1.25 m (tip radius = pitch radius + 2, root radius = pitch radius - 2.5) |
| Circular backlash | 0.10 mm per mesh: thin every tooth by 0.05 mm at its pitch circle |
| Input pinion | 20 teeth, face width 8 (z 0..8), bore Ø6, axis at (0, 0) |
| Compound idler | 40 teeth over z 0..8 and 15 teeth over z 8..16 on one solid, bore Ø8 through, axis at (60, 0) |
| Output gear | 45 teeth, face width 8 (z 8.5..16.5), bore Ø8, axis at (120, 0) |
| Centre distances | 60 mm (20 + 40 teeth) and 60 mm (15 + 45 teeth) |
| Base plate | 195 x 100 x 5 mm, corner (-25, -50, -5) to (170, 50, 0), clearance holes Ø6 at (0, 0) and Ø8 at (60, 0) and (120, 0) |

Frame: z up (every gear axis parallel to +z), the pinion axis is the origin, +x from the pinion toward the idler and the
output. The gears stand on the plate (plate top at z = 0); the output gear's bottom face is at z = 8.5, 0.5 mm above the top of
the idler's 40-tooth gear, so the two never touch axially.

Part frames (each part drafted and modelled on its own): every gear has its axis along +z through its own origin, its bottom
face at z = 0, and in its own frame a tooth centred on +x (for the idler, both its 40-tooth and its 15-tooth patterns have a
tooth centred on +x). The plate is modelled in the frame above.

Tooth phase at rest, so both meshes engage (angles about +z, in the assembly):

- pinion: 0 deg (a tooth centred on +x, toward the idler);
- idler: turned 4.5 deg (half its 9 deg pitch), which puts a 40-tooth space toward the pinion;
- output: turned 6.5 deg, which puts a 45-tooth space where the idler's 15-tooth gear (at 4.5 deg) reaches it.

Motion: the pinion is motor-driven; the idler turns at half the pinion's speed in the opposite sense; the output turns at a
third of the idler's speed in the opposite sense, so in the pinion's sense at one sixth of its speed. Both meshes must turn
through at least one pitch of their driving gear with zero interference and a flank gap of at most 0.15 mm.

The involute flanks may be built from the involute equations (recommended, 12-16 points per flank from the base circle to
the tip) or with a library's gear functions if they honour the module, tooth counts, pressure angle and backlash above.

Predictions (the evaluator measures them from the placed geometry): the whole train's transmission ratio (output angle over
pinion angle) and the output gear's angle from rest after the pinion has turned one revolution.
