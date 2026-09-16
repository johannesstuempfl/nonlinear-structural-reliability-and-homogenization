# One-off diagnostic: does the Updated Reference Strategy (Stage 1's
# form-finding algorithm) already leave the model's reference configuration
# (X0/Y0/Z0) equal to the found equilibrium shape by the time it converges?
# Finding: yes - "MESH MOVED" each iteration IS the reference configuration
# being continuously updated, so by convergence X0==X and DISPLACEMENT~=0
# already, with no extra step needed. See GUIDE.md gotcha #6 for why this
# script inspects state BEFORE calling Finalize() rather than after - the
# formfinding solver's Finalize() (which writes formfinding_result_model.mdpa)
# disturbs the model part's variable bookkeeping in a way that breaks
# GetSolutionStepValue() calls made afterwards.
import KratosMultiphysics
from KratosMultiphysics.StructuralMechanicsApplication.structural_mechanics_analysis import StructuralMechanicsAnalysis

with open("ProjectParameters.json", 'r') as f:
    parameters = KratosMultiphysics.Parameters(f.read())

model = KratosMultiphysics.Model()
analysis = StructuralMechanicsAnalysis(model, parameters)

# Manually replicate Run() but inspect BEFORE Finalize(), since Finalize()
# triggers FormfindingMechanicalSolver's WriteFormFoundMdpa side effect.
analysis.Initialize()
analysis.RunSolutionLoop()

mp = model.GetModelPart("Structure")

print("=== Reference vs current configuration (first 5 nodes), pre-Finalize ===")
for n in list(mp.Nodes)[:5]:
    d = n.GetSolutionStepValue(KratosMultiphysics.DISPLACEMENT)
    print(f"node {n.Id}: X0=({n.X0:.5f},{n.Y0:.5f},{n.Z0:.5f})  "
          f"X=({n.X:.5f},{n.Y:.5f},{n.Z:.5f})  DISPLACEMENT={tuple(round(v,6) for v in d)}")

max_gap = max(((n.X-n.X0)**2+(n.Y-n.Y0)**2+(n.Z-n.Z0)**2)**0.5 for n in mp.Nodes)
print(f"\nmax |X - X0| over all nodes: {max_gap:.6f} m")

analysis.Finalize()
print("\nFinalize() done (this triggers WriteFormFoundMdpa - check for a new .mdpa file on disk)")
