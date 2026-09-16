# One-off diagnostic for the DEFERRED material refinement (still isotropic
# for now, see GUIDE.md section 5's closing note): confirms that
# LinearElasticOrthotropic2DLaw (the paper's actual Munsch-Reinhardt-style
# material, with an independent shear modulus) and WrinklingLinear2DLaw (their
# tension-field wrinkle correction) both exist in this Kratos build, even
# though GiD's GUI only exposes the isotropic "Linear Elastic Plane Stress"
# option. To use them, you'd assign CONSTITUTIVE_LAW on the Membrane
# properties directly in Python rather than through StructuralMaterials.json's
# simple "name" string (GiD's interface doesn't have a form for the extra
# orthotropic parameters). Not yet wired in - Phase 2 showed the isotropic
# approximation already tracks the paper within ~3%, so this was deprioritized
# in favor of getting the full pipeline (form-finding -> load -> FORM) working
# end to end first.
import KratosMultiphysics
import KratosMultiphysics.StructuralMechanicsApplication as sma

try:
    import KratosMultiphysics.ConstitutiveLawsApplication as cla
except Exception as e:
    cla = None
    print("ConstitutiveLawsApplication import failed:", e)

keywords = ["ortho", "wrinkl", "membrane", "munsch", "reinhardt"]


def matches(names):
    return sorted(n for n in names if any(k in n.lower() for k in keywords))


print("=== StructuralMechanicsApplication matches ===")
print(matches(dir(sma)))

if cla is not None:
    print("=== ConstitutiveLawsApplication matches ===")
    print(matches(dir(cla)))
