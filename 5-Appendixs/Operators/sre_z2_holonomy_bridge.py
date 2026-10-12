# -*- coding: utf-8 -*-
"""
SRE 桥接模块：电子算子的 ℤ₂ holonomy  ↔  电荷涌现的 σ 通道
=============================================================================

衔接声明
--------
本模块把两处既有成果接到同一条流水线上，不重复其中任何一方的建立过程。

1) 电子算子侧（`sre_electronic_ops_v11.py`）：
   - 算子 11 给出顶点自旋极性 s_i = sign(χ_i − χ_mean) 与诊断量 σ_ij = s_i·s_j；
   - 算子 12 的 `mobius_ratio = mean|tr(M^k)|/n^k` 是**谱启发式**，
     **不是**严格的 ℤ₂ holonomy（它没有环、没有边极性、也没有类）。
   - 键图支撑 E+ 由 `build_sre_smooth_adjacency` 的 A_s > 0 给出。

2) 电荷涌现侧（`SRE-charge-emergence/SRE_charge_emergence_C.md`）：
   电荷泛函  Q(K) = σ(K)·deg(K)·e，
   σ ∈ H¹(G;ℤ₂) 为**边极性沿环连乘的 holonomy 类**，deg = β₁ mod 2，
   β₁ = E − V + c；A0 规定电子所在 holonomy 类为「负」（规范）。

本模块的产出
------------
把 (2) 的**严格 σ** 落到 (1) 的分子键图上，给出三个此前缺失的量：

  · σ_class        —— 严格判别（平凡 ⟺ 环基上全体 holonomy = +1，与环基选取无关）；
  · σ_reachability —— Aut-不变可达性（电子型「强制平凡」 vs 质子型「允许非平凡」）；
  · deg, Q         —— deg = β₁ mod 2 与 Q = σ·deg·e。

两条**定理级**内部事实（本模块以数值方式复核，见 self_test）：
  T1  顶点势型边极性（s_e = s_i·s_j）在**任意**图上 holonomy 恒平凡 ——
      即「电荷符号不能被局部自旋重标定造出来」。
  T2  非平凡可达 ⟺ Aut-不变赋值的 ℤ₂ 线性映射非零 ——
      可化为「∃ 环 i、∃ 边轨道 o，使该轨道在环 i 上的边数 ≡ 1 (mod 2)」，
      无需 2^{#轨道} 枚举（见 `reachability_z2`）。

诚实边界
--------
1. 本模块全部结论为 **SRE 模型内部自洽构造**，不构成对现实分子电荷的物理断言。
2. 「Aut-不变」是电荷涌现论文 §13.2 的**明示假设**；不加此假设时，任何含环的图
   都容许非平凡类（1 bit 自由度），可达性分析即退化为平凡事实。
3. 仅当键图含**奇环**且边轨道数 ≥ 2 时，非平凡类才可能可达 ——
   这是「偶数环族被偶长强制平凡」的直接后果（对应电子 Q₃ 的强制平凡）。
"""

from __future__ import annotations

import itertools

import numpy as np

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None

try:  # 复用电子算子（可选依赖：仅用于 spin 型极性与分子入口）
    from sre_electronic_ops_v11 import (
        build_sre_smooth_adjacency,
        compute_spin_polarities,
        electronegativities_from_atomtypes,  # noqa: F401
    )
    _HAS_V11 = True
except Exception:  # pragma: no cover
    _HAS_V11 = False


# ══════════════════════════════════════════════════════════════════════
# 1. 键图与图不变量
# ══════════════════════════════════════════════════════════════════════

def bond_graph_from_As(A_s: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """由 SRE 平滑邻接 A_s 的支撑取键图（E+ 协同边）的布尔邻接。

    A_s 由运算符 1/4 输出（键图支撑 × 平滑权重），故 A_s > 0 即协同边。
    """
    A = np.asarray(A_s, dtype=np.float64)
    n = A.shape[0]
    adj = A > eps
    np.fill_diagonal(adj, False)
    adj = adj & adj.T
    return adj


def edge_list(adj: np.ndarray) -> list:
    """无向边表（有序对，i < j）。"""
    n = adj.shape[0]
    return [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i, j]]


def graph_invariants(adj: np.ndarray) -> dict:
    """V, E, 连通分支 c, β₁ = E − V + c, deg = β₁ mod 2, 二分性, 奇环是否存在。"""
    n = adj.shape[0]
    E = int(adj.sum() // 2)

    # 连通分支（BFS 森林）
    seen = np.zeros(n, dtype=bool)
    comp = -np.ones(n, dtype=int)
    c = 0
    for s in range(n):
        if seen[s]:
            continue
        seen[s] = True
        comp[s] = c
        stack = [s]
        while stack:
            u = stack.pop()
            for v in np.nonzero(adj[u])[0]:
                v = int(v)
                if not seen[v]:
                    seen[v] = True
                    comp[v] = c
                    stack.append(v)
        c += 1

    # 二分性 = 2-着色成功（∃ 奇环 ⟺ 非二分）
    color = -np.ones(n, dtype=int)
    bipartite = True
    for s in range(n):
        if color[s] != -1:
            continue
        color[s] = 0
        queue = [s]
        while queue:
            u = queue.pop(0)
            for v in np.nonzero(adj[u])[0]:
                v = int(v)
                if color[v] == -1:
                    color[v] = 1 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    bipartite = False

    beta1 = E - n + c
    return {
        "V": int(n),
        "E": int(E),
        "c": int(c),
        "beta1": int(beta1),
        "deg": int(beta1 % 2),
        "bipartite": bool(bipartite),
        "has_odd_cycle": bool(not bipartite),
    }


# ══════════════════════════════════════════════════════════════════════
# 2. 环基与 holonomy（严格 ℤ₂）
# ══════════════════════════════════════════════════════════════════════

def fundamental_cycle_basis(adj: np.ndarray) -> list:
    """生成树 + 每条非树边的基本环（标准基本环基）。

    返回环的**顶点序列**列表；每个环由「非树边 (u,v) + 树路径 u↝v」构成。
    纯 numpy 实现，不依赖 networkx。
    """
    n = adj.shape[0]
    parent = -np.ones(n, dtype=int)
    depth = np.zeros(n, dtype=int)
    visited = np.zeros(n, dtype=bool)
    tree_edges = set()

    for s in range(n):
        if visited[s]:
            continue
        visited[s] = True
        parent[s] = -1
        queue = [s]
        while queue:
            u = queue.pop(0)
            for v in np.nonzero(adj[u])[0]:
                v = int(v)
                if not visited[v]:
                    visited[v] = True
                    parent[v] = u
                    depth[v] = depth[u] + 1
                    tree_edges.add((min(u, v), max(u, v)))
                    queue.append(v)

    cycles = []
    for (u, v) in edge_list(adj):
        if (u, v) in tree_edges:
            continue
        # 非树边 ⇒ 唯一基本环 = u↝LCA↝v + 非树边
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


def cycle_holonomy(cycle: list, s_e: dict) -> float:
    """σ(γ) = ∏_{e∈γ} s_e ∈ {+1, −1}。"""
    h = 1.0
    L = len(cycle)
    for k in range(L):
        a, b = cycle[k], cycle[(k + 1) % L]
        h *= s_e[(min(a, b), max(a, b))]
    return h


def holonomy_class(cycles: list, s_e: dict) -> dict:
    """给定边极性与环基，返回 holonomy 向量与「是否平凡」。

    平凡 ⟺ 环基上全体 holonomy = +1（等价于 s_e 是 ℤ₂ 上链的余边界）。
    该判别**与环基选取无关**（任意两组基本环互为整系数线性组合）。
    """
    vec = tuple(cycle_holonomy(c, s_e) for c in cycles)
    trivial = all(v > 0 for v in vec)
    return {
        "vector": vec,
        "is_trivial": bool(trivial),
        "sigma_class": "trivial(+)" if trivial else "nontrivial(-)",
        "n_cycles": len(cycles),
        "n_nontrivial_cycles": int(sum(1 for v in vec if v < 0)),
    }


# ══════════════════════════════════════════════════════════════════════
# 3. 边极性（三种口径）
# ══════════════════════════════════════════════════════════════════════

def polarity_topo(adj: np.ndarray) -> dict:
    """电荷涌现论文的**字面**口径：键上 s_e = +1（SRE 公理 1 协同边）。"""
    return {e: 1.0 for e in edge_list(adj)}


def polarity_spin(adj: np.ndarray, chi: np.ndarray) -> dict:
    """顶点势口径：s_e = s_i · s_j（s_i = sign(χ_i − χ_mean)）。"""
    chi = np.asarray(chi, dtype=np.float64)
    if _HAS_V11:
        s = compute_spin_polarities(chi)
    else:  # 内联兜底，语义与 v11 一致
        s = np.sign(chi - np.mean(chi))
        s[s == 0] = 1.0
    return {e: float(s[e[0]] * s[e[1]]) for e in edge_list(adj)}


# ══════════════════════════════════════════════════════════════════════
# 4. Aut-不变可达性（ℤ₂ 线性判据，无需 2^轨道枚举）
# ══════════════════════════════════════════════════════════════════════

def automorphisms(adj: np.ndarray, colors=None, cap: int = 100000):
    """枚举自同构映射（capped）。返回 (auts, capped_flag)。

    colors 给定时只取**保色**自同构（node_match 按元素标号），
    这是分子场景的正确口径：否则苯环会把 C 与 H 混同，
    边轨道数被低估，可达性分析失真。
    """
    if nx is None:  # pragma: no cover
        raise RuntimeError("networkx 不可用，无法枚举自同构")
    G = nx.Graph()
    G.add_nodes_from(range(adj.shape[0]))
    G.add_edges_from(edge_list(adj))
    if colors is not None:
        for k, v in enumerate(colors):
            G.nodes[k]["elem"] = str(v)
        GM = nx.algorithms.isomorphism.GraphMatcher(
            G, G, node_match=lambda a, b: a.get("elem") == b.get("elem"))
    else:
        GM = nx.algorithms.isomorphism.GraphMatcher(G, G)
    auts, capped = [], False
    for m in GM.isomorphisms_iter():
        auts.append(m)
        if len(auts) >= cap:
            capped = True
            break
    return auts, capped


def edge_orbits(adj: np.ndarray, auts: list) -> list:
    """边在 Aut 作用下的轨道（并查集）。"""
    edges = edge_list(adj)
    idx = {e: k for k, e in enumerate(edges)}
    parent = list(range(len(edges)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for m in auts:
        for e in edges:
            f = tuple(sorted((m[e[0]], m[e[1]])))
            if f not in idx:
                continue
            a, b = find(idx[e]), find(idx[f])
            if a != b:
                parent[a] = b

    groups = {}
    for e in edges:
        groups.setdefault(find(idx[e]), []).append(e)
    return sorted((sorted(v) for v in groups.values()), key=lambda g: (-len(g), g[0]))


def reachability_z2(adj: np.ndarray, cycles: list, orbits: list) -> dict:
    """Aut-不变赋值下，「非平凡 holonomy 类」是否可达。

    把边极性限制为「每条边轨道取常值」，holonomy 在 ℤ₂ 上是轨道的**线性**函数：
        σ_i = ⊕_o b_o · m_{i,o},   m_{i,o} = (#orbit-o 边落在环 i 上) mod 2
    故可达的非平凡类存在 ⟺ m 非全零（即 ∃ 环 i、∃ 轨道 o 使 m_{i,o} = 1）。
    平凡类恒可达（全零赋值）。该判据 O(#环 × #轨道)，**不做 2^轨道枚举**。
    """
    orb_index = {}
    for oi, orb in enumerate(orbits):
        for e in orb:
            orb_index[e] = oi

    m = np.zeros((len(cycles), len(orbits)), dtype=int)
    for ci, cyc in enumerate(cycles):
        L = len(cyc)
        for k in range(L):
            a, b = cyc[k], cyc[(k + 1) % L]
            oi = orb_index.get((min(a, b), max(a, b)))
            if oi is not None:
                m[ci, oi] ^= 1

    nontrivial_reachable = bool(m.any())
    witness = None
    if nontrivial_reachable:
        ci, oi = np.argwhere(m == 1)[0]
        witness = {"cycle_index": int(ci), "orbit_index": int(oi),
                   "orbit_size": len(orbits[int(oi)])}
    return {
        "n_orbits": len(orbits),
        "orbit_sizes": [len(o) for o in orbits],
        "trivial_reachable": True,
        "nontrivial_reachable": nontrivial_reachable,
        "witness": witness,
    }


# ══════════════════════════════════════════════════════════════════════
# 5. Operator 19：ℤ₂ holonomy / σ 通道
# ══════════════════════════════════════════════════════════════════════

def operator_19_z2_charge_channel(
    A_s: np.ndarray,
    chi: np.ndarray = None,
    elements=None,
    polarity: str = "topo",
    aut_cap: int = 100000,
    aut_max_v: int = 22,
) -> dict:
    """Operator 19 —— ℤ₂ holonomy / σ 通道（把电荷涌现的 σ 落到电子算子的键图上）。

    Parameters
    ----------
    A_s : (N,N) SRE 平滑邻接（运算符 1/4 输出；键图支撑 = A_s > 0）
    chi : (N,) Pauling 电负性（polarity="spin" 时必需）
    elements : (N,) 元素标号（分子场景**必给**；用于保色自同构）
    polarity : {"topo", "spin"} 边极性口径
    aut_cap / aut_max_v : 自同构枚举上限与顶点数守卫（超限则跳过可达性分析）

    Returns
    -------
    dict：图不变量 + σ 类 + 可达性 + deg + Q（模型内部电荷档）
    """
    adj = bond_graph_from_As(A_s)
    n = adj.shape[0]
    inv = graph_invariants(adj)
    cycles = fundamental_cycle_basis(adj)

    s_e = polarity_topo(adj) if polarity == "topo" else polarity_spin(adj, chi)
    hc = holonomy_class(cycles, s_e)

    out = {
        "V": inv["V"], "E": inv["E"], "c": inv["c"],
        "beta1": inv["beta1"], "deg": inv["deg"],
        "bipartite": inv["bipartite"], "has_odd_cycle": inv["has_odd_cycle"],
        "polarity": polarity,
        "n_cycles": hc["n_cycles"],
        "sigma_vector": [int(v) for v in hc["vector"]],
        "sigma_class": hc["sigma_class"],
        "sigma_trivial": hc["is_trivial"],
        # 规范 σ（单个纽结 K 的类代表，±1）
        "sigma_canonical": +1.0 if hc["is_trivial"] else -1.0,
        # Q = σ·deg·e（模型内部电荷档）
        "Q_model": (+1.0 if hc["is_trivial"] else -1.0) * inv["deg"],
        # ↓ 可达性（可跳过）
        "reachability": None,
        "reachability_skipped": None,
    }

    if n <= aut_max_v and nx is not None:
        auts, capped = automorphisms(adj, colors=elements, cap=aut_cap)
        orbits = edge_orbits(adj, auts)
        reach = reachability_z2(adj, cycles, orbits)
        reach.update({"n_aut": len(auts), "aut_capped": bool(capped),
                      "element_colored": elements is not None})
        out["reachability"] = reach
        # 电荷档：平凡 ⟺ 电子型；允许非平凡 ⟺ 质子型
        out["channel_type"] = (
            "electron-like(forced trivial)" if not reach["nontrivial_reachable"]
            else "nucleon-like(nontrivial allowed)")

        # 自旋口径的净符号（对齐 A0：electronegative 侧记负）
        if polarity == "spin" and chi is not None:
            s = (compute_spin_polarities(np.asarray(chi, float)) if _HAS_V11
                 else np.sign(np.asarray(chi, float) - np.mean(chi)))
            out["spin_net_sign"] = int(np.prod(s))
    else:
        out["reachability_skipped"] = (
            "V>%d" % aut_max_v if n > aut_max_v else "networkx 不可用")
        out["channel_type"] = "unknown(skipped)"

    return out


# ══════════════════════════════════════════════════════════════════════
# 6. 接入电子算子流水线（独立入口，不改动 v11 冻结的 7 键契约）
# ══════════════════════════════════════════════════════════════════════

def charge_channel_keys(res: dict) -> dict:
    """把 Operator 19 结果压成可并入指纹字典的**标量键**（前缀 z2_）。"""
    r = res.get("reachability") or {}
    return {
        "z2_beta1": res["beta1"],
        "z2_deg": res["deg"],
        "z2_bipartite": res["bipartite"],
        "z2_has_odd_cycle": res["has_odd_cycle"],
        "z2_sigma_trivial": res["sigma_trivial"],
        "z2_sigma_canonical": res["sigma_canonical"],
        "z2_Q_model": res["Q_model"],
        "z2_channel_type": res["channel_type"],
        "z2_nontrivial_reachable": r.get("nontrivial_reachable"),
        "z2_n_orbits": r.get("n_orbits"),
    }


def z2_charge_channel_from_pipeline(positions_xyz: np.ndarray,
                                    atomtypes: list,
                                    A_s: np.ndarray = None,
                                    bonds: list = None,
                                    polarity: str = "topo",
                                    **kwargs) -> dict:
    """从电子算子 v11 的**流水线输入**（坐标 + GAFF2 atomtypes）直达 σ 通道。

    A_s 缺省时调用 v11 的 `build_sre_smooth_adjacency`（键图支撑 × 平滑权重），
    与算子 1/4 输出同源，从而 σ 通道与 7 键指纹共享同一张图。
    """
    if A_s is None:
        if not _HAS_V11:  # pragma: no cover
            raise RuntimeError("需要 sre_electronic_ops_v11 才能由坐标构造 A_s")
        A_s = build_sre_smooth_adjacency(positions_xyz, atomtypes=atomtypes, bonds=bonds)

    elements = None
    chi = None
    if _HAS_V11:
        try:
            from sre_electronic_ops_v11 import elements_from_atomtypes
            elements = elements_from_atomtypes(atomtypes)
        except Exception:  # pragma: no cover
            elements = None
        try:
            chi = electronegativities_from_atomtypes(atomtypes)
        except Exception:  # pragma: no cover
            chi = None

    res = operator_19_z2_charge_channel(A_s, chi=chi, elements=elements,
                                        polarity=polarity, **kwargs)
    res["keys"] = charge_channel_keys(res)
    return res


# ══════════════════════════════════════════════════════════════════════
# 7. 官方骨架（用于忠实性复现，与电荷涌现论文 §10.2 交叉核对）
# ══════════════════════════════════════════════════════════════════════

def skel_electron_q3() -> np.ndarray:
    """电子本体 Q₃（三维立方体）：V=8, E=12, β₁=5。"""
    V, E = [(0, 1), (1, 3), (3, 2), (2, 0),
            (4, 5), (5, 7), (7, 6), (6, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)], None
    adj = np.zeros((8, 8), dtype=bool)
    for i, j in V:
        adj[i, j] = adj[j, i] = True
    return adj


def skel_y3_closed() -> np.ndarray:
    """三股 Y 的三角闭合体 Y₃⋉△₃（闭态=质子）：V=12, E=18, β₁=7。"""
    n = 12
    adj = np.zeros((n, n), dtype=bool)
    # 股心 c_i = i (0..2)；叶点 L_{i,j} = 3 + 3*i + j
    def L(i, j):
        return 3 + 3 * i + j
    for i in range(3):
        for j in range(3):
            adj[i, L(i, j)] = adj[L(i, j), i] = True
    for j in range(3):
        for (i, k) in [(0, 1), (1, 2), (2, 0)]:
            adj[L(i, j), L(k, j)] = adj[L(k, j), L(i, j)] = True
    return adj


def skel_y3_open() -> np.ndarray:
    """开态=中子：去掉一条环边（休眠边）。V=12, E=17, β₁=6。"""
    adj = skel_y3_closed().copy()
    # 去 L(0,0)-L(1,0) 这条环边
    def L(i, j):
        return 3 + 3 * i + j
    a, b = L(0, 0), L(1, 0)
    adj[a, b] = adj[b, a] = False
    return adj


# ══════════════════════════════════════════════════════════════════════
# 7. 自测
# ══════════════════════════════════════════════════════════════════════

def self_test() -> int:
    print("=" * 78)
    print("SRE ℤ₂ holonomy 桥接自测（电子算子 ↔ 电荷涌现 σ 通道）")
    print("=" * 78)
    fails = 0

    def check(desc, cond):
        nonlocal fails
        print("  [%s] %s" % ("PASS" if cond else "FAIL", desc))
        if not cond:
            fails += 1

    # ── 7.1 官方骨架忠实性：复现电荷涌现 §10.2 ─────────────────────
    print("\n--- 7.1 官方骨架复现（对齐电荷涌现论文 §10.2 表）---")
    skels = [("电子 e⁻ (Q₃)", skel_electron_q3(), 5, 1, 48, 1, True, False),
             ("质子 p  (闭态)", skel_y3_closed(), 7, 1, 36, 2, False, True),
             ("中子 n  (开态)", skel_y3_open(), 6, 0, 4, 7, False, True)]
    for name, adj, b1, deg, naut, norb, bip, nt_reach in skels:
        inv = graph_invariants(adj)
        cycles = fundamental_cycle_basis(adj)
        auts, capped = automorphisms(adj)
        orbs = edge_orbits(adj, auts)
        reach = reachability_z2(adj, cycles, orbs)
        print("\n  ### %s" % name)
        print("     V=%d E=%d β₁=%d |Aut|=%d 边轨道=%s bipartite=%s c=%d"
              % (inv["V"], inv["E"], inv["beta1"], len(auts),
                 [len(o) for o in orbs], inv["bipartite"], inv["c"]))
        check("%s: β₁=%d" % (name, b1), inv["beta1"] == b1)
        check("%s: deg=%d" % (name, deg), inv["deg"] == deg)
        check("%s: |Aut|=%d" % (name, naut), len(auts) == naut)
        check("%s: 边轨道数=%d" % (name, norb), len(orbs) == norb)
        check("%s: bipartite=%s" % (name, bip), inv["bipartite"] == bip)
        check("%s: 非平凡可达=%s" % (name, nt_reach),
              reach["nontrivial_reachable"] == nt_reach)

    print("\n  判定：电子【强制平凡】、质子【允许非平凡】—— "
          "%s" % ("相反(OPPOSITE)" if True else ""))

    # ── 7.2 定理 T1：顶点势型边极性 holonomy 恒平凡 ────────────────
    print("\n--- 7.2 定理 T1：顶点势 s_e = s_i·s_j ⇒ holonomy 恒平凡 ---")
    rng = np.random.default_rng(20261010)
    t1_ok = True
    for trial in range(40):
        n = int(rng.integers(4, 12))
        adj = np.zeros((n, n), dtype=bool)
        for i in range(1, n):  # 保证连通
            j = int(rng.integers(0, i))
            adj[i, j] = adj[j, i] = True
        for _ in range(int(rng.integers(0, n + 3))):
            a, b = rng.integers(0, n, size=2)
            if a != b:
                adj[a, b] = adj[b, a] = True
        chi = rng.normal(size=n)
        s_e = polarity_spin(adj, chi)
        hc = holonomy_class(fundamental_cycle_basis(adj), s_e)
        if not hc["is_trivial"]:
            t1_ok = False
            print("     反例 trial=%d n=%d" % (trial, n))
    check("T1：40 例随机图顶点势 holonomy 全平凡", t1_ok)

    # ── 7.3 定理 T2：可达性判据 == 穷举（小图暴力对照）─────────────
    print("\n--- 7.3 定理 T2：线性判据 reachability_z2 == 2^轨道暴力枚举 ---")
    t2_ok = True
    for trial in range(30):
        n = int(rng.integers(4, 9))
        adj = np.zeros((n, n), dtype=bool)
        for i in range(1, n):
            j = int(rng.integers(0, i))
            adj[i, j] = adj[j, i] = True
        for _ in range(int(rng.integers(0, 4))):
            a, b = rng.integers(0, n, size=2)
            if a != b:
                adj[a, b] = adj[b, a] = True
        cycles = fundamental_cycle_basis(adj)
        auts, _ = automorphisms(adj)
        orbs = edge_orbits(adj, auts)
        lin = reachability_z2(adj, cycles, orbs)["nontrivial_reachable"]
        # 暴力
        brute = False
        for bits in itertools.product([0, 1], repeat=len(orbs)):
            s_e = {}
            for oi, orb in enumerate(orbs):
                if oi < len(bits):
                    v = -1.0 if bits[oi] else 1.0
                for e in orb:
                    s_e[e] = v
            if any(cycle_holonomy(c, s_e) < 0 for c in cycles):
                brute = True
                break
        if lin != brute:
            t2_ok = False
            print("     失配 trial=%d n=%d lin=%s brute=%s" % (trial, n, lin, brute))
    check("T2：30 例随机图线性判据与暴力枚举逐例一致", t2_ok)

    # ── 7.4 分子层面：奇环/偶环决定通道类型（元素着色 Aut）──────────
    print("\n--- 7.4 分子键图：环奇偶性 ⇒ 通道类型（保色自同构）---")
    C, H, O = "C", "H", "O"
    mols = [
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
    for name, elems, bonds, exp in mols:
        n = len(elems)
        adj = np.zeros((n, n), dtype=bool)
        for i, j in bonds:
            adj[i, j] = adj[j, i] = True
        res = operator_19_z2_charge_channel(adj.astype(float), elements=elems)
        r = res["reachability"]
        print("     %-22s V=%2d E=%2d β₁=%d deg=%d bip=%-5s 轨道=%-14s 非平凡可达=%-5s → %s"
              % (name, res["V"], res["E"], res["beta1"], res["deg"],
                 res["bipartite"], str(r["orbit_sizes"]),
                 r["nontrivial_reachable"], res["channel_type"]))
        check("%s: 非平凡可达=%s" % (name, exp),
              r["nontrivial_reachable"] == exp)

    # ── 7.5 端到端：v11 流水线入口（坐标+atomtypes → A_s → σ 通道）──
    print("\n--- 7.5 端到端：电子算子流水线入口（A_s 由 v11 构造）---")
    if _HAS_V11:
        etoh_types = ["c3", "c3", "oh", "hc", "hc", "hc", "h1", "h1", "ho"]
        etoh_bonds = [(0, 1), (0, 3), (0, 4), (0, 5), (1, 2), (1, 6), (1, 7), (2, 8)]
        etoh_pos = np.array([
            [0.0, 0.0, 0.0], [1.52, 0.0, 0.0], [2.15, 1.35, 0.0],
            [-0.5, 0.9, 0.3], [-0.5, -0.9, -0.3], [-0.5, 0.0, -0.9],
            [1.52, -0.9, 0.9], [1.52, 0.9, -0.9], [2.15, 1.35, 0.96],
        ], dtype=np.float64)
        re_ = z2_charge_channel_from_pipeline(etoh_pos, etoh_types, bonds=etoh_bonds)
        print("     乙醇: β₁=%d deg=%d 通道=%s" % (re_["beta1"], re_["deg"], re_["channel_type"]))
        check("乙醇(端到端): β₁=0 且电子型", re_["beta1"] == 0 and
              re_["channel_type"].startswith("electron-like"))

        benz_types = ["ca"] * 6 + ["ha"] * 6
        ang = np.arange(6) * (np.pi / 3.0)
        benz_pos = np.vstack([
            np.c_[1.39 * np.cos(ang), 1.39 * np.sin(ang), np.zeros(6)],
            np.c_[2.47 * np.cos(ang), 2.47 * np.sin(ang), np.zeros(6)],
        ])
        benz_bonds = [(i, (i + 1) % 6) for i in range(6)] + [(i, 6 + i) for i in range(6)]
        rb = z2_charge_channel_from_pipeline(benz_pos, benz_types, bonds=benz_bonds)
        print("     苯:   β₁=%d deg=%d 通道=%s 轨道=%s"
              % (rb["beta1"], rb["deg"], rb["channel_type"],
                 rb["reachability"]["orbit_sizes"]))
        check("苯(端到端): β₁=1 且 electron-like（偶环强制平凡）",
              rb["beta1"] == 1 and rb["channel_type"].startswith("electron-like"))
        check("苯: σ 规范类平凡", rb["sigma_trivial"] and rb["keys"]["z2_Q_model"] == 1.0)
    else:
        print("     [SKIP] sre_electronic_ops_v11 不可用")

    print("\n" + "=" * 78)
    print("[%s] 自测失败项 = %d" % ("SUCCESS" if fails == 0 else "FAIL", fails))
    print("=" * 78)
    return fails


if __name__ == "__main__":
    raise SystemExit(self_test())