#!/usr/bin/env bash

#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
export PROJECT_ROOT="${SCRIPT_DIR}/.."

export INPUT_DIR="${PROJECT_ROOT}/input"
export OUTPUT_DIR="${PROJECT_ROOT}/output"
export TEMPLATE_DIR="${PROJECT_ROOT}/templates"

export HOTASMAP="${PROJECT_ROOT}/hotas_map.py"

export DEVICES_TITLE="Thrustmaster HOTAS Warthog + MFG Crosswind"
