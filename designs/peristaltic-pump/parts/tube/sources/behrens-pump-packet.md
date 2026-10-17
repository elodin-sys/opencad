# Open-source 3D-printed peristaltic pump: reference packet

Behrens, Fuller, Swist et al., *Open-source, 3D-printed Peristaltic Pumps for Small Volume Point-of-Care Liquid Handling*,
Scientific Reports 10, 1543 (2020), doi:10.1038/s41598-020-58246-6, CC BY 4.0. Printable parts from the publisher's
Dataset 1 (`41598_2020_58246_MOESM2_ESM.zip`), converted from STL to STEP solids for this case without rescaling.

## Design (from the paper)

The pump operates by peristaltic action of rolling ball bearings applying pressure to the outside of small-diameter
silicone tubing. It is modular: different tubing diameters are accepted by swapping 3D-printed parts. A stepper motor
drives the pump rotor through a 3D-printed 4:1 gearbox (to increase the available torque); an Arduino and an EasyDriver
set the rotation speed and direction. The mechanical pump is ABS parts plus basic hardware; the pump mounts on top of
the gearbox. Two tube sizes were tested, each with its own stator: 1.59 mm OD / 0.79 mm ID and 3 mm OD / 1 mm ID
silicone tubing, durometer 50 A (designed for peristaltic pumps). Rotation speed was set up to about 108 rpm, the
practical limit set by friction from manufacturing tolerances. The complete bill of materials and assembly slides are in
the paper's supplement (not included here).

## Test condition used by this case

The 3 mm OD / 1 mm ID tubing with its stator (`6.1-peristaltic-pump-stator-3mm`) and lid (`7.1-peristaltic-pump-lid-3mm`),
deionized water at room temperature, rotor speed 108 rpm, free outlet (no backpressure).

## Part files (sources/)

| file | part |
| --- | --- |
| 9-peristaltic-pump-rotor.step | pump rotor; carries the three ball-bearing rollers on pins |
| 6.1-peristaltic-pump-stator-3mm.step | stator for the 3 mm tube: the bore the rollers roll in, with the tube slots |
| 7.1-peristaltic-pump-lid-3mm.step | lid for the 3 mm tube |
| 8-peristaltic-pump-clamp.step | tube clamp |
| 2-small-gear-with-shelf.step | gearbox gear on the motor shaft |
| 3-stacked-gear.step | gearbox compound (stacked) gear |
| 5-large-gear.step | gearbox output gear, drives the rotor |
| 1-gear-box-base.step | gearbox base; mounts on the stepper motor |
| 4-gear-box-upper-case.step | gearbox upper case; the pump mounts on it |

Units: the part files keep the published STL units. Check them against the stated tubing sizes and a NEMA 17 stepper
(42.3 mm square face, 31 mm bolt spacing, 5 mm shaft) before placing anything. The ball bearings and the stepper motor
are purchased parts whose size the files imply (bearing bore = the rotor pin, bearing OD from the stator track clearance).
