"""Hero stills: clean renders plus captioned social versions.

  python compose/stills.py

Reads   out/renders/<shot>-16x9-final/still-<frame>.png (rendered by scripts/stills.sh)
Writes  out/stills/clean/*.png and out/stills/social/*.png
"""
import re
from pathlib import Path

from PIL import Image, ImageDraw

import film

ROOT = Path(__file__).resolve().parents[1]
R = ROOT / "out" / "renders"
OUT = ROOT / "out" / "stills"

court = film.facts("courtyard-house")
N_CODE = len(film.code_lines(ROOT / "plans" / "courtyard-house.arch"))
N_PLANS = len(list((ROOT / "build" / "facts").glob("*.json")))
ROOMS, AREA = court["describe"]["totals"]["rooms"], court["describe"]["totals"]["floor_area_m2"]

STILLS = [  # out name, source, kicker, title, ink
    ("01-drawing-stands-up", R / "s01_stands_up-16x9-final/still-0076.png",
     "archlang compile  →  archlang3d build", "The drawing stands up.", "dark"),
    ("02-dusk-dollhouse", R / "s02_dusk_dollhouse-16x9-final/still-0168.png",
     "courtyard-house.arch", f"{N_CODE} lines.  {ROOMS} rooms.  {AREA} m².", "light"),
    ("03-city-of-code", R / "s03_city_of_code-16x9-final/still-0192.png",
     "every one compiled from .arch", f"{N_PLANS} buildings.  None drawn by hand.", "light"),
    ("04-exploded-axon", R / "s04_exploded_axon-16x9-final/still-0144.png",
     "slab · floors · furniture · walls · roof", "One file. Every layer.", "dark"),
]


def wordmark(img, ink):
    s = img.width / 1920
    src = "archlang-wordmark-black.png" if ink == "dark" else "archlang-wordmark.png"
    wm = Image.open(ROOT / "build/brand" / src).convert("RGBA")
    ww = int(260 * s)
    wm = wm.resize((ww, int(wm.height * ww / wm.width)))
    img.alpha_composite(wm, (img.width - ww - int(80 * s), img.height - wm.height - int(72 * s)))


def social(src: Path, kicker, title, ink):
    img = Image.open(src).convert("RGBA")
    T = film.Type(img.width)
    film.caption(img, T, 50, 0, 100, title, kicker, ink)
    wordmark(img, ink)
    return img


def code_to_form():
    """Real source on the left, the same building on its drawing on the right."""
    render = Image.open(R / "s01_stands_up-16x9-final/still-0156.png").convert("RGBA")
    W, H = render.size
    s = W / 1920
    T = film.Type(W)
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


def main():
    for sub in ("clean", "social"):
        (OUT / sub).mkdir(parents=True, exist_ok=True)
    for name, src, kicker, title, ink in STILLS:
        if not src.exists():
            print("## missing", src)
            continue
        Image.open(src).convert("RGB").save(OUT / "clean" / f"{name}.png")
        social(src, kicker, title, ink).convert("RGB").save(OUT / "social" / f"{name}.png")
        print("## wrote", name)
    if (R / "s01_stands_up-16x9-final/still-0156.png").exists():
        code_to_form().convert("RGB").save(OUT / "social" / "05-code-to-form.png")
        print("## wrote 05-code-to-form")


if __name__ == "__main__":
    main()
