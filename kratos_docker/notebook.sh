#!/usr/bin/env bash
# Launches Jupyter Lab inside the kratos-mem container, with your whole
# project folder mounted at /workspace. Open the printed http://127.0.0.1:8888
# link (with its token) in your normal browser on the Mac.
#   bash notebook.sh
set -e
cd "$(dirname "$0")/.."   # project root = parent of kratos_docker/

docker run --rm -it \
    --platform linux/amd64 \
    -p 8888:8888 \
    -v "$(pwd)":/workspace \
    -w /workspace \
    kratos-mem jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
