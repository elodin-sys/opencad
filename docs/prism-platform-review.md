# Prism as a platform for the opencad pipeline

A survey of what Prism offers beyond the `prism` CAD backend proven in the bake-off, mapped against the 39 designs in
`designs/` and the way the pipeline validates them today. Written 2026-11-06 from inside a Prism session on this machine
(Prism 0.6.0 solver daemon, python-env build123d 0.11.1), so every "available / not installed" note below is what this
machine reports, not a brochure claim.

The short version: the CAD half of Prism is what the bake-off exercised. The larger half is a **simulation and evidence
workbench** — a bundled FEA solver, thirteen containerised third-party solvers behind one supervised daemon, meshing with
named sets, 3D field post-processing, typeset reports, and the orchestration features (sub-agents, scheduled runs,
plugins) that the bake-off used only in part. Most of that maps directly onto the seven machines in the corpus that
declare simulations, and onto the parts whose open questions are thermal or structural.

## 1. What Prism is, in the pipeline's terms

| Layer | What it is | opencad's equivalent today |
|---|---|---|
| Agent + sub-agents | A tool-using agent with spawnable sub-agents on any catalog model (`gpt-6-astra`, `claude-opus-5-5`, `grok-4.7`, …), notifications instead of polling, scheduled tasks | The Cursor `cad-worker` Task loop; Codex via CLI |
| Managed CAD env | build123d 0.11 + `navier_cad` (vetted sweeps/blends/profiles/patterns, materials) + `bd_warehouse` hardware; `prism_cad_run` builds, exports STEP, meshes with gmsh, checks overlaps/validity/units/mass and attaches a preview | The repo `.venv` (build123d 0.12, CadQuery), `quick`, OpenCascade inspection |
| CAD/mesh viewers | STEP viewer with body/face/edge selection the agent can read (`prism_cad_viewer_selection`), mesh viewer, `.ferro` and `.nvpost` viewers, camera control and PNG export | `view-all.png` renders from trimesh |
| Ferro (bundled FEA) | In-process linear static, modal, linear buckling, prestressed modal on Tet4/Tet10/Hex8/Hex20; loads: nodal, pressure, traction, body force, gravity, **centrifugal**, bearing; isotropic/orthotropic/temperature-dependent materials | CalculiX via FreeCAD's bundled `ccx` (`src/opencad/sim/calculix.py`) |
| Solver daemon (`navier-solverd`) | Pinned container images, run tracking, stage plans (mesh → check → decompose → solve → reconstruct → post), parallel `cores`, logs, cancel. Runtimes on this build: OpenFOAM v2512 (double and single precision), SU2 8.5, CalculiX 2.23, code_aster 17.5, Elmer 26.2, Basilisk, Project Chrono 10, Yade DEM, OpenModelica 1.27, ngspice 47, openEMS, Palace | `src/opencad/sim/runtime.py`: `opencfd/openfoam-default:2412` in Apple `container`/Docker, hand-rolled memory sizing and retries |
| Post-processing | `.nvpost` scenes (OpenFOAM cases, VTU/VTK/PVD, CalculiX `.frd`, NASTRAN `.op2`) with cuts, thresholds, contours; `postpro` method (converged-window rule, summary tables); `data-viz`; `computational-study-audit` | `simulate.json`, mesh-ladder GCI, matplotlib history plots |
| Documents | `engineering-reports` (Typst PDF: FEA/CFD reports, trade studies, memos), `presentations` (editable PPTX), `prism_render_preview` to look at the rendered pages | `report.html`/`report.md`, the `_site` build |
| Plugins (MCP) | Onshape, GitHub, GitLab, Slack, Linear, Notion, Atlassian, Smartsheet, Monday, Microsoft Files/Outlook/Teams, Sentry, LangSmith, rmfg | none |
| Cloud | NavierAI Cloud for solver jobs on AWS (per-job approval of command, machine and rate) | none |

**State of this machine today.** Solver daemon running; container engine is OrbStack and is *stopped* (every runtime shows
"Container engine unavailable"); no runtime installed; cloud runs are **not enabled for this organisation**; gmsh, Typst
and LibreOffice are not installed (Prism installs them on request). Ferro needs nothing. So the FEA path works now, the
CFD/container path needs OrbStack started and one image pulled (gigabyte-scale), and cloud is a conversation with
Navier, not a setting.

## 2. The corpus, and what each family would use

### Parts (24 designs: bracket, benchy, the Fusion and NIST reconstructions, enclosures, blades, …)

These are CAD-reconstruction problems, and the bake-off already measured Prism there. What else applies:

- **`prism_cad_run` as a second critic.** It reports overlapping bodies, invalid/negative-volume solids, unit mismatches on
  STEP re-import, and unlabelled bodies, with a preview that adds a cut-open section when bodies nest. The pipeline's
  `quick` is the gate critic and must stay so, but a worker can probe one feature inline (metres, `checks: "fast"`) before
  committing it — the worker pack already permits exactly that.
- **CAD viewer selection for assembly tasks.** The five `fusion-*-assembly` cases ask a worker to place two STEP bodies on a
  joint. In Prism the agent can open the STEP, read the user's (or its own) face/edge selection with centroid, normal,
  radius and axis, and derive the joint frame from real faces instead of parsing numbers out of a brief. The
  `design-to-cad` skill is built around this ("bolt a bracket to real structure faces"). It is a different worker method, not a
  pipeline change, and would be a fair A/B against the current `assembly-check` critic.
- **Casting parts** (`bearing-housing`, the cast flange in `fusion-*`): the `openfoam-sand-casting` skill does staged VOF
  filling and solidification screening for feeder/riser placement. Not in the contracts today; a natural *extension*
  observable if release status ever moves past reconstruction.

### Machines with reduced models only (nottingham-bearing, peristaltic-pump) and pure kinematics (four-bar, crank-slider, rack-pinion, gear-train, compound-train, planetary-set, sprite-*)

The pipeline's own kinematics (`assembly/joints.py`) and reduced models (`sim/reduced/`) are deterministic and fast; nothing
in Prism replaces them. What Prism adds is **dynamics**: Project Chrono (templates: four-bar linkage, slider-crank,
spring-damper, quadrotor hover) would turn a four-bar or crank-slider from a pose sweep into a time simulation with inertia,
joint reactions and driving torque; OpenModelica would model a pump with its motor and pipe network (`pipe-network-flow`,
`dc-motor-pid` templates). These are new observables, not better numbers for existing ones.

### Machines with declared field simulations — where the leverage is

| Design | Declared simulations (today) | Where it stands (`results/build123d/<m>/simulate.json`) | What Prism offers |
|---|---|---|---|
| **fan-01** (EAA N1UG axial fan) | `mrfDesign`, `mrfOffDesign`: steady MRF simpleFoam k-ω SST, snappyHexMesh on the labelled fluid STL, tip-gap mesh ladder | Runs (3.6 h for the design ladder); `dpts_q1403` **unresolved** (GCI 0.051 > 0.05; the finest step refines only the tip region); off-design points single-level; −25 % vs the measured 126.5 Pa | OpenFOAM v2512 under the daemon with parallel plan, run tracking and cancel; cloud machines for the ladder when enabled; `.nvpost` field views of the case (slices through the tip gap, wake); SU2 (`INC_RANS`) as a second solver on the same geometry; `postpro` converged-window reading |
| **fda-pump** | `cfdC5`, `cfd`: MRF simpleFoam | C5 unresolved (GCI 0.22); C1–C6 within 3–29 % of the FDA data | same as fan-01; the FDA benchmark has published velocity fields, which an `.nvpost` scene would let a reviewer compare by eye |
| **mixer-01** | `cfd`: MRF simpleFoam | finest levels **oscillatory** → unresolved | a transient sliding-mesh run (pimpleFoam + AMI) is the standard answer to an oscillating steady MRF solution; same runtime, different case shape; long enough to want the cloud |
| **axjet-c2** (17-part ducted fan) | `mrfCold` (OpenFOAM), `rotor1Stress` (static, centrifugal, bore fixed), `rotor1Modal` (6 modes) | CFD: 1 of 3 ladder levels did not finish in 9.3 h; **both CalculiX runs failed** (ccx exited after the banner) | **Ferro**: static with a `centrifugal` load (axis, centre, ω) and modal/prestressed modal on a Tet10 mesh from `meshing-for-fea` with the bore as a named surface — in-process, no container, minutes; `structural-design-study` if the rotor is ever sized rather than checked |
| **disc-brake** | `brakeThermal` (CalculiX transient heat with friction source), `brakeEnergy` (reduced) | Runs (25 min); peak temperature PASS, hotspot radius and dissipated heat FAIL vs reference | CalculiX 2.23 or code_aster as pinned containers (same solver, tracked runs); `.nvpost` on the `.frd` output for the temperature field; Elmer for a thermal-stress follow-on. Ferro does **not** do thermal |
| **aleph-stack-case**, **rpi5-enclosure** (parts, but with thermal open questions) | none declared; aleph's contract carries unresolved airflow/heatsink questions | — | the `openfoam-cht-multiregion` skill: steady conjugate heat transfer for electronics enclosures with a heatsink and fan (templates `heat-sink-cht-3d`, `cht-heated-block`); Elmer `heat-sink-pin-fins-3d` for a conduction-only screen. This is the one place a new *simulation* would answer an existing *open question* in a contract |

## 3. fan-01 in detail: what changes and what does not

The physics does not change. opencad already runs the right model (MRF, k-ω SST, mesh ladder with a Celik GCI) in an
OpenFOAM container; Prism runs the same family one version newer. The differences are operational and evidential:

1. **Run management.** `src/opencad/sim/openfoam.py` sizes memory itself, retries a killed snappyHexMesh at twice the
   budget, and reconstructs a run whose driver died. The daemon does the admission, parallel pipeline
   (`decomposePar` → `mpirun` → `reconstructPar`), log capture with per-run suffixes, and cancellation, and it records which
   image digest ran — the provenance `simulate.json` currently stores by hand. A `prism` entry in `sim/runtime.py` that
   submits the already-written case directory to the daemon (`prism solver submit` from the CLI, or the `prism_solver_run`
   tool when Prism orchestrates) and waits on the run id is a small adapter; case authoring, the ladder and GCI stay in opencad.
2. **Time.** The design ladder took 3.6 h on this machine and still left the finest level unresolved; axjet's did not finish.
   The daemon's core budget is the same machine. The real relief is NavierAI Cloud (per-job approval of machine and hourly
   rate), which this organisation does not have enabled. Worth asking for before the next machine campaign, since the
   `refinement` ladders are exactly the embarrassingly parallel work it suits.
3. **Looking at the field.** Today the pipeline reports scalars and a history plot. An `.nvpost` scene over the finished
   case (a cut through the rotor plane, a threshold on reversed flow at the diffuser, pressure on the blade) makes the
   −25 % at the design point reviewable: is the tip-gap leakage under-resolved, or is the chamber boundary derived in
   `domains.json` wrong? The scene lives in `package/` beside the report and opens in Prism's viewer.
4. **A second solver.** SU2's incompressible RANS on the same STL is a cheap independent witness for the pressure rise, in the
   spirit of the pipeline's "engine numbers are evidence, OpenCascade numbers are verdicts" rule applied to CFD.
5. **Reading convergence.** The `postpro` skill's converged-window rule and the `computational-study-audit` checklist
   (pre-registered reading of a result, error bars that are lower bounds, stale status in write-ups) are the same discipline
   `sim/__init__.py` encodes in `u_iteration`/`drift`; applying them to the write-up is the cheap part.

What Prism does **not** give fan-01: a validated answer. The reference is class A (measured), the model-form error of
steady MRF on this rig is unknown, and nothing in Prism changes that; `docs/validation-envelope.md` stays the place that
says so.

## 4. Orchestration features the bake-off did not use

- **Scheduled tasks.** `/regress` as a nightly unattended run (`prism_schedule_create`; runs refuse anything needing approval),
  with the bench report compared against the promoted baseline each morning.
- **Parallel sub-agents.** The aleph cell ran five module workers at once and finished in 1 h 33 m against 2.5–3.4 h for the
  sequential Codex cells. Machine part lanes (`assembly drive --jobs`) could do the same with one sub-agent per lane.
- **Plugins.** Onshape (the aleph bundles came from Onshape exports): design intake and ECR deltas straight from the document
  rather than a staged STEP. GitHub/Linear/Slack: the bake-off summary or a regression failure posted where people read it.
  All hosted; none require Node.
- **Reports.** `engineering-reports` typesets an FEA/CFD report PDF from the house templates (needs Typst, one install card);
  `presentations` builds a review deck from the bake-off numbers and renders; `prism_render_preview` lets the agent look at the
  pages before handing them over.

## 5. Limits and caveats, as found

- The daemon's OpenFOAM is v2512; opencad pins `opencfd/openfoam-default:2412`. Same physics, but a version bump that
  should be recorded in `simulate.json` provenance if the adapter switches.
- Ferro: linear static/modal/buckling/prestressed modal on one element type per mesh; no thermal, contact, nonlinear or
  shells. It covers axjet's two rotor analyses; it does not cover the brake.
- `prism_cad_run` is metres and writes STEP beside the script; inside this pipeline it is a probe, never the critic (already
  in the worker pack).
- Token metering for Prism-hosted turns is reconstructed from the thread record (lower bounds, `prism-estimate`), as documented
  in `docs/bake-off-experiments.md`; Codex cells are metered per request.
- Prism's build123d is 0.11.1 against the repo's pinned 0.12.0: a worker reusing a repo `build123d` example meets a few API
  differences (`Compound([...])`, `fillet_safe` refusing an equal minimum radius, as the bracket turn found).
- Cloud: unavailable here; local container runs need OrbStack started first (one click in the Solver Desk).

## 6. Suggested next experiments, in order of evidence per hour

1. **axjet-c2 rotor on Ferro** (no installs): mesh `rotor_1` with `meshing-for-fea` (bore as a named surface), author a
   static case with a `centrifugal` load at the operating speed and a 6-mode modal case, compare `rotor1TipGrowth` and
   `rotor1Mode1` with the contract's expectations. The two CalculiX runs that failed get an answer the same afternoon.
2. **fan-01 off-design through the daemon** (start OrbStack, pull `openfoam-2512`): add a `prism` runtime to
   `sim/runtime.py` that submits the existing `sim/mrfOffDesign/<case>` directories and reads the same result files; check
   `dpts_q1804`/`dpts_q0994` reproduce within `u_iteration`. That proves the adapter before the 3.6 h ladder uses it.
3. **An `.nvpost` scene in the fan-01 package**: rotor-plane cut and blade pressure from the existing finest-level case, no
   re-solve needed; decide from the picture whether the next ladder level should refine the tip gap or the chamber.
4. **aleph-stack-case CHT** as a new observable: steady conjugate heat transfer with the heatsink and fan, answering the
   contract's open airflow question; the CHT skill carries its own acceptance gate for "converged enough to quote".
5. **Nightly `/regress`** as a scheduled task against the promoted baseline.
6. **Cloud enablement** before the next machine campaign, so ladders run in parallel instead of serially on this laptop.
