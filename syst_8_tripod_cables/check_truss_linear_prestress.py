# One-off diagnostic: does TrussLinearElement3D2N (the genuinely small-
# displacement truss confirmed to exist in check_linear_cable_elements.py)
# actually support prestress via TRUSS_PRESTRESS_PK2, the same way
# TrussElement3D2N/CableElement3D2N do? Rather than assume, build a minimal
# 2-node truss, set prestress, apply ZERO external load, and check whether
# the reported stress comes back as the prestress value - if it does, linear
# theory + prestress works together; if it comes back 0 (or errors), it
# doesn't.
import sys
import json
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

sys.path.insert(0, "/workspace")
KratosMultiphysics.Logger.GetDefaultOutput().SetSeverity(KratosMultiphysics.Logger.Severity.WARNING)

CROSS_AREA = 0.000113097
YOUNG_MODULUS = 205e9
PRESTRESS_PK2 = 265258238.5   # Pa - same value used in tripod_model_functions.py

model = KratosMultiphysics.Model()
mp = model.CreateModelPart("Structure")
mp.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3

params_dict = {
    "problem_data": {"problem_name": "truss_test", "parallel_type": "OpenMP", "echo_level": 0, "start_time": 0.0, "end_time": 1.0},
    "solver_settings": {
        "solver_type": "static",
        "model_part_name": "Structure",
        "domain_size": 3,
        "echo_level": 0,
        "analysis_type": "linear",
        "model_import_settings": {"input_type": "use_input_model_part"},
        "time_stepping": {"time_step": 1.0},
        "convergence_criterion": "residual_criterion",
        "displacement_relative_tolerance": 1e-4,
        "displacement_absolute_tolerance": 1e-8,
        "residual_relative_tolerance": 1e-4,
        "residual_absolute_tolerance": 1e-8,
        "max_iteration": 50,
        "rotation_dofs": False,
        "volumetric_strain_dofs": False
    },
    "processes": {"constraints_process_list": [], "loads_process_list": [], "list_other_processes": []},
    "output_processes": {}
}
parameters = KratosMultiphysics.Parameters(json.dumps(params_dict))
analysis = StructuralMechanicsAnalysis(model, parameters)

mp.CreateNewNode(1, 0.0, 0.0, 0.0)
mp.CreateNewNode(2, 1.0, 0.0, 0.0)
for node in mp.Nodes:
    node.AddDof(KratosMultiphysics.DISPLACEMENT_X, KratosMultiphysics.REACTION_X)
    node.AddDof(KratosMultiphysics.DISPLACEMENT_Y, KratosMultiphysics.REACTION_Y)
    node.AddDof(KratosMultiphysics.DISPLACEMENT_Z, KratosMultiphysics.REACTION_Z)

props = mp.GetProperties()[1]
props.SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, sma.TrussConstitutiveLaw())
props.SetValue(sma.CROSS_AREA, CROSS_AREA)
props.SetValue(KratosMultiphysics.YOUNG_MODULUS, YOUNG_MODULUS)
props.SetValue(sma.TRUSS_PRESTRESS_PK2, PRESTRESS_PK2)
props.SetValue(KratosMultiphysics.DENSITY, 7850.0)

mp.Nodes[1].Fix(KratosMultiphysics.DISPLACEMENT_X)
mp.Nodes[1].Fix(KratosMultiphysics.DISPLACEMENT_Y)
mp.Nodes[1].Fix(KratosMultiphysics.DISPLACEMENT_Z)
mp.Nodes[2].Fix(KratosMultiphysics.DISPLACEMENT_X)
mp.Nodes[2].Fix(KratosMultiphysics.DISPLACEMENT_Y)
mp.Nodes[2].Fix(KratosMultiphysics.DISPLACEMENT_Z)

try:
    mp.CreateNewElement("TrussLinearElement3D2N", 1, [1, 2], props)
    print("TrussLinearElement3D2N created OK")
except Exception as e:
    print("Element creation FAILED:", e)
    sys.exit(1)

analysis.Initialize()
analysis.time = analysis._AdvanceTime()
analysis.InitializeSolutionStep()
converged = analysis._GetSolver().SolveSolutionStep()
analysis.FinalizeSolutionStep()

elem = mp.GetElement(1)
stresses = elem.CalculateOnIntegrationPoints(KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
stress_pa = stresses[0][0]
analysis.Finalize()

print(f"\nZero external load, prestress set to {PRESTRESS_PK2/1e6:.3f} MPa")
print(f"Reported stress: {stress_pa/1e6:.3f} MPa")
print("MATCHES prestress -> linear truss + prestress works together" if abs(stress_pa - PRESTRESS_PK2) < 1.0
      else "DOES NOT match prestress -> something is off, needs investigation")
