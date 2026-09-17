from syst_2_model_functions import t_S_cablenet_nonlinear, t_S_hyperplane_linear
import numpy as np
import matplotlib.pyplot as plt


sigma_list = []

l_1d = 1.65 # kN/m2
l_2d = 0.975 # kN/m2

# --- Points to highlight on the 2D section plots ---
# Points on the l_1 section (l_2 = 0), given as l_1 values [kN/m^2]
L1_POINTS = [1.1, 1.65]

# Points on the l_2 section (l_1 = 0), given as l_2 values [kN/m^2]
L2_POINTS = [0.65, 0.975]

# Range for Surface Loads
Fz_range = np.linspace(0, l_1d * 1.1, 20) # Load in kN/m2
Fy_range = np.linspace(0, l_2d * 1.1, 20) # Load in kN/m2


# Create meshgrid for 3D plotting
Fz_mesh, Fy_mesh = np.meshgrid(Fz_range, Fy_range)
sigma_mesh = np.zeros_like(Fz_mesh)

# Nonlinear analysis
for i in range(len(Fy_range)):
        for j in range(len(Fz_range)):
            Fy_val = Fy_mesh[i, j]
            Fz_val = Fz_mesh[i, j]
            
            sigma = t_S_cablenet_nonlinear(Fz_val, Fy_val)
            
            sigma_mesh[i, j] = sigma


# Linearized analysis
sigma_lin_mesh = np.zeros_like(Fz_mesh)

for i in range(len(Fy_range)):
        for j in range(len(Fz_range)):
            Fy_val = Fy_mesh[i, j]
            Fz_val = Fz_mesh[i, j]

            sigma_lin = t_S_hyperplane_linear(Fz_val, Fy_val)

            sigma_lin_mesh[i, j] = sigma_lin



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
surf2 = ax1.plot_surface(Fz_mesh, Fy_mesh, sigma_mesh, cmap='viridis', 
                         edgecolor='none', alpha=0.7, label='TH3')

ax1.set_xlabel(r'Snow load $l_{1}$ $[\mathrm{kN/m^2}]$', labelpad=12)
ax1.set_ylabel(r'Wind load $l_{2}$ $[\mathrm{kN/m^2}]$', labelpad=15)
zlabel = ax1.set_zlabel(r'Internal stress $\sigma$ $[\mathrm{N/mm^2}]$', labelpad=15)
ax1.zaxis.set_rotate_label(False)   # stop matplotlib recalculating the angle at draw time
zlabel.set_rotation(90)             
# ax1.set_title(r'$\sigma_{\mathrm{PK2}}$ as function of $l_{1}$ and $l_{2}$', fontsize=TITLE_FONTSIZE, fontweight='bold', pad=-50)
ax1.view_init(elev=15, azim=210)
ax1.zaxis.set_tick_params(pad=8)   # increase for more gap between numbers and the axis, decrease for less
ax1.xaxis.set_major_formatter(ONE_DECIMAL)
ax1.yaxis.set_major_formatter(ONE_DECIMAL)
ax1.zaxis.set_major_formatter(ONE_DECIMAL)

# Subplot 2: Contour plot (keeping your existing logic)
ax2 = fig1.add_subplot(gs1[1])
contour = ax2.contourf(Fz_mesh, Fy_mesh, sigma_mesh, levels=20, cmap='viridis')
ax2.set_xlabel(r'Snow load $l_{1}$ $[\mathrm{kN/m^2}]$')
ax2.set_ylabel(r'Wind load $l_{2}$ $[\mathrm{kN/m^2}]$')
# ax2.set_title('Contour Plot of $\sigma_{\mathrm{PK2}}$', fontsize=TITLE_FONTSIZE, fontweight='bold')
cbar = fig1.colorbar(contour, ax=ax2, label=r'Internal stress $\sigma$ $[\mathrm{N/mm^2}]$', fraction=0.046, pad=0.04)
cbar.ax.yaxis.set_major_formatter(ONE_DECIMAL)
ax2.set_box_aspect(1)   # force a square (quadratic) contour panel, regardless of data range
ax2.xaxis.set_major_formatter(ONE_DECIMAL)
ax2.yaxis.set_major_formatter(ONE_DECIMAL)
fig1.subplots_adjust(left=0.07, right=0.90, top=0.90, bottom=0.10)
fig1.savefig('./syst_2_tripod_cables/syst_2_plots/fig1_surface_contour.png', dpi=220, facecolor='white')
fig1.savefig('./syst_2_tripod_cables/syst_2_plots/fig1_surface_contour.svg', facecolor='white')




# # --- FIGURE 2: Extra Pictures (2D Projections) ---
import matplotlib.transforms as mtransforms

def style_arrow_axes(ax):
    """Open axes: spines only at x=0/y=0, arrowheads at the positive ends."""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_position(('data', 0))
    ax.spines['bottom'].set_position(('data', 0))
    ax.set_xlim(left=0)
    ax.set_ylim(bottom=0)
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False, markersize=8)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False, markersize=8)

def label_arrow_axes(ax, xlabel, ylabel):
    """x-label above (and shifted right of) the x-arrow tip; y-label horizontal, right of the y-arrow tip."""
    trans_x = mtransforms.offset_copy(ax.get_yaxis_transform(), fig=ax.figure, x=60, y=6, units='points')
    ax.text(1.0, 0.0, xlabel, transform=trans_x, ha='right', va='bottom')

    trans_y = mtransforms.offset_copy(ax.get_xaxis_transform(), fig=ax.figure, x=10, y=0, units='points')
    ax.text(0.0, 1.0, ylabel, transform=trans_y, ha='left', va='center', rotation=0)
    
# Interpolated M-values at the highlighted points, from the l_2=0 / l_1=0 sections
L1_POINTS_M = np.interp(L1_POINTS, Fz_range, sigma_mesh[0, :])
L2_POINTS_M = np.interp(L2_POINTS, Fy_range, sigma_mesh[:, 0])

def add_origin_line(ax, x1, y1):
    """Thin dashed straight line through the origin and (x1, y1), spanning the full x-range."""
    x_max = ax.get_xlim()[1]
    slope = y1 / x1
    ax.plot([0, x_max], [0, slope * x_max], color='black', linewidth=0.8, linestyle='--', zorder=1)

def add_point_guides(ax, xs, ys):
    """Solid vertical line up to the curve, dashed horizontal line back to the y-axis."""
    for x0, y0 in zip(xs, ys):
        ax.plot([x0, x0], [0, y0], color='black', linewidth=1.0, zorder=3)
        ax.plot([0, x0], [y0, y0], color='black', linewidth=1.0, linestyle='-', zorder=3)


# --- FIGURE 2a: M vs l_1, section at l_2 = 0.0 ---
fig2a, ax_l1 = plt.subplots(figsize=(8, 6))
ax_l1.plot(Fz_range, sigma_mesh[0, :], color='black')
style_arrow_axes(ax_l1)
ax_l1.plot(Fz_range, sigma_lin_mesh[0, :], color='black', linestyle='--', linewidth=0.8, zorder=1)
label_arrow_axes(ax_l1, r'$l_{1}\ [\mathrm{kN/m^2}]$', r'$\sigma\ [\mathrm{N/mm^2}]$')
add_point_guides(ax_l1, L1_POINTS, L1_POINTS_M)
ax_l1.grid(False)
ax_l1.xaxis.set_major_formatter(ONE_DECIMAL)
ax_l1.yaxis.set_major_formatter(ONE_DECIMAL)
ax_l1.tick_params(labelbottom=False, labelleft=False, bottom=False, left=False)
# ax_l1.tick_params(labelbottom=True, labelleft=True)

fig2a.savefig('./syst_2_tripod_cables/syst_2_plots/fig2a_section_l1.png', dpi=220, bbox_inches='tight', facecolor='white')
fig2a.savefig('./syst_2_tripod_cables/syst_2_plots/fig2a_section_l1.svg', bbox_inches='tight', facecolor='white')

# --- FIGURE 2b: M vs l_2, section at l_1 = 0.0 ---
fig2b, ax_l2 = plt.subplots(figsize=(8, 6))
ax_l2.plot(Fy_range, sigma_mesh[:, 0], color='black')
style_arrow_axes(ax_l2)
ax_l2.plot(Fy_range, sigma_lin_mesh[:, 0], color='black', linestyle='--', linewidth=0.8, zorder=1)
label_arrow_axes(ax_l2, r'$l_{2}\ [\mathrm{kN/m^2}]$', r'$\sigma\ [\mathrm{N/mm^2}]$')
add_point_guides(ax_l2, L2_POINTS, L2_POINTS_M)
ax_l2.grid(False)
ax_l2.xaxis.set_major_formatter(ONE_DECIMAL)
ax_l2.yaxis.set_major_formatter(ONE_DECIMAL)
ax_l2.tick_params(labelbottom=False, labelleft=False, bottom=False, left=False)
# ax_l2.tick_params(labelbottom=True, labelleft=True)

fig2b.savefig('./syst_2_tripod_cables/syst_2_plots/fig2b_section_l2.png', dpi=220, bbox_inches='tight', facecolor='white')
fig2b.savefig('./syst_2_tripod_cables/syst_2_plots/fig2b_section_l2.svg', bbox_inches='tight', facecolor='white')


# Compute single values for description in the images

t_S_l1d_0 = t_S_cablenet_nonlinear(l_1d, 0)
t_S_l1k_0 = t_S_cablenet_nonlinear(l_1d / 1.5, 0)
t_S_0_l2d = t_S_cablenet_nonlinear(0, l_2d)
t_S_0_l2k = t_S_cablenet_nonlinear(0, l_2d / 1.5)

print(f"t_S_l1d_0 = {t_S_l1d_0}")
print(f"t_S_l1k_0 = {t_S_l1k_0}")
print(f"t_S_0_l2d = {t_S_0_l2d}")
print(f"t_S_0_l2k = {t_S_0_l2k}")

