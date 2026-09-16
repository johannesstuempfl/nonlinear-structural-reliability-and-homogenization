# One-off diagnostic to answer: "if I switch the Membrane's constitutive law to
# LinearElasticOrthotropic2DLaw or WrinklingLinear2DLaw, which Kratos Variables
# do I need to add to StructuralMaterials.json (or set via Python), and what
# are they called?"
#
# Why not just read the Kratos C++ source on GitHub? We already hit one real
# mismatch between GitHub's master branch and this project's installed Kratos
# build (StructuralMechanicsAnalysis.SolveSolutionStep - see GUIDE.md gotcha
# #4), so trusting master's source for exact variable names risks being wrong
# for THIS installed version. Safer to ask the actual installed law directly.
#
# How this works: every Kratos constitutive law implements Check(properties,
# geometry, process_info), which is normally called once automatically at the
# start of a real analysis (inside Initialize()) to validate that every
# Variable the law needs is present on the Properties object - and raises a
# KRATOS_ERROR naming the specific missing variable if not. We call Check()
# directly, by hand, on a deliberately near-empty Properties object, and just
# print whatever error comes back. That error message names ONE missing
# variable (the first one Check() happens to test) - add that variable to the
# `known_good` dict below with a plausible placeholder value, rerun, and the
# next missing variable will be reported. Repeat until Check() passes cleanly;
# at that point `known_good` is your complete required-Variables list.
#
# Run with: bash run.sh check_wrinkling_orthotropic_vars.py (from kratos_docker/)
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma

try:
    import KratosMultiphysics.ConstitutiveLawsApplication as cla
except Exception as e:
    cla = None
    print("ConstitutiveLawsApplication import failed:", e)

# Minimal ModelPart + a single 3-node triangle geometry, matching what
# MembraneElement3D3N actually uses (3 nodes in 3D space, not a flat 2D
# geometry) - some laws' Check() inspects geometry dimensionality/node count,
# so this needs to look like the real thing.
model = KratosMultiphysics.Model()
mp = model.CreateModelPart("Test")
mp.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3

n1 = mp.CreateNewNode(1, 0.0, 0.0, 0.0)
n2 = mp.CreateNewNode(2, 1.0, 0.0, 0.0)
n3 = mp.CreateNewNode(3, 0.0, 1.0, 0.0)
geom = KratosMultiphysics.Triangle3D3(n1, n2, n3)


def probe_law(law_name, known_good, initialize_first=False):
    """
    known_good: dict of {KratosMultiphysics.VARIABLE: value} to pre-populate
    on the Properties before calling Check(). Start with {} (or just
    THICKNESS/DENSITY) and grow it one variable at a time based on each
    successive error message.

    initialize_first: some laws (WrinklingLinear2DLaw turned out to be one -
    it internally wraps/owns another constitutive law instance) need
    InitializeMaterial() called once before Check() will even run its
    Properties validation, otherwise it fails with "... is not initialized"
    instead of naming a missing Variable. We pass a dummy uniform shape-
    function vector (1/3, 1/3, 1/3) - fine for this purpose, since we only
    care about which Variables get read, not the numerical result.
    """
    print(f"\n=== {law_name} ===")
    print(f"Properties pre-filled with: {[k.Name() for k in known_good]}")
    law = getattr(cla, law_name)()
    props = KratosMultiphysics.Properties(1)
    for var, val in known_good.items():
        props.SetValue(var, val)
    if initialize_first:
        N = KratosMultiphysics.Vector(3)
        N[0] = 1.0 / 3.0
        N[1] = 1.0 / 3.0
        N[2] = 1.0 / 3.0
        try:
            law.InitializeMaterial(props, geom, N)
        except Exception as e:
            print("InitializeMaterial() FAILED:")
            print(e)
            return
    try:
        law.Check(props, geom, mp.ProcessInfo)
        print("Check() PASSED - known_good above is the complete required set "
              "(for this Kratos build).")
    except Exception as e:
        print("Check() FAILED (expected, until known_good is complete):")
        print(e)


# ----------------------------------------------------------------------
# Start both probes with just the two things every law obviously needs.
# Extend `known_good_*` below (uncomment/add lines) based on each run's
# error message, and rerun this script - repeat until "Check() PASSED".
# ----------------------------------------------------------------------
known_good_ortho = {
    KratosMultiphysics.THICKNESS: 0.001,
    KratosMultiphysics.DENSITY: 1000.0,
    # First error named YOUNG_MODULUS_X specifically (not the plain isotropic
    # YOUNG_MODULUS) - confirms this law wants separate warp/weft stiffnesses.
    # Filling in the other 3 orthotropic-elasticity values we'd expect it to
    # need next, guessing standard Kratos naming - if any of these guesses are
    # wrong, Check() will simply name the next missing one and we correct it.
    KratosMultiphysics.YOUNG_MODULUS_X: 600000000.0,
    KratosMultiphysics.YOUNG_MODULUS_Y: 600000000.0,
    KratosMultiphysics.SHEAR_MODULUS_XY: 214285714.0,   # placeholder, isotropic G = E/(2(1+nu))
    KratosMultiphysics.POISSON_RATIO_XY: 0.4,
}

known_good_wrinkling = {
    KratosMultiphysics.THICKNESS: 0.001,
    KratosMultiphysics.DENSITY: 1000.0,
    KratosMultiphysics.YOUNG_MODULUS: 600000000.0,
    KratosMultiphysics.POISSON_RATIO: 0.4,
}

if cla is not None:
    probe_law("LinearElasticOrthotropic2DLaw", known_good_ortho)

    # ------------------------------------------------------------------
    # WrinklingLinear2DLaw is a WRAPPER: it doesn't compute stress itself,
    # it wraps an underlying ("base") elastic law and applies the wrinkling
    # (tension-field) correction on top of whatever that base law returns.
    # "Exactly one base claw must be given (0 claws are defined for baseclaw
    # 1)" means the base law has to be attached via Properties.SubProperties
    # - the same mechanism Kratos uses for composite/layered shell plies.
    # This block builds that nested structure by hand: a sub-Properties
    # object holding the SAME LinearElasticPlaneStress2DLaw you're using
    # today (so this test isolates just the wrinkling correction, not also
    # switching to orthotropic at the same time), attached to the main
    # Properties via AddSubProperties().
    # ------------------------------------------------------------------
    base_props = KratosMultiphysics.Properties(2)
    base_props.SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, sma.LinearElasticPlaneStress2DLaw())
    for var, val in known_good_wrinkling.items():
        base_props.SetValue(var, val)

    main_props = KratosMultiphysics.Properties(1)
    for var, val in known_good_wrinkling.items():
        main_props.SetValue(var, val)
    main_props.AddSubProperties(base_props)

    print(f"\n=== WrinklingLinear2DLaw (with base law attached via sub-Properties) ===")
    law = cla.WrinklingLinear2DLaw()
    N = KratosMultiphysics.Vector(3)
    N[0] = N[1] = N[2] = 1.0 / 3.0
    try:
        law.InitializeMaterial(main_props, geom, N)
        print("InitializeMaterial() passed.")
        law.Check(main_props, geom, mp.ProcessInfo)
        print("Check() PASSED - this nested-Properties structure is what "
              "StructuralMaterials.json needs to replicate (via sub_properties).")
    except Exception as e:
        print("FAILED:")
        print(e)
