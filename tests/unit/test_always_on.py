"""Always-on / Focus-mode tests: nvidia-smi parsing, GPU-busy thresholds, focus yield
logic, and the single-instance lock (all with fakes — no GPU, no real processes)."""

from __future__ import annotations

from purple import focus, gpu
from purple.config import settings
from purple.service import SingleInstance


def test_gpu_parse_first_line():
    assert gpu.parse("23, 4096\n1, 200") == (23, 4096)


def test_gpu_busy_thresholds(monkeypatch):
    monkeypatch.setattr(gpu, "status", lambda: {"available": True, "util": 70, "vram_used_mb": 500})
    assert gpu.gpu_busy() is True  # utilisation over default 50%
    monkeypatch.setattr(
        gpu, "status", lambda: {"available": True, "util": 5, "vram_used_mb": 12000}
    )
    assert gpu.gpu_busy() is True  # VRAM over default 10 GB
    monkeypatch.setattr(gpu, "status", lambda: {"available": True, "util": 5, "vram_used_mb": 500})
    assert gpu.gpu_busy() is False
    monkeypatch.setattr(gpu, "status", lambda: {"available": False})
    assert gpu.gpu_busy() is False  # no GPU -> not busy


def test_focus_should_yield(monkeypatch):
    focus.set_focus(False)
    monkeypatch.setattr(settings, "auto_focus", True)
    monkeypatch.setattr(gpu, "gpu_busy", lambda: False)
    assert focus.should_yield_gpu() is False
    monkeypatch.setattr(gpu, "gpu_busy", lambda: True)
    assert focus.should_yield_gpu() is True  # auto-yield when GPU busy
    monkeypatch.setattr(gpu, "gpu_busy", lambda: False)
    focus.set_focus(True)
    assert focus.should_yield_gpu() is True  # manual override
    focus.set_focus(False)


def test_single_instance_lock(tmp_path):
    p = tmp_path / "purple.lock"
    a = SingleInstance(p, pid_alive=lambda _pid: True)
    assert a.acquire() is True
    b = SingleInstance(p, pid_alive=lambda _pid: True)
    assert b.acquire() is False  # held by a live instance
    a.release()
    c = SingleInstance(p, pid_alive=lambda _pid: True)
    assert c.acquire() is True  # freed after release


def test_single_instance_stale_lock(tmp_path):
    p = tmp_path / "purple.lock"
    p.write_text("999999")
    s = SingleInstance(p, pid_alive=lambda _pid: False)  # stale: pid not alive
    assert s.acquire() is True
