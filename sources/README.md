# zoo.dev source mirror

Fetched at `2026-09-13T22:01:24Z` by `scripts/fetch_zoo_sources.py`.

Native Markdown via `Accept: text/markdown` for `/docs` (except the KCL Book) and `/aquarium`.
Raw HTML plus pandoc GFM for `/research` and `/docs/kcl-book`.

## Counts

- Docs Markdown pages: 835
- KCL Book chapters (converted): 24
- KCL Book raw HTML: 24
- Aquarium pages: 128
- Aquarium screenshots: 127
- Research pages: 6
- Research raw HTML: 6
- Research figures: 36
- Failed page fetches: 3
- Failed asset fetches: 0

Full per-URL inventory: [manifest.json](manifest.json).

## Known gaps

These are stale or unpublished zoo.dev URLs (sitemap or in-page links that 404).
Hidden API pages that omit Markdown are stored via HTML fallback.

- https://zoo.dev/docs/developer-tools/api/modeling failed (http 404)
- https://zoo.dev/docs/developer-tools/api/modeling/open-a-websocket-which-accepts-modeling-commands failed (http 404)
- https://zoo.dev/docs/kcl-std/tangentialArc failed (http 404)
- https://zoo.dev/docs/developer-tools/api -> /docs/developer-tools/api/modeling (expected zoo-docs/developer-tools/api/modeling/index.md)
- https://zoo.dev/docs/developer-tools/api/modeling/opens-a-websocket-to-a-zoo-kittycad-engine-instance -> /docs/developer-tools/api/modeling (expected zoo-docs/developer-tools/api/modeling/index.md)
- https://zoo.dev/docs/developer-tools/tutorials/beginner-onboarding-js -> /docs/developer-tools/api/modeling/open-a-websocket-which-accepts-modeling-commands (expected zoo-docs/developer-tools/api/modeling/open-a-websocket-which-accepts-modeling-commands.md)
- https://zoo.dev/docs/kcl-book/print.html -> https://zoo.dev/docs/kcl-std/tangentialArc (expected zoo-docs/kcl-std/tangentialArc.md)
- https://zoo.dev/docs/kcl-book/sketch2d_curves.html -> https://zoo.dev/docs/kcl-std/tangentialArc (expected zoo-docs/kcl-std/tangentialArc.md)
- https://zoo.dev/docs/zoo-design-studio/features/system-requirements/zoo-stream -> /docs/developer-tools/api/modeling (expected zoo-docs/developer-tools/api/modeling/index.md)
- https://zoo.dev/docs/zoo-design-studio/features/system-requirements/zoo-stream -> /docs/developer-tools/api/modeling/open-a-websocket-which-accepts-modeling-commands (expected zoo-docs/developer-tools/api/modeling/open-a-websocket-which-accepts-modeling-commands.md)
