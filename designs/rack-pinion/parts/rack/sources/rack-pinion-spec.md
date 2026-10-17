# Rack and pinion on a base plate: design specification

Three separate solids (no fused bodies): a base plate, a pinion that turns on it, and a rack that slides on it. The pinion
is driven; the rack follows.

| Parameter | Value |
| --- | ---: |
| Module | 2 mm (pitch p = 2 pi = 6.283185 mm) |
| Pressure angle | 20 deg |
| Pinion | 20 teeth, pitch radius 20, tip 22, root 17.5; face width 8 (z 0..8); bore Ø6; axis at (0, 0) |
| Rack | 32 teeth on a straight pitch line, 200 mm long, 8 mm thick (z 0..8) |
| Rack teeth | addendum 2 above the pitch line, dedendum 2.5 below it; straight flanks at 20 deg from the normal to the pitch line; tooth thickness on the pitch line p/2 - 0.05 = 3.091593 (tip width 1.635712, root width 4.911444) |
| Rack body | 9.5 mm deep below the root line (back face 12 mm below the pitch line) |
| Backlash | thin every pinion tooth by 0.05 mm at its pitch circle (0.10 mm per mesh with the rack's thinning) |
| Base plate | 240 x 80 x 5 mm, corner (-120, -50, -5) to (120, 30, 0), clearance hole Ø6 at (0, 0) |

Frame: z up (the pinion axis parallel to +z), the pinion axis is the origin, the rack below the pinion with its pitch line
on y = -20 (tangent to the pinion's pitch circle) along +x, its teeth pointing +y toward the pinion. Pinion and rack stand
on the plate (plate top at z = 0).

Part frames (each part drafted and modelled on its own): the pinion has its axis along +z through its own origin, its bottom
face at z = 0 and a tooth centred on +x. The rack's own frame has its origin on the pitch line at the middle of its length,
+x along the pitch line, +y toward the tooth tips, its bottom face at z = 0; its 32 teeth are centred at x = (k + 1/2) p for
k = -16 .. 15 (so a tooth space is centred on x = 0) and its body runs from x = -100 to x = 100. The plate is modelled in the
frame above.

Rest configuration: the pinion at 0 deg (its tooth at -90 deg points into the rack space at x = 0); the rack's origin at
(0, -20, 0) in the assembly. The rack slides along +x on the plate; the pinion turns about its axis.

Motion: the pinion is motor-driven through one full revolution; its pitch point carries the rack, so the rack moves along +x
by the pitch circle's arc for every degree of pinion rotation (positive about +z moves the rack toward +x). The pair must
run through the whole revolution with zero interference.

Pinion flanks are involutes (12-16 points per flank from the base circle to the tip) or a library gear that honours the
module, tooth count, pressure angle and backlash.

Predictions (the evaluator measures them from the placed geometry): the rack's transmission ratio (rack travel in mm per
degree of pinion rotation) and the rack's total travel over one pinion revolution.
