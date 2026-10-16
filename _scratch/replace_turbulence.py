"""Replace the Turbulence chapter 3.0 with the new 4.0 sources from C:\\mywork\\wei."""
import os
import re
import subprocess

SRC = r"c:\mywork\wei"
B = r"c:\mywork\SRE-Dynamics"
CH = os.path.join(B, "2-Everything_Emerges")
BASE = "Emergence_Inevitability_and_Algebraic_Computational_Methods_of_Turbulence"
AUTHOR_RE = {
    "C": re.compile(r"^\s*(?:\*\*)?作者(?:\*\*)?\s*[:：]"),
    "E": re.compile(r"^\s*(?:\*\*)?Author(?:\*\*)?\s*[:：]"),
}


def rt(p):
    with open(p, "rb") as f:
        return f.read().decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")


def wt(p, s):
    with open(p, "wb") as f:
        f.write(s.encode("utf-8"))


def count_h1(text):
    h1 = 0
    fence = False
    for ln in text.split("\n"):
        if ln.lstrip().startswith("```"):
            fence = not fence
            continue
        if fence:
            continue
        if re.match(r"^# ", ln):
            h1 += 1
    return h1


for lang in ("C", "E"):
    body = rt(os.path.join(SRC, "n-s_%s_4.0.md" % lang))
    lines = body.split("\n")

    # collapse blank runs inside the header (everything before the first '---')
    try:
        cut = lines.index("---")
    except ValueError:
        cut = min(len(lines), 30)
    head, rest = lines[:cut], lines[cut:]
    head = [ln for ln in head if not AUTHOR_RE[lang].match(ln)]
    out = []
    for ln in head:
        if ln.strip() == "" and out and out[-1].strip() == "":
            continue
        out.append(ln)
    lines = out + rest

    text = "\n".join(lines)
    assert count_h1(text) == 1, (lang, count_h1(text))

    new = os.path.join(CH, "%s_4.0_%s.md" % (BASE, lang))
    old = os.path.join(CH, "%s_3.0_%s.md" % (BASE, lang))
    wt(new, text)
    os.remove(old)
    print("OK replace", lang, "->", os.path.basename(new))

# update file_order
for lang in ("C", "E"):
    fp = os.path.join(B, "file_order_%s.txt" % lang)
    t = rt(fp)
    t2 = t.replace("%s_3.0_%s.md" % (BASE, lang), "%s_4.0_%s.md" % (BASE, lang))
    assert t2 != t, fp
    wt(fp, t2)
    print("OK file_order", lang)

# update Part-2 abstract item 6
NEW_C = (
    "6. **用离散因果网络对标经典 Navier–Stokes 湍流（v4.0 系统基准报告）**：把 SRE 网络当作可执行的数值实验对象，"
    "在统一协议下测量其宏观可观测量，并与经典湍流现象学（K41 能量级联、−5/3 谱、3/4 律）逐项对标。"
    "以圆管转捩中心为锚点建立雷诺数映射 `Re ≈ 783/Λ`；强湍流侧手性场一维替代谱给出稳定幂律 "
    "`γ ≈ −1.81 ± 0.04`（与 K41 的 −1.667 相差约 9%，**不是**精确的 −5/3）；因果前沿剖面偏度沿层流→湍流"
    "严格经历 `+ → 0 → −` 过零，但量级差约一个数量级；相干分数 C 从 ≈0.97 单调降至 ≈0.09；"
    "尺度分离指数 β 随 N（800→25600）单调下降（0.7456→0.4360）且收敛极慢，六点链落在“对数型（β∞≈0）”"
    "与“弱幂律（p≈0.28）”的简并区，仅能给出区间约束 `β∞ ∈ [−0.2, +0.2]`。结论：SRE 网络在定性上复现经典湍流"
    "主叙事，定量上稳定偏离 K41 精确幂律，是一个尚未收敛、但结构自洽的离散代理模型。全文自包含，"
    "附录 A 给出术语标准化对照表、附录 B 给出数值出处表。"
)
NEW_E = (
    "6. **Benchmarking Classical Navier–Stokes Turbulence with a Discrete Causal Network (v4.0 systematic "
    "benchmark report)**: Treats the SRE network as an executable numerical-experiment object, measures its "
    "macroscopic observables under a unified protocol, and benchmarks them item by item against classical "
    "turbulence phenomenology (the K41 energy cascade, the −5/3 spectrum, the 3/4 law). A Reynolds-number mapping "
    "`Re ≈ 783/Λ` is anchored at the pipe-transition centre; on the strong-turbulence side the surrogate "
    "one-dimensional chiral-field spectrum yields a stable power law `γ ≈ −1.81 ± 0.04` (about 9% away from K41's "
    "−1.667, **not** the exact −5/3); the causal-front skewness strictly crosses zero `+ → 0 → −` along the "
    "laminar→turbulent direction, though its magnitude differs by about one order; the coherent fraction C falls "
    "monotonically from ≈0.97 to ≈0.09; the scale-separation exponent β decreases monotonically with N "
    "(800→25600) from 0.7456 to 0.4360 and converges extremely slowly, the six-point chain lying in a "
    "**degenerate zone** between a logarithmic form (β∞ ≈ 0) and a weak power law (p ≈ 0.28), so that only the "
    "interval constraint `β∞ ∈ [−0.2, +0.2]` can be given. Conclusion: the SRE network qualitatively reproduces "
    "the classical turbulence narrative while quantitatively deviating stably from the exact K41 power laws—a "
    "discrete surrogate model that has not yet converged but is structurally self-consistent. The report is "
    "self-contained, with Appendix A providing a standardized terminology table and Appendix B a table of "
    "numerical provenance."
)
for lang, newtext in (("C", NEW_C), ("E", NEW_E)):
    fp = os.path.join(CH, "0\u2011Abstract_Part_2_%s.md" % lang)
    lines = rt(fp).split("\n")
    idx = [i for i, ln in enumerate(lines) if ln.startswith("6. **")]
    assert len(idx) == 1, (fp, idx)
    old_line = lines[idx[0]]
    assert "v3.0" in old_line or "v3" in old_line, old_line[:80]
    lines[idx[0]] = newtext
    wt(fp, "\n".join(lines))
    print("OK abstract", lang)

print("DONE")
