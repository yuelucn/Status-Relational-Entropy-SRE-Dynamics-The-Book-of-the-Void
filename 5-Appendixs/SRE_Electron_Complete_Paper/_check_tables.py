# -*- coding: utf-8 -*-
"""校验 markdown 表格列数（只计未转义的竖线）"""
import io, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def count_pipes(line):
    s = line.replace("\\|", "")           # 去掉转义竖线
    return s.count("|")


def check(path):
    t = io.open(path, encoding="utf-8").read().splitlines()
    bad = []
    i = 0
    while i < len(t):
        h = t[i].strip()
        if h.startswith("|") and i + 1 < len(t) and re.match(r"^\|[\s:\-|]+\|$", t[i + 1].strip()):
            n = count_pipes(h)
            j = i + 2
            while j < len(t) and t[j].strip().startswith("|"):
                m = count_pipes(t[j].strip())
                if m != n:
                    bad.append((j + 1, n, m, t[j].strip()[:110]))
                j += 1
            i = j
        else:
            i += 1
    return bad


for p in ["SRE_Nucleon_Complete_Paper.md", "SRE_Nucleon_Complete_Paper_EN.md"]:
    b = check(p)
    print("%s -> mismatches: %d" % (p, len(b)))
    for L, n, m, txt in b:
        print("   L%-5d exp=%-3d got=%-3d | %s" % (L, n, m, txt))
