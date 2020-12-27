#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${THIS_DIR}/set_common_env_vars.sh"

"${HOTASMAP}" \
    --format demo \
    --joyout "${OUTPUT_DIR}/demo_joystick.png" \
    --throtout "${OUTPUT_DIR}/demo_throttle.png" \
    --compout "${OUTPUT_DIR}/demo_composite.png" \
    --title "${DEVICES_TITLE}" \
    --subtitle "Switch names"
