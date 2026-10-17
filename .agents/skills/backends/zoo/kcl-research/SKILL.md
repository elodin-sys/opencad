---
name: kcl-research
disable-model-invocation: true
description: Digest of Zoo's research articles covering the GPU B-rep engine (NURBS, sweeps, patterns, surface-surface intersection), why KCL is code, CAD file-format tradeoffs (STEP versus STL, OBJ, PLY, glTF), Zookeeper's agent loop, and hardware workflow automation. Use when choosing an export or interchange format, explaining engine behaviour such as boolean or tolerance failures, or grounding a design or tooling decision in Zoo's published rationale.
---
# kcl-research

Read `digest.md` (1.4k tok). Each section names its article slug; the full text is at `zoo.dev/research/<slug>`.

Use it for the "why": engine constraints that shape robust KCL (line-and-arc sweep paths, instanced patterns, approximate intersections), which file format to emit for which consumer, and how Zookeeper verifies work (execute, multi-view snapshot, measure) so an external agent can do the same.
