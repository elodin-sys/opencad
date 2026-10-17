"""Shared local subprocess engine: sandbox, ledger, STEP header, STL/GLB."""

from __future__ import annotations

import fcntl
import importlib.metadata
import json
import os
import re
import resource
import shutil
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from opencad import resources
from opencad.backends.base import MEMORY_PHRASE, EngineError, FailureClass, ProgramError

LEDGERS: dict[str, list[dict[str, Any]]] = {}

FILE_NAME_RE = re.compile(r"FILE_NAME\s*\((.*?)\)\s*;", re.S)
# a Part 21 string literal, or a real (digits, point, optional exponent) that is not part of an id, a keyword or an enum
STEP_TOKEN_RE = re.compile(r"'(?:[^']|'')*'|(?<![\w.#])([+-]?\d+\.\d*(?:E[+-]?\d+)?)(?![\w.])")
STEP_ZERO_SNAP = 1e-9  # Precision::Confusion()/100: a smaller real is kernel rounding noise, not geometry
KERNEL_PHRASES = (
    "stdfail_notdone",
    "standard_constructionerror",
    "standard_failure",
    "brep_api: command not done",
    "command not done",
    "recompute failed",
    "base.freecaderror",
    "isvalid() == false",
    "isvalid() is false",
)
PROGRAM_PHRASES = (
    "assertionerror",
    "assert ",
    "assertion failed",
    "nameerror",
    "syntaxerror",
    "indentationerror",
    "typeerror",
    "attributeerror",
    "keyerror",
    "import error",
    "modulenotfounderror",
    "not defined",
    "infeasible",
    "refused",
)
RESOURCE_PHRASES = ("cannot allocate memory", "memoryerror", "killed", "signal 9")

DEFAULT_AS_BYTES = 4 * 1024 * 1024 * 1024


def ledger(backend_id: str) -> list[dict[str, Any]]:
    return LEDGERS.setdefault(backend_id, [])


def reset_ledger(backend_id: str) -> list[dict[str, Any]]:
    rows = list(ledger(backend_id))
    ledger(backend_id).clear()
    return rows


def classify_text(text: str, *, code: int | None = None) -> FailureClass:
    low = (text or "").lower()
    if MEMORY_PHRASE in low:
        return "memory"
    if code == 124:
        return "timeout"
    if code in (-9, 137):
        return "resource"
    if any(p in low for p in KERNEL_PHRASES):
        return "kernel"
    if any(p in low for p in RESOURCE_PHRASES):
        return "resource"
    if any(p in low for p in PROGRAM_PHRASES):
        return "program"
    if "not a valid" in low or "invalid" in low and "valueerror" in low:
        return "kernel"
    return "unknown" if (code or 0) != 0 else "ok"


def looks_like_guard(text: str) -> bool:
    low = (text or "").lower()
    return "assert" in low or "infeasible" in low or "refused" in low


def scrub_env(home: Path) -> dict[str, str]:
    keep = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(home),
        "TMPDIR": str(home / "tmp"),
        "TMP": str(home / "tmp"),
        "TEMP": str(home / "tmp"),
        "LANG": os.environ.get("LANG", "C"),
        "LC_ALL": os.environ.get("LC_ALL", "C"),
        "TZ": os.environ.get("TZ", "UTC"),
        "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV", ""),
        "OPENCAD_FREECADCMD": os.environ.get("OPENCAD_FREECADCMD", ""),
    }
    (home / "tmp").mkdir(parents=True, exist_ok=True)
    return {k: v for k, v in keep.items() if v}


def _limit_child(as_bytes: int, cpu_s: int) -> None:
    try:
        resource.setrlimit(resource.RLIMIT_AS, (as_bytes, as_bytes))
    except (ValueError, OSError):
        pass
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s + 1))
    except (ValueError, OSError):
        pass


def slot_base(backend_id: str) -> Path:
    override = os.environ.get("OPENCAD_ENGINE_LOCK")
    if override:
        return Path(override)
    return Path.home() / ".cache" / "opencad" / f"{backend_id}.lock"


def max_slots() -> int:
    """Concurrent engine processes per backend, machine-wide: cores - 1, capped by how many fit in memory at their budget."""
    n = os.environ.get("OPENCAD_ENGINE_SLOTS")
    if n:
        return max(1, int(n))
    return max(1, min((os.cpu_count() or 2) - 1, resources.memory_slots()))


@contextmanager
def engine_slot(backend_id: str, slots: int | None = None) -> Iterator[None]:
    base = slot_base(backend_id)
    base.parent.mkdir(parents=True, exist_ok=True)
    n = max(1, slots or max_slots())
    handles = [open(base.with_name(f"{base.name}.slot{i}"), "a+") for i in range(n)]
    got = None
    try:
        while got is None:
            for fh in handles:
                try:
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    got = fh
                    break
                except BlockingIOError:
                    continue
            if got is None:
                time.sleep(0.1)
        yield
    finally:
        if got is not None:
            fcntl.flock(got.fileno(), fcntl.LOCK_UN)
        for fh in handles:
            fh.close()


def run_script(
    argv: list[str],
    *,
    backend_id: str,
    cwd: Path,
    timeout: float = 600,
    as_bytes: int = DEFAULT_AS_BYTES,
    extra_env: dict[str, str] | None = None,
    lock: bool = True,
    payload: Path | None = None,
) -> dict[str, Any]:
    """Run argv in a scrubbed env with rlimits, inside an engine slot, once its memory budget fits, under an RSS watchdog. Returns
    {ok, code, stdout, stderr, seconds, class, peak_rss, oom_killed}. Every local call takes a slot: `lock` only matters to Zoo's
    exclusive lock. `payload` is the runner's JSON sidecar: its `timings` go on the ledger row, and wall minus the runner's own
    `main_s` is the process startup."""
    home = Path(tempfile.mkdtemp(prefix=f"opencad-{backend_id}-"))
    env = scrub_env(home)
    if extra_env:
        env.update(extra_env)
    budget = resources.runner_budget()
    dog: resources.Watchdog | None = None
    wait_s = 0.0
    refused = False
    t0 = time.time()
    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    try:
        with engine_slot(backend_id):
            try:
                wait_s = resources.wait_for_memory(budget, label=f"{backend_id} engine call")
            except resources.MemoryWait as e:
                refused = True
                code, out, err = -1, "", str(e)
            else:
                p = subprocess.Popen(
                    argv,
                    cwd=str(cwd),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    # RLIMIT_CPU counts every thread: a parallel boolean spends the wall timeout's CPU seconds in a fraction of it
                    preexec_fn=lambda: _limit_child(as_bytes, max(1, int(timeout * (os.cpu_count() or 1)))),
                )
                dog = resources.Watchdog(p.pid, budget).start()
                try:
                    out, err = p.communicate(timeout=timeout)
                    code = p.returncode
                except subprocess.TimeoutExpired:
                    p.kill()
                    out, err = p.communicate()
                    code, err = 124, (err or "") + f"\ntimed out after {timeout}s"
                finally:
                    dog.stop()
    finally:
        shutil.rmtree(home, ignore_errors=True)
    seconds = time.time() - t0
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)
    peak = (dog.peak if dog else 0) or max(0, int(usage_after.ru_maxrss - usage_before.ru_maxrss))
    oom = bool(dog and dog.killed)
    if oom:
        assert dog is not None
        code, err = -9, (err or "") + f"\nkilled: RSS {resources.gb(dog.killed_rss)} {MEMORY_PHRASE} {resources.gb(budget)} (OPENCAD_ENGINE_MEM_GB)"
    text = f"{err or ''}\n{out or ''}"
    kind = "memory" if oom else "resource" if refused else classify_text(text, code=code)
    row = {
        "cmd": " ".join(str(a) for a in argv),
        "ok": code == 0,
        "code": code,
        "class": kind if code != 0 else "ok",
        "seconds": round(seconds, 3),
        "started": round(t0, 3),
        "peak_rss": peak,
        "oom_killed": oom,
        "cwd": str(cwd),
    }
    if wait_s >= 1:
        row["memory_wait_s"] = round(wait_s, 1)
    timings = _payload_timings(payload)
    if timings:
        row["timings"] = timings
        if timings.get("main_s") is not None:
            row["startup_s"] = round(max(0.0, seconds - float(timings["main_s"])), 3)
    ledger(backend_id).append(row)
    return {**row, "stdout": out or "", "stderr": err or ""}


def _payload_timings(path: Path | None) -> dict[str, float] | None:
    if path is None or not Path(path).exists():
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")).get("timings") or None
    except (json.JSONDecodeError, OSError, AttributeError):
        return None


def lap_timer() -> Any:
    """`lap(name)` records seconds since the previous lap under `name`; `lap.timings` also carries `main_s` since creation."""
    t0 = last = time.perf_counter()
    timings: dict[str, float] = {}

    def lap(name: str) -> None:
        nonlocal last
        now = time.perf_counter()
        timings[name] = round(timings.get(name, 0.0) + now - last, 3)
        timings["main_s"] = round(now - t0, 3)
        last = now

    lap.timings = timings  # type: ignore[attr-defined]
    return lap


def raise_run(row: dict[str, Any], what: str) -> None:
    if row.get("ok"):
        return
    text = (row.get("stderr") or row.get("stdout") or "")[:3000]
    kind = row.get("class") or "unknown"
    msg = f"{what} ({row.get('code')}):\n{text}"
    if kind == "program":
        raise ProgramError(msg, guard=looks_like_guard(text))
    raise EngineError(msg, kind=kind, guard=looks_like_guard(text))


def _normalize_header_text(text: str, name: str) -> tuple[str, int]:
    replacement = f"FILE_NAME('{name}.step','1970-01-01T00:00:00',('opencad'),('opencad'),'opencad','opencad','');"
    return FILE_NAME_RE.subn(lambda m: replacement, text, count=1)


def normalize_step_header(path: Path, name: str = "opencad") -> Path:
    """Rewrite FILE_NAME timestamp/author so two exports can hash-equal."""
    path = Path(path)
    new, n = _normalize_header_text(path.read_text(encoding="utf-8", errors="replace"), name)
    if n:
        path.write_text(new, encoding="utf-8")
    return path


def _snap_real(m: re.Match[str]) -> str:
    tok = m.group(1)
    if tok is None:  # a string literal
        return m.group(0)
    return "0." if abs(float(tok)) < STEP_ZERO_SNAP else tok


def canonicalize_step(path: Path, name: str = "opencad") -> Path:
    """Header normalised and every real below STEP_ZERO_SNAP written as `0.`, so two exports of one part hash-equal.

    OpenCascade keys its shape maps by address, so which of two coincident vertices a boolean keeps differs from
    process to process: `0.` in one export, `1.18E-30` or `-0.` in the next. The B-rep is the same; the bytes are not.
    A read/re-write through OCP does not remove that noise (and stamps a per-process PRODUCT counter), a text pass does.
    """
    path = Path(path)
    text, _ = _normalize_header_text(path.read_text(encoding="utf-8", errors="replace"), name)
    path.write_text(STEP_TOKEN_RE.sub(_snap_real, text), encoding="utf-8")
    return path


def collect_shapes(obj: Any) -> list[Any]:
    """Every OCC shape behind a runner `result`: a Shape (`.wrapped`), a CadQuery Workplane stack (`vals()`),
    a build123d builder (`.part`), or a list/tuple of those."""
    if isinstance(obj, (list, tuple)):
        return [s for o in obj for s in collect_shapes(o)]
    if callable(getattr(obj, "vals", None)):
        return [s for o in obj.vals() for s in collect_shapes(o)]
    if hasattr(obj, "wrapped"):
        return [obj.wrapped]
    part = getattr(obj, "part", None)
    if hasattr(part, "wrapped"):
        return [part.wrapped]
    return [obj]


def result_shape(obj: Any) -> Any:
    """The one TopoDS shape a runner analyzes and exports: a lone shape as is (single-solid output unchanged),
    several as one TopoDS_Compound so a multi-solid deliverable keeps every body (CadQuery's own exporter does the same)."""
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound, TopoDS_Shape

    shapes = [s for s in collect_shapes(obj) if isinstance(s, TopoDS_Shape) and not s.IsNull()]
    if not shapes:
        raise ValueError(f"result holds no OCC shape (got {type(obj).__name__}); assign a solid, a Compound or a list")
    if len(shapes) == 1:
        return shapes[0]
    comp = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(comp)
    for s in shapes:
        builder.Add(comp, s)
    return comp


def write_step(shape: Any, path: Path, name: str = "opencad") -> Path:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    status = writer.Write(str(path))
    if status != IFSelect_RetDone:
        raise EngineError(f"STEP write failed for {path} (status {status})", kind="kernel")
    return normalize_step_header(path, name)


def write_stl(shape: Any, path: Path, deflection: float = 0.02, angular: float = 0.5) -> Path:
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.StlAPI import StlAPI_Writer

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    BRepMesh_IncrementalMesh(shape, deflection, False, angular, True)
    w = StlAPI_Writer()
    w.ASCIIMode = False
    if not w.Write(shape, str(path)):
        raise EngineError(f"STL write failed for {path}", kind="kernel")
    return path


def analyze_shape(shape: Any, *, density_kg_m3: float | None = None) -> dict[str, Any]:
    from opencad.geomcheck.brep import bbox, volume_props

    props = volume_props(shape)
    lo, hi = bbox(shape)
    vol = props["volume"]
    mass_g = None
    if density_kg_m3 and vol is not None:
        mass_g = density_kg_m3 * (vol * 1e-9) * 1000.0
    return {
        "bbox_min": lo,
        "bbox_max": hi,
        "bbox_size": [h - l for l, h in zip(lo, hi)],
        "com": props["center_of_mass"],
        "volume_mm3": vol,
        "surface_area_mm2": props["surface_area"],
        "mass_g": mass_g,
        "density_kg_m3": density_kg_m3,
    }


def stl_to_glb(stl: Path, glb: Path) -> Path:
    """glTF as Zoo writes it: metres, Y-up, right-handed ((x, y, z) mm -> (x, z, -y) m)."""
    import numpy as np
    import trimesh

    glb = Path(glb)
    glb.parent.mkdir(parents=True, exist_ok=True)
    mesh = trimesh.load(str(stl), force="mesh")
    v = np.asarray(mesh.vertices)
    out = trimesh.Trimesh(vertices=np.column_stack((v[:, 0], v[:, 2], -v[:, 1])) / 1000.0, faces=mesh.faces, process=True)
    scene = trimesh.Scene()
    scene.add_geometry(out, node_name=glb.stem, geom_name=glb.stem)
    glb.write_bytes(scene.export(file_type="glb"))
    return glb


def finish_build(entry: Path, row: dict[str, Any], data: dict[str, Any] | None, step: Path | None, stl: Path | None, fcstd: Path | None, *,
                 density_kg_m3: float | None, deterministic: bool) -> dict[str, Any]:
    """The shared tail of `Engine.build`: mass from the density, placements sidecars, the canonical STEP."""
    from opencad.backends.placements import sidecar

    payload = row.get("payload") or {}
    if data is not None:
        data = {**data, "density_kg_m3": density_kg_m3, "seconds": row["seconds"]}
        if density_kg_m3 and data.get("volume_mm3") is not None:
            data["mass_g"] = density_kg_m3 * (float(data["volume_mm3"]) * 1e-9) * 1000.0
    out = {"analyze": data, "seconds": row["seconds"]}
    for key, p in (("step", step), ("stl", stl), ("fcstd", fcstd)):
        out[key] = Path(p) if p and Path(p).exists() else None
        if out[key] is not None and key != "fcstd":
            sidecar(out[key].parent, payload)
    if out["step"] is not None and deterministic:
        canonicalize_step(out["step"], entry.stem)
    return out


def venv_python() -> str:
    exe = Path(sys.executable)
    return str(exe)


def runner_argv(
    python: str,
    module: str,
    entry: Path,
    *,
    analyze: Path | None = None,
    export_step: Path | None = None,
    export_stl: Path | None = None,
    extra: list[str] | None = None,
) -> list[str]:
    argv = [python, "-I", "-m", module, "--entry", str(entry)]
    if analyze:
        argv += ["--analyze", str(analyze)]
    if export_step:
        argv += ["--export-step", str(export_step)]
    if export_stl:
        argv += ["--export-stl", str(export_stl)]
    if extra:
        argv += extra
    return argv


class LocalPythonEngine:
    """Engine protocol for a venv runner module (`python -I -m <module>`)."""

    independent_hints = ""

    def __init__(self, backend_id: str, module: str, version_attr: str):
        self.id = backend_id
        self.module = module
        self.version_attr = version_attr

    def preflight(self) -> dict[str, Any]:
        try:
            r = subprocess.run(
                [venv_python(), "-I", "-c", f"import {self.id}; print(getattr({self.id}, '__version__', 'unknown'))"],
                capture_output=True,
                text=True,
                timeout=30,
            )
        except Exception as e:
            return {"ok": False, "version": None, "error": str(e), "class": "unknown"}
        if r.returncode != 0:
            return {"ok": False, "version": None, "error": (r.stderr or r.stdout)[:400], "class": "program"}
        return {"ok": True, "version": r.stdout.strip(), "error": None}

    def _run(
        self,
        entry: Path,
        *,
        analyze: Path | None = None,
        export_step: Path | None = None,
        export_stl: Path | None = None,
        timeout: float = 600,
        lock: bool = True,
    ) -> dict[str, Any]:
        out_json = Path(tempfile.mkdtemp(prefix="opencad-run-")) / "out.json"
        entry = Path(entry).resolve()  # the runner starts in entry.parent: a relative entry or output path would land under it
        argv = runner_argv(
            venv_python(),
            self.module,
            entry,
            analyze=Path(analyze).resolve() if analyze else out_json,
            export_step=Path(export_step).resolve() if export_step else None,
            export_stl=Path(export_stl).resolve() if export_stl else None,
            extra=["--out", str(out_json)],
        )
        row = run_script(argv, backend_id=self.id, cwd=entry.parent, timeout=timeout, lock=lock, payload=out_json)
        payload: dict[str, Any] = {}
        if out_json.exists():
            try:
                payload = json.loads(out_json.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                payload = {}
        shutil.rmtree(out_json.parent, ignore_errors=True)
        if not row["ok"]:
            raise_run(row, f"{self.id} runner failed")
        if payload and not payload.get("ok", True):
            raise_run(
                {
                    **row,
                    "ok": False,
                    "class": payload.get("class") or row["class"],
                    "stderr": payload.get("error") or row.get("stderr"),
                },
                f"{self.id} runner failed",
            )
        return {**row, "payload": payload}

    def analyze(self, entry: Path, *, density_kg_m3: float | None = None, timeout: float = 600) -> dict[str, Any]:
        return self.build(entry, density_kg_m3=density_kg_m3, timeout=timeout)["analyze"]

    def build(self, entry: Path, *, analyze: bool = True, step: Path | None = None, stl: Path | None = None, fcstd: Path | None = None,
              density_kg_m3: float | None = None, deterministic: bool = True, timeout: float = 600, lock: bool = True) -> dict[str, Any]:
        """Every output an evaluation needs (analyze, STEP, STL) from one runner process: one model build instead of one per output.
        `fcstd` is FreeCAD-only and ignored here."""
        for p in (step, stl):
            if p:
                Path(p).parent.mkdir(parents=True, exist_ok=True)
        dest = Path(tempfile.mkdtemp(prefix="opencad-an-")) / "analyze.json"
        try:
            row = self._run(entry, analyze=dest, export_step=step, export_stl=stl, timeout=timeout, lock=lock)
            data = row["payload"].get("analyze") or (json.loads(dest.read_text(encoding="utf-8")) if dest.exists() else {})
        finally:
            shutil.rmtree(dest.parent, ignore_errors=True)
        return finish_build(Path(entry), row, data if analyze else None, step, stl, None, density_kg_m3=density_kg_m3, deterministic=deterministic)

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
        if fmt == "glb":
            stl = out_dir / f"{entry.stem}.stl"
            row = self._run(entry, export_stl=stl, timeout=timeout, lock=lock)
            from opencad.backends.placements import sidecar

            sidecar(out_dir, row.get("payload") or {})
            glb = out_dir / f"{entry.stem}.glb"
            stl_to_glb(stl, glb)
            return [glb]
        if fmt == "stl":
            dest = out_dir / f"{entry.stem}.stl"
            row = self._run(entry, export_stl=dest, timeout=timeout, lock=lock)
            from opencad.backends.placements import sidecar

            sidecar(out_dir, row.get("payload") or {})
            return [dest]
        dest = out_dir / f"{entry.stem}.step"
        row = self._run(entry, export_step=dest, timeout=timeout, lock=lock)
        from opencad.backends.placements import sidecar

        sidecar(out_dir, row.get("payload") or {})
        if dest.exists() and deterministic:
            canonicalize_step(dest, entry.stem)
        return [dest]

    def classify(self, text_or_exc: Any, *, code: int | None = None) -> FailureClass:
        if isinstance(text_or_exc, BaseException):
            kind = getattr(text_or_exc, "kind", None)
            if kind:
                return kind
            return classify_text(str(text_or_exc), code=code)
        return classify_text(str(text_or_exc), code=code)

    def kernel_patterns(self) -> list[Any]:
        return [
            re.compile(p, re.I)
            for p in (
                "StdFail_NotDone",
                "Standard_ConstructionError",
                "BRep_API: command not done",
                "Standard_Failure",
                r"not a valid",
            )
        ]

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
            "Kernel failures (StdFail_NotDone, command not done) are usually coincident faces: "
            "offset the tool 0.01-0.05 mm past the cut face, batch tools into one cut, and avoid bare edge indices."
        )

    def version(self) -> str:
        # venv_python() is this interpreter, so its installed metadata names the version preflight would import
        try:
            return importlib.metadata.version(self.id)
        except importlib.metadata.PackageNotFoundError:
            return self.preflight().get("version") or "unknown"

    def reset_ledger(self) -> list[dict[str, Any]]:
        return reset_ledger(self.id)

    def engine_calls(self) -> int:
        return len(ledger(self.id))


def cost(ledger_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "calls": len(ledger_rows),
        "seconds": round(sum(float(r.get("seconds") or 0) for r in ledger_rows), 2),
        "usd": 0,
        "peak_rss": max((int(r.get("peak_rss") or 0) for r in ledger_rows), default=0),
    }


SHARED_RULES = """\
Shared modelling rules (every backend):
- Work in millimetres and degrees. Contract parameters are top-level literal constants with the EXACT contract names and values, one per line, before any geometry, so the pipeline can rewrite them for edit tests. A `derived` parameter may instead be its formula over the stated names (`cavityWidth = outerWidth - 2 * wallThickness`), so an edit to a stated parameter carries through; it must evaluate to the contract value.
- Guard invariants with asserts that carry a message. Never lock two contract parameters together with equality (the pipeline rewrites one at a time).
- Every `edit_test.sweep` value and every `edit_test.delta` must build; every `edit_test.infeasible_deltas` value must fail an assert, never build distorted geometry.
- Do not import, read or reference any reference mesh or CAD file; a station outline or fit the contract names in `reference/reference.json` may be copied into the source as constants (at most 16 points per station). Do not edit contract.yaml, brief.md or anything under truth/.
- Verify with the local critic (`python -m opencad quick <entry> --contract <contract>`) before reporting; state measured versus expected numbers.
"""
