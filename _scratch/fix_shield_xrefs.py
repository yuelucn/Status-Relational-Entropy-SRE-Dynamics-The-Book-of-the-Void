"""Fix stale cross-references to the turbulence paper in the Gravitational Shielding chapter."""
import os

B = r"c:\mywork\SRE-Dynamics"
A4 = os.path.join(B, "4-Applications&Hypothesis")
CN = os.path.join(A4, "Hypothesis_of_Gravitational_Shielding_Derivation(SRE)_1.0_C.md")
EN = os.path.join(A4, "Hypothesis_of_Gravitational_Shielding_Derivation(SRE)_1.0_E.md")

NEW_CN_SHORT = "《N–S 湍流基准报告》"
NEW_CN_FULL = "《用离散因果网络对标经典 Navier–Stokes 湍流》"
NEW_EN_SHORT = "*N–S Turbulence Benchmark*"
NEW_EN_FULL = "《Benchmarking Classical Navier–Stokes Turbulence with a Discrete Causal Network》"


def rt(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def wt(p, s):
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))


CN_REPL = [
    # vocabulary-table cell 3
    ("§4.1 算子 1：边界扩张；§4.2 算子 2：极大熵剪枝；§4.3 增益 $\\Gamma$：外生 $\\Lambda$ 与内生 $\\lambda(n)$",
     "§2.3 算子 1（边界扩张）与算子 2（极大熵剪枝）；§2.4 剪枝增益 $\\Gamma$ 与控制量 $\\Lambda$"),
    # full title
    ("《基于离散微观因果统计与多维流形重构的湍流涌现必然性及代数计算方法》", NEW_CN_FULL),
    # ranges first
    ("《湍流涌现必然性》§4.2–§4.3", NEW_CN_SHORT + "§2.3–§2.4"),
    ("《湍流涌现必然性》§4.1", NEW_CN_SHORT + "§2.3"),
    ("《湍流涌现必然性》§4.2", NEW_CN_SHORT + "§2.3"),
    ("《湍流涌现必然性》§4.3", NEW_CN_SHORT + "§2.4"),
    ("《湍流涌现必然性》", NEW_CN_SHORT),
]

EN_REPL = [
    ("§4.1 Operator 1: boundary expansion; §4.2 Operator 2: maximum-entropy pruning; §4.3 Gain $\\Gamma$: exogenous $\\Lambda$ and endogenous $\\lambda(n)$",
     "§2.3 Operator 1 (boundary expansion) and Operator 2 (maximum-entropy pruning); §2.4 pruning gain $\\Gamma$ and control quantity $\\Lambda$"),
    ("《The Necessity of Turbulence Emergence and an Algebraic Computation Method Based on Discrete Microscopic Causal Statistics and Multidimensional Manifold Reconstruction》", NEW_EN_FULL),
    ("基于离散微观因果统计与多维流形重构的湍流涌现必然性及代数计算方法", "用离散因果网络对标经典 Navier–Stokes 湍流"),
    ("*Necessity of Turbulence Emergence* §4.2–§4.3", NEW_EN_SHORT + " §2.3–§2.4"),
    ("*Necessity of Turbulence Emergence* §4.1", NEW_EN_SHORT + " §2.3"),
    ("*Necessity of Turbulence Emergence* §4.2", NEW_EN_SHORT + " §2.3"),
    ("*Necessity of Turbulence Emergence* §4.3", NEW_EN_SHORT + " §2.4"),
    ("《Necessity of Turbulence Emergence》", "《N–S Turbulence Benchmark》"),
    ("*Necessity of Turbulence Emergence*", NEW_EN_SHORT),
]

for path, repls in ((CN, CN_REPL), (EN, EN_REPL)):
    t = rt(path)
    total = 0
    for old, new in repls:
        n = t.count(old)
        if n == 0:
            print("MISS", repr(old[:60]))
            continue
        t = t.replace(old, new)
        total += n
        print("  %2d x %s" % (n, old[:52]))
    wt(path, t)
    print("OK", os.path.basename(path), "replacements:", total)
    for bad in ("§4.1", "§4.2", "§4.3"):
        left = t.count(bad)
        if left:
            print("   remaining %s: %d" % (bad, left))
print("DONE")
