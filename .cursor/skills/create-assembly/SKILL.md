---
name: create-assembly
description: Builds a whole machine with opencad, from sources to an animated, simulated, gated engineering package. It drafts an AssemblyContract and one part contract per design, runs every part through the part pipeline in parallel lanes, has a worker place the parts on their joints, then runs kinematics, fluid domains, simulations, gates and the report. Also drives machine truth cases (`truth run` on a machine manifest). Use when invoked as /create-assembly, or when a machine case or `python -m opencad assembly drive` needs driving.
---

# Create an assembly

`python -m opencad assembly drive <asm>` is one foreground process for the whole machine:
draft -> parts -> assemble -> verify -> kinematics -> domains -> simulate -> gates -> report.
It waits on every worker turn's `done` file and prints one numbered `EVENT#k {...}` line per hand-back
(its own turns and every part lane's), exactly like `/regress`. Your job is to dispatch the workers.

A new machine normally comes in through the two user-facing skills: `/initialize-cad` states `Goal: assembly`, stages the
sources and runs the checkpoint below (drafts plus every part's blockout), and `/create-cad designs/<asm>` runs the build from
the parts stage. This skill is the detailed reference for both, and the entry for machine truth cases (`--case`).

Each part design `<asm>-<leaf>` lives under its assembly: `designs/<asm>/parts/<leaf>/` (contract), `parts/<backend>/<asm>/parts/<leaf>/`
(source) and `results/<backend>/<asm>/parts/<leaf>/` (stage JSONs, handoff, work orders), beside the assembly's own files. Commands
(`drive`, `correct`, `next --part`, `check-bundle --name`) take the design name.

## Checkpoint and changes

- `assembly drive <asm> --stop-after draft` stops once the assembly and part contracts are published; `--stop-after blockout`
  then runs each part's blockout (`assembly part <design> --blockout-only`, in parallel lanes) and stops. Both clear the
  state, so a plain `assembly drive <asm>` later starts at `parts`, and a part whose blockout passed goes straight to its
  pipeline.
- Before anything is built, reviewer notes go back as `assembly drive <asm> --amend <notes.md> --stop-after draft`: one
  `asm-draft` turn on the drafter's thread edits staged copies of the assembly and every part contract, the frames are
  cross-checked again, and each changed bundle is republished (its previous version kept as
  `designs/<asm>/.amended/<leaf>-N`, the assembly's as `.amended/assembly-N`) with that part's blockout and build results removed. Re-run `--stop-after blockout` to redo those blockouts.
- After the build, evaluator evidence goes back as `--amend <evidence.md>` without `--stop-after`: one drafter turn on the
  published assembly contract, re-publish, re-place from `assemble` (see section 5 and `.cursor/skills/cad-drive`).

## Arguments

`/create-assembly <asm> "<intent>" @sources... [--backend build123d|cadquery|freecad]`, or a machine case:
`/create-assembly --case <case> [--arm <arm>]`. On `--backend zoo` the assembly source is `main.kcl`, which imports the staged
`inputs/*.step` and places them, plus a `placements.json` sidecar; the zoo CLI exports it. Derived (boolean-built) bodies are not supported on zoo.

## 1. Preflight

```bash
.venv/bin/python -m opencad preflight --backend <be>
.venv/bin/python -m opencad next            # must be empty for this machine's parts
container system status && container image list   # Apple container + opencfd/openfoam-default:2412 for CFD
ls /Applications/FreeCAD.app/Contents/Resources/bin/ccx
```

A missing solver is not fatal: its simulations come back `unavailable` (never zero) and the report says so.

## 2. Stage (new machines only)

```bash
.venv/bin/python -m opencad assembly stage <asm> --intent "<intent>" --source <file> ... --image <drawing> ...
```

`/initialize-cad` does this for a new machine. Machine truth cases stage themselves from the arm's inputs; skip this step.

## 3. Launch

Give the Shell call `block_until_ms: 20000` so it moves to the background and note the PID it reports; never detach it.
Output goes to the log file only (a `tee` into a terminal that dies kills the run at its next print):

```bash
mkdir -p results/_logs && caffeinate -i -s .venv/bin/python -m opencad assembly drive <asm> --backend <be> > results/_logs/<asm>.log 2>&1
# or, for a machine truth case (truth stays vaulted for the whole run):
caffeinate -i -s .venv/bin/python -m opencad.truth run <case> --arm <arm> --backend <be> > results/_logs/<case>.log 2>&1
```

Re-running the same command after an interruption continues at the recorded stage (`pipeline-state.json`); a
machine case re-enters with `--continue`.

`--jobs` (default 4) is capped by memory: no more lanes run than engine budgets fit beside the headroom (six on a 64 GB Mac), a
lane starts only while `OPENCAD_LANE_MEM_GB` is free, and every engine call is admitted and watched against its budget
(ARCHITECTURE.md, Configuration, Memory). A lane killed for memory exits with `reason: memory` and continues on the next drive.

## 4. Event loop

Same loop as `.cursor/skills/regress/SKILL.md` section 3: `opencad next --watch --pid <pid> --backend <be> --timeout 1800`
returns the `NEXT` lines of every undispatched order (launch one worker Task per line on its `model` with
`run_in_background: true`, all of a pass's lines in one message, and record each with `opencad dispatch <order> --agent-id
<id> --model <slug>` before watching again), `STALE` for a worker to resume once or relaunch, `EXITED` when the command ends,
or `TIMEOUT` (read the log tail and watch again). Use the regress worker prompt template, and the `generalPurpose` fallback
when the host offers no `cad-worker` type. Roles you will see: `asm-draft` (Opus, the assembly contract), `draft` (Opus, one
per part design, in parallel), `model`/`plan`/`correction`/`blockout` (Grok, inside each part lane), `assemble` and assembly
`correction` (Grok, the placement source `parts/<be>/<asm>/main.py`). Simulations can run for hours; while they do, the
log's `== simulate <id>` lines and `results/<be>/<asm>/sim/<id>/` show progress.

Use the `/regress` worker prompt template verbatim. Do not model, place or draft anything yourself, and never edit
`designs/`, `parts/` or `truth/` from the loop.

## 5. Review

On exit the command prints the verdict and writes:

- `results/<be>/<asm>/report.md` and `report.html` (BOM, joints, motion, fluid, simulations, gates);
- `handoff/assembly.glb` (the `operate` clip only, so viewers that play every clip at once show the machine running), `handoff/assembly-clips.glb` (clips `drive:<motion>`, `operate`, `explode`; the page's clip selector), `handoff/assembly.html`;
- `package/{source,assembly,geometry,boundaries,case,results,evaluation,provenance}`;
- for machine cases, `scorecard.json` (geometry checks on the assembled STEP, performance z-scores).

Before reporting a PASS: open `handoff/assembly.html` and look at two or three moments of `operate` (pause the model-viewer
and set its `currentTime`); read every failed or n/a gate's evidence; for each simulation, quote status and the conservation
residual, and for each prediction its value, u_numerical (u_discretisation from the mesh ladder's GCI, u_iteration from the
last 20 % of iterations), whether its ladder resolves it (and why not), and its validation basis (report.md, from
`docs/validation-envelope.json`). An unresolved prediction, or one whose basis reads `unvalidated`, is not evidence of
performance, whatever its value. A ladder needs three levels for a GCI and its finest steps must refine everywhere; to try a
ladder before the contract states it, run `python -m opencad sim study <asm> <sim> --case <id> --levels ... [--dry-run]`
(an amendment that states the same levels reuses those runs). An `INCOMPLETE` verdict means a required prediction's solver was
unavailable or its ladder did not resolve it: say which.
For a linkage (a contract with `closure: true` joints or `carrier` meshes), quote `kinematics.json motions.<m>.loop`
(`closure_mm_max`, `open_at`, `free`): a loop that opens or a joint the drive leaves free is a contract error (link lengths, rest
angles or a missing mesh), so it goes back as `--amend`, not as a placement correction. Kinematic observables (`joint_value`,
`joint_range`, `point_*`) are evaluator measurements with the measured tooth/rack ratios substituted; `simulate.json` names the source.
Individual stages re-run without workers: `python -m opencad assembly stage-run <asm> <stage> --backend <be>`.
