"""
R2: 显式构造稀疏算子 R 并证明其迭代收敛到 Q3 (DCF (8,12,5))

算子定义
--------
R_strict(M): Z2-holonomy 商算子 (严格等价)
    i~j  <=>  存在全局符号 s in {+1,-1} 使 M[i,:] == s * M[j,:]  (去掉对角)
    等价类是等价关系(自反/对称/传递)，商图保留 {+-1} 词汇与 Z2 holonomy。
    R_strict^2 = R_strict  (商的商 = 商)  => 迭代一步即不动点。

R_eps(M): 耗散松弛合并算子 (物理耗散 e 下的最近 holonomy-孪生对合并)
    每步取全局 holonomy-tension 最小且 <= eps 的节点对 (i,j) 合并：
        新节点行 = sign(M[i,:] + s*M[j,:])   (多数投票, 保持 {+-1})
    无满足对时停 => 不动点。
    耗散参数 eps 由电子尺度的物理耗散定 (类 A5=delta 的角色)。

收敛定理: R_eps 节点数单调不增 + 有限节点 => 有限步内到达不动点。
          R_strict 幂等 => R_strict^n = R_strict。
          由 P0 唯一性: 满足电子 holonomy 签名(cubic+planar+bipartite+free-Z2)
          的唯一不动点 = Q3。

本脚本: 数值验证三支柱, 输出 sre_r2_convergence_results.json。
"""
import numpy as np
import networkx as nx
import json, importlib.util, os

SIM_P = r"C:\mywork\SRE-Dynamics\5-Appendixs\Theory_of_Hierarchical_Dissipative_Self-Organizing_Binary_Network_Dynamics\sim_p.py"

# ----------------------------------------------------------------------------
# 基础图工具
# ----------------------------------------------------------------------------
def cube_Q3():
    """3-立方体 Q3: 8 顶点 12 边, beta1=5, 平面/二部/自由Z2."""
    G = nx.cubical_graph()  # 默认节点 0..7
    A = nx.to_numpy_array(G, dtype=int)
    return A

def graph_invariants(S):
    """返回 (|V|, |E|, beta1, is_bipartite, girth). 自动去对角."""
    n = S.shape[0]
    S0 = S.copy()
    np.fill_diagonal(S0, 0)
    G = nx.from_numpy_array((S0 != 0).astype(int))
    V = G.number_of_nodes()
    E = G.number_of_edges()
    b1 = E - V + 1  # 连通 (beta0=1)
    try:
        bip = nx.is_bipartite(G)
    except Exception:
        bip = None
    try:
        girth = nx.girth(G) if E > 0 else 0
    except Exception:
        girth = None
    return V, E, b1, bool(bip), girth

def is_cubic(S):
    n = S.shape[0]
    A = (np.fill_diagonal(S.copy(), 0) or S)
    A = (S != 0).astype(int)
    np.fill_diagonal(A, 0)
    return bool(np.all(A.sum(axis=1) == 3))

def z2_lift(M, levels=1):
    """Z2 双覆盖提升 (通用, 可递归 levels 次): 每个节点分裂为 (v,+) 与 (v,-)。
    单层: M'[2i,2j]=s, M'[2i+1,2j+1]=s, M'[2i,2j+1]=-s, M'[2i+1,2j]=-s。
    其 Z2-holonomy 商 (精确反号等价) 还原回 M。"""
    M = np.array(M, dtype=int)
    np.fill_diagonal(M, 0)
    for _ in range(levels):
        n = M.shape[0]
        N = 2 * n
        M2 = np.zeros((N, N), dtype=int)
        for i in range(n):
            for j in range(n):
                s = M[i, j]
                if s == 0:
                    continue
                M2[2 * i, 2 * j] = s
                M2[2 * i + 1, 2 * j + 1] = s
                M2[2 * i, 2 * j + 1] = -s
                M2[2 * i + 1, 2 * j] = -s
        M = M2
    return M

# ----------------------------------------------------------------------------
# R_strict: Z2-holonomy 商 (严格)
# ----------------------------------------------------------------------------
def R_strict(M):
    """等价类合并: i~j 当行 i 与行 j 去对角后整体反号。商图保留 {+-1} + Z2。"""
    M = np.array(M, dtype=int)
    n = M.shape[0]
    S = M.copy()
    np.fill_diagonal(S, 0)
    used = np.zeros(n, dtype=bool)
    blocks = []
    for i in range(n):
        if used[i]:
            continue
        blk = [i]
        used[i] = True
        for j in range(i + 1, n):
            if used[j]:
                continue
            mask = np.ones(n, dtype=bool)
            mask[i] = mask[j] = False
            if np.all(S[i, mask] == -S[j, mask]):
                blk.append(j)
                used[j] = True
        blocks.append(blk)
    m = len(blocks)
    C = np.zeros((m, m), dtype=int)
    for a in range(m):
        for b in range(m):
            if a == b:
                continue
            vals = []
            for x in blocks[a]:
                for y in blocks[b]:
                    if M[x, y] != 0:
                        vals.append(int(M[x, y]))
            if vals:
                C[a, b] = 1 if np.sum(vals) >= 0 else -1
                C[b, a] = C[a, b]
    return C

# ----------------------------------------------------------------------------
# R_eps: 耗散松弛合并 (单步 + 不动点)
# ----------------------------------------------------------------------------
def holonomy_tension(M, i, j):
    """holonomy tension in [0,1]: 0 = 行 i,j 去对角后整体反号(精确孪生)。"""
    n = M.shape[0]
    S = M.copy()
    np.fill_diagonal(S, 0)
    s = 1 if np.sum(S[i] * S[j]) >= 0 else -1
    agree = 0.0
    cnt = 0
    for k in range(n):
        if k == i or k == j:
            continue
        if S[i, k] == 0 and S[j, k] == 0:
            continue
        cnt += 1
        if S[i, k] == s * S[j, k]:
            agree += 1
    return (0.0 if cnt == 0 else 1.0 - agree / cnt)

def merge_pair(M, i, j):
    n = M.shape[0]
    S = M.copy()
    np.fill_diagonal(S, 0)
    s = 1 if np.sum(S[i] * S[j]) >= 0 else -1
    keep = [k for k in range(n) if k != i and k != j]
    m = len(keep)
    C = np.zeros((m + 1, m + 1), dtype=int)
    # 新节点 = i,j 合并
    for a, u in enumerate(keep):
        vals = []
        if S[i, u] != 0:
            vals.append(int(S[i, u]))
        if s * S[j, u] != 0:
            vals.append(int(s * S[j, u]))
        if vals:
            C[m, a] = 1 if np.sum(vals) >= 0 else -1
            C[a, m] = C[m, a]
    # keep 之间
    for a, u in enumerate(keep):
        for b, v in enumerate(keep):
            if a >= b:
                continue
            if S[u, v] != 0:
                C[a, b] = S[u, v]
                C[b, a] = S[u, v]
    return C

def R_eps_step(M, eps):
    """单步: 合并全局最小 tension 且满足 <= eps 的对; 无则返回原矩阵。"""
    n = M.shape[0]
    best = None
    bt = 1e9
    for i in range(n):
        for j in range(i + 1, n):
            t = holonomy_tension(M, i, j)
            if t < bt:
                bt = t
                best = (i, j)
    if best is None or bt > eps:
        return M.copy()
    return merge_pair(M, best[0], best[1])

def R_eps(M, eps, max_iter=2000):
    """不动点: 反复单步直到节点数不变。"""
    cur = np.array(M, dtype=int)
    traj = [cur.shape[0]]
    for _ in range(max_iter):
        nxt = R_eps_step(cur, eps)
        traj.append(nxt.shape[0])
        if nxt.shape[0] == cur.shape[0] and np.array_equal(nxt, cur):
            break
        cur = nxt
    return cur, traj

# ----------------------------------------------------------------------------
# 主验证
# ----------------------------------------------------------------------------
def main():
    out = {}
    Q = cube_Q3()
    Vq, Eq, b1q, bipq, gq = graph_invariants(Q)
    out["Q3_invariants"] = dict(V=Vq, E=Eq, b1=b1q, bipartite=bipq, girth=gq, cubic=is_cubic(Q))
    print(f"[Q3] V={Vq} E={Eq} b1={b1q} cubic={is_cubic(Q)} bipartite={bipq} girth={gq}")

    # ---- 提取真实 M_core (N=300 -> k=60) ----
    spec = importlib.util.spec_from_file_location("sim_p", SIM_P)
    sim = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sim)
    Mfull = sim.hierarchical_dissipation_binary_network_final(steps=300, lam=0.8, seed=1111)
    k = int(0.2 * 300)
    Mcore = np.sign(Mfull[:k, :k]).astype(int)
    Vc, Ec, b1c, bipc, gc = graph_invariants(Mcore)
    out["Mcore_invariants"] = dict(V=Vc, E=Ec, b1=b1c, bipartite=bipc, girth=gc)
    print(f"[Mcore] V={Vc} E={Ec} b1={b1c} bipartite={bipc} girth={gc}")

    # ===================================================================
    # 支柱 1: R_strict 幂等 (R^2=R) + 单调性
    # ===================================================================
    Rs = R_strict(Mcore)
    Rs2 = R_strict(Rs)
    idem_strict = (Rs.shape == Rs2.shape) and np.array_equal(Rs, Rs2)
    Vrs, Ers, b1rs, _, _ = graph_invariants(Rs)
    out["R_strict_on_Mcore"] = dict(V=Vrs, E=Ers, b1=b1rs, idempotent=bool(idem_strict))
    print(f"[R_strict M_core] V={Vrs} E={Ers} b1={b1rs} idempotent={idem_strict}")

    # ===================================================================
    # 支柱 2: 深度->本体 还原 (lift 多深度 -> R_strict -> Q3)
    # ===================================================================
    lift_tests = {}
    for lvl in [1, 2]:
        L = z2_lift(Q, levels=lvl)
        Vl, El, b1l, _, _ = graph_invariants(L)
        Rl = R_strict(L)
        Vrl, Erl, b1rl, biprl, grl = graph_invariants(Rl)
        rec = (Vrl, Erl, b1rl) == (Vq, Eq, b1q) and nx.is_isomorphic(
            nx.from_numpy_array((np.fill_diagonal(Rl.copy(),0) or Rl)!=0),
            nx.from_numpy_array((np.fill_diagonal(Q.copy(),0) or Q)!=0))
        lift_tests[f"lift_lvl{lvl}"] = dict(lift_V=Vl, lift_E=El, lift_b1=b1l,
                                           R_V=Vrl, R_E=Erl, R_b1=b1rl,
                                           bipartite=biprl, girth=grl, recovered=bool(rec))
        print(f"[R_strict lift({lvl})] lift V={Vl} E={El} -> R V={Vrl} E={Erl} b1={b1rl} recovered={rec}")
    out["R_strict_lift_recovery"] = lift_tests

    # ===================================================================
    # 支柱 3: R_eps 收敛性 (单调性+终止+不动点) 在 M_core 上做 eps 扫描
    # ===================================================================
    eps_sweep = {}
    for eps in [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5]:
        Rc, traj = R_eps(Mcore, eps)
        Vr, Er, b1r, bipr, gr = graph_invariants(Rc)
        monotone = all(traj[i] >= traj[i + 1] for i in range(len(traj) - 1))
        # 验证不动点: 再走一步不变
        Rc2, _ = R_eps(Rc, eps)
        fixed = (Rc2.shape == Rc.shape) and np.array_equal(Rc2, Rc)
        is_q3 = (Vr, Er, b1r) == (Vq, Eq, b1q)
        eps_sweep[str(eps)] = dict(final_V=Vr, final_E=Er, final_b1=b1r,
                                   bipartite=bipr, girth=gr, cubic=is_cubic(Rc),
                                   monotone=bool(monotone), fixed_point=bool(fixed),
                                   is_Q3=bool(is_q3), steps=len(traj) - 1,
                                   traj_head=traj[:12])
        print(f"[R_eps eps={eps}] -> V={Vr} E={Er} b1={b1r} cubic={is_cubic(Rc)} "
              f"monotone={monotone} fixed={fixed} isQ3={is_q3} steps={len(traj)-1}")
    out["R_eps_eps_sweep_Mcore"] = eps_sweep

    # ===================================================================
    # 支柱 4: R_eps 在合成深结构上收敛到 Q3 (lift(Q3) 上松弛合并还原)
    # ===================================================================
    L = z2_lift(Q, levels=1)
    eps_best = None
    for eps in [0.0, 0.05, 0.1, 0.15, 0.2]:
        Rc, _ = R_eps(L, eps)
        Vr, Er, b1r, _, _ = graph_invariants(Rc)
        if (Vr, Er, b1r) == (Vq, Eq, b1q):
            eps_best = eps
            break
    if eps_best is not None:
        Rc, traj = R_eps(L, eps_best)
        rec = nx.is_isomorphic(
            nx.from_numpy_array((np.fill_diagonal(Rc.copy(),0) or Rc)!=0),
            nx.from_numpy_array((np.fill_diagonal(Q.copy(),0) or Q)!=0))
        out["R_eps_lift_recovery"] = dict(eps=eps_best, final_V=Rc.shape[0],
                                          final_E=graph_invariants(Rc)[1],
                                          final_b1=graph_invariants(Rc)[2],
                                          recovered=bool(rec), traj=traj)
        print(f"[R_eps lift recovery] eps={eps_best} -> Q3 recovered={rec} traj={traj}")
    else:
        out["R_eps_lift_recovery"] = dict(note="no eps in [0,0.2] recovers Q3 from lift")

    # 持久化
    with open("sre_r2_convergence_results.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\n[OK] sre_r2_convergence_results.json written")

if __name__ == "__main__":
    main()
