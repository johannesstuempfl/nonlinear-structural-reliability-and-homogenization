"""
Phase 2: static, geometrically non-linear snow-load analysis on the form-found
hypar shape. Read GUIDE.md (in the syst_7_membrane/ parent folder) first if
you haven't already - it explains every Kratos concept and gotcha referenced
in the comments below.

What this script does, in one sentence: take the equilibrium shape Stage 1
(MainKratos.py, solver_type "formfinding") found, ramp a vertical snow load
onto it step by step, and report the resulting max membrane stress in the
warp direction as a function of load - i.e. exactly the t_S(L) function from
Fusseder et al. 2021, Figure 2.

This is Stage 2 as a fixed, one-shot script (load always ramps 0 -> 1.2
kN/m^2 over 20 steps). run_phase3_FORM.py turns the same logic into a
reusable function t_S_kratos(L) callable at any target L, which is what you
need to actually plug into a limit-state function g(x) for FORM.
"""
import json
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

# ============================================================================
# 1. Solver configuration (the Python-dict equivalent of a ProjectParameters.json)
# ============================================================================
# Key differences from Stage 1's ProjectParameters.json (solver_type "formfinding"):
#   - solver_type is "static" here: a normal geometrically non-linear solver,
#     no Updated Reference Strategy, no projection_settings needed.
#   - model_import_settings.input_filename points at
#     "formfinding_result_model" (Stage 1's OUTPUT mesh, with the equilibrium
#     shape already baked in as the reference configuration X0/Y0/Z0) instead
#     of the original "hypar" mesh. This is what makes the snow load apply on
#     top of the already-prestressed equilibrium shape rather than the rough
#     initial guess geometry.
#   - material_import_settings still points at the SAME StructuralMaterials.json.
#     Re-reading the same prestress (PRESTRESS_VECTOR etc.) here is what keeps
#     the membrane "remembering" it's prestressed even in this fresh analysis -
#     the constitutive law adds the prestress term unconditionally, regardless
#     of solver_type, as long as the material property is present.
#   - residual_absolute_tolerance is deliberately loose (1e-2): GUIDE.md
#     gotcha #3 explains why absolute tolerances must be scaled to your
#     problem's force magnitude, not left at whatever default you copied from
#     a different problem.
params_dict = {
    "problem_data": {
        "problem_name": "hypar_static",
        "parallel_type": "OpenMP",
        "echo_level": 1,
        "start_time": 0.0,
        "end_time": 1.0
    },
    "solver_settings": {
        "solver_type": "static",
        "model_part_name": "Structure",
        "domain_size": 3,
        "echo_level": 1,
        "analysis_type": "non_linear",   # geometrically non-linear Newton-Raphson
        "model_import_settings": {
            "input_type": "mdpa",
            "input_filename": "formfinding_result_model"   # Stage 1's OUTPUT, not hypar.mdpa!
        },
        "material_import_settings": {
            "materials_filename": "StructuralMaterials.json"
        },
        "time_stepping": {"time_step": 0.05},   # 1/0.05 = 20 steps from time 0 to end_time=1.0
        "line_search": False,
        "convergence_criterion": "residual_criterion",
        "displacement_relative_tolerance": 1e-3,
        "displacement_absolute_tolerance": 1e-6,
        "residual_relative_tolerance": 1e-3,
        "residual_absolute_tolerance": 1e-6,
        "max_iteration": 50,
        "rotation_dofs": False,
        "volumetric_strain_dofs": False
    },
    "processes": {
        # Same corner supports as Stage 1: fix the 4 corner nodes at
        # DISPLACEMENT=(0,0,0) relative to the new (form-found) reference
        # configuration - i.e. they stay exactly where form-finding left them.
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
        # Deliberately empty: we do NOT use loads_process_list for the snow
        # load, because that mechanism only supports a single UNIFORM value
        # applied to every node/condition in a group. Our load needs a
        # DIFFERENT magnitude per node (proportional to each node's tributary
        # area), so we build and drive the point loads ourselves in Python
        # further down instead.
        "loads_process_list": [],
        "list_other_processes": []
    },
    "output_processes": {}
}

parameters = KratosMultiphysics.Parameters(json.dumps(params_dict))

model = KratosMultiphysics.Model()
analysis = StructuralMechanicsAnalysis(model, parameters)
# Initialize() reads the mesh, adds DOFs, reads materials, builds processes -
# everything EXCEPT actually solving. We call it once, then drive the solve
# loop ourselves below (instead of analysis.Run(), which would also call
# RunSolutionLoop() and Finalize() automatically) because we need to change
# the point-load magnitudes between steps.
analysis.Initialize()

mp = model.GetModelPart("Structure")
membrane_mp = mp.GetSubModelPart("Parts_Membrane_Membrane_Auto1")
support_mp = mp.GetSubModelPart("DISPLACEMENT_Displacement_Auto1")

# ============================================================================
# 2. Tributary area per node (for converting a pressure load into nodal forces)
# ============================================================================
# The snow load is specified as a pressure L [kN/m^2]. To apply it as discrete
# point loads (see part 3), each node needs to carry its "fair share" of the
# surrounding membrane's plan-projected area. Standard FE lumping: each
# triangular element contributes 1/3 of its own area to each of its 3 corner
# nodes. "Plan-projected" means we deliberately use only the reference (X0,Y0)
# coordinates and drop Z - matching the paper's convention that snow load is
# defined per unit PLAN area, not per unit curved-surface area.
tributary_area = {}
for elem in membrane_mp.Elements:
    nodes = list(elem.GetNodes())
    x1, y1 = nodes[0].X0, nodes[0].Y0
    x2, y2 = nodes[1].X0, nodes[1].Y0
    x3, y3 = nodes[2].X0, nodes[2].Y0
    area = 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))  # triangle area, shoelace formula
    for n in nodes:
        tributary_area[n.Id] = tributary_area.get(n.Id, 0.0) + area / 3.0

total_area = sum(tributary_area.values())
print(f"Total plan-projected membrane area (tributary sum): {total_area:.4f} m^2  (expect ~36 m^2 for 6x6 footprint)")

# ============================================================================
# 3. Build one PointLoadCondition3D1N per membrane node
# ============================================================================
# A "Condition" (as opposed to an "Element") only contributes to the external
# force vector, never to stiffness - exactly what we want for an applied load.
# PointLoadCondition3D1N reads the nodal vector variable POINT_LOAD and
# applies it directly as a concentrated force at that single node. We create
# these programmatically (mp.CreateNewCondition(...)) rather than relying on
# anything from the mdpa file, since the snow load wasn't authored in GiD.
load_sub_mp = mp.CreateSubModelPart("SnowLoad")
prop = mp.GetProperties()[1]   # any existing Properties object works; PointLoadCondition3D1N ignores material data
cond_id = 100000               # offset well above the mesh's own element/condition ids to avoid collisions
nodes_with_load = []
for node_id, area in tributary_area.items():
    if area <= 0.0:
        continue
    cond_id += 1
    node = mp.Nodes[node_id]
    cond = mp.CreateNewCondition("PointLoadCondition3D1N", cond_id, [node_id], prop)
    load_sub_mp.AddCondition(cond)
    load_sub_mp.AddNode(node, 0)
    nodes_with_load.append((node, area))   # keep (node, area) pairs so we can rescale the force every step

print(f"Created {len(nodes_with_load)} point-load conditions for the snow load.")

# ============================================================================
# 4. Ramp the load and solve, step by step
# ============================================================================
# Why ramp instead of applying the full load in one step? Because this is a
# geometrically NON-LINEAR solve - Newton-Raphson only converges reliably if
# consecutive steps aren't too far apart. 20 steps to 1.2 kN/m^2 (0.06
# kN/m^2/step) is proven robust for this range (see GUIDE.md gotcha #8 for
# what happens if you push further without also refining the step count).
L_MAX = 1200.0     # Pa = 1.2 kN/m^2 (final/target load for this script)
N_STEPS = 20
THICKNESS = 0.001  # m; converts Kratos's raw stress output (Pa) to the
                   # paper's force-resultant convention (kN/m) - see
                   # GUIDE.md gotcha #1 for why this multiplication is needed.

results = []

for step in range(N_STEPS):
    # _AdvanceTime() moves analysis.time forward by one time_step (0.05); we
    # don't use the value itself for anything physical, it just drives
    # Kratos's internal step counter/logging.
    analysis.time = analysis._AdvanceTime()
    t_frac = (step + 1) / N_STEPS   # 0.05, 0.10, ..., 1.00
    L = t_frac * L_MAX              # current substep's load level, in Pa

    # Force-controlled load: set each node's fixed force directly (not a
    # pressure that re-projects onto the deforming surface every iteration).
    # F_z = -(pressure) * (that node's fixed tributary area).
    total_force_z = 0.0
    for node, area in nodes_with_load:
        fz = -L * area
        node.SetSolutionStepValue(sma.POINT_LOAD, [0.0, 0.0, fz])
        total_force_z += fz

    # These three calls are what analysis.Run()'s RunSolutionLoop() would
    # normally do for you automatically, once per step. We do it manually so
    # we can change POINT_LOAD in between. Note: analysis._GetSolver()
    # .SolveSolutionStep() (not analysis.SolveSolutionStep() - that
    # convenience wrapper doesn't exist in this Kratos version, see GUIDE.md)
    # returns a bool: True if this step's Newton-Raphson actually converged.
    # We don't check it here (run_phase3_FORM.py does, and prints a warning
    # if not), but you should always at least be aware it's available.
    analysis.InitializeSolutionStep()
    analysis._GetSolver().SolveSolutionStep()
    analysis.FinalizeSolutionStep()

    # Read the stress state: CalculateOnIntegrationPoints asks each element
    # for its stress at every Gauss (integration) point. PK2_STRESS_VECTOR is
    # a 3-component vector per Gauss point: [S11, S22, S12] in the ELEMENT'S
    # LOCAL material axes. Because we set PROJECTION_TYPE_COMBO="rotational"
    # and PRESTRESS_AXIS_1_GLOBAL=[1,0,0] in StructuralMaterials.json, local
    # axis 1 (S11, index [0]) is oriented along the warp direction as drawn in
    # the paper's Figure 1 - so max(S11) across the whole mesh is exactly the
    # "max stress in warp direction" the paper plots in Figure 2.
    max_s11 = 0.0
    for elem in membrane_mp.Elements:
        stresses = elem.CalculateOnIntegrationPoints(KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
        for s in stresses:
            max_s11 = max(max_s11, s[0])

    e_kNm = max_s11 * THICKNESS / 1000.0  # Pa -> kN/m resultant (see gotcha #1)
    L_kNm2 = L / 1000.0
    results.append((L_kNm2, e_kNm))
    print(f"step {step+1:2d}  L = {L_kNm2:6.3f} kN/m^2   max stress warp (S11) = {e_kNm:7.3f} kN/m   "
          f"applied Fz = {total_force_z:9.2f} N")

# ============================================================================
# 5. Global equilibrium sanity check
# ============================================================================
# A cheap, powerful correctness check that doesn't depend on the paper's
# numbers at all: total applied external force must be balanced by the total
# support reaction (Newton's third law / static equilibrium, sum(F)=0). This
# is a normal "static" solver (not the formfinding one), so REACTION is a
# properly registered paired DOF variable here and can be read directly -
# unlike in the formfinding stage (GUIDE.md gotcha #6).
total_reaction_z = 0.0
for n in support_mp.Nodes:
    r = n.GetSolutionStepValue(KratosMultiphysics.REACTION)
    total_reaction_z += r[2]
print(f"\nEquilibrium check at final step: sum(REACTION_Z) at supports = {total_reaction_z:.2f} N "
      f"(should be roughly -{-total_force_z:.2f} N, i.e. balance the applied snow load)")

analysis.Finalize()

# ============================================================================
# 6. Compare against the paper's published checkpoints
# ============================================================================
# Fusseder et al. 2021, Figure 2 (left): at the characteristic load l_k=0.6
# kN/m^2 the reported stress is e_k=5.7 kN/m; at the design load l_d=0.9
# kN/m^2 (=gamma_F * l_k with gamma_F=1.5) it's e_d,a=7.3 kN/m. Our 20-step
# ramp is deliberately chosen (L_MAX=1200 Pa, 20 steps) so that steps 10 and
# 15 land EXACTLY on L=0.6 and L=0.9, making a direct comparison trivial.
print("\n=== Summary (compare to paper: e_k=5.7 kN/m at L=0.6, e_d,a=7.3 kN/m at L=0.9) ===")
for L_kNm2, e_kNm in results:
    flag = ""
    if abs(L_kNm2 - 0.6) < 1e-6:
        flag = "  <-- L = l_k"
    elif abs(L_kNm2 - 0.9) < 1e-6:
        flag = "  <-- L = l_d"
    print(f"L={L_kNm2:.3f} kN/m^2 : e={e_kNm:.3f} kN/m{flag}")
