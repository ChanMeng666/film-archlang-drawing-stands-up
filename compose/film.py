"""Compose the hero film: Blender frames + 2D type + end card, then score and encode.

  python compose/film.py [--quality review|final|preview] [--music a-new-life|discover|mountains] [--aspect 16x9|9x16]

Reads   out/renders/<shot>-<aspect>-<quality>/frames/f_####.png
Writes  out/film/hero-<aspect>-<quality>-<music>.mp4
Captions state only facts read from the compiler (build/facts/*.json) or the source files.
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
FONTS = ROOT / "compose" / "fonts"
FPS = 24
VOID, PLUM, SHEET, INK = (15, 17, 21), (128, 82, 255), (245, 242, 234), (17, 17, 17)

SHOTS = [  # name, frames, caption ink on this shot
    ("s01_stands_up", 156, "dark"),
    ("s02_dusk_dollhouse", 168, "light"),
    ("s03_city_of_code", 192, "light"),
    ("s04_exploded_axon", 144, "dark"),
]
END_FRAMES = 108
MUSIC = {
    "a-new-life": ("audio/music/a-new-life-eugenio-mininni-mixkit-543.mp3", 24.65),
    "discover": ("audio/music/discover-eugenio-mininni-mixkit-587.mp3", 12.9),
    "mountains": ("audio/music/mountains-andrew-ev-mixkit-187.mp3", 31.8),
}
SFX = "audio/sfx/"


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def code_lines(src: Path):
    return [ln.rstrip() for ln in src.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not re.match(r"\s*(#|//)", ln)]


def facts(name):
    return json.loads((ROOT / "build" / "facts" / f"{name}.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ type

class Type:
    def __init__(self, w, h):
        self.v = h > w  # vertical: larger type, titles break at double spaces
        self.s = w / 1270 if self.v else w / 1920
        s = self.s
        self.h1 = font("InterDisplay-Bold.ttf", int(74 * s))
        self.h2 = font("InterDisplay-SemiBold.ttf", int(40 * s))
        self.kick = font("JetBrainsMono-Medium.ttf", int(24 * s))
        cs = int((24 if self.v else 19) * s)
        self.code = font("JetBrainsMono-Regular.ttf", cs)
        self.code_b = font("JetBrainsMono-Bold.ttf", cs)
        self.code_lh = int(cs * 1.52) if self.v else int(29 * s)


def alpha_for(f, f0, f1, ramp=9):
    if f < f0 or f > f1:
        return 0.0
    a = min(1.0, (f - f0) / ramp, (f1 - f) / ramp)
    return max(0.0, a) ** 1.4


def caption(img, T, f, f0, f1, title, kicker=None, ink="dark", pos="bl"):
    a = alpha_for(f, f0, f1)
    if a <= 0:
        return
    s = T.s
    scrim_h = int(img.height * 0.42)  # soft gradient so type reads over busy drawings
    sc = (245, 242, 234) if ink == "dark" else (8, 10, 16)
    grad = Image.new("RGBA", (1, scrim_h))
    for i in range(scrim_h):
        grad.putpixel((0, i), (*sc, int(200 * a * (i / scrim_h) ** 1.6)))
    grad = grad.resize((img.width, scrim_h))
    if pos == "bl":
        img.alpha_composite(grad, (0, img.height - scrim_h))
    else:
        img.alpha_composite(grad.transpose(Image.Transpose.FLIP_TOP_BOTTOM), (0, 0))
    lines = title.split("  ") if T.v else [title]
    lh = int(86 * s)
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    rise = int((1 - min(1, (f - f0) / 12)) * 18 * s)
    col = INK if ink == "dark" else (255, 255, 255)
    shadow = (255, 255, 255, int(110 * a)) if ink == "dark" else (0, 0, 0, int(150 * a))
    x = int(96 * s)
    if pos == "bl":  # vertical: clear of the social app's bottom bar
        y = img.height - int((400 if T.v else 150) * s) - lh * (len(lines) - 1) + rise
    else:
        y = int((250 if T.v else 96) * s) + rise
    if kicker:
        d.rectangle([x, y - int(54 * s), x + int(10 * s), y - int(28 * s)], fill=(*PLUM, int(255 * a)))
        d.text((x + int(22 * s), y - int(58 * s)), kicker, font=T.kick, fill=(*col, int(230 * a)))
    for i, ln in enumerate(lines):
        for dx, dy in ((2, 2), (0, 0)):
            fill = shadow if (dx, dy) != (0, 0) else (*col, int(255 * a))
            d.text((x + dx * s, y + i * lh + dy * s), ln.strip(), font=T.h1, fill=fill)
    img.alpha_composite(lay)


def code_panel(img, T, f, lines, f0=1, f1=78):
    """Real source lines, typed in, on a Void panel at the left (top in vertical)."""
    a = alpha_for(f, f0, f1, ramp=8)
    if a <= 0:
        return
    s = T.s
    lay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0 = (int(56 * s), int(170 * s)) if T.v else (int(64 * s), int(64 * s))
    lh = T.code_lh
    cw = ImageDraw.Draw(img).textlength("M", font=T.code)
    maxc = int((img.width - 2 * x0 - 52 * s) / cw) if T.v else 46
    shown = [ln if len(ln) <= maxc else ln[: maxc - 1] + "…" for ln in lines[:22]]
    w = int(52 * s) + int(ImageDraw.Draw(img).textlength("M" * maxc, font=T.code))
    h = int(70 * s) + lh * len(shown)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(18 * s), fill=(*VOID, int(232 * a)))
    d.text((x0 + int(26 * s), y0 + int(20 * s)), "courtyard-house.arch", font=T.code_b, fill=(*PLUM, int(255 * a)))
    chars = int(max(0, f - f0) * 26)  # typing speed: characters per frame
    used = 0
    for i, ln in enumerate(shown):
        if used >= chars:
            break
        txt = ln[: max(0, chars - used)]
        used += len(ln)
        y = y0 + int(58 * s) + i * lh
        kw = re.match(r"(\s*)(\w+)(.*)", txt)
        cx = x0 + int(26 * s)
        if kw:
            d.text((cx, y), kw.group(1) + kw.group(2), font=T.code, fill=(196, 176, 255, int(255 * a)))
            cx += d.textlength(kw.group(1) + kw.group(2), font=T.code)
            d.text((cx, y), kw.group(3), font=T.code, fill=(225, 228, 235, int(255 * a)))
        else:
            d.text((cx, y), txt, font=T.code, fill=(225, 228, 235, int(255 * a)))
    img.alpha_composite(lay)


def end_card(size, T, f, bg_src: Path):
    w, h = size
    s = T.s
    base = Image.open(bg_src).convert("RGB").resize(size).filter(ImageFilter.GaussianBlur(int(18 * s)))
    img = Image.blend(Image.new("RGB", size, VOID), base, 0.28).convert("RGBA")
    word = Image.open(ROOT / "build/brand/archlang-wordmark.png").convert("RGBA")  # the mark is in the wordmark
    pop = 1 + 0.05 * max(0.0, 1 - f / 16)
    ww = int(820 * s * pop)
    word = word.resize((ww, int(word.height * ww / word.width)))
    cy = int(h * (0.40 if T.v else 0.36))
    a1 = min(1.0, f / 10)
    word.putalpha(word.getchannel("A").point(lambda v: int(v * a1)))
    img.alpha_composite(word, ((w - word.width) // 2, cy - word.height // 2))
    d = ImageDraw.Draw(img)
    a2 = min(1.0, max(0.0, (f - 16) / 10))
    tag = "Designs that compile."
    tw = d.textlength(tag, font=T.h1)
    d.text(((w - tw) / 2, cy + int(150 * s)), tag, font=T.h1, fill=(255, 255, 255, int(255 * a2)))
    a3 = min(1.0, max(0.0, (f - 30) / 10))
    cmd = "npx @chanmeng666/archlang"
    cw = d.textlength(cmd, font=T.h2)
    px, py = (w - cw) / 2, cy + int(275 * s)
    d.rounded_rectangle([px - int(28 * s), py - int(16 * s), px + cw + int(28 * s), py + int(60 * s)],
                        radius=int(14 * s), outline=(*PLUM, int(255 * a3)), width=max(2, int(3 * s)),
                        fill=(*VOID, int(200 * a3)))
    d.text((px, py), cmd, font=T.h2, fill=(225, 228, 235, int(255 * a3)))
    url = "archlang.uk  ·  open source"
    uw = d.textlength(url, font=T.kick)
    d.text(((w - uw) / 2, py + int(104 * s)), url, font=T.kick, fill=(180, 184, 196, int(255 * a3)))
    return img


# ------------------------------------------------------------------ audio

def mix(out_wav: Path, dur: float, music_key: str, cuts: list):
    music, swell = MUSIC[music_key]
    offset = max(0.0, swell - cuts[2])  # the swell lands on the city cut
    c1, c2, c3, c4 = cuts[1], cuts[2], cuts[3], cuts[4]
    # (file, start seconds, gain, extra filter)
    events = [
        (SFX + "mixkit/magical-stone-slide-mixkit-1528.wav", 1.35, 0.3, ""),
        (SFX + "mixkit/stone-debris-falling-mixkit-403.wav", 1.7, 0.1, ""),
        (SFX + "kenney/impactsoft-heavy-001-kenney-impact-sounds.ogg", 3.2, 0.38, ""),
        (SFX + "kenney/impactsoft-heavy-001-kenney-impact-sounds.ogg", 4.6, 0.3, ""),
        (SFX + "mixkit/cinematic-tunnel-reverb-woosh-mixkit-1486.wav", c1 - 0.45, 0.26, ""),
        (SFX + "mixkit/summer-night-crickets-loop-mixkit-1789.wav", c1 + 0.6, 0.16, f",afade=t=in:d=1.5,afade=t=out:st={c2 - c1 - 2.0}:d=1.4"),
        (SFX + "mixkit/on-or-off-light-switch-tap-mixkit-2585.wav", c1 + 52 / FPS, 0.25, ""),
        (SFX + "mixkit/cinematic-wind-swell-mixkit-1170.wav", c2 - 6.5, 0.3, ",afade=t=in:d=3"),
        (SFX + "mixkit/big-cinematic-impact-mixkit-788.mp3", c2 - 0.05, 0.9, ""),
        (SFX + "mixkit/drum-deep-impact-mixkit-563.wav", c2 - 0.02, 0.55, ""),
        (SFX + "mixkit/urban-park-and-traffic-mixkit-2932.wav", c2 + 0.5, 0.16, f",afade=t=in:d=2,afade=t=out:st={c3 - c2 - 2.5}:d=2"),
        (SFX + "mixkit/storm-coming-whoosh-mixkit-2408.wav", c3 - 0.6, 0.45, ""),
        (SFX + "mixkit/movie-whoosh-impact-presentation-mixkit-2903.wav", c4 - 0.35, 0.6, ""),
    ]
    taps = ["kenney/impactwood-light-001-kenney-impact-sounds.ogg", "kenney/impactwood-light-003-kenney-impact-sounds.ogg",
            "kenney/impactsoft-medium-001-kenney-impact-sounds.ogg"]
    for i in range(0, 20, 2):  # furniture landing in s01 (drop starts 98 + 2i, lands ~10 frames later)
        events.append((SFX + taps[i // 2 % 3], (98 + 2 * i + 10) / FPS, 0.18, ""))
    inputs = ["-ss", f"{offset:.3f}", "-t", f"{dur:.3f}", "-i", music]
    chains = [f"[0:a]aresample=48000,volume=0.9,afade=t=in:d=0.6,afade=t=out:st={dur - 2.8:.3f}:d=2.8[m]"]
    for k, (path, t, g, extra) in enumerate(events, start=1):
        inputs += ["-i", path]
        ms = int(max(0.0, t) * 1000)
        chains.append(f"[{k}:a]aresample=48000,aformat=channel_layouts=stereo,volume={g}{extra},adelay={ms}|{ms}[e{k}]")
    labels = "[m]" + "".join(f"[e{k}]" for k in range(1, len(events) + 1))
    fc = ";".join(chains) + f";{labels}amix=inputs={len(events) + 1}:normalize=0:duration=first,atrim=0:{dur:.3f}[mix]"
    raw = out_wav.with_suffix(".raw.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", fc, "-map", "[mix]", str(raw)], check=True, cwd=ROOT)
    # two-pass loudnorm to -14 LUFS, -1.5 dBTP (social)
    p = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True, cwd=ROOT)
    m = json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', p.stderr, re.S).group(0))
    ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", ln + ",aresample=48000", str(out_wav)], check=True, cwd=ROOT)
    print(f"## audio: music offset {offset:.2f}s, measured {m['input_i']} LUFS -> -14")


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quality", default="review")
    ap.add_argument("--music", default="a-new-life", choices=list(MUSIC))
    ap.add_argument("--only-audio", action="store_true")
    ap.add_argument("--aspect", default="16x9", choices=["16x9", "9x16"])
    a = ap.parse_args()

    out = ROOT / "out" / "film"
    frames_dir = out / (f"frames-{a.quality}" if a.aspect == "16x9" else f"frames-{a.aspect}-{a.quality}")
    frames_dir.mkdir(parents=True, exist_ok=True)
    court, city = facts("courtyard-house"), sorted((ROOT / "build" / "facts").glob("*.json"))
    n_code = len(code_lines(ROOT / "plans" / "courtyard-house.arch"))
    rooms = court["describe"]["totals"]["rooms"]
    area = court["describe"]["totals"]["floor_area_m2"]
    lines = code_lines(ROOT / "plans" / "courtyard-house.arch")

    cuts, t = [0.0], 0
    for _n, nf, _ink in SHOTS:
        t += nf
        cuts.append(t / FPS)
    total = t + END_FRAMES
    dur = total / FPS

    if not a.only_audio:
        k = 0
        T = size = None
        last_city = None
        for si, (name, nf, ink) in enumerate(SHOTS):
            src = ROOT / "out" / "renders" / f"{name}-{a.aspect}-{a.quality}" / "frames"
            top = "tl" if a.aspect == "9x16" and name != "s01_stands_up" else "bl"  # vertical: over the sky
            for f in range(1, nf + 1):
                img = Image.open(src / f"f_{f:04d}.png").convert("RGBA")
                T = T or Type(img.width, img.height)
                size = img.size
                if name == "s01_stands_up":
                    code_panel(img, T, f, lines)
                    caption(img, T, f, 84, 154, "Then it stood up.", "archlang3d build", ink)
                    caption(img, T, f, 6, 72, "This plan is text.", "archlang compile", ink, pos="bl")
                elif name == "s02_dusk_dollhouse":
                    caption(img, T, f, 20, 160, f"{n_code} lines.  {rooms} rooms.  {area} m².", "describe --json", ink, pos=top)
                elif name == "s03_city_of_code":
                    caption(img, T, f, 40, 186, f"{len(city)} buildings.  None drawn by hand.", "every one compiled from .arch", ink, pos=top)
                    if f == nf:
                        last_city = src / f"f_{f:04d}.png"
                elif name == "s04_exploded_axon":
                    caption(img, T, f, 24, 140, "One file. Every layer.", "slab · floors · furniture · walls · roof", ink, pos=top)
                k += 1
                img.convert("RGB").save(frames_dir / f"{k:05d}.png", compress_level=1)
        for f in range(1, END_FRAMES + 1):
            k += 1
            end_card(size, T, f, last_city).convert("RGB").save(frames_dir / f"{k:05d}.png", compress_level=1)
        print("## frames", k)

    wav = out / f"mix-{a.music}.wav"
    mix(wav, dur, a.music, cuts)
    if a.only_audio:
        return
    mp4 = out / f"hero-{a.aspect}-{a.quality}-{a.music}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames_dir / "%05d.png"), "-i", str(wav),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", str(mp4)], check=True)
    print("## wrote", mp4)


if __name__ == "__main__":
    main()
