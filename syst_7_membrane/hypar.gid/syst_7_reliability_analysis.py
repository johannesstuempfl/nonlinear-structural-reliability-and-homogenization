import numpy as np

from hypar_model_functions import t_S_kratos_linear, t_S_kratos_nonlinear

from ERA_Distribution_Classes_Python.Classes.ERADist import ERADist
from ERA_Distribution_Classes_Python.Classes.ERANataf import ERANataf
from ERA_Distribution_Classes_Python.Classes.FORM_HLRF import FORM_HLRF
from ERA_Distribution_Classes_Python.Classes.FORM_fmincon import FORM_fmincon

def y0(l_1k, l_2k, t_S):
    return t_S(0,0) / t_S(l_1k, l_2k)

def kappa_1(l_1k, l_1d, t_S):
    numerator = (t_S(l_1d, 0) - t_S(l_1k, 0)) * l_1k
    denominator = (t_S(l_1k, 0) - t_S(0, 0)) * (l_1d-l_1k)
    return numerator / denominator


def kappa_2(l_2k, l_2d, t_S):
    numerator = (t_S(0, l_2d) - t_S(0, l_2k)) * l_2k
    denominator = (t_S(0, l_2k) - t_S(0, 0)) * (l_2d-l_2k)
    return numerator / denominator

def kappa_12(l_1k, l_1d, l_2k, l_2d, t_S):
    numerator = (t_S(l_1d, l_2d) - t_S(l_1k, l_2k)) * np.sqrt(l_1k**2 + l_2k**2)
    denominator = (t_S(l_1k, l_2k) - t_S(0, 0)) * np.sqrt((l_1d-l_1k)**2 + (l_2d-l_2k)**2)
    return numerator / denominator

def r1(l_1k, l_2k, t_S):
    numerator = t_S(l_1k, 0) - t_S(0, 0)
    denominator = t_S(l_1k, l_2k) - t_S(0, 0)
    return numerator / denominator

def r2(l_1k, l_2k, t_S):
    numerator = t_S(0, l_2k) - t_S(0, 0)
    denominator = t_S(l_1k, l_2k) - t_S(0, 0)
    return numerator / denominator


# ---------------------------------------------------------------------------------------
# Random variables

# Snow Load kN/m^2
mu_L1, cov_L1 = 0.34, 0.3
L1_dist = ERADist('gumbel', 'MOM', [mu_L1, mu_L1 * cov_L1])

# Wind Load kN/m^2 -> REPLACE WITH ACTUAL DISTRIBUTION LATER; RIGHT NOW ONLY DUMMY DATA
mu_L2, cov_L2 = 0.5, 0.3
L2_dist = ERADist('gumbel', 'MOM', [mu_L2, mu_L2 * cov_L2])

# membrane tensile strength kN/m
mu_M, cov_M = 1.0, 0.1
M_dist = ERADist('lognormal', 'MOM', [mu_M, mu_M * cov_M])    # membrane tensile strength

# ---------------------------------------------------------------------------------------
# Construction of the Nataf Distribution
marginal_dist = [M_dist, L1_dist, L2_dist]
nataf = ERANataf(M=marginal_dist, Correlation=np.eye(len(marginal_dist)))

# ---------------------------------------------------------------------------------------
# Partial Safety Factors
gamma_F1 = 1.5  # snow
gamma_F2 = 1.5  # wind
gamma_M = 1.4   # resistance side (from Technical Specification, see paper Fußeder 2021)

# ---------------------------------------------------------------------------------------
# Characteristic values: 98th percentile of the loads, 5th percentile of the resistance
l_1k = L1_dist.icdf(0.98)
l_2k = L2_dist.icdf(0.98)
m_k = M_dist.icdf(0.05)
print(f"l_1k = {l_1k:.4f} kN/m^2")
print(f"l_2k = {l_2k:.4f} kN/m^2")
print(f"m_k = {m_k:.4f} kN/m^2")

# ---------------------------------------------------------------------------------------
# Design Values
l_1d = l_1k * gamma_F1
l_2d = l_2k * gamma_F2
print(f"l_1d = {l_1d:.4f} kN/m^2")
print(f"l_2d = {l_2d:.4f} kN/m^2")

# ---------------------------------------------------------------------------------------
# # Measures of Nonlinearity
# y0 = y0(l_1k=l_1k, l_2k=l_2k, t_S=t_S_kratos_nonlinear)
# k1 = kappa_1(l_1k=l_1k, l_1d=l_1d,t_S=t_S_kratos_nonlinear)
# k2 = kappa_2(l_2k=l_2k, l_2d=l_2d,t_S=t_S_kratos_nonlinear)
# k12 = kappa_12(l_1k=l_1k, l_1d=l_1d, l_2k=l_2k, l_2d=l_2d, t_S=t_S_kratos_nonlinear)

# print(f"y0: {y0}")
# print(f"kappa1: {k1}")
# print(f"kappa2: {k2}")
# print(f"kappa12: {k12}")

# ---------------------------------------------------------------------------------------
# Design parameters p for option 1 and 2 
e_d_opt1 = t_S_kratos_nonlinear(L_snow=l_1d, L_wind=l_2d) # kN/m

argument_1 = gamma_F1 * t_S_kratos_nonlinear(L_snow=l_1k, L_wind=(gamma_F2/gamma_F1) * l_2k)
argument_2 = gamma_F2 * t_S_kratos_nonlinear(L_snow=(gamma_F1/gamma_F2) * l_1k, L_wind=l_2k)
e_d_opt2 = max(argument_1, argument_2) # kN/m


p_opt1 = gamma_M * e_d_opt1 / m_k
p_opt2 = gamma_M * e_d_opt2 / m_k
print(f"p_opt1 = {p_opt1:.5f}")
print(f"p_opt2 = {p_opt2:.5f}")


# ---------------------------------------------------------------------------------------
# Limit State Functions g(X) for option 1 and 2 
def g_opt1(x):
    x = np.asarray(x, dtype=float)
    return p_opt1 * x[..., 0] - t_S_kratos_nonlinear(L_snow= x[..., 1], L_wind= x[..., 2])

def g_opt2(x):
    x = np.asarray(x, dtype=float)
    return p_opt2 * x[..., 0] - t_S_kratos_nonlinear(L_snow= x[..., 1], L_wind= x[..., 2])

# ---------------------------------------------------------------------------------------
# FORM via HLRF  (fmincon inserted extreme big load values -> Kratos crashed)
print("\n=== FORM (HLRF) - Design option (a) ===")
u_star_1, x_star_1, beta_1, Pf_1, _, _ = FORM_HLRF(
    g=g_opt1, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

# print("\n=== FORM (HLRF) - Design option (b) ===")
# u_star_2, x_star_2, beta_2, Pf_2, _, _ = FORM_HLRF(
#     g=g_opt2, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

print("\n\n=== SUMMARY ===")
print("\nDesign option (1)")
print(f"beta = {beta_1:.3f}") # paper: 4.96
print(f"x_star_1 = {x_star_1}")
print(f"alpha_1 = {u_star_1/beta_1}")

# print("\n\nDesign option (2)")
# print(f"beta = {beta_2:.3f}") # paper: 5.56
# print(f"x_star_2 = {x_star_2}")
# print(f"alpha_2 = {u_star_2/beta_2}")

# ---------------------------------------------------------------------------------------
# Safety Homogenization with additional PSF gamma_new


