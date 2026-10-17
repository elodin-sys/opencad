---
name: regress
description: Runs the opencad parallel regression on demand. It drafts each truth case once (Opus) and runs every case x backend in parallel (Grok), handing every worker turn to a cad-worker Task. It then reports pass or fail per backend and the wall time against the promoted baseline. Use only when explicitly invoked as /regress.
disable-model-invocation: true
---

# Regression run

`python -m opencad.truth regress` is the driver. It drafts each case once and starts that case's backend runs as soon as its design publishes. It prints one numbered `EVENT#k {...}` line per worker hand-back, notice, skipped run or exit. It also runs the preflight and writes the report. Your job is to dispatch the workers.

## Arguments

`/regress [tag] [--suite parts|assembly] [--cases a,b] [--backends x,y,z] [--reuse-designs] [--promote]`

- Defaults: cases `bearing-housing,enclosure-base` (arm `spec-and-views`), backends `cadquery,build123d,freecad`. The first backend also runs the drafts.
- `--suite assembly` runs the passing machine cases (`regress.ASSEMBLY_SUITE`) on `build123d`. A machine case has no separate draft lane: each run drafts, waits on its own orders and scores in one `truth run`, on the case's first arm. Its orders include `asm-draft`, part drafts, `assemble` and corrections; dispatch them the same way.
- The default tag is `regress-<UTC yyyymmdd>`. Add `-2`, `-3` and so on when `results/_logs/<tag>/` already exists.
- `--reuse-designs` skips a case's draft when its design is already published. That is faster, but it does not re-test drafting.

## 1. Preflight

```bash
.venv/bin/python -m opencad.truth regress --check [--cases ..] [--backends ..]
```

Exit 2 lists what blocks a run: pending orders, vaulted or missing truth, or a failed engine preflight. Report it and stop; do not work around it. Warnings (battery power, model or lean-turn overrides) go into the report.

## 2. Launch

Run from the repository root. Give the Shell call `block_until_ms: 20000` so it moves to the background, and note the PID it reports:

```bash
mkdir -p results/_logs && caffeinate -i -s .venv/bin/python -m opencad.truth regress --tag <tag> [options] > results/_logs/<tag>.log 2>&1
```

Output goes to the log file only. Never pipe it through `tee` into the terminal: when the host restarts, the terminal dies and the session dies at its next print. Never detach it (`nohup`, `setsid`, `&`). Closing Cursor stops the session.

## 3. Event loop

The session writes numbered `EVENT#k {...}` lines to its log, but the orders themselves are files. Wait on the files with `next --watch`, which works even when a terminal has died. Repeat until it prints `EXITED`:

1. Run `.venv/bin/python -m opencad next --watch --pid <session pid> --backend <be> --timeout 1800` with `block_until_ms: 1900000`. It returns as soon as there is work:
   - `NEXT {...}` lines: every order nobody has dispatched yet. The orders of a pass arrive together.
     - If `resume` is null, launch `Task(subagent_type="cad-worker", model=<model>, file_attachments=<images>, run_in_background=true, prompt=<template>)`. Omit `model` only when it is `inherit`.
     - Otherwise resume `resume` with "Read the new brief at <prompt> and follow its Worker protocol; do not re-read the skills."
     - Launch all of a pass's `NEXT` lines in one message.
     - Record every launch before watching again, since the record is what marks the order as taken: `.venv/bin/python -m opencad dispatch <order> --agent-id <id> --model <model>`.
   - `STALE {...}`: a dispatched order has been idle past 1.25 × its budget (or past `--stale S`). Resume `resume` with `interrupt: true` and "Stop at the executing checkpoint; write result.md, metrics.json and done now." If nothing moves within 10 minutes, launch a fresh worker on the same brief and record it.
   - `EXITED` (exit 3): the session ended; go to section 4.
   - `TIMEOUT` (exit 4): nothing needed a worker for 30 minutes. Read the log tail and repeat.
2. `grep '^EVENT#' results/_logs/<tag>.log | tail` shows the session's other events: `exit` or `skipped` (note the run's verdict or why it did not run) and `expired` (resume with `interrupt: true` and "The order expired; stop now and write no more files.").

When a background Task returns, stamp it: `opencad dispatch <order> --agent-id <id> --model <slug> --finished`. This fails for a draft once its backend's run has reset the results directory. Skip it in that case.

Worker prompt template. The host has twice stopped offering the `cad-worker` agent type mid-session. When it is missing, launch `subagent_type="generalPurpose"` with the same template: its first line makes the agent read the worker rules, and the results were indistinguishable.

```text
You are a opencad CAD worker: read <repo root>/.cursor/agents/cad-worker.md first and follow it as your rules.
Execute one opencad work order. Repository root: <repo root> (run every command from there, with .venv/bin/python).

Read the brief first and follow its `## Worker protocol` literally; it is self-contained (deliverables, budget, critic commands):
<order.prompt>

Finish the protocol files (result.md, metrics.json, done) in <order.order>/. Reply with two lines: what you produced, and the critic's final verdict.
```

## 4. Finish

On exit the command:
- prints one row per run, a PASS or FAIL line per backend, and the session wall;
- writes `results/_logs/<tag>/summary.json`;
- writes the bench report `results/_regress/<tag>.md`, compared against the promoted baseline (`results/_regress/baseline.json`).

Exit 0 means every backend passed the scorecard and every gate. Read the summary from the log tail (`tail -40 results/_logs/<tag>.log`). Then:

1. Append a `## Findings` section to the report. Cover:
   - the verdict per backend;
   - the session wall against the baseline;
   - cell walls and their deltas;
   - gates and accuracy;
   - corrections and their causes, from each run's `gate_feedback.json`;
   - off-brief reads.
2. For every failed run, read and follow `.cursor/skills/cad-qa/SKILL.md` for that backend and part before explaining the failure.
3. Confirm the cleanup: `python -m opencad.truth status` shows no orphans, and `opencad next --backend <be>` is empty for every backend. An orphan left by an abandoned run goes back with `python -m opencad.truth restore <case>`.

## 5. Promote (only on request)

Promote only with `--promote` or when the user asks, and only when every backend passed:

```bash
.venv/bin/python -m opencad telemetry promote --tag <tag>                     # part suite
.venv/bin/python -m opencad telemetry promote --tag <tag> --suite assembly    # machine suite
```

This rewrites the suite's pointer and snapshots the tag's telemetry rows and report into `results/_regress/baselines/`, which is tracked in git. The part suite uses `results/_regress/baseline.json`; the machine suite uses `results/_regress/baseline-assembly.json`, so promoting one never moves the other.

A machine run relays its part lanes' `NEXT` lines behind a `[backend/part]` prefix. The session turns those into numbered events as well, so wait on `EVENT#k` as usual.

## Extending the suite

Any truth case with the arm can join through `--cases`. The next kind of run to add, for multi-part machine work, is assembly tasks (`truth/cases/<case>/task.yaml`, run with `truth assemble`). That needs a new `Lane` command in `src/opencad/truth/regress.py`.
