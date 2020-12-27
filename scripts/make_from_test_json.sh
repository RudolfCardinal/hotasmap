#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${THIS_DIR}/set_common_env_vars.sh"

"${HOTASMAP}" \
    --format json \
    --input "${INPUT_DIR}/test.json" \
    --joyout "${OUTPUT_DIR}/test_joystick.png" \
    --throtout "${OUTPUT_DIR}/test_throttle.png" \
    --compout "${OUTPUT_DIR}/test_composite.png" \
    --title "Test JSON mapping (Elite:Dangerous, superseded)" \
    --subtitle "${DEVICES_TITLE}"
