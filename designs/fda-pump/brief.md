# fda-pump — assembly brief

## 1. Intent and configuration

Analysis of the FDA benchmark centrifugal blood pump (Interlaboratory Study 2) from its supplied CAD. The supplied housing
chamber model (the inner surface of the chamber and tubing) and rotor are authoritative. Both are in GAMBIT units of
100 um and are scaled by 0.1 to millimetres; they keep their supplied relative position, and the rotor turns about the pump
axis on a revolute joint at the CAD rest phase (blades along +-x and +-y, one blade 90 degrees to the outlet axis). The
assembly source builds a physical housing wall around the chamber model (derived solid) and the sealed blood-analog flow
region, chamber minus rotor (derived fluid), and names the inlet, outlet, rotor wall and housing wall. All six packet
conditions C1-C6 matter. The static pressure rise outlet minus inlet is predicted at each with a steady OpenFOAM MRF
analysis (two mesh levels at C5, one elsewhere), and a reduced Euler-head estimate is given at each under separate ids.
Nonclinical engineering use only.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/fda-pump-packet.md | text | authoritative | 793748e01192fdbe2aa3c7c6f85d91bb6024efde62638bb466bc955d52a95377 | geometry, clearances, probes, fluid, conditions C1-C6 (FDA OSEL-DAM commit ca35ecc4) |
| sources/pump_housing.step | cad | authoritative | c9cd9061f29473aa48cf422703992bb47675972ee91eaf048a5254fbc283d447 | chamber inner-surface model, 1 unit = 100 um; one solid, 20 faces |
| sources/pump_rotor.step | cad | authoritative | fa7a064cb1ed1475b7a09f6094579177e996403dd24c4f10875b879f4f7e40c8 | rotor at its position, 1 unit = 100 um; one solid, 157 faces |
| sources/coordinate_system.png | drawing | authoritative | fe11693f1ad0779ddbac38994541223399dff388a23fc52b0137366d31dc4245 | x up to the outlet, z along the inlet tube, y right-handed |
| sources/front_view_with_dimensions.png | drawing | authoritative | f66eb511075ec0f7f5bc3430879ab2908690214e480c3e654cfe5e3c9bbaaaf7 | D60 chamber, D12 tubes, D4.39 throat, 0.02 / 0.02154 m, 20 deg diffuser |
| sources/side_view_with_dimensions.png | drawing | authoritative | ac754287f16c8479930d17e33e377c077629d438f69cdd1092d34a86d49dd28d | R90 inlet bend, 0.204 m straight tube, 0.009 m width, R5 fillet |
| sources/outlet_tube_detail.png | drawing | authoritative | f49aa7536314378cf0b49636f4303525f87396a9219ced30afe6e7dbb4c2e49f | cutwater 0.01562 m above the axis, 40 um fillet, 0.24 mm throat offset |
| sources/housing_rotor_clearance.png | image | illustrative | 36b979f9dd5fa87ce29410fe676d5afd8ab4e7e84cd76ba246eeed460ad2f98f | section render: rotor, hub nose in the inlet, gaps |
| sources/pump_and_rotor_iso.png | image | illustrative | 29b102d2816a726816feb51686762d7d17f7839e0c38ed345666d65c2fe7ecd9 | isometric render of the chamber model |
| sources/pump_experimental_setup.png | image | illustrative | eec0038ded8d1c5eeec7cfa58ef3cef013abd31b82d66bdf812e8e379d486b1b | flow loop; probes 0.175 m and 0.245 m |

Measured on the supplied STEPs (OpenCascade, scaled by 0.1):

- **Chamber:** volume 88098.1 mm3, bbox [-30, -33.8, 0] .. [245, 30, 300].
- **Rotor:** volume 9768.3 mm3, bbox [-26, -26, 0] .. [26, 26, 19].
- **Rotor inside the chamber:** the common volume is 9768.3 mm3, so the rotor lies fully inside.
- **Chamber minus rotor:** one solid of 78329.9 mm3.
- **End faces:** the inlet end face (90, 0, 294) and the outlet end face (245, -27.8, 6.563) are both planar discs of 113.10 mm2 with normal +x.

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| housing | derived (solid, datum) | — | not stated | built from the chamber model | chamber grown outward 3 mm minus the chamber; closed at the back, open flush at x = 90 (inlet) and x = 245 (outlet) |
| rotor | purchased (catalog STEP, solid) | — | not stated | sources/pump_rotor.step x 0.1 | D52 disc z = 1..5, four 3 x 3 radial blades z = 5..8 from r = 7.5 to 26, D8 hub z = 5..15 with a spherical nose to z = 19, D3.2 shaft stub z = 0..1 |
| chamber | purchased (catalog STEP, construction) | — | — | sources/pump_housing.step x 0.1 | flow-region model; staged only to build housing and blood; never placed or exported |
| blood | derived (fluid) | — | blood analog, 1035 kg/m3, 0.0035 Pa s | chamber minus rotor | sealed by the chamber's own end faces; 78329.9 mm3 |

## 4. Frames, joints and motion

**Assembly frame** (the housing's frame, identical to the supplied CAD frame scaled to mm):

- **Origin:** the pump axis on the chamber's inner back face.
- **x:** along the outlet tube axis toward the outlet.
- **y:** completes a right-handed frame; the outlet throat is at y = -27.8.
- **z:** the pump axis, from the back face toward the inlet tube.

Datums: A is the back face z = 0; B is the axis x = y = 0; C is the outlet end plane x = 245; D is the inlet end plane x = 90.

Geometry in this frame:

- **Chamber:** D60 drum z = 0..9 with an R5 fillet into the D12 straight inlet tube (z = 14..204).
- **Inlet bend:** R90 about (90, 0, 204), ending at the inlet end plane x = 90 (centre z = 294).
- **Throat:** D4.39 along x = 0.4..20 on y = -27.8, z = 6.563. It is tangent to the chamber at y = -30, 0.24 mm inside the front face z = 9.
- **Cutwater:** at x = 15.62 with a 40 um fillet.
- **Diffuser and outlet tube:** a 20 deg diffuser over x = 20..41.54, then the D12 outlet tube to x = 245.

**Rotor own frame** is the scaled CAD frame (axis +z through the origin, shaft end face z = 0), so its rest placement is the
identity.

| joint | kind | parent -> child | parent frame | child frame | rest | drive |
|---|---|---|---|---|---|---|
| rotorSpin | revolute | housing -> rotor | origin (0,0,0), axis +z, ref +x | origin (0,0,0), axis +z, ref +x | offset 0, angle 0 (CAD phase: +x blade along housing +x) | motor, per case `speedRpm`, positive about +z |
| bloodFixed | rigid | housing -> blood | origin (0,0,0), axis +z, ref +x | same | identity | — |

**Rotation sense.** The rotor turns counter-clockwise seen from the inlet (+z). This is inferred: at the throat
(y = -27.8) the flow must travel +x into the outlet. There are no transmissions; the rotor is driven directly by the motor.

**Acceptance.**

- **spin motion:** sweeps rotorSpin through 0..90 deg in 12 steps, one blade pitch past the cutwater. It checks only the rotor-housing pair, because the blood body is rest-phase geometry.
- **rotorInHousing clearance:** requires no interference (min_gap 0). The shaft stub end face lies on the back face z = 0 by design; every other rotor face is at least 1 mm from the housing (1 mm axial, 4 mm at the rim).
- **Solid count:** 3 (housing, rotor, blood).

## 5. Fluid regions and named boundaries

**Fluid region `blood`.**

- **Construction:** chamber model minus the rotor at rest, built in the assembly source.
- **Evaluator check:** walls [housing], minus [rotor].
- **Caps:**
  - inletCap at (90, 0, 294), outward normal +x (flow enters along -x).
  - outletCap at (245, -27.8, 6.563), outward normal +x.
- **Seed:** (0, 0, 100), on the straight inlet tube axis. It is 6 mm from the wall and 81 mm from the rotor nose.
- **Volume band:** 78329.9 mm3 +- 1 % (chamber 88098.1 minus rotor 9768.3); hausdorff_max 0.1 mm against the evaluator-derived region.
- **Cap semantics:** the inlet cap plane x = 90 also crosses the outlet tube (x = 41.5..245). The caps must close only their own openings; they are not half-space cuts.

**Named boundaries** on `blood`, in the assembly frame at rest:

| name | role | selector | notes |
|---|---|---|---|
| inlet | inlet | plane (90, 0, 294), normal +x | D12 open end of the curved inlet tube, 113.10 mm2 |
| outlet | outlet | plane (245, -27.8, 6.563), normal +x | D12 open end of the outlet tube at the outlet probe height, 113.10 mm2 |
| rotorWall | rotating_wall | touching rotor | disc, blades, hub, nose and shaft stub |
| housingWall | wall | rest | chamber, fillet, tubes, throat, cutwater, diffuser |

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| C1 flowLMin / speedRpm / inletTurbulencePct | 2.5 / 2500 / 4 | L/min / rpm / % | stated | packet, Simulation conditions table (held_out) |
| C2 | 2.5 / 3500 / 4 | L/min / rpm / % | stated | same (held_out) |
| C3 | 4.5 / 3500 / 5 | L/min / rpm / % | stated | same (held_out) |
| C4 | 6.0 / 2500 / 7 | L/min / rpm / % | stated | same (held_out) |
| C5 | 6.0 / 3500 / 7 | L/min / rpm / % | stated | same (development; mesh-refinement case) |
| C6 | 7.0 / 3500 / 7 | L/min / rpm / % | stated | same (held_out) |
| fluidDensity | 1035 | kg/m3 | stated | packet, Newtonian blood analog |
| fluidViscosity | 0.0035 | Pa s | stated | packet, dynamic viscosity |
| inlet_diameter_mm | 12.0 | mm | stated | packet, inlet tube inner diameter |
| bladeCount | 4 | — | stated | packet, four blades at 90 degrees |
| bladeOutletAngle | 90 | deg | measured (reference model) | rotor STEP: straight radial blades |
| bladeOutletWidth | 3.0 | mm | stated | packet 0.003 m blade height; CAD z = 5..8 |
| hydraulicEfficiency | 0.65 +- 0.10 | — | inferred | small low-specific-speed radial-blade pump (n_q about 12); textbook 0.55-0.75; not tuned |
| cell_mm / refinement | 0.6 / [1.0, 0.7] at C5 | mm / — | defaulted | numerical choice; about 2 cells across the 1 mm gaps at the base level |
| iterations / processes | 1500 / 8 | — | defaulted | numerical choice (12-core host) |
| housingWallThickness | 3.0 | mm | inferred | sources give only the fluid surface; does not affect the flow region |
| inlet probe / outlet probe | (0, 0, 175) / x = 245 | mm | stated | packet, Experimental setup |

**Observables.** All are `pressure_rise` in Pa with `steady` averaging, taken as the static-pressure outlet patch average
minus the inlet patch average, with no hydrostatic component (the analysis runs without gravity).

- **pressureRiseC1..C4 and C6:** predicted by simulation `cfd`.
- **pressureRiseC5:** predicted by `cfdC5`, which runs two mesh levels.
- **eulerPressureRiseC1..C6:** predicted by `euler`, the reduced Euler-head estimate for comparison with the CFD values.

**Simulations.**

- **cfdC5** (cfd_steady, openfoam) runs on bodies [blood, rotor] at C5 with refinement [1.0, 0.7].
- **cfd** (cfd_steady, openfoam) runs on [blood, rotor] at C1, C2, C3, C4 and C6, one mesh level.
  - Both CFD runs use steady MRF simpleFoam with k-omega SST, at the frozen CAD rotor phase, with settings flow_key `flowLMin` and speed_key `speedRpm`.
  - For reference, the pump Reynolds number at C5 is rho Omega D^2 / mu = 2.93e5 (packet).
- **euler** (reduced:pump_euler) runs on [rotor] at C1-C6; the tip radius of 26 mm comes from the placed rotor.

## 7. Defaults, open questions and unrepresentable features

- **Rotation sense:** not stated in the sources. Positive speed about +z (counter-clockwise seen from the inlet) is inferred from the volute: the throat is tangent at y = -30 and leaves toward +x.
- **Inlet patch versus probe:** the inlet patch is the curved tube's open end (x = 90), but the rig's inlet probe sits downstream of it on the straight tube at (0, 0, 175).
  - The patch-average pressure rise therefore omits the tube loss between the patch and the probe, estimated at 0.1-0.3 kPa at 6-7 L/min.
  - The outlet patch coincides with the outlet probe height (x = 245).
  - The contract cannot place the inlet boundary at the probe while also naming the tube's open end as the inlet.
- **Inlet turbulence:** the per-case intensity (4, 5, 7 %) is recorded as `inletTurbulencePct`. The openfoam adapter names no key for it and may apply its own inlet turbulence.
- **Not in the sources:** housing wall thickness (3 mm, inferred) and the housing and rotor materials. None affects the flow region or the pressure-rise predictions.
- **Shaft stub:** the rotor's D3.2 stub ends flush on the chamber back face as supplied; in the rig it passes through a seal. The housing wall is closed there, so the rotor-housing gap is zero at that face (min_gap 0).
- **Euler estimate:** hydraulicEfficiency 0.65 +- 0.10 is inferred, not stated.
- **Mesh and turbulence model:**
  - The mesh settings are numerical choices.
  - The tube Reynolds numbers (about 1300-3600) are transitional, while the adapter runs k-omega SST everywhere.
  - The MRF zone extent (the rotor sweep r <= 26, z = 1..8, plus the hub nose in the inlet tube) is the adapter's choice.
- **Unrepresentable:** the rim's polishing curve and the 40 um cutwater fillet live only in the supplied CAD. The steady analysis represents the rotor at one phase only (the CAD phase).

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft | drafted | contract and brief from the packet and the measured supplied STEPs; `assembly check` run before hand-back |
