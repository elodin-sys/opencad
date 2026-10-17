---
name: bake-off
description: Runs a design on every modelling backend with the Codex Astra worker, the Zoo CLI as the zoo engine, and Cursor only orchestrating. Wraps initialize-cad and create-cad, then writes a quality, token, cost, and time report. Use only when explicitly invoked as /bake-off.
disable-model-invocation: true
---

# Bake-off

Interpret the invocation as:

```text
/bake-off <design> [--backends cadquery,build123d,freecad,zoo]
```

Default backends, in order: `cadquery`, `build123d`, `freecad`, then `zoo`. Astra (`gpt-6-astra` via the Codex CLI) authors every CAD turn, including draft, blockout, plan, model, and correction. The zoo arm executes geometry through the `zoo` CLI. This session only starts commands, watches logs, and writes the report. Do not launch a `cad-worker` task. Do not judge renders in this session; a render pass is a read-only Astra dispatch.

Set these for every command below. An exhausted Codex budget must fail the cell, not hand it to Cursor. Astra runs on the fast tier at max reasoning.

```bash
export OPENCAD_CODEX_NO_FALLBACK=1
export OPENCAD_CODEX_EFFORT=max
export CODEX_SERVICE_TIER=fast
```

## 0. Part or assembly

- `designs/<design>/assembly.yaml` is a machine. Follow `.cursor/skills/create-assembly/SKILL.md` for the build, with `OPENCAD_WORKER=codex`, `OPENCAD_CODEX_NO_FALLBACK=1`, `OPENCAD_CODEX_EFFORT=max`, `CODEX_SERVICE_TIER=fast`, and `--tag bakeoff-astra` on `python -m opencad assembly drive`. The zoo arm places with `main.kcl` + `placements.json`. Afterwards run `python -m opencad.bakeoff compare-assembly <design>` to check every backend's handoff against build123d.
- `designs/<design>/contract.yaml` is a part. The sections below apply.
- Neither file: the design is missing. Initialize it once (section 1), then build it (section 2). State which, with the phrase that decided it, before any worker turn.

Bracket is a part and its contract is already published. Do not re-draft it.

## 1. Initialize, only when the design is missing

Follow `.cursor/skills/initialize-cad/SKILL.md` with one Astra draft, not a `cad-worker` task:

```bash
OPENCAD_CODEX_NO_FALLBACK=1 OPENCAD_CODEX_EFFORT=max CODEX_SERVICE_TIER=fast \
  python -m opencad draft designs/.staging-<design> --name <design> \
  --intent "<intent>" --worker codex --tag bakeoff-astra
```

The contract is shared. Publish it once. Then block out each backend as in section 2. An existing published contract is not re-drafted.

## 2. Preconditions

From the repository root, `source .venv/bin/activate`.

1. `python -m opencad next` lists nothing pending for this design. A pending order stops the run.
2. `python -m opencad preflight --backend <id>` passes for each backend. Zoo login is required only for the zoo arm. `codex doctor` shows `gpt-6-astra`.
3. Record `date -u +%Y-%m-%dT%H:%M:%SZ` as the orchestrator start. The CAD cost does not include this session.

## 3. Build each backend

CadQuery, build123d, and FreeCAD may run together (`--parallel`, separate result trees). The zoo arm runs by itself, after those three, so its credit snapshot is not mixed with another cell.

For each backend, blockout then drive. Logs go to `results/_logs/bakeoff-<backend>-<design>.log` (`> file 2>&1`, never `tee`). Run each command in the foreground. With `--worker codex` the process does not exit 75.

```bash
mkdir -p results/_logs
OPENCAD_CODEX_NO_FALLBACK=1 OPENCAD_CODEX_EFFORT=max CODEX_SERVICE_TIER=fast \
  python -m opencad blockout <design> --backend <id> \
  --worker codex --tag bakeoff-astra --parallel \
  > results/_logs/bakeoff-<id>-<design>-blockout.log 2>&1
OPENCAD_CODEX_NO_FALLBACK=1 OPENCAD_CODEX_EFFORT=max CODEX_SERVICE_TIER=fast \
  python -m opencad drive <design> --backend <id> \
  --worker codex --fresh --tag bakeoff-astra --parallel \
  > results/_logs/bakeoff-<id>-<design>.log 2>&1
```

`--fresh` deletes that backend's `parts/<backend>/<design>/main.*` and the stage artifacts from plan onward, then Astra re-authors the part. Blockout with no pending order rebuilds the envelope and resets `credits-before.json`.

A machine's part lanes use the same environment (`OPENCAD_WORKER=codex`, `OPENCAD_CODEX_NO_FALLBACK=1`, `OPENCAD_CODEX_EFFORT=max`, `CODEX_SERVICE_TIER=fast`, tag `bakeoff-astra`). A finished turn's `settings.json` records `reasoning_effort: max` and `service_tier: fast`.

## 4. Review

After a backend exits 0 or 1, re-read gates from evidence with `.cursor/skills/cad-qa/SKILL.md`. The render pass is one read-only Astra dispatch, not this session:

```bash
python3 .agents/skills/codex-worker/scripts/codex_exec.py --read-only --cd <repo> \
  --run-dir results/<backend>/<design>/bakeoff-review \
  "Open results/<backend>/<design>/view-all.png and view-symmetry.png. Under ## Verification write one Visual line per view: each quarter and the underside. Do not edit any file."
```

Record the written findings. Exit 0 is not a PASS.

## 5. Report

Write `results/_bakeoff/orchestrator.json` with this session's wall seconds (`{"seconds": N, "model": "grok", "note": "excluded from CAD cost"}`). Then:

```bash
python -m opencad.bakeoff report
```

That command writes `results/_bakeoff/report.md`, appends a clean four-backend entry to `results/_bakeoff/published.yaml`, and rebuilds `_site` (the bake-off page and the design pages). A custom `-o` path writes the markdown only. Before finishing, confirm the design is in `published.yaml` and in `_site/bakeoff/index.html`. If a local server is already serving `_site`, reload that page. Closing note, per backend: gate verdict, OpenCascade volume against the contract, Codex tokens and USD, Zoo credit delta when the backend is zoo, worker and wall seconds, fallback count (must be 0), and links to `results/<backend>/<design>/report.html` and `results/<backend>/<design>/handoff/`. State that a PASS agrees with the contract, and that orchestrator time is excluded from the CAD cost. A gate failure with complete metering is a recorded result and a failed readiness check.
