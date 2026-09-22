"""
SRE 核子图验证 (Point 2)
==========================

把原子核映射为 SRE 关系图：节点 = 核子(p/n)，边 = 核子间关联(配对/壳层耦合)。
完全不喂坐标 —— 这正是 SRE 的本体论起点(维无关二进制关系网)。

两条管线：
  1. 谱相变扫描：随核子数 M 增大，检验魔数(2,8,20,28,50,82,126)是否以
     拓扑不变量(λ2 / n_loops)的刚性跳变形式出现 —— 与嵌入无关，反演之前即可检验。
  2. MDS 反演：对全核(16O / 40Ca)由纯关系图反求 3D 坐标，演示核空间形状从关系涌现。

两种图构造(关键对照)：
  [A] 壳层/配对关系图  —— 编码核壳层结构(魔数之源)。预期魔数处出现 λ2 跳变。
  [B] 几何邻近图        —— 球内晶格填充、按距离连边(无壳层信息)。负对照：预期魔数处无跳变。

诚实声明：壳层图里的"魔数"是壳模型容量(2,6,12,8,22,32,44)直接编码进去的，
因此 λ2 跳变是壳层结构的"拓扑重表达/一致性检查"，而非 SRE 从裸核子独立导出魔数。
几何邻近图则证明：不含壳层信息的核子堆积无法复现魔数 —— 这正是该阴性对照的意义。
"""
import numpy as np
import json
import math
import sys
sys.path.insert(0, r"C:\mywork\vasp")
from sre_electronic_ops_v11 import build_sre_smooth_adjacency

# --- 核壳层模型容量(质子/中子同序；自旋-轨道劈裂) ---
SHELL_CAP = [2, 6, 12, 8, 22, 32, 44, 58]  # 末项覆盖至 A=184，扫描到130无孤立点
MAGIC = [2, 8, 20, 28, 50, 82, 126]


# ---------------------------------------------------------------------------
# 1. 壳层 / 配对关系图
# ---------------------------------------------------------------------------
def fill_scheme(M):
    """把 M 个核子按壳容量填充，返回 [(壳序号, 占据数), ...]。"""
    occ = []
    rem = M
    for i, c in enumerate(SHELL_CAP):
        if rem <= 0:
            break
        t = min(rem, c)
        occ.append((i, t))
        rem -= t
    return occ


def shell_adjacency(M):
    """壳层图：每个壳内占据核子构成团(clique, 权重1)；相邻壳之间弱耦合(权重0.3)。"""
    occ = fill_scheme(M)
    V = M
    A = np.zeros((V, V))
    spans = []
    start = 0
    for (si, t) in occ:
        idxs = list(range(start, start + t))
        for a in idxs:
            for b in idxs:
                if a != b:
                    A[a, b] = 1.0
        spans.append((start, t))
        start += t
    for k in range(len(spans) - 1):
        s1, t1 = spans[k]
        s2, t2 = spans[k + 1]
        for a in range(s1, s1 + t1):
            for b in range(s2, s2 + t2):
                A[a, b] = A[b, a] = 0.3
    return A


# ---------------------------------------------------------------------------
# 2. 几何邻近图(负对照)
# ---------------------------------------------------------------------------
def geometric_positions(M, r0=1.2, seed=0):
    R = r0 * M ** (1.0 / 3.0)
    # 用密集晶格(固定小间距)取中心最近的 M 个点，保证任意 M≥2 都有足够候选
    d = 0.5
    n_grid = int(math.ceil(2 * R / d)) + 2
    pts = []
    for i in range(-n_grid, n_grid + 1):
        for j in range(-n_grid, n_grid + 1):
            for k in range(-n_grid, n_grid + 1):
                p = np.array([i, j, k], float) * d
                if np.linalg.norm(p) <= R:
                    pts.append(p)
    pts = np.array(pts)
    if len(pts) < M:  # 极端兜底：再放宽到无限栅格取最近 M
        allg = []
        g = int(math.ceil(M ** (1.0 / 3.0))) + 2
        for i in range(-g, g + 1):
            for j in range(-g, g + 1):
                for k in range(-g, g + 1):
                    allg.append(np.array([i, j, k], float))
        pts = np.array(allg)
    dist = np.linalg.norm(pts, axis=1)
    return pts[np.argsort(dist)[:M]]


def geometric_graph(M, nn_factor=1.6, seed=0):
    """球内晶格近邻图：每个核子只连近邻(无壳层信息)，作为负对照。
    截断 = nn_factor × 最近邻间距，固定局部尺度、不强制整体连通。"""
    pts = geometric_positions(M, seed=seed)
    V = M
    dist = np.zeros((V, V))
    for i in range(V):
        for j in range(V):
            dist[i, j] = np.linalg.norm(pts[i] - pts[j])
    d_nn1 = np.min(dist[dist > 0])
    cut = nn_factor * d_nn1
    A = np.zeros((V, V))
    for i in range(V):
        for j in range(V):
            if i != j and dist[i, j] <= cut:
                A[i, j] = 1.0
    return A


# ---------------------------------------------------------------------------
# 图不变量
# ---------------------------------------------------------------------------
def connected_components(A):
    V = A.shape[0]
    seen = [-1] * V
    c = 0
    for s in range(V):
        if seen[s] != -1:
            continue
        stack = [s]
        seen[s] = c
        while stack:
            u = stack.pop()
            for v in range(V):
                if A[u, v] > 0 and seen[v] == -1:
                    seen[v] = c
                    stack.append(v)
        c += 1
    return seen


def graph_invariants(A):
    V = A.shape[0]
    if V <= 1:
        return {"lambda2": 0.0, "n_loops": 0, "E": 0, "V": V, "components": V}
    D = np.diag(A.sum(1))
    L = D - A
    w = np.sort(np.linalg.eigvalsh(L))
    lam2 = float(w[1]) if V > 1 else 0.0
    E = int((A > 0).sum()) // 2
    labels = connected_components(A)
    C = len(set(labels))
    loops = E - V + C
    return {"lambda2": lam2, "n_loops": loops, "E": E, "V": V, "components": C}


def bonds_from_adj(A):
    n = A.shape[0]
    return [(i, j) for i in range(n) for j in range(i + 1, n) if A[i, j] > 0]


def sre_smooth_A(A):
    """把(核子)关系图喂入 SRE 平滑邻接算子 A_s —— 不需要坐标。"""
    n = A.shape[0]
    return build_sre_smooth_adjacency(np.zeros((n, 3)), bonds=bonds_from_adj(A))


def lap_lambda2(A):
    """加权图拉普拉斯的代数连通度 λ2。"""
    V = A.shape[0]
    if V <= 1:
        return 0.0
    L = np.diag(A.sum(1)) - A
    return float(np.sort(np.linalg.eigvalsh(L))[1])


def resistance_distance(A):
    """电阻距离 R_ij = L+_ii + L+_jj - 2 L+_ij（合法欧氏度量，MDS 不会塌缩）。"""
    n = A.shape[0]
    L = np.diag(A.sum(1)) - A
    Lp = np.linalg.pinv(L)
    d = np.diag(Lp)
    R = d[:, None] + d[None, :] - 2 * Lp
    np.fill_diagonal(R, 0.0)
    return np.sqrt(np.clip(R, 0.0, None))


def graph_geodesic(A, INF=1e9):
    V = A.shape[0]
    D = np.where(A > 0, 1.0, INF)
    np.fill_diagonal(D, 0.0)
    for k in range(V):
        for i in range(V):
            for j in range(V):
                if D[i, k] + D[k, j] < D[i, j]:
                    D[i, j] = D[i, k] + D[k, j]
    return np.where(D >= INF, 0.0, D)


# ---------------------------------------------------------------------------
# 3. 全核关系图(MDS 反演用)
# ---------------------------------------------------------------------------
def nucleus_shell_adjacency(Z, N):
    """全核 = 质子壳层图 + 中子壳层图 + p-n 跨壳耦合。"""
    Ap = shell_adjacency(Z)
    An = shell_adjacency(N)
    Vp = Ap.shape[0]
    Vn = An.shape[0]
    V = Vp + Vn
    A = np.zeros((V, V))
    A[:Vp, :Vp] = Ap
    A[Vp:, Vp:] = An
    # p-n 跨壳耦合：第 k 个质子壳与第 k 个中子壳弱连
    op = fill_scheme(Z)
    on = fill_scheme(N)
    ps = []
    s = 0
    for (si, t) in op:
        ps.append((s, t))
        s += t
    ns = []
    s = 0
    for (si, t) in on:
        ns.append((s, t))
        s += t
    for (sp, tp), (sn, tn) in zip(ps, ns):
        for a in range(sp, sp + tp):
            for b in range(sn, sn + tn):
                A[a, Vp + b] = A[Vp + b, a] = 0.15
    return A


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def scan():
    out = {"magic_numbers": MAGIC, "shell_graph_scan": [], "geometric_graph_scan": []}
    for M in range(2, 131):
        As = shell_adjacency(M)
        Ag = geometric_graph(M)
        row_s = {"M": M, **graph_invariants(As)}
        row_s["lambda2_q_sre_weighted"] = lap_lambda2(sre_smooth_A(As))
        row_g = {"M": M, **graph_invariants(Ag)}
        row_g["lambda2_q_sre_weighted"] = lap_lambda2(sre_smooth_A(Ag))
        out["shell_graph_scan"].append(row_s)
        out["geometric_graph_scan"].append(row_g)
    return out


def mds_nuclei():
    res = {}
    from _p3_p1a_final_scaffolds import mds_coords_from_dmat
    for name, (Z, N) in [("16O", (8, 8)), ("40Ca", (20, 20)), ("56Fe", (26, 30))]:
        A = nucleus_shell_adjacency(Z, N)
        As = sre_smooth_A(A)
        Dgeo = graph_geodesic(A)
        Dres = resistance_distance(As)     # 电阻距离：SRE 平滑邻接派生的欧氏度量
        Xg = mds_coords_from_dmat(Dgeo, ndim=3)
        Xr = mds_coords_from_dmat(Dres, ndim=3)
        res[name] = {
            "Z": Z, "N": N, "V": A.shape[0],
            "lambda2_shellgraph": graph_invariants(A)["lambda2"],
            "lambda2_q_sre": lap_lambda2(As),
            "mds_coords": Xr.tolist(),          # 主: 电阻距离(不塌缩)
            "mds_coords_geodesic": Xg.tolist(),
        }
    return res


if __name__ == "__main__":
    print("== SRE 核子图验证 ==")
    s = scan()
    # 打印魔数附近的 λ2 跳变
    sh = {r["M"]: r for r in s["shell_graph_scan"]}
    print("\n[壳层关系图] 魔数附近的 λ2 跳变(相位变证据)：")
    print(f"  {'M':>4s}  {'λ2':>8s}  {'n_loops':>8s}  {'magic?':>7s}")
    for M in range(2, 131):
        if M in MAGIC or M - 1 in MAGIC or M + 1 in MAGIC:
            r = sh[M]
            print(f"  {M:>4d}  {r['lambda2']:>8.3f}  {r['n_loops']:>8d}  "
                  f"{'MAGIC' if M in MAGIC else '':>7s}")

    # 魔数后第一点的局部 λ2 跌落
    print("\n魔数处 λ2 峰值 → 魔数+1 跌落 (刚性相位变)：")
    for m in MAGIC:
        if m + 1 <= 130:
            l_m = sh[m]["lambda2"]
            l_m1 = sh[m + 1]["lambda2"]
            print(f"  A={m:>3d} λ2={l_m:7.3f}  → A={m+1:>3d} λ2={l_m1:7.3f}  "
                  f"Δλ2={l_m1-l_m:+.3f}  (相对 {l_m1/l_m-1:+.1%})")

    # SRE 加权谱不变量 λ2_q（真实 SRE 算子，而非裸二进制图）
    print("\n[壳层关系图·SRE加权 λ2_q] 魔数处峰值 → 魔数+1 跌落：")
    for m in MAGIC:
        if m + 1 <= 130:
            q_m = sh[m]["lambda2_q_sre_weighted"]
            q_m1 = sh[m + 1]["lambda2_q_sre_weighted"]
            print(f"  A={m:>3d} λ2_q={q_m:8.4f} → A={m+1:>3d} λ2_q={q_m1:8.4f}  "
                  f"Δ={q_m1-q_m:+.4f}  (相对 {q_m1/q_m-1:+.1%})")

    # 负对照：几何邻近图(不含壳层信息)在魔数附近 λ2 应无跳变
    ge = {r["M"]: r for r in s["geometric_graph_scan"]}
    print("\n[几何邻近图·负对照] 魔数附近 λ2 (应平滑、无相位变)：")
    print(f"  {'M':>4s}  {'λ2':>8s}  {'magic?':>7s}")
    for M in range(2, 131):
        if M in MAGIC or M - 1 in MAGIC or M + 1 in MAGIC:
            r = ge[M]
            print(f"  {M:>4d}  {r['lambda2']:>8.3f}  {'MAGIC' if M in MAGIC else '':>7s}")

    mn = mds_nuclei()
    print("\n[MDS 反演] 由纯关系图涌现的核坐标(前 4 节点)：")
    for name, d in mn.items():
        X = np.array(d["mds_coords"])
        print(f"  {name}: V={d['V']} λ2(shellgraph)={d['lambda2_shellgraph']:.3f}")
        for i in range(min(4, len(X))):
            print(f"      node{i}: ({X[i,0]:+.2f},{X[i,1]:+.2f},{X[i,2]:+.2f})")

    out = {"scan": s, "mds_nuclei": mn}
    with open(r"C:\mywork\vasp\sre_nucleon_graph_results.json", "w") as f:
        json.dump(out, f, indent=2)
    print("\n[OK] sre_nucleon_graph_results.json")
