# One-off diagnostic that resolved the projection_settings.variable_name
# question for Stage 1's ProjectParameters.json (GUIDE.md gotcha #2). Lists
# every registered Kratos variable whose name contains "axis"/"prestress"/
# "orientation", so the ones with _X/_Y/_Z subcomponents (a tell for true
# Array3-typed variables, which is what ProjectVectorOnSurfaceUtility's
# variable_name setting requires) can be told apart from similarly-named but
# Vector-typed variables like PRESTRESS_AXIS_1_GLOBAL, which look like they'd
# fit but fail this specific utility's type check. Answer found: LOCAL_AXIS_1.
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma

keywords = ["axis", "prestress", "orientation"]

def matches(names):
    return sorted(n for n in names if any(k in n.lower() for k in keywords))

print("=== KratosMultiphysics core matches ===")
print(matches(dir(KratosMultiphysics)))

print("=== StructuralMechanicsApplication matches ===")
print(matches(dir(sma)))
