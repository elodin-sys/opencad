# disc-brake — assembly brief

## 1. Intent and configuration

Rebuild of the COMSOL Multiphysics 6.3 Application Library model *Heat Generation in a Disc Brake* as a machine of two separately designed parts, in COMSOL's coordinates converted to millimetres. The half-thickness disc (radius 140, z = 0..13, symmetry plane z = 0) and its radius-80 hub (z = 13..23) turn about z on a revolute joint whose speed follows the car's braking history through the wheel radius. One pad, the fixed datum, rests on the disc face z = 13. The transcribed packet `sources/comsol-brake-disc-packet.md` is authoritative; the figures are illustrative. The documentation's results are evaluator-only and appear nowhere in this bundle.

There is one operating case, `panicBrake`: an 1,800 kg car at 25 m/s brakes at 10 m/s² from t = 2 s to 4 s, then rolls on at 5 m/s without braking to t = 12 s. A transient CalculiX thermal analysis (`friction_brake` source) predicts how hot the disc and pad get and how much they cool. The reduced `brake_energy` budget cross-checks its heat balance and peak temperature. The packet notes that braking power fades above 600 K; that is the only stated limit.

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/comsol-brake-disc-packet.md | text | authoritative | 85535fc3210d6d0174945725ecf1a1f29351991bc272ba55fc138b0ad254638d | Model definition, Table 1 materials, geometry construction (metres), physics settings, mesh/study, probe line; results excluded |
| sources/figure-1-geometry.png | image | illustrative | 8c7faad09a9d6663c0a39fe6e18e5e721807c6750bf3b40b7ab67f95a36f5c54 | Disc, raised hub on the same side as the pad, one pad near the rim on +y (axes 0.1 m ticks) |
| sources/figure-2-velocity.png | image | illustrative | 05a0b5ceb2f81378a47ef8ac2b41edbf948dfe3c0c3392cb62b1c0ef8c56ccc1 | v(t): 25 m/s to t ≈ 2 s, linear to 5 m/s at t ≈ 4 s, flat to 12 s; smoothed corners |
| sources/figure-3-acceleration.png | image | illustrative | bb3f0ef43eaca917061fb013edd68fece3342aebec4ef0244089d6216d71c2dd | a(t): 0, ramps to −10 m/s² over about 1.8–2.2 s, back to 0 over about 3.8–4.2 s |
| sources/figure-5-probe-line.png | image | illustrative | f3ffe42b7cc21121f49b80d52056b377c9aa4b90aec2d13ac0fbac1ecba5d0d5 | Red radial probe line from the axis to the rim through the pad's −x (trailing) end |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| disc | modelled | disc-brake-disc | disc material, ρ 7870 kg/m³ (iron-like) | packet steps 1–2, Table 1 | One solid: cylinder r 140, z 0..13, fused with hub cylinder r 80, z 13..23. Volume 1,001,540 mm³, mass 7.882 kg |
| pad | modelled | disc-brake-pad | pad friction material, ρ 2000 kg/m³ | packet steps 3–4, Table 1 | Four-Bézier outline in z = 13, extruded 6.5 to z = 19.5. Area 3,544.4 mm², volume 23,038.5 mm³, mass 0.046 kg |

Nothing is purchased and there is no fluid body: air enters only as a convection condition. The assembled mass is 7.928 kg with its centre of mass at (0, 0.65, 8.852) mm. Both are derived acceptance values.

## 4. Frames, joints and motion

**Assembly frame** = the pad's own frame = COMSOL's frame in mm. The origin is on the disc axis in the symmetry plane. +y runs from the axis through the pad centreline, +z runs from the symmetry plane toward the pad and hub, and x completes a right-handed frame (the pad's trailing edge is on −x). Datums: A is the symmetry plane z = 0, B the axis x = y = 0, C the rubbing face / pad seat z = 13, and D the pad mirror plane x = 0. The envelope at rest is [−140, −140, 0]..[140, 140, 23] (the disc and hub; the pad lies inside it).

**Disc frame**: rotation axis +z through the origin, symmetry face on z = 0. It coincides with the assembly frame at rest.

**Pad frame**: the assembly frame itself. The contact face is at z = 13 and the outline uses COMSOL's control points in mm (B1 and B4 are rational, with weight 2.5 on (±50, 130)). The outline is mirror-symmetric about x = 0 (B3 and B4 are B2 and B1 mirrored and reversed). It spans x ±44.69, y 88.03..135.00, r 90.00..135.23, and 69.1°..110.9° from +x.

**Joint `discSpin`** (revolute, parent pad, child disc):
- Frames: the parent frame is origin (0, 0, 0), axis +z in the pad frame; the child frame is origin (0, 0, 0), axis +z in the disc frame.
- Rest pose: offset 0 and no rest phase, since the disc is axisymmetric. There are no limits.
- Drive: a motor with speed history (0 s, 795.77 rpm), (2 s, 795.77), (4 s, 159.15), (12 s, 159.15). Disc speed = v / r_wheel. With r_wheel = 0.30 m (inferred): 25/0.3 = 83.33 rad/s = 795.77 rpm, and 5/0.3 = 16.67 rad/s = 159.15 rpm.
- Sense: positive is counter-clockwise about +z, as COMSOL's u_trans = (−y, x) v / r_wheel. Disc material under the pad therefore moves from the +x (leading) end to the −x (trailing) end.

There are no transmissions. For acceptance, `discRevolution` sweeps `discSpin` through 0..360° in 12 steps, and the pad–disc pair must interfere by no more than 1 mm³. The clearance `padSeated` holds pad against disc at gap 0..0.05 mm.

## 5. Fluid regions and named boundaries

There is no fluid region. The packet models air as external forced convection (flat plate, L = 0.14 m, U = v(t), T_air) plus surface-to-ambient radiation.

| boundary | role | body | selector | area (derived) | COMSOL |
|---|---|---|---|---|---|
| discContact | contact | disc | plane z = 13, normal +z, point (0, 111.9, 13) | 41,469 mm² (whole annulus r 80..140) | boundary 11, disc side |
| padContact | contact | pad | plane z = 13, normal −z, point (0, 111.9, 13) | 3,544.4 mm² | boundary 11, pad side |
| discSymmetry | symmetry | disc | plane z = 0, normal −z | 61,575.2 mm² | boundary 3, insulated |
| discFree | convection | disc | rest: rim r 140, hub side r 80, hub top z 23 | — | heat flux + radiation, ε 0.28 |
| padFree | convection | pad | rest: top z 19.5 and side walls | — | heat flux + radiation, ε 0.8 |

The probe line runs from (0, 0, 12.9) to (−47, 131.6, 12.9) mm: 139.74 mm long at 109.65° from +x, 0.1 mm under the rubbing face, along the pad's trailing end. It is attached to `lineMaxTemperature`.

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| case panicBrake: initialSpeed | 25 | m/s | stated | Scenario; v0 |
| case panicBrake: finalSpeed | 5 | m/s | derived | v0 − 10 × (4 − 2) |
| case panicBrake: deceleration | 10 | m/s² | stated | Scenario; a0 = −10 |
| case panicBrake: brakeStart / brakeEnd | 2 / 4 | s | stated | Global parameters |
| case panicBrake: endTime | 12 | s | stated | Physics settings v(t) to 12 s; output times 6:1:12 |
| vehicleMass | 1800 | kg | stated | Scenario; m_car |
| brakeCount | 8 | – | stated | P_b = P / 8 (eight pads; one pad per half disc) |
| disc.density / specificHeat / conductivity / emissivity | 7870 / 449 / 82 / 0.28 | kg/m³, J/(kg K), W/(m K), – | stated | Table 1 |
| pad.density / specificHeat / conductivity / emissivity | 2000 / 935 / 8.7 / 0.8 | kg/m³, J/(kg K), W/(m K), – | stated | Table 1 |
| airDensity / airSpecificHeat / airConductivity | 1.170 / 1100 / 0.026 | kg/m³, J/(kg K), W/(m K) | stated | Table 1 |
| convectionLength | 0.14 | m | stated | external forced convection L = 0.14 m, U = v(t) |
| frictionCoefficient | 0.3 | – | stated | mu; contact pressure p = Q_b / (mu v) |
| contactMicrohardness | 8.0e8 | Pa | stated | thermal contact Hc = 800 MPa |
| ambientTemperature | 300 ± 5 | K | inferred | T_air not stated; Table 1 air (ρ 1.170, k 0.026) is air at ≈ 300 K, 1 atm (101325 / (1.170 × 287.05) = 302 K) |
| initialTemperature | 300 ± 5 | K | derived | = ambientTemperature (packet: initial T = T_air) |
| airViscosity | 1.85e-5 ± 5e-7 | Pa s | inferred | not in Table 1; dry air at 300 K (Sutherland) |
| wheelRadius | 0.30 ± 0.05 | m | inferred | r_wheel not stated; tyre rolling radius of a car with a 280 mm disc on 15–17 in wheels |
| drive history | 795.77 → 159.15 | rpm | derived | v / wheelRadius × 60 / 2π |
| discHeatFraction | adapter default | – | defaulted | COMSOL's thermal friction uses Charron's partition by default, as does the adapter |

Observables at `panicBrake`. The first six are scored; the rest are unscored companions. Each is listed as id: quantity (unit, averaging), then what it covers:
- `peakDiscTemperature`: max_temperature (K, maximum). Disc body. `max: 600` is the packet's fade threshold.
- `lineMaxTemperature`: line_max_temperature (K, maximum). Along the probe line.
- `timeOfPeak`: time_of_max_temperature (s). Disc body.
- `producedHeat`: produced_heat (J, integral over 0..12 s). W_prod.
- `dissipatedHeat`: dissipated_heat (J, integral). W_diss, convective plus radiative loss over all external surfaces.
- `hotspotRadius`: hotspot_radius (mm). Disc body.
- `peakPadTemperature`: max_temperature (K). Pad body; the packet asks how hot the pads get.
- The `budget*` set (peak temperature, produced, stored and dissipated heat) comes from `brakeEnergy`.

Simulations:
- `brakeThermal` (calculix, thermal_transient). Settings: source friction_brake, disc/pad = disc/pad, end_time 12 s, time_step 0.05 s (the packet's finest output spacing, 1.55:0.05:3), mesh_size_mm 6, contact_mesh_size_mm 3, line_radius_mm 3. Refinement [1.0, 0.7] gives the numerical uncertainty. COMSOL itself used about 5,800 swept elements, two through the thickness.
- `brakeEnergy` (reduced:brake_energy). Same inputs, including wheelRadius.

Analytic sanity values (not results): P_b = m v |a| / 8 falls from 56,250 W at 2 s to 11,250 W at 4 s. The total friction heat of one brake is m (v0² − v1²) / 16 = 67,500 J. The bulk rise if all of it stayed in the half disc would be 67,500 / (7.882 × 449) ≈ 19 K.

## 7. Defaults, open questions and unrepresentable features

- **T_air** (ambient and initial) is not stated. 300 K is inferred from the Table 1 air state, u = 5 K. COMSOL's 293.15 K default is the alternative.
- **r_wheel** is not stated. 0.30 m is inferred, u = 0.05 m. It changes the disc speed and flash rise, not the heat input.
- **Air viscosity** is not given. 1.85e-5 Pa s is inferred.
- **Disc contact face.** The disc has one face at z = 13, so `discContact` is the whole annulus (41,469 mm²). In COMSOL, only the pad footprint (3,544.4 mm²) is in contact; the rest of that face convects and radiates. The selectors (plane, cylinder, region, touching) cannot isolate the swept track r 90.0..135.2 without imprinting the disc.
- **Contact conductance.** COMSOL's value (Hc = 800 MPa, p = Q_b/(mu v)) also needs roughness and asperity slope, which the packet omits. mu and Hc are recorded; whether the analyses model a finite contact conductance is unverified.
- **Velocity smoothing.** COMSOL smooths v(t) over a 0.2 s zone with a continuous second derivative. The piecewise-linear drive history cannot represent this; the heat input is unchanged because v still falls from 25 to 5 m/s.
- **Eulerian disc motion.** COMSOL models the disc's rotation as translational motion (an Eulerian field fixed under the pad). Here the disc is a rotating body; the adapters use a ring average plus a moving-source flash rise.
- **W_prod / W_diss scope.** The packet says "of the disc" but integrates Q_diss over all external surfaces, so whether these cover the disc alone or disc plus pad is ambiguous.
- **Mesh and solver settings.** COMSOL's element counts and tolerances (relative tolerance 0.005, intermediate stepping) are not transferable. The CalculiX settings above are chosen, not stated.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft (order 001) | drafted | assembly.yaml and brief written from the packet; `opencad assembly check` run before hand-back |
