# syst_7_membrane: Kratos membrane pipeline — reference guide

This document explains everything set up so far for the hypar membrane reliability
analysis: the Kratos concepts you need, how the pipeline is structured, every
non-obvious gotcha we hit and why, and how it all maps onto the `syst_4` pattern
you already know (`t_S`, `g_opt_1_FORM`, `FORM_HLRF`/`FORM_fmincon`).

Read this once, then read the heavily-commented `run_phase2.py` and
`run_phase3_FORM.py` while you write your own notebook — they're built to be
read top to bottom like a tutorial.

---

## 1. Why Docker + Kratos at all

Kratos Multiphysics has no macOS wheel and no Linux/arm64 wheel — only Linux
x86_64 and Windows. `kratos_docker/` builds a small `python:3.11-slim` image
(`Dockerfile`) with Kratos + numpy/scipy/autograd/jupyter installed via pip,
and runs it through Docker Desktop's Rosetta-based x86_64 emulation on your
Apple Silicon Mac. `run.sh` mounts the whole project root at `/workspace`
inside the container and `cd`s there first, so **every relative path in a
command you pass to `run.sh` is relative to the project root**, not to
`kratos_docker/`.

```
bash run.sh bash -c "cd syst_7_membrane/hypar.gid && python3 some_script.py"
```

GiD (the desktop app) is used **only** for authoring geometry/mesh/BCs and
exporting `.mdpa` + `ProjectParameters.json` + `StructuralMaterials.json`.
Its own bundled solver is never used — everything actually *runs* through the
Docker container instead, because GiD's bundled Kratos build needs a
different, older macOS toolchain we deliberately skipped.

---

## 2. Kratos concepts you need

Kratos is a C++ FE core with Python bindings. Almost everything you touch from
Python is one of these objects:

- **`Model`** — a top-level container that owns one or more `ModelPart`s. You
  create one per analysis: `model = KratosMultiphysics.Model()`.

- **`ModelPart`** — holds `Nodes`, `Elements`, `Conditions`, `Properties`, a
  `ProcessInfo` (global scalars like current `TIME`/`STEP`), and named
  **sub-model-parts** (groups, e.g. `"Parts_Membrane_Membrane_Auto1"`,
  `"DISPLACEMENT_Displacement_Auto1"`). Sub-model-parts share the same
  underlying `Node`/`Element` objects as the parent — they're just named
  views/groups, which is how GiD exports "this group of nodes has this BC" or
  "this group of elements gets this material".

- **`Properties`** — a material/section property set, referenced by elements
  via a numeric `properties_id`. `StructuralMaterials.json` assigns a
  constitutive law + variables (Young's modulus, prestress, thickness, ...) to
  a properties id, matched by sub-model-part name. Important: **the mdpa file
  itself must already declare the properties id as existing** (even as an
  empty stub, `Begin Properties 1 / End Properties`) before elements can
  reference it — the JSON only fills in *values*, it doesn't create the slot.
  This bit us once (see gotcha #5 below).

- **Elements vs. Conditions** — Elements (`MembraneElement3D3N`,
  `CableElement3D2N`) are the physical continuum: they have stiffness and
  compute internal forces from strain. Conditions
  (`PointLoadCondition3D1N`, `SurfaceLoadCondition3D3N`) apply external loads —
  they only contribute to the right-hand side (external force), not stiffness.
  If you need a load somewhere the mesh doesn't already have a condition
  entity, you can create one directly in Python:
  `mp.CreateNewCondition("PointLoadCondition3D1N", id, [node_id], properties)`.

- **DOFs** — degrees of freedom (`DISPLACEMENT_X`, etc.) must be added to
  nodes (`AddDofs()`) before solving; the solver's `AddVariables()` /
  `AddDofs()` calls handle this, always in that order, always before the mesh
  is read from file.

- **`AnalysisStage`** (e.g. `StructuralMechanicsAnalysis`) — wraps the whole
  lifecycle: `Initialize()` (read mesh, add DOFs, read materials, build
  processes) → `RunSolutionLoop()` (repeated `InitializeSolutionStep()` /
  `SolveSolutionStep()` / `FinalizeSolutionStep()` / `OutputSolutionStep()`) →
  `Finalize()`. Calling `.Run()` does all three for you. **We instead drive
  the loop manually** (call `Initialize()` once, then loop
  `InitializeSolutionStep()` / `analysis._GetSolver().SolveSolutionStep()` /
  `FinalizeSolutionStep()` ourselves) so we can set a different point load at
  every step. Note: the installed Kratos version (10.3.0) does **not** have
  the convenience wrapper `analysis.SolveSolutionStep()` that newer
  Kratos/GitHub-master versions do — you must call
  `analysis._GetSolver().SolveSolutionStep()` directly, and it **returns a
  bool** telling you whether that step actually converged. Always check it.

- **`Parameters`** — Kratos's JSON wrapper (`KratosMultiphysics.Parameters(json_string)`).
  Solver settings are validated strictly against a schema (`GetDefaultParameters()`),
  so unexpected/missing keys throw hard errors — this is the source of most
  "works in one Kratos version, not another" pain, since GiD's bundled
  Kratos-interface templates were generated against a different Kratos version
  than the pip-installed 10.3.0.

- **`.mdpa`** — Kratos's plain-text mesh format: `Begin Properties` /
  `Begin Nodes` / `Begin Elements <Type>` / `Begin Conditions <Type>` /
  `Begin SubModelPart <name>` blocks. Element lines are
  `id  properties_id  node1  node2  ...`.

---

## 3. The two-stage pipeline

### Stage 1 — form-finding (`hypar.gid/ProjectParameters.json`, `solver_type: "formfinding"`)

Starts from the rough GiD-authored NURBS-interpolated mesh (`hypar.mdpa`) with
an assigned **isotropic prestress** and no external load, then iterates using
the **Updated Reference Strategy** (Bletzinger & Ramm 1999): at every Newton
iteration it moves the *reference* (undeformed) configuration towards the
current one — that's the repeated `MESH MOVED` log line — until the shape
stops changing under pure prestress. That's the found equilibrium (an
anticlastic minimal surface for isotropic prestress with straight boundaries).

Two things this solver does that a normal static solver doesn't:

1. It needs an extra `"projection_settings"` block in `solver_settings` (GiD's
   template omitted it in our Kratos version, defaulting to a broken
   placeholder — see gotcha #2). This defines how the local material axes
   (warp/fill) get oriented on the curved surface.
2. Its `Finalize()` method (if `write_formfound_geometry_file` is true, the
   default) calls a C++ routine `FormfindingStrategy.WriteFormFoundMdpa()`
   that **writes the equilibrium shape out to a brand new mdpa file**:
   `formfinding_result_model.mdpa`. This is the single most important
   artifact of Stage 1 — it's a complete mesh (same topology, same property
   ids, same sub-model-parts) but with the *converged* node coordinates baked
   in as the new `X0/Y0/Z0`. That's what makes Stage 2 possible without any
   in-process state-sharing trickery: just read this file fresh.

Run it:
```
bash run.sh bash -c "cd syst_7_membrane/hypar.gid && python3 MainKratos.py"
```

Validate the shape (`check_shape.py`): corners should sit exactly at your input
coordinates, and for this specific hypar (straight boundary generators, 1:1
isotropic prestress ratio) the plan-center node should sit almost exactly at
the bilinear average of the corner heights (z=1.0) — that's the analytical
signature of a correct minimal-surface equilibrium.

### Stage 2 — static load response (`run_phase2.py`, then generalized in `run_phase3_FORM.py`)

A **completely separate, fresh** analysis: reads `formfinding_result_model.mdpa`
(not the original `hypar.mdpa`!) as the new reference mesh, re-applies the same
`StructuralMaterials.json` (so the prestress term is active from the first
step), and ramps a **force-controlled** snow load from 0 up to a target value.

"Force-controlled" (the paper explicitly says this, citing Crisfield) means:
fixed, non-follower dead loads — not a pressure that re-projects onto the
deforming surface. We implement this as one `PointLoadCondition3D1N` per
membrane node, each carrying a **fixed** force equal to
`-L[Pa] * tributary_plan_area[node]`, where the tributary area is the
1/3-share of each adjacent triangle's *plan-projected* (x,y only, z dropped)
area — computed once from the reference mesh and held constant through the
ramp. This sidesteps any ambiguity between curved-surface-area pressure vs.
projected-area load, and matches the paper's stated convention.

Why ramp at all instead of applying the full load in one step? Because this is
a **geometrically non-linear** solve (`analysis_type: "non_linear"`) — Newton-
Raphson needs small enough load increments to stay in its convergence radius.
See gotcha #7 for how fine "small enough" needs to be.

---

## 4. Gotchas — read this before you touch tolerances or units again

1. **`PRESTRESS_VECTOR` is true stress (Pa), not a force resultant (N/m).**
   The paper's material is expressed as pre-integrated-over-thickness
   quantities (E in kN/m, prestress in kN/m — i.e. already "per unit width",
   thickness-independent). Kratos's `MembraneElement3D3N` instead expects
   `PRESTRESS_VECTOR` as **true stress** in Pa, and internally multiplies by
   `THICKNESS` to get the actual force. So `YOUNG_MODULUS` correctly needs
   `E[Pa] = E_paper[kN/m] * 1000 / thickness[m]`, and **so does prestress**:
   `PRESTRESS_VECTOR[Pa] = prestress_paper[kN/m] * 1000 / thickness[m]`. We
   initially only converted `YOUNG_MODULUS` and left prestress in raw kN/m
   units (1000x too weak) — the form-found *shape* was unaffected (an
   isotropic 1:1 prestress ratio gives the same equilibrium shape regardless
   of magnitude), which is exactly why this bug survived Phase 1 validation
   undetected. We caught it with a tiny standalone unit test
   (`check_prestress_units.py`): build a flat 1×1 m clamped patch with only
   the prestress active (no elastic strain since it can't move), read the
   reaction forces, and check whether they sum to the expected 3000 N/edge
   (force-resultant convention) or 3 N/edge (stress convention needing
   ×thickness). Cable prestress (`TRUSS_PRESTRESS_PK2`) does **not** have this
   issue — cables use true stress × `CROSS_AREA` directly, which is the
   standard, unambiguous convention.

2. **Missing `"projection_settings"` block → cryptic `PLEASE_SPECIFY` error.**
   `FormfindingMechanicalSolver` requires this block; if the GiD-exported JSON
   omits it, Kratos silently falls back to an internal placeholder default
   (`variable_name: "PLEASE_SPECIFY"`) instead of erroring immediately, so the
   real failure only surfaces later, deep in a C++ utility, with a confusing
   message. Also: the correct `variable_name` for this utility must be a true
   `Array3` Kratos variable with `_X/_Y/_Z` subcomponents (e.g. `LOCAL_AXIS_1`)
   — variables like `PRESTRESS_AXIS_1_GLOBAL` exist but are `Vector`-typed and
   will fail this specific utility's type check.

3. **Absolute convergence tolerances must scale with your force magnitude.**
   `residual_absolute_tolerance` / `displacement_absolute_tolerance` are
   tolerances in raw Newtons/meters, not relative fractions. When we fixed the
   1000x prestress unit bug (gotcha #1), the exact same absolute tolerance
   that worked before was suddenly 1000x too tight and form-finding stopped
   converging. Rule of thumb: keep the absolute tolerance so loose it never
   actually binds (e.g. `1e-6` relative to your problem's force scale) and let
   the **relative** tolerance (`1e-3`, scale-invariant) do the real work.

4. **Kratos version mismatch between GiD's template and the pip package.**
   GiD's bundled Kratos-interface files were generated against a different
   Kratos release than the pip-installed 10.3.0. This caused several small,
   independent schema breaks: a `list_other_processes` entry referencing a
   module (`formfinding_IO_process`) that doesn't exist in 10.3.0; an
   `output_precision` given as `[7]` (array) instead of `7` (plain int);
   `VELOCITY`/`ACCELERATION` listed as output variables even though the
   (static-type) formfinding solver never allocates them. None of these are
   conceptual errors — just treat any "variable/module not known" or
   "type mismatch" error as version drift and fix the JSON directly.

5. **`WriteFormFoundMdpa`'s own export has a bug: it references real property
   ids but only declares an empty stub for property 0.** The *original*
   GiD-exported `hypar.mdpa` has all elements reference property id `0` (a
   placeholder), and lets `material_import_settings` reassign the real ids (1
   for membrane, 2 for cable) afterward, by sub-model-part name — the file
   only needs to declare `Begin Properties 0 / End Properties`. Kratos's own
   `formfinding_result_model.mdpa` export, by contrast, bakes in the *already
   assigned* real ids (1, 2) directly into the element lines, but only writes
   a stub for property 0 — so reading it back fails with `Properties #2 is not
   found`. Fix: manually add empty `Begin Properties 1 / End Properties` and
   `Begin Properties 2 / End Properties` stubs right after the existing
   property-0 stub. (The materials JSON re-populates real values into them
   regardless, exactly as it does for property 0 in the original file.)

6. **The formfinding solver doesn't behave like a normal solver for
   post-hoc Python inspection.** After `analysis.Run()` completes (which calls
   `Finalize()`, which calls `WriteFormFoundMdpa`), trying to read
   `node.GetSolutionStepValue(DISPLACEMENT)` or `REACTION` afterwards can throw
   "variable not in this container's variables list" — some internal state
   gets touched by that C++ export routine. If you need to inspect the model
   part's state, do it **before** calling `Finalize()`: call `Initialize()`
   then `RunSolutionLoop()` yourself (skipping the wrapped `.Run()`), inspect,
   then call `Finalize()` when you're done. Also, `REACTION` specifically is
   never registered as a solution-step variable by the formfinding solver at
   all (unlike a normal static solver, where it's a standard paired DOF
   variable) — don't expect to read it there under any circumstances.

7. **A hard `max()` over ~2000 Gauss points is not smooth enough for
   gradient-based reliability methods.** FORM (HLRF/fmincon) estimates the
   limit-state gradient via finite differences, which assumes local
   smoothness. Reporting "the maximum stress anywhere in the mesh" as a hard
   `max()` is *technically* discontinuous in the input parameters, because
   which single Gauss point holds that maximum can swap as the load changes
   by an infinitesimal amount — and near such a swap, the reported value jumps
   instead of varying smoothly. We saw exactly this: stress changing by ~5%
   for a load change of 0.0001 kN/m². Fix: replace the hard max with a smooth
   **p-norm** aggregation, `smooth_max = max(s) * (sum((s_i/max(s))^p))^(1/p)`
   with `p≈30` — converges arbitrarily close to the true max while staying
   differentiable everywhere. This is a standard technique in
   stress-constrained structural optimization, and defensible in a thesis.

8. **Newton-Raphson step-size requirements grow with load, and FORM's search
   goes to load levels you wouldn't naively expect.** Phase 2's fixed 20 steps
   up to 1.2 kN/m² (0.06 kN/m²/step) worked fine for validating against the
   paper's checkpoints (`L=0.6`, `L=0.9`). But FORM's design-point search
   legitimately needs to evaluate `tS(L)` out around `L≈1.3–1.5 kN/m²` — because
   that's roughly where the actual `g(x)=0` boundary sits given the computed
   design multiplier `d`, which is a much higher load than the "nominal"
   design loads themselves (the FORM design point sits deep in the upper tail
   of the load distribution). At that range, a step size that was fine at
   lower loads started intermittently failing to converge. We confirmed via a
   one-off fine diagnostic (`investigate_high_load.py`, 80 uniform steps up to
   1.6 kN/m²) that the underlying physics is completely smooth and
   well-behaved all the way up — no wrinkling onset, no stiffness loss, no
   snap-through — so this was purely a step-resolution problem, not a genuine
   physical limit. Fix: scale the number of substeps with the *target* load
   (`n_steps = max(15, ceil(L / 0.05))`), so resolution never gets coarser
   than proven-safe regardless of how far FORM searches.

9. **`FORM_fmincon.py` in your ERA package is hard-customized for the syst_4
   7-variable frame problem** — it has hardcoded indices (`x[3]`, `x[5]`) and
   physical bounds (`upper_L1 = 6.0`, `upper_L2 = 2.0`) baked into its
   constraint list, specific to that problem's variable ordering. It will
   break immediately (index out of bounds) on our 2-variable membrane problem.
   `FORM_HLRF.py` is the clean, general, unmodified implementation — use that
   instead. It's also more faithful here anyway, since it's literally the
   Rackwitz-Fiessler method the paper itself cites (reference [15]).

10. **`autograd` cleanly fails on our Kratos-backed `g(x)`, and that's the
    correct behavior.** Both `FORM_HLRF` and `FORM_fmincon` try
    `dg = grad(g)` first (automatic differentiation) and only fall back to
    finite differences in the `except` block. Since `g` calls out to Kratos (a
    black-box C++ solver), it can't be autograd-traced — and an explicit
    `float(...)` conversion inside `t_S_kratos` reliably triggers autograd's
    `TypeError` immediately, giving a clean, deterministic fallback to finite
    differences (not silently-wrong gradients). This mirrors exactly what
    `syst_4`'s own `t_S` (calling the custom `Structure()` FE solver) relies
    on — same established, working pattern, nothing new to worry about here.

---

## 5. Mapping onto `syst_4`'s pattern

| syst_4 | syst_7 (membrane) |
|---|---|
| `t_S(l_1, l_2)` — builds a `Structure()`, solves, returns a moment [kNm] | `t_S_kratos(L)` — builds a Kratos `Model`+`StructuralMechanicsAnalysis`, ramps load, returns max warp stress [kN/m] |
| `t_S_vectorized = np.vectorize(t_S, ...)` | `t_S_kratos` already loops internally over array input (see its docstring) |
| `t_R(M_k)` — deterministic resistance | not yet built for syst_7 (paper's resistance side is just `M` directly, no separate resistance model function) |
| `g_opt_1_FORM(x)` = `resistance_side - action_side` | `g_opt_a(x)` = `d_a * x[...,0] - t_S_kratos(x[...,1])`, mirroring eq. (12) of the paper |
| `FORM_fmincon(g=..., dg=[], distr=nataf, u0=0)` | `FORM_HLRF(g=..., dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=..., tol=...)` — **use HLRF, not fmincon** (see gotcha #9) |
| `nataf = ERANataf(M=marginal_dist, Correlation=R_xx)` | identical pattern, just 2 marginals (`M`, `L`) instead of 7 |

The paper's own limit-state function (eq. 12), which `g_opt_a`/`g_opt_b`
implement directly:

```
g = d * M - tS(L),  where
d_a = gamma_M * tS(gamma_F * l_k) / m_k        (option a: PSF applied before tS)
d_b = gamma_M * gamma_F * tS(l_k) / m_k        (option b: PSF applied after tS)
```

with `l_k = L.icdf(0.98)`, `m_k = M.icdf(0.05)`, `gamma_F=1.5`, `gamma_M=1.4`,
`L ~ Gumbel(mean=0.34, cov=0.3)` kN/m², `M ~ Lognormal(mean=1.0, cov=0.1)`
(paper Table 1).

Target results to validate against (Table 2 of the paper): **beta_a = 4.96**,
**beta_b = 5.55**. Where we landed before pausing: beta_a ≈ 4.76 (converged
cleanly, ~4% off — consistent with the known isotropic-material
simplification, see below), beta_b still needs the tighter step resolution
(gotcha #8's fix) to converge properly — that's the next thing to try when you
pick the script back up.

**One more thing to keep in mind:** we're still using an **isotropic**
membrane material (`LinearElasticPlaneStress2DLaw`, single `E`, single `ν`)
as an approximation of the paper's actual orthotropic Münsch-Reinhardt law
with a separately-specified, much lower shear modulus (`G=30` kN/m vs. the
isotropic-equivalent `G≈214` kN/m implied by `E=600`, `ν=0.4`) plus a
wrinkling correction. Phase 2 showed this isotropic approximation already
tracks the paper within ~3% at the two published checkpoints — good enough to
validate the *pipeline*, but expect a few-percent systematic gap in any final
beta numbers until/unless the orthotropic + wrinkling law
(`LinearElasticOrthotropic2DLaw`, `WrinklingLinear2DLaw` — confirmed to exist
in `KratosMultiphysics.ConstitutiveLawsApplication`, see `check_laws.py`) gets
wired in as a refinement.

---

## 6. File-by-file map of what exists now

```
syst_7_membrane/
├── GUIDE.md                  <- this file
├── check_laws.py             one-off: confirms LinearElasticOrthotropic2DLaw
│                             and WrinklingLinear2DLaw exist (for later refinement)
├── check_axis_vars.py        one-off: found the correct Array3 variable name
│                             (LOCAL_AXIS_1) for projection_settings
├── check_prestress_units.py  one-off unit test: proved PRESTRESS_VECTOR is
│                             Pa (true stress), not N/m (see gotcha #1)
└── hypar.gid/                the GiD project: geometry, mesh, GiD-generated
    │                         Kratos config files, and our Python drivers
    ├── MainKratos.py          GiD-generated driver for Stage 1 (form-finding);
    │                         just reads ProjectParameters.json and runs it
    ├── ProjectParameters.json Stage 1 config (solver_type: "formfinding"),
    │                         hand-edited per gotchas #1-4
    ├── StructuralMaterials.json  material properties for Membrane (id 1) and
    │                         Cable (id 2), prestress now unit-correct
    ├── hypar.mdpa             GiD-exported mesh: rough initial guess geometry
    ├── formfinding_result_model.mdpa  <- Stage 1's OUTPUT: the equilibrium
    │                         shape, used as Stage 2's INPUT mesh
    ├── check_shape.py         validates Stage 1's output (corner positions,
    │                         center-height bilinear check)
    ├── check_reference_config.py  one-off: confirmed the Updated Reference
    │                         Strategy already leaves X0=X after convergence
    ├── run_phase2.py          Stage 2 as a standalone script: ramps a fixed
    │                         load 0->1.2 kN/m^2 over 20 steps, prints the
    │                         full tS(L) curve, checks global force balance
    ├── investigate_high_load.py  one-off fine diagnostic (80 steps to 1.6
    │                         kN/m^2) that proved gotcha #8 was pure numerics,
    │                         not real physical instability
    └── run_phase3_FORM.py     Stage 2 generalized into t_S_kratos(L), wired
                              into g_opt_a/g_opt_b and FORM_HLRF - this is
                              the file to build your own notebook from
```

`run_phase2.py` and `run_phase3_FORM.py` now have detailed inline comments
explaining every block — read them next.
