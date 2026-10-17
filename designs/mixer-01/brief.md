# mixer-01 — assembly brief

## 1. Intent and configuration

Sealed magnetic-drive paddle mixer for water, from `sources/mixer-01-spec.md` (the only source, authoritative). Water enters
through an axial D12 inlet tube in the lid, a four-blade D40 paddle impeller spinning on a fixed D6 pin stirs it in a D50 x 25
cylindrical chamber, and it leaves through a radial D10 outlet tube in the side wall. A purchased D30 x 40 motor under the
floor turns the impeller through the floor by a magnetic coupling (not modelled), so no shaft crosses the wall and the water
space is sealed.

Four separate bodies, none fused: `housing` (modelled, polypropylene), `impeller` (modelled, acetal), `motor` (purchased
cylinder) and `water` (derived fluid region, built in the assembly source from the placed housing and impeller, capped at
the two port planes).

One operating case matters: `design` (impeller 1500 rpm, 2.0 L/min, inlet turbulence intensity 5 %). Predictions at it:
the static pressure rise (outlet minus inlet, area-averaged) and the impeller torque from a steady MRF CFD with a three-level
mesh study, an Euler-head estimate of the same pressure rise, and the water volume. Requirement: static pressure rise at
least 500 Pa (gated on the CFD prediction).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| sources/mixer-01-spec.md | text | authoritative | 7c08f09900a1078122226978351d2ff7878b3adda1dc49b70bada1a4dcf2a8a1 | frame, dimensions, placement, motion, fluid, operating point, requirement and predictions |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| housing | modelled | mixer-01-housing | polypropylene, 900 kg/m3 | spec Bodies, Dimensions | datum part, modelled in the assembly frame; chamber, lid, floor, both tubes and the pin in one solid; about 31076 mm3 (27.97 g) |
| impeller | modelled | mixer-01-impeller | acetal, 1410 kg/m3 | spec Bodies, Dimensions | D12 x 10 hub with a D8 bore, four radial blades 2.0 thick, r 6..20, 8.0 tall; about 1525.6 mm3 (2.15 g) |
| motor | purchased | (catalog cylinder) | not stated | spec Bodies, Dimensions | D30 x 40, z -40..0 in its own frame; stationary body, the magnetic coupling is not modelled |
| water | derived | (assembly source) | water at 20 degC | spec Fluid | housing cavity minus the impeller, capped at z = 48 and x = 58; about 52425 mm3 |

Housing (assembly frame): chamber r 25.0 over z 0..25; side wall outer r 28.0 over z -3..28; floor z -3..0; lid z 25..28.
Inlet tube on the axis, ID 12.0 / OD 16.0, z 28..48, its bore continuing through the lid (z 25..48). Outlet tube on
y = 0, z = 12.5 along +x, ID 10.0 / OD 14.0, from the wall's outer face to x = 58, its bore continuing through the wall.
Pin D6.0 on the axis, z 0..12, flat top. Bounding box x -28..58, y -28..28, z -3..48.

Impeller (own frame): hub OD 12.0, z 0..10, through bore D8.0. Blades at 0/90/180/270 deg, 2.0 thick centred on the radius
line, from the hub (roots merged into it at r 6.0) to tips trimmed to r 20.0, over z 1..9. Bounding box x, y -20..20,
z 0..10.

Motor (own frame): cylinder D30.0 x 40.0 on the axis, z -40..0, origin at the centre of its top (output) face.

## 4. Frames, joints and motion

Assembly frame = housing frame: origin at the centre of the chamber floor's inside face, +z up the impeller axis, +x toward
the outlet, y completing a right-handed frame. Datums: A floor inside face z = 0; B impeller and pin axis x = y = 0; C outlet
axis y = 0, z = 12.5. Assembled envelope at rest: min (-28, -28, -43), max (58, 28, 48) (motor bottom z = -43, inlet end
z = 48, outlet end x = 58, wall r 28).

Own frames: impeller origin at the centre of its hub's bottom face, +z its axis, one blade along +x; motor origin at the
centre of its top face, +z along its shaft; water built directly in the assembly frame.

| joint | kind | parent | child | parent frame (parent's own frame) | child frame (child's own frame) | rest | drive |
|---|---|---|---|---|---|---|---|
| motorMount | rigid | housing | motor | origin (0, 0, -3), axis +z, ref +x | origin (0, 0, 0), axis +z, ref +x | top face on the floor's underside | none |
| impellerSpin | revolute | housing | impeller | origin (0, 0, 1), axis +z, ref +x | origin (0, 0, 0), axis +z, ref +x | angle 0: the +x blade points at the outlet | motor, speed from case value `impellerRpm` |
| waterFixed | rigid | housing | water | origin (0, 0, 0), axis +z, ref +x | origin (0, 0, 0), axis +z, ref +x | identity | none |

Placed impeller: hub z 1..11, blades z 2..10, pin top z 12 stands 1.0 above the hub. Rest clearances: 1.0 to the floor,
1.0 radial on the pin, 5.0 at the tips, 14.0 to the lid. Rotation is positive about +z (counter-clockwise seen from above),
continuous (no limits). Housing and motor are stationary.

Transmissions: none. The motor-to-impeller magnetic coupling is not modelled; the drive sits on `impellerSpin` directly.

Acceptance: clearance `impellerOnPin` (impeller to housing, 0.9..1.1: the 1.0 bore and floor gaps), `motorSeat` (motor to
housing, 0..0.05: face contact), `impellerClearOfMotor` (at least 3.5; the floor lies between, 4.0 at rest); motion
`impellerTurn`: `impellerSpin` 0..360 deg in 36 steps, pairs impeller-housing and impeller-motor (the water region is
fluid and is left out of the sweep).

## 5. Fluid regions and named boundaries

Fluid volume `water` (body `water`): walls `housing`, minus `impeller`, caps `inletCap` at (0, 0, 48) normal +z and
`outletCap` at (58, 0, 12.5) normal +x (both outward). Seed (12.3, 5.7, 17.1): r 13.6 above the impeller, 7.1 above the
blade tops, 7.9 below the lid, 11.4 from the side wall. Volume band 52425 mm3 +- 1 %:

| piece | volume mm3 | formula |
|---|---|---|
| chamber | 49087.4 | pi 25^2 x 25 |
| inlet bore, lid and tube | 2601.2 | pi 6^2 x (48 - 25) |
| outlet bore, wall and tube | 2601.7 | disc r 5 from the chamber cylinder r 25 to x = 58 (integrated) |
| pin | -339.3 | pi 3^2 x 12 |
| impeller | -1525.6 | hub pi (6^2 - 4^2) x 10 = 628.3, plus 4 blades of 224.3 (2.0 wide, root on r 6, tip on r 20, 8.0 tall) |
| water | 52425.4 | the spec states about 5.24e4 |

The pin alone is 0.65 % of the volume, inside the 1 % band; the pin is proven by `impellerOnPin` and the renders, not
the volume.

| boundary | role | body | selector | expected |
|---|---|---|---|---|
| inlet | inlet | water | plane (0, 0, 48), normal +z | area 113.097 mm2 (pi 6^2) +- 1 % |
| outlet | outlet | water | plane (58, 0, 12.5), normal +x | area 78.540 mm2 (pi 5^2) +- 1 % |
| impellerWall | rotating_wall | water | touching `impeller` | the impeller's whole wetted surface |
| housingWall | wall | water | rest | stationary: chamber, lid, floor, both bores and the pin, also inside the rotating zone |

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| design.impellerRpm | 1500 | rpm | stated | spec Operating point |
| design.flowLMin | 2.0 | L/min | stated | spec Operating point |
| design.inletTurbulencePct | 5 | % | stated | spec Operating point |
| cfd, euler: fluidDensity | 998.2 | kg/m3 | stated | spec Fluid (water at 20 degC) |
| cfd: fluidViscosity | 1.002e-3 | Pa s | stated | spec Fluid (dynamic) |
| cfd: cell_mm / surface_level | 1.5 / 1 | mm / levels | stated | spec Predictions item 1 ("about 1.5 mm interior cells, walls one level finer") |
| cfd: refinement | [1.0, 0.75, 0.5625] | factor | inferred | three levels each refining everywhere (spec Predictions item 1) at a constant ratio 4/3 (above Celik's 1.3); the finest (0.84 mm, walls 0.42 mm) is sized for the 20-minute budget |
| cfd: processes / timeout_s | 4 / 1200 | - / s | stated | spec Predictions item 1 (under 20 minutes on 4 cores per level) |
| cfd: iterations | 1500 | - | defaulted | steady MRF; the values are the mean of the last 20 % |
| cfd: inlet_diameter_mm | 12.0 | mm | stated | spec Dimensions (inlet tube inner diameter) |
| euler: bladeCount | 4 | - | stated | spec Dimensions (four blades) |
| euler: bladeOutletAngle | 90 | deg | stated | spec Predictions item 2 (straight radial blades) |
| euler: bladeOutletWidth | 8.0 | mm | stated | spec Predictions item 2 (8.0 tall at the tip) |
| euler: hydraulicEfficiency | 0.35 +- 0.15 | - | inferred | the spec says it is not known; radial blades without a volute or diffuser keep at most the reaction part (one half to two thirds) of the Euler work as static pressure, and open paddles with a 5 mm tip gap lose more |
| housing density | 900 | kg/m3 | stated | spec Bodies |
| impeller density | 1410 | kg/m3 | stated | spec Bodies |

Observables (design case): `pressureRiseCfd` (pressure_rise, Pa, cfd, steady, min 500: the requirement), `impellerTorque`
(torque, N m, cfd, steady), `pressureRiseEuler` (pressure_rise, Pa, euler, steady; comparison only), `eulerHeadIdeal`
(euler_head, m, euler; the ideal head behind the estimate), `waterVolume` (volume, mm3, body water; measured on the
derived region). No measured value is written into the contract.

Scale for the reviewer (not contract values): tip speed U2 = 157.08 rad/s x 0.020 m = 3.142 m/s, rho U2^2 = 9852 Pa;
inlet mean velocity 0.295 m/s (Re 3523), outlet 0.424 m/s; impeller Reynolds number rho N D^2 / mu = 3.98e4 (turbulent);
the through-flow meridional velocity at the tip is 0.033 m/s, so the stirring dominates the flow.

Simulations: `cfd` (cfd_steady, openfoam, bodies [water, impeller], settings flow_key flowLMin, speed_key impellerRpm,
turbulence_key inletTurbulencePct) predicts `pressureRiseCfd`, `impellerTorque`; `euler` (reduced:pump_euler, bodies
[impeller], the tip radius from the placed rotor) predicts `pressureRiseEuler`, `eulerHeadIdeal`.

## 7. Defaults, open questions and unrepresentable features

- Hydraulic efficiency: not known (spec); inferred 0.35 with a standard uncertainty of 0.15. The Euler estimate is a
  comparison, so the 500 Pa requirement is gated only on the CFD prediction.
- Impeller rest phase: the spec places the impeller by translation only; taken as angle 0 (a blade along +x, pointing at
  the outlet). The frozen-rotor MRF result depends weakly on it.
- Stationary walls inside the rotating zone: the pin, the floor under the hub and the lid are stationary walls even where
  the MRF zone encloses them; the zone's extent (between the tips at r 20 and the wall at r 25, above the pin top) is the
  CFD adapter's choice and is not in the contract.
- Magnetic coupling and motor internals are not modelled; the motor's material and mass are not stated, so there is no
  assembly mass or centre-of-mass acceptance.
- No fillets, chamfers, draft or tube-to-wall blends are stated; sharp edges. The blade tips are trimmed to r 20.0 (a flat
  tip would reach r 20.03 at its corners and raise the Euler tip speed by 0.1 %).
- Mesh ladder [1.0, 0.75, 0.5625] with iterations 1500 and a 1200 s timeout per level; if the finest level overruns or its
  grid-convergence index exceeds 0.05, `sim study` should try another ladder.
- No outlet back-pressure or inlet turbulence length scale is stated; the CFD adapter's defaults apply (static-pressure
  outlet, length scale from the 12.0 inlet diameter).
- The 1.0 mm gaps (hub bore to pin, hub to floor) are only about 2.4 wall cells wide at the finest level; they carry little
  of the torque, which is dominated by the paddles' pressure drag.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft | ok | `python -m opencad assembly check designs/.staging-mixer-01 --name mixer-01` |
