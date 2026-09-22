# -*- coding: utf-8 -*-
"""讨论用临时分析：核物理可借用数据的无量纲筛选。
不产出论文文件，仅用于支撑讨论。
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

M_P, M_N, M_E = 938.27208816, 939.56542052, 0.51099895000
DM = M_N - M_P
ALPHA = 1.0 / 137.035999084
AM_P = ALPHA * M_P
RHO = (7 + 13 ** 0.5) / 2.0
PI1 = (7 - 13 ** 0.5) / 18.0
KAPPA = (DM / M_P) / ALPHA


def sec(t):
    print("\n" + "=" * 74 + "\n" + t + "\n" + "=" * 74)


sec("[0] SRE 核子侧已有的两个自然能量标度")
print("  dm_np = m_n - m_p        = %.8f MeV   (闭合度差 1 的释能)" % DM)
print("  dm_np / m_p              = %.8e" % (DM / M_P))
print("  kappa = (dm/m_p)/alpha   = %.9f" % KAPPA)
print("  Pi1 = (7-sqrt13)/18      = %.9f   dev %.4f%%" % (PI1, 100 * abs(PI1 - KAPPA) / KAPPA))
print("  alpha * m_p              = %.6f MeV   (电子标度的核子化)" % AM_P)
print("  rho = (7+sqrt13)/2       = %.9f" % RHO)

# 结合能 MeV（AME2020 量级）
NUC = {
    "d":     (2,   1,    2.224566),
    "t":     (3,   1,    8.481798),
    "he3":   (3,   2,    7.718043),
    "he4":   (4,   2,   28.2957),
    "li6":   (6,   3,   31.9945),
    "c12":   (12,  6,   92.1617),
    "o16":   (16,  8,  127.6193),
    "ca40":  (40, 20,  342.0513),
    "ca48":  (48, 20,  415.99),
    "ni62":  (62, 28,  545.26),
    "fe56":  (56, 26,  492.2539),
    "pb208": (208, 82, 1636.43),
    "u238":  (238, 92, 1801.6935),
}

sec("[1] 结合能，换算为 SRE 的两种单位")
print("  %-7s %5s %5s %10s %11s %11s %10s" %
      ("nucl", "A", "Z", "B(MeV)", "B/dm_np", "(B/A)/dm", "B/(a*m_p)"))
for k, (A, Z, Bv) in NUC.items():
    print("  %-7s %5d %5d %10.4f %11.4f %11.4f %10.4f" %
          (k, A, Z, Bv, Bv / DM, (Bv / A) / DM, Bv / AM_P))

sec("[2] 每核子结合能（饱和问题）")
for k in ["d", "he4", "c12", "o16", "fe56", "ni62", "u238"]:
    A, Z, Bv = NUC[k]
    print("  %-6s  B/A = %7.4f MeV | (B/A)/dm = %7.4f | (B/A)/(a*m_p) = %7.4f"
          % (k, Bv / A, (Bv / A) / DM, (Bv / A) / AM_P))

fe_ba = NUC["fe56"][2] / 56
ni_ba = NUC["ni62"][2] / 62
peak = max(fe_ba, ni_ba)
print()
print("  峰值 B/A (Fe56=%.4f, Ni62=%.4f) 取 %.4f MeV" % (fe_ba, ni_ba, peak))
print("  峰值 / dm_np            = %.6f   (vs beta1 = 7 , dev %.3f%%)"
      % (peak / DM, 100 * abs(peak / DM - 7) / 7))
print("  峰值 / (alpha*m_p)      = %.6f   (vs 9/7 = %.6f , dev %.3f%%)"
      % (peak / AM_P, 9 / 7, 100 * abs(peak / AM_P - 9 / 7) / (9 / 7)))
print("  峰值 / (alpha*m_p)      = %.6f   (vs 1 , dev %.3f%%)"
      % (peak / AM_P, 100 * abs(peak / AM_P - 1)))
print("  B(He4)/B_d              = %.6f" % (NUC["he4"][2] / NUC["d"][2]))
print("  B(He4)/dm_np            = %.6f   (vs 4*rho = %.5f , dev %.2f%%)"
      % (NUC["he4"][2] / DM, 4 * RHO,
         100 * abs(NUC["he4"][2] / DM - 4 * RHO) / (4 * RHO)))
print("  核物质饱和 E/A = -16 MeV -> |E/A|/(alpha*m_p) = %.4f ; /dm = %.4f"
      % (16.0 / AM_P, 16.0 / DM))

sec("[3] 氘核（唯一束缚两体系统）")
Bd = NUC["d"][2]
print("  B_d                     = %.6f MeV" % Bd)
print("  B_d / dm_np             = %.6f" % (Bd / DM))
print("     候选 sqrt3 = %.6f (dev %.3f%%) ; 12/7 = %.6f (dev %.3f%%) ; lam3_A = 1.697224 (dev %.3f%%)"
      % (3 ** 0.5, 100 * abs(Bd / DM - 3 ** 0.5) / 3 ** 0.5,
         12 / 7, 100 * abs(Bd / DM - 12 / 7) / (12 / 7),
         100 * abs(Bd / DM - 1.697224) / 1.697224))
print("  B_d / m_p               = %.8e" % (Bd / M_P))
print("  B_d / m_e               = %.4f" % (Bd / M_E))
SC = {"np_t": 5.4194, "np_s": -23.748, "nn": -18.5, "pp": -17.3}
print("  散射长度 fm:", SC)
print("  a_s/a_t = %.6f ; a_nn/a_t = %.6f ; a_pp/a_t = %.6f"
      % (SC["np_s"] / SC["np_t"], SC["nn"] / SC["np_t"], SC["pp"] / SC["np_t"]))
print("  束缚态存在性: np(T=0,S=1)=有 ; np(T=1,S=0)/nn/pp = 无(虚态)")
print("  电磁: Q_d = +0.2859 fm^2 (非零 -> 共享单元有取向)")
mu_p, mu_n, mu_d = 2.79284734, -1.91304273, 0.85743823
print("        mu_p+mu_n = %.6f ; mu_d = %.6f ; 差 = %+.6f (%.2f%%)"
      % (mu_p + mu_n, mu_d, mu_d - (mu_p + mu_n), 100 * (mu_d - (mu_p + mu_n)) / (mu_p + mu_n)))

sec("[4] 半经验质量公式的计数结构（Bethe-Weizsacker）")
aV, aS, aC, aA, aP = 15.75, 17.8, 0.711, 23.7, 11.18
print("  B = aV*A - aS*A^(2/3) - aC*Z(Z-1)/A^(1/3) - aA*(N-Z)^2/A + delta")
print("  aV=%.2f aS=%.2f aC=%.3f aA=%.2f aP=%.2f MeV" % (aV, aS, aC, aA, aP))
for k in ["he4", "fe56", "u238"]:
    A, Z, Bv = NUC[k]
    N = A - Z
    tV = aV * A
    tS = -aS * A ** (2 / 3)
    tC = -aC * Z * (Z - 1) / A ** (1 / 3)
    tS2 = -aA * (N - Z) ** 2 / A
    print("   %-6s A=%3d Z=%3d: V=%8.2f S=%8.2f C=%8.2f sym=%8.2f sum=%8.2f (B=%.1f)"
          % (k, A, Z, tV, tS, tC, tS2, tV + tS + tC + tS2, Bv))
print()
print("  库仑项用 Z(Z-1) 而非 Z^2  -> 两两对数 C(Z,2)，非独立叠加")
print("  对称项 (N-Z)^2/A 二次且平滑 -> 开闭计数失配的二阶展开")
print("  对能项 delta = +-aP/sqrt(A):")
for A in [2, 4, 56, 238]:
    print("     A=%3d : |delta| = %.4f MeV" % (A, aP / A ** 0.5))

sec("[5] 几何标度（A^(1/3) 的维度含义）")
for k in ["he4", "fe56", "pb208"]:
    A = NUC[k][0]
    print("  %-6s A=%3d  A^(1/3)=%6.3f  A^(2/3)=%7.2f  表面/体积=A^(-1/3)=%.4f"
          % (k, A, A ** (1 / 3), A ** (2 / 3), A ** (-1 / 3)))

sec("[6] 壳模型魔数（闭合单元容量序列）")
magic = [2, 8, 20, 28, 50, 82, 126]
inc = [magic[0]] + [magic[i] - magic[i - 1] for i in range(1, len(magic))]
print("  魔数   :", magic)
print("  增量   :", inc)
print("  2j+1 容量序列: 2,4,2,6,2,4,8,4,6,2,10,...（偶数）")
print("  对照电子侧通道容量: 14/15 族 = 3, 16 族 = 2, 17 族 = 1")

sec("[7] 核力强度的其他经典表征")
print("  对称能 S_v      = ~32 MeV    -> /dm = %.3f ; /(a*m_p) = %.3f"
      % (32.0 / DM, 32.0 / AM_P))
print("  不可压缩性 K    = ~240 MeV   -> /dm = %.2f ; /(a*m_p) = %.2f"
      % (240.0 / DM, 240.0 / AM_P))
print("  g_A             = 1.2756     (夸克模型 5/3 = 1.6667)")
print("  piN 耦合 g^2/4pi = ~14       (耦合常数, 非比)")
print("  核物质 n0       = 0.16 fm^-3")
print()
print("  镜像核 3H/3He: B(t)-B(he3) = %.4f MeV (主为库仑差)"
      % (NUC["t"][2] - NUC["he3"][2]))
print("  核质量差 = dm_np + B(he3)-B(t) = %.4f MeV" % (DM + NUC["he3"][2] - NUC["t"][2]))
print("  原子质量差(含电子) = 上式 - m_e = %.4f MeV (实测 Q_beta = 0.01859)"
      % (DM + NUC["he3"][2] - NUC["t"][2] - M_E))

sec("[8] 多重比较风险速估")
print("  若在 N 个观测与 M 个图量间做全部配对、阈值 eps：")
for N, M, eps in [(6, 16, 0.02), (20, 30, 0.01), (20, 30, 0.005)]:
    print("    N=%2d M=%2d eps=%.3f -> 比较数=%d, 偶然命中期望=%.1f"
          % (N, M, eps, N * M * 2, N * M * 2 * eps))
print("  注：只有\"先验给出数值再对实验\"才算验证；事后配对全是线索。")
print("\n[done]")
