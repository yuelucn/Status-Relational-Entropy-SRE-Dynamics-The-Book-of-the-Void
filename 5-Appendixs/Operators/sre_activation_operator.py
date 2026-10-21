# -*- coding: utf-8 -*-
"""
SRE 算子 20：活化 / 桥接算子 𝒦_act
=============================================================================

规范文档
--------
《算子 20：活化 / 桥接算子 𝒦_act —— 严格数学规范》（v0.3）
    `Operator_20_C.md`

公共入口
--------
    operator_20_activation_index(R, **kw) -> dict

依赖
----
仅 numpy（不依赖 networkx / v11 电子算子）。

对象（D1）
----------
    R = ( G, {(w_j, n_j)}_{j=0..m}, B, E_I, w_I )
      · G = 骨架（重原子，顶点 0..n-1，边 E = E_R ∪ E_P，成/断键用 0 权重表示）
      · w_j ∈ [0,3]^E  第 j 个 waypoint 的键级；n_j ∈ Z_{>=0}^V 氢覆盖
      · B = (V_B, E_B) 外部催化剂边界图（顶点 n..n+n_B-1）
      · E_I ⊆ V × V_B  界面边；w_I ∈ R_{>=0}^{E_I}

三个相互独立的通道（D4/D5/D7）
------------------------------
    ϱ  = ‖δ_e,harm‖ / ‖δ_e‖     边拓扑挫折（H¹(G;R)）
    ν  = ‖δ_v⊥‖ / ‖δ_v‖         顶点对比度（氢覆盖再分配）
    κ  = Σ_j ∫ dt / (γ + ε)     刚度瓶颈（内生谱隙比 γ = λ₂/α_n）

实现约定（相对 v0.2 §2.3 的**一处必要澄清**）
--------------------------------------------
v0.2 §2.3 写「γ 在**含活性位的最大连通分量**上计算」。若严格按「最大连通分量」
取值，则该分量按定义连通，λ₂ 恒 > 0，P20.5 的等价式退化为恒真，V7 的
「γ→0、κ~1/ε」永远不可观测。

本实现按**该约定的本意**取：

    X = V ∪ { 至少有一条正权界面边的边界顶点 }
    γ = λ₂(L|_X) / λ_n(L|_X)

即「**含活性位的连通分量之并**」（骨架顶点全部视为活性位）。
- w_I = 0（直接参考）时 B 不与骨架耦合，X = V，孤立催化剂被自动排除；
- 骨架自身因 0 权边断开时 X 不连通 ⇒ λ₂ = 0 ⇒ P20.5 成立、κ ~ 1/ε；
- 催化剂经界面边把断开的两片重新桥接时 λ₂ > 0 ⇒ κ 有限（这正是 A20 的机制）。

**该措辞需在规范 v0.3 中同步修订**（「最大连通分量」→「含活性位的连通分量之并」）。

边界（规范 §10）
----------------
1. w_I 是唯一自由输入且无法内生 ⇒ 只能做「固定金属下的结构排序」，不能排金属；
2. 不是最小能量路径，κ 是**指标**不是势垒上界；
3. Hodge 默认标准欧氏内积（无参数）；
4. 不覆盖含 2-胞腔（填面）复形；
5. ε 敏感性：必须报告多档 ε 下的排序稳定性；
6. H 不建节点，C–H 键能不在模型内（只有覆盖变化进入顶点通道）；
7. 0 K、无熵、无溶剂；8. t 是同伦参数不是时间；9. 单基元步；
10. H20.1（与 DFT 势垒秩相关 ≥0.7）**未证**，本模块只提供内部自洽计算。
"""

from __future__ import annotations

import numpy as np

__all__ = [
    "build_reaction", "incidence", "hodge_g1", "uniform_split",
    "cycle_basis_bfs", "cycle_basis_dfs", "orientation_sign", "holonomy_R",
    "orient_from_cycle", "spectral_gamma", "operator_20_activation_index",
    "pareto_leq", "activation_keys", "self_test",
]

_TOL = 1e-12


# ══════════════════════════════════════════════════════════════════════
# 0. 基础工具
# ══════════════════════════════════════════════════════════════════════

def _ekey(i: int, j: int):
    """无向边的规范化键（i < j）。"""
    return (i, j) if i < j else (j, i)


def orientation_sign(i: int, j: int) -> float:
    """§2.2 定向符号：参考定向取 i < j（i→j），遍历同向取 +1，反向取 −1。"""
    return 1.0 if i < j else -1.0


def incidence(n: int, edges) -> np.ndarray:
    """0-阶边界算子 d₁ 的转置写法 B (n × m)：B[head,e]=+1, B[tail,e]=−1（tail<head）。"""
    m = len(edges)
    B = np.zeros((n, m), dtype=np.float64)
    for k, (i, j) in enumerate(edges):
        B[j, k] = 1.0
        B[i, k] = -1.0
    return B


def hodge_g1(delta: np.ndarray, n: int, edges) -> dict:
    """D4：1-上链 δ 在 G 上的 Hodge 分解（无 2-胞腔 ⇒ 只有梯度 + 调和两分量）。

        δ = δ_grad + δ_harm ,  δ_grad = B φ ,  φ = argmin‖Bφ − δ‖
        ϱ = ‖δ_harm‖ / ‖δ‖ ∈ [0,1] ,  ‖δ‖ = 0 时约定 ϱ = 0
    """
    d = np.asarray(delta, dtype=np.float64).reshape(-1)
    nrm = float(np.linalg.norm(d))
    if nrm < 1e-300:
        z = np.zeros_like(d)
        return {"grad": z.copy(), "harm": z.copy(), "phi": np.zeros(n), "rho": 0.0}
    B = incidence(n, edges)                        # (n_v × m_e)
    phi = np.linalg.lstsq(B.T, d, rcond=None)[0]   # B.T 为 (m_e × n_v)，与 d 行数一致
    grad = B.T @ phi                               # δ_grad = Bᵀφ，(m_e,)
    harm = d - grad
    return {"grad": grad, "harm": harm, "phi": phi, "rho": float(np.linalg.norm(harm) / nrm)}


def uniform_split(dv: np.ndarray) -> dict:
    """D5：顶点通道正交分解 δ_v = μ·1 + δ_v⊥；返回 μ、⊥ 分量与 ν。"""
    d = np.asarray(dv, dtype=np.float64).reshape(-1)
    nrm = float(np.linalg.norm(d))
    if nrm < 1e-300:
        return {"mu": 0.0, "perp": np.zeros_like(d), "nu": 0.0}
    mu = float(d.mean())
    perp = d - mu
    return {"mu": mu, "perp": perp, "nu": float(np.linalg.norm(perp) / nrm)}


# ══════════════════════════════════════════════════════════════════════
# 1. 环基与 R 值 holonomy（D3 / §2.2）
# ══════════════════════════════════════════════════════════════════════

def _spanning_forest(n: int, edges, mode: str = "bfs", root: int = 0):
    """生成森林（纯 numpy）。返回 (parent, depth, tree_edges)。"""
    adj = [[] for _ in range(n)]
    for (i, j) in edges:
        adj[i].append(j)
        adj[j].append(i)
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
        queue = [s]
        while queue:
            u = queue.pop(0) if mode == "bfs" else queue.pop()
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    parent[v] = u
                    depth[v] = depth[u] + 1
                    tree.add(_ekey(u, v))
                    queue.append(v)
    return parent, depth, tree


def _basis(n: int, edges, mode: str, root: int):
    parent, depth, tree = _spanning_forest(n, edges, mode=mode, root=root)
    cycles = []
    for (u, v) in edges:
        if _ekey(u, v) in tree:
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
        cycles.append(path_u + path_v[-2::-1])   # 顶点序列（闭环）
    return cycles


def cycle_basis_bfs(n: int, edges, root: int = 0):
    """基本环基（BFS 生成树）。返回环的顶点序列列表。"""
    return _basis(n, edges, "bfs", root)


def cycle_basis_dfs(n: int, edges, root: int = 0):
    """基本环基（DFS 生成树，用于环基无关性交叉比对）。"""
    return _basis(n, edges, "dfs", root)


def _canon_index(index) -> dict:
    """把可能含非规范键 (j,i) 的边索引统一为 _ekey 键（便于外部传入原始边表索引）。"""
    return {_ekey(int(e[0]), int(e[1])): int(k) for e, k in index.items()}


def holonomy_R(delta: np.ndarray, edges, cycle, index=None) -> float:
    """D3：Hol_R(δ, γ) = Σ_{e∈γ} ε_{e,γ} · δ_e（带定向，见 §2.2）。"""
    idx = _canon_index(index) if index is not None else {e: k for k, e in enumerate(edges)}
    d = np.asarray(delta, dtype=np.float64).reshape(-1)
    L = len(cycle)
    s = 0.0
    for t in range(L):
        a, b = cycle[t], cycle[(t + 1) % L]
        s += orientation_sign(a, b) * d[idx[_ekey(a, b)]]
    return float(s)


def orient_from_cycle(n: int, edges, cycle, index=None) -> np.ndarray:
    """由给定遍历方向生成显式边定向 ς_e（规范 §2.2 的可选输入）。

    取 ς_e = ε_{e,γ}（沿 cycle 遍历的定向符号），则"整环同步施加的位移"会被读作
    纯环通道（ϱ = 1），而不会被记为含梯度成分。用于把化学直觉（"整环同步升/降键级"）
    转成规范的定向约定。未出现在 cycle 中的边取 +1。
    """
    idx = _canon_index(index) if index is not None else {e: k for k, e in enumerate(edges)}
    ori = np.ones(len(edges), dtype=np.float64)
    L = len(cycle)
    for t in range(L):
        a, b = cycle[t], cycle[(t + 1) % L]
        ori[idx[_ekey(a, b)]] = orientation_sign(a, b)
    return ori


# ══════════════════════════════════════════════════════════════════════
# 2. 反应对象构造（D1）
# ══════════════════════════════════════════════════════════════════════

def _cochain(values, keys, index, name: str) -> np.ndarray:
    """把 dict 或序列统一为按 keys 顺序的向量。"""
    if isinstance(values, dict):
        out = np.zeros(len(keys), dtype=np.float64)
        for e, val in values.items():
            k = _ekey(int(e[0]), int(e[1]))
            if k not in index:
                raise KeyError("%s 中出现未定义边 %s" % (name, k))
            out[index[k]] = float(val)
        return out
    arr = np.asarray(values, dtype=np.float64).reshape(-1)
    if arr.size != len(keys):
        raise ValueError("%s 长度 %d ≠ 边数 %d" % (name, arr.size, len(keys)))
    return arr


def _trapz(y, x) -> float:
    """梯形积分（自实现，避免 numpy 版本间 np.trapz/np.trapezoid 差异）。"""
    y = np.asarray(y, dtype=np.float64).reshape(-1)
    x = np.asarray(x, dtype=np.float64).reshape(-1)
    if y.size < 2:
        return 0.0
    return float(np.sum(0.5 * (y[1:] + y[:-1]) * np.diff(x)))


def _scalar_or_vec(v, m: int, name: str) -> np.ndarray:
    arr = np.asarray(v, dtype=np.float64).reshape(-1)
    if arr.size == 1:
        return np.full(m, float(arr[0]))
    if arr.size != m:
        raise ValueError("%s 长度 %d ≠ %d" % (name, arr.size, m))
    return arr


def build_reaction(n_atoms: int, edges, waypoints,
                   boundary_edges=None, n_boundary: int = 0,
                   interface_edges=None, w_I=1.0, w_B=1.0,
                   segment_lengths=None, orient=None) -> dict:
    """构造反应对象 R（D1）。

    Parameters
    ----------
    n_atoms : 骨架重原子数（顶点 0..n-1）
    edges : G 的边表 [(i, j), ...]（E = E_R ∪ E_P；成/断键用 0 权重表示）
    waypoints : [{"w": {...}|array, "nH": {...}|array}, ...]，至少 2 个
                m = 1 → 直接路径；m = 2 → 催化路径（中间为吸附态 w_ads）
    boundary_edges : E_B（边界图内部边，顶点用全局编号 n..）
    n_boundary : 边界顶点数（0 时由 index 自动推断）
    interface_edges : E_I，元素为 (骨架顶点, 边界顶点)
    w_I : 界面权重（标量或长度 |E_I| 的向量）；0 表示未耦合（直接参考）
    w_B : 边界图内部权重
    segment_lengths : 段长 ℓ_j（默认均分，Σℓ_j = 1）
    orient : **显式边定向 ς_e ∈ {+1,-1}**（规范 §2.2）。可为标量、
             长度 |E| 的向量，或 {(i,j): ±1} 字典。默认 None ⟹ ς_e ≡ +1，
             即 v0.2 的 i<j 参考定向（结果逐位一致）。
             ς_e 只作用于边通道：δ_e ← ς_e·δ_e 后再做 Hodge 分解，
             **不影响** κ（用 W，无定向）、ν/μ（顶点通道，无定向）。
    """
    n = int(n_atoms)
    E, seen = [], set()
    for e in edges:
        k = _ekey(int(e[0]), int(e[1]))
        if k[0] == k[1] or k in seen:
            continue
        seen.add(k)
        E.append(k)
    if not E:
        raise ValueError("骨架至少需要一条边")
    m = len(E)
    idx = {e: k for k, e in enumerate(E)}

    wps = []
    for wp in waypoints:
        if isinstance(wp, dict):
            wv, nv = wp.get("w", {}), wp.get("nH", {})
        else:
            wv, nv = wp[0], wp[1]
        w = _cochain(wv, E, idx, "w")
        if isinstance(nv, dict):
            nh = np.zeros(n, dtype=np.float64)
            for v, val in nv.items():
                nh[int(v)] = float(val)
        else:
            nh = np.asarray(nv, dtype=np.float64).reshape(-1)
            if nh.size != n:
                raise ValueError("nH 长度 %d ≠ 顶点数 %d" % (nh.size, n))
        wps.append({"w": w, "nH": nh})
    if len(wps) < 2:
        raise ValueError("至少需要 2 个 waypoint")

    BE, seenB = [], set()
    for e in (boundary_edges or []):
        k = _ekey(int(e[0]), int(e[1]))
        if k[0] == k[1] or k in seenB:
            continue
        seenB.add(k)
        BE.append(k)

    IE = []
    for e in (interface_edges or []):
        a, b = int(e[0]), int(e[1])
        if a >= n and b < n:
            a, b = b, a
        if b < n:
            raise ValueError("界面边 %s 需要一个边界端点（编号 ≥ %d）" % ((a, b), n))
        IE.append((a, b))

    mx = n - 1
    for e in BE:
        mx = max(mx, e[0], e[1])
    for e in IE:
        mx = max(mx, e[0], e[1])
    nb = max(int(n_boundary), mx + 1 - n, 0)

    seg = len(wps) - 1
    if segment_lengths is None:
        ell = np.full(seg, 1.0 / seg)
    else:
        ell = np.asarray(segment_lengths, dtype=np.float64).reshape(-1)
        if ell.size != seg:
            raise ValueError("段长个数 %d ≠ 段数 %d" % (ell.size, seg))
        if ell.sum() <= 0:
            raise ValueError("段长之和必须为正")
        ell = ell / ell.sum()

    # 显式边定向 ς_e（规范 §2.2）；默认全 +1 ⇒ 与 v0.2 的 i<j 参考定向逐位一致
    if orient is None:
        ori = np.ones(m, dtype=np.float64)
    elif isinstance(orient, dict):
        ori = np.ones(m, dtype=np.float64)
        for e, val in orient.items():
            k = _ekey(int(e[0]), int(e[1]))
            if k not in idx:
                raise KeyError("orient（ς_e）中出现未定义边 %s" % (k,))
            ori[idx[k]] = float(val)
    else:
        ori = _scalar_or_vec(orient, m, "orient")
    sgn = np.sign(ori)
    if not np.all(np.abs(sgn) == 1.0):
        raise ValueError("orient（ς_e）只能取 +1 或 -1，实际含 %s"
                         % sorted(set(np.asarray(ori).tolist()))[:5])
    ori = sgn

    return {
        "n": n, "n_boundary": nb, "n_total": n + nb,
        "edges": E, "n_edges": m,
        "waypoints": wps, "n_waypoints": len(wps),
        "ell": ell, "n_segments": seg,
        "boundary_edges": BE,
        "interface_edges": IE,
        "w_I": _scalar_or_vec(w_I, len(IE), "w_I"),
        "w_B": _scalar_or_vec(w_B, len(BE), "w_B"),
        "orient": ori,
    }


# ══════════════════════════════════════════════════════════════════════
# 3. 谱隙比 γ（D7 本意约定：X = V ∪ 正权界面边所连的边界顶点）
# ══════════════════════════════════════════════════════════════════════

def _active_mask(R: dict) -> np.ndarray:
    nt = R["n_total"]
    mask = np.zeros(nt, dtype=bool)
    mask[:R["n"]] = True
    for k, (_, b) in enumerate(R["interface_edges"]):
        if R["w_I"][k] > _TOL:
            mask[b] = True
    return mask


def spectral_gamma(R: dict, w_core: np.ndarray, return_assets: bool = False):
    """在 X 上算 γ = λ₂(L|_X)/λ_n(L|_X)；|X| ≤ 1 时约定 γ = 1。

    L|_X 为 X 上诱导加权图的拉普拉斯（骨架边 w_core、边界边 w_B、界面边 w_I）。
    图不连通 ⇒ ev[1] = 0 ⇒ γ = 0（P20.5）。
    """
    nt = R["n_total"]
    W = np.zeros((nt, nt), dtype=np.float64)
    for k, (i, j) in enumerate(R["edges"]):
        w = float(w_core[k])
        if w > _TOL:
            W[i, j] += w; W[j, i] += w
    for k, (i, j) in enumerate(R["boundary_edges"]):
        w = float(R["w_B"][k])
        if w > _TOL:
            W[i, j] += w; W[j, i] += w
    for k, (i, j) in enumerate(R["interface_edges"]):
        w = float(R["w_I"][k])
        if w > _TOL:
            W[i, j] += w; W[j, i] += w

    mask = _active_mask(R)
    size = int(mask.sum())
    if size <= 1:
        return (1.0, 0.0, 1.0, size) if return_assets else 1.0

    Ws = W[np.ix_(mask, mask)]
    L = np.diag(Ws.sum(axis=1)) - Ws
    ev = np.linalg.eigvalsh(L)
    lam2 = float(ev[1])
    alphan = float(ev[-1])
    gamma = float(lam2 / alphan) if alphan > 1e-300 else 1.0
    gamma = min(max(gamma, 0.0), 1.0)
    if return_assets:
        return gamma, lam2, alphan, size
    return gamma


def _chebyshev_moments(L: np.ndarray, alpha: float, K: int) -> np.ndarray:
    """算子 13 口径：τ_k = (1/N)·tr(T_k(Y))，Y = 2L/α_n − I。"""
    N = L.shape[0]
    Y = 2.0 * L / max(alpha, 1e-300) - np.eye(N)
    T = [np.eye(N), Y]
    for k in range(2, K + 1):
        T.append(2.0 * Y @ T[k - 1] - T[k - 2])
    return np.array([np.trace(T[k]) / N for k in range(K + 1)])


# ══════════════════════════════════════════════════════════════════════
# 4. v1 路径：矩空间插值 + 约束反演（D6）
# ══════════════════════════════════════════════════════════════════════

def _moment_path(R: dict, wa: np.ndarray, wb: np.ndarray, K_grid: int,
                 K_mom: int, lam: float, s_max: float):
    """D6：τ(t) = (1−s)τ(w_a) + s·τ(w_b)，按 s 顺序做约束反演（warm start + 步长上界）。

    返回 (s_grid, W路径 (K_grid × m), 可行性残差)。
    """
    n, m = R["n"], R["n_edges"]
    # 共同参考 α_n（否则不同 w 的 τ 不可比）
    w_ref = np.maximum(wa, wb)
    W_ref = np.zeros((n, n))
    for k, (i, j) in enumerate(R["edges"]):
        W_ref[i, j] = W_ref[j, i] = w_ref[k]
    L_ref = np.diag(W_ref.sum(1)) - W_ref
    alpha_ref = float(np.linalg.eigvalsh(L_ref)[-1])
    alpha_ref = max(alpha_ref, 1e-12)

    def tau(w):
        W = np.zeros((n, n))
        for k, (i, j) in enumerate(R["edges"]):
            W[i, j] = W[j, i] = w[k]
        L = np.diag(W.sum(1)) - W
        return _chebyshev_moments(L, alpha_ref, K_mom)

    ta, tb = tau(wa), tau(wb)
    s_grid = np.linspace(0.0, 1.0, K_grid)
    path = np.zeros((K_grid, m))
    w_prev = wa.copy()
    path[0] = w_prev
    resid = 0.0
    h = 1e-5
    for gi in range(1, K_grid):
        s = float(s_grid[gi])
        t_target = (1.0 - s) * ta + s * tb

        def F(w):
            r = tau(w) - t_target
            return float(r @ r + lam * np.sum((w - w_prev) ** 2))

        w = w_prev.copy()
        for _ in range(40):
            r = tau(w) - t_target
            if float(np.linalg.norm(r)) < 1e-10:
                break
            J = np.zeros((len(t_target), m))
            for e in range(m):
                wp = w.copy(); wp[e] = min(3.0, wp[e] + h)
                wm = w.copy(); wm[e] = max(0.0, wm[e] - h)
                if wp[e] - wm[e] < 1e-14:
                    continue
                J[:, e] = (tau(wp) - tau(wm)) / (wp[e] - wm[e])
            g = 2.0 * J.T @ r + 2.0 * lam * (w - w_prev)
            d = -g
            dn = float(np.linalg.norm(d))
            if dn < 1e-14:
                break
            if dn > s_max:                      # 步长上界（路径连续）
                d = d * (s_max / dn)
            F0 = F(w)
            t = 1.0
            wn = w
            for _ in range(20):
                cand = np.clip(w + t * d, 0.0, 3.0)
                if F(cand) < F0:
                    wn = cand
                    break
                t *= 0.5
            if np.allclose(wn, w):
                break
            w = wn
        resid = max(resid, float(np.linalg.norm(tau(w) - t_target)))
        path[gi] = w
        w_prev = w
    return s_grid, path, resid


# ══════════════════════════════════════════════════════════════════════
# 5. 算子 20 主入口（D8）
# ══════════════════════════════════════════════════════════════════════

def operator_20_activation_index(R: dict, K: int = 32, eps: float = 1e-3,
                                 lam: float = 1e-2, s_max: float = 0.1,
                                 version: str = "v0") -> dict:
    """算子 20 —— 活化 / 桥接算子。

    Parameters
    ----------
    R : build_reaction(...) 的输出
    K : 每段谱采样点数（默认 32）
    eps : κ 的正则（默认 1e-3；规范要求报告 {1e-1,1e-2,1e-3} 三档）
    lam, s_max : v1 的 D6 锚正则与步长上界
    version : {"v0", "v1"}；v0 = 键级空间线性插值（低成本），v1 = 矩空间 + 约束反演

    Returns
    -------
    dict：κ、ϱ_path、ν_path、μ 为核心量；ϱ_tot、ν_tot、γ*、feasible 为诊断量。
    """
    if version not in ("v0", "v1"):
        raise ValueError("version 只能是 'v0' 或 'v1'")
    n, m, seg = R["n"], R["n_edges"], R["n_segments"]
    wps, ell = R["waypoints"], R["ell"]
    ori = R["orient"]                       # ς_e（规范 §2.2），默认全 +1
    edge_index = {e: k for k, e in enumerate(R["edges"])}
    cycles = cycle_basis_bfs(n, R["edges"])

    # ── 通道 1/2：分段位移、ϱ、ν、μ ─────────────────────────────────
    # ς_e 在此接入：δ_e ← ς_e·δ_e（定向上链），随后 Hodge 分解（规范 §2.2/D4）
    seg_info = []
    rho_path = 0.0
    nu_path = 0.0
    for j in range(seg):
        de = ori * (wps[j + 1]["w"] - wps[j]["w"])
        dv = wps[j + 1]["nH"] - wps[j]["nH"]
        hd = hodge_g1(de, n, R["edges"])
        us = uniform_split(dv)
        rho_path += float(ell[j]) * hd["rho"]
        nu_path += float(ell[j]) * us["nu"]
        seg_info.append({"rho": hd["rho"], "nu": us["nu"], "mu": us["mu"],
                         "delta_e": de, "delta_v": dv})

    de_tot = ori * (wps[-1]["w"] - wps[0]["w"])
    dv_tot = wps[-1]["nH"] - wps[0]["nH"]
    rho_tot = hodge_g1(de_tot, n, R["edges"])["rho"]
    nu_tot = uniform_split(dv_tot)["nu"]
    mu = float(dv_tot.mean())

    # ── 通道 3：沿路径的 γ 曲线 → κ ────────────────────────────────
    kappa = 0.0
    gamma_star = 1.0
    feasible = None
    for j in range(seg):
        wa, wb = wps[j]["w"], wps[j + 1]["w"]
        if version == "v0":
            s_grid = np.linspace(0.0, 1.0, K)
            path = np.array([(1.0 - s) * wa + s * wb for s in s_grid])
        else:
            s_grid, path, resid = _moment_path(R, wa, wb, K, 8, lam, s_max)
            feasible = True if feasible is None else feasible
            feasible = bool(feasible and (resid < 1e-2))
            seg_info[j]["moment_residual"] = resid
        g = np.array([spectral_gamma(R, w) for w in path])
        gamma_star = min(gamma_star, float(g.min()))
        kappa += float(ell[j]) * _trapz(1.0 / (g + eps), s_grid)
        seg_info[j]["gamma_curve"] = g.tolist()
        seg_info[j]["s_grid"] = s_grid.tolist()

    return {
        # 核心量
        "kappa": float(kappa),
        "rho_path": float(rho_path),
        "nu_path": float(nu_path),
        "mu": float(mu),
        # 诊断量
        "rho_tot": float(rho_tot),
        "nu_tot": float(nu_tot),
        "gamma_star": float(gamma_star),
        "feasible": feasible,
        # 元信息
        "version": version, "K": int(K), "eps": float(eps),
        "n_core": n, "n_boundary": R["n_boundary"],
        "n_edges": m, "n_segments": seg,
        "n_iface": len(R["interface_edges"]),
        "n_orient_flipped": int(np.sum(ori < 0)),
        "segments": seg_info,
    }


def pareto_leq(KA: dict, KB: dict, tol: float = 0.0) -> bool:
    """D8 的 Pareto 偏序：A ⪯ B ⟺ 三通道全不劣，且至少一项严格。"""
    keys = ("kappa", "rho_path", "nu_path")
    le = all(KA[k] <= KB[k] + tol for k in keys)
    lt = any(KA[k] < KB[k] - tol for k in keys)
    return bool(le and lt)


def activation_keys(res: dict) -> dict:
    """压成可并入报告/指纹的标量键。"""
    return {
        "act_kappa": res["kappa"],
        "act_rho_path": res["rho_path"],
        "act_nu_path": res["nu_path"],
        "act_mu": res["mu"],
        "act_rho_tot": res["rho_tot"],
        "act_nu_tot": res["nu_tot"],
        "act_gamma_star": res["gamma_star"],
    }


# ══════════════════════════════════════════════════════════════════════
# 6. 自测
# ══════════════════════════════════════════════════════════════════════

def self_test() -> int:
    print("=" * 78)
    print("SRE 算子 20 自测（活化 / 桥接算子 𝒦_act）")
    print("=" * 78)
    fails = 0

    def check(desc, cond):
        nonlocal fails
        print("  [%s] %s" % ("PASS" if cond else "FAIL", desc))
        if not cond:
            fails += 1

    def _raises(fn):
        try:
            fn()
        except Exception:
            return True
        return False

    # 6.1 环己烷 → 苯（芳构化）：环上键级 1→1.5
    # 规范 §11-4 只要求 ϱ > 0。按 §2.2 的 i<j 参考定向，本值 = 2/3（不是 1），
    # 因为环绕闭合边的参考定向与遍历方向相反 ⇒ 均匀升键级并非纯调和（见下方 V3 说明）。
    R = build_reaction(6, [(i, (i + 1) % 6) for i in range(6)],
                       [{"w": {(i, (i + 1) % 6): 1.0 for i in range(6)},
                         "nH": {i: 2 for i in range(6)}},
                        {"w": {(i, (i + 1) % 6): 1.5 for i in range(6)},
                         "nH": {i: 1 for i in range(6)}}],
                       w_I=0.0)
    r = operator_20_activation_index(R)
    print("     环己烷→苯: ϱ=%.6f (>0)  μ=%.4f  ν=%.4f  κ=%.6f"
          % (r["rho_tot"], r["mu"], r["nu_tot"], r["kappa"]))
    check("环己烷→苯: ϱ_tot > 0（非平凡边通道）", r["rho_tot"] > 1e-9)
    check("环己烷→苯: μ = (6−12)/6 = −1", abs(r["mu"] + 1.0) < 1e-9)
    check("环己烷→苯: ν_tot = 0（氢覆盖均匀变化）", abs(r["nu_tot"]) < 1e-9)

    # 6.2 乙烷 C–C 旋转：键级与覆盖都不变 ⇒ ϱ = ν = 0
    R2 = build_reaction(2, [(0, 1)],
                        [{"w": {(0, 1): 1.0}, "nH": {0: 3, 1: 3}},
                         {"w": {(0, 1): 1.0}, "nH": {0: 3, 1: 3}}], w_I=0.0)
    r2 = operator_20_activation_index(R2)
    check("乙烷 C–C 旋转: ϱ_tot = ν_tot = 0", abs(r2["rho_tot"]) < 1e-12
          and abs(r2["nu_tot"]) < 1e-12)

    # 6.3 乙醇脱氢：μ < 0 且 ν > 0
    R3 = build_reaction(3, [(0, 1), (1, 2)],
                        [{"w": {(0, 1): 1.0, (1, 2): 1.0}, "nH": {0: 3, 1: 2, 2: 1}},
                         {"w": {(0, 1): 1.0, (1, 2): 1.0}, "nH": {0: 3, 1: 1, 2: 0}}],
                        w_I=0.0)
    r3 = operator_20_activation_index(R3)
    print("     乙醇脱氢: ϱ=%.4f μ=%.4f ν=%.4f" % (r3["rho_tot"], r3["mu"], r3["nu_tot"]))
    check("乙醇脱氢: ϱ_tot = 0（键级不变）", abs(r3["rho_tot"]) < 1e-12)
    check("乙醇脱氢: μ < 0 且 ν_tot > 0", r3["mu"] < 0 and r3["nu_tot"] > 0)

    # 6.4 零权割 ⇒ γ = 0（P20.5）
    R4 = build_reaction(4, [(0, 1), (1, 2), (2, 3)],
                        [{"w": {(0, 1): 1.0, (1, 2): 1.0, (2, 3): 1.0}, "nH": {}},
                         {"w": {(0, 1): 1.0, (1, 2): 0.0, (2, 3): 1.0}, "nH": {}}],
                        w_I=0.0)
    r4 = operator_20_activation_index(R4)
    check("零权割: γ* = 0（骨架断开，P20.5）", r4["gamma_star"] < 1e-12)
    ks = [operator_20_activation_index(R4, eps=e)["kappa"] for e in (1e-2, 1e-3, 1e-6)]
    print("     零权割: κ(ε=1e-2,1e-3,1e-6) = %.3f, %.3f, %.3f" % tuple(ks))
    check("零权割: κ 随 ε 单调不减（κ ~ 1/ε 发散）",
          ks[0] < ks[1] < ks[2] and ks[2] / ks[1] > 100.0)

    # 6.5 界面桥接：w_I > 0 时不连通的两片被催化剂重新连通
    R5 = build_reaction(4, [(0, 1), (1, 2), (2, 3)],
                        [{"w": {(0, 1): 1.0, (1, 2): 1.0, (2, 3): 1.0}, "nH": {}},
                         {"w": {(0, 1): 1.0, (1, 2): 0.0, (2, 3): 1.0}, "nH": {}}],
                        interface_edges=[(1, 4), (2, 4)], n_boundary=1, w_I=1.0)
    r5 = operator_20_activation_index(R5)
    print("     桥接: γ*=%.4f κ=%.4f（对照 未桥接 γ*=%.4f κ=%.4f）"
          % (r5["gamma_star"], r5["kappa"], r4["gamma_star"], r4["kappa"]))
    check("桥接: γ* > 0 且 κ 显著下降", r5["gamma_star"] > 1e-3 and r5["kappa"] < r4["kappa"])

    # 6.6 T20.3 端点不变性：任意 E_I / w_I 不改 ϱ_tot
    base = operator_20_activation_index(R3)["rho_tot"]
    ok = True
    for wI in (0.0, 0.5, 3.0):
        for ie in ([(0, 3)], [(0, 3), (1, 4)], [(0, 3), (1, 3), (2, 5)]):
            Ra = build_reaction(3, [(0, 1), (1, 2)],
                                [{"w": {(0, 1): 1.0, (1, 2): 1.0}, "nH": {0: 3, 1: 2, 2: 1}},
                                 {"w": {(0, 1): 1.0, (1, 2): 1.0}, "nH": {0: 3, 1: 1, 2: 0}}],
                                interface_edges=ie, n_boundary=3, w_I=wI)
            ok &= abs(operator_20_activation_index(Ra)["rho_tot"] - base) < 1e-12
    check("T20.3: 端点不变性（ϱ_tot 与 E_I/w_I 无关）", ok)

    # 6.7 显式边定向 ς_e（规范 §2.2 / v0.3 新增输入）
    # 同一物理反应（环上键级均匀 +0.5），默认 i<j 参考定向给 ϱ=2/3；
    # 若声明 ς_e 与自然环遍历一致，则被读作纯环通道 ϱ=1。
    E6 = [(i, (i + 1) % 6) for i in range(6)]
    wps6 = [{"w": {e: 1.0 for e in E6}, "nH": {}}, {"w": {e: 1.5 for e in E6}, "nH": {}}]
    r_def = operator_20_activation_index(build_reaction(6, E6, wps6, w_I=0.0))
    ori_nat = orient_from_cycle(6, E6, [0, 1, 2, 3, 4, 5], {e: k for k, e in enumerate(E6)})
    r_ori = operator_20_activation_index(
        build_reaction(6, E6, wps6, w_I=0.0, orient=ori_nat))
    print("     ς_e: 默认 ϱ=%.6f（2/3）; 自然环定向 ς=%s → ϱ=%.6f（1）"
          % (r_def["rho_tot"], ori_nat.astype(int).tolist(), r_ori["rho_tot"]))
    check("ς_e 默认（≡+1）与 v0.2 一致：环均匀 +0.5 ⇒ ϱ = 2/3",
          abs(r_def["rho_tot"] - 2.0 / 3.0) < 1e-12)
    check("ς_e = 自然环遍历定向 ⇒ 同一反应 ϱ = 1（纯环通道）",
          abs(r_ori["rho_tot"] - 1.0) < 1e-12)
    check("ς_e 不影响 κ（κ 用 W，与定向无关）",
          abs(r_ori["kappa"] - r_def["kappa"]) < 1e-12)
    check("ς_e 全局取反不改变 ϱ（δ 与梯度分量同时反号）",
          abs(operator_20_activation_index(
              build_reaction(6, E6, wps6, w_I=0.0, orient=-ori_nat))["rho_tot"]
              - r_ori["rho_tot"]) < 1e-12)
    check("orient 只接受 ±1（0 应报错）",
          _raises(lambda: build_reaction(6, E6, wps6, orient=0.0)))
    check("ς_e 以字典形式给出（单边覆盖）与向量形式等价",
          abs(operator_20_activation_index(
              build_reaction(6, E6, wps6, w_I=0.0, orient={(0, 5): -1.0}))["rho_tot"]
              - r_ori["rho_tot"]) < 1e-12)

    print("\n" + "=" * 78)
    print("[%s] 自测失败项 = %d" % ("SUCCESS" if fails == 0 else "FAIL", fails))
    print("=" * 78)
    return fails


if __name__ == "__main__":
    raise SystemExit(self_test())
