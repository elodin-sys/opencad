---
name: zoo-tooling
disable-model-invocation: true
description: Zoo CLI (zoo kcl format, lint, export, snapshot, analyze), the Zoo MCP server's 46 tools (execute_kcl, modeling sessions, snapshot, physical properties, docs and sample lookup), and the REST API endpoint index. Use when running, checking, rendering, measuring, exporting, or converting KCL or CAD files from a terminal or an agent, when configuring the Zoo MCP server for Codex, Claude, or Cursor, or when calling api.zoo.dev directly.
---
# zoo-tooling

## Verification loop
1. Format: `format_kcl` or `zoo kcl format --write`.
2. Lint: `lint_and_fix_kcl` or `zoo kcl lint`.
3. Execute: `execute_kcl` in a session (artifact graph returned); `mock_execute_kcl` for a cheap pass without geometry.
4. Look: `snapshot(session_id, camera_view = [...])` with front, top, right, isometric, or `zoo kcl snapshot --angle four-ways`.
5. Measure: `calculate_kcl_physical_properties` or `zoo kcl analyze --format json`. Set the real density first: the CLI defaults to 1 kg/m3 and the MCP tool to 1000 kg/m3, so an unset mass is not the part's mass.
6. Export: `export_kcl` or `zoo kcl export -t step --deterministic <input> <output-dir>`; STEP for CAD/CAM, STL only for slicing.

Auth is `ZOO_API_TOKEN`. Hosted operations bill as API usage: bound retries, and `stop_modeling_session` when done.

The CLI skips `.kcl` files that a repository `.gitignore` pattern matches directly and reports `i/o: No such file <name> found`. In this repo that is any file exactly three levels under `results/` (`results/_spikes/<name>/main.kcl`), so keep scratch KCL one directory deeper (`results/_spikes/<name>/<case>/main.kcl`).

## Files
- `cli.md` (1.7k tok): every `zoo` command, flags for `zoo kcl *`, environment variables.
- `mcp.md` (1.9k): install, client config, session rules, all tools grouped with signatures.
- `api.md` (3.0k): REST endpoints by section, auth, async operations, hidden endpoints marked.
