# -*- coding: utf-8 -*-
"""
_sre_h2o_geometry_provenance.py  —  H2O 键角 104 度「是怎么得到的」复核（纯 numpy）

缘起（2026-09-24 第二十一轮）：用户问「这个 104 弯曲是如何得到的」。
本脚本不复算 `_sre_h2o_degeneracy.py` 的图侧结论，只查**测量/数值的出处**，
并登记两处诚实问题（内部不自洽 + 数值巧合）。

预注册判据（先于任何数值写死在代码里）
------------------------------------------------------------------
Q1 实验链再现：由文献转动常数 (A,B,C) 以**刚性转子**反演 (r, theta)；
   与文献**平衡几何** (r_e, theta_e) 对比。
   判据：若两者不一致 > 0.1 度 ⇒ 「常数 -> 几何」这一步是**模型输入**，
        不是测量直读（该差值 = 转动-振动/非谐修正步的大小）。
Q2 项目三元组自洽性：`_sre_h2o_degeneracy.py` PART 4 用了
   r(O-H)=0.9584 A、r(H...H)=1.51383 A、theta_exp=104.474 度。
   判据：三者的闭合角度若偏离所标角度 > 0.05 度 ⇒ 登记为**内部不自洽**。
Q3 巧合量化：项目 PART 2 用 t=1.5811。核算 t ≡ 2*sin(theta/2)（归一化后
   与 r 无关），并检验 cos(theta_real) 是否近似 -1/4（即 t 是否近似 sqrt(2.5)）。
   判据：若 |t - sqrt(2.5)| < 1e-3 且 |cos(theta_real) + 0.25| < 1e-3
        ⇒ 登记为**数值巧合**，不得当作「图预言了水角」的证据。
"""
import json
from math import sqrt, sin, cos, atan2, degrees, radians, acos, pi

K = 16.857629          # B[cm^-1] = K / I[amu*A^2]   (h / 8*pi^2*c)
mH = 1.0078250319      # amu
mO = 15.9949146221     # amu

OUT = {}
L = []


def P(s=""):
    print(s)
    L.append(s)


def inertia(r, theta_deg):
    """C2v 平面三原子：O 在原点，H 在 (v,0,u)/(−v,0,u)，边长 r、顶角 theta。
    返回升序主转动惯量 [I_A, I_B, I_C]（amu*A^2）。"""
    a = radians(theta_deg) / 2.0
    v = r * sin(a)                 # = r*sin(theta/2)，H 到 C2 轴的距离
    u = r * cos(a)                 # H 的 C2 方向坐标
    beta = 2.0 * mH / (mO + 2.0 * mH)
    Zc = beta * u                  # 质心在 C2 轴上
    Izz = 2.0 * mH * v * v                     # 绕 C2 轴
    Iyy = mO * Zc * Zc + 2.0 * mH * (u - Zc) ** 2   # 面内、垂直 C2
    Ixx = Iyy + Izz                            # 垂直分子面（垂直轴定理）
    return sorted([Ixx, Iyy, Izz])


def consts(I):
    """转动惯量 -> 转动常数 A,B,C (cm^-1)。I 升序 => A>=B>=C。"""
    return [K / x for x in I]


def invert_ABC(A, B):
    """刚性转子反演：由 (A,B) 解 (r, theta)。
    A <-> I_A(最小, 面内垂直 C2)；B <-> I_B(绕 C2)。闭式解。"""
    I_A = K / A
    I_B = K / B
    v = sqrt(I_B / (2.0 * mH))                     # I_B = 2*mH*v^2
    beta = 2.0 * mH / (mO + 2.0 * mH)
    den = mO * beta ** 2 + 2.0 * mH * (1.0 - beta) ** 2
    u = sqrt(I_A / den)                            # I_A = u^2 * den
    theta = 2.0 * degrees(atan2(v, u))
    r = sqrt(u * u + v * v)
    return r, theta


# ==================================================================
P("=" * 78)
P("Q1  实验链再现：转动常数 -> 刚性转子 -> 几何；以及『模型步』的大小")
P("=" * 78)
P()
P("  实验链（真实测到的永远是谱线频率）：")
P("    微波纯转动谱（气相，极性分子） -> 拟合出 A, B, C (cm^-1)")
P("    -> 转动惯量 I_A,B,C = K / (A,B,C)")
P("    -> [模型步] 刚性转子 + 振动/离心修正 -> r, theta")
P("    红外/拉曼 -> 力场；同位素取代 (D2O, T2O, HDO) -> 分离 r 与 theta")
P()

# 文献 A0,B0,C0（Herzberg 1966，经 CCCBDB 转载）
lit = dict(A=27.877, B=14.512, C=9.285)
r_inv, th_inv = invert_ABC(lit["A"], lit["B"])
I_inv = sorted([K / lit["A"], K / lit["B"], K / lit["C"]])

# 文献平衡几何（Hoy & Bunker 1979，经 CCCBDB 转载）
r_e, th_e = 0.9578, 104.4776
I_e = inertia(r_e, th_e)
ABC_e = consts(I_e)

P("  (a) 文献转动常数 (A0,B0,C0) = %.3f, %.3f, %.3f cm^-1   [Herzberg 1966]"
  % (lit["A"], lit["B"], lit["C"]))
P("      刚性转子反演 => r = %.4f A, theta = %.4f 度" % (r_inv, th_inv))
P()
P("  (b) 文献平衡几何        r_e = %.4f A, theta_e = %.4f 度   [Hoy & Bunker 1979]"
  % (r_e, th_e))
P("      正向计算 => (A,B,C) = %.3f, %.3f, %.3f cm^-1" % tuple(ABC_e))
P("      H...H = %.4f A" % (2.0 * r_e * sin(radians(th_e) / 2.0)))
P()

d_th = abs(th_inv - th_e)
d_r = abs(r_inv - r_e)
P("  (c) 差值：Δtheta = %.4f 度   Δr = %.5f A" % (d_th, d_r))
P("      两套平衡几何的文献值本身也在打架 [Cook/De Lucia/Helminger 1974 综述]：")
P("        1D 非谐近似还原的平衡结构 r_e = 0.9587 A, theta_e = 103.9 度")
P("        基态平均结构 <r>(O-H) = 0.9724 A, <HOH> = 104.50 度")
P("      => 同一分子的『角』在 103.9 ~ 104.5 度之间随平均约定移动。")
P()
q1 = d_th > 0.1
P("  >>> Q1 判据（> 0.1 度 即判『模型输入』）：Δtheta = %.4f 度  =>  %s"
  % (d_th, "模型输入成立" if q1 else "与直读无区别"))
P("      结论：A,B,C -> (r,theta) 这一步需要**外部模型**（刚性转子 + 转动-振动/")
P("      非谐修正 + 同位素取代），且不同平均约定给出不同的『角』。")
P("      ⇒ 与项目上一轮结论一致：测到的是**能量差（谱线）**，几何是**反演量**。")
OUT["Q1"] = dict(A0=lit, r_inv=r_inv, th_inv=th_inv, r_e=r_e, th_e=th_e,
                ABC_e_from_re=ABC_e, d_theta=d_th, d_r=d_r, verdict=bool(q1))

# ==================================================================
P()
P("=" * 78)
P("Q2  项目三元组 (0.9584, 1.51383, 104.474) 的内部自洽性")
P("=" * 78)
P()
r_OH, r_HH, th_lab = 0.9584, 1.51383, 104.474
t_used = r_HH / r_OH
th_closed = degrees(acos(max(-1.0, min(1.0, 1.0 - t_used ** 2 / 2.0))))
r_HH_need = 2.0 * r_OH * sin(radians(th_lab) / 2.0)
P("  脚本用的三个数：r(O-H)=%.4f  r(H...H)=%.5f  theta=%.3f" % (r_OH, r_HH, th_lab))
P("  归一化 t = r(H...H)/r(O-H) = %.6f" % t_used)
P("  由等腰三角闭式反推的角        = %.4f 度" % th_closed)
P("  要与 theta=%.3f 保持一致所需的 r(H...H) = %.5f A" % (th_lab, r_HH_need))
P()
d_q2 = abs(th_closed - th_lab)
P("  >>> 偏差 = %.4f 度" % d_q2)
P("      原因：0.9584 A 是 r_e 量级的值，而 1.51383 A 是 r0(基态平均)量级的 H...H；")
P("      把两个**不同平均约定**的数混用，闭合角就偏了 %.3f 度。" % d_q2)
P("      一致的 (r_e, r(H...H), theta_e) 三元组应为：")
P("        r(O-H)=%.4f  r(H...H)=%.4f  theta=%.4f  [Hoy & Bunker 1979]"
  % (r_e, 2.0 * r_e * sin(radians(th_e) / 2.0), th_e))
P()
q2 = d_q2 > 0.05
P("  >>> Q2 判据（> 0.05 度 即判『内部不自洽』）：%s" % ("成立（须登记）" if q2 else "通过"))
P("      登记：`_h2o_degeneracy.log` PART 4 把该处标为『自洽』，宜改为")
P("      『同量级、差 0.15 度（源于混用 r_e 与 r0）』。")
OUT["Q2"] = dict(r_OH=r_OH, r_HH=r_HH, theta_lab=th_lab, t_used=t_used,
                theta_closed=th_closed, rHH_needed=r_HH_need, d_theta=d_q2,
                verdict=bool(q2))

# ==================================================================
P()
P("=" * 78)
P("Q3  项目 t = 1.5811 的来源：它是**回代**，且撞上 cos(theta) ~ -1/4")
P("=" * 78)
P()
P("  归一化后 t 与 r 无关，恒有恒等式：")
P("      t = r(H...H)/r(O-H) = 2*sin(theta/2)     （等腰三角的纯几何恒等式）")
P()
P("  项目 PART 2 扫的是 t = [..., 1.5811, ...] 并宣称与 104.4739 度逐位吻合。")
P("  但 1.5811 = 2*sin(104.474/2) 的反函数值 —— **t 是由角度算出来的**，")
P("  所以『吻合』是回代，不是预言。")
P()
sqrt25 = sqrt(2.5)
t_from_real = 2.0 * sin(radians(th_e) / 2.0)
c = cos(radians(th_e))
P("  巧合量化：")
P("      sqrt(2.5)              = %.6f" % sqrt25)
P("      2*sin(theta_e/2)       = %.6f   （theta_e=%.4f 度）" % (t_from_real, th_e))
P("      差                     = %.6f" % abs(t_from_real - sqrt25))
P("      cos(theta_e)           = %+.6f" % c)
P("      cos(theta_e) + 0.25    = %+.6f" % (c + 0.25))
P("      => 水的角满足 cos(theta) ~ -1/4（= 1 - 2.5/2），")
P("         所以归一化 t 恰好近似 sqrt(2.5)，于是 1.5811 看起来『漂亮』。")
P()
q3 = (abs(t_from_real - sqrt25) < 1e-3) and (abs(c + 0.25) < 1e-3)
P("  >>> Q3 判据（两项都 < 1e-3 即判『数值巧合』）：%s"
  % ("成立（须登记为陷阱）" if q3 else "不成立"))
P("      ⇒ t=1.5811 既不是对水的预测，也不是对水的拟合；它是一个恒等式的数值改写。")
P("      ⇒ 与『塔上 Pi1(Q_k)=1/k 在 k=137 恰近似 1/137』同类：构造性巧合，不得当证据。")
OUT["Q3"] = dict(sqrt25=sqrt25, t_from_real=t_from_real,
                diff=abs(t_from_real - sqrt25), cos_theta=c,
                cos_plus_quarter=c + 0.25, verdict=bool(q3))

# ==================================================================
P()
P("=" * 78)
P("总表：H2O 与 H...H 的数值一览（全部可追溯）")
P("=" * 78)
P()
P("  %-34s %10s %10s %10s" % ("来源", "r(O-H)/A", "r(H...H)/A", "theta/度"))
P("  " + "-" * 68)
rows = [
    ("平衡 r_e [Hoy&Bunker 1979]", r_e, 2 * r_e * sin(radians(th_e) / 2), th_e),
    ("基态平均 <r> [Cook+ 1974]", 0.9724, None, 104.50),
    ("r_e 1D非谐近似 [Cook+ 1974]", 0.9587, None, 103.9),
    ("刚性转子反演 (A0,B0)", r_inv, None, th_inv),
    ("项目脚本 PART4 所用", r_OH, r_HH, th_lab),
]
for name, a, b, c_ in rows:
    P("  %-34s %10s %10s %10s"
      % (name, "%.4f" % a if a else "-", "%.4f" % b if b else "-",
         "%.4f" % c_ if c_ else "-"))
P()
P("  ⇒ 『104 度』不是一个直读数字：它随平均约定在 103.9 ~ 105.1 度之间，")
P("    收敛值 ≈ 104.5 度的是**基态平均**结构，104.478 度是**平衡**结构。")
P("  ⇒ 项目真正做到的是：证明『必须存在非键合 H...H 关系』（结构预言，非循环），")
P("    而该关系的**尺度** t 是外部输入（与 G12 一致）。")
OUT["table"] = [dict(src=n, rOH=a, rHH=b, theta=c_) for n, a, b, c_ in rows]

with open("_h2o_geometry_provenance.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, ensure_ascii=False, indent=2)
with open("_h2o_geometry_provenance.log", "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
P()
P("[已写出 _h2o_geometry_provenance.log / .json]")
