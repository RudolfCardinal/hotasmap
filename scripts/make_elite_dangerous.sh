#!/usr/bin/env bash

THIS_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

source "${THIS_DIR}/set_common_env_vars.sh"

"${HOTASMAP}" \
    --format ed \
    --input "${INPUT_DIR}/Custom.2.0_2018_01_21.binds" \
    --joyout "${OUTPUT_DIR}/elite_dangerous_joystick.png" \
    --throtout "${OUTPUT_DIR}/elite_dangerous_throttle.png" \
    --compout "${OUTPUT_DIR}/elite_dangerous_composite.png" \
    --title "Elite:Dangerous" \
    --subtitle "${DEVICES_TITLE}"
