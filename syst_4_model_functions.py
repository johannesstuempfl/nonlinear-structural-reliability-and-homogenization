from structure import Structure
from solver_1st import Solver1stOrder 
from solver_2nd import Solver2ndOrder
from buckling_analysis import BucklingAnalysis
import numpy as np
import matplotlib.pyplot as plt

# # NEW modified IPE 120 -> eta = 100% for Th.I.O.
# E = 210e6 # kN/m2 
# A = 1.321e-3 # m2
# I = 0.2740555e-5 # m4
# h = 0.12  # m
# z = h/2  # m
# sigma_yield = 35.5 # kN/cm2 
# alpha = 1.14
# M_yield = I/z * sigma_yield * 100e2 * 1.14 # kNm

# approximately resembles an IPE 120
E = 210e6 # kN/m2 
A = 1.321e-3 # m2
I = 0.318e-5 # m4
h = 0.12  # m
z = h/2  # m
sigma_yield = 35.5 # kN/cm2 
alpha = 1.14
M_yield = I/z * sigma_yield * 100e2 * alpha # kNm



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

# Load Distribution Length (Lasteinzugsbreite)
e = 5 # m

# Wind Last Beiwert (Bereich D)
c_pe = 0.8 


def t_S_linear(l_1, l_2, e=e, c_pe=c_pe):
    """
    DEPRECATED !!
    l_1 = vertical load in kN/m2
    l_2 = horizontal load in kN/m2
    e = Load Distribution Length (Lasteinzugsbreite)
    """
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

    # Surface Load (kN/m2) -> Line Load (kN/m)
    l_1 *= e
    l_2 *= (e * c_pe)
    
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
    #solver2 = Solver2ndOrder(tol=1e-6, max_iter=60)

    # print(f"l_1 = {l_1}")
    # print(f"l_2 = {l_2}")
    res1 = solver1.solve(s)
    #res2 = solver2.solve(s)

    #res1.print_summary()
    #res2.print_summary()

    M_max = res1.internal_forces(s.elements[14])["M_j"]

    return M_max


def t_S_hyperplane_linear(l_1, l_2) -> float:
    """
    This is the linear hyperplane function for the cablenet structure. 
    It is constructed as follows: 
    First, the plane is defined trough the three points: p1, p2, p3 which correspond to t_S(0,0), t_S(l1k,0), t_S(0,l2k). 
    Then, t_S(0,0) is subtracted.
    """
    
    # Here are the results of the nonlinear model. They serve for calibrating this linear hyperplane.
    l1k = 1.1                       # kN/m2
    l2k = 0.65                      # kN/m2
    t_S_l1k_0 = 1.442207357172265   # kNm
    t_S_0_l2k = 11.020249560912257  # kNm
    t_S_0_0 = 0.0           # kNm
    
    
    # Constructing the array representation of the three points, which define the plane
    p1 = np.array([0, 0 , t_S_0_0])
    p2 = np.array([l1k, 0 , t_S_l1k_0])
    p3 = np.array([0, l2k , t_S_0_l2k])
    
    # Form the edge vectors 
    v1 = p2 - p1 
    v2 = p3 - p1
    
    # Normal Vector via cross product 
    n = np.cross(v1, v2)
    
    # Expanding with n = (a,b,c) and d = n * p1
    a, b, c = n
    d = n @ p1
    
    # Getting the slopes m1 and m2 in l1 and l2 direction as well as the z-intercept z0
    m1 = -a/c
    m2 = -b/c
    z0 = d/c
    
    # Hyperplane function
    z = m1 * l_1 + m2 * l_2 + z0 - t_S_0_0
    
    return z 


def t_S_nonlinear(l_1, l_2, e=e, c_pe=c_pe): 
    """
    l_1 = vertical load in kN/m2
    l_2 = horizontal load in kN/m2
    e = Load Distribution Length (Lasteinzugsbreite)
    """
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

    # Surface Load (kN/m2) -> Line Load (kN/m)
    l_1 *= e
    l_2 *= (e * c_pe)

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


    #solver1 = Solver1stOrder()
    solver2 = Solver2ndOrder(tol=1e-6, max_iter=60)

    # print(f"l_1 = {l_1}")
    # print(f"l_2 = {l_2}")
    #res1 = solver1.solve(s)
    res2 = solver2.solve(s)

    #res1.print_summary()
    #res2.print_summary()

    M_max = res2.internal_forces(s.elements[14])["M_j"]

    return M_max


# # Verification of t_S_hyperplane_linear
# print(t_S_hyperplane_linear(l_1=1.1, l_2=0.0)) # should give 1.442
# print(t_S_hyperplane_linear(l_1=0.0, l_2=0.65)) # should give 11.020