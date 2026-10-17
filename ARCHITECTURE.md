# opencad architecture

The canonical map of the CAD pipeline: what each layer does, where its code lives, what
it writes, and how a claim becomes evidence. Read it once top to bottom; each section then
stands alone.

The system turns one immutable source bundle — `designs/<part>/contract.yaml` plus its
brief and sources — into a worker-authored part on a chosen modelling backend (Zoo/KCL,
CadQuery, build123d, or FreeCAD PartDesign), independently measured exports, a
12-gate verdict, a self-contained report, and a handoff package. A separate, SHA-pinned
`truth/` corpus establishes reconstruction accuracy against external references. Select
the backend with `--backend` / `OPENCAD_BACKEND`. Layout is `parts/<backend>/<part>` and
`results/<backend>/<part>`; a part design an assembly names nests under it (`<asm>/parts/<leaf>`, below).

```
/initialize-cad <part> "<intent>" @docs @drawings @tables @mesh
   sources -> ingest (mesh/table, deterministic) -> worker contract draft -> brief
   -> publish designs/<part>/ -> blockout checkpoint (envelope-only KCL, four-view)
                                              |
                                              v  /create-cad designs/<part>  (python -m opencad run)
   plan (worker, read-only) -> model (worker writes parts/<backend>/<part>/main.*)
   -> verify (format/lint/hygiene, engine.analyze, local STL snapshots)
   -> export (STEP x2 deterministic, STL, GLB)
   -> inspect (OpenCascade on STEP, trimesh on STL, sections, probes, faces, deviation)
   -> edit (parameter edits -> STEP -> OpenCascade; baseline re-export hash)
   -> gates (12, tiered)  --one bounded worker correction on tier-A or model-attributable export failure-->  model
   -> report.html / report.md / contact-sheet.png / handoff/
                                              |
   truth/cases/<case>  (scorer-only)  ------> python -m opencad.truth score -> scorecard
```

## Design principles

- **Contract first.** `PartContract` (pydantic 2, `src/opencad/schemas.py`) is the single
  source of intent. Every number carries provenance (`stated`, `measured`,
  `measured (reference model)`, `derived` + formula, `inferred`/`defaulted` + rationale) and
  a digital tolerance. No stage may relax it.
- **Cursor orchestrates, workers model.** All KCL authoring, drawing interpretation and
  spatial reasoning are worker turns. The control plane never calls a model itself: a stage
  that needs a turn issues a **work order** (`results/<backend>/<part>/worker/NNN-<role>/brief.md`), the
  command exits 75 with one `NEXT {...}` line, the orchestrating Cursor agent runs the order
  with a `cad-worker` `Task` sub-agent on the order's model (`NEXT.model`, per role in `worker/profiles.py`) and
  re-runs the printed `continue` command (`.cursor/skills/cad-drive`). Codex is opt-in
  (`--worker codex`) and falls back to the handback when its budget is exhausted. Pipeline
  segments run in the foreground; nothing is detached (`nohup` / `setsid`).
- **Engine numbers are evidence, OpenCascade numbers are verdicts.** Backend `engine.analyze`
  is disclosed only; the exported STEP read by
  OpenCascade (OCP) is authoritative for envelope, mass properties, sections, probes and
  faces. STL (trimesh) is a third witness for agreement. A **Backend** is a `Language` +
  `Engine` (`src/opencad/backends/`); Zoo is hosted CLI, CadQuery/build123d run in the
  repo `.venv`, FreeCAD is `freecadcmd` (never imported).
- **`ok: true` is a claim.** Every stage writes `results/<backend>/<part>/<stage>.json` with a
  provenance stamp (zoo version, git head, engine-call ledger, worker agent/thread ids). The 12
  gates re-read those files; the report quotes evidence paths.
- **Bounded autonomy.** The worker self-corrects at most three times inside the model stage; the
  orchestrator grants exactly one retry for a tier-A gate failure or a model-attributable
  export failure (`export_integrity` when the STEP is valid but the mesh is open;
  `export_agreement` when the engine responded), with measured deltas. The retry rewrites
  the KCL; tier C artifacts are never repaired in place. Retries are recorded in
  `gate_feedback.json`.
- **Truth is sequestered.** While any run holds a case, its `truth/`, manifest, mutants,
  scorecards and `attempts.yaml` live in the vault (`~/.cache/opencad-vault/<case>`), out of the
  worker's reach; only the scorer reads them. Scorecards are hash-bound to manifest, inputs,
  truth, source and STEP.

## Repository layout

```
designs/            immutable source bundles: contract.yaml, brief.md, sources/, reference/
  _template/        seed copied by `opencad stage-bundle`
  <asm>/            assembly.yaml, brief.md, sources/; parts/<leaf>/ its part bundles; .amended/<leaf|assembly>-N/ replaced versions
parts/<backend>/<part>/  worker deliverable (`main.kcl` or `main.py`)
results/<backend>/<part>/  stage JSONs, snapshots/, export/, handoff/, report.html; worker/NNN-<role>/ work orders, telemetry.jsonl,
                    pipeline-state.json / attempt-state.json while a worker turn is pending (only handoff/ and gate_feedback.json
                    are committed, for each design and part design; meshes through Git LFS. designs/ .amended/ and ECR sources/
                    copies, and parts/ worker scratch, stay local)
parts|results/<backend>/<asm>/parts/<leaf>/  the same per part design of an assembly, beside the assembly's own files
results/_regress/   regression bench reports; baseline.json, baseline-assembly.json and baselines/<tag>.{jsonl,md} (the promoted baselines, committed)
truth/              registry.yaml, cases/<case>/{manifest.yaml,mutants.yaml,inputs/,truth/,scorecards/,attempts.yaml}, calibration-log.yaml
                    change-request cases (<base>-ecr<n>: an arm with `ecr:`, inputs/contract-delta.yaml) and held-out assembly tasks (task.yaml)
src/opencad/       the control plane (below)
.cursor/skills/     cad-drive, initialize-cad, create-cad, cad-qa, regress, create-assembly (Cursor skills)
.agents/skills/     backends/{zoo,cadquery,build123d,freecad}/ (worker packs; Zoo: kcl-docs, kcl-examples, kcl-research, zoo-tooling), codex-worker (opt-in Codex dispatch)
smoke/              toolchain smoke campaign (CLI, MCP, Codex worker when opted in)
scripts/            setup_env.sh; derive_*_truth.py case builders (scorer-side OpenCascade, no Zoo); render_reference.py,
                    dimension_sheet.py, pdf_pages.py (agent-facing views and sheets from evaluator CAD); derive_ecr_case.py,
                    rpi5_ecr_deltas.py (change-request cases and reference-derived contract deltas); select_fusion_joints.py
docs/               validation-envelope.md (generated by `truth report`), design-ladder.md, exemplar-contract.yaml
                    (inlined into draft briefs), notes/
```

A part design of an assembly is named `<asm>-<leaf>`; the design name stays its identity everywhere (contracts,
handoff STEPs, telemetry, truth manifests), and `designs/<asm>/assembly.yaml` naming it is what nests its three
folders. Build a design's paths with `design_dir`, `part_dir` and `results_dir` (`src/opencad/paths.py`), never
`ROOT / name`.

`src/opencad/`: `schemas` (contract), `contract` (load/check/stage/publish), `paths`,
`io` (stage JSON, hashes, provenance), `zoo` (CLI wrappers + engine ledger + classify/lock), `worker/`
(work orders, role profiles, dispatch policy, resumable state, opt-in Codex backend with budget fallback),
`codex` (brief building blocks, report parsing, Codex event timeline), `telemetry` (per-turn/stage/attempt rows, bench,
promote), `backends/` (registry, `pyrunner` for CadQuery and build123d, per-backend language and engine; Zoo's `kclsrc`
tokenizer and parameter rewriter), `initialize` (headless contract draft), `interfaces` (preserved-item
measurement for edits and change requests), `reference/` (mesh and profile ingest), `stages/` (blockout, plan,
model, verify, export, inspect_stage, edit, ecr, decompose, pipeline), `geomcheck/` (brep via OCP, mesh via trimesh,
features, multibody, assembly, gears), `gates`, `report`, `truth/` (manifest, runner, scorer, regress, parity,
extra_kinds, mutants, assembly_task, assemble, machine, performance, effort, report), `assembly/` (the machine pipeline),
`sim/` (runtime, mesh, calculix, openfoam, reduced), `cli`/`orchestrator`.

Modelling rules reach every brief through `language.rules()`: `KCL_RULES` in `backends/zoo/rules.py` for Zoo; for CadQuery,
build123d and FreeCAD, `SHARED_RULES` in `backends/local.py` (millimetres, contract parameters as literal top-level constants,
asserts but never an equality lock between parameters, no reference geometry) plus `backends/<id>/rules.py`.

## Configuration

- Worker models: `src/opencad/worker/profiles.py` (drafts `claude-opus-5-5-max`, every other role `grok-4.7-xhigh-fast`, since the host dropped `grok-4.7-medium-fast` on 2026-09-27;
  per-role wall budgets and Codex effort). `OPENCAD_MODEL` / `OPENCAD_MODEL_<ROLE>` override the model (`inherit` gives the
  Task the orchestrator's model), `OPENCAD_BUDGET_<ROLE>` the budget in seconds, `OPENCAD_CODEX_EFFORT` every role's effort
  (`max` is GPT-6 Astra Max; a per-role `OPENCAD_CODEX_EFFORT_<ROLE>` wins).
  Briefs inline the schema, skills and critic method; `OPENCAD_LEAN_TURNS=0` restores full-read briefs.
- Codex: `--worker codex` / `OPENCAD_WORKER=codex` runs turns through `.agents/skills/codex-worker/scripts/codex_exec.py`
  (`model=gpt-6-astra`; a 300 s idle watchdog, 900 s at effort `max`). `worker/codex_backend.py` gives `codex exec` its own
  process group only so the watchdog can kill a hung turn; it is not a detached runner. An exhausted Codex budget (rate limit,
  spend cap, no credits) hands the turn to the `cad-worker` and records it in `results/<backend>/_campaign/worker-state.json`,
  unless `OPENCAD_CODEX_NO_FALLBACK=1`, which stops the run. A resume id recorded as a Cursor agent is not passed to `codex exec resume`.
  `/bake-off` and `python -m opencad.bakeoff run` set that variable and `--worker codex --tag bakeoff-astra`. Token USD uses the fast-tier card in `worker/pricing.py` (`usage.json` sums every `turn.completed`). A Zoo cell's monetary cost is the balance delta in `results/<backend>/<part>/cost.json`.
- Backends: `--backend` / `OPENCAD_BACKEND` (default `build123d`). CadQuery, build123d and gmsh run in the repo `.venv` (`uv add`;
  pins in `uv.lock`). FreeCAD is the installed `freecadcmd` (`OPENCAD_FREECADCMD`, default
  `/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd`), never imported into the venv. Hosted Zoo calls are billed and
  serialised by `OPENCAD_ZOO_LOCK` (default `~/.cache/opencad/zoo.lock`; one path per concurrent part).
- Solvers: CalculiX `OPENCAD_CCX` (default FreeCAD's bundled `ccx`); OpenFOAM image `opencfd/openfoam-default:2412` in Apple
  `container`, Docker as fallback (`OPENCAD_CONTAINER=container|docker` pins one).
- Memory (`opencad.resources`): every local engine call (analyze, export, `quick`) takes one of `OPENCAD_ENGINE_SLOTS`
  machine-wide slots (default cores - 1, capped at (RAM - `OPENCAD_MEM_HEADROOM_GB`, 16) / `OPENCAD_ENGINE_MEM_GB`, 8: six on a
  64 GB Mac), starts only while its budget plus half the headroom is free (after `OPENCAD_MEM_WAIT_S`, 1800 s, it fails as
  `resource`), and is killed by an RSS watchdog past `OPENCAD_ENGINE_MEM_GB` (class `memory`: the model's failure, so a correction
  turn, never a tooling retry). The edit stage exports at most `OPENCAD_EDIT_WORKERS` (4) variants at once; the kinematics and
  gear-mesh pools (`OPENCAD_KIN_WORKERS`, `OPENCAD_MESH_WORKERS`) and assembly part lanes (`--jobs`) are capped by the same count;
  a lane starts only while `OPENCAD_LANE_MEM_GB` (4) is free and is killed, with its state kept, when its own RSS passes twice the
  engine budget. Sources over `OPENCAD_MAX_SOURCE_LINES` (4000) lines or `OPENCAD_MAX_SOURCE_LITERALS` (6000) numeric literals
  fail `source_hygiene` and `independence` as traced geometry. Turn and stage telemetry rows carry `peak_rss_gb` and `oom_killed`,
  with an alert past 75 % of the budget.

## Lifecycle

### 1. Initialize — `/initialize-cad`

`python -m opencad stage-bundle <part>` seeds `designs/.staging-<part>/`. Text sources
are read by the orchestrator; drawings are attached to the worker as images; meshes go through
`python -m opencad.reference ingest` (declared unit, axes map, datum, unit anchor,
sections, silhouettes, `reference.json`); coordinate tables through `... profile`.
`python -m opencad draft` sends the worker the intent, sources and schema; the worker writes
`contract.yaml` and `brief.md` in place and must make `check-bundle` print `ok` (up to
three rounds). `publish` is one same-filesystem rename into `designs/<part>/`. `check-bundle` runs
`contract.lint_contract` (seal radius vs port, void-point clearance, blind-floor normals, edit estimates on lofts and
sweeps, sweep values vs declared infeasible values); a published design is evaluated as written.
`python -m opencad preflight --backend <id>` probes the selected engine; a failure (Zoo billing hold, missing
`freecadcmd`, import error) stops a run before any worker turn.

`python -m opencad blockout designs/<part>` asks the worker for an envelope-only KCL (no
fillets, holes or patterns), exports STEP, and measures it with OpenCascade. `zoo kcl
analyze` is recorded as evidence (and may be missing on a transient). The bounding box is
checked against `envelope` and the volume against `acceptance.blockout`. Four views plus an
isometric are rendered. At most two iterations. It is a scale/frame checkpoint, not
validation.

For a machine, `/initialize-cad` first states the goal (`Goal: assembly` when the request describes bodies moving relative to
each other, a fluid region, operating conditions or performance predictions), then runs `assembly stage` and
`assembly drive <asm> --stop-after blockout`: the drafts, the frame cross-check, publication and every part's blockout (see the
assembly pipeline section). `/create-cad designs/<asm>` then runs `assembly drive <asm>` from the parts stage.

### 2. Create — `/create-cad` = `python -m opencad run`

| stage | writes | what it establishes |
|---|---|---|
| plan | `plan.md`, `plan.json` | the worker's construction sequence, parameter map, invariants, risks (read-only) |
| model | `parts/<backend>/<part>/main.*`, `model.json` | the source, worker agent/thread id, self-reported verification |
| verify | `verify.json`, `snapshots/` | format/lint/hygiene (`ok` does not require analyze); engine measurements and snapshots are evidence (missing engine recorded as `status: missing`); nine crease-aware views (`view-all.png` 3×3) plus `view-symmetry.png` when the contract declares a mirror |
| export | `export/`, `export.json` | STEP exported twice with identical sha256, STL (mm, Z-up), GLB (glTF metres, Y-up; local backends map `(x, y, z)` mm → `(x, z, -y)` m) |
| inspect | `inspect.json` | OCP: validity, solid count, volume, area, COM, bbox; sections (area/loops/holes/regions, Common or Section-wire fallback); named faces (`mode`/`center`); cylinders (axis, radius, extent, hole/pin), inclined planes, dimensions; solids by contained point, hardware envelopes and clearances, passages (voxel flood fill), wall thickness (inward ray casts), probes, cylinder counts (optional `region`), gear teeth and meshing sweeps; void shells; KCL-STEP-STL agreement (engine volume optional); deviation vs `reference/` (ten signed bands along the reference's longest axis, the worst 2 % clustered, `deviation-map.png`; a band over the p95 limit is a failing item); `acceptance.symmetry` mirror-plane deviation on the STL |
| edit | `edit.json` | each `edit_test`: rewrite the defining module's constant, export STEP, OCP deltas vs expectation, interface preservation; optional `sweep` (regeneration over N values) and `infeasible_deltas` (an assert must refuse them); baseline re-export hash unchanged |
| ecr | `ecr/<label>/` | `python -m opencad ecr`: revised contract from a delta, the worker edits the part on its model thread, verify->gates re-run, preserved interfaces compared with the baseline STEP; an infeasible request must be refused with the KCL unchanged |
| gates | `gate_feedback.json` | 12 gates with tier, evidence, failure meaning, permitted knob; retry record |
| report | `report.html`, `report.md`, `contact-sheet.png`, `handoff/` | human review artefact and downstream package |

Gates: A `contract_provenance`, `envelope`, `mass_properties`, `features`,
`reference_fidelity`; B `export_agreement`, `edit_robustness`, `source_hygiene`;
C `export_integrity`, `traceability`, `evidence_separation`, `independence`. Tier A means
"fix the contract or the model", B "reconcile before trusting", C "artifact truth, never
repaired in place". One bounded retry covers tier-A failures and model-attributable
export failures; it changes the KCL, then verify/export/inspect/edit run again.

### 3. Validate — `python -m opencad.truth`

`regress` (the `/regress` skill) is the regression suite: one draft per case, then every case x backend in
parallel (`--resume-from blockout --force` per backend), numbered `EVENT#k` lines for the orchestrator, a
summary, and the bench report against the baseline that `python -m opencad telemetry promote` set.

`run <case>` sequesters that case's `truth/`, `manifest.yaml`, `mutants.yaml`, `scorecards/` and `attempts.yaml`
(concurrent runs share one vault and the last to leave restores; they stay vaulted across worker handbacks: the
command exits 75, the orchestrator runs the order, `run <case> --arm <arm> --continue` re-enters at the recorded
point), stages
inputs, ingests references declared by the arm (mesh or profile, including nondimensional
`scale_to_mm`), drafts the contract through a worker turn, publishes, runs the blockout and the
pipeline, restores truth, scores, and appends to `attempts.yaml`. `--resume-from` continues
an interrupted attempt: `publish` takes `designs/.staging-<design>`, `blockout` keeps a
published design, `pipeline` keeps a passed blockout (fresh plan/model), `retry` keeps the
modelled part and its thread (verify, gates, the bounded retry). `score` compares the
handoff STEP/STL with the manifest observables (bbox, volume, COM, sections with region
matching, named faces with `mode`/`center`, cylinders and cylinder counts with an optional
`region`, planes, dimensions, solids/clearances/passages/thickness/probes, teeth and
`gear_mesh`, deviation p95/Hausdorff/silhouette IoU, closed or open `profile2d`,
`not_matching`) and logs an attempt; an arm with `ecr: <label>` scores
`results/<design>/ecr/<label>/handoff/` (after `python -m opencad ecr`). `mutate <case>`
scores the deliberately wrong parts in `mutants.yaml` (each must FAIL while the baseline
passes). `assemble <case>` runs a task-driven held-out assembly case (`task.yaml`). Default
`--mode modelled` on local backends: the worker writes `parts/<backend>/<case>/main.py` that
imports the two dataset STEPs, places them, and assigns `result` plus `placements`; the
pipeline exports a 2-solid STEP, agrees each solid with input×placement, writes
`work/assembly.yaml` from the dict, and scores with `truth/assembly_task.py` against the
dataset joint. `--mode placement` (Zoo default) is yaml-only. The task text (v2) states each
side's joint key point and axis in the body's local frame plus the evaluator's definitions
(`inputs/joint-task.json`); `assembly-check <work> [--entry main.py --backend <id>]` is the
worker's local critic. Every scored attempt writes
`results/<backend>/<case>/handoff/assembly.{glb,html}` (`truth/assembly_viz.py`): the bodies
with the joint animated along its degree of freedom, a model-viewer page with a joint slider
and body/ghost toggles, the dataset pose as a translucent ghost. `status` lists live cases,
latest verdicts, vault orphans, and `task.yaml` assembly cases; `restore <case>` merges an abandoned
run's vault back into the tree and re-pins.
`report` writes `docs/validation-envelope.md` with reliability and effort columns.

Truth classes: A physical measurement; B reference geometry published by the benchmark
authors; C derived from published dimensions; D self-consistency; E illustrative.

Current envelope (class, source kind → result):

| case | class | what it proves |
|---|---|---|
| coupon / bracket | D / training | plumbing, holes, fillets, edit tests, engine-bbox trap |
| NASA backstep | C, text | derived flow domain, named faces, no equality-lock |
| NIST bridge drawing | B, figures | drawing reading, 12-leg pattern, sealed cavity, coplanar tabs |
| NIST bridge mesh | B, STL | reference ingest, same solid from a mesh |
| SPLEEN C1 | B, xlsx | dense profile, LE/TE landmarks vs farthest-pair, table-over-CAD, v1 `not_matching` |
| chiral-keyplate | D, text | C4 pinwheel; volume/silhouette survive a mirror, centred floors and `not_matching` do not |
| NASA ATB bump | C, inch text + surfpts | first revolve; unit trap (in → mm); open-polyline meridian |

## What a PASS means

A pipeline PASS: the KCL, its exports and the contract agree within the declared
tolerances, the model is parametric in the contract's terms, and the artefacts are
deterministic and traceable. A scorecard PASS: the exported geometry matches the pinned
external reference within the manifest's bands. Neither is engineering validation,
manufacturability, or physical inspection; downstream targets (flow reattachment, part
distortion, blade loading) are recorded in the manifests and never scored by CAD.

## Known engine behaviours (recorded, not worked around silently)

- `zoo kcl analyze` bounding boxes can include internal cut-tool extents (about 10 % of a
  negative-extrude depth on each side); volumes are tessellated (+0.007 % on the bracket).
  Engine numbers are evidence; OpenCascade on the exported STEP is the verdict.
- `zoo.classify` maps recorded strings: `transient` ("modeling connection interrupted" /
  "please reconnect and retry") is retried; `credits` raises `ZooCreditsError` and stops
  without briefing the worker; `kcl` ("KCL execution failed") is a geometry class and may brief
  the worker; `timeout` is CLI 124. The ledger stores one row per attempt. `run(engine=True)`
  takes `fcntl.flock` on `~/.cache/opencad/zoo.lock` (`OPENCAD_ZOO_LOCK` relocates it);
  the workers' own `zoo` calls are unlocked (recorded per order by `opencad zoo --ledger`); give concurrent parts their own lock.
- A missing engine volume yields `kcl_vs_step_rel: None` and `engine_missing: true`;
  `export_agreement` then depends on STL vs STEP and discloses the class. A `kcl`-class
  verify failure fails the gate. Snapshot flakes after a good analyze are recorded, not
  fatal. `tooling_failed` covers verify/export `transient`/`timeout` so the worker is not
  retried on a dead connection.
- Credit UX prints plan, prepaid remaining, PAYG price, and a forecast call count
  (analyze, snapshots, STEP×2, STL, GLB, edit exports). A cell's Zoo cost is the
  prepaid-credit and monetary-value delta in `results/<backend>/<part>/cost.json`
  (`credits-before.json` at blockout start, `credits-after.json` when the run finishes).
- `hole::` `cutAt` is read in the target face's local frame (see `smoke/README.md`).
- Touching bodies exported to one STL share edges, so the combined mesh is non-manifold while
  every shell is closed: `export_integrity` judges watertightness per shell when
  `solid_count > 1` (`mesh.components_watertight`). The gear meshing sweep (`gears.mesh_motion`)
  is coarse-to-fine (12 parallel coarse poses, then the requested fine resolution around the
  worst pose): 23 poses in about 70 s instead of 73 in 20 minutes, same verdict. Inspect and edit
  results are cached by the hashes of what they measure (`opencad.cache`, `OPENCAD_NO_CACHE=1`
  disables).
- Snapshots, the GLB and the determinism re-export run after the gates (`pipeline.finish`), so
  the retry decision waits for two hosted calls (analyze, STEP + STL) instead of ten; the edit
  stage exports up to `OPENCAD_EDIT_WORKERS` variants concurrently, each in an engine slot, and
  measures them sequentially (the STEP reader is not thread-safe).
- macOS does not enforce `RLIMIT_AS`: a build123d runner reached 41 GB under the 4 GiB limit (a
  rear shell traced into 34,000 numeric literals), and four part lanes rebuilding such models for
  their edit tests took the machine down. `resources.Watchdog` therefore polls each runner's RSS
  (0.25 s) and kills it past the budget. Every CAD process descends from the editor's agent shell,
  so an unbounded run shows as the editor holding the machine's memory.
- OpenCascade planar sections through B-spline solids carry about 0.2 % area bias; the
  planar end faces are exact. When `BRepAlgoAPI_Common` is not done, `brep.section` falls
  back to `BRepAlgoAPI_Section` wires (`method`).
- `codex exec` refuses a `--cd` outside a trusted project directory; spikes live under
  `results/_spikes/`. A control-plane edit while `truth run` is in flight is invisible to
  that process (hot-reload); do not change `src/opencad` expecting the live interpreter
  to pick it up.

## Decomposition and corrections

Large contracts (above 50 parameters or 25 features, after a kernel-stuck attempt, or `--decompose`) are modelled
in parts. A `partition` turn writes `partition.yaml` (feature groups, each with a spatial `region`), `params` and a
`datum`; one `module` turn per group runs in parallel against a sub-contract; a composition probe composes datum +
modules step by step, measures every step and names the module whose step first broke an item; the `integrate`
turn starts from those findings. After the gates, corrections are short targeted turns: three are granted, turns
4–6 (`OPENCAD_MAX_CORRECTIONS`) are earned by a falling failing-item count, and the loop stops on an identical
failing set or two turns without progress. A correction that leaves a non-executing source is reverted to the
worker's checkpoint. Correction briefs lead with a ranked `Fix first` block and attach the part beside the input
renders; budgets scale with the work (see `worker/profiles.py`, times the engine's `turn_factor`).
`python -m opencad kcl-bisect <main.kcl>` names the first failing `|>` step of a Zoo part.
`python -m opencad.truth parity <case>` (evaluator-side) maps every truth observable to its nearest contract item
and reports missing or looser counterparts; contracts are tightened from worker-visible sources, never relaxed.

## Assemblies, motion and simulation

`designs/<asm>/assembly.yaml` (`AssemblyContract`, `src/opencad/schemas.py`) names the bodies (modelled parts are ordinary part
bundles, design `<asm>-<leaf>` at `designs/<asm>/parts/<leaf>/`; purchased parts carry catalog geometry; a fluid region or a housing wall is a `derived` body the
assembly source builds by booleans; a supplied model that is not a physical body, such as a flow-region CAD, is a `construction`
input: staged, never placed), joints as frames in each body's own frame forming a tree from `datum_part` (plus one `closure: true`
joint per closed loop: a four-bar's last pin, a crank-slider's guide), transmissions (ratio, gear mesh check; `carrier` for an
epicyclic mesh, where a rigid driver is a fixed ring; a gear from a revolute to a slider is a rack in mm/deg), fluid volumes (walls,
bodies inside, port caps, seed), named boundaries (plane, cylinder, region, touching, rest), operating cases, observables (what to
predict, never a measured value) and simulations (`reduced:<model>`, `calculix`, `openfoam`) whose inputs carry provenance.
`contract.lint_assembly` cross-checks each joint's child frame (and a rigid joint's parent frame) against the drafted part
envelopes (a moving joint's axis may pass beside a stationary parent) and counts each motion's follower joints against the loop and
transmission equations.

Joint values (`assembly/joints.py`): a pure tree with plain transmissions propagates driven = ratio x driver exactly. Closure joints
and carrier meshes make the values the solution of the constraint system (transmission equations relative to the carrier; a closure
joint's frames coincide per kind), solved by damped least squares from the previous pose in steps of at most 2 deg or 2 mm so a loop
keeps the branch it was assembled in; a rank-deficient system reports the joints the drive leaves free. Kinematic observables
(`joint_value`, `joint_range`, `point_x|y|z`, `transmission_ratio` of one body) are evaluator measurements computed on that path with
the measured tooth or rack ratios substituted for the declared ones.

`python -m opencad assembly drive <asm>` (`src/opencad/assembly/pipeline.py`) runs, in one foreground process:

| stage | module | writes | establishes |
|---|---|---|---|
| draft | `assembly/draft.py` | `designs/<asm>/`, `designs/<asm>/parts/<leaf>/` | one `asm-draft` turn, then one part draft per design in parallel, frame cross-check, publish |
| parts | `assembly/parts.py` | each part's `parts/<be>/<asm>/parts/<leaf>/`, `results/<be>/<asm>/parts/<leaf>/` | every design through blockout + the part pipeline, one lane subprocess each (`assembly part <design>`) |
| assemble | `assembly/assemble.py` | `parts/<be>/<asm>/{inputs/,main.py}` (zoo: `main.kcl` + `placements.json`) | handoff STEPs and catalog solids staged; the worker places them (critic `assembly check-source`); on zoo the KCL imports the STEPs and `ZooEngine.build_assembly` exports them |
| verify | `assembly/verify.py` | `verify.json`, `export/` | one engine build; each solid matched to its body and agreed with input x placement; joint fidelity; clearances; envelope; mass |
| kinematics | `assembly/kinematics.py` | `kinematics.json` | every motion sweep with transmissions propagated and loops solved (closure residual per pose), pairwise interference per pose (parallel, bbox-prefiltered), gear meshing, ratio from tooth counts (external, internal ring, rack pitch), limits |
| domains | `assembly/domains.py` | `domains.json`, `boundaries/*.stl` (copied into `package/boundaries/` by report) | fluid region by boolean (padded box minus walls and inner bodies; a port whose plane the fluid crosses elsewhere closed by a local plug, others by a half-space; sealed, volume band, p99 agreement with the source's fluid body); every face of a bounded body on exactly one boundary |
| simulate | `assembly/simulate.py`, `sim/` | `simulate.json`, `sim/<id>/` | each analysis over its mesh ladder; observables with u_iteration, u_discretisation (the ladder's GCI), u_numerical and `resolved`; conservation; `unavailable` when a solver is missing |
| gates | `assembly/gates.py` | `gate_feedback.json` | A parts_pass, bom_complete, joint_fidelity (a joint a checked gear mesh couples sits within 0.2 x its backlash_max of its axis), clearances, motion_clear, fluid_domain; B export_agreement, performance, conservation, refinement (every prediction of every mesh ladder resolved; a lost level fails it; one-level analyses are listed as having no discretisation estimate); C source_hygiene, boundaries_complete, provenance, evidence_separation; up to two correction turns on the assemble thread (placements only; a contract error goes back as `--amend <evidence.md>`: one asm-draft turn on the drafter's thread, re-publish, re-place from assemble) |
| report | `assembly/report.py`, `assembly/viz.py` | `report.md/html`, `handoff/`, `package/` | `assembly.glb` (the `operate` clip only) and `assembly-clips.glb` (a clip per motion, `operate`, `explode`), each body under one pivot node per moving joint; model-viewer page on the clips file; per simulation its model, assumptions and mesh ladder level by level (cells, values, u_iteration, drift, GCI, observed order, Richardson value); per prediction its uncertainty, whether it is resolved, and its validation basis from `docs/validation-envelope.json` (also `package/evaluation/validation.json`); the engineering package |

`--stop-after draft|blockout` is the `/initialize-cad` checkpoint for a machine: it stops once the drafts are published, or once
every part's blockout has run (`assembly part <design> --blockout-only`, in parallel lanes), and clears the state so a plain
`drive` later starts at `parts`, where a part whose blockout passed goes straight to its pipeline. With `--amend <notes.md>` it is a
pre-build revision (`draft.revise`): one asm-draft turn on the drafter's thread over staged copies of the assembly and every part
contract, the frame cross-check with its fix rounds, and each changed bundle republished (the previous version kept as
`designs/<asm>/.amended/<leaf>-N`, the assembly's own as `designs/<asm>/.amended/assembly-N`) with that part's blockout and build
results removed. Without `--stop-after`, `--amend <evidence.md>`
is the post-build engineering change above.

Solvers (`src/opencad/sim/`): `calculix.py` (gmsh C3D10 meshes from `sim/mesh.py`, boundaries mapped to element faces;
transient heat with the `friction_brake` source, static with centrifugal and pressure loads, modal), `openfoam.py` (snappyHexMesh
on the labelled fluid STL, MRF zone about the rotor axis, simpleFoam k-omega SST, patch pressures, mass balance, torque, probes;
`runtime.py` runs the image in Apple `container`, Docker as fallback; the container gets twice the mesh's memory estimate for
snappyHexMesh's castellation peak and one retry at twice that after a kill; a finished case is reused while its inputs hash the
same, also across a restart, which sets `sim/` aside as `sim.prev/` for the adapter to adopt from; a case whose inputs changed
starts from a clean directory; a run's start marker `started.json` (the inputs' hash) lets a later run recover a case whose driver
died while the container finished: same hash, solver at its end time and the parallel run reconstructed), `reduced/`
(small models with assumption lists: `brake_energy`, `peristaltic`, `pump_euler`, `reynolds_film` (finite partial-arc Reynolds with
cavitation, load balance and a thermal wedge), `stirling_schmidt` (rhombic-drive Schmidt analysis)). Each machine case records a Run A
in `truth/calibration-log.yaml`: the reference geometry through these analyses, so model-form error is known before agent geometry is
scored.

Numerical uncertainty (`sim/__init__.py`, the same for every adapter). A steady OpenFOAM observable is the mean of its last 20 % of
iterations; `u_iteration` is the spread there and `drift` that mean against the 20 % before it. `Simulation.refinement` is the mesh
ladder coarse to fine, its last level the prediction: a size factor, or `{factor, regions: {<region>: n}, iterations}`, where
`Simulation.regions` names zones refined n levels past the finest surface cells (`rotor_tip`, the annulus spanning a rotor's tip
radius over its tips' axial reach; `cylinder`; `box`). The finest three levels give the grid-convergence index (Celik et al. 2008:
observed order capped at 2, Fs 1.25; a pair, or oscillating or diverging levels, Fs 3 at order 2; the refinement ratio from the cell
counts, 2 per level inside a region): `u_discretisation` = GCI x value and `u_numerical` = sqrt(u_discretisation^2 + u_iteration^2).
A prediction is `resolved` when every level finished, the finest three converge monotonically (or a pair differs little), GCI and
`u_numerical` <= `settings.refinement_tolerance` (0.05) of the value, no level's mean still trends (moves more than its own spread and
1 % between the last two fifths), and its finest steps refine everywhere (a step only inside a region is a sensitivity study of that
region). One level gives no discretisation estimate (`resolved: null`). `python -m
opencad sim study <asm> <sim> --case <id> [--levels JSON] [--regions JSON] [--set k=v] [--dry-run]` runs one case's ladder into the
same case directories (an amendment stating the same levels reuses them); `--dry-run` reports which runs a ladder would reuse.

Machine truth cases (`manifest.yaml kind: machine`, `src/opencad/truth/machine.py`): `truth run` sequesters truth for the whole run,
stages the arm's inputs as the draft request (the scored observable ids, not their values, go into the draft brief), drives
the assembly, then scores the assembled handoff STEP with the ordinary observables and the simulations with `performance:`
references (`truth/performance.py`: z = |pred - ref| / sqrt(u_meas^2 + u_num^2 + u_input^2) <= z_max, or an absolute tolerance
for exact references; series by RMS z). A prediction its ladder does not resolve is `unresolved`: its z is reported, it neither passes
nor fails, so a wide u_numerical never buys a pass. Evidence classes: A experimental, N numerical reference, C analytic, X extension
(never scored). Verdicts PASS / FAIL / INCOMPLETE (a required prediction's solver was unavailable or its ladder left it unresolved);
scorecards count required predictions by split and name each row's solver and model. `truth report` aggregates every machine
scorecard per solver and quantity into the validation envelope (`docs/validation-envelope.md` and `.json`: points by split, machines,
bias and spread of the relative error, worst z, pass / fail / unresolved, mesh-resolved count), which a machine without truth data
quotes as each prediction's validation basis. `scripts/fetch_reference.py` downloads references into the sequestered `truth/raw/`
with sha256, date and licence in `provenance.yaml`.

## Telemetry and baselines

Every worker turn, evaluator stage, gate evaluation and attempt is a row in `results/<backend>/<part>/telemetry.jsonl`
and `results/<backend>/_campaign/telemetry.jsonl` (`--tag` labels a run). `telemetry summary|timeline|compare|bench`
read them; `bench --tag <tag>` is the case × backend table with exclusive critical-path buckets
(worker > evaluator > interruption > latency > other), drafts shared by a regression listed apart.
`telemetry promote --tag <tag>` points `results/_regress/baseline.json` at a run and snapshots its rows and report to
`results/_regress/baselines/` (committed); `bench` compares against it by default. `python -m opencad dispatch <order>
--agent-id <id>` records who ran a turn; `python -m opencad next --stale S` shows orders nobody has touched, and
`next --watch --pid <pid>` blocks on the order files until one needs a worker (NEXT), a dispatched one stalls (STALE) or the
pipeline exits (EXITED), so the drive loop survives a dead terminal (pipeline output goes to `results/_logs/<name>.log`).

## Open residuals

Do not add a case to make a gate look better; add one when a failure class has been seen and is not yet a
required observable.

- Conical, toroidal and freeform walls have no sampled-point observable; deviation covers them only globally and per band.
- A structural change request (moved fasteners) leaves volume, COM and face areas undetermined; its delta must drop
  them explicitly (`scripts/rpi5_ecr_deltas.py` builds the determined ones from the reference).
- Deviation is sampled (20,000 points, seed 0), silhouette IoU is a 2400 px raster, and section island matching is
  greedy by centre distance.
- A computed KCL constant (`span = 100mm + 65mm`) still defeats the Zoo parameter rewriter.
- A blockout cannot be promoted to the deliverable without a model session.
- No CI runs `pytest` and `truth validate`.
- Corpus gaps: class A (CMM or scan), sweep/loft/helix, mates, an adversarial same-volume wrong part, fillet-heavy
  and organic B-rep, sheet metal, PMI and GD&T.
