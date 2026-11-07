"""Final 1080p film render, gentle on a shared laptop.

One Blender at a time, below-normal priority, RENDER_THREADS threads (default 4). Before each
shot it waits until at least MIN_FREE_GB of physical memory is free. While a shot renders, a
watchdog stops Blender if free memory stays under LOW_FREE_GB for a minute, waits for
MIN_FREE_GB again and resumes; frames already written are kept. Then composes the film.
Log: out/film/render-final.log

  python scripts/render_final.py [--aspect 16x9|9x16]
"""
import argparse
import ctypes
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS = [("s01_stands_up", 156), ("s02_dusk_dollhouse", 168), ("s04_exploded_axon", 144), ("s03_city_of_code", 192)]
MIN_FREE_GB = float(os.environ.get("MIN_FREE_GB", "2.0"))
LOW_FREE_GB = float(os.environ.get("LOW_FREE_GB", "1.0"))
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


def done(shot, aspect):
    d = ROOT / "out" / "renders" / f"{shot}-{aspect}-final" / "frames"
    if not d.exists():
        return 0
    for z in d.glob("f_*.png"):  # placeholders left by an interrupted run
        if z.stat().st_size == 0:
            z.unlink()
    return sum(1 for f in d.glob("f_*.png") if f.stat().st_size > 1024)


def wait_for_memory():
    while free_gb() < MIN_FREE_GB:
        log(f"waiting: {free_gb():.1f} GB free < {MIN_FREE_GB} GB")
        time.sleep(120)


def render(shot, aspect):
    """One Blender run. Returns its exit code, or None if the watchdog stopped it for memory."""
    p = subprocess.Popen([sys.executable, str(ROOT / "scripts" / "render.py"), shot, "--anim", "--quality", "final",
                          "--aspect", aspect])
    low_since = None
    while p.poll() is None:
        time.sleep(10)
        if free_gb() < LOW_FREE_GB:
            low_since = low_since or time.time()
            if time.time() - low_since > 60:
                subprocess.run(["taskkill", "/T", "/F", "/PID", str(p.pid)], capture_output=True)
                p.wait()
                return None
        else:
            low_since = None
    return p.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aspect", default="16x9", choices=["16x9", "9x16"])
    aspect = ap.parse_args().aspect
    os.environ.setdefault("RENDER_THREADS", "4")
    for shot, n in SHOTS:
        have = done(shot, aspect)
        if have >= n:
            log(f"{shot}-{aspect}: already complete ({have}/{n})")
            continue
        t = time.time()
        while True:
            wait_for_memory()
            log(f"{shot}-{aspect}: start ({have}/{n} done, {free_gb():.1f} GB free, {os.environ['RENDER_THREADS']} threads)")
            rc = render(shot, aspect)
            have = done(shot, aspect)
            if rc is not None:
                break
            log(f"{shot}-{aspect}: paused at {have}/{n}, free memory under {LOW_FREE_GB} GB for a minute")
        log(f"{shot}-{aspect}: exit {rc}, {have}/{n} frames, {(time.time() - t) / 60:.1f} min")
        if have < n:
            log("stopping: shot incomplete; rerun this script to resume")
            sys.exit(1)
    log(f"composing film {aspect}")
    r = subprocess.run([sys.executable, str(ROOT / "compose" / "film.py"), "--quality", "final", "--music", "a-new-life",
                        "--aspect", aspect])
    log(f"compose exit {r.returncode}")
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
