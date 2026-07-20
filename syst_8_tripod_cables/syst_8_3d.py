from syst_8_model_functions import t_S_cablenet_nonlinear, t_S_cablenet_linear
import numpy as np
import matplotlib.pyplot as plt


sigma_list = []

# Range für Punktlasten
Fy_range = np.linspace(0, 30 * 1e3, 20) # Load in kN
Fz_range = np.linspace(0, 30 * 1e3, 20) # Load in kN

# Fz = 30 * 1e3
# Fy = 30 * 1e3

Fz = 0
Fy = 0

# Create meshgrid for 3D plotting
Fy_mesh, Fz_mesh = np.meshgrid(Fy_range, Fz_range)
sigma_mesh = np.zeros_like(Fy_mesh)


for i in range(len(Fy_range)):
        for j in range(len(Fz_range)):
            Fy_val = Fy_mesh[i, j]
            Fz_val = Fz_mesh[i, j]
            
            sigma = t_S_cablenet_nonlinear(-Fy_val, -Fz_val)
            
            sigma_mesh[i, j] = sigma
            


# --- FIGURE 1: 3D Surface & Contour (Updated) ---
fig1 = plt.figure(figsize=(16, 7))

# Subplot 1: 3D surface with BOTH M_Th1 and M_Th2
ax1 = fig1.add_subplot(121, projection='3d')


# Plotting Theory 3 Surface
surf2 = ax1.plot_surface(Fy_mesh, Fz_mesh, sigma_mesh, cmap='viridis', 
                         edgecolor='none', alpha=0.7, label='sigma')

ax1.set_xlabel('Fz [kN]')
ax1.set_ylabel('Fy [kN]')
ax1.set_zlabel('sigma [MPa]')
ax1.set_title('sigma as function of Fz and Fy', fontsize=12, fontweight='bold')
ax1.view_init(elev=15, azim=210)

# Subplot 2: Contour plot (keeping your existing logic)
ax2 = fig1.add_subplot(122)
contour = ax2.contourf(Fy_mesh/1000, Fz_mesh/1000, sigma_mesh, levels=20, cmap='viridis')
ax2.set_xlabel('Fz [kN]')
ax2.set_ylabel('Fy [kN]')
ax2.set_title('sigma [MPa]', fontsize=12, fontweight='bold')
fig1.colorbar(contour, ax=ax2, label='sigma [MPa]')
plt.savefig("./syst_8_tripod_cables/plots/3D_plot_surface", dpi=300)
plt.tight_layout()


# --- FIGURE 2: Extra Pictures (2D Projections) ---
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))

# Picture 1: V vs M (Looking "sideways" at the 3D plot)
# We plot multiple lines for different H values to show the trend
for i in range(0, len(Fy_range), 4): # Plot every 4th H-level for clarity
    ax3.plot(Fz_range / 1000, sigma_mesh[i, :], label=f'Fy = {Fy_range[i] / 1000:.1f} kN')

ax3.set_xlabel('Fz [kN]')
ax3.set_ylabel('sigma [MPa]')
ax3.set_title('sigma as function of Fz (Various Fy)', fontweight='bold')
ax3.grid(True, linestyle='--', alpha=0.6)
ax3.legend(fontsize='small')

# Picture 2: H vs M (Looking "front-on" at the 3D plot)
# We plot multiple lines for different V values
for i in range(0, len(Fz_range), 4): # Plot every 4th V-level
    ax4.plot(Fy_range/ 1000, sigma_mesh[:, i], label=f'V = {Fz_range[i] / 1000:.1f} kN')

ax4.set_xlabel('Fy [kN]')
ax4.set_ylabel('sigma [MPa]')
ax4.set_title('sigma as function of Fy (Various Fz)', fontweight='bold')
ax4.grid(True, linestyle='--', alpha=0.6)
ax4.legend(fontsize='small')

plt.tight_layout()
plt.savefig("./syst_8_tripod_cables/plots/3D_plot_sections", dpi=300)
plt.show()
