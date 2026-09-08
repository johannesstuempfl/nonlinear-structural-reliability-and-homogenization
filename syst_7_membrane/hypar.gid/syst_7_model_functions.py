"""
Phase 3: wrap the Kratos membrane pipeline (Stage 2 from run_phase2.py,
generalized to any target load) as a reusable structural-response function
t_S_kratos(L), then use it to build a limit-state function g(x) and run FORM
- exactly mirroring syst_4_reliability_analysis_nonl.ipynb's
t_S / g_opt_1_FORM / FORM_fmincon pattern, but for this membrane problem.

Read GUIDE.md (in the syst_7_membrane/ parent folder) first - it explains
every Kratos concept and every gotcha referenced below in much more detail,
plus a side-by-side table mapping this file's pieces onto syst_4's.

STATUS (as of pausing this script to hand control back): design option (a)
converges cleanly, beta=4.76 vs paper's 4.96. Design option (b) does not yet
converge cleanly - its FORM search needs to evaluate t_S_kratos out around
L~1.3-1.5 kN/m^2, and even with the current step-size scaling that region is
occasionally still too coarse. investigate_high_load.py already proved the
underlying physics is smooth there (no wrinkling/instability) - it's purely a
numerical step-resolution issue, so the fix is simply "finer steps", at the
cost of runtime. That's the natural next thing to tune if you pick this back up.
"""
import sys
import os
import json
import math
import numpy as np

# The project root is mounted at /workspace inside the Docker container (see
# kratos_docker/run.sh). ERA_Distribution_Classes_Python lives there, not
# under syst_7_membrane/, so it needs to be added to sys.path explicitly -
# this script is normally run from inside syst_7_membrane/hypar.gid/, which
# wouldn't otherwise see it.
sys.path.insert(0, "/workspace")

import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis
import KratosMultiphysics.ConstitutiveLawsApplication as cla

from ERA_Distribution_Classes_Python.Classes.ERADist import ERADist
from ERA_Distribution_Classes_Python.Classes.ERANataf import ERANataf
from ERA_Distribution_Classes_Python.Classes.FORM_HLRF import FORM_HLRF
from ERA_Distribution_Classes_Python.Classes.FORM_fmincon import FORM_fmincon

# Kratos's own per-step logging (STEP/TIME lines, mdpa read summaries, etc.)
# is very verbose and would otherwise drown out the [call N] trace below,
# which is what actually tells you whether FORM's search is behaving.
KratosMultiphysics.Logger.GetDefaultOutput().SetSeverity(KratosMultiphysics.Logger.Severity.WARNING)

THICKNESS = 0.001  # m, converts Pa (true stress, what Kratos computes) -> kN/m
                   # (the resultant convention the paper and StructuralMaterials.json use)
                   
def _run_static_kratos_linear(L_1: float = 0.0, L_2: float = 0.0) -> float:
    """
    Takes in loads L_1 and L_2 in kN/m2. 
    L_1 points in negative z-direction (downwards).
    L_2 points in positive x-direction.
    Returns max stress of the membrane in kN/m
    """
    L_snow_Pa = L_1 * 1000 # conversion from kN/m2 to Pa -> * 1000
    L_wind_Pa = L_2 * 1000 # conversion from kN/m2 to Pa -> * 1000
    
    params_dict = {
        "problem_data": {
            "problem_name": "hypar_static",
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
                "input_type": "mdpa",
                "input_filename": "formfinding_result_model"
            },
            "material_import_settings": {
                "materials_filename": "StructuralMaterials.json"
            },
            "time_stepping": {"time_step": 1.0},
            "line_search": False,
            "convergence_criterion": "residual_criterion",
            "displacement_relative_tolerance": 1e-3,
            "displacement_absolute_tolerance": 1e-6,
            "residual_relative_tolerance": 1e-3,
            "residual_absolute_tolerance": 1e-6,
            "max_iteration": 80,
            "rotation_dofs": False,
            "volumetric_strain_dofs": False
        },
        "processes": {
            "constraints_process_list": [{
                "python_module": "assign_vector_variable_process",
                "kratos_module": "KratosMultiphysics",
                "process_name": "AssignVectorVariableProcess",
                "Parameters": {
                    "model_part_name": "Structure.DISPLACEMENT_Displacement_Auto1",
                    "variable_name": "DISPLACEMENT",
                    "interval": [0.0, "End"],
                    "constrained": [True, True, True],
                    "value": [0.0, 0.0, 0.0]
                }
            }],
            "loads_process_list": [],
            "list_other_processes": []
        },
        "output_processes": {}
    }

    parameters = KratosMultiphysics.Parameters(json.dumps(params_dict))
    model = KratosMultiphysics.Model()
    analysis = StructuralMechanicsAnalysis(model, parameters)
    analysis.Initialize()

    mp = model.GetModelPart("Structure")
    membrane_mp = mp.GetSubModelPart("Parts_Membrane_Membrane_Auto1")
    
    # Snow: plan (X-Y) projected area, force in -Z
    tributary_area = {}
    for elem in membrane_mp.Elements:
        nodes = list(elem.GetNodes())
        x1, y1 = nodes[0].X0, nodes[0].Y0
        x2, y2 = nodes[1].X0, nodes[1].Y0
        x3, y3 = nodes[2].X0, nodes[2].Y0
        area = 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        for n in nodes:
            tributary_area[n.Id] = tributary_area.get(n.Id, 0.0) + area / 3.0
    
    # Wind: frontal (Y-Z) projected area, force in +X
    frontal_area = {}
    for elem in membrane_mp.Elements:
        nodes = list(elem.GetNodes())
        y1, z1 = nodes[0].Y0, nodes[0].Z0
        y2, z2 = nodes[1].Y0, nodes[1].Z0
        y3, z3 = nodes[2].Y0, nodes[2].Z0
        area = 0.5 * abs((y2 - y1) * (z3 - z1) - (y3 - y1) * (z2 - z1))
        for n in nodes:
            frontal_area[n.Id] = frontal_area.get(n.Id, 0.0) + area / 3.0

    prop = mp.GetProperties()[1]
    load_sub_mp = mp.CreateSubModelPart("CombinedLoad")
    cond_id = 100000
    nodes_with_load = []
    for node_id in set(tributary_area) | set(frontal_area):
        snow_a = tributary_area.get(node_id, 0.0)
        wind_a = frontal_area.get(node_id, 0.0)
        if snow_a <= 0.0 and wind_a <= 0.0:
            continue
        cond_id += 1
        node = mp.Nodes[node_id]
        cond = mp.CreateNewCondition("PointLoadCondition3D1N", cond_id, [node_id], prop)
        load_sub_mp.AddCondition(cond)
        load_sub_mp.AddNode(node, 0)
        nodes_with_load.append((node, snow_a, wind_a))

    for node, snow_a, wind_a in nodes_with_load:
        node.SetSolutionStepValue(sma.POINT_LOAD, [L_wind_Pa * wind_a, 0.0, -L_snow_Pa * snow_a])


    analysis.time = analysis._AdvanceTime()
    analysis.InitializeSolutionStep()
    analysis._GetSolver().SolveSolutionStep()
    analysis.FinalizeSolutionStep()

    all_s11 = []
    for elem in membrane_mp.Elements:
        stresses = elem.CalculateOnIntegrationPoints(KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
        all_s11.extend(s[0] for s in stresses)
    
    # #  Verify the displacements
    # sample_node = nodes_with_load[100][0]   # pick one specific node
    # disp = sample_node.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)
    # print(f"    sample node {sample_node.Id}: DISPLACEMENT = ({disp[0]:.6e}, {disp[1]:.6e}, {disp[2]:.6e})  at L={L_kNm2:.4f}")
    
    analysis.Finalize()

    return max(all_s11) * THICKNESS / 1000.0   # hard max, kN/m - no p-norm needed for a one-off comparison


def _run_static_kratos_nonlinear(L_1: float, L_2: float = 0.0) -> float:
    """
    Takes in loads L_1 and L_2 in kN/m2. 
    L_1 points in negative z-direction (downwards).
    L_2 points in positive x-direction.
    Returns max stress of the membrane in kN/m
    """
    L_snow_Pa = L_1 * 1000 # conversion from kN/m2 to Pa -> * 1000
    L_wind_Pa = L_2 * 1000 # conversion from kN/m2 to Pa -> * 1000
    
    # How many load substeps to use for THIS particular target load. This
    # matters more than it looks: Newton-Raphson for a geometrically
    # non-linear problem only converges reliably if consecutive load steps
    # are close enough together, and "close enough" needs to hold not just at
    # the checkpoints we've validated (L=0.6, 0.9) but at whatever L values
    # FORM's search happens to probe - which, for the design points we're
    # after, legitimately goes out to L~1.3-1.5 kN/m^2 (see module docstring
    # and GUIDE.md gotcha #8). investigate_high_load.py empirically confirmed
    # 0.02 kN/m^2/step converges cleanly and smoothly the WHOLE way from 0 to
    # 1.6 kN/m^2 - no physical instability anywhere in that range. We use
    # 0.05 kN/m^2/step here as a cheaper (fewer Kratos calls -> faster FORM
    # runs) but still-safe middle ground; tighten this (e.g. to 0.02-0.03) if
    # you still see "!! non-convergence" warnings below.
    n_steps = max(15, math.ceil(L_1 / 0.05), math.ceil(L_2 / 0.05))


    # Same solver_settings structure as run_phase2.py's Stage 2, with
    # echo_level dropped to 0 (Logger severity above already silences most of
    # it anyway) and residual_absolute_tolerance tightened to 1e-6 (see
    # GUIDE.md gotcha #3: this makes the RELATIVE tolerance the one that
    # actually governs convergence, giving more consistent results between
    # calls at very similar L - important for finite-difference gradients).
    params_dict = {
        "problem_data": {
            "problem_name": "hypar_static",
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
                "input_type": "mdpa",
                "input_filename": "formfinding_result_model"
            },
            "material_import_settings": {
                "materials_filename": "StructuralMaterials.json"
            },
            "time_stepping": {"time_step": 1.0 / n_steps},
            "line_search": False,
            "convergence_criterion": "residual_criterion",
            "displacement_relative_tolerance": 1e-3,
            "displacement_absolute_tolerance": 1e-6,
            "residual_relative_tolerance": 1e-3,
            "residual_absolute_tolerance": 1e-6,
            "max_iteration": 80,
            "rotation_dofs": False,
            "volumetric_strain_dofs": False
        },
        "processes": {
            "constraints_process_list": [{
                "python_module": "assign_vector_variable_process",
                "kratos_module": "KratosMultiphysics",
                "process_name": "AssignVectorVariableProcess",
                "Parameters": {
                    "model_part_name": "Structure.DISPLACEMENT_Displacement_Auto1",
                    "variable_name": "DISPLACEMENT",
                    "interval": [0.0, "End"],
                    "constrained": [True, True, True],
                    "value": [0.0, 0.0, 0.0]
                }
            }],
            "loads_process_list": [],
            "list_other_processes": []
        },
        "output_processes": {}
    }

    parameters = KratosMultiphysics.Parameters(json.dumps(params_dict))
    model = KratosMultiphysics.Model()
    analysis = StructuralMechanicsAnalysis(model, parameters)
    analysis.Initialize()

    mp = model.GetModelPart("Structure")
    membrane_mp = mp.GetSubModelPart("Parts_Membrane_Membrane_Auto1")

    prop = mp.GetProperties()[1]

    # Linear Elastic Plane Stress 2D Law
    base_props = KratosMultiphysics.Properties(2)
    base_props.SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, sma.LinearElasticPlaneStress2DLaw())
    base_props.SetValue(KratosMultiphysics.YOUNG_MODULUS, 600000000.0)
    base_props.SetValue(KratosMultiphysics.POISSON_RATIO, 0.4)

    prop.SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, cla.WrinklingLinear2DLaw())
    prop.AddSubProperties(base_props)


    # WrinklingLinear2DLaw (not chosen, since results are less accurate to paper)
    # prop.SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, cla.LinearElasticOrthotropic2DLaw())
    # prop.SetValue(KratosMultiphysics.YOUNG_MODULUS_X, 600000000.0)
    # prop.SetValue(KratosMultiphysics.YOUNG_MODULUS_Y, 600000000.0)
    # prop.SetValue(KratosMultiphysics.SHEAR_MODULUS_XY, 214285714.0)
    # prop.SetValue(KratosMultiphysics.POISSON_RATIO_XY, 0.4)
    
    for elem in membrane_mp.Elements:
        elem.Initialize(mp.ProcessInfo)
        
    
    # Snow: plan (X-Y) projected area, force in -Z
    tributary_area = {}
    for elem in membrane_mp.Elements:
        nodes = list(elem.GetNodes())
        x1, y1 = nodes[0].X0, nodes[0].Y0
        x2, y2 = nodes[1].X0, nodes[1].Y0
        x3, y3 = nodes[2].X0, nodes[2].Y0
        area = 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        for n in nodes:
            tributary_area[n.Id] = tributary_area.get(n.Id, 0.0) + area / 3.0

    # Wind: frontal (Y-Z) projected area, force in +X
    frontal_area = {}
    for elem in membrane_mp.Elements:
        nodes = list(elem.GetNodes())
        y1, z1 = nodes[0].Y0, nodes[0].Z0
        y2, z2 = nodes[1].Y0, nodes[1].Z0
        y3, z3 = nodes[2].Y0, nodes[2].Z0
        area = 0.5 * abs((y2 - y1) * (z3 - z1) - (y3 - y1) * (z2 - z1))
        for n in nodes:
            frontal_area[n.Id] = frontal_area.get(n.Id, 0.0) + area / 3.0

    prop_load = mp.GetProperties()[1]
    load_sub_mp = mp.CreateSubModelPart("CombinedLoad")
    cond_id = 100000
    nodes_with_load = []   # (node, snow_area, wind_area)
    for node_id in set(tributary_area) | set(frontal_area):
        snow_a = tributary_area.get(node_id, 0.0)
        wind_a = frontal_area.get(node_id, 0.0)
        if snow_a <= 0.0 and wind_a <= 0.0:
            continue
        cond_id += 1
        node = mp.Nodes[node_id]
        cond = mp.CreateNewCondition("PointLoadCondition3D1N", cond_id, [node_id], prop_load)
        load_sub_mp.AddCondition(cond)
        load_sub_mp.AddNode(node, 0)
        nodes_with_load.append((node, snow_a, wind_a))

    all_s11 = []
    for step in range(n_steps):
        analysis.time = analysis._AdvanceTime()
        t_frac = (step + 1) / n_steps
        L_snow = t_frac * L_snow_Pa
        L_wind = t_frac * L_wind_Pa

        for node, snow_a, wind_a in nodes_with_load:
            node.SetSolutionStepValue(sma.POINT_LOAD, [L_wind * wind_a, 0.0, -L_snow * snow_a])

        analysis.InitializeSolutionStep()
        converged = analysis._GetSolver().SolveSolutionStep()
        analysis.FinalizeSolutionStep()

        if not converged:
            print(f"    !! non-convergence at L_snow={L_1:.4f}, L_wind={L_2:.4f} kN/m^2, "
                  f"substep {step+1}/{n_steps}", flush=True)

        if step == n_steps - 1:
            all_s11 = []
            for elem in membrane_mp.Elements:
                stresses = elem.CalculateOnIntegrationPoints(
                    KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
                for s in stresses:
                    all_s11.append(s[0])

    analysis.Finalize()

    all_s11 = np.array(all_s11)
    hard_max = np.max(all_s11)
    p = 100.0
    ratios = all_s11 / hard_max
    smooth_max = hard_max * np.sum(np.clip(ratios, 0.0, None) ** p) ** (1.0 / p)
    
    
    # return smooth_max * THICKNESS / 1000.0 # in kN/m
    return smooth_max / 1e6 # in N/mm^2


_CALL_COUNT = [0]  # plain list so the closure below can mutate it (no `nonlocal` needed)



def t_S_hypar_nonlinear(L_1: float = 0.0, L_2: float = 0.0):
    """
    The structural-response function - this is syst_7's analog of syst_4's
    t_S(l_1, l_2). Takes a snow load L [kN/m^2] and returns the resulting max
    warp-direction membrane stress [kN/m].

    Accepts either a plain scalar OR a 1D array-like of L values, and returns
    a matching scalar or 1D array. This dual behavior is NOT optional - it's
    required by how FORM_HLRF's finite-difference gradient estimator calls
    g(x) internally: once with a single point (1D array of length d, the
    number of random variables) to get the LSF value, and once with a (d,d)
    matrix (one row per perturbed dimension) to estimate the gradient. Your
    own g(x) needs to pass whatever "L slice" it receives straight through to
    this function and trust it to handle both shapes - see g_opt_a/g_opt_b
    below for exactly how that's done (x[..., 1] handles both cases via
    numpy's ellipsis indexing).

    Every call prints its own [call N] trace line - deliberately verbose,
    because watching this trace is how you tell whether FORM's search is
    converging sensibly or wandering into a bad region (see the "Middle
    part"/"Lower part" transcripts referenced in the module docstring for
    what a problematic trace looks like: repeated near-identical L values
    with inconsistent e, or L drifting to physically extreme values).
    """
    scalar_in = (np.ndim(L_1) == 0) and (np.ndim(L_2) == 0)
    L_snow_arr = np.atleast_1d(np.asarray(L_1, dtype=float))
    L_wind_arr = np.atleast_1d(np.asarray(L_2, dtype=float))
    L_snow_arr, L_wind_arr = np.broadcast_arrays(L_snow_arr, L_wind_arr)
    out = np.empty(L_snow_arr.shape[0])
    for i in range(L_snow_arr.shape[0]):
        _CALL_COUNT[0] += 1
        val = _run_static_kratos_nonlinear(float(L_snow_arr[i]), float(L_wind_arr[i]))
        out[i] = val
        print(f"  [call {_CALL_COUNT[0]:4d}] L_snow={L_snow_arr[i]:9.4f}  L_wind={L_wind_arr[i]:9.4f} kN/m^2  ->  e={val:9.4f} kN/m2", flush=True)
    return out[0] if scalar_in else out




def t_S_hyperplane_linear(F_Z: float = 0.0, F_Y: float = 0.0) -> float:
    """
    This is the linear hyperplane function for the cablenet structure. 
    It does not use KratosMultiphysics but is constructed as follows: 
    The hyperplane is calibrated by keeping the load ratios r1 and r2 equal to the nonlinear model, including prestress. 
    So first, the plane is defined trough the three points: p1, p2, p3 which correspond to t_S(0,0), t_S(l1k,0), t_S(0,l2k). 
    Then, t_S(0,0) is subtracted.
    """
    
    # Here are the results of the nonlinear model. They serve for calibrating this linear hyperplane.
    l1k = 1.1                       # kN/m2
    l2k = 0.65                      # kN/m2
    t_S_l1k_0 = 8.700958843457569   # MPa
    t_S_0_l2k = 3.1749104137090716   # MPa
    t_S_0_0 = 3.0596512849207254     # MPa
    
    # # With the given values, the point t_S(0,0) is calculated by rearranging the equations for r1 and r2
    # t_S_0_0 = t_S_l1k_0 - r_1_nonl * ((t_S_l1k_0 - t_S_0_l2k)/(r_1_nonl - r_2_nonl))
    # # doesn't work
    
    # Constructing the array representation of the three points, which define the plane
    p1 = np.array([0, 0 , t_S_0_0])
    p2 = np.array([l1k, 0 , t_S_l1k_0])
    p3 = np.array([0, l2k , t_S_0_l2k])
    
    # Form the edge vectors 
    v1 = p2 - p1 
    v2 = p3 - p1
    
    # Normal Vector via cross product 
    n = np.cross(v1, v2)
    
    # Expanding with n = (a,b,c) and d = n * p1
    a, b, c = n
    d = n @ p1
    
    # Getting the slopes m1 and m2 in l1 and l2 direction as well as the z-intercept z0
    m1 = -a/c
    m2 = -b/c
    z0 = d/c
    
    # Hyperplane function
    z = m1 * F_Z + m2 * F_Y + z0 - t_S_0_0
    
    return z 