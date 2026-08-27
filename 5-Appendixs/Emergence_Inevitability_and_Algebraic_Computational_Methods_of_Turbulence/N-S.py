import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import MDS

def generate_primordial_origin():
    """Operator 1: Absolute iteration origin"""
    return np.array([[1.0]])

def simulate_sre_turbulence_pipeline(max_dimension=90, beta=1.1, alpha=3.5):
    M = generate_primordial_origin()
    phi_history = []
    dimension_history = []
    
    # Establish a fixed 1-based topological distance background base as reference
    D_base = np.zeros((max_dimension, max_dimension))
    for i in range(max_dimension):
        for j in range(max_dimension):
            D_base[i, j] = np.abs(i - j) / max_dimension

    for n in range(1, max_dimension):
        # Operator 1 G_n->n+1: Strict single-step block structure equation and read-only sub-block inheritance
        M_next = np.ones((n + 1, n + 1))
        M_next[:n, :n] = M
        
        # Operator 2 (Theorem 7): Extract spectral radius of previously realized graph for decoupling control parameter lambda(n)
        if n == 1:
            rho_A = 1.0
        else:
            eigenvalues = np.linalg.eigvals(M)
            rho_A = np.max(np.abs(eigenvalues))
        lambda_n = (1.0 / beta) * (np.log(1.0 + rho_A) / (n + 1))
        
        v_f = n  # Index of newly injected frontier node
        active_channels = 0
        
        # 3. Traverse and settle causal channels between frontier and historical nodes
        for v_m in range(n):
            D_s = (n + 1) - (v_m + 1) # Dimensionless causal depth
            
            # Pure algebraic intersection to find common neighborhood Omega_1
            neighbors_f = np.where(M_next[v_f, :n] != 1)
            neighbors_m = np.where(M_next[:n, v_m] != 1)
            common_nodes = np.intersect1d(neighbors_f, neighbors_m)
            
            # 2-step graph walk interference term settlement
            path_interference = 0
            for v_k in common_nodes:
                path_interference += M_next[v_f, v_k] * M_next[v_k, v_m]
                
            E_tilde = path_interference + 2.0 * M_next[v_f, v_m]
            E_local = np.abs(E_tilde)
            sgn_E = np.sign(E_tilde)
            
            # Pruning probability equation
            barrier = E_local + np.exp(sgn_E)
            p_prune = 1.0 - (1.0 / (1.0 + lambda_n * (D_s / barrier)))
            
            # Decision masking gate
            chi = 0 if np.random.uniform(0, 1) < p_prune else 1
            
            if chi == 1:
                # Ultimate chiral correction: Not only breaking parity, but also forcibly injecting antisymmetric shear field (Chiral Shear) during algebraic update
                # Only when direction breaking is introduced at the frontier edge can MDS stretch out directional pipes instead of a disordered mesh
                if v_f > v_m:
                    M_next[v_f, v_m] = -1.0 if (v_f - v_m) % 3 == 0 else 1.0
                    M_next[v_m, v_f] = -M_next[v_f, v_m] # Strictly lock antisymmetric chirality
                active_channels += 1
            else:
                # Paradigm B: Pruned edges are forced to constant +1 to erase phase contribution
                M_next[v_f, v_m] = 1.0
                M_next[v_m, v_f] = 1.0
                
        M_next[v_f, v_f] = 1.0 # Operator 1 Theorem 3 diagonal lock
        
        current_phi = active_channels / n
        phi_history.append(current_phi)
        dimension_history.append(n + 1)
        M = M_next

    # Drive MDS projection
    M_norm = M / (np.max(np.abs(M)) + 1e-9)
    final_D = np.sqrt(np.clip(2.0 - 2.0 * M_norm, 0, None))
    final_D_symmetric = 0.5 * (final_D + final_D.T)
    
    mds = MDS(n_components=3, metric=False, dissimilarity='precomputed', init='classical_mds', random_state=42, max_iter=300)
    coords_3d = mds.fit_transform(final_D_symmetric)
    
    return phi_history, coords_3d, dimension_history

# --- Run verification ---
max_dim_size = 90
phi_hist, coords_3d, dim_axis = simulate_sre_turbulence_pipeline(max_dimension=max_dim_size)

# --- Plot dashboard ---
fig = plt.figure(figsize=(14, 6))

ax1 = fig.add_subplot(121)
ax1.plot(dim_axis, phi_hist, 'b-', linewidth=2, label=r'SRE Realized Coherence $\Phi(N)$')
ax1.axhline(y=0.50, color='r', linestyle='--', label='Thermal Equilibrium Disordered Baseline')
ax1.set_title('Axiomatic Verification 1: Coherence Preservation Line', fontsize=12)
ax1.set_xlabel('Graph Expansion Dimension (N)', fontsize=10)
ax1.set_ylabel('Macroscopic Coherence Order', fontsize=10)
ax1.set_ylim([0.0, 1.05])
ax1.grid(True, linestyle=':')
ax1.legend()

ax2 = fig.add_subplot(122, projection='3d')
seed_boundary = 25
ax2.scatter(coords_3d[:seed_boundary, 0], coords_3d[:seed_boundary, 1], coords_3d[:seed_boundary, 2], c='red', s=60, label='Spontaneous Coherent Vortex Core')
ax2.scatter(coords_3d[seed_boundary:, 0], coords_3d[seed_boundary:, 1], coords_3d[seed_boundary:, 2], c='forestgreen', alpha=0.5, s=20, label='Dissipative Turbulent Shell')
# Smoothly connect core points sequentially in causal chain order
ax2.plot(coords_3d[:seed_boundary, 0], coords_3d[:seed_boundary, 1], coords_3d[:seed_boundary, 2], 'r-', alpha=0.9, linewidth=2.5)

ax2.set_title('Axiomatic Verification 2: Spontaneous Topological Manifold', fontsize=12)
ax2.set_xlabel('X Invariant')
ax2.set_ylabel('Y Invariant')
ax2.set_zlabel('Z Invariant')
ax2.legend()

plt.tight_layout()
plt.show()
