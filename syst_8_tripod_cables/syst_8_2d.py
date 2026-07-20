from syst_8_model_function import t_S_cablenet
import numpy as np
import matplotlib.pyplot as plt

# # Validation Check
# A = 12**2 * np.pi / 4 # mm2
# x = t_S_cablenet(F_Y=-30.0 * 1e3, F_Z=-30.0 * 1e3) # input in kN
# print(f"Stress: {x} MPa") # kN
# print(f"Force: {x * A / 1000} kN") # kN




sigma_list = []

# Range für Punktlasten
Fy_range = np.linspace(0, 30 * 1e3, 20) # Load in kN
Fz_range = np.linspace(0, 30 * 1e3, 20) # Load in kN

# Fz = 30 * 1e3
# Fy = 30 * 1e3

Fz = 0
Fy = 0

#for Fy in Fy_range:
for Fz in Fz_range:
    sigma = t_S_cablenet(F_Y=-Fy, F_Z=-Fz)
    
    sigma_list.append(sigma)


    
def plot_Fy_range():
    # Speicherpfad 
#     ORDNERNAME = "frame_plots"
#     os.makedirs(ORDNERNAME, exist_ok=True)
#     DATEINAME = f"H_{H:.1f}.png" 
#     VOLLSTAENDIGER_PFAD = os.path.join(ORDNERNAME, DATEINAME)

    # Plot der ersten Linie (Th. I. O.) mit Datenpunkten
    plt.plot(Fy_range/1000, sigma_list, 
            label='N', 
            marker='.',          # Fügt Punkte hinzu
            markersize=4,       # Größe der Punkte
            color='blue',        # Farbe frei wählbar (z.B. 'red' oder 'orange')
            linestyle='-')      # Durchgehende Linie


    # Achsenbeschriftungen
    plt.xlabel('Fy in [kN]', fontsize=12)
    #plt.xlabel('v in [kN/m]', fontsize=12)
    plt.ylabel('sigma in [MPa]', fontsize=12)

    # Überschrift mit dem Wert von H hinzufügen
    #plt.title(f"H = {H} kN", fontsize=14, )
    plt.title(f"Fz = {Fz/1000} kN", fontsize=14, )

    # Grid anzeigen
    plt.grid(True, linestyle=':', alpha=0.6) # 'linestyle' macht es punktiert, 'alpha' macht es blasser

    # Legende (oben links, damit sie nicht über den Linien liegt)
    plt.legend(loc='upper left', fontsize=10)

    # Sicherstellen, dass die Achsen bei 0 beginnen
    #plt.xlim(left=0)
    #plt.ylim(bottom=-10)

    plt.tight_layout() # Verhindert, dass Titel/Achsen abgeschnitten werden

    # SPEICHERN 
    plt.savefig("./Fy_range", dpi=300) # dpi=300 sorgt für hohe Auflösung

    # Plot anzeigen
    plt.show()

def plot_Fz_range():
    # Speicherpfad 
#     ORDNERNAME = "frame_plots"
#     os.makedirs(ORDNERNAME, exist_ok=True)
#     DATEINAME = f"V_{V:.1f}.png" 
#     VOLLSTAENDIGER_PFAD = os.path.join(ORDNERNAME, DATEINAME)

    # Plot der ersten Linie (Th. I. O.) mit Datenpunkten
    plt.plot(Fz_range / 1000, sigma_list, 
            label='N', 
            marker='.',          # Fügt Punkte hinzu
            markersize=4,       # Größe der Punkte
            color='blue',        # Farbe frei wählbar (z.B. 'red' oder 'orange')
            linestyle='-')      # Durchgehende Linie

    # Achsenbeschriftungen
    #plt.xlabel('H in [kN]', fontsize=12)
    plt.xlabel('Fz in [kN]', fontsize=12)
    plt.ylabel('sigma in [MPa]', fontsize=12)

    # Überschrift mit dem Wert von H hinzufügen
    plt.title(f"Fy = {Fy/1000} kN", fontsize=14, )
    #plt.title(f"v = {v} kN/m", fontsize=14, )
    # Grid anzeigen
    plt.grid(True, linestyle=':', alpha=0.6) # 'linestyle' macht es punktiert, 'alpha' macht es blasser

    # Legende (oben links, damit sie nicht über den Linien liegt)
    plt.legend(loc='upper left', fontsize=10)

    # Sicherstellen, dass die Achsen bei 0 beginnen
    #plt.xlim(left=0)
    #plt.ylim(bottom=0)

    plt.tight_layout() # Verhindert, dass Titel/Achsen abgeschnitten werden

    # SPEICHERN 
    plt.savefig("./Fz_range", dpi=300) # dpi=300 sorgt für hohe Auflösung

    # Plot anzeigen
    plt.show()


plot_Fz_range()
#plot_Fy_range()
