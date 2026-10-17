"""Zoo/KCL hosted engine: CLI runner, ledger, preflight, analyze/export."""

from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from opencad.backends.base import BillingError, EngineError, FailureClass, ProgramError

LEDGER: list[dict[str, Any]] = []

# Paid modeling-app tiers bill overage; prepaid remaining can be 0 and the engine still runs.
_PAID_PLANS = frozenset({"pro", "team", "enterprise", "business", "plus"})

_TRANSIENT = (
    "modeling connection interrupted",
    "connection interrupted",
    "please reconnect and retry",
    "too many active connections",
)
ENGINE_SLOTS = int(os.environ.get("OPENCAD_ZOO_SLOTS", "2"))
_CREDITS = (
    "no api credits available",
    "not included in your current plan",
    "pay-as-you-go collection threshold",
    "outstanding usage invoice",
    "update your payment details",
    "your account is blocked",
    "payment method failed",
)
_KCL = ("kcl execution failed:", "kcl execution had errors")
_KERNEL = (
    "cannot handle this 3d",
    "kernel error",
    "kernel failure",
    "kernel failed",
    "kernel crash",
    "boolean failed",
    "boolean failure",
    "boolean error",
    "engine error",
    "engine panic",
    "failed to fuse",
    "failed to subtract",
    "failed to union",
    "failed to intersect",
)
KERNEL_RE = re.compile(
    r"cannot handle this 3D|kernel (error|failure|failed|crash)|boolean (failed|failure|error)|engine (error|panic)|failed to (fuse|subtract|union|intersect)",
    re.I,
)

HINTS = (
    'Engine booleans that fail with "cannot handle this 3D subtraction" or a kernel error are usually '
    "coincident or tangent faces: offset the tool slightly past the face it cuts (0.01-0.05 mm overrun), "
    "split the cut into simpler tools, or cut before fusing the body that makes it fail."
)


class ZooError(EngineError):
    kind: str = "unknown"

    def __init__(self, message: str, *, kind: str = "unknown", guard: bool = False):
        super().__init__(message, kind=kind, guard=guard)


class ZooCreditsError(BillingError, ZooError):
    def __init__(self, message: str):
        BillingError.__init__(self, message)
        self.kind = "billing"


class ZooKclError(ProgramError, ZooError):
    def __init__(self, message: str, *, guard: bool = False):
        ProgramError.__init__(self, message, guard=guard)
        self.kind = "program"
        self.guard = guard


@dataclass
class Result:
    args: list[str]
    code: int
    stdout: str
    stderr: str
    seconds: float

    @property
    def ok(self) -> bool:
        return self.code == 0


def _looks_like_guard(text: str) -> bool:
    low = text.lower()
    return "assert" in low


def classify(result: Result | str | BaseException, *, code: int | None = None) -> FailureClass:
    """Classify a CLI result or recorded error string. Credits -> billing, KCL -> program."""
    if isinstance(result, BaseException) and not isinstance(result, Result):
        kind = getattr(result, "kind", None)
        if kind in (
            "ok",
            "transient",
            "billing",
            "credits",
            "program",
            "kcl",
            "kernel",
            "timeout",
            "resource",
            "memory",
            "unknown",
        ):
            return {"credits": "billing", "kcl": "program"}.get(kind, kind)  # type: ignore[return-value]
        result = str(result)
    if isinstance(result, Result):
        if result.ok:
            return "ok"
        code = result.code
        text = f"{result.stderr or ''}\n{result.stdout or ''}"
    else:
        text = str(result)
        if code is None:
            code = 124 if "timed out after" in text.lower() else 1
    if code == 124:
        return "timeout"
    low = text.lower()
    if any(s in low for s in _TRANSIENT):
        return "transient"
    if any(s in low for s in _CREDITS):
        return "billing"
    if any(s in low for s in _KERNEL):
        return "kernel"
    if any(s in low for s in _KCL):
        return "program"
    return "unknown"


def error_kind(exc: BaseException) -> FailureClass:
    kind = getattr(exc, "kind", None)
    mapped = {"credits": "billing", "kcl": "program"}.get(kind, kind)
    if mapped in ("transient", "billing", "program", "kernel", "timeout", "resource", "memory", "unknown", "ok"):
        return mapped  # type: ignore[return-value]
    return classify(str(exc))


def raise_for(result: Result, what: str) -> None:
    if result.ok:
        return
    kind = classify(result)
    text = (result.stderr or result.stdout).strip()
    msg = f"{what} ({result.code}):\n{text[:3000]}"
    if kind == "billing":
        raise ZooCreditsError(msg)
    if kind == "program":
        raise ZooKclError(msg, guard=_looks_like_guard(text))
    raise ZooError(msg, kind=kind, guard=_looks_like_guard(text))


def zoo_bin() -> str:
    exe = shutil.which("zoo")
    if not exe:
        raise ZooError("zoo CLI not found on PATH")
    return exe


def lock_path() -> Path:
    override = os.environ.get("OPENCAD_ZOO_LOCK")
    if override:
        return Path(override)
    return Path.home() / ".cache" / "opencad" / "zoo.lock"


@contextmanager
def _engine_lock() -> Iterator[None]:
    path = lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a+") as fh:
        fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)


@contextmanager
def _engine_slot() -> Iterator[None]:
    """Bounded concurrency: one of ENGINE_SLOTS slot files (the engine refuses a third active connection)."""
    base = lock_path()
    base.parent.mkdir(parents=True, exist_ok=True)
    slots = [base.with_name(f"{base.name}.slot{i}") for i in range(max(1, ENGINE_SLOTS))]
    handles = [open(p, "a+") for p in slots]
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
                time.sleep(0.2)
        yield
    finally:
        if got is not None:
            fcntl.flock(got.fileno(), fcntl.LOCK_UN)
        for fh in handles:
            fh.close()


IMPORT_RE = re.compile(r'^(\s*import\b[^"\n]*")([^"\n]+\.kcl)(")', re.MULTILINE)
STAGED_SUBCOMMANDS = ("analyze", "export", "snapshot")


def outside_imports(entry: Path) -> dict[str, Path]:
    """Import literals of `entry` that resolve to a KCL file outside its directory (a decompose scratch main's `../../parts/...`)."""
    home = entry.parent.resolve()
    out: dict[str, Path] = {}
    for m in IMPORT_RE.finditer(entry.read_text(encoding="utf-8", errors="replace")):
        p = (entry.parent / m.group(2)).resolve()
        if p.is_file() and not p.is_relative_to(home):
            out[m.group(2)] = p
    return out


@contextmanager
def staged_entry(entry: Path) -> Iterator[Path]:
    """The engine rejects imports outside the entry's directory: run such an entry from a flat temporary project holding every
    `.kcl` of the imported directories, then the entry's own siblings, with the outside imports rewritten to bare names."""
    import tempfile

    outside = outside_imports(entry)
    if not outside:
        yield entry
        return
    with tempfile.TemporaryDirectory(prefix="opencad-zoo-project-") as td:
        root = Path(td)
        for d in sorted({p.parent for p in outside.values()}):
            for f in d.glob("*.kcl"):
                shutil.copy2(f, root / f.name)
        for f in entry.parent.glob("*.kcl"):
            if f != entry and not (root / f.name).exists():
                shutil.copy2(f, root / f.name)
        text = IMPORT_RE.sub(lambda m: m.group(1) + (outside[m.group(2)].name if m.group(2) in outside else m.group(2)) + m.group(3),
                             entry.read_text(encoding="utf-8"))
        dest = root / (f"_entry-{entry.name}" if entry.name in {p.name for p in outside.values()} else entry.name)
        dest.write_text(text, encoding="utf-8")
        yield dest


@contextmanager
def staged_args(args: list[str]) -> Iterator[list[str]]:
    """`args` with each existing `.kcl` target of an analyze/export/snapshot call replaced by its staged copy."""
    if len(args) < 2 or args[0] != "kcl" or args[1] not in STAGED_SUBCOMMANDS:
        yield args
        return
    from contextlib import ExitStack

    with ExitStack() as stack:
        yield [str(stack.enter_context(staged_entry(Path(a)))) if a.endswith(".kcl") and Path(a).is_file() else a for a in args]


def _retry_sleep(attempt_index: int) -> None:
    base = float(os.environ.get("OPENCAD_ZOO_RETRY_BASE", "5"))
    if base <= 0:
        return
    time.sleep(base * (2**attempt_index))


def run(args: list[str], *, engine: bool, timeout: float = 300, cwd: Path | None = None, lock: bool = True) -> Result:
    """`lock=False` lets the pipeline run a bounded batch of independent hosted calls concurrently."""
    attempts = 4 if engine else 1
    last: Result | None = None
    t0 = time.time()
    lock_cm = (_engine_lock() if lock else _engine_slot()) if engine else nullcontext()
    with lock_cm, staged_args(args) as argv:
        for i in range(attempts):
            t_try = time.time()
            try:
                p = subprocess.run(
                    [zoo_bin(), *argv],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    cwd=cwd,
                    env={**os.environ},
                )
                code, out, err = p.returncode, p.stdout, p.stderr
            except subprocess.TimeoutExpired:
                code, out, err = 124, "", f"zoo {' '.join(args)} timed out after {timeout}s"
            last = Result(args, code, out, err, time.time() - t_try)
            kind = classify(last)
            if engine:
                LEDGER.append(
                    {
                        "cmd": "zoo " + " ".join(args),
                        "attempt": i + 1,
                        "class": kind,
                        "ok": last.ok,
                        "seconds": round(last.seconds, 2),
                    }
                )
            if last.ok or not engine or kind != "transient" or i == attempts - 1:
                break
            _retry_sleep(i)
    r = last if last is not None else Result(args, 1, "", "no attempt", 0.0)
    r.seconds = time.time() - t0
    return r


def engine_calls() -> int:
    return len(LEDGER)


def reset_ledger() -> list[dict[str, Any]]:
    global LEDGER
    old = list(LEDGER)
    LEDGER.clear()
    return old


def version() -> str:
    r = run(["version"], engine=False, timeout=20)
    return r.stdout.strip().splitlines()[0] if r.ok and r.stdout.strip() else "unknown"


def credits() -> dict[str, Any]:
    r = run(["api", "/user/payment/balance"], engine=False, timeout=30)
    if not r.ok:
        return {"known": False, "error": (r.stderr or r.stdout).strip()[:300]}
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"known": False, "error": r.stdout[:300]}
    plan = (d.get("subscription_details") or {}).get("modeling_app") or {}
    monthly = d.get("monthly_api_credits_remaining") or 0
    stable = d.get("stable_api_credits_remaining") or 0
    name = (plan.get("name") or "").lower()
    payg_price = plan.get("pay_as_you_go_api_credit_price")
    can_execute = (monthly + stable) > 0 or name in _PAID_PLANS or bool(payg_price)
    return {
        "known": True,
        "monthly_remaining": monthly,
        "stable_remaining": stable,
        "remaining_total": monthly + stable,
        "monetary_value": (d.get("monthly_api_credits_remaining_monetary_value") or 0)
        + (d.get("stable_api_credits_remaining_monetary_value") or 0),
        "refresh_at": d.get("monthly_api_credits_refresh_at"),
        "plan": plan.get("name"),
        "pay_as_you_go_price": payg_price,
        "can_execute": can_execute,
    }


PROBE_CACHE = Path(
    os.environ.get("OPENCAD_ENGINE_PROBE") or (Path.home() / ".cache" / "opencad" / "engine-probe.json")
)
PROBE_TTL_S = 600.0
PROBE_KCL = """@settings(defaultLengthUnit = mm, kclVersion = 2.0)
s = sketch(on = XY) {
  a = line(start = [0, 0], end = [1, 0])
  b = line(start = [1, 0], end = [1, 1])
  c = line(start = [1, 1], end = [0, 1])
  d = line(start = [0, 1], end = [0, 0])
}
probe = extrude(region(segments = [s.a, s.b]), length = 1)
"""


def engine_probe(force: bool = False) -> dict[str, Any]:
    if not force and PROBE_CACHE.exists():
        try:
            cached = json.loads(PROBE_CACHE.read_text())
            if cached.get("ok") and time.time() - float(cached.get("t", 0)) < PROBE_TTL_S:
                return cached
        except (json.JSONDecodeError, ValueError):
            pass
    import tempfile

    with tempfile.TemporaryDirectory(prefix="opencad-probe-") as td:
        kcl = Path(td) / "probe.kcl"
        kcl.write_text(PROBE_KCL, encoding="utf-8")
        r = run(["kcl", "analyze", "--format", "json", str(kcl)], engine=True, timeout=120)
    out = {
        "t": time.time(),
        "ok": r.ok,
        "class": None if r.ok else classify(r),
        "error": None if r.ok else (r.stderr or r.stdout).strip()[:400],
    }
    PROBE_CACHE.parent.mkdir(parents=True, exist_ok=True)
    PROBE_CACHE.write_text(json.dumps(out))
    return out


def require_credits(minimum: int = 20, probe: bool = True) -> dict[str, Any]:
    c = credits()
    if not c.get("known"):
        return c
    if c.get("can_execute"):
        # the balance API reports can_execute while the engine refuses a blocked account
        if probe:
            pr = engine_probe()
            c["probe"] = pr
            if not pr["ok"] and pr.get("class") in ("billing", "credits"):
                raise ZooCreditsError(f"the Zoo engine refuses hosted calls on this account: {pr['error']}")
        return c
    if c["remaining_total"] < minimum:
        raise ZooCreditsError(
            f"Zoo API credits exhausted ({c['remaining_total']} remaining on plan {c['plan']!r}; refresh {c.get('refresh_at')}). "
            "Hosted analyze/export/snapshot calls will be refused. Enable pay-as-you-go or upgrade at https://zoo.dev/account/billing, then re-run."
        )
    return c


def forecast_calls(contract: Any, from_stage: str = "verify") -> dict[str, Any]:
    n_edit = sum(1 for p in getattr(contract, "parameters", []) if getattr(p, "edit_test", None))
    breakdown = {"analyze": 0, "snapshots": 0, "step": 0, "stl": 0, "glb": 0, "edit_exports": 0}
    order = ["plan", "model", "verify", "export", "inspect", "edit", "gates", "report"]
    start = order.index(from_stage) if from_stage in order else 0
    if start <= order.index("verify"):
        breakdown["analyze"] = 1
    if start <= order.index("export"):
        breakdown["step"] = 2
        breakdown["stl"] = 1
        breakdown["glb"] = 1
    if start <= order.index("edit"):
        breakdown["edit_exports"] = n_edit + 1
    return {
        "total": sum(breakdown.values()),
        "breakdown": breakdown,
        "edit_tests": n_edit,
        "from_stage": from_stage,
        "note": "monetary cost unknown on PAYG; snapshots render locally from STL",
    }


def credit_banner(credits_info: dict[str, Any], forecast: dict[str, Any] | None = None) -> str:
    plan = credits_info.get("plan", "?")
    prepaid = credits_info.get("remaining_total", "?")
    payg = credits_info.get("pay_as_you_go_price")
    bits = [f"zoo credits: plan {plan}, prepaid {prepaid}, PAYG {payg if payg is not None else 'off'}"]
    if forecast:
        b = forecast["breakdown"]
        bits.append(
            f"forecast {forecast['total']} calls (analyze {b['analyze']}, snapshots {b['snapshots']}, "
            f"STEP {b['step']}, STL {b['stl']}, GLB {b['glb']}, edit exports {b['edit_exports']})"
        )
        bits.append(forecast.get("note") or "monetary cost unknown on PAYG")
    return "; ".join(bits)


def preflight() -> dict[str, Any]:
    try:
        c = require_credits()
    except ZooCreditsError as e:
        return {"ok": False, "version": version(), "billing": None, "error": str(e), "class": "billing"}
    return {
        "ok": bool(c.get("can_execute") or not c.get("known")),
        "version": version(),
        "billing": c,
        "error": c.get("error"),
    }


def kcl_files(target: Path) -> list[Path]:
    target = Path(target)
    if target.is_file():
        return [target]
    return sorted(p for p in target.rglob("*.kcl"))


def format_check(target: Path) -> dict[str, Any]:
    findings = []
    for f in kcl_files(target):
        r = run(["kcl", "format", str(f)], engine=False, timeout=60)
        if not r.ok:
            findings.append({"file": str(f), "error": (r.stderr or r.stdout).strip()[:500]})
            continue
        if r.stdout.rstrip() != f.read_text(encoding="utf-8").rstrip():
            findings.append({"file": str(f), "error": "not formatted (zoo kcl format --write would change it)"})
    return {"ok": not findings, "findings": findings}


def format_write(target: Path) -> Result:
    return run(["kcl", "format", "--write", str(target)], engine=False, timeout=60)


def lint(target: Path) -> dict[str, Any]:
    r = run(["kcl", "lint", str(target)], engine=False, timeout=120)
    text = (r.stdout + r.stderr).strip()
    return {"ok": r.ok and not text, "code": r.code, "output": text[:4000]}


def analyze(
    target: Path, *, density_kg_m3: float | None = None, timeout: float = 600, lock: bool = True
) -> dict[str, Any]:
    args = [
        "kcl",
        "analyze",
        "--format",
        "json",
        "--volume-output-unit",
        "mm3",
        "--center-of-mass-output-unit",
        "mm",
        "--surface-area-output-unit",
        "mm2",
        "--mass-output-unit",
        "g",
    ]
    if density_kg_m3:
        args += ["--material-density", str(density_kg_m3), "--material-density-unit", "kg:m3"]
    args.append(str(target))
    r = run(args, engine=True, timeout=timeout, lock=lock)
    raise_for(r, "zoo kcl analyze failed")
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        raise ZooError(f"analyze returned non-JSON: {r.stdout[:500]}", kind="unknown") from e
    bb = data.get("bounding_box", {})
    c, d = bb.get("center", {}), bb.get("dimensions", {})
    if c and d:
        data["bbox_min"] = [c[a] - d[a] / 2 for a in "xyz"]
        data["bbox_max"] = [c[a] + d[a] / 2 for a in "xyz"]
        data["bbox_size"] = [d[a] for a in "xyz"]
    com = data.get("center_of_mass", {}).get("center_of_mass", {})
    data["com"] = [com.get(a) for a in "xyz"] if com else None
    data["volume_mm3"] = data.get("volume", {}).get("volume")
    data["surface_area_mm2"] = data.get("surface_area", {}).get("surface_area")
    data["mass_g"] = data.get("mass", {}).get("mass") if density_kg_m3 else None
    data["density_kg_m3"] = density_kg_m3
    data["seconds"] = round(r.seconds, 2)
    return data


def export(
    target: Path, out_dir: Path, fmt: str, *, deterministic: bool = True, timeout: float = 600, lock: bool = True
) -> list[Path]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    before = {p.name for p in out_dir.iterdir()}
    args = ["kcl", "export", "--output-format", fmt]
    if deterministic:
        args.append("--deterministic")
    args += [str(target), str(out_dir)]
    r = run(args, engine=True, timeout=timeout, lock=lock)
    raise_for(r, f"zoo kcl export {fmt} failed")
    written = sorted(
        p
        for p in out_dir.iterdir()
        if p.is_file() and (p.name not in before or p.stat().st_mtime > time.time() - r.seconds - 5)
    )
    if not written:
        raise ZooError(f"zoo kcl export {fmt} reported success but wrote nothing into {out_dir}", kind="unknown")
    return written


_analyze = analyze  # build's `analyze` flag shadows the function


def build(entry: Path, *, analyze: bool = True, step: Path | None = None, stl: Path | None = None, density_kg_m3: float | None = None,
          deterministic: bool = True, timeout: float = 1800, lock: bool = True) -> dict[str, Any]:
    import tempfile

    entry = Path(entry)
    t0 = time.time()
    out: dict[str, Any] = {"analyze": None, "step": None, "stl": None}
    with tempfile.TemporaryDirectory(prefix="opencad-zoo-build-") as td:
        for key, dest, fmt in (("step", step, "step"), ("stl", stl, "stl")):
            if not dest:
                continue
            written = [p for p in export(entry, Path(td) / fmt, fmt, deterministic=deterministic, timeout=timeout, lock=lock) if p.suffix.lower() == f".{fmt}"]
            if not written:
                raise ZooError(f"zoo kcl export {fmt} wrote no .{fmt} file", kind="unknown")
            dest = Path(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(written[0]), dest)
            out[key] = dest
    for sidecar in ("placements.json", "joints.json"):
        src = entry.parent / sidecar
        if src.exists() and out["step"] is not None:
            shutil.copy2(src, out["step"].parent / sidecar)
    if analyze:
        out["analyze"] = _analyze(entry, density_kg_m3=density_kg_m3, timeout=timeout, lock=lock)
    out["seconds"] = round(time.time() - t0, 2)
    return out


def snapshot(
    target: Path,
    out_file: Path,
    *,
    angle: str = "four-ways",
    camera_style: str | None = None,
    timeout: float = 600,
    lock: bool = True,
) -> Path:
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    args = ["kcl", "snapshot", "--angle", angle]
    if camera_style:
        args += ["--camera-style", camera_style]
    args += [str(target), str(out_file)]
    r = run(args, engine=True, timeout=timeout, lock=lock)
    if not r.ok or not out_file.exists():
        raise_for(r, f"zoo kcl snapshot {angle} failed")
        raise ZooError(f"zoo kcl snapshot {angle} failed ({r.code}): wrote no file", kind=classify(r))
    return out_file


def snapshots(
    target: Path, out_dir: Path, angles: tuple[str, ...] = ("front", "top", "right-side", "iso"), **kw: Any
) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for a in angles:
        out[a] = snapshot(target, Path(out_dir) / f"view-{a}.png", angle=a, **kw)
    return out


def file_volume_mm3(path: Path, timeout: float = 300) -> float | None:
    fmt = {
        ".step": "step",
        ".stp": "step",
        ".stl": "stl",
        ".obj": "obj",
        ".ply": "ply",
        ".glb": "glb",
        ".gltf": "gltf",
    }.get(Path(path).suffix.lower())
    if not fmt:
        return None
    r = run(
        ["file", "volume", "--format", "json", "--src-format", fmt, "--output-unit", "mm3", str(path)],
        engine=True,
        timeout=timeout,
    )
    if not r.ok:
        return None
    try:
        return float(json.loads(r.stdout).get("volume"))
    except Exception:
        return None


def ledger_wrapper(argv: list[str], ledger: Path | None) -> int:
    """`python -m opencad engine [--ledger PATH] -- <zoo args>`: run the CLI and append one ledger row per hosted call."""
    from opencad.io import utc_now

    path = ledger or Path(
        os.environ.get("OPENCAD_ENGINE_LEDGER") or (Path.home() / ".cache" / "opencad" / "engine-ledger.jsonl")
    )
    engine = bool(argv) and argv[0] in ("kcl", "file") and (len(argv) < 2 or argv[1] not in ("format", "lint"))
    t0 = time.time()
    try:
        with _engine_slot() if engine else nullcontext(), staged_args(argv) as staged:
            code = subprocess.run([zoo_bin(), *staged]).returncode
    except ZooError as e:
        print(str(e), file=sys.stderr)
        return 127
    seconds = time.time() - t0
    if engine:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "ts": utc_now(),
                        "cmd": "zoo " + " ".join(argv),
                        "seconds": round(seconds, 2),
                        "ok": code == 0,
                        "code": code,
                    }
                )
                + "\n"
            )
    return code


def cost(ledger_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "calls": len(ledger_rows),
        "seconds": round(sum(float(r.get("seconds") or 0) for r in ledger_rows), 2),
        "usd": None,
    }


class ZooEngine:
    id = "zoo"

    def preflight(self) -> dict[str, Any]:
        return preflight()

    def analyze(self, entry: Path, *, density_kg_m3: float | None = None, timeout: float = 600) -> dict[str, Any]:
        return analyze(entry, density_kg_m3=density_kg_m3, timeout=timeout)

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
        return export(entry, out_dir, fmt, deterministic=deterministic, timeout=timeout, lock=lock)

    # not named `build`: part stages treat an engine `build` as the local single-run path
    def build_assembly(self, entry: Path, *, analyze: bool = True, step: Path | None = None, stl: Path | None = None,
                       density_kg_m3: float | None = None, deterministic: bool = True, timeout: float = 1800, lock: bool = True) -> dict[str, Any]:
        """Hosted STEP and STL exports of an assembly `main.kcl`, with its `placements.json` / `joints.json` beside the STEP."""
        return build(entry, analyze=analyze, step=step, stl=stl, density_kg_m3=density_kg_m3, deterministic=deterministic, timeout=timeout, lock=lock)

    def classify(self, text_or_exc: Any, *, code: int | None = None) -> FailureClass:
        return classify(text_or_exc, code=code)

    def kernel_patterns(self) -> list[re.Pattern[str]]:
        return [KERNEL_RE]

    def max_concurrency(self) -> int:
        return ENGINE_SLOTS

    def ledger_wrapper(self, argv: list[str], ledger: Path | None) -> int:
        return ledger_wrapper(argv, ledger)

    def cost(self, ledger_rows: list[dict[str, Any]]) -> dict[str, Any]:
        return cost(ledger_rows)

    def hints(self) -> str:
        return HINTS

    def version(self) -> str:
        return version()

    def reset_ledger(self) -> list[dict[str, Any]]:
        return reset_ledger()

    def engine_calls(self) -> int:
        return engine_calls()
