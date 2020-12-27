#!/usr/bin/env bash
set -e
THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${THIS_DIR}/set_common_env_vars.sh"

JOYSTICK_OUT="${OUTPUT_DIR}/test_joystick.png"
THROTTLE_OUT="${OUTPUT_DIR}/test_throttle.png"
COMPOSITE_OUT="${OUTPUT_DIR}/test_composite.png"

"${HOTASMAP}" \
    --format json \
    --input "${INPUT_DIR}/test.json" \
    --joyout "${JOYSTICK_OUT}" \
    --throtout "${THROTTLE_OUT}" \
    --compout "${COMPOSITE_OUT}" \
    --title "Test JSON mapping (Elite:Dangerous, superseded)" \
    --subtitle "${DEVICES_TITLE}"

rm "${JOYSTICK_OUT}"
rm "${THROTTLE_OUT}"
