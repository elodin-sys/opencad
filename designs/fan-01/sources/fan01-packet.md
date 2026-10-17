# FAN-01 low-pressure axial fan (EAA benchmark, fan N1UG): reference packet

Transcribed from the FAN-01 benchmark (Zenodo; Zenger et al. 2016 SAE 2016-01-1805; Schoder and Czwielong 2022,
arXiv:2211.12014) and the dataset's measurement document `LA_Case4_AxialFan_measurements.pdf`: set-up, design parameters and
the published CAD. No measured results are included.

## Test set-up

- Standardised inlet test chamber to ISO 5801 (anechoic). The fan draws air from the test chamber and discharges to ambient
  through a short duct: an inlet nozzle (bellmouth) on the suction side, the Ø500 mm duct around the rotor and a diffuser on
  the pressure side, mounted through the chamber wall (`figure-1-setup.png`; 390 mm from the nozzle lip to the diffuser exit).
- The operating point is set with a butterfly damper or an auxiliary fan; the volumetric flow is measured with a standardised
  bellmouth inlet upstream of the chamber. The fan's total-to-static pressure difference is ambient static pressure minus
  the chamber pressure (air at rest in the chamber).
- The fan is driven by a motor outside the duct (ambient side); torque and speed are measured with a precision torque meter
  on the shaft between them. The rotation is clockwise as seen from the suction side in the LDA figures.

## Fan design parameters (Schoder and Czwielong 2022, Table 2, after Zenger et al. 2016)

| Parameter | Value |
| --- | --- |
| Fan diameter | 495 mm |
| Hub diameter | 248 mm |
| Tip clearance | 2.5 mm |
| Blades | 9, NACA 4510 profiles, zero skew |
| Design volumetric flow | 1.4 m3/s |
| Design total-to-static pressure difference | 150 Pa |
| Rotational speed | 1486 1/min |
| Circumferential velocity hub / tip | 19.4 / 38.9 m/s |
| Chord length hub / tip | 103 / 58 mm |
| Reynolds number hub / tip | 1.25e5 / 1.50e5 |

The tip Mach number is 0.113, so the flow is incompressible. Air properties are not stated.

## CAD (sources/)

The benchmark's `cad_model.igs` (Solid Edge, millimetres) models the whole rig as untrimmed surfaces. Sewn at 0.05 mm it
closes into 32 shells; four are supplied here as valid STEP solids in the rig's own frame (mm), all on one axis along +y
through (x, z) = (-400, 1515):

- `fan-rotor.step`: the rotor ring and nine blades, y -421..-306, tip radius 247.5 mm, inner radius 89.7 mm (the ring
  mounts on the hub; nothing of the rotor lies inside r 89.7 in the CAD).
- `fan-duct.step`: the duct with the inlet nozzle (suction side, toward -y) and the diffuser (toward +y), y -510..-136,
  one axisymmetric solid: nozzle lip flange y -510..-505 (r 298..325) and a bellmouth down to the bore; bore radius 250 mm
  from the nozzle to the diffuser (2 mm wall, outer radius 252, between the flanges), so the rotor tip gap is 2.5 mm;
  flanges y -455..-442 and -272..-259 (rings to r 275 and r 285..295 either side of a plate at y -450..-447 and
  -267..-264 that spans r 250..295); straight-cone diffuser from y -259 (bore 250) to y -136 (bore 275, outer 277). The
  IGES models the nozzle, the plates, the rotor duct and the diffuser as touching parts; their sewn shell is not a valid
  solid, so this one is their union rebuilt as the revolution of the published section (the flow surfaces are the IGES
  surfaces; the notches in the outer flange rims are not reproduced).
- `fan-shaft.step`: the drive shaft, radius 20 mm (15 mm bore), y -404.5..-114 (the sewn shell was inside-out; re-oriented).
- `fan-hub.step`: a Ø170 disc on the shaft downstream of the rotor, y -193..-133.

Air flows from -y (test chamber) to +y (ambient). The stand, frame, motor and torque-meter shells of the rig CAD are not
supplied, and the chamber wall is not in the CAD: figure 1 places it where the diffuser begins, separating the chamber side
from ambient, so the duct is the only passage between them.
