#!/usr/bin/env python3
"""Re-download every audio asset listed in audio/manifest.json and verify its SHA-256.

The media files are gitignored (Mixkit's licence forbids redistributing them standalone),
so this script is how a fresh clone reproduces audio/music/ and audio/sfx/.

Standard library only. Usage:

    python audio/fetch.py                 # fetch into the repo (paths are relative to the repo root)
    python audio/fetch.py --root DIR      # fetch into another directory (e.g. a temp copy)
    python audio/fetch.py --verify-only   # hash what is on disk, download nothing
    python audio/fetch.py --force         # re-download even when a file already verifies

Exit status is 0 only when every file is present and matches its manifest hash.
"""
import argparse
import hashlib
import json
import os
import sys
import tempfile
import time
import urllib.request

UA = "Mozilla/5.0 (compatible; archlang-cinematic-fetch/1.0)"
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, dest, attempts=3):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    last = None
    for i in range(attempts):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = r.read()
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(dest), suffix=".part")
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            return tmp
        except Exception as e:  # network errors: retry with backoff
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"download failed after {attempts} attempts: {url}: {last}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default=os.path.join(HERE, "manifest.json"))
    ap.add_argument("--root", default=REPO, help="directory the manifest paths are relative to (default: repo root)")
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    with open(args.manifest, encoding="utf-8") as f:
        manifest = json.load(f)

    ok = bad = 0
    for a in manifest["assets"]:
        dest = os.path.join(args.root, *a["path"].split("/"))
        have = os.path.exists(dest) and sha256_file(dest) == a["sha256"]
        if have and not args.force:
            print(f"ok      {a['path']}")
            ok += 1
            continue
        if args.verify_only:
            print(f"MISSING {a['path']}" if not os.path.exists(dest) else f"BADHASH {a['path']}")
            bad += 1
            continue
        try:
            tmp = download(a["download_url"], dest)
        except RuntimeError as e:
            print(f"FAILED  {a['path']}: {e}")
            bad += 1
            continue
        got = sha256_file(tmp)
        if got != a["sha256"]:
            os.remove(tmp)
            print(f"BADHASH {a['path']}: expected {a['sha256']}, got {got} (upstream file changed?)")
            bad += 1
            continue
        os.replace(tmp, dest)
        print(f"fetched {a['path']}")
        ok += 1

    print(f"\n{ok} verified, {bad} failed, {len(manifest['assets'])} total")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
