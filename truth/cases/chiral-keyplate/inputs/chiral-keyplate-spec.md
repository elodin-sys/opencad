# Chiral key plate

A square key plate, 80 mm by 80 mm by 8 mm thick, specified entirely in millimetres.
The plate lies in the XY plane with its centre at the origin and its bottom face at
z = 0 (top at z = 8). +x and +y run along the plate edges; +z is through the thickness.

Four identical rectangular slots are cut from the top face as pockets 4 mm deep; they
do not break through the bottom. Each slot is 16 mm by 6 mm in plan. They form a C4
pinwheel about the plate centre:

- Slot A: centre (20, 8) mm, long axis along x (the 16 mm side is parallel to x).
- Slot B: the 90 degree counter-clockwise rotation of A about z through the origin:
  centre (-8, 20) mm, long axis along y.
- Slot C: 180 degrees; centre (-20, -8) mm, long axis along x.
- Slot D: 270 degrees; centre (8, -20) mm, long axis along y.

The pinwheel is chiral. The left-right mirror of this pattern is a different key:
volume, bounding box, centre of mass and principal inertia are unchanged under that
mirror; the slot arrangement is not. Do not substitute a centred cross, a plus with
four-fold mirror symmetry, or the mirrored pinwheel.

One solid. Expose plateWidth (80 mm), plateHeight (80 mm), plateThickness (8 mm),
slotLength (16 mm), slotWidth (6 mm), slotDepth (4 mm), slotCentreX (20 mm) and
slotCentreY (8 mm, the centre of slot A) as named parameters. Prefer edit tests on
plateThickness and slotLength. Name the four pocket floors (z = 4 mm, outward normal
+z) so they can be told apart by their in-plane centres.
