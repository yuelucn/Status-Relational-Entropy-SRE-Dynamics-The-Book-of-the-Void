# -*- coding: utf-8 -*-
"""
_sre_validation_metric_audit.py — 审计「之前的验证路线是否用了推算结果而非实验结果」
（纯 numpy）

用户命题（2026-09-24 第二十二轮）：
  「从某种意义上之前的验证路线是错的，用的是推算结果，而不是实验结果。」

本脚本不替用户下结论，只做两件可判定的事：
  A. 检验 MDS 线**两个保真指标**的信息量（它们是否退化为恒等式 / 算法性质）。
  B. 把项目主要验证条目按「对比目标的认识论类型」分类并计数：
       E = 独立实验观测量（外样本）｜R = 反演量 / 模型依赖量｜C = 构造性 / 循环（恒等式、回代、自证）

预注册判据
------------------------------------------------------------------
A1 若 n=3 时「距离集 Pearson」对键角不敏感（恒 ±1）⇒ 该指标在 H2O 上零信息。
A2 若经典 MDS 的「反演忠诚性」对任意欧氏 D 恒 = 1 ⇒ 它是**算法收敛性指标**，不是物理验证。
B  若 C/R 类条目**全部落在几何/形状一支**、E 类条目**全部落在谱层/数值一支**
   ⇒ 用户命题成立，但作用域是「某一条线」，不是「整条验证路线」。
"""
import json
import numpy as np

OUT = {}
L = []


def P(s=""):
    print(s)
    L.append(s)


def pearson(a, b):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    return float(np.corrcoef(a, b)[0, 1])


def classical_mds(D, k=3):
    D = np.asarray(D, float)
    n = D.shape[0]
    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    w, V = np.linalg.eigh(B)
    idx = np.argsort(w)[::-1][:k]
    w = np.clip(w[idx], 0, None)
    return V[:, idx] * np.sqrt(w)


def pdist(X):
    X = np.asarray(X, float)
    n = X.shape[0]
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            D[i, j] = D[j, i] = np.linalg.norm(X[i] - X[j])
    return D


# ==================================================================
P("=" * 78)
P("A  MDS 线的指标 1「涌现几何 vs 真实」：n=3 时对键角**盲**")
P("=" * 78)
P()
P("  纯拓扑 D（键图最短路径）对 H2O 恒为 (1,1,2)——因为 H-O-H 路径长 = 两段 O-H 之和。")
P("  真实几何的距离集恒为 (r, r, x)，x = 2r*sin(theta/2)。")
P("  解析：两个长度 3 的向量都是 (a,a,b) 形式 ⇒ Pearson 恒 = sign((a-b)(c-d)) = ±1，")
P("        与 theta 完全无关。数值核验：")
P()
P(  "    theta(度)    真实距离集(归一)         r(rec vs real)   样本数")
P("  " + "-" * 66)
rows_a = []
D_rec = np.array([1.0, 1.0, 2.0])          # 纯拓扑（退化共线）
for th in [180.0, 150.0, 120.0, 104.4776, 90.0, 60.0, 30.0]:
    x = 2.0 * np.sin(np.radians(th) / 2.0)
    D_real = np.array([1.0, 1.0, x])
    degen = bool(np.std(D_real) < 1e-12)   # 向量恒定 => 相关系数无定义
    r = pearson(D_rec, D_real) if not degen else float("nan")
    P("    %8.3f    (1, 1, %.4f)         %s          3"
      % (th, x, "退化(向量恒定)" if degen else "%+.6f" % r))
    rows_a.append(dict(theta=th, D_real=list(D_real),
                       r_vs_real=(None if degen else r), degenerate=degen))
P()
P("  规律：r 的**幅度恒为 1**；符号在 x = r（即 theta = 60 度）处翻转；")
P("        theta = 60 度时真实距离集为 (1,1,1) 恒定，相关系数无定义。")
P("        ⇒ 该指标对 theta 的全部信息只有『是否 > 60 度』这一个比特。")
P()
allpm1 = all((x["degenerate"] or abs(abs(x["r_vs_real"]) - 1.0) < 1e-9) for x in rows_a)
P("  >>> A1 判据（幅度恒 1 即『零信息』）：%s" % ("成立（该指标对键角盲）" if allpm1 else "不成立"))
P("      ⇒ H2O 行里『涌现 vs 真实 r=0.985』无法分辨 180 度与 104.5 度；")
P("        日志报 0.985 说明该处不是同一构造（含缩放/加权/平均）—— 但无论哪种，")
P("        **它都不是对键角的检验**。")
OUT["A1"] = dict(rows=rows_a, verdict=bool(allpm1))

# ==================================================================
P()
P("=" * 78)
P("B  MDS 线的指标 2「反演忠诚 r(复现D)」：对任意欧氏 D 恒 = 1（算法性质）")
P("=" * 78)
P()
P("  经典（Torgerson）MDS 的目标函数**就是**最小化 ||D - dist(X)||：")
P("  只要 D 欧氏可嵌入，重建就精确复现 D ⇒ r = 1 是**算法收敛的定义**，")
P("  与分子是什么、键角多大都无关。数值核验（随机 3D 点集）：")
P()
P("     n      r(dist(X_rec), D)")
P("  " + "-" * 30)
rows_b = []
rng = np.random.default_rng(7)
for n in [4, 6, 10, 20]:
    X = rng.normal(size=(n, 3))
    D = pdist(X)
    Xr = classical_mds(D, 3)
    r = pearson(pdist(Xr).ravel(), D.ravel())
    P("    %2d      %.6f" % (n, r))
    rows_b.append(dict(n=n, r=r))
# 退化共线 D 也恒 1
D_deg = np.array([[0, 1, 2], [1, 0, 1], [2, 1, 0]], float)
Xr = classical_mds(D_deg, 2)
r_deg = pearson(pdist(Xr).ravel(), D_deg.ravel())
P("     (1,1,2)  %.6f   ← H2O 的纯拓扑 D（欧氏但共线退化）" % r_deg)
rows_b.append(dict(n="(1,1,2)", r=r_deg))
P()
allone = all(abs(x["r"] - 1.0) < 1e-9 for x in rows_b)
P("  >>> A2 判据（恒 = 1 即『算法性质』）：%s" % ("成立" if allone else "不成立"))
P("      ⇒『反演忠诚 r=0.95~1.00』不是物理证据；它只说明输入 D 基本欧氏。")
P()
P("  逻辑补充（无需计算）：三条 D 里的 `weighted_bondlength` **按真实键长加权**，")
P("  即**已把实验几何从后门喂回输入**；再用它去反演并与真实几何比 ⇒ 必然高 r。")
P("  该分支**不构成独立检验**。")
OUT["A2"] = dict(rows=rows_b, verdict=bool(allone))

# ==================================================================
P()
P("=" * 78)
P("C  审计表：各验证条目的「对比目标」认识论类型")
P("=" * 78)
P()
P("  E = 独立实验外样本｜R = 反演量 / 模型依赖量｜C = 构造性 / 循环 / 回代")
P()
audit = [
    # (条目, 对比目标, 类型, 结果)
    ("P0 唯一性 (19320 图 -> 5 类)", "公理 (数学穷举)", "M", "成立"),
    ("R2 / R3 收敛与鲁棒性", "数值定理", "M", "成立"),
    ("L1 判据 n<=4 记分卡 8/8", "实测基态存在性", "E", "成立(事后读法)"),
    ("L1 外样本 A>=5 (26 项, 22/34)", "实测基态存在性", "E", "退化"),
    ("12.11 定价层证伪 (d/3H/3He/4He)", "实测结合能", "E", "判负(整类)"),
    ("12.12 lambda 阈值 vs B(4He)", "实测结合能", "E", "门槛被满足非被定住"),
    ("Pi1(Y3) vs kappa_N=(mn-mp)/mp", "CODATA 实测", "E", "偏 0.165%"),
    ("alpha = Pi1(M60) vs CODATA", "CODATA 实测", "E", "偏 1.45e-5"),
    ("12.15 L4 三目标 (mp/me, md/mp, mn/mp)", "CODATA 实测", "E", "判负"),
    ("13.3 指数律 + 物种消去律", "实测 T1/2 (Re/Dy/Pu)", "E", "律成立, 强读法判负"),
    ("维度塌缩 d(1->2)=0.352 a0", "实测键长", "E", "成立(离子对失效)"),
    ("判据(1) 锚 (2mu+md)/mp", "MS-bar 方案量", "R", "已降级为旁证"),
    ("MDS 反演苯/立方烷 (纯拓扑)", "实验几何(经 Pearson)", "R", "偏正(指标弱)"),
    ("MDS 反演 H2O", "实验几何(经 Pearson)", "C", "指标对键角盲"),
    ("H2O 104.474 度三元组", "混用 r_e 与 r0", "C", "差 0.146 度"),
    ("t=1.5811 <-> 104.4739 逐位吻合", "自身回代 + cos= -1/4", "C", "零预测"),
    ("v1 C5  N_p ~ 5.446e19", "循环自证", "C", "已登记"),
]
P("  %-40s %-24s %4s %s" % ("条目", "对比目标", "类型", "结果"))
P("  " + "-" * 96)
cnt = {"E": 0, "R": 0, "C": 0, "M": 0}
for name, target, typ, res in audit:
    cnt[typ] += 1
    P("  %-40s %-24s %4s %s" % (name, target, typ, res))
P()
P("  计数：E = %d ｜ R = %d ｜ C = %d ｜ M(纯数学) = %d" % (cnt["E"], cnt["R"], cnt["C"], cnt["M"]))
P()
# 判据 B：C/R 是否全部落在几何-形状一支？
geom_items = {"MDS 反演苯/立方烷 (纯拓扑)", "MDS 反演 H2O",
              "H2O 104.474 度三元组", "t=1.5811 <-> 104.4739 逐位吻合",
              "v1 C5  N_p ~ 5.446e19", "判据(1) 锚 (2mu+md)/mp"}
cr = [a for a in audit if a[2] in ("C", "R")]
cr_in_geom = [a for a in cr if a[0] in geom_items]
verdict_b = (len(cr_in_geom) == len(cr))
P("  >>> B 判据（C/R 是否全在几何-形状一支）：%s" % ("成立" if verdict_b else "不成立"))
P("      ⇒ 结论的正确表述：**不是「整条验证路线」用了推算结果**，而是")
P("        **几何/形状这一支的『验证』退化为构造性自洽**；")
P("        而谱层/数值一支（L1 外样本、四核结合能、L4 三目标、T1/2、alpha）")
P("        确实拿的是**真实验值**——并且正因为如此，它们**成串判负**。")
OUT["B"] = dict(counts=cnt, audit=[dict(item=a[0], target=a[1], type=a[2], result=a[3])
                                   for a in audit], verdict=bool(verdict_b))

# ==================================================================
P()
P("=" * 78)
P("D  由此逼出的「合格性三判据」（可作为对历史结论的筛子）")
P("=" * 78)
P()
crit = [
    ("① 外样本性", "对比目标必须是**独立实验量**，且**未被用于构图/构参**。"
                   "凡输入里已含该量（如按真实键长加权的 D）⇒ 循环，不计。"),
    ("② 非退化性", "待检量必须有**非零预测余量**：不能是恒等式的改写、回代，"
                   "或低自由度下的构造性复原（n=3 距离集、r=1 的 MDS）。"),
    ("③ 窗宽挂钩", "容差须与已证精度同量级（G4）；3% 窗宽不构成证据。"),
]
for k, v in crit:
    P("  %s：%s" % (k, v))
P()
P("  按这三条重筛：几何/形状一支**目前 0 条合格**（MDS 的 D 要么含实验键长、")
P("  要么纯拓扑而在 H2O 上失败；指标本身在低 n 退化）。")
P("  ⇒ 该支的**修复方向**：① 用纯拓扑 D、② 停在 n>=4、③ 判据改为**直接比夹角/键长**")
P("     （如苯比 120 度、立方烷比 90 度），而不是比『全距离集的 Pearson』。")
OUT["criteria"] = [dict(name=k, text=v) for k, v in crit]

with open("_validation_metric_audit.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
with open("_validation_metric_audit.log", "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
P()
P("[已写出 _validation_metric_audit.log / .json]")
