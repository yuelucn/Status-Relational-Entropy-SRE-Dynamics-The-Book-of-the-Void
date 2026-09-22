"""End-to-end audit: every number printed in the papers must exist in the dataset.

Parses the tables of main_CN.md / main_EN.md (papers) and tables_CN.md /
tables_EN.md (data appendix), and checks each row against the authoritative
dataset data/phase_data_v2.json. Reports any mismatch beyond rounding tolerance.

Run from anywhere:  python code/audit.py
"""
import json
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "phase_data_v2.json")
OUT = os.path.join(ROOT, "papers", "audit_result.txt")

D = json.load(open(DATA, encoding="utf-8"))


def parse_lambda(cell):
    """'$10^{-4}$' -> 1e-4 ; '$3.16\\times10^{-1}$' -> 0.316 ; '$1$' -> 1.0"""
    s = cell.replace("$", "").replace("\\times", "*").replace("{", "").replace("}", "")
    s = s.replace("^", "**").replace(" ", "")
    try:
        return float(eval(s, {"__builtins__": {}}, {}))
    except Exception:
        m = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
        return float(m[0]) if m else None


def num(cell):
    s = cell.replace("\u2212", "-").replace("$", "").strip()
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    return float(m.group(0)) if m else None


def rows_of(md, header_marker):
    """Extract data rows of the markdown table that follows header_marker."""
    lines = md.split("\n")
    i = next(k for k, l in enumerate(lines) if header_marker in l)
    out = []
    for l in lines[i:]:
        if not l.strip().startswith("|"):
            if out:
                break
            continue
        cells = [c for c in l.split("|")]
        if len(cells) < 5:
            continue
        # skip the |---:|---:| separator row (every body cell made of - and :)
        if all(set(c.strip()) <= set("-: ") for c in cells[1:]):
            continue
        # skip the header row
        if any(c.strip() in ("\u039b", "$\\Lambda$") for c in cells):
            continue
        out.append(cells)
    return out


def nearest(rows, lam):
    return min(rows, key=lambda r: abs(math.log10(r["lam"]) - math.log10(lam)))


def check(path, mode, marker, cols, tol):
    md = open(path, encoding="utf-8").read()
    ref = D["modes"][mode]
    problems, checked = [], 0
    for cells in rows_of(md, marker):
        lam = parse_lambda(cells[1])
        if lam is None or lam <= 0:
            continue
        r = nearest(ref, lam)
        if abs(math.log10(r["lam"]) - math.log10(lam)) > 0.02:
            problems.append("no dataset row near Lambda=%g" % lam)
            continue
        for ci, key in cols:
            if ci >= len(cells):
                continue
            v = num(cells[ci])
            if v is None:
                continue
            rv = r.get(key)
            if rv is None:
                problems.append("Lambda=%.4g %s: paper=%s dataset=null" % (lam, key, v))
                continue
            if abs(v - rv) > tol.get(key, 0.0006):
                problems.append("Lambda=%.4g %s: paper=%.4f dataset=%.4f" % (lam, key, v))
            checked += 1
    return checked, problems


# (column index inside the split row, dataset key)
# main papers §6.2: | Lambda | Re | density | sd | anisotropy | slope | sd |
COLS_MAIN = [(3, "frac_neg"), (5, "anisotropy"), (6, "slope")]
# main papers §6.3: | Lambda | density | slope |
COLS_MODEB = [(2, "frac_neg"), (3, "slope")]
# data appendix: | Lambda | Re | density | sd | anisotropy | sd | slope | sd |
COLS_TABLES = [(3, "frac_neg"), (5, "anisotropy"), (7, "slope")]
TOL = {"frac_neg": 0.0006, "anisotropy": 0.0006, "slope": 0.0006}

P = os.path.join(ROOT, "papers")
TARGETS = [
    (os.path.join(P, "main_CN.md"), "exogenous", "### 6.2", COLS_MAIN, "CN", "6.2", "A"),
    (os.path.join(P, "main_CN.md"), "adaptive", "### 6.3", COLS_MODEB, "CN", "6.3", "B"),
    (os.path.join(P, "main_EN.md"), "exogenous", "### 6.2", COLS_MAIN, "EN", "6.2", "A"),
    (os.path.join(P, "main_EN.md"), "adaptive", "### 6.3", COLS_MODEB, "EN", "6.3", "B"),
    (os.path.join(P, "tables_CN.md"), "exogenous", "### 模式 A", COLS_TABLES, "CN", "appx", "A"),
    (os.path.join(P, "tables_CN.md"), "adaptive", "### 模式 B", COLS_TABLES, "CN", "appx", "B"),
    (os.path.join(P, "tables_EN.md"), "exogenous", "### Mode A", COLS_TABLES, "EN", "appx", "A"),
    (os.path.join(P, "tables_EN.md"), "adaptive", "### Mode B", COLS_TABLES, "EN", "appx", "B"),
]

TEXT = {
    "CN": {
        "title": "SRE v2 端到端一致性审计",
        "src": "数据集：data/phase_data_v2.json",
        "scope": "覆盖范围：主论文中英两版 §6.2/§6.3 + 数据附表中英两版，共 8 张表。",
        "row": "%-22s : 核验 %2d 个数值，%d 处不一致",
        "tot": "合计：核验 %d 个数值，%d 处不一致",
        "ok": "结论：一致（CONSISTENT）",
        "bad": "结论：不一致（INCONSISTENT）",
        "file": lambda lg, sec, md: "main_%s.md §%s 模式 %s" % (lg, sec, md) if sec != "appx"
        else "tables_%s.md 模式 %s" % (lg, md),
    },
    "EN": {
        "title": "SRE v2 end-to-end consistency audit",
        "src": "dataset: data/phase_data_v2.json",
        "scope": "Scope: main paper (CN + EN) §6.2/§6.3 and data appendix (CN + EN), 8 tables in total.",
        "row": "%-22s : checked %2d values, %d mismatch",
        "tot": "TOTAL: %d values checked, %d mismatches",
        "ok": "RESULT: CONSISTENT",
        "bad": "RESULT: INCONSISTENT",
        "file": lambda lg, sec, md: "main_%s.md §%s mode %s" % (lg, sec, md) if sec != "appx"
        else "tables_%s.md mode %s" % (lg, md),
    },
}

# run every check once; each language report then renders the full set
CHECKED = []
for path, mode, marker, cols, lang, sec, mdl in TARGETS:
    c, p = check(path, mode, marker, cols, TOL)
    CHECKED.append((lang, sec, mdl, c, p))

for lang in ("CN", "EN"):
    t = TEXT[lang]
    report = [t["title"], "", t["src"], "",
              t["scope"]]
    total = 0
    bad = 0
    for slang, sec, mdl, c, p in CHECKED:
        total += c
        bad += len(p)
        report.append(t["row"] % (TEXT[lang]["file"](slang, sec, mdl), c, len(p)))
        for x in p:
            report.append("    ! " + x)
    report.append("")
    report.append(t["tot"] % (total, bad))
    report.append(t["ok"] if bad == 0 else t["bad"])
    txt = "\n".join(report)
    out = OUT.replace("audit_result.txt", "audit_result_%s.txt" % lang)
    open(out, "w", encoding="utf-8").write(txt)
    print(txt)
    print()
