#!/usr/bin/env bash
# Create the pinned Python 3.12 environment for the opencad pipeline (no sudo).
set -euo pipefail
cd "$(dirname "$0")/.."

command -v uv >/dev/null || { echo "install uv first: https://github.com/astral-sh/uv#installation" >&2; exit 1; }
command -v zoo >/dev/null || echo "warning: zoo CLI not on PATH (https://zoo.dev/docs/developer-tools/cli)" >&2
command -v codex >/dev/null || echo "warning: codex CLI not on PATH; /create-cad needs it" >&2

uv python install 3.12 >/dev/null
uv sync --locked 2>/dev/null || uv sync
.venv/bin/python -c "import OCP, trimesh, pydantic; print('opencad env ok:', OCP.__version__ if hasattr(OCP, '__version__') else 'OCP', 'trimesh', trimesh.__version__)"
echo "activate with: source .venv/bin/activate"
