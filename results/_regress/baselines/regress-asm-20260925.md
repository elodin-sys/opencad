# Bench `regress-asm-20260925`

Generated 2026-09-25T10:57:20Z by `python -m skillkat telemetry bench --tag regress-asm-20260925`. Times in m:ss; buckets are exclusive (worker > evaluator > interruption > latency > other) and sum to the wall. Accuracy is the tolerance-normalized score (0-100). Estimated tokens are generated characters / 4, a lower bound. Off-brief reads are Read/Grep calls under `src/skillkat`, `tests/`, `truth/`, another part, or another order.

Regression (scorecard PASS and no failed gate): build123d PASS (1/1).

| case | backend | wall | verdict | gates | rounds | turns | worker | evaluator | latency | interruption | other | engine share | model | accuracy | est tokens | off-brief reads |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| None | build123d | 64:35 | PASS | 10/10 | - | - | - | - | - | - | - | - | - | - | - | - |

| cell | attempts | PASS | completion | median wall | p95 wall | median worker | median evaluator | median latency | accuracy | est tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| None / build123d | 1 | 1 | 100% | 64:35 | 64:35 | 0:00 | 0:00 | 0:00 | - | - |

All cells: 1/1 PASS (100%), median wall 64:35, p95 64:35.

## Against the baseline `regress-20260924`

Per cell: median wall and its delta (this bench minus the baseline), completion, gates, mean accuracy and median estimated tokens. A cell's wall here includes its case's draft wall: the draft ran once and every backend reused it.

| cell | median wall | delta | completion | gates | accuracy | est tokens | baseline wall | baseline accuracy | baseline tokens |
|---|---|---|---|---|---|---|---|---|
| None / build123d | 64:35 | - | 1/1 | 10/10 | - | - | - | - | - |
| bearing-housing / build123d | - | - | - | - | - | - | 19:00 | 99.7 | 9343 |
| bearing-housing / cadquery | - | - | - | - | - | - | 19:57 | 99.6 | 12228 |
| bearing-housing / freecad | - | - | - | - | - | - | 19:32 | 99.7 | 10386 |
| enclosure-base / build123d | - | - | - | - | - | - | 14:05 | 100.0 | 3502 |
| enclosure-base / cadquery | - | - | - | - | - | - | 13:50 | 100.0 | 3148 |
| enclosure-base / freecad | - | - | - | - | - | - | 18:06 | 100.0 | 8926 |

Median wall 64:35 (baseline 18:33, delta +46:02).

Evaluator stages (mean s per run, by backend):

| stage | build123d |
|---|---|
| domains | 4 (n=1) |
| edit | 57 (n=3) |
| export | 0 (n=3) |
| finalize | 12 (n=3) |
| gates | 0 (n=7) |
| inspect | 10 (n=3) |
| kinematics | 314 (n=1) |
| simulate | 0 (n=1) |
| verify | 42 (n=4) |

Worker turns (median worker s / engine share, by role and backend):

| role | build123d |
|---|---|
| asm-draft | 604 / 0.00 (n=1) |
| assemble | 441 / 0.50 (n=1) |
| draft | 434 / 0.00 (n=3) |
| model | 456 / 0.04 (n=3) |
