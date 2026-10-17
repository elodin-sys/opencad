"""FreeCAD backend: freecadcmd subprocess, PartDesign::Body deliverable."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from opencad.backends.base import EngineError, FailureClass
from opencad.backends.freecad.lang import FreeCADLanguage
from opencad.backends.local import (
    canonicalize_step,
    classify_text,
    cost,
    finish_build,
    ledger,
    max_slots,
    raise_run,
    reset_ledger,
    run_script,
    stl_to_glb,
)
from opencad.backends.registry import register

DEFAULT_FREECADCMD = "/Applications/FreeCAD.app/Contents/Resources/bin/freecadcmd"


def _no_cache() -> bool:
    return os.environ.get("OPENCAD_NO_CACHE", "") in ("1", "true", "yes")


def freecadcmd() -> str:
    return os.environ.get("OPENCAD_FREECADCMD") or DEFAULT_FREECADCMD


class FreeCADEngine:
    id = "freecad"
    turn_factor = 1.5  # every worker critic run is a freecadcmd export: turns need ~1.5x the in-process backends' wall time
    _versions: dict[str, str] = {}

    def _runner(self) -> Path:
        return Path(__file__).resolve().parent / "runner.py"

    def _env(
        self,
        entry: Path,
        *,
        analyze: Path | None = None,
        export_step: Path | None = None,
        export_stl: Path | None = None,
        export_fcstd: Path | None = None,
        out: Path | None = None,
    ) -> dict[str, str]:
        env = {"OPENCAD_FREECADCMD": freecadcmd(), "OPENCAD_FC_ENTRY": str(Path(entry).resolve())}
        if analyze:
            env["OPENCAD_FC_ANALYZE"] = str(Path(analyze).resolve())
        if export_step:
            env["OPENCAD_FC_STEP"] = str(Path(export_step).resolve())
        if export_stl:
            env["OPENCAD_FC_STL"] = str(Path(export_stl).resolve())
        if export_fcstd:
            env["OPENCAD_FC_FCSTD"] = str(Path(export_fcstd).resolve())
        if out:
            env["OPENCAD_FC_OUT"] = str(Path(out).resolve())
        return env

    def _run(self, entry: Path, **paths: Path | None) -> dict[str, Any]:
        out = Path(tempfile.mkdtemp(prefix="opencad-fc-")) / "out.json"
        env = self._env(entry, out=out, **{k: v for k, v in paths.items() if v is not None})
        runner = self._runner()
        argv = [freecadcmd(), "-c", f"exec(open({str(runner)!r}).read())"]
        row = run_script(argv, backend_id=self.id, cwd=entry.parent, extra_env=env, payload=out)
        payload: dict[str, Any] = {}
        if out.exists():
            try:
                payload = json.loads(out.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
        shutil.rmtree(out.parent, ignore_errors=True)
        if payload and not payload.get("ok", True):
            row = {
                **row,
                "ok": False,
                "class": payload.get("class") or row.get("class"),
                "stderr": payload.get("error") or payload.get("traceback") or row.get("stderr"),
            }
        if not row["ok"]:
            raise_run(row, "freecadcmd runner failed")
        return {**row, "payload": payload}

    def preflight(self) -> dict[str, Any]:
        exe = freecadcmd()
        if not Path(exe).exists():
            return {"ok": False, "version": None, "error": f"freecadcmd not found at {exe}", "class": "unknown"}
        row = run_script(
            [exe, "-c", "import FreeCAD, PartDesign; print(FreeCAD.Version())"],
            backend_id=self.id,
            cwd=Path.cwd(),
            timeout=60,
        )
        if not row["ok"]:
            return {"ok": False, "version": None, "error": (row.get("stderr") or "")[:400], "class": row.get("class")}
        return {"ok": True, "version": (row.get("stdout") or "").strip() or "FreeCAD", "error": None}

    def analyze(self, entry: Path, *, density_kg_m3: float | None = None, timeout: float = 600) -> dict[str, Any]:
        return self.build(entry, density_kg_m3=density_kg_m3, timeout=timeout)["analyze"]

    def build(self, entry: Path, *, analyze: bool = True, step: Path | None = None, stl: Path | None = None, fcstd: Path | None = None,
              density_kg_m3: float | None = None, deterministic: bool = True, timeout: float = 600, lock: bool = True) -> dict[str, Any]:
        """Analyze, STEP, STL and FCStd from one freecadcmd process (one recompute instead of one per output)."""
        for p in (step, stl, fcstd):
            if p:
                Path(p).parent.mkdir(parents=True, exist_ok=True)
        dest = Path(tempfile.mkdtemp(prefix="opencad-fca-")) / "analyze.json"
        try:
            row = self._run(Path(entry), analyze=dest, export_step=step, export_stl=stl, export_fcstd=fcstd)
            data = row["payload"].get("analyze") or (json.loads(dest.read_text(encoding="utf-8")) if dest.exists() else {})
        finally:
            shutil.rmtree(dest.parent, ignore_errors=True)
        out = finish_build(Path(entry), row, data if analyze else None, step, stl, fcstd, density_kg_m3=density_kg_m3, deterministic=deterministic)
        if out["analyze"] is not None:
            out["analyze"]["feature_tree"] = row["payload"].get("feature_tree")
        if deterministic and out["step"] is not None:
            cache = self._step_cache(Path(entry))
            if cache.exists() and not _no_cache():
                shutil.copy2(cache, out["step"])
                canonicalize_step(out["step"], Path(entry).stem)
            else:
                self._store(cache, out["step"], out["fcstd"])
        return out

    @staticmethod
    def _step_cache(entry: Path) -> Path:
        """The deterministic STEP of a source tree: freecadcmd's STEP bytes differ run to run, so the first export is the one every
        later deterministic export (and the determinism re-export) returns."""
        h = hashlib.sha256(Path(entry).name.encode())  # two entries in one directory are two parts
        for p in sorted(Path(entry).parent.rglob("*.py")):
            h.update(p.read_bytes())
        return Path(os.environ.get("OPENCAD_ENGINE_CACHE") or (Path.home() / ".cache" / "opencad" / "engine")) / "freecad-step" / f"{h.hexdigest()}.step"

    @staticmethod
    def _store(cache: Path, step: Path, fcstd: Path | None) -> None:
        cache.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(step, cache)
        plc = step.parent / "placements.json"
        if plc.exists():
            shutil.copy2(plc, cache.with_suffix(".placements.json"))
        if fcstd is not None and fcstd.exists():
            shutil.copy2(fcstd, cache.with_name(cache.stem + ".FCStd"))

    def export(
        self,
        entry: Path,
        out_dir: Path,
        fmt: str,
        *,
        deterministic: bool = True,
        timeout: float = 600,
        lock: bool = True,
    ) -> list[Path]:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        fmt = fmt.lower()
        from opencad.backends.placements import sidecar

        if fmt == "glb":
            stl = out_dir / f"{entry.stem}.stl"
            row = self._run(entry, export_stl=stl)
            sidecar(out_dir, row.get("payload") or {})
            glb = out_dir / f"{entry.stem}.glb"
            stl_to_glb(stl, glb)
            return [glb]
        if fmt == "stl":
            dest = out_dir / f"{entry.stem}.stl"
            row = self._run(entry, export_stl=dest)
            sidecar(out_dir, row.get("payload") or {})
            return [dest]
        if fmt in ("fcstd", "fcstd"):
            dest = out_dir / f"{entry.parent.name}.FCStd"
            self._run(entry, export_fcstd=dest)
            return [dest]
        dest = out_dir / f"{entry.stem}.step"
        fcstd = out_dir / f"{entry.parent.name}.FCStd"
        cache = None
        if deterministic:
            cache = self._step_cache(entry)
            plc_cache = cache.with_suffix(".placements.json")
            if cache.exists() and not _no_cache():
                shutil.copy2(cache, dest)
                canonicalize_step(dest, entry.stem)
                if plc_cache.exists():
                    shutil.copy2(plc_cache, out_dir / "placements.json")
                fcstd_cache = cache.with_name(cache.stem + ".FCStd")
                if fcstd_cache.exists():
                    shutil.copy2(fcstd_cache, fcstd)
                elif not fcstd.exists():
                    self._run(entry, export_fcstd=fcstd)
                return [dest]
        row = self._run(entry, export_step=dest, export_fcstd=fcstd)
        sidecar(out_dir, row.get("payload") or {})
        if not dest.exists():
            raise EngineError(f"freecadcmd wrote no STEP at {dest}", kind="unknown")
        if deterministic:
            canonicalize_step(dest, entry.stem)
            if cache is not None:
                self._store(cache, dest, fcstd)
        return [dest]

    def classify(self, text_or_exc: Any, *, code: int | None = None) -> FailureClass:
        if isinstance(text_or_exc, BaseException):
            kind = getattr(text_or_exc, "kind", None)
            if kind:
                return kind
            return classify_text(str(text_or_exc), code=code)
        return classify_text(str(text_or_exc), code=code)

    def kernel_patterns(self) -> list[Any]:
        return [re.compile(p, re.I) for p in ("Recompute failed", "StdFail_NotDone", "BRep_API", "isValid")]

    def max_concurrency(self) -> int:
        return max_slots()

    def ledger_wrapper(self, argv: list[str], ledger_path: Path | None) -> int:
        if not argv:
            print("usage: opencad engine -- analyze <entry> | export <fmt> <entry> <out_dir>", file=sys.stderr)
            return 2
        cmd, *rest = argv
        try:
            if cmd == "analyze" and rest:
                self.analyze(Path(rest[0]))
            elif cmd == "export" and len(rest) >= 3:
                self.export(Path(rest[1]), Path(rest[2]), rest[0])
            else:
                row = run_script(argv, backend_id=self.id, cwd=Path.cwd())
                raise_run(row, "engine")
        except EngineError as e:
            print(e, file=sys.stderr)
            return 1
        if ledger_path:
            ledger_path.parent.mkdir(parents=True, exist_ok=True)
            with ledger_path.open("a", encoding="utf-8") as f:
                for row in ledger(self.id):
                    f.write(json.dumps(row, default=str) + "\n")
        return 0

    def cost(self, ledger_rows: list[dict[str, Any]]) -> dict[str, Any]:
        return cost(ledger_rows)

    def hints(self) -> str:
        return (
            "PartDesign: fully constrain sketches; find faces by normal and centre, never FaceN; "
            "one Pocket/Hole per family; Refine=True on the last feature; recompute must leave every feature valid."
        )

    def version(self) -> str:
        """Remembered per freecadcmd path and mtime: every stage stamp and critic cache key asks, and freecadcmd takes seconds to start."""
        exe = Path(freecadcmd())
        if not exe.exists():
            return self.preflight().get("version") or "unknown"
        key = f"{exe}:{exe.stat().st_mtime_ns}"
        if key in self._versions:
            return self._versions[key]
        cache = Path.home() / ".cache" / "opencad" / "freecad-version.json"
        try:
            known = json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            known = {}
        v = known.get(key)
        if not v:
            v = self.preflight().get("version") or "unknown"
            if v != "unknown":
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({**known, key: v}), encoding="utf-8")
        self._versions[key] = v
        return v

    def reset_ledger(self) -> list[dict[str, Any]]:
        return reset_ledger(self.id)

    def engine_calls(self) -> int:
        return len(ledger(self.id))


class FreeCADBackend:
    id = "freecad"
    language = FreeCADLanguage()
    engine = FreeCADEngine()
    independent_of_evaluator = False


register(FreeCADBackend())
