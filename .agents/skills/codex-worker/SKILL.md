---
name: codex-worker
description: Opt-in dispatch of a bounded task to the local Codex CLI (GPT-6 Astra; per-role reasoning effort, catalog context window, Fast tier) returning its report, thread id and token usage. The pipeline uses it only with `--worker codex` / OPENCAD_WORKER=codex and falls back to the Cursor cad-worker when the Codex budget is exhausted. Use for an independent second opinion or when the user asks for Codex explicitly.
---
# codex-worker

Cursor orchestrates; by default the `cad-worker` Task sub-agent executes CAD turns through work orders (see AGENTS.md and `.cursor/skills/cad-drive`). This skill is the opt-in Codex path: `python -m opencad <cmd> --worker codex` or `OPENCAD_WORKER=codex`, or a direct dispatch for an independent review.

## Dispatch

```bash
python3 .agents/skills/codex-worker/scripts/codex_exec.py [--cd DIR] [--read-only] [--image PATH]... \
  [--resume THREAD_ID] [--run-dir DIR] [--timeout SEC] "BRIEF" [-- extra codex exec args]
```

- Worker settings: `workspace-write` sandbox with network (Zoo engine reachable), `approval_policy=never`, `model=gpt-6-astra`, `model_reasoning_effort=$CODEX_REASONING_EFFORT` (default `high`; the pipeline sets it per role, or `OPENCAD_CODEX_EFFORT` for every role, `max` for GPT-6 Astra Max), `service_tier=$CODEX_SERVICE_TIER` (default `fast`; empty omits it), the catalog context window unless `CODEX_CONTEXT_WINDOW` is set, `model_auto_compact_token_limit=$CODEX_COMPACT_LIMIT` (default 160000). `--read-only` is for reviews: no writes, no network.
- `--cd` is Codex's working root and its only writable tree. Point it at a scratch directory for prototypes and at the repository root only when Codex should edit real files. The directory must sit inside a trusted project (`~/.codex/config.toml` `[projects]`), so use `results/_spikes/<name>` rather than `/tmp`; otherwise `codex exec` exits 1 with "Not inside a trusted directory" (or pass `-- --skip-git-repo-check`).
- Stdout: a summary header (`run_dir`, `thread_id`, `exit`, `seconds`, `commands`, `usage`) then the final message. The usage figures sum every `turn.completed` in the exec (a running thread total is billed from the last event only; `usage_mode` says which). Artifacts in the run dir: `prompt.md`, `events.jsonl`, `usage.json`, `stderr.log`, `result.md`. Exit code is Codex's; 124 means the timeout hit.
- Follow up on the same thread with `--resume <thread_id>` (no `--cd` or `--read-only`; the session keeps them). Record thread ids per task; never rely on `--last`.
- Pass `"-"` as the brief to read it from stdin; anything after `--` goes to `codex exec` verbatim (`--worktree`, `--output-schema FILE`, `--add-dir DIR`).

## Brief template

Codex sees none of the Cursor conversation, so the brief is self-contained:

1. Objective in one paragraph, plus the exact deliverable paths.
2. Inputs: files to read (absolute paths), reference images via `--image`.
3. Constraints: units, `kclVersion = 2.0`, allowed scope, what must not change.
4. Acceptance criteria with numbers: analytic volume, bounding box, centre of mass, tolerances, required exports.

The script prepends the worker contract (skills location, no nested Codex, no git writes) and requires the report sections `Result`, `Files changed`, `Verification`, `Open questions`.

## After the run

- Read `result.md`, then verify the claims independently: `zoo kcl analyze <dir> --format json --volume-output-unit mm3 --center-of-mass-output-unit mm`, `zoo kcl export`. Never accept unverified numbers.
- Non-zero exit or `turn.failed` in `events.jsonl`: report it; resume the thread with a precise correction instead of re-briefing from scratch.
- Concurrent implementation workers need separate `--cd` trees (or `-- --worktree`); concurrent read-only reviews are fine.
