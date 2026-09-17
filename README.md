# Safety Level Homogenization for Geometrically Non-linear Structures under Multi-Dimensional Loading

Companion code repository for the Master's thesis *"Safety Level Homogenization for Geometrically Non-linear Structures under Multi-Dimensional Loading"*, submitted to the Chair of Engineering Risk Analysis, Department of Civil, Geo and Environmental Engineering, Technische Universität München.

**Author:** Johannes Stümpfl ([johannes.stuempfl@tum.de](mailto:johannes.stuempfl@tum.de))
**Supervisors:** Dr. Max Teichgräber, Univ.-Prof. Dr. Daniel Straub

This repository contains the full implementation used to analyze three example structures (an edged steel beam, a prestressed cable net, and a prestressed hypar membrane), quantify their non-linear structural behavior, compute their structural reliability via FORM and Subset Simulation, and derive partial safety factors for homogenization.

## Repository structure

Each of the three example structures analyzed in the thesis has its own top-level folder, named to match the thesis's System 1/2/3 numbering:

```
syst_1_edged_beam/     System 1: edged steel beam
    dsm_core/           Custom Direct Stiffness Method (DSM) solver
                         (Theory of 1st and 2nd order)
    syst_1_*.ipynb       Reliability analysis notebooks (linear / non-linear)
    syst_1_*.py          Model functions and measures of non-linearity
    syst_1_plots/        Generated figures

syst_2_cablenet/       System 2: prestressed cable net
    syst_2_*.py          Model functions, measures of non-linearity,
                         reliability analysis (linear / non-linear)
    syst_2_plots/         Generated figures

syst_3_membrane/hypar.gid/   System 3: prestressed hypar membrane
    MainKratos.py             Kratos Multiphysics entry point
    ProjectParameters.json    Kratos solver/analysis settings
    StructuralMaterials.json  Material and prestress definitions
    hypar.mdpa                Finite element mesh
    syst_3_*.py                Model functions, measures of non-linearity,
                               reliability analysis (linear / non-linear)

ERA_Distribution_Classes_Python/   Third-party reliability toolbox (see below)

kratos_docker/          Docker setup used to run Kratos Multiphysics
```

Systems 2 and 3 are solved using Kratos Multiphysics (geometrically non-linear, Theory of 3rd order for the cable net; large-displacement/large-strain formulation for the membrane). System 1 is solved with the custom DSM solver in `dsm_core/` and does not require Kratos.

## Requirements and setup

### Python environment (all systems)

```bash
pip install -r requirements.txt
```

This installs `numpy`, `matplotlib`, `scipy`, `ipykernel`, and `autograd`, which is sufficient to run **System 1** end to end.

### Kratos Multiphysics (Systems 2 and 3 only)

Kratos is run inside a Docker container, since it is not readily pip-installable on most systems. Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) to be installed and running.

Build the image once:

```bash
bash kratos_docker/build.sh
```

Run any script inside the container, with the whole repository mounted at `/workspace`:

```bash
bash kratos_docker/run.sh python3 syst_2_cablenet/syst_2_reliability_analysis_lin.py
```

Or launch a Jupyter Lab session inside the container:

```bash
bash kratos_docker/notebook.sh
```

then open the printed `http://127.0.0.1:8888` link (with its token) in your browser.

## Reproducing the results

| System | Entry point | Requires Docker/Kratos |
|---|---|---|
| 1 — Edged beam | `syst_1_edged_beam/syst_1_reliability_analysis_lin.ipynb` and `syst_1_reliability_analysis_nonl.ipynb` | No |
| 2 — Cable net | `syst_2_cablenet/syst_2_reliability_analysis_lin.py` and `syst_2_reliability_analysis_nonl.py` | Yes |
| 3 — Hypar membrane | `syst_3_membrane/hypar.gid/syst_3_reliability_analysis_lin.py` and `syst_3_reliability_analysis_nonlin.py` | Yes |

Each `*_model_functions.py` file defines the structural response function $t_S(L_1, L_2)$ for that system, and each `*_measures_of_nonlinearity.py` file computes the corresponding non-linearity measures ($y_0$, $\kappa_1$, $\kappa_2$, $\kappa_{12}$, $r_1$, $r_2$) used throughout Chapter 4 of the thesis.

Note that `syst_3_membrane/hypar.gid/` also contains several Kratos-generated output files (`vtk_output/`, `Logs/`, `*.post.bin`, `*.post.lst`, `formfinding_result_model.mdpa`). These are regenerated automatically on each run and are not meant to be edited by hand.

## Third-party code

`ERA_Distribution_Classes_Python/` is the Engineering Risk Analysis (ERA) distribution and reliability toolbox and is **not** original work of this thesis. It provides the random variable classes (`ERADist`, `ERANataf`) and reliability methods (`FORM_HLRF`, `FORM_fmincon`, `SuS`) used throughout. See `ERA_Distribution_Classes_Python/system.pdf` for its own documentation.

Original source: [ERA-Software on GitHub](https://github.com/ERA-Software/Overview).

## Reference

For the full methodology, derivations, and discussion of results, see the accompanying thesis:

> Stümpfl, J. (2026). *Safety Level Homogenization for Geometrically Non-linear Structures under Multi-Dimensional Loading.* Master's thesis, Technische Universität München.
