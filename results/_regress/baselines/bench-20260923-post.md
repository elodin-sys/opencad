# Bench `bench-20260923-post`

Generated 2026-09-23T14:48:44Z by `python -m skillkat telemetry bench --tag bench-20260923-post`. Times in m:ss; buckets are exclusive (worker > evaluator > interruption > latency > other) and sum to the wall. Accuracy is the tolerance-normalized score (0-100). Estimated tokens are generated characters / 4, a lower bound.

Baseline model: claude-opus-5-5, 1M context, max effort.

| case | backend | wall | verdict | gates | rounds | turns | worker | evaluator | latency | interruption | other | engine share | model | accuracy | est tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| bearing-housing | build123d | 41:56 | PASS | 11/11 | 2 | 4 | 35:34 | 2:01 | 4:00 | 0:00 | 0:22 | 0.01 | claude-opus-5-5, 1M context, max effort | 90.7 | 68242 |
| bearing-housing | build123d | 20:38 | PASS | 11/11 | 0 | 2 | 17:36 | 0:41 | 0:41 | 0:00 | 1:40 | 0.016 | claude-opus-5-5, 1M context, max effort | 99.7 | 32326 |
| bearing-housing | cadquery | 29:20 | PASS | 11/11 | 1 | 3 | 25:36 | 1:22 | 2:01 | 0:00 | 0:21 | 0.015 | claude-opus-5-5, 1M context, max effort | 99.7 | 51984 |
| bearing-housing | cadquery | 47:37 | PASS | 11/11 | 2 | 4 | 42:49 | 1:57 | 2:30 | 0:00 | 0:22 | 0.013 | claude-opus-5-5, 1M context, max effort | 99.7 | 79199 |
| bearing-housing | freecad | 22:15 | PASS | 11/11 | 0 | 2 | 19:57 | 0:40 | 1:36 | 0:00 | 0:02 | 0.006 | claude-opus-5-5, 1M context, max effort | 99.7 | 34700 |
| bearing-housing | freecad | 19:40 | PASS | 11/11 | 0 | 2 | 18:00 | 0:40 | 0:58 | 0:00 | 0:02 | 0.005 | claude-opus-5-5, 1M context, max effort | 99.7 | 36728 |
| enclosure-base | build123d | 16:09 | PASS | 11/11 | 0 | 2 | 14:00 | 0:57 | 0:50 | 0:00 | 0:22 | 0.033 | claude-opus-5-5, 1M context, max effort | 100.0 | 30729 |
| enclosure-base | build123d | 18:16 | PASS | 11/11 | 0 | 2 | 16:13 | 0:44 | 0:59 | 0:00 | 0:20 | 0.014 | claude-opus-5-5, 1M context, max effort | 100.0 | 33114 |
| enclosure-base | cadquery | 18:55 | PASS | 11/11 | 0 | 2 | 16:42 | 0:44 | 1:10 | 0:00 | 0:19 | 0.01 | claude-opus-5-5, 1M context, max effort | 100.0 | 34562 |
| enclosure-base | cadquery | 21:14 | PASS | 11/11 | 0 | 2 | 19:16 | 0:43 | 0:56 | 0:00 | 0:19 | 0.017 | claude-opus-5-5, 1M context, max effort | 100.0 | 37609 |
| enclosure-base | freecad | 21:54 | PASS | 11/11 | 0 | 2 | 19:43 | 1:04 | 1:04 | 0:00 | 0:03 | 0.006 | claude-opus-5-5, 1M context, max effort | 100.0 | 34644 |
| enclosure-base | freecad | 25:29 | PASS | 11/11 | 0 | 2 | 22:54 | 1:03 | 1:29 | 0:00 | 0:03 | 0.006 | claude-opus-5-5, 1M context, max effort | 100.0 | 41782 |

| cell | attempts | PASS | completion | median wall | p95 wall | median worker | median evaluator | median latency | accuracy | est tokens |
|---|---|---|---|---|---|---|---|---|---|---|
| bearing-housing / build123d | 2 | 2 | 100% | 31:17 | 41:56 | 26:35 | 1:21 | 2:20 | 95.2 | 50284 |
| bearing-housing / cadquery | 2 | 2 | 100% | 38:28 | 47:37 | 34:12 | 1:40 | 2:16 | 99.7 | 65592 |
| bearing-housing / freecad | 2 | 2 | 100% | 20:58 | 22:15 | 18:58 | 0:40 | 1:17 | 99.7 | 35714 |
| enclosure-base / build123d | 2 | 2 | 100% | 17:12 | 18:16 | 15:06 | 0:50 | 0:54 | 100.0 | 31922 |
| enclosure-base / cadquery | 2 | 2 | 100% | 20:04 | 21:14 | 17:59 | 0:44 | 1:03 | 100.0 | 36086 |
| enclosure-base / freecad | 2 | 2 | 100% | 23:42 | 25:29 | 21:18 | 1:04 | 1:16 | 100.0 | 38213 |

All cells: 12/12 PASS (100%), median wall 21:34, p95 41:56, mean accuracy 99.1, median est tokens 35714.

Evaluator stages (mean s per run, by backend):

| stage | build123d | cadquery | freecad |
|---|---|---|---|
| briefs | 0 (n=8) | 0 (n=12) | - |
| draft-check | 0 (n=5) | 0 (n=4) | 0 (n=4) |
| edit | 20 (n=6) | 17 (n=7) | 13 (n=4) |
| export | 2 (n=6) | 2 (n=7) | 0 (n=4) |
| finalize | 10 (n=4) | 10 (n=4) | 14 (n=4) |
| gates | 0 (n=10) | 0 (n=11) | 0 (n=8) |
| inspect | 5 (n=6) | 5 (n=7) | 18 (n=4) |
| parity | 0 (n=5) | 0 (n=4) | 0 (n=4) |
| score | 6 (n=4) | 6 (n=4) | 6 (n=4) |
| snapshots | 8 (n=2) | 8 (n=3) | - |
| verify | 5 (n=6) | 5 (n=7) | 1 (n=4) |

Worker turns (median worker s / engine share, by role and backend):

| role | build123d | cadquery | freecad |
|---|---|---|---|
| correction | 529 / 0.01 (n=2) | 583 / 0.02 (n=3) | - |
| draft | 439 / 0.00 (n=4) | 524 / 0.00 (n=4) | 423 / 0.00 (n=4) |
| model | 536 / 0.03 (n=4) | 673 / 0.02 (n=4) | 764 / 0.01 (n=4) |
