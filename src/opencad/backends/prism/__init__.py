"""Prism backend: build123d 0.11 + navier_cad run in Prism's managed python-env (a separate interpreter, never imported here)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any

from opencad.backends.local import LocalPythonEngine
from opencad.backends.prism.lang import PrismLanguage
from opencad.backends.registry import register

DEFAULT_PRISM_PYTHON = Path.home() / "Library" / "Application Support" / "prism" / "python-env" / ".venv" / "bin" / "python"
RUNNER = Path(__file__).resolve().parent / "runner.py"
_PROBE = (
    "import build123d, navier_cad, OCP, sys, importlib.metadata as m; "
    "print(getattr(build123d, '__version__', 'unknown'), m.version('navier_cad'), sys.version.split()[0])"
)


def prism_python() -> str:
    return os.environ.get("OPENCAD_PRISM_PYTHON") or str(DEFAULT_PRISM_PYTHON)


class PrismEngine(LocalPythonEngine):
    """`LocalPythonEngine` on Prism's interpreter: the same slot, watchdog, ledger and canonical STEP, a self-contained runner."""

    _versions: dict[str, str] = {}

    def __init__(self):
        super().__init__("prism", "opencad.backends.prism.runner", "__version__")

    def _argv(
        self,
        entry: Path,
        *,
        analyze: Path | None,
        export_step: Path | None,
        export_stl: Path | None,
        out_json: Path,
    ) -> list[str]:
        argv = [prism_python(), "-I", str(RUNNER), "--entry", str(entry)]
        if analyze:
            argv += ["--analyze", str(analyze)]
        if export_step:
            argv += ["--export-step", str(export_step)]
        if export_stl:
            argv += ["--export-stl", str(export_stl)]
        return argv + ["--out", str(out_json)]

    def preflight(self) -> dict[str, Any]:
        exe = prism_python()
        if not Path(exe).exists():
            return {
                "ok": False,
                "version": None,
                "error": f"Prism python-env interpreter not found at {exe} (OPENCAD_PRISM_PYTHON relocates it)",
                "class": "unknown",
            }
        try:
            r = subprocess.run([exe, "-I", "-c", _PROBE], capture_output=True, text=True, timeout=60)
        except Exception as e:
            return {"ok": False, "version": None, "error": str(e), "class": "unknown"}
        if r.returncode != 0:
            return {"ok": False, "version": None, "error": (r.stderr or r.stdout)[:400], "class": "program"}
        b3d, navier, py = (r.stdout.split() + ["?", "?", "?"])[:3]
        version = f"build123d {b3d} navier_cad {navier} (prism python-env, python {py})"
        self._versions[exe] = version
        return {"ok": True, "version": version, "error": None, "python": exe}

    def version(self) -> str:
        exe = prism_python()
        if exe not in self._versions:
            pf = self.preflight()
            self._versions[exe] = pf.get("version") or "unknown"
        return self._versions[exe]

    def hints(self) -> str:
        return (
            super().hints()
            + " Prism's env is build123d 0.11: `Compound([...])` takes a list, `a & b` is None when disjoint, and the part is in millimetres."
        )


class PrismBackend:
    id = "prism"
    language = PrismLanguage()
    engine = PrismEngine()
    independent_of_evaluator = False  # same OCP 7.9.3.1 kernel as the evaluator's OpenCascade, in another install


register(PrismBackend())
