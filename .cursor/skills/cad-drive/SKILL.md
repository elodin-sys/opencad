---
name: cad-drive
description: The drive loop that runs any opencad pipeline command (drive/run, blockout, draft, ecr, correct, truth run/ecr/assemble) to completion by handing each worker turn to a `cad-worker` Task sub-agent. Use whenever a opencad command exits 75 and prints a `NEXT {...}` line, or when /create-cad, /initialize-cad, or a truth run needs to be driven end to end.
---
# cad-drive: the handback loop

opencad's pipeline never models CAD itself and, by default, never calls Codex. Pass `--backend`
(or `OPENCAD_BACKEND`) so parts and results land under `parts/<backend>/<part>` and
`results/<backend>/<part>` (a part of an assembly: `<asm>/parts/<leaf>` in both, and in `designs/`; commands
still take the design name). When a stage needs a worker turn (draft, blockout, plan, model,
correction, ECR, correct, assembly), the command writes a work order under
`results/<backend>/<part>/worker/NNN-<role>/`, prints one line

```text
NEXT {"action":"worker","part":"...","id":"003-model","role":"model","model":"grok-4.7-xhigh-fast","budget_s":2700,"prompt":".../brief.md","images":[...],"resume":null,"dispatch_record":".../dispatch.json","done":".../done","continue":"python -m opencad drive <part>"}
```

and exits with code **75**. Everything else (verify, export, inspect, edit, gates, report, scoring)
runs inside the command.

## Loop

1. Run the command in the foreground from the repository root with `source .venv/bin/activate`,
   its output redirected to `results/_logs/<name>.log` (`> results/_logs/<name>.log 2>&1`, then read
   the log's tail); never pipe it through `tee`, since a terminal that dies takes the run with it at its
   next print. Segments are evaluator work and usually take
   seconds to a few minutes; gears and large sweeps can take 20 minutes. Run a segment in its own
   Cursor sub-agent only when it is expected to exceed ~10 minutes or when several parts run in
   parallel; never detach it.
2. Exit code 0/1: the run finished; **exit 0 is not a PASS to report**. Read
   `.cursor/skills/cad-qa/SKILL.md` and execute it first. A PASS message must carry
   per-view findings (each quarter and the underside, plus `view-symmetry.png` when
   present). Exit code 2: a pipeline error; read it. Exit code **75**: parse the
   `NEXT` line (or run `python -m opencad next`).
3. Launch the worker: `Task(subagent_type="cad-worker", prompt=<contents of NEXT.prompt>,
   file_attachments=<NEXT.images>, model=<NEXT.model>)`. `NEXT.model` is the role's model from
   `profiles.py` (drafts on `claude-opus-5-5-max`, every other role on `grok-4.7-xhigh-fast`)
   or an override; omit `model` only when it is `inherit`, so the Task uses this conversation's
   model. When `NEXT.resume` is not
   null, pass `resume=<NEXT.resume>` instead of `model` (a resumed agent keeps the model it
   started with; record that model in the dispatch record) and tell it to read the new
   order's `brief.md` without re-reading the skills. Pass the brief verbatim (or point the
   worker at its path); it already contains the protocol, budget and deliverables. Do not
   add instructions that change the contract, and do not model anything yourself. When the host
   offers no `cad-worker` agent type, launch `generalPurpose` with the worker prompt template of
   `.cursor/skills/regress/SKILL.md`, whose first line has it read `.cursor/agents/cad-worker.md`.
4. Right after launching the Task, record its agent id and the model it runs on (`NEXT.model`, or this session's model
   when that is `inherit`). Later turns resume that worker, and the bench report shows the model:
   `python -m opencad dispatch <NEXT.order> --agent-id <task agent id> --model <slug>`
   Run it again with `--finished` when the Task returns. If the worker did not create
   `NEXT.done`, check `result.md`; a worker that stopped without finishing the protocol gets one short
   follow-up Task (resume) asking only for the protocol files.
   Idle rule: `python -m opencad next --stale 1200` lists dispatched orders nobody has touched for 20
   minutes (`idle_s` = newest mtime under the order dir, its ledger, deliverables and writable dirs). Such a
   worker is stuck mid-tool: send one resume asking for the protocol files; if nothing moves within another
   10 minutes, launch a fresh `cad-worker` on the same brief (no `resume`) and record the new id.
5. Run `NEXT.continue` (for example `python -m opencad drive <part>` or
   `python -m opencad.truth run <case> --arm <arm> --continue`). Repeat from step 2.

## Waiting instead of re-running (`--wait`)

`truth run|ecr` and `opencad run|drive` accept `--wait`: after printing a `NEXT` line the command keeps
running, polls the pending orders' `done` files every 5 s and continues by itself, so a finished turn
is picked up within seconds instead of when this loop next looks. The printed `continue` command
carries `--wait` (and `--tag`) for the case where the waiting process is gone.

1. Start the command with a short `block_until_ms` (about 20 s) so the shell call returns while it waits.
2. Launch the worker for each `NEXT` line and record its id (step 4 above).
3. `AwaitShell` on that shell with `pattern` matching the next order's sequence number or a stale line,
   for example `NEXT .*"id": "004-|^STALE ` after order 003 (the pattern matches old output too, so
   key it on the next number), and a long `block_until_ms`. It returns on the next `NEXT`, on `STALE`,
   or when the command exits; repeat from step 2.
4. `STALE {...}` means a dispatched worker has been idle for more than 1.25 × its budget: resume
   `STALE.resume` with `interrupt: true` and "stop at the executing checkpoint, write result.md,
   metrics.json and done now". If nothing moves within 10 minutes, launch a fresh `cad-worker` on the
   same brief and record the new id. The waiting command picks the result up either way.
5. With `--enforce-budgets` (opt-in, with `--wait`) a turn past 1.5 × its budget is taken at its executing
   deliverable or the worker's checkpoint and the command prints `EXPIRED {...}`: resume `EXPIRED.resume`
   with `interrupt: true` and "the order expired; stop now and write no more files".

With the output in a log file, wait on the order files instead of the terminal:
`python -m opencad next --watch --pid <pid> [--backend <be>] [--timeout S]` blocks until an order nobody has
dispatched appears (its `NEXT` line), a dispatched one goes idle past 1.25 × its budget (`STALE`, or past `--stale S`),
or the process exits (`EXITED`, exit 3). Record each dispatch before watching again; that record marks the order taken.

Worker Tasks run on the role's model; role models and budgets live in
`src/opencad/worker/profiles.py`. `OPENCAD_MODEL` / `OPENCAD_MODEL_<ROLE>` override one
run or role (`inherit` hands the Task this conversation's model); `--worker codex` runs the
turns through the local Codex CLI instead and falls back to this loop when its budget is exhausted.

## Parallel module turns

A decomposed part (`--decompose`, automatic for large contracts or after a kernel-stuck attempt)
prints several `NEXT` lines at once, one per feature-group module. Launch one `cad-worker` Task per
line in a single message (they have separate scratch directories and deliverables), wait for all of
them, record each agent id, then run the `continue` command once. The same applies to the
correction rounds of a decomposed part: `correction-N-<module>` orders (one per module that owns a
failing item) come out together and run in parallel; the integrate correction follows on the next
`continue`. Between the module turns and the integrate turn the pipeline itself exports and
measures the composition step by step (no worker; several hosted calls), so that `continue` takes
a few minutes.

A run that stops with a **preflight failure** (Zoo billing hold, missing `freecadcmd`, or a
backend import error) is not a pipeline failure: nothing is modelled, no order is issued; fix
the engine (or pick another `--backend`) and re-run the same command. Do not spend Zoo credits;
that account is exhausted: replay recorded Zoo artefacts instead.

## Machines (`assembly drive`, machine truth cases)

`python -m opencad assembly drive <asm>` and `python -m opencad.truth run <machine case>` never exit 75: they wait on
each order's `done` file and print numbered `EVENT#k {...}` lines for their own turns and for every part lane. Drive
them with the `next --watch` event loop of `.cursor/skills/regress/SKILL.md` (section 3); `.cursor/skills/create-assembly/SKILL.md`
covers launch and review.

A correction turn only moves placements. When its worker shows the placements already sit on the contract's joint frames
and the failing check is the contract itself (a seat the supplied parts cannot reach, an envelope the parts overrun, a
tolerance ideal geometry assumes), write that evidence to a markdown file and run
`python -m opencad.truth run <case> --arm <arm> --amend <file>` (or `assembly drive <asm> --amend <file>`). One
`asm-draft` turn continues the drafter's thread on a staged copy of the published contract. The bundle is re-checked and
re-published, and the machine is re-placed from `assemble`. Truth stays sequestered throughout.

## Several parts at once

Each part has its own state (`results/<part>/pipeline-state.json`) and orders, so two or three
drive loops can run concurrently: pass `--parallel` (a per-part engine lock instead of the global
one), launch their worker Tasks in one message, and never let two loops drive the same part.

## Model override (optional)

Every run can be labelled: `--tag <label>` stamps each telemetry row. To pin a different
model than the role defaults for a comparison run:

```bash
OPENCAD_MODEL=<slug> python -m opencad drive coupon --fresh --tag ab-<label>
python -m opencad telemetry compare tag:ab-a tag:ab-b
```

Change a role default in `profiles.py` (`DRAFT_MODEL`, `WORK_MODEL`), never in a brief.

## Do not

- Edit `parts/<backend>/<part>/main.*`, `designs/<part>/contract.yaml`, or anything under `truth/` from the
  drive loop. Geometry changes are worker turns; a part's contract changes go back through
  `/initialize-cad`, a machine's through `assembly drive <asm> --amend <file>` (with `--stop-after draft` before
  anything is built).
- Start a fresh run while an order is pending (`python -m opencad next` lists them). `drive`
  continues automatically; `--fresh` discards the state on purpose.
- Detach the command (`nohup`, `setsid`, `&` + ignore SIGHUP). Cursor closing is an anomaly.
