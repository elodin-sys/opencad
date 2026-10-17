# Engineering change request ECR-1: heat-set insert size change

The rear housing now uses M3 heat-set inserts with a Ø5.0 mm x 6.0 mm deep bore. Modify the two heat-set
traps on the back (mating) face of the extruder front at (x, z) = (-18.5, 22.0) and (-17.0, -20.0):

- the Ø6.5 mm x 9.8 mm deep bores from the back face (y = 0) become Ø5 mm x 6 mm deep;
- the Ø3.5 mm through portion of those two holes is unchanged.

Preserve every other interface exactly: all other hole axes, diameters and depths, the keyhole bore
stack, the hotend clamp channel, and the mating planes y = 0, y = 14, z = -30 and x = -26.5. The
bounding box must not change. Do not enlarge or shift anything else. Report the new analytic volume
delta (two bores: Ø6.5 x 9.8 minus Ø5.0 x 6.0 each).
