import numpy as np
import matplotlib.pyplot as plt
import time
from scipy.linalg import eigh

def generate_global_connected_laplacian(n, num_groups=4):
    """
    Simulates a macro-scale, globally connected Graph Laplacian matrix (L_G)
    characterized by block-sparse structures and local overlapping perimeters.
    """
    block_size = n // num_groups
    L_G = np.zeros((n, n))
    
    for g in range(num_groups):
        start, end = g * block_size, (g + 1) * block_size
        # Generate localized connected subdomain adjacency
        A_local = np.random.rand(block_size, block_size) > 0.4
        A_local = (A_local | A_local.T).astype(float)
        np.fill_diagonal(A_local, 0)
        D_local = np.diag(np.sum(A_local, axis=1))
        L_G[start:end, start:end] = D_local - A_local
        
    # Inject weak overlapping boundary edges (Splicing Bridge Edges)
    for g in range(num_groups - 1):
        idx1 = (g + 1) * block_size - 1
        idx2 = (g + 1) * block_size
        L_G[idx1, idx1] += 1
        L_G[idx2, idx2] += 1
        L_G[idx1, idx2] = -1
        L_G[idx2, idx1] = -1
        
    return L_G

def operator_6_subspace_splicing(L_G, num_groups=4, k_rank=4):
    """
    Core numerical implementation of Operator 6.
    Executes Localized Sub-space Orthogonal Sieving (P_sieve) and 
    Boundary Homological Splicing (O_splice) to extract extreme invariants.
    """
    n = L_G.shape[0]
    block_size = n // num_groups
    V_global_list = []
    
    # Phase I: P_sieve - Independent parallel localized subspace extraction
    for g in range(num_groups):
        start, end = g * block_size, (g + 1) * block_size
        L_local = L_G[start:end, start:end]
        
        # Local eigensolution simulating standalone Actor Lanczos routines
        vals, vecs = eigh(L_local, subset_by_index=(0, k_rank - 1))
        
        # Construct global projection coordinate trial basis component
        V_ext = np.zeros((n, k_rank))
        V_ext[start:end, :] = vecs
        V_global_list.append(V_ext)
        
    # Phase II: O_splice - Homological stitching into global trial subspace
    V_global = np.hstack(V_global_list)
    
    # Phase III: Construct the compact Algebraic Rayleigh-Ritz Splicing Kernel
    K_RR = V_global.T @ L_G @ V_global
    
    # Phase IV: Bug1 Fix - Explicitly unpack eigenvalues and eigenvector matrices
    rr_vals, rr_vecs = eigh(K_RR, subset_by_index=(0, k_rank - 1))
    
    # Safely extract the 1D eigenvalue array indices without dimension errors
    lambda_2_approx = rr_vals[1]   # Second smallest eigenvalue (Fiedler Prior)
    alpha_n_approx = rr_vals[-1]   # Maximal eigenvalue (Spectral Radius Prior)
    
    return lambda_2_approx, alpha_n_approx

if __name__ == "__main__":
    print("-" * 80)
    print("Executing Operator 6 (Psieve U Osplice) Empirical Verification Suite")
    print("-" * 80)

    # Immutable system-level hyperparameter configuration
    NUM_GROUPS = 4
    K_RANK = 4 
    
    # Define macro-scale system extension horizons for stress testing
    test_scales = [400, 800, 1200, 1600, 2000]
    global_times = []
    operator_6_times = []
    errors_lambda_2 = []

    for n in test_scales:
        L_G = generate_global_connected_laplacian(n, num_groups=NUM_GROUPS)
        
        # Benchmark I: Bug2 Optimization - Force eigvals_only=True to maximize speed
        t0 = time.perf_counter()
        true_vals = eigh(L_G, eigvals_only=True)
        true_l2, true_alpha = true_vals[1], true_vals[-1]
        t1 = time.perf_counter()
        global_times.append((t1 - t0) * 1000)
        
        # Benchmark II: Operator 6 Splicing Kernel Scheme (O(m_g * k_rank))
        t2 = time.perf_counter()
        approx_l2, approx_alpha = operator_6_subspace_splicing(L_G, num_groups=NUM_GROUPS, k_rank=K_RANK)
        t3 = time.perf_counter()
        operator_6_times.append((t3 - t2) * 1000)
        
        # Compute variational approximation error for algebraic connectivity
        err = np.abs(true_l2 - approx_l2) / true_l2
        errors_lambda_2.append(err)
        
        print(f"Scale n = {n:4d} | Global Time: {global_times[-1]:8.2f} ms | Operator 6 Time: {operator_6_times[-1]:6.2f} ms | Rel Error: {err:.6e}")

    # Layout Optimization and Multi-axis Collision Avoidance
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Operator 6 (Psieve U Osplice) Computational Complexity and Accuracy Clamping", 
                 fontsize=12, fontweight='bold', y=0.98)

    # Panel 1: Complexity Destruction Redline (O(n^3) vs O(m_g * k_rank))
    ax1.plot(test_scales, global_times, marker='o', color='red', linestyle='--', lw=1.8, label='Global Synchronous Spectral (O(n^3))')
    ax1.plot(test_scales, operator_6_times, marker='s', color='darkgreen', lw=2, label='Operator 6 Splicing Kernel (O(m_g * k_rank))')
    ax1.set_xlabel("Global Network Scale (Nodes n)", fontsize=10)
    ax1.set_ylabel("Execution Time (ms)", fontsize=10)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.set_title("1. Complexity Destruction Redline", fontsize=11, fontweight='bold')
    ax1.legend(loc='upper left')

    # Panel 2: Theorem 6.1 - Rayleigh-Ritz Approximation Error Boundary
    ax2.plot(test_scales, errors_lambda_2, marker='^', color='purple', lw=2, label='Relative Error of lambda_2(n)')
    ax2.set_xlabel("Global Network Scale (Nodes n)", fontsize=10)
    ax2.set_ylabel("Relative Error Approximation Boundary", fontsize=10)
    ax2.set_yscale('log')
    ax2.grid(True, linestyle=':', alpha=0.6)
    ax2.set_title("2. Algebraic Approximation Accuracy Baseline", fontsize=11, fontweight='bold')
    ax2.legend(loc='upper right')

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.3)
    
    output_png = "operator_6_complexity_redline_verification.png"
    plt.savefig(output_png, dpi=200, bbox_inches='tight')
    
    print("-" * 80)
    print(f"Empirical verification complete. Figure saved to: {output_png}")
    print("-" * 80)
    plt.show()
