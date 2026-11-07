"""Shot 5: code to form. Each wall glows while its own source line is highlighted (compose adds the
code panel), in the compiler's order; then every wall pulses at once. Golden hour, roof off."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import lib  # noqa: E402
from code_to_form_timing import F_END, PULSE, wall_window  # noqa: E402

PLAN = "courtyard-house"

a = lib.args()
V = a.aspect == "9x16"
SQ = a.aspect == "1x1"
lib.reset()
sc = lib.setup_render(a, frames=(1, F_END))
sc.view_settings.exposure = -0.4

plan = lib.Plan(lib.BUILD / "glb" / f"{PLAN}.glb", PLAN)
for o in plan.get("roof"):
    o.hide_render = True
for o in plan.get("floor"):  # finished floors sit just above the drawing
    o.location.z = 0.012
vb = lib.read_viewbox(lib.BUILD / "sheets" / f"{PLAN}.svg")
lib.add_sheet(lib.BUILD / "sheets" / f"{PLAN}.png", vb)
lib.add_ground("#f4f2ee", rough=1.0)
sky = lib.Sky(elev=14, azim=250, sun_strength=7.0, sky_strength=0.25)

# ---- glow: each wall gets its own copy of the wall look, with a keyed plum emission ----
PLUM = lib.lin(lib.BRAND["plum"])
walls = sorted(plan.get("wall"), key=lambda o: plan.meta(o, "order", 0))
print("## WALLS", [plan.meta(o, "id") for o in walls])


def glow(mat, keys):
    """Mix the wall's own shader toward a pure plum emission; keys are (frame, mix factor)."""
    nt = mat.node_tree
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    src = out.inputs["Surface"].links[0].from_socket
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = PLUM
    em.inputs["Strength"].default_value = 1.1  # AgX washes brighter plum out to lavender
    mix = nt.nodes.new("ShaderNodeMixShader")
    nt.links.new(src, mix.inputs[1])
    nt.links.new(em.outputs["Emission"], mix.inputs[2])
    nt.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    sock = mix.inputs["Fac"]
    for f, v in keys:
        sock.default_value = v
        sock.keyframe_insert("default_value", frame=f)


for i, w in enumerate(walls):
    f0, f1 = wall_window(i)
    keys = [(1, 0.0), (f0, 0.0), (f0 + 3, 0.85), (f1 - 2, 0.75), (f1 + 5, 0.0),
            (PULSE - 1, 0.0), (PULSE + 4, 0.85), (PULSE + 20, 0.3), (F_END, 0.3)]
    for slot in w.material_slots:
        if slot.material and slot.material.name.startswith("lk:wall"):
            slot.material = slot.material.copy()
            glow(slot.material, keys)

# ---- camera: slow orbit; the building sits beside (16:9, 1:1) or below (9:16) the code panel ----
mn, mx = plan.bounds()
centre = (mn + mx) / 2
centre.z = 0.5
cam = lib.Cam()
cam.dof(0.9)
width, elev, shift = (24.5, 56.0, (0.0, 0.30)) if V else (33.0, 52.0, (-0.2, 0.0)) if SQ else (31.0, 50.0, (-0.19, 0.0))


def cam_at(f):
    t = lib.smooth(f / F_END)
    dist = 34.0
    cam.place(centre, dist, lib.lerp(elev, elev - 4, t), lib.lerp(18, 46, t),
              lib.Cam.lens_for_width(width * lib.lerp(1.0, 1.0 if V else 1.18, t), dist), frame=f, shift=shift)


lib.keyframes(1, F_END, cam_at)
lib.run("s05_code_to_form", a)
