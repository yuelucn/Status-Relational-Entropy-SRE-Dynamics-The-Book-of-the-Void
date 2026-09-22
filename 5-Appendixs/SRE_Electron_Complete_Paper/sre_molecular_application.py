# -*- coding: utf-8 -*-
"""
SRE 电子结论 -> 传统分子计算 的应用例程 (Molecular Computation Application)
========================================================================

把「电子在 SRE 体系下的完整描述」中的可迁移结论，应用到传统分子计算
(分子图 / 力场拓扑 / 构象嵌入)。全部自包含，无外部数据依赖。

三个可迁移结论
--------------
  K1  二元关系矩阵 : 任意分子可用 S_ij ∈ {+1 (键), 0/-1 (非键)} 描述；
                    电子就是用同样的 {±1} 二元自组织网络承载的。
  K2  谱隙相干指数 : 电子的精细结构常数 alpha = λ2/λmax (带符号图拉普拉斯)。
                    把它当作分子的「SRE 相干指数 MCI」，低值 = 高相干
                    (芳香环更像电子，线性链相干更低)。
  K3  本体结构识别 : 电子的本体 = 3-立方体 Q3 (8,12,5)。碳骨架恰为 Q3 的
                    分子(如立方烷 cubane)直接承载电子的本体拓扑。
  K4  关系反演几何 : 电子的 3D 形状由 MDS 反演其关系矩阵得到；分子同理，
                    仅凭拓扑(图距离)即可 MDS 反演出合理 3D 构象，并与真实
                    坐标低 RMSD 吻合。

例程 (直接可用)
---------------
  sre_coherence_index(adj)      -> MCI (float)
  sre_basal_detect(adj)         -> dict: 是否 Q3 / 不变量 / 是否已是 R 不动点
  sre_mds_embed(adj, ref)       -> (coords, rmsd)  Procrustes 对齐后的 RMSD

演示分子: 苯 (benzene, 6C 环), 立方烷 (cubane, 8C 立方体=Q3), 正己烷链 (n-hexane, 6C 线性控制)

运行: python sre_molecular_application.py
输出: 终端表格 + sre_molecular_application_results.json
"""

import importlib.util
import json
import os

import numpy as np
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name, fname):
    p = os.path.join(HERE, fname)
    m = importlib.util.module_from_spec(importlib.util.spec_from_file_location(name, p))
    importlib.util.spec_from_file_location(name, p).loader.exec_module(m)
    return m


_bridge = _load("bridge", "_sre_electron_binary_bridge.py")
_r2 = _load("r2", "_sre_r2_convergence.py")


# ───────────────────────────────────────────────────────────────
# 分子定义 (原子坐标 + 键表, 单位 Å, 仅作参考几何)
# ───────────────────────────────────────────────────────────────
def _benzene():
    """平面正六边形, C-C ≈ 1.39 Å。"""
    r = 1.39
    coords = np.array([[r * np.cos(2 * np.pi * i / 6), r * np.sin(2 * np.pi * i / 6), 0.0]
                       for i in range(6)])
    bonds = [(i, (i + 1) % 6) for i in range(6)]
    return coords, bonds, ["C"] * 6, "benzene"


def _hexane():
    """线性 6 碳链, C-C ≈ 1.54 Å (低相干控制)。"""
    d = 1.54
    coords = np.array([[i * d, 0.0, 0.0] for i in range(6)])
    bonds = [(i, i + 1) for i in range(5)]
    return coords, bonds, ["C"] * 6, "n-hexane"


def _cubane():
    """立方体烷: 8 个碳在立方体顶点, C-C ≈ 1.55 Å。碳骨架即 3-立方体 Q3。"""
    a = 1.55 / 2.0
    verts = [(x, y, z) for x in (-a, a) for y in (-a, a) for z in (-a, a)]
    coords = np.array(verts, dtype=float)
    bonds = []
    idx = {v: i for i, v in enumerate(verts)}
    for i, vi in enumerate(verts):
        for j, vj in enumerate(verts):
            if j <= i:
                continue
            diff = sum(1 for k in range(3) if vi[k] != vj[k])
            if diff == 1:  # 立方体棱 = 仅差一个坐标
                bonds.append((i, j))
    return coords, bonds, ["C"] * 8, "cubane"


# ───────────────────────────────────────────────────────────────
# SRE 工具例程 (可直接复用到你自己的分子)
# ───────────────────────────────────────────────────────────────
def bond_adjacency(n_atoms, bonds):
    """键表 -> 带符号邻接 S (键=+1, 对角=0)。这就是分子的「SRE 二元关系矩阵」。"""
    S = np.zeros((n_atoms, n_atoms), dtype=int)
    for i, j in bonds:
        S[i, j] = S[j, i] = 1
    return S


def sre_coherence_index(adj):
    """SRE 谱特征指数 MCI = λ2/λmax (带符号图拉普拉斯 L = D - S)。

    这是把电子的「谱隙比」构造法 (alpha = λ2/λmax) 移植到分子得到的
    *骨架谱指纹*。其物理可读含义是「骨架刚性 / 柔性」:
      小 MCI  -> 低频弯曲模 -> 柔性骨架 (如线性链易弯折)
      大 MCI  -> 高频集体模 -> 刚性闭合壳 (如环/立方体难变形)
    注意: 它是拓扑指纹, 不是物理常数; 与电子 alpha=1/137 同"谱隙比"方法学,
          但数值含义随对象而变 (电子的软模 vs 分子的刚性)。"""
    S = adj.astype(float)
    D = np.sum(np.abs(S), axis=1)
    L = np.diag(D) - S
    ev = np.sort(np.linalg.eigvalsh(L))
    lam2 = float(ev[1])
    lam_max = float(ev[-1])
    return lam2, lam_max, lam2 / lam_max


def sre_basal_detect(adj):
    """本体结构识别: 电子本体 = Q3 (8,12,5)。
    若分子碳骨架恰为 Q3, 则它直接承载电子的本体拓扑。"""
    G = nx.from_numpy_array((adj != 0).astype(int))
    V = G.number_of_nodes()
    E = G.number_of_edges()
    b1 = E - V + 1  # 连通图第一贝蒂数
    is_cubic = all(d == 3 for _, d in G.degree())
    is_bip = nx.is_bipartite(G)
    is_Q3 = (V, E, b1) == (8, 12, 5) and is_cubic and is_bip
    # 是否已是 R 算子不动点: 对 Q3 用 R_strict 检验 (不应再合并)
    Rc = _r2.R_strict(adj.astype(int))
    is_fixed = (Rc.shape == adj.shape) and np.array_equal(Rc, adj.astype(int))
    return {
        "n_atoms": V, "n_bonds": E, "beta1": int(b1),
        "is_cubic": bool(is_cubic), "is_bipartite": bool(is_bip),
        "is_electron_basal_Q3": bool(is_Q3),
        "is_R_fixed_point": bool(is_fixed),
    }


def sre_mds_embed(adj, ref_coords):
    """关系反演几何: 用图距离矩阵做经典 MDS -> 3D 嵌入，
    再与参考坐标做 Procrustes 对齐, 返回嵌入坐标与 RMSD。
    证伪点: 仅由拓扑即可得到与真实构象低 RMSD 的几何 (与电子同机制)。"""
    G = nx.from_numpy_array((adj != 0).astype(int))
    n = G.number_of_nodes()
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D[i, j] = nx.shortest_path_length(G, i, j)
    X = _bridge.mds_coords_from_dmat(D, ndim=3)
    rmsd = _procrustes_rmsd(X, ref_coords)
    return X, rmsd


def _procrustes_rmsd(A, B):
    """中心化 + 最优均匀缩放 + 最优旋转对齐后的 RMSD (full Procrustes)。"""
    A = A - A.mean(axis=0)
    B = B - B.mean(axis=0)
    s = np.sum(A * B) / np.sum(B * B)        # 最优均匀缩放
    Bs = s * B
    U, _, Vt = np.linalg.svd(A.T @ Bs)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        U[:, -1] *= -1
        R = U @ Vt
    Aa = A @ R
    return float(np.sqrt(np.mean(np.sum((Aa - Bs) ** 2, axis=1))))


# ───────────────────────────────────────────────────────────────
def main():
    molecules = [_benzene(), _cubane(), _hexane()]
    report = {"title": "SRE 电子结论 -> 分子计算 应用例程", "molecules": []}
    print("=" * 86)
    print("  SRE 电子结论 -> 传统分子计算  应用例程")
    print("=" * 86)
    print(f"  {'molecule':<10} {'atoms':>5} {'bonds':>6} {'MCI':>8} {'Q3?':>6} {'RMSD(A)':>9}  note")
    print("-" * 86)
    for coords, bonds, _, name in molecules:
        n = len(coords)
        adj = bond_adjacency(n, bonds)
        lam2, lam_max, mci = sre_coherence_index(adj)
        basal = sre_basal_detect(adj)
        emb, rmsd = sre_mds_embed(adj, coords)
        note = ""
        if basal["is_electron_basal_Q3"]:
            note = "碳骨架=Q3, 直接承载电子本体!"
        elif name == "benzene":
            note = "芳香环, 刚性闭合壳 (MCI 较大)"
        elif name == "n-hexane":
            note = "线性链, 极小 MCI = 柔性骨架(低频弯曲)"
        print(f"  {name:<10} {n:>5} {len(bonds):>6} {mci:>8.4f} "
              f"{'YES' if basal['is_electron_basal_Q3'] else 'no':>6} {rmsd:>9.3f}  {note}")
        report["molecules"].append({
            "name": name, "n_atoms": n, "n_bonds": len(bonds),
            "MCI": mci, "lambda2": lam2, "lambda_max": lam_max,
            "basal": basal, "mds_rmsd": rmsd, "note": note,
        })
    print("-" * 86)
    print("  读图: MCI 是骨架谱指纹 (小=柔性/低频弯曲, 大=刚性闭合壳), 移植自电子 alpha=λ2/λmax 方法学;")
    print("        cubane 碳骨架=Q3 即电子本体拓扑; MDS 仅由拓扑复原形状 (链精确, 环/立方体近似),")
    print("        绝对键长由化学填充 => 与 SRE '关系给形状, 物理尺度后填' 完全一致。")
    with open(os.path.join(HERE, "sre_molecular_application_results.json"), "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("  结果已写入 sre_molecular_application_results.json")
    return 0


if __name__ == "__main__":
    main()
