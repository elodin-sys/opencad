# nottingham-bearing — assembly brief

## 1. Intent and configuration

The half-journal bearing test section of the University of Nottingham highly loaded bearing rig (Layton et al. 2026,
*Experimental Investigation of a Highly Loaded Half-Journal Bearing*, Lubricants 14(2) 76, section 2), reconstructed as a
machine from the text packet `sources/bearing-packet.md`. That packet is the only source and it is authoritative. It has no
CAD, drawings or measured results, so the reference geometry is the stated dimensions.

- **Bodies.** An EN24T steel shaft with a D100.0 journal turns on a revolute joint inside a stationary 180-degree EN24T bush
  (D100.2 bore, 75 long). The oil film between them (Eastman Turbo Oil 2197) is a derived fluid body, concentric at rest,
  with a 0.1 mm radial clearance.
- **Case frame.** The bearing axis is +z and the bush spans z = 0..75. Bottom dead centre (BDC) points toward -y, so the
  bush is below the shaft. The shaft turns positively about +z, so its surface at BDC moves toward +x: the inlet edge of
  the arc is at -x and the outlet edge at +x. The applied load presses the shaft toward the bush along BDC (-y).
- **Predictions.** The reduced thermal Reynolds film analysis (`reduced:reynolds_film`) predicts, at six speed/load points
  of the test matrix: the film pressure at the -20 and -45 deg tappings, the minimum operating film thickness and its
  angle from BDC, and the ratio of the maximum bush-centreline temperature to the temperature nearest the inlet (-85 deg).
- **Cases.** The cases that matter are the 10 kN speed sweep (1000, 3000 and 4000 rpm; development) and the higher-load
  points 2000 rpm / 15 kN, 3000 rpm / 15 kN and 4000 rpm / 20 kN (held out).

## 2. Sources

| file | kind | role | sha256 | notes |
|---|---|---|---|---|
| `sources/bearing-packet.md` | text | authoritative | `59abf634a3867c0c21ea6118b6bf08e72e4cfdfc5d0eb56ceacbfd8c8d944c4b` | Layton et al. (2026), doi:10.3390/lubricants14020076, CC BY 4.0; section 2 (experimental method) only: unit under test, lubricant, instrumentation, test matrix. No measured results, no images, no CAD. |

## 3. Bill of materials

| body | kind | design | material | source | notes |
|---|---|---|---|---|---|
| `bush` | modelled (datum) | `nottingham-bearing-bush` | EN24T steel, Ra 0.1 um; 7850 kg/m3 (inferred) | packet, Unit under test | Half annulus 50.1 <= r <= 75, y <= 0, z = 0..75. The 180 deg arc runs from -90 deg (inlet, -x) through BDC (-y) to +90 deg (outlet, +x). The D150 outside is inferred. Tappings and thermocouples are locations only, not holes. |
| `shaft` | modelled | `nottingham-bearing-shaft` | EN24T steel, Ra 0.1 um; 7850 kg/m3 (inferred) | packet, Unit under test | Plain D100.0 cylinder, z = -115..+115 in its own frame, so 230 long: the stated support-bearing span. Mid-length sits on the bush centreline (inferred). |
| `oil` | derived (fluid) | — | Eastman Turbo Oil 2197, 996.8 kg/m3 at 15 degC | packet, Lubricant | Concentric half-annulus film 50.0 <= r <= 50.1, y <= 0, z = 0..75, built in the assembly source; 1179.3 mm3. |

Not modelled: the two cylindrical roller bearings supporting the shaft, the chamber, the inlet film generator, the loading
mechanism, the oil supply and drain, and the sensors.

## 4. Frames, joints and motion

**Assembly frame.** This is the bush's own frame (`datum_part: bush`).

- Origin: on the bearing axis in the bush end face z = 0.
- x: horizontal, toward the outlet edge (+90 deg).
- y: from BDC toward the shaft.
- z: the bearing axis.
- Datums: A is the end face z = 0, B is the axis x = y = 0, C is the split plane y = 0, and D is the centreline z = 37.5.

Angles t are measured from BDC, positive in the direction the shaft surface moves. A point at radius r and angle t is
(r sin t, -r cos t, z). For the -20 deg tap on the bore (r = 50.1) this gives (-17.135, -47.079); for the -45 deg tap it
gives (-35.426, -35.426). Both match the observable locations.

**Part frames.**

- `bush`: identical to the assembly frame.
- `shaft`: axis +z through its origin, with the origin at mid-length (the mid-span between the support bearings).
- `oil`: built directly in the assembly frame.

**Joints.**

| joint | kind | parent → child | parent frame (bush) | child frame | rest | drive |
|---|---|---|---|---|---|---|
| `journal` | revolute | bush → shaft | origin (0, 0, 37.5), axis +z | origin (0, 0, 0), axis +z | offset 0 (shaft mid-length on the bush centreline, concentric); axisymmetric, so no ref or angle | motor, `case_value: speedRpm` (set point ±4 rpm), positive about +z |
| `oilFixed` | rigid | bush → oil | origin 0, axis +z, ref +x | origin 0, axis +z, ref +x | coincident | — |

There are no transmissions. Only the joint defines the concentric rest pose. The operating eccentricity and attitude
angle are outputs of the film analysis and are not placed in the geometry.

**Acceptance.**

- Clearance `journalClearance` (shaft to bush): min_gap 0.09, max_gap 0.11. That is the nominal 0.100 radial clearance
  plus or minus the stated 0.01 mm manufacturing tolerance.
- Motion `spin`: `journal` from 0 to 360 deg in 8 steps, checking the shaft-bush pair only. The journal must clear the bore
  at every step. The film is a fluid and is excluded from the interference sweep.

**Derived context.** These follow from the stated inputs and are not measured results.

- Surface speed \(U = \pi D N / 60\): 5.24 m/s at 1000 rpm, 10.47 m/s at 2000 rpm, 15.71 m/s at 3000 rpm and 20.94 m/s at
  4000 rpm.
- Specific load \(W / (L D)\): 1.33 MPa at 10 kN, 2.00 MPa at 15 kN and 2.67 MPa at 20 kN.

## 5. Fluid regions and named boundaries

**Fluid region `oil`** (body `oil`).

- Walls: `[bush]`. Minus: `[shaft]`.
- Caps:
  - `splitCap`: the split plane y = 0, outward normal +y. It closes both arc edges.
  - `endCap0`: z = 0, normal -z.
  - `endCap75`: z = 75, normal +z.
- Seed: (0, -50.05, 37.5), mid-film at BDC. The film is only 0.1 mm thick, so the seed is 0.05 mm from each wall and the
  1 mm rule cannot be met (see section 7).
- Volume band: (pi/2)(50.1^2 - 50.0^2) x 75 = 1179.3 mm3, ±5 % (derived).

**Boundaries.** All are on the `oil` body, in the assembly frame at rest.

| name | role | selector | description |
|---|---|---|---|
| `oilFeed` | inlet | region: centroid box x -50.2..-49.9, y ±0.05, z -0.05..75.05 | Inlet edge at -90 deg, fed by the inlet film generator at the tank temperature |
| `oilOutlet` | outlet | region: centroid box x 49.9..50.2, y ±0.05, z -0.05..75.05 | Outlet edge at +90 deg, discharging into the ambient chamber |
| `endZ0` | opening | plane z = 0, normal -z | Side leakage at ambient chamber pressure |
| `endZ75` | opening | plane z = 75, normal +z | Side leakage at ambient chamber pressure |
| `shaftSurface` | rotating_wall | cylinder r = 50.0 about +z through the origin, tolerance 0.02 | Film face on the journal, at the case speed |
| `bushBore` | wall | rest | Film face on the stationary D100.2 bore |

Both arc edges lie in the same plane y = 0, so the inlet and outlet are told apart by region selectors rather than by
plane. The cylinder selector uses a 0.02 tolerance, well under the 0.1 film thickness, so the journal face cannot capture
the film's end faces.

## 6. Operating cases, observables and simulation inputs

| item | value | unit | provenance | source / formula / rationale |
|---|---|---|---|---|
| case `n1000w10` (development) | speedRpm 1000, loadKN 10 | rpm, kN | stated | packet, Test matrix (1000-4000 rpm in 500 rpm steps; 5-20 kN in 2.5 kN steps) |
| case `n2000w15` (held out) | speedRpm 2000, loadKN 15 | rpm, kN | stated | packet, Test matrix |
| case `n3000w10` (development) | speedRpm 3000, loadKN 10 | rpm, kN | stated | packet, Test matrix |
| case `n3000w15` (held out) | speedRpm 3000, loadKN 15 | rpm, kN | stated | packet, Test matrix |
| case `n4000w10` (development) | speedRpm 4000, loadKN 10 | rpm, kN | stated | packet, Test matrix; the highest speed, 20 L/min supply |
| case `n4000w20` (held out) | speedRpm 4000, loadKN 20 | rpm, kN | stated | packet, Test matrix; the highest speed, 20 L/min supply |
| `oilDensity` | 996.8 (u = 15) | kg/m3 | stated | packet, Lubricant: "0.9968" at 15 degC. About 3 % lower at the film temperatures and not corrected, hence the uncertainty. |
| `oilViscosity40` | 26.98 | mm2/s | stated | packet, Lubricant (kinematic, 40 degC) |
| `oilViscosity100` | 5.28 | mm2/s | stated | packet, Lubricant (kinematic, 100 degC) |
| `oilSpecificHeat` | 2000 (u = 100) | J/kg K | inferred | Not stated. Typical of polyol-ester (MIL-PRF-23699 class) turbine oils at 40-100 degC (1.9-2.1 kJ/kg K). |
| `inletTemperature` | 30 (u = 3) | degC | inferred | The tank is stated at 30 degC (cartridge heater). The film inlet is taken at the tank temperature, with no line heating or carry-over. |
| settings | load_key `loadKN`, speed_key `speedRpm`, grid [181, 41], thermal true, ratio_reference_deg -85 | — | defaulted | The adapter's defaults. The ratio reference is the thermocouple nearest the inlet (packet, Instrumentation). |
| refinement | [1.0, 0.5] | grid-size factor | defaulted | Two grid levels for the numerical uncertainty |
| geometry | radius 50.0, clearance 0.1, length 75, arc 180 deg | mm, deg | stated | Measured by the adapter from the placed shaft and bush |

**Observables.** Simulation `film` (`reduced:reynolds_film`, bodies `[shaft, bush]`) predicts all of them. None has a
requirement band, because the sources state none.

- **Film pressure** (`pressure`, MPa, steady), at bore points:
  - The -20 deg tap on the centreline, (-17.135, -47.079, 37.5): `p20c_n1000w10`, `p20c_n3000w10`, `p20c_n3000w15` and
    `p20c_n4000w10`.
  - The -20 deg tap at z = 18.5, (-17.135, -47.079, 18.5): `p20s_n3000w10`.
  - The -45 deg tap on the centreline, (-35.426, -35.426, 37.5): `p45c_n3000w10`.
- **Minimum film thickness** (`min_film_thickness`, um, minimum) and **its angle** (`min_film_angle`, deg from BDC in the
  rotation direction, steady): `hmin_*` and `hminAngle_*` for `n1000w10`, `n3000w10`, `n4000w10`, `n3000w15`, `n2000w15`
  and `n4000w20`.
- **Temperature ratio** (`max_temperature_ratio`, dimensionless, steady): the maximum film temperature over the film
  temperature at -85 deg, both in degC. Declared as `tRatio_n1000w10`, `tRatio_n3000w10` and `tRatio_n4000w10`.

## 7. Defaults, open questions and unrepresentable features

**Inferred or defaulted, and why.**

- Bush outside diameter: D150, a 24.9 mm wall. The sources give no outside dimension.
- Shaft: a plain D100.0 x 230 cylinder spanning the stated support-bearing span, symmetric about the bush centreline. The
  sources give no shaft length, seats or drive end.
- EN24T density: 7850 kg/m3 (typical low-alloy steel). Not stated.
- Oil specific heat: 2000 ± 100 J/kg K. Not stated.
- Film inlet temperature: 30 ± 3 degC, equal to the stated tank temperature.
- Adapter settings: its defaults (grid, thermal wedge, -85 deg ratio reference).

**Open questions.** These repeat the contract's `open_questions`.

1. The bush outside geometry is not stated. It is modelled as a D150 half cylinder; the tapping and thermocouple holes,
   the inlet film generator and the loading mechanism are not modelled.
2. The shaft length, bearing seats and drive end are not stated. The shaft is a plain D100.0 x 230 cylinder between the
   support-bearing centres, symmetric about the bush centreline; the support roller bearings and the chamber are not
   modelled.
3. The oil specific heat is not stated: 2000 J/kg K is inferred (standard uncertainty 100 J/kg K).
4. The film inlet temperature is not stated. It is taken as the 30 degC tank temperature (standard uncertainty 3 K);
   supply-line heating and hot-oil carry-over at the inlet edge are neglected.
5. The oil density is stated at 15 degC only, and the analysis uses it at every film temperature (about 3 % high at
   60 degC).
6. Viscosity is stated at 40 and 100 degC only. The 30 degC inlet lies below that range, so the viscosity-temperature law
   extrapolates there.
7. The supply flow is stated only at the highest speed (20 L/min, partly overflowing). The film is taken as fully flooded
   at the -90 deg inlet edge in every case, with ambient (zero gauge) pressure at the arc edges and bush ends.
8. The EN24T density is inferred and no thermal properties of the steel are stated. Heat conduction into the bush and
   shaft is not an input of the reduced film analysis.
9. The thermocouples sit 1 mm below the bush surface, while the reduced analysis predicts film temperatures. The
   temperature ratio compares the film maximum with the film at -85 deg.
10. The film is 0.1 mm thick, so the fluid seed cannot be 1 mm from every wall. It sits mid-film at BDC, 0.05 mm from each
    wall.
11. Rigid, aligned, smooth surfaces are assumed. Elastic and thermal distortion of the highly loaded bush, shaft
    deflection between the supports, misalignment and the Ra 0.1 um roughness are not represented.

**Not representable in the contract.**

- The operating eccentricity: the geometry is placed concentric, and the adapter solves the eccentricity.
- The cavitation or film-rupture boundary condition, which is internal to the adapter.
- Oil overflow into the chamber, and the gravity drain.
- Sensor response: the 0-200 bar transducers (±0.9534 bar), K-type thermocouples (±2.5 degC), the ultrasonic film sensors
  (±2.1 um) and the angular encoder (0.22 deg). These are measurement uncertainties that belong to the truth manifest, not
  the contract.

## 8. Run log

| stage | verdict | note |
|---|---|---|
| asm-draft (order 001) | ok | `python -m opencad assembly check`: 3 bodies, 2 joints, 0 transmissions, 1 simulation, no warnings |
