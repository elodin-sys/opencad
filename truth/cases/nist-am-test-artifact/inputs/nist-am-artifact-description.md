# NIST Additive Manufacturing Test Artifact: published description (excerpts)

Source: S. P. Moylan, J. A. Slotwinski, A. L. Cooke, K. K. Jurrens, M. A. Donmez, "An Additive
Manufacturing Test Artifact", J. Res. NIST 119 (2014), doi:10.6028/jres.119.017, section 7 and Fig. 8;
NIST's artifact page (public domain, US Government work). The engineering drawing (Fig. 8, two pages)
is attached as `drawing-01.png` and `drawing-02.png`; its GD&T tolerance boxes read "xx" on purpose.

## Overview (paper, section 7)

"The artifact is comprised of several features with simple geometry, atop or within a diamond-shaped
base." "The part should be built in the center of the building platform with the 4 mm pins and holes
aligned along the machine x- and y-axes. It is 17 mm tall and has a volume of approximately 101 000
mm3."

Feature list (Fig. 7 labels): Top Surface; Center Hole; Central Cylinders; 4 mm Holes (x4); 4 mm Pins
(x16); Staircases (two) with Vertical Surfaces; Ramp; Lateral Features; Fine Features: Negative (x5
holes) and Positive (x5 pins), plus neighbouring rectangular bosses/holes; Outer Edges.

## Datum frame used for this reconstruction

- 7.1 "The top surface of the part is the primary datum feature defining the z-direction and the
  z-origin of the measurement coordinate system." So z = 0 on the top surface, +z toward the pin tips;
  the diamond base extends to z = -10 (10 mm thick) and the tallest features reach z = +7 (17 mm total).
- 7.2 "The center hole in the part is the secondary datum feature defining the x- and y-origin." So
  the Ø10 through hole is on the z axis at x = y = 0.
- 7.3 "The right-most hole in the top view of the part is the tertiary datum feature defining the
  x-direction." So +x points from the centre toward the 4 mm hole at x = +60, and the 4 mm pin and
  hole rows lie along +-x and +-y.
- The diamond base is a 100 mm square rotated 45 deg about z: its corners lie on the x and y axes.

## Feature notes (paper, sections 7.2-7.9)

- Center hole and central cylinders: a round through hole on the z axis inside two concentric round
  bosses that rise from the top surface (7.6: "round or arced bosses ... concentric features").
- Pins and holes (7.3): sixteen Ø4 pins standing on the top surface along the +-x and +-y axes at
  20, 30, 40 and 50 mm from centre; four Ø4 holes through the base at 60 mm from centre on the same
  axes.
- Staircases (7.4): two L-shaped staircases with 1 mm steps ("the distance between steps (1 mm)");
  one rises above the top surface in the (-x, +y) quadrant, the other descends into the base in the
  (-x, -y) quadrant. Section F-F / G-G on drawing page 2 give the step heights 3, 4, 5, 6, 7 mm from
  datum A. Step treads are 10 mm squares.
- Ramp (7.7): "designed to slope constantly with a 1 mm rise over a 25 mm run", with "2.5 mm flat
  landings at its top and bottom", in the (+x, -y) quadrant along the diagonal, rising from 1 mm to
  2 mm above the top surface (drawing section C-C).
- Lateral features (7.8): on one outer edge (the (-x, +y) diamond side) a set of shallow lateral
  cavities and bosses of different cross-sections (round Ø3 x 3 deep and Ø6 x 5 deep holes, square,
  diamond, hexagon and lens shapes) cut into the vertical side face at mid-height of the base
  (drawing section A-A). Reproduce the round ones exactly; the others as drawn.
- Fine features (7.9): "the widths of the fine features descend from 2 mm to 0.25 mm from the center
  of the set outward ... All features are 2 mm tall or deep." Round pins (Ø2, 1.5, 1, 0.5, 0.25) on
  the top surface along the diagonal in the (+x, +y) quadrant and matching round holes on the other
  side of that diagonal (section D-D); neighbouring rectangular bosses and slots of widths 2 to 0.25
  along the diagonal further out (section E-E).
- Outer edges (7.5): three plain 45 deg diamond sides; the fourth carries the lateral features.

The renders (`renders/*.png`, orthographic with a mm grid) and section drawings show exactly where
each feature sits. `dimension-sheet.md` lists every planar face level, cylindrical feature axis,
diameter and depth, and section summary measured from the reference geometry by the evaluator. The
reference CAD itself is not available to the design agent.
