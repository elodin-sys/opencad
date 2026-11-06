# prism sources

The prism backend runs the part in Prism's managed python-env (`~/Library/Application Support/prism/python-env/.venv`,
`OPENCAD_PRISM_PYTHON` relocates it): build123d 0.11.x, `navier_cad` 0.1 (Prism's vetted geometry vocabulary), `bd_warehouse`
0.2 (ISO/DIN hardware, millimetres), OCP 7.9. Nothing is fetched into `sources/prism/`; the environment is Prism's own.

- build123d documentation and examples: `sources/build123d/` after `scripts/fetch_sources.py --backend build123d`
  (written for 0.12; `SKILL.md` lists the 0.11 differences).
- `navier_cad` signatures: inlined in `SKILL.md` (`inspect.signature` of the installed package). The package sources live in
  the python-env's `site-packages/navier_cad/`; the worker does not read them.
- `bd_warehouse`: https://bd-warehouse.readthedocs.io (`fastener`, `thread`, `bearing`, `gear`, `pipe`, `flange`, `open_builds`).
