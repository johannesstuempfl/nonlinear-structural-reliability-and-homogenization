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
# IMPORTANT: use FORM_HLRF, not FORM_fmincon. FORM_fmincon.py in this ERA
# package has been hard-customized for syst_4's specific 7-variable frame
# problem - it hardcodes indices x[3]/x[5] and physical load bounds into its
# constraint list, and will crash (index out of range) on our 2-variable
# problem. FORM_HLRF.py is the clean, general, unmodified Rackwitz-Fiessler
# implementation - which is also literally the method the paper itself cites
# (reference [15]), so it's the more faithful choice here anyway.
from ERA_Distribution_Classes_Python.Classes.FORM_HLRF import FORM_HLRF

# Kratos's own per-step logging (STEP/TIME lines, mdpa read summaries, etc.)
# is very verbose and would otherwise drown out the [call N] trace below,
# which is what actually tells you whether FORM's search is behaving.
KratosMultiphysics.Logger.GetDefaultOutput().SetSeverity(KratosMultiphysics.Logger.Severity.WARNING)

THICKNESS = 0.001  # m, converts Pa (true stress, what Kratos computes) -> kN/m
                   # (the resultant convention the paper and StructuralMaterials.json use)


def _run_static_kratos(L_kNm2: float) -> float:
    """
    Runs ONE complete, standalone static/non-linear Kratos analysis: reads
    formfinding_result_model.mdpa fresh (Stage 1's equilibrium-shape output),
    ramps a force-controlled snow load from 0 up to L_kNm2 [kN/m^2], and
    returns the max membrane stress in the warp direction [kN/m].

    This is the generalized version of run_phase2.py's body: same physics,
    same tributary-area point-load setup, but as a function of an arbitrary
    target load instead of a fixed 0->1.2 kN/m^2 ramp. Every call below is a
    FRESH Kratos Model/analysis (not reusing state between calls) - simplest
    and safest way to avoid any accumulated-deformation bugs, at the cost of
    re-reading the ~500-node mesh every time (fast, a fraction of a second).
    """
    L_max_Pa = max(L_kNm2, 0.0) * 1000.0

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
    n_steps = max(15, math.ceil(L_kNm2 / 0.05))

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

    base_props = KratosMultiphysics.Properties(2)
    base_props.SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, sma.LinearElasticPlaneStress2DLaw())
    # (or cla.LinearElasticOrthotropic2DLaw() here instead, if you want wrinkling
    #  + orthotropic combined - set that law's 4 variables on base_props too)
    base_props.SetValue(KratosMultiphysics.YOUNG_MODULUS, 600000000.0)
    base_props.SetValue(KratosMultiphysics.POISSON_RATIO, 0.4)

    prop.SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, cla.WrinklingLinear2DLaw())
    prop.AddSubProperties(base_props)
    
    for elem in membrane_mp.Elements:
        elem.Initialize(mp.ProcessInfo)
    # Tributary plan-projected area per node - see run_phase2.py part 2 for
    # the full explanation. Recomputed every call since this is a fresh
    # Model/mesh read each time (cheap: ~1000 triangles).
    tributary_area = {}
    for elem in membrane_mp.Elements:
        nodes = list(elem.GetNodes())
        x1, y1 = nodes[0].X0, nodes[0].Y0
        x2, y2 = nodes[1].X0, nodes[1].Y0
        x3, y3 = nodes[2].X0, nodes[2].Y0
        area = 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        for n in nodes:
            tributary_area[n.Id] = tributary_area.get(n.Id, 0.0) + area / 3.0

    # One PointLoadCondition3D1N per membrane node - see run_phase2.py part 3.
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

    # Ramp 0 -> L_max_Pa over n_steps substeps, collecting every Gauss point's
    # S11 (warp-direction) stress only at the FINAL step (that's the load
    # level the caller actually asked for).
    all_s11 = []
    for step in range(n_steps):
        analysis.time = analysis._AdvanceTime()
        t_frac = (step + 1) / n_steps
        L = t_frac * L_max_Pa

        for node, area in nodes_with_load:
            node.SetSolutionStepValue(sma.POINT_LOAD, [0.0, 0.0, -L * area])

        analysis.InitializeSolutionStep()
        # SolveSolutionStep() returns True/False - whether Newton-Raphson
        # actually satisfied the convergence criterion this step. Unlike
        # run_phase2.py, we DO check this here and print a loud warning if it
        # fails, because a silently-non-converged step here would feed a
        # slightly-wrong stress value into FORM's finite-difference gradient,
        # which is exactly the kind of subtle corruption that caused the
        # divergence episode documented in the module docstring / GUIDE.md
        # gotcha #8.
        converged = analysis._GetSolver().SolveSolutionStep()
        analysis.FinalizeSolutionStep()

        if not converged:
            print(f"    !! non-convergence at L_target={L_kNm2:.4f} kN/m^2, "
                  f"substep {step+1}/{n_steps} (L_sub={L/1000.0:.4f})", flush=True)

        if step == n_steps - 1:
            all_s11 = []
            for elem in membrane_mp.Elements:
                stresses = elem.CalculateOnIntegrationPoints(
                    KratosMultiphysics.PK2_STRESS_VECTOR, mp.ProcessInfo)
                for s in stresses:
                    all_s11.append(s[0])   # index 0 = S11 = local axis 1 = warp direction

    analysis.Finalize()

    # ------------------------------------------------------------------
    # Smooth (p-norm) approximation of "the maximum stress anywhere in the
    # mesh", instead of a hard max().
    #
    # Why this matters: with ~1000 elements x a few Gauss points each, WHICH
    # single Gauss point holds the current maximum can swap as the load
    # changes by an infinitesimally small amount (two regions of the membrane
    # can have very close peak stresses, and their ranking flips as load
    # increases). A hard max() is then technically discontinuous at that
    # crossover: the reported value jumps instead of varying smoothly, even
    # though the underlying physical stress FIELD itself is perfectly smooth.
    # FORM's finite-difference gradient estimation assumes local smoothness,
    # so this kink was corrupting the search (see module docstring).
    #
    # The p-norm ||s||_p = (sum(s_i^p))^(1/p) converges to max(s) as p -> inf,
    # while staying differentiable everywhere for finite p. We normalize by
    # the hard max first (ratios = s / max(s), all <= 1) purely for numerical
    # stability - without it, s_i^30 would overflow float64 for s_i ~ 1e7-1e8
    # ------------------------------------------------------------------
    all_s11 = np.array(all_s11)
    hard_max = np.max(all_s11)
    # Increase p from 30.0 to 100.0 in the effort of bringing hard_max and soft_max closer together
    p = 100.0
    ratios = all_s11 / hard_max
    smooth_max = hard_max * np.sum(np.clip(ratios, 0.0, None) ** p) ** (1.0 / p)
    # Check the smooth_max function
    # print(f"    hard_max={hard_max*THICKNESS/1000:.4f}  smooth_max={smooth_max*THICKNESS/1000:.4f}")
    return smooth_max * THICKNESS / 1000.0  # Pa -> kN/m


_CALL_COUNT = [0]  # plain list so the closure below can mutate it (no `nonlocal` needed)


def t_S_kratos(L):
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
    scalar_in = (np.ndim(L) == 0)
    L_arr = np.atleast_1d(np.asarray(L, dtype=float))
    out = np.empty_like(L_arr)
    for i, Lv in enumerate(L_arr):
        _CALL_COUNT[0] += 1
        # NOTE: this float(Lv) conversion is also what makes autograd fail
        # cleanly (TypeError) if FORM_HLRF tries automatic differentiation
        # first, correctly forcing it to fall back to finite differences -
        # see GUIDE.md gotcha #10. Don't remove it thinking it's redundant.
        val = _run_static_kratos(float(Lv))
        out[i] = val
        print(f"  [call {_CALL_COUNT[0]:4d}] L={Lv:9.4f} kN/m^2  ->  e={val:9.4f} kN/m", flush=True)
    return out[0] if scalar_in else out


if __name__ == "__main__":
    print("===Test Phase by Jo===")
    
    N_out = t_S_kratos(0.0)
    print(f"\nN = {N_out}")
    
    
    
    # ------------------------------------------------------------------
    # Regression check: t_S_kratos should reproduce run_phase2.py's already-
    # validated curve at L=0.6 and L=0.9 (5.517 and 7.070 kN/m). If these
    # don't match closely, something about the generalization broke - don't
    # trust anything below until these two lines look right.
    # ------------------------------------------------------------------
    # print("=== Sanity check against Phase 2 results ===")
    # e_06 = t_S_kratos(0.6)
    # e_09 = t_S_kratos(0.9)
    # print(f"t_S_kratos(0.6) = {e_06:.3f} kN/m  (Phase 2 gave 5.517, paper e_k=5.7)")
    # print(f"t_S_kratos(0.9) = {e_09:.3f} kN/m  (Phase 2 gave 7.070, paper e_d,a=7.3)")

    # # ------------------------------------------------------------------
    # # Random variables - Fusseder et al. 2021, Table 1. Same ERADist('...',
    # # 'MOM', [mean, std]) pattern as syst_4; 'MOM' = method of moments, so the
    # # second argument is [mean, std], not [mean, cov] - std = mean * cov.
    # # ------------------------------------------------------------------
    # mu_L, cov_L = 0.34, 0.3
    # L_dist = ERADist('gumbel', 'MOM', [mu_L, mu_L * cov_L])       # snow load, kN/m^2

    # mu_M, cov_M = 1.0, 0.1
    # M_dist = ERADist('lognormal', 'MOM', [mu_M, mu_M * cov_M])    # membrane tensile strength

    # marginal_dist = [M_dist, L_dist]   # x[0] = M, x[1] = L - keep this order consistent everywhere below
    # nataf = ERANataf(M=marginal_dist, Correlation=np.eye(2))       # uncorrelated, like syst_4's R_xx

    # gamma_F = 1.5   # partial safety factor, load side
    # gamma_M = 1.4   # partial safety factor, resistance side (from the Technical Specification, per the paper)

    # # Characteristic values: 98th percentile of the load, 5th percentile of
    # # the resistance - standard Eurocode 0 convention, same as syst_4's s_k/m_k.
    # l_k = L_dist.icdf(0.98)
    # m_k = M_dist.icdf(0.05)
    # print(f"\nl_k = {l_k:.4f} kN/m^2  (paper: 0.6)")
    # print(f"m_k = {m_k:.4f} kN/m^2  (paper: implied ~0.83-0.85 from Fig 2 scale)")

    # # ------------------------------------------------------------------
    # # Design values d_a, d_b - paper eq. (11). This is the semi-probabilistic
    # # design computed ONCE, deterministically, before any reliability
    # # analysis: it answers "how much design margin do we get from applying
    # # the two partial safety factors, under design option (a) vs (b)?"
    # #   option (a): apply gamma_F to the LOAD before computing its effect (tS)
    # #   option (b): apply gamma_F to the EFFECT (tS output) directly
    # # These give the same answer only if tS is linear - it isn't (that's the
    # # whole point of the paper), so d_a != d_b in general.
    # # ------------------------------------------------------------------
    # e_d_a_input = t_S_kratos(gamma_F * l_k)   # tS(gamma_F * l_k) - option (a)'s effect
    # e_k_for_b = t_S_kratos(l_k)               # tS(l_k) - option (b) applies gamma_F AFTER this
    # d_a = gamma_M * e_d_a_input / m_k
    # d_b = gamma_M * gamma_F * e_k_for_b / m_k
    # print(f"\ntS(gamma_F * l_k) = {e_d_a_input:.4f} kN/m  (paper e_d,a=7.3)")
    # print(f"tS(l_k)           = {e_k_for_b:.4f} kN/m  (paper e_k=5.7)")
    # print(f"d_a = {d_a:.5f}")
    # print(f"d_b = {d_b:.5f}")

    # # ------------------------------------------------------------------
    # # Limit-state functions - paper eq. (12): g = d*M - tS(L). This is the
    # # direct analog of syst_4's g_opt_1_FORM: resistance_side - action_side.
    # # x[..., 0] / x[..., 1] (ellipsis indexing) instead of x[0]/x[1] or
    # # x[:,0]/x[:,1] is what makes this work correctly whether FORM_HLRF calls
    # # g with a single point (x.shape == (2,)) or a perturbation batch
    # # (x.shape == (2,2)) - see t_S_kratos's docstring above.
    # # ------------------------------------------------------------------
    # def g_opt_a(x):
    #     x = np.asarray(x, dtype=float)
    #     return d_a * x[..., 0] - t_S_kratos(x[..., 1])

    # def g_opt_b(x):
    #     x = np.asarray(x, dtype=float)
    #     return d_b * x[..., 0] - t_S_kratos(x[..., 1])

    # # ------------------------------------------------------------------
    # # FORM via HLRF (Rackwitz-Fiessler) - syst_4 used FORM_fmincon, we use
    # # FORM_HLRF instead (see the import comment above for why). dg=[] tells
    # # it to estimate the gradient itself (autograd first, finite differences
    # # as the fallback that actually gets used here). u0=0 starts the search
    # # at the mean point in standard-normal space, same as syst_4.
    # #
    # # maxit/tol: HLRF's own convergence check is ||u_{k+1} - u_k|| <= tol in
    # # standard-normal space. The DEFAULT tol=1e-6 turned out to be tighter
    # # than our Kratos-based g(x) can reliably resolve (a real FE solve always
    # # carries some small numerical noise floor), so it was capped at
    # # maxit=... iterations without satisfying that criterion. Loosening tol to
    # # 1e-4 (still tight enough to trust the resulting beta to 3 significant
    # # figures) let it actually terminate cleanly instead of just running out
    # # of iterations. If FORM_HLRF prints "may have converged to wrong value!"
    # # afterwards, that means it STILL hit maxit before converging - see the
    # # module docstring for the current status of option (b).
    # # ------------------------------------------------------------------
    # print("\n=== FORM (HLRF) - Design option (a) ===")
    # u_star_a, x_star_a, beta_a, Pf_a, _, _ = FORM_HLRF(
    #     g=g_opt_a, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

    # print("\n=== FORM (HLRF) - Design option (b) ===")
    # u_star_b, x_star_b, beta_b, Pf_b, _, _ = FORM_HLRF(
    #     g=g_opt_b, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

    # print("\n\n=== SUMMARY ===")
    # print(f"Design option (a): beta = {beta_a:.3f}   (paper: 4.96)")
    # print(f"Design option (b): beta = {beta_b:.3f}   (paper: 5.55)")
