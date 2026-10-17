# Offset crank-slider mechanism: design specification

Four separate solids (no fused bodies): a ground plate, a crank, a connecting rod and a slider, forming one closed loop. The
crank is driven through full revolutions; the slider reciprocates along a straight guide offset from the crank axis.

| Part | Geometry |
| --- | --- |
| Ground | plate 200 x 70 x 5, corner (-40, -30, -5) to (160, 40, 0), Ø6 hole at the crank axis O (0, 0) |
| Crank | O to crank pin A: 30; stadium plate 5 thick, 16 wide, semicircular ends of radius 8 centred on its two holes, Ø6 holes |
| Connecting rod | A to wrist pin B: 100; stadium plate as the crank |
| Slider | block 30 (along the guide) x 16 x 5 centred on B, Ø6 hole at B |
| Guide | the line y = 10 (offset e = 10 from the crank axis), parallel to +x |

Frame: z up (every pin axis parallel to +z), O is the origin, the guide parallel to +x. Layers: ground z -5..0, crank and
slider z 0..5 (they never meet: the slider stays beyond x = 54), rod z 5..10 on top of both.

Part frames (each part drafted and modelled on its own): the crank and the rod have their first hole (O for the crank, A for
the rod) at their own origin, their second hole on +x at their length, and their bottom face at z = 0; the slider's own
origin is at its hole centre on its bottom face, its 30 mm length along +x. The ground is modelled in the frame above.

Rest configuration: crank at 0 deg (A at (30, 0)); wrist pin B at (129.498744, 10) on the guide (|AB| = 100); rod at
5.739170 deg from +x; slider centred on B.

Joints: O between ground and crank (revolute, the motor), A between crank and rod (revolute), B between rod and slider
(revolute), and the guide between ground and slider (prismatic along +x, no rotation). They close one loop, so one of them
is the loop's closing joint.

Motion: the crank turns one full revolution from rest (0 to 360 deg); the loop must stay closed and interference-free.

Predictions (the evaluator measures them from the placed geometry): the slider's travel along the guide from rest as a series
over the crank's revolution, and its stroke (total travel range) over it.
