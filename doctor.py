#!/usr/bin/env python3
"""Purple environment doctor.

Run this FIRST on your PC, before installing anything heavy:

    python doctor.py

It uses only the Python standard library, so it works on a bare install. It checks
everything Purple needs (Python, GPU/CUDA, RAM, disk, Ollama, PostgreSQL, ffmpeg)
and prints a report. Copy the whole report back to me and I'll tell you exactly
what to fix.
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import urllib.request

OK, WARN, FAIL, INFO = "[ OK ]", "[WARN]", "[FAIL]", "[INFO]"
_results: list[tuple[str, str]] = []


def line(status: str, msg: str) -> None:
    _results.append((status, msg))
    print(f"{status}  {msg}")


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return out.returncode, (out.stdout or "") + (out.stderr or "")
    except Exception as exc:  # noqa: BLE001
        return 1, str(exc)


def check_python() -> None:
    section("Python")
    v = sys.version_info
    msg = f"Python {v.major}.{v.minor}.{v.micro} ({platform.python_implementation()})"
    if (v.major, v.minor) >= (3, 12):
        line(OK, msg)
    elif (v.major, v.minor) >= (3, 10):
        line(WARN, msg + " — 3.12 recommended")
    else:
        line(FAIL, msg + " — need Python 3.10+ (3.12 recommended)")


def check_system() -> None:
    section("System")
    line(INFO, f"OS: {platform.platform()}")
    line(INFO, f"CPU: {platform.processor() or 'unknown'}")
    # RAM
    ram_gb = None
    try:
        if os.name == "nt":
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            stat = MEMORYSTATUSEX()
            stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            ram_gb = stat.ullTotalPhys / (1024**3)
        else:
            ram_gb = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / (1024**3)
    except Exception:  # noqa: BLE001
        pass
    if ram_gb is None:
        line(WARN, "RAM: could not detect")
    elif ram_gb >= 30:
        line(OK, f"RAM: {ram_gb:.0f} GB")
    else:
        line(WARN, f"RAM: {ram_gb:.0f} GB — 32 GB+ recommended (16 GB is tight with model+Whisper+DB)")


def check_disk() -> None:
    section("Disk")
    # Check the drive Purple lives on
    target = os.path.abspath(os.path.dirname(__file__)) or "."
    try:
        usage = shutil.disk_usage(target)
        free_gb = usage.free / (1024**3)
        msg = f"Free space on Purple's drive: {free_gb:.0f} GB"
        if free_gb >= 50:
            line(OK, msg)
        elif free_gb >= 20:
            line(WARN, msg + " — models are large; 50 GB+ is comfortable")
        else:
            line(FAIL, msg + " — likely too little for models")
    except Exception as exc:  # noqa: BLE001
        line(WARN, f"Disk: could not detect ({exc})")


def check_gpu() -> None:
    section("GPU / CUDA")
    if not shutil.which("nvidia-smi"):
        line(WARN, "nvidia-smi not found — no NVIDIA GPU detected, or driver not installed. "
                   "Whisper/LLM will fall back to CPU (slow). Tell me your GPU if it's AMD/Intel.")
        return
    code, out = _run([
        "nvidia-smi",
        "--query-gpu=name,memory.total,driver_version",
        "--format=csv,noheader",
    ])
    if code == 0 and out.strip():
        for gpu in out.strip().splitlines():
            line(OK, f"GPU: {gpu.strip()}")
    else:
        line(WARN, f"nvidia-smi present but query failed: {out.strip()[:200]}")


def check_ffmpeg() -> None:
    section("ffmpeg (needed by Whisper)")
    if shutil.which("ffmpeg"):
        line(OK, "ffmpeg found on PATH")
    else:
        line(WARN, "ffmpeg not found — install it (winget install Gyan.FFmpeg) so STT can decode audio")


def check_ollama() -> None:
    section("Ollama (LLM runtime)")
    base = os.environ.get("PURPLE_OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    want = os.environ.get("PURPLE_LLM_MODEL", "qwen2.5:14b-instruct-q4_K_M")
    try:
        with urllib.request.urlopen(f"{base}/api/tags", timeout=4) as resp:
            data = json.loads(resp.read().decode())
        models = [m.get("name", "") for m in data.get("models", [])]
        line(OK, f"Ollama is running at {base}")
        if any(want.split(":")[0] in m for m in models):
            line(OK, f"Model available: {want}")
        else:
            line(WARN, f"Model '{want}' not pulled yet. Run:  ollama pull {want}")
        if models:
            line(INFO, "Installed models: " + ", ".join(models))
    except Exception:  # noqa: BLE001
        line(FAIL, f"Ollama not reachable at {base}. Install from ollama.com and run `ollama serve`.")


def check_postgres() -> None:
    section("PostgreSQL")
    host, port = "127.0.0.1", 5432
    dsn = os.environ.get("PURPLE_PG_DSN", "")
    if "@" in dsn and ":" in dsn.split("@")[-1]:
        try:
            hostport = dsn.split("@")[-1].split("/")[0]
            host = hostport.split(":")[0]
            port = int(hostport.split(":")[1])
        except Exception:  # noqa: BLE001
            pass
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((host, port))
        line(OK, f"PostgreSQL is accepting connections on {host}:{port}")
        line(INFO, "Make sure the 'vector' extension is enabled:  CREATE EXTENSION IF NOT EXISTS vector;")
    except Exception:  # noqa: BLE001
        line(FAIL, f"No PostgreSQL on {host}:{port}. Install it and create the 'purple' database.")
    finally:
        sock.close()


def summary() -> None:
    section("Summary")
    fails = sum(1 for s, _ in _results if s == FAIL)
    warns = sum(1 for s, _ in _results if s == WARN)
    if fails:
        print(f"{FAIL}  {fails} blocker(s) and {warns} warning(s). Fix blockers before running Purple.")
    elif warns:
        print(f"{WARN}  No blockers, {warns} warning(s). Purple should run; address warnings for best results.")
    else:
        print(f"{OK}  Environment looks ready for Purple.")
    print("\nCopy everything above and send it back so I can advise on next steps.")


def main() -> None:
    print("Purple environment doctor\n" + "=" * 40)
    check_python()
    check_system()
    check_disk()
    check_gpu()
    check_ffmpeg()
    check_ollama()
    check_postgres()
    summary()


if __name__ == "__main__":
    main()
