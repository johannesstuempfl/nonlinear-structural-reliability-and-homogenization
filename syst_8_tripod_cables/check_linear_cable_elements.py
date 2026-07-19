# One-off diagnostic: does this Kratos build have a genuinely small-
# displacement, TENSION-ONLY cable element (as opposed to CableElement3D2N,
# which is large-displacement)? We already confirmed TrussLinearElement3D2N
# exists (see syst_7_membrane/check_linear_membrane_elements.py) - but that's
# a general truss (takes compression too), not a cable. Rather than assume a
# linear cable variant does or doesn't exist, just try creating one.
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma

model = KratosMultiphysics.Model()
mp = model.CreateModelPart("ElemTest")
mp.ProcessInfo[KratosMultiphysics.DOMAIN_SIZE] = 3
mp.CreateNewNode(1, 0.0, 0.0, 0.0)
mp.CreateNewNode(2, 1.0, 0.0, 0.0)
props = mp.GetProperties()[1]
props.SetValue(sma.CROSS_AREA, 0.0001)

candidates = [
    "CableElement3D2N",              # known-good control - should always succeed
    "TrussLinearElement3D2N",        # known-good control - already confirmed to exist
    "CableLinearElement3D2N",
    "LinearCableElement3D2N",
    "CableElement3D2NLinear",
    "SmallDisplacementCableElement3D2N",
]

for i, name in enumerate(candidates, start=1):
    try:
        mp.CreateNewElement(name, i, [1, 2], props)
        print(f"  {name:35s} EXISTS (created OK)")
    except Exception as e:
        print(f"  {name:35s} not available: {e}".splitlines()[0])
