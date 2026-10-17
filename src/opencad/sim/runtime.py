"""Container runtime for solver images: Apple `container` first, Docker (OrbStack) as the fallback; `OPENCAD_CONTAINER`
(container|docker) pins one. Runs are foreground subprocesses with bind mounts; the image digest goes into provenance."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

RUNTIMES = ("container", "docker")


def _ok(argv: list[str]) -> bool:
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=30, check=False).returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def detect() -> str | None:
    pref = os.environ.get("OPENCAD_CONTAINER")
    for rt in ([pref] if pref else list(RUNTIMES)):
        if rt == "container" and shutil.which("container") and _ok(["container", "system", "status"]):
            return "container"
        if rt == "docker" and shutil.which("docker") and _ok(["docker", "info"]):
            return "docker"
    return None


def has_image(image: str, rt: str | None = None) -> bool:
    rt = rt or detect()
    if rt == "container":
        out = subprocess.run(["container", "image", "list", "--format", "json"], capture_output=True, text=True, check=False).stdout
        try:
            names = {f"{i.get('reference') or i.get('name')}" for i in json.loads(out or "[]")}
        except json.JSONDecodeError:
            names = set(out.split())
        return any(image == n or n.endswith(f"/{image}") or n.startswith(image) for n in names) or image in out
    if rt == "docker":
        return _ok(["docker", "image", "inspect", image])
    return False


def pull(image: str, rt: str | None = None, *, arch: str = "arm64", timeout: float = 3600) -> subprocess.CompletedProcess[str]:
    rt = rt or detect()
    if rt is None:
        raise RuntimeError("no container runtime is running (Apple `container system start`, or OrbStack/Docker)")
    argv = ["container", "image", "pull", "--arch", arch, image] if rt == "container" else ["docker", "pull", "--platform", f"linux/{arch}", image]
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, check=False)


def digest(image: str, rt: str | None = None) -> str | None:
    rt = rt or detect()
    if rt == "docker":
        r = subprocess.run(["docker", "image", "inspect", "--format", "{{index .RepoDigests 0}}", image], capture_output=True, text=True, check=False)
        return r.stdout.strip() or None
    if rt == "container":
        r = subprocess.run(["container", "image", "inspect", image], capture_output=True, text=True, check=False)
        try:
            data = json.loads(r.stdout)
            first = data[0] if isinstance(data, list) else data
            return (first.get("index") or {}).get("digest") or first.get("digest") or first.get("id")
        except (json.JSONDecodeError, AttributeError, IndexError):
            return None
    return None


def run(image: str, argv: list[str], *, mounts: dict[Path, str], workdir: str, env: dict[str, str] | None = None, timeout: float | None = None,
        cpus: int | None = None, memory: str | None = None, rt: str | None = None, log: Path | None = None) -> dict[str, Any]:
    """Run argv in the image with host dirs bind-mounted; returns {code, runtime, image, digest, seconds, log}."""
    import time

    rt = rt or detect()
    if rt is None:
        raise RuntimeError("no container runtime is running")
    cmd = [rt, "run", "--rm"]
    for host, guest in mounts.items():
        cmd += ["--mount", f"type=bind,source={Path(host).resolve()},target={guest}"] if rt == "container" else ["-v", f"{Path(host).resolve()}:{guest}"]
    cmd += ["-w", workdir]
    for k, v in (env or {}).items():
        cmd += ["-e", f"{k}={v}"]
    if cpus:
        cmd += ["-c", str(cpus)] if rt == "container" else ["--cpus", str(cpus)]
    if memory:
        cmd += ["-m", memory]
    cmd += [image, *argv]
    t0 = time.time()
    with (open(log, "w", encoding="utf-8") if log else open(os.devnull, "w")) as fh:
        try:
            p = subprocess.run(cmd, stdout=fh, stderr=subprocess.STDOUT, text=True, timeout=timeout, check=False)
            code = p.returncode
        except subprocess.TimeoutExpired:
            code = 124
    return {"code": code, "runtime": rt, "image": image, "digest": digest(image, rt), "seconds": round(time.time() - t0, 1), "log": str(log) if log else None,
            "command": " ".join(cmd)}
