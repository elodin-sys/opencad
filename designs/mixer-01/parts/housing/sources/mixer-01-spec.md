# mixer-01: sealed magnetic-drive paddle mixer, design specification

A small sealed mixer for water. Water enters through an axial inlet tube in the lid, a four-blade paddle impeller spinning on
a fixed pin stirs it in a cylindrical chamber, and it leaves through a radial outlet tube in the side wall. A motor under the
floor turns the impeller through the floor by a magnetic coupling (not modelled), so no shaft crosses the chamber wall and the
water space is sealed.

Bodies (separate solids, none fused):

1. **housing**: one modelled part (polypropylene, 900 kg/m3).
2. **impeller**: one modelled part (acetal, 1410 kg/m3).
3. **motor**: a purchased motor body, geometry a plain cylinder (see below).
4. **water**: the fluid region, derived from the placed housing and impeller.

## Frame

Assembly frame (mm): origin at the centre of the chamber floor's inside face, +z up along the impeller axis, +x toward the
outlet. The housing is modelled in this frame. The impeller's own frame has its origin at the centre of its hub's bottom face
and +z along its axis; one blade lies along its +x. The motor's own frame has its origin at the centre of its top (output)
face and +z along its shaft.

## Dimensions

| Item | Value |
| --- | --- |
| Chamber | inner diameter 50.0 (radius 25.0), inner height 25.0 (z 0..25) |
| Side wall | 3.0 thick (outer radius 28.0), z -3..28 |
| Floor | 3.0 thick, z -3..0 |
| Lid | 3.0 thick, z 25..28 |
| Inlet tube | on the axis, inner diameter 12.0, outer diameter 16.0, from the lid top z = 28 to z = 48, open at z = 48; its bore continues through the lid |
| Outlet tube | axis along +x at y = 0, z = 12.5; inner diameter 10.0, outer diameter 14.0; from the side wall to its open end at x = 58; its bore continues through the side wall |
| Pin | fixed, part of the housing, on the axis, diameter 6.0, from the floor z = 0 to z = 12 |
| Impeller hub | outer diameter 12.0, height 10.0 (z 0..10 in its own frame), through bore diameter 8.0 (1.0 radial clearance on the pin) |
| Impeller blades | four flat radial blades at 0, 90, 180, 270 deg about the axis, each 2.0 thick (tangentially, centred on its radius line), from radius 6.0 to radius 20.0, over z 1..9 in the impeller's frame (8.0 tall) |
| Motor body | cylinder diameter 30.0, length 40.0 (z -40..0 in its own frame) |

## Placement

- impeller: on the pin, its hub's bottom face 1.0 above the floor, so its own origin sits at (0, 0, 1) in the assembly frame
  (hub z 1..11, blades z 2..10; the pin's top at z = 12 stands 1.0 above the hub). Blade tips at radius 20 leave 5.0 to the
  chamber wall.
- motor: its top face against the floor's underside (z = -3), on the axis, fixed to the housing.

## Motion

The impeller turns about +z at the operating speed, positive counter-clockwise seen from above; the housing and motor body
are stationary. A full impeller turn must be free of interference with the housing (clearances at rest: 1.0 to the floor,
1.0 on the pin, 5.0 at the tips, 14.0 to the lid).

## Fluid

The water fills the chamber and both tube bores around the impeller and the pin. It is bounded by the housing and the
impeller and closed by two port planes: the inlet at the inlet tube's open end (z = 48, outward normal +z) and the outlet at
the outlet tube's open end (x = 58, outward normal +x). Its volume is about 5.24e4 mm3 (the chamber, the two bores, minus the
pin and the impeller). Boundaries: the inlet plane, the outlet plane, the impeller's wetted surface (rotating), and every
other wetted surface of the housing (stationary walls, the pin included).

Water at 20 degC: density 998.2 kg/m3, dynamic viscosity 1.002e-3 Pa s.

## Operating point

Design: impeller 1500 rpm, water flow 2.0 L/min, inlet turbulence intensity 5 %.

## Requirement

At the design point the static pressure rise from the inlet plane to the outlet plane is at least 500 Pa.

## Predictions

At the design point:

1. The static pressure rise (outlet minus inlet, area-averaged, Pa) and the torque the impeller absorbs about its axis (N m),
   from a steady CFD analysis of the water region with the impeller rotating. Report the numerical uncertainty from a
   three-level mesh study, each level refining everywhere. Runtime budget: each mesh level should solve in under 20 minutes
   on 4 cores (about 1.5 mm interior cells, walls one level finer, is a reasonable start).
2. An Euler-head estimate of the same static pressure rise for comparison. The blades are straight and radial (90 degree
   outlet angle), 8.0 tall at the tip; the hydraulic efficiency is not known.
3. The water volume.
