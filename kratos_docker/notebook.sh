#!/usr/bin/env bash
# Launches Jupyter Lab inside the kratos-mem container
set -e
cd "$(dirname "$0")/.."   # project root = parent of kratos_docker/

docker run --rm -it \
    --platform linux/amd64 \
    -p 8888:8888 \
    -v "$(pwd)":/workspace \
    -w /workspace \
    kratos-mem jupyter lab --ip=0.0.0.0 --port=8888 --no-browser --allow-root
