
import sys
import os
import json
import math
import numpy as np

sys.path.insert(0, "/workspace")

import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis
import KratosMultiphysics.ConstitutiveLawsApplication as cla

from ERA_Distribution_Classes_Python.Classes.ERADist import ERADist
from ERA_Distribution_Classes_Python.Classes.ERANataf import ERANataf
from ERA_Distribution_Classes_Python.Classes.FORM_HLRF import FORM_HLRF
from ERA_Distribution_Classes_Python.Classes.FORM_fmincon import FORM_fmincon


KratosMultiphysics.Logger.GetDefaultOutput().SetSeverity(KratosMultiphysics.Logger.Severity.WARNING)

THICKNESS = 0.001  # m, converts Pa (true stress, what Kratos computes) -> kN/m


def _run_static_kratos_nonlinear(L_1: float, L_2: float = 0.0) -> float:
    """
    Takes in loads L_1 and L_2 in kN/m2. 
    L_1 points in negative z-direction (downwards).
    L_2 points in positive x-direction.
    Returns max stress of the membrane in kN/m
    """
    L_snow_Pa = L_1 * 1000 # conversion from kN/m2 to Pa -> * 1000
    L_wind_Pa = L_2 * 1000 # conversion from kN/m2 to Pa -> * 1000
    
    n_steps = max(15, math.ceil(L_1 / 0.05), math.ceil(L_2 / 0.05))


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


_CALL_COUNT = [0] 



def t_S_hypar_nonlinear(L_1: float = 0.0, L_2: float = 0.0):
    """
    t_S(l_1, l_2). Takes a snow load L [kN/m^2] and returns the resulting max
    warp-direction membrane stress [kN/m].
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
