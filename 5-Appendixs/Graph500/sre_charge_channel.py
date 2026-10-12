# sre_charge_channel.py
import logging
from typing import Optional, List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None


class SREChargeChannelSuite:
    """
    SRE 动力学第七层：电荷符号 / ℤ₂ holonomy 通道层 (Operator 19)
    声明：此模块把电荷涌现的严格 σ 落到电子算子的分子键图上，给出
    σ_class（平凡判别）、σ_reachability（Aut-不变可达性）、deg 与 Q_model。
    依赖：numpy；networkx 为可选（仅用于自同构枚举与可达性分析）。
    """

    def __init__(
        self,
        aut_cap: int = 100000,
        aut_max_v: int = 22,
        eps: float = 1e-12,
        enable_debug_log: bool = True,
    ):
        """
        初始化电荷通道套件参数

        参数:
            aut_cap: int, 自同构枚举上限
            aut_max_v: int, 顶点数守卫（超限则跳过可达性分析）
            eps: float, 键图支撑判定阈值
            enable_debug_log: bool, 是否启用调试日志
        """
        if aut_cap <= 0:
            raise ValueError(f"aut_cap 必须为正整数，当前输入: {aut_cap}")
        if aut_max_v <= 0:
            raise ValueError(f"aut_max_v 必须为正整数，当前输入: {aut_max_v}")
        if eps <= 0:
            raise ValueError(f"eps 必须大于 0，当前输入: {eps}")

        self.aut_cap = aut_cap
        self.aut_max_v = aut_max_v
        self.eps = eps
        self.enable_debug_log = enable_debug_log

    def _log_debug(self, msg: str, *args):
        """控制调试日志输出"""
        if self.enable_debug_log:
            logger.debug(msg, *args)

    # =========================================================================
    # 1. 键图与图不变量
    # =========================================================================
    def bond_graph_from_As(self, A_s: np.ndarray) -> np.ndarray:
        """由 SRE 平滑邻接 A_s 的支撑取键图（E+ 协同边）的布尔邻接"""
        A = np.asarray(A_s, dtype=np.float64)
        adj = A > self.eps
        np.fill_diagonal(adj, False)
        adj = adj & adj.T
        return adj

    @staticmethod
    def edge_list(adj: np.ndarray) -> List[Tuple[int, int]]:
        """无向边表（有序对，i < j）"""
        n = adj.shape[0]
        return [(i, j) for i in range(n) for j in range(i + 1, n) if adj[i, j]]

    @staticmethod
    def graph_invariants(adj: np.ndarray) -> Dict[str, Any]:
        """V, E, 连通分支 c, β₁ = E − V + c, deg = β₁ mod 2, 二分性, 奇环是否存在"""
        n = adj.shape[0]
        E = int(adj.sum() // 2)

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
            "V": int(n), "E": int(E), "c": int(c),
            "beta1": int(beta1), "deg": int(beta1 % 2),
            "bipartite": bool(bipartite), "has_odd_cycle": bool(not bipartite),
        }

    # =========================================================================
    # 2. 环基与 holonomy（严格 ℤ₂）
    # =========================================================================
    def fundamental_cycle_basis(self, adj: np.ndarray) -> List[List[int]]:
        """生成树 + 每条非树边的基本环（标准基本环基）"""
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
        for (u, v) in self.edge_list(adj):
            if (u, v) in tree_edges:
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

    @staticmethod
    def cycle_holonomy(cycle: List[int], s_e: Dict[Tuple[int, int], float]) -> float:
        """σ(γ) = ∏_{e∈γ} s_e ∈ {+1, −1}"""
        h = 1.0
        L = len(cycle)
        for k in range(L):
            a, b = cycle[k], cycle[(k + 1) % L]
            h *= s_e[(min(a, b), max(a, b))]
        return h

    def holonomy_class(self, cycles: List[List[int]], s_e: Dict) -> Dict[str, Any]:
        """给定边极性与环基，返回 holonomy 向量与「是否平凡」"""
        vec = tuple(self.cycle_holonomy(c, s_e) for c in cycles)
        trivial = all(v > 0 for v in vec)
        return {
            "vector": vec,
            "is_trivial": bool(trivial),
            "sigma_class": "trivial(+)" if trivial else "nontrivial(-)",
            "n_cycles": len(cycles),
            "n_nontrivial_cycles": int(sum(1 for v in vec if v < 0)),
        }

    # =========================================================================
    # 3. 边极性（两种口径）
    # =========================================================================
    def polarity_topo(self, adj: np.ndarray) -> Dict[Tuple[int, int], float]:
        """拓扑口径：键上 s_e = +1（SRE 公理 1 协同边）"""
        return {e: 1.0 for e in self.edge_list(adj)}

    def polarity_spin(self, adj: np.ndarray, chi: np.ndarray) -> Dict[Tuple[int, int], float]:
        """顶点势口径：s_e = s_i · s_j（s_i = sign(χ_i − χ_mean)）"""
        chi = np.asarray(chi, dtype=np.float64)
        s = np.sign(chi - np.mean(chi))
        s[s == 0] = 1.0
        return {e: float(s[e[0]] * s[e[1]]) for e in self.edge_list(adj)}

    # =========================================================================
    # 4. Aut-不变可达性（ℤ₂ 线性判据）
    # =========================================================================
    def automorphisms(self, adj: np.ndarray, colors=None) -> Tuple[list, bool]:
        """枚举自同构映射（capped）。返回 (auts, capped_flag)"""
        if nx is None:  # pragma: no cover
            raise RuntimeError("networkx 不可用，无法枚举自同构")
        G = nx.Graph()
        G.add_nodes_from(range(adj.shape[0]))
        G.add_edges_from(self.edge_list(adj))
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
            if len(auts) >= self.aut_cap:
                capped = True
                break
        return auts, capped

    def edge_orbits(self, adj: np.ndarray, auts: list) -> list:
        """边在 Aut 作用下的轨道（并查集）"""
        edges = self.edge_list(adj)
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

    def reachability_z2(self, adj: np.ndarray, cycles: list, orbits: list) -> Dict[str, Any]:
        """Aut-不变赋值下，「非平凡 holonomy 类」是否可达"""
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

    # =========================================================================
    # 算子 19: ℤ₂ holonomy / σ 电荷通道
    # =========================================================================
    def execute_operator_19_z2_charge_channel(
        self,
        A_s: np.ndarray,
        chi: Optional[np.ndarray] = None,
        elements=None,
        polarity: str = "topo",
    ) -> Dict[str, Any]:
        """
        Operator 19 —— ℤ₂ holonomy / σ 通道（把电荷涌现的 σ 落到电子算子的键图上）。

        参数:
            A_s: np.ndarray, (N,N) SRE 平滑邻接（运算符 1/4 输出；键图支撑 = A_s > 0）
            chi: np.ndarray, (N,) Pauling 电负性（polarity="spin" 时必需）
            elements: list, 元素标号（用于保色自同构）
            polarity: str, {"topo", "spin"} 边极性口径

        返回 (dict):
            图不变量 + σ 类 + 可达性 + deg + Q_model
        """
        if not isinstance(A_s, np.ndarray) or A_s.ndim != 2 or A_s.shape[0] != A_s.shape[1]:
            raise ValueError(f"A_s 必须为二维方阵，当前形状: {getattr(A_s, 'shape', None)}")
        if polarity not in ("topo", "spin"):
            raise ValueError(f"polarity 必须为 'topo' 或 'spin'，当前输入: {polarity}")
        if polarity == "spin" and chi is None:
            raise ValueError("polarity='spin' 时必须提供 chi（电负性向量）")

        adj = self.bond_graph_from_As(A_s)
        n = adj.shape[0]
        inv = self.graph_invariants(adj)
        cycles = self.fundamental_cycle_basis(adj)

        s_e = self.polarity_topo(adj) if polarity == "topo" else self.polarity_spin(adj, chi)
        hc = self.holonomy_class(cycles, s_e)

        out = {
            "V": inv["V"], "E": inv["E"], "c": inv["c"],
            "beta1": inv["beta1"], "deg": inv["deg"],
            "bipartite": inv["bipartite"], "has_odd_cycle": inv["has_odd_cycle"],
            "polarity": polarity,
            "n_cycles": hc["n_cycles"],
            "sigma_vector": [int(v) for v in hc["vector"]],
            "sigma_class": hc["sigma_class"],
            "sigma_trivial": hc["is_trivial"],
            "sigma_canonical": +1.0 if hc["is_trivial"] else -1.0,
            "Q_model": (+1.0 if hc["is_trivial"] else -1.0) * inv["deg"],
            "reachability": None,
            "reachability_skipped": None,
        }

        if n <= self.aut_max_v and nx is not None:
            auts, capped = self.automorphisms(adj, colors=elements)
            orbits = self.edge_orbits(adj, auts)
            reach = self.reachability_z2(adj, cycles, orbits)
            reach.update({"n_aut": len(auts), "aut_capped": bool(capped),
                          "element_colored": elements is not None})
            out["reachability"] = reach
            out["channel_type"] = (
                "electron-like(forced trivial)" if not reach["nontrivial_reachable"]
                else "nucleon-like(nontrivial allowed)")

            if polarity == "spin" and chi is not None:
                s = np.sign(np.asarray(chi, float) - np.mean(np.asarray(chi, float)))
                s[s == 0] = 1.0
                out["spin_net_sign"] = int(np.prod(s))
        else:
            out["reachability_skipped"] = (
                "V>%d" % self.aut_max_v if n > self.aut_max_v else "networkx 不可用")
            out["channel_type"] = "unknown(skipped)"

        self._log_debug(
            "算子 19 执行成功 | V=%d, E=%d, beta1=%d, sigma_class=%s, channel=%s",
            out["V"], out["E"], out["beta1"], out["sigma_class"], out["channel_type"]
        )
        return out

    # =========================================================================
    # 工具：压缩为标量键
    # =========================================================================
    @staticmethod
    def charge_channel_keys(res: Dict[str, Any]) -> Dict[str, Any]:
        """把 Operator 19 结果压成可并入指纹字典的标量键（前缀 z2_）"""
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
