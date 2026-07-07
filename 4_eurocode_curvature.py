from structure import Structure
from solver_1st import Solver1stOrder 
from solver_2nd import Solver2ndOrder
from buckling_analysis import BucklingAnalysis
import numpy as np
import matplotlib.pyplot as plt

# approximately resembles an IPE 120
# E = 210e6 # kN/m2 
# A = 1.321e-3 # m2
# I = 0.318e-5 # m4
# h = 0.12  # m
# z = h/2  # m
# sigma_yield = 35.5 # kN/cm2 
# M_yield = I/z * sigma_yield * 100e2 * 1.14 # kNm

# NEW modified IPE 120 -> eta = 100% for Th.I.O.
E = 210e6 # kN/m2 
A = 1.321e-3 # m2
I = 0.2736705e-5 # m4
h = 0.12  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
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
w_k = q_b * 0.8 # wind load kN/m2 with c_pe,10 = 0.8 (Area D)



# Naming Convention according to Max PHD 
l_1k = s_k * e
l_2k = w_k * e

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



# Structural Model Function
def t_S(l_1, l_2):
    s = Structure()
    # Stab 1 
    n1 = s.add_node(x=delta_x_1 * 0/15,z=delta_z_1 * 0/15, kind="frame", support={"u": True, "w": True, "phi": False})
    n2 = s.add_node(x=delta_x_1 * 1/15,z=delta_z_1 * 1/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n3 = s.add_node(x=delta_x_1 * 2/15,z=delta_z_1 * 2/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n4 = s.add_node(x=delta_x_1 * 3/15,z=delta_z_1 * 3/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n5 = s.add_node(x=delta_x_1 * 4/15,z=delta_z_1 * 4/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n6 = s.add_node(x=delta_x_1 * 5/15,z=delta_z_1 * 5/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n7 = s.add_node(x=delta_x_1 * 6/15,z=delta_z_1 * 6/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n8 = s.add_node(x=delta_x_1 * 7/15,z=delta_z_1 * 7/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n9 = s.add_node(x=delta_x_1 * 8/15,z=delta_z_1 * 8/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n10 = s.add_node(x=delta_x_1 * 9/15,z=delta_z_1 * 9/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n11 = s.add_node(x=delta_x_1 * 10/15,z=delta_z_1 * 10/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n12 = s.add_node(x=delta_x_1 * 11/15,z=delta_z_1 * 11/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n13 = s.add_node(x=delta_x_1 * 12/15,z=delta_z_1 * 12/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n14 = s.add_node(x=delta_x_1 * 13/15,z=delta_z_1 * 13/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n15 = s.add_node(x=delta_x_1 * 14/15,z=delta_z_1 * 14/15, kind="frame", support={"u": False, "w": False, "phi": False})
    n16 = s.add_node(x=delta_x_1 * 15/15,z=delta_z_1 * 15/15, kind="frame", support={"u": False, "w": False, "phi": False})

    e1 = s.add_element(node_i=n1,node_j=n2, E=E, A=A, I=I)
    e2 = s.add_element(node_i=n2,node_j=n3, E=E, A=A, I=I)
    e3 = s.add_element(node_i=n3,node_j=n4, E=E, A=A, I=I)
    e4 = s.add_element(node_i=n4,node_j=n5, E=E, A=A, I=I)
    e5 = s.add_element(node_i=n5,node_j=n6, E=E, A=A, I=I)
    e6 = s.add_element(node_i=n6,node_j=n7, E=E, A=A, I=I)
    e7 = s.add_element(node_i=n7,node_j=n8, E=E, A=A, I=I)
    e8 = s.add_element(node_i=n8,node_j=n9, E=E, A=A, I=I)
    e9 = s.add_element(node_i=n9,node_j=n10, E=E, A=A, I=I)
    e10 = s.add_element(node_i=n10,node_j=n11, E=E, A=A, I=I)
    e11 = s.add_element(node_i=n11,node_j=n12, E=E, A=A, I=I)
    e12 = s.add_element(node_i=n12,node_j=n13, E=E, A=A, I=I)
    e13 = s.add_element(node_i=n13,node_j=n14, E=E, A=A, I=I)
    e14 = s.add_element(node_i=n14,node_j=n15, E=E, A=A, I=I)
    e15 = s.add_element(node_i=n15,node_j=n16, E=E, A=A, I=I)

    # Stab 2
    n17 = s.add_node(x=x_2 + delta_x_2 * 1/17,z=z_2 + delta_z_2 * 1/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n18 = s.add_node(x=x_2 + delta_x_2 * 2/17,z=z_2 + delta_z_2 * 2/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n19 = s.add_node(x=x_2 + delta_x_2 * 3/17,z=z_2 + delta_z_2 * 3/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n20 = s.add_node(x=x_2 + delta_x_2 * 4/17,z=z_2 + delta_z_2 * 4/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n21 = s.add_node(x=x_2 + delta_x_2 * 5/17,z=z_2 + delta_z_2 * 5/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n22 = s.add_node(x=x_2 + delta_x_2 * 6/17,z=z_2 + delta_z_2 * 6/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n23 = s.add_node(x=x_2 + delta_x_2 * 7/17,z=z_2 + delta_z_2 * 7/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n24 = s.add_node(x=x_2 + delta_x_2 * 8/17,z=z_2 + delta_z_2 * 8/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n25 = s.add_node(x=x_2 + delta_x_2 * 9/17,z=z_2 + delta_z_2 * 9/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n26 = s.add_node(x=x_2 + delta_x_2 * 10/17,z=z_2 + delta_z_2 * 10/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n27 = s.add_node(x=x_2 + delta_x_2 * 11/17,z=z_2 + delta_z_2 * 11/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n28 = s.add_node(x=x_2 + delta_x_2 * 12/17,z=z_2 + delta_z_2 * 12/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n29 = s.add_node(x=x_2 + delta_x_2 * 13/17,z=z_2 + delta_z_2 * 13/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n30 = s.add_node(x=x_2 + delta_x_2 * 14/17,z=z_2 + delta_z_2 * 14/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n31 = s.add_node(x=x_2 + delta_x_2 * 15/17,z=z_2 + delta_z_2 * 15/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n32 = s.add_node(x=x_2 + delta_x_2 * 16/17,z=z_2 + delta_z_2 * 16/17,kind="frame", support={"u": False, "w": False, "phi": False})
    n33 = s.add_node(x=x_2 + delta_x_2 * 17/17,z=z_2 + delta_z_2 * 17/17,kind="frame", support={"u": False, "w": True, "phi": False})

    e16 = s.add_element(node_i=n16,node_j=n17, E=E, A=A, I=I)
    e17 = s.add_element(node_i=n17,node_j=n18, E=E, A=A, I=I)
    e18 = s.add_element(node_i=n18,node_j=n19, E=E, A=A, I=I)
    e19 = s.add_element(node_i=n19,node_j=n20, E=E, A=A, I=I)
    e20 = s.add_element(node_i=n20,node_j=n21, E=E, A=A, I=I)
    e21 = s.add_element(node_i=n21,node_j=n22, E=E, A=A, I=I)
    e22 = s.add_element(node_i=n22,node_j=n23, E=E, A=A, I=I)
    e23 = s.add_element(node_i=n23,node_j=n24, E=E, A=A, I=I)
    e24 = s.add_element(node_i=n24,node_j=n25, E=E, A=A, I=I)
    e25 = s.add_element(node_i=n25,node_j=n26, E=E, A=A, I=I)
    e26 = s.add_element(node_i=n26,node_j=n27, E=E, A=A, I=I)
    e27 = s.add_element(node_i=n27,node_j=n28, E=E, A=A, I=I)
    e28 = s.add_element(node_i=n28,node_j=n29, E=E, A=A, I=I)
    e29 = s.add_element(node_i=n29,node_j=n30, E=E, A=A, I=I)
    e30 = s.add_element(node_i=n30,node_j=n31, E=E, A=A, I=I)
    e31 = s.add_element(node_i=n31,node_j=n32, E=E, A=A, I=I)
    e32 = s.add_element(node_i=n32,node_j=n33, E=E, A=A, I=I)


    # Vertical Load on Beam 2
    s.add_dist_load(e16, qz=l_1, local=True)
    s.add_dist_load(e17, qz=l_1, local=True)
    s.add_dist_load(e18, qz=l_1, local=True)
    s.add_dist_load(e19, qz=l_1, local=True)
    s.add_dist_load(e20, qz=l_1, local=True)
    s.add_dist_load(e21, qz=l_1, local=True)
    s.add_dist_load(e22, qz=l_1, local=True)
    s.add_dist_load(e23, qz=l_1, local=True)
    s.add_dist_load(e24, qz=l_1, local=True)
    s.add_dist_load(e25, qz=l_1, local=True)
    s.add_dist_load(e26, qz=l_1, local=True)
    s.add_dist_load(e27, qz=l_1, local=True)
    s.add_dist_load(e28, qz=l_1, local=True)
    s.add_dist_load(e29, qz=l_1, local=True)
    s.add_dist_load(e30, qz=l_1, local=True)
    s.add_dist_load(e31, qz=l_1, local=True)
    s.add_dist_load(e32, qz=l_1, local=True) 


    # Wind Load on Beam 1 
    s.add_dist_load(e1, qz=l_2, local=True)
    s.add_dist_load(e2, qz=l_2, local=True)
    s.add_dist_load(e3, qz=l_2, local=True)
    s.add_dist_load(e4, qz=l_2, local=True)
    s.add_dist_load(e5, qz=l_2, local=True)
    s.add_dist_load(e6, qz=l_2, local=True)
    s.add_dist_load(e7, qz=l_2, local=True)
    s.add_dist_load(e8, qz=l_2, local=True)
    s.add_dist_load(e9, qz=l_2, local=True)
    s.add_dist_load(e10, qz=l_2, local=True)
    s.add_dist_load(e11, qz=l_2, local=True)
    s.add_dist_load(e12, qz=l_2, local=True)
    s.add_dist_load(e13, qz=l_2, local=True)
    s.add_dist_load(e14, qz=l_2, local=True)
    s.add_dist_load(e15, qz=l_2, local=True)


    solver1 = Solver1stOrder()
    solver2 = Solver2ndOrder(tol=1e-6, max_iter=50)

    res1 = solver1.solve(s)
    res2 = solver2.solve(s)

    #res1.print_summary()
    #res2.print_summary()

    M_max = res1.internal_forces(s.elements[14])["M_j"]

    return M_max


def kappa_1(l_1k, l_1d):
    numerator = (t_S(l_1=l_1d, l_2=0) - t_S(l_1=l_1k, l_2=0)) * l_1k
    denominator = (t_S(l_1=l_1k, l_2=0) - t_S(l_1=0, l_2=0)) * (l_1d-l_1k)
    return numerator / denominator


def kappa_2(l_2k, l_2d):
    numerator = (t_S(l_1=0, l_2=l_2d) - t_S(l_1=0, l_2=l_2k)) * l_2k
    denominator = (t_S(l_1=0, l_2=l_2k) - t_S(l_1=0, l_2=0)) * (l_2d-l_2k)
    return numerator / denominator

def kappa_12(l_1k, l_1d, l_2k, l_2d):
    numerator = (t_S(l_1=l_1d, l_2=l_2d) - t_S(l_1=l_1k, l_2=l_2k)) * np.sqrt(l_1k**2 + l_2k**2)
    denominator = (t_S(l_1=l_1k, l_2=l_2k) - t_S(l_1=0, l_2=0)) * np.sqrt((l_1d-l_1k)**2 + (l_2d-l_2k)**2)
    return numerator / denominator

def r1(l_1k, l_2k):
    numerator = t_S(l_1=l_1k, l_2=0) - t_S(l_1=0, l_2=0)
    denominator = t_S(l_1=l_1k, l_2=l_2k) - t_S(l_1=0, l_2=0)
    return numerator / denominator

def r2(l_1k, l_2k):
    numerator = t_S(l_1=0, l_2=l_2k) - t_S(l_1=0, l_2=0)
    denominator = t_S(l_1=l_1k, l_2=l_2k) - t_S(l_1=0, l_2=0)
    return numerator / denominator

k1 = kappa_1(l_1k=l_1k, l_1d=l_1d)
k2 = kappa_2(l_2k=l_2k, l_2d=l_2d)
k12 = kappa_12(l_1k=l_1k, l_1d=l_1d, l_2k=l_2k, l_2d=l_2d)
r1 = r1(l_1k=l_1k, l_2k=l_2k)
r2 = r2(l_1k=l_1k, l_2k=l_2k)

M_Ed = t_S(l_1=l_1d, l_2=l_2d)

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