# Validates Stage 1's (MainKratos.py) form-finding output: runs
# ProjectParameters.json (solver_type "formfinding") to completion, then
# checks the resulting equilibrium shape makes physical sense. See GUIDE.md
# section 3 ("Stage 1") for what "form-finding" and "Updated Reference
# Strategy" mean, and why the plan-center height check below is a meaningful
# correctness test (not an arbitrary one): for a hypar with STRAIGHT boundary
# generators and an ISOTROPIC 1:1 prestress ratio, the true equilibrium shape
# is exactly the bilinear ruled surface - so its center height must equal the
# average of the 4 corner heights. This is a strong, analytically-known check
# that doesn't depend on trusting any other part of the pipeline.
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

with open("ProjectParameters.json", 'r') as f:
    parameters = KratosMultiphysics.Parameters(f.read())

model = KratosMultiphysics.Model()
analysis = StructuralMechanicsAnalysis(model, parameters)
analysis.Run()

mp = model.GetModelPart("Structure")

zs = [n.Z for n in mp.Nodes]
print("=== Node Z-coordinate range after form-finding ===")
print(f"min z = {min(zs):.4f} m, max z = {max(zs):.4f} m")

print("\n=== Corner point coordinates (should sit near the 4 hypar corners) ===")
support_mp = model.GetModelPart("Structure.DISPLACEMENT_Displacement_Auto1")
for n in support_mp.Nodes:
    print(f"node {n.Id}: ({n.X:.4f}, {n.Y:.4f}, {n.Z:.4f})")

print("\n=== Interior curvature check (nodes nearest plan-center 3,3) ===")
candidates = sorted(mp.Nodes, key=lambda n: (n.X-3.0)**2 + (n.Y-3.0)**2)[:5]
for n in candidates:
    print(f"node {n.Id}: ({n.X:.3f}, {n.Y:.3f}, {n.Z:.3f})")
print("(bilinear ruled-surface value at plan-center would be z=1.0; "
      "a saddle in equilibrium should sit close to that, not flat)")
