from structure import Structure
from solver_1st import Solver1stOrder 
from solver_2nd import Solver2ndOrder
from buckling_analysis import BucklingAnalysis
import numpy as np
import matplotlib.pyplot as plt

# approximately resembles an IPE 140 
E = 210e6 # kN/m2 
A = 1.6e-3 # m2
I = 0.54e-5 # m4
h = 0.14  # m
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

# Node 3
x_3 = 3.0
z_3 = -3.0

# Node 4
x_4 = 6.0
z_4 = -3.0

# Node 5
x_5 = 6.0
z_5 = 0.0

# Outer dimensions for beam 1
delta_x_1 = x_2 - x_1
delta_z_1 = z_2 - z_1

# Outer dimensions for beam 2
delta_x_2 = x_3 - x_2
delta_z_2 = z_3 - z_2

# Outer dimensions for beam 3
delta_x_3 = x_4 - x_3
delta_z_3 = z_4 - z_3

# Outer dimensions for beam 4
delta_x_4 = x_5 - x_4
delta_z_4 = z_5 - z_4

elements_per_beam = 10

# Loads 
v = 0
h = 10

# # Loads for test, result in equilibrium!!!
# v = 11140.597101578878
# h = 8912.477681263103

s = Structure()
# Stab 1 
n1 = s.add_node(x=delta_x_1 * 0/elements_per_beam,z=delta_z_1 * 0/elements_per_beam, kind="frame", support={"u": True, "w": True, "phi": False})
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

# Stab 2
n12 = s.add_node(x=x_2 + delta_x_2 * 1/elements_per_beam,z=z_2 + delta_z_2 * 1/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n13 = s.add_node(x=x_2 + delta_x_2 * 2/elements_per_beam,z=z_2 + delta_z_2 * 2/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n14 = s.add_node(x=x_2 + delta_x_2 * 3/elements_per_beam,z=z_2 + delta_z_2 * 3/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n15 = s.add_node(x=x_2 + delta_x_2 * 4/elements_per_beam,z=z_2 + delta_z_2 * 4/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n16 = s.add_node(x=x_2 + delta_x_2 * 5/elements_per_beam,z=z_2 + delta_z_2 * 5/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n17 = s.add_node(x=x_2 + delta_x_2 * 6/elements_per_beam,z=z_2 + delta_z_2 * 6/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n18 = s.add_node(x=x_2 + delta_x_2 * 7/elements_per_beam,z=z_2 + delta_z_2 * 7/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n19 = s.add_node(x=x_2 + delta_x_2 * 8/elements_per_beam,z=z_2 + delta_z_2 * 8/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n20 = s.add_node(x=x_2 + delta_x_2 * 9/elements_per_beam,z=z_2 + delta_z_2 * 9/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n21 = s.add_node(x=x_2 + delta_x_2 * 10/elements_per_beam,z=z_2 + delta_z_2 * 10/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})

e11 = s.add_element(node_i=n11,node_j=n12, E=E, A=A, I=I)
e12 = s.add_element(node_i=n12,node_j=n13, E=E, A=A, I=I)
e13 = s.add_element(node_i=n13,node_j=n14, E=E, A=A, I=I)
e14 = s.add_element(node_i=n14,node_j=n15, E=E, A=A, I=I)
e15 = s.add_element(node_i=n15,node_j=n16, E=E, A=A, I=I)
e16 = s.add_element(node_i=n16,node_j=n17, E=E, A=A, I=I)
e17 = s.add_element(node_i=n17,node_j=n18, E=E, A=A, I=I)
e18 = s.add_element(node_i=n18,node_j=n19, E=E, A=A, I=I)
e19 = s.add_element(node_i=n19,node_j=n20, E=E, A=A, I=I)
e20 = s.add_element(node_i=n20,node_j=n21, E=E, A=A, I=I)

# Stab 3
n22 = s.add_node(x=x_3 + delta_x_3 * 1/elements_per_beam,z=z_3 + delta_z_3 * 1/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n23 = s.add_node(x=x_3 + delta_x_3 * 2/elements_per_beam,z=z_3 + delta_z_3 * 2/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n24 = s.add_node(x=x_3 + delta_x_3 * 3/elements_per_beam,z=z_3 + delta_z_3 * 3/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n25 = s.add_node(x=x_3 + delta_x_3 * 4/elements_per_beam,z=z_3 + delta_z_3 * 4/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n26 = s.add_node(x=x_3 + delta_x_3 * 5/elements_per_beam,z=z_3 + delta_z_3 * 5/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n27 = s.add_node(x=x_3 + delta_x_3 * 6/elements_per_beam,z=z_3 + delta_z_3 * 6/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n28 = s.add_node(x=x_3 + delta_x_3 * 7/elements_per_beam,z=z_3 + delta_z_3 * 7/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n29 = s.add_node(x=x_3 + delta_x_3 * 8/elements_per_beam,z=z_3 + delta_z_3 * 8/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n30 = s.add_node(x=x_3 + delta_x_3 * 9/elements_per_beam,z=z_3 + delta_z_3 * 9/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n31 = s.add_node(x=x_3 + delta_x_3 * 10/elements_per_beam,z=z_3 + delta_z_3 * 10/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})

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

# Stab 4
n32 = s.add_node(x=x_4 + delta_x_4 * 1/elements_per_beam,z=z_4 + delta_z_4 * 1/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n33 = s.add_node(x=x_4 + delta_x_4 * 2/elements_per_beam,z=z_4 + delta_z_4 * 2/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n34 = s.add_node(x=x_4 + delta_x_4 * 3/elements_per_beam,z=z_4 + delta_z_4 * 3/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n35 = s.add_node(x=x_4 + delta_x_4 * 4/elements_per_beam,z=z_4 + delta_z_4 * 4/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n36 = s.add_node(x=x_4 + delta_x_4 * 5/elements_per_beam,z=z_4 + delta_z_4 * 5/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n37 = s.add_node(x=x_4 + delta_x_4 * 6/elements_per_beam,z=z_4 + delta_z_4 * 6/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n38 = s.add_node(x=x_4 + delta_x_4 * 7/elements_per_beam,z=z_4 + delta_z_4 * 7/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n39 = s.add_node(x=x_4 + delta_x_4 * 8/elements_per_beam,z=z_4 + delta_z_4 * 8/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n40 = s.add_node(x=x_4 + delta_x_4 * 9/elements_per_beam,z=z_4 + delta_z_4 * 9/elements_per_beam,kind="frame", support={"u": False, "w": False, "phi": False})
n41 = s.add_node(x=x_4 + delta_x_4 * 10/elements_per_beam,z=z_4 + delta_z_4 * 10/elements_per_beam,kind="frame", support={"u": True, "w": True, "phi": False})

e31 = s.add_element(node_i=n31,node_j=n32, E=E, A=A, I=I)
e32 = s.add_element(node_i=n32,node_j=n33, E=E, A=A, I=I)
e33 = s.add_element(node_i=n33,node_j=n34, E=E, A=A, I=I)
e34 = s.add_element(node_i=n34,node_j=n35, E=E, A=A, I=I)
e35 = s.add_element(node_i=n35,node_j=n36, E=E, A=A, I=I)
e36 = s.add_element(node_i=n36,node_j=n37, E=E, A=A, I=I)
e37 = s.add_element(node_i=n37,node_j=n38, E=E, A=A, I=I)
e38 = s.add_element(node_i=n38,node_j=n39, E=E, A=A, I=I)
e39 = s.add_element(node_i=n39,node_j=n40, E=E, A=A, I=I)
e40 = s.add_element(node_i=n40,node_j=n41, E=E, A=A, I=I)


# Horizontal Load on Beam 1
s.add_dist_load(e1, qz=h, local=True)
s.add_dist_load(e2, qz=h, local=True)
s.add_dist_load(e3, qz=h, local=True)
s.add_dist_load(e4, qz=h, local=True)
s.add_dist_load(e5, qz=h, local=True)
s.add_dist_load(e6, qz=h, local=True)
s.add_dist_load(e7, qz=h, local=True)
s.add_dist_load(e8, qz=h, local=True)
s.add_dist_load(e9, qz=h, local=True)
s.add_dist_load(e10, qz=h, local=True)


# Vertical Load on Beam 2
s.add_dist_load(e11, qz=v, local=True)
s.add_dist_load(e12, qz=v, local=True)
s.add_dist_load(e13, qz=v, local=True)
s.add_dist_load(e14, qz=v, local=True)
s.add_dist_load(e15, qz=v, local=True)
s.add_dist_load(e16, qz=v, local=True)
s.add_dist_load(e17, qz=v, local=True)
s.add_dist_load(e18, qz=v, local=True)
s.add_dist_load(e19, qz=v, local=True)
s.add_dist_load(e20, qz=v, local=True)

# Vertical Load on Beam 3
s.add_dist_load(e21, qz=v, local=True)
s.add_dist_load(e22, qz=v, local=True)
s.add_dist_load(e23, qz=v, local=True)
s.add_dist_load(e24, qz=v, local=True)
s.add_dist_load(e25, qz=v, local=True)
s.add_dist_load(e26, qz=v, local=True)
s.add_dist_load(e27, qz=v, local=True)
s.add_dist_load(e28, qz=v, local=True)
s.add_dist_load(e29, qz=v, local=True)
s.add_dist_load(e30, qz=v, local=True)

# Horizontal Load on Beam 4
s.add_dist_load(e31, qz=-h, local=True)
s.add_dist_load(e32, qz=-h, local=True)
s.add_dist_load(e33, qz=-h, local=True)
s.add_dist_load(e34, qz=-h, local=True)
s.add_dist_load(e35, qz=-h, local=True)
s.add_dist_load(e36, qz=-h, local=True)
s.add_dist_load(e37, qz=-h, local=True)
s.add_dist_load(e38, qz=-h, local=True)
s.add_dist_load(e39, qz=-h, local=True)
s.add_dist_load(e40, qz=-h, local=True)


solver1 = Solver1stOrder()
#solver2 = Solver2ndOrder(tol=1e-6, max_iter=50)

res1 = solver1.solve(s)
#res2 = solver2.solve(s)

res1.print_summary()
#res2.print_summary()

M_max = res1.internal_forces(s.elements[29])["M_j"]
print(M_max)

# # Stabilitätsanalyse
# buckling = BucklingAnalysis(n_modes=3)
# result   = buckling.solve(s)

# # Ausgabe
# buckling.print_summary(result, s)

