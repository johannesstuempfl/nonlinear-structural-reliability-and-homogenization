# Kratos Multiphysics ships pip wheels only for Windows and Linux (manylinux
# x86_64)
FROM --platform=linux/amd64 python:3.11-slim

# libgomp1: OpenMP runtime needed by Kratos's compiled C++ core
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Kratos itself, plus the packages the existing reliability pipeline
# (node.py / structure.py / ERA_Distribution_Classes_Python) needs
RUN pip install --no-cache-dir \
        KratosMultiphysics-all \
        numpy \
        scipy \
        matplotlib \
        autograd \
        ipykernel \
        jupyterlab

WORKDIR /workspace
CMD ["python3"]
