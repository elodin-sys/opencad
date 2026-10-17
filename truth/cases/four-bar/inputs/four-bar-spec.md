# Planar four-bar linkage (crank-rocker): design specification

Four separate solids (no fused bodies): a ground plate and three links (crank, coupler, rocker) connected by pins into one
closed loop. The crank is driven through full revolutions; the rocker swings back and forth.

| Link | Hole centres | Body |
| --- | --- | --- |
| Ground | O2 (0, 0) and O4 (100, 0): ground length 100 | plate 160 x 60 x 5, corner (-30, -30, -5) to (130, 30, 0), Ø6 holes at O2 and O4 |
| Crank | O2 to A: 40 | stadium plate 5 thick, 16 wide, semicircular ends of radius 8 centred on its two holes, Ø6 holes |
| Coupler | A to B: 100 | stadium plate as the crank |
| Rocker | O4 to B: 80 | stadium plate as the crank |

Grashof: shortest + longest = 40 + 100 <= 100 + 80, with the shortest link as the crank, so the crank turns fully.

Frame: z up (every pin axis parallel to +z), O2 is the origin, +x from O2 toward O4. The links lie in layers so they never
touch except at their pins: ground z -5..0, crank z 0..5, coupler z 5..10, rocker z 10..15.

Part frames (each part drafted and modelled on its own): every link has its first hole (the one listed first above) at its
own origin, its second hole on +x at the link length, and its bottom face at z = 0. The ground is modelled in the frame above.

Rest configuration (the assembled, open configuration; angles about +z in the assembly):

- crank at 0 deg: A at (40, 0);
- coupler at 53.130102 deg: B at (100, 80) (the triangle A, O4, B has sides 60, 80, 100);
- rocker at 90 deg from O4: B at (100, 80).

Pins (all revolute about +z): O2 between ground and crank (the motor), A between crank and coupler, B between coupler and
rocker, O4 between ground and rocker. Four pins close one loop, so one of them is the loop's closing joint.

Coupler point P: fixed on the coupler at (50, 30) in the coupler's own frame (50 mm along A to B and 30 mm to its left), at
(46, 58) in the assembly at rest.

Motion: the crank turns one full revolution from rest (0 to 360 deg); the loop must stay closed and interference-free.

Predictions (the evaluator measures them from the placed geometry): the rocker's angle about O4 from rest (the ground as the
reference) as a series over the crank's revolution, the rocker's total swing over it, and the x and y coordinates of P over it.
