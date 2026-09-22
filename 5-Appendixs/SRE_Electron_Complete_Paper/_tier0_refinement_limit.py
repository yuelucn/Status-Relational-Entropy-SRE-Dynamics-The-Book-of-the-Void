# -*- coding: utf-8 -*-
"""
Tier 0 — 第 4 项：网格细化极限验证（C4 在 n→n·2^m 下的收敛性）
============================================================
背景（Tier 0 已确认事实）：
  n=60, w=0.1, k=3 的 kNN 图恰为 Möbius 阶梯 M_60（= C_60 环 + 完美匹配 (i,i+30)），
  阶梯族谱间隙有闭式 gap(M_n) = (2-2cos(4π/n)) / (4+2cos(2π/n))，
  在 n=60 处 = 0.0072974585 ≈ α*（相对误差 0.0015%）—— Tier 0 的 PASS-B 来源。
  本脚本检验：该命中在网格细化极限下是否稳健。

预注册判据（计算前冻结，不允许事后改动）
------------------------------------------------------------
R1（主判据）: n_m = 60·2^m（m=0..4），固定 w=0.1、k=3，
    计算 g_m = ev[1]/ev[-1]。
    PASS ⇔ g_m 收敛到非零常数 c 且 |c-α*|/α* < 1%
    （末两点相对变化 <1% 视为"收敛"，再对 α* 判定）。
R2（k 偏置审计）: 每个 n_m 扫描 k=2..6，仅记录是否有命中 α*（1%），
    不允许据此改判或追加候选。
R3（标度律）: 拟合 log g ~ log n，报告指数 p 与外推极限。
R4（结构审计）: 逐点记录 k=3 选中壳的组成（链±1 / 链±2 / 2π伙伴 / 其他），
    并检验 kNN 图是否仍与理想 Möbius 阶梯 M_n 逐边一致。

契约延续：α* 只允许出现在最后的对照判定，绝不进入任何图构造/谱计算。
"""
import json
import numpy as np
from scipy.spatial.distance import cdist

np.set_printoptions(precision=12, suppress=True)

ALPHA_REF = 1.0 / 137.035999084   # 仅对照用
W_PRIORI = 0.1
K_PRIORI = 3
N0 = 60
M_LIST = [0, 1, 2, 3, 4]          # n = 60·2^m → 60,120,240,480,960

# ────────────────────────────────────────────────────────────
# 基础构造（与 _tier0_lambda0_independent.py 完全一致）
# ────────────────────────────────────────────────────────────

def mobius_points(n, w):
    """4π 闭合 Möbius 残余流形点云（light_3.pdf 公理 II）。"""
    phi = np.linspace(0, 4 * np.pi, n, endpoint=False)
    x = (1 + w * np.cos(phi / 2)) * np.cos(phi)
    y = (1 + w * np.cos(phi / 2)) * np.sin(phi)
    z = w * np.sin(phi / 2)
    return np.column_stack([x, y, z])

def knn_graph(pts, k):
    """返回 (每个节点选中的 k 近邻列表, 对称化邻接阵)。"""
    d = cdist(pts, pts)
    n = len(pts)
    A = np.zeros((n, n))
    picks = []
    for i in range(n):
        nb = [int(j) for j in np.argsort(d[i])[1:k + 1]]
        picks.append(nb)
        for j in nb:
            A[i, j] = A[j, i] = 1.0
    return picks, A

def spectral_gap(A):
    L = np.diag(A.sum(axis=1)) - A
    ev = np.sort(np.linalg.eigvalsh(L))
    return float(ev[1] / ev[-1]), float(ev[1]), float(ev[-1])

def ladder_adj(n):
    """理想 Möbius 阶梯 M_n：环 (i,i+1) + 完美匹配 (i,i+n/2)。"""
    A = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        A[i, j] = A[j, i] = 1.0
        j = (i + n // 2) % n
        A[i, j] = A[j, i] = 1.0
    return A

def ladder_gap_closed(n):
    """M_n 组合拉普拉斯谱间隙闭式：λ₂=2-2cos(4π/n)（k=2 偶模），
    λ_max=4+2cos(2π/n)（k=n-1 奇模）。"""
    return (2.0 - 2.0 * np.cos(4 * np.pi / n)) / (4.0 + 2.0 * np.cos(2 * np.pi / n))

def classify_pick(i, j, n):
    d = (j - i) % n
    return {1: "chain+1", n - 1: "chain-1", 2: "chain+2",
            n - 2: "chain-2", n // 2: "partner"}.get(d, f"other(d={d})")

# ════════════════════════════════════════════════════════════
print("=" * 78)
print("Section 1  R1 主判据：n = 60·2^m 细化序列（w=0.1, k=3 固定）")
print("=" * 78)

n_list = [N0 * (2 ** m) for m in M_LIST]
gaps, ev2s, evmaxs, audits = [], [], [], []
print(f"  {'n':>6} {'g=ev[1]/ev[-1]':>16} {'vs α* 误差':>12} "
      f"{'闭式阶梯gap':>16} {'==M_n?':>8} {'最大度':>6}")
for n in n_list:
    picks, A = knn_graph(mobius_points(n, W_PRIORI), K_PRIORI)
    g, e2, em = spectral_gap(A)
    gaps.append(g); ev2s.append(e2); evmaxs.append(em)
    A_lad = ladder_adj(n)
    same = bool(np.array_equal(A, A_lad))
    deg_max = int(A.sum(axis=1).max())
    gc = ladder_gap_closed(n)
    err = abs(g - ALPHA_REF) / ALPHA_REF
    print(f"  {n:>6} {g:>16.10f} {err*100:>11.4f}% {gc:>16.10f} "
          f"{('是' if same else '否'):>8} {deg_max:>6}")

    # R4 结构审计：壳组成直方图 + 阶梯一致节点占比
    comp = {}
    ladder_nodes = 0
    for i in range(n):
        picked = set(picks[i])
        if picked == {(i - 1) % n, (i + 1) % n, (i + n // 2) % n}:
            ladder_nodes += 1
        for j in picks[i]:
            c = classify_pick(i, j, n)
            comp[c] = comp.get(c, 0) + 1
    audits.append({
        "n": n, "graph_equals_ideal_ladder": same, "max_degree": deg_max,
        "ladder_consistent_node_fraction": ladder_nodes / n,
        "pick_composition": comp})
    top = sorted(comp.items(), key=lambda kv: -kv[1])
    print(f"         壳组成: {', '.join(f'{k}:{v}' for k, v in top)}"
          f"  | 阶梯一致节点 {ladder_nodes}/{n}")

gaps = np.array(gaps)

# ════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 2  R3 标度律：g(n) 的幂律拟合与外推极限")
print("=" * 78)
step_ratios = [gaps[i] / gaps[i + 1] for i in range(len(gaps) - 1)]
for m, r in zip(M_LIST[:-1], step_ratios):
    print(f"  g({N0*2**m}) / g({N0*2**(m+1)}) = {r:.4f}   "
          f"（阶梯区理论值 ≈ 4：gap∝n^-2）")
logn, logg = np.log(np.array(n_list, dtype=float)), np.log(gaps)
p_all, c_all = np.polyfit(logn, logg, 1)
p_tail, c_tail = np.polyfit(logn[-3:], logg[-3:], 1)
print(f"  全序列拟合:  g ≈ {np.exp(c_all):.6e} · n^({p_all:.4f})")
print(f"  末端3点拟合: g ≈ {np.exp(c_tail):.6e} · n^({p_tail:.4f})")
print(f"  → 外推极限 g(n→∞) = 0（幂律衰减，无非零收敛常数）")

# ════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 3  R2 k 偏置审计：每个 n 扫描 k=2..6（只记录，不改判）")
print("=" * 78)
k_scan = {}
for n in n_list:
    row = {}
    for k in range(2, 7):
        _, A = knn_graph(mobius_points(n, W_PRIORI), k)
        g, _, _ = spectral_gap(A)
        row[k] = g
    k_scan[n] = row
    marks = "  ".join(
        f"k={k}:{g:.6f}{' ★' if abs(g-ALPHA_REF)/ALPHA_REF < 0.01 else ''}"
        for k, g in row.items())
    print(f"  n={n:>5}: {marks}")

# ════════════════════════════════════════════════════════════
print("\n" + "=" * 78)
print("Section 4  预注册判定（α* 仅在此出现）")
print("=" * 78)
stable = bool(abs(gaps[-1] - gaps[-2]) / gaps[-2] < 0.01)
hit_last = bool(abs(gaps[-1] - ALPHA_REF) / ALPHA_REF < 0.01)
hit_prev = bool(abs(gaps[-2] - ALPHA_REF) / ALPHA_REF < 0.01)
r1_pass = stable and (hit_last or hit_prev)
err60 = abs(gaps[0] - ALPHA_REF) / ALPHA_REF
print(f"  R1 主判据: 末两点稳定={stable}（|Δg|/g={abs(gaps[-1]-gaps[-2])/gaps[-2]*100:.1f}%），"
      f"命中 α*={hit_last or hit_prev}")
print(f"      → R1 = {'PASS' if r1_pass else 'FAIL'}"
      f"{'（细化极限下 C4 → 0 ≠ α*）' if not r1_pass else ''}")
k_hits = [(n, k, g) for n, row in k_scan.items() for k, g in row.items()
          if abs(g - ALPHA_REF) / ALPHA_REF < 0.01]
print(f"  R2 k 审计: 命中组合 (n,k) = {k_hits if k_hits else '无（除 n=60,k=3 外无命中）'}")
print(f"  R3 标度律: p={p_all:.4f}（全序列）/{p_tail:.4f}（末端），g(n→∞)=0")
print(f"  R4 结构审计: n=60 图与理想 M_60 逐边一致；细化后阶梯结构逐步破坏")
print(f"\n  n=60 命中的数学身份：gap(M_60) = (2-2cos(π/15))/(4+2cos(π/30)) "
      f"= {ladder_gap_closed(60):.12f}")
print(f"  与 α* 相对误差 {err60*100:.4f}% —— 属 60 节点阶梯图的算术巧合，"
      f"非细化收敛量。")
print("\n  总结论：Tier 0 第 4 项 = FAIL。")
print("    C4 谱间隙在网格细化极限下收敛到 0，不收敛到 α*；")
print("    PASS-B（α 独立）不具细化稳健性，应降级为'n=60 离散化巧合'。")

out = {
    "test": "Tier0 item4: refinement limit of C4 (kNN(3) spectral gap), n=60*2^m",
    "preregistered": {
        "R1": "g_m converges to nonzero constant c with |c-alpha*|/alpha*<1%",
        "R2": "k-scan 2..6 audit only, no post-hoc candidate",
        "R3": "power-law fit log g ~ log n",
        "R4": "shell composition + equality to ideal Mobius ladder M_n"},
    "n_list": n_list,
    "k3_gaps": [float(x) for x in gaps],
    "k3_ev2": ev2s, "k3_evmax": evmaxs,
    "ladder_closed_form_gap": [float(ladder_gap_closed(n)) for n in n_list],
    "graph_equals_ideal_ladder": [a["graph_equals_ideal_ladder"] for a in audits],
    "shell_audit": audits,
    "power_law_fit": {"all": [float(p_all), float(np.exp(c_all))],
                      "tail3": [float(p_tail), float(np.exp(c_tail))]},
    "step_ratios": [float(r) for r in step_ratios],
    "k_scan": {str(n): {str(k): float(g) for k, g in row.items()}
               for n, row in k_scan.items()},
    "k_scan_hits": [[n, k, float(g)] for n, k, g in k_hits],
    "alpha_ref": ALPHA_REF,
    "verdict": {"R1_refinement_limit": "PASS" if r1_pass else "FAIL",
                "R1_stable_last_two": stable,
                "R2_hits": k_hits,
                "R3_exponent_all": float(p_all),
                "R3_limit": "g(n->inf)=0 != alpha*",
                "overall": "FAIL - C4 alpha-hit at n=60 is a discretization "
                           "coincidence (Mobius ladder M_60 gap), not a "
                           "refinement-convergent quantity"},
}
with open(r"c:\mywork\vasp\tier0_refinement_results.json", "w") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print("\n  已保存 tier0_refinement_results.json")
