"""Shot 1: the compiled sheet, seen straight down, stands up into the building at golden hour."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

PLAN = "courtyard-house"
F_END = 156  # 6.5 s @ 24

a = lib.args()
lib.reset()
sc = lib.setup_render(a, frames=(1, F_END))
sc.view_settings.exposure = -0.4

plan = lib.Plan(lib.BUILD / "glb" / f"{PLAN}.glb", PLAN)
for o in plan.get("roof", "slab", "floor"):  # the drawing is the floor in this shot
    o.hide_render = True
vb = lib.read_viewbox(lib.BUILD / "sheets" / f"{PLAN}.svg")
lib.add_sheet(lib.BUILD / "sheets" / f"{PLAN}.png", vb)
lib.add_ground("#f4f2ee", rough=1.0)

# sunset side from describe(): W
sky = lib.Sky(elev=11, azim=250, sun_strength=8.0, sky_strength=0.22)

mn, mx = plan.bounds()
centre = (mn + mx) / 2
centre.z = 0.0

# ---- build sequence, in the compiler's own order (extras.archlang.order) ----
walls = sorted(plan.get("wall"), key=lambda o: plan.meta(o, "order", 0))
for i, w in enumerate(walls):
    f0 = 34 + i * 4
    lib.grow(w, f0, f0 + 40)
openings = plan.get("door", "window")
for o in openings:
    lib.grow(o, 60, 104)
furn = sorted(plan.get("furniture"), key=lambda o: (lib.world_bounds(o)[0].x, -lib.world_bounds(o)[0].y))
for i, o in enumerate(furn):
    f0 = 98 + i * 2
    lib.drop(o, f0, f0 + 14, height=1.6)

# ---- camera: straight-down "this is the PNG" → low golden three-quarter ----
cam = lib.Cam()
cam.dof(0.6)
sheet_w = 30.0  # metres of sheet across the frame at the start
top = {"target": lib.Vector(((vb[0] + vb[2] / 2) / 1000, -(vb[1] + vb[3] / 2) / 1000, 0))}


def cam_at(f):
    t = lib.smooth((f - 20) / (F_END - 20))
    tgt = centre
    dist = lib.lerp(320.0, 34.0, lib.ease_out(t, 2))
    elev = lib.lerp(89.9, 31.0, t)
    azim = lib.lerp(0.0, 34.0, t)
    width = lib.lerp(sheet_w, 22.0, t)
    lens = lib.Cam.lens_for_width(width, dist)
    shift_x = 0.0 if a.still else lib.lerp(-0.19, 0.0, lib.smooth((f - 60) / 50))  # film: plan right of the code panel
    cam.place(tgt, dist, elev, azim, lens, frame=f, shift=(shift_x, 0.0))


lib.keyframes(1, F_END, cam_at)
lib.run("s01_stands_up", a)
