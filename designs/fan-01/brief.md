# fan-01 — assembly brief

## 1. Intent and configuration

FAN-01 low-pressure axial fan (EAA benchmark fan N1UG) analysed from its supplied CAD in the rig frame. The nine-blade rotor
turns about +y through (x, z) = (-400, 1515) inside the stationary duct (inlet nozzle, Ø500 bore, diffuser). The shaft and the
downstream hub disc turn with the rotor. The derived stationary flow boundary is the chamber wall at the diffuser start and
the hub closure plugging the rotor web's bore. The derived air body runs from a chamber-side settling region through the duct to
an ambient-side discharge region, between an inlet cap and an outlet cap. A steady OpenFOAM MRF analysis predicts the
total-to-static pressure rise at 0.994, 1.403 and 1.804 m3/s and the rotor torque at 1.403 m3/s, all at 1486 rpm, with a
mesh-refinement pair at the design flow. Authoritative sources: `fan01-packet.md` and the four STEP files. Figure 1 is
illustrative.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/fan01-packet.md | text | authoritative | 6aca0573ce272e5a183a7ce4532700154e7fa6e5e642f544c1a768f277a30fa6 | set-up, design table, CAD description |
| sources/fan-duct.step | cad | authoritative | 9b70daad9041bb6d47d6d276d23de0b4747d370e0bae2ea5dd6442fad57b0f74 | duct, nozzle, diffuser (rig frame, mm) |
| sources/fan-rotor.step | cad | authoritative | 6a526e10e9e1f9634d9eee157ad6b9758669141a03354609033ca3fac681932c | rotor ring and nine blades |
| sources/fan-shaft.step | cad | authoritative | 8a2716709cddba77254aad4885ba238d406cdb7de0a71ce4ec5b245e8e5eb426 | drive shaft |
| sources/fan-hub.step | cad | authoritative | 0b291d0c414b1ad6af321f45edcadaa7e23a332ad35a8247a00f859771da80c4 | Ø170 hub disc |
| sources/figure-1-setup.png | image | illustrative | 23729299c2297dd027068d32f3bd8e59cbc03eb44b7a608863951488d5ce7ec6 | chamber wall position, schematic |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| duct | purchased (catalog STEP) | | not stated | fan-duct.step | datum part; y -510..-136, bore r 250, outer r up to 325; volume 3.482e6 mm3 |
| rotor | purchased (catalog STEP) | | not stated | fan-rotor.step | y -421..-306, tip r 247.5, web bore r 89.7 (y -410.6..-404.5), rim r 121..125; 1.173e6 mm3 |
| shaft | purchased (catalog STEP) | | not stated | fan-shaft.step | solid stepped shaft y -404.5..-114, r 20 to 7.5 |
| hubDisc | purchased (catalog STEP) | | not stated | fan-hub.step | Ø170, y -193..-133; 4.00e5 mm3; does not overlap the shaft |
| chamberWall | derived (solid) | | | figure 1, packet | slab y -259..-159 across the fluid box, hole on the diffuser's outer cone |
| hubClosure | derived (solid) | | | packet (ring bore) | plug r <= 89.7, y -410.6..-404.5 |
| air | derived (fluid) | | air | intent | box minus every solid, one connected solid |

The four supplied bodies are used unchanged (analysis mode). Every body's own frame is the rig frame.

## 4. Frames, joints and motion

The assembly frame is the rig CAD frame (mm). The fan axis runs along +y through x = -400, z = 1515, and the flow goes from
-y (test chamber) to +y (ambient). Every body, derived or supplied, is described in this frame, so every placement is the
identity.

- `rotorSpin`: revolute, duct → rotor. Both frames sit at (-400, -363.5, 1515) with axis +y, offset 0. Motor drive with
  `case_value: speedRpm` (1486 rpm), positive about +y. The packet says the rotor turns clockwise seen from the suction side,
  which is positive about +y. The measured blade stagger agrees: at r 185 the leading edge (y -373.5) sits 16.6° ahead of the
  trailing edge (y -341.3) in the +y rotation sense on all nine blades.
- `shaftOnRotor` and `hubDiscOnRotor`: rigid, rotor → shaft and rotor → hubDisc. Frames at (-400, -363.5, 1515), axis +y,
  ref +x.
- `chamberWallFixed`, `hubClosureFixed` and `airFixed`: rigid on the duct, with identity frames on the axis.
- No transmissions. The acceptance motion `spin` sweeps one blade pitch (0..40°) and checks the tip gap (2.5 mm stated,
  minimum 2.0).

## 5. Fluid regions and named boundaries

The air region is the box x -1150..350, y -1260..864, z 765..2265 minus the duct, chamberWall, rotor, shaft, hubDisc and
hubClosure. Only the connected solid containing the seed (-388.9, -902.7, 1526.3) is kept. That drops the air pocket that the
wall closes in the downstream flange groove, if one exists.

- Settling region (chamber side): from y -1260 to the chamber wall's upstream face at y -259, around and upstream of the
  nozzle.
- Duct interior: from the nozzle lip at -510 to the diffuser exit at -136.
- Discharge region (ambient side): from the wall's downstream face at y -159 to y 864.
- Caps: `inletCap` at y -1260 (normal -y) and `outletCap` at y 864 (normal +y). Four side planes also close the box:
  x -1150 and x 350, z 765 and z 2265, each with an outward normal.
- Walls for the region derivation are duct, chamberWall and hubClosure; the rotor, shaft and hubDisc are subtracted.
- Volume band: the 1500 × 1500 × 2124 box is 4.779e9 mm3. The chamber wall takes 2.034e8 of that (a 2.25e8 slab minus a
  2.16e7 cone hole), and the measured supplied bodies plus the closure take 5.5e6. The expected fluid volume is 4.570e9 mm3
  (±3 %), with a Hausdorff limit of 5 mm.

Boundaries on `air`:

- `inlet` is the plane y -1260 (area 2.25e6 mm2) and `outlet` is the plane y 864 (2.25e6 mm2).
- Rotating walls `rotorWall`, `shaftWall` and `hubDiscWall` select the faces touching each rotating body.
- Stationary walls `ductWall`, `chamberWallFaces` and `hubClosureWall` select the faces touching those bodies. `sideWalls`
  takes the rest, which is the four box side planes.

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| q1403 flowM3s / flowLMin | 1.403 / 84180 | m3/s / L/min | stated | case named in the checks; L/min = m3/s × 60000 for the adapter |
| q1804 flowM3s / flowLMin | 1.804 / 108240 | m3/s / L/min | stated | case named in the checks |
| q0994 flowM3s / flowLMin | 0.994 / 59640 | m3/s / L/min | stated | case named in the checks |
| speedRpm (all cases) | 1486 | rpm | stated | fan01-packet.md Table 2 |
| fluidDensity | 1.204 ± 0.03 | kg/m3 | inferred | air at 20 °C, 101.325 kPa; tip Mach 0.113 at 38.9 m/s gives a = 344 m/s |
| fluidViscosity | 1.813e-5 ± 3e-7 | Pa s | inferred | air at 20 °C; tip Re 1.50e5, 38.9 m/s, 58 mm chord gives nu = 1.50e-5 m2/s |
| inlet_turbulence_pct | 5 | % | defaulted | adapter default; not stated |
| inlet_diameter_mm | 1692.6 | mm | derived | equal-area diameter of the 1500 × 1500 inlet cap |
| mesh | cell 25, surface level 3, refinement 1.0 / 0.7 | mm | defaulted | pair at the design flow |

The observables are:

- `dpts_q1403`, `dpts_q1804` and `dpts_q0994`: `pressure_rise_total_to_static` in Pa, steady. This is ambient static minus
  chamber total pressure (ISO 5801).
- `torque_q1403`: torque in N m, steady. It is the driving torque the rotating walls absorb about the axis.

`mrfDesign` (openfoam, cfd_steady) runs case q1403 with refinement [1.0, 0.7]. `mrfOffDesign` runs q1804 and q0994 on the
level 1.0 mesh. Both use bodies [air, rotor] and flow_key flowLMin, speed_key speedRpm. The packet's design values (1.4 m3/s,
150 Pa) are not requirements, so no min, max or expected value is set.

## 7. Defaults, open questions and unrepresentable features

- Air properties are not stated. The values used are inferred from the packet's Mach and Reynolds numbers (20 °C air).
- The chamber wall's thickness and exact position are not in the CAD. It is a 100 mm slab from the diffuser start; figure 1 is
  schematic and shows about 130 mm.
- The chamber and ambient sizes are not stated. The fluid box extends 1.5 D from the axis, 750 mm upstream of the nozzle lip and
  1000 mm downstream of the diffuser exit, with no-slip side walls. The ambient far field is a wall because the adapter reads
  only the inlet, outlet, rotating_wall and wall roles.
- The intent makes the hub closure stationary. Physically, the hub the ring mounts on turns with the rotor. The closure exposes
  only two discs of r <= 89.7, so the effect on torque is below 0.01 N m.
- The rotor's hub cup (inside the rim r 121, y -404.5..-306) stays open downstream and is fluid, because the CAD has no rear hub
  plate.
- The inlet turbulence intensity is the 5 % default.
- The flange-rim notches and the stand, motor and torque meter are absent from the supplied CAD.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft | drafted | contract and brief from the packet and measured STEP bodies |
