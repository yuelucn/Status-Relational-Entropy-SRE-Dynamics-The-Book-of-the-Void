# -*- coding: utf-8 -*-
"""
_sre_light_source_universality.py —— 第 36 轮
=================================================================
问题：能否用同一套 SRE 描述，同时覆盖
      (a) **化学能 → 光/电磁波**（分子/电子层级的重组释放辐射），
      (b) **核 → 光/电磁波**（核能级跃迁放 γ）？

既有口径（引原文，不转述）
--------------------------
· 电子论文 §3.1【公理 I（残余性）】：Psi_light(phi,w) = ker(d_mutual(A_t, B_t'))
  —— 「光不是独立的物质本体 …… 光体现为联合执行链因果交集处的互不湮灭拓扑残余」。
· 电子拓扑 §2.2：加权 Möbius 阶梯 M_n，对合 P = S^{n/2}，P² = I，P v_k = (-1)^k v_k；
  **k 偶 = 电子扇区（软模），k 奇 = 光子扇区**（Fork A §3.5）。
· 电子拓扑 §3.4：delta 指纹 mu_k(1+delta) - mu_k(1) = 2·delta (k 奇) / 0 (k 偶)。
· 核子论文 §9.3：**rho 是过渡的严格不变量**（闭↔开、开哪条环边，极差 ~1e-15）。
· _sre_boson_transition.py PART D：Axiom I + 「rho 是过渡不变量」⇒
  **纯过渡无质量 ⇒ 光子唯一**（零参数正面计数，已登记）。

本脚本做的是**结构实测**：把「源的不可见性」与「源只注入一个数」变成可复算的读数。
输出：_sre_light_source_universality.log / .json
"""
import sys
import math
import cmath
import json

import numpy as np
import networkx as nx

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

OUT = {}
W3 = cmath.exp(2j * math.pi / 3)


def P(*a):
    print(*a, flush=True)


def head(t):
    P()
    P("=" * 86)
    P(t)
    P("=" * 86)


# ------------------------------------------------------------------
# 加权 Möbius 阶梯 M_n（n 偶）：环边权 c，横档（holonomy）边权 w
#   V = n, E = n + n/2 = 3n/2, beta1 = n/2 + 1
#   拉普拉斯 L = D - A，D_ii = 2c + w（两个环邻居 + 一个对合伙伴）
#   ⇒ 闭式谱 mu_k = 2c(1 - cos(2*pi*k/n)) + w(1 - (-1)^k)     [本脚本推导并实测]
#     偶 k: mu = 2c(1-cos)          （电子扇区）
#     奇 k: mu = 2c(1-cos) + 2w     （光子扇区）
# ------------------------------------------------------------------
def mobius_weighted(n, c=1.0, w=1.0):
    assert n % 2 == 0, "n must be even"
    A = np.zeros((n, n))
    for i in range(n):
        j = (i + 1) % n
        A[i, j] += c
        A[j, i] += c
    for i in range(n // 2):          # 对合伙伴：恰好一个
        A[i, i + n // 2] += w
        A[i + n // 2, i] += w
    L = np.diag(A.sum(1)) - A
    return A, L


def closed_mu(n, c, w):
    k = np.arange(n)
    return 2.0 * c * (1.0 - np.cos(2.0 * np.pi * k / n)) + w * (1.0 - ((-1.0) ** k))


def involution(n):
    Pm = np.zeros((n, n))
    for i in range(n):
        Pm[i, (i + n // 2) % n] = 1.0
    return Pm


# 质量侧骨架 Y3（第 29/30/32/35 轮同一构造）
def Y3(open_ring=None):
    G = nx.Graph()
    for i in range(3):
        G.add_node("c%d" % i)
        for j in range(3):
            G.add_node("L%d%d" % (i, j))
            G.add_edge("c%d" % i, "L%d%d" % (i, j))
    for j in range(3):
        G.add_edge("L0%d" % j, "L1%d" % j)
        G.add_edge("L1%d" % j, "L2%d" % j)
        G.add_edge("L2%d" % j, "L0%d" % j)
    if open_ring is not None:
        G.remove_edge("L0%d" % open_ring, "L1%d" % open_ring)
    return G


# ==================================================================
head("PART A  光载体：一个整数决定一切（0 个连续自由参数）")
# ==================================================================
P("A1. 闭式谱 mu_k = 2c(1 - cos(2*pi*k/n)) + w(1 - (-1)^k)  与数值谱对照")
P("    （把谱写成这个形式是**本轮的关键一步**：它把「源通道」分成了两项 —— 先看数值是否对得上）")
P()
P("      n    数值谱 vs 闭式谱 最大偏差     mu_0(恒零?)      奇偶两支")
P("    " + "-" * 78)
rowsA = []
for n in (6, 8, 10, 20, 30, 60):
    A, L = mobius_weighted(n, 1.0, 1.0)
    num = np.sort(np.linalg.eigvalsh(L))
    cl = np.sort(closed_mu(n, 1.0, 1.0))
    dev = float(np.abs(num - cl).max())
    ev = closed_mu(n, 1.0, 1.0)
    even = sorted(set(np.round(ev[0::2], 12).tolist()))
    odd = sorted(set(np.round(ev[1::2], 12).tolist()))
    P("    %4d      %.3e                  %.1e        |偶|=%2d  |奇|=%2d"
      % (n, dev, abs(closed_mu(n, 1.0, 1.0)[0]), len(ev[0::2]), len(ev[1::2])))
    rowsA.append(dict(n=n, dev=dev, mu0=float(closed_mu(n, 1.0, 1.0)[0])))
OUT["A_closed_form"] = rowsA

P()
P("A2. 对合 P = S^{n/2}（n=60）—— 扇区结构的**唯一**来源，只由 n 决定")
n, c, w = 60, 1.0, 1.0
A, L = mobius_weighted(n, c, w)
Pm = involution(n)
Ppm = 0.5 * (np.eye(n) + Pm)
Pmm = 0.5 * (np.eye(n) - Pm)
chk = {
    "P^2 = I": bool(np.allclose(Pm @ Pm, np.eye(n))),
    "P != I": bool(not np.allclose(Pm, np.eye(n))),
    "P in Aut (P A P^T = A)": bool(np.allclose(Pm @ A @ Pm.T, A)),
    "[P, L] = 0（可同时对角化）": bool(np.allclose(Pm @ L, L @ Pm)),
    "spec(P) 恰为 {+1, -1}": bool(np.allclose(sorted(set(np.round(np.linalg.eigvalsh(Pm), 9))), [-1.0, 1.0])),
    "tr(P) = 0（两支等重）": bool(abs(np.trace(Pm)) < 1e-12),
    "P_+ 幂等": bool(np.allclose(Ppm @ Ppm, Ppm)),
    "P_- 幂等": bool(np.allclose(Pmm @ Pmm, Pmm)),
    "P_+ P_- = 0（正交）": bool(np.allclose(Ppm @ Pmm, 0)),
    "P_+ + P_- = I": bool(np.allclose(Ppm + Pmm, np.eye(n))),
    "rank(P_+) = rank(P_-) = n/2": bool(abs(np.trace(Ppm) - n / 2) < 1e-9 and abs(np.trace(Pmm) - n / 2) < 1e-9),
}
for k, v in chk.items():
    P("      %-34s : %s" % (k, v))
OUT["A_involution_check"] = {k: bool(v) for k, v in chk.items()}

P()
P("A3. 参数计数（这是本轮要的答案里最硬的一条）")
P()
P("    载体                 决定它的输入            连续自由参数")
P("    " + "-" * 66)
P("    光：对称性载体 P       一个整数 n               0（谱被锁成 {+1,-1}）")
P("    光：谱标度 (c, w)      ——                      2，但只有 w 是「光专属」")
P("    质量：算子 A           Re c0, Re c1, Im c1      3（不变量 2：c0 与 |c1|）")
P()
P("    ⇒ 光载体 P **没有位置可以放源**：它由 n 完全决定，不含任何连续输入。")
P("      （对照：质量算子 A 的自由度 (c0, |c1|) 才是「账本」的落点。）")

# ==================================================================
head("PART B  源只注入一个数：唯一通道 与 「谱形不变」")
# ==================================================================
P("B1. 先把谱的两项分清楚（本轮的解析核心）")
P("        mu_k = 2c(1 - cos(2*pi*k/n))  +  w(1 - (-1)^k)")
P("               ^^^^^^^^^^^^^^^^^^^^     ^^^^^^^^^^^^^")
P("               扇区盲项（c 通道）        奇扇区常数项（w 通道）")
P()
P("    · c 通道（环向权）：**两个扇区一视同仁**，且逐模位移 ∝ (1-cos(2πk/n)) —— 非均匀；")
P("    · w 通道（横档/holonomy）：**只在奇扇区**，且是**纯常数平移 2w** —— 无形状。")
P()

P("B2. w 通道实测：平移是否严格均匀？（对照项目 §3.4 的 delta 指纹）")
P("      delta    奇扇区 Δmu 极差     奇扇区 Δmu/2δ 最小~最大        偶扇区 Δmu 极差")
P("    " + "-" * 84)
rowsB = []
for delta in (1e-3, 1e-2, 1e-1, 5e-1):
    ev0 = closed_mu(n, 1.0, 1.0)
    ev1 = closed_mu(n, 1.0, 1.0 + delta)
    d = ev1 - ev0
    do, de = d[1::2], d[0::2]
    spread_o = float(do.max() - do.min())
    spread_e = float(de.max() - de.min())
    P("    %-8.3f  %.3e             %.9f ~ %.9f    %.3e"
      % (delta, spread_o, do.min() / (2 * delta), do.max() / (2 * delta), spread_e))
    rowsB.append(dict(delta=delta, spread_odd=spread_o, spread_even=spread_e,
                      ratio_min=float(do.min() / (2 * delta)), ratio_max=float(do.max() / (2 * delta))))
OUT["B_w_channel"] = rowsB
P()
P("    ⇒ 奇扇区**全部 n/2 个模**平移量严格相同（极差 ~1e-16 = 机器精度）；偶扇区恒不动。")
P("      这就是「源在光侧只留下一个数」的直接实测：**源进不来形状，只进得来大小。**")

P()
P("B3. 「谱形不变」的直接检验：减去平移量后与基准逐位相同")
for delta in (1e-2, 1e-1):
    ev0 = closed_mu(n, 1.0, 1.0)
    ev1 = closed_mu(n, 1.0, 1.0 + delta)
    odd0 = np.sort(ev0[1::2])
    odd1 = np.sort(ev1[1::2])
    P("      delta=%.2f : max| (奇谱 - 2δ) - 奇谱基准 | = %.3e" % (delta, np.abs(odd1 - 2 * delta - odd0).max()))
P()
P("    ⇒ 光的谱形**逐位不变**。换言之：**在光侧，源不可见，只可闻其声（振幅）。**")

P()
P("B4. 对照实验（反例）：环向通道 c 就不是这样")
P("      u (c=1+u)   奇扇区位移类型            偶扇区位移类型        是否只在奇扇区？")
P("    " + "-" * 84)
for u in (1e-2, 1e-1):
    ev0 = closed_mu(n, 1.0, 1.0)
    evu = closed_mu(n, 1.0 + u, 1.0)
    d = evu - ev0
    do, de = d[1::2], d[0::2]
    P("    %-10.3f  非均匀（极差 %.2e）     非均匀（极差 %.2e）  否（两扇区同时动）"
      % (u, do.max() - do.min(), de.max() - de.min()))
P()
P("    ⇒ 判据：**「只在奇扇区」+「均匀」两条同时成立 ⇒ 通道唯一 = w（横档 / holonomy）。**")
P("      （c 通道要么两扇区同动，要么给出非均匀位移 —— 两条都过不了。）")

# ==================================================================
head("PART C  无质量性：光载体没有加性标度（迹为零）")
# ==================================================================
P("C1. 光载体 P：|本征值| 恒 = 1，谱均值 = tr(P)/n = 0")
P()
P("      n     |spec(P)| 取值        mean(spec P)        mu_0(光载体谱的零模)")
P("    " + "-" * 72)
rowsC = []
for nn in (6, 8, 20, 60):
    Pn = involution(nn)
    evp = np.linalg.eigvalsh(Pn)
    P("    %4d      {%s}              %.1e              %.1e"
      % (nn, ",".join("%.0f" % x for x in sorted(set(np.round(evp, 9)))), float(evp.mean()),
         float(closed_mu(nn, 1.0, 1.0)[0])))
    rowsC.append(dict(n=nn, mean_specP=float(evp.mean()), mu0=float(closed_mu(nn, 1.0, 1.0)[0]),
                      absvals=sorted(set(np.round(np.abs(evp), 9).tolist()))))
OUT["C_light_no_scale"] = rowsC
P()
P("    ⇒ 光载体谱**恒有零模**（mu_0 = 0）、且 |本征值| ≡ 1 ⇒ **没有加性自由常数 c0**。")

P()
P("C2. 对照：质量载体 A = c0*I + c1*S + conj(c1)*S^2，其**谱均值恰为 c0**（c0 是自由参数）")
P()
W = W3
S = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]], dtype=complex)


def mass_spectrum(c0, c1):
    A = c0 * np.eye(3, dtype=complex) + c1 * S + np.conj(c1) * (S @ S)
    return np.sort(np.linalg.eigvalsh(A).real)


P("      c0     |c1|    theta(deg)   谱                                         谱均值")
P("    " + "-" * 88)
rowsC2 = []
for c0, a, th in ((0.0, 0.3, 40.0), (0.5, 0.3, 40.0), (1.0, 0.3, 40.0), (2.0, 0.3, 40.0), (1.0, 0.0, 0.0)):
    sp = mass_spectrum(c0, a * cmath.exp(1j * math.radians(th)))
    P("    %-6.2f %-7.2f %-12.1f  (%s)   %.9f"
      % (c0, a, th, ", ".join("%.9f" % x for x in sp), sp.mean()))
    rowsC2.append(dict(c0=c0, c1_abs=a, theta=th, spec=sp.tolist(), mean=float(sp.mean())))
OUT["C_mass_scale"] = rowsC2
P()
P("    ⇒ 质量载体谱均值**精确等于 c0**（自由参数）；光载体均值**精确为 0**（被锁）。")
P()
P("C3. 结论（与既有条目互证，注意这是**同一结论的两种说法**，非两条独立证据）：")
P("    · 本轮 C1-C2：光载体无加性标度，质量载体有 ⇒ c0 就是那个「须外部输入」的维。")
P("    · 既有 _sre_boson_transition.py PART D：『rho 是过渡不变量 ⇒ 纯过渡无质量 ⇒ 光子唯一』。")
P("    · 第 32/33 轮：绝对标度 c0 ∈ SRE 外（SRE 只给比值）。")
P("    三者指向同一位置：**质量需要一个 SRE 给不出的标度；光不需要。**")

# ==================================================================
head("PART D  能量在账本里、不在谱里 —— 这才是「化学与核同机制」的根据")
# ==================================================================
P("D1. Y3 骨架 闭 ↔ 开（断一条环边）的签名向量实测")
P()


def lap_stats(G):
    """项目口径：rho = **拉普拉斯**最大特征值；lam2 = 拉普拉斯次小特征值。"""
    G = nx.convert_node_labels_to_integers(G)
    A = nx.to_numpy_array(G).astype(float)
    L = np.diag(A.sum(1)) - A
    ev = np.sort(np.linalg.eigvalsh(L))
    return dict(V=G.number_of_nodes(), E=G.number_of_edges(),
                b1=G.number_of_edges() - G.number_of_nodes() + nx.number_connected_components(G),
                rho=float(ev[-1]), lam2=float(ev[1]))


sc, so = lap_stats(Y3(None)), lap_stats(Y3(0))
P("      量       闭态            开态            差             归类")
P("    " + "-" * 72)
for key, label, kind in (("V", "V", "账本"), ("E", "E", "账本"), ("b1", "beta1", "账本"),
                         ("rho", "rho", "谱"), ("lam2", "lambda2", "谱")):
    dv = so[key] - sc[key]
    P("    %-6s  %-14s  %-14s  %-14s  %s"
      % (key, "%.9f" % sc[key] if key in ("rho", "lam2") else "%d" % sc[key],
         "%.9f" % so[key] if key in ("rho", "lam2") else "%d" % so[key],
         "%.3e" % dv if key in ("rho", "lam2") else "%+d" % dv, kind))
OUT["D_ledger"] = dict(closed=sc, open=so)
P()
P("    ⇒ **账本量动（E: -1, beta1: -1），谱量不动（rho, lambda2 极差 ~1e-16）。**")
P()
P("D1b. 稳健性：把**每一条边**逐条断开（共 18 条），分「环边 / 股边」两类看谱量是否不动")
G0 = Y3(None)
ring_e, spoke_e = [], []
for (u, v) in sorted(tuple(sorted(e)) for e in G0.edges()):
    if u.startswith("L") and v.startswith("L"):
        ring_e.append((u, v))
    else:
        spoke_e.append((u, v))
res = {}
for tag, elist in (("环边 (L-L)", ring_e), ("股边 (c-L)", spoke_e)):
    rho_s, lam_s = [], []
    for (u, v) in elist:
        Gx = G0.copy()
        Gx.remove_edge(u, v)
        if not nx.is_connected(Gx):
            continue
        st = lap_stats(Gx)
        rho_s.append(st["rho"])
        lam_s.append(st["lam2"])
    res[tag] = dict(n=len(rho_s), rho_spread=float(max(rho_s) - min(rho_s)),
                    lam2_spread=float(max(lam_s) - min(lam_s)),
                    lam2_min=float(min(lam_s)), lam2_max=float(max(lam_s)))
    P("      %-10s 断开 %d 条 :  rho 极差 = %.3e  |  lambda2 极差 = %.3e  (lambda2 ∈ [%.9f, %.9f])"
      % (tag, len(rho_s), res[tag]["rho_spread"], res[tag]["lam2_spread"],
         res[tag]["lam2_min"], res[tag]["lam2_max"]))
P("      基准（闭态）: rho = %.12f , lambda2 = %.12f" % (sc["rho"], sc["lam2"]))
OUT["D_robust"] = res
P()
P("      ⇒ **rho：两类边都不动（极差 ~1e-15）⇒ 全局严格不变量**（复现并加强项目 §4）。")
P("        **lambda2：在同一类边内严格不变（每类 9 条，极差 ~1e-15），但两类给出不同值**")
P("        （环边 1.000000000 vs 股边 0.527166091）——")
P("        这是本轮必须如实登记的**精化**：")
P("        **rho = 全局不变量；lambda2 = 轨道级不变量（只依赖边的 Aut-轨道，不依赖具体哪条边）。**")
P("        故 λ₂ 的不变性**不可**写成「对断哪条边都免疫」。")
P()
P("D2. 判读：这是「化学能」与「核能」能被同一套话描述的真正原因 ——")
P("    · **能量**（释出多少）住在**账本**里（差值 E/beta1/T）；")
P("    · **光的载体**住在**谱不变量**里（rho / lambda2 / 扇区结构）；")
P("    · 二者**正交** ⇒ 源（哪一层发生过渡）**只改账本，不改载体**。")
P("    化学：过渡发生在 L1/L2（电子-分子层）；核：过渡发生在 L3（核层）。载体同一个。")
P()
P("D3. ⚠ 禁止挪用（同名不同义，本轮新增一条）")
P("    项目既有「三层跨度 13.40 量级」（L1 -2.30 / L2 -0.09 / L3 +11.10）是**衰变率对环境**")
P("    的**敏感度**跨度，**不是光子能量跨度**。两者物理量不同 ⇒ **禁互相引用**。")
P()
P("D4. 外部输入（标注为**外部**，非本轮实测、非 SRE 输出）：")
P("    · 原子/分子发光的特征能量量级 ~ 1–10 eV（化学键能同量级）；")
P("    · 核 gamma 的特征能量量级 ~ 0.1–10 MeV。")
P("    ⇒ 比值 ~1e5–1e6。**这是源的账本量级，SRE 侧没有对应读数**（同 c0 缺口）。")

# ==================================================================
head("PART E  统一命题与可证伪判据")
# ==================================================================
P("E1. 统一命题（本轮结论）")
P()
P("    一次发光 = 一次**闭→开过渡**。其中：")
P("      (i)  过渡的**账本差**承载能量（E/beta1/T 各 -1）—— 量纲化须外部输入；")
P("      (ii) 过渡的**谱不变量**承载光的载体（rho / lambda2 / P 的奇扇区）；")
P("      (iii) 源（化学的电子重组 / 核的能级跃迁）**只能**通过 w 通道注入一个标量，")
P("            因为「只在奇扇区 + 均匀平移」这一对性质把通道唯一地钉死在 w 上（PART B）。")
P()
P("E2. 由此得到的可证伪判据（零参数）")
P("      J1. **载体同一**：化学来源与核来源的光，在 SRE 载体上必须结构同一，")
P("          只允许在 w 的大小（振幅）上不同。若发现任一结构差 ⇒ 命题失败。")
P("      J2. **形状不变**：源强度的变化只能平移光子扇区，不得改变其谱形")
P("          （PART B3 实测：谱形逐位不变，残差 ~1e-16）。")
P("      J3. **不越界**：不得把光的载体量（rho/lambda2）当作能量读数，反之亦然（PART D2）。")
P()
P("E3. 「看起来不同」但不属于载体的量（全部归 L2 映射 / 源账本）")
P("      能量、偏振态、角分布、相干时间、谱线宽度 —— 都是**源与环境的账本**，")
P("      不是载体属性。把它们混进载体，就是第 32 轮警告过的「打开层越界」。")

# ==================================================================
head("PART F  诚实边界")
# ==================================================================
P("F1. 本轮全部读数为**模型内结构实测**（闭式谱 + 矩阵构造双重核对），无任何实验数据拟合。")
P("F2. 「化学光与核光同一载体」是**结构同源**（同一 P、同一奇扇区），")
P("    不是两套物理机制的等价性证明；也未给出任何能量数值预言。")
P("F3. 闭式谱 mu_k = 2c(1-cos) + w(1-(-1)^k) 是本人由加权 Möbius 阶梯**推导并数值核对**的；")
P("    它与项目既有闭式（第 35 轮引 code/_sre_downward_scope.py：mu_k=(2+w)-2cos-w(-1)^k）")
P("    在 c=1 时等价 —— 本轮只是把 c 显式分离出来，以便比较「通道」。")
P("F4. D4 的 eV / MeV 是**外部参考量级**，非本轮实测、非 SRE 输出，仅用于说明「区别在账本」。")
P("F5. PART B4 的「通道唯一」限定在**保 P 对称性的线性扰动族**内；非线性/破坏对称的源")
P("    未在本轮范围内，须另立一轮。")
P("F6. 「光 = 残余」是项目公理（Axiom I），本轮沿用它，未重新论证。")
P("F7. **本轮对既有结论做了一处精化（不是推翻）**：")
P("    项目 §3/§4 记「开态断一环边 ⇒ rho、lambda2 不变」。本轮逐边实测 18 条发现：")
P("      · rho  —— 全局严格不变量（18/18，极差 ~1e-15）；")
P("      · lambda2 —— **轨道级**不变量：环边轨道给 1.000000000、股边轨道给 0.527166091，")
P("        同轨道内 9/9 严格相同（极差 ~1e-15）。")
P("    ⇒ 原表述在「断环边」这一语境下正确；但若推广到任意边则不成立。")
P("      本轮不改既有文档，仅登记此精化，并按项目纪律**双写**（本脚本 + 记忆）。")

# ------------------------------------------------------------------
with open("_sre_light_source_universality.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=1, default=str)
P()
P("saved _sre_light_source_universality.json")
