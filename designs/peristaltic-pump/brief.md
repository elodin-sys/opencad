# peristaltic-pump — assembly brief

## 1. Intent and configuration

Open-source 3D-printed peristaltic pump (Behrens, Fuller, Swist et al., Sci. Rep. 10, 1543, 2020, CC BY 4.0), assembled in
analysis mode from the publisher's printed parts: the STEP files under `sources/` are the reference geometry and are placed as
purchased bodies at scale 10 (the STL units are centimetres: the base's NEMA 17 bolt square measures 3.1 x 3.1 file units = 31 mm).
A NEMA 17 stepper under the gearbox base drives a reverted 4:1 spur train (12 -> 24, 12 -> 24) whose output gear is coaxial with the
motor and turns the pump rotor. Three ball-bearing rollers on the rotor's pins squeeze a 3 mm OD / 1 mm ID silicone tube against
the track of the 3 mm stator (6.1), closed by its lid (7.1) with the tube clamp (8) on the inlet side. The one operating case is the
packet's test condition: rotor 108 rpm, deionized water at room temperature, free outlet. Predictions: the delivered flow
(`flowRate`, reduced peristaltic displacement model) and the motor-to-rotor drive ratio (`driveRatio`, measured from the placed geometry).
`sources/behrens-pump-packet.md` is authoritative for the design and test condition; the STEP files are authoritative for geometry.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| behrens-pump-packet.md | text | authoritative | bdab3462725e9554f44290ad423461456b135361fc6bab52adb83e5a7b961bae | design, tube sizes, 4:1 gearbox, 108 rpm test condition |
| 1-gear-box-base.step | cad | authoritative | d63eaba9c1df2347b1a3cc5805a3f3ed12b02543237d9153ffa7a46b2dab9288 | faceted, cm; datum |
| 2-small-gear-with-shelf.step | cad | authoritative | 943cf69986d0810e5d4dd4b4f1307508561b4f0620361e9e163c47bf6ead20d7 | 12T motor gear, D5.1 bore |
| 3-stacked-gear.step | cad | authoritative | 971d50c72c09b05d80cafb364090821e1777ec649e82339345000e8397d878dc | 24T + 12T compound gear |
| 4-gear-box-upper-case.step | cad | authoritative | 41f6a78782749909ac611119009a52841b0666f8ea1c0d71bf764aec6700fa3d | pump seat on top |
| 5-large-gear.step | cad | authoritative | 47a710ed206130d114428870aeb2fa7ac577d3ae4f2cbba6491e986152cc01a3 | 24T output gear |
| 6.1-peristaltic-pump-stator-3mm.step | cad | authoritative | 6b531c2802d6d9605d8659b4cf54d25659df54942c976bdcff04cbbd7672bd16 | track R12.17 |
| 7.1-peristaltic-pump-lid-3mm.step | cad | authoritative | a1a12d25456202fc4cc002c5363d7d1b463c31409ec005a6697ce4d167095c82 | lid, R10.8 tube lip |
| 8-peristaltic-pump-clamp.step | cad | authoritative | f948d46506a753fc7d160b323e1d5971ae638f2004d152bb3e3ec31e09f24994 | clamp, holes 22.3 apart |
| 9-peristaltic-pump-rotor.step | cad | authoritative | 996c2325ecae541f8a0b060d69add927e81f9233b26cdd3ddab105f1a90e562f | three D3 pins on R5.77 |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| base | purchased (step x10) | | ABS | 1-gear-box-base.step | datum; motor face y = 0, top face y = 12 |
| motor | purchased (box) | | steel | packet (NEMA 17) | 42.3 x 42.3 x 40, D5 shaft (not a body) |
| motorGear | purchased (step x10) | | ABS | 2-small-gear-with-shelf.step | 12T, tip D23.64, face 5.5, shelf z 9..11 |
| stackedGear | purchased (step x10) | | ABS | 3-stacked-gear.step | 24T z 0..9.5 (tip D43.06), 12T z 9.5..17 |
| outputGear | purchased (step x10) | | ABS | 5-large-gear.step | 24T, face 6, D6.1 bore |
| upperCase | purchased (step x10) | | ABS | 4-gear-box-upper-case.step | 31 tall, turned -90 deg on the base |
| stator | purchased (step x10) | | ABS | 6.1-peristaltic-pump-stator-3mm.step | block y 0..21 with track R12.17; raised -x half + tube ear to y 37 |
| lid | purchased (step x10) | | ABS | 7.1-peristaltic-pump-lid-3mm.step | half plate on the block's +x half (y = 21), turned -90 deg; lip backs the tube |
| clamp | purchased (step x10) | | ABS | 8-peristaltic-pump-clamp.step | on the stator's -x face |
| rotor | purchased (step x10) | | ABS | 9-peristaltic-pump-rotor.step | rigid to the output gear; 4.2 mm bearing gap at y -1.42..2.77 |
| roller1..3 | purchased (cylinder) | | steel | inferred 623 bearing | 3 x 10 x 4 on the D3 pins |
| tube | modelled, compliant | peristaltic-pump-tube | silicone 50 A | packet | OD 3, ID 1, 180 deg arc R10.67 + two 30 mm legs |

## 4. Frames, joints and motion

Assembly frame = base file frame x 10: motor axis along +y at (x, z) = (-20.5, -20.5), motor face y = 0, base top y = 12; the
countershaft axis is (-20.5, -50.5), 30.0 mm from the motor axis. Gears have their axis on own +z through the origin with a
tooth centred on own +x (measured). The rotor axis is its own y through (-2.887, -5.0); the housing parts keep their file frames.

| joint | kind | parent -> child | parent frame (parent's own) | child frame (child's own) | rest | drive |
|---|---|---|---|---|---|---|
| motorMount | rigid | base -> motor | (-20.5, 0, -20.5), +y, ref +x | origin, +z, ref +x | | |
| motorSpin | revolute | motor -> motorGear | origin, +z | origin, +z | offset 12, angle 0 | motor, case `motorRpm` |
| stackedSpin | revolute | base -> stackedGear | (-20.5, 12, -50.5), +y | origin, +z | angle 7.5 (half a 24T pitch) | free (stage1) |
| outputSpin | revolute | base -> outputGear | (-20.5, 23, -20.5), +y | origin, +z | angle 3.75 | free (stage2) |
| upperCaseMount | rigid | base -> upperCase | (-20.5, 12, -20.5), +y, ref +z | (-15.5, 0, -30.5), +y, ref +x | -90 deg about y | |
| rotorDrive | rigid | outputGear -> rotor | (0, 0, 49.125), +z, ref +x | (-2.887, 0, -5), +y, ref +x | rotor y 66.1..78.9 | |
| statorMount | rigid | upperCase -> stator | (-15.5, 31, -30.5), +y | (-20.5, 0, -20.5), +y | bolt squares aligned | |
| lidMount | rigid | stator -> lid | (-20.5, 21, -20.5), +y, ref +z | (-20.5, 0, -20.5), +y, ref +x | -90 deg about y, lid y 64..78 | |
| clampMount | rigid | stator -> clamp | (-46, 30, -20.5), +y, ref +z | (-16.5, 0, -5), +y, ref +x | | |
| tubeSeat | rigid | stator -> tube | (-20.5, 29.8, -20.5), +y | origin, +z | tube mid-plane assembly y 72.8 | |
| roller1..3Pin | rigid | rotor -> rollerK | pins (0, 0.675, 0), (-8.66, 0.675, -5), (0, 0.675, -10), +y | origin, +z | roller mid-plane = tube mid-plane | |

Transmissions: `stage1` motorSpin -> stackedSpin ratio -0.5 (12/24), `stage2` stackedSpin -> outputSpin ratio -0.5 (12/24), both
spur meshes at 30 mm centres (mesh check over one 30 deg driver pitch). Motor to rotor = +0.25, the packet's 4:1 gearbox, same sense.
Motion `rollerPass`: motorSpin 0..1440 deg (one rotor revolution) in 48 steps, so every roller passes the whole 180 deg tube arc.

## 5. Fluid regions and named boundaries

No derived fluid body: the `reduced:peristaltic` model reads the tube diameters, the rollers and the stator track directly, so no
`fluid_volumes` or `boundaries` are declared. The flow observable is located at the tube outlet end, assembly (-31.17, 72.8, -50.5).

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| rotor108.rotorRpm | 108 | rpm | stated | packet, Test condition |
| rotor108.motorRpm | 432 | rpm | derived | rotorRpm / 0.25 |
| tubeInnerDiameter | 1.0 | mm | stated | packet, Design / Test condition |
| tubeOuterDiameter | 3.0 | mm | stated | packet, Design / Test condition |
| fluid | deionized water, room temperature, free outlet | | stated | packet, Test condition (not an input of the reduced model) |
| unitScale | 10 | | derived | 31 mm NEMA bolt spacing / 3.1 file units |
| trackRadius | 12.17 | mm | measured (reference model) | stator STEP circle fit |
| pinPitchRadius | 5.774 | mm | measured (reference model) | rotor STEP pin centres |
| roller OD | 10.0 | mm | inferred | 623 bearing (4 wide fits the 4.2 rotor gap) on the D3 pin; occlusion gap 1.40 vs a 2.0 double wall |
| observable flowRate | predict | mL/min | | simulation `peristaltic`, case rotor108, time-averaged |
| observable driveRatio | 0.25 expected | | derived | (12/24)(12/24); evaluator measures it, no simulation |

## 7. Defaults, open questions and unrepresentable features

- Bearing size inferred (623, 3 x 10 x 4): the rotor's 4.2 mm gap takes a 4 mm race, and a 693 (3 x 8 x 4) would leave 2.4 mm (no occlusion). The packet gives no BOM.
- Axial stack inferred from faces: gears on the base top y = 12, the output gear on the motor gear's shelf (y = 23), the stator and
  the half-plate lid on the stator block top (y = 21) turned -90 deg to back the +x half of the tube arc; the D6 output shaft and the countershaft pin are not in the part files and are not modelled (the rotor is rigid
  to the output gear).
- Tube mid-plane (stator y = 29.8) estimated from the ear slot floor (y 28.3..30) and the lid lip band (stator y 26.4..32.8); the lid lip
  (r 10.0..11.6) may make the effective track radius on the +x half smaller than 12.17. Stator orientation (0 deg of four) not stated.
- The motor gear's shelf may graze the stacked 24T tip at y 21..21.5; the assembly check decides.
- The NEMA 17 body length (40 mm) is a default. Roller outer-race spin is not tracked; roller-tube squeeze is intended.
- Not representable: tube compression (the tube is compliant and overlaps the rollers), slip and backflow in the reduced model.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft | drafted | contract and brief from the packet and STEP measurements (001-asm-draft) |
