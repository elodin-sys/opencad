# Design ladder

Every bundle under `designs/<part>/` ordered easiest → hardest for the pipeline. Difficulty = kernel operations the worker must land × how much the sources leave underspecified × how many independent truth checks are scored. Distilled from `scratch/agentic_cad_engineering_primer.md`, `scratch/test-cases.md`, `scratch/improvement-campaign.md` and each `designs/*/brief.md`. Status is as of 2026-09-24; live verdicts regenerate into `docs/validation-envelope.md` (`python -m opencad.truth report`).

## Checks every design gets

- Contract vs exported STEP (OpenCascade is authoritative; `ok: true` in a stage JSON is a claim): bbox, volume, surface area, COM, solid count, named faces, sections (area + outer-loop/hole counts), solid/void probes.
- Blockout checkpoint: an envelope-only primary solid must hit the finished bbox and a volume band before detail modelling.
- Editability: single-parameter edits with analytic ΔV/Δbbox; sanity asserts only, never equality locks between parameters; infeasible edits must refuse.
- Export integrity: deterministic STEP, watertight STL, KCL/STEP/STL volume agreement ≤ 0.2 %.
- Provenance: each parameter is stated / derived / measured / measured (reference model) / inferred / defaulted; unknowns become open questions, not silent approximations; reference CAD is evaluator-only and never imported.
- Truth class: A physical measurement, B published reference geometry, C arithmetic from published dimensions, D self-consistency, E illustrative. Mutants (deliberately wrong parts) must fail the scorer.

## Fast pair (regression gate)

Two small public teaching examples, frozen as class B references, that together exercise every gate the pipeline runs
except sealed passages (still the Voron's job) at a target of <= 15 min per backend from the case inputs (draft ->
blockout -> model -> corrections -> score). Run them with `/regress`: each case is drafted once, every backend runs in
parallel, and the bench report compares the session with the promoted baseline. Public examples: treat them as
regression tests, not evidence of unseen-design generalization.

0a. **bearing-housing** — build123d "Cast Bearing Unit", housing only: an oval flange (hull of Ø57 and two Ø22 lobes,
    J = 76.5) and a Ø57 boss to z = 26, every side face drafted 4°, every edge rounded r = 1 before the holes, Ø47 × 14
    counterbore over a Ø14 bore, two Ø10 holes; spec + three views. Class B (`scripts/derive_bearing_housing_truth.py`,
    build123d@cdaf1caa).
    Draft scored by geometry (two boss annulus sections, four inclined flats with normals carrying sin 4°), rounds by
    face areas, stepped bore by cylinder extents (`t_range`), 23 observables; mutants: shifted/missing hole, filled
    counterbore, no draft, 1.1× scale.

0b. **enclosure-base** — CadQuery "A Parametric Enclosure", base only: an open 100 × 150 × 47 box (47, not the 50 mm
    enclosure height), r = 10 corners, r = 2 bottom round, 3 mm walls and floor, four free-standing Ø10 posts with Ø4
    bores that stop at the floor; spec + three views. Class B (`scripts/derive_enclosure_base_truth.py`,
    CadQuery@17846d63).
    Cavity, floor and blind bores by sections, centroid-matched faces and solid/void probes, p05 wall thickness >= 2.9,
    25 observables; mutants: 2 mm wall, bore through the floor, filled cavity, shifted bore, built 50 tall, 1.1× scale.

## Ladder

1. **coupon** — 60×40×4 mm block, no features; text spec. Class D, text-only.
   Toolchain smoke test (contract → worker turn → analyze → STEP/STL → gates → report) with closed-form V = 9600 mm³ and COM. Speed baseline: 256 s worker + 24 s evaluator. Gates PASS.

2. **bracket** — 80×50×6 plate, 4×Ø4.5 holes inset 10, R5 vertical-edge fillets; text spec. Class D.
   First fillets, holes, sections (z = 3 mid-plane; x = 10 through two holes), probes and edit tests, all analytic (V = 23489.5 mm³). The x = 10 section catches a hole pattern swapped by the engine's local-frame `cutAt`; volume alone cannot.

3. **nasa-backstep-driver-seegmiller** — Driver–Seegmiller backward-facing-step *air volume*: H = 12.7, 1:9 and 1:12 ratios, x/H −105..+50, one profile extrusion; NASA text only. Class C, text-only.
   A negative (CFD-domain) model with 8 named boundary faces; inch→mm and ratio-derived parameters; edit tests on derived parameters as formula overrides. Origin of the no-equality-asserts rule (edits aborted on `assert(width == 12·H)`). Reattachment x_r/H = 6.26 is recorded as a downstream target, never a geometry input. PASS 15/15 over 10 attempts.

4. **chiral-keyplate** — 80×80×8 plate, four 16×6×4 blind pockets in a C4 pinwheel; text spec. Class D calibration, text-only.
   Handedness. Volume, bbox, COM, inertia, horizontal sections and silhouette are identical for the mirror image; only signed solid/void probes and four individually named floors (`mode: one`, centroid-matched) reject it. Also named-face persistence through STEP. PASS 14/14.

5. **nasa-atb-axisymmetric-bump** — Bachalo–Johnson bump: Ø152.4 cylinder, 203.2 mm chord circular arc (R1 = 280.46) rising 19.05, tangent R2 = 183 leading blend, sharp trailing join, revolved 360°; inch spec + 181-point surface table. Class C, text-and-points.
   Tangent-arc construction and revolve with closed-form V/S/COM integrals; the table fixes only scale and axial extent (−650..900) and its trailing-edge smoothing must not be fitted; R2 alternate (203.2) carried as an open question with a wide band. PASS 11/11.

6. **spleen-c1-blade** — SPLEEN C1 turbine blade: 1001+1001-point airfoil from xlsx (metres), straight 165 mm extrusion, LE at origin, TE (47.614, −21.600) ⇒ −24.4° stagger. Class B, table-and-notes.
   Data → faithful curve → solid at ≤ 0.001 mm point fidelity; no generic airfoil, no smoothing, no added root. Source-version trap: the database's v1 CAD had the wrong stagger, coordinates govern. Curved side faces are unnameable in the schema, so caps and axial sections carry the check. PASS 12/12.

7. **nist-amb2022-01-bridge** — NIST AMB2022-01 bridge 75×5×12.5: 45° tapered nose, 12 legs (5/2.5/0.5 wide, 14 pitch) under 2 mm gaps with 45° overhangs, 11 top tabs, hollow leg L10 (0.5 walls, 1 base, four 4 mm internal walls ⇒ 5 sealed cavities); dimensioned drawing + figures. Class B, drawing-only.
   Drawing reading with pixel corroboration; 40 parameters (25 stated / 9 derived / 4 measured / 2 inferred); patterns anchored from the far end; sealed internal voids (13-island sections, 5 holes); undocumented wall widths kept inferred with open questions. PASS 14/14.

8. **nist-amb2022-01-bridge-mesh** — same part plus the NIST STL as an inspection-only reference ingest. Class B, mesh-input.
   Adds mesh-deviation gates (p95 ≤ 0.2, Hausdorff ≤ 0.5, silhouette IoU ≥ 0.98) and `measured (reference model)` provenance while forbidding import; the mesh's six shells must resolve to one solid with five cavities, not six bodies. PASS 14/14.

9. **benchy** — #3DBenchy tugboat 60×31×48 from the official caliper set (roof 23, chimney Ø3/Ø7 blind 11, cargo box 8×7×9, windows, hawsepipe Ø4, 40° bow, 5.5° roof; 15.55 cm³); hull OML unpublished. No truth case; pipeline gates only.
   Freeform surfacing under underspecification: 48 parameters, 25 inferred with 0.5–4 mm bands; lofted symmetric hull; blind bore, pocket and through-windows checked by sections; ±10 % volume band. Speed benchmark 7651 s → 2252 s worker wall. Gates PASS, V = 16954 mm³.

10. **nist-am-test-artifact** — NIST AM Test Artifact (Moylan 2014): 100 mm square rotated 45° × 10 thick, Ø10 bore with Ø20/Ø15 bosses, 16 Ø4 pins + 4 holes, two L staircases with 1 mm steps, 1-in-25 ramp, 8 lateral cavities (round/square/diamond/rhombus), fine pins and holes Ø2→Ø0.25, 20 fine rectangles; drawing + renders + dimension sheet. Class B.
    Feature-by-feature scoring: 64 parameters, 79 mandatory features, 35 individual cylinders, 69 truth checks; a correct base cannot compensate for a missing Ø0.25 pin. Diagonal (u, v) frames, repeated equal-area faces disambiguated by centroid, positive/negative feature pairs that cancel in volume. PASS 69/69; mutants fail. First campaign case to close.

11. **rpi5-enclosure** — design-to-requirements, not reconstruction: two-solid FFF base + lid for a Raspberry Pi 5, 102×73×33; board keep-outs, 7 plug envelopes, four Ø6.2 standoffs with Ø2.5×5 pilots, four corner-post lid screws; requirements doc + board drawing. Class C, requirements.
    Multi-solid hardware fit: no-interference clearances against keep-out and plug boxes, lid closure gap 0..0.1, p05 wall thickness ≥ 2 mm, pinned interfaces. Parametric robustness: 10-value `headroom` sweep (15..35) plus an infeasible value that must assert. ECR chain: ECR-1 +10 headroom, ECR-2 3 mm shell, ECR-3 side fasteners (all PASS); ECR-4 lower lid correctly refused INFEASIBLE. PASS 28/28; mutants 4/4 caught.

12. **gear-pair** — m2 / 20° spur pair: 20T pinion (Ø6 bore) at origin, 40T wheel (Ø8) at (60, 0), face 8, 0.10 mm backlash, phased to mesh, on a 110×50×5 carrier; three separate solids; text spec only. Class C, spec-only.
    Math-derived involute flanks with backlash thinning, three touching-but-separate bodies, tooth-count observables, 72-step full-pitch meshing sweep (zero interference, flank gap ≤ 0.15; measured 0.047). Whole-profile p95 ≤ 0.10 is evaluator-only. PASS 16/16; sweep 1224 s → 72 s.

13. **fusion-*-recon** (5) — Fusion 360 Gallery held-out bodies from renders + dimension sheet; pipeline frozen, reference CAD evaluator-only. Class B, renders-and-sheet. By face count:
    - **01184** T-bar 10×88×50, R4 fillets, Ø5 bore + Ø5 shaft (14 faces). PASS 18/18.
    - **13786** 100×100×3 plate: 45° chamfers, R3 corner pins, Ø5 hole, 35×14 elliptical slot, two Ø2×5 blind edge bores (18 faces). PASS 15/15.
    - **12944** 126.7×15×108 flange: four Ø24 bosses, two Ø174 side cuts, Ø18 bore, Ø36 hub, 3 mm pockets both faces, four Ø10 (27 faces). PASS 22/22.
    - **15317** Ø88.9 flange on Ø50.8 hub with revolved waist, U-slot, stepped arm bores, rim holes (37 faces; decomposed, 44 acceptance items). PASS 20/20.
    - **16418** 36-tooth disc 20.5×4, hex boss + hex socket, Ø3.1 floor bore (161 faces; decomposed, 78 items). PASS 11/11.

    Tests generalization beyond hand-tuned cases, decomposition (partition → parallel modules → integrate) on the two largest, and drafting quality: all five passed truth while failing their own drafted contracts on `passages` and first-order `edit_test` deltas. Surfaced evaluator artefacts (logged, not patched): coaxial-cylinder merge, concentric-coplanar face pairing, half-face revolves, tooth_count contamination by an inner hex, passage seal radius.

    Companion `fusion-*-assembly` cases (same five joint sets) are a bake-off rung of their own: local backends run **modelled** mode (`python -m opencad.truth assemble <case> --backend <id>`). The worker writes `parts/<backend>/<case>/main.py` that imports the two dataset STEPs, places them, and assigns `result` plus a `placements` dict; the pipeline exports a 2-solid STEP, agrees each solid with input×placement (volume rel ≤ 1e-4, Hausdorff ≤ 0.05 mm), scores the joint against the unchanged `joint_set.json`, and builds the animated handoff GLB from the exported bodies. Zoo v2 remains the frozen placement-only reference (5/5 PASS). Verdict = program + solid_count + agreement + integrity + joint checks.

14. **prusa-mini-extruder-front** — Original Prusa MINI extruder front housing 53×14×63.7: keyhole opening stacks, 8 screw axes with Ø6.5 counterbores and hex nut traps with 0.3 mm print bridges, Ø4 filament bores (one angled), hotend half-clamp bores (axial, tilted, 45°), bevels, 4 mating datums; 40 cylinders; renders + sections + dimension sheet. Class B, renders-and-sheet.
    Functional geometry that must mate with other parts: each assembly-governing hole is an acceptance cylinder measured on the exported STEP, datums are interfaces with checks, cosmetics optional. Zoo never landed the booleans (best FAIL 24/33); CadQuery, build123d and FreeCAD PASS 33/33 through decomposition. ECR-1 deferred.

15. **voron-sb-duct** — Voron Stealthburner front housing 71×27.4×59.1: two mirrored sealed part-cooling ducts (~8×19, 1 mm walls) forking to four nozzle outlets, 26×35 hotend cavity open at back and bottom, Ø37.5 fan mouth, 30 cylinders, 9 inclined planes; renders + 11 sections + dimension sheet. Class B, renders-sections-sheet.
    The interior: voxel passage connectivity with port plugs (each inlet → both branches; ducts never connected to each other), p05 wall ≥ 0.75, 11 section stations, void probes. Zoo stalled at FAIL 12–15/22 on kernel `BooleanUnion`/`BooleanSubtract`; CadQuery, build123d and FreeCAD PASS 21/21 through decomposition. ECR-1 deferred.
