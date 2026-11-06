"""Shot 4: exploded axonometric. One GLB separated into its layers (slab, floors, furniture, walls,
roof) per storey, under an orthographic camera."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

PLAN = "hillside-villa"
F_END = 144  # 6 s

a = lib.args()
lib.reset()
sc = lib.setup_render(a, frames=(1, F_END))
sc.view_settings.exposure = -0.2

plan = lib.Plan(lib.BUILD / "glb" / f"{PLAN}.glb", PLAN)
lib.add_ground(lib.BRAND["sheet"], z=-0.4, rough=1.0)
sky = lib.Sky(elev=42, azim=215, sun_strength=4.0, sky_strength=0.35, sky_saturation=0.35)

LAYER = {"slab": 0.0, "floor": 0.9, "furniture": 2.2, "wall": 4.2, "door": 4.2, "window": 4.2, "roof": 8.5}
STOREY_GAP = 9.5
levels = sorted({plan.meta(o, "level", 1) for o in plan.objects if "archlang" in o.keys()})
print("## LEVELS", levels, {k: len(v) for k, v in plan.kind.items()})

movers = []
for o in plan.objects:
    if o.type != "MESH":
        continue
    k = plan.meta(o, "kind", o.name.split(":")[0])
    lvl = plan.meta(o, "level", 1)
    lift = LAYER.get(k, 2.2) + (levels.index(lvl)) * STOREY_GAP if lvl in levels else 0
    if k == "roof" and lvl != levels[-1]:
        lift -= 3.0
    movers.append((o, o.location.z, lift))


def explode_at(f):
    t = lib.smooth((f - 18) / 66)
    for o, z0, lift in movers:
        o.location.z = z0 + lift * t
        o.keyframe_insert("location", index=2, frame=f)


lib.keyframes(1, F_END, explode_at)

mn, mx = plan.bounds()
centre = (mn + mx) / 2
cam = lib.Cam()
cam.data.type = "ORTHO"


def cam_at(f):
    t = f / F_END
    tgt = centre.copy()
    tgt.z = lib.lerp(2.5, 11.5, lib.smooth((f - 18) / 66))
    cam.place(tgt, 120, 30, lib.lerp(28, 62, t), 50, frame=f)
    cam.data.ortho_scale = lib.lerp(31, 50, lib.smooth((f - 18) / 66))
    cam.data.keyframe_insert("ortho_scale", frame=f)


lib.keyframes(1, F_END, cam_at)
lib.run("s04_exploded_axon", a)
