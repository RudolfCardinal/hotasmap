#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${THIS_DIR}/set_common_env_vars.sh"

"${HOTASMAP}" \
    --format json \
    --input "${INPUT_DIR}/star_wars_squadrons_2020.json" \
    --joyout "${OUTPUT_DIR}/star_wars_squadrons_joystick.png" \
    --throtout "${OUTPUT_DIR}/star_wars_squadrons_throttle.png" \
    --compout "${OUTPUT_DIR}/star_wars_squadrons_composite.png" \
    --title "Star Wars: Squadrons" \
    --subtitle "${DEVICES_TITLE}"
