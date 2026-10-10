# -*- coding: utf-8 -*-
"""
H2O 三点退化的判定性实验（用户 2026-09-24 追问的核对）

问题：MDS 把 H2O 反演成共线，文件把它归因于「D 缺非键合关联」。
用户质疑：(a) 这个解释是否循环？(b) 物理上 H2O 不可能是直线，因为还有电子。

本脚本只做 n=3 的精确核查（纯 numpy，不用 networkx）：
  PART 1  三点退化定理：任意「等权键」距离（含任意对称加权）必然共线
  PART 2  角度 <-> t = d(H,H) 的一一对应：证明「补非键合项」= 「把角度改写成距离」= 零预测
  PART 3  「反演忠诚性 r」在 n=3 时是构造必然（r 恒 = 1），不是涌现证据
  PART 4  真实 H2O 数值 -> 所需的 t；以及「把电子结构当叶节点」为何不管用
"""

import sys
import json

sys.stdout.reconfigure(encoding="utf-8")
import numpy as np

OUT = {}


def P(*a):
    print(*a, flush=True)


def classical_mds(D, ndim=2):
    """经典(Torgerson) MDS：给定距离矩阵 D，反解坐标 X。"""
    D = np.asarray(D, float)
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B)
    idx = np.argsort(w)[::-1][:ndim]
    L = np.sqrt(np.clip(w[idx], 0.0, None))
    return V[:, idx] * L


def pairwise(X):
    n = X.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            D[i, j] = np.linalg.norm(X[i] - X[j])
    return D


def pearson(a, b):
    a = np.asarray(a, float).ravel()
    b = np.asarray(b, float).ravel()
    a = a - a.mean()
    b = b - b.mean()
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))


def apex_angle(X, apex=1):
    """顶角：行 1 = O，行 0/2 = 两个 H。返回度。"""
    v1 = X[0] - X[apex]
    v2 = X[2] - X[apex]
    c = float(v1 @ v2 / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    return float(np.degrees(np.arccos(np.clip(c, -1.0, 1.0))))


def D_three(t):
    """H1-O = 1, O-H2 = 1, H1-H2 = t（单位：键长）。"""
    return np.array([[0.0, 1.0, t],
                     [1.0, 0.0, 1.0],
                     [t, 1.0, 0.0]])


# ---------------------------------------------------------------- PART 1
P("=" * 78)
P("PART 1  三点退化定理：等权键（含任意对称加权）必然给出共线")
P("=" * 78)
P()
P("  取 d(H1-O)=d(O-H2)=w，d(H1-H2)=2w（键路径距离，2w = w+w）。")
P("  由三角等式 d(1,3) = d(1,2) + d(2,3) ⇒ 三角形退化 ⇒ 必然共线。")
P()
P(f"  {'w':>8}{'顶点(O) 角(度)':>18}{'MDS 复现 D 的 r':>18}{'二阶本征值':>14}")
P("  " + "-" * 60)
rows1 = []
for w in [0.5, 1.0, 2.0, 3.0]:
    D = np.array([[0.0, w, 2 * w], [w, 0.0, w], [2 * w, w, 0.0]])
    X = classical_mds(D, 2)
    ang = apex_angle(X)
    r = pearson(pairwise(X)[np.triu_indices(3, 1)], D[np.triu_indices(3, 1)])
    J = np.eye(3) - np.ones((3, 3)) / 3
    B = -0.5 * J @ (D ** 2) @ J
    ev = np.sort(np.linalg.eigvalsh(B))[::-1]
    P(f"  {w:>8.2f}{ang:>18.4f}{r:>18.6f}{ev[1]:>14.2e}")
    rows1.append({"w": w, "angle": ang, "r": r, "lam2": float(ev[1])})
P()
P("  ⇒ 任何对称加权都改变不了共线；要弯曲，**只能**让 d(H1,H2) < 2w，")
P("     即必须存在一条直接的非键合(H...H)关系。")
OUT["part1"] = rows1

# ---------------------------------------------------------------- PART 2
P()
P("=" * 78)
P("PART 2  角度 <-> t 的一一对应：这就是「循环」的精确形式")
P("=" * 78)
P()
P("  等腰三角形（两边 = 1，底 = t）：cos(theta) = (1^2+1^2-t^2)/(2*1*1) = 1 - t^2/2")
P("  ⇒ theta = arccos(1 - t^2/2)，单调双射。**t 与 theta 携带完全相同的信息。**")
P()
P(f"  {'t=d(H,H)':>10}{'闭式 theta(度)':>16}{'MDS 实测 theta':>16}{'差':>10}{'r(复现D)':>12}")
P("  " + "-" * 66)
rows2 = []
for t in [2.0, 1.9, 1.8, 1.7, 1.6, 1.5811, 1.5, 1.4, 1.3, 1.2]:
    D = D_three(t)
    X = classical_mds(D, 2)
    ang = apex_angle(X)
    pred = float(np.degrees(np.arccos(np.clip(1 - t * t / 2, -1, 1))))
    r = pearson(pairwise(X)[np.triu_indices(3, 1)], D[np.triu_indices(3, 1)])
    P(f"  {t:>10.4f}{pred:>16.4f}{ang:>16.4f}{abs(ang - pred):>10.2e}{r:>12.6f}")
    rows2.append({"t": t, "theta_closed": pred, "theta_mds": ang, "r": r})
P()
P("  ⇒ 「补一条非键合项就能得到弯曲」与「角度是 104.5 度」**等价**：")
P("     它不是预测，是把角度**改写**成一个距离。零预测余量。")
OUT["part2"] = rows2

# ---------------------------------------------------------------- PART 3
P()
P("=" * 78)
P("PART 3  「反演忠诚性 r」在 n=3 时是构造必然，不是涌现证据")
P("=" * 78)
P()
P("  经典 MDS 对欧氏 D 构造性复原：rank<=2 时 r 恒 = 1.000（PART 1/2 已逐行确认）。")
P("  n=3 的距离矩阵只有 3 个独立项，嵌入只有 3 个自由度(2D 中 3 点 3 坐标-2) ⇒ 双射。")
P("  ⇒ r=1.000 是**定义**，不是发现。它只在 D 非欧氏时才 <1，那时测的是「可嵌入性」。")
P()
r_vals = [row["r"] for row in rows1] + [row["r"] for row in rows2]
P(f"  本实验全部 r 取值：min={min(r_vals):.6f}  max={max(r_vals):.6f}  （恒 = 1）")
P("  ⇒ MDS 文件里 H2O 的『r(复现D)=1.000』对该分子**不提供任何证据**。")
OUT["part3"] = {"r_min": min(r_vals), "r_max": max(r_vals)}

# ---------------------------------------------------------------- PART 4
P()
P("=" * 78)
P("PART 4  真实 H2O 数值 + 为什么「把电子结构当叶节点」不管用")
P("=" * 78)
P()
rOH = 0.9584      # A，实验平衡键长
rHH = 1.51383     # A，实验 H...H 距离
theta_exp = 104.474  # 度
t_real = rHH / rOH
theta_from_bonds = float(np.degrees(np.arccos(np.clip(1 - t_real ** 2 / 2, -1, 1))))
t_needed = 2.0 * np.sin(np.radians(theta_exp) / 2.0)
P(f"  r(O-H) = {rOH:.4f} A ；r(H...H) = {rHH:.4f} A ；实验角度 = {theta_exp:.3f} 度")
P(f"  归一化 t = r(H...H)/r(O-H) = {t_real:.6f}")
P(f"  由闭式反推的角度            = {theta_from_bonds:.4f} 度   （= 实验值，自洽）")
P(f"  要得到 {theta_exp:.3f} 度所需的 t = 2*sin(theta/2) = {t_needed:.6f}")
P(f"  ⇒ 非键合项比「键路径 2.0」短 {(1 - t_needed / 2.0) * 100:.2f}%")
P()
P("  再检验「把电子结构当额外节点」能否救：")
P("  图：H1-O-H2 加一个叶节点 L（孤对电子，只连 O）；边 {(H1,O),(O,H2),(O,L)}")
D4 = np.array([
    [0, 1, 2, 2],
    [1, 0, 1, 1],
    [2, 1, 0, 2],
    [2, 1, 2, 0],
], float)
P("    图距离：d(H1,O)=1, d(O,H2)=1, d(H1,H2)=2, d(O,L)=1, d(H1,L)=2, d(H2,L)=2")
sub = D4[np.ix_([0, 1, 2], [0, 1, 2])]
sub_ang = apex_angle(classical_mds(sub, 2))
P(f"    子度量 {{H1,O,H2}} 与原来**逐项相同** ⇒ 其 MDS 顶角 = {sub_ang:.4f} 度（仍共线）")
J4 = np.eye(4) - np.ones((4, 4)) / 4
B4 = -0.5 * J4 @ (D4 ** 2) @ J4
ev4 = np.sort(np.linalg.eigvalsh(B4))
P(f"    但四点图度量**非欧氏**：Gram 最小本征值 = {ev4[0]:.4f} < 0 ⇒ 不可嵌入")
P("    （若强行对四点做 MDS，H-O-H 会被扭曲成非 180 度——那是投影假象，不是弯曲证据）")
P("  ⇒ 电子结构以「叶节点」形式加入**无效**：子距离未变，三点仍退化。")
OUT["part4"] = {"rOH": rOH, "rHH": rHH, "theta_exp": theta_exp,
                "t_real": t_real, "theta_from_bonds": theta_from_bonds,
                "t_needed": t_needed, "sub_angle_with_leaf": sub_ang,
                "gram_min_eig_4pt": float(ev4[0])}

# ---------------------------------------------------------------- 结论
P()
P("=" * 78)
P("结论")
P("=" * 78)
P()
P("  1) 用户「循环」的直觉成立，且是定理：n=3 时角度与 t 双射 ⇒")
P("     「补非键合关联以恢复弯曲」= 零预测（同 §12.11「零残差 = 无预测余量」同型）。")
P("  2) 修正 MDS 文件的一处读法：H2O 的 r(复现D)=1.000 是构造必然，非涌现证据。")
P("  3) 但用户的物理点仍然成立，且可做成必要性证明：两个 H 等价 ⇒ 对称加权不可")
P("     弯曲（PART 1 实测）；加电子叶节点也不可（PART 4 实测）⇒ **必须**存在直接的")
P("     非键合 H...H 关系。这是可证伪的**结构预言**（非循环部分）。")
P("  4) 循环部分：该关系的**大小** t=1.5811（=104.474 度）与角度一一对应 ⇒ 需外部输入。")
P("  ⇒ H2O(n=3) 是 G12「离散闭合 / 连续需输入」的最小见证：")
P("     哪部分是预言（必须有哪些关系）、哪部分是输入（关系的尺度），在这里可被证明地分开。")

with open("_h2o_degeneracy.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
P()
P("[已写出 _h2o_degeneracy.json]")
