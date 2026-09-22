"""
Operator 12: Topological Closed-Loop Audit (v1.1)
=================================================

通过简单环枚举 + SRE 符号矩阵相位审计，检测
"N 尺度拓扑闭合环 + Möbius 双层相位" 模式。

SRE 理论将电子描述为"N 尺度拓扑闭合环，Möbius 双层相位"。
在分子图中，这对应于：
  - 化学环结构（苯环 6 元环、环氧 3 元环等）→ 拓扑闭合环
  - Möbius 相位 → 2N 步回溯才恢复对称性 → 自旋 1/2 特征

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v1.1 修正（D3）：消除回溯污染 / 谱假阳性
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

原版用 trace(A^k) 闭合行走 + R(k) 比判环，在全连通加权图上
出现假阳性（乙醇开链被判有环）。v1.1 改用：

  1. n_loops 由简单环枚举（DFS，无回溯、方向去重）直接计数
     - 乙醇 = 0，苯环 = 1
     - 无全连通距离核导致的虚假三角形

  2. mobius_ratio 在 SRE 符号矩阵 M 上定义（定理 12.3）：
     mobius_ratio = mean_{k=3..N_max} |tr(M^k)| / n^k
     - =1 ⟺ 无 Möbius 相位（完全符号平衡）
     - <1 ⟺ 有 Möbius 相位（电子自旋特征存在）

  3. 环上子图谱量（定义 5.4）：
     lambda_2_loop = λ2(L_q[S,S])，S = 环原子并集
     定理 12.5 交错不等式：λ2_loop >= λ2_q > 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
输入 / 输出
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

输入:
    A_q  : 电荷加权邻接矩阵（Operator 11 输出）
    M    : SRE 符号矩阵（+-1 无零元）；为 None 时由 A_q 支撑反推
    N_max: 最大环长度（默认 min(N, 8)）

输出 (dict):
    n_loops        : 简单环计数（定义 5.2）
    mobius_ratio   : Möbius 相位比（定义 5.3）
    lambda_2_loop  : 环原子子图 Fiedler 值（定义 5.4）
    kappa_loop    : 环原子子图条件数 (λmax/λ2)
    loop_atoms     : 参与环的原子索引列表

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
与 SRE 电子拓扑理论的对应关系
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SRE 理论                          Operator 12 实现
──────────────                    ─────────────────────
N 尺度拓扑闭合环                  n_loops（简单环计数）
[A₁,...,A_N] 回溯因果             DFS 环枚举（无回溯污染）
Möbius 双层相位                    mobius_ratio = |tr(M^k)| / n^k
2N 步恢复对称性                    mobius_ratio < 1 → 需双倍周期
自旋 1/2 涌现                      mobius_ratio ≠ 1 的统计涌现
电荷 = 拓扑偏置                    A_q 中电负性调制的边权重偏置

自测: python Operator_12_P.py
依赖: numpy（共享工具函数自包含）
"""

import numpy as np


def sre_sign_matrix(A_s: np.ndarray) -> np.ndarray:
    """
    由平滑邻接支撑反推 SRE 符号矩阵 M：
    M_ij = +1 若 A_s_ij > 0（协同边），否则 -1；对角 +1。
    （公理 1：M 元素 ∈ {+1, -1}，无零元）
    """
    M = np.where(A_s > 0, 1.0, -1.0)
    np.fill_diagonal(M, 1.0)
    return M


# ─── Operator 12: Topological Closed-Loop Audit (v1.1) ────────────────

def enumerate_simple_cycles(adj: np.ndarray, N_max: int) -> list:
    """
    DFS 枚举长度 <= N_max 的简单环（无向图）。

    无回溯（路径内顶点不重复）、无重复计数（每个环以其最小顶点
    为起点枚举一次；正反两个方向按规范表示去重）。
    复杂度对稀疏分子图（|E| ~ O(n)）为 O(n · 2^{N_max})，
    N_max <= 8 时开销可忽略。
    """
    n = adj.shape[0]
    supp = adj > 1e-12
    cycles_raw = []
    for s in range(n):
        path = [s]

        def dfs(u):
            if len(path) >= 3 and len(path) <= N_max and supp[u, s]:
                cycles_raw.append(list(path))
            if len(path) >= N_max:
                return
            for v in range(s + 1, n):
                if supp[u, v] and v not in path:
                    path.append(v)
                    dfs(v)
                    path.pop()

        dfs(s)
    seen, cycles = set(), []
    for c in cycles_raw:
        m = min(c)
        k = c.index(m)
        rot = c[k:] + c[:k]
        rev = [rot[0]] + rot[:0:-1]
        key = min(tuple(rot), tuple(rev))
        if key not in seen:
            seen.add(key)
            cycles.append(c)
    return cycles


def operator_12_closed_loop_audit(A_q: np.ndarray,
                                  M: np.ndarray = None,
                                  N_max: int = None) -> dict:
    """
    Operator 12 — Topological Closed-Loop Audit（v1.1 规范式 (5.1)-(5.4)）。

    n_loops       = 简单环计数（定义 5.2；定理 12.2 消除回溯污染）
    mobius_ratio  = mean_{k=3..N_max} |tr(M^k)| / n^k（定义 5.3；
                    定理 12.3 符号平衡判据：=1 ⟺ 无 Möbius，<1 ⟺ 有）
    lambda_2_loop = λ2(L_q[S,S])，S = 环原子并集（定义 5.4；
                    定理 12.5 交错：λ2_loop >= λ2_q > 0）
    kappa_loop    = λmax(L_q[S,S]) / λ2(L_q[S,S])（<= kappa_q）

    参数:
        A_q  : 电荷加权邻接矩阵（Operator 11 输出）
        M    : SRE 符号矩阵（+-1 无零元）；为 None 时由 A_q 支撑反推
        N_max: 最大环长度枚举上限（默认 min(N, 8)）

    返回 (dict):
        n_loops, n_closed_loops, mobius_ratio,
        lambda_2_loop, kappa_loop, loop_atoms
    """
    N = A_q.shape[0]
    if N_max is None:
        N_max = min(N, 8)
    if M is None:
        M = sre_sign_matrix(A_q)

    cycles = enumerate_simple_cycles(A_q, N_max)
    n_loops = len(cycles)
    loop_atoms = sorted(set(v for c in cycles for v in c))

    # Möbius 相位比（定义 5.3）：在符号矩阵 M 上，|tr(M^k)| / n^k
    ratios = []
    for k in range(3, N_max + 1):
        Mk = np.linalg.matrix_power(M, k)
        tau = np.trace(Mk)
        ratios.append(abs(tau) / float(N ** k))
    mobius_ratio = float(np.mean(ratios)) if ratios else 1.0

    # 环上子图谱量（定义 5.4）
    if len(loop_atoms) >= 3:
        deg = A_q.sum(axis=1)
        L_q = np.diag(deg) - A_q
        sub = np.ix_(loop_atoms, loop_atoms)
        L_loop = L_q[sub]
        ev = np.linalg.eigvalsh(L_loop)
        lambda_2_loop = float(ev[1])
        kappa_loop = float(ev[-1] / ev[1]) if ev[1] > 1e-12 else float("inf")
    else:
        lambda_2_loop = float("nan")
        kappa_loop = float("nan")

    return {
        "n_loops": n_loops,
        "n_closed_loops": n_loops,
        "mobius_ratio": mobius_ratio,
        "lambda_2_loop": lambda_2_loop,
        "kappa_loop": kappa_loop,
        "loop_atoms": loop_atoms,
    }


# ─── Self-test ────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Operator 12: Topological Closed-Loop Audit (v1.1) Self-Test ===\n")

    # ── 乙醇（开链，β1 = 0）──────────────────────────────────────────
    # 构建乙醇的 A_q（简化：直接用化学键邻接作为 A_q）
    ethanol_bonds = [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 6), (1, 7), (2, 8)]
    n_atoms = 9
    A_q_ethanol = np.zeros((n_atoms, n_atoms))
    for i, j in ethanol_bonds:
        A_q_ethanol[i, j] = A_q_ethanol[j, i] = 1.0

    print("--- Ethanol (open chain, expect n_loops=0) ---")
    M_ethanol = sre_sign_matrix(A_q_ethanol)
    result_ethanol = operator_12_closed_loop_audit(A_q_ethanol, M_ethanol, N_max=8)
    print("  n_loops=%d  mobius_ratio=%.6f  lambda_2_loop=%s"
          % (result_ethanol["n_loops"], result_ethanol["mobius_ratio"],
             "NaN" if np.isnan(result_ethanol["lambda_2_loop"])
             else "%.6f" % result_ethanol["lambda_2_loop"]))

    # ── 苯环（单环，β1 = 1）──────────────────────────────────────────
    benz_bonds = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0)]
    n_benz = 6
    A_q_benz = np.zeros((n_benz, n_benz))
    for i, j in benz_bonds:
        A_q_benz[i, j] = A_q_benz[j, i] = 1.0

    print("\n--- Benzene Ring (6C, expect n_loops=1) ---")
    M_benz = sre_sign_matrix(A_q_benz)
    result_benz = operator_12_closed_loop_audit(A_q_benz, M_benz, N_max=8)
    print("  n_loops=%d  mobius_ratio=%.6f  lambda_2_loop=%.6f  kappa_loop=%.6f"
          % (result_benz["n_loops"], result_benz["mobius_ratio"],
             result_benz["lambda_2_loop"], result_benz["kappa_loop"]))

    # ── 断言 ──────────────────────────────────────────────────────────
    fails = []
    def check(desc, cond):
        print(("  [PASS] " if cond else "  [FAIL] ") + desc)
        if not cond:
            fails.append(desc)

    print("\n--- Assertions ---")
    check("乙醇 n_loops = 0（定理 12.2/12.4）", result_ethanol["n_loops"] == 0)
    check("苯环 n_loops = 1 = beta_1（定理 12.4）", result_benz["n_loops"] == 1)
    check("苯环 lambda_2_loop > 0（定理 12.5）", result_benz["lambda_2_loop"] > 0)

    print("\n" + ("All operator 12 self-tests passed."
                  if not fails else "Failed: %s" % fails))
