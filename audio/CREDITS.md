# Audio credits: archlang-cinematic

Every file below is a real recording or a sound designer's library effect, downloaded from a
royalty-free or CC0 source. No music here is AI-generated, and no commercial tracks are used.
The media files are gitignored. `python audio/fetch.py` downloads them again and checks each
SHA-256 against `audio/manifest.json`, which also holds durations, loudness and per-second
loudness envelopes.

## Licences in brief

- **Mixkit Stock Music Free License** ([text](https://mixkit.co/license/#musicFree)): free for
  commercial and non-commercial use in web, social and video-on-demand video, podcasts and ads.
  Attribution is appreciated but not required. It does **not** cover TV or radio broadcast,
  CDs or DVDs, or video games. You may not remix a track into a music-only piece, claim it as
  your own, or register it with a rights-management service such as YouTube Content ID. If a
  claim arrives, forward it to team@mixkit.co.
- **Mixkit Sound Effects Free License** ([text](https://mixkit.co/license/#sfxFree)): free in
  any end product, broadcast included. You may not redistribute a file on its own, as stock, or
  in a template.
- **CC0 1.0** ([text](https://creativecommons.org/publicdomain/zero/1.0/)): public domain.
  Credit is appreciated but not required.

Mixkit forbids redistributing its files on their own. That is why `audio/music/` and
`audio/sfx/` stay out of git.

## Music (candidates)

| File | Title | Author | Source | Licence | Role |
|---|---|---|---|---|---|
| `music/a-new-life-eugenio-mininni-mixkit-543.mp3` | A New Life | Eugenio Mininni | [Mixkit, Film Score](https://mixkit.co/free-stock-music/film-score/) (`assets.mixkit.co/music/543/543.mp3`) | Mixkit Music Free | **Recommended primary.** Hard swell at 24.6 s; start the film about 11.6 s into the track |
| `music/discover-eugenio-mininni-mixkit-587.mp3` | Discover | Eugenio Mininni | [Mixkit, Film Score](https://mixkit.co/free-stock-music/film-score/) (`assets.mixkit.co/music/587/587.mp3`) | Mixkit Music Free | Candidate 2. Swell at 12.6 to 13.4 s with no offset |
| `music/mountains-andrew-ev-mixkit-187.mp3` | Mountains | Andrew Ev | [Mixkit, Uplifting](https://mixkit.co/free-stock-music/mood/uplifting/) (`assets.mixkit.co/music/187/187.mp3`) | Mixkit Music Free | Candidate 3, electronic. Step up at 31.8 s; start about 20 s in |

Fallbacks, not staged here because the sister project archlang-spectacle already uses them:
"Valley Sunset" by Alejandro Magaña (Mixkit 127) and "Vastness" by Andrew Ev (Mixkit 184).

## Sound effects

| File | Title | Author | Source | Licence | Role |
|---|---|---|---|---|---|
| `sfx/mixkit/cinematic-tunnel-reverb-woosh-mixkit-1486.wav` | Cinematic tunnel reverb woosh | Mixkit | [Mixkit Whoosh](https://mixkit.co/free-sound-effects/whoosh/) | Mixkit SFX Free | Transition whoosh |
| `sfx/mixkit/storm-coming-whoosh-mixkit-2408.wav` | Storm coming whoosh | Mixkit | [Mixkit Whoosh](https://mixkit.co/free-sound-effects/whoosh/) | Mixkit SFX Free | Transition whoosh |
| `sfx/mixkit/movie-whoosh-impact-presentation-mixkit-2903.wav` | Movie whoosh impact presentation | Mixkit | [Mixkit Whoosh](https://mixkit.co/free-sound-effects/whoosh/) | Mixkit SFX Free | Transition whoosh with soft landing (end card) |
| `sfx/mixkit/big-cinematic-impact-mixkit-788.mp3` | Big cinematic impact | Mixkit | [Mixkit Impact](https://mixkit.co/free-sound-effects/impact/) | Mixkit SFX Free | Low boom for the city reveal |
| `sfx/mixkit/drum-deep-impact-mixkit-563.wav` | Drum deep impact | Mixkit | [Mixkit Cinematic](https://mixkit.co/free-sound-effects/cinematic/) | Mixkit SFX Free | Deep drum hit for the city reveal (alternative or layer) |
| `sfx/mixkit/magical-stone-slide-mixkit-1528.wav` | Magical stone slide | Mixkit | [Mixkit Slide](https://mixkit.co/free-sound-effects/slide/) | Mixkit SFX Free | Walls rising: stone slide |
| `sfx/mixkit/stone-debris-falling-mixkit-403.wav` | Stone debris falling | Mixkit | [Mixkit Rock](https://mixkit.co/free-sound-effects/rock/) | Mixkit SFX Free | Walls rising: grit layer |
| `sfx/kenney/impactsoft-heavy-001-kenney-impact-sounds.ogg` | impactSoft_heavy_001 | Kenney | [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds) | CC0 | Walls rising: heavy thud at full height |
| `sfx/kenney/impactwood-light-001-kenney-impact-sounds.ogg` | impactWood_light_001 | Kenney | [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds) | CC0 | Furniture landing: wooden tap |
| `sfx/kenney/impactwood-light-003-kenney-impact-sounds.ogg` | impactWood_light_003 | Kenney | [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds) | CC0 | Furniture landing: wooden tap (variation) |
| `sfx/kenney/impactsoft-medium-001-kenney-impact-sounds.ogg` | impactSoft_medium_001 | Kenney | [Kenney Impact Sounds](https://kenney.nl/assets/impact-sounds) | CC0 | Furniture landing: cushioned tap |
| `sfx/mixkit/summer-night-crickets-loop-mixkit-1789.wav` | Summer night crickets loop | Mixkit | [Mixkit Crickets](https://mixkit.co/free-sound-effects/crickets/) | Mixkit SFX Free | Dusk ambience under the orbit (loopable) |
| `sfx/mixkit/urban-park-and-traffic-mixkit-2932.wav` | Urban park and traffic | Mixkit | [Mixkit City](https://mixkit.co/free-sound-effects/city/) | Mixkit SFX Free | Distant city and birds ambience |
| `sfx/mixkit/on-or-off-light-switch-tap-mixkit-2585.wav` | On or off light switch tap | Mixkit | [Mixkit Light](https://mixkit.co/free-sound-effects/light/) | Mixkit SFX Free | Light switch as the interior lights come on |
| `sfx/mixkit/cinematic-wind-swell-mixkit-1170.wav` | Cinematic wind swell | Mixkit | [Mixkit Swell](https://mixkit.co/free-sound-effects/swell/) | Mixkit SFX Free | Riser into the drop |

Mixkit SFX download URLs follow `https://assets.mixkit.co/active_storage/sfx/{id}/{id}.wav`.
Item 788 is the exception: Mixkit serves it only as `.mp3`. The Kenney files come from a
per-file mirror of the official CC0 pack,
`https://cc0-sounds.exi.software/sounds/kenney_impactsounds/Audio/{name}.ogg`. The official
pack zip is on the Kenney page linked above.

## Attribution lines for posts

None of these licences requires attribution. We credit everyone anyway. Use the line that
matches the track in the final cut:

> Music: "A New Life" by Eugenio Mininni via Mixkit. SFX: Mixkit Sound Effects + Kenney Impact Sounds (CC0).

> Music: "Discover" by Eugenio Mininni via Mixkit. SFX: Mixkit Sound Effects + Kenney Impact Sounds (CC0).

> Music: "Mountains" by Andrew Ev via Mixkit. SFX: Mixkit Sound Effects + Kenney Impact Sounds (CC0).
