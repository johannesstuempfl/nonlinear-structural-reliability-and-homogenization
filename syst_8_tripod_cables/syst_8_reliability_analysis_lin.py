import numpy as np
from syst_8_measures_of_nonlinearity import y0, kappa_1, kappa_2, kappa_12, r1, r2
from syst_8_model_functions import t_S_cablenet_linear, t_S_cablenet_nonlinear

from ERA_Distribution_Classes_Python.Classes.ERADist import ERADist
from ERA_Distribution_Classes_Python.Classes.ERANataf import ERANataf
from ERA_Distribution_Classes_Python.Classes.FORM_HLRF import FORM_HLRF
from ERA_Distribution_Classes_Python.Classes.FORM_fmincon import FORM_fmincon
from ERA_Distribution_Classes_Python.Classes.SuS import SuS

# Vectorized Version of the Structural response function (Better for array handling later)
t_S_lin_vectorized = np.vectorize(t_S_cablenet_linear, otypes=[float])


# ---------------------------------------------------------------------------------------
# Target characteristic Values for calibrating Random Variables

# Characteristic yield strength in MPa 
#f_u = 1601.7305471 # deprecated
f_u = 1726.2770986111154 # adjusted to eta = 100% for Design Opt 2

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
print("Transformation of steel yielding strength")
print("================================")

percentile_M = M_dist.icdf(.05)

steel_shift = f_u / percentile_M # ratio of target to current percentile, by which mean and std get multiplied

mu_M_shifted = mu_M * steel_shift
sig_M_shifted = sig_M * steel_shift
M_shifted_dist = ERADist('lognormal','MOM',[mu_M_shifted, sig_M_shifted])

print(f"""Steel yielding strength gets shifted by {steel_shift}""")
print(f"""Old mean: {mu_M}; New mean: {mu_M_shifted}""")
print(f"""Old std: {sig_M}; New std: {sig_M_shifted}""")
print(f"""Old 5th percentile: {M_dist.icdf(.05)}; New 5th percentile: {M_shifted_dist.icdf(.05)}""")
print(f"""Old COV: {M_dist.std()/M_dist.mean()}; New COV: {M_shifted_dist.std()/M_shifted_dist.mean()}""")

# ---------------------------------------------------------------------------------------
# Partial Safety Factors
gamma_F1 = 1.5
gamma_F2 = 1.5
psi_0 = 1.0 # 0.6  # Windload
gamma_M = 1.5 # Material Side (DIN EN 1993-1-11)

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
l_2d = l_2k * gamma_F2 * psi_0
m_d = m_k / gamma_M
print(f"l_1d = {l_1d:.4f} kN/m^2")
print(f"l_2d = {l_2d:.4f} kN/m^2")
print(f"m_d = {m_d:.4f} MPa")

# ---------------------------------------------------------------------------------------
# Measures of Nonlinearity

y0 = y0(l_1k=l_1k, l_2k=l_2k, t_S=t_S_cablenet_linear)
k1 = kappa_1(l_1k=l_1k, l_1d=l_1d, t_S=t_S_cablenet_linear)
k2 = kappa_2(l_2k=l_2k, l_2d=l_2d, t_S=t_S_cablenet_linear)
k12 = kappa_12(l_1k=l_1k, l_1d=l_1d, l_2k=l_2k, l_2d=l_2d, t_S=t_S_cablenet_linear)
r1 = r1(l_1k=l_1k, l_2k=l_2k, t_S=t_S_cablenet_linear)
r2 = r2(l_1k=l_1k, l_2k=l_2k, t_S=t_S_cablenet_linear)

e_d_1 = t_S_cablenet_linear(l_1d, l_2d)

argument_1 = gamma_F1 * t_S_cablenet_linear(l_1k,  (gamma_F2 / gamma_F1) * l_2k)
argument_2 = gamma_F2 * t_S_cablenet_linear((gamma_F1 / gamma_F2) * l_1k, l_2k)
e_d_2 = max(argument_1,argument_2)

e_d_linear = t_S_cablenet_linear(l_1d, l_2d)

print(f"\n")
print("================================")
print("Measures of nonlinearity")
print("================================")

print(f"\n")
print(f"y0 = {y0}")
print(f"kappa1 = {k1}")
print(f"kappa2 = {k2}")
print(f"kappa12 = {k12}")
print(f"r1 = {r1}")
print(f"r2 = {r2}")

print(f"\n")
print("Design Option 1:")
print(f"e_d = {e_d_1} MPa")
print(f"eta = {e_d_1/m_d}")
print(f"\n")
print("Design Option 2:")
print(f"e_d = {e_d_2} MPa")
print(f"eta = {e_d_2/m_d}")

# ---------------------------------------------------------------------------------------
# Construction of the Nataf Distribution
marginal_dist = [Theta_M_dist, 
                 M_shifted_dist, 
                 Theta_L1_dist, 
                 L1_shifted_dist, 
                 Theta_L2_dist, 
                 L2_shifted_dist, 
                 Theta_S_dist]

nataf = ERANataf(M=marginal_dist, Correlation=np.eye(len(marginal_dist)))


# ---------------------------------------------------------------------------------------
# Design parameters p for option 1 and 2 
e_d_opt1 = t_S_cablenet_linear(F_Z=l_1d, F_Y=l_2d) # kN/m

argument_1 = gamma_F1 * t_S_cablenet_linear(F_Z=l_1k, F_Y=(gamma_F2/gamma_F1) * l_2k)
argument_2 = gamma_F2 * t_S_cablenet_linear(F_Z=(gamma_F1/gamma_F2) * l_1k, F_Y=l_2k)
e_d_opt2 = max(argument_1, argument_2) # kN/m


p_opt1 = gamma_M * e_d_opt1 / m_k
p_opt2 = gamma_M * e_d_opt2 / m_k

print(f"\n")
print("================================")
print("Design Parameters p")
print("================================")
print(f"p_opt1 = {p_opt1}")
print(f"p_opt2 = {p_opt2}")

# ---------------------------------------------------------------------------------------
# Limit State Functions g(X) for option 1 and 2 with SuS

def g_opt1_SuS(x):
    
    resistance_side = p_opt1 * x[:,0] * x[:,1]
    action_side = x[:,6] * t_S_lin_vectorized((x[:,2] * x[:,3]), (x[:,4] * x[:,5]))
    
    return resistance_side - action_side

def g_opt2_SuS(x):
    
    resistance_side = p_opt2 * x[:,0] * x[:,1]
    action_side = x[:,6] * t_S_lin_vectorized((x[:,2] * x[:,3]), (x[:,4] * x[:,5]))
    
    return resistance_side - action_side

# ---------------------------------------------------------------------------------------
# Subset Simulation

# # Option 1
# np.random.seed(42)

# samples_return = 1
# N  = 10000        # Total number of samples for each level
# p0 = 0.1         # Probability of each subset, chosen adaptively

# print('\n\nSUBSET SIMULATION OPTION 1: ')
# [Pf_SuS_1, delta_SuS, b, Pf_1, b_sus, pf_sus, samplesU, samplesX_1, fs_iid] = SuS(N, p0, g_opt1_SuS, nataf, samples_return)


# # Option 2 
# samples_return = 1
# N  = 10000        # Total number of samples for each level
# p0 = 0.1         # Probability of each subset, chosen adaptively

# print('\n\nSUBSET SIMULATION OPTION 2: ')
# [Pf_SuS_2, delta_SuS, b, Pf_2, b_sus, pf_sus, samplesU, samplesX_2, fs_iid] = SuS(N, p0, g_opt2_SuS, nataf, samples_return)



# print("\n\n=== SUMMARY SUBSET SIMULATION ===")

# print("\nDesign option (1)")
# print(f"Pr(F) = {Pf_SuS_1}")
# X = ERADist('standardnormal','MOM',[])
# beta_1_SuS = - X.icdf(Pf_SuS_1)
# print(f"beta = {beta_1_SuS}")

# print("\nDesign option (2)")
# print(f"Pr(F) = {Pf_SuS_2}")
# X = ERADist('standardnormal','MOM',[])
# beta_2_SuS = - X.icdf(Pf_SuS_2)
# print(f"beta = {beta_2_SuS}")



# ---------------------------------------------------------------------------------------
# Limit State Functions g(X) for option 1 and 2 with FORM

def g_opt1_FORM(x):
    
    resistance_side = p_opt1 * x[0] * x[1]
    action_side = x[6] * t_S_lin_vectorized((x[2] * x[3]), (x[4] * x[5]))
    
    return resistance_side - action_side

def g_opt2_FORM(x):
    
    resistance_side = p_opt2 * x[0] * x[1]
    action_side = x[6] * t_S_lin_vectorized((x[2] * x[3]), (x[4] * x[5]))
    
    return resistance_side - action_side

# ---------------------------------------------------------------------------------------
# FORM via HLRF # converged to beta = 0.0
# print("\n=== FORM (HLRF) - Design option (1) ===")
# [u_star_1, x_star_1, beta_1, Pf_1, _, _] = FORM_HLRF(
#     g=g_opt1_FORM, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

# FORM via fmincon  
print("\n=== FORM (fmincon) - Design option (1) ===")
[u_star_1, x_star_1, beta_1, alpha_1, Pf_1]  = FORM_fmincon(
    g=g_opt1_FORM, dg=[] , distr=nataf, u0=0, maxit=60, tol=1e-6)

# FORM via HLRF # converged to beta = 0.0
# print("\n=== FORM (HLRF) - Design option (2) ===")
# u_star_2, x_star_2, beta_2, Pf_2, _, _ = FORM_HLRF(
#     g=g_opt2_FORM, dg=[], distr=nataf, sensitivity_analysis=0, u0=0, maxit=60, tol=1e-4)

# FORM via fmincon  
print("\n=== FORM (fmincon) - Design option (2) ===")
[u_star_2, x_star_2, beta_2, alpha_2, Pf_2]  = FORM_fmincon(
    g=g_opt2_FORM, dg=[] , distr=nataf, u0=0, maxit=60, tol=1e-6)

print("\n\n=== SUMMARY ===")
print("\nDesign option (1)")
print(f"Pf_1 = {Pf_1}")
print(f"beta_1 = {beta_1}") 
print(f"x_star_1 = {x_star_1}")
print(f"alpha_1 = {u_star_1/beta_1}")

print("\n\nDesign option (2)")
print(f"Pf_2 = {Pf_2}")
print(f"beta_2 = {beta_2}") 
print(f"x_star_2 = {x_star_2}")
print(f"alpha_2 = {u_star_2/beta_2}")


