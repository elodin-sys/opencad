# NASA TMR axisymmetric transonic bump (Bachalo–Johnson)

Source: NASA Turbulence Modeling Resource, ATB: Axisymmetric Transonic Bump
https://www.nasa.gov/reference/atb-axisymmetric-transonic-bump/
mirror: https://tmbwg.github.io/turbmodels/axibump_val.html
Bachalo, W. D. and Johnson, D. A., AIAA Journal Vol. 24 No. 3, 1986, pp. 437–443.

The model was designed and built in English units. Reconstruct ONE solid of revolution
suitable for a CFD outer-mould line, in millimetres, from the dimensions below. Do not
treat the inch figures as millimetres.

## Geometry (as built)

- Cylinder diameter d = 6 inches.
- Bump chord c = 8 inches (axial length of the circular-arc bump).
- Bump height t = 3/4 inch above the cylinder radius.
- The bump is a circular arc of radius R1 = 0.5 (t^2 + 0.25 c^2) / t.
- A leading-edge fillet of radius R2 blends the upstream cylinder to the bump. The
  references list R2 as 18.30 cm; 20.32 cm also appears. Use 18.30 cm (183.0 mm) and
  record 20.32 cm as an open question with an inferred alternate.
- There is no trailing-edge fillet in the experiment; a sharp join of the arc back onto
  the cylinder is correct.
- Axial extent: the attached surface-point file bumpgrd.surfpts_orig.dat lists the
  meridian used for the NASA grids. Coordinates are nondimensionalized by the 8-inch
  chord (so Y = 0.375 on the cylinder). Convert to millimetres by multiplying by
  8 inches. The solid runs over the full x-range of that file, with planar end caps.

## Frame

+x along the cylinder axis, increasing downstream. The bump chord occupies x = 0 to
x = c, so the leading-edge fillet sits at slightly negative x. The origin is on the
axis. +y and +z are radial; the solid is a full 360 degree revolve about +x.

## Parameters to expose

cylinderDiameter, bumpChord, bumpHeight, filletRadius (R2), and the upstream and
downstream axial extents (from the surface-point file). Edit tests: bumpHeight and
cylinderDiameter.

One solid. Name the two planar end caps.
