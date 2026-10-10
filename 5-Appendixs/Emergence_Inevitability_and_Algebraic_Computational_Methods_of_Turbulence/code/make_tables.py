"""Render phase_data_v2.json as markdown tables for direct use in the paper."""
import json

d = json.load(open("C:/mywork/wei/phase_data_v2.json", encoding="utf-8"))
L = []

def f(v, spec="%.4f"):
    """Render a possibly-null (NaN in the source data) value."""
    return "—" if v is None else spec % v


for mode, title in (("exogenous", "模式 A：外生 Λ（p = 1 − 1/(1 + Λ·D_s/𝔅)）"),
                    ("adaptive", "模式 B：Λ × λ(n) 自适应（Theorem 7 接入）")):
    rows = d["modes"][mode]
    L.append("### " + title)
    L.append("")
    L.append("| Λ | Re ∝ 1/Λ | 结构密度 | sd | 各向异性 | sd | 谱斜率 | sd |")
    L.append("|---:|---:|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        L.append("| %.4g | %.4g | %s | %s | %s | %s | %s | %s |" % (
            r["lam"], r["re"],
            f(r["frac_neg"]), f(r["frac_neg_sd"]),
            f(r["anisotropy"]), f(r["anisotropy_sd"]),
            f(r["slope"], "%+.3f"), f(r["slope_sd"], "%.3f")))
    L.append("")

L.append("### 有限尺寸检验（模式 A，外生 Λ）")
L.append("")
L.append("| N | Λ | 结构密度 | 谱斜率 | 各向异性 |")
L.append("|---:|---:|---:|---:|---:|")
for r in d["finite_size"]:
    L.append("| %d | %g | %.4f | %+.3f | %.4f |" % (
        r["n"], r["lam"], r["frac_neg"], r["slope"], r["anisotropy"]))
L.append("")

open("C:/mywork/wei/tables.md", "w", encoding="utf-8").write("\n".join(L))
print("wrote tables.md")
