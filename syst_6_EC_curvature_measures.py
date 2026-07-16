from structure import Structure
from solver_1st import Solver1stOrder 
from solver_2nd import Solver2ndOrder
from buckling_analysis import BucklingAnalysis
import numpy as np
import matplotlib.pyplot as plt
from measures_of_nonlinearity import kappa_1, kappa_2, kappa_12, r1, r2

# approximately resembles an IPE 160 
E = 210e6 # kN/m2 
A = 2.0e-3 # m2
I = 0.869e-5 # m4
h = 0.16  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * alpha # kNm


# Node 1 
x_1 = 0.0
z_1 = 0.0

# Node 2
x_2 = 0.015
z_2 = -3.0


# Outer dimensions for beam 1
delta_x_1 = x_2 - x_1
delta_z_1 = z_2 - z_1

elements_per_beam = 10


# e = 5 # load distribution length in m


# s_k = 1.1  # snow kN/m2
# q_b = 0.65 # wind pressure kN/m2
# w_k = q_b * 0.8 # wind load kN/m2 with c_pe,10 = 0.8 (Area D)



# # Naming Convention according to Max PHD 
# l_1k = s_k * e
# l_2k = w_k * e

l_1k = 200
l_2k = 3.333


# # Partial Safety Factors
# gamma_G = 1.35
# gamma_Q = 1.5
# psi_0 = 1.0 # 0.6     # Windload

# # Design Loads
# e_d_vertical = gamma_Q * l_1k                    # vertical distributed load
# e_d_horizontal = gamma_Q * psi_0 * l_2k          # horizontal distributed load

# Naming Convention according to Max PHD 
l_1d = 300 # Vertical Design load
l_2d = 5 # Horizontal Design load



# Structural Model Function
def t_S(l_1, l_2):
    s = Structure()
    # Stab 1 
    n1 = s.add_node(x=delta_x_1 * 0/elements_per_beam,z=delta_z_1 * 0/elements_per_beam, kind="frame", support={"u": True, "w": True, "phi": True})
    n2 = s.add_node(x=delta_x_1 * 1/elements_per_beam,z=delta_z_1 * 1/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})
    n3 = s.add_node(x=delta_x_1 * 2/elements_per_beam,z=delta_z_1 * 2/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})
    n4 = s.add_node(x=delta_x_1 * 3/elements_per_beam,z=delta_z_1 * 3/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})
    n5 = s.add_node(x=delta_x_1 * 4/elements_per_beam,z=delta_z_1 * 4/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})
    n6 = s.add_node(x=delta_x_1 * 5/elements_per_beam,z=delta_z_1 * 5/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})
    n7 = s.add_node(x=delta_x_1 * 6/elements_per_beam,z=delta_z_1 * 6/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})
    n8 = s.add_node(x=delta_x_1 * 7/elements_per_beam,z=delta_z_1 * 7/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})
    n9 = s.add_node(x=delta_x_1 * 8/elements_per_beam,z=delta_z_1 * 8/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})
    n10 = s.add_node(x=delta_x_1 * 9/elements_per_beam,z=delta_z_1 * 9/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})
    n11 = s.add_node(x=delta_x_1 * 10/elements_per_beam,z=delta_z_1 * 10/elements_per_beam, kind="frame", support={"u": False, "w": False, "phi": False})

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

    # # Horizontal Load on Beam 1
    # s.add_dist_load(e1, qz=h, local=True)
    # s.add_dist_load(e2, qz=h, local=True)
    # s.add_dist_load(e3, qz=h, local=True)
    # s.add_dist_load(e4, qz=h, local=True)
    # s.add_dist_load(e5, qz=h, local=True)
    # s.add_dist_load(e6, qz=h, local=True)
    # s.add_dist_load(e7, qz=h, local=True)
    # s.add_dist_load(e8, qz=h, local=True)
    # s.add_dist_load(e9, qz=h, local=True)
    # s.add_dist_load(e10, qz=h, local=True)

    # Point Load on Top
    s.add_node_load(node=n11, Fz=l_1)

    # Point Load on Top
    s.add_node_load(node=n11, Fx=l_2)

    #solver1 = Solver1stOrder()
    solver2 = Solver2ndOrder(tol=1e-6, max_iter=50)

    #res1 = solver1.solve(s)
    res2 = solver2.solve(s)

    #res1.print_summary()
    #res2.print_summary()

    M_max = abs(res2.internal_forces(s.elements[0])["M_i"])

    return M_max


k1 = kappa_1(l_1k=l_1k, l_1d=l_1d, t_S=t_S)
k2 = kappa_2(l_2k=l_2k, l_2d=l_2d, t_S=t_S)
k12 = kappa_12(l_1k=l_1k, l_1d=l_1d, l_2k=l_2k, l_2d=l_2d, t_S=t_S)
r1 = r1(l_1k=l_1k, l_2k=l_2k, t_S=t_S)
r2 = r2(l_1k=l_1k, l_2k=l_2k, t_S=t_S)

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