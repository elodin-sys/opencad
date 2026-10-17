---
name: kcl-examples
disable-model-invocation: true
description: Indexed library of 126 production KCL 2 sample projects from the zoo.dev Aquarium with their .kcl sources extracted. Use when a worked example of a KCL feature is needed (sweep, loft, helix, gears, holes, patterns, sketch-on-face, multi-file assemblies) or when a reference model should be adapted into a new part.
---
# kcl-examples

1. Know the feature: open `by-feature.md` (0.9k tok), pick a slug. Browsing by name or category: `index.md` (2.7k), one line per sample with file count, notable features, categories.
2. Read `samples/<slug>/main.kcl`. Multi-file samples import siblings from the same directory; shared dimensions sit in `parameters.kcl`.
3. Lift contiguous idioms, keeping the constraint style. All samples use KCL 2 sketch blocks and render on zoo.dev, but five declare `kclVersion = 1.0` or none (flagged `!kcl…` in `index.md`): write `kclVersion = 2.0` in anything adapted from them. Samples using `gear::` or `view::` carry `experimentalFeatures = allow`.

Sample page with screenshot and description: `zoo.dev/aquarium/<slug>`. Language rules and signatures: the kcl-docs skill.
