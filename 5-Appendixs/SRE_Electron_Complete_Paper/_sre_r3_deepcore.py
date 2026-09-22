"""
R3: 深核上 R 的鲁棒收敛验证 + 收敛步数随深度 L 的标度 + ε 物理定标

1. 镜像 sim_p.py 演化循环, 提取每步的休眠概率 dorm = 1/(1+ratio)
   (ratio = lam*d/(|M@M|+1)), 得到网络固有耗散尺度; 用其特征值(中位数)给 ε 物理定标.
2. 在构造深核 lift(Q3, L) (L=1..5) 上加边噪声 rho, 验证 R 鲁棒收敛到 Q3:
   - R_strict (精确, 脆性): 噪声下应退化
   - R_eps(ε_calib) (鲁棒): 在噪声窗内应仍还原 Q3
3. 测收敛步数随深度 L 的标度 (应 ~ O(L) 线性).
"""
import numpy as np
import networkx as nx
import json, importlib.util, sys

R2 = r"C:\mywork\vasp\_sre_r2_convergence.py"
r2spec = importlib.util.spec_from_file_location("r2", R2)
r2 = importlib.util.module_from_spec(r2spec)
r2spec.loader.exec_module(r2)

SIM_P = r"C:\mywork\SRE-Dynamics\5-Appendixs\Theory_of_Hierarchical_Dissipative_Self-Organizing_Binary_Network_Dynamics\sim_p.py"
simspec = importlib.util.spec_from_file_location("sim_p", SIM_P)
sim = importlib.util.module_from_spec(simspec)
simspec.loader.exec_module(sim)


# ---------------------------------------------------------------------------
# 1. 镜像演化 + 提取休眠概率
# ---------------------------------------------------------------------------
def evolve_with_dormancy(steps=300, lam=0.8, seed=1111, sample_steps=None):
    """完全镜像 sim_p.hierarchical_dissipation_binary_network_final,
    额外返回演化中收集到的休眠概率样本 (代表相干尺度 50..steps)."""
    np.random.seed(seed)
    M = np.array([[1]], dtype=int)
    dorm_samples = []
    if sample_steps is None:
        sample_steps = list(range(50, steps, 5))
    for n in range(1, steps):
        size = n + 1
        new_M = np.empty((size, size), dtype=int)
        new_M[:n, :n] = M
        E_local = np.abs(M @ M)
        i_idx = np.arange(n)[:, None]
        j_idx = np.arange(n)[None, :]
        d_matrix = n - np.maximum(i_idx, j_idx)
        ratio = (lam * d_matrix) / (E_local + 1)
        p_matrix = 1.0 - 1.0 / (1.0 + ratio)
        dorm = 1.0 - p_matrix  # 休眠概率
        if n in sample_steps:
            dorm_samples.append(dorm.flatten())
        rand = np.random.rand(n, n)
        rand = np.triu(rand) + np.triu(rand, 1).T
        act = rand >= p_matrix
        mask = np.where(act, M, 1)
        nb = np.prod(mask, axis=1)
        has = np.any(act, axis=1)
        nb = np.where(has, nb, 1)
        new_M[:n, n] = nb
        new_M[n, :n] = nb
        tot = np.sum(new_M[:n, :n])
        new_M[n, n] = -1 if tot >= 0 else 1
        M = new_M
    return M, dorm_samples


def add_edge_noise(M, rho, rng):
    """对称地翻转每条边 (i<j) 的符号, 概率 rho; 保持 {+-1} 词汇."""
    M = M.copy().astype(int)
    n = M.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            if M[i, j] != 0 and rng.random() < rho:
                s = -M[i, j]
                M[i, j] = s
                M[j, i] = s
    return M


def is_Q3(S):
    V, E, b1, bip, g = r2.graph_invariants(S)
    if (V, E, b1) != (8, 12, 5):
        return False, (V, E, b1)
    G = nx.from_numpy_array((np.fill_diagonal(S.copy(), 0) or S) != 0)
    Q = nx.from_numpy_array((np.fill_diagonal(r2.cube_Q3().copy(), 0) or r2.cube_Q3()) != 0)
    return nx.is_isomorphic(G, Q), (V, E, b1)


# ---------------------------------------------------------------------------
# 主验证
# ---------------------------------------------------------------------------
def main():
    out = {}
    rng_master = np.random.default_rng(20260917)

    # ===== 1. ε 物理定标 =====
    M_final, dorm_samples = evolve_with_dormancy(steps=300, lam=0.8, seed=1111)
    k = int(0.2 * 300)
    Mcore = np.sign(M_final[:k, :k]).astype(int)
    Vc, Ec, b1c, _, _ = r2.graph_invariants(Mcore)
    all_dorm = np.concatenate(dorm_samples)
    dorm_stats = dict(
        n_samples=int(all_dorm.size),
        median=float(np.median(all_dorm)),
        mean=float(np.mean(all_dorm)),
        p10=float(np.percentile(all_dorm, 10)),
        p90=float(np.percentile(all_dorm, 90)),
        min=float(all_dorm.min()), max=float(all_dorm.max()))
    # 物理定标: ε = 中位数休眠概率 (网络固有耗散尺度)
    eps_calib = float(np.median(all_dorm))
    out["epsilon_calibration"] = dict(
        dormancy_stats=dorm_stats, eps_calibrated=eps_calib,
        Mcore_invariants=dict(V=Vc, E=Ec, b1=b1c),
        note="eps = 网络中位休眠概率 1/(1+lam*d/(|M@M|+1)); 不再是扫描参数, 而是物理输入")
    print(f"[ε-calib] dorm median={eps_calib:.4f} mean={dorm_stats['mean']:.4f} "
          f"range=[{dorm_stats['min']:.3f},{dorm_stats['max']:.3f}]", flush=True)

    # ===== 2. 噪声鲁棒收敛 (深核 lift(Q3,L)); L<=3 (避免 128 节点 O(n^4) 过慢) =====
    noise_test = {}
    rhos = [0.0, 0.02, 0.05, 0.1, 0.15, 0.2]
    for L in [1, 2, 3]:
        base = r2.z2_lift(r2.cube_Q3(), levels=L)
        row = {}
        for rho in rhos:
            rng = np.random.default_rng(1000 * L + int(rho * 1000))
            noisy = add_edge_noise(base, rho, rng)
            # R_strict (精确, 脆性)
            strict = noisy
            for _ in range(L + 3):
                nxt = r2.R_strict(strict)
                if nxt.shape == strict.shape and np.array_equal(nxt, strict):
                    break
                strict = nxt
            ok_s, inv_s = is_Q3(strict)
            # R_eps(ε_calib) (鲁棒)
            eps_rel, _ = r2.R_eps(noisy, eps_calib)
            ok_e, inv_e = is_Q3(eps_rel)
            # ε_calib 邻域鲁棒性 (对定标不敏感)
            ok_e_fac = {}
            for fac in [0.5, 2.0]:
                e2, _ = r2.R_eps(noisy, eps_calib * fac)
                ok_e_fac[str(fac)], _ = is_Q3(e2)
            row[str(rho)] = dict(
                strict_recovered=bool(ok_s), strict_inv=list(inv_s),
                eps_recovered=bool(ok_e), eps_inv=list(inv_e),
                eps_neighborhood_recovery=ok_e_fac)
        noise_test[f"L{L}"] = row
        print(f"[noise L={L}] done", flush=True)
        for rho in rhos:
            r = row[str(rho)]
            print(f"   rho={rho}: strict={r['strict_recovered']}{tuple(r['strict_inv'])} "
                  f"eps={r['eps_recovered']}{tuple(r['eps_inv'])} eps_fac={r['eps_neighborhood_recovery']}", flush=True)
    out["noise_robustness"] = noise_test

    # ===== 3. 收敛步数随深度 L 标度 =====
    scaling = {}
    for L in range(1, 5):
        base = r2.z2_lift(r2.cube_Q3(), levels=L)
        cur = base
        steps_strict = 0
        for _ in range(L + 5):
            nxt = r2.R_strict(cur)
            steps_strict += 1
            if nxt.shape == cur.shape and np.array_equal(nxt, cur):
                break
            cur = nxt
        ok, inv = is_Q3(cur)
        # R_eps 合并步数 (单步算一次合并)
        cur2 = base
        steps_eps = 0
        for _ in range(base.shape[0] + 5):
            nxt = r2.R_eps_step(cur2, eps_calib)
            steps_eps += 1
            if nxt.shape == cur2.shape and np.array_equal(nxt, cur2):
                break
            cur2 = nxt
        ok2, inv2 = is_Q3(cur2)
        scaling[f"L{L}"] = dict(start_nodes=base.shape[0],
                                strict_steps=steps_strict, strict_is_Q3=bool(ok),
                                eps_steps=steps_eps, eps_is_Q3=bool(ok2))
        print(f"[scaling L={L}] start={base.shape[0]} strict_steps={steps_strict}(Q3={ok}) "
              f"eps_steps={steps_eps}(Q3={ok2})")
    out["step_scaling"] = scaling

    # 拟合 steps ~ L (线性检验)
    Ls = np.array([int(k[1:]) for k in scaling])
    ss = np.array([scaling[k]["strict_steps"] for k in scaling])
    if len(Ls) > 1:
        A = np.vstack([Ls, np.ones_like(Ls)]).T
        slope, intercept = np.linalg.lstsq(A, ss, rcond=None)[0]
        out["scaling_fit"] = dict(slope=float(slope), intercept=float(intercept),
                                  note="steps ~ slope*L + intercept; 接近平表明 O(L)")
        print(f"[fit] steps = {slope:.3f}*L + {intercept:.3f}")

    with open("sre_r3_deepcore_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\n[OK] sre_r3_deepcore_results.json written")


if __name__ == "__main__":
    main()
