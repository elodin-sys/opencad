# opencad

<img width="1153" height="550" alt="image" src="https://github.com/user-attachments/assets/fd9a67d6-287a-4395-9d39-f37878d37c13" />    


Agentic CAD on a pluggable modelling backend ([Zoo](https://zoo.dev)/KCL, [CadQuery](https://cadquery.readthedocs.io),
[build123d](https://build123d.readthedocs.io), or [FreeCAD](https://www.freecad.org) PartDesign), built the way
[open-air](https://github.com/elodin-sys/open-air) does aero design: a cheap, reviewable **initialize** step that
turns intent, documents, drawings, tables or a reference mesh into a part contract and a blockout checkpoint, and a
**create** step in which a Cursor `cad-worker` sub-agent authors the source one work order at a
time (Codex is opt-in) while an independent Python control plane measures it with OpenCascade and trimesh, evaluates twelve tiered
gates, and writes a report and a handoff package. A sequestered truth corpus scores the
result against external references. Pass `--backend cadquery|build123d|freecad|zoo` (or `OPENCAD_BACKEND`;
default build123d).

```
/initialize-cad <name> "<intent>" @docs @drawings @tables @reference.stl   # says part or assembly, drafts, runs the blockouts
/create-cad designs/<name>      # builds the part, or the whole machine
/regress                        # every truth case in the suite on every local backend, against the baseline
```

A request that describes bodies moving relative to each other, a fluid region, operating conditions or a performance
prediction is a machine: `/initialize-cad` drafts an AssemblyContract and one part contract per design and runs every part's
blockout; `/create-cad` then builds the parts in parallel, places them on their joints, and runs kinematics, fluid domains,
simulations, gates and the report ([create-assembly](.cursor/skills/create-assembly/SKILL.md) has the details).

The full map is [ARCHITECTURE.md](ARCHITECTURE.md). Skills read by the workers live in
`.agents/skills/`; Cursor skills (including the `cad-drive` handback loop) in `.cursor/skills/`;
the worker sub-agent in `.cursor/agents/cad-worker.md`; agent rules in `AGENTS.md`.

## Setup (no sudo)

```bash
./scripts/setup_env.sh          # uv-managed Python 3.12 .venv (pydantic, trimesh, cadquery, build123d, ruff, cadquery-ocp, ...)
source .venv/bin/activate
# Local backends need no Zoo login. Zoo (`--backend zoo`) is hosted and billed; this account is exhausted — do not re-run it.
# FreeCAD: install the app; default freecadcmd is /Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd (override OPENCAD_FREECADCMD). Never import FreeCAD into the venv.
codex login                     # only for --worker codex (opt-in); ~/.codex/config.toml: model = "gpt-6-astra"
python3 smoke/run.py --sections env,skills,cli   # optional toolchain smoke
python -m opencad preflight --backend cadquery  # or build123d / freecad / zoo
```

## Your first part

1. `/initialize-cad my-plate "80 x 50 x 6 mm plate with four 4.5 mm holes ..." @drawing.png`
   writes `designs/my-plate/{contract.yaml,brief.md,sources/}` and runs the blockout;
   look at `results/<backend>/my-plate/blockout/blockout-four-ways.png`.
2. `/create-cad designs/my-plate` (add `--backend cadquery` etc.) drives `python -m opencad drive designs/my-plate --backend <id>`:
   plan, model, verify, export, inspect, edit, gates, report. Each worker turn comes back
   as a work order (exit 75 + a `NEXT {...}` line) that the orchestrating agent runs with a
   `cad-worker` Task before re-running `drive`.
3. Review `results/<backend>/my-plate/report.html`, the gate table in `gate_feedback.json`, the source in
   `parts/<backend>/my-plate/`, and the STEP/STL/GLB plus `properties.json`, `faces.json`,
   `provenance.json` in `results/<backend>/my-plate/handoff/`.

Headless equivalents: `python -m opencad stage-bundle | draft | check-bundle | publish |
blockout | drive | run | next | telemetry | <stage>`. `python -m opencad --help`.

## Your first machine

1. `/initialize-cad my-mixer "inline mixer: a 4-blade impeller on the motor shaft inside a housing tube, pressure rise and torque at 1500 rpm" @spec.md`
   says `Goal: assembly`, stages the sources, and runs `python -m opencad assembly drive my-mixer --stop-after blockout`:
   the assembly contract and brief in `designs/my-mixer/`, one part bundle per design in `designs/my-mixer-<part>/`, and each
   part's `results/<backend>/<design>/blockout/blockout-four-ways.png`. Review them; changes go back as
   `python -m opencad assembly drive my-mixer --amend notes.md --stop-after draft`.
2. `/create-cad designs/my-mixer` runs `python -m opencad assembly drive my-mixer`: the part lanes, placement, verify,
   kinematics, fluid domains, simulations (each prediction with its mesh-ladder uncertainty and validation basis), gates and
   the report.
3. Review `results/<backend>/my-mixer/report.html`, the animated viewer `handoff/assembly.html`, and `package/`.

## Validation corpus

`truth/cases/` holds the pinned validation corpus: the NASA/Driver–Seegmiller
backward-facing-step flow passage (class C, text), the NIST AM Bench AMB2022-01 bridge
(class B; drawing-only and mesh-input), the SPLEEN C1 turbine blade (class B, table and
notes, plus a v1 `not_matching` CAD), the chiral-keyplate (class D, calibration), the NASA
TMR axisymmetric transonic bump (class C, inch-native text and surface points; first
revolve), and the improvement-campaign ladder: the NIST additive-manufacturing test
artifact (class B, 69 feature observables), the Prusa MINI extruder front (class B,
functional interfaces, plus a change-request case), the Raspberry Pi 5 two-piece enclosure
(class C, design to requirements, three change-request cases and an infeasible request),
the Voron Stealthburner duct (class B, interior passages and wall thickness), a spur-gear
pair (class C, tooth counts, involute profile and a meshing sweep), and five held-out Fusion
360 Gallery joint sets (reconstruction and assembly tasks). `python -m opencad.truth validate`
checks pins and leakage; `run` sequesters truth, drives the two skills headlessly through
worker turns (`--continue` after each handback), restores, scores; `ecr` does the same for a change request on a passing design;
`assemble` runs a held-out Fusion 360 assembly task, placing supplied parts (not the machine pipeline above; `assembly-check` is its local critic; every scored
attempt writes an animated GLB and a model-viewer page under `results/<backend>/<case>/handoff/`);
`mutate` proves the scorer rejects deliberately wrong parts; `report` writes
[docs/validation-envelope.md](docs/validation-envelope.md).
Changes made in response to a case are logged in `truth/calibration-log.yaml`; cases are
never edited to pass (authoring errors the agent exposes are corrected and logged).

## Cost and budget

The local backends (CadQuery, build123d, FreeCAD) cost nothing per engine call. Zoo is hosted and billed per
`zoo kcl analyze/export/snapshot` (about 40–55 calls per part); this account's allowance is exhausted, so Zoo runs
are replay-only: `python -m opencad credits` shows the balance, and `run`, `blockout` and `truth run` refuse to
start at zero credits.

## Regression

`/regress` (`.cursor/skills/regress`) reruns the regression suite on demand: each case is drafted once and every
case x backend runs in parallel, then the bench report compares the session with the promoted baseline
(`results/_regress/baseline.json`, snapshots in `results/_regress/baselines/`).

## Tests

```bash
pytest                      # schema, ingest, KCL static checks, gates on recorded stage JSONs, truth manifests
pytest -m engine            # (none yet) tests that need the hosted engine
```

A PASS from the pipeline means the KCL, its exports and the contract agree; a PASS from the
scorer means the exported geometry matches the pinned reference within the manifest bands.
Neither is engineering validation, manufacturability, or physical inspection.
