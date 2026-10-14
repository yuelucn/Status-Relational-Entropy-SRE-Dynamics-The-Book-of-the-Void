#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 math-graph / graph500 的最新更新同步进书。

范围：
  A. 算子10 论文（中/英）重新入书（去署名、闭源→开源、单 H1）
  B. 算子10 相关算法程序（Operator_10_P.py / sre_commercial_core.py）
  C. Graph500 章节 2.0 -> 2.1（正文取自 math-vector_v2 的 2.1 文章）
  D. Graph500 程序（C 内核 + SCALE 日志 + 结果）
  E. 19 算子发布包 docs（math-vector_v2/sre_19_operators_release/docs）
  F. Graph500 英文报告 graph500_E.md（全开源口径改写后放入附件）
"""
import os
import re
import shutil

MG = r"c:\mywork\math-graph"
MV2 = r"c:\mywork\math-graph\math-vector_v2"
G500 = r"c:\mywork\graph500\src"
B = r"c:\mywork\SRE-Dynamics"

CLOSED = r"闭源|封闭式|商业核心|商业级|专属规范|Proprietary|Closed Core|closed-source|closed source|commercial core"
REWRITES_CN = [
    ("1.0 (2026年7月·封闭式商业核心专属规范)", "1.0 (2026年7月·开源规范)"),
    ("核心防御与闭源子系统", "核心防御与开源子系统"),
    ("首个核心商业级黑盒/闭源算子", "首个核心开源算子"),
    ("商业核心层（7–10）", "开源核心层（7–10）"),
]
REWRITES_EN = [
    ("1.0 (July 2026 · Proprietary / Closed Core Subsystem Specification)",
     "1.0 (July 2026 · Open-Source Specification)"),
    ("Except for operators 7, 8, 9, and 10, which are closed-source commercial core modules, the full set of system papers, complete algebraic derivations for operators 1–6, and simulation code are fully open.",
     "The full set of system papers, the complete algebraic derivations for operators 1–19, and the simulation code are fully open."),
    ("Except for operators 7, 8, 9, and 10, which are closed-source commercial core modules, the full set of system papers, complete algebraic derivations for operators 1–6, and simulation code are fully open source.",
     "The full set of system papers, the complete algebraic derivations for operators 1–19, and the simulation code are fully open source."),
]


def rt(p):
    with open(p, "rb") as f:
        raw = f.read()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")


def wt(p, t):
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(t)


def count_h1(text):
    fence = None
    out = []
    for line in text.split("\n"):
        m = re.match(r"^\s*(`{3,}|~{3,})", line)
        if fence is None:
            if m:
                fence = m.group(1)[0]
                out.append("")
            else:
                out.append(line)
        else:
            if m and m.group(1)[0] == fence:
                fence = None
            out.append("")
    return len(re.findall(r"^#\s+", "\n".join(out), re.M))


# ---------- A. 算子10 论文重新入书 ----------
for src, dst, key, rw in [
    ("Operator_10_C.md", "Operator_10_1.0_C.md", "作者", REWRITES_CN),
    ("Operator_10_E.md", "Operator_10_1.0_E.md", "Author", REWRITES_EN),
]:
    t = rt(os.path.join(MG, src))
    t = "\n".join(ln for ln in t.split("\n")
                  if not re.match(r"^\*\*%s\*\*\s*[:：]" % key, ln))
    for a, b in rw:
        t = t.replace(a, b)
    left = re.findall(CLOSED, t)
    assert not left, f"{dst} 残留闭源口径 {set(left)}"
    n = count_h1(t)
    assert n == 1, f"{dst} H1={n}"
    wt(os.path.join(B, "3-Mathematical_Support", dst), t)
    print("OK  A 章节", dst, "lines=", len(t.splitlines()))

# ---------- B. 算子10 程序 ----------
for f in ["Operator_10_P.py", "sre_commercial_core.py"]:
    shutil.copyfile(os.path.join(MG, f),
                    os.path.join(B, "5-Appendixs", "Operators", f))
    print("OK  B 程序", f)

# ---------- C. Graph500 章节 2.0 -> 2.1 ----------
for src, cur, new, anchor, vold, vnew in [
    (os.path.join(MV2, "SRE_19_operators_graph500_article_2.1_C.md"),
     os.path.join(B, "4-Applications&Hypothesis", "Graph500_2.0_C.md"),
     os.path.join(B, "4-Applications&Hypothesis", "Graph500_2.1_C.md"),
     "## 一、背景", "版本: 2.0", "版本: 2.1"),
    (os.path.join(MV2, "SRE_19_operators_graph500_article_2.1_E.md"),
     os.path.join(B, "4-Applications&Hypothesis", "Graph500_2.0_E.md"),
     os.path.join(B, "4-Applications&Hypothesis", "Graph500_2.1_E.md"),
     "## 1. Background", "Version: 2.0", "Version: 2.1"),
]:
    body = rt(src)
    body = body[body.index(anchor):]
    head = rt(cur)
    head = head[:head.index(anchor)].replace(vold, vnew)
    out = head.rstrip("\n") + "\n\n" + body
    n = count_h1(out)
    assert n == 1, f"{new} H1={n}"
    wt(new, out)
    os.remove(cur)
    print("OK  C 章节", os.path.basename(new))

# ---------- D. Graph500 程序 ----------
for f in ["sre_csr_kernel.c", "sre_csr_kernel.h",
          "sre_scale12_stdout.txt", "sre_scale20_stdout.txt", "sre_scale24_stdout.txt",
          "result.txt", "result_20.txt", "result_22.txt", "result_24.txt"]:
    src = os.path.join(G500, f)
    if os.path.exists(src):
        shutil.copyfile(src, os.path.join(B, "5-Appendixs", "Graph500", f))
        print("OK  D 程序", f)

# ---------- E. 发布包 docs ----------
rel_src = os.path.join(MV2, "sre_19_operators_release", "docs")
rel_dst = os.path.join(B, "5-Appendixs", "SRE_19_operators_release", "docs")
for f in sorted(os.listdir(rel_src)):
    if f.endswith(".md"):
        shutil.copyfile(os.path.join(rel_src, f), os.path.join(rel_dst, f))
        print("OK  E 文档", f)

# ---------- F. Graph500 英文报告（全开源改写） ----------
t = rt(os.path.join(MV2, "graph500_E.md"))
for a, b in REWRITES_EN:
    t = t.replace(a, b)
left = re.findall(r"closed-source|commercial core|Proprietary", t)
if left:
    print("!!  F 仍残留:", set(left))
wt(os.path.join(B, "5-Appendixs", "Graph500", "graph500_E.md"), t)
print("OK  F 报告 graph500_E.md")

print("DONE")
