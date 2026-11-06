"""Run one Blender shot at below-normal priority (one heavy process at a time on this laptop).

  python scripts/render.py s01_stands_up --still 1 80 156
  python scripts/render.py s01_stands_up --anim --quality final
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLENDER = os.environ.get("BLENDER") or shutil.which("blender") or r"D:\Blender\blender-5.2.3-windows-x64\blender.exe"


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    shot = ROOT / "blender" / "shots" / f"{sys.argv[1]}.py"
    cmd = [BLENDER, "-b", "--factory-startup", "-t", "6", "--python-exit-code", "1",
           "--python", str(shot), "--", *sys.argv[2:]]
    flags = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
    p = subprocess.run(cmd, creationflags=flags, capture_output=True, text=True, encoding="utf-8", errors="replace")
    keep = [ln for ln in p.stdout.splitlines() + p.stderr.splitlines()
            if any(k in ln for k in ("##", "WROTE", "Error", "Traceback", "File \"", "line ", "Saved:", "Time:"))
            and "Blender create" not in ln]
    print("\n".join(keep[-40:]))
    sys.exit(p.returncode)


if __name__ == "__main__":
    main()
