#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${THIS_DIR}/set_common_env_vars.sh"

"${HOTASMAP}" \
    --format blank \
    --joyout "${OUTPUT_DIR}/blank_joystick.png" \
    --throtout "${OUTPUT_DIR}/blank_throttle.png" \
    --compout "${OUTPUT_DIR}/blank_composite.png" \
    --title "${DEVICES_TITLE}" \
    --subtitle "Template for pen-and-paper editing"
