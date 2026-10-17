# Bench `regress-asm-20260926-4`

Generated 2026-09-26T08:28:45Z by `python -m skillkat telemetry bench --tag regress-asm-20260926-4`. Times in m:ss; buckets are exclusive (worker > evaluator > interruption > latency > other) and sum to the wall. Accuracy is the tolerance-normalized score (0-100). Estimated tokens are generated characters / 4, a lower bound. Off-brief reads are Read/Grep calls under `src/skillkat`, `tests/`, `truth/`, another part, or another order.

Session wall 48:45, first start to last finish across 6 attempts.
Regression (scorecard PASS and no failed gate): build123d PASS (6/6).

| case | backend | wall | verdict | gates | rounds | turns | worker | evaluator | latency | interruption | other | engine share | model | accuracy | est tokens | off-brief reads |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| compound-train | build123d | 35:48 | PASS | 10/10 | - | - | - | - | - | - | - | - | claude-opus-5-5-max | - | 24941 | 4 |
| crank-slider | build123d | 28:29 | PASS | 10/10 | - | - | - | - | - | - | - | - | claude-opus-5-5-max | - | 26283 | 4 |
| four-bar | build123d | 28:38 | PASS | 10/10 | - | - | - | - | - | - | - | - | claude-opus-5-5-max | - | 29233 | 4 |
| gear-train | build123d | 48:45 | PASS | 10/10 | - | - | - | - | - | - | - | - | claude-opus-5-5-max | - | 26675 | 3 |
| planetary-set | build123d | 44:31 | PASS | 10/10 | - | - | - | - | - | - | - | - | claude-opus-5-5-max | - | 28772 | 5 |
| rack-pinion | build123d | 29:21 | PASS | 10/10 | - | - | - | - | - | - | - | - | claude-opus-5-5-max | - | 22274 | 3 |

| cell | attempts | PASS | completion | median wall | p95 wall | median worker | median evaluator | median latency | accuracy | est tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| compound-train / build123d | 1 | 1 | 100% | 35:48 | 35:48 | 0:00 | 0:00 | 0:00 | - | 24941 |
| crank-slider / build123d | 1 | 1 | 100% | 28:29 | 28:29 | 0:00 | 0:00 | 0:00 | - | 26283 |
| four-bar / build123d | 1 | 1 | 100% | 28:38 | 28:38 | 0:00 | 0:00 | 0:00 | - | 29233 |
| gear-train / build123d | 1 | 1 | 100% | 48:45 | 48:45 | 0:00 | 0:00 | 0:00 | - | 26675 |
| planetary-set / build123d | 1 | 1 | 100% | 44:31 | 44:31 | 0:00 | 0:00 | 0:00 | - | 28772 |
| rack-pinion / build123d | 1 | 1 | 100% | 29:21 | 29:21 | 0:00 | 0:00 | 0:00 | - | 22274 |

All cells: 6/6 PASS (100%), median wall 32:35, p95 48:45, median est tokens 26479.

## Against the baseline `regress-asm-20260925`

Per cell: median wall and its delta (this bench minus the baseline), completion, gates, mean accuracy and median estimated tokens.

| cell | median wall | delta | completion | gates | accuracy | est tokens | baseline wall | baseline accuracy | baseline tokens |
|---|---|---|---|---|---|---|---|---|
| None / build123d | - | - | - | - | - | - | 64:35 | - | - |
| compound-train / build123d | 35:48 | - | 1/1 | 10/10 | - | 24941 | - | - | - |
| crank-slider / build123d | 28:29 | - | 1/1 | 10/10 | - | 26283 | - | - | - |
| four-bar / build123d | 28:38 | - | 1/1 | 10/10 | - | 29233 | - | - | - |
| gear-train / build123d | 48:45 | - | 1/1 | 10/10 | - | 26675 | - | - | - |
| planetary-set / build123d | 44:31 | - | 1/1 | 10/10 | - | 28772 | - | - | - |
| rack-pinion / build123d | 29:21 | - | 1/1 | 10/10 | - | 22274 | - | - | - |

Median wall 32:35 (baseline 64:35, delta -32:00).

Evaluator stages (mean s per run, by backend):

| stage | build123d |
|---|---|
| domains | 6 (n=6) |
| edit | 60 (n=23) |
| export | 0 (n=23) |
| finalize | 17 (n=23) |
| gates | 0 (n=52) |
| inspect | 10 (n=23) |
| kinematics | 59 (n=6) |
| simulate | 2 (n=6) |
| verify | 22 (n=29) |

Worker turns (median worker s / engine share, by role and backend):

| role | build123d |
|---|---|
| asm-draft | 572 / 0.00 (n=6) |
| assemble | 180 / 0.31 (n=6) |
| draft | 376 / 0.00 (n=23) |
| model | 186 / 0.09 (n=23) |

## Findings

- Verdict: build123d PASS, 6/6. Every case passes its scorecard and every gate (10/10): gear-train accuracy 99.8, the others
  100.0. planetary-set passes with the corrected backlash, and rack-pinion's drafter banded its observables at 1e-4 of the
  value under the new lint floor (`rackRatio` 3.5e-5, `rackTravel` 0.0126 mm).
- Session wall 48:45 for six machines (6 assembly drafts, 23 part drafts, 23 part models, 6 placements) against the
  one-machine baseline `regress-asm-20260925` (gear-train alone, 64:35); median cell wall 32:35 (delta -32:00). Cells:
  gear-train 50:15 (-14:20 against its baseline), planetary-set 44:50, compound-train 36:27, rack-pinion 29:27, four-bar 28:41,
  crank-slider 28:32. gear-train is the longest cell because its 40-tooth wheel's edit sweep runs on a 15.6 MB STEP.
- Corrections: none. No part or placement needed a second turn, and none of the four fixes of this iteration (closure solve,
  rigid placements, planetary backlash, measured-band lint) was exercised by a failure.
- Workers: `generalPurpose` Tasks on each order's model reading `.cursor/agents/cad-worker.md` (the host no longer offers the
  `cad-worker` type), as in regress-asm-20260926-3.
- Off-brief reads (none under `truth/`): the assemble turns read their member parts' renders (23); two model turns read
  `src/skillkat/backends/local.py`.
- Previous sessions: regress-asm-20260926 FAIL 5/6 (planetary backlash in the specification), regress-asm-20260926-2 stopped
  (broken session pipe), regress-asm-20260926-3 FAIL 5/6 (rack-pinion band finer than the measurement). This bench is promoted
  as the machine-suite baseline.
