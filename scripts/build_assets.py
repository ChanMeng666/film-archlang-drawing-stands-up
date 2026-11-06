"""Compile every plan in plans/ into the inputs the Blender shots read.

  build/sheets/<name>.svg   archlang compile (viewBox = plan mm, used for register)
  build/sheets/<name>.png   archlang compile -f png -w 6000 (the ground texture)
  build/glb/<name>.glb      archlang3d build --doors plan
  build/facts/<name>.json   archlang describe --json + source line count

Usage: python scripts/build_assets.py [name ...]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "node_modules" / ".bin"


def tool(name):
    for ext in (".cmd", ""):
        p = BIN / f"{name}{ext}"
        if p.exists():
            return str(p)
    sys.exit(f"missing {name}; run npm install")


ARCH, ARCH3D = tool("archlang"), tool("archlang3d")


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return r.returncode, r.stdout, r.stderr


def build(src: Path):
    n = src.stem
    out = {k: ROOT / "build" / k for k in ("sheets", "glb", "facts")}
    for d in out.values():
        d.mkdir(parents=True, exist_ok=True)
    status = {}
    status["svg"], _, e1 = run([ARCH, "compile", str(src), "-o", str(out["sheets"] / f"{n}.svg"), "-q"])
    status["png"], _, e2 = run([ARCH, "compile", str(src), "-f", "png", "-w", "6000", "-o", str(out["sheets"] / f"{n}.png"), "-q"])
    status["png2k"], _, _ = run([ARCH, "compile", str(src), "-f", "png", "-w", "2500", "-o", str(out["sheets"] / f"{n}-2k.png"), "-q"])
    status["glb"], _, e3 = run([ARCH3D, "build", str(src), "-o", str(out["glb"] / f"{n}.glb"), "--doors", "plan", "--json"])
    rc, desc, e4 = run([ARCH, "describe", str(src), "--json"])
    status["describe"] = rc
    facts = {"name": n, "source": str(src.relative_to(ROOT)).replace("\\", "/"),
             "lines": sum(1 for line in src.read_text(encoding="utf-8").splitlines() if line.strip()),
             "bytes": src.stat().st_size}
    try:
        facts["describe"] = json.loads(desc)
    except json.JSONDecodeError:
        facts["describe"] = None
    (out["facts"] / f"{n}.json").write_text(json.dumps(facts, indent=2), encoding="utf-8")
    errs = " | ".join(e.strip().splitlines()[-1] for e in (e1, e2, e3, e4) if e.strip())
    print(f"{n:22s} " + " ".join(f"{k}={v}" for k, v in status.items()) + (f"  [{errs[:160]}]" if errs and any(status.values()) else ""))
    return status


def main():
    names = sys.argv[1:]
    srcs = sorted((ROOT / "plans").glob("*.arch"))
    if names:
        srcs = [s for s in srcs if s.stem in names]
    bad = [s.stem for s in srcs if any(build(s).values())]
    if bad:
        print("NOT BUILDABLE:", ", ".join(bad))


if __name__ == "__main__":
    main()
