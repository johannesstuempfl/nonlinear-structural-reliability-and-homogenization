from syst_8_model_functions import t_S_cablenet_linear, t_S_cablenet_nonlinear
from syst_8_measures_of_nonlinearity import y0, kappa_1, kappa_2, kappa_12, r1, r2

sigma_Rd = 1500 # MPa

e = 35 # arbitrary load distribution area in m2 (chosen for calibration of design parameter p)


s_k = 1.1  # snow kN/m2 (in negative z-direction)
q_b = 0.65 # wind pressure kN/m2 (in negative y-direction)
w_k = q_b  # wind load kN/m2 without c_pe,10. Choice of loads more arbitrary than syst_4

# Characteristic Loads
l_1k = s_k * e * 1000 # conversion from kN to N -> * 1000
l_2k = w_k * e * 1000 # conversion from kN to N -> * 1000

# Partial Safety Factors
gamma_F1 = 1.5
gamma_F2 = 1.5
psi_0 = 1.0 # 0.6     # Windload

# Design Loads
l_1d = gamma_F1 * l_1k                    # vertical distributed load
l_2d = gamma_F2 * psi_0 * l_2k          # horizontal distributed load



y0 = y0(l_1k=l_1k, l_2k=l_2k, t_S=t_S_cablenet_nonlinear)
k1 = kappa_1(l_1k=l_1k, l_1d=l_1d, t_S=t_S_cablenet_nonlinear)
k2 = kappa_2(l_2k=l_2k, l_2d=l_2d, t_S=t_S_cablenet_nonlinear)
k12 = kappa_12(l_1k=l_1k, l_1d=l_1d, l_2k=l_2k, l_2d=l_2d, t_S=t_S_cablenet_nonlinear)
r1 = r1(l_1k=l_1k, l_2k=l_2k, t_S=t_S_cablenet_nonlinear)
r2 = r2(l_1k=l_1k, l_2k=l_2k, t_S=t_S_cablenet_nonlinear)

sigma_Ed_1 = t_S_cablenet_nonlinear(l_1d, l_2d)

argument_1 = gamma_F1 * t_S_cablenet_nonlinear(l_1k,  (gamma_F2 / gamma_F1) * l_2k)
argument_2 = gamma_F2 * t_S_cablenet_nonlinear((gamma_F1 / gamma_F2) * l_1k, l_2k)
sigma_Ed_2 = max(argument_1,argument_2)


print("Design Option 1:")
print(f"sigma = {sigma_Ed_1}")

print("Design Option 2:")
print(f"sigma = {sigma_Ed_2}")

print(f"y0 = {y0}")
print(f"kappa1 = {k1}")
print(f"kappa2 = {k2}")
print(f"kappa12 = {k12}")
print(f"r1 = {r1}")
print(f"r2 = {r2}")

print(f"l1k = {l_1k}")
print(f"l1d = {l_1d}")
print(f"l2k = {l_2k}")
print(f"l2d = {l_2d}")
print(f"sigma_Rd = {sigma_Rd}")
print("Design Option 1:")
print(f"sigma = {sigma_Ed_1}")
print(f"eta = {sigma_Ed_1/sigma_Rd}")

print("Design Option 2:")
print(f"sigma = {sigma_Ed_2}")
print(f"eta = {sigma_Ed_2/sigma_Rd}")