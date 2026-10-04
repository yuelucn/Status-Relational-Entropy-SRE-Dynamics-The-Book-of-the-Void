# -*- coding: utf-8 -*-
"""
_sre_cyclic_mass_formalism.py
SRE 的「质量」的准确数学表述：循环矩阵 / 挠子上的等变结构
（第三十二轮，2026-09-28）

用户命题：
  「SRE 描述的质量是一个**没有打开的、循环的**演化逻辑。
    准确的数学描述和表达应该是什么？」

形式化答案（本脚本逐条验证）：
  命题1(对象)  三环 = Z3-挠子（第 30 轮已证：1 条轨道、大小 3、显式阶 3 元）
               ⇒ 「质量算子」的 Z3-等变性
  命题2(循环)  与循环移位 S 交换 ⇔ 循环矩阵（circulant）
               ——「循环的演化逻辑」的精确数学名字
  命题3(形状)  Hermitian 循环矩阵的谱 = c0 + 2|c1| cos(theta + 2*pi*k/3)
               ⇒ 「三点共一条余弦」= Koide 参数化的**唯一一阶形式**（非拟合）
  命题4(没打开) SRE 原生产物 = 等变类 = 多重集，不变量模空间 2 维 (eta, delta mod 2pi/3)
               其中 Q = 1/3 + (2/3)eta^2 **只占 eta 那一个方向**（对 delta 免疫）
  命题5(打开)  「打开」= 给多重集一个原点（DFT 相位约定）= Z3（3 重）规范
               不变量完全不变，只决定「哪一代叫第一代」
  命题6(Koide) 真实带电轻子复算：Q = 2/3 <=> eta^2 = 1/2
  命题7(对照)  与既有 rho / Pi1 / lambda2 的不变性类型对照

引用：
  C:/myapp/miniconda3/envs/ai/python.exe -u _sre_cyclic_mass_formalism.py > _sre_cyclic_mass_formalism.log 2>&1
"""
import json
import math
import cmath
import numpy as np

OUT = {}
W = cmath.exp(2j * math.pi / 3.0)


def P(*a):
    print(*a)


def head(t):
    P()
    P("=" * 92)
    P(t)
    P("=" * 92)


def shift_matrix(n=3):
    """循环移位 S：S e_k = e_{k+1}（列 k -> 行 k+1）。"""
    S = np.zeros((n, n))
    for k in range(n):
        S[(k + 1) % n, k] = 1.0
    return S


def is_circulant(A, tol=1e-9):
    """循环矩阵判据：A[i][j] 只依赖 (j-i) mod n。"""
    n = A.shape[0]
    c = A[0, :]
    for i in range(n):
        for j in range(n):
            if abs(A[i, j] - c[(j - i) % n]) > tol:
                return False
    return True


def amps(eta, delta):
    """三代质量振幅 a_k = 1 + 2*eta*cos(delta + 2*pi*k/3)（尺度归一化 c0 = 1）。"""
    return [1.0 + 2.0 * eta * math.cos(delta + 2.0 * math.pi * k / 3.0) for k in range(3)]


def Q_of(a):
    """Koide 组合（作用在振幅 a = sqrt(m) 上）。"""
    return sum(x * x for x in a) / (sum(a) ** 2)


def invs(a):
    """返回两个尺度不变 + 置换不变的不变量：Q（对 delta 免疫）与 R（依赖 delta）。"""
    m = [x * x for x in a]
    e1 = sum(m)
    return Q_of(a), (max(m) - min(m)) / e1


# ==================================================================================
# PART A —— 定理：与循环移位交换 ⇔ 循环矩阵
# ==================================================================================
head("PART A  定理：「循环的演化逻辑」的精确数学名字 = 循环矩阵（circulant）")

n = 3
I = np.eye(n)
S = shift_matrix(n)
S2 = S @ S

P("A0  循环移位 S（S e_k = e_{k+1}）：")
for r in range(n):
    P("      [%s]" % "  ".join("%.0f" % S[r, c] for c in range(n)))
P()
P("A1  「与 S 交换的算子」全体（中心化子）—— 用 9x9 线性方程组 AS = SA 的零空间求：")
L = np.kron(S.T, I) - np.kron(I, S)
sv = np.linalg.svd(L, compute_uv=False)
rank = int(np.sum(sv > 1e-9))
dim_c = n * n - rank
P("      vec(AS) - vec(SA) = [(S^T kron I) - (I kron S)] vec(A)")
P("      系数矩阵秩 = %d（在 %d 维空间里）⇒ 解空间（中心化子）维数 = %d" % (rank, n * n, dim_c))
P("      循环矩阵空间的维数 = n = %d   ⇒ 二者相符：%s" % (n, "是" if dim_c == n else "否"))
P()

U, s_, Vt = np.linalg.svd(L)
null_basis = Vt[rank:, :]
allcirc = all(is_circulant(null_basis[i].reshape(n, n)) for i in range(null_basis.shape[0]))
P("A2  零空间一组基 reshape 成矩阵后**全部是循环矩阵**：%s" % allcirc)
P("      ⇒ 标准基可取 {I, S, S^2}：")
for nm, M in (("I", I), ("S", S), ("S^2", S2)):
    P("        %-5s 是循环矩阵 = %s" % (nm, is_circulant(M)))
P()
P("A3  维数分级（「循环」是硬约束，额外的物理条件继续削参数）：")
P("      · 一般复循环矩阵   c0*I + c1*S + c2*S^2          : 3 个复参数（6 实）")
P("      · 实循环矩阵                                     : 3 实参数")
P("      · 实对称循环矩阵   (c1 = c2 均实)                : 2 实参数  ⇒ 谱恒为 2+1")
P("      · Hermitian 循环   (c0 实, c2 = conj(c1))        : 3 实参数  ⇒ 谱一般 1+1+1")
P()
P("      ⇒ 「循环」把 9 个矩阵元素压到 3 个；这是 Z3-等变性的全部代价。")
OUT["A"] = {"dim_centralizer": dim_c, "all_null_basis_circulant": bool(allcirc),
            "expected_dim": n}


# ==================================================================================
# PART B —— Hermitian 循环矩阵的谱 = Koide 参数化
# ==================================================================================
head("PART B  形状：Hermitian 循环矩阵的谱 = c0 + 2|c1| cos(theta + 2*pi*k/3) = Koide 参数化")

P("B0  设 M = c0*I + c1*S + conj(c1)*S^2（Hermitian）。")
P("    S 的本征向量是 DFT 基、本征值 omega^j = exp(2*pi*i*j/3)：")
P("        lambda_j = c0 + c1*omega^j + conj(c1)*omega^{-j}")
P("                 = c0 + 2*|c1| * cos(theta + 2*pi*j/3),   c1 = |c1| e^{i theta}")
P("    ⇒ 三个本征值**落在同一条余弦的 120 度采样点上**。")
P("      这正是 Koide 的参数化形式。")
P("      ⚠ 但**必须立刻澄清**：该形式对**任意**三代都自动成立（见 B3）——")
P("        因此「余弦形状」是**免费的重参数化**，不是约束。")
P()

P("B1  数值验证（随机 c0、|c1|、theta，对比解析式）：")
rng = np.random.default_rng(7)
tabB = []
for k in range(5):
    c0 = rng.uniform(0.5, 2.0)
    m1 = rng.uniform(0.0, 0.45 * c0)
    th = rng.uniform(0.0, 2.0 * math.pi)
    c1 = m1 * cmath.exp(1j * th)
    M = c0 * I + c1 * S + np.conj(c1) * (S @ S)
    herm = bool(np.allclose(M, M.conj().T))
    ev = np.sort(np.linalg.eigvalsh(M))
    frm = np.sort([c0 + 2.0 * m1 * math.cos(th + 2.0 * math.pi * j / 3.0) for j in range(3)])
    err = float(np.max(np.abs(ev - frm)))
    tabB.append({"c0": c0, "abs_c1": m1, "theta": th, "hermitian": herm, "max_err": err})
    P("      c0=%.4f |c1|=%.4f theta=%+.4f  Herm=%s  最大误差=%.2e  lambda=%s"
      % (c0, m1, th, herm, err, np.array2string(ev, precision=6)))
P()
P("B2  「实对称 ⇒ 2+1」vs「带复相位 ⇒ 1+1+1」（这直接回答「为什么必须有相位」）：")
for tag, m1, th in (("实对称 (theta = 0)", 0.30, 0.0), ("复相位 (theta = 1.0)", 0.30, 1.0)):
    c1 = m1 * cmath.exp(1j * th)
    M = 1.0 * I + c1 * S + np.conj(c1) * (S @ S)
    ev = np.sort(np.real(np.linalg.eigvalsh(M)))
    uniq = len(set(np.round(ev, 9).tolist()))
    part = {1: "3", 2: "2+1", 3: "1+1+1"}[uniq]
    P("      %-22s lambda = %-34s 取值个数 = %d  ->  划分 %s"
      % (tag, np.array2string(ev, precision=6), uniq, part))
P()
P("      ⇒ 实对称循环矩阵的谱恒为 (c0+2|c1|, c0-|c1|, c0-|c1|) —— 只有两值（2+1）；")
P("        要三代互异（1+1+1），循环矩阵**必须带复相位**（Hermitian 而非实对称）。")
P("      · 观察（登记，非结论）：这与第 30 轮「闭态 Z3 / 开态 Z2」在算子层呼应 ——")
P("        开态 = 只剩两值（Z2 型退化）；闭态 = 一般三值（Z3 完整）。")
P()
P("B3  ⚠ 关键澄清（消解一个可能的误读）：**任意**三个实数都能写成上面这个形式。")
P("    反解（设 a_k = c0 + 2|c1|cos(theta + 2*pi*k/3)）：")
P("        c0  = mean(a)")
P("        z   = sum_k a_k * omega^k  =  3|c1| * e^{-i theta}")
P("      ⇒ |c1| = |z|/3,  theta = -arg(z) —— 3 个未知、3 个方程，一般**唯一**有解。")
P()
rng2 = np.random.default_rng(11)
maxerr = 0.0
for _ in range(8):
    a = list(rng2.uniform(-2.0, 5.0, 3))
    c0x = sum(a) / 3.0
    zx = sum(a[k] * (W ** k) for k in range(3))
    c1a = abs(zx) / 3.0
    thx = (-cmath.phase(zx)) % (2.0 * math.pi)
    rec = [c0x + 2.0 * c1a * math.cos(thx + 2.0 * math.pi * k / 3.0) for k in range(3)]
    maxerr = max(maxerr, float(max(abs(rec[k] - a[k]) for k in range(3))))
P("    随机 8 组「任意三数」→ 反解 → 重构，最大误差 = %.2e" % maxerr)
P()
P("    ⇒ **「三点共一条余弦」不是约束，是免费的重参数化**（任意三数皆然）。")
P("      ⇒ **Koide 的内容不是「形状」，而是「形状的参数恰为 eta = |c1|/c0 = 1/sqrt2」。**")
P("      ⇒ 与第 30 轮结论一致（内容 = eta^2 = 1/2），但**纠正**了「Z3 给出 Koide 形状」的说法：")
P("        形状是平凡的；Z3 的真实贡献是「为什么恰有 3 个位置」（挠子大小 3）")
P("        与「delta 为何是规范」（挠子无原点）。")
P()
koide_amp = [math.sqrt(x) for x in (0.51099895069, 105.6583755, 1776.93)]
c0k = sum(koide_amp) / 3.0
zk = sum(koide_amp[k] * (W ** k) for k in range(3))
eta_meas = (abs(zk) / 3.0) / c0k
P("    真实轻子反解： eta = |c1|/c0 = %.9f   1/sqrt2 = %.9f   偏差 = %+.3e"
  % (eta_meas, 1.0 / math.sqrt(2.0), eta_meas - 1.0 / math.sqrt(2.0)))
P("    ⚠ D1 纪律：1/sqrt2 是无理数（好），但 1/2 = eta^2 仍是小分母有理数 ⇒ 数值命中不作独立证据。")
OUT["B3"] = {"arbitrary_triple_reconstruction_max_err": maxerr,
             "eta_measured": eta_meas, "eta_target": 1.0 / math.sqrt(2.0)}
OUT["B"] = {"checks": tabB,
            "note": "Hermitian circulant spectrum = c0 + 2|c1|cos(theta+2pi k/3); real-symmetric forces 2+1; "
                    "WARNING: the cos-form is a free reparametrization valid for ANY triple (see B3)"}


# ==================================================================================
# PART C —— 「没有打开」的精确含义：SRE 原生产物 = 等变类（多重集）
# ==================================================================================
head("PART C  「没有打开」的精确含义：SRE 原生产物 = 等变类 = 多重集（2 个不变量）")

P("C0  SRE 的「未打开」输出 = 循环算子的**等变类**（基无关）。")
P("    参数化：a_k = 1 + 2*eta*cos(delta + 2*pi*k/3)（c0 已归一化掉，尺度即外部输入）。")
P()
P("C1  不变量 1：Q = sum(a^2)/(sum a)^2 —— 验证其**与 delta 无关**（只依赖 eta）：")
tabC1 = []
for eta in (0.30, 0.50, 1.0 / math.sqrt(2), 0.80):
    qs = [Q_of(amps(eta, d)) for d in np.linspace(0.0, 2.0 * math.pi, 361)]
    ana = 1.0 / 3.0 + 2.0 * eta * eta / 3.0
    tabC1.append({"eta": eta, "Q_range": max(qs) - min(qs), "Q": qs[0], "analytic": ana})
    P("      eta=%.6f   Q 的极差 = %.3e   Q = %.9f   解析 1/3+(2/3)eta^2 = %.9f"
      % (eta, max(qs) - min(qs), qs[0], ana))
P()
P("C2  不变量 2：R = (m_max - m_min)/sum(m) —— 验证其**依赖 delta**（故独立于 Q）：")
tabC2 = []
for delta in (0.0, 0.4, 0.8, 1.2):
    Q, R = invs(amps(1.0 / math.sqrt(2), delta))
    tabC2.append({"delta": delta, "Q": Q, "R": R})
    P("      eta=1/sqrt2  delta=%.3f   Q = %.9f   R = %.9f" % (delta, Q, R))
P()
P("C3  不变量模空间是 **2 维**：(eta, delta mod 2*pi/3)。")
P("      · Q 只探测 (eta, delta) 里的 **eta** 方向（对 delta 免疫）；")
P("      · delta（mod 2*pi/3）是**第二个**独立不变量 —— 第 30 轮实测 delta ~ 2/9 正是在测它；")
P("      · 因此「未打开」的准确含义 = SRE 给的是**多重集**（无序三元组，2 参数），")
P("        而非**有序三元组**（还要多出 1 个离散的 Z3 选择，见 PART D）。")
P()
P("C4  ⚠ 一条必须修正的过度简化：")
P("      「SRE 的不变量只有 Q 一个」是**错的**。Q 只是 eta 方向的坐标；")
P("      delta 方向上有独立信息（多重集本身依赖 delta）。二者合起来才是完整的不变量。")
OUT["C"] = {"Q_delta_independent": tabC1, "R_delta_dependent": tabC2,
            "invariant_moduli_dim": 2}


# ==================================================================================
# PART D —— 「打开」= 给多重集一个原点：Z3（3 重）规范
# ==================================================================================
head("PART D  「打开」= 给多重集一个原点（DFT 相位约定）：Z3（3 重）规范自由度")

P("D0  什么叫「打开」？把振幅的**多重集** {a_0,a_1,a_2} 写成**有序三元组** (a_0,a_1,a_2)，")
P("    等价于给特征标 omega^k 选一个**原点**（= 给「第一代」命名）。")
P()
P("D1  实测：原点有 3 种选法（= 循环移位），它们给出**完全相同的物理**：")
a0 = amps(1.0 / math.sqrt(2), 2.0 / 9.0)
Q0, R0 = invs(a0)
P("      基准： a = %-34s  Q = %.12f   R = %.12f"
  % (np.array2string(np.array(a0), precision=6), Q0, R0))
tabD = [{"shift": 0, "Q": Q0, "R": R0, "dQ": 0.0, "dR": 0.0}]
for r in (1, 2):
    ar = a0[r:] + a0[:r]
    Q1, R1 = invs(ar)
    tabD.append({"shift": r, "Q": Q1, "R": R1, "dQ": abs(Q1 - Q0), "dR": abs(R1 - R0)})
    P("      移位%d：a = %-34s  Q = %.12f   R = %.12f   (|dQ|,|dR|) = (%.1e, %.1e)"
      % (r, np.array2string(np.array(ar), precision=6), Q1, R1, abs(Q1 - Q0), abs(R1 - R0)))
P()
P("      ⇒ 3 个代表元给出**完全相同的不变量** ⇒ 它们是同一个等变类的 3 个代表元。")
P()
P("D2  ⇒ 「打开」**不改变任何 SRE 可观测量**；它只决定「哪一代叫第一代」。")
P("      这是**规范**（冗余），不是信息 —— 与「挠子无原点」严格对应。")
P()
P("D3  ⚠ 必须区分两个层次的「打开」（不可混）：")
P("      (i)  规范层（本节）：选原点 = Z3 标号 —— 不变量不变（冗余）；")
P("      (ii) 物理层（第 30 轮 PART C）：闭态 -> 开态（断一条环边）——")
P("           |Aut| 36 -> 4、阶 3 元 8 -> 0，这是**真实**破缺 Z3 -> Z2，改变可及不变量。")
P("      ⇒ 用户命题里的「没有打开」指的是 **(i)**：循环保持在规范未定的状态。")
OUT["D"] = {"representatives": tabD,
            "note": "opening = choosing a DFT origin = Z3 gauge; invariants unchanged"}


# ==================================================================================
# PART E —— Koide：Q = 1/3 + (2/3)eta^2；Q=2/3 <=> eta^2 = 1/2
# ==================================================================================
head("PART E  Koide 定理：Q = 1/3 + (2/3)eta^2，Q = 2/3 <=> eta^2 = 1/2（真实轻子复算）")

P("E0  解析：sum_k cos(.) = 0、sum_k cos^2(.) = 3/2 ⇒ sum a = 3、sum a^2 = 3 + 6*eta^2")
P("    ⇒ Q = sum a^2/(sum a)^2 = (3 + 6*eta^2)/9 = 1/3 + (2/3)*eta^2 —— **与 delta 无关**")
P("    ⇒ Q = 2/3  <=>  eta^2 = 1/2  <=>  |c1|/c0 = 1/(2*sqrt2)  <=>  与 (1,1,1) 夹角 45 度")
P()
P("E1  真实带电轻子（PDG 质量）：")
tabE = []
for nm, m in (("m_tau = 1776.86（归档）", [0.51099895069, 105.6583755, 1776.86]),
              ("m_tau = 1776.93（2026 PDG）", [0.51099895069, 105.6583755, 1776.93])):
    aa = [math.sqrt(x) for x in m]
    Q = Q_of(aa)
    eta2 = (3.0 * Q - 1.0) / 2.0
    tabE.append({"case": nm, "Q": Q, "eta2": eta2, "dev": Q - 2.0 / 3.0})
    P("      %-30s Q = %.9f   eta^2 = %.9f   偏差 vs 2/3 = %+.3e" % (nm, Q, eta2, Q - 2.0 / 3.0))
P()
P("      ⇒ eta^2 = 1/2 在真实数据上成立到 ~%.1e。" % abs(tabE[1]["eta2"] - 0.5))
P("      ⚠ D1 纪律：1/2、1/3、2/3 全是小分母有理数 ⇒ 单独无判别力；")
P("        本定理的价值在**结构性**（Q 对 delta 免疫 = 规范不变），不在数值命中。")
OUT["E"] = {"cases": tabE,
            "theorem": "Q = 1/3 + (2/3)eta^2, independent of delta; Q=2/3 <=> eta^2=1/2"}


# ==================================================================================
# PART F —— 结构总结与对照
# ==================================================================================
head("PART F  结构总结与与既有结果的对照")

P("F0  三层结构（这就是「准确的数学描述」）：")
P("      ┌ 对象层   质量算子 = 三环挠子上的 Z3-等变算子 = **循环矩阵**      [SRE 内]")
P("      ├ 不变量层 等变类 = 振幅多重集 = (eta, delta mod 2pi/3)，**2 维**；  [SRE 内]")
P("      │          Q = 1/3+(2/3)eta^2 只占其中 eta 方向（对 delta 免疫）")
P("      └ 打开层   选 DFT 原点 ⇒ 有序三代 (a_0,a_1,a_2)；**Z3（3 重）规范**  [冗余，非信息]")
P("      外部输入：尺度 c0（= 绝对质量 / 能标）—— 唯一真正「SRE 外」的东西。")
P()
P("F1  与项目既有不变量的对照（全都是「对什么免疫」的类型学）：")
P("      %-20s %-34s %-16s" % ("量", "不变性（对什么免疫）", "所在层"))
for nm, inv, typ in (("rho（谱半径）", "断环（18 次断开极差 ~1e-15）", "谱层"),
                     ("Pi1 = lambda2/rho", "图同构（Aut）", "谱层"),
                     ("Q（Koide）", "Z3 原点（delta 的三重置换）", "挠子/映射层"),
                     ("eta^2", "Z3 原点", "挠子层"),
                     ("绝对质量 c0", "—（不免疫任何东西）", "SRE 外")):
    P("      %-20s %-34s %-16s" % (nm, inv, typ))
P()
P("F2  一句话总裁决：")
P("      质量 = 「Z3 上的循环」的**不变量**；")
P("      数学载体 = **循环矩阵（circulant）**；")
P("      「没有打开」= 不做带原点的谱分解 ⇒ 只输出等变类（多重集）；")
P("      「打开」= 选原点（DFT 约定）⇒ 有序三代 —— 这是**规范**，不是新信息。")
P()
P("F3  本轮最重要的一条认识（**修正性质**）：")
P("      「三点共一条余弦」的自由度计数：3 个未知 (c0, |c1|, theta) 对 3 个数据 ⇒ **恒可解**。")
P("      ⇒ 循环结构提供的是**语言**，不是**约束**；SRE 对质量的全部内容收敛到**一个数**")
P("        eta = |c1|/c0（Koide 的内容 = eta = 1/sqrt2）。")
P("      ⇒ 这也回过头解释第 31 轮：为什么「算不出绝对质量」—— 那个数是尺度 c0，属 SRE 外。")
P()
P("F4  诚实边界：")
P("      1. 本报告为 SRE 模型内部 / 线性代数与群论层面的**自洽表述**，不是数值预言。")
P("      2. 「取 a = sqrt(m) 而非 m」这一层是 Koide 的**经验内容**，")
P("         等价于「质量算子的平方根是 Z3-等变的」——这是一个可检验的结构假设，未证。")
P("      3. PART B2 的「实对称 ⇒ 2+1」与「开态」的呼应只是**观察**，未证同一机制。")
P("      4. 尺度 c0（绝对质量）仍须外部输入 —— 与第 30/31 轮的 G12 结论一致。")
OUT["F"] = {"layers": ["object: circulant (Z3-equivariant operator)",
                       "invariant: (eta, delta mod 2pi/3), 2-dim",
                       "open: DFT origin, Z3 gauge"],
            "honest_boundary": ["model-internal self-consistency only",
                                "the cos-form is a FREE reparametrization valid for ANY triple (not a constraint)",
                                "sqrt(m) vs m is empirical (Koide)",
                                "real-symmetric<->open-state link is an observation, not proved",
                                "absolute scale c0 requires external input"]}

with open("_sre_cyclic_mass_formalism.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P()
P("已写出 _sre_cyclic_mass_formalism.json")
