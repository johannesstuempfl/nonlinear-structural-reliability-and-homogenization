import numpy as np
from syst_7_measures_of_nonlinearity import y0, kappa_1, kappa_2, kappa_12, r1, r2
from syst_7_model_functions import t_S_hypar_nonlinear, t_S_hyperplane_linear

from ERA_Distribution_Classes_Python.Classes.ERADist import ERADist
from ERA_Distribution_Classes_Python.Classes.ERANataf import ERANataf
from ERA_Distribution_Classes_Python.Classes.FORM_HLRF import FORM_HLRF
from ERA_Distribution_Classes_Python.Classes.FORM_fmincon import FORM_fmincon

# Vectorized Version of the Structural response function (Better for array handling later)
t_S_lin_vectorized = np.vectorize(t_S_hyperplane_linear, otypes=[float])

# ---------------------------------------------------------------------------------------
# Target characteristic Values for calibrating Random Variables

# Characteristic tensile strength in MPa 
m_k = 12.088790043382897 # adjusted to eta = 100% for Design Opt 1 TH1 (linear)

# Characteristic Loads in kN/m2
s_k = 1.1  # snow  (in negative z-direction)
q_b = 0.65 # wind pressure (in negative y-direction)
w_k = q_b  # wind load without c_pe,10. Choice of loads more arbitrary than syst_4


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


# Structural Response Model Uncertainty $\Theta_{S}$: Annahme!
mu_Theta_S = 1.0
cov_Theta_S = 0.15
sig_Theta_S = mu_Theta_S * cov_Theta_S
Theta_S_dist = ERADist('normal', 'MOM', [mu_Theta_S, sig_Theta_S])


# Resistance Model Uncertainty $\Theta_{M}$ Annahme !
mu_Theta_M = 1.0
cov_Theta_M = 0.15
sig_Theta_M = mu_Theta_M * cov_Theta_M
Theta_M_dist = ERADist('lognormal', 'MOM', [mu_Theta_M, sig_Theta_M])


# membrane tensile strength in MPa from paper with Martin -> i don't know where how it is derived!!
mu_M = 1.0
cov_M = 0.1
sig_M = mu_M * cov_M
M_dist = ERADist('lognormal', 'MOM', [mu_M, sig_M]) 

# ---------------------------------------------------------------------------------------
# Shifting / Scaling Random Variables 
# Snow 
print(f"\n")
print("================================")
print("Transformation of snow load on ground")
print("================================")

percentile_L1 = L1_dist.icdf(0.98)

snow_shift = s_k / percentile_L1 # ratio of target to current percentile, by which mean and std get multiplied

mu_L1_shifted = mu_L1 * snow_shift
sig_L1_shifted = sig_L1 * snow_shift
L1_shifted_dist = ERADist('gumbel','MOM',[mu_L1_shifted, sig_L1_shifted])

print(f"""Snow Load on Ground gets shifted by {snow_shift}""")
print(f"""Old mean: {mu_L1}; New mean: {mu_L1_shifted}""")
print(f"""Old std: {sig_L1}; New std: {sig_L1_shifted}""")
print(f"""Old 98th percentile: {L1_dist.icdf(.98)}; New 98th percentile: {L1_shifted_dist.icdf(.98)}""")
print(f"""Old COV: {L1_dist.std()/L1_dist.mean()}; New COV: {L1_shifted_dist.std()/L1_shifted_dist.mean()}""")


# Wind
print(f"\n")
print("================================")
print("Transformation of wind velocity pressure")
print("================================")

percentile_L2 = L2_dist.icdf(0.98)

wind_shift = q_b / percentile_L2 # ratio of target to current percentile, by which mean and std get multiplied

mu_L2_shifted = mu_L2 * wind_shift
sig_L2_shifted = sig_L2 * wind_shift
L2_shifted_dist = ERADist('gumbel','MOM',[mu_L2_shifted, sig_L2_shifted])

print(f"""Sind velocity pressure gets shifted by {wind_shift}""")
print(f"""Old mean: {mu_L2}; New mean: {mu_L2_shifted}""")
print(f"""Old std: {sig_L2}; New std: {sig_L2_shifted}""")
print(f"""Old 98th percentile: {L2_dist.icdf(.98)}; New 98th percentile: {L2_shifted_dist.icdf(.98)}""")
print(f"""Old COV: {L2_dist.std()/L2_dist.mean()}; New COV: {L2_shifted_dist.std()/L2_shifted_dist.mean()}""")


# Steel 
print(f"\n")
print("================================")
print("Transformation of membrane tensile strength")
print("================================")

percentile_M = M_dist.icdf(.05)

tensile_shift = m_k / percentile_M # ratio of target to current percentile, by which mean and std get multiplied

mu_M_shifted = mu_M * tensile_shift
sig_M_shifted = sig_M * tensile_shift
M_shifted_dist = ERADist('lognormal','MOM',[mu_M_shifted, sig_M_shifted])

print(f"""Membrane tensile strength strength gets shifted by {tensile_shift}""")
print(f"""Old mean: {mu_M}; New mean: {mu_M_shifted}""")
print(f"""Old std: {sig_M}; New std: {sig_M_shifted}""")
print(f"""Old 5th percentile: {M_dist.icdf(.05)}; New 5th percentile: {M_shifted_dist.icdf(.05)}""")
print(f"""Old COV: {M_dist.std()/M_dist.mean()}; New COV: {M_shifted_dist.std()/M_shifted_dist.mean()}""")


# ---------------------------------------------------------------------------------------
# Partial Safety Factors
gamma_F1 = 1.5  # snow
gamma_F2 = 1.5  # wind
gamma_M = 1.4   # resistance side (from Technical Specification, CEN TC250 WG5)

# ---------------------------------------------------------------------------------------
# Characteristic values derived from Random Variables for further calculation
print(f"\n")
print("================================")
print("Characteristic values")
print("================================")
l_1k = L1_shifted_dist.icdf(0.98)
l_2k = L2_shifted_dist.icdf(0.98)
m_k = M_shifted_dist.icdf(0.05)
print(f"l_1k = {l_1k:.4f} kN/m^2")
print(f"l_2k = {l_2k:.4f} kN/m^2")
print(f"m_k = {m_k:.4f} MPa")

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
print(f"m_d = {m_d:.4f} MPa")

# ---------------------------------------------------------------------------------------
# Measures of Nonlinearity
y0 = y0(l_1k=l_1k, l_2k=l_2k, t_S=t_S_hyperplane_linear)
k1 = kappa_1(l_1k=l_1k, l_1d=l_1d,t_S=t_S_hyperplane_linear)
k2 = kappa_2(l_2k=l_2k, l_2d=l_2d,t_S=t_S_hyperplane_linear)
k12 = kappa_12(l_1k=l_1k, l_1d=l_1d, l_2k=l_2k, l_2d=l_2d, t_S=t_S_hyperplane_linear)
r1 = r1(l_1k=l_1k, l_2k=l_2k, t_S=t_S_hyperplane_linear)
r2 = r2(l_1k=l_1k, l_2k=l_2k, t_S=t_S_hyperplane_linear)

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
marginal_dist_with_uncertainties = [Theta_M_dist, 
                 M_shifted_dist, 
                 Theta_L1_dist, 
                 L1_shifted_dist, 
                 Theta_L2_dist, 
                 L2_shifted_dist, 
                 Theta_S_dist]

nataf_with_uncertainties = ERANataf(M=marginal_dist_with_uncertainties, Correlation=np.eye(len(marginal_dist_with_uncertainties)))


marginal_dist_without_uncertainties = [M_shifted_dist, L1_shifted_dist, L2_shifted_dist]

nataf_without_uncertainties = ERANataf(M=marginal_dist_without_uncertainties, Correlation=np.eye(len(marginal_dist_without_uncertainties)))


# ---------------------------------------------------------------------------------------
# Design parameters p for option 1 and 2 
# Design Opt 1
e_d_1 = t_S_hyperplane_linear(l_1d, l_2d)

# Design Opt 2
argument_1 = gamma_F1 * t_S_hyperplane_linear(l_1k,  (gamma_F2 / gamma_F1) * l_2k)
argument_2 = gamma_F2 * t_S_hyperplane_linear((gamma_F1 / gamma_F2) * l_1k, l_2k)
e_d_2 = max(argument_1, argument_2)

# Design Opt 2'
argument_1_primed = gamma_F1 * (t_S_hyperplane_linear(l_1k,  (gamma_F2 / gamma_F1) * l_2k) - t_S_hyperplane_linear(0,0)) + t_S_hyperplane_linear(0,0)
argument_2_primed = gamma_F2 * (t_S_hyperplane_linear((gamma_F1 / gamma_F2) * l_1k, l_2k) - t_S_hyperplane_linear(0,0)) + t_S_hyperplane_linear(0,0)
e_d_2_primed = max(argument_1_primed, argument_2_primed)


p_opt1 = gamma_M * e_d_1 / m_k
p_opt2 = gamma_M * e_d_2 / m_k
p_opt2_primed = gamma_M * e_d_2_primed / m_k

print(f"\n")
print("================================")
print("Design Parameters p")
print("================================")
print(f"\n")
print("Design Option 1:")
print(f"e_d = {e_d_1} MPa")
print(f"eta = {e_d_1/m_d}")
print(f"p_opt1 = {p_opt1}")
print(f"\n")
print("Design Option 2:")
print(f"e_d = {e_d_2} MPa")
print(f"eta = {e_d_2/m_d}")
print(f"p_opt2 = {p_opt2}")
print(f"\n")
print("Design Option 2':")
print(f"e_d = {e_d_2_primed} MPa")
print(f"eta = {e_d_2_primed/m_d}")
print(f"p_opt2' = {p_opt2_primed}")

# ---------------------------------------------------------------------------------------
# Subset Simulation
# not feasible, simulation takes too long

# ---------------------------------------------------------------------------------------
# Limit State Functions g(X) for option 1 and 2 with FORM, with model uncertainties

def g_opt1_FORM(x):
    
    resistance_side = p_opt1 * x[0] * x[1]
    action_side = x[6] * t_S_lin_vectorized((x[2] * x[3]), (x[4] * x[5]))
    
    return resistance_side - action_side

# def g_opt1_FORM(x):
#     x = np.asarray(x, dtype=float)
#     resistance_side = p_opt1 * x[0] * x[1]

#     F_BOUND = 10.0  # hard upper limit that the cablenet model still can solve to prevent crashing
#     F_Z = np.clip(np.nan_to_num(x[3], nan=0.0, posinf=F_BOUND, neginf=0.0), 0.0, F_BOUND)
#     F_Y = np.clip(np.nan_to_num(x[5], nan=0.0, posinf=F_BOUND, neginf=0.0), 0.0, F_BOUND)

#     action_side = x[6] * t_S_lin_vectorized(x[2] * F_Z, x[4] * F_Y)

#     g_val = resistance_side - action_side
#     return np.nan_to_num(g_val, nan=-1e6, posinf=1e6, neginf=-1e6)

def g_opt2_FORM(x):
    
    resistance_side = p_opt2 * x[0] * x[1]
    action_side = x[6] * t_S_lin_vectorized((x[2] * x[3]), (x[4] * x[5]))
    
    return resistance_side - action_side

def g_opt2_primed_FORM(x):
    
    resistance_side = p_opt2_primed * x[0] * x[1]
    action_side = x[6] * t_S_lin_vectorized((x[2] * x[3]), (x[4] * x[5]))
    
    return resistance_side - action_side


# ---------------------------------------------------------------------------------------
# FORM via fmincon, with model uncertainties

print("\n=== FORM (fmincon) - Design option (1) ===")
[u_star_1, x_star_1, beta_1, alpha_1, Pf_1]  = FORM_fmincon(
    g=g_opt1_FORM, dg=[] , distr=nataf_with_uncertainties, u0=1, maxit=60, tol=1e-6)


# FORM via fmincon  
print("\n=== FORM (fmincon) - Design option (2) ===")
[u_star_2, x_star_2, beta_2, alpha_2, Pf_2]  = FORM_fmincon(
    g=g_opt2_FORM, dg=[] , distr=nataf_with_uncertainties, u0=1, maxit=60, tol=1e-6)

# FORM via fmincon  
print("\n=== FORM (fmincon) - Design option (2') ===")
[u_star_2_primed, x_star_2_primed, beta_2_primed, alpha_2_primed, Pf_2_primed]  = FORM_fmincon(
    g=g_opt2_primed_FORM, dg=[] , distr=nataf_with_uncertainties, u0=1, maxit=60, tol=1e-6)

print("\n\n=== SUMMARY ===")
print("\nDesign option (1)")
print(f"Pf_1 = {Pf_1}")
print(f"beta_1 = {beta_1}") 
print(f"x_star_1 = {x_star_1}")
print(f"(alpha_1)^2 = {(u_star_1/beta_1)**2}")
print(f"g(X*) = {g_opt1_FORM(x_star_1)}")

print("\n\nDesign option (2)")
print(f"Pf_2 = {Pf_2}")
print(f"beta_2 = {beta_2}") 
print(f"x_star_2 = {x_star_2}")
print(f"(alpha_2)^2 = {(u_star_2/beta_2)**2}")
print(f"g(X*) = {g_opt2_FORM(x_star_2)}")

print("\n\nDesign option (2')")
print(f"Pf_2' = {Pf_2_primed}")
print(f"beta_2' = {beta_2_primed}") 
print(f"x_star_2' = {x_star_2_primed}")
print(f"(alpha_2')^2 = {(u_star_2_primed/beta_2_primed)**2}")
print(f"g(X*) = {g_opt2_primed_FORM(x_star_2_primed)}")



# ---------------------------------------------------------------------------------------
# Limit State Functions g(X) for option 1, 2 and 2' with FORM, without model uncertainties

def g_opt1_FORM(x):
    
    resistance_side = p_opt1 * x[0]
    action_side = t_S_lin_vectorized((x[1]), (x[2]))
    
    return resistance_side - action_side

def g_opt2_FORM(x):
    
    resistance_side = p_opt2 * x[0] 
    action_side = t_S_lin_vectorized((x[1]), (x[2]))
    
    return resistance_side - action_side

def g_opt2_primed_FORM(x):
    
    resistance_side = p_opt2_primed * x[0] 
    action_side = t_S_lin_vectorized((x[1]), (x[2]))
    
    return resistance_side - action_side

# ---------------------------------------------------------------------------------------
# FORM via fmincon, without model uncertainties

# print("\n=== FORM (fmincon) - Design option (1) ===")
# [u_star_1, x_star_1, beta_1, alpha_1, Pf_1]  = FORM_fmincon(
#     g=g_opt1_FORM, dg=[] , distr=nataf_without_uncertainties, u0=1, maxit=60, tol=1e-6)

# # FORM via fmincon  
# print("\n=== FORM (fmincon) - Design option (2) ===")
# [u_star_2, x_star_2, beta_2, alpha_2, Pf_2]  = FORM_fmincon(
#     g=g_opt2_FORM, dg=[] , distr=nataf_without_uncertainties, u0=1, maxit=60, tol=1e-6)

# # FORM via fmincon  
# print("\n=== FORM (fmincon) - Design option (2') ===")
# [u_star_2_primed, x_star_2_primed, beta_2_primed, alpha_2_primed, Pf_2_primed]  = FORM_fmincon(
#     g=g_opt2_primed_FORM, dg=[] , distr=nataf_without_uncertainties, u0=1, maxit=60, tol=1e-6)


# print("\n\n=== SUMMARY ===")
# print("\nDesign option (1)")
# print(f"Pf_1 = {Pf_1}")
# print(f"beta_1 = {beta_1}") 
# print(f"x_star_1 = {x_star_1}")
# print(f"(alpha_1)^2 = {(u_star_1/beta_1)**2}")

# print("\n\nDesign option (2)")
# print(f"Pf_2 = {Pf_2}")
# print(f"beta_2 = {beta_2}") 
# print(f"x_star_2 = {x_star_2}")
# print(f"(alpha_2)^2 = {(u_star_2/beta_2)**2}")

# print("\n\nDesign option (2')")
# print(f"Pf_2' = {Pf_2_primed}")
# print(f"beta_2' = {beta_2_primed}") 
# print(f"x_star_2' = {x_star_2_primed}")
# print(f"(alpha_2')^2 = {(u_star_2_primed/beta_2_primed)**2}")