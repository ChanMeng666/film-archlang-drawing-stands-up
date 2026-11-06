#!/usr/bin/env bash
# Final-quality hero stills (2560x1440), one Blender process at a time, then captions.
set -e
cd "$(dirname "$0")/.."
python scripts/render.py s01_stands_up      --quality final --res 2560x1440 --still 76 156
python scripts/render.py s02_dusk_dollhouse --quality final --res 2560x1440 --still 168
python scripts/render.py s03_city_of_code   --quality final --res 2560x1440 --still 192
python scripts/render.py s04_exploded_axon  --quality final --res 2560x1440 --still 144
python compose/stills.py
