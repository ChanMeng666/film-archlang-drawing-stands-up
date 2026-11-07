# ArchLang Cinematic

[![The drawing stands up: a floor plan compiled by ArchLang, with the same building's walls rising out of it in 3D](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/01-drawing-stands-up-social.jpg)](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/archlang-cinematic-hero-16x9-1080p.mp4)

<p align="center"><strong>A floor plan written as text, compiled, and then made to stand up.</strong><br>
Blender-rendered promo films and stills for <a href="https://github.com/ChanMeng666/archlang">ArchLang</a>, the open-source language that compiles text into precise floor plans.<br>
▶ <a href="https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/archlang-cinematic-hero-16x9-1080p.mp4">Watch the 32-second hero film</a> · <a href="https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/archlang-cinematic-hero-9x16-1080p.mp4">9:16 vertical</a> · <a href="https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/archlang-cinematic-code-to-form-16x9-1080p.mp4">Code to form (12 s)</a> · <a href="https://github.com/ChanMeng666/archlang-cinematic/releases/tag/v0.4.0">All assets (v0.4.0)</a></p>

Every wall, door, window, room and piece of furniture on screen was produced by the compiler.
`archlang compile` draws the dimensioned sheet, and `archlang3d build` turns the same `.arch`
file into a checked GLB. Blender adds only a camera, light, materials and motion. It invents no
geometry.

## Gallery

| | |
|---|---|
| [![Drawing stands up](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/01-drawing-stands-up-social.jpg)](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/01-drawing-stands-up-social.png) **The drawing stands up.** The compiled sheet, with the building risen out of it in exact register. | [![Dusk dollhouse](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/02-dusk-dollhouse-social.jpg)](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/02-dusk-dollhouse-social.png) **99 lines. 11 rooms. 163 m².** The courtyard house at blue hour, roof off, every room lit. |
| [![City of code](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/03-city-of-code-social.jpg)](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/03-city-of-code-social.png) **13 buildings. None drawn by hand.** Each one stands on a crop of its own compiled sheet. | [![Exploded axonometric](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/04-exploded-axon-social.jpg)](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/04-exploded-axon-social.png) **One file. Every layer.** Slab, floors, furniture, walls and roof of a two-storey villa, separated. |

[![Code to form](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/05-code-to-form-social.jpg)](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/05-code-to-form-social.png)

**Code to form:** the real source of `courtyard-house.arch` beside the building it compiles to.

Every still comes in three aspects, each framed in Blender rather than cropped: 16:9 at 2560×1440,
9:16 at 1440×2560 (`*-9x16`, for Stories) and 1:1 at 2048×2048 (`*-1x1`, for feeds). Captioned
versions (`*-social`) and text-free versions (`*-clean`) are attached to the
[release](https://github.com/ChanMeng666/archlang-cinematic/releases/tag/v0.4.0). In 9:16 and 1:1,
still 05 is the code-to-form clip's last beat: every wall line lit beside every wall.

| 9:16 | 1:1 |
|---|---|
| [![Dusk dollhouse, 9:16](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/02-dusk-dollhouse-social-9x16.jpg)](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/02-dusk-dollhouse-social-9x16.png) | [![Code to form, 1:1](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/05-code-to-form-social-1x1.jpg)](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/05-code-to-form-social-1x1.png) |

## The hero film

32 s, 16:9, 24 fps, scored with real recordings and mixed to −14 LUFS.

| Time | Shot | What happens |
|---|---|---|
| 0:00 | **The drawing stands up** | The camera starts straight down on the compiled plan while the `.arch` source types itself in. The walls then rise out of the ink lines in the compiler's own build order, and the furniture drops into place. |
| 0:06 | **Dusk dollhouse** | The roof is off and the sun sets. Each room's light turns on in source order. |
| 0:13 | **City of code** | The music swells and the camera cranes up over 13 compiled buildings at night. |
| 0:21 | **Exploded axonometric** | One GLB separates into its layers, storey by storey. |
| 0:27 | **End card** | *Designs that compile.* `npx @chanmeng666/archlang` |

Both films are final: 64 EEVEE samples, each rendered on a laptop's integrated GPU in about
6 hours. The 720p review cut stays in [v0.1.0](https://github.com/ChanMeng666/archlang-cinematic/releases/tag/v0.1.0).

| Film | Size | Use |
|---|---|---|
| [`archlang-cinematic-hero-16x9-1080p.mp4`](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/archlang-cinematic-hero-16x9-1080p.mp4) | 1920×1080 | YouTube, X, LinkedIn, websites |
| [`archlang-cinematic-hero-9x16-1080p.mp4`](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/archlang-cinematic-hero-9x16-1080p.mp4) | 1080×1920 | Reels, TikTok, Shorts, Stories |

The vertical cut is re-framed in Blender, not cropped from the 16:9 frames. Each shot sets its own
vertical camera, the city is re-packed into a taller town, and its last frame is fitted by
projecting every plot corner into the camera. Captions sit at the top, clear of the apps' bottom bars.

## Code to form

12.5 s, in 16:9 and 9:16. Each `wall id=…` line of `courtyard-house.arch` lights up while the wall
with that id glows plum in the model, in the compiler's build order. Then all 12 walls pulse at once:
*12 lines. 12 walls.* The ids come from the GLB's `extras.archlang`, so the text and the model are
matched by the compiler, not by hand. The code panel shows the file's real line numbers.

| Film | Size |
|---|---|
| [`archlang-cinematic-code-to-form-16x9-1080p.mp4`](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/archlang-cinematic-code-to-form-16x9-1080p.mp4) | 1920×1080 |
| [`archlang-cinematic-code-to-form-9x16-1080p.mp4`](https://github.com/ChanMeng666/archlang-cinematic/releases/download/v0.4.0/archlang-cinematic-code-to-form-9x16-1080p.mp4) | 1080×1920 |

## How it works

The trick that makes the "drawing stands up" shot possible: **the compiled SVG's user units are
plan millimetres** (x right, y down), and the GLB is in metres with y flipped. A sheet rasterised
by the compiler can therefore be laid on the ground at `viewBox / 1000` and sits in exact register
under the 3D model, title block, dimensions and all.

```
plans/*.arch ──► scripts/build_assets.py ──► build/sheets/*.svg|png   archlang compile
                                         ├─► build/glb/*.glb          archlang3d build --doors plan
                                         └─► build/facts/*.json       archlang describe --json
                         │
blender/shots/sNN_*.py ◄─┘  blender/lib.py: GLB import, materials keyed by the GLB's material
        │                   names, the sheet in register, physical sky, a warm area light per
        │                   room, camera rigs. Motion follows each node's extras.archlang
        │                   (kind, stage, order, level).
        ▼
out/renders/<shot>/frames ──► compose/film.py ──► captions, code panel, end card,
                                                  audio mix (two-pass loudnorm), H.264
```

Facts in captions (line counts, rooms, areas, number of buildings) are read from
`archlang describe --json` and from the source at compose time, never typed by hand.

## Run it

Requirements:

- Node 20+, then `npm install` (pins `@chanmeng666/archlang` 1.56.0 and `@chanmeng666/archlang-3d` 0.3.0)
- [Blender](https://www.blender.org/download/) 5.2 LTS, run headless (`blender -b --python …`). No
  add-on or MCP server is needed; the glTF importer ships with Blender. Put `blender` on `PATH` or set `BLENDER`.
- Python 3.11+ with Pillow, and `ffmpeg` on `PATH`

```bash
npm install
python audio/fetch.py                                          # download the audio, verify each SHA-256
python scripts/build_assets.py                                 # compile every plan: sheets, GLBs, facts
python scripts/render.py s01_stands_up --still 1 70 156        # preview stills (960×540)
python scripts/render.py s01_stands_up --anim --quality review # frames; repeat for s02–s04
python compose/film.py --quality review --music a-new-life     # captions + score + mp4
bash scripts/stills.sh [16x9|9x16|1x1]                         # final stills in one aspect
python scripts/render_final.py                                 # final 1080p film: all shots, then compose
python scripts/render_final.py --aspect 9x16                   # the same for the vertical cut
python scripts/render_final.py --only s05_code_to_form         # the code-to-form clip (add --aspect 9x16)
```

| Quality | Resolution (16:9) | EEVEE samples | Use |
|---|---|---|---|
| `preview` | 960×540 | 16 | iterate on a shot (about 1.5 s per frame on a Ryzen 7 5700U iGPU) |
| `review` | 1280×720 | 24 | full-length cut for approval |
| `final` | 1920×1080 | 64 | release (about 45 s per night frame on the same laptop) |

`scripts/render.py` runs one Blender process at a time at below-normal priority. Renders resume
where they stopped, because existing frames are skipped. `scripts/render_final.py` renders every
shot at `final` quality with 4 threads (`RENDER_THREADS`), waits before each shot until 2 GB of
memory is free (`MIN_FREE_GB`), stops Blender if free memory stays under `LOW_FREE_GB` (default
1 GB) for a minute and resumes when it recovers, logs to `out/film/render-final.log`, then composes
the film. On a
Ryzen 7 5700U the four shots took 22, 80, 16 and 270 minutes; the night city is the slowest.

## Layout

```
plans/          .arch sources (ArchLang examples + Villa La Rotonda from archlang-showcase)
blender/        lib.py and one script per shot
compose/        film.py, stills.py, brand rasteriser, fonts (Inter, JetBrains Mono; SIL OFL)
audio/          manifest.json, fetch.py, CREDITS.md (media is downloaded, not committed)
brand/          official ArchLang marks (recolour only)
docs/           creative-brief.md, post-copy.md
scripts/        asset build, Blender runner, stills batch, contact sheets
```

## Audio

All audio is real recordings. None of it is AI-generated or synthesised.

- Music: "A New Life" by Eugenio Mininni ([Mixkit](https://mixkit.co/free-stock-music/film-score/), Mixkit Stock Music Free License)
- SFX: [Mixkit](https://mixkit.co/free-sound-effects/) (Mixkit Sound Effects Free License) and [Kenney](https://kenney.nl/assets/impact-sounds) Impact Sounds (CC0)

Mixkit's licence does not allow redistributing files on their own, so the media is gitignored.
`audio/fetch.py` re-downloads each file and checks it against the SHA-256 in `audio/manifest.json`.
Full credits, licence terms and two alternative tracks are in [`audio/CREDITS.md`](audio/CREDITS.md).

## Rules this project keeps

- No geometry the compiler did not emit. The ground, the sky and the sheet texture are the only additions.
- `brand/archlang-logo-master.svg` is byte-sacred: recolour only, never redraw.
- The type is 2D and composited after rendering. There is no 3D text.

## Licence

- Code (scripts, Blender and compositing code, docs): [MIT](LICENSE) © 2026 Chan Meng
- Plans: from [ArchLang](https://github.com/ChanMeng666/archlang) and [archlang-showcase](https://github.com/ChanMeng666/archlang-showcase) (MIT)
- Fonts: Inter and JetBrains Mono, SIL Open Font License (texts in `compose/fonts/`)
- Audio: under its own licences (see above). It is not covered by MIT.
- Rendered films and stills: credit ArchLang when reusing them.

## Related

- [ArchLang](https://github.com/ChanMeng666/archlang): the language and compiler · [archlang.uk](https://archlang.uk) · [playground](https://playground.archlang.uk)
- [`@chanmeng666/archlang-3d`](https://www.npmjs.com/package/@chanmeng666/archlang-3d): the GLB and replay builder these renders start from
- [film-archlang-explainer-and-shorts](https://github.com/ChanMeng666/film-archlang-explainer-and-shorts): the bright explainer films
