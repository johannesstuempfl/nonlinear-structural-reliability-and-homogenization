import numpy as np

from hypar_model_functions import t_S_hypar_linear, t_S_hypar_nonlinear

from ERA_Distribution_Classes_Python.Classes.ERADist import ERADist
from ERA_Distribution_Classes_Python.Classes.ERANataf import ERANataf
from ERA_Distribution_Classes_Python.Classes.FORM_HLRF import FORM_HLRF
from ERA_Distribution_Classes_Python.Classes.FORM_fmincon import FORM_fmincon

# Vectorized Version of the Structural response function (Better for array handling later)
t_S_nonl_vectorized = np.vectorize(t_S_hypar_nonlinear, otypes=[float])


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

# Snow time-invariant part $\Theta_{L_{1}}$ (JRC Report)
mu_Theta_L1 = 0.81
cov_Theta_L1 = 0.26
sig_Theta_L1 = mu_Theta_L1 * cov_Theta_L1
Theta_L1_dist = ERADist('lognormal', 'MOM', [mu_Theta_L1, sig_Theta_L1])


# Snow Load in kN/m^2 from paper with Martin -> i don't know where how it is derived!!
mu_L1 = 0.34
cov_L1 = 0.3
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


# Structural Response Model Uncertainty $\Theta_{S}$: stresses in 2D solids (JCSS Part 3, Table 3.9.1)
mu_Theta_S = 0.0
cov_Theta_S = 0.05
# since mu = 0, here: COV = sigma
Theta_S_dist = ERADist('normal', 'MOM', [mu_Theta_S, cov_Theta_S])


# Resistance Model Uncertainty $\Theta_{M}$ find a source !!
mu_Theta_M = 1.0
cov_Theta_M = 0.05
sig_Theta_M = mu_Theta_M * cov_Theta_M
Theta_M_dist = ERADist('lognormal', 'MOM', [mu_Theta_M, sig_Theta_M])


# membrane tensile strength in kN/m from paper with Martin -> i don't know where how it is derived!!
mu_M = 1.0
cov_M = 0.1
sig_M = mu_M * cov_M
M_dist = ERADist('lognormal', 'MOM', [mu_M, sig_M]) 


# ---------------------------------------------------------------------------------------
# Partial Safety Factors
gamma_F1 = 1.5  # snow
gamma_F2 = 1.5  # wind
gamma_M = 1.4   # resistance side (from Technical Specification, see paper Fußeder 2021)

# ---------------------------------------------------------------------------------------
# Characteristic values derived from Random Variables for further calculation
print(f"\n")
print("================================")
print("Characteristic values")
print("================================")
l_1k = L1_dist.icdf(0.98)
l_2k = L2_dist.icdf(0.98)
m_k = M_dist.icdf(0.05)
print(f"l_1k = {l_1k:.4f} kN/m^2")
print(f"l_2k = {l_2k:.4f} kN/m^2")
print(f"m_k = {m_k:.4f} kN/m")

# ---------------------------------------------------------------------------------------
# Design Values
print(f"\n")
print("================================")
print("Design Values")
print("================================")
l_1d = l_1k * gamma_F1
l_2d = l_2k * gamma_F2
m_d = m_k / gamma_M
print(f"l_1d = {l_1d:.4f} kN/m^2")
print(f"l_2d = {l_2d:.4f} kN/m^2")
print(f"m_d = {m_d:.4f} kN/m")

# ---------------------------------------------------------------------------------------
# Measures of Nonlinearity
y0 = y0(l_1k=l_1k, l_2k=l_2k, t_S=t_S_hypar_nonlinear)
k1 = kappa_1(l_1k=l_1k, l_1d=l_1d,t_S=t_S_hypar_nonlinear)
k2 = kappa_2(l_2k=l_2k, l_2d=l_2d,t_S=t_S_hypar_nonlinear)
k12 = kappa_12(l_1k=l_1k, l_1d=l_1d, l_2k=l_2k, l_2d=l_2d, t_S=t_S_hypar_nonlinear)
r1 = r1(l_1k=l_1k, l_2k=l_2k, t_S=t_S_hypar_nonlinear)
r2 = r2(l_1k=l_1k, l_2k=l_2k, t_S=t_S_hypar_nonlinear)

print(f"\n")
print("================================")
print("Measures of nonlinearity")
print("================================")

print(f"y0: {y0}")
print(f"kappa1: {k1}")
print(f"kappa2: {k2}")
print(f"kappa12: {k12}")
print(f"r1 = {r1}")
print(f"r2 = {r2}")

# ---------------------------------------------------------------------------------------
# Construction of the Nataf Distribution
marginal_dist = [Theta_M_dist, 
                 M_dist, 
                 Theta_L1_dist, 
                 L1_dist, 
                 Theta_L2_dist, 
                 L2_dist, 
                 Theta_S_dist]

nataf = ERANataf(M=marginal_dist, Correlation=np.eye(len(marginal_dist)))

# ---------------------------------------------------------------------------------------
# Design parameters p for option 1 and 2 
e_d_opt1 = t_S_hypar_nonlinear(L_1=l_1d, L_2=l_2d) # kN/m

argument_1 = gamma_F1 * t_S_hypar_nonlinear(L_1=l_1k, L_2=(gamma_F2/gamma_F1) * l_2k)
argument_2 = gamma_F2 * t_S_hypar_nonlinear(L_1=(gamma_F1/gamma_F2) * l_1k, L_2=l_2k)
e_d_opt2 = max(argument_1, argument_2) # kN/m

# Here, p has the [m] ! -> not unitless as with syst_4 and syst_8
p_opt1 = gamma_M * e_d_opt1 / m_k
p_opt2 = gamma_M * e_d_opt2 / m_k


print(f"\n")
print("================================")
print("Design Parameters p")
print("================================")
print("Design Option 1:")
print(f"e_d = {e_d_opt1} kN/m2")
print(f"p_opt1 = {p_opt1:.5f}")
print(f"\n")
print("Design Option 2:")
print(f"e_d = {e_d_opt2} kN/m2")
print(f"p_opt2 = {p_opt2:.5f}")

# ---------------------------------------------------------------------------------------
# Subset Simulation
# not feasible, simulation takes too long on my computer (see Meeting 14 notes)

# ---------------------------------------------------------------------------------------
# Limit State Functions g(X) for option 1 and 2 with FORM
# def g_opt1_FORM(x):
#     x = np.asarray(x, dtype=float)
#     return p_opt1 * x[..., 0] - t_S_hypar_nonlinear(L_1= x[..., 1], L_2= x[..., 2])

# def g_opt2_FORM(x):
#     x = np.asarray(x, dtype=float)
#     return p_opt2 * x[..., 0] - t_S_hypar_nonlinear(L_1= x[..., 1], L_2= x[..., 2])

# Test: Conventional indexing
def g_opt1_FORM(x):
    resistance_side = p_opt1 * x[0] * x[1]
    action_side = x[6] * t_S_nonl_vectorized((x[2] * x[3]), (x[4] * x[5]))
    
    return resistance_side - action_side

def g_opt2_FORM(x):
    resistance_side = p_opt2 * x[0] * x[1]
    action_side = x[6] * t_S_nonl_vectorized((x[2] * x[3]), (x[4] * x[5]))
    
    return resistance_side - action_side
# ---------------------------------------------------------------------------------------
# FORM via HLRF # 
# print("\n=== FORM (HLRF) - Design option (1) ===")
# [u_star_1, x_star_1, beta_1, Pf_1, _, _] = FORM_HLRF(
#     g=g_opt1_FORM, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

# FORM via fmincon  
print("\n=== FORM (fmincon) - Design option (1) ===")
[u_star_1, x_star_1, beta_1, alpha_1, Pf_1]  = FORM_fmincon(
    g=g_opt1_FORM, dg=[] , distr=nataf, u0=0, maxit=60, tol=1e-6)

# FORM via HLRF # 
# print("\n=== FORM (HLRF) - Design option (2) ===")
# u_star_2, x_star_2, beta_2, Pf_2, _, _ = FORM_HLRF(
#     g=g_opt2_FORM, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

# # FORM via fmincon  
# print("\n=== FORM (fmincon) - Design option (2) ===")
# [u_star_2, x_star_2, beta_2, alpha_2, Pf_2]  = FORM_fmincon(
#     g=g_opt2_FORM, dg=[] , distr=nataf, u0=0, maxit=60, tol=1e-6)

print("\n\n=== SUMMARY ===")
print("\nDesign option (1)")
print(f"beta = {beta_1:.3f}") 
print(f"x_star_1 = {x_star_1}")
print(f"alpha_1 = {u_star_1/beta_1}")

# print("\n\nDesign option (2)")
# print(f"beta = {beta_2:.3f}") 
# print(f"x_star_2 = {x_star_2}")
# print(f"alpha_2 = {u_star_2/beta_2}")


# ---------------------------------------------------------------------------------------
# Safety Homogenization is out of scope
