"""
Simple standalone example: three CableElement3D2N members sharing one common
(free) node, each prestressed, loaded by a point load (Y and Z components) at
that shared node.

Unlike syst_7_membrane, this needs NO GiD mesh and NO form-finding stage:
with explicit truss/cable elements, the node positions ARE the input
geometry (you specify them directly), prestress is just a material
property, and the solver finds equilibrium under prestress + the external
load in one pass. So the whole model - nodes, elements, properties,
supports, loads - is built by hand in Python below, the same raw-API style
used in syst_7_membrane/check_*.py, just running a real analysis this time
instead of a one-off probe.

Layout (all nodes at X=0 - genuinely 2D, living in the Y-Z plane):

    Anchor 1: (0, -4,  0)   \
    Anchor 2: (0,  0,  0)    >  fixed supports, spread along Y at Z=0
    Anchor 3: (0,  4,  0)   /
    Common node C: (0, 0, 3)   <- free, loaded in Y and Z

EVERYTHING under "EDIT THESE" below is a placeholder illustrative choice,
not derived from any real structure - change freely to match what you
actually want.

Run with (from the project root, inside Docker):
    bash run.sh python3 syst_8_tripod_cables/tripod_cables.py
"""
import sys
import json
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

sys.path.insert(0, "/workspace")

KratosMultiphysics.Logger.GetDefaultOutput().SetSeverity(KratosMultiphysics.Logger.Severity.WARNING)

# ============================================================================
# EDIT THESE - geometry, section/material, prestress, loads
# ============================================================================
ANCHOR_COORDS = [
    (0.0, -3.0, 0.0),
    (0.0,  3.0, 0.0),
    (0.0,  0.0, -6.0),
]
COMMON_COORD = (0.0, 0.0, -3.0)

# Section/material - reusing the same steel cable properties already used for
# the hypar's boundary cables (12 mm diameter round steel bar).
CROSS_AREA = 0.000113097     # m^2
YOUNG_MODULUS = 205e9        # Pa
DENSITY = 7850.0             # kg/m^3

# TrussConstitutiveLaw's actual prestress variable is TRUSS_PRESTRESS_PK2 (a
# true stress in Pa) - NOT PRESTRESS_VECTOR, which StructuralMaterials.json's
# Cable section also sets but which is vestigial/unused by this law (see
# GUIDE.md). Prestress FORCE = TRUSS_PRESTRESS_PK2 * CROSS_AREA, so this
# value (~265 MPa) gives ~30 kN of prestress force per cable.
PRESTRESS_PK2 = 265258238.5  # Pa

# External load at the common node
LOAD_Y = -10000 #5000.0    # N
LOAD_Z = -10000# -30000.0   # N

N_STEPS = 20
# ============================================================================

model = KratosMultiphysics.Model()
mp = model.CreateModelPart("Structure")
mp.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3

params_dict = {
    "problem_data": {
        "problem_name": "tripod",
        "parallel_type": "OpenMP",
        "echo_level": 0,
        "start_time": 0.0,
        "end_time": 1.0
    },
    "solver_settings": {
        "solver_type": "static",
        "model_part_name": "Structure",
        "domain_size": 3,
        "echo_level": 0,
        "analysis_type": "non_linear",
        # "use_input_model_part" tells the solver the ModelPart already
        # exists (built above) rather than trying to read an .mdpa file -
        # the standard Kratos pattern for a purely programmatically-built
        # model. This hasn't been exercised anywhere else in this project
        # (everything else reads from GiD-authored .mdpa files), so treat
        # this stage as the most likely spot for a first-run surprise.
        "model_import_settings": {
            "input_type": "use_input_model_part"
        },
        "time_stepping": {"time_step": 1.0 / N_STEPS},
        "line_search": False,
        "convergence_criterion": "residual_criterion",
        "displacement_relative_tolerance": 1e-4,
        "displacement_absolute_tolerance": 1e-8,
        "residual_relative_tolerance": 1e-4,
        "residual_absolute_tolerance": 1e-8,
        "max_iteration": 50,
        "rotation_dofs": False,
        "volumetric_strain_dofs": False
    },
    "processes": {
        "constraints_process_list": [],
        "loads_process_list": [],
        "list_other_processes": []
    },
    "output_processes": {}
}

parameters = KratosMultiphysics.Parameters(json.dumps(params_dict))
analysis = StructuralMechanicsAnalysis(model, parameters)

# Nodes: anchors get ids 1..N, the common node gets the next id
for i, (x, y, z) in enumerate(ANCHOR_COORDS, start=1):
    mp.CreateNewNode(i, x, y, z)
common_id = len(ANCHOR_COORDS) + 1
common_node = mp.CreateNewNode(common_id, *COMMON_COORD)

for node in mp.Nodes:
    node.AddDof(KratosMultiphysics.DISPLACEMENT_X, KratosMultiphysics.REACTION_X)
    node.AddDof(KratosMultiphysics.DISPLACEMENT_Y, KratosMultiphysics.REACTION_Y)
    node.AddDof(KratosMultiphysics.DISPLACEMENT_Z, KratosMultiphysics.REACTION_Z)

# One shared Properties object for all 3 cables (identical prestress/section
# here). Give each cable its own Properties(id) instead if you want different
# prestress or section per member.
props = mp.GetProperties()[1]
props.SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, sma.TrussConstitutiveLaw())
props.SetValue(sma.CROSS_AREA, CROSS_AREA)
props.SetValue(KratosMultiphysics.YOUNG_MODULUS, YOUNG_MODULUS)
props.SetValue(KratosMultiphysics.DENSITY, DENSITY)
props.SetValue(sma.TRUSS_PRESTRESS_PK2, PRESTRESS_PK2)


# Fix all 3 anchors fully; the common node stays free
for i in range(1, len(ANCHOR_COORDS) + 1):
    node = mp.Nodes[i]
    node.Fix(KratosMultiphysics.DISPLACEMENT_X)
    node.Fix(KratosMultiphysics.DISPLACEMENT_Y)
    node.Fix(KratosMultiphysics.DISPLACEMENT_Z)
# The common node has no X load and lives at X=0 for all members, so nothing
# would ever move it in X - fixing X there too keeps the system well-posed
# without changing the Y-Z physics you actually care about.
common_node.Fix(KratosMultiphysics.DISPLACEMENT_X)

# 3 CableElement3D2N, each from one anchor to the shared common node
for i in range(1, len(ANCHOR_COORDS) + 1):
    mp.CreateNewElement("CableElement3D2N", i, [i, common_id], props)

mp.CreateNewCondition("PointLoadCondition3D1N", 100, [common_id], props)

analysis.Initialize()


# Ramp the external load 0 -> target over N_STEPS substeps, same reasoning as
# syst_7_membrane: a geometrically non-linear solve (cables large-displacement,
# tension-only) converges far more reliably with small load increments than
# one big jump, especially starting from a prestressed-but-unloaded state.
for step in range(N_STEPS):
    analysis.time = analysis._AdvanceTime()
    t_frac = (step + 1) / N_STEPS
    common_node.SetSolutionStepValue(sma.POINT_LOAD, [0.0, t_frac * LOAD_Y, t_frac * LOAD_Z])

    analysis.InitializeSolutionStep()
    converged = analysis._GetSolver().SolveSolutionStep()
    analysis.FinalizeSolutionStep()

    if not converged:
        print(f"    !! non-convergence at step {step + 1}/{N_STEPS} "
              f"(Y={t_frac * LOAD_Y:.1f} N, Z={t_frac * LOAD_Z:.1f} N)", flush=True)


# ----------------------------------------------------------------------
# Results: common node's displacement, each cable's axial force, and a
# global equilibrium check (sum of reactions should balance the applied load).
# ----------------------------------------------------------------------
disp = common_node.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)
print(f"\nCommon node displacement: dx={disp[0]:.6e}  dy={disp[1]:.6e}  dz={disp[2]:.6e}  m")

print("\nCable axial forces (PK2 stress x CROSS_AREA):")
for i in range(1, len(ANCHOR_COORDS) + 1):
    elem = mp.GetElement(i)
    stresses = elem.CalculateOnIntegrationPoints(KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
    stress_pa = stresses[0][0]
    force_n = stress_pa * CROSS_AREA
    state = "taut (tension)" if force_n > 0 else "SLACK (compression - cable can't sustain this)"
    print(f"  Cable {i} (anchor {i} -> common): stress={stress_pa/1e6:8.3f} MPa   "
          f"force={force_n:9.2f} N   [{state}]")

total_rx = sum(mp.Nodes[i].GetSolutionStepValue(KratosMultiphysics.REACTION)[0] for i in range(1, len(ANCHOR_COORDS) + 1))
total_ry = sum(mp.Nodes[i].GetSolutionStepValue(KratosMultiphysics.REACTION)[1] for i in range(1, len(ANCHOR_COORDS) + 1))
total_rz = sum(mp.Nodes[i].GetSolutionStepValue(KratosMultiphysics.REACTION)[2] for i in range(1, len(ANCHOR_COORDS) + 1))
print(f"\nEquilibrium check: sum(REACTION) = ({total_rx:.2f}, {total_ry:.2f}, {total_rz:.2f}) N")

