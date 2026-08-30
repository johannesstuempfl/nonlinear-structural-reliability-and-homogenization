from measures_of_nonlinearity import kappa_1, kappa_2, kappa_12, r1, r2
from syst_4_model_functions import t_S_linear, t_S_nonlinear

# NEW modified IPE 120 -> eta = 100% for Th.I.O.
E = 210e6 # kN/m2 
A = 1.321e-3 # m2
I = 0.2740555e-5 # m4
h = 0.12  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * 1.14 # kNm


# Node 1 
x_1 = 0.0
z_1 = 0.0
# Node 2
x_2 = 0.1
z_2 = -3.0
# Node 3
x_3 = 3.6
z_3 = -3.0

# Outer dimensions for beam 1
delta_x_1 = x_2 - x_1
delta_z_1 = z_2 - z_1

# Outer dimensions for beam 2
delta_x_2 = x_3 - x_2
delta_z_2 = z_3 - z_2


e = 5 # load distribution length in m


s_k = 1.1  # snow kN/m2
q_b = 0.65 # wind pressure kN/m2


# Naming Convention according to Max PHD 
l_1k = s_k
l_2k = q_b 

# Partial Safety Factors
gamma_G = 1.35
gamma_Q = 1.5
psi_0 = 1.0 # 0.6     # Windload

# Design Loads
e_d_vertical = gamma_Q * l_1k                    # vertical distributed load
e_d_horizontal = gamma_Q * psi_0 * l_2k          # horizontal distributed load

# Naming Convention according to Max PHD 
l_1d = e_d_vertical # Vertical Design load
l_2d = e_d_horizontal # Horizontal Design load



k1 = kappa_1(l_1k=l_1k, l_1d=l_1d, t_S=t_S_nonlinear)
k2 = kappa_2(l_2k=l_2k, l_2d=l_2d, t_S=t_S_nonlinear)
k12 = kappa_12(l_1k=l_1k, l_1d=l_1d, l_2k=l_2k, l_2d=l_2d, t_S=t_S_nonlinear)
r1 = r1(l_1k=l_1k, l_2k=l_2k, t_S=t_S_nonlinear)
r2 = r2(l_1k=l_1k, l_2k=l_2k, t_S=t_S_nonlinear)

M_Ed = t_S_nonlinear(l_1=l_1d, l_2=l_2d)

print(f"kappa1: {k1}")
print(f"kappa2: {k2}")
print(f"kappa12: {k12}")
print(f"r1: {r1}")
print(f"r2: {r2}")

print(f"l1k= {l_1k}")
print(f"l1d= {l_1d}")
print(f"l2k= {l_2k}")
print(f"l2d= {l_2d}")
print(f"M_pl_Rd= {M_yield}")
print(f"M_Ed = {M_Ed}")
print(f"eta= {M_Ed/M_yield}")