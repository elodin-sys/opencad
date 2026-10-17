# Bench `regress-asm-20260927-2`

Generated 2026-09-27T17:13:52Z by `python -m skillkat telemetry bench --tag regress-asm-20260927-2`. Times in m:ss; buckets are exclusive (worker > evaluator > interruption > latency > other) and sum to the wall. Accuracy is the tolerance-normalized score (0-100). Estimated tokens are generated characters / 4, a lower bound. Off-brief reads are Read/Grep calls under `src/skillkat`, `tests/`, `truth/`, another part, or another order.

Session wall 51:05, first start to last finish across 6 attempts.
Regression (scorecard PASS and no failed gate): build123d PASS (6/6).

| case | backend | wall | verdict | gates | rounds | turns | worker | evaluator | latency | interruption | other | engine share | model | accuracy | est tokens | off-brief reads |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| compound-train | build123d | 45:39 | PASS | 10/10 | - | - | - | - | - | - | - | - | grok-4.7-xhigh-fast | - | 23180 | 0 |
| crank-slider | build123d | 30:53 | PASS | 10/10 | - | - | - | - | - | - | - | - | grok-4.7-xhigh-fast | - | 23138 | 0 |
| four-bar | build123d | 35:31 | PASS | 9/9 | - | - | - | - | - | - | - | - | grok-4.7-xhigh-fast | - | 27482 | 0 |
| gear-train | build123d | 39:06 | PASS | 10/10 | - | - | - | - | - | - | - | - | grok-4.7-xhigh-fast | - | 23088 | 3 |
| planetary-set | build123d | 51:05 | PASS | 10/10 | - | - | - | - | - | - | - | - | grok-4.7-xhigh-fast | - | 31224 | 0 |
| rack-pinion | build123d | 34:55 | PASS | 10/10 | - | - | - | - | - | - | - | - | grok-4.7-xhigh-fast | - | 25267 | 6 |

| cell | attempts | PASS | completion | median wall | p95 wall | median worker | median evaluator | median latency | accuracy | est tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| compound-train / build123d | 1 | 1 | 100% | 45:39 | 45:39 | 0:00 | 0:00 | 0:00 | - | 23180 |
| crank-slider / build123d | 1 | 1 | 100% | 30:53 | 30:53 | 0:00 | 0:00 | 0:00 | - | 23138 |
| four-bar / build123d | 1 | 1 | 100% | 35:31 | 35:31 | 0:00 | 0:00 | 0:00 | - | 27482 |
| gear-train / build123d | 1 | 1 | 100% | 39:06 | 39:06 | 0:00 | 0:00 | 0:00 | - | 23088 |
| planetary-set / build123d | 1 | 1 | 100% | 51:05 | 51:05 | 0:00 | 0:00 | 0:00 | - | 31224 |
| rack-pinion / build123d | 1 | 1 | 100% | 34:55 | 34:55 | 0:00 | 0:00 | 0:00 | - | 25267 |

All cells: 6/6 PASS (100%), median wall 37:18, p95 51:05, median est tokens 24224.

## Against the baseline `regress-asm-20260926-4`

Per cell: median wall and its delta (this bench minus the baseline), completion, gates, mean accuracy and median estimated tokens.

| cell | median wall | delta | completion | gates | accuracy | est tokens | baseline wall | baseline accuracy | baseline tokens |
|---|---|---|---|---|---|---|---|---|
| compound-train / build123d | 45:39 | +9:51 | 1/1 | 10/10 | - | 23180 | 35:48 | - | 24941 |
| crank-slider / build123d | 30:53 | +2:24 | 1/1 | 10/10 | - | 23138 | 28:29 | - | 26283 |
| four-bar / build123d | 35:31 | +6:52 | 1/1 | 9/9 | - | 27482 | 28:38 | - | 29233 |
| gear-train / build123d | 39:06 | -9:39 | 1/1 | 10/10 | - | 23088 | 48:45 | - | 26675 |
| planetary-set / build123d | 51:05 | +6:34 | 1/1 | 10/10 | - | 31224 | 44:31 | - | 28772 |
| rack-pinion / build123d | 34:55 | +5:33 | 1/1 | 10/10 | - | 25267 | 29:21 | - | 22274 |

Median wall 37:18 (baseline 32:35, delta +4:44).

Evaluator stages (mean s per run, by backend):

| stage | build123d |
|---|---|
| domains | 3 (n=6) |
| edit | 66 (n=23) |
| export | 0 (n=23) |
| finalize | 26 (n=23) |
| gates | 0 (n=52) |
| inspect | 11 (n=23) |
| kinematics | 48 (n=6) |
| simulate | 3 (n=6) |
| verify | 26 (n=29) |

Worker turns (median worker s / engine share, by role and backend):

| role | build123d |
|---|---|
| asm-draft | 563 / 0.00 (n=6) |
| assemble | 193 / 0.26 (n=6) |
| draft | 379 / 0.00 (n=23) |
| model | 313 / 0.11 (n=23) |

## Findings

- Verdict: build123d PASS 6/6. Every case passed its scorecard (accuracy 99.8 for gear-train, 100 for the other five) and every
  gate: 10/10 each, and 9/9 for four-bar, whose contract states no performance requirement.
- Session wall 51:29 against the baseline's 48:45 (regress-asm-20260926-4); median cell 37:18 against 32:35 (+4:44). The whole
  session ran beside the FAN-01 tip-gap CFD study, which held 8 of the 12 cores (a 4.2 M-cell simpleFoam run). Gear-train ran
  9:39 faster, the other five 2:24-9:51 slower. This morning's session (regress-asm-20260927, 38:50) ran with no CFD beside it.
- This is the final iteration-3 code: the passage-volume bracket, the lint for observables nothing measures, the requirement
  band, the report and viewer uncertainty columns, the CFD recovery marker and the `sim` command module rename came after the
  morning session. None of them changed a mechanism result.
- Corrections: none. Every lane passed on its first model turn and its first placement.
- Off-brief reads: the table's 9 (gear-train 3, rack-pinion 6) are placement turns re-reading their attached part renders and
  the machine's own part contracts, both listed by the brief. The part lanes add 2 that are genuine: the rack-pinion-base model
  worker read two windows of `src/skillkat/backends/local.py` after `engine --help`, to learn the engine command's arguments.
  It wrote nothing there, and its part passed.
- The drive loop was `skillkat next --watch --pid`, with the session's output only in its log file; no worker turn went stale.
- Cleanup: `truth status` shows no vault orphans in any of the 33 cases, and `skillkat next --backend build123d` lists no
  pending turn.
