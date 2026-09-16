# One-off unit test, built directly with the low-level Kratos API (no mdpa
# file, no ProjectParameters.json) rather than a full AnalysisStage, because
# the question is deliberately narrow: build a flat 1x1 m membrane patch,
# clamp all 4 corners so it CANNOT move (zero elastic strain by construction),
# apply ONLY the prestress property (no external load), and read the reaction
# forces. Since strain=0, the only stress present is whatever PRESTRESS_VECTOR
# contributes - so the reaction force directly reveals how Kratos interprets
# that property's units.
#
# RESULT: reaction = 1.5 N per node * 2 nodes = 3.0 N total on a 1m edge, for
# PRESTRESS_VECTOR=[3000,3000,0]. That's the "true stress in Pa, x THICKNESS
# to get a force resultant" convention (3000 Pa * 0.001 m = 3 N/m), NOT the
# "already a force resultant in N/m" convention the paper uses directly. See
# GUIDE.md gotcha #1 for the full story and the fix (multiply by 1000/thickness
# before entering values from the paper into StructuralMaterials.json).
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma
import KratosMultiphysics.ConstitutiveLawsApplication  # noqa: F401 (registers laws)

model = KratosMultiphysics.Model()
mp = model.CreateModelPart("Structure")
mp.SetBufferSize(2)
mp.AddNodalSolutionStepVariable(KratosMultiphysics.DISPLACEMENT)
mp.AddNodalSolutionStepVariable(KratosMultiphysics.REACTION)
mp.AddNodalSolutionStepVariable(KratosMultiphysics.VOLUME_ACCELERATION)

# 1m x 1m flat square patch, 2 triangles
n1 = mp.CreateNewNode(1, 0.0, 0.0, 0.0)
n2 = mp.CreateNewNode(2, 1.0, 0.0, 0.0)
n3 = mp.CreateNewNode(3, 1.0, 1.0, 0.0)
n4 = mp.CreateNewNode(4, 0.0, 1.0, 0.0)

for n in [n1, n2, n3, n4]:
    n.AddDof(KratosMultiphysics.DISPLACEMENT_X, KratosMultiphysics.REACTION_X)
    n.AddDof(KratosMultiphysics.DISPLACEMENT_Y, KratosMultiphysics.REACTION_Y)
    n.AddDof(KratosMultiphysics.DISPLACEMENT_Z, KratosMultiphysics.REACTION_Z)
    n.Fix(KratosMultiphysics.DISPLACEMENT_X)
    n.Fix(KratosMultiphysics.DISPLACEMENT_Y)
    n.Fix(KratosMultiphysics.DISPLACEMENT_Z)

props = mp.GetProperties()[1]
props.SetValue(KratosMultiphysics.THICKNESS, 0.001)
props.SetValue(KratosMultiphysics.DENSITY, 1000.0)
props.SetValue(KratosMultiphysics.YOUNG_MODULUS, 600000000.0)
props.SetValue(KratosMultiphysics.POISSON_RATIO, 0.4)
props.SetValue(sma.PRESTRESS_VECTOR, KratosMultiphysics.Vector([3000.0, 3000.0, 0.0]))
props.SetValue(sma.PRESTRESS_AXIS_1_GLOBAL, KratosMultiphysics.Vector([1.0, 0.0, 0.0]))
cl = KratosMultiphysics.ConstitutiveLawsApplication if False else None
from KratosMultiphysics import StructuralMechanicsApplication as _sma
props.SetValue(KratosMultiphysics.CONSTITUTIVE_LAW, sma.LinearElasticPlaneStress2DLaw())

e1 = mp.CreateNewElement("MembraneElement3D3N", 1, [1, 2, 3], props)
e2 = mp.CreateNewElement("MembraneElement3D3N", 2, [1, 3, 4], props)

mp.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3

scheme = KratosMultiphysics.ResidualBasedIncrementalUpdateStaticScheme()
lin_solver = KratosMultiphysics.LinearSolverFactory().Create(KratosMultiphysics.Parameters('{"solver_type":"skyline_lu_factorization"}'))
builder_and_solver = KratosMultiphysics.ResidualBasedBlockBuilderAndSolver(lin_solver)
conv_criteria = KratosMultiphysics.ResidualCriteria(1e-6, 1e-9)
strategy = KratosMultiphysics.ResidualBasedNewtonRaphsonStrategy(
    mp, scheme, conv_criteria, builder_and_solver, 30, True, False, True)
strategy.SetEchoLevel(1)
strategy.Check()
strategy.Solve()

print("=== Reaction forces at the 4 clamped corners of a flat 1x1 m patch, prestress-only ===")
total = [0.0, 0.0, 0.0]
for n in [n1, n2, n3, n4]:
    r = n.GetSolutionStepValue(KratosMultiphysics.REACTION)
    print(f"node {n.Id}: Rx={r[0]:.4f}, Ry={r[1]:.4f}, Rz={r[2]:.4f}")
    total[0] += r[0]; total[1] += r[1]; total[2] += r[2]
print(f"sum: Rx={total[0]:.4f}, Ry={total[1]:.4f}, Rz={total[2]:.4f}")
print("\nIf PRESTRESS_VECTOR=3000 is a force resultant (N/m), the two nodes on one")
print("edge should together resist ~3000 N pulling outward along that edge.")
print("If it's being treated as true stress (Pa), that number will be ~1000x smaller (~3 N).")
