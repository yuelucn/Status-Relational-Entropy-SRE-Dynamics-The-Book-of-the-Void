"""
DEPRECATED — v1 fluidised-bed cluster predictor. Superseded by `sre_core.py` (v2).

This file is a coarse toy mapping, not a derivation from the operator chain:
  * `base_frustration = C_s**2 * np.random.uniform(...)` is an ad-hoc construction;
  * `pruning_mask = c_e_matrix > (1.2 / U_g)` carries two hand-set constants;
  * the 35% dormancy threshold is a fitted cutoff, not an algebraic invariant.

It therefore cannot serve as evidence for the claims in n-s.md. The engineering
phase boundaries it produced (see sim-result.md) should be re-derived through
sre_core.py and then calibrated against ECT/PIV data as described in
train_Turbulence.md section 9.

Kept for provenance only. Do not cite numbers produced by this file.
"""
import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.linalg import eigh
from sklearn.manifold import MDS

def operator_5_latency_calibration(W_e, alpha_n, delta_flt=1e-16, c_max=3.0):
    """
    [Operator 5: Clamped Discrete Penetration Rate]
    Computes local conduction velocity to evaluate time dilation fields.
    """
    log_contraction = np.log(1.0 + W_e)
    denominator = log_contraction + delta_flt
    raw_c_e = alpha_n / denominator
    return np.minimum(raw_c_e, c_max)

def simulate_fluidized_bed_with_physics(n, U_g, C_s, alpha_n=1.5):
    """
    [Endogenous Gas-Solid Physics Simulator]
    Maps macroscopic hot-energy parameters (Gas Velocity U_g, Solid Conc C_s)
    into SRE matrix spaces using Operator 2, 5, and 6 invariants.
    """
    # 1. Map physics to topological path-overlap invariants (Operator 4 baseline)
    base_frustration = (C_s ** 2) * np.random.uniform(0.1, 1.5, size=(n, n))
    W_e_matrix = (base_frustration + base_frustration.T) / 2.0
    
    # 2. Activate Operator 5 to compute localized penetration rates
    c_e_matrix = operator_5_latency_calibration(W_e_matrix, alpha_n)
    
    # 3. Microscopic Pruning Decision - Driven by Boltzmann thermodynamic limits
    pruning_mask = c_e_matrix > (1.2 / U_g) 
    
    # 4. Enforce Operator 2 - Paradigm B: Elimination-Conduction (Forced Spin-1 Mode)
    M_matrix = np.ones((n, n))
    M_matrix[pruning_mask] = np.random.choice([-1, 1], size=np.sum(pruning_mask))
    
    # [CRITICAL BUGFIX]: Enforce absolute real symmetry over the spin matrix
    # Restores matrix parity to satisfy sklearn strict validation checks
    M_matrix = (M_matrix + M_matrix.T) / 2.0
    M_matrix = np.sign(M_matrix)
    M_matrix[M_matrix == 0] = 1.0 # Guarantee no continous zero state
    
    np.fill_diagonal(M_matrix, 1.0) # Rigid diagonal self-loop invariant
    
    # Derive standard Graph Laplacian from the realized SRE spin matrix
    A_matrix = (M_matrix == -1).astype(float)
    D_matrix = np.diag(np.sum(A_matrix, axis=1))
    L_G = D_matrix - A_matrix
    
    # Determine cluster onset condition: if more than 35% of channels collapse to identity +1
    dormancy_ratio = np.sum(~pruning_mask) / (n * n)
    is_clustered = dormancy_ratio > 0.35
    
    return L_G, M_matrix, is_clustered, dormancy_ratio

if __name__ == "__main__":
    print("-" * 80)
    print("Executing SRE Advanced Fluidized Bed Cluster Onset Predictor")
    print("-" * 80)

    # Operational parameters entry configuration
    gas_velocities = np.linspace(1.0, 5.0, 5) 
    solid_concentrations = np.linspace(0.5, 3.5, 5) 
    
    N_nodes = 80 
    
    print("Mapping Spontaneous Cluster Phase Boundaries...")
    for ug in gas_velocities:
        for cs in solid_concentrations:
            _, _, clustered, ratio = simulate_fluidized_bed_with_physics(N_nodes, ug, cs)
            status = "CLUSTER ONSET" if clustered else "DISPERSED"
            print(f" -> Input: U_g = {ug:.1f} m/s, C_s = {cs:.1f} kg/m3 | Dormancy Ratio = {ratio:.2%} | State: {status}")

    # -------------------------------------------------------------------------
    # Visualizing Manifestation: 3D MDS Manifold Splicing (Acceptance Criteria 1)
    # -------------------------------------------------------------------------
    print("\nRendering Spontaneous Topological Manifold Layout...")
    # Select a highly clustered dense operating condition to project vortex filaments
    L_G, M_spin, _, _ = simulate_fluidized_bed_with_physics(n=60, U_g=4.5, C_s=3.0)
    
    # Convert correlation spins into structural distance metrics: Dist = sqrt(2 - 2*M)
    distance_matrix = np.sqrt(np.clip(2.0 - 2.0 * (M_spin / M_spin.max()), 0, 4.0))
    
    # [API UPDATE]: Reconfigured initialization and metric params to comply with modern sklearn standards
    # Suppresses deprecation warnings in newer versions
    mds = MDS(n_components=3, metric=True, init='classical_mds', random_state=42, normalized_stress=False)
    coordinates = mds.fit_transform(distance_matrix)
    
    # Setup visualization panels
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    ax.set_title("Axiomatic Verification: Spontaneous Toroidal Attractor Core (Cluster Core)", 
             fontsize=12, fontweight='bold')
    
    X, Y, Z = coordinates[:, 0], coordinates[:, 1], coordinates[:, 2]
    
    # Plot active coherent particles (Chiral Core Paths)
    ax.scatter(X, Y, Z, color='darkgreen', alpha=0.5, s=25, label='Dissipative Turbulent Shell (Gas)')
    
    # Connect active non-unity channels to visualize the rigid centerline filament
    for i in range(len(X)):
        for j in range(i+1, len(X)):
            if M_spin[i, j] == -1: 
                ax.plot([X[i], X[j]], [Y[i], Y[j]], [Z[i], Z[j]], color='red', alpha=0.4, lw=1)
                
    ax.set_xlabel("X Invariant Metric")
    ax.set_ylabel("Y Invariant Metric")
    ax.set_zlabel("Z Invariant Metric")
    ax.legend(loc='upper right')
    
    output_png = "fluidized_bed_spontaneous_cluster_manifold.png"
    plt.savefig(output_png, dpi=200, bbox_inches='tight')
    print("-" * 80)
    print(f"Manifold generation complete. Asset saved to: {output_png}")
    print("-" * 80)
    plt.show()
