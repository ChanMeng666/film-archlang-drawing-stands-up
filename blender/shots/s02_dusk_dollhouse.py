"""Shot 2: roofless courtyard house; the sun sets, and each room's light turns on in source order."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

PLAN = "courtyard-house"
F_END = 168  # 7 s

a = lib.args()
V = a.aspect == "9x16"
SQ = a.aspect == "1x1"
lib.reset()
sc = lib.setup_render(a, frames=(1, F_END))

plan = lib.Plan(lib.BUILD / "glb" / f"{PLAN}.glb", PLAN)
for o in plan.get("roof"):
    o.hide_render = True
for o in plan.get("floor"):  # finished floors sit just above the drawing
    o.location.z = 0.012
vb = lib.read_viewbox(lib.BUILD / "sheets" / f"{PLAN}.svg")
lib.add_sheet(lib.BUILD / "sheets" / f"{PLAN}.png", vb)  # still standing on its drawing
lib.add_ground("#f4f2ee", rough=1.0)

sky = lib.Sky(elev=9, azim=250, sun_strength=7.0, sky_strength=0.3, sky_saturation=0.9)
lamps = sorted(lib.room_lights(plan, power_per_m2=7.0), key=lambda lf: plan.meta(lf[1], "order", 0))


def light_at(f):
    t = lib.smooth((f - 1) / 120)
    sky.set(lib.lerp(9, -5, t), lib.lerp(250, 262, t), lib.lerp(7.0, 0.0, lib.smooth((f - 1) / 100)),
            lib.lerp(0.3, 0.55, t), frame=f)
    sky.set_night(lib.smooth((f - 50) / 90), frame=f)
    sc.view_settings.exposure = lib.lerp(-0.3, 0.3, t)
    sc.view_settings.keyframe_insert("exposure", frame=f)


lib.keyframes(1, F_END, light_at)

for i, (ob, floor) in enumerate(lamps):  # on in the compiler's room order
    f0 = 52 + i * 7
    for f in range(f0 - 1, f0 + 13):
        ob.data.energy = ob.data["full"] * lib.ease_out((f - f0) / 12) if f >= f0 else 0.0
        ob.data.keyframe_insert("energy", frame=f)

mn, mx = plan.bounds()
centre = (mn + mx) / 2
centre.z = 0.6
cam = lib.Cam()
cam.dof(0.9)


def cam_at(f):
    t = lib.smooth(f / F_END)
    w0, w1, e0, e1 = (21.5, 19, 52, 44) if V else (23.5, 20.5, 48, 40) if SQ else (25, 22, 44, 36)
    cam.place(centre, lib.lerp(36, 31, t), lib.lerp(e0, e1, t), lib.lerp(40, 112, t),
              lib.Cam.lens_for_width(lib.lerp(w0, w1, t), lib.lerp(36, 31, t)), frame=f)


lib.keyframes(1, F_END, cam_at)
lib.run("s02_dusk_dollhouse", a)
