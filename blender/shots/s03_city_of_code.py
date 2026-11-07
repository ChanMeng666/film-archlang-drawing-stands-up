"""Shot 3: every buildable plan, each standing on a crop of its own compiled sheet, lit at night.
The camera cranes up from one house to the whole town."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402

F_END = 192  # 8 s
MARGIN, STREET, ROW_W = 4.0, 3.0, 125.0

a = lib.args()
V = a.aspect == "9x16"
SQ = a.aspect == "1x1"
TOWN_ASPECT = 0.62 if V else 1.1 if SQ else 1.75  # town w/h that fills the frame at the end elevation
lib.reset()
sc = lib.setup_render(a, frames=(1, F_END))
sc.view_settings.exposure = 0.15

names = sorted(p.stem for p in (lib.BUILD / "glb").glob("*.glb"))
plans = []
for n in names:
    p = lib.Plan(lib.BUILD / "glb" / f"{n}.glb", n)
    for o in p.get("roof"):
        o.hide_render = True
    for o in p.get("floor"):
        o.location.z += 0.012
    mn, mx = p.bounds()
    region = (mn.x - MARGIN, mn.y - MARGIN, mx.x + MARGIN, mx.y + MARGIN)
    svg, _png, png2k = lib.sheet_files(n)
    lib.add_sheet_crop(png2k, lib.read_viewbox(svg), region, name=f"sheet:{n}", parent=p.root)
    plans.append((p, region))

# shelf-pack the plots, tallest first; pick the row width whose town is closest to 16:9
plans.sort(key=lambda pr: -(pr[1][3] - pr[1][1]))


def pack(row_w):
    rows, row, x = [], [], 0.0
    for i, (_p, (x0, y0, x1, y1)) in enumerate(plans):
        w = x1 - x0
        if row and x + w > row_w:
            rows.append(row)
            row, x = [], 0.0
        row.append((i, x))
        x += w + STREET
    rows.append(row)
    widths = [r[-1][1] + (plans[r[-1][0]][1][2] - plans[r[-1][0]][1][0]) for r in rows]
    max_w = max(widths)
    spots, y = [None] * len(plans), 0.0
    for r, rw in zip(rows, widths):
        row_h = max(plans[i][1][3] - plans[i][1][1] for i, _ in r)
        for i, x in r:
            x0, y0, x1, y1 = plans[i][1]
            spots[i] = (x + (max_w - rw) / 2 - x0, y - y1 - (row_h - (y1 - y0)) / 2)
        y -= row_h + STREET
    return spots, max_w, -y - STREET


best = min((pack(rw) for rw in range(30, 420, 5)),
           key=lambda r: abs(r[1] / r[2] - TOWN_ASPECT) + 0.002 * (r[1] * r[2]) ** 0.5)
for (p, _), (ox, oy) in zip(plans, best[0]):
    p.root.location = (ox, oy, 0)
lib.bpy.context.view_layer.update()
xs, ys = [], []
for p, (x0, y0, x1, y1) in plans:
    xs += [x0 + p.root.location.x, x1 + p.root.location.x]
    ys += [y0 + p.root.location.y, y1 + p.root.location.y]
for p, (x0, y0, x1, y1) in plans:
    print("## PLOT", p.root.name, [round(v, 1) for v in (x0 + p.root.location.x, y0 + p.root.location.y, x1 + p.root.location.x, y1 + p.root.location.y)])
total_w, total_h = max(xs) - min(xs), max(ys) - min(ys)
centre = lib.Vector(((max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, 0))
END_W = (max(total_w, total_h * 0.88 * (9 / 16 if V else 1.0)) if V or SQ else max(total_w, total_h * 16 / 9)) * 1.08

lib.add_ground("#10141f", size=1200, rough=0.6)
sky = lib.Sky(elev=-6, azim=250, sun_strength=0.0, sky_strength=0.5, sky_saturation=0.9)
sky.set_night(1.0)
n_lamps = 0
for p, _ in plans:
    n_lamps += len(lib.room_lights(p, power_per_m2=7.0))
print("## CITY", len(plans), "plans,", n_lamps, "lamps, extent", round(total_w), "x", round(total_h), "m")

# hero: start close on the courtyard house, crane up to the whole town
hero = next(p for p, _ in plans if p.root.name == "plan:courtyard-house")
hmn, hmx = hero.bounds()
hc = (hmn + hmx) / 2
hc.z = 1.0
cam = lib.Cam()
cam.dof(2.0)


FIT = [1.0, 0.0, 0.0]  # end-frame correction: width scale, shift x, shift y (vertical only)


def cam_at(f, key=True):
    t = lib.smooth((f - 8) / (F_END - 8))
    tgt = hc.lerp(centre, lib.smooth((f - 20) / (F_END - 20)))
    dist = lib.lerp(26, END_W * 1.3, lib.ease_out(t, 2.2))
    k = lib.ease_out(t, 2.2)
    width = lib.lerp(19 if V else 24, END_W * lib.lerp(1.0, FIT[0], k), k)
    cam.place(tgt, dist, lib.lerp(24, 62, t), lib.lerp(30, 6, t), lib.Cam.lens_for_width(width, dist),
              frame=f if key else None, shift=(FIT[1] * k, FIT[2] * k))


if V or SQ:  # perspective makes the near rows larger: fit the town's corners into the last frame
    from bpy_extras.object_utils import world_to_camera_view
    corners = [lib.Vector((x, y, 0)) for p, (x0, y0, x1, y1) in plans
               for x, y in ((x0 + p.root.location.x, y0 + p.root.location.y), (x1 + p.root.location.x, y0 + p.root.location.y),
                            (x0 + p.root.location.x, y1 + p.root.location.y), (x1 + p.root.location.x, y1 + p.root.location.y))]

    def measure():
        cam_at(F_END, key=False)
        lib.bpy.context.view_layer.update()
        uv = [world_to_camera_view(sc, cam.ob, c) for c in corners]
        us, vs = [q.x for q in uv], [q.y for q in uv]
        return min(us), max(us), min(vs), max(vs)

    for _ in range(6):
        u0, u1, v0, v1 = measure()
        FIT[0] *= max((u1 - u0) / 0.92, (v1 - v0) / 0.90)
        u0, u1, v0, v1 = measure()
        base = ((u0 + u1) / 2, (v0 + v1) / 2)
        FIT[1] += 0.01
        du = ((sum(measure()[:2]) / 2) - base[0]) / 0.01
        FIT[1] -= 0.01
        FIT[2] += 0.01
        dv = ((sum(measure()[2:]) / 2) - base[1]) / 0.01
        FIT[2] -= 0.01
        FIT[1] -= (base[0] - 0.5) / du
        FIT[2] -= (base[1] - (0.47 if V else 0.52)) / dv  # a little low: the caption sits on top
    print("## FIT", [round(v, 3) for v in FIT], [round(v, 3) for v in measure()])
    cam._prev = None

lib.keyframes(1, F_END, cam_at)
lib.run("s03_city_of_code", a)
