# AGENTS.md

opencad: an agentic CAD pipeline for parts and machines with a scorer-only truth suite. [ARCHITECTURE.md](ARCHITECTURE.md) is the map (layout, stages, configuration).

## Rules

- Orchestrate, never model. CAD and spatial work (backend source, geometry, placement, reading drawings or renders) is a `cad-worker` Task on the work order's `NEXT.model`; you write briefs, verify independently (backend `engine.analyze`, OpenCascade on the exported STEP) and integrate.
- Never hand-edit `parts/<backend>/<part>/main.*` (an assembly's part: `parts/<backend>/<asm>/parts/<leaf>/main.*`); a geometry change is `python -m opencad correct <part> --backend <id> --note <md>`.
- A part design an assembly names (`<asm>-<leaf>`) lives under its assembly in all three trees: `designs/<asm>/parts/<leaf>`, `parts/<backend>/<asm>/parts/<leaf>`, `results/<backend>/<asm>/parts/<leaf>`. Commands take the design name.
- `designs/<name>/contract.yaml` or `assembly.yaml` is the intent; stages never relax it. `ok: true` in a stage JSON is a claim, `gate_feedback.json` is the verdict, the exported STEP is authoritative.
- `truth/` is scorer-only: never edit a case to pass; never tune against a case without a `truth/calibration-log.yaml` entry.
- Pipeline commands run in the foreground from the repo root with output redirected to `results/_logs/<name>.log` (never through `tee`); never detach (`nohup`, `setsid`, `disown`, `&`, `start_new_session`). Wait on worker orders with `python -m opencad next --watch --pid <pid>`. Never start a run for a part with a pending order (`python -m opencad next`).
- Never edit `src/opencad` while a pipeline segment is running (the interpreter keeps its imported modules); between segments is safe.
- Default backend `build123d` (`--backend`, `OPENCAD_BACKEND`).
- Codex only when asked (`--worker codex`); its scratch is `results/_spikes/<name>`, never `/tmp`.
- Visuals are animated GLBs and the HTML viewer; no GIFs or MP4s.
- Never commit, amend, push or open pull requests.

## Routing

- A command exits 75 and prints `NEXT {...}`: `.cursor/skills/cad-drive` (handback loop, `--wait`, `--amend`, model override).
- New part or machine from sources: `/initialize-cad` (it states whether the goal is a part or an assembly, drafts, and runs the blockouts). Build or fix either: `/create-cad`. Review a part result: `.cursor/skills/cad-qa`.
- Bake-off across backends: `/bake-off` (Astra via `--worker codex` authors every CAD turn, the Zoo CLI is the zoo engine, Cursor only orchestrates; the report adds tokens, USD, and time, then rebuilds `_site`, including the bake-off page).
- Machine detail (assemblies, motion, fluid domains, simulations, package; the checkpoint, revisions and amendments) and machine truth cases: `/create-assembly`.
- Regression, baselines, `truth status|restore`: `/regress`.
- Worker rules and critics: `.cursor/agents/cad-worker.md` (when the host offers no `cad-worker` type, a `generalPurpose` Task reads it first: the `/regress` prompt template); backend rules: `.agents/skills/backends/<id>/`; Codex: `.agents/skills/codex-worker`.
- A prediction is evidence only when its mesh ladder resolves it and `docs/validation-envelope.json` covers its solver and quantity; `python -m opencad sim study` tries a ladder.
- Models per role, `OPENCAD_*` variables, solver paths and locks: ARCHITECTURE.md, Configuration.
