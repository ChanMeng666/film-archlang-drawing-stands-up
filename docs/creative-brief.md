# Creative brief — ArchLang Cinematic

## The one idea

**A drawing that stands up.** ArchLang turns a few dozen lines of text into a precise, dimensioned
floor plan. The shareable moment is not "a pretty house". It is seeing *that exact drawing* lift off
the paper into a lit building, in perfect register, and knowing a person (or an AI) only wrote text.

Every pixel of architecture on screen is compiler output:

| Layer | Made by | How it reaches Blender |
|---|---|---|
| 2D sheet (walls, dims, title block, north arrow) | `archlang compile -f png -w 6000` | Image texture on a ground plane. SVG user units are plan mm, so the sheet is placed at `viewBox / 1000` metres with y flipped and lands in exact register under the model |
| 3D model (walls, doors, windows, floors, furniture, roof) | `archlang3d build --doors plan` | glTF import. Nodes are named `wall:<id>`, `door:<id>`, `furniture:<kind>_<n>`, `floor:<room>`, so Blender can animate and light by element and by source id |
| Facts in captions (rooms, areas, line counts) | `archlang describe --json`, `wc -l` | Read at compose time, never typed by hand |

Blender only adds what a camera adds: light, lens, time of day, motion and materials. It never
invents walls. The sister project's v1/v2 Blender spectacle built purple solids and helix towers
the compiler never produced, and its own v3 brief threw them out. We keep that rule.

## Why this can travel (the hooks)

1. **Match cut "drawing → building".** A top-down orthographic frame that is indistinguishable
   from the PNG the compiler wrote, then the walls grow straight up out of the ink lines. That is
   the thumbnail and the first 2 seconds.
2. **Dusk dollhouse.** The roof lifts away, the sun sets, and each room's light turns on in source
   order. Warm windows on a blue-hour sky is the most-shared look in architecture visualisation.
3. **City of code.** A drone pull-up over every example plan the compiler ships, laid out as a town
   at night. "14 buildings. 0 drawn by hand." Scale is the spectacle.
4. **Exploded axonometric.** Slab, floors, walls, glazing, furniture and roof separate in layers
   and rotate. Architecture Twitter/Instagram's favourite diagram, made from one GLB.
5. **Code ↔ form.** The source sits beside the model; a line highlights, and the wall with that id
   glows. This proves "text in, building out" and gives developers a reason to share.

## Deliverables (round 1)

Stills (PNG, 16:9 master 2560×1440, plus 1:1 and 9:16 crops):

- `01-drawing-stands-up` — the courtyard house half-risen from its own sheet, golden hour
- `02-dusk-dollhouse` — roofless courtyard house at blue hour, rooms lit
- `03-city-of-code` — aerial night view of every buildable example as a town
- `04-exploded-axon` — exploded layers of the hillside villa
- `05-code-to-form` — source panel + render, ids highlighted

Film:

- `hero-16x9.mp4` (~32 s, 1920×1080, 24 fps), with a real-recording music bed and real SFX, mixed
  to about −14 LUFS for social. Shots: stands-up → dusk orbit → city pull-up (the drop) →
  exploded axon → end card ("Designs that compile." + `npx @chanmeng666/archlang`).
- `hero-9x16.mp4` cut-down after the 16:9 is approved (camera re-framed in Blender, not cropped).

## Look

- Brand: Void `#0f1115`, Plum `#8052ff`, Sheet `#f5f2ea`, Ink `#111111`. Plum is an accent
  (selection glow, code highlight, end card), never the colour of the building.
- Type is 2D and composited after rendering (Inter / Inter Display, JetBrains Mono). No 3D text.
- Materials: warm limewash walls, oak floors, tile in wet rooms, clear glazing. Read the GLB's
  material names (`wall`, `floor:timber`, `fixture:wood`…) and map each to a PBR look in
  `blender/lib.py`.
- Light: Nishita/procedural sky for golden and blue hour; warm 2700 K area lights per room at
  night. No HDRI downloads needed.

## Rules

- No geometry the compiler did not emit. Ground planes, sky and the sheet texture are the only
  additions. Anything ArchLang 3D leaves out (stairs, fences, outdoor) stays out.
- Facts in captions come from `describe --json` at compose time.
- Logo: `brand/archlang-logo-master.svg` is byte-sacred. Recolour only, never redraw.
- Audio: real recordings only, licence and SHA-256 in `audio/manifest.json`; media is gitignored
  and re-fetched by `audio/fetch.py`.
- Laptop budget (Ryzen 7 5700U, integrated Radeon, 15 GB): EEVEE only, one Blender process at a
  time, `preview` quality (960×540, low samples) for iteration, `final` only for approved shots.
