"""Shared Blender helpers for ArchLang Cinematic.

Run shots as:  blender -b --factory-startup --python blender/shots/<shot>.py -- [--quality preview|final]
               [--still FRAME [FRAME ...]] [--anim] [--res WxH]

Everything architectural comes from an ArchLang GLB (archlang3d build) or a compiled sheet PNG
(archlang compile). This module only adds light, lens, materials, motion and the ground.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from pathlib import Path

import bpy
from mathutils import Euler, Vector

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "build"
OUT = ROOT / "out"


# ---------------------------------------------------------------- args / scene

def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--quality", choices=["preview", "review", "final"], default="preview")
    p.add_argument("--still", type=int, nargs="*")
    p.add_argument("--anim", action="store_true")
    p.add_argument("--res", default=None, help="WxH override")
    p.add_argument("--aspect", choices=["16x9", "9x16", "1x1"], default="16x9")
    p.add_argument("--frames", default=None, help="F0-F1 subrange for --anim")
    p.add_argument("--tag", default="", help="suffix for still filenames")
    return p.parse_args(argv)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    prefs = bpy.context.preferences.edit
    prefs.keyframe_new_interpolation_type = "LINEAR"


RES = {"16x9": (1920, 1080), "9x16": (1080, 1920), "1x1": (1440, 1440)}


def setup_render(a, fps=24, frames=(1, 1)):
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    w, h = RES[a.aspect]
    if a.res:
        w, h = (int(v) for v in a.res.lower().split("x"))
    final = a.quality == "final"
    if a.quality == "preview" and not a.res:
        w, h = w // 2, h // 2
    elif a.quality == "review" and not a.res:
        w, h = w * 2 // 3, h * 2 // 3
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.fps = fps
    sc.frame_start, sc.frame_end = frames
    ee = sc.eevee
    ee.taa_render_samples = {"preview": 16, "review": 24, "final": 64}[a.quality]
    ee.use_raytracing = True
    ee.use_shadows = True
    try:
        ee.shadow_resolution_scale = 0.5 if a.quality == "preview" else 1.0
        ee.use_fast_gi = True
        ee.fast_gi_method = "GLOBAL_ILLUMINATION"
    except Exception:
        pass
    vs = sc.view_settings
    for vt, look in (("AgX", "AgX - Medium High Contrast"), ("AgX", "AgX - Base Contrast"), ("Filmic", "None")):
        try:
            vs.view_transform = vt
            vs.look = look
            break
        except TypeError:
            continue
    sc.render.film_transparent = False
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    sc.render.image_settings.compression = 30
    return sc


# ---------------------------------------------------------------- colour + materials

def lin(hexstr: str, a: float = 1.0):
    hexstr = hexstr.lstrip("#")
    c = [int(hexstr[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return (*c, a)


BRAND = {"void": "#0f1115", "plum": "#8052ff", "sheet": "#f5f2ea", "ink": "#111111"}

_MAT_CACHE: dict[str, bpy.types.Material] = {}


def principled(name, color, rough=0.6, metal=0.0, transmission=0.0, alpha=1.0,
               emission=None, emission_strength=0.0, noise=0.0, noise_scale=8.0, bump=0.0,
               blended=False):
    if name in _MAT_CACHE:
        return _MAT_CACHE[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = lin(color)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    bsdf.inputs["Transmission Weight"].default_value = transmission
    bsdf.inputs["Alpha"].default_value = alpha
    if emission:
        bsdf.inputs["Emission Color"].default_value = lin(emission)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    if noise > 0 or bump > 0:
        tc = nt.nodes.new("ShaderNodeTexCoord")
        nz = nt.nodes.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = noise_scale
        nz.inputs["Detail"].default_value = 6.0
        nt.links.new(tc.outputs["Object"], nz.inputs["Vector"])
        if noise > 0:
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs["Factor"].default_value = noise
            mix.inputs[6].default_value = lin(color)
            nt.links.new(nz.outputs["Color"], mix.inputs[7])
            nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
        if bump > 0:
            b = nt.nodes.new("ShaderNodeBump")
            b.inputs["Strength"].default_value = bump
            nt.links.new(nz.outputs["Fac"], b.inputs["Height"])
            nt.links.new(b.outputs["Normal"], bsdf.inputs["Normal"])
    if blended or alpha < 1.0:
        m.surface_render_method = "BLENDED"
    _MAT_CACHE[name] = m
    return m


def timber_floor():
    if "lk:timber" in _MAT_CACHE:
        return _MAT_CACHE["lk:timber"]
    m = principled("lk:timber", "#b48558", rough=0.45)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")  # planks: long thin bricks, hairline joints
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.004
    brick.inputs["Brick Width"].default_value = 1.8
    brick.inputs["Row Height"].default_value = 0.19
    brick.offset = 0.37
    brick.inputs["Color1"].default_value = lin("#b98b5c")
    brick.inputs["Color2"].default_value = lin("#a3764a")
    brick.inputs["Mortar"].default_value = lin("#6e4e30")
    nt.links.new(tc.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def tile_floor():
    if "lk:tile" in _MAT_CACHE:
        return _MAT_CACHE["lk:tile"]
    m = principled("lk:tile", "#dcd9d3", rough=0.25)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.006
    brick.inputs["Brick Width"].default_value = 0.6
    brick.inputs["Row Height"].default_value = 0.6
    brick.offset = 0.0
    brick.inputs["Color1"].default_value = lin("#e2dfd9")
    brick.inputs["Color2"].default_value = lin("#d6d2cb")
    brick.inputs["Mortar"].default_value = lin("#a8a39b")
    nt.links.new(tc.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    return m


def glass():
    return principled("lk:glass", "#cfe3ea", rough=0.03, alpha=0.18, blended=True)


LOOK = {
    "wall": lambda: principled("lk:wall", "#efe9df", rough=0.9, noise=0.08, noise_scale=3, bump=0.04),
    "slab": lambda: principled("lk:slab", "#bdb7ad", rough=0.95, noise=0.12, noise_scale=2),
    "roof": lambda: principled("lk:roof", "#6c675f", rough=0.85, noise=0.1),
    "door": lambda: principled("lk:door", "#9b7451", rough=0.55, noise=0.08, noise_scale=20),
    "window:frame": lambda: principled("lk:frame", "#2c2c30", rough=0.35, metal=0.7),
    "window:glass": glass,
    "floor:timber": timber_floor,
    "floor:tile": tile_floor,
    "floor:": lambda: principled("lk:floor", "#cbc4b8", rough=0.7),
    "fixture:wood": lambda: principled("lk:wood", "#a87d52", rough=0.5, noise=0.1, noise_scale=25),
    "fixture:wood_dark": lambda: principled("lk:wood_dark", "#5a3f2b", rough=0.45),
    "fixture:ceramic": lambda: principled("lk:ceramic", "#f4f3ef", rough=0.12),
    "fixture:metal": lambda: principled("lk:metal", "#b9b9b9", rough=0.28, metal=1.0),
    "fixture:linen": lambda: principled("lk:linen", "#ece6da", rough=0.95),
    "fixture:wool": lambda: principled("lk:wool", "#8a8f9a", rough=1.0),
    "fixture:stone": lambda: principled("lk:stone", "#d3cdc3", rough=0.45, noise=0.1, noise_scale=6),
    "fixture:paint": lambda: principled("lk:paint", "#e4e0d8", rough=0.6),
    "fixture:rubber": lambda: principled("lk:rubber", "#262626", rough=0.9),
    "fixture:appliance": lambda: principled("lk:appliance", "#ececea", rough=0.25),
    "fixture:screen": lambda: principled("lk:screen", "#101114", rough=0.08),
    "fixture:foliage": lambda: principled("lk:foliage", "#4d7a3a", rough=0.8, noise=0.25, noise_scale=12),
    "fixture:fabric": lambda: principled("lk:fabric", "#6f7d8c", rough=0.95),
    "fixture:cushion": lambda: principled("lk:cushion", "#cdb998", rough=0.95),
    "fixture:glass": glass,
    "fixture:water": lambda: principled("lk:water", "#5b9db3", rough=0.04, alpha=0.6, blended=True),
    "fixture:": lambda: principled("lk:fixture", "#cfcac2", rough=0.6),
}


def look_for(name: str):
    if name in LOOK:
        return LOOK[name]()
    for key in sorted(LOOK, key=len, reverse=True):
        if key.endswith(":") and name.startswith(key):
            return LOOK[key]()
    return None


def restyle(objs):
    for o in objs:
        if o.type != "MESH":
            continue
        for slot in o.material_slots:
            if slot.material is None:
                continue
            new = look_for(slot.material.name.split(".")[0])
            if new is not None:
                slot.material = new


# ---------------------------------------------------------------- plan import

class Plan:
    """One imported GLB under a root empty, grouped by node kind."""

    def __init__(self, glb: Path, name: str, offset=(0.0, 0.0, 0.0), yaw_deg=0.0):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(glb))
        new = [o for o in bpy.data.objects if o not in before]
        self.root = bpy.data.objects.new(f"plan:{name}", None)
        bpy.context.scene.collection.objects.link(self.root)
        for o in new:
            if o.parent is None:
                o.parent = self.root
        self.root.location = offset
        self.root.rotation_euler = (0, 0, math.radians(yaw_deg))
        self.objects = new
        self.kind: dict[str, list] = {}
        for o in new:
            k = o.get("archlang", {}).get("kind") if "archlang" in o.keys() else None
            k = k or o.name.split(":")[0]
            self.kind.setdefault(k, []).append(o)
        restyle(new)
        bpy.context.view_layer.update()

    def get(self, *kinds):
        return [o for k in kinds for o in self.kind.get(k, [])]

    def meta(self, o, key, default=None):
        return dict(o["archlang"]).get(key, default) if "archlang" in o.keys() else default

    def bounds(self, kinds=("wall",)):
        pts = [o.matrix_world @ Vector(c) for o in self.get(*kinds) for c in o.bound_box]
        mn = Vector([min(p[i] for p in pts) for i in range(3)])
        mx = Vector([max(p[i] for p in pts) for i in range(3)])
        return mn, mx


def world_bounds(o):
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    mn = Vector([min(p[i] for p in pts) for i in range(3)])
    mx = Vector([max(p[i] for p in pts) for i in range(3)])
    return mn, mx


def read_viewbox(svg: Path):
    import re
    head = svg.read_text(encoding="utf-8")[:600]
    x, y, w, h = (float(v) for v in re.search(r'viewBox="([^"]+)"', head).group(1).split())
    return x, y, w, h


def add_sheet(png: Path, viewbox, z=0.006, name="sheet", ink_gamma=2.6):
    """The compiled sheet as a ground texture, in exact register with the GLB.

    SVG user units are plan millimetres, x right / y down. The GLB is metres with y flipped.
    """
    x, y, w, h = viewbox
    bpy.ops.mesh.primitive_plane_add(size=1)
    p = bpy.context.active_object
    p.name = name
    p.scale = (w / 1000, h / 1000, 1)
    p.location = ((x + w / 2) / 1000, -(y + h / 2) / 1000, z)
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(png))
    tex.interpolation = "Cubic"
    gamma = nt.nodes.new("ShaderNodeGamma")  # ink reads darker; paper stays white
    gamma.inputs["Gamma"].default_value = ink_gamma
    nt.links.new(tex.outputs["Color"], gamma.inputs["Color"])
    nt.links.new(gamma.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.92
    p.data.materials.append(m)
    return p


def add_ground(color="#f3f1ec", size=600, z=-0.03, rough=0.95, name="ground"):
    bpy.ops.mesh.primitive_plane_add(size=size, location=(0, 0, z))
    g = bpy.context.active_object
    g.name = name
    g.data.materials.append(principled(f"lk:{name}", color, rough=rough))
    return g


# ---------------------------------------------------------------- light

def sun_direction(elev_deg, azim_deg):
    e, a = math.radians(elev_deg), math.radians(azim_deg)
    return Vector((math.cos(e) * math.sin(a), math.cos(e) * math.cos(a), math.sin(e)))


class Sky:
    """Physical sky + matching sun lamp; animate with .set(elev, azim, frame)."""

    def __init__(self, elev=8.0, azim=230.0, sun_strength=4.0, sky_strength=1.0, sky_saturation=0.5):
        w = bpy.data.worlds.new("sky")
        bpy.context.scene.world = w
        w.use_nodes = True
        nt = w.node_tree
        self.bg = nt.nodes["Background"]
        self.tex = nt.nodes.new("ShaderNodeTexSky")
        self.tex.sky_type = "MULTIPLE_SCATTERING"
        self.tex.sun_disc = False
        self.hsv = nt.nodes.new("ShaderNodeHueSaturation")  # tame the blue fill
        self.hsv.inputs["Saturation"].default_value = sky_saturation
        nt.links.new(self.tex.outputs["Color"], self.hsv.inputs["Color"])
        self.night = nt.nodes.new("ShaderNodeMix")  # blend toward a deep blue-hour ambient
        self.night.data_type = "RGBA"
        self.night.inputs["Factor"].default_value = 0.0
        self.night.inputs[7].default_value = lin("#33508f")
        nt.links.new(self.hsv.outputs["Color"], self.night.inputs[6])
        nt.links.new(self.night.outputs[2], self.bg.inputs["Color"])
        self.bg.inputs["Strength"].default_value = sky_strength
        lamp = bpy.data.lights.new("sun", "SUN")
        lamp.angle = math.radians(1.5)
        self.sun = bpy.data.objects.new("sun", lamp)
        bpy.context.scene.collection.objects.link(self.sun)
        self.set(elev, azim, sun_strength, sky_strength)

    def set_night(self, fac, frame=None):
        self.night.inputs["Factor"].default_value = fac
        if frame is not None:
            self.night.inputs["Factor"].keyframe_insert("default_value", frame=frame)

    def set(self, elev, azim, sun_strength=None, sky_strength=None, frame=None):
        self.tex.sun_elevation = math.radians(elev)
        self.tex.sun_rotation = math.radians(azim)
        d = sun_direction(elev, azim)
        self.sun.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        # warmer and weaker as the sun drops
        t = max(0.0, min(1.0, (elev + 2) / 30))
        self.sun.data.color = (1.0, 0.50 + 0.42 * t, 0.26 + 0.64 * t)
        if sun_strength is not None:
            self.sun.data.energy = sun_strength
        if sky_strength is not None:
            self.bg.inputs["Strength"].default_value = sky_strength
        if frame is not None:
            self.tex.keyframe_insert("sun_elevation", frame=frame)
            self.tex.keyframe_insert("sun_rotation", frame=frame)
            self.sun.keyframe_insert("rotation_euler", frame=frame)
            self.sun.data.keyframe_insert("color", frame=frame)
            self.sun.data.keyframe_insert("energy", frame=frame)
            self.bg.inputs["Strength"].keyframe_insert("default_value", frame=frame)


def room_lights(plan: Plan, power_per_m2=9.0, height=2.55, color=(1.0, 0.64, 0.34)):
    """A warm ceiling area light over every floor the compiler emitted. Returns [(light, floor)]."""
    out = []
    for f in plan.get("floor"):
        mn, mx = world_bounds(f)
        sx, sy = mx.x - mn.x, mx.y - mn.y
        if sx < 0.4 or sy < 0.4:
            continue
        lamp = bpy.data.lights.new(f"lamp:{f.name}", "AREA")
        lamp.shape = "RECTANGLE"
        k = 0.85 if sx * sy > 60 else 0.55  # spread big halls instead of a hot spot
        lamp.size, lamp.size_y = sx * k, sy * k
        lamp.color = color
        lamp.energy = power_per_m2 * (sx * sy) ** 0.8 * 1.6  # big halls glow, not blow out
        lamp["full"] = lamp.energy
        ob = bpy.data.objects.new(lamp.name, lamp)
        ob.location = ((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z + height)
        bpy.context.scene.collection.objects.link(ob)
        out.append((ob, f))
    return out


# ---------------------------------------------------------------- motion

def smooth(t):  # smootherstep
    t = max(0.0, min(1.0, t))
    return t * t * t * (t * (t * 6 - 15) + 10)


def ease_out(t, p=3):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** p


def ease_out_back(t, s=1.4):
    t = max(0.0, min(1.0, t)) - 1
    return t * t * ((s + 1) * t + s) + 1


def lerp(a, b, t):
    return a + (b - a) * t


def keyframes(f0, f1, fn):
    """Call fn(frame) and let it insert keys for every frame f0..f1."""
    for f in range(f0, f1 + 1):
        fn(f)


def grow(o, f0, f1, ease=ease_out):
    """Scale an object's z from 0 to 1 (GLB nodes have origin at world 0, floor at z=0)."""
    for f in (f0 - 1, f1 + 1):
        o.scale.z = 1e-4 if f < f0 else 1.0
        o.keyframe_insert("scale", index=2, frame=f)
    for f in range(f0, f1 + 1):
        o.scale.z = max(1e-4, ease((f - f0) / max(1, f1 - f0)))
        o.keyframe_insert("scale", index=2, frame=f)


def drop(o, f0, f1, height=2.5, ease=ease_out_back):
    for f in range(f0 - 1, f1 + 1):
        t = (f - f0) / max(1, f1 - f0)
        o.location.z = height * (1 - ease(t)) if f >= f0 else height
        o.keyframe_insert("location", index=2, frame=f)
    o.hide_render = True
    o.keyframe_insert("hide_render", frame=f0 - 1)
    o.hide_render = False
    o.keyframe_insert("hide_render", frame=f0)


def show_from(o, frame):
    o.hide_render = True
    o.keyframe_insert("hide_render", frame=frame - 1)
    o.hide_render = False
    o.keyframe_insert("hide_render", frame=frame)


class Cam:
    """A camera driven by (target, distance, elevation, azimuth, lens), keyed every frame."""

    def __init__(self, name="cam", clip_end=2000):
        self.data = bpy.data.cameras.new(name)
        self.data.clip_end = clip_end
        self.data.sensor_fit = "HORIZONTAL"
        self.data.sensor_width = 36
        self.ob = bpy.data.objects.new(name, self.data)
        bpy.context.scene.collection.objects.link(self.ob)
        bpy.context.scene.camera = self.ob
        self._prev = None

    def dof(self, fstop):
        self.data.dof.use_dof = True
        self.data.dof.aperture_fstop = fstop
        self.data.dof.aperture_blades = 7

    def place(self, target, dist, elev_deg, azim_deg, lens, roll_deg=0.0, frame=None, shift=(0, 0),
              focus=None):
        target = Vector(target)
        e, a = math.radians(elev_deg), math.radians(azim_deg)
        offset = Vector((math.cos(e) * math.sin(a), -math.cos(e) * math.cos(a), math.sin(e))) * dist
        self.ob.location = target + offset
        q = (target - self.ob.location).to_track_quat("-Z", "Y")
        eul = q.to_euler()
        if elev_deg > 89.5:  # straight down: keep north up
            eul = Euler((0, 0, math.radians(azim_deg)))
        if roll_deg:
            eul.rotate_axis("Z", math.radians(roll_deg))
        if self._prev is not None:
            eul.make_compatible(self._prev)
        self._prev = eul.copy()
        self.ob.rotation_euler = eul
        self.data.lens = lens
        self.data.shift_x, self.data.shift_y = shift
        self.data.clip_start = max(0.05, dist * 0.01)
        self.data.dof.focus_distance = focus if focus is not None else dist
        if frame is not None:
            self.data.keyframe_insert("clip_start", frame=frame)
            self.data.dof.keyframe_insert("focus_distance", frame=frame)
            self.ob.keyframe_insert("location", frame=frame)
            self.ob.keyframe_insert("rotation_euler", frame=frame)
            self.data.keyframe_insert("lens", frame=frame)
            self.data.keyframe_insert("shift_x", frame=frame)
            self.data.keyframe_insert("shift_y", frame=frame)

    @staticmethod
    def lens_for_width(width_m, dist, sensor=36):
        return sensor * dist / width_m


# ---------------------------------------------------------------- output

def out_dir(shot: str, a) -> Path:
    d = OUT / "renders" / f"{shot}-{a.aspect}-{a.quality}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run(shot: str, a):
    sc = bpy.context.scene
    d = out_dir(shot, a)
    if a.still:
        for f in a.still:
            sc.frame_set(f)
            sc.render.filepath = str(d / f"still-{f:04d}{a.tag}.png")
            bpy.ops.render.render(write_still=True)
            print("WROTE", sc.render.filepath)
    if a.anim:
        if a.frames:
            sc.frame_start, sc.frame_end = (int(v) for v in a.frames.split("-"))
        sc.render.filepath = str(d / "frames" / "f_####")
        sc.render.use_overwrite = False  # resumable
        sc.render.use_placeholder = True
        bpy.ops.render.render(animation=True)
        print("WROTE_ANIM", d / "frames")
    if os.environ.get("ARCH_SAVE_BLEND"):
        bpy.ops.wm.save_as_mainfile(filepath=str(d / f"{shot}.blend"))


def facts(name: str) -> dict:
    p = BUILD / "facts" / f"{name}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def add_sheet_crop(png: Path, viewbox, region, z=0.006, name="sheet", ink_gamma=2.6, parent=None):
    """A rectangle of the compiled sheet, still in register: region = (x0, y0, x1, y1) world metres."""
    import bmesh
    vx, vy, vw, vh = viewbox
    x0, y0, x1, y1 = region
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z)) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    face = bm.faces.new(vs)
    uv = bm.loops.layers.uv.new("UVMap")
    for loop in face.loops:
        X, Y = loop.vert.co.x, loop.vert.co.y
        loop[uv].uv = ((X * 1000 - vx) / vw, 1 - ((-Y * 1000) - vy) / vh)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    if parent is not None:
        ob.parent = parent
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(str(png))
    tex.interpolation = "Cubic"
    tex.extension = "CLIP"
    gamma = nt.nodes.new("ShaderNodeGamma")
    gamma.inputs["Gamma"].default_value = ink_gamma
    nt.links.new(tex.outputs["Color"], gamma.inputs["Color"])
    nt.links.new(gamma.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.92
    me.materials.append(m)
    return ob


def sheet_files(name: str):
    """(svg, png, png2k) for a plan; multi-storey plans use their ground-level sheet."""
    s = BUILD / "sheets"
    if (s / f"{name}.svg").exists():
        return s / f"{name}.svg", s / f"{name}.png", s / f"{name}-2k.png"
    return s / f"{name}.L1.svg", s / f"{name}.L1.png", s / f"{name}-2k.L1.png"
