"""Timing shared by the s05 shot (Blender) and compose/code_to_form.py (Pillow): wall i, in the
compiler's order (= source order), glows from WALL_START + i * WALL_STEP for WALL_STEP frames."""
WALL_START = 30
WALL_STEP = 14
PULSE = 206  # every wall at once
F_END = 240  # 10 s @ 24


def wall_window(i):
    f0 = WALL_START + i * WALL_STEP
    return f0, f0 + WALL_STEP
