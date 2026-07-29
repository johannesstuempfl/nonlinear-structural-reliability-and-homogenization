from syst_8_model_functions import t_S_cablenet_nonlinear, t_S_cablenet_linear
import numpy as np
import matplotlib.pyplot as plt


sigma_list = []

# Range for Surface Loads
Fy_range = np.linspace(0, 1.65, 20) # Load in kN/m2
Fz_range = np.linspace(0, 0.975, 20) # Load in kN/m2


# Create meshgrid for 3D plotting
Fy_mesh, Fz_mesh = np.meshgrid(Fy_range, Fz_range)
sigma_mesh = np.zeros_like(Fy_mesh)


for i in range(len(Fy_range)):
        for j in range(len(Fz_range)):
            Fy_val = Fy_mesh[i, j]
            Fz_val = Fz_mesh[i, j]
            
            sigma = t_S_cablenet_nonlinear(Fz_val, Fy_val)
            #sigma = t_S_cablenet_linear(Fz_val, Fy_val)
            
            sigma_mesh[i, j] = sigma
            


from matplotlib.ticker import FormatStrFormatter

plt.rcParams.update({
    "mathtext.fontset": "cm",
    "font.family": "cmr10",
    "axes.unicode_minus": False,
    "font.size": 18,
})

ONE_DECIMAL = FormatStrFormatter('%.1f')   # forces every tick label to read e.g. "2.0" instead of "2"

TITLE_FONTSIZE = 18 

# --- FIGURE 1: 3D Surface & Contour (Updated) ---
fig1 = plt.figure(figsize=(16, 7))
gs1 = fig1.add_gridspec(1, 2, width_ratios=[1.1, 1.0], wspace=0.4)

# Subplot 1: 3D surface with BOTH M_Th1 and M_Th2
ax1 = fig1.add_subplot(gs1[0], projection='3d')


# Plotting Theory 3 Surface
surf2 = ax1.plot_surface(Fy_mesh, Fz_mesh, sigma_mesh, cmap='viridis', 
                         edgecolor='none', alpha=0.7, label='TH3')

ax1.set_xlabel(r'Vertical Force $l_{1}$ $[\mathrm{kN/m^2}]$', labelpad=12)
ax1.set_ylabel(r'Horizontal Force $l_{2}$ $[\mathrm{kN/m^2}]$', labelpad=15)
zlabel = ax1.set_zlabel(r'$\sigma_{\mathrm{PK2}}$ $[\mathrm{MPa}]$', labelpad=15)
ax1.zaxis.set_rotate_label(False)   # stop matplotlib recalculating the angle at draw time
zlabel.set_rotation(90)             
ax1.set_title(r'$\sigma_{\mathrm{PK2}}$ as function of $l_{1}$ and $l_{2}$', fontsize=TITLE_FONTSIZE, fontweight='bold', pad=-50)
ax1.view_init(elev=15, azim=210)
ax1.zaxis.set_tick_params(pad=8)   # increase for more gap between numbers and the axis, decrease for less
ax1.xaxis.set_major_formatter(ONE_DECIMAL)
ax1.yaxis.set_major_formatter(ONE_DECIMAL)
ax1.zaxis.set_major_formatter(ONE_DECIMAL)

# Subplot 2: Contour plot (keeping your existing logic)
ax2 = fig1.add_subplot(gs1[1])
contour = ax2.contourf(Fy_mesh, Fz_mesh, sigma_mesh, levels=20, cmap='viridis')
ax2.set_xlabel(r'Vertical Force $l_{1}$ $[\mathrm{kN/m^2}]$')
ax2.set_ylabel(r'Horizontal Force $l_{2}$ $[\mathrm{kN/m^2}]$')
ax2.set_title('Contour Plot of $\sigma_{\mathrm{PK2}}$', fontsize=TITLE_FONTSIZE, fontweight='bold')
cbar = fig1.colorbar(contour, ax=ax2, label=r'$\sigma_{\mathrm{PK2}}$ $[\mathrm{MPa}]$', fraction=0.046, pad=0.04)
cbar.ax.yaxis.set_major_formatter(ONE_DECIMAL)
ax2.set_box_aspect(1)   # force a square (quadratic) contour panel, regardless of data range
ax2.xaxis.set_major_formatter(ONE_DECIMAL)
ax2.yaxis.set_major_formatter(ONE_DECIMAL)
fig1.subplots_adjust(left=0.07, right=0.90, top=0.90, bottom=0.10)
fig1.savefig('./syst_8_tripod_cables/syst_8_plots/fig1_surface_contour.png', dpi=220, facecolor='white')
fig1.savefig('./syst_8_tripod_cables/syst_8_plots/fig1_surface_contour.svg', facecolor='white')




# --- FIGURE 2: Extra Pictures (2D Projections) ---
fig2, (ax3, ax4) = plt.subplots(1, 2, figsize=(16, 6))

# Picture 1: V vs M (Looking "sideways" at the 3D plot)
# We plot multiple lines for different H values to show the trend
for i in range(0, len(Fy_range), 4): # Plot every 4th H-level for clarity
    ax3.plot(Fz_range, sigma_mesh[i, :], label=fr'$l_{2} = {Fy_range[i]:.1f}\ \mathrm{{kN/m^2}}$')

ax3.set_xlabel(r'Vertical Force $l_{1}$ $[\mathrm{kN/m^2}]$')
ax3.set_ylabel(r'$\sigma_{\mathrm{PK2}}$ $[\mathrm{MPa}]$')
ax3.set_title(r'$\sigma_{\mathrm{PK2}}$ as function of $l_{1}$ (various $l_{2}$)', fontsize=TITLE_FONTSIZE, fontweight='bold')
ax3.grid(True, linestyle='--', alpha=0.6)
ax3.legend(fontsize='small', loc='upper left')
ax3.xaxis.set_major_formatter(ONE_DECIMAL)
ax3.yaxis.set_major_formatter(ONE_DECIMAL)

# Picture 2: H vs M (Looking "front-on" at the 3D plot)
# We plot multiple lines for different V values
for i in range(0, len(Fz_range), 4): # Plot every 4th V-level
    ax4.plot(Fy_range, sigma_mesh[:, i], label=fr'$l_{1} = {Fz_range[i]:.1f}\ \mathrm{{kN/m^2}}$')

ax4.set_xlabel(r'Horizontal Force $l_{2}$ $[\mathrm{kN/m^2}]$')
ax4.set_ylabel(r'$\sigma_{\mathrm{PK2}}$ $[\mathrm{MPa}]$')
ax4.set_title(r'$\sigma_{\mathrm{PK2}}$ as function of $l_{2}$ (various $l_{1}$)', fontsize=TITLE_FONTSIZE, fontweight='bold')
ax4.grid(True, linestyle='--', alpha=0.6)
ax4.legend(fontsize='small', loc='upper left')
ax4.xaxis.set_major_formatter(ONE_DECIMAL)
ax4.yaxis.set_major_formatter(ONE_DECIMAL)

plt.tight_layout()

fig2.savefig('./syst_8_tripod_cables/syst_8_plots/fig2_projections.png', dpi=220, bbox_inches='tight', facecolor='white')
fig2.savefig('./syst_8_tripod_cables/syst_8_plots/fig2_projections.svg', bbox_inches='tight', facecolor='white')

