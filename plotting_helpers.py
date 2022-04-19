import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

_palette = sns.color_palette()

#
#   Gaussian Process Surrogate Plotting
#

def plot_gp_heatmap(normC1_grid, normangle_grid, z_vector, z_label, raw_data, num_C1_ticks=6, num_angle_ticks=6, num_z_ticks=6, C1_ticks_dp=1, angle_ticks_dp=1, z_ticks_dp=2, z_lims=None,  x_label=None, y_label=None):   
    z_grid = z_vector.reshape(normC1_grid.shape, order='F')
    fig, ax = plt.subplots()
    im = plt.imshow(z_grid, cmap='coolwarm', origin='lower')
    _create_colourbar(im, z_grid, z_label, z_lims, num_z_ticks, z_ticks_dp)
    set_x_and_y_ticks(ax, normC1_grid, normangle_grid, num_C1_ticks, num_angle_ticks, C1_ticks_dp, angle_ticks_dp)
    set_x_and_y_labels(ax, x_label, y_label)
    plot_gp_points_as_crosses(raw_data, normC1_grid, normangle_grid, color='black')
    clean_up_plot(fig)
    return fig

def _create_colourbar(im, z_grid, z_label, z_lims, num_z_ticks, z_ticks_dp):
    z_lims = _create_z_lims(z_lims, z_grid, z_ticks_dp)
    ticks = np.linspace(z_lims[0], z_lims[1], num_z_ticks+1)
    ticks = np.around(ticks, decimals=z_ticks_dp)
    cbar = plt.colorbar(im, ticks=ticks)
    cbar.set_label(z_label, rotation=270, labelpad=15)

def _create_z_lims(z_lims, z, ticks_dp):
    if z_lims is None:
        z_lims = (np.min(z), np.max(z))
    return z_lims

def set_x_and_y_ticks(ax, x_grid, y_grid, num_x_ticks=6, num_y_ticks=6, x_dp=1, y_dp=1):
    
    num_y_pts, num_x_pts = x_grid.shape

    x = _create_vector_from_grid(x_grid)
    x_ticks = np.linspace(np.min(x_grid), np.max(x_grid), num_x_ticks)
    ax.set_xticks(np.linspace(0, num_x_pts-1, num_x_ticks))
    ax.set_xticklabels([f"{val:.{x_dp}f}" for val in x_ticks])
    
    y = _create_vector_from_grid(y_grid)
    y_ticks = np.linspace(np.min(y_grid), np.max(y_grid), num_y_ticks)
    ax.set_yticks(np.linspace(0, num_y_pts-1, num_y_ticks))
    ax.set_yticklabels([f"{val:.{y_dp}f}" for val in y_ticks])

def _create_vector_from_grid(grid):
    return np.unique(grid.flatten())

def set_x_and_y_labels(ax, x_label=None, y_label=None):
    if x_label is None:
        x_label = 'Normalised Stiffness'
    ax.set_xlabel(x_label)
    if y_label is None:
        y_label = 'Normalised Beam Angle'
    ax.set_ylabel(y_label)

def plot_gp_points_as_crosses(raw_data, x_grid, y_grid, color, x_key='C_1', y_key='beam_angle'):
    num_y_pts, num_x_pts = x_grid.shape
    # Convert fraction positions (i.e. between 0 and 1) to pixel positions:
    x_plot_pts = _compute_pixel_positions(raw_data[x_key], x_grid, axes_dim=0)
    y_plot_pts = _compute_pixel_positions(raw_data[y_key], y_grid, axes_dim=1)
    plt.plot(x_plot_pts, y_plot_pts, 'x', color=color, markersize=5)

def _compute_pixel_positions(pts, grid_coords, axes_dim):
    min_coord = np.min(grid_coords)
    max_coord = np.max(grid_coords)
    norm_positions = (pts - min_coord)/(max_coord - min_coord)
    num_pts = grid_coords.shape[axes_dim]
    return norm_positions*(num_pts-1)

#
#   Probability Distribution Plotting
#

def plot_distributions(pdf, x, xlabel=None, ylabel=None, pdf_labels=None, alpha=0.2):
    for _ in range(2 - pdf.ndim):
        pdf = pdf[None,:]
    if ylabel is None:
        ylabel = 'Probability Density'
    fig, ax = plt.subplots()
    for i, pdf_i in enumerate(pdf):
        sns.lineplot(x=x.squeeze(), y=pdf_i.squeeze(), color=_palette[i])
        ax.fill_between(x.squeeze(), pdf_i.squeeze(), alpha=alpha, color=_palette[i])
    plt.legend(pdf_labels, frameon=False)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    clean_up_plot(fig)

def plot_loss_history(loss_history, y_label=None):
    fig, ax = plt.subplots()
    sns.lineplot(x=np.arange(len(loss_history)), y=np.array(loss_history))
    ax.set_xlabel('Iteration Number')
    if y_label is None:
        y_label = 'loss'
    ax.set_ylabel(ylabel)
    clean_up_plot(fig)
    return fig

def plot_amortised_phi(amortised_approx, y_lims, d_lims, num_y_pts, num_d_pts, phi_key, num_y_ticks=10, num_d_ticks=10, num_phi_ticks=10, phi_ticks_dp=1, y_ticks_dp=1, d_ticks_dp=1, phi_lims=None):
    y_grid, d_grid = create_2d_point_grid(y_lims, d_lims, num_y_pts, num_d_pts)
    y = y_grid.flatten().reshape(-1,1)
    d = d_grid.flatten().reshape(-1,1)
    phi = amortised_approx.phi(y,d)[phi_key]
    phi = phi.reshape(num_y_pts, num_d_pts)
    fig, ax = plt.subplots()
    im = plt.imshow(phi, cmap='coolwarm', origin='lower')
    _create_colourbar(im, phi, phi_key, phi_lims, num_phi_ticks, phi_ticks_dp)
    set_x_and_y_ticks(ax, y_grid, d_grid, num_y_ticks, num_d_ticks, y_ticks_dp, d_ticks_dp)
    set_x_and_y_labels(ax, x_label='Normalised Beam Tip Displacement', y_label='Normalised Stiffness')
    clean_up_plot(fig)
    return fig

#
#   General Plotting Methods
#

def clean_up_plot(fig):
    fig.patch.set_facecolor('white')

#
#   Point Grid Methods
#

def create_2d_point_grid(C1_lims, angle_lims, num_C1_pts, num_angle_pts):
    C_1_pts = np.linspace(np.atleast_1d(C1_lims[0]), np.atleast_1d(C1_lims[1]), num_C1_pts)
    angle_pts = np.linspace(np.atleast_1d(angle_lims[0]), np.atleast_1d(angle_lims[1]), num_angle_pts)
    normangle_grid, normC1_grid = np.meshgrid(C_1_pts.squeeze(), angle_pts.squeeze())
    return normC1_grid, normangle_grid

def flatten_and_stack_grids(C1_grid, angle_grid):
    return np.stack([C1_grid.flatten(), angle_grid.flatten()], axis=1)