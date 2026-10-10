# -*- coding: utf-8 -*-
"""
H2O：「比值」还是「几何」？—— SRE 体系下形状的表示层级（用户 2026-09-24 追问）

用户命题：
  (P) 按 SRE 体系，H2O 体现出来的应是「3 者比值」，而不是几何关系；
      因为**只有映射才有几何关系**（几何是 map 的性质，不是 graph 的性质）。

本脚本把它拆成两条可判定的分句，纯 math/numpy：
  PART A  graph 层：水分子拓扑有哪些内蕴量（谱 / 度 / 轨道数）——里面**没有比值也没有角**
  PART B  【定理】角 ∉ functions(graph)：同一个图、两个度量 ⇒ 两个角（图不变量全同）
  PART C  【定理】同一个比值、不同映射 ⇒ 不同几何：
          欧氏 / 球面(K>0) / 双曲(K<0) 三种映射，"比值"完全相同而"角"不同；
          且弯曲空间里 **角还依赖绝对尺度**（相似性只在欧氏成立）。
  PART D  分层表 + 归属

关键点：PART C 是**分布无关**的（不需要"恰好命中"某数），因此不受「数值巧合」质疑。
"""

import sys
import json
import math

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

OUT = {}


def P(*a):
    print(*a, flush=True)


def lap(edges, n):
    L = np.zeros((n, n))
    for i, j in edges:
        L[i, i] += 1.0
        L[j, j] += 1.0
        L[i, j] -= 1.0
        L[j, i] -= 1.0
    return L


def adj(edges, n):
    A = np.zeros((n, n))
    for i, j in edges:
        A[i, j] = A[j, i] = 1.0
    return A


def spec(M):
    return np.sort(np.linalg.eigvalsh(M))


def degs(edges, n):
    d = [0] * n
    for i, j in edges:
        d[i] += 1
        d[j] += 1
    return d


def orbit_count(edges, n):
    """暴力轨道计数：由邻接矩阵的行编码分类（已按度+邻居集排序归一）。"""
    A = adj(edges, n)
    keys = []
    for i in range(n):
        nb = tuple(sorted(int(k) for k in np.nonzero(A[i])[0]))
        keys.append((len(nb), nb))
    # 用「度 + 邻居度的排序元组」作为不变式（足够这 2 个图）
    keys2 = []
    for i in range(n):
        nb = sorted(int(k) for k in np.nonzero(A[i])[0])
        keys2.append((len(nb), tuple(sorted(int(sum(A[k])) for k in nb))))
    return len(set(keys2))


# ================================================================ PART A
P("=" * 78)
P("PART A  graph 层：水分子拓扑的内蕴量里没有『比值』也没有『角』")
P("=" * 78)
P()
edges_P3 = [(0, 1), (0, 2)]        # H1 - O - H2
edges_K3 = [(0, 1), (0, 2), (1, 2)]  # 若补一条 H...H
for name, E in [("P3 = O 连两 H（纯键拓扑）", edges_P3),
                ("K3 = 再补一条 H...H", edges_K3)]:
    L = lap(E, 3)
    A = adj(E, 3)
    P(f"  {name}")
    P(f"    度序列        = {degs(E, 3)}")
    P(f"    L 谱          = {np.round(spec(L), 6).tolist()}")
    P(f"    A 谱          = {np.round(spec(A), 6).tolist()}")
    P(f"    Aut 轨道数(G10 口径) = {orbit_count(E, 3)}")
    P(f"    ⇒ 内蕴量全是整数 / 整数比，**没有任何长度、没有角**")
    P()
P("  根源：图论对象 = (顶点集, 边集)。它**不带度量**；")
P("        「长度 / 距离 / 角」都属于度量结构，必须由外部赋予（= D）。")
OUT["partA"] = {"P3": {"deg": degs(edges_P3, 3), "Lspec": spec(lap(edges_P3, 3)).tolist(),
                       "orbit": orbit_count(edges_P3, 3)},
                "K3": {"deg": degs(edges_K3, 3), "Lspec": spec(lap(edges_K3, 3)).tolist(),
                       "orbit": orbit_count(edges_K3, 3)}}

# ================================================================ PART B
P()
P("=" * 78)
P("PART B  【定理】角 ∉ functions(graph)：同图两度量 ⇒ 两角")
P("=" * 78)
P()
P("  证明（构造性，无需任何数值巧合）：")
P("    取**同一个图** P3（H1-O-H2，两条边）。")
P("    赋予两个合法度量 D(t)：d(H1,O)=d(O,H2)=1，d(H1,H2)=t。")
P("      t = 2.0  ⇒ 等权键路径 ⇒ 顶角 = 180.0000°")
P("      t = 1.2  ⇒ 顶角 = 73.7398°")
P("    图不变量（度序列 / L 谱 / A 谱 / 轨道数）在两种情形下**逐项相同**。")
P("    ⇒ 角不是图不变量；角 = f(D)，D 是**输入**。")
P()
def theta_euclid(t):
    return math.degrees(math.acos(max(-1.0, min(1.0, 1.0 - t * t / 2.0))))


P(f"  {'t=d(H,H)':>10}{'顶角(度)':>12}   | 同图 P3，同一套图不变量")
P("  " + "-" * 56)
rowsB = []
for t in [2.0, 1.5811388, 1.2]:
    ang = theta_euclid(t)
    P(f"  {t:>10.4f}{ang:>12.4f}   | deg=(2,1,1)  L谱=(0,1,3)  orbit=2")
    rowsB.append({"t": t, "theta": ang})
P()
P("  ⇒ 用户命题中『几何关系不是 SRE 内蕴产物』这一半：**成立且是定理**。")
OUT["partB"] = rowsB

# ================================================================ PART C
P()
P("=" * 78)
P("PART C  【定理】同一个比值 + 不同映射 ⇒ 不同几何（分布无关）")
P("=" * 78)
P()
t0 = 2.0 * math.sin(math.radians(104.4776) / 2.0)
P(f"  固定 H2O 的『3 者比值』= (1, 1, t0)，t0 = 2*sin(104.4776°/2) = {t0:.6f}")
P("  把这个**完全相同**的比值放进三种映射（欧氏 / 球面 / 双曲），看顶角：")
P()


def theta_sphere(t, s, R=1.0):
    a, c = s / R, t * s / R
    cv = (math.cos(c) - math.cos(a) ** 2) / math.sin(a) ** 2
    return (math.degrees(math.acos(cv)) if -1.0 <= cv <= 1.0 else None), cv


def theta_hyper(t, s, R=1.0):
    a, c = s / R, t * s / R
    cv = (math.cosh(a) ** 2 - math.cosh(c)) / math.sinh(a) ** 2
    return (math.degrees(math.acos(cv)) if -1.0 <= cv <= 1.0 else None), cv


P(f"  欧氏(K=0)  —— 比值即定角，且**与尺度无关**（相似性）：")
P(f"      theta = arccos(1 - t0^2/2) = {theta_euclid(t0):.4f}°   对任意尺度 s")
P()
for label, fn in [("球面 K>0 (R=1)", theta_sphere), ("双曲 K<0 (R=1)", theta_hyper)]:
    P(f"  {label} —— 同一比值，扫绝对尺度 s（弯曲空间里**没有相似性**）：")
    P(f"      {'尺度 s':>10}{'边 x=t0*s':>12}{'顶角(度)':>12}   备注")
    P("      " + "-" * 50)
    rows = []
    for s in [0.10, 0.30, 0.50, 0.80, 1.00, 1.30, 1.60, 1.90]:
        if s * t0 > math.pi and label.startswith("球面"):
            P(f"      {s:>10.2f}{s*t0:>12.4f}{'--':>12}   边长 > pi，无三角形")
            continue
        ang, cv = fn(t0, s)
        if ang is None:
            P(f"      {s:>10.2f}{s*t0:>12.4f}{'--':>12}   |cos|>1，无解（退化）")
        else:
            P(f"      {s:>10.2f}{s*t0:>12.4f}{ang:>12.4f}   cos={cv:+.4f}")
            rows.append({"s": s, "theta": ang})
    P(f"      ⇒ 同一比值 t0 给出顶角区间 [{min(r['theta'] for r in rows):.2f}°, "
      f"{max(r['theta'] for r in rows):.2f}°]")
    P()
    OUT["partC_" + ("sphere" if label.startswith("球面") else "hyper")] = {
        "rows": rows,
        "theta_min": min(r["theta"] for r in rows),
        "theta_max": max(r["theta"] for r in rows)}
P("  结论（定理级，不依赖任何数值巧合）：")
P("    · 欧氏里『比值 → 角』是一一映射，这是**欧氏相似性**的性质；")
P("    · 同一比值在球面可给出 104°→145°，在双曲可给出 104°→82°；")
P("    · 甚至在同一弯曲空间内，改**绝对尺度**就改角。")
P("    ⇒ 角 = f(比值, 映射)；映射一变，角就变。**几何是映射的性质，不是图的性质。**")
P("    ⇒ 用户命题『只有映射才有几何关系』：**成立且是定理**。")
OUT["partC"] = {"t0": t0, "theta_euclid": theta_euclid(t0),
                "theta_sphere_range": [OUT["partC_sphere"]["theta_min"],
                                       OUT["partC_sphere"]["theta_max"]],
                "theta_hyper_range": [OUT["partC_hyper"]["theta_min"],
                                      OUT["partC_hyper"]["theta_max"]]}

# ================================================================ PART D
P()
P("=" * 78)
P("PART D  分层表与归属")
P("=" * 78)
P()
P("  ┌ L0 拓扑层 ─ 图 P3 ─────────────────────────────────────────────┐")
P("  │ SRE 免费给出：度序列 (2,1,1)、L 谱 (0,1,3)、轨道数 2 —— 全整数   │")
P("  │ 没有比值、没有角。（离散侧，闭合）                              │")
P("  └─────────────────────── 付：度量 D ─────────────────────────────┘")
P("  ┌ L1 比值层 ─ (1,1,t) ─ 「3 者比值」= 用户的命题落点 ─────────────┐")
P("  │ SRE 给出：形式（一个无量纲数 t）；t = 2 sin(theta/2)            │")
P("  │ 需输入：D（含非键合 H...H）⇒ 决定 t 的**值**                    │")
P("  │ 与几何**无关**：无需任何坐标 / 环境空间                          │")
P("  └─────────────────── 付：映射（欧氏 / 曲率 / 尺度）─────────────┘")
P("  ┌ L2 几何层 ─ 角 theta ─────────────────────────────────────────┐")
P("  │ SRE 不给出任何东西；theta = arccos(1 - t^2/2) 是**映射输出**    │")
P("  │ 同比值不同映射 ⇒ 不同 theta（PART C 实测）                      │")
P("  └───────────────────────────────────────────────────────────────┘")
P()
P("  用户命题的精确化：")
P("    (a) 『体现出来的应是 3 者比值，而不是几何』—— **成立**：比值是 L1，几何是 L2，")
P("        而 SRE 的原生产物停在 L1（无量纲、无坐标）。")
P("    (b) 『只有映射才有几何关系』—— **成立且是定理**（PART B + PART C）。")
P("    (c) 需补的精度：L1 的**形式**是 SRE 相容的，但它的**值**仍需输入 D（G12）。")
P("        比值不是说「免费」，而是说「这是正确的表示层级」——它不欠映射这一笔。")
P()
P("  项目级旁证：SRE 迄今所有**获得通过**的量都是无量纲比值（Pi1、lam2/rho、")
P("    Pi1(Q_k)=1/k、lam2=2-sqrt3、轨道数、|Aut| 比值）；所有**判负**都发生在")
P("    要求把一个**量纲化的值**赋给某结构时（L4 赋质量、alpha 的绝对值）。")
P("    ⇒ 「比值 vs 值」的裂缝，与本轮「比值 vs 几何」是同一条 G12 缝的不同截面。")

with open("_h2o_ratio_vs_geometry.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P()
P("[已写出 _h2o_ratio_vs_geometry.json]")
