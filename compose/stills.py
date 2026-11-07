"""Hero stills: clean renders plus captioned social versions.

  python compose/stills.py [--aspect 16x9|9x16|1x1]

Reads   out/renders/<shot>-<aspect>-final/still-<frame>.png (rendered by scripts/stills.sh)
Writes  out/stills/clean/*.png and out/stills/social/*.png (names end in -9x16 / -1x1 for those aspects)
"""
import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw

import code_to_form as c2f
import film

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "out" / "renders"
OUT = ROOT / "out" / "stills"

court = film.facts("courtyard-house")
N_CODE = len(film.code_lines(ROOT / "plans" / "courtyard-house.arch"))
N_PLANS = len(list((ROOT / "build" / "facts").glob("*.json")))
ROOMS, AREA = court["describe"]["totals"]["rooms"], court["describe"]["totals"]["floor_area_m2"]

STILLS = [  # out name, shot, frame, kicker, title, ink
    ("01-drawing-stands-up", "s01_stands_up", 76,
     "archlang compile  →  archlang3d build", "The drawing stands up.", "dark"),
    ("02-dusk-dollhouse", "s02_dusk_dollhouse", 168,
     "courtyard-house.arch", f"{N_CODE} lines.  {ROOMS} rooms.  {AREA} m².", "light"),
    ("03-city-of-code", "s03_city_of_code", 192,
     "every one compiled from .arch", f"{N_PLANS} buildings.  None drawn by hand.", "light"),
    ("04-exploded-axon", "s04_exploded_axon", 144,
     "slab · floors · furniture · walls · roof", "One file. Every layer.", "dark"),
]


def wordmark(img, ink):
    s = film.Type(img.width, img.height).s
    src = "archlang-wordmark-black.png" if ink == "dark" else "archlang-wordmark.png"
    wm = Image.open(ROOT / "build/brand" / src).convert("RGBA")
    ww = int(260 * s)
    wm = wm.resize((ww, int(wm.height * ww / wm.width)))
    img.alpha_composite(wm, (img.width - ww - int(80 * s), img.height - wm.height - int(72 * s)))


def social(src: Path, kicker, title, ink):
    img = Image.open(src).convert("RGBA")
    T = film.Type(img.width, img.height)
    film.caption(img, T, 50, 0, 100, title, kicker, ink, pos="tl" if T.v else "bl")
    wordmark(img, ink)
    return img


def code_to_form():
    """Real source on the left, the same building on its drawing on the right."""
    render = Image.open(R / "s01_stands_up-16x9-final/still-0156.png").convert("RGBA")
    W, H = render.size
    s = W / 1920
    T = film.Type(W, H)
    img = Image.new("RGBA", (W, H), (*film.VOID, 255))
    pw = int(W * 0.40)
    right = render.crop((int(W * 0.12), 0, int(W * 0.12) + W - pw, H))
    img.alpha_composite(right, (pw, 0))
    d = ImageDraw.Draw(img)
    lines = film.code_lines(ROOT / "plans" / "courtyard-house.arch")
    x, y, lh = int(64 * s), int(150 * s), int(27 * s)
    d.text((x, int(64 * s)), "courtyard-house.arch", font=T.code_b, fill=(*film.PLUM, 255))
    d.text((x, int(96 * s)), f"{N_CODE} lines of text", font=T.kick, fill=(160, 166, 180, 255))
    maxc = 52
    for ln in lines[: (H - y - int(60 * s)) // lh]:
        ln = ln if len(ln) <= maxc else ln[: maxc - 1] + "…"
        m = re.match(r"(\s*)(\w+)(.*)", ln)
        cx = x
        if m:
            d.text((cx, y), m.group(1) + m.group(2), font=T.code, fill=(196, 176, 255, 255))
            cx += d.textlength(m.group(1) + m.group(2), font=T.code)
            d.text((cx, y), m.group(3), font=T.code, fill=(225, 228, 235, 255))
        else:
            d.text((cx, y), ln, font=T.code, fill=(225, 228, 235, 255))
        y += lh
    grad = Image.new("RGBA", (int(90 * s), H))
    for i in range(grad.width):
        ImageDraw.Draw(grad).line([(i, 0), (i, H)], fill=(*film.VOID, int(255 * (1 - i / grad.width))))
    img.alpha_composite(grad, (pw, 0))
    wordmark(img, "dark")
    return img


def code_to_form_pulse(src: Path):
    """9:16 and 1:1: the code-to-form shot at its pulse, every wall line lit beside its wall."""
    img = Image.open(src).convert("RGBA")
    T = film.Type(img.width, img.height)
    lines, walls, span = c2f.source_window()
    c2f.panel(img, T, c2f.PULSE + 8, lines, walls, span)
    n = len(walls)
    film.caption(img, T, 50, 0, 100, f"{n} lines.  {n} walls.", "same ids in the text and the model", "dark")
    wordmark(img, "dark")
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--aspect", default="16x9", choices=["16x9", "9x16", "1x1"])
    asp = ap.parse_args().aspect
    tag = "" if asp == "16x9" else f"-{asp}"
    for sub in ("clean", "social"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    for name, shot, frame, kicker, title, ink in STILLS:
        src = R / f"{shot}-{asp}-final" / f"still-{frame:04d}.png"
        if not src.exists():
            print("## missing", src)
            continue
        Image.open(src).convert("RGB").save(OUT / "clean" / f"{name}{tag}.png")
        social(src, kicker, title, ink).convert("RGB").save(OUT / "social" / f"{name}{tag}.png")
        print("## wrote", name + tag)
    if asp == "16x9":
        if (R / "s01_stands_up-16x9-final/still-0156.png").exists():
            code_to_form().convert("RGB").save(OUT / "social" / "05-code-to-form.png")
            print("## wrote 05-code-to-form")
    else:
        src = R / f"s05_code_to_form-{asp}-final/still-0214.png"
        if src.exists():
            code_to_form_pulse(src).convert("RGB").save(OUT / "social" / f"05-code-to-form{tag}.png")
            print("## wrote 05-code-to-form" + tag)


if __name__ == "__main__":
    main()
