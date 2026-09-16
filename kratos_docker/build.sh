#!/usr/bin/env bash
# Builds the kratos-mem image. Run once, and again whenever you edit Dockerfile.
#   bash build.sh
set -e
cd "$(dirname "$0")"
docker build --platform linux/amd64 -t kratos-mem -f Dockerfile .
