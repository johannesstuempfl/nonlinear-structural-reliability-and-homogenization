from structure import Structure
from solver_1st import Solver1stOrder 
from solver_2nd import Solver2ndOrder
import numpy as np
import matplotlib.pyplot as plt

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


l_1d = 8.25
l_2d = 3.9

V_range = np.linspace(0, l_1d * 1.0, 20)
H_range = np.linspace(0, l_2d * 1.0, 20)

# Create meshgrid for 3D plotting
V_mesh, H_mesh = np.meshgrid(V_range, H_range)
M_Th1_mesh = np.zeros_like(V_mesh)
M_Th2_mesh = np.zeros_like(V_mesh)


for i in range(len(V_range)):
        for j in range(len(H_range)):
            V_val = V_mesh[i, j]
            H_val = H_mesh[i, j]
            
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
            s.add_dist_load(e16, qz=V_val, local=True)
            s.add_dist_load(e17, qz=V_val, local=True)
            s.add_dist_load(e18, qz=V_val, local=True)
            s.add_dist_load(e19, qz=V_val, local=True)
            s.add_dist_load(e20, qz=V_val, local=True)
            s.add_dist_load(e21, qz=V_val, local=True)
            s.add_dist_load(e22, qz=V_val, local=True)
            s.add_dist_load(e23, qz=V_val, local=True)
            s.add_dist_load(e24, qz=V_val, local=True)
            s.add_dist_load(e25, qz=V_val, local=True)
            s.add_dist_load(e26, qz=V_val, local=True)
            s.add_dist_load(e27, qz=V_val, local=True)
            s.add_dist_load(e28, qz=V_val, local=True)
            s.add_dist_load(e29, qz=V_val, local=True)
            s.add_dist_load(e30, qz=V_val, local=True)
            s.add_dist_load(e31, qz=V_val, local=True)
            s.add_dist_load(e32, qz=V_val, local=True)

            # Wind Load on Beam 1 
            s.add_dist_load(e1, qz=H_val, local=True)
            s.add_dist_load(e2, qz=H_val, local=True)
            s.add_dist_load(e3, qz=H_val, local=True)
            s.add_dist_load(e4, qz=H_val, local=True)
            s.add_dist_load(e5, qz=H_val, local=True)
            s.add_dist_load(e6, qz=H_val, local=True)
            s.add_dist_load(e7, qz=H_val, local=True)
            s.add_dist_load(e8, qz=H_val, local=True)
            s.add_dist_load(e9, qz=H_val, local=True)
            s.add_dist_load(e10, qz=H_val, local=True)
            s.add_dist_load(e11, qz=H_val, local=True)
            s.add_dist_load(e12, qz=H_val, local=True)
            s.add_dist_load(e13, qz=H_val, local=True)
            s.add_dist_load(e14, qz=H_val, local=True)
            s.add_dist_load(e15, qz=H_val, local=True)
            
            solver1 = Solver1stOrder()
            # solver2 = Solver2ndOrder(tol=1e-6, max_iter=50)
            
            print("="*50)
            # print(f"Next Load Step: v = {V_val}, h = {H_val}")
            
            res1 = solver1.solve(s)
            # res2 = solver2.solve(s)
            
            # Verschiebungen im Eck
            print(f"Displacements TH1: {res1.displacements(s.nodes[15])}")
            # print(f"Displacements TH2: {res2.displacements(s.nodes[15])}")
            
            # Moment am Endknoten M_j 
            M_j_Th1 = res1.internal_forces(s.elements[14])["M_j"] 
            # M_j_Th2 = res2.internal_forces(s.elements[14])["M_j"]
            
            print(f"Moment TH1: {M_j_Th1} kNm")
            # print(f"Moment TH2: {M_j_Th2} kNm")
            
            M_Th1_mesh[i, j] = M_j_Th1
            # M_Th2_mesh[i, j] = M_j_Th2

for i in range(len(V_range)):
        for j in range(len(H_range)):
            V_val = V_mesh[i, j]
            H_val = H_mesh[i, j]
            
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
            s.add_dist_load(e16, qz=V_val, local=True)
            s.add_dist_load(e17, qz=V_val, local=True)
            s.add_dist_load(e18, qz=V_val, local=True)
            s.add_dist_load(e19, qz=V_val, local=True)
            s.add_dist_load(e20, qz=V_val, local=True)
            s.add_dist_load(e21, qz=V_val, local=True)
            s.add_dist_load(e22, qz=V_val, local=True)
            s.add_dist_load(e23, qz=V_val, local=True)
            s.add_dist_load(e24, qz=V_val, local=True)
            s.add_dist_load(e25, qz=V_val, local=True)
            s.add_dist_load(e26, qz=V_val, local=True)
            s.add_dist_load(e27, qz=V_val, local=True)
            s.add_dist_load(e28, qz=V_val, local=True)
            s.add_dist_load(e29, qz=V_val, local=True)
            s.add_dist_load(e30, qz=V_val, local=True)
            s.add_dist_load(e31, qz=V_val, local=True)
            s.add_dist_load(e32, qz=V_val, local=True)

            # Wind Load on Beam 1 
            s.add_dist_load(e1, qz=H_val, local=True)
            s.add_dist_load(e2, qz=H_val, local=True)
            s.add_dist_load(e3, qz=H_val, local=True)
            s.add_dist_load(e4, qz=H_val, local=True)
            s.add_dist_load(e5, qz=H_val, local=True)
            s.add_dist_load(e6, qz=H_val, local=True)
            s.add_dist_load(e7, qz=H_val, local=True)
            s.add_dist_load(e8, qz=H_val, local=True)
            s.add_dist_load(e9, qz=H_val, local=True)
            s.add_dist_load(e10, qz=H_val, local=True)
            s.add_dist_load(e11, qz=H_val, local=True)
            s.add_dist_load(e12, qz=H_val, local=True)
            s.add_dist_load(e13, qz=H_val, local=True)
            s.add_dist_load(e14, qz=H_val, local=True)
            s.add_dist_load(e15, qz=H_val, local=True)
            
            # solver1 = Solver1stOrder()
            solver2 = Solver2ndOrder(tol=1e-6, max_iter=50)
            
            print("="*50)
            print(f"Next Load Step: v = {V_val}, h = {H_val}")
            
            # res1 = solver1.solve(s)
            res2 = solver2.solve(s)
            
            # Verschiebungen im Eck
            # print(f"Displacements TH1: {res1.displacements(s.nodes[15])}")
            print(f"Displacements TH2: {res2.displacements(s.nodes[15])}")
            
            # Moment am Endknoten M_j 
            # M_j_Th1 = res1.internal_forces(s.elements[14])["M_j"] 
            M_j_Th2 = res2.internal_forces(s.elements[14])["M_j"]
            
            # print(f"Moment TH1: {M_j_Th1} kNm")
            print(f"Moment TH2: {M_j_Th2} kNm")
            
            # M_Th1_mesh[i, j] = M_j_Th1
            M_Th2_mesh[i, j] = M_j_Th2

# =========================================================================================================

# plt.rcParams.update({
#     "mathtext.fontset": "cm",
#     "font.family": "cmr10",
#     "axes.unicode_minus": False,
#     "font.size": 14,
# })
 
# TITLE_FONTSIZE = 18   # <-- bump this to make all headings bigger/smaller
 
# # --- FIGURE 1: 3D Surface & Contour (Updated) ---
# fig1 = plt.figure(figsize=(16, 7))
 
# # Subplot 1: 3D surface with BOTH M_Th1 and M_Th2
# ax1 = fig1.add_subplot(121, projection='3d')
 
# # # Plotting Theory 1 Surface
# #surf1 = ax1.plot_surface(V_mesh, H_mesh, M_Th1_mesh, cmap='plasma',
# #                          edgecolor='none', alpha=0.5, label='Th. 1')
 
# # Plotting Theory 2 Surface
# surf2 = ax1.plot_surface(V_mesh, H_mesh, M_Th2_mesh, cmap='viridis',
#                          edgecolor='none', alpha=0.7, label='TH2')
 
# ax1.set_xlabel(r'Vertical Force $l_{1}$ $[\mathrm{kN/m}]$')
# ax1.set_ylabel(r'Horizontal Force $l_{2}$ $[\mathrm{kN/m}]$')
# ax1.set_zlabel(r'Internal Moment $M$ $[\mathrm{kNm}]$')
# ax1.set_title(r'$M$ as function of $l_{1}$ and $H$', fontsize=TITLE_FONTSIZE, fontweight='bold')
# ax1.view_init(elev=25, azim=225)
 
# # Subplot 2: Contour plot (keeping your existing logic)
# ax2 = fig1.add_subplot(122)
# contour = ax2.contourf(V_mesh, H_mesh, M_Th2_mesh, levels=20, cmap='viridis')
# ax2.set_xlabel(r'Vertical Force $l_{1}$ $[\mathrm{kN/m}]$')
# ax2.set_ylabel(r'Horizontal Force $l_{2}$ $[\mathrm{kN/m}]$')
# ax2.set_title(r'Internal Moment $M$ - Contour Plot', fontsize=TITLE_FONTSIZE, fontweight='bold')
# fig1.colorbar(contour, ax=ax2, label=r'$M$ $[\mathrm{kNm}]$')
 
# plt.tight_layout()
 
# # --- FIGURE 2: Extra Pictures (2D Projections) ---
# fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))
 
# # Picture 1: V vs M (Looking "sideways" at the 3D plot)
# # We plot multiple lines for different H values to show the trend
# for i in range(0, len(H_range), 4): # Plot every 4th H-level for clarity
#     ax3.plot(V_range, M_Th2_mesh[i, :], label=fr'$l_{2} = {H_range[i]:.1f}\ \mathrm{{kN/m}}$')
 
# ax3.set_xlabel(r'Vertical Force $l_{1}$ $[\mathrm{kN/m}]$')
# ax3.set_ylabel(r'Internal Moment $M$ $[\mathrm{kNm}]$')
# ax3.set_title(r'$M$ as function of $l_{1}$ (Various $l_{2}$)', fontsize=TITLE_FONTSIZE, fontweight='bold')
# ax3.grid(True, linestyle='--', alpha=0.6)
# ax3.legend(fontsize='small')
 
# # Picture 2: H vs M (Looking "front-on" at the 3D plot)
# # We plot multiple lines for different V values
# for i in range(0, len(V_range), 4): # Plot every 4th V-level
#     ax4.plot(H_range, M_Th2_mesh[:, i], label=fr'$l_{1} = {V_range[i]:.1f}\ \mathrm{{kN/m}}$')
 
# ax4.set_xlabel(r'Horizontal Force $l_{2}$ $[\mathrm{kN/m}]$')
# ax4.set_ylabel(r'Internal Moment $M$ $[\mathrm{kNm}]$')
# ax4.set_title(r'$M$ as function of $l_{2}$ (Various $l_{1}$)', fontsize=TITLE_FONTSIZE, fontweight='bold')
# ax4.grid(True, linestyle='--', alpha=0.6)
# ax4.legend(fontsize='small')
 
# plt.tight_layout()
# plt.show()


plt.rcParams.update({
    "mathtext.fontset": "cm",
    "font.family": "cmr10",
    "axes.unicode_minus": False,
    "font.size": 14,
})

TITLE_FONTSIZE = 18   # <-- bump this to make all headings bigger/smaller

# --- FIGURE 1: 3D Surface & Contour (Updated) ---
fig1 = plt.figure(figsize=(16, 7))

# Subplot 1: 3D surface with BOTH M_Th1 and M_Th2
ax1 = fig1.add_subplot(121, projection='3d')

# # Plotting Theory 1 Surface
#surf1 = ax1.plot_surface(V_mesh, H_mesh, M_Th1_mesh, cmap='plasma',
#                          edgecolor='none', alpha=0.5, label='Th. 1')

# Plotting Theory 2 Surface
surf2 = ax1.plot_surface(V_mesh, H_mesh, M_Th2_mesh, cmap='viridis',
                         edgecolor='none', alpha=0.7, label='TH2')

ax1.set_xlabel(r'Vertical Force $l_{1}$ $[\mathrm{kN/m}]$')
ax1.set_ylabel(r'Horizontal Force $l_{2}$ $[\mathrm{kN/m}]$')
ax1.set_zlabel(r'Internal Moment $M$ $[\mathrm{kNm}]$')
ax1.set_title(r'$M$ as function of $l_{1}$ and $H$', fontsize=TITLE_FONTSIZE, fontweight='bold')
ax1.view_init(elev=25, azim=225)

# Subplot 2: Contour plot (keeping your existing logic)
ax2 = fig1.add_subplot(122)
contour = ax2.contourf(V_mesh, H_mesh, M_Th2_mesh, levels=20, cmap='viridis')
ax2.set_xlabel(r'Vertical Force $l_{1}$ $[\mathrm{kN/m}]$')
ax2.set_ylabel(r'Horizontal Force $l_{2}$ $[\mathrm{kN/m}]$')
ax2.set_title(r'Internal Moment $M$ - Contour Plot', fontsize=TITLE_FONTSIZE, fontweight='bold')
fig1.colorbar(contour, ax=ax2, label=r'$M$ $[\mathrm{kNm}]$')

plt.tight_layout()
fig1.savefig('./plots/fig1_surface_contour.png', dpi=220, bbox_inches='tight', facecolor='white')
fig1.savefig('./plots/fig1_surface_contour.svg', bbox_inches='tight', facecolor='white')

# --- FIGURE 2: Extra Pictures (2D Projections) ---
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))

# Picture 1: V vs M (Looking "sideways" at the 3D plot)
# We plot multiple lines for different H values to show the trend
for i in range(0, len(H_range), 4): # Plot every 4th H-level for clarity
    ax3.plot(V_range, M_Th2_mesh[i, :], label=fr'$l_{2} = {H_range[i]:.1f}\ \mathrm{{kN/m}}$')

ax3.set_xlabel(r'Vertical Force $l_{1}$ $[\mathrm{kN/m}]$')
ax3.set_ylabel(r'Internal Moment $M$ $[\mathrm{kNm}]$')
ax3.set_title(r'$M$ as function of $l_{1}$ (Various $l_{2}$)', fontsize=TITLE_FONTSIZE, fontweight='bold')
ax3.grid(True, linestyle='--', alpha=0.6)
ax3.legend(fontsize='small', loc='upper left')

# Picture 2: H vs M (Looking "front-on" at the 3D plot)
# We plot multiple lines for different V values
for i in range(0, len(V_range), 4): # Plot every 4th V-level
    ax4.plot(H_range, M_Th2_mesh[:, i], label=fr'$l_{1} = {V_range[i]:.1f}\ \mathrm{{kN/m}}$')

ax4.set_xlabel(r'Horizontal Force $l_{2}$ $[\mathrm{kN/m}]$')
ax4.set_ylabel(r'Internal Moment $M$ $[\mathrm{kNm}]$')
ax4.set_title(r'$M$ as function of $l_{2}$ (Various $l_{1}$)', fontsize=TITLE_FONTSIZE, fontweight='bold')
ax4.grid(True, linestyle='--', alpha=0.6)
ax4.legend(fontsize='small', loc='upper left')

plt.tight_layout()

fig2.savefig('./plots/fig2_projections.png', dpi=220, bbox_inches='tight', facecolor='white')
fig2.savefig('./plots/fig2_projections.svg', bbox_inches='tight', facecolor='white')
