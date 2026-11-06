"""Tile PNGs into one contact sheet: python scripts/contact.py out.png a.png b.png ... [--cols 2]"""
import sys
from PIL import Image, ImageDraw
args = sys.argv[1:]; cols = 2
if "--cols" in args:
    i = args.index("--cols"); cols = int(args[i + 1]); del args[i:i + 2]
out, files = args[0], args[1:]
ims = [Image.open(f).convert("RGB") for f in files]
w = 960; ims = [im.resize((w, int(im.height * w / im.width))) for im in ims]
h = max(im.height for im in ims); rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w + (cols - 1) * 8, rows * h + (rows - 1) * 8), "#222")
for k, (im, f) in enumerate(zip(ims, files)):
    x, y = (k % cols) * (w + 8), (k // cols) * (h + 8); sheet.paste(im, (x, y))
    ImageDraw.Draw(sheet).text((x + 8, y + 6), f.replace("\\", "/").split("/")[-1], fill="#ff00aa")
sheet.save(out); print(out, sheet.size)
