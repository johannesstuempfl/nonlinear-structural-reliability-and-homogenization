from structure import Structure
from solver_1st import Solver1stOrder 
from solver_2nd import Solver2ndOrder
import numpy as np
import matplotlib.pyplot as plt
from buckling_analysis import BucklingAnalysis
from pprint import pprint

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
x_2 = 0.0
z_2 = -3.0


# Outer dimensions for beam 1
delta_x_1 = x_2 - x_1
delta_z_1 = z_2 - z_1

elements_per_beam = 10

M_Th1_list = []
M_Th2_list = []

v = 300
h = 5

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
s.add_node_load(node=n11, Fz=v)

# Point Load on Top
s.add_node_load(node=n11, Fx=h)
#s.add_node_load(node=n11, M=h)



solver1 = Solver1stOrder()
#solver2 = Solver2ndOrder(tol=1e-6, max_iter=50)

res1 = solver1.solve(s)
#res2 = solver2.solve(s)

res1.print_summary()
#res2.print_summary()

M_max = res1.internal_forces(s.elements[0])["M_i"]
print(M_max)

# # Stabilitätsanalyse
# buckling = BucklingAnalysis(n_modes=3)
# result   = buckling.solve(s)

# # Ausgabe
# buckling.print_summary(result, s)