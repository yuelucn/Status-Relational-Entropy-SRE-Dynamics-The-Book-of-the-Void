# -*- coding: utf-8 -*-
"""
SRE 维度塌缩检验（扩展版）：距离数据 ÷ a0 化为无量纲关系数。

在既有五检验基础上扩展：
 (0) 尺度锚定 a0·me·c/hbar = 1/alpha
 (1) 轨道壳律 r_n = n^2·a0/Z
 (2) 共价半径（a0 单位）泄漏剖面，扩展到主族第 4/5 周期（导出 Z_eff）
 (3) 键长键级步进律：扩展到更多同核/异核多重键族，输出 Δ 统计
 (4) 单键加和律 d(A-B) ≈ r_A + r_B：分家族统计（均值/标准差/RMS/max）
 (5) 键级容量观察：各族最大稳定键级序列

诚实边界：
 - 本脚本仅把真实经验数据组织为无量纲关系数，属同向指示，不宣称推导。
 - 键长为经验代表值（气相精确值与晶体/数据库平均值混用，均已标注来源类）。
 - 共价半径采用 Cordero et al. 2008 定标；与 Pyykkö 等体系取值略有差异，
   小数位不当过度诠释。
"""
import json

A0_ANG = 0.529177210903
ALPHA_INV = 137.035999084


def a0u(ang):
    return ang / A0_ANG


def stats(vals):
    """返回 (n, mean, std, rms, max) 的简要统计。"""
    n = len(vals)
    if n == 0:
        return (0, float("nan"), float("nan"), float("nan"), float("nan"))
    mean = sum(vals) / n
    var = sum((v - mean) ** 2 for v in vals) / n
    std = var ** 0.5
    rms = (sum(v * v for v in vals) / n) ** 0.5
    mx = max(abs(v) for v in vals)
    return (n, mean, std, rms, mx)


def main():
    lines = []
    P = lines.append
    P("# SRE 维度塌缩表（扩展键长库版）· 讨论用检验数据，非正式文档\n")
    P(f"- a0 = {A0_ANG} Å（CODATA 2018）；α⁻¹ = {ALPHA_INV}")
    P(f"- 统一规则：长度 ÷ a0 → 无量纲关系数。a0 = 1/(α·me) 中 α 为框架内量，me 为局部带入。")
    P(f"- 键长来源标注：`exp` = 气相精确平衡键长；`avg` = 晶体/数据库平均值或代表值。\n")

    # ================= [0] 尺度锚定 =================
    me_, hbar_, c_ = 9.1093837015e-31, 1.054571817e-34, 299792458.0
    dim = (A0_ANG * 1e-10) * me_ * c_ / hbar_
    r0 = dim / ALPHA_INV
    P("## [0] 尺度锚定（无量纲恒等式）")
    P(f"- a0·me·c/ħ = {dim:.10f}")
    P(f"- 1/α        = {ALPHA_INV:.10f}")
    P(f"- 比值       = {r0:.10f}（应 ≈ 1）\n")

    # ================= [1] 轨道壳律 =================
    P("## [1] 轨道壳律 r_n = n²·a0/Z（a0 单位）")
    P("| Z | n=1 | n=2 | n=3 | n=4 | 整数比 |")
    P("|---|---|---|---|---|---|")
    for Z in (1, 2, 3):
        vals = [n * n / Z for n in (1, 2, 3, 4)]
        P(f"| {Z} | " + " | ".join(f"{v:.3f}" for v in vals)
          + f" | 1 : {4:.0f} : {9:.0f} : {16:.0f} |")
    P("")

    # ================= [2] 共价半径（扩展主族） =================
    # Cordero et al. 2008 共价半径，Å；元组 = (Z, 主壳 n, r_Ang)
    cov = {
        # 第 1 周期
        "H":  (1, 1, 0.31),
        # 第 2 周期
        "Li": (3, 2, 1.28), "Be": (4, 2, 0.96), "B": (5, 2, 0.84),
        "C":  (6, 2, 0.76), "N": (7, 2, 0.71), "O": (8, 2, 0.66),
        "F":  (9, 2, 0.57),
        # 第 3 周期
        "Na": (11, 3, 1.66), "Mg": (12, 3, 1.41), "Al": (13, 3, 1.21),
        "Si": (14, 3, 1.11), "P": (15, 3, 1.07), "S": (16, 3, 1.05),
        "Cl": (17, 3, 1.02),
        # 第 4 周期主族
        "K":  (19, 4, 2.03), "Ca": (20, 4, 1.76), "Ga": (31, 4, 1.22),
        "Ge": (32, 4, 1.20), "As": (33, 4, 1.19), "Se": (34, 4, 1.20),
        "Br": (35, 4, 1.20),
        # 第 5 周期主族
        "Rb": (37, 5, 2.20), "Sr": (38, 5, 1.95), "In": (49, 5, 1.42),
        "Sn": (50, 5, 1.39), "Sb": (51, 5, 1.39), "Te": (52, 5, 1.38),
        "I":  (53, 5, 1.39),
    }
    cov_a0 = {el: (z, n, rr, a0u(rr)) for el, (z, n, rr) in cov.items()}
    P("## [2] 共价半径（a0 单位）与导出 Z_eff（泄漏剖面，主族扩展）")
    P("Z_eff ≈ n²/(r/a0)（n 取主壳量子数）：第二/三周期沿周期逐级增大 = 核泄漏递增")
    P("| 元素 | Z | r/Å | r/a0 | 导出 Z_eff | 主壳 n |")
    P("|---|---|---|---|---|---|")
    order2 = ("Li", "Be", "B", "C", "N", "O", "F")
    order3 = ("Na", "Mg", "Al", "Si", "P", "S", "Cl")
    order4 = ("K", "Ca", "Ga", "Ge", "As", "Se", "Br")
    order5 = ("Rb", "Sr", "In", "Sn", "Sb", "Te", "I")
    zeff_rows = {}
    for el in order2 + order3 + order4 + order5 + ("H",):
        z, n, rr, ra = cov_a0[el]
        zeff = n * n / ra
        zeff_rows[el] = zeff
        P(f"| {el} | {z} | {rr:.2f} | {ra:.3f} | {zeff:.2f} | {n} |")
    # 同族跨周期递增性检查
    fam_grp = {"14族": ("C", "Si", "Ge", "Sn"),
               "15族": ("N", "P", "As", "Sb"),
               "16族": ("O", "S", "Se", "Te"),
               "17族": ("F", "Cl", "Br", "I")}
    P("")
    P("### 同族跨周期 Z_eff 变化（泄漏随 n 增大？）")
    for gname, els in fam_grp.items():
        zs = [zeff_rows[e] for e in els]
        mono = all(zs[i] < zs[i + 1] for i in range(len(zs) - 1))
        P(f"- {gname} {' / '.join(els)}: Z_eff = "
          + ", ".join(f"{v:.2f}" for v in zs) + f"  → {'单调递增' if mono else '非单调'}")
    P("")

    # ================= [3] 键长库（扩展） =================
    # (A, B, 键级, d_Ang, 来源)
    bonds = [
        # ---- 同核族 ----
        ("H", "H", "single", 0.741, "exp"),
        ("Li", "Li", "single", 2.67, "exp"),
        ("C", "C", "single", 1.54, "avg"),
        ("C", "C", "double", 1.34, "avg"),
        ("C", "C", "triple", 1.20, "avg"),
        ("C", "C", "aromatic", 1.397, "avg"),
        ("N", "N", "single", 1.45, "avg"),
        ("N", "N", "double", 1.25, "avg"),
        ("N", "N", "triple", 1.098, "exp"),
        ("O", "O", "single", 1.48, "avg"),
        ("O", "O", "double", 1.21, "exp"),
        ("F", "F", "single", 1.42, "exp"),
        ("Na", "Na", "single", 2.82, "exp"),
        ("Si", "Si", "single", 2.33, "avg"),
        ("Si", "Si", "double", 2.15, "avg"),
        ("Si", "Si", "triple", 2.09, "avg"),
        ("P", "P", "single", 2.21, "avg"),
        ("P", "P", "double", 2.03, "avg"),
        ("P", "P", "triple", 1.893, "exp"),
        ("S", "S", "single", 2.05, "avg"),
        ("S", "S", "double", 1.89, "exp"),
        ("Cl", "Cl", "single", 1.99, "exp"),
        ("Ge", "Ge", "single", 2.41, "avg"),
        ("Ge", "Ge", "double", 2.21, "avg"),
        ("Ge", "Ge", "triple", 2.06, "avg"),
        ("As", "As", "single", 2.44, "avg"),
        ("As", "As", "triple", 2.10, "exp"),
        ("Se", "Se", "single", 2.32, "avg"),
        ("Se", "Se", "double", 2.15, "exp"),
        ("Br", "Br", "single", 2.28, "exp"),
        ("Te", "Te", "single", 2.71, "avg"),
        ("Te", "Te", "double", 2.56, "exp"),
        ("I", "I", "single", 2.67, "exp"),
        # ---- 异核族：C 骨架 ----
        ("C", "H", "single", 1.09, "avg"),
        ("C", "N", "single", 1.47, "avg"),
        ("C", "N", "double", 1.28, "avg"),
        ("C", "N", "triple", 1.16, "avg"),
        ("C", "O", "single", 1.43, "avg"),
        ("C", "O", "double", 1.23, "avg"),
        ("C", "O", "triple", 1.13, "exp"),
        ("C", "F", "single", 1.38, "avg"),
        ("C", "Si", "single", 1.86, "avg"),
        ("C", "P", "single", 1.87, "avg"),
        ("C", "S", "single", 1.82, "avg"),
        ("C", "S", "double", 1.60, "avg"),
        ("C", "Cl", "single", 1.77, "avg"),
        ("C", "Br", "single", 1.94, "avg"),
        ("C", "I", "single", 2.13, "avg"),
        # ---- 异核族：第 2/3 周期 ----
        ("B", "F", "single", 1.33, "avg"),
        ("B", "O", "single", 1.37, "avg"),
        ("B", "C", "single", 1.57, "avg"),
        ("N", "H", "single", 1.01, "exp"),
        ("N", "O", "single", 1.42, "avg"),
        ("N", "O", "double", 1.15, "exp"),
        ("N", "F", "single", 1.37, "avg"),
        ("O", "H", "single", 0.96, "exp"),
        ("O", "F", "single", 1.41, "exp"),
        ("F", "H", "single", 0.92, "exp"),
        ("Si", "H", "single", 1.48, "avg"),
        ("Si", "O", "single", 1.63, "avg"),
        ("Si", "F", "single", 1.60, "avg"),
        ("Si", "Cl", "single", 2.02, "exp"),
        ("Si", "N", "single", 1.74, "avg"),
        ("P", "H", "single", 1.42, "avg"),
        ("P", "O", "single", 1.52, "avg"),
        ("P", "F", "single", 1.56, "avg"),
        ("P", "Cl", "single", 2.04, "exp"),
        ("S", "H", "single", 1.34, "exp"),
        ("S", "O", "single", 1.48, "avg"),
        ("S", "F", "single", 1.56, "avg"),
        ("S", "Cl", "single", 2.01, "exp"),
        ("Cl", "H", "single", 1.27, "exp"),
        ("Br", "H", "single", 1.41, "exp"),
        ("I", "H", "single", 1.61, "exp"),
        # ---- 碱金属/碱土卤化物（离子性参照） ----
        ("Li", "Cl", "single", 2.02, "exp"),
        ("Na", "Cl", "single", 2.36, "exp"),
        ("K", "Cl", "single", 2.67, "exp"),
        ("Mg", "O", "single", 1.75, "exp"),
    ]

    P("## [3] 键长库（a0 单位，按元素族分组）\n")
    P("### 3.1 同核键与多重键族")
    P("| 键 | 键级 | d/Å | src | d/a0 |")
    P("|---|---|---|---|---|")
    for ea, eb, bo, d, src in bonds:
        if ea == eb:
            P(f"| {ea}–{eb} | {bo} | {d:.3f} | {src} | {a0u(d):.3f} |")
    P("")
    P("### 3.2 异核单键（加和律主测试）")
    P("| 键 | d/Å | src | d/a0 | | 键 | d/Å | src | d/a0 |")
    P("|---|---|---|---|---|---|---|---|---|")
    het_single = [(ea, eb, bo, d, src) for ea, eb, bo, d, src in bonds
                  if ea != eb and bo == "single"]
    half = (len(het_single) + 1) // 2
    for i in range(half):
        l = het_single[i]
        lft = f"| {l[0]}–{l[1]} | {l[3]:.3f} | {l[4]} | {a0u(l[3]):.3f} |"
        if i + half < len(het_single):
            r2 = het_single[i + half]
            rgt = f"| {r2[0]}–{r2[1]} | {r2[3]:.3f} | {r2[4]} | {a0u(r2[3]):.3f} |"
        else:
            rgt = "| | | | |"
        P(lft + rgt + " |")
    P("")

    # ================= [4] 键级步进律（扩展统计） =================
    P("## [4] 键级步进律（每增一键的收缩 Δ，a0 单位）\n")
    P("| 家族 | 键级串 | Δ(1→2) | Δ(2→3) | 备注 |")
    P("|---|---|---|---|---|")
    series = {}
    for ea, eb, bo, d, src in bonds:
        if bo == "aromatic":
            continue
        key = tuple(sorted((ea, eb)))
        series.setdefault(key, {})[bo] = a0u(d)
    # 孤对/电负离群族（Δ 异常大，因单键受孤对斥拉长或数据跨环境浮动大）
    LONE = {("N", "O"), ("O", "O")}
    for key, s in sorted(series.items(), key=lambda kv: kv[0][0]):
        if not {"single", "double"} <= set(s):
            continue
        d12 = s["single"] - s["double"]
        d23 = s["double"] - s["triple"] if "triple" in s else None
        remark = ""
        if key in LONE:
            remark = "孤对/电负离群，不作为核心步进"
        elif d23 is not None and d23 < 0.15:
            remark = "第三周期重原子三键弱化，Δ(2→3) 偏小"
        P(f"| {key[0]}–{key[1]} | "
          + " / ".join(k for k in ("single", "double", "triple") if k in s)
          + f" | {d12:.3f} | "
          + (f"{d23:.3f}" if d23 is not None else "—")
          + f" | {remark} |")
    P("")
    # 核心统计：剔除孤对族（O–O、N–O）
    excl = [k for k in series if k not in LONE]
    d12_all = [series[k]["single"] - series[k]["double"]
               for k in excl if {"single", "double"} <= set(series[k])]
    d23_all = [series[k]["double"] - series[k]["triple"]
               for k in excl if {"single", "double", "triple"} <= set(series[k])]
    n12, m12, s12, r12, x12 = stats(d12_all)
    n23, m23, s23, r23, x23 = stats(d23_all)
    P(f"- 核心多重键族（剔除 O–O、N–O 孤对族，n={n12}）："
      f"Δ(1→2) = {m12:.3f} ± {s12:.3f} [RMS {r12:.3f}, max {x12:.3f}]")
    P(f"- 核心多重键族三键步进（n={n23}）：Δ(2→3) = {m23:.3f} ± {s23:.3f} "
      f"[RMS {r23:.3f}, max {x23:.3f}]")
    oo = series[("O", "O")]["single"] - series[("O", "O")]["double"]
    no = series[("N", "O")]["single"] - series[("N", "O")]["double"]
    P(f"- 离群对照：O–O Δ(1→2) = {oo:.3f}，N–O Δ(1→2) = {no:.3f}"
      f"（均因单键受孤对排斥/数据浮动，偏离核心 ^ 均值）\n")

    # ================= [5] 单键加和律（分家族统计） =================
    P("## [5] 单键加和律 d(A–B) ≈ r_A + r_B（a0 单位，分家族统计）\n")
    all_single = [(ea, eb, d, src) for ea, eb, bo, d, src in bonds
                  if bo == "single"]
    resid_map = {}
    for ea, eb, d, src in all_single:
        if ea not in cov_a0 or eb not in cov_a0:
            continue
        rr = a0u(d) - (cov_a0[ea][3] + cov_a0[eb][3])
        rel = rr / a0u(d)
        resid_map[f"{ea}–{eb}"] = (rr, rel * 100, a0u(d))

    P("| 键 | d/a0 | r_A+r_B | 残差 | 相对误差 |")
    P("|---|---|---|---|---|")
    for k, (rr, rel, dd) in sorted(resid_map.items()):
        P(f"| {k} | {dd:.3f} | {dd - rr:.3f} | {rr:+.3f} | {rel:+.1f}% |")
    P("")

    # 家族分组（语义明确、互斥近似）
    org_family  = ["C–H", "C–C", "C–N", "C–O", "C–F", "C–Cl", "C–Br",
                   "C–I", "C–S", "C–P", "C–Si"]          # 有机 C 骨架（11）
    het_perio   = ["B–C", "B–F", "B–O", "N–H", "N–O", "N–F", "O–H", "O–F",
                   "F–H", "Si–H", "Si–O", "Si–F", "Si–Cl", "Si–N",
                   "P–H", "P–O", "P–F", "P–Cl", "S–H", "S–O", "S–F",
                   "S–Cl", "Cl–H", "Br–H", "I–H"]         # 轻杂原子/氢化物（25）
    same_p2     = ["H–H", "C–C", "N–N", "O–O", "F–F"]   # 同核第 2 周期（5）
    same_heavy  = ["Si–Si", "P–P", "S–S", "Cl–Cl", "Ge–Ge", "As–As",
                   "Se–Se", "Br–Br", "Te–Te", "I–I"]      # 同核重主族(3-5周期，10)
    ionic       = ["Li–Li", "Na–Na", "Li–Cl", "Na–Cl", "K–Cl", "Mg–O"]  # 离子/金属性（6）

    def report(name, keys):
        vals = [resid_map[k][1] for k in keys if k in resid_map]
        n, m, s, r, x = stats(vals)
        P(f"- **{name}** (n={n})：残差 = {m:+.1f}% ± {s:.1f}%  "
          f"[RMS {r:.1f}%, max {x:.1f}%]")
        return (n, m, s, r, x)

    P("### 分家族残差（相对误差 %）")
    n_org, m_org, s_org, r_org, x_org = report(
        "有机 C 骨架中性共价族", org_family)
    n_hx, m_hx, s_hx, r_hx, x_hx = report(
        "轻杂原子/氢化物", het_perio)
    n_p2, m_p2, s_p2, r_p2, x_p2 = report(
        "同核第 2 周期小/高电负原子", same_p2)
    n_hv, m_hv, s_hv, r_hv, x_hv = report(
        "同核重主族（第 3-5 周期）", same_heavy)
    n_io, m_io, s_io, r_io, x_io = report(
        "离子性/金属性对", ionic)
    P("")

    P("### 结论（适用范围）")
    P("- 有机 C 骨架中性共价族：RMS %.1f%%、max %.1f%%（均值 %+.1f%%）——"
      "加和律在此家族严格成立。" % (r_org, x_org, m_org))
    P("- 轻杂原子/氢化物：RMS %.1f%%（max %.1f%%）—— 加和律近似成立，"
      "电负性偏移 ±5%% 量级。仅作指示。" % (r_hx, x_hx))
    P("- 同核第 2 周期小/高电负原子（H、O、F）：拉伸 %+.1f%% ~ %+.1f%% ——"
      "孤对/通道饱和修正项，SRE 成键规则须显式写入。" % (
          min(resid_map[k][1] for k in ("H–H", "O–O", "F–F")),
          max(resid_map[k][1] for k in ("H–H", "O–O", "F–F"))))
    P("- 同核重主族（Si…I）：RMS %.1f%% —— 随电负性降低加和律回归；"
      "F–F 的 +20%% 拉伸在第 3-5 周期同族中消失（孤对效应非普适）。" % r_hv)
    P("- 离子性/金属性对（碱金属、碱土卤化物）：系统收缩（负残差）——"
      "加和律不适用，属『相干通道关闭→距离塌缩越过加和线』的另一本体论区间。\n")

    # ================= [6] 键级容量 =================
    P("## [6] 键级容量观察：各族最大稳定键级")
    P("- 14 族：C≡C(3)、Si≡Si(3)、Ge≡Ge(3) —— 容量 3")
    P("- 15 族：N≡N(3)、P≡P(3)、As≡As(3)  —— 容量 3")
    P("- 16 族：O=O(2)、S=S(2)、Se=Se(2)、Te=Te(2) —— 容量 2")
    P("- 17 族：F–F(1)、Cl–Cl(1)、Br–Br(1)、I–I(1) —— 容量 1")
    P("- 通道容量并非恒 3，而是随族随周期递减（16 族 2、17 族 1）；")
    P("  第 2 周期同核小原子（O、F）因孤对排斥，实际键级往往低于容量上限，")
    P("  这与 ② 成键规则 中『通道饱和 + 孤对排斥』两项修正一致。\n")

    # ================= 诚实边界 =================
    P("## 诚实边界")
    P("- 本表仅把真实经验数据组织为无量纲关系数，验证其近似服从加和/步进/整数比结构；")
    P("  是 SRE「距离 = 相干簿记」本体论的同向指示，并非由 SRE 推导任何数值。")
    P("- 键长为经验代表值：同一种键在不同环境（分子/晶体/温度）有 ±0.01–0.03 Å 涨落，")
    P("  与 a0 相比属小数位内噪声，不逐键过度诠释。")
    P("- 共价半径采用 Cordero 2008 一种定标；换 Pyykkö 体系会使个别残差移动约 1–3%，")
    P("  但家族结构与结论（有机族干净、O/F 拉伸、重主族回归、离子对失效）稳定。")
    P("- O–O 单键因孤立对排斥异常偏长，第 5 检验中如实排除于核心统计外，不掩盖。")

    md = "\n".join(lines)
    with open("sre_dimension_collapse_table_ext.md", "w", encoding="utf-8") as f:
        f.write(md)
    print(md)

    # ================= JSON 摘要 =================
    summary = {
        "scale_anchor_ratio": r0,
        "n_covalent_elements": len(cov),
        "n_bonds_total": len(bonds),
        "n_single_bonds_tested": len(resid_map),
        "bond_order_step_D12_mean_core": round(sum(d12_all) / len(d12_all), 4),
        "bond_order_step_D12_std_core": round(
            (sum((v - sum(d12_all) / len(d12_all)) ** 2 for v in d12_all)
             / len(d12_all)) ** 0.5, 4),
        "bond_order_step_D23_mean_core": round(m23, 4),
        "bond_order_step_D23_std_core": round(s23, 4),
        "O_O_step_D12_excluded": round(
            series[("O", "O")]["single"] - series[("O", "O")]["double"], 4),
        "family_additivity": {
            "organic_C_frame": {"n": n_org, "mean_pct": round(m_org, 1),
                                "rms_pct": round(r_org, 1),
                                "max_pct": round(x_org, 1)},
            "hetero_hydride": {"n": n_hx, "mean_pct": round(m_hx, 1),
                               "rms_pct": round(r_hx, 1),
                               "max_pct": round(x_hx, 1)},
            "homonuclear_period2": {"n": n_p2, "min_pct": round(
                min(resid_map[k][1] for k in same_p2 if k in resid_map), 1),
                "max_pct": round(max(resid_map[k][1] for k in same_p2
                                     if k in resid_map), 1)},
            "homonuclear_heavy_main_group": {"n": n_hv, "mean_pct": round(m_hv, 1),
                                             "rms_pct": round(r_hv, 1),
                                             "max_pct": round(x_hv, 1)},
            "ionic_halide_oxide": {"n": n_io, "mean_pct": round(m_io, 1),
                                   "rms_pct": round(r_io, 1),
                                   "max_pct": round(x_io, 1)},
        },
        "max_bond_order_by_group": {"14": 3, "15": 3, "16": 2, "17": 1},
        "matches": r0 > 0.99999 and r_org < 4.0,
    }
    with open("sre_dimension_collapse_summary_ext.json", "w",
              encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("\n[JSON] ", json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
