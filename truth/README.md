# truth/ — external truth corpus

`cases/<id>/manifest.yaml` freezes a case: truth class, role, source, the `/initialize-cad`
intent, pinned `inputs/` (all the agent may see), pinned `truth/` (scorer-only), arms,
observables, and downstream targets that CAD never scores.

- `python -m opencad.truth validate` — manifests, sha256 pins, and leakage checks.
- `python -m opencad.truth run <case> [--arm A] [--force]` — sequesters `truth/`, the manifest,
  mutants, scorecards and `attempts.yaml` outside the repository, runs the headless initializer
  (worker contract draft, blockout) and the full pipeline on `inputs/`, restores, scores, and
  appends to `attempts.yaml`.
- `python -m opencad.truth regress --tag <tag>` — the regression suite (`/regress`): each case
  drafted once, every case x backend in parallel, the bench report against the promoted baseline.
- `python -m opencad.truth score <case>` — re-score an existing `results/<backend>/<design>/handoff`.
- `python -m opencad.truth report` — writes `docs/validation-envelope.md`.
- `python -m opencad.truth pin <case>` — fill sha256 pins after adding files (once).

Rules: never tune a pipeline against a `validation` case without recording it in
`calibration-log.yaml`; never edit a case to make it pass; scorecards are hash-bound to
manifest, inputs, truth, KCL, and STEP so stale evidence cannot be reported.
