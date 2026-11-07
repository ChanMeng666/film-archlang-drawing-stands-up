"""Code to form: a 12.5 s clip. Each `wall id=…` line of the source lights up while the wall it
compiles to glows plum in the render (blender/shots/s05_code_to_form.py), in the compiler's order.

  python compose/code_to_form.py [--quality final] [--aspect 16x9|9x16]

Reads   out/renders/s05_code_to_form-<aspect>-<quality>/frames/f_####.png
Writes  out/film/code-to-form-<aspect>-<quality>.mp4
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

import film

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "blender"))
from code_to_form_timing import F_END, PULSE, wall_window  # noqa: E402

END_FRAMES = 60
SRC = ROOT / "plans" / "courtyard-house.arch"


def active(f, i):
    """How lit wall line i is at frame f (0..1), matching the shot's glow keys."""
    f0, f1 = wall_window(i)
    if f0 <= f <= f1 + 5:
        return min(1.0, (f - f0) / 3, (f1 + 5 - f) / 7)
    if f >= PULSE:
        return max(0.35, 1 - max(0, f - PULSE - 4) / 16) if f < PULSE + 20 else 0.35
    return 0.0


def panel(img, T, f, lines, walls, span):
    """The source around the wall block; the line being compiled is highlighted."""
    s = T.s
    a = min(1.0, f / 8)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cw = d.textlength("M", font=T.code)
    x0, y0 = (int(56 * s), int(170 * s)) if T.v else (int(64 * s), int(64 * s))
    maxc = int((img.width - 2 * x0 - 52 * s) / cw) if T.v else 46
    lh = T.code_lh
    w = int(52 * s + cw * maxc)
    h = int(70 * s) + lh * len(lines)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(18 * s), fill=(*film.VOID, int(232 * a)))
    d.text((x0 + int(26 * s), y0 + int(20 * s)), f"courtyard-house.arch  ·  lines {span[0]}–{span[1]}",
           font=T.code_b, fill=(*film.PLUM, int(255 * a)))
    for k, ln in enumerate(lines):
        y = y0 + int(58 * s) + k * lh
        ln = ln if len(ln) <= maxc else ln[: maxc - 1] + "…"
        lit = active(f, walls.index(k)) if k in walls else 0.0
        if lit > 0:
            d.rounded_rectangle([x0 + int(12 * s), y - int(4 * s), x0 + w - int(12 * s), y + lh - int(4 * s)],
                                radius=int(6 * s), fill=(*film.PLUM, int(150 * lit * a)))
        m = re.match(r"(\s*)(\w+)(.*)", ln)
        cx = x0 + int(26 * s)
        rest = (255, 255, 255) if lit > 0 else (225, 228, 235)
        if m:
            kw = (255, 255, 255) if lit > 0 else (196, 176, 255)
            d.text((cx, y), m.group(1) + m.group(2), font=T.code, fill=(*kw, int(255 * a)))
            cx += d.textlength(m.group(1) + m.group(2), font=T.code)
            d.text((cx, y), m.group(3), font=T.code, fill=(*rest, int(255 * a)))
        else:
            d.text((cx, y), ln, font=T.code, fill=(*rest, int(255 * a)))
    img.alpha_composite(lay)


def source_window(pad=3):
    """Code lines (as film.code_lines filters them) around the wall block, the indices of the wall
    lines in that window, and the window's first and last line numbers in the file."""
    numbered = [(no, ln.rstrip()) for no, ln in enumerate(SRC.read_text(encoding="utf-8").splitlines(), start=1)
                if ln.strip() and not re.match(r"\s*(#|//)", ln)]
    wl = [k for k, (_no, ln) in enumerate(numbered) if re.match(r"\s*wall\s+id=", ln)]
    lo, hi = max(0, wl[0] - pad), min(len(numbered), wl[-1] + pad)
    win = numbered[lo:hi]
    return [ln for _no, ln in win], [k - lo for k in wl], (win[0][0], win[-1][0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quality", default="final")
    ap.add_argument("--aspect", default="16x9", choices=["16x9", "9x16"])
    a = ap.parse_args()

    lines, walls, span = source_window()
    n = len(walls)

    src = ROOT / "out" / "renders" / f"s05_code_to_form-{a.aspect}-{a.quality}" / "frames"
    out = ROOT / "out" / "film"
    frames_dir = out / f"frames-c2f-{a.aspect}-{a.quality}"
    frames_dir.mkdir(parents=True, exist_ok=True)
    k = 0
    T = size = None
    for f in range(1, F_END + 1):
        img = Image.open(src / f"f_{f:04d}.png").convert("RGBA")
        T = T or film.Type(img.width, img.height)
        size = img.size
        panel(img, T, f, lines, walls, span)
        film.caption(img, T, f, 6, PULSE - 12, "Each line is a wall.", "archlang3d build", "dark")
        film.caption(img, T, f, PULSE + 2, F_END + 9, f"{n} lines.  {n} walls.", "same ids in the text and the model", "dark")
        k += 1
        img.convert("RGB").save(frames_dir / f"{k:05d}.png", compress_level=1)
    last_frame = src / f"f_{F_END:04d}.png"
    for f in range(1, END_FRAMES + 1):
        k += 1
        film.end_card(size, T, f, last_frame).convert("RGB").save(frames_dir / f"{k:05d}.png", compress_level=1)
    print("## frames", k, "wall lines", n)

    dur = k / film.FPS
    taps = ["kenney/impactwood-light-001-kenney-impact-sounds.ogg", "kenney/impactwood-light-003-kenney-impact-sounds.ogg",
            "kenney/impactsoft-medium-001-kenney-impact-sounds.ogg"]
    events = [(film.SFX + taps[i % 3], (wall_window(i)[0] + 1) / film.FPS, 0.22, "") for i in range(n)]
    events += [
        (film.SFX + "mixkit/magical-stone-slide-mixkit-1528.wav", 0.2, 0.2, ""),
        (film.SFX + "mixkit/movie-whoosh-impact-presentation-mixkit-2903.wav", PULSE / film.FPS - 0.35, 0.55, ""),
    ]
    music, _swell = film.MUSIC["a-new-life"]
    wav = out / f"mix-c2f-{a.aspect}.wav"
    film.render_mix(wav, dur, music, 0.0, events)
    mp4 = out / f"code-to-form-{a.aspect}-{a.quality}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(film.FPS), "-i", str(frames_dir / "%05d.png"),
                    "-i", str(wav), "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-shortest", str(mp4)], check=True, cwd=ROOT)
    print("## wrote", mp4)


if __name__ == "__main__":
    main()
