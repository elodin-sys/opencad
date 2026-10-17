---
name: create-cad
description: Runs the full opencad pipeline on an initialized part or machine. For a part, the cad-worker plans and authors the source through handback work orders, the pipeline verifies independently (OpenCascade on STEP, trimesh on STL), exports, tests editability, evaluates the 12 gates, and writes the report and handoff package, then the CAD QA review runs. For a machine (designs/<name>/assembly.yaml) it runs the assembly pipeline: every part in parallel lanes, placement, kinematics, fluid domains, simulations, gates and the report. Use only when explicitly invoked as /create-cad.
disable-model-invocation: true
---

# Create a CAD part or machine

Treat the text after `/create-cad` as the design argument.

## Resolve the argument

1. Require exactly one design. Accept `designs/<name>`, `<name>`, or a `contract.yaml` or `assembly.yaml` path. When
   `designs/<name>/assembly.yaml` exists, the design is a machine: follow **Machines** below; the part sections do not apply.
2. Work from the repository root with `source .venv/bin/activate`. Honour `--backend` /
   `OPENCAD_BACKEND` (default `build123d`). Local backends (cadquery, build123d, freecad) need
   no Zoo login; `python -m opencad preflight --backend <id>` must pass. A preflight
   failure stops the run — do not spend Zoo credits (account exhausted). `codex --version`
   only matters with `--worker codex`.
3. Reject `..`, absolute paths outside this repository, and anything that would write
   outside `designs/`, `parts/`, or `results/`.

## Missing design

If neither `designs/<name>/contract.yaml` nor `designs/<name>/assembly.yaml` exists, do not scaffold it here. Point to the
initializer, which decides whether the goal is a part or a machine, and stop:

```text
/initialize-cad <name> "<intent>" @requirements @drawings @tables @reference-mesh
```

## Machines

1. **Preconditions.** `python -m opencad assembly check designs/<name> --name <name>` prints ok. Every part design is published
   and its blockout passed at initialization (`results/<backend>/<design>/blockout.json` with `ok: true`); otherwise re-run
   `python -m opencad assembly drive <name> --backend <be> --stop-after blockout`, or proceed only when the user accepts
   building without it, and say so in the report. The open questions of the assembly and its parts are read: one that changes
   geometry is a stop (back to the revision step of `/initialize-cad` section 8). `python -m opencad next --backend <be>` lists
   nothing for this machine, and `python -m opencad preflight --backend <be>` passes.
2. **Build** with `python -m opencad assembly drive <name> --backend <be>`; it starts at the parts stage because the drafts
   are published. Follow `.cursor/skills/create-assembly/SKILL.md` sections 3 to 5: the launch with output to
   `results/_logs/<name>.log`, the `next --watch` event loop, and the review (the viewer at two or three moments, every failed
   or n/a gate, each simulation's conservation residual, each prediction's u_numerical, whether its ladder resolves it, and
   its validation basis).
3. A contract error the built machine exposes (a seat the parts cannot reach, an unmeasurable observable, a ladder that needs
   another level) goes back as `python -m opencad assembly drive <name> --amend <evidence.md>`, without `--stop-after`: one
   drafter turn, re-publish, re-place from `assemble`.

## Preconditions

1. `python -m opencad validate designs/<part>` passes and `brief.md` has no placeholders.
2. `results/<backend>/<part>/blockout.json` exists with `ok: true`. If it is missing or failed, run
   `python -m opencad blockout designs/<part> --backend <id>` and look at the four-view PNG first. Use
   `--skip-blockout` only when the user explicitly accepts running without the checkpoint,
   and say so in the report.
3. Read the contract's `open_questions`. A question that changes geometry (an unknown
   dimension the model must invent) is a stop: ask the user or send the part back to
   `/initialize-cad`. Questions about material, process, or downstream use may proceed.
4. Record `git rev-parse HEAD` and whether the tree is dirty; the stages stamp both. No
   commits are made by this skill.

## Run

Start the drive loop **as soon as preconditions pass**, before extra reading or a
status write-up. Read `.cursor/skills/cad-drive/SKILL.md` and follow it: every worker
turn (plan, model, correction) comes back as a work order with exit code 75 and a
`NEXT {...}` line; you launch a `cad-worker` Task with `model=<NEXT.model>`
(omit `model` only when `NEXT.model` is `inherit`), record its agent id in the
order's `dispatch.json`, and re-run the printed `continue` command until the run exits 0 or 1.

```bash
mkdir -p results/_logs
python -m opencad drive designs/<part> > results/_logs/<part>-create-cad.log 2>&1   # then read the log's tail
# exit 75 -> Task(subagent_type="cad-worker", model=<NEXT.model>, prompt=<NEXT.prompt contents>) -> drive again
```

```bash
python -m opencad drive designs/<part>                # plan, model, verify, export, inspect, edit, gates, report; continues an interrupted run
python -m opencad run designs/<part> --from-stage verify   # re-verify an edited parts/<backend>/<part>/main.*
python -m opencad run designs/<part> --no-retry       # disable the single bounded gate retry
python -m opencad drive designs/<part> --fresh        # discard an interrupted run's state on purpose
python -m opencad next                                # list pending work orders
```

Watch the log for `== plan`, `== model`, `== gates`, `== worker turn pending`, and
`report:`. The worker's own notes accumulate in `results/<backend>/<part>/model-work/`
(`construction-log.md`, `checkpoint.kcl`) and each order's `result.md`. With
`--worker codex` the segment instead prints `[codex]` event lines and
`python scripts/tail_codex_events.py results/<backend>/<part>/model-work/codex/events.jsonl` follows
the stream. Do QA only after the run exits 0 or 1.

The pipeline owns stage order, stale-artifact cleanup, the one bounded correction turn
(tier-A failures and model-attributable export failures, with measured-vs-expected
deltas to the same worker; then re-export / re-measure), and presentation. Do not replace
it with hand-picked stages. Do not edit `parts/<backend>/<part>/main.*` yourself: geometry changes
are worker turns (`python -m opencad correct <part> --backend <id> --note <md>` issues
the order on the model thread recorded in `results/<backend>/<part>/model.json` and re-verifies).

Stage outputs, all under `results/<backend>/<part>/` (for a part of an assembly, `results/<backend>/<asm>/parts/<leaf>/`,
with its source in `parts/<backend>/<asm>/parts/<leaf>/` and contract in `designs/<asm>/parts/<leaf>/`):

- `plan.md`, `plan.json` — the worker's construction sequence (read-only pass).
- `model.json` — worker agent/thread id, report sections, files written to `parts/<backend>/<part>/`.
- `worker/NNN-<role>/` — every work order: `brief.md`, `result.md`, `metrics.json`,
  `engine-ledger.jsonl`, `dispatch.json`; `telemetry.jsonl` — per-turn and per-stage rows.
- `verify.json` — format/lint/hygiene (`ok` is those three); `zoo kcl analyze` vs
  contract when the engine responds; snapshots. A missing analyze is disclosed, not
  a verify fail.
- `export.json` — deterministic STEP (two exports, hashes), STL, GLB.
- `inspect.json` — OpenCascade validity/volume/COM/bbox, sections, named faces, feature
  probes, KCL/STEP/STL agreement, deviation vs reference when one exists.
- `edit.json` — parameter edit tests and baseline re-export hash.
- `gate_feedback.json` — the 12 gates with evidence paths, tiers, and the retry record.
- `report.html`, `report.md`, `contact-sheet.png`, `handoff/` (STEP, STL, GLB,
  `properties.json`, `faces.json`, `provenance.json`).

## QA review

After the run, exit 0 is not a PASS to report. Read `.cursor/skills/cad-qa/SKILL.md` and
execute it: every gate is re-read from its evidence path, never inferred from `ok: true`;
at least one headline value is recomputed independently; open `view-all.png` and
`view-symmetry.png` and record per-view findings (each quarter and the underside); optional-feature
omissions and worker open questions are surfaced.

## Finish

Report: verdict (PASS/FAIL with the gate summary **and per-view findings**), the
measured-vs-expected table for bbox, volume, centre of mass, symmetry and every failed
check, `view-all.png` inline, the worker turns (role, model, wall time from
`telemetry.jsonl`) and engine-call total, the open questions, and links to
`results/<backend>/<part>/report.html`, `parts/<backend>/<part>/main.*`, and `results/<backend>/<part>/handoff/`.
State explicitly that a PASS is agreement with the contract (and the reference model when
present), not engineering or physical validation. To iterate on geometry, issue a
correction turn with the failed evidence and re-run from `verify`; to change intent, edit
the contract and re-run from `plan`.
