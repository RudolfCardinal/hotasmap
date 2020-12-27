#!/usr/bin/env bash
set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${THIS_DIR}/set_common_env_vars.sh"

JOYSTICK_OUT="${OUTPUT_DIR}/blank_joystick.png"
THROTTLE_OUT="${OUTPUT_DIR}/blank_throttle.png"
COMPOSITE_OUT="${OUTPUT_DIR}/blank_composite.png"

"${HOTASMAP}" \
    --format blank \
    --joyout "${JOYSTICK_OUT}" \
    --throtout "${THROTTLE_OUT}" \
    --compout "${COMPOSITE_OUT}" \
    --title "${DEVICES_TITLE}" \
    --subtitle "Template for pen-and-paper editing"

rm "${JOYSTICK_OUT}"
rm "${THROTTLE_OUT}"
