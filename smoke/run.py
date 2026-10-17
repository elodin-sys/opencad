#!/usr/bin/env python3
"""Smoke-test campaign: local readiness for agentic CAD with Zoo.

Exercises the zoo CLI, the REST API (via `zoo api` / `zoo file`), the Zoo MCP server, and
the curated skills in .agents/skills. Writes smoke/report.md. Exit 1 on any FAIL.

  python3 smoke/run.py              # full campaign (~15 engine executions, billed as API usage; the
                                    # codex section adds two GPT-6 Astra tasks and a few minutes)
  python3 smoke/run.py --sections env,skills,cli
  python3 smoke/run.py --studio     # also open the bracket in Zoo Design Studio at the end
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SMOKE = ROOT / "smoke"
OUT = SMOKE / "out"
PARTS = SMOKE / "parts"
SKILLS = ROOT / ".agents" / "skills"
ZOO_SKILLS = SKILLS / "backends" / "zoo"
SAMPLES = ZOO_SKILLS / "kcl-examples" / "samples"
COUPON = PARTS / "coupon" / "main.kcl"
BRACKET = PARTS / "bracket" / "main.kcl"
BROKEN = PARTS / "broken.kcl"
MULTI_FILE_SAMPLE = SAMPLES / "coilover-assembly"
CODEX_EXEC = SKILLS / "codex-worker" / "scripts" / "codex_exec.py"

# Analytic expectations (mm). Coupon: 60 x 40 x 4 plate. Bracket: 80 x 50 x 6 plate,
# four R5 corner fillets, four 4.5 mm through holes. Plate (Codex task): 40 x 30 x 5
# with one centred through hole, first 10 mm then 12 mm.
COUPON_VOLUME = 60 * 40 * 4
COUPON_AREA = 2 * (60 * 40 + 60 * 4 + 40 * 4)
BRACKET_VOLUME = 80 * 50 * 6 - 4 * (25 - math.pi * 25 / 4) * 6 - 4 * math.pi * 2.25**2 * 6
PLATE_VOLUME = 40 * 30 * 5 - math.pi * 5**2 * 5
PLATE_VOLUME_12 = 40 * 30 * 5 - math.pi * 6**2 * 5

ENGINE_CALLS = 0


def count_engine_call() -> None:
    global ENGINE_CALLS
    ENGINE_CALLS += 1


@dataclass
class Check:
    id: str
    name: str
    status: str = "PASS"
    evidence: str = ""
    seconds: float = 0.0


@dataclass
class Section:
    name: str
    checks: list[Check] = field(default_factory=list)


def rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def run(
    cmd: list[str], timeout: float = 240, engine: bool = False, env: dict | None = None
) -> subprocess.CompletedProcess:
    if engine:
        count_engine_call()
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT, env=env)


def approx(actual: float, expected: float, rel_tol: float) -> bool:
    return abs(actual - expected) <= abs(expected) * rel_tol


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def tokens(path: Path) -> int:
    return len(path.read_text(encoding="utf-8")) // 4


class Runner:
    def __init__(self, wanted: list[str]) -> None:
        self.sections: list[Section] = []
        self.token: str | None = None
        self.notes: list[str] = []
        self.wanted = wanted

    def section(self, name: str) -> Section:
        s = Section(name)
        self.sections.append(s)
        return s

    @staticmethod
    def _execute(cid: str, name: str, fn) -> Check:
        c = Check(cid, name)
        t0 = time.time()
        try:
            evidence = fn()
            c.evidence = evidence or ""
        except AssertionError as e:
            c.status, c.evidence = "FAIL", str(e)
        except Exception as e:  # noqa: BLE001 - any failure is a smoke failure
            c.status, c.evidence = "FAIL", f"{type(e).__name__}: {str(e)[:300]}"
        c.seconds = time.time() - t0
        return c

    @staticmethod
    def _print(c: Check) -> None:
        mark = {"PASS": "ok", "FAIL": "FAIL", "SKIP": "skip"}[c.status]
        print(f"  [{mark:4}] {c.id:4} {c.name} ({c.seconds:.1f}s) {c.evidence[:110]}")

    def check(self, section: Section, cid: str, name: str, fn) -> Check:
        c = self._execute(cid, name, fn)
        section.checks.append(c)
        self._print(c)
        return c

    # ------------------------------------------------------------------ env
    def env(self) -> None:
        s = self.section("Environment")

        def cli_version() -> str:
            assert shutil.which("zoo"), "zoo CLI not on PATH"
            r = run(["zoo", "version"])
            assert r.returncode == 0, r.stderr
            m = re.search(r"zoo (\S+) \(([0-9a-f]+)\)", r.stdout)
            assert m, r.stdout
            return f"zoo {m.group(1)} ({m.group(2)[:12]})"

        def auth() -> str:
            r = run(["zoo", "auth", "status"])
            m = re.search(r"Logged in to (\S+) as (\S+)", r.stdout + r.stderr)
            assert m, (r.stdout + r.stderr).strip()[:200]
            return f"{m.group(2)} @ {m.group(1)}"

        def token() -> str:
            tok = os.environ.get("ZOO_API_TOKEN")
            source = "env ZOO_API_TOKEN"
            if not tok:
                r = run(["zoo", "auth", "status", "-t"])
                m = re.search(r"Token:\s*(\S+)", r.stdout + r.stderr)
                assert m and "*" not in m.group(1), "no usable token: set ZOO_API_TOKEN or `zoo auth login`"
                tok, source = m.group(1), "zoo auth status -t"
            self.token = tok
            return f"{len(tok)} chars via {source} (used for the MCP server)"

        def uv() -> str:
            assert shutil.which("uvx"), "uvx not found (install uv)"
            r = run(["uv", "--version"])
            return r.stdout.strip()

        def studio() -> str:
            app = Path("/Applications/Zoo Design Studio.app")
            assert app.exists(), "Zoo Design Studio.app not in /Applications"
            plist = app / "Contents" / "Info.plist"
            r = run(["defaults", "read", str(plist), "CFBundleShortVersionString"])
            return f"installed, v{r.stdout.strip() or '?'}"

        self.check(s, "E1", "zoo CLI present", cli_version)
        self.check(s, "E2", "zoo auth logged in", auth)
        self.check(s, "E3", "API token available for MCP", token)
        self.check(s, "E4", "uv/uvx present", uv)
        self.check(s, "E5", "Zoo Design Studio installed", studio)

    # --------------------------------------------------------------- skills
    def skills(self) -> None:
        s = self.section("Skills (static)")

        def gates() -> str:
            r = run([sys.executable, str(ROOT / "scripts" / "check_skills.py")], timeout=120)
            passes = re.findall(r"^\[PASS\*?\] (\S+)", r.stdout, re.M)
            fails = re.findall(r"^\[FAIL\] (\S+)", r.stdout, re.M)
            assert r.returncode == 0 and not fails, f"gates failing: {fails}\n{r.stdout[-600:]}"
            return f"{len(passes)} gates pass: {', '.join(passes)}"

        def discovery() -> str:
            found = []
            for sk in sorted(SKILLS.rglob("SKILL.md")):
                d = sk.parent
                m = re.search(r"^name:\s*(\S+)", sk.read_text(encoding="utf-8"), re.M)
                assert m and m.group(1) == d.name, f"{d.relative_to(SKILLS)}: frontmatter name mismatch"
                found.append(str(d.relative_to(SKILLS)))
            zoo = [f"backends/zoo/{n}" for n in ("kcl-docs", "kcl-examples", "kcl-research", "zoo-tooling")]
            missing = [p for p in ["codex-worker", *zoo] if p not in found]
            assert not missing, f"missing skills: {missing}; found {found}"
            return ", ".join(found)

        def cold_read() -> str:
            tasks = {
                "plate with M4 holes": [
                    "backends/zoo/kcl-docs/SKILL.md",
                    "backends/zoo/kcl-docs/patterns.md",
                    "backends/zoo/kcl-docs/std/hole.md",
                    "backends/zoo/kcl-docs/std/sketch.md",
                ],
                "extrude(method = NEW)": [
                    "backends/zoo/kcl-docs/SKILL.md",
                    "backends/zoo/kcl-docs/std/index.md",
                    "backends/zoo/kcl-docs/std/sketch.md",
                ],
                "helix sweep sample": [
                    "backends/zoo/kcl-examples/SKILL.md",
                    "backends/zoo/kcl-examples/by-feature.md",
                    "backends/zoo/kcl-examples/samples/coilover-assembly/spring.kcl",
                ],
                "B-rep vs mesh": ["backends/zoo/kcl-research/SKILL.md", "backends/zoo/kcl-research/digest.md"],
                "export STEP via CLI": ["backends/zoo/zoo-tooling/SKILL.md", "backends/zoo/zoo-tooling/cli.md"],
            }
            costs = {k: sum(tokens(SKILLS / f) for f in v) for k, v in tasks.items()}
            over = {k: v for k, v in costs.items() if v > 8000}
            assert not over, f"over 8k tokens: {over}"
            return "; ".join(f"{k} {v}" for k, v in costs.items()) + " tok"

        def corpus_files() -> str:
            files = list(SAMPLES.rglob("*.kcl"))
            dirs = sorted(d for d in SAMPLES.iterdir() if d.is_dir())
            assert len(files) == 176 and len(dirs) == 126, f"{len(files)} files / {len(dirs)} samples"
            outliers = set()
            for d in dirs:
                m = re.search(r"kclVersion\s*=\s*2\.0", (d / "main.kcl").read_text(encoding="utf-8"))
                if not m:
                    outliers.add(d.name)
            index = (ZOO_SKILLS / "kcl-examples" / "index.md").read_text(encoding="utf-8")
            flagged = set(re.findall(r"^- `([^`]+)`.*!kcl", index, re.M))
            assert flagged == outliers, f"index flags {sorted(flagged)} but files say {sorted(outliers)}"
            self.notes.append(
                f"{len(outliers)} aquarium samples use sketch blocks but declare kclVersion 1.0 or none "
                f"({', '.join(sorted(outliers))}); kcl-examples/index.md flags them `!kcl…`."
            )
            return f"{len(dirs)} samples, {len(files)} files; {len(outliers)} without kclVersion = 2.0 are flagged in index.md: {', '.join(sorted(outliers))}"

        self.check(s, "S1", "check_skills.py gates", gates)
        self.check(s, "S2", "skill discovery (SKILL.md under .agents/skills)", discovery)
        self.check(s, "S3", "cold-read task budgets <= 8k tokens", cold_read)
        self.check(s, "S4", "sample corpus extracted intact", corpus_files)

    # ------------------------------------------------------------------ cli
    def cli(self) -> None:
        s = self.section("CLI: zoo kcl")
        out = OUT / "cli"
        shutil.rmtree(out, ignore_errors=True)
        (out / "step-a").mkdir(parents=True)
        (out / "step-b").mkdir(parents=True)
        (out / "stl").mkdir(parents=True)

        def fmt() -> str:
            r = run(["zoo", "kcl", "format", str(COUPON)])
            assert r.returncode == 0, r.stderr
            assert r.stdout.rstrip() == COUPON.read_text().rstrip(), "formatter changed the coupon"
            return "formatted output identical to committed source"

        def lint_ok() -> str:
            r = run(["zoo", "kcl", "lint", str(COUPON)])
            assert r.returncode == 0 and not r.stdout.strip(), r.stdout + r.stderr
            return "no lint findings"

        def lint_broken() -> str:
            r = run(["zoo", "kcl", "lint", str(BROKEN)])
            assert r.returncode != 0, "lint accepted `var width`"
            msg = r.stdout + r.stderr
            m = re.search(r'message: "([^"]+)"', msg)
            assert m and "var" in m.group(1), msg[:200]
            return f"exit {r.returncode}: {m.group(1)[:90]}"

        def analyze() -> str:
            r = run(
                [
                    "zoo",
                    "kcl",
                    "analyze",
                    str(COUPON),
                    "--format",
                    "json",
                    "--volume-output-unit",
                    "mm3",
                    "--center-of-mass-output-unit",
                    "mm",
                    "--surface-area-output-unit",
                    "mm2",
                ],
                engine=True,
            )
            assert r.returncode == 0, r.stderr or r.stdout
            d = json.loads(r.stdout)
            v, a = d["volume"]["volume"], d["surface_area"]["surface_area"]
            c = d["center_of_mass"]["center_of_mass"]
            dims = d["bounding_box"]["dimensions"]
            assert approx(v, COUPON_VOLUME, 1e-4), f"volume {v}"
            assert approx(a, COUPON_AREA, 1e-4), f"area {a}"
            assert all(abs(c[k] - e) < 0.01 for k, e in zip("xyz", (30, 20, 2))), f"com {c}"
            assert all(abs(dims[k] - e) < 0.01 for k, e in zip("xyz", (60, 40, 4))), f"bbox {dims}"
            return f"volume {v:.2f} mm3, area {a:.1f} mm2, com ({c['x']:.2f}, {c['y']:.2f}, {c['z']:.2f}), bbox 60x40x4"

        def export_step() -> str:
            for d in ("step-a", "step-b"):
                r = run(
                    ["zoo", "kcl", "export", "--output-format=step", "--deterministic", str(COUPON), str(out / d)],
                    engine=True,
                )
                assert r.returncode == 0, r.stderr or r.stdout
            a, b = out / "step-a" / "output.step", out / "step-b" / "output.step"
            assert a.exists() and b.exists(), "output.step missing"
            text = a.read_text(errors="replace")
            assert text.startswith("ISO-10303-21"), text[:20]
            assert sha256(a) == sha256(b), "two deterministic exports differ"
            topo = {
                k: len(re.findall(rf"\b{k}\(", text))
                for k in ("MANIFOLD_SOLID_BREP", "ADVANCED_FACE", "EDGE_CURVE", "VERTEX_POINT")
            }
            assert (topo["MANIFOLD_SOLID_BREP"], topo["ADVANCED_FACE"], topo["EDGE_CURVE"], topo["VERTEX_POINT"]) == (
                1,
                6,
                12,
                8,
            ), topo
            return (
                f"{a.stat().st_size} bytes, identical sha256 across two exports ({sha256(a)[:12]}); "
                f"B-rep topology 1 solid / 6 faces / 12 edges / 8 vertices"
            )

        def export_stl() -> str:
            r = run(["zoo", "kcl", "export", "--output-format=stl", str(COUPON), str(out / "stl")], engine=True)
            assert r.returncode == 0, r.stderr or r.stdout
            tris = read_stl(out / "stl" / "output.stl")
            vol, bbox, manifold = mesh_stats(tris)
            assert manifold, "mesh is not a closed manifold (edge mismatch)"
            assert approx(vol, COUPON_VOLUME, 5e-3), f"mesh volume {vol}"
            lo, hi = bbox
            assert all(abs(x) < 1e-3 for x in lo) and all(abs(h - e) < 1e-3 for h, e in zip(hi, (60, 40, 4))), (
                f"bbox {bbox}"
            )
            return f"{len(tris)} triangles, closed manifold, mesh volume {vol:.2f} mm3 (independent stdlib check)"

        def snapshot() -> str:
            png = out / "coupon-four-ways.png"
            r = run(["zoo", "kcl", "snapshot", "--angle=four-ways", str(COUPON), str(png)], engine=True)
            assert r.returncode == 0, r.stderr or r.stdout
            w, h = png_size(png)
            assert w >= 512 and h >= 512, f"{w}x{h}"
            return f"{rel(png)} {w}x{h}"

        def bracket() -> str:
            r = run(
                [
                    "zoo",
                    "kcl",
                    "analyze",
                    str(BRACKET.parent),
                    "--format",
                    "json",
                    "--volume-output-unit",
                    "mm3",
                    "--center-of-mass-output-unit",
                    "mm",
                ],
                engine=True,
            )
            assert r.returncode == 0, r.stderr or r.stdout
            d = json.loads(r.stdout)
            v = d["volume"]["volume"]
            c = d["center_of_mass"]["center_of_mass"]
            assert approx(v, BRACKET_VOLUME, 1e-3), f"volume {v:.2f} vs analytic {BRACKET_VOLUME:.2f}"
            assert all(abs(c[k] - e) < 0.05 for k, e in zip("xyz", (40, 25, 3))), f"com {c}"
            self.notes.append(
                "hole::hole/holes `cutAt` is read in the target face's local frame: on the END face of an XY "
                "extrusion `[a, b]` lands at global `(b, a)`. smoke/parts/bracket encodes this; a future engine "
                "change would show up here as a volume/centre-of-mass mismatch."
            )
            return f"volume {v:.2f} mm3 vs analytic {BRACKET_VOLUME:.2f} ({(v / BRACKET_VOLUME - 1) * 100:+.3f}%), com centred: tags, fillet, hole::holes, assert all exercised"

        def sample() -> str:
            r = run(["zoo", "kcl", "volume", str(MULTI_FILE_SAMPLE), "-f", "json", "--output-unit", "mm3"], engine=True)
            assert r.returncode == 0, r.stderr or r.stdout
            v = json.loads(r.stdout)["volume"]
            assert v > 0, r.stdout
            n = len(list(MULTI_FILE_SAMPLE.glob("*.kcl")))
            return f"{MULTI_FILE_SAMPLE.name} ({n} files, imports parameters.kcl) volume {v:.0f} mm3"

        self.check(s, "C1", "format is idempotent on the coupon", fmt)
        self.check(s, "C2", "lint passes on the coupon", lint_ok)
        self.check(s, "C3", "lint rejects `var width` with a readable error", lint_broken)
        # Sequential on purpose: the hosted engine serialises one user's requests, so
        # concurrency only blurs per-check timings.
        self.check(s, "C4", "analyze coupon matches analytic volume/area/com/bbox", analyze)
        self.check(s, "C5", "export STEP is deterministic with exact B-rep topology", export_step)
        self.check(s, "C6", "export STL passes independent mesh check", export_stl)
        self.check(s, "C7", "snapshot four-ways PNG", snapshot)
        self.check(s, "C8", "bracket (skill patterns) matches analytic volume", bracket)
        self.check(s, "C9", "multi-file skill sample executes as a project", sample)

    # ------------------------------------------------------------------ api
    def api(self) -> None:
        s = self.section("REST API via CLI")

        def user() -> str:
            r = run(["zoo", "api", "/user"])
            assert r.returncode == 0, r.stderr
            d = json.loads(r.stdout)
            return f"GET /user -> {d.get('email')}"

        def ping() -> str:
            r = run(["zoo", "api", "/ping"])
            assert r.returncode == 0, r.stderr
            assert "pong" in r.stdout.lower(), r.stdout
            return "GET /ping -> pong"

        def file_volume() -> str:
            step = OUT / "cli" / "step-a" / "output.step"
            if not step.exists():
                r = run(
                    ["zoo", "kcl", "export", "--output-format=step", "--deterministic", str(COUPON), str(step.parent)],
                    engine=True,
                )
                assert r.returncode == 0, r.stderr
            r = run(["zoo", "file", "volume", str(step), "-f", "json", "--output-unit", "mm3"], engine=True)
            assert r.returncode == 0, r.stderr or r.stdout
            d = json.loads(r.stdout)
            assert d.get("status") == "completed" and approx(d["volume"], COUPON_VOLUME, 1e-4), r.stdout[:200]
            return f"POST /file/volume on exported STEP -> {d['volume']:.2f} mm3 (round-trip agrees with KCL)"

        self.check(s, "A1", "authenticated GET /user", user)
        self.check(s, "A2", "GET /ping", ping)
        self.check(s, "A3", "file API volume of exported STEP", file_volume)

    # ------------------------------------------------------------------ mcp
    def mcp(self) -> None:
        s = self.section("MCP server (uvx zoo-mcp)")
        if not self.token:
            self.check(
                s, "M0", "MCP prerequisites", lambda: (_ for _ in ()).throw(AssertionError("no API token (see E3)"))
            )
            return
        out = OUT / "mcp"
        shutil.rmtree(out, ignore_errors=True)
        out.mkdir(parents=True)
        client = McpClient(self.token)
        try:

            def init() -> str:
                info = client.initialize()
                return f"{info.get('name')} v{info.get('version')}, protocol {client.protocol}"

            def tools() -> str:
                names = sorted(client.list_tools())
                doc = (ZOO_SKILLS / "zoo-tooling" / "mcp.md").read_text(encoding="utf-8")
                documented = sorted(set(re.findall(r"^- `([a-z_0-9]+)\(", doc, re.M)))
                assert names == documented, (
                    f"live {len(names)} vs skill {len(documented)}; diff {sorted(set(names) ^ set(documented))[:6]}"
                )
                return f"{len(names)} tools, identical to zoo-tooling/mcp.md"

            def fmt() -> str:
                res = client.call("format_kcl", {"kcl_code": COUPON.read_text()})
                assert res["text"].rstrip() == COUPON.read_text().rstrip(), "format_kcl changed the coupon"
                return "format_kcl returns the source unchanged"

            def lint() -> str:
                res = client.call("lint_and_fix_kcl", {"kcl_code": COUPON.read_text()})
                fixed, messages = res["structured"]
                unfixed = [m for m in messages if "fixed" not in m.lower()]
                assert fixed.rstrip() == COUPON.read_text().rstrip() and not unfixed, f"unfixed: {unfixed}"
                return f"lint_and_fix_kcl: source unchanged, {'; '.join(messages) or 'no messages'}"

            def mock_ok() -> str:
                ok, msg = client.call("mock_execute_kcl", {"kcl_path": str(COUPON)})["structured"]
                assert ok is True, msg
                return f"coupon mock-executes: {msg}"

            def mock_broken() -> str:
                ok, msg = client.call("mock_execute_kcl", {"kcl_path": str(BROKEN)})["structured"]
                assert ok is False and "var" in msg, msg
                return f"broken.kcl rejected: {kcl_error_line(msg)}"

            def mock_assert() -> str:
                thin = BRACKET.read_text().replace("plateThickness = 6mm", "plateThickness = 2mm")
                ok, msg = client.call("mock_execute_kcl", {"kcl_code": thin})["structured"]
                assert ok is False and "plate too thin" in msg, msg
                return f"assert fires without the engine: {kcl_error_line(msg)}"

            def corpus() -> str:
                dirs = sorted(d for d in SAMPLES.iterdir() if d.is_dir())
                bad, needs_engine = [], []
                for d in dirs:
                    ok, msg = client.call("mock_execute_kcl", {"kcl_path": str(d)}, timeout=120)["structured"]
                    if ok is True:
                        continue
                    if "engine isn't available" in msg:
                        needs_engine.append(d.name)  # hole:: and other face queries need the engine
                    else:
                        bad.append(f"{d.name}: {msg.strip()[:80]}")
                assert not bad, f"{len(bad)} samples fail mock execution: {bad[:3]}"
                self.notes.append(
                    f"mock_execute_kcl cannot evaluate face-dependent std code: {len(needs_engine)} samples using "
                    f'hole:: ({", ".join(needs_engine)}) report "engine isn\'t available" and need execute_kcl.'
                )
                return (
                    f"{len(dirs) - len(needs_engine)}/{len(dirs)} mock-execute locally; "
                    f"{len(needs_engine)} need the engine (hole::): {', '.join(needs_engine)}"
                )

            def props() -> str:
                res = client.call(
                    "calculate_kcl_physical_properties",
                    {"kcl_path": str(COUPON), "unit_volume": "mm3", "unit_length": "mm"},
                    engine=True,
                )
                d = res["structured"]
                assert approx(d["volume"], COUPON_VOLUME, 1e-4), d
                return f"volume {d['volume']:.2f} mm3, com ({d['center_of_mass']['x']:.1f}, {d['center_of_mass']['y']:.1f}, {d['center_of_mass']['z']:.1f})"

            def docs() -> str:
                d = client.call("search_kcl_docs", {"query": "fillet", "max_results": 3})["text"]
                assert "std-solid-fillet" in d, d[:200]
                sm = client.call("search_kcl_samples", {"query": "gear rack", "max_results": 2})["text"]
                assert "gear-rack" in sm, sm[:200]
                return "search_kcl_docs('fillet') -> std-solid-fillet; search_kcl_samples('gear rack') -> gear-rack"

            self.check(s, "M1", "initialize handshake", init)
            self.check(s, "M2", "tools/list matches skill inventory", tools)
            self.check(s, "M3", "format_kcl", fmt)
            self.check(s, "M4", "lint_and_fix_kcl (code string, no writes)", lint)
            self.check(s, "M5", "mock_execute_kcl coupon", mock_ok)
            self.check(s, "M6", "mock_execute_kcl surfaces `var` error", mock_broken)
            self.check(s, "M7", "assert() fails fast under mock execution", mock_assert)
            self.check(s, "M8", "skill samples mock-execute (local interpreter)", corpus)
            self.check(s, "M9", "calculate_kcl_physical_properties coupon", props)
            self.check(s, "M10", "docs and sample lookup", docs)
            if "e2e" in self.wanted:
                self.e2e(client)
        finally:
            client.close()

    # ------------------------------------------------------------------ e2e
    def e2e(self, client: "McpClient") -> None:
        """The bounded agent loop from the primer, driven entirely through MCP tools."""
        s = self.section("Agent loop via MCP (bracket)")
        out = OUT / "e2e"
        shutil.rmtree(out, ignore_errors=True)
        out.mkdir(parents=True)
        code = BRACKET.read_text()
        state: dict = {}

        def check_source() -> str:
            assert client.call("format_kcl", {"kcl_code": code})["text"].rstrip() == code.rstrip(), (
                "format changed the bracket"
            )
            fixed, msgs = client.call("lint_and_fix_kcl", {"kcl_code": code})["structured"]
            assert fixed.rstrip() == code.rstrip(), f"lint wants changes: {msgs}"
            ok, msg = client.call("mock_execute_kcl", {"kcl_code": code})["structured"]
            assert ok is False and "engine isn't available" in msg, "expected mock to defer hole:: to the engine"
            return "format + lint clean; mock defers hole:: to the engine as documented"

        def execute() -> str:
            sid = client.call("start_modeling_session", {})["structured"]
            state["sid"] = sid
            res = client.call(
                "execute_kcl", {"kcl_path": str(BRACKET.parent), "session_id": sid}, engine=True, timeout=180
            )
            result = res["structured"] if isinstance(res["structured"], dict) else {}
            assert result.get("ok") is True, res["text"][:200]
            graph = Path(result.get("path_artifact_graph", ""))
            assert graph.exists() and graph.stat().st_size > 0, f"artifact graph missing: {graph}"
            return f"session {sid[:8]}, artifact graph {graph.stat().st_size // 1024} KB"

        def look() -> str:
            client.call(
                "snapshot",
                {
                    "session_id": state["sid"],
                    "camera_view": ["front", "top", "right", "isometric"],
                    "output_path": str(out),
                },
                engine=True,
                timeout=180,
            )
            images = sorted(p for p in out.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
            assert images, "no snapshot written"
            head = images[0].read_bytes()[:8]
            assert head[:2] == b"\xff\xd8" or head == b"\x89PNG\r\n\x1a\n", f"{images[0].name} is not an image"
            return f"4-view composite {rel(images[0])}"

        def measure() -> str:
            d = client.call(
                "calculate_kcl_physical_properties",
                {"kcl_path": str(BRACKET.parent), "unit_volume": "mm3", "unit_length": "mm"},
                engine=True,
                timeout=180,
            )["structured"]
            assert approx(d["volume"], BRACKET_VOLUME, 1e-3), (
                f"volume {d['volume']:.2f} vs analytic {BRACKET_VOLUME:.2f}"
            )
            c = d["center_of_mass"]
            assert all(abs(c[k] - e) < 0.05 for k, e in zip("xyz", (40, 25, 3))), f"com {c}"
            return f"volume {d['volume']:.2f} mm3 ({(d['volume'] / BRACKET_VOLUME - 1) * 100:+.3f}% vs analytic), com centred"

        def export_step() -> str:
            step = out / "bracket.step"
            client.call(
                "export_kcl",
                {"kcl_path": str(BRACKET.parent), "export_path": str(step), "export_format": "step"},
                engine=True,
                timeout=180,
            )
            assert step.exists(), "STEP not written"
            state["step"] = step
            text = step.read_text(errors="replace")
            faces = len(re.findall(r"\bADVANCED_FACE\(", text))
            # 6 plate faces + 4 fillet faces + 4 holes, each hole as two half-cylinder faces.
            assert text.startswith("ISO-10303-21") and faces == 18, f"faces {faces} (expected 18)"
            return f"{rel(step)} {step.stat().st_size // 1024} KB, 18 B-rep faces (6 plate + 4 fillets + 4 holes x 2 half-cylinders)"

        def convert() -> str:
            stl = out / "bracket.stl"
            client.call(
                "convert_cad_file",
                {"input_file": str(state["step"]), "export_path": str(stl), "export_format": "stl"},
                engine=True,
                timeout=180,
            )
            assert stl.exists(), "STL not written"
            tris = read_stl(stl)
            vol, bbox, manifold = mesh_stats(tris)
            assert manifold, "mesh not closed"
            assert approx(vol, BRACKET_VOLUME, 1e-2), f"mesh volume {vol:.1f}"
            lo, hi = bbox
            assert all(abs(h - e) < 0.01 for h, e in zip(hi, (80, 50, 6))), f"bbox {bbox}"
            state["stl"] = stl
            return f"STEP -> STL: {len(tris)} triangles, closed, mesh volume {vol:.1f} mm3 ({(vol / BRACKET_VOLUME - 1) * 100:+.2f}%, tessellation)"

        def cad_props() -> str:
            d = client.call(
                "calculate_cad_physical_properties",
                {
                    "input_file": str(state["step"]),
                    "unit_length": "mm",
                    "unit_mass": "g",
                    "unit_density": "kg:m3",
                    "density": 2700.0,
                    "unit_area": "mm2",
                    "unit_volume": "mm3",
                },
                engine=True,
                timeout=180,
            )["structured"]
            assert approx(d["volume"], BRACKET_VOLUME, 1e-3), d
            expected_mass_g = BRACKET_VOLUME * 2700 / 1e6
            assert approx(d["mass"], expected_mass_g, 2e-3), f"mass {d['mass']} g vs {expected_mass_g:.2f} g"
            return f"exported STEP re-measured: volume {d['volume']:.2f} mm3, mass {d['mass']:.2f} g at 2700 kg/m3 (aluminium)"

        def stop() -> str:
            client.call("stop_modeling_session", {"session_id": state["sid"]})
            assert client.call("get_modeling_sessions", {})["structured"] == [], "session still listed"
            return "session closed, none left open"

        self.check(s, "L1", "source checks: format, lint, mock", check_source)
        self.check(s, "L2", "execute in a modeling session", execute)
        self.check(s, "L3", "inspect: 4-view snapshot", look)
        self.check(s, "L4", "measure against the analytic contract", measure)
        self.check(s, "L5", "export STEP (exact B-rep)", export_step)
        self.check(s, "L6", "convert STEP -> STL and check the mesh independently", convert)
        self.check(s, "L7", "re-measure the exported file with a real density", cad_props)
        self.check(s, "L8", "clean up the session", stop)

    # ---------------------------------------------------------------- codex
    def codex(self) -> None:
        """Cursor -> codex_exec.py -> Codex (GPT-6 Astra): a round trip, then a real CAD task and a follow-up."""
        s = self.section("Codex worker (GPT-6 Astra)")
        out = OUT / "codex"
        for d in ("X3", "X4", "X5", "plate"):  # leave other runs under smoke/out/codex alone
            shutil.rmtree(out / d, ignore_errors=True)
        plate = out / "plate"
        plate.mkdir(parents=True)
        state: dict = {}

        def dispatch(name: str, prompt: str, *flags: str, timeout: float) -> dict:
            r = run(
                [
                    sys.executable,
                    str(CODEX_EXEC),
                    "--run-dir",
                    str(out / name),
                    "--timeout",
                    str(timeout),
                    *flags,
                    prompt,
                ],
                timeout=timeout + 60,
            )
            events = [
                json.loads(l)
                for l in (out / name / "events.jsonl").read_text(encoding="utf-8").splitlines()
                if l.strip()
            ]
            d = {"thread": "", "usage": {}, "commands": 0, "seconds": 0, "events": events}
            for e in events:
                if e.get("type") == "thread.started":
                    d["thread"] = e.get("thread_id", "")
                elif e.get("type") == "turn.completed":
                    d["usage"] = e.get("usage", {})
                elif e.get("type") == "item.completed" and e["item"].get("type") == "command_execution":
                    d["commands"] += 1
                    if "zoo kcl" in e["item"].get("command", ""):
                        count_engine_call()  # Codex's own engine calls are billed too
            m = re.search(r"seconds=(\d+)", r.stdout)
            d["seconds"] = int(m.group(1)) if m else 0
            assert r.returncode == 0, f"codex_exec.py exit {r.returncode}: {(r.stdout + r.stderr)[-400:]}"
            d["result"] = (out / name / "result.md").read_text(encoding="utf-8")
            return d

        def usage(d: dict) -> str:
            u = d["usage"]
            return (
                f"{d['commands']} commands, {d['seconds']}s, tokens in {u.get('input_tokens', 0)} "
                f"(cached {u.get('cached_input_tokens', 0)}) out {u.get('output_tokens', 0)}"
            )

        def quotes(text: str, expected: float) -> bool:
            return any(approx(float(n), expected, 1e-3) for n in re.findall(r"\d+\.\d+|\d+", text))

        def analyze() -> tuple[float, dict, dict]:
            r = run(
                [
                    "zoo",
                    "kcl",
                    "analyze",
                    str(plate),
                    "--format",
                    "json",
                    "--volume-output-unit",
                    "mm3",
                    "--center-of-mass-output-unit",
                    "mm",
                ],
                engine=True,
            )
            assert r.returncode == 0, r.stderr or r.stdout
            d = json.loads(r.stdout)
            return d["volume"]["volume"], d["center_of_mass"]["center_of_mass"], d["bounding_box"]["dimensions"]

        def cli() -> str:
            assert shutil.which("codex"), "codex CLI not on PATH"
            r = run(["codex", "--version"])
            m = re.search(r"codex-cli (\S+)", r.stdout)
            assert m, r.stdout + r.stderr
            return f"codex-cli {m.group(1)}"

        def doctor() -> str:
            r = run(["codex", "doctor", "--json"], timeout=120)
            d = json.loads(r.stdout)
            cfg = d["checks"]["config.load"]["details"]
            auth = d["checks"]["auth.credentials"]
            assert d["overallStatus"] != "fail", d["overallStatus"]
            assert cfg["model"] == "gpt-6-astra" and cfg["model provider"] == "openai", (
                f"{cfg['model']} via {cfg['model provider']}"
            )
            assert auth["status"] == "ok", auth["summary"]
            return f"{cfg['model']} via {cfg['model provider']}, auth {auth['details']['stored auth mode']}, doctor {d['overallStatus']}"

        def roundtrip() -> str:
            d = dispatch(
                "X3",
                "Reply with exactly the text OPENCAD-OK and nothing else. Do not run any commands.",
                "--read-only",
                timeout=300,
            )
            assert "OPENCAD-OK" in d["result"], d["result"][:200]
            assert d["thread"], "no thread.started event"
            rollouts = list((Path.home() / ".codex" / "sessions").rglob(f"rollout-*-{d['thread']}.jsonl"))
            effort = "rollout not found"
            if rollouts:
                ctx = [
                    json.loads(l) for l in rollouts[0].read_text(encoding="utf-8").splitlines() if '"turn_context"' in l
                ]
                effort = ctx[0]["payload"].get("effort") if ctx else "no turn_context"
                assert effort == "max", f"reasoning effort {effort}"
            return f"thread {d['thread'][:8]} answered OPENCAD-OK, effort {effort}; {usage(d)}"

        def cad() -> str:
            brief = (
                f"Create a KCL 2 part at {plate}/main.kcl. Your working directory is {plate} and it is the only place you may write.\n"
                "Part: a rectangular plate 40 mm (X) by 30 mm (Y) by 5 mm thick (Z), lower-left corner at the origin, sketched on the XY "
                "plane and extruded in +Z, with one 10 mm diameter through-hole centred at (20, 15).\n"
                "Start the file with @settings(defaultLengthUnit = mm, kclVersion = 2.0). Read the backends/zoo/kcl-docs and backends/zoo/zoo-tooling skills first.\n"
                f"Verify with `zoo kcl analyze {plate} --format json --volume-output-unit mm3 --center-of-mass-output-unit mm` "
                f"(network is enabled) and report the measured volume, bounding box and centre of mass against the analytic volume "
                f"{PLATE_VOLUME:.2f} mm3, bounding box 40 x 30 x 5 mm and centre of mass (20, 15, 2.5)."
            )
            d = dispatch("X4", brief, "--cd", str(plate), timeout=1500)
            state["thread"] = d["thread"]
            assert (plate / "main.kcl").exists(), "Codex did not write main.kcl"
            v, c, dims = analyze()
            assert approx(v, PLATE_VOLUME, 1e-3), f"volume {v:.2f} vs analytic {PLATE_VOLUME:.2f}"
            assert all(abs(dims[k] - e) < 0.01 for k, e in zip("xyz", (40, 30, 5))), f"bbox {dims}"
            assert all(abs(c[k] - e) < 0.05 for k, e in zip("xyz", (20, 15, 2.5))), f"com {c}"
            assert quotes(d["result"], v), "Codex's report does not quote the measured volume"
            return (
                f"main.kcl written and self-verified; independent analyze: volume {v:.2f} mm3 "
                f"({(v / PLATE_VOLUME - 1) * 100:+.3f}% vs analytic), bbox 40x30x5, com centred; {usage(d)}"
            )

        def followup() -> str:
            d = dispatch(
                "X5",
                f"In the same file {plate}/main.kcl change the through-hole diameter to 12 mm, keep everything else, "
                f"re-run the same zoo kcl analyze command and report the new measured volume against the analytic "
                f"{PLATE_VOLUME_12:.2f} mm3.",
                "--resume",
                state["thread"],
                timeout=1200,
            )
            assert d["thread"] in ("", state["thread"]), f"resume started thread {d['thread']}"
            v, _, _ = analyze()
            assert approx(v, PLATE_VOLUME_12, 1e-3), f"volume {v:.2f} vs analytic {PLATE_VOLUME_12:.2f}"
            return f"thread {state['thread'][:8]} resumed; volume {v:.2f} mm3 ({(v / PLATE_VOLUME_12 - 1) * 100:+.3f}% vs analytic); {usage(d)}"

        self.check(s, "X1", "codex CLI present", cli)
        self.check(s, "X2", "codex doctor: gpt-6-astra via openai, ChatGPT auth", doctor)
        self.check(s, "X3", "read-only round trip at max effort", roundtrip)
        self.check(s, "X4", "CAD task: plate with hole, verified independently", cad)
        self.check(s, "X5", "resume the thread: change the hole, re-verify", followup)

    # --------------------------------------------------------------- studio
    def studio(self) -> None:
        s = self.section("Zoo Design Studio")

        def open_app() -> str:
            r = run(["zoo", "app", str(BRACKET.parent)], timeout=60)
            assert r.returncode == 0, r.stderr or r.stdout
            return f"opened {rel(BRACKET.parent)} in Zoo Design Studio (visual check: 4 holes, 4 rounded corners)"

        self.check(s, "D1", "zoo app opens the bracket project", open_app)

    # --------------------------------------------------------------- report
    def report(self, started: datetime, seconds: float) -> int:
        total = sum(len(s.checks) for s in self.sections)
        failed = [c for s in self.sections for c in s.checks if c.status == "FAIL"]
        lines = [
            "# Smoke test report",
            "",
            f"Run: {started.strftime('%Y-%m-%d %H:%M:%S UTC')} on {os.uname().nodename}, {seconds:.0f}s, "
            f"{total - len(failed)}/{total} checks passed, {ENGINE_CALLS} hosted engine executions (billed as API usage).",
            "",
        ]
        for s in self.sections:
            lines += [f"## {s.name}", "", "| id | check | status | time | evidence |", "|---|---|---|---|---|"]
            for c in s.checks:
                ev = c.evidence.replace("|", "\\|").replace("\n", " ")
                lines.append(f"| {c.id} | {c.name} | {c.status} | {c.seconds:.1f}s | {ev} |")
            lines.append("")
        if self.notes:
            lines += ["## Notes", ""] + [f"- {n}" for n in self.notes] + [""]
        (SMOKE / "report.md").write_text("\n".join(lines), encoding="utf-8")
        print(
            f"\n{total - len(failed)}/{total} passed in {seconds:.0f}s, {ENGINE_CALLS} engine executions. Report: {rel(SMOKE / 'report.md')}"
        )
        for c in failed:
            print(f"  FAIL {c.id} {c.name}: {c.evidence[:200]}")
        return 1 if failed else 0


# ---------------------------------------------------------------- helpers


def kcl_error_line(msg: str) -> str:
    """The `× ...` message of a KCL diagnostic (continuation lines joined, frame dropped)."""
    msg = msg.replace("\\n", "\n").replace("\\'", "'")  # tool returns a repr()-escaped string
    m = re.search(r"×\s*(.+?)(?:\n\s*╭|\Z)", msg, re.S)
    text = m.group(1) if m else msg
    return " ".join(text.replace("│", " ").split())[:140]


def read_stl(path: Path) -> list[tuple[tuple[float, float, float], ...]]:
    data = path.read_bytes()
    if data[:5] == b"solid" and b"facet" in data[:400]:
        nums = re.findall(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)
        verts = [tuple(float(x) for x in v) for v in nums]
        return [tuple(verts[i : i + 3]) for i in range(0, len(verts) - 2, 3)]
    n = struct.unpack_from("<I", data, 80)[0]
    tris = []
    for i in range(n):
        off = 84 + i * 50 + 12
        vals = struct.unpack_from("<9f", data, off)
        tris.append((vals[0:3], vals[3:6], vals[6:9]))
    return tris


def mesh_stats(tris) -> tuple[float, tuple[tuple[float, ...], tuple[float, ...]], bool]:
    vol = 0.0
    edges: dict[tuple, int] = {}
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    key = lambda v: tuple(round(x, 5) for x in v)  # noqa: E731
    for a, b, c in tris:
        vol += (
            a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])
        ) / 6
        for v in (a, b, c):
            for i in range(3):
                lo[i] = min(lo[i], v[i])
                hi[i] = max(hi[i], v[i])
        ka, kb, kc = key(a), key(b), key(c)
        for e in ((ka, kb), (kb, kc), (kc, ka)):
            edges[e] = edges.get(e, 0) + 1
    manifold = all(count == 1 and (e[1], e[0]) in edges for e, count in edges.items())
    return abs(vol), (tuple(lo), tuple(hi)), manifold


def png_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", f"{path.name} is not a PNG"
    w, h = struct.unpack(">II", data[16:24])
    return w, h


class McpClient:
    """Minimal MCP stdio client: newline-delimited JSON-RPC over a `uvx zoo-mcp` subprocess."""

    def __init__(self, token: str) -> None:
        env = dict(os.environ, ZOO_API_TOKEN=token, PYTHONWARNINGS="ignore")
        self.proc = subprocess.Popen(
            ["uvx", "zoo-mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
            cwd=ROOT,
        )
        self.stderr: list[str] = []
        threading.Thread(target=self._drain, daemon=True).start()
        self.next_id = 1
        self.protocol = ""

    def _drain(self) -> None:
        for line in self.proc.stderr:
            self.stderr.append(line)

    def _send(self, obj: dict) -> None:
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _request(self, method: str, params: dict, timeout: float) -> dict:
        rid = self.next_id
        self.next_id += 1
        self._send({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        deadline = time.time() + timeout
        while time.time() < deadline:
            line = self.proc.stdout.readline()
            if not line:
                if self.proc.poll() is not None:
                    raise RuntimeError("MCP server exited: " + "".join(self.stderr[-5:])[-300:])
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError:
                continue
            if msg.get("id") == rid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg["result"]
        raise TimeoutError(f"{method} timed out after {timeout}s")

    def initialize(self) -> dict:
        res = self._request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "opencad-smoke", "version": "0.1"},
            },
            120,
        )
        self.protocol = res.get("protocolVersion", "")
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        return res.get("serverInfo", {})

    def list_tools(self) -> list[str]:
        return [t["name"] for t in self._request("tools/list", {}, 60)["tools"]]

    def call(self, name: str, arguments: dict, timeout: float = 90, engine: bool = False) -> dict:
        if engine:
            count_engine_call()
        res = self._request("tools/call", {"name": name, "arguments": arguments}, timeout)
        text = "\n".join(c.get("text", "") for c in res.get("content", []) if c.get("type") == "text")
        if res.get("isError"):
            raise RuntimeError(f"{name} returned isError: {text[:300]}")
        structured = (
            res.get("structuredContent", {}).get("result") if isinstance(res.get("structuredContent"), dict) else None
        )
        return {"text": text, "structured": structured, "raw": res}

    def close(self) -> None:
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument(
        "--sections",
        default="env,skills,cli,api,mcp,e2e,codex",
        help="comma list from env,skills,cli,api,mcp,e2e,codex (e2e runs inside the mcp server)",
    )
    ap.add_argument("--studio", action="store_true", help="open the bracket project in Zoo Design Studio at the end")
    args = ap.parse_args()
    wanted = [s.strip() for s in args.sections.split(",") if s.strip()]

    OUT.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    t0 = time.time()
    r = Runner(wanted)
    steps = {"env": r.env, "skills": r.skills, "cli": r.cli, "api": r.api, "mcp": r.mcp, "codex": r.codex}
    for name in wanted:
        if name == "e2e":
            continue  # driven from within the mcp section (shares the server process)
        print(f"\n== {name} ==")
        steps[name]()
    if args.studio:
        print("\n== studio ==")
        r.studio()
    return r.report(started, time.time() - t0)


if __name__ == "__main__":
    sys.exit(main())
