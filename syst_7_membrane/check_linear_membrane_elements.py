# One-off diagnostic: "is there a genuinely small-displacement/linear membrane
# (or shell) element registered in this Kratos build, as an alternative to
# MembraneElement3D3N (which is inherently a large-displacement, Green-Lagrange
# formulation with no small-displacement variant, as far as we've assumed so
# far)?" Rather than trust memory/GitHub master (already burned once by a
# version mismatch - see GUIDE.md gotcha #4), list every registered Element
# name matching relevant keywords and actually look at what exists in THIS
# installed build.
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma

try:
    import KratosMultiphysics.ConstitutiveLawsApplication as cla
except Exception as e:
    cla = None

keywords = ["membrane", "shell", "small_displacement", "smalldisplacement"]


def matches(names):
    return sorted(n for n in names if any(k in n.lower() for k in keywords))


print("=== StructuralMechanicsApplication matches (dir search) ===")
print(matches(dir(sma)))

# dir() on the module only lists Python-exposed CLASSES (constitutive laws,
# utilities, processes) - Elements are registered in the C++ kernel and
# normally only created by NAME STRING via ModelPart.CreateNewElement(...),
# not instantiated directly from Python the way LinearElasticPlaneStress2DLaw
# was - which is exactly why no Shell/Membrane ELEMENT classes showed up in
# the dir() search above (only their associated Variables + a couple of
# Process helper classes did). KratosComponents isn't exposed as a bare
# attribute in this build either (see error below if you already hit it), so
# the reliable way to check "does element X exist" is to just try creating
# one and see whether Kratos complains that the name isn't registered.
print("\n=== Trying to create candidate elements by name ===")
model2 = KratosMultiphysics.Model()
mp2 = model2.CreateModelPart("ElemTest")
mp2.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3
n1 = mp2.CreateNewNode(1, 0.0, 0.0, 0.0)
n2 = mp2.CreateNewNode(2, 1.0, 0.0, 0.0)
n3 = mp2.CreateNewNode(3, 0.0, 1.0, 0.0)
n4 = mp2.CreateNewNode(4, 1.0, 1.0, 0.0)
props2 = mp2.GetProperties()[1]
props2.SetValue(KratosMultiphysics.THICKNESS, 0.001)

candidates_3n = [
    "MembraneElement3D3N",              # known-good control case - should always succeed
    "ShellThinElement3D3N",
    "ShellThickElement3D3N",
    "ShellThinElementCorotational3D3N",
    "ShellThickElementCorotational3D3N",
    "SmallDisplacementElement3D3N",
    "TotalLagrangianElement3D3N",
]
candidates_4n = [
    "MembraneElement3D4N",
    "ShellThinElement3D4N",
    "ShellThickElement3D4N",
]

eid = 1
for name in candidates_3n:
    try:
        mp2.CreateNewElement(name, eid, [1, 2, 3], props2)
        print(f"  {name:35s} EXISTS (created OK)")
    except Exception as e:
        print(f"  {name:35s} not available: {e}".splitlines()[0])
    eid += 1

for name in candidates_4n:
    try:
        mp2.CreateNewElement(name, eid, [1, 2, 3, 4], props2)
        print(f"  {name:35s} EXISTS (created OK)")
    except Exception as e:
        print(f"  {name:35s} not available: {e}".splitlines()[0])
    eid += 1
