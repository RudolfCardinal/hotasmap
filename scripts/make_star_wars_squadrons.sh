#!/usr/bin/env bash
set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${THIS_DIR}/set_common_env_vars.sh"

JOYSTICK_OUT="${OUTPUT_DIR}/star_wars_squadrons_joystick.png"
THROTTLE_OUT="${OUTPUT_DIR}/star_wars_squadrons_throttle.png"
COMPOSITE_OUT="${OUTPUT_DIR}/star_wars_squadrons_composite.png"

"${HOTASMAP}" \
    --format json \
    --input "${INPUT_DIR}/star_wars_squadrons_2020.json" \
    --joyout "${JOYSTICK_OUT}" \
    --throtout "${THROTTLE_OUT}" \
    --compout "${COMPOSITE_OUT}" \
    --showmapping \
    --title "Star Wars: Squadrons" \
    --subtitle "${DEVICES_TITLE}" \
    --wrap_linesep " │ " \
    --extra_text "CONTROLS → ADVANCED:
► Invert flight = OFF
► Power management = ADVANCED
CONTROLS → FLIGHT STICK:
► Flight stick 1 device =
      Joystick - HOTAS Warthog
► Flight stick 2 device =
      Throttle - HOTAS Warthog
► Flight st. 3 dev. = MFG Crosswind v2

KEY:
○ Press
○○ Double-tap
●… Hold
[F] Flight, [M] Menus, [H] Hangar"

rm "${JOYSTICK_OUT}"
rm "${THROTTLE_OUT}"
