#!/usr/bin/env bash
# Runs a command inside the kratos-mem container, with your whole project
# folder mounted at /workspace (so node.py, structure.py, the ERA classes,
# and any Kratos scripts you write can all see each other).
#
# Examples:
#   bash run.sh                                   # drop into a Python shell
#   bash run.sh python3 -c "import KratosMultiphysics"
#   bash run.sh python3 my_membrane_script.py
set -e
cd "$(dirname "$0")/.."   # project root = parent of kratos_docker/

docker run --rm -it \
    --platform linux/amd64 \
    -v "$(pwd)":/workspace \
    -w /workspace \
    kratos-mem "$@"
