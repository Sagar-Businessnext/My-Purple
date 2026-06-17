"""GPU status via nvidia-smi — used by Focus mode to know when to yield the GPU.

Best-effort and never raises: no NVIDIA GPU / no nvidia-smi simply means "not busy",
so behaviour degrades gracefully on any machine.
"""

from __future__ import annotations

import shutil
import subprocess

from purple.config import settings


def _query() -> str | None:
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=utilization.gpu,memory.used",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=4,
        )
        return out.stdout if out.returncode == 0 else None
    except Exception:
        return None


def parse(output: str) -> tuple[int, int]:
    """Parse the first GPU line ('23, 4096') into (utilisation %, VRAM used MB)."""
    line = output.strip().splitlines()[0]
    util, mem = (part.strip() for part in line.split(","))
    return int(util), int(mem)


def _query_total() -> int | None:
    """Total VRAM (MB) via a separate query, so parse()/gpu_busy() stay unchanged."""
    if not shutil.which("nvidia-smi"):
        return None
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=4,
        )
        return int(out.stdout.strip().splitlines()[0]) if out.returncode == 0 else None
    except Exception:
        return None


def status() -> dict:
    out = _query()
    if not out:
        return {"available": False}
    try:
        util, mem = parse(out)
    except Exception:
        return {"available": False}
    s: dict = {"available": True, "util": util, "vram_used_mb": mem}
    total = _query_total()
    if total:
        s["vram_total_mb"] = total
        s["vram_pct"] = round(mem / total * 100)
    return s


def gpu_busy() -> bool:
    """True if the GPU looks heavily used (a game/render), so Purple should yield it."""
    s = status()
    if not s.get("available"):
        return False
    return s["util"] >= settings.gpu_busy_util or s["vram_used_mb"] >= settings.gpu_busy_vram_mb
