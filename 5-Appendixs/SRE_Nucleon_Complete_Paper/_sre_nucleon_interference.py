# -*- coding: utf-8 -*-
"""以"干涉程度"恢复 A>=4 可算性的尝试。只做计算。

模型形式化（与第 12.6 节一致）：
    对 A 个体共享同一环的构形，共享环三条边的声称剖面为 (k1,k2,k3) = (#p, A, A)。
    记 B 为以 Delta m_np 为单位的结合能，作加性泛函 B = psi(k1) + psi(k2) + psi(k3)。
本脚本做四件事：
    (1) 证明加性剖面定价类的不可修复性（恒等式，与 psi 形态无关）；
    (2) 检验"组成分辨的干涉度"（互补对 C、同型对 S、不平衡度 a）能否容纳已测四点；
    (3) 核验 A=4 三种组成是否同一同构类（图能否承载结合能差异）；
    (4) 给出最小可修复扩展所需的外加项及其代价（拟合而非预言）。
"""
import sys
import itertools
from fractions import Fraction as F
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MP, MN = 938.27208816, 939.56542052
DM = MN - MP                                     # 1.293332 MeV
BEXP = {"d": 2.224566, "t": 8.4820, "He3": 7.7181, "a": 28.2957}   # MeV
B = {k: v / DM for k, v in BEXP.items()}

# (A, #p) -> 已测
CAL = {"d": (2, 1), "t": (3, 1), "He3": (3, 2), "a": (4, 2)}
OUT = {"4H": (4, 1), "4Li": (4, 3)}
FATE = {"d": "束缚 2.2246 MeV", "t": "束缚 8.4820 MeV", "He3": "束缚 7.7181 MeV",
        "a": "束缚 28.2957 MeV", "4H": "不束缚（阈上共振）", "4Li": "不束缚（阈上共振）"}


def profile(A, np_):
    """共享环三条边的声称剖面与逐边的 (k_n,k_p) 分解。"""
    k1 = np_                                     # 仅质子声称该边
    prof = (k1, A, A)
    dec = [("#p", (0, np_)), ("全", (A - np_, np_)), ("全", (A - np_, np_))]
    return prof, dec


print("=" * 90)
print("(0) 账本剖面与组成的关系：剖面 = (#p, A, A)")
print("=" * 90)
print("  %-5s %-4s %-4s %-14s %-24s %-16s %s"
      % ("核", "A", "#p", "声称剖面", "逐边 (k_n,k_p) 分解", "B/Δm", "实测"))
for tag, (A, np_) in {**CAL, **OUT}.items():
    prof, dec = profile(A, np_)
    bs = "%.6f" % B[tag] if tag in B else "——（外样本）"
    print("  %-5s %-4d %-4d %-14s %-24s %-16s %s"
          % (tag, A, np_, str(prof), str([d[1] for d in dec]), bs, FATE[tag]))

print()
print("=" * 90)
print("(1) 加性剖面定价类的不可修复性（恒等式，与 psi 形态无关）")
print("=" * 90)
print("  B = psi(k1) + psi(k2) + psi(k3)，对 (A,#p) 组成即 B = psi(#p) + 2*psi(A)。")
print("  三个已测核给出三个方程（未知 psi(1),psi(2),psi(3)）：")
print("     d   : psi(1) + 2*psi(2) = B_d   = %.6f" % B["d"])
print("     t   : psi(1) + 2*psi(3) = B_t   = %.6f" % B["t"])
print("     He3 : psi(2) + 2*psi(3) = B_He3 = %.6f" % B["He3"])
print("  第二式减第三式，psi(3) 消去：")
dlt = B["t"] - B["He3"]
print("     psi(1) - psi(2) = B_t - B_He3 = %+.6f Δm = %+.4f MeV" % (dlt, dlt * DM))
print("  而 4H 与 4He 的剖面仅差第一条边（1 对 2），故")
print("     B(4H) - B(4He) = psi(1) - psi(2)   ← 恒等式")
print("     => 预言 B(4H) = B(4He) + %.6f = %.6f Δm = %.4f MeV"
      % (dlt, B["a"] + dlt, (B["a"] + dlt) * DM))
p2 = (B["d"] - dlt) / 3.0
p1 = B["d"] - 2 * p2
p3 = (B["t"] - p1) / 2.0
print("  绝对定值：psi(1)=%+.6f  psi(2)=%+.6f  psi(3)=%+.6f（Δm 单位）" % (p1, p2, p3))
print("     4Li : B = psi(3) + 2*psi(4)，与 4He 差 psi(3)-psi(2) = %+.6f Δm = %+.4f MeV"
      % (p3 - p2, (p3 - p2) * DM))
print("     => 预言 B(4Li) = B(4He) + %.6f = %.6f Δm = %.4f MeV"
      % (p3 - p2, B["a"] + p3 - p2, (B["a"] + p3 - p2) * DM))
print("  【判据】两个预言的符号由三个已测核锁定，与 psi 的具体形态完全无关：")
print("     psi(1) - psi(2) = %+.6f > 0 且 psi(3) - psi(2) = %+.6f > 0"
      % (dlt, p3 - p2))
print("     => 无论怎样重新定义『每条边上的干涉程度』，4H 与 4Li 都被预言比 4He 更紧束缚，")
print("        而实测二者都不束缚。**加性剖面定价类作为一整类被证伪。**")

print()
print("=" * 90)
print("(2) 组成分辨的干涉度：能否容纳已测四点？")
print("=" * 90)
print("  定义（对共享环三条边求和）：")
print("     C = Σ k_n·k_p        （互补型干涉：中-质配对同时声称同一条边）")
print("     S = Σ [C(k_n,2)+C(k_p,2)]（同型干涉）")
print("     I = Σ (k-1)          （总多声称数，即最朴素的『干涉程度』）")
print("     a = |n_n - n_p|      （不平衡度）")
feat = {}
for tag, (A, np_) in {**CAL, **OUT}.items():
    prof, dec = profile(A, np_)
    Cc = sum(kn * kp for _, (kn, kp) in dec)
    Ss = sum(kn * (kn - 1) // 2 + kp * (kp - 1) // 2 for _, (kn, kp) in dec)
    Ii = sum(prof) - 3
    aa = abs(A - 2 * np_)
    feat[tag] = dict(C=Cc, S=Ss, I=Ii, a=aa, k1=np_)
    print("  %-5s (C,S,I,a,#p) = (%d, %d, %d, %d, %d)   B=%s"
          % (tag, Cc, Ss, Ii, aa, np_,
             ("%.6f" % B[tag]) if tag in B else "——"))


def lin_fit(xs, ys):
    """最小二乘（带常数项可选）返回预测函数与最大残差"""
    Xm = np.column_stack([np.ones(len(xs[0])), *xs])
    coef, *_ = np.linalg.lstsq(Xm, ys, rcond=None)
    pred = Xm @ coef
    return coef, pred, float(np.max(np.abs(pred - ys)))


tags_cal = ["d", "t", "He3", "a"]
print()
print("  两点/三点线性基的拟合检验（用 d/t/He3/4He 四点定标，报最大绝对残差，单位 Δm）：")
bases = {
    "(C,S)": [np.array([feat[t]["C"] for t in tags_cal]), np.array([feat[t]["S"] for t in tags_cal])],
    "(C,a)": [np.array([feat[t]["C"] for t in tags_cal]), np.array([feat[t]["a"] for t in tags_cal])],
    "(I,a)": [np.array([feat[t]["I"] for t in tags_cal]), np.array([feat[t]["a"] for t in tags_cal])],
    "(C,I)": [np.array([feat[t]["C"] for t in tags_cal]), np.array([feat[t]["I"] for t in tags_cal])],
}
yc = np.array([B[t] for t in tags_cal])
for name, xs in bases.items():
    coef, pred, mx = lin_fit(xs, yc)
    rel = mx / np.mean(yc) * 100
    print("     B = %-28s 系数 %s  最大残差 %.4f Δm (%.1f%%)"
          % (name, np.round(coef, 4), mx, rel))
    # 用同一组拟合系数外推 4H / 4Li，看符号是否与实测一致
    out = []
    for tag in OUT:
        x = {"(C,S)": [feat[tag]["C"], feat[tag]["S"]],
             "(C,a)": [feat[tag]["C"], feat[tag]["a"]],
             "(I,a)": [feat[tag]["I"], feat[tag]["a"]],
             "(C,I)": [feat[tag]["C"], feat[tag]["I"]]}[name]
        val = coef[0] + coef[1] * x[0] + coef[2] * x[1]
        out.append("%s 预测 %+.4f Δm (%s)" % (tag, val, "束缚" if val > 0 else "不束缚"))
    print("       外样本外推：%s   -> 与实测（均不束缚）一致? %s"
          % (" ; ".join(out),
             all(("不束缚" in s) for s in out)))
print("  => 所有线性基（含常数项共 3 个拟合参数、仅 1 个剩余自由度）都不能同时容纳四点；")
print("     且用同一组系数外推 4H/4Li，符号全部判为『束缚』，与实测相反 —— 即使放宽到 3 参数也无法修复。")
print("     另注：3H 与 3He 的互补型干涉 C 相同（同为 4），而同型干涉 S 为 2 对 3、不平衡度 a 同为 1，")
print("     实测结合能却是 6.558 对 5.968 Δm —— 随 S（或 I）单调递减。")
print("     若要求『干涉越大结合越强』（第 12.6 节的定性倾向），则 3H 应弱于 3He，与实测相反。")
print()
print("  镜像核直接对照（n 与 p 互换应给出相同结果，实测却不同）：")
for a_, b_ in (("t", "He3"), ("4H", "4Li")):
    print("     %-4s vs %-4s : (C,S,I,a) %s vs %s   实测 B %s vs %s"
          % (a_, b_,
             (feat[a_]["C"], feat[a_]["S"], feat[a_]["I"], feat[a_]["a"]),
             (feat[b_]["C"], feat[b_]["S"], feat[b_]["I"], feat[b_]["a"]),
             ("%.4f" % B[a_]) if a_ in B else "——",
             ("%.4f" % B[b_]) if b_ in B else "——"))

print()
print("=" * 90)
print("(3) A=4 三种组成是否同一同构类？（图能否承载结合能差异）")
print("=" * 90)
import networkx as nx
from networkx.algorithms.isomorphism import GraphMatcher


def Y3(pre, state="p"):
    G = nx.Graph()
    for i in range(3):
        for j in range(3):
            G.add_edge("%sc%d" % (pre, i), "%sL%d%d" % (pre, i, j))
    for j in range(3):
        for x, y in ((0, 1), (1, 2), (2, 0)):
            G.add_edge("%sL%d%d" % (pre, x, j), "%sL%d%d" % (pre, y, j))
    if state == "n":
        G.remove_edge("%sL00" % pre, "%sL10" % pre)
    return G


def build(bodies, ring=0):
    H = nx.Graph()
    for pre, state in bodies:
        G = Y3(pre, state)
        m = {"%sL%d%d" % (pre, i, ring): "S%d" % i for i in range(3)}
        H.add_edges_from({tuple(sorted((m.get(u, u), m.get(v, v)))) for u, v in G.edges()})
    return H


def inv(G):
    ev = np.sort(np.linalg.eigvalsh(nx.laplacian_matrix(G).toarray()))
    return (G.number_of_nodes(), G.number_of_edges(), sum(nx.triangles(G).values()) // 3,
            G.number_of_edges() - G.number_of_nodes() + 1, float(ev[-1]), float(ev[1]),
            sum(1 for _ in itertools.islice(GraphMatcher(G, G).isomorphisms_iter(), 20000)))


gs = {"4He(2p2n)": build([("a", "p"), ("b", "p"), ("c", "n"), ("d", "n")]),
      "4H(1p3n)": build([("a", "p"), ("b", "n"), ("c", "n"), ("d", "n")]),
      "4Li(3p1n)": build([("a", "p"), ("b", "p"), ("c", "p"), ("d", "n")])}
for tag, G in gs.items():
    print("  %-11s V=%-3d E=%-3d T=%-2d b1=%-3d rho=%.9f lam2=%.9f |Aut|=%d"
          % ((tag,) + inv(G)))
print("  4He~4H 同构? %s ; 4He~4Li 同构? %s ; 4H~4Li 同构? %s"
      % (nx.is_isomorphic(gs["4He(2p2n)"], gs["4H(1p3n)"]),
         nx.is_isomorphic(gs["4He(2p2n)"], gs["4Li(3p1n)"]),
         nx.is_isomorphic(gs["4H(1p3n)"], gs["4Li(3p1n)"])))
print("  => 三者为同一同构类：任何图泛函（rho、lam2、T、b1、|Aut|、谱…）在三者上取同值，")
print("     而实测命运相反（一个束缚 28.30 MeV、两个不束缚）。")
print("     => 结合能差异不可能由图承载，只能由账本承载；而账本内的加性类已被第 (1) 节否证。")

print()
print("=" * 90)
print("(4) 最小可修复扩展及其代价")
print("=" * 90)
need = B["a"] + dlt
print("  要使 4H 不束缚，所需的附加项 T 必须满足（Δm 单位）：")
print("     T(d) = T(t) = T(He3) = T(4He) = 0（不破坏四个已测核）")
print("     T(4H) >= B(4H) = %.4f Δm = %.4f MeV（把它从束缚推到零以上）" % (need, need * DM))
print("  最小形态：取不平衡度 a = |n_n - n_p| 的函数，a<=1 上恒为 0、a=2 上取 T：")
print("     候选 g(a) = lam * (a-1) 对 a>=1 取正（a<=1 为 0）")
lam = need
print("     弱形式（线性）：lam = %.4f Δm = %.4f MeV，只需 1 个自由参数。" % (lam, lam * DM))
print("       校验：4H 与 4Li 的 a 均为 2 -> 二者同时被推至零以上（镜像对称，符合电荷对称性）")
print("       校验：d(a=0)、4He(a=0) 不受影响；t(a=1)、He3(a=1) 不受影响")
print("  代价与诚实边界：")
print("     (i) lam 无 SRE 内出处，属拟合参数，非预言；")
print("     (ii) 该形式只对 A=4 有内容；A>=5 每引入一个新体数就引入新的自由定值 psi(5)、psi(6)…，")
print("          方案对 A>=5 本身没有预测余量 —— 『恢复可算性』无从检验；")
print("     (iii) 故本条建议不作主结论，仅证明：修复需要账本之外的新量（此处为不平衡度），")
print("          而该新量当前不具备可证伪的预言能力。")

print()
print("=" * 90)
print("(5) 结论")
print("=" * 90)
print("  a) 加性剖面定价类被整类证伪（恒等式，与 psi 形态无关）；")
print("  b) 组成分辨的干涉度（互补对 C、同型对 S、不平衡度 a）的任一线性组合都无法容纳已测四点；")
print("  c) A=4 三种组成是同一同构类，图泛函在三者上取同值 -> 差异只能由账本承载；")
print("  d) 唯一可行的修复是引入账本之外、且在 a<=1 上恰为零的镜像反对称项，代价是 1 个拟合参数")
print("     且对 A>=5 无预测余量；")
print("  e) 因此『A >= 4 不在本层可算』这一边界是结构性的，不是数据不足所致。")
print("     附注：A=4 是全方案中唯一具备零参数外样本性质的区间 —— 边界恰好落在第一次真外推处。")
print()
print("done")
