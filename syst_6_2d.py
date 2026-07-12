from structure import Structure
from solver_1st import Solver1stOrder 
from solver_2nd import Solver2ndOrder
import numpy as np
import matplotlib.pyplot as plt
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
x_2 = 3.0
z_2 = 0.0


# Outer dimensions for beam 1
delta_x_1 = x_2 - x_1
delta_z_1 = z_2 - z_1

elements_per_beam = 10

M_Th1_list = []
M_Th2_list = []

# Range für Linienlasten über beide Elemente
V_range = np.linspace(0, 300, 20)
H_range = np.linspace(0, 5, 20)

v = 300
h = 5

# TH1 LOOP
for h in H_range:
#for v in V_range:
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
    
    # Point Load on Beam 2
    s.add_node_load(node=n11, Fx=-v)

    
    solver1 = Solver1stOrder()
    # solver2 = Solver2ndOrder(tol=1e-6, max_iter=60)
    
    res1 = solver1.solve(s)
    # res2 = solver2.solve(s)
    
    # Verschiebungen im Eck
    print(f"Displacements TH1: {res1.displacements(s.nodes[10])}")
    # print(f"Displacements TH2: {res2.displacements(s.nodes[5])}")
    
    # Moment am Endknoten M_j
    M_j_Th1 = res1.internal_forces(s.elements[0])["M_i"] 
    # M_j_Th2 = res2.internal_forces(s.elements[4])["M_i"]
    
    M_Th1_list.append(abs(M_j_Th1))
    # M_Th2_list.append(M_j_Th2)

# TH2 LOOP
for h in H_range:
#for v in V_range:
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
    
    # Point Load on Beam 2
    s.add_node_load(node=n11, Fx=-v)
    
    # solver1 = Solver1stOrder()
    solver2 = Solver2ndOrder(tol=1e-6, max_iter=60)
    
    # res1 = solver1.solve(s)
    res2 = solver2.solve(s)
    
    # Verschiebungen im Eck
    # print(f"Displacements TH1: {res1.displacements(s.nodes[5])}")
    print(f"Displacements TH2: {res2.displacements(s.nodes[10])}")
    
    # Moment am Endknoten M_j
    # M_j_Th1 = res1.internal_forces(s.elements[4])["M_i"] 
    M_j_Th2 = res2.internal_forces(s.elements[0])["M_i"]
    
    # M_Th1_list.append(M_j_Th1)
    M_Th2_list.append(abs(M_j_Th2))


def plot_V_range():
    # Speicherpfad 
#     ORDNERNAME = "frame_plots"
#     os.makedirs(ORDNERNAME, exist_ok=True)
#     DATEINAME = f"H_{H:.1f}.png" 
#     VOLLSTAENDIGER_PFAD = os.path.join(ORDNERNAME, DATEINAME)

    # Plot der ersten Linie (Th. I. O.) mit Datenpunkten
    plt.plot(V_range, M_Th1_list, 
            label='M Th.I.O.', 
            marker='.',          # Fügt Punkte hinzu
            markersize=4,       # Größe der Punkte
            color='blue',        # Farbe frei wählbar (z.B. 'red' oder 'orange')
            linestyle='-')      # Durchgehende Linie

    # Plot der zweiten Linie (Th. II. O.) in einer anderen Farbe
    plt.plot(V_range, M_Th2_list, 
            label='M Th.II.O.', 
            marker='.',          # Fügt Punkte hinzu
            markersize=4,       # Größe der Punkte
            color='red',        # Farbe frei wählbar (z.B. 'red' oder 'orange')
            linestyle='-')     # Gestrichelte Linie zur besseren Unterscheidung

    # Die horizontale Grenzwert-Linie (M_yield) 
    plt.axhline(y=M_yield,        
                label='M_yield',  # Label für die Legende
                color='orange',      # Wie gewünscht rot
                linestyle='-.',   # Punkt-Strich für bessere Abgrenzung
                linewidth=2)      # Etwas dicker, damit sie auffällt

    # Achsenbeschriftungen
    plt.xlabel('V in [kN]', fontsize=12)
    #plt.xlabel('v in [kN/m]', fontsize=12)
    plt.ylabel('M in [kNm]', fontsize=12)

    # Überschrift mit dem Wert von H hinzufügen
    #plt.title(f"H = {H} kN", fontsize=14, )
    plt.title(f"h = {h} kN/m", fontsize=14, )

    # Grid anzeigen
    plt.grid(True, linestyle=':', alpha=0.6) # 'linestyle' macht es punktiert, 'alpha' macht es blasser

    # Legende (oben links, damit sie nicht über den Linien liegt)
    plt.legend(loc='upper left', fontsize=10)

    # Sicherstellen, dass die Achsen bei 0 beginnen
    plt.xlim(left=0)
    #plt.ylim(bottom=-10)

    plt.tight_layout() # Verhindert, dass Titel/Achsen abgeschnitten werden

    # SPEICHERN 
    #plt.savefig(VOLLSTAENDIGER_PFAD, dpi=300) # dpi=300 sorgt für hohe Auflösung

    # Plot anzeigen
    plt.show()

def plot_H_range():
    # Speicherpfad 
#     ORDNERNAME = "frame_plots"
#     os.makedirs(ORDNERNAME, exist_ok=True)
#     DATEINAME = f"V_{V:.1f}.png" 
#     VOLLSTAENDIGER_PFAD = os.path.join(ORDNERNAME, DATEINAME)

    # Plot der ersten Linie (Th. I. O.) mit Datenpunkten
    plt.plot(H_range, M_Th1_list, 
            label='M Th.I.O.', 
            marker='.',          # Fügt Punkte hinzu
            markersize=4,       # Größe der Punkte
            color='blue',        # Farbe frei wählbar (z.B. 'red' oder 'orange')
            linestyle='-')      # Durchgehende Linie

    # Plot der zweiten Linie (Th. II. O.) in einer anderen Farbe
    plt.plot(H_range, M_Th2_list, 
            label='M Th.II.O.', 
            marker='.',          # Fügt Punkte hinzu
            markersize=4,       # Größe der Punkte
            color='red',        # Farbe frei wählbar (z.B. 'red' oder 'orange')
            linestyle='-')     # Gestrichelte Linie zur besseren Unterscheidung

    # Die horizontale Grenzwert-Linie (M_yield) 
    plt.axhline(y=M_yield,        
                label='M_yield',  # Label für die Legende
                color='orange',      # Wie gewünscht rot
                linestyle='-.',   # Punkt-Strich für bessere Abgrenzung
                linewidth=2)      # Etwas dicker, damit sie auffällt

    # Achsenbeschriftungen
    #plt.xlabel('H in [kN]', fontsize=12)
    plt.xlabel('h in [kN/m]', fontsize=12)
    plt.ylabel('M in [kNm]', fontsize=12)

    # Überschrift mit dem Wert von H hinzufügen
    plt.title(f"V = {v} kN", fontsize=14, )
    #plt.title(f"v = {v} kN/m", fontsize=14, )
    # Grid anzeigen
    plt.grid(True, linestyle=':', alpha=0.6) # 'linestyle' macht es punktiert, 'alpha' macht es blasser

    # Legende (oben links, damit sie nicht über den Linien liegt)
    plt.legend(loc='upper left', fontsize=10)

    # Sicherstellen, dass die Achsen bei 0 beginnen
    plt.xlim(left=0)
    plt.ylim(bottom=0)

    plt.tight_layout() # Verhindert, dass Titel/Achsen abgeschnitten werden

    # SPEICHERN 
    #plt.savefig(VOLLSTAENDIGER_PFAD, dpi=300) # dpi=300 sorgt für hohe Auflösung

    # Plot anzeigen
    plt.show()


#plot_V_range()
plot_H_range()
