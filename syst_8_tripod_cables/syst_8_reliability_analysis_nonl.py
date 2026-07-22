import numpy as np
from syst_8_measures_of_nonlinearity import y0, kappa_1, kappa_2, kappa_12, r1, r2
from syst_8_model_functions import t_S_cablenet_linear, t_S_cablenet_nonlinear

from ERA_Distribution_Classes_Python.Classes.ERADist import ERADist
from ERA_Distribution_Classes_Python.Classes.ERANataf import ERANataf
from ERA_Distribution_Classes_Python.Classes.FORM_HLRF import FORM_HLRF
from ERA_Distribution_Classes_Python.Classes.FORM_fmincon import FORM_fmincon

# ---------------------------------------------------------------------------------------
# Characteristic Values 
e = 20 # arbitrary load distribution area in m2 (chosen for calibration of design parameter p)

# characteristic tensile strength in MPa 
#f_u = 1601.7305471 # deprecated
f_u = 1711.4064623286197 # adjusted to eta = 100%

s_k = 1.1  # snow kN/m2 (in negative z-direction)
q_b = 0.65 # wind pressure kN/m2 (in negative y-direction)
w_k = q_b  # wind load kN/m2 without c_pe,10. Choice of loads more arbitrary than syst_4

# Characteristic Loads
l_1k = s_k * e  # conversion from kN to N -> * 1000
l_2k = w_k * e  # conversion from kN to N -> * 1000

# ---------------------------------------------------------------------------------------
# Random variables

# Snow time-invariant part $\Theta_{L_{1}}$ (JRC Report)
mu_Theta_L1 = 0.81
cov_Theta_L1 = 0.26
sig_Theta_L1 = mu_Theta_L1 * cov_Theta_L1
Theta_L1_dist = ERADist('lognormal', 'MOM', [mu_Theta_L1, sig_Theta_L1])


# Snow load on ground $L_{1}$ in kN/m2 (JRC Report)
mu_L1 = 1.0
cov_L1 = 0.2
sig_L1 = mu_L1 * cov_L1
L1_dist = ERADist('gumbel', 'MOM', [mu_L1, sig_L1])


# Wind time-invariant part $\Theta_{L_{2}}$ (JRC Report)
mu_Theta_L2 = 0.97
cov_Theta_L2 = 0.26
sig_Theta_L2 = mu_Theta_L2 * cov_Theta_L2
Theta_L2_dist = ERADist('lognormal', 'MOM', [mu_Theta_L2, sig_Theta_L2])


# Wind velocity pressure $L_{2}$ in kN/m2 (JRC Report)
mu_L2 = 1.0
cov_L2 = 0.14
sig_L2 = mu_L2 * cov_L2
L2_dist = ERADist('gumbel', 'MOM', [mu_L2, sig_L2])


# Structural Response Model Uncertainty $\Theta_{S}$: axial force in frames (JCSS Part 3, Table 3.9.1)
mu_Theta_S = 1.0
cov_Theta_S = 0.05
sig_Theta_S = mu_Theta_S * cov_Theta_S
Theta_S_dist = ERADist('lognormal', 'MOM', [mu_Theta_S, sig_Theta_S])


# Resistance Model Uncertainty $\Theta_{M}$  for Steel (Köhler et al. Calibration of ...)
mu_Theta_M = 1.0
cov_Theta_M = 0.05
sig_Theta_M = mu_Theta_M * cov_Theta_M
Theta_M_dist = ERADist('lognormal', 'MOM', [mu_Theta_M, sig_Theta_M])

# Material strength: steel yielding strength $M$ in MPa (JRC Report)
mu_M = 1.0
cov_M = 0.05
sig_M = mu_M * cov_M
M_dist = ERADist('lognormal', 'MOM', [mu_M, sig_M])


# ---------------------------------------------------------------------------------------
# Shifting / Scaling Random Variables 
percentile_L1 = L1_dist.icdf(0.98)
print(f"Snow 98% Percentile: {percentile_L1}")

snow_shift = s_k / percentile_L1 # ratio of target to current percentile, by which mean and std get multiplied

mu_L1_shifted = mu_L1 * snow_shift
sig_L1_shifted = sig_L1 * snow_shift
L1_shifted = ERADist('gumbel','MOM',[mu_L1_shifted, sig_L1_shifted])

print(f"""Snow Load on Ground gets shifted by {snow_shift}""")
print(f"""Old mean: {mu_L1}; New mean: {mu_L1_shifted}""")
print(f"""Old std: {sig_L1}; New std: {sig_L1_shifted}""")
print(f"""Old 98th percentile: {L1.icdf(.98)}; New 98th percentile: {L1_shifted.icdf(.98)}""")
print(f"""Old COV: {L1.std()/L1.mean()}; New COV: {L1_shifted.std()/L1_shifted.mean()}""")



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
e_d_opt1 = t_S_cablenet_nonlinear(L_snow=l_1d, L_wind=l_2d) # kN/m

argument_1 = gamma_F1 * t_S_cablenet_nonlinear(L_snow=l_1k, L_wind=(gamma_F2/gamma_F1) * l_2k)
argument_2 = gamma_F2 * t_S_cablenet_nonlinear(L_snow=(gamma_F1/gamma_F2) * l_1k, L_wind=l_2k)
e_d_opt2 = max(argument_1, argument_2) # kN/m


p_opt1 = gamma_M * e_d_opt1 / m_k
p_opt2 = gamma_M * e_d_opt2 / m_k
print(f"p_opt1 = {p_opt1:.5f}")
print(f"p_opt2 = {p_opt2:.5f}")


# ---------------------------------------------------------------------------------------
# Limit State Functions g(X) for option 1 and 2 
def g_opt1(x):
    x = np.asarray(x, dtype=float)
    return p_opt1 * x[..., 0] - t_S_cablenet_nonlinear(L_snow= x[..., 1], L_wind= x[..., 2])

def g_opt2(x):
    x = np.asarray(x, dtype=float)
    return p_opt2 * x[..., 0] - t_S_cablenet_nonlinear(L_snow= x[..., 1], L_wind= x[..., 2])

# ---------------------------------------------------------------------------------------
# FORM via HLRF  (fmincon inserted extreme big load values -> Kratos crashed)
print("\n=== FORM (HLRF) - Design option (a) ===")
u_star_1, x_star_1, beta_1, Pf_1, _, _ = FORM_HLRF(
    g=g_opt1, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

print("\n=== FORM (HLRF) - Design option (b) ===")
u_star_2, x_star_2, beta_2, Pf_2, _, _ = FORM_HLRF(
    g=g_opt2, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

print("\n\n=== SUMMARY ===")
print("\nDesign option (1)")
print(f"beta = {beta_1:.3f}") # paper: 4.96
print(f"x_star_1 = {x_star_1}")
print(f"alpha_1 = {u_star_1/beta_1}")

print("\n\nDesign option (2)")
print(f"beta = {beta_2:.3f}") # paper: 5.56
print(f"x_star_2 = {x_star_2}")
print(f"alpha_2 = {u_star_2/beta_2}")

# ---------------------------------------------------------------------------------------
# Safety Homogenization with additional PSF gamma_new


