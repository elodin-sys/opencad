# Closed airfoil profiles in KCL 2

## Result

**Provisional recommendation: use [arcs_adaptive_0p001_literals.kcl](arcs_adaptive_0p001_literals.kcl), 37 fitted pieces per side: 72 circular arcs plus two short straight segments overall.** It preserves shared endpoints, uses ordinary KCL 2 sketch primitives, and extrudes 165 mm. Its measured full-table point-to-curve deviation is **p95 0.000704090 mm; maximum 0.000981421 mm**. Both are well below 0.05/0.1 mm. Area is **230.635171122 mm²**, -0.001946660 mm² (-0.000844%) against the table. The matching KCL interpreter accepted the full extrusion program in **0.373 s**, and its emitted profile matches the analytical construction to 3.3e-12 mm.

**Hosted verification is incomplete.** Zoo stopped accepting new runs with an account/API-credit rejection. Only `polyline_uniform_60` and `polyline_literals_60` completed hosted analysis and deterministic STEP export; neither meets the maximum-deviation target. The recommended arc model has passed format, lint, the matching offline KCL interpreter/solver, and independent geometry checks, but **has no hosted volume measurement or STEP export**. This spike cannot establish a production-verified winner or a hosted engine point-count limit with the available credits.

### What the experiments establish

1. **Lines work; uniform row sampling wastes vertices on low-curvature regions.** 60 points per side / 118 edges execute on the hosted engine, but max deviation is 0.233762 mm at the trailing edge. Uniform 120 / 238 edges analytically pass at 0.079243 mm maximum. Adaptive Ramer–Douglas–Peucker (RDP) sampling at 0.01 mm uses only **45 PS + 62 SS points**, or **105 unique vertices/edges**, with p95 0.008303 mm and max 0.009852 mm. [The fixed-literal version](polyline_adaptive_0p01_literals.kcl) is the simpler fallback if fitting circular pieces is undesirable.
2. **Large sketch blocks are not proven to exhaust the solver.** The 120-point-per-side sketch alone takes 0.547 s; adding `region` still takes 0.548 s; the full mock extrusion takes 41.462 s. A 240-point-per-side sketch alone finishes in 2.607 s, while its full program exceeds 45 s. This localizes the observed slowdown to **extrusion or full-result handling**, not sketch solving or region extraction. Mock execution includes result serialization, so its limits cannot be assigned directly to the hosted GPU engine. Constant coordinates did not fix the large full-program timeout.
3. **`controlPointSpline` is a control-polygon B-spline, not table interpolation.** Three controls select degree 2; four or more select degree 3. It needs `experimentalFeatures = allow` for acceptance. [Official spline reference](https://zoo.dev/docs/kcl-std/functions/std-solver-controlPointSpline).
4. **The tested spline implementation emits straight paths.** Open-uniform clamped knots are used. Each nonfinal span emits 23 new sample points and the final span emits 24; internal knot points themselves are skipped. For n cubic controls, that is `23 × (n − 3) + 1` lines per spline. Two 60-control splines emit **2,624 straight edges**, yet still miss the target (max 0.245552 mm). This is confirmed by actual mock region paths, not inferred solely from a screenshot. [Versioned implementation](https://github.com/KittyCAD/modeling-app/blob/34bbd47ae48cac11104454cc4f08d88522670b82/rust/kcl-lib/src/std/solver.rs).
5. **Fitted cubic chunks are much better than using raw table points as controls.** Twenty endpoint-preserving cubic fits, four controls each, emit 480 lines and achieve p95 0.020671 / max 0.026797 mm; 26 fits emit 624 lines and achieve 0.005760 / 0.009745 mm. Both execute offline; hosted execution/export was credit-blocked. Four raw-control chunks per side do not meet the target at 8 or 16 controls per chunk. Large spline extrusions trap in WASM even when the corresponding sketch/region succeeds.
6. **Circular arc fitting gives the best tested local accuracy/complexity combination.** The 0.001 mm fit uses 74 pieces versus 105 for the 0.01 mm adaptive polyline, with about ten times smaller maximum deviation and a smaller area error. KCL emits 72 native `Arc` paths and two `ToPoint` paths. A 26-arc fit also meets the requested deviations (0.012923 / 0.022214 mm), but has larger local tangent discontinuities.
7. **Other documented options:** the KCL 2 solver offers lines, arcs, circles, points and the experimental control-point spline. No fit-point interpolating spline, explicit knot/weight input, or arbitrary dense-table profile primitive is documented. `bezierCurve`, `startProfile`, `close`, and the old polygon/pipeline functions are sketch v1; conic/ellipse variants are also marked v1-only in the supplied reference. They were not used. Fitted four-control `controlPointSpline` pieces are the tested KCL 2 cubic alternative. See the supplied [solver reference](/Users/danieldriscoll/dual/opencad/.agents/skills/backends/zoo/kcl-docs/std/solver.md) and [sketch reference](/Users/danieldriscoll/dual/opencad/.agents/skills/backends/zoo/kcl-docs/std/sketch.md).

![Analytical profile, endpoint details, and deviations](comparison.png)

### Fidelity measurements

Distances are from **every one of the 2,000 original unique table points** to the nearest point on the entire closed constructed boundary. They are not same-index point differences. Values below are **analytical predictions from supplied coordinates**; for successful mock runs, actual emitted paths were independently checked against them. Spline rows use the emitted polyline, with the ideal B-spline metrics retained separately in `candidates.json`. Volumes in this table are **area × 165**, not hosted measurements.

| Candidate | KCL pieces | Emitted edges | p95 mm | Max mm | Area mm² | Δ area mm² | Expected volume mm³ | Deviation pass |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [polyline_uniform_60](polyline_uniform_60.kcl) | 118 | 118 | 0.013736 | 0.233762 | 230.050454 | -0.586664 | 37958.324881 | no |
| [polyline_uniform_120](polyline_uniform_120.kcl) | 238 | 238 | 0.003238 | 0.079243 | 230.497167 | -0.139951 | 38032.032477 | yes |
| [polyline_uniform_240](polyline_uniform_240.kcl) | 478 | 478 | 0.000806 | 0.022964 | 230.601072 | -0.036046 | 38049.176866 | yes |
| [polyline_uniform_500](polyline_uniform_500.kcl) | 998 | 998 | 0.000140 | 0.005999 | 230.630666 | -0.006452 | 38054.059846 | yes |
| [polyline_adaptive_0p025](polyline_adaptive_0p025.kcl) | 72 | 72 | 0.019973 | 0.024973 | 230.460886 | -0.176231 | 38026.046268 | yes |
| [polyline_adaptive_0p01](polyline_adaptive_0p01.kcl) | 105 | 105 | 0.008303 | 0.009852 | 230.564267 | -0.072851 | 38043.104101 | yes |
| [spline_raw_60](spline_raw_60.kcl) | 2 | 2624 | 0.043858 | 0.245552 | 229.654973 | -0.982145 | 37893.070480 | no |
| [arcs_adaptive_0p025](arcs_adaptive_0p025.kcl) | 26 | 26 | 0.012923 | 0.022214 | 230.647511 | +0.010393 | 38056.839331 | yes |
| [arcs_adaptive_0p01](arcs_adaptive_0p01.kcl) | 31 | 31 | 0.008160 | 0.009901 | 230.553603 | -0.083515 | 38041.344479 | yes |
| [arcs_adaptive_0p001](arcs_adaptive_0p001.kcl) | 74 | 74 | 0.000704 | 0.000981 | 230.635171 | -0.001947 | 38054.803235 | yes |
| [spline_bezier_0p025](spline_bezier_0p025.kcl) | 20 | 480 | 0.020671 | 0.026797 | 230.619036 | -0.018082 | 38052.140901 | yes |
| [spline_bezier_0p01](spline_bezier_0p01.kcl) | 26 | 624 | 0.005760 | 0.009745 | 230.617072 | -0.020045 | 38051.816940 | yes |
| [spline_raw_12](spline_raw_12.kcl) | 2 | 416 | 0.560483 | 0.839256 | 216.637693 | -13.999424 | 35745.219402 | no |
| [spline_raw_24](spline_raw_24.kcl) | 2 | 968 | 0.255971 | 0.411318 | 226.162122 | -4.474996 | 37316.750172 | no |
| [spline_raw_120](spline_raw_120.kcl) | 2 | 5384 | 0.007118 | 0.112706 | 230.360526 | -0.276592 | 38009.486724 | no |
| [spline_raw_240](spline_raw_240.kcl) | 2 | 10904 | 0.001627 | 0.036578 | 230.559753 | -0.077365 | 38042.359215 | yes |
| [spline_raw_500](spline_raw_500.kcl) | 2 | 22864 | 0.000364 | 0.008838 | 230.621575 | -0.015543 | 38052.559883 | yes |
| [spline_raw_1001](spline_raw_1001.kcl) | 2 | 45910 | 0.000090 | 0.002142 | 230.634891 | -0.002227 | 38054.757034 | yes |
| [spline_chunks_4x8](spline_chunks_4x8.kcl) | 8 | 928 | 0.198487 | 0.343413 | 227.292363 | -3.344755 | 37503.239925 | no |
| [spline_chunks_4x16](spline_chunks_4x16.kcl) | 8 | 2400 | 0.040253 | 0.245004 | 229.678957 | -0.958160 | 37897.027956 | no |
| [polyline_literals_1001](polyline_literals_1001.kcl) | 2000 | 2000 | 0.000000 | 0.000000 | 230.637118 | +0.000000 | 38055.124434 | yes |
| [spline_raw_4](spline_raw_4.kcl) | 2 | 48 | 6.549036 | 6.733464 | 122.975180 | -107.661938 | 20290.904689 | no |

Fixed-literal counterparts have identical analytical geometry; the no-flag spline variants have identical geometry but fail acceptance. Full-1001-point lines have zero error against the table polygon by construction, but timed out in the full offline program.

### Execution and export measurements

Every candidate was formatted and linted successfully. Each command ran serially. Times include process launch; hosted times also include connection/API work. `credits rejected` is an environmental failure, **not a geometry failure**. `not run` means the hosted route was already blocked. A timeout is the benchmark's own limit, not a Zoo-reported time limit. Offline runs use a mock engine and do not certify a solid.

| Candidate | Full offline execution | Hosted analyze | Deterministic STEP export |
| --- | --- | --- | --- |
| [polyline_uniform_60](polyline_uniform_60.kcl) | 1.081 s OK | 2.951 s OK | 2.936 s OK |
| [polyline_uniform_120](polyline_uniform_120.kcl) | 41.462 s OK | credits rejected (1.671 s) | not run |
| [polyline_uniform_240](polyline_uniform_240.kcl) | >45 s timeout | credits rejected (1.620 s) | not run |
| [polyline_uniform_500](polyline_uniform_500.kcl) | >45 s timeout | credits rejected (1.713 s) | not run |
| [polyline_adaptive_0p025](polyline_adaptive_0p025.kcl) | 0.321 s OK | credits rejected (1.598 s) | not run |
| [polyline_adaptive_0p01](polyline_adaptive_0p01.kcl) | 0.763 s OK | credits rejected (1.839 s) | not run |
| [polyline_literals_60](polyline_literals_60.kcl) | 1.094 s OK | 3.229 s OK | 2.411 s OK |
| [spline_raw_60_no_flag](spline_raw_60_no_flag.kcl) | experimental error (7.074 s) | >120 s timeout | not run |
| [spline_raw_60](spline_raw_60.kcl) | 7.333 s OK | >120 s timeout | not run |
| [arcs_adaptive_0p025](arcs_adaptive_0p025.kcl) | 0.252 s OK | credits rejected (1.959 s) | not run |
| [arcs_adaptive_0p01](arcs_adaptive_0p01.kcl) | 0.255 s OK | credits rejected (1.765 s) | not run |
| [arcs_adaptive_0p001](arcs_adaptive_0p001.kcl) | 0.373 s OK | credits rejected (1.738 s) | not run |
| [spline_bezier_0p025](spline_bezier_0p025.kcl) | 2.537 s OK | credits rejected (2.128 s) | not run |
| [spline_bezier_0p01](spline_bezier_0p01.kcl) | 7.062 s OK | credits rejected (1.679 s) | not run |
| [spline_raw_12](spline_raw_12.kcl) | 0.318 s OK | credits rejected (1.833 s) | not run |
| [spline_raw_24](spline_raw_24.kcl) | 0.606 s OK | credits rejected (1.914 s) | not run |
| [spline_raw_120](spline_raw_120.kcl) | WASM trap (4.482 s) | not run | not run |
| [spline_raw_240](spline_raw_240.kcl) | WASM trap (2.633 s) | not run | not run |
| [spline_raw_500](spline_raw_500.kcl) | WASM trap (1.757 s) | not run | not run |
| [spline_raw_1001](spline_raw_1001.kcl) | WASM trap (1.483 s) | not run | not run |
| [spline_chunks_4x8](spline_chunks_4x8.kcl) | 2.376 s OK | credits rejected (1.885 s) | not run |
| [spline_chunks_4x16](spline_chunks_4x16.kcl) | WASM trap (12.781 s) | not run | not run |
| [polyline_literals_500](polyline_literals_500.kcl) | >45 s timeout | credits rejected (1.759 s) | not run |
| [polyline_adaptive_0p01_literals](polyline_adaptive_0p01_literals.kcl) | 0.694 s OK | not run | not run |
| [arcs_adaptive_0p001_literals](arcs_adaptive_0p001_literals.kcl) | 0.373 s OK | not run | not run |
| [polyline_literals_1001](polyline_literals_1001.kcl) | >45 s timeout | not run | not run |
| [spline_raw_4_no_flag](spline_raw_4_no_flag.kcl) | experimental error (0.200 s) | credits rejected (2.092 s) | not run |
| [spline_raw_4](spline_raw_4.kcl) | 0.200 s OK | credits rejected (1.815 s) | not run |

### Bounding boxes and expected centers of mass

All rows below are from the analytical constructed boundary. Extrusion Z is **0 … 165 mm**, with expected CoM Z = **82.5 mm**. Fixed-literal and no-flag variants share the corresponding geometry.

| Candidate | X min … max, mm | Y min … max, mm | Expected CoM (x,y,z), mm |
| --- | --- | --- | --- |
| polyline_uniform_60 | -0.139368 … 47.614447 | -21.599723 … 9.508408 | (20.614293, 1.065836, 82.5) |
| polyline_uniform_120 | -0.190029 … 47.748048 | -21.665181 … 9.511370 | (20.618890, 1.049650, 82.5) |
| polyline_uniform_240 | -0.190029 … 47.757719 | -21.692734 … 9.513486 | (20.619263, 1.046262, 82.5) |
| polyline_uniform_500 | -0.196859 … 47.775827 | -21.696250 … 9.513838 | (20.619583, 1.045167, 82.5) |
| polyline_adaptive_0p025 | -0.191601 … 47.775827 | -21.696250 … 9.504318 | (20.631096, 1.033451, 82.5) |
| polyline_adaptive_0p01 | -0.191601 … 47.775827 | -21.696250 … 9.511937 | (20.618821, 1.044789, 82.5) |
| spline_raw_60 | -0.045023 … 47.614447 | -21.599723 … 9.500358 | (20.622917, 1.071597, 82.5) |
| arcs_adaptive_0p025 | -0.196498 … 47.774895 | -21.694612 … 9.511606 | (20.615619, 1.049369, 82.5) |
| arcs_adaptive_0p01 | -0.196498 … 47.774895 | -21.698477 … 9.513649 | (20.619000, 1.046480, 82.5) |
| arcs_adaptive_0p001 | -0.196498 … 47.775872 | -21.698529 … 9.513958 | (20.619406, 1.045117, 82.5) |
| spline_bezier_0p025 | -0.196849 … 47.770471 | -21.697088 … 9.514207 | (20.620257, 1.044403, 82.5) |
| spline_bezier_0p01 | -0.196849 … 47.770471 | -21.697088 … 9.514207 | (20.619869, 1.045189, 82.5) |
| spline_raw_12 | 0.000000 … 47.614447 | -21.599723 … 9.139004 | (21.049116, 0.993164, 82.5) |
| spline_raw_24 | 0.000000 … 47.614447 | -21.599723 … 9.426869 | (20.709843, 1.096997, 82.5) |
| spline_raw_120 | -0.153017 … 47.663514 | -21.613769 … 9.510266 | (20.619030, 1.053774, 82.5) |
| spline_raw_240 | -0.184852 … 47.739463 | -21.670337 … 9.512844 | (20.618681, 1.047899, 82.5) |
| spline_raw_500 | -0.194868 … 47.768421 | -21.693127 … 9.513729 | (20.619462, 1.045520, 82.5) |
| spline_raw_1001 | -0.196362 … 47.773997 | -21.697296 … 9.513870 | (20.619629, 1.045011, 82.5) |
| spline_chunks_4x8 | 0.000000 … 47.614447 | -21.599723 … 9.437222 | (20.675017, 1.093720, 82.5) |
| spline_chunks_4x16 | -0.047415 … 47.614447 | -21.599723 … 9.498261 | (20.622093, 1.071058, 82.5) |
| polyline_literals_1001 | -0.196859 … 47.775827 | -21.698406 … 9.513908 | (20.619658, 1.044925, 82.5) |
| spline_raw_4 | 0.000000 … 47.614447 | -21.599723 … 2.968164 | (23.254539, -3.400226, 82.5) |

### Exact KCL idioms

The full linked candidate files are runnable; the primitive snippets below show the exact required syntax.

```kcl
@settings(defaultLengthUnit = mm, kclVersion = 2.0)
```

Inside `profile = sketch(on = XY) { ... }`, constants or literal `var` guesses both work. For example, the first recommended arc is:

```kcl
e0000 = arc(
  start = [0mm, 0mm],
  end = [0.427175152413mm, -0.282804317698mm],
  center = [0.697786629931mm, 0.589979194365mm],
  direction = CCW,
)
```

`direction = CW` is required for clockwise pieces; direction is calculated from the ordered sample triplet. There is no three-point solver-arc argument: calculate the center before emitting KCL. Keep each end numerically identical to the next start. The two line pieces use `line(start = [...], end = [...])`. No coincidence or dimensional constraints are necessary for this coordinate-driven spike. `var` must precede a **literal**, e.g. `[var 0mm, var 0mm]`; it cannot precede a variable name or an expression.

After all closed-loop pieces have been declared:

```kcl
airfoilRegion = region(segments = [profile.e0000, profile.e0001])
blade = extrude(airfoilRegion, length = 165mm)
hide(profile)
blade
```

The two segments select the traced boundary; this argument is not a list that must enumerate every edge. There is no legacy `close()`. Do not add zero-length closing lines at the shared leading or trailing edge, and do not use the same spent region for another feature. [Region documentation](https://zoo.dev/docs/kcl-std/functions/region).

Spline files instead start with:

```kcl
@settings(defaultLengthUnit = mm, kclVersion = 2.0, experimentalFeatures = allow)
```

Inside the sketch use `controlPointSpline(points = [[...], [...], [...], [...]])`; `solver::` is already in scope inside a sketch block. For cubic fitting, supply the **fitted four control points**, including shared end controls, not four arbitrary table points. Do not use legacy `bezierCurve`.

## Files changed

- **`findings.md`** — this report; **`comparison.png`** — standalone analytical comparison.
- **28 candidate `.kcl` files** at the spike root: uniform/adaptive/fixed-literal polylines, adaptive arc fits, raw/chunked/fitted-control splines, and experimental-flag probes. Links appear in the execution table.
- **`exports/polyline_uniform_60/output.step`**, **`exports/polyline_literals_60/output.step`** — the two successful deterministic hosted exports.
- **`baseline.json`**, **`table_mm.csv`**, **`candidates.json`**, **`measurements.csv`**, **`mock_geometry_checks.json`**, **`step_checks.json`** — input fingerprint, converted coordinates, all fit/control data, full-precision metrics and independent comparisons.
- **`profile_geometry.py`**, **`fit_candidates.py`**, **`measure_curves.py`**, **`run_benchmarks.py`**, **`mock_execute.mjs`**, **`verify_geometry.py`**, **`make_report.py`** — generators, bounded command harness, offline runner and measurement/report tools.
- **`logs/`** — exact command arrays, exit codes, UTC start times, wall times, raw stdout/stderr, and reduced actual mock geometry.
- **`tooling/`** — official `@kittycad/kcl-wasm-lib` 0.1.184 package (KCL library 0.2.184) and package metadata, plus local plotting cache. **`references/`** — source/version evidence. No runtime dependency was installed outside this directory.

The pre-existing `codex/` files and the source workbook were not edited. No commit, push, PR, nested Codex session, or external-account change was performed.

## Verification

### Input and mathematical reference

- Workbook: `/Users/danieldriscoll/dual/opencad/truth/cases/spleen-c1-blade/inputs/SPLEENC1_Geometry_Airfoil_2D_v1.xlsx`; sheet `SPLEENC1_Coord`; skip two headers; 1,001 numeric rows per side.
- SHA-256: `eb02e45c1ff8b6f94fcb7a91209f5b0113c96b1ffa27f9cbaff18133cb37a4f2`.
- Multiply every coordinate by **1,000** to convert metres to millimetres. Loop = PS forward followed by SS reversed, omitting the duplicate two seam points.
- Actual shared trailing edge = **(47.6144470215, −21.59972305301) mm**; retain workbook precision rather than the rounded prompt values.
- Full-table polygon area = **230.637117781966 mm²** (the prompt's 230.637 mm² is rounded).
- Bounds = **X -0.196858635786 … 47.775827064170; Y -21.698405978851 … 9.513908364697 mm**.
- Expected full-table extrusion volume = **38055.124434024 mm³**; CoM = **(20.619657984838, 1.044925389020, 82.5) mm**; surface area = **20885.712651687 mm²**.

Polyline distances use clamped orthogonal projection onto every finite segment; areas/centroids use the shoelace formulas. Uniform sampling selects rounded evenly spaced row indices including both endpoints. RDP runs separately on each side. Arc fits recursively split until all assigned table points are within tolerance of the finite arc through the interval's start/middle/end; two-point intervals become lines. Arc distances check angular extent before using radial distance. Area and moments use Green's-theorem integrals; bounds include arc cardinal extrema. Cubic fits use chord-length parameters and endpoint-preserving least squares, recursively splitting on residual. Ideal spline distances solve the stationary-distance polynomial in each span; area/moments integrate the span polynomials and extrema solve their derivatives. Emitted spline samples exactly reproduce the library's open-uniform sampling policy.

Checks compare actual mock region paths against predicted coordinates and remeasure the emitted geometry. All **19** completed geometric outputs, including two error-flag outputs, agree within **3.3e-12 mm**; closure gaps are below 1e-7 mm. Arc-area integration was also checked against a separately sampled dense polygon. Spline line counts/positions match the actual mock result, so spline fidelity is not based on an unsupported assumption about the curve the engine receives. Hosted spline STEP topology remains unverified.

### Hosted measurements versus expected values

Both successful variants returned the same values. This validates the measurement route and coordinate idioms at **118 edges**, not the fidelity of that downsampling choice.

| Property | Measured by zoo analyze | Expected from 118-edge polygon | Difference |
| --- | --- | --- | --- |
| Volume mm³ | 37958.327627763 | 37958.324880975 | +0.002746788 |
| Area inferred as V/165 mm² | 230.050470471 | 230.050453824 | +0.000016647 |
| Surface area mm² | 20828.198669534 | 20828.197355284 | +0.001314250 |
| CoM x mm | 20.614284515381 | 20.614292617636 | -0.000008102255 |
| CoM y mm | 1.065836191177 | 1.065835587960 | +0.000000603217 |
| CoM z mm | 82.499931335449 | 82.500000000000 | -0.000068664551 |

Hosted bbox matches the 118-edge analytical box to the printed precision: **X −0.139367850232 … 47.614447021500, Y −21.599723053010 … 9.508408398959, Z 0 … 165 mm**. Compared with the full table, this loses the leading-edge minimum by 0.057491 mm, trailing-edge maximum X by 0.161380 mm, minimum Y by 0.098683 mm, and maximum Y by 0.005500 mm. Measured volume is **96.796806 mm³ below** the full-table expectation.

Each STEP has **118 lower-cap boundary vertices and 120 faces**, exactly expected, with 354 line curves and no B-spline/circle curves. Its vertex rounding differs from supplied points by at most **6.878e-6 mm**. Both files have SHA-256 **`ca212196d4ef88e43776b7a958c90acb6b694779e07f1798bdfbd6356c4e427f`** and fixed 1970 timestamps. STEP coordinates declare metres; the independent check converts them back to mm.

### Commands run

Commands were recorded verbatim per candidate in `logs/*.json`. The acceptance sequence was:

```sh
zoo --version
zoo kcl format --write <candidate.kcl>
zoo kcl lint <candidate.kcl>
zoo kcl analyze --format json --volume-output-unit mm3 --center-of-mass-output-unit mm --surface-area-output-unit mm2 <candidate.kcl>
zoo kcl export --output-format step --deterministic <candidate.kcl> <output-dir>
zoo kcl bounding-box --format json --output-unit mm <candidate.kcl>
```

`analyze` already includes a bounding box; the standalone bounding-box command was run on the two successful variants but printed a table despite `--format json`. Use the JSON bbox in `analyze`. No `--allow-errors` was used. No material-mass claim is made; the CLI's default density was left alone.

The matching offline tool was obtained from the official npm registry; package integrity was checked. CLI version **0.2.196** pins `kcl-lib = 0.2.184` in its [release manifest](https://github.com/KittyCAD/cli/blob/v0.2.196/Cargo.toml). The WASM library reports **0.2.184**, Node **24.1.0**. Mock execution disables network and uses no account credentials.

```sh
/Users/danieldriscoll/dual/opencad/.venv/bin/python -B profile_geometry.py
/Users/danieldriscoll/dual/opencad/.venv/bin/python -B fit_candidates.py
/Users/danieldriscoll/dual/opencad/.venv/bin/python -B measure_curves.py
/Users/danieldriscoll/dual/opencad/.venv/bin/python -B run_benchmarks.py <names> --timeout 120
/Users/danieldriscoll/dual/opencad/.venv/bin/python -B run_benchmarks.py <names> --timeout 45 --phases mock
node mock_execute.mjs polyline_uniform_120 --sketch-only
node mock_execute.mjs polyline_uniform_120 --region-only
/Users/danieldriscoll/dual/opencad/.venv/bin/python -B verify_geometry.py
/Users/danieldriscoll/dual/opencad/.venv/bin/python -B make_report.py
```

The first three Python commands regenerate all 28 candidates and their measurements from the workbook. Format the generated files afterward. Regeneration was checked against the original tested, formatted candidates using SHA-256: all 28 files were byte-identical. For a specific preserved candidate, rerun just the command harness and verification.

### Errors, exact messages, and remedies

| Class | Exact message / observation | Candidates and remedy |
| --- | --- | --- |
| Experimental feature rejection | ``Use of `controlPointSpline` is experimental and may change or be removed.`` | Offline `spline_raw_4_no_flag` and `spline_raw_60_no_flag`: `severity: Error`, twice per file. Add `experimentalFeatures = allow`; the corresponding enabled files finish without issues. A returned mock body alone is insufficient for acceptance: inspect `issues`. |
| Hosted external timeout | No diagnostic before the harness killed the process at **120.015 s** / **120.006 s**. | Raw 60 controls per side, absent/enabled experimental flag. Cause cannot be localized from hosted logs. The enabled version emits 2,624 edges offline; reduce the control count via fitting, or use the compact arc fit. Hosted remedy not verified. |
| Offline external timeout | No KCL message; subprocess killed at the configured **45 s** limit. | Uniform 240/500 per side, literal 500/1001. Adaptive 105-edge lines and 74-piece arcs complete. This is not a solver-convergence diagnostic. |
| WASM runtime trap | `RuntimeError: unreachable` | Raw 120/240/500/1001 controls per side and 4 × 16-control chunks per side. Full stack traces are in `.mock.stderr`. Sketch-only probes succeed for raw 120 and chunks 4 × 16; raw 120 also succeeds through `region`. Smaller fitted chunks complete. Trap root cause is unverified; do not relabel it a memory/constraint-limit error without evidence. |
| API credits exhausted | `Failed executing KCL on engine, errors: This request is not included in your current plan, and your account has no API credits available. Enable pay as you go or update your plan in your account: https://zoo.dev/account/billing` | All remaining attempted hosted analyses. Requires account credits/plan change by the account owner; no account change was attempted. This prevented required hosted comparisons and exports. |

**No explicit solver-convergence failure or “too many constraints” message was observed.** Format/lint reported no problems, including for files later rejected for experimental use at execution. The full-program slowdown occurs after successful region construction in the stage probes; the offline API also serializes a large result, so extrusion execution and result handling are not separated by this experiment. [Mock executor implementation](https://github.com/KittyCAD/modeling-app/blob/main/rust/kcl-wasm-lib/src/context.rs).

## Open questions

- **Required remaining verification:** restore Zoo API access, then analyze and deterministically export the recommended arc fit, the adaptive-line fallback, the fitted cubic candidates, and the larger line counts. Until then, their predicted volumes/CoMs/bboxes must not be presented as hosted measurements, and no reliable hosted point-count ceiling is established.
- The arc fit is position-continuous but does not impose tangent constraints. Measured maximum tangent jump is **6.412°** for the 74-piece fit (p95 **1.151°**); two very short intervals use straight segments. The 26-arc fit has a **12.342°** maximum jump. If the eventual reconstruction requires C1/C2 surface smoothness, define that requirement and validate a tangent-continuous fit separately. The specified point-deviation criterion alone does not establish smoothness.
- Distances are one-sided, table-point-to-constructed-boundary, exactly as requested. No claim is made about unsampled true airfoil geometry or a continuous symmetric Hausdorff distance. Native spline surfaces are not demonstrated by this implementation.
- The exact cause of the WASM traps/full-extrusion slowdown and the hosted 120-second spline stalls remains unverified. The existing evidence rules out a blanket claim that 120-point sketches cannot solve.
- Timings are individual serial trials, not a statistical reliability study. The two matching hosted exports provide a small repeatability check at 118 edges; the provisional winner still needs its first hosted build.
