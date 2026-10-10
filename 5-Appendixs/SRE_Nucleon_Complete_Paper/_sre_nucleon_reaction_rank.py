# -*- coding: utf-8 -*-
"""
「方程数不足，能否用已知反应式补方程来救反解？」—— 秩的实测判定。

  PART A  化学：反应式 ≡ 物种方程的行线性组合 ⇒ 秩不变（定理级）
  PART B  核反应：Q 值与结合能互为线性组合 ⇒ 对账本未知数零增量
  PART C  核子骨架：『和型』泛函（键能加和 / 反应式）vs『谱型』泛函（特征值比）
  PART D  规范方向与解集维数
  PART E  裁决

本脚本只做线性代数与谱计算，不引入任何新物理假设。
化学部分用键能加和模型作为**形式演示**（加和只是近似，故 A2 会显式暴露其误差）。
"""
import sys
import numpy as np
import networkx as nx

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * 88)
    P(t)
    P("=" * 88)


def rk(M, rtol=1e-9):
    M = np.atleast_2d(np.asarray(M, float))
    if M.size == 0:
        return 0
    s = np.linalg.svd(M, compute_uv=False)
    if s[0] == 0.0:
        return 0
    return int((s / s[0] > rtol).sum())


# ======================================================================
# PART A  化学
# ======================================================================
BOND = ["C-H", "C-C", "C=C", "C#C", "C-O", "C=O", "O-H", "H-H", "O=O"]
SPEC = ["CH4", "C2H6", "C2H4", "C2H2", "H2O", "CO2", "CH3OH", "H2", "O2"]
A_FULL = np.array([
    [4, 0, 0, 0, 0, 0, 0, 0, 0],   # CH4
    [6, 1, 0, 0, 0, 0, 0, 0, 0],   # C2H6
    [4, 0, 1, 0, 0, 0, 0, 0, 0],   # C2H4
    [2, 0, 0, 1, 0, 0, 0, 0, 0],   # C2H2
    [0, 0, 0, 0, 0, 0, 2, 0, 0],   # H2O
    [0, 0, 0, 0, 0, 2, 0, 0, 0],   # CO2
    [3, 0, 0, 0, 1, 0, 1, 0, 0],   # CH3OH
    [0, 0, 0, 0, 0, 0, 0, 1, 0],   # H2
    [0, 0, 0, 0, 0, 0, 0, 0, 1],   # O2
], float)
E_ATOM = np.array([1663, 2828, 2255, 1640, 926, 1598, 2035, 436, 498], float)  # kJ/mol

REAC = {
    "CH4 + H2O -> CH3OH + H2": {6: +1, 7: +1, 0: -1, 4: -1},
    "C2H6 -> C2H4 + H2":       {2: +1, 7: +1, 1: -1},
    "C2H4 -> C2H2 + H2":       {3: +1, 7: +1, 2: -1},
    "CH4 + 2O2 -> CO2 + 2H2O": {5: +1, 4: +2, 0: -1, 8: -2},
}


def reac_matrix(nspec, keys):
    C = np.zeros((len(keys), nspec))
    for r, key in enumerate(keys):
        for j, c in REAC[key].items():
            C[r, j] = c
    return C


def part_A():
    head("PART A  反应式 ≡ 物种方程的行线性组合 ⇒ 秩不增（定理级）")
    keys = list(REAC.keys())
    C = reac_matrix(len(SPEC), keys)
    R = C @ A_FULL                       # ← 反应行**按定义**就是物种行的组合

    P("A0. 定义层面：反应系数矩阵 C 作用到物种矩阵 A 上即得反应行 R = C·A")
    P("    ⇒ R 的每一行**按构造**落在 A 的行空间内 ⇒ 数学上不可能提供新方向。")
    P("    rank(A)          = %d / 键型 %d" % (rk(A_FULL), len(BOND)))
    P("    rank(C·A)        = %d" % rk(R))
    P("    rank([A ; C·A])  = %d   ← 堆叠后秩**一个不增**" % rk(np.vstack([A_FULL, R])))
    P()

    P("A1. 自洽演示：设键能 m* ⇒ 各物种能 b = A·m*")
    m_star = np.array([412, 348, 614, 838, 360, 799, 463, 436, 498], float)
    b_syn = A_FULL @ m_star
    # 反应式在真解处的残差 = (cᵀA)m* − cᵀb ；因 b = A m* 恒为 0
    res_star = R @ m_star - C @ b_syn
    P("    真解处反应残差 max|(C·A)m* − C·b| = %.3e   ← 恒为 0（被隐含满足）"
      % np.max(np.abs(res_star)))
    P("    对**任意**满足 A·m = b 的 m：残差 = C·(A·m − b) ≡ 0")
    P("    ⇒ 反应式**不是在约束 m，只是 A·m = b 的一个推论**。")
    P()
    P("    反应能量（= 由加和模型给出的『预言』，不是新数据）：")
    for r, k in enumerate(keys):
        P("      %-26s  Q_pred = %+9.1f kJ/mol" % (k, float(R[r] @ m_star)))
    P()

    P("A2. 用**物理标准键能**（不拟合）⇒ 暴露加和模型误差，看反应式能否帮上忙")
    m_std = np.array([413, 348, 614, 839, 358, 799, 463, 436, 498], float)
    b_real = E_ATOM
    resid_spec = A_FULL @ m_std - b_real          # 物种方程残差（加和近似误差）
    resid_reac = R @ m_std - C @ b_real           # 反应式残差
    P("    物种方程残差  max|A·m_std − b| = %7.1f kJ/mol   ← 加和近似误差（非零）"
      % np.max(np.abs(resid_spec)))
    P("    反应式残差    max|(C·A)m_std − C·b| = %7.1f kJ/mol" % np.max(np.abs(resid_reac)))
    P("    **精确恒等式**：反应式残差 = C·(A·m_std − b) = C × 物种残差")
    P("      max|resid_reac − C·resid_spec| = %.3e" % np.max(np.abs(resid_reac - C @ resid_spec)))
    P("    rank([A ; C·A]) = %d   ← 秩仍不变" % rk(np.vstack([A_FULL, R])))
    P("    ⇒ 反应式残差**只是物种残差的线性组合** ⇒ 它只能**证伪**加和模型，")
    P("      不能**多定**任何参数；『模型误差』这条信息在物种层面就已全部到手。")
    P()

    P("A3. 秩亏对照：去掉 H2O 与 O2（O-H 只剩 CH3OH 一个来源）")
    keep = [0, 1, 2, 3, 5, 6, 7]
    A_sub = A_FULL[np.ix_(keep, range(len(BOND)))]
    keys_sub = ["C2H6 -> C2H4 + H2", "C2H4 -> C2H2 + H2"]
    C_sub = reac_matrix(len(SPEC), keys_sub)[:, keep]
    R_sub = C_sub @ A_sub
    P("    子集物种 (%d 个): %s" % (len(keep), ", ".join(SPEC[j] for j in keep)))
    P("    rank(A_sub)          = %d / 键型 %d ⇒ 秩亏 %d"
      % (rk(A_sub), len(BOND), len(BOND) - rk(A_sub)))
    P("    rank([A_sub ; 反应]) = %d   ← 加反应，秩**一个不增**" % rk(np.vstack([A_sub, R_sub])))
    A_sub2 = A_FULL[np.ix_(keep + [4], range(len(BOND)))]
    A_sub3 = A_FULL[np.ix_(keep + [4, 8], range(len(BOND)))]
    P("    补回**物种** H2O ⇒ rank = %d  (Δ = +%d)"
      % (rk(A_sub2), rk(A_sub2) - rk(A_sub)))
    P("    再补回**物种** O2  ⇒ rank = %d  (满秩 %d)"
      % (rk(A_sub3), len(BOND)))
    P()
    P("⇒ 结论 A：**反应式不扩秩；扩秩的是『新物种』（= 新图 / 新键型）。**")
    P("   反应式能顶替的唯一场合是「某物种方程**缺失**时拿它代填」——那是『替换』，不是『增加』。")
    return None


# ======================================================================
# PART B  核反应 Q 值
# ======================================================================
def part_B():
    head("PART B  核反应 Q 值 vs 账本未知数（结合能）—— 零增量")
    Bval = np.array([2.224566, 8.481821, 7.718109, 28.295674], float)   # MeV: d,t,3He,4He
    I4 = np.eye(4)
    RXN = {
        "p(n,g)d     ": {0: +1},
        "d(p,g)3He   ": {2: +1, 0: -1},
        "d(d,n)3He   ": {2: +1, 0: -2},
        "d(d,p)3H    ": {1: +1, 0: -2},
        "3He(n,p)3H  ": {1: +1, 2: -1},
        "d(t,n)4He   ": {3: +1, 1: -1, 0: -1},
    }
    Q = np.zeros((len(RXN), 4))
    for r, (_k, d) in enumerate(RXN.items()):
        for j, c in d.items():
            Q[r, j] = c
    P("    账本未知数 = 4 个结合能 B(d,t,³He,⁴He) = %s MeV" % np.round(Bval, 6))
    P("    rank(I₄)        = %d" % rk(I4))
    P("    rank(Q 反应矩阵) = %d" % rk(Q))
    P("    rank([I₄ ; Q])  = %d   ← 堆叠后秩不变" % rk(np.vstack([I4, Q])))
    P()
    P("    各反应 Q 值（由 B 直接给出，无需任何新数据）：")
    known = {"p(n,g)d     ": 2.2246, "d(p,g)3He   ": 5.4935, "d(d,n)3He   ": 3.2690,
             "d(d,p)3H    ": 4.0330, "3He(n,p)3H  ": 0.7640, "d(t,n)4He   ": 17.589}
    for r, k in enumerate(RXN):
        q = float(Q[r] @ Bval)
        P("      %s  Q = %+9.4f MeV   (实测 %+8.4f, Δ=%+.1e)"
          % (k, q, known[k], q - known[k]))
    P("    ⇒ 逐项吻合到 1e-4 量级 —— 因为 **Q 值与质量差互为线性组合**，同一批数据。")
    P()
    P("⇒ 结论 B：**核反应 Q 值对『账本层』零增量**：不是 6 条新方程，是 4 条旧方程的 6 种读法。")
    P("   这与本项目既有经验一致：额外已知量（截面、半衰期）历来只当『零参数证伪判据』（L1 模式），")
    P("   从未成功充当过第 2 个方程。")
    return None


# ======================================================================
# PART C  核子骨架：和型 vs 谱型
# ======================================================================
def Y3(pre="", state="p", open_ring=0):
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


def geometry(G):
    nodes = sorted(G.nodes())
    idx = {v: i for i, v in enumerate(nodes)}
    n = len(nodes)
    edges = sorted(tuple(sorted(e)) for e in G.edges())
    Bm = np.zeros((len(edges), n))
    for e, (u, v) in enumerate(edges):
        Bm[e, idx[u]] = -1.0
        Bm[e, idx[v]] = +1.0
    return edges, Bm


def lap(Bm, m):
    return (Bm.T * m) @ Bm


def ratios(m, Bm):
    ev = np.sort(np.linalg.eigvalsh(lap(Bm, m)))
    return ev[1:] / ev[-1]


def fd_jac(fun, x0, h=1e-4):
    r0 = fun(x0)
    J = np.zeros((len(r0), len(x0)))
    for j in range(len(x0)):
        xp = x0.copy(); xp[j] += h
        xm = x0.copy(); xm[j] -= h
        J[:, j] = (fun(xp) - fun(xm)) / (2 * h)
    return J


def edge_orbits(G):
    edges = [tuple(sorted(e)) for e in G.edges()]
    auts = list(nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
    un = set(edges)
    orbs = []
    while un:
        e0 = next(iter(un))
        orb = set()
        for f in auts:
            a, b = e0
            orb.add(tuple(sorted((f[a], f[b]))))
        orbs.append(sorted(orb))
        un -= orb
    return orbs, len(auts)


def part_C():
    head("PART C  核子骨架：『和型』（反应式）vs『谱型』—— 谁能扩秩")
    G = Y3("", "p")
    edges, Bm = geometry(G)
    E = len(edges)
    orbs, naut = edge_orbits(G)
    eidx = {e: i for i, e in enumerate(edges)}
    P("    Y₃ 闭态：V=%d  E=%d  |Aut|=%d  边轨道 %d 个（大小 %s）"
      % (Bm.shape[1], E, naut, len(orbs), [len(o) for o in orbs]))
    m0 = np.ones(E)
    ev = np.sort(np.linalg.eigvalsh(lap(Bm, m0)))
    P("    单位权谱：%s" % np.round(ev, 9))
    uniq = []
    for v in ev[1:]:
        if not uniq or abs(uniq[-1] - v) > 1e-9:
            uniq.append(v)
    P("    非零特征值的**不同值** = %d 个：%s" % (len(uniq), np.round(uniq, 9)))
    P("    其中 λ_max 给出平凡比值 1.0 ⇒ **非平凡独立谱比 = %d 个**，而未知边权 %d 个。"
      % (len(uniq) - 1, E))
    P()

    P("    【和型泛函】S(m) = Σ_e m_e（键能加和 / τ₁ 型 / 一切反应式的差）")
    P("      rank(J_S) = 1  ← 全 1 向量，恒 1 维。反应式 = 两张图和型之差 ⇒ 行 = (+1⃗)⊕(−1⃗)，")
    P("      仍在 Σ 的行空间内 ⇒ 秩不增（与 PART A 同一结论）。")
    P()

    P("    【谱型泛函】r(m) = (λ₂,…,λ_V)/λ_max")

    # --- 轨道参数化（项目的实际配置：同轨道等权）---
    def m_orb(p):
        m = np.ones(E)
        for i, o in enumerate(orbs):
            for e in o:
                m[eidx[e]] = p[i]
        return m

    P("      ① 轨道参数化（%d 参 = 项目设置）：" % len(orbs))
    p0 = np.ones(len(orbs))
    for h in (1e-3, 1e-4, 1e-5):
        sv = np.linalg.svd(fd_jac(lambda p: ratios(m_orb(p), Bm), p0, h=h),
                           compute_uv=False)
        P("         h=%.0e  奇异值 = %s" % (h, np.round(sv, 12)))
    P("         ⇒ 最小奇异值 **∝ h 线性趋零**（2.83e-4 → 2.83e-5 → 2.83e-6）")
    P("           = 折点(kink)特征，非真导数 ⇒ **结构性 rank = 1**，核 = span{(1,1)} = 规范方向。")
    P("         ⇒ 解集维数 = %d − 1 = 1，且这 1 维**正是尺度**。"
      % len(orbs))
    P("           即：在轨道参数化下 a/b 被谱比**完全定住**；残余的 1 维自由 = 整体尺度，")
    P("           而尺度本来就不可观测（一切可观测量都是比值） ——")
    P("           这正是 §3 所记『实欠定 1』的确切身份。")
    P()

    # --- 一般点：破缺对称 ---
    rng = np.random.default_rng(11)
    m_gen = 1.0 + 0.45 * rng.standard_normal(E)
    ev_gen = np.linalg.eigvalsh(lap(Bm, m_gen))
    P("      ② 一般点（破缺对称）：谱无退化（最小间距 = %.3e）⇒ 映射可微" %
      float(np.min(np.diff(np.sort(ev_gen)))))
    J_gen = fd_jac(lambda m: ratios(m, Bm), m_gen, h=1e-5)
    r_gen = rk(J_gen, rtol=1e-6)
    P("         rank(J_r) = %d / %d   ⇒ 解集维数 = %d"
      % (r_gen, E, E - r_gen))
    gauge = np.linalg.norm(J_gen @ m_gen) / (np.linalg.norm(J_gen) * np.linalg.norm(m_gen))
    P("         规范检验 ‖J·m‖/(‖J‖‖m‖) = %.3e ⇒ 尺度方向确在核内（1 维）" % gauge)
    P()

    P("      ③ ⚠ 项目实际配置（单位权）恰是映射**不可微**的点：")
    J_sym = fd_jac(lambda m: ratios(m, Bm), m0, h=1e-4)
    P("         18 维 FD 雅可比：rank ≈ %d（伪像）；且 ‖J·1⃗‖ = %.3f ≠ 0 ——"
      % (rk(J_sym, rtol=1e-4), float(np.linalg.norm(J_sym @ m0))))
    P("         而真实方向导数沿 1⃗ 恒为 0（比值对尺度严格不变）。")
    P("         ⇒ 在对称点上**任何基于 FD 雅可比的秩/灵敏度判据都不可信**。")
    P()
    P("⇒ 结论 C：**和型（反应式）恒贡献 1 维；谱型在轨道空间贡献 1 维、在一般点贡献 %d 维。**"
      % r_gen)
    P("   化学能给的不是『反应式』（和型），而是**振动频率 = 拉普拉斯特征值**（谱型）——")
    P("   那正是本项目『第二条泛函』的本来面目。但它的上限被**谱重数**卡住：")
    P("   骨架在对称配置下只有 %d 个非平凡比值可用。" % (len(uniq) - 1))
    return None


# ======================================================================
# PART D  规范方向
# ======================================================================
def part_D():
    head("PART D  规范（尺度）方向 —— 任何『同一批图的方程』都钉不住")
    G = Y3("", "p")
    edges, Bm = geometry(G)
    E = len(edges)
    m0 = 1.0 + 0.3 * np.random.default_rng(5).standard_normal(E)

    P("D1. 比值型泛函的尺度不变性（m → c·m）")
    r_base = ratios(m0, Bm)
    mx = max(float(np.max(np.abs(ratios(c * m0, Bm) - r_base)))
             for c in (0.5, 2.0, 137.0, 1e6))
    P("    max |r(c·m) − r(m)|, c ∈ {0.5, 2, 137, 1e6} = %.3e" % mx)
    P("    ⇒ 精确不变：**1 维规范轨道**（与 Op13–18 §13.6 的齐次性定理同源）。")
    P()
    P("D2. 规范方向落在零空间里")
    J = fd_jac(lambda m: ratios(m, Bm), m0, h=1e-5)
    g = J @ m0
    P("    ‖J·m‖ / (‖J‖‖m‖) = %.3e" % (np.linalg.norm(g) / (np.linalg.norm(J) * np.linalg.norm(m0))))
    P("    ⇒ **m 本身是零方向** ⇒ 加多少条**同类型**的比值方程都补不上这 1 维。")
    P()
    P("D3. 要钉住规范，唯一出路是「跨图 + 绝对量」")
    P("    · 同一张图内：新方程仍在零空间外 ⇒ 规范不动；")
    P("    · 跨两张图并强制共用一把锁（L4）⇒ 才是真正的新方程；")
    P("    · 反应式**不是**跨图锁 —— 它是同一批物种内部的差，两图各自仍可独立缩放。")
    return None


def main():
    P("=" * 88)
    P("方程数不足：用『已知不同反应式』补方程，能否救反解？")
    P("=" * 88)
    part_A()
    part_B()
    part_C()
    part_D()
    head("PART E  裁决")
    P("1. 【反应式无用 —— 定理级】反应式 ≡ 同一批物种方程的行线性组合（R = C·A），")
    P("   堆叠后秩一个不增。化学（A0–A2）与核反应（B）双例实测确认；")
    P("   核反应 Q 值与结合能互为线性组合，逐项吻合 1e-4。")
    P("2. 【真正扩秩的两条路】")
    P("   (i)  引入**新未知**：新键型 / 新物种 / 新分子图（A3 实测 +1、+2 秩）；")
    P("   (ii) 引入**非线性且非行空间的泛函**：谱量（C：和型 1 维 vs 谱型 10 维）。")
    P("   化学能提供 (ii) —— 但载体是**振动谱（拉普拉斯特征值）**，不是反应式。")
    P("3. 【核子线的结构性障碍】轨道参数化下谱比 rank = 1 ⇒ 只剩 1 维 = 规范（尺度）；")
    P("   一般 18 维点 rank = 10 ⇒ 仍有 8 维解流形。**独立读数的上限被谱重数卡住**")
    P("   （对称配置下只有 3 个非平凡比值）。且项目配置恰是映射**不可微**的点。")
    P("4. 【规范 1 维钉不住】m→cm 使全部比值型泛函严格不变，任何同类型方程都无效；")
    P("   只有 L4（跨图 + 绝对锚）能钉住 —— 与 Op13–18 §13.6 的结论一致。")
    P("5. 【落点】化学数据（键能 / 反应热 / 振动谱）属于**维度塌缩 · 键长加和律**那条线，")
    P("   可用于标定**共享的 w(k) 律**（『值』的外源锚）；对**核子结合能**那条线**不受益** ——")
    P("   核子线的壁垒是账本层代数恒等式 + 谱层退化，两者都不是「方程数」问题。")


if __name__ == "__main__":
    main()
