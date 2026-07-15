"""
One-off diagnostic: a single, finely-resolved load ramp from 0 to 1.6 kN/m^2
(well past the region 1.3-1.5 kN/m^2 where FORM's search kept hitting solver
trouble), to see whether this is a real physical effect (stiffness loss as
the membrane approaches its tension-field limits) or just needs finer steps.

RESULT: with 80 uniform steps (0.02 kN/m^2/step), every single step converged
(converged=True throughout), and both max stress and max out-of-plane
displacement grow smoothly and monotonically the whole way to 1.6 kN/m^2 - no
plateau, no kink, no instability. Conclusion: the non-convergence seen during
FORM's search was purely a step-resolution problem (see GUIDE.md gotcha #8),
not a real physical limit of the membrane. run_phase3_FORM.py's n_steps
formula was tightened accordingly after this result.
"""
import json
import numpy as np
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

KratosMultiphysics.Logger.GetDefaultOutput().SetSeverity(KratosMultiphysics.Logger.Severity.WARNING)

THICKNESS = 0.001
L_MAX_KNM2 = 1.6
N_STEPS = 80  # 0.02 kN/m^2 per step - very fine

params_dict = {
    "problem_data": {
        "problem_name": "hypar_static", "parallel_type": "OpenMP",
        "echo_level": 0, "start_time": 0.0, "end_time": 1.0
    },
    "solver_settings": {
        "solver_type": "static", "model_part_name": "Structure", "domain_size": 3,
        "echo_level": 0, "analysis_type": "non_linear",
        "model_import_settings": {"input_type": "mdpa", "input_filename": "formfinding_result_model"},
        "material_import_settings": {"materials_filename": "StructuralMaterials.json"},
        "time_stepping": {"time_step": 1.0 / N_STEPS},
        "line_search": False, "convergence_criterion": "residual_criterion",
        "displacement_relative_tolerance": 1e-3, "displacement_absolute_tolerance": 1e-6,
        "residual_relative_tolerance": 1e-3, "residual_absolute_tolerance": 1e-6,
        "max_iteration": 100, "rotation_dofs": False, "volumetric_strain_dofs": False
    },
    "processes": {
        "constraints_process_list": [{
            "python_module": "assign_vector_variable_process", "kratos_module": "KratosMultiphysics",
            "process_name": "AssignVectorVariableProcess",
            "Parameters": {
                "model_part_name": "Structure.DISPLACEMENT_Displacement_Auto1",
                "variable_name": "DISPLACEMENT", "interval": [0.0, "End"],
                "constrained": [True, True, True], "value": [0.0, 0.0, 0.0]
            }
        }],
        "loads_process_list": [], "list_other_processes": []
    },
    "output_processes": {}
}

parameters = KratosMultiphysics.Parameters(json.dumps(params_dict))
model = KratosMultiphysics.Model()
analysis = StructuralMechanicsAnalysis(model, parameters)
analysis.Initialize()

mp = model.GetModelPart("Structure")
membrane_mp = mp.GetSubModelPart("Parts_Membrane_Membrane_Auto1")

tributary_area = {}
for elem in membrane_mp.Elements:
    nodes = list(elem.GetNodes())
    x1, y1 = nodes[0].X0, nodes[0].Y0
    x2, y2 = nodes[1].X0, nodes[1].Y0
    x3, y3 = nodes[2].X0, nodes[2].Y0
    area = 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
    for n in nodes:
        tributary_area[n.Id] = tributary_area.get(n.Id, 0.0) + area / 3.0

prop = mp.GetProperties()[1]
load_sub_mp = mp.CreateSubModelPart("SnowLoad")
cond_id = 100000
nodes_with_load = []
for node_id, area in tributary_area.items():
    if area <= 0.0:
        continue
    cond_id += 1
    node = mp.Nodes[node_id]
    cond = mp.CreateNewCondition("PointLoadCondition3D1N", cond_id, [node_id], prop)
    load_sub_mp.AddCondition(cond)
    load_sub_mp.AddNode(node, 0)
    nodes_with_load.append((node, area))

L_max_Pa = L_MAX_KNM2 * 1000.0
print(f"{'step':>5} {'L[kN/m2]':>10} {'hard_max[kN/m]':>15} {'converged':>10} {'max_disp_z[m]':>15}")
for step in range(N_STEPS):
    analysis.time = analysis._AdvanceTime()
    t_frac = (step + 1) / N_STEPS
    L = t_frac * L_max_Pa

    for node, area in nodes_with_load:
        node.SetSolutionStepValue(sma.POINT_LOAD, [0.0, 0.0, -L * area])

    analysis.InitializeSolutionStep()
    converged = analysis._GetSolver().SolveSolutionStep()
    analysis.FinalizeSolutionStep()

    max_s11 = 0.0
    for elem in membrane_mp.Elements:
        stresses = elem.CalculateOnIntegrationPoints(KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
        for s in stresses:
            max_s11 = max(max_s11, s[0])

    max_disp_z = max(abs(n.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)[2]) for n in mp.Nodes)

    e_kNm = max_s11 * THICKNESS / 1000.0
    L_kNm2 = L / 1000.0
    print(f"{step+1:5d} {L_kNm2:10.4f} {e_kNm:15.4f} {str(converged):>10} {max_disp_z:15.5f}")

analysis.Finalize()
