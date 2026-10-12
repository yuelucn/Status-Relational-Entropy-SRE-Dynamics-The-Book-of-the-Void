# sre_electronic_layer.py
import logging
from typing import Optional, List, Dict, Any, Tuple
import numpy as np

logger = logging.getLogger(__name__)


class SREElectronicOperatorSuite:
    """
    SRE 动力学第五层：电子自由度扩展层 (Operators 11, 12)
    声明：此模块在 SRE 平滑邻接矩阵 A_s 上叠加电负性差强度，将电子自由度
    编码为图的边权重增益，并通过简单环枚举 + SRE 符号矩阵相位审计检测
    "N 尺度拓扑闭合环 + Möbius 双层相位" 模式。
    依赖：仅 numpy（内置 Pauling 电负性表 + 共价半径表 + GAFF2 元素映射）。
    """
    # Pauling 电负性表
    _PAULING_ELECTRONEGATIVITY = {
        "H": 2.20, "He": 0.00,
        "Li": 0.98, "Be": 1.57, "B": 2.04, "C": 2.55, "N": 3.04, "O": 3.44, "F": 3.98, "Ne": 0.00,
        "Na": 0.93, "Mg": 1.31, "Al": 1.61, "Si": 1.90, "P": 2.19, "S": 2.58, "Cl": 3.16, "Ar": 0.00,
        "K": 0.82, "Ca": 1.00, "Sc": 1.36, "Ti": 1.54, "V": 1.63, "Cr": 1.66, "Mn": 1.55,
        "Fe": 1.83, "Co": 1.88, "Ni": 1.91, "Cu": 1.90, "Zn": 1.65, "Ga": 1.81, "Ge": 2.01,
        "As": 2.18, "Se": 2.55, "Br": 2.96, "Kr": 3.00,
        "Rb": 0.82, "Sr": 0.95, "I": 2.66, "Xe": 2.60,
        "Cs": 0.79, "Ba": 0.89,
    }

    # 共价半径表（Å），用于化学键判定：d < (r_i + r_j) * factor
    _COVALENT_RADIUS = {
        "H": 0.31, "C": 0.76, "N": 0.71, "O": 0.66, "F": 0.57,
        "Cl": 1.02, "S": 1.05, "P": 1.07, "Br": 1.20, "I": 1.39,
        "Na": 1.66, "Mg": 1.41, "Si": 1.11, "B": 0.84, "Li": 1.28,
        "K": 2.03, "Ca": 1.76, "Fe": 1.32, "Zn": 1.22, "Cu": 1.32,
    }

    # GAFF2 atomtype → element mapping
    _GAFF2_TO_ELEMENT = {
        "c3": "C", "c2": "C", "c1": "C", "ca": "C", "cc": "C", "cd": "C",
        "ce": "C", "cf": "C", "cg": "C", "ch": "C", "ci": "C", "cj": "C",
        "cp": "C", "cq": "C", "cv": "C", "cw": "C", "cx": "C", "cy": "C",
        "cz": "C", "c": "C",
        "n3": "N", "n2": "N", "n1": "N", "na": "N", "nb": "N", "nc": "N",
        "nd": "N", "ne": "N", "nf": "N", "ng": "N", "nh": "N", "ni": "N",
        "nj": "N", "nk": "N", "nl": "N", "nm": "N", "nn": "N", "no": "N",
        "nv": "N", "n": "N",
        "o": "O", "oh": "O", "os": "O", "o2": "O", "op": "O",
        "s": "S", "s2": "S", "sh": "S", "ss": "S", "sx": "S", "sy": "S",
        "s4": "S", "s6": "S",
        "p2": "P", "p3": "P", "p4": "P", "p5": "P", "px": "P", "pb": "P",
        "h1": "H", "h2": "H", "h3": "H", "h4": "H", "h5": "H",
        "hc": "H", "hn": "H", "ho": "H", "hp": "H", "hs": "H", "hw": "H",
        "hx": "H", "hy": "H",
        "f": "F", "cl": "Cl", "br": "Br", "i": "I",
        "mg": "Mg", "ca_ion": "Ca", "zn": "Zn", "fe": "Fe",
        "OW_spc": "O", "HW_spc": "H", "OW": "O", "HW": "H",
        "NA": "Na", "K_ion": "K", "CL": "Cl", "NA_ion": "Na",
    }

    def __init__(
        self,
        rho: float = 0.5,
        bond_factor: float = 1.25,
        eps_topo: float = 1e-6,
        N_max_default: int = 8,
        enable_debug_log: bool = True,
    ):
        """
        初始化电子自由度算子套件参数与防护阈值

        参数:
            rho: float, 电负性差调制强度 (默认 0.5)
            bond_factor: float, 共价半径键判定倍数 (默认 1.25)
            eps_topo: float, 拓扑正则化下界 (默认 1e-6)
            N_max_default: int, 算子 12 默认最大环长度 (默认 8)
            enable_debug_log: bool, 是否启用调试日志
        """
        if rho < 0:
            raise ValueError(f"rho 必须非负，当前输入: {rho}")
        if bond_factor <= 0:
            raise ValueError(f"bond_factor 必须大于 0，当前输入: {bond_factor}")
        if eps_topo <= 0:
            raise ValueError(f"eps_topo 必须大于 0，当前输入: {eps_topo}")
        if N_max_default < 3:
            raise ValueError(f"N_max_default 必须至少为 3，当前输入: {N_max_default}")

        self.rho = rho
        self.bond_factor = bond_factor
        self.eps_topo = eps_topo
        self.N_max_default = N_max_default
        self.enable_debug_log = enable_debug_log

    def _log_debug(self, msg: str, *args):
        """控制调试日志输出"""
        if self.enable_debug_log:
            logger.debug(msg, *args)

    # =========================================================================
    # 工具：元素/电负性转换与化学键判定
    # =========================================================================
    def gaff2_to_element(self, atomtype: str) -> str:
        """将 GAFF2/GROMACS atomtype 映射为元素符号"""
        at = str(atomtype).strip()
        if at in self._GAFF2_TO_ELEMENT:
            return self._GAFF2_TO_ELEMENT[at]
        first = at[0].upper()
        if first in self._PAULING_ELECTRONEGATIVITY:
            return first
        return "C"

    def get_electronegativity(self, element: str) -> float:
        """获取元素的 Pauling 电负性"""
        return self._PAULING_ELECTRONEGATIVITY.get(element, 2.0)

    def electronegativities_from_atomtypes(self, atomtypes: list) -> np.ndarray:
        """将 GAFF2 atomtype 列表转换为电负性向量"""
        chis = [self.get_electronegativity(self.gaff2_to_element(at)) for at in atomtypes]
        return np.array(chis, dtype=np.float64)

    def elements_from_atomtypes(self, atomtypes: list) -> list:
        """将 GAFF2 atomtype 列表转换为元素符号列表"""
        return [self.gaff2_to_element(at) for at in atomtypes]

    def infer_bonds(self, positions_xyz: np.ndarray, elements: list = None) -> list:
        """
        由坐标 + 元素符号判定化学键：d_ij < (r_i + r_j) * bond_factor。
        无元素信息时退化为距离阈值 1.85 Å。

        参数:
            positions_xyz: np.ndarray, (N, 3) 原子坐标
            elements: list, 元素符号列表；None 时用距离阈值

        返回:
            bonds: list[(int, int)], 化学键列表（i < j）
        """
        X = np.asarray(positions_xyz, dtype=np.float64)
        n = len(X)
        D2 = np.sum((X[:, None, :] - X[None, :, :]) ** 2, axis=2)
        D = np.sqrt(np.maximum(D2, 0.0))
        if elements is None:
            self._log_debug("infer_bonds: 无元素信息，使用 1.85 Å 距离阈值")
            cutoff = np.full((n, n), 1.85)
        else:
            radii = np.array([self._COVALENT_RADIUS.get(el, 0.76) for el in elements])
            cutoff = (radii[:, None] + radii[None, :]) * self.bond_factor
        bonds = []
        for i in range(n):
            for j in range(i + 1, n):
                if D[i, j] < cutoff[i, j]:
                    bonds.append((i, j))
        return bonds

    # =========================================================================
    # 工具：SRE 平滑邻接与符号矩阵
    # =========================================================================
    def build_sre_smooth_adjacency(
        self,
        positions_xyz: np.ndarray,
        atomtypes: list = None,
        bonds: list = None,
    ) -> np.ndarray:
        """
        构建 SRE 平滑邻接 A_s = W_e ⊙ P+（定义 3.1/3.2）。
        P+ 为化学键支撑投影；W_e 为算子 4 平滑权重；M 为 SRE 符号矩阵。
        不使用 k-NN；不使用全连通距离核。

        参数:
            positions_xyz: np.ndarray, (N, 3) 原子坐标
            atomtypes: list, GAFF2 atomtype 列表（用于推断元素）
            bonds: list, 化学键列表；None 时由坐标推断

        返回:
            A_s: np.ndarray, (N, N) SRE 平滑邻接矩阵
        """
        X = np.asarray(positions_xyz, dtype=np.float64)
        n = len(X)
        if bonds is None:
            elements = self.elements_from_atomtypes(atomtypes) if atomtypes else None
            bonds = self.infer_bonds(X, elements)

        bond = np.zeros((n, n), dtype=bool)
        for i, j in bonds:
            bond[i, j] = bond[j, i] = True

        # 键图拉普拉斯（Fiedler / 谱半径）
        A_b = bond.astype(float)
        deg_b = A_b.sum(axis=1)
        L_b = np.diag(deg_b) - A_b
        ev_b = np.linalg.eigvalsh(L_b)
        lam2 = float(ev_b[1]) if n > 1 else 0.0
        alpha = float(ev_b[-1]) if n > 0 else 1.0

        # SRE 符号矩阵 M（公理 1：无零元）
        M = np.where(bond, 1.0, -1.0)
        np.fill_diagonal(M, 1.0)

        D_ii = np.abs(M).sum(axis=1)
        D_self = np.diag(M).copy()
        num = np.sqrt(np.outer(D_ii, D_ii))
        denom = np.sqrt(lam2 + D_self[:, None] + D_self[None, :] + self.eps_topo)
        M2 = M @ M
        damp = 1.0 + np.abs(M2) * np.log(1.0 + lam2 / max(alpha, 1e-12)) \
            / (alpha + np.sqrt(np.outer(D_ii, D_ii)))
        W_e = (num / denom) * damp
        A_s = W_e * bond.astype(float)
        np.fill_diagonal(A_s, 0.0)
        self._log_debug("SRE 平滑邻接构建完成 | N=%d, 键数=%d", n, len(bonds))
        return A_s

    @staticmethod
    def sre_sign_matrix(A_s: np.ndarray) -> np.ndarray:
        """
        由平滑邻接支撑反推 SRE 符号矩阵 M：
        M_ij = +1 若 A_s_ij > 0（协同边），否则 -1；对角 +1。
        """
        M = np.where(A_s > 0, 1.0, -1.0)
        np.fill_diagonal(M, 1.0)
        return M

    # =========================================================================
    # 算子 11: 自旋-电荷邻接算子 (Spin-Charge Adjacency)
    # =========================================================================
    def execute_operator_11_spin_charge_adjacency(
        self,
        A_s: np.ndarray,
        electronegativities: np.ndarray,
        rho: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Operator 11 — Spin-Charge Adjacency（规范式 (4.1)-(4.6)）。

        权重调制（解耦自旋极性）:
            w_q(i,j)  = |tanh(chi_i - chi_j)|
            A_q(i,j)  = A_s(i,j) * (1 + rho * w_q(i,j))
            L_q       = diag(A_q 1) - A_q
            lambda_2_q = λ2(L_q), alpha_q = max|λ(L_q)|,
            kappa_q    = alpha_q / lambda_2_q

        诊断标量（s/sigma/d 仅用于诊断，不参与调制）:
            s_i        = sign(chi_i - chi_mean)
            sigma_ij   = s_i * s_j, d_ij = (1 - sigma_ij)/2
            q_dispersion      = std(|chi|) / mean(|chi|)
            max_spin_coupling = max_{(i,j) in E+} |sigma_ij * w_q(i,j)|

        参数:
            A_s: np.ndarray, (N, N) SRE 平滑邻接矩阵
            electronegativities: np.ndarray, (N,) Pauling 电负性向量
            rho: float, 调制强度（默认取 __init__ 的 rho）

        返回 (dict):
            A_q, L_q, lambda_2_q, alpha_q, kappa_q,
            q_dispersion, max_spin_coupling, s, sigma, d, wq
        """
        if not isinstance(A_s, np.ndarray) or A_s.ndim != 2 or A_s.shape[0] != A_s.shape[1]:
            raise ValueError(f"A_s 必须为二维方阵，当前形状: {getattr(A_s, 'shape', None)}")
        chi = np.asarray(electronegativities, dtype=np.float64)
        if chi.ndim != 1 or chi.shape[0] != A_s.shape[0]:
            raise ValueError(
                f"electronegativities 形状异常: 期望 ({A_s.shape[0]},)，实际 {chi.shape}"
            )

        rho_eff = rho if rho is not None else self.rho
        N = len(chi)

        # 自旋极性（诊断量）
        chi_mean = np.mean(chi)
        s = np.sign(chi - chi_mean)
        s[s == 0] = 1.0
        sigma = np.outer(s, s)
        d = (1.0 - sigma) / 2.0

        # 权重调制
        wq = np.abs(np.tanh(chi[:, None] - chi[None, :]))
        A_q = A_s * (1.0 + rho_eff * wq)
        np.fill_diagonal(A_q, 0.0)

        # 谱量
        deg = A_q.sum(axis=1)
        L_q = np.diag(deg) - A_q
        eigvals = np.linalg.eigvalsh(L_q)
        lambda_2_q = float(eigvals[1]) if N > 1 else 0.0
        alpha_q = float(np.max(np.abs(eigvals)))
        kappa_q = alpha_q / lambda_2_q if lambda_2_q > 1e-12 else float("inf")

        q_dispersion = float(np.std(np.abs(chi)) / (np.mean(np.abs(chi)) + 1e-12))

        support = A_s > 0
        sc_sup = np.abs(sigma * wq)[support]
        max_spin_coupling = float(np.max(sc_sup)) if support.any() else 0.0

        self._log_debug(
            "算子 11 执行成功 | lambda_2_q=%.6e, alpha_q=%.6e, kappa_q=%.6e, max_spin_coupling=%.6e",
            lambda_2_q, alpha_q, kappa_q, max_spin_coupling
        )

        return {
            "A_q": A_q, "L_q": L_q,
            "lambda_2_q": lambda_2_q, "alpha_q": alpha_q, "kappa_q": kappa_q,
            "q_dispersion": q_dispersion, "max_spin_coupling": max_spin_coupling,
            "s": s, "sigma": sigma, "d": d, "wq": wq,
        }

    # =========================================================================
    # 算子 12: 拓扑闭合环审计算子 (Topological Closed-Loop Audit)
    # =========================================================================
    def enumerate_simple_cycles(self, adj: np.ndarray, N_max: int) -> list:
        """
        DFS 枚举长度 <= N_max 的简单环（无向图）。
        无回溯（路径内顶点不重复）、无重复计数。

        参数:
            adj: np.ndarray, 邻接矩阵（非零表示边）
            N_max: int, 最大环长度

        返回:
            cycles: list[list[int]], 简单环顶点序列列表
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

    def execute_operator_12_closed_loop_audit(
        self,
        A_q: np.ndarray,
        M: np.ndarray = None,
        N_max: int = None,
    ) -> Dict[str, Any]:
        """
        Operator 12 — Topological Closed-Loop Audit（规范式 (5.1)-(5.4)）。

        n_loops       = 简单环计数（定义 5.2；定理 12.2 消除回溯污染）
        mobius_ratio  = mean_{k=3..N_max} |tr(M^k)| / n^k（定义 5.3；
                        定理 12.3 符号平衡判据：=1 ⟺ 无 Möbius，<1 ⟺ 有）
        lambda_2_loop = λ2(L_q[S,S])，S = 环原子并集（定义 5.4；
                        定理 12.5 交错：λ2_loop >= λ2_q > 0）
        kappa_loop    = λmax(L_q[S,S]) / λ2(L_q[S,S])（<= kappa_q）

        参数:
            A_q: np.ndarray, 电荷加权邻接矩阵（Operator 11 输出）
            M: np.ndarray, SRE 符号矩阵；None 时由 A_q 支撑反推
            N_max: int, 最大环长度枚举上限（默认 N_max_default）

        返回 (dict):
            n_loops, n_closed_loops, mobius_ratio,
            lambda_2_loop, kappa_loop, loop_atoms
        """
        if not isinstance(A_q, np.ndarray) or A_q.ndim != 2 or A_q.shape[0] != A_q.shape[1]:
            raise ValueError(f"A_q 必须为二维方阵，当前形状: {getattr(A_q, 'shape', None)}")

        N = A_q.shape[0]
        if N_max is None:
            N_max = min(N, self.N_max_default)
        if N_max < 3:
            raise ValueError(f"N_max 必须至少为 3，当前输入: {N_max}")

        if M is None:
            M = self.sre_sign_matrix(A_q)

        cycles = self.enumerate_simple_cycles(A_q, N_max)
        n_loops = len(cycles)
        loop_atoms = sorted(set(v for c in cycles for v in c))

        # Möbius 相位比（定义 5.3）
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

        self._log_debug(
            "算子 12 执行成功 | n_loops=%d, mobius_ratio=%.6e",
            n_loops, mobius_ratio
        )

        return {
            "n_loops": n_loops,
            "n_closed_loops": n_loops,
            "mobius_ratio": mobius_ratio,
            "lambda_2_loop": lambda_2_loop,
            "kappa_loop": kappa_loop,
            "loop_atoms": loop_atoms,
        }

    # =========================================================================
    # 组合：电子指纹（7 键）
    # =========================================================================
    def compute_electronic_fingerprint(
        self,
        positions_xyz: np.ndarray,
        A_smooth: np.ndarray,
        electronegativities: np.ndarray,
        rho: Optional[float] = None,
        N_max: int = None,
    ) -> Dict[str, float]:
        """
        完整电子 SRE 指纹（7 键，不重叠既有几何 4 键）。

        参数:
            positions_xyz: np.ndarray, (N, 3) 原子坐标（保留接口，未直接使用）
            A_smooth: np.ndarray, (N, N) 上游算子 1/4 输出的 SRE 平滑邻接
            electronegativities: np.ndarray, (N,) 电负性向量
            rho: float, 调制强度
            N_max: int, 环枚举上限

        返回 (dict, 7 个标量):
            lambda_2_q, kappa_q, alpha_q, n_loops, mobius_ratio,
            q_dispersion, max_spin_coupling
        """
        M = self.sre_sign_matrix(A_smooth)
        op11 = self.execute_operator_11_spin_charge_adjacency(A_smooth, electronegativities, rho)
        op12 = self.execute_operator_12_closed_loop_audit(op11["A_q"], M, N_max)
        return {
            "lambda_2_q": op11["lambda_2_q"],
            "kappa_q": op11["kappa_q"],
            "alpha_q": op11["alpha_q"],
            "n_loops": op12["n_loops"],
            "mobius_ratio": op12["mobius_ratio"],
            "q_dispersion": op11["q_dispersion"],
            "max_spin_coupling": op11["max_spin_coupling"],
        }
