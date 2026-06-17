"""Downloads + system-health watcher tests. Real temp dir for downloads; faked psutil
for CPU/RAM so the hysteresis (consecutive breaches, no repeat) is deterministic."""

from __future__ import annotations

import types

from purple.config import settings
from purple.triggers.priority import IMPORTANT, NORMAL
from purple.triggers.watchers import DownloadsWatcher, SystemHealthWatcher


async def test_downloads_watcher_primes_then_notifies(monkeypatch, tmp_path):
    (tmp_path / "already_here.zip").write_text("x")
    monkeypatch.setattr(settings, "download_dir", str(tmp_path))
    w = DownloadsWatcher()
    assert await w.check() == []  # primes on the existing file
    (tmp_path / "report.pdf").write_text("done")
    (tmp_path / "movie.mkv.crdownload").write_text("partial")  # still downloading
    events = await w.check()
    assert len(events) == 1
    assert events[0].source == "download" and "report.pdf" in events[0].title
    assert events[0].priority == NORMAL


async def test_downloads_watcher_missing_dir(monkeypatch, tmp_path):
    monkeypatch.setattr(settings, "download_dir", str(tmp_path / "nope"))
    assert await DownloadsWatcher().check() == []


def _fake_psutil(cpu: float, ram: float) -> types.ModuleType:
    mod = types.ModuleType("psutil")
    mod.cpu_percent = lambda interval=None: cpu
    mod.virtual_memory = lambda: types.SimpleNamespace(percent=ram)
    return mod


def _quiet_gpu(monkeypatch) -> None:
    from purple import gpu

    monkeypatch.setattr(gpu, "status", lambda: {"available": False})


async def test_system_health_needs_sustained_breach(monkeypatch):
    monkeypatch.setattr(settings, "cpu_high_pct", 90)
    monkeypatch.setattr(settings, "ram_high_pct", 90)
    _quiet_gpu(monkeypatch)
    import sys

    monkeypatch.setitem(sys.modules, "psutil", _fake_psutil(95.0, 50.0))
    w = SystemHealthWatcher()
    assert await w.check() == []  # 1st breach
    assert await w.check() == []  # 2nd breach
    events = await w.check()  # 3rd — fires once
    assert len(events) == 1 and "CPU" in events[0].title
    assert await w.check() == []  # already warned: no nagging


async def test_system_health_ram_is_important_and_recovers(monkeypatch):
    monkeypatch.setattr(settings, "ram_high_pct", 90)
    _quiet_gpu(monkeypatch)
    import sys

    monkeypatch.setitem(sys.modules, "psutil", _fake_psutil(10.0, 96.0))
    w = SystemHealthWatcher()
    await w.check()
    await w.check()
    events = await w.check()
    assert len(events) == 1 and events[0].priority == IMPORTANT  # memory pressure breaks through

    monkeypatch.setitem(sys.modules, "psutil", _fake_psutil(10.0, 40.0))  # recovered
    assert await w.check() == []
    monkeypatch.setitem(sys.modules, "psutil", _fake_psutil(10.0, 96.0))  # high again
    await w.check()
    await w.check()
    assert len(await w.check()) == 1  # re-arms and warns again


async def test_system_health_gpu_util_and_vram(monkeypatch):
    monkeypatch.setattr(settings, "gpu_high_pct", 97)
    monkeypatch.setattr(settings, "gpu_vram_high_pct", 92)
    import sys

    monkeypatch.setitem(sys.modules, "psutil", _fake_psutil(10.0, 10.0))  # cpu/ram quiet
    from purple import gpu

    monkeypatch.setattr(gpu, "status", lambda: {"available": True, "util": 99, "vram_pct": 95})
    w = SystemHealthWatcher()
    await w.check()
    await w.check()
    events = await w.check()  # 3rd sustained breach: both GPU util + VRAM fire
    titles = " ".join(e.title for e in events)
    assert "GPU pinned" in titles and "GPU memory" in titles
    vram_ev = next(e for e in events if "GPU memory" in e.title)
    assert vram_ev.priority == IMPORTANT


async def test_system_health_no_gpu_is_silent(monkeypatch):
    _quiet_gpu(monkeypatch)
    import sys

    monkeypatch.setitem(sys.modules, "psutil", _fake_psutil(10.0, 10.0))
    w = SystemHealthWatcher()
    for _ in range(4):
        assert await w.check() == []  # no nvidia-smi → no GPU events, nothing else breaching
