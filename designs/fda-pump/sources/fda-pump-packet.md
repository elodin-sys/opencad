# FDA benchmark blood pump (Interlaboratory Study 2): reference packet

Transcribed from the FDA / OSEL-DAM *CFD and Blood Damage Benchmarks* repository, `Blood Pump/Blood_Pump_Instructions.zip`
(commit ca35ecc44137fa6bd0d735190eb836ea0dc0d547, accessed 2026-09-25): pump geometry, CAD files, experimental setup and
simulation conditions. Nonclinical engineering use only; no results are included.

## Pump geometry

All units in the source documents are SI. The test object is a simplified centrifugal blood pump.

- Rotor: outside diameter 0.052 m; four blades at 90 degrees, each 0.003 m x 0.003 m x 0.0185 m long; including the blades
  the rotor is 0.007 m thick; rotor shaft diameter 0.0032 m. The rotor edges are filleted (0.05-0.6 mm radii, included in the
  CAD); the rim has a slight curve in z from polishing.
- Housing chamber: inner diameter 0.06 m, inner width 0.009 m. The cutwater has a 40 um fillet (included in the CAD).
- Housing/rotor clearances: 0.001 m between the housing and the front and back rotor faces; 0.004 m between the housing and
  the rotor rim.
- Inlet: tube inner diameter 0.012 m, curved with a 0.09 m radius (for flow visualisation), leading into a straight inlet
  tube that extends 0.204 m from the end of the curved tube to the opposite side of the housing chamber; 0.005 m fillet
  where the inlet tube meets the chamber.
- Outlet: throat 0.02 m long with a 0.00439 m inner diameter, widening through a 0.02154 m long diffuser to the 0.012 m
  inner-diameter outlet tube.

## CAD files (sources/)

`pump_housing.step` and `pump_rotor.step` (created in GAMBIT; ACIS and IGES versions exist upstream). The housing model is
the INNER surface of the pump chamber and tubing: subtract the rotor from it to get the flow domain. The rotor is in its
proper position relative to the housing and gives the proper clearances when subtracted; one rotor blade is 90 degrees to
the outlet, the orientation to use for steady simulations. The CAD was created with a scale factor of 1 unit = 100 um:
re-scale to get a housing diameter of 0.06 m. The files use the Cartesian coordinates of the drawings (see
`coordinate_system.png`).

## Experimental setup

The inlet pressure probe is at the same height as the pump axis, 0.175 m from the bottom of the pump chamber; the outlet
pressure probe is 0.245 m above the pump axis. Pressures are static, spatially averaged over the inlet and outlet tubing at
those locations, and the pressure rise is outlet minus inlet with the hydrostatic component zeroed.

## Simulation conditions

Newtonian blood-analog fluid: density 1035 kg/m3, dynamic viscosity 0.0035 Pa s.

| Condition | Flow (L/min) | Flow (m3/s) | Pump speed (rpm) | Angular speed (rad/s) | Inlet turbulence intensity (%) |
| --- | ---: | ---: | ---: | ---: | ---: |
| C1 | 2.5 | 4.16667e-5 | 2500 | 261.799 | 4 |
| C2 | 2.5 | 4.16667e-5 | 3500 | 366.519 | 4 |
| C3 | 4.5 | 7.50000e-5 | 3500 | 366.519 | 5 |
| C4 | 6.0 | 1.00000e-4 | 2500 | 261.799 | 7 |
| C5 | 6.0 | 1.00000e-4 | 3500 | 366.519 | 7 |
| C6 | 7.0 | 1.16667e-4 | 3500 | 366.519 | 7 |

Pump Reynolds number = rho Omega D^2 / mu with D = 0.052 m (C5: 293073). Steady simulations run with one rotor blade 90
degrees to the outlet (the CAD orientation).
