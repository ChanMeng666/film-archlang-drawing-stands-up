#!/usr/bin/env bash
# Final-quality hero stills, one Blender process at a time, then captions.
#   bash scripts/stills.sh [16x9|9x16|1x1]     (2560x1440, 1440x2560 or 2048x2048)
# Each aspect is framed in Blender (the shots' --aspect branches), never cropped from another.
set -e
cd "$(dirname "$0")/.."
ASPECT=${1:-16x9}
case $ASPECT in
  16x9) RES=2560x1440 ;;
  9x16) RES=1440x2560 ;;
  1x1)  RES=2048x2048 ;;
  *) echo "aspect must be 16x9, 9x16 or 1x1" >&2; exit 2 ;;
esac
R="--quality final --aspect $ASPECT --res $RES"
python scripts/render.py s01_stands_up      $R --still 76 156
python scripts/render.py s02_dusk_dollhouse $R --still 168
python scripts/render.py s03_city_of_code   $R --still 192
python scripts/render.py s04_exploded_axon  $R --still 144
if [ "$ASPECT" != 16x9 ]; then  # 05 for these aspects is the code-to-form shot's pulse frame
  python scripts/render.py s05_code_to_form $R --still 214
fi
python compose/stills.py --aspect "$ASPECT"
