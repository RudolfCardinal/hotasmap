#!/usr/bin/env bash
set -e

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${THIS_DIR}/set_common_env_vars.sh"

JOYSTICK_OUT="${OUTPUT_DIR}/elite_dangerous_joystick.png"
THROTTLE_OUT="${OUTPUT_DIR}/elite_dangerous_throttle.png"
COMPOSITE_OUT="${OUTPUT_DIR}/elite_dangerous_composite.png"

"${HOTASMAP}" \
    --format ed \
    --input "${INPUT_DIR}/Custom.2.0_2018_01_21.binds" \
    --joyout "${JOYSTICK_OUT}" \
    --throtout "${THROTTLE_OUT}" \
    --compout "${COMPOSITE_OUT}" \
    --title "Elite:Dangerous" \
    --subtitle "${DEVICES_TITLE}"

rm "${JOYSTICK_OUT}"
rm "${THROTTLE_OUT}"
