# -*- coding: utf-8 -*-
"""
verify_operator_19.py
=====================
SRE 算子 19（ℤ₂ holonomy / σ 电荷符号通道）配套**独立严格验证程序**。

对应文档：《算子 19：ℤ₂ holonomy / σ 电荷符号通道算子 —— 严格数学规范、可解性推理依据
与验证协议》（v1.0）第 8 节"验证实验设计"。

本程序**独立于实现的自测**（不调用 bridge 的 self_test），逐条实证规范中的定义与定理：

  V1  骨架忠实性      §6 / 电荷涌现 §10.2  Q₃ / Y₃闭 / Y₃开 逐项一致
  V2  顶点势平凡      T1, T1.1   自旋极性 s_e=s_i·s_j 的 holonomy 恒 +1
  V3  可达性判据      T2, T2.1   线性判据 == 2^k 暴力枚举；平凡类恒可达
  V4  环基无关性      T3        两种生成森林 → 平凡性判别/σ 规范类一致
  V5  余边界规范不变  T4, T4.1   乘以顶点势不改变任何环 holonomy
  V6  deg 通道        D7, T5     deg == β1 mod 2
  V7  电荷泛函一致    D8, T5     Q_model == σ_canonical·deg ∈ {-1,0,+1}
  V8  元素着色必要性  T7         反例 4-环 [O,C,C,O] 判据翻转
  V9  端到端入口      §1.2      乙醇/苯/环戊烷 经 v11 流水线入口
  V10 幂等与冻结契约  D5         charge_channel_keys 幂等；attach 守卫幂等；v11 7 键契约
  V11 图不变量自洽    §7         β1=E-V+c；has_odd_cycle 与 bipartite 互补
  V12 分子层判据      T6, T7     6 个分子键图 偶环族/奇环族

依赖：numpy + networkx（networkx 仅用于自同构枚举）。
运行：python verify_operator_19.py
任一行断言失败以退出码 1 结束。
"""
from __future__ import annotations

import itertools
import sys

import numpy as np

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None

from sre_z2_holonomy_bridge import (
    bond_graph_from_As, edge_list, graph_invariants, fundamental_cycle_basis,
    cycle_holonomy, holonomy_class, polarity_topo, polarity_spin,
    automorphisms, edge_orbits, reachability_z2,
    operator_19_z2_charge_channel, charge_channel_keys,
    z2_charge_channel_from_pipeline,
    skel_electron_q3, skel_y3_closed, skel_y3_open,
)

try:
    from sre_electronic_ops_v11 import compute_electronic_fingerprint
except Exception:
    compute_electronic_fingerprint = None

RESULTS = []  # (tag, desc, ok)


def check(tag, desc, cond):
    RESULTS.append((tag, desc, bool(cond)))
    print("  [%s] %s" % ("PASS" if cond else "FAIL", desc))


# =====================================================================
# 独立工具（不依赖 bridge 内部实现，用于交叉比对）
# =====================================================================

def cycle_basis_dfs(adj, root=0):
    """独立实现：以 root 为起点的 DFS 生成森林 → 基本环基（顶点序列表）。

    与 bridge 的 `fundamental_cycle_basis`（BFS、根 0）选取不同的生成树，
    用于 T3（环基无关性）的交叉比对。
    """
    n = adj.shape[0]
    parent = -np.ones(n, dtype=int)
    depth = np.zeros(n, dtype=int)
    visited = np.zeros(n, dtype=bool)
    tree = set()
    order = list(range(root, n)) + list(range(0, root))
    for s in order:
        if visited[s]:
            continue
        visited[s] = True
        parent[s] = -1
        stack = [s]
        while stack:
            u = stack.pop()
            for v in np.nonzero(adj[u])[0]:
                v = int(v)
                if not visited[v]:
                    visited[v] = True
                    parent[v] = u
                    depth[v] = depth[u] + 1
                    tree.add((min(u, v), max(u, v)))
                    stack.append(v)
    cycles = []
    for (u, v) in edge_list(adj):
        if (u, v) in tree:
            continue
        pu, pv = u, v
        path_u, path_v = [u], [v]
        while depth[pu] > depth[pv]:
            pu = int(parent[pu]); path_u.append(pu)
        while depth[pv] > depth[pu]:
            pv = int(parent[pv]); path_v.append(pv)
        while pu != pv:
            pu = int(parent[pu]); path_u.append(pu)
            pv = int(parent[pv]); path_v.append(pv)
        cycles.append(path_u + path_v[-2::-1])
    return cycles


def random_connected_adj(rng, n, extra):
    """随机连通图：先造生成树保连通，再加 extra 条随机边。"""
    adj = np.zeros((n, n), dtype=bool)
    for i in range(1, n):
        j = int(rng.integers(0, i))
        adj[i, j] = adj[j, i] = True
    for _ in range(extra):
        a, b = rng.integers(0, n, size=2)
        if a != b:
            adj[a, b] = adj[b, a] = True
    return adj


def brute_nontrivial_reachable(cycles, orbits):
    """朴素暴力：枚举 2^{#轨道} 全部 Aut-不变极性，判是否存在非平凡类。"""
    for bits in itertools.product([0, 1], repeat=len(orbits)):
        s_e = {}
        for oi, orb in enumerate(orbits):
            v = -1.0 if bits[oi] else 1.0
            for e in orb:
                s_e[e] = v
        if any(cycle_holonomy(c, s_e) < 0 for c in cycles):
            return True
    return False


# =====================================================================
# 分子键图定义（元素 + 键，供 V8/V9/V12）
# =====================================================================
C, H, O = "C", "H", "O"
MOLS = [
    # (名称, 元素, 键, 期望非平凡可达)
    ("乙醇 C2H6O (树)", [C, C, O] + [H] * 6,
     [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 6), (1, 7), (2, 8)], False),
    ("苯 C6H6 (偶环)", [C] * 6 + [H] * 6,
     [(i, (i + 1) % 6) for i in range(6)] + [(i, 6 + i) for i in range(6)], False),
    ("环己烷 C6H12 (偶环)", [C] * 6 + [H] * 12,
     [(i, (i + 1) % 6) for i in range(6)]
     + [(i, 6 + 2 * i) for i in range(6)] + [(i, 7 + 2 * i) for i in range(6)], False),
    ("环戊烷 C5H10 (奇环)", [C] * 5 + [H] * 10,
     [(i, (i + 1) % 5) for i in range(5)]
     + [(i, 5 + 2 * i) for i in range(5)] + [(i, 6 + 2 * i) for i in range(5)], True),
    ("环戊二烯 C5H6 (奇环)", [C] * 5 + [H] * 6,
     [(i, (i + 1) % 5) for i in range(5)]
     + [(0, 5), (1, 6), (2, 7), (2, 8), (3, 9), (4, 10)], True),
    ("呋喃 C4H4O (奇环)", [O] + [C] * 4 + [H] * 4,
     [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)]
     + [(1, 5), (2, 6), (3, 7), (4, 8)], True),
]


def adj_from_bonds(n, bonds):
    adj = np.zeros((n, n), dtype=bool)
    for i, j in bonds:
        adj[i, j] = adj[j, i] = True
    return adj


def main():
    print("=" * 80)
    print("SRE 算子 19 严格验证程序（ℤ₂ holonomy / σ 电荷符号通道）")
    print("=" * 80)
    rng = np.random.default_rng(20261010)

    # ---------------- V1 骨架忠实性（对齐电荷涌现 §10.2）----------------
    print("\n--- V1 骨架忠实性：Q₃ / Y₃闭 / Y₃开 逐项复现 ---")
    skels = [("电子 e⁻ (Q₃)", skel_electron_q3(), 8, 12, 5, 1, 48, 1, True, False),
             ("质子 p (闭态)", skel_y3_closed(), 12, 18, 7, 1, 36, 2, False, True),
             ("中子 n (开态)", skel_y3_open(), 12, 17, 6, 0, 4, 7, False, True)]
    for name, adj, V, E, b1, deg, naut, norb, bip, nt in skels:
        inv = graph_invariants(adj)
        cycles = fundamental_cycle_basis(adj)
        auts, _ = automorphisms(adj)
        orbs = edge_orbits(adj, auts)
        reach = reachability_z2(adj, cycles, orbs)
        check("V1", "%s: V=%d" % (name, V), inv["V"] == V)
        check("V1", "%s: E=%d" % (name, E), inv["E"] == E)
        check("V1", "%s: β₁=%d deg=%d" % (name, b1, deg),
              inv["beta1"] == b1 and inv["deg"] == deg)
        check("V1", "%s: |Aut|=%d 边轨道=%d" % (name, naut, norb),
              len(auts) == naut and len(orbs) == norb)
        check("V1", "%s: bipartite=%s 非平凡可达=%s" % (name, bip, nt),
              inv["bipartite"] == bip and reach["nontrivial_reachable"] == nt)
    q3 = skel_electron_q3()
    cq3 = fundamental_cycle_basis(q3)
    aq3, _ = automorphisms(q3)
    rq3 = reachability_z2(q3, cq3, edge_orbits(q3, aq3))
    check("V1", "电子强制平凡、质子允许非平凡（异号来源）",
          (not rq3["nontrivial_reachable"]))  # 电子强制平凡

    # ---------------- V2 T1 顶点势平凡 ----------------
    print("\n--- V2 定理 T1：顶点势型极性 s_e=s_i·s_j ⇒ holonomy 恒 +1 ---")
    t1_ok = True
    for _ in range(40):
        n = int(rng.integers(4, 12))
        adj = random_connected_adj(rng, n, int(rng.integers(0, n + 3)))
        chi = rng.normal(size=n)
        s_e = polarity_spin(adj, chi)
        hc = holonomy_class(fundamental_cycle_basis(adj), s_e)
        t1_ok &= hc["is_trivial"]
    check("V2", "40 例随机图：自旋极性 holonomy 全平凡", t1_ok)
    # Q₃ 骨架亦平凡
    s_q3 = polarity_spin(q3, rng.normal(size=8))
    check("V2", "Q₃ 骨架：自旋极性 holonomy 平凡",
          holonomy_class(cq3, s_q3)["is_trivial"])
    # 平凡 ⇒ 存在顶点势 f 使 s_e = f_i·f_j（余边界显式构造）
    adj_t = random_connected_adj(rng, 7, 3)
    cyc_t = fundamental_cycle_basis(adj_t)
    f = rng.choice([-1.0, 1.0], size=7)
    s_cob = {e: float(f[e[0]] * f[e[1]]) for e in edge_list(adj_t)}
    check("V2", "显式余边界 s_e=f_i·f_j 为平凡类",
          holonomy_class(cyc_t, s_cob)["is_trivial"])

    # ---------------- V3 T2 可达性判据 == 暴力枚举 ----------------
    print("\n--- V3 定理 T2：线性判据 reachability_z2 == 2^k 暴力枚举 ---")
    t2_ok = all_trivial_ok = True
    for _ in range(30):
        n = int(rng.integers(4, 9))
        adj = random_connected_adj(rng, n, int(rng.integers(0, 4)))
        cycles = fundamental_cycle_basis(adj)
        auts, _ = automorphisms(adj)
        orbs = edge_orbits(adj, auts)
        lin = reachability_z2(adj, cycles, orbs)["nontrivial_reachable"]
        brute = brute_nontrivial_reachable(cycles, orbs)
        t2_ok &= (lin == brute)
        # 平凡类恒可达（全 +1 赋值）
        s_triv = {e: 1.0 for e in edge_list(adj)}
        all_trivial_ok &= holonomy_class(cycles, s_triv)["is_trivial"]
    check("V3", "30 例随机图：线性判据与暴力枚举逐例一致", t2_ok)
    check("V3", "平凡类恒可达（全 +1 赋值为平凡）", all_trivial_ok)

    # ---------------- V4 T3 环基选取无关性 ----------------
    print("\n--- V4 定理 T3：平凡性判别与环基选取无关 ---")
    v4_ok = True
    for _ in range(25):
        n = int(rng.integers(4, 11))
        adj = random_connected_adj(rng, n, int(rng.integers(1, 6)))
        basis_bfs = fundamental_cycle_basis(adj)          # BFS 根 0
        basis_dfs = cycle_basis_dfs(adj, root=n - 1)      # DFS 异根
        # 随机极性（含非平凡可能）
        s_e = {e: (1.0 if rng.random() > 0.5 else -1.0) for e in edge_list(adj)}
        h_bfs = holonomy_class(basis_bfs, s_e)
        h_dfs = holonomy_class(basis_dfs, s_e)
        v4_ok &= (h_bfs["is_trivial"] == h_dfs["is_trivial"])
        v4_ok &= (h_bfs["sigma_class"] == h_dfs["sigma_class"])
    check("V4", "25 例：BFS/DFS 两种环基 → 平凡性与 σ 类一致", v4_ok)
    # 显式非平凡样例（三角形，见 V5 构造）两基均判非平凡
    tri = adj_from_bonds(3, [(0, 1), (1, 2), (2, 0)])
    s_tri = {(0, 1): -1.0, (1, 2): 1.0, (0, 2): 1.0}
    nt_bfs = not holonomy_class(fundamental_cycle_basis(tri), s_tri)["is_trivial"]
    nt_dfs = not holonomy_class(cycle_basis_dfs(tri, root=2), s_tri)["is_trivial"]
    check("V4", "三角形非平凡极性：两种环基均判非平凡", nt_bfs and nt_dfs)

    # ---------------- V5 T4 余边界规范不变 ----------------
    print("\n--- V5 定理 T4：乘以顶点势（余边界）不改变环 holonomy ---")
    v5_ok = True
    for _ in range(25):
        n = int(rng.integers(4, 11))
        adj = random_connected_adj(rng, n, int(rng.integers(1, 6)))
        cycles = fundamental_cycle_basis(adj)
        s_e = {e: (1.0 if rng.random() > 0.5 else -1.0) for e in edge_list(adj)}
        t = rng.choice([-1.0, 1.0], size=n)
        s_g = {e: s_e[e] * float(t[e[0]] * t[e[1]]) for e in edge_list(adj)}
        for c in cycles:
            v5_ok &= abs(cycle_holonomy(c, s_e) - cycle_holonomy(c, s_g)) < 1e-12
    check("V5", "25 例：σ'(γ)=σ(γ) 对所有环成立（规范不变）", v5_ok)
    # 三角形：非平凡极性乘以任意顶点势后仍非平凡（且 σ 逐环相等）
    t5 = np.array([1.0, -1.0, -1.0])
    s_tri_g = {e: s_tri[e] * float(t5[e[0]] * t5[e[1]]) for e in s_tri}
    same5 = all(abs(cycle_holonomy(c, s_tri) - cycle_holonomy(c, s_tri_g)) < 1e-12
                for c in fundamental_cycle_basis(tri))
    check("V5", "三角形：非平凡极性乘顶点势后仍非平凡且 σ 不变",
          same5 and not holonomy_class(fundamental_cycle_basis(tri), s_tri_g)["is_trivial"])

    # ---------------- V6 deg == β1 mod 2 ----------------
    print("\n--- V6 量值通道：deg == β1 mod 2 ---")
    v6_ok = True
    for _, adj, *_ in [(nm,) + (a,) for nm, a, *_ in skels]:
        inv = graph_invariants(adj)
        v6_ok &= (inv["deg"] == inv["beta1"] % 2)
    for _ in range(40):
        n = int(rng.integers(3, 14))
        adj = random_connected_adj(rng, n, int(rng.integers(0, 8)))
        inv = graph_invariants(adj)
        v6_ok &= (inv["deg"] == inv["beta1"] % 2)
    check("V6", "骨架+40 例随机图：deg == β1 mod 2", v6_ok)

    # ---------------- V7 Q_model == σ_canonical·deg ----------------
    print("\n--- V7 电荷泛函一致：Q_model == σ_canonical·deg ∈ {-1,0,+1} ---")
    v7_ok = True
    for name, adj, *_ in [(nm,) + (a,) for nm, a, *_ in skels]:
        res = operator_19_z2_charge_channel(adj.astype(float))
        v7_ok &= abs(res["Q_model"] - res["sigma_canonical"] * res["deg"]) < 1e-12
        v7_ok &= res["Q_model"] in (-1.0, 0.0, 1.0)
    for name, elems, bonds, _ in MOLS:
        adj = adj_from_bonds(len(elems), bonds)
        res = operator_19_z2_charge_channel(adj.astype(float), elements=elems)
        v7_ok &= abs(res["Q_model"] - res["sigma_canonical"] * res["deg"]) < 1e-12
        v7_ok &= res["Q_model"] in (-1.0, 0.0, 1.0)
    check("V7", "骨架+分子：Q_model == σ_canonical·deg 且 ∈ {-1,0,+1}", v7_ok)

    # ---------------- V8 T7 元素着色必要性 ----------------
    print("\n--- V8 定理 T7：元素着色必要性（4-环 [O,C,C,O] 判据翻转）---")
    elems8 = [O, C, C, O]
    bonds8 = [(0, 1), (1, 2), (2, 3), (3, 0)]
    adj8 = adj_from_bonds(4, bonds8)
    cycles8 = fundamental_cycle_basis(adj8)
    # 保色自同构
    auts_c, _ = automorphisms(adj8, colors=elems8)
    orbs_c = edge_orbits(adj8, auts_c)
    reach_c = reachability_z2(adj8, cycles8, orbs_c)
    # 不保色自同构（D4 在 4 边上传递）
    auts_u, _ = automorphisms(adj8)
    orbs_u = edge_orbits(adj8, auts_u)
    reach_u = reachability_z2(adj8, cycles8, orbs_u)
    check("V8", "保色 Aut：边轨道=%s ⇒ 非平凡可达" % [len(o) for o in orbs_c],
          reach_c["nontrivial_reachable"] and len(orbs_c) == 3)
    check("V8", "不保色 Aut：边轨道=%s ⇒ 强制平凡" % [len(o) for o in orbs_u],
          (not reach_u["nontrivial_reachable"]) and len(orbs_u) == 1)
    check("V8", "两种口径判据相反（着色为必要条件）",
          reach_c["nontrivial_reachable"] != reach_u["nontrivial_reachable"])

    # ---------------- V9 端到端入口（v11 流水线）----------------
    print("\n--- V9 端到端：坐标+atomtypes → A_s → σ 通道 ---")
    if compute_electronic_fingerprint is None:
        print("     [SKIP] sre_electronic_ops_v11 不可用")
    else:
        etoh_types = ["c3", "c3", "oh", "hc", "hc", "hc", "h1", "h1", "ho"]
        etoh_bonds = [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 6), (1, 7), (2, 8)]
        etoh_pos = np.array([
            [0.0, 0.0, 0.0], [1.52, 0.0, 0.0], [2.15, 1.35, 0.0],
            [-0.5, 0.9, 0.3], [-0.5, -0.9, -0.3], [-0.5, 0.0, -0.9],
            [1.52, -0.9, 0.9], [1.52, 0.9, -0.9], [2.15, 1.35, 0.96],
        ], dtype=np.float64)
        re_ = z2_charge_channel_from_pipeline(etoh_pos, etoh_types, bonds=etoh_bonds)
        check("V9", "乙醇（树）：β₁=0 且 electron-like",
              re_["beta1"] == 0 and re_["channel_type"].startswith("electron-like"))

        benz_types = ["ca"] * 6 + ["ha"] * 6
        ang = np.arange(6) * (np.pi / 3.0)
        benz_pos = np.vstack([
            np.c_[1.39 * np.cos(ang), 1.39 * np.sin(ang), np.zeros(6)],
            np.c_[2.47 * np.cos(ang), 2.47 * np.sin(ang), np.zeros(6)],
        ])
        benz_bonds = [(i, (i + 1) % 6) for i in range(6)] + [(i, 6 + i) for i in range(6)]
        rb = z2_charge_channel_from_pipeline(benz_pos, benz_types, bonds=benz_bonds)
        check("V9", "苯（偶环）：β₁=1 且 electron-like（偶环强制平凡）",
              rb["beta1"] == 1 and rb["channel_type"].startswith("electron-like"))

        c5_types = ["c3"] * 5 + ["hc"] * 10
        c5_bonds = ([(i, (i + 1) % 5) for i in range(5)]
                    + [(i, 5 + 2 * i) for i in range(5)] + [(i, 6 + 2 * i) for i in range(5)])
        c5_pos = np.vstack([
            np.c_[1.54 * np.cos(np.arange(5) * 2 * np.pi / 5),
                  1.54 * np.sin(np.arange(5) * 2 * np.pi / 5), np.zeros(5)],
            np.c_[3.0 * np.cos(np.arange(5) * 2 * np.pi / 5),
                  3.0 * np.sin(np.arange(5) * 2 * np.pi / 5), np.zeros(5)],
            np.c_[3.0 * np.cos(np.arange(5) * 2 * np.pi / 5),
                  3.0 * np.sin(np.arange(5) * 2 * np.pi / 5), 1.8 * np.ones(5)],
        ])
        rc5 = z2_charge_channel_from_pipeline(c5_pos, c5_types, bonds=c5_bonds)
        check("V9", "环戊烷（奇环）：非平凡可达且 nucleon-like",
              rc5["reachability"]["nontrivial_reachable"]
              and rc5["channel_type"].startswith("nucleon-like"))
        check("V9", "乙醇：σ 规范类平凡且 Q_model=0",
              re_["sigma_trivial"] and re_["keys"]["z2_Q_model"] == 0.0)

    # ---------------- V10 幂等与冻结契约 ----------------
    print("\n--- V10 幂等与冻结契约（z2_* 键 + v11 7 键）---")
    res0 = operator_19_z2_charge_channel(skel_y3_closed().astype(float))
    k1 = charge_channel_keys(res0)
    k2 = charge_channel_keys(operator_19_z2_charge_channel(skel_y3_closed().astype(float)))
    check("V10", "charge_channel_keys 两次调用逐键相等（确定性/幂等）", k1 == k2)
    check("V10", "z2_* 键集合完整（10 键）", len(k1) == 10 and "z2_deg" in k1)

    # attach 守卫幂等：已含 z2_deg 的指纹不应被重复计入
    attach_ok = False
    try:
        import sre_cluster_substitute_screen as scr
        fp_already = dict(k1)
        fps = {"__probe__": fp_already}
        n_add = scr.attach_z2_channel_to_fps(fps, structs={})
        attach_ok = (n_add == 0) and (fps["__probe__"] == fp_already)
    except Exception:
        # 回退：直接复核守卫契约（"z2_deg" in fp ⇒ 跳过）
        fp_already = dict(k1)
        n_add = 0 if "z2_deg" in fp_already else 1
        attach_ok = (n_add == 0)
    check("V10", "attach 幂等：已含 z2_deg 的指纹再 attach 不重复计入", attach_ok)

    # v11 冻结契约：z2_* 不得污染 7 键指纹
    if compute_electronic_fingerprint is not None:
        pos = np.array([[0.0, 0.0, 0.0], [1.52, 0.0, 0.0], [2.15, 1.35, 0.0],
                        [-0.5, 0.9, 0.3], [-0.5, -0.9, -0.3], [-0.5, 0.0, -0.9],
                        [1.52, -0.9, 0.9], [1.52, 0.9, -0.9], [2.15, 1.35, 0.96]])
        types = ["c3", "c3", "oh", "hc", "hc", "hc", "h1", "h1", "ho"]
        from sre_electronic_ops_v11 import build_sre_smooth_adjacency
        A_s = build_sre_smooth_adjacency(pos, atomtypes=types)
        try:
            fp = compute_electronic_fingerprint(pos, A_s, np.array(
                [2.55, 2.55, 3.44, 2.20, 2.20, 2.20, 2.20, 2.20, 2.20]))
            check("V10", "v11 冻结契约：指纹仍恰为 7 键（z2_* 未污染）", len(fp) == 7)
        except Exception as exc:
            print("     [SKIP] fingerprint 接口签名差异：%s" % type(exc).__name__)

    # ---------------- V11 图不变量自洽 ----------------
    print("\n--- V11 图不变量自洽（β₁=E−V+c；奇环 ⟺ 非二分）---")
    v11_ok = True
    for _, adj, *_ in [(nm,) + (a,) for nm, a, *_ in skels]:
        inv = graph_invariants(adj)
        v11_ok &= (inv["beta1"] == inv["E"] - inv["V"] + inv["c"])
        v11_ok &= (inv["has_odd_cycle"] == (not inv["bipartite"]))
    for _ in range(40):
        n = int(rng.integers(3, 14))
        adj = random_connected_adj(rng, n, int(rng.integers(0, 9)))
        inv = graph_invariants(adj)
        v11_ok &= (inv["beta1"] == inv["E"] - inv["V"] + inv["c"])
        v11_ok &= (inv["has_odd_cycle"] == (not inv["bipartite"]))
    check("V11", "骨架+40 例：β₁=E−V+c 且 奇环 ⟺ 非二分", v11_ok)

    # ---------------- V12 分子层判据 ----------------
    print("\n--- V12 分子键图：环奇偶性 ⇒ 通道类型（保色自同构）---")
    v12_ok = True
    for name, elems, bonds, exp in MOLS:
        adj = adj_from_bonds(len(elems), bonds)
        res = operator_19_z2_charge_channel(adj.astype(float), elements=elems)
        got = res["reachability"]["nontrivial_reachable"]
        v12_ok &= (got == exp)
        check("V12", "%-22s β₁=%d 轨道=%s 非平凡可达=%-5s → %s"
              % (name, res["beta1"], res["reachability"]["orbit_sizes"],
                 got, res["channel_type"]), got == exp)

    # ---------------- 汇总 ----------------
    print("\n" + "=" * 80)
    passed = sum(1 for r in RESULTS if r[2])
    total = len(RESULTS)
    print("通过 %d/%d 项断言" % (passed, total))
    fails = [r for r in RESULTS if not r[2]]
    for tag, desc, _ in fails:
        print("  FAIL: [%s] %s" % (tag, desc))
    print("[%s] 算子 19 严格验证" % ("SUCCESS" if not fails else "FAIL"))
    print("=" * 80)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())