"""
Three CableElement3D2N members sharing one common (free) node, each
prestressed, loaded by a point load (Y and Z components) at that shared node.

Unlike syst_7_membrane, this needs NO GiD mesh and NO form-finding stage:
with explicit truss/cable elements, the node positions ARE the input
geometry (you specify them directly), prestress is just a material
property, and the solver finds equilibrium under prestress + the external
load in one pass. So the whole model - nodes, elements, properties,
supports, loads - is built by hand in Python, the same raw-API style used
in syst_7_membrane/check_*.py.

t_S_tripod(F_Y, F_Z) wraps that into a reusable structural-response
function, the same pattern as syst_7_membrane's t_S_kratos_nonlinear(L):
takes the two load components [N] at the common node and returns the PK2
stress [Pa] in cable element 2 - a fresh Kratos Model built from scratch
every call, so there's no risk of state leaking between calls.

Geometry/section/prestress below are fixed "given" properties of the
structure (only the two loads vary per call) - EDIT THESE to match what you
actually want; everything under that heading is currently a placeholder.

Run with (from the project root, inside Docker):
    bash run.sh python3 syst_8_tripod_cables/tripod_model_functions.py
"""
import sys
import json
import numpy as np
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

sys.path.insert(0, "/workspace")

KratosMultiphysics.Logger.GetDefaultOutput().SetSeverity(KratosMultiphysics.Logger.Severity.WARNING)


# # 4 cable system
# ANCHOR_COORDS = [
#     (0.0,  0.0,  0.0),
#     (6.0,  0.0,  0.0),
#     (6.0,  0.0, -0.2),
#     (0.0,  0.0, -0.2),
# ]
# COMMON_COORD = (3.0, 0.0, -0.1)

# Test: 8 cable system
ANCHOR_COORDS = [
    (0.0,  0.0,  0.0),
    (6.0,  0.0,  0.0),
    (6.0,  0.0, -0.2),
    (0.0,  0.0, -0.2),
    (0.0,  0.1,  0.0),
    (6.0,  0.1,  0.0),
    (6.0,  0.1, -0.2),
    (0.0,  0.1, -0.2),
]
COMMON_COORD = (3.0, 0.05, -0.1)

# Section/material - reusing the same steel cable properties already used for
# the hypar's boundary cables (12 mm diameter round steel bar).
DIAMETER = 0.012 # m
CROSS_AREA = DIAMETER**2 * np.pi / 4    # m^2
YOUNG_MODULUS = 205e9                   # Pa
DENSITY = 7850.0                        # kg/m^3

# Prestress FORCE = TRUSS_PRESTRESS_PK2 * CROSS_AREA.
PRESTRESS_PK2 = 265258238.5  # Pa

# ============================================================================


def t_S_cablenet_nonlinear(F_Y: float = 0.0, F_Z: float = 0.0) -> float:
    """
    Builds the cable structure fresh, ramps [0, F_Y, F_Z] onto the common node over
    N_STEPS substeps (same reasoning as syst_7_membrane: a geometrically
    non-linear, tension-only cable system converges far more reliably with
    small load increments than one big jump), and returns cable element 2's
    (anchor 2 -> common node) PK2 stress [Pa] at the final step.

    Prints the common node's displacement every call so you can see how the
    structure is actually deforming, not just the resulting stress number.
    """
    model = KratosMultiphysics.Model()
    mp = model.CreateModelPart("Structure")
    mp.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3
    
    N_STEPS = 20
    
    params_dict = {
        "problem_data": {
            "problem_name": "cablenet",
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

    # Nodes: anchors get ids 1..N, the common node gets the next id. Must be
    # created AFTER the analysis object above (that's what registers
    # DISPLACEMENT/REACTION/POINT_LOAD/etc. on the model part) and BEFORE
    # analysis.Initialize() below.
    for i, (x, y, z) in enumerate(ANCHOR_COORDS, start=1):
        mp.CreateNewNode(i, x, y, z)
    common_id = len(ANCHOR_COORDS) + 1
    common_node = mp.CreateNewNode(common_id, *COMMON_COORD)

    for node in mp.Nodes:
        node.AddDof(KratosMultiphysics.DISPLACEMENT_X, KratosMultiphysics.REACTION_X)
        node.AddDof(KratosMultiphysics.DISPLACEMENT_Y, KratosMultiphysics.REACTION_Y)
        node.AddDof(KratosMultiphysics.DISPLACEMENT_Z, KratosMultiphysics.REACTION_Z)

    # One shared Properties object for all 3 cables (identical prestress/
    # section here). Give each cable its own Properties(id) instead if you
    # want different prestress or section per member.
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
    # No X load is ever applied and every node lives at X=0, so nothing would
    # ever move the common node in X - fixing it there too keeps the system
    # well-posed without changing the Y-Z physics you actually care about.
    common_node.Fix(KratosMultiphysics.DISPLACEMENT_X)

    # 3 CableElement3D2N, each from one anchor to the shared common node
    for i in range(1, len(ANCHOR_COORDS) + 1):
        mp.CreateNewElement("CableElement3D2N", i, [i, common_id], props)

    # The nodal POINT_LOAD value set in the ramp loop below does nothing on
    # its own - it's just storage. This CONDITION is what actually reads it
    # and contributes it to the system during assembly (properties content
    # doesn't matter here, this condition type ignores material data).
    mp.CreateNewCondition("PointLoadCondition3D1N", 100, [common_id], props)
    
    analysis.Initialize()

    for step in range(N_STEPS):
        analysis.time = analysis._AdvanceTime()
        t_frac = (step + 1) / N_STEPS
        common_node.SetSolutionStepValue(sma.POINT_LOAD, [0.0, t_frac * F_Y, t_frac * F_Z])
    
        
        analysis.InitializeSolutionStep()
        converged = analysis._GetSolver().SolveSolutionStep()
        analysis.FinalizeSolutionStep()

        if not converged:
            print(f"    !! non-convergence at step {step + 1}/{N_STEPS} "
                  f"(F_Y={t_frac * F_Y:.1f} N, F_Z={t_frac * F_Z:.1f} N)", flush=True)

    disp = common_node.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)
    print(f"  t_S_tripod(F_Y={F_Y:.1f}, F_Z={F_Z:.1f})  ->  "
          f"common node displacement: dx={disp[0]:.6e}  dy={disp[1]:.6e}  dz={disp[2]:.6e}  m",
          flush=True)

    # elem2 = mp.GetElement(2)
    # stresses = elem2.CalculateOnIntegrationPoints(KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
    # stress_pa = stresses[0][0]
    
    # Test: 8 cable system
    elem5 = mp.GetElement(5)
    stresses = elem5.CalculateOnIntegrationPoints(KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
    stress_pa = stresses[0][0]

    analysis.Finalize()

    return stress_pa /1e6 # output in MPa, not Pa



def t_S_cablenet_linear(F_Y: float = 0.0, F_Z: float = 0.0) -> float:
    """
    Docstring to be written 
    """
    model = KratosMultiphysics.Model()
    mp = model.CreateModelPart("Structure")
    mp.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3
    
    N_STEPS = 1

    params_dict = {
        "problem_data": {
            "problem_name": "cablenet",
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
            "analysis_type": "linear",
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

    # Nodes: anchors get ids 1..N, the common node gets the next id. Must be
    # created AFTER the analysis object above (that's what registers
    # DISPLACEMENT/REACTION/POINT_LOAD/etc. on the model part) and BEFORE
    # analysis.Initialize() below.
    for i, (x, y, z) in enumerate(ANCHOR_COORDS, start=1):
        mp.CreateNewNode(i, x, y, z)
    common_id = len(ANCHOR_COORDS) + 1
    common_node = mp.CreateNewNode(common_id, *COMMON_COORD)

    for node in mp.Nodes:
        node.AddDof(KratosMultiphysics.DISPLACEMENT_X, KratosMultiphysics.REACTION_X)
        node.AddDof(KratosMultiphysics.DISPLACEMENT_Y, KratosMultiphysics.REACTION_Y)
        node.AddDof(KratosMultiphysics.DISPLACEMENT_Z, KratosMultiphysics.REACTION_Z)

    # One shared Properties object for all 3 cables (identical prestress/
    # section here). Give each cable its own Properties(id) instead if you
    # want different prestress or section per member.
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
    # No X load is ever applied and every node lives at X=0, so nothing would
    # ever move the common node in X - fixing it there too keeps the system
    # well-posed without changing the Y-Z physics you actually care about.
    common_node.Fix(KratosMultiphysics.DISPLACEMENT_X)

    # 4 TrussLinearElement3D2N. Unlike CableElement3D2N,
    # this element can carry compression - no more tension-only/slack behavior.
    for i in range(1, len(ANCHOR_COORDS) + 1):
        mp.CreateNewElement("TrussLinearElement3D2N", i, [i, common_id], props)


    mp.CreateNewCondition("PointLoadCondition3D1N", 100, [common_id], props)
    
    analysis.Initialize()

    for step in range(N_STEPS):
        analysis.time = analysis._AdvanceTime()
        t_frac = (step + 1) / N_STEPS
        common_node.SetSolutionStepValue(sma.POINT_LOAD, [0.0, t_frac * F_Y, t_frac * F_Z])
    
        
        analysis.InitializeSolutionStep()
        converged = analysis._GetSolver().SolveSolutionStep()
        analysis.FinalizeSolutionStep()

        if not converged:
            print(f"    !! non-convergence at step {step + 1}/{N_STEPS} "
                  f"(F_Y={t_frac * F_Y:.1f} N, F_Z={t_frac * F_Z:.1f} N)", flush=True)

    disp = common_node.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)
    print(f"  t_S_tripod(F_Y={F_Y:.1f}, F_Z={F_Z:.1f})  ->  "
          f"common node displacement: dx={disp[0]:.6e}  dy={disp[1]:.6e}  dz={disp[2]:.6e}  m",
          flush=True)

    # elem2 = mp.GetElement(2)
    # stresses = elem2.CalculateOnIntegrationPoints(KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
    # stress_pa = stresses[0][0]
    
    # Test: 8 cable system
    elem5 = mp.GetElement(5)
    stresses = elem5.CalculateOnIntegrationPoints(KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
    stress_pa = stresses[0][0]
    

    analysis.Finalize()

    return stress_pa /1e6 # output in MPa, not Pa