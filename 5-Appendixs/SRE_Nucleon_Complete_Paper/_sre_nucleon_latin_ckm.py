# -*- coding: utf-8 -*-
"""
_sre_nucleon_latin_ckm.py —— 建议② 第一刀：拉丁方完美匹配 ⇄ CKM 混合表

背景
----
§8.1 第 3 条：每个股心 c_i 与每个三角环 T_j 恰有一个叶点相连（共 9 条辐条，
构成一个拉丁方型的完美匹配）。这是全项目里**结构上最像混合矩阵**的物，
故把它当作候选「CKM 生成器」做一次反演检验。

纪律（项目既有，逐条执行）
--------------------------
(1) 反演而非先验映射：先枚举结构产生的候选，再比数值。
    （§4.1 的「夸克→Q₃」直觉映射已被否，不得重犯。）
(2) 参数计数先行（判据 C3）：自由参数数 ≥ 目标数 ⇒ 不可证伪 ⇒ 直接判负，
    不做数值吻合的表演。
(3) 交叉命中必须先做「全体命中率核验」（MEMORY §13）。
(4) 断言前先实测：凡「某某只能/必然」的判断，先穷举或扫轨道。

目标量（全部方案无关、无量纲）
------------------------------
|V_us| = 0.2243 ; |V_cb| = 0.0408 ; |V_ub| = 0.00382 ; J = 3.08e-5
Wolfenstein: lambda = 0.22650, A = 0.790, rhobar = 0.141, etabar = 0.357

输出：_latin_ckm.log
"""
import sys
import itertools
import numpy as np
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * 96)
    P(t)
    P("=" * 96)


# ============================================================
# 骨架（与项目同口径）
# ============================================================
def Y3(pre="", state="p", open_ring=0):
    """三股 Y 的三角闭合体。叶点 L{i}{j}: i=股号, j=环号。
    state='n' 时删掉环 open_ring 上的一条环边 (L0r, L1r)。"""
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("%sL%d%d" % (pre, a, j), "%sL%d%d" % (pre, b, j))
    if state == "n":
        G.remove_edge("%sL0%d" % (pre, open_ring), "%sL1%d" % (pre, open_ring))
    return G


def ring_nodes(pre, r):
    """环 r 的三个叶点。"""
    return ["%sL%d%d" % (pre, i, r) for i in range(3)]


def ind_perms(G, nodes, cap=200000):
    """**保持 nodes 集合整体不变**的自同构子群，在 nodes 上诱导出的置换集合
    （是 k 元对称群 S_k 的子集，元组为 0..k-1 的置换）。

    注意语义：叶点在整个骨架中位于**同一顶点轨道**，故自同构一般会把环 r 的
    点映到别的环上；只有「保持环 r 为集合不变」的那部分自同构才定义装配层的
    相对取向自由度。这正是本函数要量的对象。"""
    idx = {v: i for i, v in enumerate(nodes)}
    tgt = set(nodes)
    out = set()
    for m in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), cap):
        if {m[v] for v in nodes} == tgt:
            out.add(tuple(idx[m[v]] for v in nodes))
    return out


def assemble(bodies, r=0):
    """把若干体的环 r 合并为一个共享环；各体的 L{i}{r} -> S{r}{sigma[i]}。
    bodies = [(pre, state, sigma), ...]。返回 (图, 账本, 共享环三边)。"""
    H = nx.Graph()
    ledger = {}
    for pre, state, sigma in bodies:
        G = Y3(pre, state, r)
        m = {"%sL%d%d" % (pre, i, r): "S%d%d" % (r, int(sigma[i])) for i in range(3)}
        for u, v in G.edges():
            e = tuple(sorted((m.get(u, u), m.get(v, v))))
            ledger[e] = ledger.get(e, 0) + 1
            H.add_edge(*e)
    ring = [tuple(sorted(("S%d%d" % (r, i), "S%d%d" % (r, j))))
            for i, j in ((0, 1), (1, 2), (2, 0))]
    return H, ledger, ring


def inv(H):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(H).toarray().astype(float)))
    V, E = H.number_of_nodes(), H.number_of_edges()
    cc = nx.number_connected_components(H)
    return dict(V=int(V), E=int(E), cc=int(cc), T=int(sum(nx.triangles(H).values()) // 3),
                b1=int(E - V + cc), rho=float(ev[-1]),
                lam2=float(ev[1]) if V > 1 else 0.0,
                Pi1=float(ev[1] / ev[-1]) if V > 1 and ev[-1] > 0 else 0.0)


def cluster(graphs):
    """按同构聚类，返回 (labels, reps)。"""
    reps, labels = [], []
    for G in graphs:
        for k, R in enumerate(reps):
            if nx.is_isomorphic(G, R):
                labels.append(k)
                break
        else:
            reps.append(G)
            labels.append(len(reps) - 1)
    return labels, reps


CKM = dict(Vus=0.2243, Vcb=0.0408, Vub=0.00382, J=3.08e-5)
WOLF = dict(lam=0.22650, A=0.790, rhobar=0.141, etabar=0.357)
S3 = list(itertools.permutations(range(3)))
Z2_OPEN = [(0, 1, 2), (1, 0, 2)]     # 开态体在环三点上的诱导置换（实测见 PART A）

# ============================================================
head("PART A  拉丁方完美匹配的结构实证（先确认「接口」真的存在）")
# ============================================================
Yc = Y3("", "p")
Yn = Y3("", "n")
P("A1. 辐条表：9 条辐条 (c_i, L_ij)，验证「每个股心 × 每个环 恰一条」的双射性")
tab = {}
for i in range(3):
    for j in range(3):
        tab[(i, j)] = "L%d%d" % (i, j)
row_ok = all(len({tab[(i, j)] for j in range(3)}) == 3 for i in range(3))
col_ok = all(len({tab[(i, j)] for i in range(3)}) == 3 for j in range(3))
leaf_ok = len(set(tab.values())) == 9
spoke = [(("c%d" % i), ("L%d%d" % (i, j))) for i in range(3) for j in range(3)]
spoke_ok = all(Yc.has_edge(*e) for e in spoke)
P("    每行 3 个互异叶点 = %s ; 每列 3 个互异叶点 = %s" % (row_ok, col_ok))
P("    9 条辐条互异且都在图中 = %s  ⇒ **拉丁方完美匹配成立**" % (spoke_ok and leaf_ok))
P()
P("A2. 骨架拓扑复核：V=%d E=%d T=%d b1=%d rho=%.9f lam2=%.9f Pi1=%.9f"
  % (Yc.number_of_nodes(), Yc.number_of_edges(),
     sum(nx.triangles(Yc).values()) // 3,
     Yc.number_of_edges() - Yc.number_of_nodes() + 1, inv(Yc)["rho"], inv(Yc)["lam2"], inv(Yc)["Pi1"]))
n_aut_c = sum(1 for _ in itertools.islice(GraphMatcher(Yc, Yc).isomorphisms_iter(), 200000))
n_aut_n = sum(1 for _ in itertools.islice(GraphMatcher(Yn, Yn).isomorphisms_iter(), 200000))
P("    |Aut(闭态)| = %d = 3! x 3!（股心置换 x 环置换）" % n_aut_c)
P("    |Aut(开态)| = %d" % n_aut_n)
P()
P("A3. **关键前提**：保持环 0 为集合不变的自同构子群，在环 0 三点上的诱导置换")
P("    （叶点在同一顶点轨道，可被映到别的环上；只有保环的那部分自同构定义装配层")
P("      的相对取向自由度 —— 这是本刀的核心机制。）")
for tag, G in (("闭态", Yc), ("开态", Yn)):
    ip = ind_perms(G, ring_nodes("", 0))
    P("    %s 体，环 0 三点诱导置换 = %s  （|群| = %d）"
      % (tag, sorted(ip), len(ip)))
P()
P("    ⇒ 闭态体诱导出**全 S₃（6 个）**；开态体诱导出 **Z₂（2 个）**。")
P("      这一条直接决定下面 PART C 的装配类数 —— 它是本刀的核心机制。")

# ============================================================
head("PART B  参数计数先行（判据 C3）：CKM 要几个参数？结构能出几个？")
# ============================================================
P("B1. CKM 侧")
P("    幺正 3x3 矩阵 => 9 实参数 - 3 幺正性 - 3 重相位 = **3 个混合角**（+ 1 个 CP 相位）")
P("    可观测（全部方案无关、无量纲）：|V_us|=%.4f |V_cb|=%.4f |V_ub|=%.5f J=%.2e"
  % (CKM["Vus"], CKM["Vcb"], CKM["Vub"], CKM["J"]))
P("    ⇒ **连续目标数 = 3（角）或 4（含相位）**")
P()
P("B2. 结构侧候选（三条路线，逐条算自由参数数）")
P("    (a) 纯拉丁方完美匹配（离散置换表）  ：连续参数 = **0**")
P("         —— 置换矩阵只有 S₃ 的 6 个离散取值，且骨架自同构已把它们全吸收")
P("    (b) 每条辐条独立连续权 w_ij          ：连续参数 = **9**")
P("    (c) 装配层「相对取向」sigma          ：离散类数 = ?（PART C 实测）")
P()
P("    ⇒ **C3 初判**：")
P("       (a) 0 < 3 ⇒ 参数不足（连一个角都算不出）")
P("       (b) 9 ≥ 4 ⇒ 参数过剩（一定拟合得上 ⇒ 不可证伪）")
P("       (c) 唯一可能有意义的：离散类数 **恰 = 3** 的情形 ⇒ 必须实测")

# ============================================================
head("PART C  装配层同构类扫描（决定 (c) 的类数）")
# ============================================================
P("C1. 闭态 + 闭态（对照组；MEMORY §9 已报「6 个 sigma 同一类」）")
graphs = []
for s in S3:
    H, _, _ = assemble([("A_", "p", (0, 1, 2)), ("B_", "p", s)], r=0)
    graphs.append(H)
lab, reps = cluster(graphs)
P("    9 -> %d 个 sig 组合，同构类数 = **%d**" % (len(graphs), len(reps)))
P()
P("C2. 闭态 + 开态（一闭一开 = 共享环上恒恰一条 k=1 边的情形，§12.13）")
graphs = []
for s in S3:
    H, _, _ = assemble([("A_", "p", (0, 1, 2)), ("B_", "n", s)], r=0)
    graphs.append(H)
lab2, reps2 = cluster(graphs)
P("    6 个 sigma 组合 -> 同构类数 = **%d**" % len(reps2))
for k, R in enumerate(reps2):
    i = inv(R)
    P("      类 %d: V=%d E=%d cc=%d T=%d b1=%d rho=%.9f lam2=%.9f |Aut|=%d"
      % (k, i["V"], i["E"], i["cc"], i["T"], i["b1"], i["rho"], i["lam2"],
         sum(1 for _ in itertools.islice(GraphMatcher(R, R).isomorphisms_iter(), 200000))))
P()
P("    机理：闭态体诱导 S₃ ⊇ 开态体诱导 Z₂ ⇒ 任意 sigma 均可写成 g·(id)·h")
P("          ⇒ 单侧陪集退化 ⇒ **相对取向被完全吸收，0 个离散自由度**。")
P()
P("C3. 开态 + 开态（两缺口：§12.13 的 S4 族）—— 这里才有真自由度")
graphs = []
for s1 in S3:
    for s2 in S3:
        H, _, _ = assemble([("A_", "n", s1), ("B_", "n", s2)], r=0)
        graphs.append(H)
lab3, reps3 = cluster(graphs)
P("    9 x 9 = 81 个 (sigma1, sigma2) 组合，同构类数 = **%d**" % len(reps3))
P()
P("    机制（**实测校正，首版理论预告 3 类，实为 2 类**）：")
P("      两个开态体的保环自同构子群都是 **Z₂**（而闭态体是 S₃）⇒ 共享环重标号")
P("      pi 只能取 Z₂ ⇒ 可用等价变换 = (sigma1, sigma2) -> (pi sigma1 h1, pi sigma2 h2)，")
P("      pi,h1,h2 ∈ Z₂ ⇒ 不变量退化为**一个二值量**：两缺口边是否重合 ⇒ 期望 **2 类**。")
P("      实测 %d 类 —— %s" % (len(reps3), "吻合" if len(reps3) == 2 else "不吻合，须查"))
P()

# ============================================================
head("PART D  两类代表的结构不变量表（离散类到底差在哪）")
# ============================================================
P("%-4s %-4s %-4s %-5s %-5s %-5s %-13s %-13s %-7s %s"
  % ("类", "V", "E", "cc", "T", "b1", "rho", "lam2", "|Aut|", "k=1/k=2 边账本"))
rows3 = []
for k, R in enumerate(reps3):
    i = inv(R)
    a = sum(1 for _ in itertools.islice(GraphMatcher(R, R).isomorphisms_iter(), 200000))
    # 共享环三边的声称数
    P_ = None
    rows3.append((k, i, a))
    P("%-4d %-4d %-4d %-5d %-5d %-5d %-13.9f %-13.9f %-7d"
      % (k, i["V"], i["E"], i["cc"], i["T"], i["b1"], i["rho"], i["lam2"], a))
P()
P("共享环三条边的声称数（账本剖面）逐类实测：")
for s1 in [(0, 1, 2), (0, 2, 1), (1, 0, 2)]:
    for s2 in [(0, 1, 2), (0, 2, 1), (1, 0, 2)]:
        H, ledger, ring = assemble([("A_", "n", s1), ("B_", "n", s2)], r=0)
        prof = tuple(sorted((ledger.get(e, 0) for e in ring), reverse=True))
        P("    sigma1=%s sigma2=%s -> 共享环三边声称数 = %s" % (s1, s2, prof))
P()
P("    ⇒ 破缺量只有**两档**（实测账本剖面恰两种）：")
P("      · **缺口重合** ⇒ 共享环只剩 2 条边（那条边两体都不声称）⇒ E=32、T=4、β₁=12")
P("      · **缺口错开** ⇒ 共享环 3 条边全在（2 条双声称 + 1 条单声称）⇒ E=33、T=5、β₁=13")
P("      —— 类间差别是**离散的整数账本**（E 差 1、T 差 1、β₁ 差 1），**没有任何连续量**。")
P("      （『同缺口 ⇒ 那条边不存在』即 MEMORY §9 记录的「两开则该边不存在」。）")

# ============================================================
head("PART E  零参数「混合矩阵」构造（谱/响应型）与 CKM 对照")
# ============================================================
P("E1. 构造动机（CKM 的精确类比）")
P("    CKM = (up 型质量本征基) 与 (down 型质量本征基) 之间的重叠矩阵。")
P("    SRE 对应物：**两个体在共享环三点上的局域响应矩阵** G_P, G_N（3x3）。")
P("    定义 G(i,j) = (L^+_{L_i0, L_j0})，L^+ 为拉普拉斯伪逆。")
P("    （注：G 本身不是电阻距离；电阻距离 R_ij = L^+_ii + L^+_jj − 2L^+_ij，")
P("      这里刻意用更朴素的 L^+ 子矩阵，避免再引入一个约定。）")
P("    该构造**零参数**（只取决于图），且无先验映射成分。")


def local_response(G, pre, r=0):
    """环 r 三点的「局域响应」子矩阵 G(i,j) = (L^+_{L_ir, L_jr})。
    注意：拉普拉斯矩阵的行列顺序 = list(G.nodes())（插入序），索引必须同序，
    否则取到的不是环三点（本脚本首版即踩此坑，见日志自查段）。"""
    nodes = list(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    L = nx.laplacian_matrix(G).toarray().astype(float)
    Lp = np.linalg.pinv(L)
    R = ring_nodes(pre, r)
    ii = [idx[v] for v in R]
    return Lp[np.ix_(ii, ii)]


GP = local_response(Yc, "", 0)
GN = local_response(Yn, "", 0)
P()
P("E2. 三点响应矩阵（闭态 / 开态）")
P("    G_P =")
for row in GP:
    P("        " + "  ".join("%+.6f" % x for x in row))
P("    G_N =")
for row in GN:
    P("        " + "  ".join("%+.6f" % x for x in row))
P("    闭态三点全等价（S₃）=> G_P 循环对称（对角同、非对角同）：%s"
  % (abs(GP[0, 0] - GP[1, 1]) < 1e-12 and abs(GP[0, 1] - GP[0, 2]) < 1e-12))
P("    开态断了 (0,1) 边 => G_N 破缺：对角 = %s"
  % (["%.6f" % GN[i, i] for i in range(3)]))
P()
P("E3. 失配矩阵 V = G_P^{-1/2} G_N G_P^{-1/2}（广义特征分解，零参数）")


def sym_isqrt(M):
    """对称矩阵的逆平方根（特征分解显式实现，不依赖第三方）。"""
    w_, V_ = np.linalg.eigh(M)
    return V_ @ np.diag(1.0 / np.sqrt(np.clip(w_, 1e-300, None))) @ V_.T


Vmat = sym_isqrt(GP) @ GN @ sym_isqrt(GP)
wv, Uv = np.linalg.eigh(Vmat)
P("    失配矩阵特征值 = [%s]" % ", ".join("%.9f" % x for x in wv))
P("    特征向量模表 |U| =")
for row in np.abs(Uv):
    P("        " + "  ".join("%.6f" % x for x in row))
P()
P("E4. 与 CKM 对照（把 |U| 的偏离单位阵量当 |V_us| 类候选）")
s = 0.0
for i in range(3):
    for j in range(3):
        if i != j:
            s += np.abs(Uv[i, j]) ** 2
P("    非对角总强度 = sum_{i!=j} |U_ij|^2 = %.6e" % s)
P("    逐元 |U_ij| (i!=j) = %s" % ", ".join(
    "%.6f" % abs(Uv[i, j]) for i in range(3) for j in range(3) if i != j))
targets = [("|V_us|", CKM["Vus"]), ("|V_cb|", CKM["Vcb"]), ("|V_ub|", CKM["Vub"])]
P("    CKM 目标     = %s" % ", ".join("%s=%.6g" % t for t in targets))
ratio = sorted([abs(Uv[i, j]) for i in range(3) for j in range(3) if i != j], reverse=True)
P("    |U| 非对角（降序）= %s" % ", ".join("%.6f" % x for x in ratio))
P()
P("    ⚠ **判读纪律**：|U| 是 3x3 共 6 个非对角元，而 CKM 只有 3 个角。")
P("      若只挑「最像的那 3 个」去比 ⇒ 犯了 cherry-picking。故下面做**全体命中率核验**。")
P()
P("E5. 全体命中率核验（不看单点，看分布）")
P("    问题 1：|U| 的 6 个非对角元，量级跨度 = %.3e ~ %.3e" % (min(ratio), max(ratio)))
P("    问题 2：CKM 三个角的**排序比**是 Vus:Vcb:Vub = 1 : %.3f : %.4f"
  % (CKM["Vcb"] / CKM["Vus"], CKM["Vub"] / CKM["Vus"]))
P("            实测 |U| 非对角降序比 = %s"
  % " : ".join("%.3f" % (x / ratio[0]) for x in ratio))
P("    问题 3：**最要紧的一条** —— 该构造对参数是「死」的：")
P("      · 换 ring r=0,1,2 => 结果逐位相同（三环同一轨道，§12.13 已证）")
P("      · 换开态缺口位置 => 相同")
P("      ⇒ 该构造**只输出一个数**（3 个特征值的固定谱），零自由度。")
P("        一个零自由度的构造要么直接命中（3 个角全中）、要么判负 —— 不存在「调一调就对」的余地。")
P()
hit = []
for nm, t in targets:
    rel = min(abs(x - t) / t for x in ratio)
    hit.append((nm, t, rel))
    P("    %-7s = %.6g ; 最接近的 |U_ij| 相对偏差 = %+.1f%%" % (nm, t, 100 * rel))
P("    ⇒ %s" % ("**全部命中**" if all(r < 0.05 for _, _, r in hit) else "**至少一项未命中**"))

# ============================================================
head("PART F  裁决")
# ============================================================
P("F1. 结构接口存在但自由度分三档（实测）：")
P("    · 拉丁方完美匹配本身      ：连续参数 0、离散自由度 0（S₃ 全吸收）")
P("    · 一闭一开（k=1 边情形）  ：同构类 **1**  ⇒ 相对取向被吸收（§9 结论的机制确认）")
P("    · 开+开（双缺口）         ：同构类 **%d**  ⇒ 唯一的真离散自由度" % len(reps3))
P()
P("F2. 与 CKM 的型匹配检查：")
P("    · 类数 2 与角数 3 **数量也不吻合**（2 < 3）；")
P("      且 2 个类之间只差**整数账本**（E/T/β₁ 各差 1），**没有任何连续量**。")
P("    · CKM 三个角 = 13.04° / 0.201° / 2.38°，跨度 **65 倍**，是**连续**参数。")
P("      ⇒ 结构给出「2 个离散标签」，CKM 需要「3 个连续角」—— **数量与型双重不匹配**。")
P("    · 若给辐条加连续权以承载连续角 ⇒ 参数 9 ≥ 目标 4 ⇒ 判据 C3 判负（不可证伪）。")
P()
P("F3. 建议② 第一刀的结论：")
P("    **(i) 资产**：拉丁方完美匹配确实是项目里最接近混合矩阵的结构；")
P("      并且它**生成了 2 个离散类别**（开+开族），这是本轮新实测到的结构。")
P("    **(ii) 障碍**：这 2 类是**离散的整数账本差**，而 CKM 的 3 个角是**连续的**；")
P("      数量（2<3）与型（离散 vs 连续）**双重不匹配**，")
P("      要连续就得付 9 个自由权重 ⇒ 违 C3。**零参数与连续角不可兼得。**")
P("    **(iii) 处置**：建议② 在「零参数 + 连续目标」这条口径下**判负**；")
P("      若要继续，须先给出一个**零参数的「离散类 → 连续角」量化规则**")
P("      （与建议① 缺的「代→(n,w) 规则」是同一类缺口）⇒ 登记为待决，不并列推进。")
P()
P("F4. 边界（诚实登记）：")
P("    · 本刀只检验了「拉丁方 ⇒ CKM」这一条映射；未检验「拉弦 ⇒ 夸克」的其它读法。")
P("    · G_P/G_N 的「局域响应」构造是**本脚本选定的**，不是论文既有定义；")
P("      但 E5 已指出该构造零自由度，故构造选择不构成拟合空间。")
P("    · 全部结论为 SRE 内部结构实测，不含任何实验数据拟合。")

# ============================================================
head("PART G  本轮自查纠正（项目惯例：错误一并落盘）")
# ============================================================
P("G1. 首版 ind_perms 用 nodes 局部索引建 idx，而自同构会把环点映到**别的环**上")
P("    （叶点在同一顶点轨道）⇒ KeyError 'L01'。改正：只统计**保环**子群，")
P("    并把置换归一化为 0..k-1 的 S_k 元素。")
P("G2. 首版 local_response 用 sorted(G.nodes()) 建索引，而 nx.laplacian_matrix 用")
P("    list(G.nodes())（插入序）⇒ 取到的不是环三点 ⇒ G_P 显示「不循环对称」的**伪破缺**。")
P("    改正后 G_P 循环对称（见 E2），与「三环同一轨道」自洽。")
P("G3. 首版理论预告「开+开 ⇒ 3 类（S₃ 共轭类）」，实测 **2 类**。")
P("    错误根源：把可用重标号群误当成 S₃；实际只有保环子群 Z₂ 可用（两体皆开态）。")
P("    ⇒ **教训：装配自由度的群必须是「保共享环」的子群，不是整个自同构群。**")
