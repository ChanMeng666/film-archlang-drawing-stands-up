"""Final 1080p film render, gentle on a shared laptop.

One Blender at a time, below-normal priority, RENDER_THREADS threads (default 4). Before each
shot it waits until at least MIN_FREE_GB of physical memory is free. Frames resume: rerun after
any interruption. Then composes the film. Log: out/film/render-final.log

  python scripts/render_final.py
"""
import ctypes
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS = [("s01_stands_up", 156), ("s02_dusk_dollhouse", 168), ("s04_exploded_axon", 144), ("s03_city_of_code", 192)]
MIN_FREE_GB = float(os.environ.get("MIN_FREE_GB", "2.0"))
LOG = ROOT / "out" / "film" / "render-final.log"


class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def free_gb():
    m = MEMORYSTATUSEX()
    m.dwLength = ctypes.sizeof(m)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
    return m.ullAvailPhys / 2**30


def log(msg):
    LOG.parent.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}"
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def done(shot, n):
    d = ROOT / "out" / "renders" / f"{shot}-16x9-final" / "frames"
    if not d.exists():
        return 0
    for z in d.glob("f_*.png"):  # placeholders left by an interrupted run
        if z.stat().st_size == 0:
            z.unlink()
    return sum(1 for f in d.glob("f_*.png") if f.stat().st_size > 1024)


def main():
    os.environ.setdefault("RENDER_THREADS", "4")
    for shot, n in SHOTS:
        have = done(shot, n)
        if have >= n:
            log(f"{shot}: already complete ({have}/{n})")
            continue
        while free_gb() < MIN_FREE_GB:
            log(f"waiting: {free_gb():.1f} GB free < {MIN_FREE_GB} GB")
            time.sleep(120)
        log(f"{shot}: start ({have}/{n} done, {free_gb():.1f} GB free, {os.environ['RENDER_THREADS']} threads)")
        t = time.time()
        r = subprocess.run([sys.executable, str(ROOT / "scripts" / "render.py"), shot, "--anim", "--quality", "final"])
        have = done(shot, n)
        log(f"{shot}: exit {r.returncode}, {have}/{n} frames, {(time.time() - t) / 60:.1f} min")
        if have < n:
            log("stopping: shot incomplete; rerun this script to resume")
            sys.exit(1)
    log("composing film")
    r = subprocess.run([sys.executable, str(ROOT / "compose" / "film.py"), "--quality", "final", "--music", "a-new-life"])
    log(f"compose exit {r.returncode}")
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
