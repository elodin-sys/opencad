# AXJET-220: Design and Implementation Guide

A single-spool, two-stage all-axial micro turbojet sized to the engine bay of a 3.5 m sport jet. This guide is the complete definition needed to model it as an opencad assembly, analyse it, manufacture a first article and run it on a test stand. It stands alone; it does not depend on the research that produced it.

**Navigation:** [1 The engine in one page](#1-the-engine-in-one-page) | [2 Requirements](#2-requirements-and-constraints) | [3 Flow path and stations](#3-architecture-flow-path-and-stations) | [4 Compressor](#4-compressor) | [5 Diffuser and combustor](#5-diffuser-and-combustor) | [6 Turbine](#6-turbine) | [7 Exhaust and nozzle](#7-exhaust-duct-and-nozzle) | [8 Rotor system](#8-rotor-system) | [9 Inlet](#9-inlet) | [10 Fuel, ignition, control, instrumentation](#10-fuel-ignition-control-and-instrumentation) | [11 Materials and manufacturing](#11-materials-and-manufacturing) | [12 Mass budget](#12-mass-budget) | [13 Analysis plan](#13-analysis-plan) | [14 opencad implementation](#14-opencad-implementation) | [15 Build and test plan](#15-build-and-test-plan) | [16 Growth](#16-growth-paths) | [A Sizing script](#appendix-a-sizing-script) | [B Conventions](#appendix-b-conventions-and-formulas) | [C Provenance](#appendix-c-parameter-provenance)

Units are mm, degrees, kg, s, K, Pa unless written otherwise. Angles are measured from the axial direction. Every number is a **design-point calculation** (Appendix A reproduces it) unless marked *stated* (from a source or a requirement) or *assumed*. Nothing has been measured on hardware.

## 1. The engine in one page

![AXJET-220/2 meridional section, drawn to scale](axjet_220_section.png)

*Meridional section drawn to scale from sections 3–8, with the gas path tinted by design-point total temperature (the flame zone is illustrative). After a geometry change, regenerate it with `.venv/bin/python scratch/turbine/axjet_220_section.py`.*

| Item | Value | Status |
|---|---|---|
| Designation | AXJET-220/2 (two-stage); AXJET-220/3 is the growth variant | – |
| Type | single-spool turbojet, 2-stage transonic axial compressor, straight-through annular combustor, 1-stage uncooled axial turbine, fixed convergent nozzle | design |
| Envelope | max diameter 224 mm over flanges (casing 212), length 665 mm from nose tip to nozzle exit (−165 … +500), test bellmouth included | design; bay fit *to be measured* (section 2.1) |
| Dry mass | 16 kg target with starter, pump, valves and harness; the bottom-up estimate of section 12 is 20 kg before weight work | estimate ±30 % |
| Design speed | 44,000 rpm (ω = 4608 rad/s); overspeed trip 110 % = 48,400 rpm | design |
| Airflow | 2.30 kg/s (sea-level static, ISA) | design |
| Overall pressure ratio | 2.33 (stage 1: 1.525, stage 2: 1.528) | design, η per stage 0.85/0.86 *assumed* |
| Turbine inlet temperature | 1150 K average; 1200 K max transient | design limit |
| Compressor exit | 2.36 bar, 381 K | design |
| Shaft power (compressor) | 215 kW | design |
| Fuel flow | 50.5 g/s = 3.8 L/min Jet A-1 (f = 0.0219) | design |
| Static thrust | 1,169 N nominal; **design-to value 1,000 N**; pessimistic (η 0.78/0.82, TIT 1120 K) 1,063 N | design |
| Specific thrust / SFC | 508 N/(kg/s); 0.155 kg/(N h) = 43 g/(kN s) | design |
| Jet | nozzle pressure ratio 1.57, M₉ 0.85, V₉ 498 m/s, exit D 128 mm | design |
| Compressor tip speed / relative Mach | 415 m/s; 1.30 (R1 tip), 1.20 (R2 tip) | design |
| Turbine | r 47.6 … 92.4 at the rotor, tip speed 426 m/s, ψ = Δh/U² 0.89 at r_m 70, reaction 0.56, PR 1.41 | design |
| Bearings | front: matched pair 25 × 52 × 15 hybrid angular-contact (DB), rear: single 25 × 52 × 15 hybrid, both oil-mist on 4.5 % oil-in-fuel; DN 1.1 × 10⁶ | design |
| Materials | 2618-T61 blisks (Ti-6Al-4V option), 6061-T6 vane rings, casings and inlet, 321 SS combustor casing, Inconel 625 liner and vaporisers, cast IN713LC turbine wheel with integral stub, Haynes 282 (LPBF) or cast IN713C NGV ring, 321 SS exhaust | design |
| Stored rotor energy at 44 krpm | 64 kJ (J ≈ 6.0 g m²) | estimate |
| Life target (first article) | 25 h at design point, 200 start cycles; overhaul inspection every 5 h for the first 25 h | requirement |

What the engine is for: a research demonstrator of full axial flow at micro scale that can be ground-tested to self-sustaining, repeatable operation and later installed in a 3.5 m-class airframe. What it is not: a drop-in for a 320 N hobby turbine (it is five times heavier and burns four times the fuel), and not a supersonic engine on its own. The [V2 guide](axjet_v2_design_and_implementation_guide.md) adds a reheat module and a variable nozzle to this core for a twin-engine Mach 1.2 airframe; the interfaces, materials, fuel pump and controller below are set so that upgrade bolts on (section 2.4).

## 2. Requirements and constraints

### 2.1 Installation envelope (airframe: Elite Aerosports BDXL)

*Stated*: span 3.5 m, length 3.7 m, 36.7 kg dry, sold for a 320 N engine (KingTech K-320G4+: Ø132.5 × 335 mm, 2.9 kg, 0.53 kg/s), 9.0 L fuel cell, stainless dual-wall thrust pipe, three-piece composite fuselage.

*Assumed until measured* (the first task of the build plan): the bay at the engine station accepts a 224 mm diameter × 665 mm cylinder with 15 mm radial clearance for mounts and heat shielding; the firewall-to-tailpipe-exit length allows the 128 mm nozzle to exhaust into a 150 mm-bore tailpipe; the dorsal intake can be rebuilt to a 140 cm² throat (section 9); the structure at the engine station carries 16 kg with 6 g vertical and 3 g lateral; the CG can be restored with equipment relocation.

Measure and record before any geometry is frozen: bay width and height at 100 mm stations from the wing-root leading edge aft; distance from the firewall/former to the tailpipe exit; intake throat area and duct cross-sections at 50 mm stations; tailpipe bore and exit diameter; fuel-cell and UAT positions; mount hard points. If the bay accepts less than 224 mm, scale the engine photographically: thrust ∝ D², speed ∝ 1/D (a 180 mm version runs 55,000 rpm for ~0.79 kN).

### 2.2 Performance requirements

| Requirement | Value | Verification |
|---|---|---|
| Self-sustaining operation (starter off) with fuel only | at ≥ 45 % speed (19,800 rpm) | ground test, logged |
| Static thrust at 100 % speed, ISA sea level, bellmouth inlet | ≥ 1,000 N (design 1,169) | load cell, corrected to ISA |
| Specific fuel consumption at 100 % | ≤ 0.17 kg/(N h) | fuel flowmeter / load cell |
| Exhaust gas temperature (Tt5) at 100 % | ≤ 1,100 K average, ≤ 1,130 K any probe | 4 × K-type at station 5 |
| Acceleration idle → 100 % | ≤ 6 s without surge or EGT exceedance | logged |
| Start | kerosene start with glow plugs, light-off ≤ 20 % speed, idle 45 % | logged |
| Vibration at bearing housings | ≤ 10 mm/s rms steady, ≤ 20 mm/s transient | accelerometers |
| Bearing housing temperature | ≤ 140 °C | thermocouples |
| Life | 25 h / 200 cycles first article; turbine wheel retired at 25 h or at first crack indication | inspection record |

### 2.3 Design constraints

- Single spool; no variable geometry; no bleed valves; no turbine cooling; fixed nozzle with interchangeable trim rings.
- Blisks machinable on a 5-axis mill from plate or forged bar; no blade count below 17 or above 47; minimum blade thickness 0.8 mm at the tip, root fillet ≥ 1.5 mm.
- Kerosene/Jet A-1 with 4.5 % synthetic turbine oil; the oil in the fuel lubricates the bearings (no separate oil system).
- All rotating parts within 1 mm of their nominal radius at 110 % speed; cold tip clearance 0.25 mm (compressor) and 0.40 mm (turbine).
- Test stand first; the flight installation (inlet duct, tailpipe, mounts, structure, CG) is a separate package after the ground program (section 15, gate I).

### 2.4 Interfaces, mounts and design loads (set for V1 flight and the V2 upgrade)

| Interface | Definition |
|---|---|
| Inlet flange | `inlet-frame` front flange z −72 … −67, OD 224, 8 × M5 on PCD 216, inner contour r 95.8 at the face (on the bellmouth ellipse). The test bellmouth lip (z −98 … −72) and the flight inlet adapters (BDXL duct, V2 pitot-inlet duct) bolt here |
| Main mount | clamp ring on the combustor front flange (z 115 … 120) with two trunnions on ±y; carries thrust, vertical and lateral loads |
| Rear mount | one link on +x at the combustor rear flange (z 317 … 322), spherical rod ends, axially free for ~1.5 mm of thermal growth |
| Aft module flange | z 322, OD 224, 12 × M6, shared with the NGV and combustor-casing flanges: carries the V1 dry exhaust module (duct, tail cone, nozzle ring, 1.8 kg) or the V2 reheat module (7.7 kg, with its own sliding aft support) |
| Fuel and electrical | core fuel manifold inlet on the combustor casing at z 125; starter, sensor and pt2 lines through the +x strut; glow plugs on the casing; ECU harness carries the V2 channels (section 10) |
| Design loads | ±6 g vertical and ±3 g lateral on the mounts; internal pressures 1.5 × the static design values (V2's low-altitude limit, Mach 0.85 at sea level, reaches pt3 3.3 bar); shaft torque 64 N m (1.4 × design) |

## 3. Architecture, flow path and stations

Frame (also the opencad assembly frame): origin on the engine axis at the stage-1 rotor leading-edge plane; **z** along the axis, flow toward +z; **x** up (toward the aircraft's dorsal intake); **y** completes a right-handed frame. Radii are measured from the axis.

### 3.1 Station table (sea-level static, ISA, 44,000 rpm)

| Station | Location | z (mm) | pt (bar) | Tt (K) | ṁ (kg/s) | Notes |
|---|---|---:|---:|---:|---:|---|
| 0 | ambient | – | 1.013 | 288.2 | – | ρ 1.225 kg/m³ |
| 2 | compressor face (R1 LE) | 0 | 1.013 | 288.2 | 2.30 | bellmouth loss neglected; aircraft inlet derate 2 % |
| 2.5 | after stator 1 | 40 | 1.545 | 331.7 | 2.30 | stage 1 PR 1.525 |
| 3 | after OGV | 80 | 2.361 | 381.3 | 2.30 | OPR 2.331, M 0.23 |
| 3.1 | combustor casing inlet | 115 | 2.35 | 381.3 | 2.30 | diffuser loss 0.5 % |
| 4 | turbine inlet (NGV LE) | 300 | 2.243 | 1150 | 2.350 | burner loss 5 %, f 0.0219, η_b 0.97 |
| 4.5 | rotor inlet (NGV exit) | 325 | 2.18 | 1150 | 2.350 | α 54°, M 0.55 |
| 5 | turbine exit | 352 | 1.594 | 1070 | 2.350 | PR_t 1.408, η_t 0.86, zero swirl, M 0.33 |
| 9 | nozzle exit | 500 | 1.594 | 1070 | 2.350 | NPR 1.573 (unchoked), M₉ 0.85, T₉ 953 K, V₉ 498 m/s (C_v 0.97), A₉ 128.7 cm², D₉ 128 mm |

Thrust F = ṁ₉ V₉ = 1,169 N (no pressure term; unchoked). Compressor power 215 kW; turbine work 92.5 kJ/kg of gas.

### 3.2 Flow-path radii by axial station

| z (mm) | Element | Hub r (mm) | Tip / casing r (mm) | Annulus (cm²) |
|---:|---|---:|---:|---:|
| −165 | nose tip; tangent ogive to z −130 | 0 → 32 | – | – |
| −130 … −80 | nose-cone cylinder Ø64 around the starter (section 8.3) | 32 | – | – |
| −95 | bellmouth lip | 32 | 125 | – |
| −80 | nose cone joins the inlet-frame hub | 32 | 100.2 | – |
| −72 | bellmouth / inlet-frame flange (the flight inlet adapters mate here) | 32 | 95.8 | – |
| −70 … −40 | inlet struts (5) | 32 | 90.25 (from −45) | – |
| −40 … −15 | inlet-frame hub fairing rises | 32 → 57.6 | 90.25 | – |
| −15 … −11 | fairing (stationary) ends; 3 mm axial gap to the R1 hub | 57.6 | 90.25 | 150 |
| −8 … 0 | R1 front hub extension (rotating) | 57.6 | 90.25 | 150 |
| 0 | R1 leading edge | 57.6 | 90.0 (blade tip), 90.25 (bore) | 150 |
| 16 | R1 trailing edge | 61.0 | 90.0 | 139 |
| 22 … 36 | S1 vanes | 61.0 → 64.5 | 90.0 (shroud band) | 139 → 124 |
| 42 | R2 leading edge | 64.8 | 90.0 | 123 |
| 55 | R2 trailing edge | 66.5 | 90.0 | 115 |
| 61 … 76 | OGV vanes | 66.5 → 67.5 | 90.0 | 115 → 111 |
| 80 | station 3 | 67.5 | 90.25 | 111 |
| 80 … 115 | annular diffuser | 67.5 → 60 | 90.25 → 95 | 111 → 170 |
| 115 | dump into casing | 45 (tunnel OD) | 105 (casing ID) | 283 |
| 140 | liner dome | liner 55 … 97 | – | liner 200 |
| 140 … 300 | flame tube | 55 | 97 | 200 (passages: inner 45–55, outer 97–105) |
| 285 … 305 | liner exit transition | 55 → 47.6 | 97 → 92.4 | 200 → 197 |
| 300 … 322 | NGV vanes (17) | 47.6 | 92.4 | 197 |
| 327 … 345 | turbine blades (23) | 47.6 | 92.4 (tip), 92.8 (shroud bore) | 197 |
| 352 | station 5 | 47.6 | 92.4 | 197 |
| 352 … 470 | tail cone | 47.6 → 0 | 92.4 → 72 | 197 → 163 |
| 470 … 500 | nozzle ring | 0 | 72 → 64 | 163 → 128.7 |

Casing outer diameters: compressor rings 200 (flanges 212); combustor casing 212 (flanges 224); exhaust duct 190 → 140. Hub contours between the tabulated points are straight lines; the casing bore is cylindrical through the compressor (constant-tip design).

## 4. Compressor

Constant tip radius 90.0 mm, rising hub, no inlet guide vanes, two rotor–stator stages; the second stator is the outlet guide vane row and leaves the flow axial into the diffuser.

### 4.1 Stage data

| Quantity | Stage 1 | Stage 2 |
|---|---:|---:|
| Hub/tip at rotor LE | 0.64 (r 57.6) | 0.72 (r 64.8) |
| Inlet Tt / pt | 288.2 K / 1.013 bar | 331.7 K / 1.545 bar |
| Axial Mach / axial velocity at rotor LE | 0.40 / 135 m/s | 0.34 / 122 m/s |
| Work Δh / temperature rise | 43.7 kJ/kg / 43.5 K | 50.0 kJ/kg / 49.7 K |
| Stage total pressure ratio (η_s 0.85 / 0.86) | 1.525 | 1.528 |
| Loading ψ = Δh/U² at hub / mean / tip | 0.62 / 0.38 / 0.25 | 0.56 / 0.39 / 0.29 |
| Flow coefficient φ = Cx/U at mean | 0.40 | 0.34 |
| Rotor blade count / mean chord / mean solidity | 29 / 22 mm / 1.37 | 31 / 20 mm / 1.27 |
| Stator vane count / chord / mean solidity | 41 / 15 mm / 1.30 | 47 (OGV) / 14 mm / 1.34 |
| Blade-chord Reynolds number (rotor, mean) | 5.4 × 10⁵ | 6.7 × 10⁵ |
| Cold tip clearance / span | 0.25 mm / 32.4 mm (0.77 %) | 0.25 mm / 25.2 mm (0.99 %) |

### 4.2 Velocity triangles (free-vortex baseline, no inter-row swirl)

Rotor 1 (U at r 57.6 / 73.8 / 90.0 = 265 / 340 / 415 m/s):

| Radius | β₁ (rel. inlet) | W₁ (m/s) | M_rel | β₂ (rel. exit) | W₂ | ΔCθ | α₂ (abs. exit) | C₂ | de Haller W₂/W₁ | DF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hub | 63.0° | 298 | 0.89 | 36.7° | 169 | 165 | 50.5° | 213 | 0.57 | 0.59 |
| mean | 68.3° | 366 | 1.09 | 57.4° | 251 | 128 | 43.5° | 187 | 0.69 | 0.44 |
| tip | 71.9° | 436 | 1.30 | 66.4° | 338 | 105 | 37.9° | 172 | 0.77 | 0.33 |

Rotor 2 (U at r 64.8 / 77.4 / 90.0 = 299 / 357 / 415 m/s):

| Radius | β₁ | W₁ | M_rel | β₂ | W₂ | ΔCθ | α₂ | C₂ | de Haller | DF |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hub | 67.7° | 323 | 0.89 | 47.0° | 180 | 167 | 53.8° | 207 | 0.56 | 0.60 |
| mean | 71.1° | 377 | 1.04 | 60.5° | 249 | 140 | 48.9° | 186 | 0.66 | 0.47 |
| tip | 73.6° | 432 | 1.20 | 67.4° | 319 | 120 | 44.5° | 172 | 0.74 | 0.38 |

Stators (baseline removes all swirl): S1 turns 50.5°/43.5°/37.9° → 0° (hub/mean/tip); OGV turns 53.8°/48.9°/44.5° → 0°.

**Required redistribution.** Hub diffusion factors of 0.59–0.60 and stator turning above 50° exceed the comfortable limits (DF ≤ 0.55 hub, ≤ 0.45 tip; stator turning ≤ 40° per row). The blading step (section 13, steps 2–3) must deliver the same stage work with:

1. a controlled-vortex work distribution: hub work 85 %, tip work 115 % of the free-vortex value (raises tip DF to ~0.40, lowers hub DF to ~0.52);
2. 15–20° of co-rotating swirl left by S1 into R2 (reduces S1 turning to ~30° and R2 tip relative Mach to ~1.12; R2 work is restored by raising its exit swirl);
3. the OGV as a tandem pair (OGV-A 49° → 20°, OGV-B 20° → 0°) or a single row at solidity ≥ 1.8;
4. hub solidity 1.7–1.8 on both rotors (chord 24 mm at the hub tapering to 20 at the tip for R1; 22 → 18 for R2).

### 4.3 Baseline metal angles (circular-arc camber, Carter deviation; starting definition only)

| Row | Position | Inlet metal angle | Camber | Exit metal angle | Stagger (approx.) | Max thickness / chord |
|---|---|---:|---:|---:|---:|---:|
| R1 | hub | 62.0° | 32.7° | 29.3° | 45.6° | 8 % |
| R1 | mean | 67.3° | 14.0° | 53.3° | 60.3° | 5 % |
| R1 | tip | 71.4° | 7.6° | 63.8° | 67.6° | 3.5 % |
| S1 (baseline, 0° exit) | hub | 50.5° | 61.9° | −11.4° | 19.5° | 8 % |
| S1 | mean | 43.5° | 54.5° | −11.0° | 16.3° | 7 % |
| S1 | tip | 37.9° | 48.5° | −10.6° | 13.6° | 6 % |
| R2 | hub | 66.7° | 26.3° | 40.4° | 53.6° | 8 % |
| R2 | mean | 70.1° | 13.6° | 56.5° | 63.3° | 5 % |
| R2 | tip | 73.1° | 8.5° | 64.6° | 68.8° | 3.5 % |
| OGV (baseline, 0° exit) | hub | 53.8° | 65.3° | −11.5° | 21.1° | 8 % |
| OGV | mean | 48.9° | 60.4° | −11.5° | 18.7° | 7 % |
| OGV | tip | 44.5° | 56.0° | −11.5° | 16.5° | 6 % |

Incidence +1° at rotor hub/mean, +0.5° at rotor tips, 0° on stators; deviation from Carter's rule with m = 0.23 + α₂/500 (degrees) and δ = m θ/√σ. With the swirl option of 4.2 the stator cambers fall to 30–40° and the stator exit metal angles to +12 … +15°. Transonic tip sections (M_rel > 1.1) use multiple-circular-arc profiles with the forward 40 % of the camber nearly flat; leading-edge radius 0.3 mm (rotors), 0.25 mm (stators); trailing-edge thickness 0.5 mm.

### 4.4 Blisk geometry

| Feature | Rotor 1 | Rotor 2 |
|---|---|---|
| Blades | 29, radial stacking on the section centroids, no lean/sweep in v1 | 31, same |
| Hub flow surface | r 57.6 from z −8 (front hub extension) to z 0, then → 61.0 at z 16 (straight) | r 64.8 at z 42 → 66.5 at z 55 |
| Blade axial extent (hub) | z 0 … 16 | z 42 … 55 |
| Disc | web 10 mm thick at the bore, 6 mm at r 50; rim r 50 … 57.6 from z −8 to 16 under the front hub extension and the blade roots; bore Ø40 H6; axial extent z −8 … 24, seal arm to z −18 | same proportions; z 38 … 62 |
| Front/rear faces | front: face at z −8, 3 mm behind the trailing edge of the inlet-frame hub fairing (z −11); a seal arm (r 44 … 48.1, three teeth to Ø96.2) projects forward to z −18 inside the fairing's seal sleeve (bore Ø97, 0.4 mm radial gap); rear: spigot Ø100 that pilots the S1 seal spacer (OD Ø115, z 24 … 38, running 0.5 mm inside the S1 inner band) | front: face against the seal spacer; rear: seal sleeve OD Ø126 from z 62 to 70 running 0.5 mm inside the OGV inner band |
| Drive | 10 µm interference on the Ø40 drum, two Ø4 dowels per blisk, clamped axially (section 8) | same |
| Root fillet / tip | r 1.5 / flat tip at r 90.0, 0.8 mm thick | r 1.5 / r 90.0, 0.8 mm |
| Material | 2618-T61 forged bar (the turbocharger-wheel alloy, ~300 MPa yield at 150 °C), machined; Ti-6Al-4V option | 2618-T61; compressor exit ≤ 381 K static, ≤ 420 K across the V2 envelope; Ti-6Al-4V option if the clearance budget needs it |
| Mass | 0.9 kg | 1.0 kg |
| Balance | G2.5 single plane at 3,000 rpm, material removal on the rear face at r 45 | same |

Casing: three bolted aluminium rings (6061-T6), bore Ø180.5 over the rotors, 8 × M6 flanges on PCD 206, OD 200 (flanges 212): `case-r1` z −18 … 18, `stator-1` ring z 18 … 58 (vanes z 22 … 36 on an outer band r 90.0 … 93.5, then plain bore over R2), `ogv-ring` z 58 … 80 (vanes z 61 … 76). Over each rotor the bore carries a 0.5 mm-thick sprayed Al-Si/polyester abradable (rated to ~325 °C; filled epoxies soften near 120 °C, below the V2 compressor-exit temperature) machined to Ø180.5. Stator inner bands: 3 mm thick (inner surface r 58.0 for S1, r 63.5 for the OGV), each with a two-tooth labyrinth facing the rotating seal spacer (S1) or the rotor-2 rear sleeve (OGV) at 0.5 mm radial gap.

### 4.5 Off-design expectations

Free-vortex scaling with flow ∝ N: 45 % speed (idle, 19,800 rpm) OPR ≈ 1.21 and ~220 N; 60 % OPR 1.39, ~430 N; 80 % OPR 1.76, ~780 N. At low OPR there is no need for bleed or variable vanes (the NASA four-stage OPR 4 engine snap-accelerated without surge). The front stage will run at positive incidence at part speed; the stall margin at 100 % is to be verified at ≥ 15 % by the 3D CFD speed line and the rig.

## 5. Diffuser and combustor

### 5.1 Diffuser

Annular diffuser from station 3 (r 67.5 … 90.25, 111 cm², M 0.23) over z 80 … 115: outer wall r 90.25 → 95.0, inner wall 67.5 → 60.0, area ratio 1.53, half-angles 7.8° outer and −12° inner (the inner wall descends; the equivalent cone angle stays under 10°). At z 115 the flow dumps into the casing annulus (r 45 … 105, 283 cm²); the dome of the liner sits 25 mm downstream (z 140). Expected total-pressure loss 0.5 % (diffuser) + 1 % (dump). The inner wall continues as the bearing tunnel (OD 90) and carries a 2 % P3 bleed through 12 × Ø3 holes at z 125 into the tunnel for rear-bearing buffering and turbine-disc cooling.

### 5.2 Combustor sizing

| Quantity | Value |
|---|---|
| Casing annulus | r 45 … 105, A_ref 283 cm² |
| Inlet state | 2.35 bar, 381 K, ρ₃ 2.16 kg/m³ |
| Reference velocity | 37.7 m/s (casing), liner velocity ~5 m/s in the primary zone after splits |
| Flame tube | annular, r 55 … 97 (height 42 mm), z 140 … 300 (length 160 mm, L/H 3.8), area 200 cm², liner/casing ratio 0.71 |
| Air split (design) | primary 22 %, secondary 28 %, dilution 38 %, cooling 12 % |
| Primary-zone equivalence ratio | 22 % of the air through the primary holes plus ~8 % dome and film air entrained gives φ_pz ≈ 1.07 at design (f 0.0219 / 0.30 / 0.068) and ≈ 0.6 at idle (12 g/s fuel, 1.03 kg/s air) |
| Residence time (liner volume 3.2 L, bulk density ~0.6 kg/m³ at ~1400 K) | ~0.8 ms bulk; the primary-zone recirculation multiplies the effective time; drops would not burn out in this time, hence vaporisers rather than atomisers |
| Heat-release density ṁ_f LHV /(V_liner p₃) | 290 MW/(m³ bar): hobby micro-turbine class (a KJ66 is ~310), 5–8 times an aircraft combustor; combustion efficiency 0.95–0.97 expected, 0.90 planned for in the fuel system; liner can grow to 200 mm (L/H 4.8) at the expense of 40 mm of exhaust duct if the rig shows incomplete combustion |
| Total pressure loss | 5 % (3.5 % liner, 1.5 % diffuser and dump) |
| Exit temperature | 1150 K mean; pattern factor target ≤ 0.25; radial profile peaked at 60 % span |
| Fuel injection | 12 vaporiser tubes, Inconel 625, Ø8 × 0.5 wall, inserted axially through the dome at r 76 (mid liner height) to z 185, then bent 180° (R 12) in the circumferential direction, so the return leg also lies at r 76, 18° from the inlet leg, and ends open at z 160 pointing upstream into the primary zone; each fed by a Ø1.0 capillary from the fuel manifold; 4.2 g/s per tube at design |
| Ignition | 2 glow plugs (1/4-32 model type) at z 170, r 97, 180° apart, each with a start-fuel orifice Ø0.4 mm fed by the start solenoid ("kero-start") |
| Liner wall | Inconel 625, 0.8 mm; dome 1.0 mm; cooling by three rows of louvred film slots (60 × 1.2 mm slots per row at z 180, 220, 260 on both walls) |

Hole pattern (starting point, to be set by the flow-split calculation and cold-flow test): primary 2 rows × 24 Ø4.0 (outer liner z 165 and inner liner z 170, staggered 7.5°), secondary 24 Ø5.0 at z 205 (outer) and 24 Ø4.5 (inner), dilution 24 Ø7.0 at z 250 (outer) and 24 Ø6.0 (inner). Hole discharge coefficient 0.6 assumed. Keep the counts multiples of 12 to align with the vaporisers; avoid multiples of 17 and 23 (NGV and turbine blade counts).

Outer casing: 321 stainless, 1.0 mm rolled and seam-welded, ID 210, flanges at z 115 (to the diffuser) and z 322 (to the exhaust duct), OD 224 flanges with 12 × M6; bosses for 2 glow plugs, 12 vaporiser feed-throughs, 2 × p3 taps, 2 × T3. Inner casing (bearing tunnel): 321 SS tube OD 90 × 1.5 from z 115 to 322 carrying the rear bearing housing (section 8).

### 5.3 Risk and first-run plan

Reference velocity 38 m/s is at the high end of practice for this class (the TRI 60 is similar; textbook micro combustors use 12–30 m/s). The first light-offs run at 80 % of design flow (N ≈ 80 %) and the hole pattern is adjusted on the atmospheric combustor rig (section 15) before the engine sees design flow. If stability is marginal, the casing radius grows to 113 mm (240 mm engine, V_ref 34 m/s) — a casing, liner and NGV-flange change, nothing else.

## 6. Turbine

Single stage, uncooled, zero exit swirl, 56 % reaction at the mean radius.

| Quantity | Value |
|---|---|
| Mean radius / blade height | 70.0 mm / 44.8 mm (r 47.6 … 92.4) |
| Blade speed U_m / tip speed | 323 m/s / 426 m/s |
| Work / loading ψ = Δh/U_m² / flow coefficient φ | 92.5 kJ/kg / 0.89 / 0.65 (Cx 210 m/s) |
| NGV exit (station 4.5) | α₂ 54°, C₂ 355 m/s, M 0.55, static 1.78 bar, 1095 K |
| Rotor relative inlet / exit | β₂ −10° (W 213 m/s) / β₃ 57° (W 385 m/s); turning 67° |
| Exit | axial, C₃ 210 m/s, M 0.33, Tt5 1070 K |
| NGV | 17 vanes, chord 26 mm (axial ~20), solidity 1.12, throat 9.6 mm at the mean, trailing edge 0.8 mm; one-piece ring with inner and outer platforms, z 300 … 322 |
| Rotor | 23 blades, chord 20 mm (axial ~16), solidity 1.41 at the mean, Zweifel 0.78, z 327 … 345; tapered 3.5 mm root to 1.2 mm tip thickness; tip at r 92.4, flat, 0.40 mm cold clearance to the shroud bore r 92.8 |
| Disc | hub r 47.6, web 12 mm at r 30, 20 mm rim thickness; **no central bore**: integral stub shaft forward — Ø30 to a shoulder at z 295, Ø25 h5 bearing journal z 280 … 295, Ø24 seat with a 6 × 6 key z 270 … 280, M20 × 1.5 thread z 262 … 270 |
| Coupling hub | separate 17-4PH H1025 hub, keyed on the Ø24 seat after the rear bearing is fitted: flange Ø60 × 8 at z 262 … 270 (6 × Ø5.3 on PCD 50, Ø44 × 2 centring spigot entering the drum flange), sleeve OD 40 to z 280 (OD 32 at its rear face); an M20 × 1.5 thin nut in its Ø34 front counterbore clamps the hub and the bearing inner race against the stub shoulder |
| Stresses (estimates) | blade root 320 MPa centrifugal (0.6 taper factor); disc 160 MPa centre (solid) + rim load; coupling-hub flange 60 MPa |
| Metal temperatures (estimates) | blade mid-span 1000–1050 K, root 950 K, disc rim 900 K, disc centre 700 K with the tunnel cooling flow |
| Material | investment-cast IN713LC to AMS 5377, HIP optional, machined journal, key seat, thread and tip; retire at 25 h |
| Mass | 2.6 kg including the stub |

NGV material: LPBF Haynes 282 (solution 1250 °C option per the heat-treatment literature) or investment-cast IN713C; the ring bolts to the combustor casing flange at z 322 through an outer flange (OD 224) and locates the liner exit on a sliding spigot (inner r 47.6 lip, outer r 92.4 lip, 0.3 mm gaps for thermal growth). Shroud: integral with the exhaust duct, 321 SS, 20 mm long, bore Ø185.6, optional 1 mm brazed IN625 honeycomb.

## 7. Exhaust duct and nozzle

- Duct: 321 SS 0.8 mm, from the turbine shroud (r 92.4 bore at z 352) converging linearly to r 72 at z 470; flange OD 224 at z 322 (shared with the NGV ring), 12 × M6.
- Tail cone: 321 SS 0.8 mm, from r 47.6 at z 352 to a rounded point at z 470, carried by 4 NACA-section struts (8 mm thick, 30 mm axial chord) at z 365 … 385; struts spaced 90°, one on +x; EGT probes enter beside the struts at z 360.
- Nozzle ring: bolt-on, z 470 … 500, bore converging from r 72 to r 64 (D₉ 128) over 25 mm (18° half-angle), then a 5 mm straight exit; trim set D₉ = 120, 124, 128, 132, 136 (±6 % area). Exit Mach 0.85 at design; the nozzle never chokes dry (NPR 1.57 < 1.85).
- Aircraft tailpipe (not part of the engine): bore ≥ 150 mm, length ≤ 600 mm, with a 10 mm annular ejector gap at the nozzle for bay cooling.

## 8. Rotor system

### 8.1 Layout (TRI 60 pattern: front bearing ahead of the compressor, rear bearing ahead of the turbine)

| Element | Definition |
|---|---|
| Drum shaft | 17-4PH H1025 tube Ø40 h6 × Ø28 from z −45 to 254; solid front section with Ø25 h5 journal z −75 … −40, thread M20 × 1 (LH) z −90 … −75 for the nose nut and starter clutch; shoulder Ø46 × 6 at z −14 … −8 (R1 front stop); thread M39 × 1.5 at z 62 … 72 for the stack nut; flange Ø60 × 8 at z 254 … 262, 6 × M5 on PCD 50, Ø44 H7 × 2 recess in its rear face for the coupling-hub spigot |
| Rotor stack (front to back) | nose nut with the starter clutch cup (z −95 … −75) → front bearing pair inner races + spacer (against the Ø25/Ø40 step at z −40) → **blisk 1** (z −8 … 24, seal arm to z −18, against the Ø46 shoulder) → S1 seal spacer (OD Ø115 × ID Ø40, z 24 … 38) → **blisk 2** (z 38 … 62, with its rear seal sleeve to z 70) → stack nut (z 62 … 72) → drum → drum flange (z 254 … 262) bolted to the coupling hub (z 262 … 280) → rear bearing (z 280 … 295) on the **turbine stub**, clamped by the hub and the stub nut against the shoulder at z 295 → turbine disc (z 318 … 352) |
| Front bearing | 2 × 25 × 52 × 15 hybrid angular-contact (Si₃N₄ balls, 15° contact, P4), back-to-back, light preload (~50 N spring-free, clamped), steel outer rings in a 6061 housing with two Viton O-rings as a squeeze-film damper; takes the net axial load (~700 N forward at design) |
| Rear bearing | 1 × 25 × 52 × 15 hybrid angular-contact or deep-groove, outer ring floating axially with a wave-spring preload of 80 N, O-ring damped, in a 321 SS housing inside the tunnel at z 278 … 300; buffer air from the 2 % bleed, oil mist from the fuel system |
| Lubrication | 4.5 % synthetic turbine oil in the fuel; two Ø0.5 × 300 mm metering capillaries from the pump outlet, ~5 ml/min each; mist vents through labyrinths into the inlet (front) and the turbine disc cavity (rear) |
| Seals | labyrinths: Ø96 front of blisk 1 (3 teeth, 0.4 mm), blisk spigots to stator bands (2 teeth, 0.4 mm), tunnel front at z 130 (3 teeth, 0.3 mm) |
| Balance | blisks and the wheel (with its bearing inner race, coupling hub and nut fitted) individually to G2.5; assembled rotor in two planes (blisk 1 rear face, turbine disc front face) to residual unbalance ≤ 1 g mm per plane at 3,000 rpm; journal runout ≤ 10 µm TIR |
| Rotor dynamics requirement | first bending mode ≥ 1.25 × 44,000 rpm (≥ 917 Hz) with bearing stiffness 1–3 × 10⁷ N/m; rigid-body modes on the O-ring mounts below 13,000 rpm; verified with ROSS (section 13, step 6) before manufacture, and by a slow run-up with proximity probes before the first hot run |
| Stored energy / containment | 64 kJ at 44,000 rpm; all runs above 5,000 rpm inside a containment ring (10 mm steel band over the compressor, 12 mm over the turbine plane) in a remote-operated cell |

### 8.2 Axial and radial clearance budget (cold → design)

| Gap | Cold | Centrifugal | Thermal | Running (design) |
|---|---:|---:|---:|---:|
| R1 tip to bore | 0.25 | −0.10 (blisk growth) | −0.02 (blisk warm, case cooler) | ~0.13 |
| R2 tip to bore | 0.25 | −0.11 | −0.07 (blisk at 381 K, case at ~350 K) | ~0.07 (Ti blisk: ~0.11) |
| Turbine tip to shroud | 0.40 | −0.10 | −0.15 (wheel 1000 K vs shroud 900 K and larger casing growth) | ~0.15 |
| Rotor axial position (front DB pair fixes it) | – | – | drum growth +0.4 mm at the turbine | NGV–rotor axial gap 5.0 → 4.6 |

If the R2 running clearance proves too small on the rig (rub marks), switch R2 to Ti-6Al-4V or open the cold gap to 0.30 mm.

### 8.3 Starter

1 kW-class outer-rotor brushless motor (Ø50 × 35, 22–28 V) inside the nose cone: its body (z −143 … −108) is mounted on a bulkhead at z −108 … −105 and its shaft drives a one-way needle clutch (rated ≥ 2 N m, z −105 … −95) that engages the cup on the nose nut. It cranks the spool to 5,000 rpm (11 % N) for light-off in ≤ 10 s: the compressor absorbs about 0.3 kW there (215 kW × (5,000/44,000)³, 0.6 N m), seals and bearings add ~0.1 N m, and the rotor (6 g m²) stores 0.8 kJ. After light-off it assists to ~11,000 rpm (25 % N), where the turbine accelerates the spool on its own and the clutch overruns. Wires leave through the bulkhead, the hub and the +x strut. No shaft generator in the first article (28 V battery for the test cell); an integral starter-generator inside the hub fairing is the growth option (section 16).

## 9. Inlet

- Test configuration: a bolt-on bellmouth lip (z −98 … −72) on the `inlet-frame` front flange (z −72 … −67, OD 224), the quarter-ellipse running from r 125 at z −95 through r 95.8 at the flange to r 90.25 at z −45, then cylindrical to the rear flange (z −24 … −18, OD 212), which bolts to `case-r1` at z −18; 5 struts (symmetric 12 % section, 30 mm axial chord, 12 mm max thickness) at z −70 … −40 from the hub (r 32) to the wall, one on +x carrying the oil-mist, starter and instrumentation lines; the hub is the front bearing housing (bore Ø52 H6, z −75 … −35) and continues as a 3 mm fairing that rises from r 32 at z −40 to r 57.6 at z −15 and ends at z −11, 3 mm ahead of the R1 hub, carrying the front seal sleeve (bore Ø97, z −21 … −11); the nose cone closes the front (Ø64 cylinder z −80 … −130, tangent ogive to the tip at z −165) and houses the starter (section 8.3).
- Compressor-face conditions assumed: pt2 = p0 (bellmouth), distortion < 2 %, no inlet swirl.
- Aircraft duct (separate project): throat ≥ 140 cm² (D_eq 133 mm, throat Mach 0.45 at 2.3 kg/s static), diffusing to the 150 cm² compressor face with ≤ 3 % total-pressure loss and ≤ 5 % circumferential distortion at the face; a dorsal S-duct from a BD-5-style scoop is the expected shape; the bellmouth lip is replaced by a short duct adapter on the same z −72 flange (the V2 pitot-inlet duct uses the same flange).

## 10. Fuel, ignition, control and instrumentation

| System | Definition |
|---|---|
| Fuel | Jet A-1 or kerosene + 4.5 % synthetic turbine oil; design flow 50.5 g/s (3.8 L/min), idle ~12 g/s |
| Pump | brushless gear pump, ≥ 7 L/min at 10 bar (micro-turbine class or industrial), PWM/analog controlled, fuel flowmeter (turbine type) downstream. Sized for flight: ram raises the airflow ~15 % at BDXL speeds and ~40 % at V2's low-altitude limit, where the core needs 5.1 L/min against a 3.3 bar combustor |
| Valves | manual shutoff cock, normally-closed main solenoid, start-fuel solenoid; the main solenoid closes on loss of power |
| Manifold | 321 SS ring Ø6 × 1 at r 118, z 125, 12 × Ø1.0 capillaries to the vaporisers; bearing capillaries teed from the pump outlet |
| Ignition | 2 glow plugs (12 V, 30 A each for 20 s) with start fuel at 2 g/s each; spark ignition as a growth option |
| Control (test cell) | deterministic PID speed governor with EGT, acceleration and deceleration limits, implemented on a microcontroller with a reviewed state machine (off → crank → light-off → warm-up → idle → run → cool-down) and logged at 100 Hz; the main throttle demand comes from the test-stand console, never from an autonomous agent. Flight provisions (BDXL and V2): speed scheduled as corrected speed N/√θ₂ from Tt2 and pt2 at the compressor face; spare driver and input channels for a reheat pump, a pilot igniter and a nozzle actuator with position feedback; a CAN port for a second engine and the flight computer |
| Independent protection (hardwired relay logic, separate speed pickup) | overspeed > 48,400 rpm; EGT > 1,120 K (any probe); loss of speed signal > 0.3 s; bearing housing > 150 °C; vibration > 20 mm/s rms; flame-out (EGT falling > 100 K/s while fuel on); E-stop; each closes the main solenoid and keeps the lube/cooling air logic as designed for coast-down |
| Measurements (first article) | N (2 eddy-current probes in `case-r1` over the R1 tips, 29 pulses per revolution; they also read tip clearance), Tt2 (2), pt2/bellmouth Δp (airflow; in flight a Kiel probe on the +x strut gives pt2), ps3 (2 wall taps), pt3 (Kiel at OGV exit, +x), Tt3 (2), ps4 (1, liner exit, optional), Tt5 (4 × K-type at z 360, 90° apart), ps5 (2), fuel flow, fuel pressure, bearing temperatures (2), accelerometers (2 radial + keyphasor), thrust (load cell, 2 kN), ambient p/T/RH, vaporiser manifold pressure |
| Data | immutable raw log per run with configuration hash (engine build, nozzle ring, software version, calibration ids); derived performance in a separate file |

## 11. Materials and manufacturing

| Part | Material | Process | Finish / inspection | Notes |
|---|---|---|---|---|
| Blisks R1, R2, seal spacer | 2618-T61 forged bar (Ti-6Al-4V option) | 5-axis milling from forged bar, flank milling of blades | Ra ≤ 0.8 µm on airfoils; CMM on 3 sections per blade (4 blades) and hub/bore; dye penetrant; balance | drawings call metal angles at 5 sections |
| Stator-1 ring, OGV ring | 6061-T6 (2618-T61 option) | 5-axis milling (vanes integral with both bands) or LPBF AlSi10Mg + machined bands | Ra ≤ 1.6 µm; CMM; throat gauge | split rings not needed with the stacked casing |
| Casing rings, diffuser-tunnel front half, inlet-frame, bellmouth lip, nose cone | 6061-T6 | turning + milling; inlet-frame struts machined or printed in AlSi10Mg and bonded/bolted | bore Ø180.5 H7 concentric to the bearing bores within 0.03 TIR | abradable bonded and machined in situ |
| Drum shaft | 17-4PH H1025 | turning, grinding of journals and seats | journals Ø25 h5, runout ≤ 5 µm, bore honed | magnetic particle |
| Combustor outer/inner casing | 321 stainless 1.0 / 1.5 mm | rolled, TIG seam-welded, flanges turned and welded | pressure test 6 bar | – |
| Liner | Inconel 625 0.8 mm (dome 1.0) | rolled, laser-cut holes and slots, TIG-welded, louvres formed | weld inspection, hole count/size audit | – |
| Vaporisers, manifold | Inconel 625 tube Ø8 × 0.5; 321 SS Ø6 × 1 | bent, brazed (BNi-2) | flow-matched ±3 % per tube on a water bench | – |
| NGV ring | Haynes 282 (LPBF, HIP, solution 1135–1250 °C + age) or cast IN713C | print/cast, machine flanges and lips | CT or radiography; throat gauge all 17 passages | – |
| Turbine wheel + stub | IN713LC, AMS 5377, investment cast (HIP recommended) | cast, machine journal/key seat/thread/tip | CT of the disc; FPI; cold spin to 115 % (50,600 rpm) in a spin pit with growth measurement | retire at 25 h |
| Coupling hub, stub nut | 17-4PH H1025 | turning, keyway broaching, grinding | bore Ø24 H6, flange face runout ≤ 5 µm | balanced with the wheel |
| Exhaust duct, tail cone, nozzle rings | 321 stainless 0.8 mm | rolled/spun, welded | – | nozzle rings turned |
| Bearings | 25 × 52 × 15 hybrid angular-contact, P4, 15° (e.g., GRW, Barden, SKF hybrid lines) | purchased | cert | 3 per engine + spares |
| Starter | 1 kW-class outer-rotor BLDC (Ø50 × 35) + one-way needle clutch (≥ 2 N m) | purchased + machined bulkhead | – | – |

Every part carries a serial, a material certificate, the as-built CMM record and its balance report in the traveller; the engine build record lists them with the clearances measured at assembly.

## 12. Mass budget

| Group | Mass (kg) |
|---|---:|
| Blisks (0.9 + 1.0) | 1.9 |
| Stator-1 and OGV rings | 1.0 |
| Casing rings, diffuser-tunnel (Al part) | 1.8 |
| Inlet-frame, nose cone | 1.5 |
| Drum shaft, nuts, spacers | 1.6 |
| Bearings and housings | 0.6 |
| Combustor outer and inner casings | 2.0 |
| Liner, vaporisers, manifold | 1.5 |
| NGV ring | 1.2 |
| Turbine wheel with stub | 2.6 |
| Exhaust duct, tail cone, nozzle ring | 1.8 |
| **Bare engine, bottom-up estimate** | **17.5** |
| Starter, pump, valves, igniters, harness, sensors | 2.5 |
| **Dry engine with accessories, estimate** | **20.0** |
| **Target after weight work** (thinner flanges, pocketed casing rings, Ti bolts, 0.6 mm exhaust) | **16.0** |

Static thrust-to-weight 5.8 at the estimate and 7.4 at the target (1,169 N). CG estimate: z ≈ 200 mm (combustor front flange); rotor polar inertia 6.0 g m².

## 13. Analysis plan

Each step names its tool, inputs, outputs and the acceptance that releases the next step. Steps 1–3 and 6 are gates; nothing is machined before they pass.

| # | Analysis | Tool | Inputs | Outputs / acceptance |
|---|---|---|---|---|
| 1 | Cycle and sizing | Appendix A script; cross-check in pyCycle | Section 3 values | Station table reproduced within 1 %; sensitivity to η_c, η_t, TIT, Δp_b, nozzle area; operating line vs N |
| 2 | Compressor meanline and throughflow | MULTALL-OPEN `meangen` + `stagen`, or T-AXI `tcdes`/`taxi`; TurboDesigner as a cross-check | Section 4.1–4.2, controlled-vortex and swirl rules of 4.2 | Hub DF ≤ 0.55, tip DF ≤ 0.45, de Haller ≥ 0.65 on every row at the hub, stator turning ≤ 40° per row, tip M_rel ≤ 1.32; blade sections at 5 radii per row |
| 3 | Compressor 3D CFD | MULTALL-OPEN `multall` (multistage, mixing planes), then SU2 or OpenFOAM compressible on the final geometry | Step-2 geometry, tip clearance 0.15 mm running | At 100 % N: OPR ≥ 2.25 at 2.3 kg/s, η_tt ≥ 0.82 per stage, stall margin ≥ 15 %; 60 % and 80 % speed lines; a validation run on the TUDa OpenStage case first |
| 4 | Turbine meanline and blading | TurboFlow (meanline), T-Blade3 sections, MULTALL stage CFD | Section 6 | η_tt ≥ 0.86, NGV throat area within 2 % of the required flow capacity, exit swirl ≤ 5°, Zweifel 0.7–0.9 |
| 5 | Combustor | Lefebvre-method flow split spreadsheet, Cantera PSR/PFR network for primary-zone residence and blow-out, cold-flow OpenFOAM of the liner | Section 5 | Δp 4–6 %, φ_pz 1.0–1.1 at design and ≥ 0.6 at idle, primary-zone residence ≥ 1 ms, pattern factor estimate ≤ 0.25; hole pattern frozen for the rig |
| 6 | Rotor dynamics | ROSS (shaft elements for drum and stub, lumped blisks/wheel, bearing stiffness 1–3 × 10⁷ N/m, O-ring damping 0.05–0.1) | Section 8 masses and dimensions | First bending ≥ 917 Hz or a documented supercritical passage below 50 % N with damping ratio ≥ 0.05; unbalance response ≤ 25 µm at the bearings for 1 g mm per plane; Campbell diagram with 1×, 2×, 5× (struts), 17×, 23×, 29×, 31×, 41×, 47× lines |
| 7 | Blisk and wheel stress and modes | CalculiX (in the pipeline for displacement and modal; standalone for stress), hot properties for IN713LC at 950 K | Section 4.4, 6 | Blisk: peak von Mises ≤ 0.6 σ_y at 110 % N; tip radial growth ≤ 0.15 mm; first blade mode ≥ 2 kHz, no crossing of 17×, 23× (turbine) or 41×, 47× (stators) within ±10 % of 100 % N; wheel: blade root ≤ 350 MPa, disc centre ≤ 450 MPa at 110 % N and 950 K; burst margin ≥ 1.4 on speed; casings, liner and flanges at the section 2.4 design loads (1.5 × static pressures, 64 N m torque, 6 g), with 2618-T61 properties at 420 K for the blisks |
| 8 | Thermal | hand calculation + CalculiX steady thermal of the wheel and NGV with assumed convective coefficients | Section 6 metal temperatures | wheel rim ≤ 950 K, blade ≤ 1050 K at TIT 1150; tunnel bleed sized for a disc-centre ≤ 750 K |
| 9 | Containment and energy | hand calculation (Hagg–Sankey or equivalent) | 64 kJ rotor, blade release cases | ring thicknesses of section 8.1 confirmed by a specialist |
| 10 | Starting | shaft inertia model: J dω/dt = τ_starter + τ_turbine − τ_compressor − τ_loss | step 1 off-design, starter torque curve | light-off at ≤ 20 % N, self-sustaining at ≤ 45 % N, idle within 60 s |

## 14. opencad implementation

Two machines, run in order. Both are `Goal: assembly` (bodies move relative to each other, an operating speed, predictions). The source packet for `/initialize-cad` is this document (section 3.2 is the flow-path table) and, optionally, the blade-section coordinate files produced by step 2 of the analysis plan; in the absence of section files the worker builds the baseline sections from the metal angles of section 4.3 with circular-arc camber lines and NACA-65 thickness.

### 14.1 Machine 1: `axjet-c2`, the compressor module

Purpose: the hardest geometry first (two blisks, two vane rings, the stacked casing, the inlet frame, the drum), with a cold-flow MRF sanity case and the blisk structural/modal cases, before the hot section exists.

Assembly frame as in section 3. Datum part: `case-r1`.

| Body | Kind | Design | Own frame | Intent (summary) | Material / density |
|---|---|---|---|---|---|
| `case-r1` | modelled | `axjet-c2-case-r1` | assembly frame | ring z −18 … 18, bore Ø180.5, OD 200, front and rear flanges OD 212 with 8 × Ø6.4 on PCD 206 (one hole on +x), 0.5 mm abradable recess z −2 … 18 | 6061-T6, 2700 |
| `bellmouth` | modelled | `axjet-c2-bellmouth` | assembly frame | bolt-on test lip z −98 … −72: quarter-ellipse inner contour from r 125 at z −95 to r 95.8 at its rear face, 3 mm rounded lip, outer skin from r 131 back to the flange at OD 224, 8 × Ø5.5 on PCD 216 | 6061-T6, 2700 |
| `inlet-frame` | modelled | `axjet-c2-inlet-frame` | assembly frame | front flange z −72 … −67 (OD 224, 8 × M5 on PCD 216), inner contour continuing the bellmouth ellipse from r 95.8 at z −72 to r 90.25 at z −45, cylindrical to z −18 with a rear flange (z −24 … −18, OD 212, 8 × Ø6.4 on PCD 206) mating `case-r1`; hub r 32 from z −80 to −40 with bore Ø52 H6 z −75 … −35, then a 3 mm fairing rising to r 57.6 at z −15 and ending at z −11, with a seal sleeve (bore Ø97) z −21 … −11; five struts at z −70 … −40 (one on +x), 12 mm thick, from r 32 to the wall | 6061-T6, 2700 |
| `nose-cone` | modelled | `axjet-c2-nose-cone` | own origin at the hub front face (assembly z −80) | Ø64 cylinder z −80 … −130, tangent ogive to the tip at z −165, 2 mm wall; internal starter bulkhead 3 mm thick at z −108 … −105 with the motor's 4 × M3 pattern and a Ø12 shaft hole; 4 × M3 to the hub | 6061-T6 |
| `rotor-1` | modelled | `axjet-c2-rotor-1` | own origin at the LE plane (assembly z 0), axis +z | blisk per section 4.4: 29 blades, hub 57.6 → 61.0 over z 0 … 16 behind a front hub extension at r 57.6 from z −8, tip r 90.0, disc z −8 … 24, front seal arm r 44 … 48.1 with three teeth to z −18, bore Ø40, spigot Ø100 rear; blade sections from 4.3 (or step-2 files) | 2618-T61, 2760 |
| `stator-1` | modelled | `axjet-c2-stator-1` | assembly frame | ring z 18 … 58: outer band r 90.0 … 93.5 (vanes z 22 … 36, 41 vanes, chord 15, metal angles 4.3), inner band r 61.0 → 64.5 (z 20 … 38), 3 mm thick with its inner surface at r 58.0 carrying a two-tooth labyrinth facing the seal spacer; plain bore r 90.25 over z 40 … 58 with abradable recess; OD 200, flanges as `case-r1` | 6061-T6, 2700 |
| `seal-spacer` | modelled (ring) | `axjet-c2-seal-spacer` | own origin at its front face (assembly z 24) | ring OD 115, ID 40, length 14, piloted on the rotor-1 rear spigot; runs 0.5 mm inside the S1 inner band | 2618-T61, 2760 |
| `rotor-2` | modelled | `axjet-c2-rotor-2` | own origin at its LE plane (assembly z 42) | 31 blades, hub 64.8 → 66.5 over z 0 … 13 (own frame), tip 90.0, disc z −4 … 20 (assembly 38 … 62), bore Ø40, rear seal sleeve OD 126 × ID 60 from z 20 to 28 (assembly 62 … 70) | 2618-T61, 2760 |
| `ogv-ring` | modelled | `axjet-c2-ogv-ring` | assembly frame | ring z 58 … 80: 47 vanes z 61 … 76, chord 14, inner band r 66.5 → 67.5 with its inner surface at r 63.5 and a two-tooth labyrinth facing the rotor-2 sleeve; outer band r 90.0 … 93.5; rear flange to the diffuser | 6061-T6, 2700 |
| `drum-shaft` | modelled | `axjet-c2-drum-shaft` | own origin at the R1 LE plane (assembly z 0), axis +z | per section 8.1 from the nose thread (z −90) to the coupling flange (z 262): Ø25 journal z −75 … −40, Ø46 shoulder at z −8, Ø40 drum, M39 thread z 62 … 72, Ø60 flange z 254 … 262 with a Ø44 H7 × 2 recess in its rear face | 17-4PH, 7800 |
| `bearing-front` | modelled (simple ring) | `axjet-c2-bearing-front` | own origin at its front face (assembly z −72) | ring OD 52, ID 25, length 30 (the DB pair as one envelope ring), 0.5 mm chamfers | steel, 7800 |
| `stack-nut` | modelled | `axjet-c2-stack-nut` | own origin at its front face (assembly z 62) | ring OD 56, ID 39, length 10 with 6 spanner notches | 17-4PH |
| `starter` | purchased | – | catalog cylinder | point (0, 0, −143) in the assembly frame, axis +z, Ø50 × 35 (z −143 … −108), inside the nose cone | – |
| `air` | derived (fluid) | – | – | plenum cylinder r 150, z −220 … −95 (ambient side) plus the bellmouth interior and the compressor annulus to the outlet cap at z 90 (annulus r 67.5 … 90.25), minus rotor-1, seal-spacer, rotor-2, drum-shaft, stator-1, ogv-ring, inlet-frame hub/struts, nose-cone; walls: bellmouth, inlet-frame, case-r1, stator-1, ogv-ring, nose-cone; inlet cap at z −220 (disc r 150), outlet cap at z 90; seed (0, 0, −200), ahead of the nose tip; expected volume ≈ 1.2 × 10⁷ mm³ ± 20 % | – |

Joints: `rotorSpin` revolute, parent `case-r1`, child `drum-shaft`, axis +z through the origin, `drive: motor`, `case_value: speedRpm`; `rotor1OnDrum`, `spacerOnDrum`, `rotor2OnDrum`, `stackNutOnDrum` rigid (child frames at their own origins on the drum at assembly z 0, 24, 42, 62); `inletFrameOnCase`, `bellmouthOnFrame`, `stator1OnCase`, `ogvOnCase`, `noseOnInlet`, `starterOnNose`, `bearingFrontInHub` rigid; `airFixed` rigid to `case-r1`.

Operating cases: `cold` (development): speedRpm 8,000, flowLMin 20,900 (0.418 kg/s at 1.204 kg/m³), air 1.204 kg/m³ / 1.813 × 10⁻⁵ Pa s; `design` (held out, no fluid simulation): speedRpm 44,000.

Observables:
- `dpCold`: `pressure_rise` (outlet static minus inlet static) from `mrfCold`, case `cold`; meanline expectation ≈ 2.9 kPa static-to-static (3.2 kPa total-to-total scaled by (8/44)²) — class X, an estimate, not a reference;
- `torqueCold`: `torque` from `mrfCold` ≈ 1.5 N m;
- `rotor1TipGrowth`: `max_displacement` from `rotor1Stress`, case `design`, body `rotor-1`, max 0.20 mm (expect 0.10–0.15);
- `rotor1Mode1`: `natural_frequency_1` from `rotor1Modal`, min 2,000 Hz.

Simulations:
- `mrfCold`: `cfd_steady` / `openfoam`, bodies [`air`, `rotor-1`, `rotor-2`, `drum-shaft`] rotating about the `rotorSpin` axis, `flow_key: flowLMin`, `speed_key: speedRpm`, `inlet_diameter_mm: 300`, `cell_mm: 6`, `surface_level: 3`, `iterations: 1500`, `processes: 8`; regions `tip1` and `tip2` (`rotor_tip` about each rotor: inside 1.0, outside 1.5, axial margin 3 mm); refinement `[1.0, {factor: 0.8, regions: {tip1: 1, tip2: 1}}, {factor: 0.64, regions: {tip1: 1, tip2: 1}}]` so each step refines everywhere; timeout 36,000 s. Expect `resolved: false` on the first ladder (FAN-01 experience) and treat the result as a geometry check.
- `rotor1Stress`: `structural_static` / `calculix`, body `rotor-1`, case `design`, fixed boundary: the bore face, E 74.5 GPa, ν 0.33, ρ 2760 (2618-T61); mesh 1.5 mm; refinement `[1.0, 0.7, 0.5]`.
- `rotor1Modal`: `modal` / `calculix`, body `rotor-1`, fixed bore, 6 modes.

Acceptance: clearances `rotor1Tip` (rotor-1 to case-r1, min_gap 0.20), `rotor2Tip` (rotor-2 to stator-1, min_gap 0.20), `rotor1ToStator1` (min_gap 4.0, the axial row gap), `rotor2ToOgv` (min_gap 4.0), `rotor1ToInletFrame` (min_gap 0.3, the front labyrinth; the 40 mm strut-to-blade distance is checked by a dimension between the strut trailing-edge face and the rotor-1 LE plane), `spacerSeal` (seal-spacer to stator-1 min_gap 0.4), `sleeveSeal` (rotor-2 to ogv-ring min_gap 0.4); motion `spin` on `rotorSpin` over 0 … 12.41° (one R1 pitch) in 12 steps with interference tolerance 0.05.

Expected part-pipeline difficulty: the blisks are lofted multi-section blades on a revolved hub (the SPLEEN blade and FAN-01 rotor are the closest precedents); stator rings are the same loft between two bands; everything else is turned geometry with flanges and patterns. Budget one correction turn per blade row.

### 14.2 Machine 2: `axjet`, the complete engine

Adds the hot section and reuses the module's part designs by copying their contracts (the pipeline does not share designs between machines; the leaf names stay the same under `designs/axjet/parts/`).

| Body | Kind | Intent (summary) | Material |
|---|---|---|---|
| all of 14.1 except `air` | as above | unchanged | – |
| `diffuser-tunnel` | modelled | z 80 … 322: annular diffuser (outer wall r 90.25 → 95 over z 80 … 115 ending in a flange OD 224 at z 115; inner wall 67.5 → 60 over z 80 … 115, then a cone to r 45 at z 130), the bearing tunnel tube OD 90 × 1.5 to z 322 with 12 × Ø3 bleed holes at z 125, the rear bearing housing bore Ø52 H6 at z 278 … 300 with an O-ring groove, a three-tooth labyrinth bore Ø60 at z 130; the front part is aluminium, the tunnel is stainless (model as one body; note the joint in the brief) | 6061-T6 / 321 SS |
| `comb-outer-case` | modelled | tube ID 210 × 1.0 from z 115 to 322 with flanges OD 224 (12 × Ø6.4 on PCD 216, one on +x) at both ends; bosses: 2 glow-plug M10 at z 170 (±y), 12 × Ø9 vaporiser feed-throughs at z 140 on r 105 every 30° (first at +x), 2 × p3 taps Ø3 at z 125 | 321 SS |
| `liner` | modelled, 1 solid | outer liner r 97 × 0.8 and inner liner r 55 × 0.8 from z 140 to 300 joined by the dome (1.0 mm, flat with a 6 mm edge radius) at z 140 with 12 × Ø8.2 vaporiser holes at r 76 every 30°; hole rows per section 5.2 (primary 2 × 24 Ø4, secondary 24 Ø5 outer / 24 Ø4.5 inner, dilution 24 Ø7 outer / 24 Ø6 inner); three film-slot rows modelled as 60 × 1.2 × 6 mm slots at z 180, 220, 260 on both walls; exit transition z 285 … 305 from r 55/97 to r 47.6/92.4 with 0.3 mm sliding lips | Inconel 625 |
| `vaporizer-set` | modelled, 12 solids | 12 Ø8 × 0.5 tubes: straight from r 105 (casing) radially inward to r 76 at z 135, then axially +z through the dome to z 185, a 180° bend (R 12) in the circumferential direction (+θ) and a return leg at r 76, 18° from the inlet leg, ending open at z 160; feed capillary not modelled | Inconel 625 |
| `ngv-ring` | modelled | 17 vanes z 300 … 322 between platforms r 47.6 (inner, 4 mm thick) and 92.4 (outer, 4 mm thick); outer flange OD 224 at z 318 … 322 matching the casing bolts; inner lip Ø95.2 bore for the liner exit; vane sections: inlet metal 0°, exit 54°, chord 26, max thickness 18 % (uncooled solid), TE 0.8 mm | Haynes 282 / IN713C |
| `turbine-wheel` | modelled | own origin at the blade LE plane (assembly z 327): disc per section 6 (hub r 47.6, rim 22 mm wide z −2 … 20 own frame, web 12 mm tapering, no bore), 23 blades z 0 … 18 own frame, tip r 92.4, sections: inlet metal −10°, exit 57°, chord 20, thickness 3.5 → 1.2 mm; integral stub forward: Ø30 from the disc to a shoulder at z −32 own (assembly 295), Ø25 h5 journal to z −47 (assembly 280), Ø24 key seat to z −57 (assembly 270), M20 × 1.5 thread to the front end at z −65 (assembly 262) | IN713LC, 7910 |
| `coupling-hub` | modelled | own origin at its flange face (assembly z 262): flange Ø60 × 8 (6 × Ø5.3 on PCD 50) with a Ø44 × 2 centring spigot forward, sleeve OD 40 to z 18 own (OD 32 over its last 2 mm), bore Ø24 H6 with a 6 mm keyway, Ø34 × 8 front counterbore; the M20 thin nut is modelled as part of the hub | 17-4PH, 7800 |
| `bearing-rear` | modelled (ring) | OD 52, ID 25, length 15 at assembly z 280 … 295 | steel |
| `exhaust-duct` | modelled | flange OD 224 at z 322 … 326, shroud bore Ø185.6 z 322 … 350, outer wall r 92.4 at z 352 converging to r 72 at z 470 (0.8 mm), rear flange OD 160 at z 466 … 470 with 8 × M5; 4 EGT bosses at z 360 | 321 SS |
| `tail-cone` | modelled | cone from r 47.6 at z 352 to a 4 mm radius tip at z 470, 0.8 mm; 4 struts (8 × 30 mm NACA 0012-like) at z 365 … 385 to r 93 ending in 2 mm pads welded to the duct (model the pads as part of the cone) | 321 SS |
| `nozzle-ring` | modelled | z 470 … 500, flange OD 160 front, bore r 72 → 64 over z 470 … 495 (18° half-angle) then straight to z 500; 1.5 mm wall; trim family D₉ 120 … 136 by one parameter `exitDiameter` | 321 SS |
| `glow-plug` ×2 | purchased | catalog cylinder Ø10 × 40 on radial axes at z 170, ±y, from r 97 to r 137 | – |

Joints add `couplingOnDrum` rigid (the coupling hub bolted to the drum flange; child frame at the hub's own origin, parent frame on the drum at z 262), `turbineOnCoupling` rigid (the keyed stub; child frame at the wheel's own origin, assembly z 327), `bearingRearInTunnel` rigid to `diffuser-tunnel`, and rigid chains for the static parts (`diffuserOnOgv`, `caseOnDiffuser`, `linerOnCase` (the liner is located by the vaporisers and the exit lips; model it rigid to `comb-outer-case`), `vaporizersOnCase`, `ngvOnCase`, `exhaustOnNgv`, `tailConeOnExhaust`, `nozzleOnExhaust`, `glowPlugsOnCase`).

Operating cases: `design` 44,000 rpm; `idle` 19,800 rpm; `overspeed` 48,400 rpm (structural only).

Observables and simulations: `turbineTipGrowth` (`max_displacement`, `structural_static` on `turbine-wheel` at `overspeed`, fixed at the bearing journal, E 200 GPa, ν 0.3, ρ 7910, max 0.25 mm); `turbineMode1` (`modal`, min 1,500 Hz); `rotor2TipGrowth` as for rotor 1; mass properties: expected total mass 17.5 kg ± 20 % (the pipeline sums densities); `rotorInertia` is not an observable the evaluator offers, so record J from the handoff `properties.json`.

Acceptance: clearances `turbineTip` (wheel to exhaust-duct shroud, min_gap 0.35), `ngvToRotor` (min_gap 4.0), `linerToCase` (liner to comb-outer-case min_gap 7.0, the outer passage), `linerToTunnel` (liner to diffuser-tunnel min_gap 9.0), `vaporizerToLiner` (0.1 … the tubes pass through Ø8.2 holes: set min_gap 0.05), `wheelToTunnel` (turbine-wheel to diffuser-tunnel min_gap 0.25 at the labyrinth); motions `spin` (one turbine pitch, 15.65°, 12 steps) and the `explode` clip for the handoff.

Simulations of the hot gas path are **not** in the pipeline; the brief's section 7 must say so and point at the analysis plan.

### 14.3 Invocation

```bash
# 1. compressor module
/initialize-cad axjet-c2 "AXJET-220 two-stage transonic axial compressor module per scratch/turbine/axjet_design_and_implementation_guide.md section 14.1: bolt-on bellmouth lip, inlet frame with five struts, hub fairing and front bearing housing, nose cone with the starter, 29-blade rotor-1 blisk, 41-vane stator-1 ring, 31-blade rotor-2 blisk, 47-vane OGV ring, stacked casing rings, Ø40 drum shaft; one revolute joint at 44,000 rpm design and an 8,000 rpm cold MRF case on the derived air body; blisk centrifugal displacement and modal cases" @scratch/turbine/axjet_design_and_implementation_guide.md --kind assembly
/create-cad designs/axjet-c2

# 2. complete engine (after the module passes)
/initialize-cad axjet "AXJET-220/2 complete engine per section 14.2 of the guide: the compressor module plus diffuser-tunnel, combustor casing, liner with 12 vaporisers, 17-vane NGV ring, 23-blade IN713LC turbine wheel with integral stub shaft, keyed coupling hub and rear bearing, exhaust duct, tail cone and 128 mm nozzle ring; design 44,000 rpm, idle 19,800, overspeed 48,400; wheel and blisk displacement and modal cases; no hot-gas simulation" @scratch/turbine/axjet_design_and_implementation_guide.md --kind assembly
/create-cad designs/axjet
```

Review points for the drafts (`/initialize-cad` section 8 step 4): every radius and z in sections 3.2, 4.4, 6, 7 and 8 appears as a `stated` parameter with this document as its source; blade and vane counts are `stated`; blade sections are `derived` from the metal angles (or `stated` from the step-2 files); the air body's volume band and caps match 14.1; no open question changes geometry except the pending bay measurement (recorded as a note, not a question, because the envelope is a design input).

## 15. Build and test plan

Mapped to the evidence gates A (learning and scope) to I (application) of the [research guide, Addendum B.1](axial_microjet_research_guide.md#b1-evidence-gates).

| Gate | Work | Evidence to advance |
|---|---|---|
| B. Cycle feasibility | Analysis step 1 with pessimistic cases | NPR ≥ 1.4 and thrust ≥ 900 N at η_c 0.78, η_t 0.82, TIT 1120 K |
| C. Component preliminary design | Analysis steps 2–8; opencad `axjet-c2` and `axjet` PASS | geometry package, clearance budget, Campbell diagrams, ROSS report, stress margins |
| D. Manufacturing evidence | one blisk-1 in 2618-T61, one stator ring, casing ring; a cast IN713LC test wheel or a vendor coupon set | CMM within 0.05 mm on airfoils, Ra ≤ 0.8 µm, balance ≤ G2.5; wheel CT clean to 0.5 mm, chemistry and rupture coupon per AMS 5377 |
| E1. Rotor evidence | cold spin of each blisk to 115 % in a spin pit; assembled rotor on the module casing driven by an electric spindle to 50 % N (22,000 rpm, ≤ 30 kW) with proximity probes | growth within 0.03 mm of prediction, no permanent set; first critical located, response ≤ 25 µm |
| E2. Compressor evidence | the same rig instrumented (bellmouth Δp, pt3 rake, torque): speed lines at 30/40/50 % N | OPR and efficiency within 5 % of the step-3 CFD at the same corrected speed; no rotating stall at the design operating line |
| F1. Combustor evidence | atmospheric liner rig (blower, electric preheat to 380 K, full-scale liner and vaporisers) at 20–100 % of design mass flow (corrected for pressure) | ignition within 2 s, lean blow-out below 40 % of design fuel, exit pattern factor ≤ 0.3 with 12 thermocouples, Δp ≤ 6 % |
| F2. Hot-section evidence | turbine wheel hot spin not available; rely on casting certification, cold spin to 115 %, FPI, and the first engine runs limited to TIT 1050 K for the first 2 h | wheel growth and FPI after each hour for the first 5 h |
| G. Integrated ground engine | containment cell, remote console, protections tested with simulated faults; first runs: crank (no fuel), light-off and shut down, idle 5 min, 60 %, 80 %, 100 % in steps with inspections | self-sustaining at ≤ 45 % N; thrust, SFC, EGT, vibration per section 2.2 |
| H. Repeatability | 25 h / 200 cycles with borescope every 5 h and a teardown at 25 h | wear, clearances and balance within limits; model-vs-test reconciliation report |
| I. Application | only after H: inlet duct, tailpipe, mounts, structure, CG and electrical design for the airframe | separate package |

The engine itself serves as the full-speed compressor rig (a 215 kW electric drive at 44,000 rpm is not practical); the electric rig covers 0–50 % speed where the first critical and the front-stage incidence behaviour are examined.

## 16. Growth paths

| Variant | Change | Expected result |
|---|---|---|
| AXJET-220/3 | third stage (hub/tip 0.78, 33 blades) and third vane ring in a 45 mm longer casing; same turbine | OPR 2.7–3.3, 1.30–1.43 kN, SFC 0.13–0.14 kg/(N h), shaft power 270–350 kW; turbine ψ rises to 1.1–1.3, still single-stage |
| Ti blisks | Ti-6Al-4V rotors | 0.05 mm more running clearance margin, better HCF, +0.6 kg |
| Higher TIT | 1200 K with MAR-M247 wheel | +7 % thrust, wheel life assessment required |
| 240 mm casing | combustor r 113, 2.8 kg/s | ~1.5 kN, V_ref 34 m/s |
| Reheat module and variable nozzle (V2) | bolts to the z 322 flange in place of the dry exhaust module: 1900 K reheat, V-gutter flame holders with a pilot burner, 8-petal nozzle D 122 … 160 mm; see the [V2 guide](axjet_v2_design_and_implementation_guide.md) | 1.46 kN static, 1.54 kN at Mach 1.2 and 6 km (0.92 kN dry with the module fitted) |
| Integral starter-generator | PM machine on the drum inside the hub fairing, ~1 kW | replaces the nose starter and removes the battery dependence for an installation |

## Appendix A: sizing script

Reproduces sections 3–6 (station table, stage triangles, combustor reference velocity, turbine sizing, thrust). Constant-property gas model; run with any Python 3.10+.

```python
import math
R=287.0; CPA,GA=1005.0,1.4; CPG,GG=1150.0,1.33; T0,P0=288.15,101325.0; LHV=43.1e6
def flux(M,pt,Tt,g=GA): return pt/math.sqrt(Tt)*math.sqrt(g/R)*M*(1+(g-1)/2*M*M)**(-(g+1)/(2*(g-1)))
def mach(f,pt,Tt,g=GA):
    lo,hi=1e-4,1.0
    for _ in range(80):
        m=0.5*(lo+hi); lo,hi=(m,hi) if flux(m,pt,Tt,g)<f else (lo,m)
    return 0.5*(lo+hi)
N=44000; w=2*math.pi*N/60; rt=0.090; mdot=2.30
stages=[(0.64,0.62,0.85,1.40,22.0),(0.72,0.56,0.86,1.40,20.0)]   # hub/tip, psi_hub, eta_s, sigma_mean, chord mm
Tt,pt,opr,work=T0,P0,1.0,0.0
for k,(ht,psi,eta,sig,c) in enumerate(stages,1):
    rh=ht*rt; rm=0.5*(rh+rt); A=math.pi*(rt**2-rh**2); M=mach(mdot/A,pt,Tt)
    Ts=Tt/(1+0.2*M*M); Cx=M*math.sqrt(GA*R*Ts); dh=psi*(w*rh)**2; dT=dh/CPA
    pr=(1+eta*dT/Tt)**3.5
    print(f"stage {k}: r_h {rh*1e3:.1f} M_ax {M:.2f} Cx {Cx:.0f} dT {dT:.1f} PR {pr:.3f}")
    for name,r in (("hub",rh),("mean",rm),("tip",rt)):
        U=w*r; dCt=dh/U; W1=math.hypot(Cx,U); W2=math.hypot(Cx,U-dCt); s=sig*rm/r
        print(f"   {name}: U {U:.0f} b1 {math.degrees(math.atan2(U,Cx)):.1f} b2 {math.degrees(math.atan2(U-dCt,Cx)):.1f} "
              f"a2 {math.degrees(math.atan2(dCt,Cx)):.1f} dH {W2/W1:.2f} DF {1-W2/W1+dCt/(2*s*W1):.2f} Mrel {W1/math.sqrt(GA*R*Ts):.2f}")
    Tt+=dT; pt*=pr; opr*=pr; work+=dh
print(f"OPR {opr:.3f} Tt3 {Tt:.1f} pt3 {pt/1e5:.3f} bar  power {work*mdot/1e3:.0f} kW")
rho3=pt/(R*Tt); Aref=math.pi*(0.105**2-0.045**2); print(f"combustor V_ref {mdot/(rho3*Aref):.1f} m/s")
TIT=1150.0; f=(CPG*(TIT-298)-CPA*(Tt-298))/(0.97*LHV-CPG*(TIT-298)); mg=mdot*(1+f)
pt4=pt*0.95; dht=work*mdot/(0.99*mg); Tt5=TIT-dht/CPG; Tt5s=TIT-dht/(CPG*0.86)
prt=(TIT/Tt5s)**(GG/(GG-1)); pt5=pt4/prt; npr=pt5/P0
M9=math.sqrt(2/(GG-1)*(npr**((GG-1)/GG)-1)); T9=Tt5/(1+(GG-1)/2*M9*M9); V9=0.97*M9*math.sqrt(GG*R*T9)
A9=mg/((P0/(R*T9))*V9); F=mg*V9
print(f"f {f:.4f} fuel {f*mdot*1e3:.1f} g/s  PR_t {prt:.3f} Tt5 {Tt5:.0f}  NPR {npr:.3f} M9 {M9:.2f} V9 {V9:.0f}  D9 {2*math.sqrt(A9/math.pi)*1e3:.0f} mm")
print(f"thrust {F:.0f} N  SFC {f*mdot/F*3600:.3f} kg/(N h)")
# turbine (zero exit swirl, r_m 70 mm, phi 0.65)
rm=0.070; U=w*rm; Cx=0.65*U; Ct2=dht/U; C2=math.hypot(Cx,Ct2); Ts2=TIT-C2*C2/(2*CPG)
ps2=pt4*0.97*(Ts2/TIT)**(GG/(GG-1)); A=mg/((ps2/(R*Ts2))*Cx); h=A/(2*math.pi*rm)
print(f"turbine: U_m {U:.0f} psi {dht/U**2:.2f} alpha2 {math.degrees(math.atan2(Ct2,Cx)):.1f} M2 {C2/math.sqrt(GG*R*Ts2):.2f} "
      f"h {h*1e3:.1f} mm r {1e3*(rm-h/2):.1f}..{1e3*(rm+h/2):.1f} tip speed {w*(rm+h/2):.0f} m/s beta3 {math.degrees(math.atan2(U,Cx)):.1f}")
```

## Appendix B: conventions and formulas

- Angles from the axial direction; α absolute, β relative; positive in the direction of rotation. Stations per section 3.1.
- Velocity triangles: $\mathbf C = \mathbf W + \mathbf U$, $U = \omega r$; Euler work $\Delta h_t = U_2 C_{\theta 2} - U_1 C_{\theta 1}$; free vortex $r C_\theta$ = const across the span; loading $\psi = \Delta h_t/U^2$; flow coefficient $\phi = C_x/U$.
- Diffusion factor (Lieblein) $DF = 1 - W_2/W_1 + \Delta C_\theta/(2\sigma W_1)$; de Haller $W_2/W_1$; solidity $\sigma = c/s$, $s = 2\pi r/Z$.
- Carter deviation $\delta = m\,\theta/\sqrt{\sigma}$, $m = 0.23 + \alpha_2/500$ (circular arc, angles in degrees); metal angles $\kappa_1 = \beta_1 - i$, $\kappa_2 = \beta_2 - \delta$, camber $\theta = \kappa_1 - \kappa_2$.
- Compressor stage: $T_{t,out} = T_{t,in} + \Delta h/c_p$, $\pi_s = (1 + \eta_s \Delta T/T_{t,in})^{\gamma/(\gamma-1)}$.
- Fuel–air ratio: $f = [c_{p,g}(T_{t4}-298) - c_{p,a}(T_{t3}-298)]/[\eta_b\,LHV - c_{p,g}(T_{t4}-298)]$.
- Turbine: $\pi_t = (T_{t4}/T_{t5s})^{\gamma_g/(\gamma_g-1)}$ with $T_{t5s} = T_{t4} - \Delta h_t/(c_{p,g}\eta_t)$; reaction $R = 1 - C_{\theta 2}/(2U)$ for axial exit.
- Nozzle: unchoked when $p_{t5}/p_0 < ((\gamma_g+1)/2)^{\gamma_g/(\gamma_g-1)} = 1.85$; $M_9$ from the isentropic relation, $V_9 = C_v M_9 a_9$, $F = \dot m_9 V_9 + (p_9 - p_0)A_9$.
- Combustor: $V_{ref} = \dot m/(\rho_3 A_{ref})$; loading $\theta = p_3^{1.75} A_{ref} H\,e^{T_3/300}/\dot m$ (SI).
- Centrifugal: blade root stress $\sigma \approx K\,\rho\,\omega^2 (r_t^2 - r_h^2)/2$ with taper factor $K$ ≈ 0.6; solid disc centre stress $(3+\nu)\rho\omega^2 r^2/8$; rim radial growth of a solid disc $\rho\omega^2 r^3(1-\nu)/(4E)$; rotor energy $E = \tfrac12 J\omega^2$.
- Speed scaling: at constant blade speed, rpm ∝ 1/D, flow ∝ D², Reynolds ∝ D.

## Appendix C: parameter provenance

| Parameter | Value | Status | Basis |
|---|---|---|---|
| Envelope diameter / length | 224 / 665 mm | assumed (design input) | BDXL bay unmeasured; section 2.1 |
| Design speed | 44,000 rpm | derived | tip speed 415 m/s at r 90 for tip M_rel 1.30 |
| Tip radius | 90 mm | derived | casing 200 mm within the envelope |
| Hub/tip ratios | 0.64 / 0.72 | derived | hub loading ψ ≤ 0.62 with 2.3 kg/s |
| Stage efficiencies | 0.85 / 0.86 | assumed | small transonic stages; NASA 1976 achieved 0.69–0.75, TRI 60-class engines higher; pessimistic case run at 0.78 |
| Turbine efficiency | 0.86 | assumed | lightly loaded uncooled stage |
| TIT | 1150 K | assumed limit | uncooled IN713LC wheel, 25 h life |
| Burner pressure loss / efficiency | 5 % / 0.97 | assumed | annular micro combustors |
| Airflow | 2.30 kg/s | derived | combustor V_ref ≤ 38 m/s in r 45 … 105 |
| Blade/vane counts | 29 / 41 / 31 / 47 / 17 / 23 | derived | solidity targets, mutually prime |
| Chords | 22 / 15 / 20 / 14 / 26 / 20 mm | derived | solidity and aspect ratio 1.3–2.2 |
| Tip clearances | 0.25 / 0.40 mm | assumed | 0.8–1.0 % of span; growth budget 8.2 |
| Bearings | 25 × 52 × 15 hybrid | derived | DN 1.1 × 10⁶, drum Ø40 |
| Blisk material | 2618-T61 | selected | compressor exit ≤ 420 K across the V2 envelope; 7075 overages above ~120 °C |
| Materials | per section 11 | assumed | precedent engines; vendor confirmation pending |
| Mass | 16 kg | estimate | section 12; ±30 % |
| Thrust | 1,169 N | derived | Appendix A |
