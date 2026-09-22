# -*- coding: utf-8 -*-
"""反对称系数的尝试：lam 能否由 SRE 内量导出？

背景（承接第 12.9/12.11 节）：加性剖面定价 B = psi(k1)+psi(k2)+psi(k3)（剖面 = (#p,A,A)）
被一条与 psi 形态无关的恒等式整类证伪（4H、4Li 被强制预言为比 4He 更紧束缚）。
第 12.11(4) 节给出的唯一修补是引入账本之外、在 a = |n_n - n_p| <= 1 上恰为零的
镜像反对称惩罚项：B_model = psi(#p) + 2*psi(A) - lam*max(0, a-1)，lam >= B(4H)。
该节登记 lam 属拟合、无 SRE 内出处。本脚本把这一登记升级为定量检验。

三件事：
    (1) lam 的定量约束：阈值的性质。要求 lam >= B(4H) 意味着什么？
        与四个已测核结合能、与半经验不对称能系数对照。
    (2) lam 的候选择一检验：把 lam 取为 SRE 内可得量的封闭组合，看是否被唯一确定
        （欠定性论证）；并给出"一个自由参数、零检验余量"的形式化陈述。
    (3) 把"反对称"从【能量项】降格为【存在性判据】后是否仍有内容：
        判据 L1: |n_n - n_p| <= 1（零参数、n<->p 对称）；
        与第 12.8 节读法甲在 8 项记分卡上对照；再以 A >= 5 的实测存在性做外样本检验。
"""
import sys
import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MP, MN = 938.27208816, 939.56542052
DM = MN - MP                                     # 1.293332 MeV
BEXP = {"d": 2.224566, "t": 8.4820, "He3": 7.7181, "a": 28.2957}   # MeV
B = {k: v / DM for k, v in BEXP.items()}

CAL = {"d": (2, 1), "t": (3, 1), "He3": (3, 2), "a": (4, 2)}
OUT = {"4H": (4, 1), "4Li": (4, 3)}

# 已测四核定死的 psi(1..4)（第 12.6 节）
psi = {}
dlt = B["t"] - B["He3"]                          # psi(1) - psi(2)
psi[2] = (B["d"] - dlt) / 3.0
psi[1] = B["d"] - 2 * psi[2]
psi[3] = (B["t"] - psi[1]) / 2.0
psi[4] = (B["a"] - psi[2]) / 2.0

# A=4 共享环族的图不变量（第 12.5 节）
RHO4, T4, B1_4, AUT4, V4, E4, LAM2 = 7.909515966, 9, 25, 2304, 39, 63, 2 - np.sqrt(3)

print("=" * 96)
print("(0) 待导出的对象与恒等式回顾")
print("=" * 96)
print("  模型：B_model(A,#p) = psi(#p) + 2*psi(A) - lam*max(0, a-1)，a = |A - 2*#p|")
print("  已测四核（d、t、He3、4He）定死 psi(1..4)：")
for k in (1, 2, 3, 4):
    print("     psi(%d) = %+.6f Δm = %+.4f MeV" % (k, psi[k], psi[k] * DM))
print("  恒等式（与 psi 形态无关）：psi(1) - psi(2) = B_t - B_He3 = %+.6f Δm = %+.4f MeV"
      % (dlt, dlt * DM))
print("  因此 4H 的账面结合能为 B_ledger(4H) = psi(1) + 2*psi(4) = %.6f Δm = %.4f MeV"
      % (psi[1] + 2 * psi[4], (psi[1] + 2 * psi[4]) * DM))
lam_min = psi[1] + 2 * psi[4]
print("  要使 4H 不束缚，惩罚项必须满足  lam >= B_ledger(4H) = %.6f Δm = %.4f MeV"
      % (lam_min, lam_min * DM))

print()
print("=" * 96)
print("(1) lam 的定量约束：阈值的性质")
print("=" * 96)
print("  (1a) 阈值与四个已测核结合能对照（Δm 单位 / MeV）：")
rows = [("B_d   (氘核)", B["d"]), ("B_t   (³H)", B["t"]), ("B_He3 (³He)", B["He3"]),
        ("B_α   (⁴He)", B["a"]), ("lam 阈值 = B_ledger(4H)", lam_min)]
for nm, v in rows:
    mark = "  <-- 阈值以上" if v >= lam_min else ("  <-- 阈值以下（差 %.4f Δm = %.4f MeV）"
                                                  % (lam_min - v, (lam_min - v) * DM))
    print("     %-24s %+9.6f Δm  %+9.4f MeV%s" % (nm, v, v * DM, mark))
print("  事实：所需惩罚 lam >= %.4f MeV **超过 ⁴He 的结合能本身 %.4f MeV**。"
      % (lam_min * DM, B["a"] * DM))
print("        即：|n_n-n_p|=2 的『不对称代价』必须大于整个 α 粒子的结合能。")

print()
print("  (1b) 与半经验不对称能系数对照（核物理中唯一现成的不对称机制）：")
print("        液滴模型：E_asym = a_sym * (N-Z)^2 / A，经验 a_sym ≈ 22 ~ 24 MeV。")
for asym in (22.0, 23.0, 24.0):
    easym4 = asym * (2.0 ** 2) / 4.0              # A=4, |N-Z|=2 -> (N-Z)^2/A = 1
    easym3 = asym * (1.0 ** 2) / 3.0              # A=3, |N-Z|=1 -> 1/3
    print("        a_sym = %4.1f MeV : E_asym(A=4,|N-Z|=2) = %6.3f MeV  (缺 %.3f MeV, %.1f%%)"
          "   而 E_asym(³H) = %5.3f MeV（须为 0，实际非零 -> 另有污染）"
          % (asym, easym4, lam_min * DM - easym4,
             (lam_min * DM - easym4) / (lam_min * DM) * 100, easym3))
print("        结论：经验不对称能系数即使取上界 24 MeV，仍比所需阈值低 %.2f MeV（%.1f%%）。"
      % (lam_min * DM - 24.0, (lam_min * DM - 24.0) / (lam_min * DM) * 100))
print("        且该机制在 A=3 上给出 E_asym(³H) ≈ 7.7 MeV 的非零值 —— 但 ³H 已用于定标，")
print("        其账本项必须为零惩罚。故『不对称能』这一现成机制在两点上都不成立。")

print()
print("=" * 96)
print("(2) lam 能否由 SRE 内量导出：候选择一检验")
print("=" * 96)
print("  逻辑前提（第 12.11(1) 节）：A=4 三种组成属同一同构类，图泛函在 4He/4H/4Li 上取同值；")
print("  故 SRE 在 A=4 上可用的全部输入就是账本 (A, #p)（等价地剖面 (#p,A,A)）。")
print("  推论：任何 SRE 内量 X 都是 (A,#p) 的函数，故 X = X(a) 与 g(a) 同类 —— ")
print("        『把 lam 写成 SRE 内量』不产生新的约束，只产生一次重命名。")
print()
print("  尽管如此，仍逐项检验『自然候选』是否恰好被门槛定住：")
cands = {
    "B_α（α 结合能）": B["a"],
    "2*psi(4)": 2 * psi[4],
    "psi(4)-psi(2)": psi[4] - psi[2],
    "psi(4)-psi(1)": psi[4] - psi[1],
    "rho_4（闭合度势）": RHO4,
    "rho_4 - rho_2": RHO4 - 6.0,
    "sqrt(V+1) = sqrt(40)": float(np.sqrt(V4 + 1)),
    "T_4（闭合单元数）": float(T4),
    "beta1_4": float(B1_4),
    "|Aut|^(1/3)": AUT4 ** (1.0 / 3.0),
    "E_4 - V_4": float(E4 - V4),
    "(E_4-V_4)/lam_2": float(E4 - V4) / LAM2,
    "1/lam_2 = 2+sqrt(3)": 1.0 / LAM2,
    "rho_4^2 / |Aut|^(1/3)": RHO4 ** 2 / AUT4 ** (1.0 / 3.0),
    "2*B_α": 2 * B["a"],
    "B_α + B_d": B["a"] + B["d"],
}
print("     %-26s %-14s %-14s %s" % ("候选 X", "X / Δm", "X / MeV", "X >= 阈值?"))
for nm, v in sorted(cands.items(), key=lambda kv: kv[1]):
    print("     %-26s %+11.6f    %+11.4f    %s"
          % (nm, v, v * DM, "是" if v >= lam_min else "否"))
over = [v for v in cands.values() if v >= lam_min]
under = [v for v in cands.values() if v < lam_min]
print("  统计：%d 个候选落在阈值以上、%d 个落在阈值以下。" % (len(over), len(under)))
if over and under:
    print("        阈值落在候选池的%.4f Δm 至 %.4f Δm 之间的空隙里，两侧都不唯一。"
          % (max(under), min(over)))
print("  => 门槛是被『满足』的，不是被『定住』的：SRE 内没有选一原理把 lam 钉在一个值上。")
print()
print("  (2b) 更强的结构约束：lam 的『形』被 SRE 定住，『值』没有。")
print("     · 若 lam 取自图不变量（rho、T、beta1、|Aut|、谱…），因 A=4 三种组成同一同构类，")
print("       该量在 4He/4H/4Li 上取**同一常数**。常数惩罚会同时落在已定标的 ⁴He 上，")
print("       使四条定标方程不再被 psi(1..4) 满足 —— 定标自身被破坏。")
print("       => lam 必须是**组成相关**的，即必须是账本 (A,#p) 的函数、且在定标集 {a<=1} 上为零。")
print("     · 因此 SRE 决定的恰是 lam 的『形』：support(a<=1 为零) 与单调性（lambda>0 单调减结合能）；")
print("       而 SRE 不决定 lam 的『值』（幅度）：值只被不等式 lam >= %.4f Δm 界定，不被方程界定。"
      % lam_min)
print("     · 关键：A=4 的要求是**二值（存在性）**而非数值。二值要求只用到 lam 的『形』，")
print("       用不到『值』 —— 因为只要 lam > 0 且落在 a=2 上，4H/4Li 即被推向阈上，")
print("       与 lam 具体多大无关（前提 lam >= 阈值）。")
print("       => **系数 lam 对该二值要求是可省的**；它只在要求给出结合能数值时才有必要，")
print("          而在 A=4 上给不出可检验的数值（(2) 的零检验余量）。")
print()
print("  形式化陈述（零检验余量）：")
print("     待定集合 = {psi(1..4)} ∪ {lam}，方程 = 4 条（四已测核）。")
print("     故 lam 有 1 个自由参数；4 个数据点已用尽，A=4 上的任何 lam 取值都不能被证伪。")
print("     要证伪只能靠 A >= 5；但 A >= 5 每引入一个新体数就带进一个新的自由定值 psi(A)，")
print("     方案自身的参数增加速度与数据增加速度同阶 -> 对 A >= 5 无预测余量。")
print("     => 【lam 不可由 SRE 导出，也不可由 SRE 固定】：它不是可导出的系数，而是可吸收的自由度。")

print()
print("=" * 96)
print("(3) 降格为存在性判据：零参数的『反对称判据』是否有内容？")
print("=" * 96)
print("  观察：lam 存在的唯一理由是『让 4H/4Li 不束缚』—— 这是一个二值（存在性）要求，")
print("        不是数值要求。若把反对称性直接写成【合法性判据】而非【能量惩罚】，则不需 lam。")
print()
print("  判据 L1（反对称判据，零参数、n<->p 对称）：")
print("     合法（预言束缚）  <=>  |n_n - n_p| <= 1")
print("  判据 甲（第 12.8 节读法甲，作为对照）：")
print("     合法 <=> 1 <= n_n <= 2 且 n_p >= 1")


def verdict_L1(A, Z):
    return abs((A - Z) - Z) <= 1


def verdict_JIA(A, Z):
    nn, npp = A - Z, Z
    return (1 <= nn <= 2) and (npp >= 1)


SCORE = [("n-p", 2, 1, True), ("n-n", 2, 0, False), ("p-p", 2, 2, False),
         ("³H", 3, 1, True), ("³He", 3, 2, True), ("⁴He", 4, 2, True),
         ("⁴H", 4, 1, False), ("⁴Li", 4, 3, False)]
print()
print("  (3a) 第 12.8 节 8 项记分卡：")
print("     %-6s %-4s %-4s %-4s %-6s %-14s %-14s %s"
      % ("核", "A", "Z", "a", "实测", "L1 预测", "甲 预测", "命中"))
ok1 = okJ = 0
for nm, A, Z, bound in SCORE:
    a = abs((A - Z) - Z)
    p1 = verdict_L1(A, Z)
    pj = verdict_JIA(A, Z)
    ok1 += (p1 == bound)
    okJ += (pj == bound)
    print("     %-6s %-4d %-4d %-4d %-6s %-14s %-14s L1:%s 甲:%s"
          % (nm, A, Z, a, "束缚" if bound else "不束缚",
             "束缚" if p1 else "不束缚", "束缚" if pj else "不束缚",
             "√" if p1 == bound else "×", "√" if pj == bound else "×"))
print("     => L1（反对称判据）：%d/8 命中；甲（读法甲）：%d/8 命中。" % (ok1, okJ))
print("        L1 在 A<=4 上等效于『束缚 <=> 该 A 下 |N-Z| 取极小值』：")
print("        A=2 取 a=0（氘核）、A=3 取 a=1（³H、³He）、A=4 取 a=0（⁴He），全部命中；")
print("        甲的唯一失配（⁴Li）恰因『g<=2』只封顶中子数、不封顶质子数 —— L1 天然镜像对称。")

print()
print("  (3b) A>=5 外样本：实测存在性（基态是否束缚）")
print("     数据来源：各核基态存在性（束缚 = 有束缚基态）。⁸Be 标为不束缚（仅 0.092 MeV，α 不稳定）。")
EXT = [
    ("⁵He", 5, 2, False), ("⁵Li", 5, 3, False), ("⁵H", 5, 1, False),
    ("⁶He", 6, 2, True), ("⁶Li", 6, 3, True), ("⁶Be", 6, 4, False),
    ("⁷Li", 7, 3, True), ("⁷Be", 7, 4, True),
    ("⁸He", 8, 2, True), ("⁸Li", 8, 3, False), ("⁸Be", 8, 4, False), ("⁸B", 8, 5, False),
    ("⁹Be", 9, 4, True), ("⁹Li", 9, 3, False),
    ("¹⁰Be", 10, 4, True), ("¹⁰B", 10, 5, True), ("¹⁰C", 10, 6, False),
    ("¹¹B", 11, 5, True), ("¹¹Li", 11, 3, True), ("¹¹Be", 11, 4, True),
    ("¹²C", 12, 6, True), ("¹²Be", 12, 4, True), ("¹²B", 12, 5, True),
    ("¹⁴C", 14, 6, True), ("¹⁴N", 14, 7, True), ("¹⁴Be", 14, 4, True),
]
print("     %-6s %-4s %-4s %-4s %-8s %-10s %-10s %s"
      % ("核", "A", "Z", "a", "实测", "L1 预测", "甲 预测", "命中"))
stat = {}
okE1 = okEJ = 0
for nm, A, Z, bound in EXT:
    a = abs((A - Z) - Z)
    p1 = verdict_L1(A, Z)
    pj = verdict_JIA(A, Z)
    h1, hj = (p1 == bound), (pj == bound)
    okE1 += h1
    okEJ += hj
    if bound:
        stat.setdefault(A, []).append(a)
    print("     %-6s %-4d %-4d %-4d %-8s %-10s %-10s L1:%s 甲:%s"
          % (nm, A, Z, a, "束缚" if bound else "不束缚",
             "束缚" if p1 else "不束缚", "束缚" if pj else "不束缚",
             "√" if h1 else "×", "√" if hj else "×"))
print("     => L1：%d/%d 命中；甲：%d/%d 命中。" % (okE1, len(EXT), okEJ, len(EXT)))
print()
print("  分区间统计：")
for lab, lo, hi in (("A<=4（记分卡）", 1, 4), ("A=5（α+1 区）", 5, 5),
                    ("A=6..9", 6, 9), ("A=10..14", 10, 14)):
    sub = [(nm, A, Z, b) for nm, A, Z, b in EXT if lo <= A <= hi]
    if lab.startswith("A<=4"):
        sub = [(nm, A, Z, b) for nm, A, Z, b in SCORE]
    if not sub:
        continue
    n1 = sum(1 for nm, A, Z, b in sub if verdict_L1(A, Z) == b)
    nJ = sum(1 for nm, A, Z, b in sub if verdict_JIA(A, Z) == b)
    print("     %-16s 项数 %2d   L1 %2d/%2d  甲 %2d/%2d" % (lab, len(sub), n1, len(sub), nJ, len(sub)))
print("     合计：L1 %d/%d 命中，甲 %d/%d 命中。"
      % (ok1 + okE1, 8 + len(EXT), okJ + okEJ, 8 + len(EXT)))

print()
print("  (3c) 失配的性质诊断（L1）：")
print("     · A=5：⁵He(2,3)、⁵Li(3,2) 的 a 均为 1（该 A 下最小），L1 预言束缚，实测均不束缚。")
print("       两个失配都是『α 加一个核子不束缚』的闭合效应 —— 与不对称性无关，")
print("       故 **任何仅依赖组成 (A,Z) 的判据在 A=5 上必然失配**（A=5 无束缚核）。")
print("     · A>=6：实测**束缚核**所允许的 |N-Z| 上限随 A 上升（液滴图像 (N-Z)^2/A 的必然结果）。")
print("       逐 A 实测束缚核的 |N-Z| 上限（本样本内）：", end="")
for A in sorted(stat):
    print("A=%d:%d " % (A, max(stat[A])), end="")
print()
print("       固定阈值 |N-Z|<=1 在 A>=8 上系统性过严（把 ⁸He、¹¹Li、¹²Be、¹⁴Be 等")
print("       中子晕/滴线核判为不束缚，实测均束缚）。")
print("       => L1 不是基本律，而是**轻区的截断式分类规则**：在 A<=4 上精确，")
print("          在 A>=5 上退化为经验近似（其原因正是它缺少 A 的标度）。")

print()
print("  (3d) 若把判据改成带 A 标度的形式 ((N-Z)^2/A <= c)，能否同时容纳两端？")
need_lo = (2.0 ** 2) / 4.0                      # 4H/4Li：须非法 -> c < 1
drip = {"⁸He": (8, 2, 6), "¹¹Li": (11, 3, 8), "¹²Be": (12, 4, 8), "¹⁴Be": (14, 4, 10)}
need_hi = max(((A - 2 * Z) ** 2) / A for A, Z, N in drip.values())
print("        上界约束：4H/4Li 在 A=4 上 (N-Z)^2/A = %.3f，要判为非法须 c < %.3f。" % (need_lo, need_lo))
print("        下界约束：滴线/中子晕核（⁸He、¹¹Li、¹²Be、¹⁴Be）实测束缚，其 (N-Z)^2/A 最大 %.3f，"
      % need_hi)
print("                  要判为合法须 c >= %.3f。" % need_hi)
print("        两约束不相容（c < 1 与 c >= %.1f）=> 单一常数 c 的 (N-Z)^2/A 判据不可能同时容纳两端。" % need_hi)
for c in (0.25, 0.50, 0.80, 1.0, 2.0, 2.5, 3.0):
    n_all = sum(1 for nm, A, Z, b in SCORE if ((A - 2 * Z) ** 2 / A <= c) == b)
    n_ext = sum(1 for nm, A, Z, b in EXT if ((A - 2 * Z) ** 2 / A <= c) == b)
    print("        c = %5.3f : 记分卡 %d/8   外样本 %d/%d   合计 %d/%d"
          % (c, n_all, n_ext, len(EXT), n_all + n_ext, 8 + len(EXT)))
print("        故 A=4 一侧必须由**闭合效应**（α 单元的特殊闭合）承担，而非 (N-Z)^2/A 标度；")
print("        这与第 12.11 节判据⑤（闭合度部分再平衡）的取向一致。")

print()
print("=" * 96)
print("(4) 结论")
print("=" * 96)
print("  a) lam 不可由 SRE 导出：所需阈值 lam >= %.4f MeV 超过 α 结合能 %.4f MeV，"
      % (lam_min * DM, B["a"] * DM))
print("     也超过经验不对称能系数所能提供的最大值（a_sym=24 MeV 时低 %.2f MeV）。"
      % (lam_min * DM - 24.0))
print("     结构上：SRE 内量只有两类来源 —— 图不变量（在同构类上为常数，会破坏定标）与")
print("     账本函数（与 g(a) 同类，不产生新约束）；两类都不提供把 lam 钉住的选一原理。")
print("     SRE 定住 lam 的『形』（a<=1 上为零、单调减结合能），不定住其『值』。")
print("  b) lam 也不可由 SRE 固定：待定 5 个（psi(1..4)、lam）对 4 个方程 -> 1 个自由参数，")
print("     A=4 上零检验余量；A>=5 上参数增加与数据增加同阶 -> 无外样本可证伪。")
print("  c) 反对称性唯一有内容的形态是【存在性判据】：L1: |n_n-n_p| <= 1，零参数、n<->p 对称，")
print("     在 12.8 节 8 项记分卡上 8/8 命中（甲 7/8）—— 本层可比原登记更精确地判定 A=4 存在性。")
print("  d) 但 L1 不是基本律：A=5 两个失配属闭合效应（A=5 无束缚核，任何组成判据必失配）；")
print("     A>=8 系统性过严（缺 A 标度）。故 L1 的精确性限于轻区，边界被**移位**（A=4 -> A>=5）")
print("     而非取消。")
print("  e) 对第 12.9/12.11 节边界的修订：**结合能数值**在 A>=4 仍不可算（12.11(2) 恒等式不受影响）；")
print("     **存在性**在 A=4 上可由 L1 以零参数判定（8/8），在 A>=5 上不可（判据退化）。")
print()
print("done")
